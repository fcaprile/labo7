# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 14:48:49 2019

@author: DG
"""

import numpy as np
from matplotlib import pyplot as plt
import os
from numpy import genfromtxt
from scipy.integrate import cumtrapz as integrar
from scipy.signal import butter, filtfilt
from scipy.optimize import curve_fit

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
        
    def encontrar_picos(self,porcentaje_altura,distancia_entre_picos=10,valle=False,plotear=False):
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
        for i in range(self.long):
            self.y[i]=max(self.y[i],-maximum)
            self.y[i]=min(self.y[i],maximum)
   
    def butcher_noice(self,tinf,tsup,leeway=1,reduction=1):
        down=posicion_x(self.x,tinf)
        upper=posicion_x(self.x,tsup)
        maximum=max(abs(self.y[down:upper]))*leeway
        mask=abs(self.y)>maximum
        for i in range(self.long):
            if mask[i]==True:
                self.y[i]=self.y[i-1]

     
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

def promediar_vectores(matriz): #formato: filas de vectores
    columnas=len(matriz[0,:])
    filas=len(matriz[:,0])
    prom=np.zeros(columnas)
    para_prom=np.zeros(filas,columnas)
    for j in range(columnas):
        prom[j]=np.mean(para_prom[:,j])

def posicion_x(x,valorx):
    posicion_x=np.where(abs(x-valorx)==min(abs(x-valorx)))[0][0]
    return posicion_x

def y_dado_x(x,y,valorx):
    pos=posicion_x(x,valorx)
    return y[pos]

def ajustar_entre(f,x,y,ey,xinf,xsup,escalax=1,escalay=1,color='g',label='Ajuste',plot=True):
    a=posicion_x(x,xinf)
    b=posicion_x(x,xsup)    
    y=y[a:b]
    x=x[a:b]
    ey=ey[a:b]
    popt, pcov = curve_fit(f,x,y,sigma =ey)
    if plot==True:
        xx=np.linspace(min(x),max(x),1000)                    
        plt.plot(xx*escalax,f(xx, *popt)*escalay, color=color, label = label)#los popt son los valores de las variables fiteadas que usara la funcion f                      
    return popt,pcov

def vector_entre(x,xinf,xsup):
    a=posicion_x(x,xinf)
    b=posicion_x(x,xsup)    
    return x[a:b]    

