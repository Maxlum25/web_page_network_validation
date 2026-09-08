import flask
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
import os
from werkzeug.middleware.proxy_fix import ProxyFix
import credential
from procesamiento_archivo import tratar_textarea, tratar_csv, check_mpls_port_data
import command_tacacs
from command_tacacs import check_port_status
from zabbix import get_hostid, get_itemid, get_rx_trend, format_history_rx
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect



app = flask.Flask(__name__)
load_dotenv()

if not os.path.exists('logs'):
    os.mkdir('logs')

file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)

file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))

file_handler.setLevel(logging.INFO)

app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

app.logger.info('Sistema de monitoreo iniciado correctamente')

limiter = Limiter(get_remote_address, app=app, storage_uri="memory://")

# --- Configuración ---
app.secret_key = os.getenv("APP_SECRET_KEY")
csrf = CSRFProtect(app)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Strict",
    SESSION_COOKIE_SECURE=True,   # detrás de Nginx con HTTPS
    MAX_CONTENT_LENGTH=10 * 1024 * 1024,  # 10 MB máx para subidas
)

# ProxyFix: Flask ve la IP real y el esquema https detrás de Nginx
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# --- Variables de entorno ---
URL_ZABBIX_CENTRAL = os.getenv("URL_ZABBIX_CENTRAL")
TOKEN_ZABBIX = os.getenv("TOKEN_ZABBIX")
TACACS_USER = os.getenv("TACACS_USER")
TACACS_PASSWORD = os.getenv("TACACS_PASSWORD")


@app.route("/", methods=["GET", "POST"])
def index():
    error_textarea = None
    salida_mpls = []
    historial_rx = []
    host_port = []

    if not flask.session.get("flag_session"):
        return flask.redirect(flask.url_for("login"))

    if flask.request.method == "POST":
        accion = flask.request.form.get("accion")

        try:
            if accion == "subir_csv":
                try:
                    archivo_csv = flask.request.files["archivo_csv"]
                    MIME_PERMITIDOS = ['text/csv', 'application/vnd.ms-excel', 'text/plain']
                    if archivo_csv.filename == "" or not archivo_csv.filename.lower().endswith(".csv") or archivo_csv.content_type not in MIME_PERMITIDOS:
                        error_csv = "Archivo no valido, adjunta un CSV"
                        return flask.render_template("index.html", error_csv=error_csv)
                    else:
                        archivo_csv = tratar_csv(archivo_csv)
                        for host, port in archivo_csv:
                            print(f"{host}: {port}")
                            if not command_tacacs.puerto_abierto(host):
                                salida_mpls.append(f"No fue posible conectar con {host}")
                                fecha_potencia = [('sin información', 'sin información')]
                                historial_rx.append(fecha_potencia)
                                host_port.append(f"{host}: {port}")
                                continue
                            salida_mpls.append(check_port_status(host, TACACS_USER, TACACS_PASSWORD, port))
                            hostid = get_hostid(URL_ZABBIX_CENTRAL, TOKEN_ZABBIX, host)
                            itemid = get_itemid(URL_ZABBIX_CENTRAL, TOKEN_ZABBIX, hostid, port)
                            history = get_rx_trend(URL_ZABBIX_CENTRAL, TOKEN_ZABBIX, itemid)
                            history = format_history_rx(history)
                            host_port.append(f"{host}: {port}")
                            historial_rx.append(history)

                        datos_combinados = zip(historial_rx, salida_mpls, host_port)
                        return flask.render_template("index.html", datos_combinados=datos_combinados)
                except Exception as e:
                    app.logger.error(f"Error crítico procesando CSV: {str(e)}", exc_info=True)
                    return flask.render_template("index.html", error_csv="Ocurrió un error interno al procesar el archivo")

            elif accion == "revisar_equipos":
                equipos_puertas = flask.request.form.get("equipos_puertas")
                if equipos_puertas == "":
                    print("No se escribio nada en el Textarea")
                    error_textarea = "Primero debes proporcionar los datos"
                    return flask.render_template("index.html", error_textarea=error_textarea)
                equipos_puertas = tratar_textarea(equipos_puertas)
                print(f"Equipos y puertos: {equipos_puertas}")
                if not check_mpls_port_data(equipos_puertas):
                    error_textarea = "Revisa los datos y vuelve a colocarlos"
                    return flask.render_template("index.html", error_textarea=error_textarea)
                for host, port in equipos_puertas:
                    if not command_tacacs.puerto_abierto(host):
                        salida_mpls.append(f"No fue posible conectar con {host}")
                        fecha_potencia = [('sin información', 'sin información')]
                        historial_rx.append(fecha_potencia)
                        host_port.append(f"{host}: {port}")
                        continue
                    salida_mpls.append(check_port_status(host, TACACS_USER, TACACS_PASSWORD, port))
                    hostid = get_hostid(URL_ZABBIX_CENTRAL, TOKEN_ZABBIX, host)
                    itemid = get_itemid(URL_ZABBIX_CENTRAL, TOKEN_ZABBIX, hostid, port)
                    history = get_rx_trend(URL_ZABBIX_CENTRAL, TOKEN_ZABBIX, itemid)
                    history = format_history_rx(history)
                    host_port.append(f"{host}: {port}")
                    historial_rx.append(history)

            datos_combinados = zip(historial_rx, salida_mpls, host_port)
            return flask.render_template("index.html", datos_combinados=datos_combinados, error_textarea=error_textarea)
        
        except Exception as e:
            app.logger.error(f"Error crítico procesando solicitud: {str(e)}", exc_info=True)
            error_general = "Ocurrió un error interno al procesar la solicitud."
            return flask.render_template("index.html", error_textarea=error_general if accion == "revisar_equipos" else None, 
                                         error_csv=error_general if accion == "subir_csv" else None)

    return flask.render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
@limiter.limit("20 per minute", methods=["POST"])
def login():
    login_error = None
    if flask.request.method == "POST":
        username = flask.request.form["username"]
        password = flask.request.form["password"]
        validate_user = credential.test_credential(username, password)
        if validate_user:
            flask.session.update({"flag_session": True})
            return flask.redirect(flask.url_for("index"))
        else:
            login_error = "Error al iniciar sesion"
            return flask.render_template("login.html", login_error=login_error)
    return flask.render_template("login.html")


@app.get("/healthz")
def healthz():
    return {"status": "ok"}, 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)