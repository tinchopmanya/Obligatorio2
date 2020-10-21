

class Equipo(object) :



    def __init__(self, ip):
        self.ip = ip
        self.archivos = []

class Archivo :

    global contidArchivo
    def __init__(self, idArchivo , nombre , largo , md5):
        self.idArchivo = idArchivo
        self.md5 = md5
        self.nombre = nombre
        self.largo = largo
        self.ips = []


