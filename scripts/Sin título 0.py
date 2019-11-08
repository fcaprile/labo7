# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 20:00:54 2019

@author: ferchi
"""

import numpy as np
from matplotlib import pyplot as plt
import numpy as np
import os
from numpy import genfromtxt
from scipy.integrate import cumtrapz as integrar
from scipy.signal import butter, filtfilt
from scipy.optimize import curve_fit

carpeta=r'C:/Users/ferchi/Desktop/github/labo7/scripts/sonda langmuir doble\\'.replace('\\','/')[:-1]

dist,t,et=np.loadtxt(carpeta+'tiempos de vuelo.txt')
plt.plot(dist,t)

