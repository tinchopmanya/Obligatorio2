import hashlib
import os
import threading
from random import random
from random import uniform

import TCPManager
import utilesFiles
import Objetos
import socket
import time

from os import walk

ipEsteEquipo = ""
equipos = []
misArchivos = {}
listaArchivos = []
tambloqueGlobal  = 1024000

def getListArchivos():
    strRetorno = ""
    for arc in listaArchivos:
        strRetorno = strRetorno + "<" + str(arc.idArchivo) + "><" + str(arc.largo)  + "><" + arc.nombre + ">\r\n"
    return  strRetorno


def escucharAnuncios():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
    # Enable broadcasting mode
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client.bind(("", 2020))
    while True:
        data, addr = client.recvfrom(1024)

        #if ipEsteEquipo != addr[0]:
        #print(" UDP Recibido con origen :  " + addr[0] )
        print(" UDP Recibido en IP : " + ipEsteEquipo + " -  origen :  " + addr[0] )

        equipo =  Objetos.Equipo("0")

        for eq in equipos:
            if eq.ip == addr[0]:
                equipo = eq

        if equipo.ip == '0':
            equipo = Objetos.Equipo(addr[0])
            equipos.append(equipo)

        if equipo.ip != ipEsteEquipo:
            x = data.decode().split("\n")

            #print(len(x))
            if x[0] == "ANNOUNCE":
                for strlinea in x:
                    if strlinea != "ANNOUNCE":
                        #print(strlinea)
                        h = strlinea.split("\t")
                        Archiv = Objetos.Archivo(0, "0", "0", "0")
                        ultimoAnuncio = time.time()
                        if len(h) == 3 :
                            if not tengo_ese_md5_en_misArchivos(h[2]):
                                for fl in equipo.archivos:
                                    if fl.md5 == h[2]:
                                        Archiv = fl
                                if Archiv.md5 == "0":
                                    for fl in listaArchivos:
                                        if fl.md5 == h[2]:
                                            fl.ips.append(addr[0])
                                            peer = Objetos.Peer(addr[0], 0, ultimoAnuncio)
                                            fl.peers.append(peer)
                                            Archiv = fl
                                    if Archiv.md5 == "0":
                                        Objetos.Archivo.contidArchivo = Objetos.Archivo.contidArchivo + 1
                                        Archiv = Objetos.Archivo(Objetos.Archivo.contidArchivo, h[0], h[1], h[2])
                                        peer = Objetos.Peer(equipo.ip, 0, ultimoAnuncio)
                                        Archiv.peers.append(peer)
                                        Archiv.ips.append(addr[0])
                                        equipo.archivos.append(Archiv)
                                        listaArchivos.append(Archiv)
                                    else:
                                        for peer in Archiv.peers:
                                            if peer.ip == equipo.ip:
                                                peer.ultimoAnuncio = ultimoAnuncio
                                        equipo.archivos.append(Archiv)
                                else:
                                        for peer in Archiv.peers:
                                            if peer.ip == equipo.ip:
                                                peer.ultimoAnuncio = ultimoAnuncio
            elif x[0] == "REQUEST":
                time.sleep(uniform(0,5))
                mensaje = "ANNOUNCE\n"
                archivos = ls("compartida")
                for archivo in archivos:
                    if misArchivos[arc]['offer'] == True:
                        dirName = os.path.dirname("__file__")
                        folderName = os.path.join(dirName, 'compartida', '')
                        sizeFile = os.stat(folderName + archivo).st_size
                        md5suma = hashlib.md5(open(folderName + archivo, 'rb').read()).hexdigest()
                        mensaje += archivo + "\t" + str(sizeFile) + "\t" + md5suma + "\n"
                if mensaje != "ANNOUNCE\n":
                    client.sendto(mensaje.encode(), (addr[0], 2020))

def tengo_ese_md5_en_misArchivos(md5):
    for nombre in misArchivos:
        if misArchivos[nombre]['md5'] == md5:
                return True
    return False

def anunciarArchivos():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    sock.sendto( "REQUEST\n".encode() , ('<broadcast>', 2020))
    # Set a timeout so the socket does not block indefinitely when trying to receive data.
    sock.settimeout(0.2)

    while True:
        mensaje = "ANNOUNCE\n"
        archivos = ls("compartida")
        stringarc = ""
        for arc in archivos:
            if misArchivos[arc]['offer'] == True:
                stringarc = ""
                stringarc = stringarc + arc
                dirname = os.path.dirname("__file__")
                folderName = os.path.join(dirname, 'compartida', '')
                sizefile = os.stat(folderName + arc).st_size
                md5suma = hashlib.md5(open(folderName + arc, 'rb').read()).hexdigest()
                mensaje = mensaje + stringarc + "\t" + str(sizefile) + "\t" + md5suma + "\n"
                #if (misArchivos.count(md5suma) == 0):
                #    misArchivos.append(md5suma)
        if mensaje != "ANNOUNCE\n":
            sock.sendto( mensaje.encode() , ('<broadcast>', 2020))
        #print("mensaje enviado al puerto 2020 (anunciarArchivos)\n")
        aleatorio = random()
        #  print( "\n numero aleatorio de 0 a 1 " + str(aleatorio))
        time.sleep(10 + aleatorio)


# Retorna el Peer (Host) , a partir de su ip
def obtenerPeer(archivoToDescargar, ip):
    peerRet = Objetos.Peer(0,0,0)
    for peer in archivoToDescargar.peers:
        if peer.ip == ip :
            peerRet = peer
    return peerRet


# Este metodo se encarga de...
# 1 - Realizar la descarga del archivo del cual se hizo el get en la consola
#      abriendo un hilo para la descarga en paralelo para cada host que posee el archivo
# 2 - Esperar que se descarguen todas las partes de todos los peers(hosts)
# 3 - Unificar el archivo final a partir de las partes descargadas, y eliminar las partes
def descargarArchivo(archivoToDescargar):
    cantidadHost = len(archivoToDescargar.ips)
    total = int( archivoToDescargar.largo)
    tamBlock = tambloqueGlobal
    cant = int( total / tamBlock)
    rest = total - ( cant * tamBlock)
    if rest > 0 :
        cant = cant + 1
    for ip in archivoToDescargar.ips:
        peer =  Objetos.Peer(ip,0,0)
        archivoToDescargar.peers.append(peer)

    desde = 0
    strret = ""
    for i in range(cant):
        ipnumero = i % cantidadHost
        if i == cant - 1 :
            hasta = desde +  rest
        else:
            hasta = desde + tamBlock
       
        parte =  Objetos.ParteArchivo(i, archivoToDescargar.ips[ipnumero], desde , hasta , 0)
        archivoToDescargar.partes.append(parte)
        desde = desde + tamBlock
    
    for parte in archivoToDescargar.partes:
        peer = obtenerPeer(archivoToDescargar,parte.ip)
        peer.partes.append(parte)

    # Se inicia un hilo para cada host que tiene el archivo
    # permitiendo que el archivo se descargue en paralelo entre los host destinos
    for peer in archivoToDescargar.peers:
        hilo = threading.Thread(target=TCPManager.DescargarPartesFromPeer,
                            args=( archivoToDescargar, peer ),
                            kwargs={})
        hilo.start()

    # Para cada host del cual se esta realizando la descarga
    # solo se puede continuar si los hilos abiertos, ya descargaron todas las partes
    # Por lo tanto el objetivo del for siguiente, es esperar que las descargas terminen
    for peer in archivoToDescargar.peers:
        cont = 0
        while peer.finalizado == 0:
           cont = cont + 1
           time.sleep(1)

    nroParte = 0
    
    time.sleep(1) 
    cantPartes = len(archivoToDescargar.partes)

    suma = 0
    archivoTotal = b""
    for i in range (cantPartes):        
        cont = utilesFiles.ObtenerContenidoArchivo(archivoToDescargar.nombre + str(i))
        archivoTotal = archivoTotal + cont        
        suma = suma + len(cont)

    # Se guarda todo el archivo unificado en la carpeta compartida.
    utilesFiles.GuardarArchivo(archivoTotal, "compartida" , archivoToDescargar.nombre)
    print( "Archivo Descargado , borrando las partes temporales" )
    archivoTotal = ""

    # Se borran todas las partes temporales del archivo ya descargado
    for i in range (cantPartes):
        utilesFiles.BorrarParte(archivoToDescargar.nombre + str(i))

    index = 0
    indexToDelete = -1
    for fl in listaArchivos:
        if fl.md5 == archivoToDescargar.md5:
            indexToDelete = index
        index = index + 1

    if indexToDelete > -1:
        del(listaArchivos[indexToDelete])
        misArchivos[archivoToDescargar.nombre] = { 'md5': archivoToDescargar.md5, 'offer': False}
    else:
        print(" No Se elimino el archivo de la lista de archivos")

    strret = " Se termino de descargar el archivo, puede encontrarlo en la carpeta compartida"
    return  strret


# Busca el archivo a descargar a partir del numero que lo identifica en el comando list
def ObtenerArchivoADescargar(numeroArchivo):
    archivoToDescargar =  Objetos.Archivo(0, "0","0","0")
    ipsToDownload = []

    encontre = 0
    for  arch in listaArchivos:
        if arch.idArchivo == int(numeroArchivo):
            archivoToDescargar = arch
            encontre = 1
    
    if encontre == 0:
        raise Exception("La ID ingresada no es correcta")
    #print("Descargando archivo " + archivoToDescargar.nombre)

    for eq in equipos:
        for arc in eq.archivos:
            print(eq.ip + " - " + arc.nombre + " - " + str(arc.idArchivo))

    destinos = ""
    cont = 0
    for ip in archivoToDescargar.ips:
        destinos =  destinos + ip
        cont = cont + 1
        if len(archivoToDescargar.ips) > cont:
            destinos = destinos + " , "
    return "Descargando Archivo:  ---->  '" + archivoToDescargar.nombre + "' \r\nDesde los host : " + destinos + "\r\n" , archivoToDescargar


def ls(ruta='.'):
    dir, subdirs, archivos = next(walk(ruta))
    return archivos


#  terminal telnet
def terminalConsola():
    host = ''  # (2)
    port = 2025  # (3)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # (4)
    s.bind((host, port))  # (5)
    s.listen(1024)  # (7)

    while (True):
        conn, addr = s.accept()
        conn.sendall(b'>')
        data = ""
        while (True):
            data += conn.recv(1024).decode()
            if not data:
                break
            if not data.endswith("\r\n"):
                continue
            splitted_data = data.split()
            if len(splitted_data) != 0:
                if data == "list\r\n":
                    strListArchivos = "\r\n" + getListArchivos() + "\r\n"
                    conn.sendall(strListArchivos.encode())
                elif (splitted_data[0] == 'get' and len(splitted_data) == 2) and splitted_data[1].isdigit():
                    try:
                        retorno , archivo = ObtenerArchivoADescargar(splitted_data[1])
                        conn.sendall(retorno.encode())
                        retorno = descargarArchivo(archivo)
                        conn.sendall(retorno.encode())
                        conn.sendall("\r\n".encode())
                    except Exception as msg:
                        conn.sendall((str(msg)+"\r\n").encode())

                elif (splitted_data[0] == 'offer' and len(splitted_data) == 2):
                    nombre = splitted_data[1]
                    if misArchivos.get(nombre) != None:
                        misArchivos[nombre]['offer'] = True
                    else:
                        conn.sendall("El nombre de archivo no existe\r\n".encode())
                else:
                    conn.sendall("Error en el comando\r\n".encode())
                data = ""
            data = ""
            conn.sendall(b'>')
        print('Cerrando socket conn')
        conn.close()


# Borra archivos que no fueron anunciados hace mas de 90 segundos
def borrarArchivos():
    while True:
        time.sleep(10)
        tiempoActual = time.time()
        for archivo in listaArchivos:
            for peer in archivo.peers:
                print("tiempo actual - ultimo" + str(tiempoActual - peer.ultimoAnuncio))
                if (tiempoActual - peer.ultimoAnuncio > 90):
                    print("hay que borrar")
                    print(peer.ip)
                    for eq in equipos:
                        if eq.ip == peer.ip:
                            eq.archivos.remove(archivo)
                    archivo.peers.remove(peer)
            if len(archivo.peers) == 0:
                print("borrado de la lista")
                print(archivo.nombre)
                listaArchivos.remove(archivo)


if __name__ == '__main__':
    Objetos.Archivo.contidArchivo = 0
    ipEsteEquipo = [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1][0]
    
    archivos = ls("compartida")
    for arc in archivos:
        dirname = os.path.dirname("__file__")
        folderName = os.path.join(dirname, 'compartida', '')
        md5suma = hashlib.md5(open(folderName + arc, 'rb').read()).hexdigest()
        misArchivos[arc] = { 'md5': md5suma, 'offer': False }

    # Hilo para hacer los anuncios de archivos UDP
    hiloAnuncios = threading.Thread(target=anunciarArchivos, args=())
    hiloAnuncios.start()

    # Hilo para escuchar los anuncios
    hiloEscuchaAnuncios = threading.Thread(target=escucharAnuncios, args=())
    hiloEscuchaAnuncios.start()

    # Hilo para la terminal telnet
    hiloterminalConsola = threading.Thread(target=terminalConsola, args=())
    hiloterminalConsola.start()

    # Hilo para responder solicitudes de descarga
    hiloservidorTCP = threading.Thread(target=TCPManager.ServidorTCP, args=())
    hiloservidorTCP.start()

    # Hilo para borrar archivos
    hiloBorrarArchivos = threading.Thread(target=borrarArchivos, args=())
    hiloBorrarArchivos.start()