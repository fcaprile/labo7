# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 10:50:40 2019

@author: Admin
"""
import numpy as np
import os
import time
#path='C:/Users/Admin/Desktop/labo6_Rosenberg_Caprile/mediciones/'
#path='C:/Users/Admin/Desktop/labo6_Rosenberg_Caprile/mediciones/'
#day=str(time.localtime()[1])+'-'+str(time.localtime()[2])
carpeta='C:/Users/DG/Documents/GitHub/labo7/mediciones/iman/config 2/filtrar/'
voltajes=np.array([19,21,25,27])
for i in voltajes:
    os.mkdir(carpeta+str(i)+'/')


#path='C:/Users/ferchi/Desktop/github labo 6/labo6/mediciones/mediciones removidas por ser diferentes/'
#for i in tensiones:
#    os.mkdir(path+str(i)+'/')
