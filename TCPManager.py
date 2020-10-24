
import os
import threading
import utilesFiles
import Objetos
import socket
import time
import re



#  Descarga todas las partes de un archivo de un host determinado
def DescargarPartesFromPeer(archivoToDescargar , peer):
    print("peer " + str(peer.ip  + " cantidad de partes " + str(len(peer.partes))) )
    for parte in peer.partes:
        ClienteTCP(archivoToDescargar, parte.idParte , parte.desde , parte.hasta, parte.ip)
        parte.finalizada = 1
    peer.finalizado = 1



# Realiza los solicitud de descarga
def ClienteTCP(archivoToDescargar, parte , desde, hasta , ip, **datos):
    start = desde
    size = hasta - desde
    solicitud = "DOWNLOAD\n"
    solicitud = solicitud + "<" + archivoToDescargar.nombre + ">\n"
    solicitud = solicitud + "<" + archivoToDescargar.md5 + ">\n"
    solicitud = solicitud + "<" + str(start) + ">\n"
    solicitud = solicitud + "<" + str(size) + ">\n"
    misocket = socket.socket()
    misocket.connect((ip, 2020))
    misocket.send(solicitud.encode())
    respuesta = misocket.recv(hasta + utilesFiles.tambloqueGlobal - desde)
    utilesFiles.GuardarArchivo(respuesta, "temp",  archivoToDescargar.nombre + str(parte))
    misocket.close()


# Escucha conecciones de descarga y abre un nuevo hilo
# con destino el metodo AtenderCliente
def ServidorTCP():
    misocket = socket.socket()
    misocket.bind(("", 2020))
    misocket.listen(5)
    #print(" Nueva conexion estableida")

    num_hilo = 0
    while True:
        conexion, addr = misocket.accept()
        #print(" Nueva conexion estableida")
        #print(addr)


        num_hilo = num_hilo + 1
        hilo = threading.Thread(target=AtenderCliente,
                                args=(num_hilo, conexion, addr))
        hilo.start()

# Atiende los clientes del lado del servidor TCP , retornando la parte del archivo solicitada
def AtenderCliente( num_hilo, conexion , addr , **datos):
    respuesta = conexion.recv(utilesFiles.tambloqueGlobal).decode()
    splitResp = re.sub('[<>]', '', respuesta).split('\n')
    nombreArchivo = splitResp[1]
    desde = splitResp[3]
    cant = splitResp[4]
    parteArchivo = utilesFiles.ObtenerParte(nombreArchivo, desde, cant)
    conexion.send(parteArchivo)
    conexion.close()
