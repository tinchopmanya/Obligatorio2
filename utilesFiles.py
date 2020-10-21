import os
import socket
import re

def retornarNombre(name):
    return  "siasd"




def guardarParte( data , nombreArhivo , nroParte ):
    archivoPDF = open(nombreArhivo + nroParte, 'wb')  # abre el archivo datos.txt
    archivoPDF.write(data)
    archivoPDF.close()


def obtenerParte( nombreArhivo , desde , cant):
    dirname = os.path.dirname(__file__)
    rutaArchivo = os.path.join(dirname, 'compartida', '', nombreArhivo)
    archivoPDF = open(rutaArchivo, 'rb')  # abre el archivo datos.txt
    contenido = archivoPDF.read()
    archivoPDF.close()
    parte = contenido[int(desde) : int(cant)]
    return parte

def ObtenerContenidoArchivo( nombreArhivo ):
    archivoPDF = open(nombreArhivo, 'rb')  # abre el archivo datos.txt
    contenido = archivoPDF.read()
    archivoPDF.close()
    return contenido


def UltimaParte( nombreArhivo , cantidadPartes):
    archivoPDF = open(nombreArhivo, 'rb')  # abre el archivo datos.txt
    contenido = archivoPDF.read()
    archivoPDF.close()
    total = len(contenido)
    rest = total - ( cantidadPartes * 1024)
    return rest

def cantidadPartes( nombreArhivo ):
    archivoPDF = open(nombreArhivo, 'rb')  # abre el archivo datos.txt
    contenido = archivoPDF.read()
    archivoPDF.close()
    total = len(contenido)
    cant = int( total / 1024)
    rest = total - ( cant * 1024)
    if rest > 0 :
        cant = cant +1
    return cant


def atenderCliente( num_hilo, conexion , addr , **datos):

    respuesta = conexion.recv(1024).decode()
    splitResp = re.sub('[<>]', '', respuesta).split('\n')

    nombreArchivo = splitResp[1]
    desde = splitResp[3]
    cant = splitResp[4]

    # Aca esta faltando obtner la parte del archivo
    # y retornarlo  , este metodo obtiene la parte de un archivo
    parteArchivo = obtenerParte(nombreArchivo, desde, cant)

    print(respuesta)
    print(parteArchivo)

    conexion.send(b"prueba")

    conexion.close()

def clienteTCP(archivoToDescargar, parte , desde, hasta , ip, **datos):
    start = desde
    size = hasta - desde
    solicitud = "DOWNLOAD\n"
    solicitud = solicitud + "<" + archivoToDescargar.nombre + ">\n"
    solicitud = solicitud + "<" + archivoToDescargar.md5 + ">\n"
    solicitud = solicitud + "<" + str(start) + ">\n"
    solicitud = solicitud + "<" + str(size) + ">\n"
    print(solicitud)
    misocket = socket.socket()
    misocket.connect((ip, 2020))


    misocket.send(solicitud.encode())

    respuesta = misocket.recv(hasta + 1024 - desde)
    print(respuesta.decode())
    print(len(respuesta))
    misocket.close()
