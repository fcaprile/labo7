# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 14:49:38 2019

@author: DG
"""
import numpy as np
import os
from matplotlib import pyplot as plt

carpeta='C:/Users/DG/Documents/GitHub/labo7/mediciones/9-6/50Kohm/0/'
carpeta='C:/Users/DG/Documents/GitHub/labo7/mediciones/9-11/electrodo 3 tapado/corriente y flotante/'
indice=[]
for archivo in os.listdir(carpeta):
    if archivo.endswith(".csv"):
        indice.append(archivo)
jmax=len(indice)//2
for j in range(jmax):
    flotante=Csv(carpeta,2*j,punta=10)
    corriente=Csv(carpeta,2*j+1,punta=10)
#    flotante.sacar_lineal()
    plt.plot(flotante.x*10**6,flotante.y*6/np.log(2))
    plt.plot(corriente.x*10**6,corriente.y*10)
plt.ylabel('Tensión (V)')
plt.xlabel('tiempo (us)')
plt.grid()


