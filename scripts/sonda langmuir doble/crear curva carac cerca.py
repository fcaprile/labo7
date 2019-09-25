# -*- coding: utf-8 -*-
"""
Created on Wed Jun  5 10:43:02 2019

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

def curva_por_carpeta(carpeta_base,tinf,tsup,filtrar=False):
    indice_carpetas=[]
    for carpeta in os.listdir(carpeta_base):
        indice_carpetas.append(carpeta)
#    print(indice_carpetas)
    corrientes=[]
    tensiones=[]
    corriente_media=[]
    tension_media=[]
    error_corriente_media=[]
    error_tension_media=[]
    for i in indice_carpetas:
        corrientes_esta_carpeta=[]
        tensiones_esta_carpeta=[]
        carpeta=carpeta_base+i+'/'
#        print(carpeta)
        indice=[]
        for archivo in os.listdir(carpeta):
            if archivo.endswith(".csv"):
                indice.append(archivo)
#        print(indice)
        descarga_media=[]
        for j in range(int(len(indice)/2)):   
            R=Csv(carpeta,2*j+1)
#            if j==0:
#                plt.plot(R.x,R.y)
            bobina=Csv(carpeta,2*j,es_bobina=True)
            bobina.sacar_lineal()
            pico_bobina=bobina.encontrar_picos(0.8,distancia_entre_picos=100,valle=True)[0]
            tiempo0=bobina.x[pico_bobina]
            altura_pico_bobina=bobina.y[pico_bobina]
            bobina.x-=tiempo0
            R.x-=tiempo0
            data=-R.y/altura_pico_bobina
#            print(altura_pico_bobina)
            descarga_media.append(altura_pico_bobina)
            tiempo=R.x
            if filtrar==True:
                R.butcher(tinf,tsup,1)
                R.filtrar_por_vecinos(200)
                R.filtrar(fc,order)
            #promedio entre 4 y 5 us
#            t1=4*10**-6
#            t2=6*10**-6
            pos1=posicion_x(tiempo,tinf)
            pos2=posicion_x(tiempo,tsup)
            corr=np.mean(data[pos1:pos2])
            corrientes.append(corr)
            corrientes_esta_carpeta.append(corr)
            #restar caida sobre resistencia
            V=float(i)#-np.mean(R.y[pos1:pos2])
            tensiones.append(V)
            tensiones_esta_carpeta.append(V)
#        print(np.mean(descarga_media))
        corriente_media.append(np.mean(corrientes_esta_carpeta)*np.mean(descarga_media)/5)        
        tension_media.append(np.mean(tensiones_esta_carpeta))        
        error_corriente_media.append(np.std(corrientes_esta_carpeta)*np.mean(descarga_media)/5/np.sqrt(len(corrientes_esta_carpeta)))
        error_tension_media.append(np.std(tensiones_esta_carpeta)/np.sqrt(len(corrientes_esta_carpeta)))
        print('Carpeta',i,'analizada!')
    
#    tensiones=[]
#    for i in indice_carpetas:
#        tensiones.append(float(i))    
    
    return tensiones,corrientes,tension_media,corriente_media,error_tension_media,error_corriente_media

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

#%%
#analizo
carpeta_base1='C:/Users/ferchi/Desktop/GitHub/labo7/mediciones/8-28/'
carpeta_base1='C:/Users/DG/Documents/GitHub/labo7/mediciones/9-20/'
carpeta_base2='C:/Users/DG/Documents/GitHub/labo7/mediciones/9-25/'
#falta filtrar 6-3
fc=0.7*10**5
order=4

tc,c,tm1,cm1,et1,ec1=curva_por_carpeta(carpeta_base1,0.5*10**-6,1*10**-6,filtrar=False)#,sacar_outliers=True)
t2,c2,tm2,cm2,et2,ec2=curva_por_carpeta(carpeta_base2,0.5*10**-6,1*10**-6,filtrar=False)#,sacar_outliers=True)
#t3,c3,tm3,cm3,et3,ec3=curva_por_carpeta(carpeta_base3)#,sacar_outliers=True)
#t4,c4,tm4,cm4,et4,ec4=curva_por_carpeta(carpeta_base4)#,sacar_outliers=True)
'''
np.savetxt('curva carac cerca 1000V con t entre 0,5 y 1.txt',[tensiones,corrientes,error_corrientes], delimiter='\t')
tensiones,corrientes,error_tensiones,error_corrientes=np.loadtxt('curva carac 800V final.txt',delimiter='\t')
'''
#%%
#ploteo mediciones promediadas
tensiones=np.concatenate([tm1,tm2])
corrientes=np.concatenate([cm1,cm2])
error_tensiones=np.concatenate([et1,et2])
error_corrientes=np.concatenate([ec1,ec2])

A2=np.array([tensiones,corrientes,error_corrientes,error_tensiones])
A2=np.transpose(A2)
A2=A2[A2[:,0].argsort()]
A2=np.transpose(A2)#dificil de creer pero funciona
tensiones,corrientes,error_corrientes,error_tensiones=A2

#tensiones=np.array(tensiones)
#tensiones=tensiones*-1
#corrientes*=corrientes[24]

plt.plot(tensiones[:-1],-corrientes[:-1],'g*',label='Mediciones del 15/5')#para que de rasonable dividi por 2... no encuentro el motivo de que sea necesario
plt.errorbar(tensiones[:-1],-corrientes[:-1],error_corrientes[1:],linestyle = 'None')

plt.ylabel('Corriente (A)')
plt.xlabel('Tensión (V)')
plt.grid()

