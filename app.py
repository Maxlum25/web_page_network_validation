import flask
from dotenv import load_dotenv
import os

app = flask.Flask(__name__)
load_dotenv()

URL_ZABBIX_CENTRAL = os.getenv("URL_ZABBIX_CENTRAL")
app.secret_key = os.getenv("APP_SECRET_KEY")
TOKEN_ZABBIX = os.getenv("TOKEN_ZABBIX")
TACACS_USER = os.getenv("TACACS_USER")
TACACS_PASSWORD = os.getenv("TACACS_PASSWORD")


@app.route("/", methods=["GET", "POST"])
def index():
    
    if not flask.session.get("flag_session"):
        return flask.redirect(flask.url_for("login"))
    
    return flask.render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    
    if flask.request.method == "POST":
        username = flask.request.form["username"]
        password = flask.request.form["password"]
        
        #aqui se verifica el usuario y contraseña en la DB.
        

