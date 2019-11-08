# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 11:06:09 2019

@author: DG
"""

import numpy as np
from matplotlib import pyplot as plt
import os

carpeta='C:/Users/DG/Documents/GitHub/labo7/scripts/iman/'

indice=[]
for archivo in os.listdir(carpeta):
    if archivo.endswith(".txt"):
        indice.append(archivo)

nro=3

corrientes,ts=np.loadtxt(carpeta+indice[nro])
ts=np.array(ts[1:])/1.74
corrientes=np.array(corrientes[1:])

def promediar(t,n=10):
    tprom=[]
    ttot=len(t)
    for i in range(ttot):
        down=max(0,i-n)
        upper=min(ttot,i+n)
        tprom.append(np.mean(t[down:upper]))
    return np.array(tprom)

prom=15
tprom=promediar(ts,prom)  
corrientes=promediar(corrientes,10)  
#%%
plt.clf()
plt.close()
plt.figure(num=0, figsize=(10, 6), dpi=80, facecolor='w', edgecolor='k')
plt.plot(corrientes)
plt.xlabel('N')
plt.ylabel('Corriente (A)')
plt.figure(num=1, figsize=(10, 6), dpi=80, facecolor='w', edgecolor='k')
plt.plot(np.array(ts))
plt.xlabel('N')
plt.ylabel('\u0394 t')
plt.figure(num=2, figsize=(10, 6), dpi=80, facecolor='w', edgecolor='k')
plt.plot(tprom)
plt.xlabel('N')
plt.ylabel('\u0394 t promediado cada'+str(prom)+' descargas')

