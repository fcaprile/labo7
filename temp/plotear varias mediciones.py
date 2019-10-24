# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 14:49:38 2019

@author: DG
"""
import numpy as np
import os
from matplotlib import pyplot as plt

carpeta=r'C:\Users\ferchi\Desktop\temp\\'.replace('\\','/')[:-1]
indice=[]
for archivo in os.listdir(carpeta):
    if archivo.endswith(".csv"):
        indice.append(archivo)
jmax=len(indice)//2
for j in range(jmax):
    flotante=Csv(carpeta,2*j+1,punta=10)
    corriente=Csv(carpeta,2*j,punta=1)
    corriente.y-=1
    pos_pico=corriente.encontrar_picos(0.8,valle=True)[0]
    alt_pico=corriente.y[pos_pico]
    t0=corriente.x[pos_pico]
    flotante.x-=t0
    corriente.x-=t0
#    flotante.y/=-alt_pico
#    flotante.filtrar(40*10**5,order=3)
    flotante.filtrar_por_vecinos(5)
#    flotante.y-=flotante.y[0]
#    flotante.sacar_lineal()
#    flotante.y-=25
    plt.plot(flotante.x*10**6,flotante.y/np.log(2)/10)
#    plt.plot(corriente.x*10**6,corriente.y*10)
plt.ylabel('Tensión (V)')
plt.ylabel('Te (eV)')
plt.xlabel('tiempo (us)')
plt.grid()


