import json
import requests
import time
from datetime import datetime
from dotenv import load_dotenv
import os



def get_token(url, username, password):
    url = f"{url}/api_jsonrpc.php"
    headers = {"Content-Type": "application/json-rpc"}
    
    payload = {
    "jsonrpc": "2.0",
    "method": "user.login",
    "params": {
        "username": username,
        "password": password
    },
    "id": 1,
    "auth": None
    }
    
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
        respuesta_json = response.json()
        if "result" in respuesta_json:
            return respuesta_json["result"]
        else:
            print (f"Error al obtener token: {respuesta_json.get("error")}")
            return None
    
    except Exception as e:
        print(f"Error exception al intentar obtener token: {e}")
        return None
    
def get_hostid(url, token, host):
    url = f"{url}/api_jsonrpc.php"
    headers = {"Content-Type": "application/json-rpc"}
    
    payload = {
        "jsonrpc": "2.0",
        "method": "host.get",
        "params": {
            "filter": {
                "name": [
                    host
                ]
            }     

        },
        "auth": token,
        "id": 1
        }
    
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
        respuesta_json = response.json()
        
        if "result" in respuesta_json:
            return respuesta_json["result"][0]["hostid"]
        else:
            print(f"Error al obtener el hostid: {respuesta_json.get("error")}")
            return None
    except Exception as e:
        print(f"Error exception al intentar obtener hostid: {e}")
        return None
    
def get_itemid(url, token, hostid, port):
    url= f"{url}/api_jsonrpc.php"
    headers = {"Content-Type": "application/json-rpc"}
    
    payload = {
    "jsonrpc": "2.0",
    "method": "item.get",
    "params": {
        "output": "itemid",
        "hostids": hostid,
        "search": {
            "key_": f"RxPower[{port}]"
        },
        "filter": {
            "key_": f"RxPower[{port}]"
        }
        
    },
    "auth": token,
    "id": 3
    }
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
        respuesta_json = response.json()
        if "result" in respuesta_json:
            return respuesta_json["result"][0]["itemid"]
        else:
            print(f"Error al obtener el itemid: {respuesta_json.get("error")}")
            return None
    
    except Exception as e:
        print(f"Error exception al obtener itemid: {e}")
        return None
    

def get_rx_trend(url, token, itemid):
    url= f"{url}/api_jsonrpc.php"
    headers = {"Content-Type": "application/json-rpc"}
    
    payload = {
    "jsonrpc": "2.0",
    "method": "trend.get",
    "params": {
        "output": [
            "clock",
            "value_avg",
        ],
        "itemids": [
            itemid
        ],
        "time_from": int(time.time()) - (90 * 24 * 60 * 60),
        "time_till": int(time.time()),
        "limit": "10000"
    },
    "auth": token,
    "id": 5
    }
    try:
        response= requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
        respuesta_json= response.json()  
        if "result" in respuesta_json:
            return respuesta_json["result"]
        else:
            print(f"No se pudo obtener el historial: {respuesta_json.get("error")}")
            return None
    except Exception as e:
        print(f"Error de exception al obtener historial: {e}")
            
def format_history_rx(history):
    fecha = []
    fecha_formato = []
    salida = []
    
    try:
        for i in range(len(history)):
            fecha.append(int(history[i]["clock"]))
        for i in fecha:
            dt_object = datetime.fromtimestamp(i)
            fecha_formato.append(dt_object.strftime('%Y-%m-%d %H:%M'))
        for i in range(len(fecha_formato)):
            salida.append((fecha_formato[i], history[i]["value_avg"]))
        return salida
    except Exception as e:
        print(f"Error de exception No se pudo formatear los datos de historial rx: {e}")
        return None
    

if __name__ == "__main__":

    load_dotenv()

    ZABBIX_USER = os.getenv("ZABBIX_USER")
    ZABBIX_PASSWORD = os.getenv("ZABBIX_PASSWORD")
    URL_ZABBIX_CENTRAL = os.getenv("URL_ZABBIX_CENTRAL")
    token = get_token(URL_ZABBIX_CENTRAL, ZABBIX_USER, ZABBIX_PASSWORD)
    print(f"Token obtenido: {token}")