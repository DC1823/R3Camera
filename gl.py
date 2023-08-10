import struct
import libmat
import math
from objeto import Objeto
from textura import Textura
from collections import namedtuple

P2 = namedtuple("Punto", ["x", "y"])
P3 = namedtuple("Punto", ["x", "y", "z"])
Puntos=0
Lineas=1
Triangulos=2
Quads=3

def char(c):
    return struct.pack("=c", c.encode("ascii"))
def word(w):
    return struct.pack("=h", w)
def dword(d):
    return struct.pack("=l", d)

def color(r, g, b):
    return bytes([int(b * 255), int(g * 255), int(r * 255)])

class Modelo(object):
    def __init__(self, filename, trans=(0,0,0), rotar=(0,0,0), escala=(1,1,1)):
        modelo = Objeto(filename)
        self.caras = modelo.caras
        self.vertices = modelo.vertices
        self.tcrds = modelo.tcrds
        self.normales = modelo.normales
        self.trans=trans
        self.rotar=rotar
        self.escala=escala

    def cargartextura(self, filename):
        self.textura = Textura(filename)

class Renderer(object):
    def __init__(self,width,height):
        self.width = width
        self.height = height
        self.glClearC(0,0,0)
        self.glClear()
        self.glColor(1,1,1)
        self.fondo=None
        self.objetos=[]
        self.vShader = None
        self.fragShader = None
        self.primitiveType = Triangulos
        self.vBuffer=[]
        self.texturaact = None
        self.activemdmat = None
        self.glViewP(0,0,self.width,self.height)
        self.glCamara()
        self.glprojemat()
        self.luzdir = (0,0,0)
    
    def glLuzdir(self, x, y, z):
        self.luzdir = libmat.nrv((x,y,z))

    def gladdv(self, verts):
        for vert in verts:
            self.vBuffer.append(vert)
    
    def glPrimeas(self, tvers, ttcrd, tnormal):
        primitivos=[]
        for i in range(0, len(tvers), 3):
            verts=[]
            tcrds=[]
            normales=[]
            verts.append(tvers[i])
            verts.append(tvers[i+1])
            verts.append(tvers[i+2])
            tcrds.append(ttcrd[i])
            tcrds.append(ttcrd[i+1])
            tcrds.append(ttcrd[i+2])
            normales.append(tnormal[i])
            normales.append(tnormal[i+1])
            normales.append(tnormal[i+2])
            triangu=[verts,tcrds,normales]
            primitivos.append(triangu)
        return primitivos
    
    def glfondot(self, filename):
        self.fondo = Textura(filename)

    def cfondo(self):
        self.glClear()
        if self.fondo:
            for x in range(self.vpX, self.vpX+self.vpwidth+1):
                for y in range(self.vpY, self.vpY+self.vpheight+1):
                    i = (x - self.vpX)/self.vpwidth
                    j = (y - self.vpY)/self.vpheight
                    texcolor=self.fondo.obtener_color(i,j)
                    if texcolor:
                        self.glPunto(x,y,color(texcolor[0],texcolor[1],texcolor[2]))
    
    def glClearC(self, r,g,b):
        self.clearC=color(r,g,b)
    
    def glColor(self, r,g,b):
        self.ccolor = color(r,g,b)

    def glClear(self):
        self.pixeles = [[self.clearC for y in range(self.height)] for x in range(self.width)]
        self.zbuffer = [[float('inf') for y in range(self.height)] for x in range(self.width)]
    
    def glPunto(self, x, y, cl=None):
        if(0<=x<self.width) and (0<=y<self.height):
            self.pixeles[int(x)][int(y)] = cl or self.ccolor
        
    def gltrib(self, verts, tcrds, normals):
        A=verts[0]
        B=verts[1]
        C=verts[2]
        minx = round(min(A[0], B[0], C[0]))
        miny = round(min(A[1], B[1], C[1]))
        maxX = round(max(A[0], B[0], C[0]))
        maxY = round(max(A[1], B[1], C[1]))
        cA=(1,0,0)
        cB=(0,1,0)
        cC=(0,0,1)
        for x in range(minx, maxX+1):
            for y in range(miny, maxY+1):
                if(0<=x<self.width) and (0<=y<self.height):
                    P=(x,y)
                    bcrds=libmat.barcrd(A,B,C,P)
                    u, v, w = bcrds
                    if 0<=u<1 and 0<=v<1 and 0<=w<1:
                        z=A[2]*u+B[2]*v+C[2]*w
                        if z<self.zbuffer[x][y]:
                            self.zbuffer[x][y]=z
                            if self.fragShader != None:
                                pcolor=self.fragShader(textu=self.texturaact, tcrds=tcrds, normales=normals, dluz=self.luzdir, bcrds=bcrds, mdmat=self.activemdmat)
                                self.glPunto(x,y,color(pcolor[0],pcolor[1],pcolor[2]))
                            else:
                                self.glPunto(x,y,self.ccolor)
    def gltri(self, v,v2,v3,cl=None):
        self.glLinea(v,v2,cl or self.ccolor)
        self.glLinea(v2,v3,cl or self.ccolor)
        self.glLinea(v3,v,cl or self.ccolor)
    def glViewP(self, x,y,width,height):
        self.vpX=x
        self.vpY=y
        self.vpwidth=width
        self.vpheight=height
        self.vpmat=[[self.vpwidth/2, 0, 0, self.vpX+self.vpwidth/2], [0, self.vpheight/2, 0, self.vpY+self.vpheight/2], [0, 0, 0.5, 0.5], [0, 0, 0, 1]]
    def glCamara(self, trans=(0,0,0), rotar=(0,0,0)):
        self.cmat=self.glModelmat(trans, rotar)
        self.viewmat=libmat.matrizInversa(self.cmat)
    def glMirar(self, cpos=(0,0,0), epos=(0,0,0)):
        fw=libmat.nrv(libmat.sv(epos,cpos))
        rg=libmat.nrv(libmat.prodcruz((0,1,0),fw))
        up=libmat.nrv(libmat.prodcruz(fw,rg))
        self.cmat=[[rg[0],up[0],fw[0],cpos[0]],[rg[1],up[1],fw[1],cpos[1]],[rg[2],up[2],fw[2],cpos[2]],[0,0,0,1]]
        self.viewmat=libmat.matrizInversa(self.cmat)
    def glprojemat(self, fv=60, n=0.1, f=1000):
        aspR=self.vpwidth/self.vpheight
        tn=math.tan((fv*math.pi/180)/2)*n
        rf=tn*aspR
        self.projecmat=[[n/rf,0,0,0],[0,n/tn,0,0],[0,0,-(f+n)/(f-n),-(2*f*n)/(f-n)],[0,0,-1,0]]
    def glModelmat(self, trans=(0,0,0), rotar=(0,0,0), escala=(1,1,1)):
        transmat=[[1,0,0,trans[0]], [0,1,0,trans[1]],[0,0,1,trans[2]], [0,0,0,1]]
        escalamat=[[escala[0],0,0,0], [0,escala[1],0,0], [0,0,escala[2],0], [0,0,0,1]]
        rx = [[1,0,0,0], [0,math.cos(math.radians(rotar[0])),-math.sin(math.radians(rotar[0])),0],[0,math.sin(math.radians(rotar[0])),math.cos(math.radians(rotar[0])),0],[0,0,0,1]]
        ry = [[math.cos(math.radians(rotar[1])),0,math.sin(math.radians(rotar[1])),0],[0,1,0,0],[-math.sin(math.radians(rotar[1])),0,math.cos(math.radians(rotar[1])),0],[0,0,0,1]]
        rz = [[math.cos(math.radians(rotar[2])),-math.sin(math.radians(rotar[2])),0,0],[math.sin(math.radians(rotar[2])),math.cos(math.radians(rotar[2])),0,0],[0,0,1,0],[0,0,0,1]]
        rotarmat=libmat.nmult([rx,ry,rz])
        return libmat.nmult([transmat,rotarmat,escalamat])  
    
    def glLinea(self, v, v2, cl=None):
        x=int(v[0])
        y=int(v[1])
        x2=int(v2[0])
        y2=int(v2[1])
        dx=abs(x2-x)
        dy=abs(y1-y)
        paso=dx>dy
        if paso:
            x, y = y, x
            x2, y2 = y2, x2
        if x>x2:
            x, x2 = x2, x
            y, y2 = y2, y
        dx=abs(x2-x)
        dy=abs(y2-y)
        offset=0
        limit=0.5
        m=dy/dx
        y1=y
        for x in range(x, x2+1):
            if paso:
                self.glPunto(y,x,cl or self.ccolor)
            else:
                self.glPunto(x,y,cl or self.ccolor)
            offset+=m
            if offset>=limit:
                y+=1 if y1<y2 else -1
                limit+=1
    
    def glLoadM(self, filename, texname, trans=(0,0,0), rotar=(0,0,0), escala=(1,1,1)):
        modelo=Modelo(filename,trans,rotar,escala)
        if texname:
            modelo.cargartextura(texname)
        self.objetos.append(modelo)
    def glRender(self):
        transver=[]
        tcrds=[]
        normals=[]
        for modelo in self.objetos:
            self.texturaact=modelo.textura
            self.activemdmat=self.glModelmat(modelo.trans,modelo.rotar,modelo.escala)
            for cara in modelo.caras:
                vertc=len(cara)
                v=modelo.vertices[cara[0][0]-1]
                v2=modelo.vertices[cara[1][0]-1]
                v3=modelo.vertices[cara[2][0]-1]
                if vertc==4:
                    v4=modelo.vertices[cara[3][0]-1]
                
                if self.vShader:
                    v=self.vShader(v,mdmat=self.activemdmat,viewmat=self.viewmat,projecmat=self.projecmat,vpmat=self.vpmat)
                    v2=self.vShader(v2,mdmat=self.activemdmat,viewmat=self.viewmat,projecmat=self.projecmat,vpmat=self.vpmat)
                    v3=self.vShader(v3,mdmat=self.activemdmat,viewmat=self.viewmat,projecmat=self.projecmat,vpmat=self.vpmat)   
                    if vertc==4:
                        v4=self.vShader(v4,mdmat=self.activemdmat,viewmat=self.viewmat,projecmat=self.projecmat,vpmat=self.vpmat)
                transver.append(v)
                transver.append(v2)
                transver.append(v3)
                if vertc==4:
                    transver.append(v)
                    transver.append(v3)
                    transver.append(v4)
                
                vt=modelo.tcrds[cara[0][1]-1]
                vt2=modelo.tcrds[cara[1][1]-1]
                vt3=modelo.tcrds[cara[2][1]-1]
                if vertc==4:
                    vt4=modelo.tcrds[cara[3][1]-1]
                tcrds.append(vt)
                tcrds.append(vt2)
                tcrds.append(vt3)
                if vertc==4:
                    tcrds.append(vt)
                    tcrds.append(vt3)
                    tcrds.append(vt4)
                vn=modelo.normales[cara[0][2]-1]
                vn2=modelo.normales[cara[1][2]-1]
                vn3=modelo.normales[cara[2][2]-1]
                if vertc==4:
                    vn4=modelo.normales[cara[3][2]-1]
                normals.append(vn)
                normals.append(vn2)
                normals.append(vn3)
                if vertc==4:
                    normals.append(vn)
                    normals.append(vn3)
                    normals.append(vn4)
        primitivos=self.glPrimeas(transver,tcrds,normals)
        for primitivo in primitivos:
            self.gltrib(primitivo[0],primitivo[1],primitivo[2])

    def glFinish(self, filename):
        with open(filename, "wb") as file:
            file.write(char('B'))
            file.write(char('M'))
            file.write(dword(14 + 40 + self.width * self.height * 3))
            file.write(dword(0))
            file.write(dword(14 + 40))
            file.write(dword(40))
            file.write(dword(self.width))
            file.write(dword(self.height))
            file.write(word(1))
            file.write(word(24))
            file.write(dword(0))
            file.write(dword((self.width*self.height * 3)))
            file.write(dword(0))
            file.write(dword(0))
            file.write(dword(0))
            file.write(dword(0))
            for y in range(self.height):
                for x in range(self.width):
                    file.write(self.pixeles[x][y])
                    