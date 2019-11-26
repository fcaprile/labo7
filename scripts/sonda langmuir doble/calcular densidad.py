# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 10:44:59 2019

@author: DG
"""
import numpy as np
from uncertainties import ufloat


#Ii0=ufloat(0.087)

'''
valores para cerca sin iman
Ii0=ufloat(0.2325,0.0025**0.5) 
Te=ufloat(4.6*e,1*e)
'''

'''
valores para 3J (L6)
Ii0=ufloat(0.0006,0.000002) 
Te=ufloat(4.0*e,1.3*e)
'''

'''
valores para 4.5J (L6)
Ii0=ufloat(0.002,0.0001) 
Te=ufloat(6*e,1*e)
'''

'''
valores para config 2
Ii0=ufloat(0.1627,0.0054**0.5) 
Te=ufloat(5.6*e,2.5*e)
'''


'''
valores para config 3
Ii0=ufloat(0.107,0.0024**0.5) 
Te=ufloat(6*e,3*e)
'''


e=1.6*10**-19
mn=1.67*10**-27
mf=19*mn
mc=12*mn

r=0.0005
h=0.005
A=2*np.pi*r*h+np.pi*r**2

v=(Te/mc)**0.5/3+2*(Te/mf)**0.5/3
ne=Ii0/0.61/e/A/v

print(ne)