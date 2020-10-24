

class Equipo(object) :
    def __init__(self, ip):
        self.ip = ip
        self.archivos = []

class ParteArchivo:

	def __init__(self, idParte , ip , desde , hasta , finalizada):
			self.idParte =idParte
			self.ip = ip
			self.desde = desde
			self.hasta = hasta
			self.finalizada = finalizada
	
		
		
class Archivo :

    global contidArchivo
    def __init__(self, idArchivo , nombre , largo , md5):
        self.idArchivo = idArchivo
        self.md5 = md5
        self.nombre = nombre
        self.largo = largo
        self.ips = []
        self.peers = []
        self.partes = []
	
	
class Peer :
    def __init__(self,  ip, finalizado, ultimoAnuncio):
        self.ip = ip
        self.finalizado = finalizado
        self.ultimoAnuncio = ultimoAnuncio
        self.partes = []
		


