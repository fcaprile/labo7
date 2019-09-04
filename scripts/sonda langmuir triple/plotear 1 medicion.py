# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 14:49:38 2019

@author: DG
"""
carpeta='C:/Users/DG/Documents/GitHub/labo7/mediciones/9-4/triple/'
indice=[]
for archivo in os.listdir(carpeta):
    if archivo.endswith(".csv"):
        indice.append(archivo)
jmax=len(indice)
j=0
flotante=Csv(carpeta,2*j)
corriente=Csv(carpeta,2*j+1,punta=10)
flotante.sacar_lineal()

plt.plot(flotante.x*10**6,flotante.y*10)
plt.plot(corriente.x*10**6,corriente.y)
plt.ylabel('Tensión (V)')
plt.xlabel('tiempo (us)')
plt.grid()
