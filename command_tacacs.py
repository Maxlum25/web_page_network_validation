from netmiko import ConnectHandler
from netmiko.exceptions import NetMikoTimeoutException, NetMikoAuthenticationException


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
        print("Error: Falló la autenticación (Usuario/Pass incorrectos)")
        return "No fue posible extraer los datos"
    except NetMikoTimeoutException:
        print("Error: Tiempo de espera agotado (El equipo no responde)")
        return "No fue posible extraer los datos"
    except Exception as e:
        print(f"Error desconocido SSH: {str(e)}")
        return "No fue posible extraer los datos"