# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 10:44:59 2019

@author: DG
"""
import numpy as np
Ii0=0.23
Te=4.6*1.6*10**-19
mn=1.67*10**-27
mf=19*mn
mc=12*mn
e=1.6*10**-19

r=0.0005
h=0.005
A=2*np.pi*r*h+np.pi*r**2

v=np.sqrt(Te/mc)/3+2*np.sqrt(Te/mf)/3
ne=Ii0/0.61/e/A/v

print(ne)