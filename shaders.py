import libmat
import math

def vShader(verx, **kwarg):
    mdmat=kwarg["mdmat"]
    viewmat=kwarg["viewmat"]
    projecmat=kwarg["projecmat"]
    vpmat=kwarg["vpmat"]
    vt=[verx[0],verx[1],verx[2],1]
    matrs=libmat.nmult([vpmat, projecmat, viewmat, mdmat])
    vt=libmat.mvmult(matrs, vt)
    vt=[vt[0]/vt[3],vt[1]/vt[3],vt[2]/vt[3],vt[3]/vt[3]]
    return vt
