import os
import socket
import re
from os import remove


tambloqueGlobal  = 1024000


# Guarda un archivo en el directorio indicado por parametros

def GuardarArchivo( data , directorio , nombreArhivo  ):
    dirname = os.path.dirname(__file__)
    rutaArchivo = os.path.join(dirname, directorio, '', nombreArhivo )
    archivoPDF = open(rutaArchivo, 'wb')
    archivoPDF.write(data)
    archivoPDF.close()



# Elimina un archivo del directorio temp

def BorrarParte( nombreArhivo ):
    dirname = os.path.dirname(__file__)
    rutaArchivo = os.path.join(dirname, 'temp', '', nombreArhivo )
    remove(rutaArchivo)
    


# Retorna parte del contenido de un archivo del directorio compartida

def ObtenerParte( nombreArhivo , desde , cant):
    dirname = os.path.dirname(__file__)
    rutaArchivo = os.path.join(dirname, 'compartida', '', nombreArhivo)
    archivoPDF = open(rutaArchivo, 'rb')
    contenido = archivoPDF.read()
    archivoPDF.close()
    hasta = int(desde) + int(cant)
    parte = contenido[int(desde) : int(hasta)]
    return parte


# Retorna todo el contenido de un archivo del directorio temp

def ObtenerContenidoArchivo( nombreArhivo ):
    dirname = os.path.dirname(__file__)
    rutaArchivo = os.path.join(dirname, 'temp', '', nombreArhivo )
    archivoPDF = open(rutaArchivo, 'rb') 
    contenido = archivoPDF.read()
    archivoPDF.close()
    return contenido



