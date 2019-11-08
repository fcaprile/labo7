# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 14:40:52 2019

@author: DG
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 14:42:32 2019

@author: DG
"""
import sys
import keyboard
import numpy as np
from numpy import genfromtxt
from scipy.integrate import cumtrapz as integrar
from scipy.signal import butter, filtfilt
from scipy.optimize import curve_fit

from matplotlib import pyplot as plt
import pyvisa
import numpy as np
import time
import os
rm=pyvisa.ResourceManager()
carpeta='C:/Users/Admin/Desktop/L6 Caprile Rosenberg/python/mediciones/4-3/'
carpeta='C:/Users/DG/Documents/GitHub/labo6_2/mediciones/8-23/'
#carpeta=path+day+'/'
#key=rm.list_resources_info().keys()[0]
dicti=rm.list_resources_info()#'USB0::0x0699::0x0363'*?                                                                                                                                                                                                        
resource_name=dicti.values()
osci=rm.open_resource(dicti['USB0::0x0699::0x03A1::C012822::INSTR'][3])
        
#print(osci.query('*IDN?'))
def setup():
    osci.write('DAT:ENC RPB')
    osci.write('DAT:WID 1')
    try:
        xze,xin,yze1,ymu1,yoff1=osci.query_ascii_values('WFMPRE:XZE?;XIN?;CH1:YZE?;YMU?;YOFF?',separator=';')
    except:
        print('Se corto la comunicación, cerrandola:')
        osci.close()
    osci.write('DAT:SOU CH1' )
    return xze,xin,yze1,ymu1,yoff1
    
def medir_trigger(t0):
    osci.write('ACQuire:STATE RUN')
    osci.write('ACQuire:STOPAfter SEQuence')
    try:
        r=osci.query('ACQuire:STATE?')
    except:
        r='1\n'
    while r=='1\n':
        try:
            r=osci.query('ACQuire:STATE?')
            time.sleep(0.05)
        except:
            r='1\n'
    elapsed = time.time() - t0
    t = time.time()
    data1=osci.query_binary_values('CURV?', datatype='B',container=np.array)
    return data1,elapsed,t

def medir(ch):
    xze,xin,yze1,ymu1,yoff1=osci.query_ascii_values('WFMPRE:XZE?;XIN?;CH1:YZE?;YMU?;YOFF?',separator=';')
    yze2,ymu2,yoff2=osci.query_ascii_values('WFMPRE:CH2:YZE?;YMU?;YOFF?',separator=';')
    osci.write('DAT:ENC RPB')
    osci.write('DAT:WID 1')
    osci.write('DAT:SOU CH{}'.format(ch) )
    data=osci.query_binary_values('CURV?', datatype='B',container=np.array)
    if ch==1:
        data=(data-yoff1)*ymu1+yze1
    if ch==2:
        data=(data-yoff2)*ymu2+yze2
        
    tiempo = xze + np.arange(len(data)) * xin

    return tiempo,data

    
#%%
N=30000
disparos=0
fallidos=0
mediciones=np.zeros([N,2500])
parametros=np.zeros([5,N])
xze,xin,yze1,ymu1,yoff1=setup()
ts=[]
print('A MEDIR!!')

for i in range(N):
    if i==0:
        data1,elapsed,t0=medir_trigger(0)
    else:
        data1,elapsed,t0=medir_trigger(t0)        
#    print(elapsed)
    ts.append(elapsed)
    disparos+=1
    if elapsed>2.5 and i>0:
        fallidos+=np.floor(elapsed/1.7)-1
#    print('Hubo '+str(disparos)+' disparos,'+str(fallidos)+' fallos',end="\r")
    if i%100==0 and i!=0:
        print('Se realizaron',disparos,'mediciones,',fallidos,'salieron mal')
    
    mediciones[i,:]=data1
    
    #poder parar programa
    try:
        if keyboard.is_pressed('Esc'):
            print("\nyou pressed Esc, so exiting...")
            sys.exit(0)
    except:
        break
ts=np.array(ts)
print(np.mean(ts[1:]))
corrientes=np.zeros(disparos)
tiempo = xze + np.arange(2500) * xin

for i in range(disparos):
    y=mediciones[i,:]
    y=(y-yoff1)*ymu1+yze1 
    y-=y[0]
    y=integrar(y,tiempo)
    y=np.append(y,0)
#    recta=np.linspace(y[0],y[-20],2500)
#    y-=recta
    A=2.2*10**9
#        B=0.911 #esto quedo de cuando usabamos la R=0.07, en realidad era causado por la inductancia de la R asi que no lo hago más
    y*=A
#    plt.plot(y)
#        self.x=self.x[1:]*B
#    y*=-1
    picos=detect_peaks(y,max(y)*0.7,20,valley=False,show=False)
    if len(picos)>0:
        corrientes[i]=y[picos[0]]
#    mediciones[:,i,:]=tiempo,data1
'''
plt.plot(corrientes)
print(np.mean(corrientes))
'''
carpeta='C:/Users/DG/Documents/GitHub/labo7/scripts/iman/'
np.savetxt(carpeta+str(disparos)+' descargas-'+str(time.localtime()[0])+'-'+str(time.localtime()[1])+'-'+str(time.localtime()[2])+'-'+str(time.localtime()[3])+'-'+str(time.localtime()[4])+'.txt',[corrientes,ts], fmt='%.18g', delimiter='\t', newline=os.linesep)

print('Hubo',disparos,'disparos y',fallidos,'descargas fallidas')
print('La efectividad fue del',"%.1f" %(disparos/(disparos+fallidos)*100),'%')
#usar para medir ambos canales 1 sola vez

#t,ch1=medir(1)
#t,ch2=medir(2)
#plt.plot(t,ch1)
#plt.plot(t,ch2*1000)
#tiempo,data1=medir(1)
#tiempo,data2=medir(2)
