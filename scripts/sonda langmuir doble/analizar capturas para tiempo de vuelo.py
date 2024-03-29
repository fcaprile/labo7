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
from uncertainties import ufloat
from scipy.stats import chi2
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

def plot(x,y,fig_num=0,escala=1,color='b-'):
    plt.figure(num= fig_num , figsize=(14, 10), dpi=80, facecolor='w', edgecolor='k')        
    plt.plot(x,y*escala,color)
    plt.grid(True) # Para que quede en hoja cuadriculada
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Tension (V)')
    
    
#%%
plt.clf()
plt.close()


def tiempo_vuelo(carpeta_madre,tinf,tsup,fc,order,reduction=1,punta=10,n_vecinos=20,invert=False):
    carpetas=[]
    for archivo in os.listdir(carpeta_madre):
            carpetas.append(archivo)
    imax=len(carpetas)
    vuelo_medio=[]
    desviación=[]
    distancias=[]
    for i in range(imax):
        distancias.append(float(carpetas[i]))
        carpeta=carpeta_madre+carpetas[i]+'/'
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
#            resistencia.filtrar_por_vecinos(n_vecinos)
            bobina.sacar_lineal()
            pico_bobina=bobina.encontrar_picos(0.8,distancia_entre_picos=200,valle=True)[0]
            altura_pico_bobina=bobina.y[pico_bobina]
            tiempo0=bobina.x[pico_bobina]
            bobina.x-=tiempo0
            resistencia.x-=tiempo0
            if invert==True:
                resistencia.y*=-1
            
            resistencia.butcher(tinf,tsup,1)
            resistencia.filtrar(fc,order)
#            bobina.plot(fig_num=1,tamañox=14,tamañoy=6,color='b-')
#            resistencia.plot(fig_num=1,escala=100,tamañox=14,tamañoy=10,color='r-')
            
            bottom=posicion_x(resistencia.x,tinf)
            upper=posicion_x(resistencia.x,tsup)
            
            pico_resistencia=detect_peaks(resistencia.y,0.8*max(resistencia.y),10)
            if len(pico_resistencia)>0:
                pos_pico_resistencia=pico_resistencia[0]
        #    print(resistencia.x[pico_resistencia])
#            if len(pico_resistencia)>0:
                vuelos.append(resistencia.x[pos_pico_resistencia])
        vuelo_medio.append(np.mean(vuelos))
        desviación.append(np.std(vuelos)/(np.sqrt(jmax)-1))
    return distancias,vuelo_medio,desviación
#%%
#carpeta='C:/Users/ferchi/Desktop/github/labo7/mediciones/8-23/166/'
carpeta_madre='C:/Users/ferchi/Desktop/github/labo7/mediciones/8-23,28 tiempo vuelo limpias/'
carpeta_madre2='C:/Users/ferchi/Desktop/github/labo7/mediciones/8-30 tiempo vuelo/'
carpeta_madre='C:/Users/DG/Documents/GitHub/labo7/mediciones/8-23,28 tiempo vuelo limpias/'
carpeta_madre2='C:/Users/DG/Documents/GitHub/labo7/mediciones/8-30 tiempo vuelo/'
carpeta_madre='C:/Users/DG/Documents/GitHub/labo7/mediciones/tiempo vuelo sin outliers/8-23,28/'
carpeta_madre2='C:/Users/DG/Documents/GitHub/labo7/mediciones/tiempo vuelo sin outliers/8-30/'
carpeta_madre2='C:/Users/DG/Documents/GitHub/labo7/mediciones/9-4/vuelo/'

carpeta_madre='C:/Users/ferchi/Desktop/github/labo7/mediciones/tiempo vuelo sin outliers/8-23,28/'
carpeta_madre2='C:/Users/ferchi/Desktop/github/labo7/mediciones/9-4/vuelo/'


tinf=2*10**-6
tsup=6*10**-6
  
distancias_dia_1,vuelo_medio_dia_1,desviación_dia_1=tiempo_vuelo(carpeta_madre,tinf,tsup,fc=0.7*10**5,order=4,reduction=0.8,punta=10,n_vecinos=50)
'''
np.savetxt('tiempos de vuelo.txt',[distancias,vuelo_medio,desviación], delimiter='\t')
'''

distancias_dia_1=np.array(distancias_dia_1)
vuelo_medio_dia_1=np.array(vuelo_medio_dia_1)
desviación_dia_1=np.array(desviación_dia_1)

distancias_dia_2,vuelo_medio_dia_2,desviación_dia_2=tiempo_vuelo(carpeta_madre2,2*tinf,4*tinf,fc=0.7*10**5,order=4,reduction=0.8,punta=10,n_vecinos=50,invert=False)
#%%
distancias2=np.array(distancias_dia_2)
vuelo_medio2=np.array(vuelo_medio_dia_2)#-2.95*10**-6
desviación2=np.array(desviación_dia_2)

distancias=np.concatenate((distancias_dia_1,distancias2), axis = 0)
vuelo_medio=np.concatenate((vuelo_medio_dia_1,vuelo_medio2), axis = 0)
desviación=np.concatenate((desviación_dia_1,desviación2), axis = 0)
#distancias=np.delete(distancias,4)
#vuelo_medio=np.delete(vuelo_medio,4)
#desviación=np.delete(desviación,4)


'''
distancias,vuelo_medio,desviación=np.loadtxt('tiempos de vuelo.txt', delimiter='\t')
'''
distancias/=1000
f=lambda  x,A,y0:A*x+y0
parametros_optimizados, matriz_covarianza = curve_fit(f,distancias,vuelo_medio,sigma = desviación,absolute_sigma=False)#yo lo tenia hecho con true, con el cual da +-0.2

t_vuelo=ufloat(parametros_optimizados[0],np.sqrt(matriz_covarianza[0,0]))
vel=1/t_vuelo
print(vel)

def test_chi2(f,x,y,ey,parametros_ajustados=[]):
    '''
    f es la fucnion con la que ajustaste, x,y lo que mediste y ey el error con el que lo mediste 
    (si no te pusiste a caracterizar el error lee abajo la parte de desviacion standard)
    parametros_ajustados son los valores que te da el ajuste
    '''
    n=len(parametros_ajustados)
    N=len(y)
    if n==0: #si la f no viene de un ajuste
        t=np.sum(((y-f(x))/ey)**2) #t es el nombre teorico que se le da al resultado de esa cuenta, no tiene nada que ver con el tiempo
    else:
        t=np.sum(((y-f(x,*parametros_ajustados))/ey)**2)
        #para ser rigurosos, esto funciona si f es lineal en los parámetros (no la definiste como algo que depende de A**2), pero bue
    
    p_valor=1-chi2.cdf(t,N-n)
    return p_valor,t    
    


print(test_chi2(f,distancias,vuelo_medio,abs(desviación),parametros_optimizados))                                                     
#print(parametros_optimizados[0],'+-',np.sqrt(matriz_covarianza[0,0]))   
#print(parametros_optimizados[1],'+-',np.sqrt(matriz_covarianza[1,1]))   
plt.rcParams['font.size']=20#tamaño de fuente
plt.figure(num=0, figsize=(9,6), dpi=80, facecolor='w', edgecolor='k')
plt.subplots_adjust(left=0.14, bottom=0.13, right=0.98, top=0.98, wspace=None, hspace=None)
plt.plot(distancias-min(distancias),f(distancias, *parametros_optimizados)*10**6, 'g-')
plt.plot(distancias-min(distancias),vuelo_medio*10**6,'b*')
plt.errorbar(distancias-min(distancias),vuelo_medio*10**6,desviación*10**6,linestyle = 'None')
plt.grid(True) # Para que quede en hoja cuadriculada
plt.xlabel('Distancia (mm)')
plt.ylabel('Tiempo de vuelo (us)')
plt.legend(loc = 'upper left') 

#print(np.mean(vuelo),'+-',np.std(vuelo)/np.mean(vuelo))
#plt.plot(distancias2-min(distancias),vuelo_medio2*10**6-3,'b*')
