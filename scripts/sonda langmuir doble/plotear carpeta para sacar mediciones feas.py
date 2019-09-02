# -*- coding: utf-8 -*-
"""
Created on Mon Sep  2 18:13:25 2019

@author: ferchi
"""

# -*- coding: utf-8 -*-
"""
Created on Wed May 29 22:11:27 2019

@author: ferchi
"""

import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import os
from numpy import genfromtxt
from scipy.integrate import cumtrapz as integrar
#plt.clf()
#plt.close()

#carpeta='C:/Users/Admin/Desktop/labo6_Rosenberg_Caprile/mediciones/4-10/'




class Data:        
    def sacar_offset(self,n):
        suma=0
        for valor in self.y[:n]:
            suma+=valor
        suma/=n
        self.y=self.y-suma
    
    def filtrar_por_vecinos(self,n_vecinos=15):
        yfilt=[]
        for i in range(len(self.y)):
            if i>n_vecinos and i<len(self.y)-n_vecinos:
                suma=0
                for j in range(n_vecinos):
                    suma+=self.y[i+j]+self.y[i-j]
                yfilt.append(suma/(2*n_vecinos+1))
            if i<n_vecinos:
                suma=0
                for j in range(i):
                    suma+=self.y[i+j]+self.y[i-j]
                yfilt.append(suma/(2*i+1))
            if i>len(self.y)-n_vecinos:
                suma=0
                for j in range(len(self.y)-i):
                    suma+=self.y[i+j]+self.y[i-j]
                yfilt.append(suma/(2*(len(self.y)-i)+1))            
        yfilt.append(0)
        yfilt.append(0)
        self.y=np.array(yfilt)

    def calibrar_bobina(self,num_vecinos=20):
#        self.y=self.filtrar_por_vecinos(num_vecinos)
        self.y=integrar(self.y,self.x)
        A=9.72*10**8
        B=0.911
        self.y*=A
        self.x=self.x[1:]*B
        self.y*=-1
        self.x-=0.7*10**-6
        
    def encontrar_picos(self,porcentaje_altura,distancia_entre_picos=1,valle=False,plotear=False):
        if valle==False:            
            picos=detect_peaks(self.y,max(self.y)*porcentaje_altura,distancia_entre_picos,show=plotear)
        if valle==True:            
            picos=detect_peaks(self.y,min(self.y)*porcentaje_altura,distancia_entre_picos,valley=valle,show=plotear)
        return picos
    def sacar_lineal(self):
        recta=np.linspace(self.y[0],self.y[-1],len(self.y))
        self.y-=recta
   

     
class Csv(Data):
    def __init__ (self,carpeta,numero_de_archivo,es_bobina=False):
        indice=[]
        for archivo in os.listdir(carpeta):
            if archivo.endswith(".csv"):
                indice.append(archivo)
        nombre=indice[numero_de_archivo]        
        self.values=genfromtxt(carpeta+nombre, delimiter=',')
        self.values=self.values[1:,:]
        self.x=np.array(self.values[:,0])
        self.y=np.array(self.values[:,1])
        if es_bobina==True:
            super().sacar_offset(50)
            super().calibrar_bobina()
            
    def plot(self,fig_num=0,escala=1,tamañox=14,tamañoy=10,color='b-'):
        plt.figure(num= fig_num , figsize=(tamañox, tamañoy), dpi=80, facecolor='w', edgecolor='k')        
        plt.plot(self.x,self.y*escala,color)
        plt.grid(True) # Para que quede en hoja cuadriculada
        plt.xlabel('Tiempo (s)')
        plt.ylabel('Tension (V)')

def plot(x,y,fig_num=0,escala=1,color='b-'):
    plt.figure(num= fig_num , figsize=(14, 10), dpi=80, facecolor='w', edgecolor='k')        
    plt.plot(x,y*escala,color)
    plt.grid(True) # Para que quede en hoja cuadriculada
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Tension (V)')

def posicion_x(x,valorx):
    posicion_x=np.where(abs(x-valorx)==min(abs(x-valorx)))[0][0]
    return posicion_x

#%%
plt.clf()
plt.close()

carpeta_base='C:/Users/ferchi/Desktop/GitHub/labo7/mediciones/curva carac 8-28 limpias/'
indice_carpetas=[]
for archivo in os.listdir(carpeta_base):
    indice_carpetas.append(archivo)

'''
num=-1
'''

num+=1
volt=26
carpeta=carpeta_base+str(volt)+'/'
#carpeta=carpeta_base+indice_carpetas[num]+'/'
#print(indice_carpetas[num])
indice=[]
for archivo in os.listdir(carpeta):
    if archivo.endswith(".csv"):
        indice.append(archivo)

corrientes=[]
alturas_picos=[]
datas=np.zeros([len(indice)//2,4000])
tiempos=np.zeros([len(indice)//2,4000])
for j in range(len(indice)//2):
    R=Csv(carpeta,2*j+1)
    bobina=Csv(carpeta,2*j,es_bobina=True)
    bobina.sacar_lineal()
    pico_bobina=bobina.encontrar_picos(0.8,distancia_entre_picos=100,valle=True)[0]
    tiempo0=bobina.x[pico_bobina]
    altura_pico_bobina=bobina.y[pico_bobina]
    bobina.x-=tiempo0
    R.x-=tiempo0
    data=-R.y/altura_pico_bobina
    tiempo=R.x
    #promedio entre 3 y 5 us
    t1=3.5*10**-6
    t2=4.7*10**-6
    pos1=posicion_x(tiempo,t1)
    pos2=posicion_x(tiempo,t2)
    valor=np.mean(data[pos1:pos2])
#    print('medicion',j,'dio',valor)
#    plt.plot(tiempo,data)
    corrientes.append(valor)
    alturas_picos.append(altura_pico_bobina)
    datas[j,:]=data
    tiempos[j,:]=tiempo
plt.rcParams['font.size']=15#tamaño de fuente
plt.figure(num=0, figsize=(14,10), dpi=80, facecolor='w', edgecolor='k')
plt.subplots_adjust(left=0.14, bottom=0.13, right=0.98, top=0.98, wspace=None, hspace=None)

altura_media_pico_bobina=np.mean(np.array(alturas_picos))    
#altura_media_pico_bobina=-568
for i in range(len(datas[:,0])):
    plt.plot(tiempos[i,:]*10**6,-datas[i,:]*altura_media_pico_bobina,label=str(indice[2*i]))
    plt.legend(loc = 'best') 
media=np.mean(corrientes)*altura_media_pico_bobina
print(media)
corrientes=np.array(corrientes)
for i in range(len(corrientes)):
    if abs(corrientes[i]*altura_media_pico_bobina-media)>abs(media*0.4):
        print('medicion',indice[2*i],'esta lejos')
#plt.hist(corrientes)
