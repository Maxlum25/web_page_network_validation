from netmiko import ConnectHandler
from netmiko.exceptions import NetMikoTimeoutException, NetMikoAuthenticationException
import socket
import logging

# Crea un logger con el nombre del módulo
logger = logging.getLogger(__name__)

def check_port_status(host, username, password, port):
    #this host has diferent names between zabbix and tacacs.
    if host == "mpls03-mqui2.redip.cl":
        host = "mpls03-mqui.redip.cl"
    device = {
        "device_type": "nokia_sros",
        "host": host,
        "username": username,
        "password": password,
        "port": 22,
        "conn_timeout": 15,
    }
        
    try:
        
        net_connect = ConnectHandler(**device)
        comand = f"show port {port}"
        output = net_connect.send_command(comand)
        net_connect.disconnect()
        return output
    
    except NetMikoAuthenticationException:
        logger.error(f"Error: Falló la autenticación (Usuario/Pass incorrectos), exc_info=True")
        return "No fue posible extraer los datos"
    except NetMikoTimeoutException:
        logger.error(f"Error: Tiempo de espera agotado (El equipo no responde), exc_info=True")
        return "No fue posible extraer los datos"
    except Exception as e:
        logger.error(f"Error desconocido SSH: {str(e)}, exc_info=True")
        return "No fue posible extraer los datos"


def puerto_abierto(host, puerto=22):
    # Intenta una conexión TCP con un timeout muy bajo
    try:
        # socket.create_connection es extremadamente rápido
        with socket.create_connection((host, puerto), timeout=0.5):
            return True
    except OSError:
        logger.error(f"no fue posible conectar con equipo {host}, exc_info=True")
        return False