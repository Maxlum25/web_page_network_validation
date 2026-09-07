import flask
from dotenv import load_dotenv
import os
import credential
from procesamiento_archivo import tratar_textarea, check_mpls_port_data
import command_tacacs
from command_tacacs import check_port_status
from zabbix import get_hostid, get_itemid, get_rx_trend, format_history_rx

app = flask.Flask(__name__)
load_dotenv()

URL_ZABBIX_CENTRAL = os.getenv("URL_ZABBIX_CENTRAL")
app.secret_key = os.getenv("APP_SECRET_KEY")
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
         #En el index, el usuario tiene multiples acciones que ejecutar, por lo tanto cada boton tienen el nombre accion y luego se evalua el valor para saber que cosa quiere hacer el usuario.       
        accion = flask.request.form.get("accion")
        
        if accion == "subir_csv":
            #Se guarda el filestorage del archivo en la variable archivo_csv
            archivo_csv = flask.request.files["archivo_csv"]
            #Se crea lista con los tipos correctos de archivo csv
            MIME_PERMITIDOS = ['text/csv', 'application/vnd.ms-excel', 'text/plain']
            # A continuacion se verifica si los datos guardados en la variabale es un .csv
            if archivo_csv.filename == "" or not archivo_csv.filename.lower().endswith(".csv") or archivo_csv.content_type not in MIME_PERMITIDOS:
                error_csv = "Archivo no valido, adjunta un CSV"
                return flask.render_template("index.html", error_csv=error_csv)
            # luego de validar que se haya subido el archivo correctamente, viene el proceso de lectura y procesamiento.
            else:
                archivo_csv = tratar_csv(archivo_csv)
               
                for host, port in archivo_csv:
                    print(f"{host}: {port}")
                    if not puerto_abierto(host):
                        salida_mpls.append(f"No fue posible conectar con {host}")
                        fecha_potencia = [('sin información', 'sin información')]
                        historial_rx.append(fecha_potencia)
                        host_port.append(f"{host}: {port}")                                                
                        continue                   
                    salida_mpls.append(check_port_status(host, usuario, contraseña, port))
                    hostid = get_hostid(url_zabbix, token, host)
                    itemid = get_itemid(url_zabbix, token, hostid, port)
                    history = get_rx_trend(url_zabbix, token, itemid)
                    history = format_history_rx(history)
                    host_port.append(f"{host}: {port}")
                    historial_rx.append(history)
            
                datos_combinados = zip(historial_rx, salida_mpls, host_port)
                return flask.render_template("index.html",datos_combinados=datos_combinados)
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
                return flask.render_template("index.html", error_textarea= error_textarea)
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
        return flask.render_template("index.html",datos_combinados=datos_combinados, error_textarea=error_textarea)
    
        
    
    return flask.render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    
    login_error = None
    
    if flask.request.method == "POST":
        username = flask.request.form["username"]
        password = flask.request.form["password"]
        
        validate_user = credential.test_credential(username, password)
        if validate_user:
            flask.session.update({
                "flag_session": True
            })
            return flask.redirect(flask.url_for("index"))
        else:
            login_error = "Error al iniciar sesion"
            return flask.render_template("login.html", login_error = login_error)
    return flask.render_template("login.html")
        

@app.get("/healthz")
def healthz():
    return {"status": "ok"}, 200     
        
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)