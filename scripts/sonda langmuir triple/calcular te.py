# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 13:02:15 2019

@author: DG
"""
import numpy as np
import os
from scipy.optimize import minimize as minim
from matplotlib import pyplot as plt

def calcular_Te(v2,v3,te0):
    g=lambda te: abs(2*np.exp(-v3/te)-1-np.exp(-v2/te))
    return minim(g,te0)['x']

v2=55
v3=100
te0=6
r=calcular_Te(v2,v3,te0)
print(r,v3/np.log(2))

carpeta='C:/Users/DG/Documents/GitHub/labo7/mediciones/9-6/50Kohm/0/'
carpeta='C:/Users/DG/Documents/GitHub/labo7/mediciones/9-11/destapado/0/'
indice=[]
for archivo in os.listdir(carpeta):
    if archivo.endswith(".csv"):
        indice.append(archivo)
jmax=len(indice)//2
#for j in range(jmax):
j=0
flotante=Csv(carpeta,2*j,punta=10)
corriente=Csv(carpeta,2*j+1,punta=10)
imax=len(flotante.x)
tes=[]
for v3 in flotante.y:
    tes.append(calcular_Te(55.3,v3))
    
plt.plot(tes)