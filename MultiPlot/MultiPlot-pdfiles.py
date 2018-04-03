# -*- coding: utf-8 -*-

# Plot several Hysteresis Loops

import matplotlib.pyplot as plt
import pandas as pd
from glob import glob

filelist = glob('*.pd')
filelist.sort()

f = figure('Hysteresis-Multi-Plot',figsize=(8,6))
ax = f.add_subplot(111)

for file in filelist:
	data = pd.read_pickle(file)
	
	E = data.E
	P = data.P
	
	split_container = file.split('_')
	
	legend_label = split_container[4]
	ax.plot(data.E, data.P*100,label=legend_label)
	
ax.set_xlabel('E (V/m)')
ax.set_ylabel('P (µC/cm2)')
ax.grid(linestyle='--')
ax.legend()