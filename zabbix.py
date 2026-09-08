import json
import requests
import time
from datetime import datetime
from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger(__name__)

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
        # NOTA DE SEGURIDAD: verify=False es necesario si tu Zabbix es HTTP o tiene certificado autofirmado.
        # Asegúrate de que esto sea aceptable en tu política de seguridad interna.
        response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
        respuesta_json = response.json()
        
        if "result" in respuesta_json:
            return respuesta_json["result"]
        else:
            # CORREGIDO: exc_info fuera de las comillas y uso de comillas simples para evitar conflictos
            error_msg = respuesta_json.get("error")
            logger.error(f"Error al obtener token: {error_msg}", exc_info=True)
            return None
    
    except Exception as e:
        logger.error(f"Error exception al intentar obtener token: {e}", exc_info=True)
        return None
    
def get_hostid(url, token, host):
    url = f"{url}/api_jsonrpc.php"
    headers = {"Content-Type": "application/json-rpc"}
    
    payload = {
        "jsonrpc": "2.0",
        "method": "host.get",
        "params": {
            "filter": {
                "name": [host]
            }     
        },
        "auth": token,
        "id": 1
    }
    
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
        respuesta_json = response.json()
        
        if "result" in respuesta_json and len(respuesta_json["result"]) > 0:
            return respuesta_json["result"][0]["hostid"]
        else:
            error_msg = respuesta_json.get("error")
            logger.error(f"Error al obtener el hostid para {host}: {error_msg}", exc_info=True)
            return None
    except Exception as e:
        logger.error(f"Error exception al intentar obtener hostid: {e}", exc_info=True)
        return None
    
def get_itemid(url, token, hostid, port):
    url = f"{url}/api_jsonrpc.php"
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
        
        if "result" in respuesta_json and len(respuesta_json["result"]) > 0:
            return respuesta_json["result"][0]["itemid"]
        else:
            error_msg = respuesta_json.get("error")
            logger.error(f"Error al obtener el itemid para puerto {port}: {error_msg}", exc_info=True)
            return None
    
    except Exception as e:
        logger.error(f"Error exception al obtener itemid: {e}", exc_info=True)
        return None
    

def get_rx_trend(url, token, itemid):
    url = f"{url}/api_jsonrpc.php"
    headers = {"Content-Type": "application/json-rpc"}
    
    payload = {
        "jsonrpc": "2.0",
        "method": "trend.get",
        "params": {
            "output": ["clock", "value_avg"],
            "itemids": [itemid],
            "time_from": int(time.time()) - (90 * 24 * 60 * 60),
            "time_till": int(time.time()),
            "limit": "10000"
        },
        "auth": token,
        "id": 5
    }
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
        respuesta_json = response.json()  
        
        if "result" in respuesta_json:
            return respuesta_json["result"]
        else:
            error_msg = respuesta_json.get("error")
            logger.error(f"No se pudo obtener el historial: {error_msg}", exc_info=True)
            return None
    except Exception as e:
        logger.error(f"Error de exception al obtener historial: {e}", exc_info=True)
        return None  # Agregado return None para consistencia
            
def format_history_rx(history):
    fecha = []
    fecha_formato = []
    salida = []
    
    if not history:
        return []

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
        logger.error(f"Error de exception No se pudo formatear los datos de historial rx: {e}", exc_info=True)
        return None
    

if __name__ == "__main__":
    load_dotenv()

    ZABBIX_USER = os.getenv("ZABBIX_USER")
    ZABBIX_PASSWORD = os.getenv("ZABBIX_PASSWORD")
    URL_ZABBIX_CENTRAL = os.getenv("URL_ZABBIX_CENTRAL")
    
    if not all([ZABBIX_USER, ZABBIX_PASSWORD, URL_ZABBIX_CENTRAL]):
        print("Faltan variables de entorno para Zabbix")
    else:
        token = get_token(URL_ZABBIX_CENTRAL, ZABBIX_USER, ZABBIX_PASSWORD)
        print(f"Token obtenido: {token}")