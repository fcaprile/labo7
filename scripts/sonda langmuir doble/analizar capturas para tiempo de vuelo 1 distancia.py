# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 10:52:27 2019

@author: DG
"""

# -*- coding: utf-8 -*-
"""
Created on Mon May 13 12:47:22 2019

@author: DG
"""

# -*- coding: utf-8 -*-
"""
Created on Mon May 13 00:05:48 2019

@author: ferchi
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 15:35:12 2019

@author: Admin
"""
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import os
from numpy import genfromtxt
from scipy.integrate import cumtrapz as integrar
from scipy.signal import butter, filtfilt
from scipy.optimize import curve_fit
#plt.clf()
#plt.close()

def posicion_x(x,valorx):
    posicion_x=np.where(abs(x-valorx)==min(abs(x-valorx)))[0][0]
    return posicion_x

def y_dado_x(x,y,valorx):
    pos=posicion_x(x,valorx)
    return y[pos]


#nuevo descubrimiento: hay que multiplicar por 10... por la punta

class Data:
        
    def sacar_offset(self,n):
        self.y-=np.mean(self.y[:n])
    
    def filtrar_por_vecinos(self,n_vecinos=15):
        yfilt=np.zeros(self.long)
        for i in range(self.long):
            down=max(0,i-n_vecinos)
            upper=min(self.long,i+n_vecinos)
            yfilt[i]=np.mean(self.y[down:upper])
        self.y=np.array(yfilt)

    def calibrar_bobina(self,num_vecinos=20):
#        self.y=self.filtrar_por_vecinos(num_vecinos)
        self.y=integrar(self.y,self.x)
        self.y=np.append(self.y,0)
        A=2.2*10**9
#        B=0.911 #esto quedo de cuando usabamos la R=0.07, en realidad era causado por la inductancia de la R asi que no lo hago más
        self.y*=A
#        self.x=self.x[1:]*B
        self.y*=-1
        self.x+=-7.48*10**-7
        
    def encontrar_picos(self,porcentaje_altura,distancia_entre_picos=1,valle=False,plotear=False):
        if valle==False:            
            picos=detect_peaks(self.y,max(self.y)*porcentaje_altura,distancia_entre_picos,show=plotear)
        if valle==True:            
            picos=detect_peaks(self.y,min(self.y)*porcentaje_altura,distancia_entre_picos,valley=valle,show=plotear)
        return picos
    
    def sacar_lineal(self):
        recta=np.linspace(self.y[0],self.y[-1],self.long)
        self.y-=recta
    
    def filtrar(self,cutoff,order=5):        
        def butter_lowpass(cutoff,fs,order):
            nyq = 0.5 * fs
            normal_cutoff = cutoff / nyq
            b, a = butter(order, normal_cutoff, btype='low', analog=False)
            return b, a
                
        def butter_lowpass_filter(data, cutoff, fs, order=5):
            b, a = butter_lowpass(cutoff, fs, order=order)
        #    y = lfilter(b, a, data)
            y = filtfilt(b, a, data)
            return y

        fs = self.long/(self.x[-1]-self.x[0])       # sample rate, Hz
#        fs=1/(self.x[-1]-self.x[0])
        self.y = butter_lowpass_filter(self.y, cutoff, fs, order)
    
    def butcher(self,tinf,tsup,leeway=1):
        down=posicion_x(self.x,tinf)
        upper=posicion_x(self.x,tsup)
        maximum=max(abs(self.y[down:upper]))*leeway
        for i in range():
            self.y[i]=max(self.y[i],-maximum)
            self.y[i]=min(self.y[i],maximum)
   
    def butcher_noice(self,tinf,tsup,leeway=1,reduction=1):
        down=posicion_x(self.x,tinf)
        upper=posicion_x(self.x,tsup)
        maximum=max(abs(self.y[down:upper]))*leeway
        mask=abs(self.y)>maximum
        for i in range(self.long):
            if mask[i]==True:
                self.y[i]=self.y[i-1]*reduction

     
class Csv(Data):
    def __init__ (self,carpeta,numero_de_archivo,es_bobina=False,punta=1):
        indice=[]
        for archivo in os.listdir(carpeta):
            if archivo.endswith(".csv"):
                indice.append(archivo)
        nombre=indice[numero_de_archivo]        
        self.values=genfromtxt(carpeta+nombre, delimiter=',')
        self.values=self.values[1:,:]
        self.x=np.array(self.values[:,0])
        self.y=np.array(self.values[:,1])
        self.y*=punta
        self.long=len(self.y)
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
    
    
#%%
plt.clf()
plt.close()


def tiempo_vuelo_1_carpeta(carpeta,tinf,tsup,fc,order,reduction=1,punta=10,n_vecinos=20):
    print(carpeta)
    indice=[]
    for archivo in os.listdir(carpeta):
        if archivo.endswith(".csv"):
            indice.append(archivo)
    #curvasresistencias=np.zeros([int(len(indice)/2)])
    jmax=len(indice)/2
    vuelos=[]
    for j in range(int(jmax)):
    #    plt.clf()
    #    plt.close()
#            print(indice[2*j])
        bobina=Csv(carpeta,2*j,es_bobina=True)
        resistencia=Csv(carpeta,2*j+1,punta=punta)
        #resistencia.y-=ruido
        resistencia.filtrar_por_vecinos(n_vecinos)
        bobina.sacar_lineal()
        pico_bobina=bobina.encontrar_picos(0.8,distancia_entre_picos=100,valle=True)[0]
        altura_pico_bobina=bobina.y[pico_bobina]
        tiempo0=bobina.x[pico_bobina]
        bobina.x-=tiempo0
        resistencia.x-=tiempo0
        
        resistencia.butcher_noice(tinf,tsup,1,reduction)
        resistencia.filtrar(fc,order)
        bobina.plot(fig_num=1,tamañox=14,tamañoy=6,color='b-')
        resistencia.plot(fig_num=1,escala=100,tamañox=14,tamañoy=10,color='r-')
        
        bottom=posicion_x(resistencia.x,tinf)
        upper=posicion_x(resistencia.x,tsup)
        
        pico_resistencia=detect_peaks(resistencia.y[bottom:upper],0.8*max(resistencia.y[bottom:upper]),10)
        if len(pico_resistencia)>0:
            pico_resistencia=pico_resistencia[0]+bottom
    #    print(resistencia.x[pico_resistencia])
#            if len(pico_resistencia)>0:
            vuelos.append(resistencia.x[pico_resistencia])
    return distancias,vuelo_medio,desviación
#%%
#carpeta='C:/Users/ferchi/Desktop/github/labo7/mediciones/8-23/166/'
carpeta_madre='C:/Users/ferchi/Desktop/github/labo7/mediciones/8-23/'
carpeta_madre='C:/Users/DG/Documents/GitHub/labo7/mediciones/8-23/166/'

tinf=2*10**-6
tsup=6*10**-6
  
distancias,vuelo_medio,desviación=tiempo_vuelo(carpeta_madre,tinf,tsup,fc=7*10**5,order=4,reduction=0.7 ,punta=10,n_vecinos=50)
'''
#funcan: 
fc=7*10**5,order=4,reduction=0.7                da 6.12638808829e-08
fc=10*10**5,order=4,reduction=0.5               da 4.03203424136e-08
fc=7*10**5,order=4,reduction=1                  da 4.04528670502e-08
fc=10*10**5,order=4,reduction=1                 da 2.74604102974e-08
fc=10*10**5,order=4,reduction=1 sin butcher     da 5.61846018492e-08
fc=4*10**5,order=2,reduction=1 sin butcher      da 5.85702501558e-08
fc=4*10**5,order=2,reduction=0.7                da 1.85755454758e-08
fc=20*10**5,order=2,reduction=0.5               da 1.56990215733e-08
fc=7*10**5,order=2,reduction=0.8 feo ajuste     da 3.113408864136538e-08
fc=2*10**5,order=2,reduction=0.5                da 1.2561231684271965e-08
fc=2*10**5,order=5,reduction=0.5                da 1.646924319122793e-08
'''

distancias=np.array(distancias)
vuelo_medio=np.array(vuelo_medio)
desviación=np.array(desviación)

f=lambda  x,A,y0:A*x+y0
parametros_optimizados, matriz_covarianza = curve_fit(f,distancias,vuelo_medio,sigma = desviación+10**-8,absolute_sigma=True) 

print(parametros_optimizados[0])   
plt.rcParams['font.size']=20#tamaño de fuente
plt.figure(num=0, figsize=(9,6), dpi=80, facecolor='w', edgecolor='k')
plt.subplots_adjust(left=0.14, bottom=0.13, right=0.98, top=0.98, wspace=None, hspace=None)
plt.plot(distancias-min(distancias),f(distancias, *parametros_optimizados)*10**6, 'g-', label = 'Ajuste')
plt.plot(distancias-min(distancias),vuelo_medio*10**6,'b*')
plt.errorbar(distancias-min(distancias),vuelo_medio*10**6,desviación*10**6,linestyle = 'None')
plt.grid(True) # Para que quede en hoja cuadriculada
plt.xlabel('Distancia (mm)')
plt.ylabel('Tiempo de vuelo (us)')
plt.legend(loc = 'best') 

#print(np.mean(vuelo),'+-',np.std(vuelo)/np.mean(vuelo))
