import math

def nmult(mts):
    resu = [[1, 0, 0, 0],[0, 1, 0, 0],[0, 0, 1 ,0],[0, 0, 0, 1]]
    for mat in mts:
        resu = mmult(resu, mat)
    return resu

def mmult(m,m2):
    resu = [[0, 0, 0, 0] for i in range(4)]
    for i in range(4):
        for j in range(4):
            for k in range(4):
                resu[i][j] += m[i][k] * m2[k][j]
    return resu

def mvmult(m,v):
    resu = [0, 0, 0, 0]
    for i in range(4):
        for j in range(4):
            resu[i] += m[i][j] * v[j]
    return resu

def barcrd(A,B,C,P):
    arePCB = (B[1]-C[1])*(P[0]-C[0])+(C[0]-B[0])*(P[1]-C[1])
    areACP = (C[1]-A[1])*(P[0]-C[0])+(A[0]-C[0])*(P[1]-C[1])
    areABC = (B[1]-C[1])*(A[0]-C[0])+(C[0]-B[0])*(A[1]-C[1])
    try:
        return [arePCB/areABC, areACP/areABC, 1-arePCB/areABC-areACP/areABC]
    except:
        return -1,-1,-1

#Obtener la Submatriz de una Matriz
def submatriz(m, fila, colu):
    return [fila[:colu] + fila[colu + 1:] for fila in (m[:fila] + m[fila + 1:])]

#Obtener el Cofactor de una Matriz
def matrizCofact(m, fila, colu):
    return (-1) ** (fila + colu) * matrizDete(submatriz(m, fila, colu))

#Obtener el Determinante de una Matriz
def matrizDete(m):
    numFilas = len(m)
    if(numFilas==1):
        return m[0][0]
    if(numFilas==2):
        return m[0][0]*m[1][1]-m[0][1]*m[1][0]
    deter=0
    for i in range(numFilas):
        deter+=m[0][i]*matrizCofact(m,0,i)
    return deter

#Obtener la Matriz Transpuesta
def transpuesta(m):
    return [[m[j][i] for j in range(len(m))] for i in range(len(m[0]))]

#Obtener la Matriz Inversa
def matrizInversa(m):
    deter = matrizDete(m)
    if(deter==0):
        raise ValueError("La matriz no tiene inversa")
    lm = len(m)
    admat= transpuesta([[matrizCofact(m,i,j) for j in range(lm)] for i in range(lm)])
    return [[admat[i][j]/deter for j in range(lm)] for i in range(lm)]

def sv(v,v2):
    return (v[0]-v2[0],v[1]-v2[1],v[2]-v2[2])

def nrv(v):
    vectl = list(v)
    magn = math.sqrt(sum(x**2 for x in vectl))
    if magn == 0:
        raise ValueError("El vector no tiene magnitud")
    normal = tuple([x/magn for x in vectl])
    return normal

def prodcruz(v,v2):
    x = v[1]*v2[2]-v[2]*v2[1]
    y = v[2]*v2[0]-v[0]*v2[2]
    z = v[0]*v2[1]-v[1]*v2[0]
    return (x,y,z)

def prodpunto(v,v2):
    return sum([x*y for x,y in zip(list(v),list(v2))])

def negativev(t):
    return (-t[0],-t[1],-t[2])