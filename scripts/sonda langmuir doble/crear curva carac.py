# -*- coding: utf-8 -*-
"""
Created on Wed Jun  5 10:43:02 2019

@author: DG
"""

import numpy as np
from matplotlib import pyplot as plt
import os

def filtrar(data):
    def butter_lowpass(cutoff, fs, order=5):
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return b, a
    
    
    def butter_lowpass_filter(data, cutoff, fs, order=5):
        b, a = butter_lowpass(cutoff, fs, order=order)
    #    y = lfilter(b, a, data)
        y = filtfilt(b, a, data)
        return y
    
    
    # Filter requirements.
    order = 5
    fs = len(data)/(tiempo[-1]-tiempo[0])       # sample rate, Hz
    fs=1/(tiempo[1]-tiempo[0])
    cutoff =7*10**4  # desired cutoff frequency of the filter, Hz
    cutoff=4*10**5
    b, a = butter_lowpass(cutoff, fs, order)
    
    y = butter_lowpass_filter(data, cutoff, fs, order)
    return(y)

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

def curva_por_carpeta(carpeta_base):
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
            bobina=Csv(carpeta,2*j,es_bobina=True)
            bobina.sacar_lineal()
            pico_bobina=bobina.encontrar_picos(0.8,distancia_entre_picos=100,valle=True)[0]
            tiempo0=bobina.x[pico_bobina]
            altura_pico_bobina=bobina.y[pico_bobina]
            bobina.x-=tiempo0
            R.x-=tiempo0
            data=-R.y/altura_pico_bobina
            descarga_media.append(altura_pico_bobina)
            tiempo=R.x
            #y=filtrar(data)
            #promedio entre 4 y 5 us
            t1=4*10**-6
            t2=5*10**-6
            pos1=posicion_x(tiempo,t1)
            pos2=posicion_x(tiempo,t2)
            corr=np.mean(data[pos1:pos2])
            corrientes.append(corr)
            corrientes_esta_carpeta.append(corr)
            #restar caida sobre resistencia
            V=float(i)-np.mean(R.y[pos1:pos2])
            tensiones.append(V)
            tensiones_esta_carpeta.append(V)
        corriente_media.append(np.mean(corrientes_esta_carpeta)*10*np.mean(descarga_media)/180)        
        tension_media.append(np.mean(tensiones_esta_carpeta))        
        error_corriente_media.append(np.std(corrientes_esta_carpeta)*10*np.mean(descarga_media)/180)
        error_tension_media.append(np.std(tensiones_esta_carpeta))#/np.sqrt(len(corrientes_esta_carpeta)))
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
carpeta_base1='C:/Users/ferchi/Desktop/github labo 6/labo6/mediciones/5-15/'
carpeta_base1='C:/Users/DG/Documents/GitHub/labo7/mediciones/8-28/'
#falta filtrar 6-3

tc,c,tensiones,corrientes,error_tensiones,error_corrientes=curva_por_carpeta(carpeta_base1)#,sacar_outliers=True)
#t2,c2,tm2,cm2,et2,ec2=curva_por_carpeta(carpeta_base2)#,sacar_outliers=True)
#t3,c3,tm3,cm3,et3,ec3=curva_por_carpeta(carpeta_base3)#,sacar_outliers=True)
#t4,c4,tm4,cm4,et4,ec4=curva_por_carpeta(carpeta_base4)#,sacar_outliers=True)
#%%
tensiones,corrientes,error_tensiones,error_corrientes=np.loadtxt('curva carac 800V final.txt',delimiter='\t')


#%%
#ploteo todas las mediciones

#tensiones=np.concatenate([t1,t2,t3,t4])
#corrientes=np.concatenate([np.array(c1),c2,c3,c4])*568

A2=np.array([tensiones,corrientes])
A2=np.transpose(A2)
A2=A2[A2[:,0].argsort()]
A2=np.transpose(A2)#dificil de creer pero funciona
tensiones,corrientes=A2

#corrientes-=y_dado_x(tensiones,corrientes,0)

plt.plot(tensiones,-corrientes*1000,'g*',label='Mediciones del 15/5')#para que de rasonable dividi por 2... no encuentro el motivo de que sea necesario
plt.ylabel('Corriente (mA)')
plt.xlabel('Tensión (V)')
plt.grid()
#np.savetxt('curva carac 1000V con t entre 4 y 5 polarizada bien.txt',[tensiones,corrientes,error_corrientes], delimiter='\t')
#%%
#ploteo mediciones promediadas
#tensiones=np.concatenate([tm1,tm2,tm3,tm4])
#corrientes=np.concatenate([np.array(cm1),cm2,cm3,cm4])*568#ver de dividir por 2 a c1...
#error_tensiones=np.concatenate([et1,et2,et3,et4])
#error_corrientes=np.concatenate([ec1,ec2,ec3,ec4])*568

A2=np.array([tensiones,corrientes,error_corrientes,error_tensiones])
A2=np.transpose(A2)
A2=A2[A2[:,0].argsort()]
A2=np.transpose(A2)#dificil de creer pero funciona
tensiones,corrientes,error_corrientes,error_tensiones=A2

#tensiones=np.array(tensiones)
#tensiones=tensiones*-1
#corrientes*=corrientes[24]

plt.plot(tensiones[:-1],corrientes[:-1]*1000,'g*',label='Mediciones del 15/5')#para que de rasonable dividi por 2... no encuentro el motivo de que sea necesario
plt.errorbar(tensiones[:-1],corrientes[:-1]*1000,error_corrientes[1:]*1000,linestyle = 'None')

plt.ylabel('Corriente (mA)')
plt.xlabel('Tensión (V)')
plt.grid()

