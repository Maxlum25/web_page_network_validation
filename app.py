import flask
from dotenv import load_dotenv
import os
import credential
from procesamiento_archivo import tratar_textarea, check_mpls_port_data

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
            pass
        elif accion == "revisar_equipos":
            equipos_puertas = flask.request.form.get("equipos_puertas")
            if equipos_puertas == "":
                print("No se escribio nada en el Textarea")
                error_textarea = "Primero debes proporcionar los datos"
                return flask.render_template("index.html", error_textarea=error_textarea)
            equipos_puertas = tratar_textarea(equipos_puertas)
            if not check_mpls_port_data(equipos_puertas):
                error_textarea = "Revisa los datos y vuelve a colocarlos"
                return flask.render_template("index.html", error_textarea= error_textarea)
            for host, port in equipos_puertas:
                
        
        
    
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
        
        
        
if __name__ == "__main__":
    app.run(debug=True)
