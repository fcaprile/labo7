# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 11:12:30 2019

@author: DG
"""

# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 20:43:36 2019
@author: ferchi
"""
import numpy as np
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit

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
    popt, pcov = curve_fit(f,x,y)#,sigma =ey)#,absolute_sigma=True)
    if plot==True:
        xx=np.linspace(min(x),max(x),1000)                    
        plt.plot(xx*escalax,f(xx, *popt)*escalay, color=color, label = label)#los popt son los valores de las variables fiteadas que usara la funcion f                      
    return popt,pcov

def vector_entre(x,xinf,xsup):
    a=posicion_x(x,xinf)
    b=posicion_x(x,xsup)    
    return x[a:b]    
#%%
#calculo temperatura electronica con funcion

#V_min, V_max son los valores entre los cuales se hara el calculo log
def Temp_elec_asim(tensiones,corrientes,error_corrientes,lin_neg,lin_pos,sat_neg,sat_pos,V_min,V_max,plot=True):

    f=lambda x,A,y0:A*x+y0
    #ajuste saturacion
    p_sat_neg,cov_sat_neg=ajustar_entre(f,tensiones,corrientes,error_corrientes,tensiones[0],sat_neg,escalay=1000,plot=False)
    p_sat_pos,cov_sat_pos=ajustar_entre(f,tensiones,corrientes,error_corrientes,sat_pos,tensiones[-1],escalay=1000,plot=False)
    #ajuste baja amplitud
    p_lin,cov_lin=ajustar_entre(f,tensiones,corrientes,error_corrientes,lin_neg,lin_pos,escalay=1000,plot=False)
        
    #analisis
#    Ii0_pos=p_sat_pos[1]
#    Ii0_neg=p_sat_neg[1]
    #Ii0=(abs(Ii0_pos)+abs(Ii0_neg))/2
    #
    #Te=1/2/p_lin[0]*Ii0
    #
    #print('Te =',Te)
    a=posicion_x(tensiones,V_min)
    b=posicion_x(tensiones,V_max)
    t_lin=tensiones[a:b]
    Ie1=abs(f(t_lin,*p_sat_pos)-corrientes[a:b])
    Ie2=abs(f(t_lin,*p_sat_neg)-corrientes[a:b])
    
    #propagacion de error:
    def error_lineal(xa,cov):
        error = np.sqrt(cov[1,1]+xa**2*cov[0,0]+2*xa*cov[0,1])
        return(error)
    
    Error_Ie1=np.sqrt(error_lineal(t_lin,cov_sat_pos)**2+error_corrientes[a:b]**2)
    Error_Ie2=np.sqrt(error_lineal(t_lin,cov_sat_neg)**2+error_corrientes[a:b]**2)
#    cov_Ie1_Ie2=np.cov([Ie1,Ie2])
    
    Error_log=np.sqrt((Error_Ie1/Ie1)**2+(Error_Ie2/Ie2)**2-2/Ie1/Ie2*np.cov([Ie1,Ie2])[0,1])

    par_log,cov_log=curve_fit(f,t_lin,np.log(Ie1/Ie2),sigma=Error_log)
    Teb=1/par_log[0]
    Error_Teb=np.sqrt(cov_log[0,0])/par_log[0]**2
    print('Contemplando la asimetria, Te=',"%.2f" %Teb,'+-',"%.2f" %Error_Teb)
    
    
    if plot==True:
        plt.rcParams['font.size']=20#tamaño de fuente
        plt.figure(num=0, figsize=(9,6), dpi=80, facecolor='w', edgecolor='k')
        plt.subplots_adjust(left=0.14, bottom=0.13, right=0.98, top=0.98, wspace=None, hspace=None)
        plt.plot(tensiones,corrientes*1000,'b*')
        plt.errorbar(tensiones,corrientes*1000,error_corrientes*1000,linestyle = 'None')
        plt.ylabel('Corriente (mA)')
        plt.xlabel('Tensión (V)')
        plt.grid()

        x_plot=np.linspace(tensiones[0],sat_neg*0.2,100)
        plt.plot(x_plot,f(x_plot,*p_sat_neg)*1000,'r',label='Linea de saturación')
        x_plot=np.linspace(sat_pos*0.2,tensiones[-1],100)
        plt.plot(x_plot,f(x_plot,*p_sat_pos)*1000,'r')
        
        x_plot=np.linspace(lin_neg*1.8,lin_pos*1.8,100)
        plt.plot(x_plot,f(x_plot,*p_lin)*1000,'g',label='Lineal')

        plt.figure(num=1, figsize=(9,6), dpi=80, facecolor='w', edgecolor='k')
        plt.subplots_adjust(left=0.14, bottom=0.13, right=0.98, top=0.98, wspace=None, hspace=None)
        plt.plot(t_lin,np.log(Ie1/Ie2),'b*',label='log(Ie1/Ie2)')
        plt.errorbar(t_lin,np.log(Ie1/Ie2),Error_log,linestyle = 'None')
        plt.plot(t_lin,f(t_lin,*par_log))
        plt.ylabel('log( Ie1 / Ie2 )')
        plt.xlabel('Tensión (V)')
        plt.grid()

#%%
def analisis_simetrico(tensiones,corrientes,error_corrientes,lin_neg,lin_pos,sat_min,sat_max,rama_pos=True,plot=True):
    f=lambda x,A,y0:A*x+y0
    par_lin,cov_lin=ajustar_entre(f,tensiones,corrientes,error_corrientes,lin_neg,lin_pos,plot=False)
    par_sat,cov_sat=ajustar_entre(f,tensiones,corrientes,error_corrientes,sat_min,sat_max,plot=False)
    Error_Te=np.sqrt(cov_lin[0,0]*par_sat[0]**2/(2*par_lin[0]**2)**2+cov_sat[1,1]/(2*par_lin[0])**2)
    print('i0=',par_sat[1])
    Te=1/2/par_lin[0]*par_sat[1]
    print('A orden simetrico, Te=',Te,'+-',Error_Te)
    
    if plot==True:
        plt.rcParams['font.size']=20#tamaño de fuente
        plt.figure(num=0, figsize=(9,6), dpi=80, facecolor='w', edgecolor='k')
        plt.plot(tensiones,corrientes,'b*',label='Con imán')
        plt.errorbar(tensiones,corrientes,error_corrientes,linestyle = 'None')
        if rama_pos==True:
            x_plot=np.linspace(0,tensiones[-1],100)
        else:
            x_plot=np.linspace(tensiones[1],0,100)
            
        plt.plot(x_plot,f(x_plot,*par_sat),'r')
    #        x_plot=np.linspace(sat,tensiones[-1],100)
    #        plt.plot(x_plot,f(x_plot,*par_sat)*1000,'g',label='Puntos usadoss para el ejuste')
        
        x_plot=np.linspace(lin_neg,lin_pos,100)
        plt.plot(x_plot,f(x_plot,*par_lin),'g')
        
        
#%%
tensiones,corrientes,error_corrientes=np.loadtxt('curva carac 1000V con t entre 1 y 3 config 2.txt',delimiter='\t')
#analisis_simetrico_rama_pos(tensiones,corrientes,error_corrientes,0,10,30)

#%%  Corro la funcion para analizar
       
#tensiones,corrientes,error_corrientes=np.loadtxt('C:/Users/ferchi/Desktop/github labo 6/labo6/resultados/curva característica sonda doble Langmuir/txt/curva carac 800V entre 4 y 4.7.txt',delimiter='\t')
#corrientes/=1000
#error_corrientes/=1000

#sacar outliers
#tensiones2=np.delete(tensiones,0)#si es .np
#corrientes2=np.delete(corrientes,0)#si es .np
#error_corrientes2=np.delete(error_corrientes,0)#si es .np
#tensiones=np.delete(tensiones,7)#si es .np
#corrientes=np.delete(corrientes,7)#si es .np
#error_corrientes=np.delete(error_corrientes,7)#si es .np
#corrientes=-corrientes   

corrientes-=y_dado_x(tensiones,corrientes,0)    
analisis_simetrico(tensiones,corrientes,error_corrientes,0,26,30,60,rama_pos=True)    
#analisis_simetrico(tensiones,corrientes,error_corrientes,-20,20,-60,-15,rama_pos=False)    
plt.subplots_adjust(left=0.19, bottom=0.13, right=0.98, top=0.98, wspace=None, hspace=None)
plt.ylabel('Corriente (mA)')
plt.xlabel('Tensión (V)')
plt.grid()
 