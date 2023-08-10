import struct
class Textura(object):
    def __init__(self, filename):
        with open(filename, "rb") as imagen:
            imagen.seek(10)
            header_s = struct.unpack("=l", imagen.read(4))[0]
            imagen.seek(18)
            self.ancho = struct.unpack("=l", imagen.read(4))[0]
            self.alto = struct.unpack("=l", imagen.read(4))[0]
            imagen.seek(header_s)
            self.pixeles = []
            for y in range(self.alto):
                pixeles_fila = []
                for x in range(self.ancho):
                    b = ord(imagen.read(1))/255
                    g = ord(imagen.read(1))/255
                    r = ord(imagen.read(1))/255
                    pixeles_fila.append([r, g, b])
                self.pixeles.append(pixeles_fila)
    
    def obtener_color(self, tx, ty):
        if 0 <= tx < 1 and 0 <= ty < 1:
            return self.pixeles[int(ty * self.alto)][int(tx * self.ancho)]
        else: 
            return None