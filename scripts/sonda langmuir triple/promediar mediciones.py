# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 15:03:14 2019

@author: DG
"""
import math as m

carpeta='C:/Users/DG/Documents/GitHub/labo7/mediciones/9-4/triple/'
indice=[]
for archivo in os.listdir(carpeta):
    if archivo.endswith(".csv"):
        indice.append(archivo)
jmax=len(indice)

DeltaV=40

calcular_Te=lambda T,v1,v2: abs(1-(2*np.exp()))

for j in range(jmax):
    flotante=Csv(carpeta,2*j)
    corriente=Csv(carpeta,2*j+1,punta=10)
    flotante.sacar_lineal()
    
    
