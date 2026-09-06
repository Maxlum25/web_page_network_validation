
text_area = """mpls01-a1.redip.cl   1/1/1
    mpls01-a2.redi.cl           2/2/2     """


def tratar_csv(contenido_csv):
    contenido_csv = contenido_csv.read().decode("utf-8")
    contenido_csv = contenido_csv.replace(";", ",")
    contenido_csv = contenido_csv.strip().split("\n")
    contenido_csv = [fila.split(",") for fila in contenido_csv if fila]
    datos_unicos = []
    vistos = set()
    pos_clave = 4
    pos_valor = 5
    for fila in contenido_csv[1:]:
        fila[pos_clave] = fila[pos_clave].replace('"', '')
        fila[pos_valor] = fila[pos_valor].replace('"', '')
        valor_nuevo = fila[pos_valor].replace("P_","")
        valor_nuevo = valor_nuevo.replace("_Status","")
        pareja = (fila[pos_clave], valor_nuevo)
        if "mpls" in pareja[0]:
            if pareja not in vistos:
                datos_unicos.append(pareja)
                vistos.add(pareja)
    return datos_unicos


def tratar_textarea(contenido: str) -> list:
    contenido = contenido.lower()
    contenido = contenido.strip()
    contenido = contenido.splitlines()
    contenido_list = []
    for i in contenido:
        i = i.split()
        contenido_list.append(i)
    return contenido_list

def check_mpls_port_data(contenido: list) -> bool:
    for i in contenido:
        if not len(i) == 2:
            return False
    for i in range(len(contenido)):
        if not "mpls" in contenido[i][0]:
            return False
        elif not ".redip.cl" in contenido[i][1]:
            return False
    return True
            
        
    

if __name__ == "__main__":
    texto_tratado = tratar_textarea(text_area)
    print(texto_tratado)