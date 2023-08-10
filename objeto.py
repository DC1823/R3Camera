class Objeto(object):
    def __init__(self, filename):
        with open(filename, "r") as arch:
            self.archivo = arch.read().splitlines()
        self.vertices = []
        self.tcrds = []
        self.normales = []
        self.caras = []
        for archi in self.archivo:
            try:
                prefi, val = archi.split(" ", 1)
            except:
                continue
            if prefi == "v":
                self.vertices.append(list(map(float,list(filter(None,val.split(" "))))))
            elif prefi == "vt":
                self.tcrds.append(list(map(float,list(filter(None,val.split(" "))))))
            elif prefi == "vn":
                self.normales.append(list(map(float, list(filter(None,val.split(" "))))))
            elif prefi == "f":
                self.caras.append([list(map(int, list(filter(None, vr.split("/"))))) for vr in list(filter(None,val.split(" ")))])