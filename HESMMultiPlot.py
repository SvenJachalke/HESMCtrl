#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Plot of (multiple) pandas data pickles measured with HESMCtrl
"""

# imports ---------------------------------------------------------------------
from matplotlib.style import use
from matplotlib.pyplot import figure, show
import tubafcdpy as tubafcd
from glob import glob
import pandas as pd
from HESMCtrl.Evaluation import get_PR

# functions -------------------------------------------------------------------
def get_tubaf_colorarray(n):
	"""
	return array of n colors based on tubafcolormap
	"""
	from numpy import linspace, array
	colormap = tubafcd.tubafcmap()
	c = linspace(0,1,len(filelist))
	colors = []
	for i in c:
		colors.append(colormap(i))
	colors = array(colors)
	return colors

def get_PR(data):
	"""
	calculates remanent polarization and error
	"""
	from numpy import mean
	PR = mean(abs(data.iloc[(data['E']-0).abs().argsort()[:20]].P))		#mean of 20 values close to E=0
	PR_error = mean(abs(data.iloc[(data['E']-0).abs().argsort()[:20]].P_error))
	
	return PR, PR_error

# read files ------------------------------------------------------------------
use('science')

filelist = glob('*.pd')
filelist.sort()

try:
	sample_name = filelist[0].strip('.pd')
	colors = get_tubaf_colorarray(len(filelist))
	
	result = pd.DataFrame()
	
	raw = figure('RawData',figsize=(8,6))
	axraw = raw.add_subplot(111)
	
	hyst = figure('P-E-Hysteresis',figsize=(8,6))
	ax1 = hyst.add_subplot(111)
	
	i = 0
	for file in filelist:
		# extract Voltage ampltiude
		Vamp = float(file.split('_')[4].split('-')[0].strip('AV'))
		print('----------------------------------')
		print('File: %s'%file)
		print('Vamp: %.2f V'%Vamp)
		
		# read and calc data
		data = pd.read_pickle(file)
		
		# get PR
		PR, PR_error = get_PR(data)
		print('PR: (%f +- %f) mC/m2'%(abs(PR)*1000,abs(PR_error)*1000))
	#	print('Vdiff: %f V'%(data.Vdiff.max()))
		
		# save result
		series = {'Vamp':Vamp,'PR':PR,'PR_error':PR_error}
		df = pd.DataFrame({i:series}).T
		result = result.append(df)	
			
		# plot
		axraw.plot(data.time*1000,data.I*1000,label=r'%.1f V'%(Vamp),color=colors[i])
	#	axraw.plot(data.time*1000,data.I_Loss*1000,color=colors[i],linestyle='--',label='Loss')
		ax1.plot(data.E/1e6,data.P*1000,label=r'%.1f V'%(Vamp),color=colors[i])
		i = i+1
	
	# save result file ------------------------------------------------------------
	result.to_csv(sample_name+'_PRs.txt',sep='\t',columns=['Vamp','PR','PR_error'])
	
	# plot formatting -------------------------------------------------------------
	axraw.set_xlabel(r'$t$ (ms)')
	axraw.set_ylabel(r'$I$ (mA)')
	#axraw.set_yscale('symlog')
	
	axraw.grid()
	axraw.legend(title=r'$V_{\mathrm{Amp}}$')
	
	ax1.set_xlabel(r'$E$ (\si{\mega\volt\per\meter})')
	ax1.set_ylabel(r'$P$ (\si{\milli\coulomb\per\square\meter})') 
	
	ax1.axhline(0,linestyle='--',color='k')
	ax1.axvline(0,linestyle='--',color='k')
	
	ax1.grid()
	ax1.legend(loc=4,title=r'$V_{\mathrm{Amp}}$')
	
	raw.tight_layout()
	raw.savefig(sample_name+'_raw.pdf')
	
	hyst.tight_layout()
	hyst.savefig(sample_name+'_P-E.pdf')
	
	show()

except IndexError:
	print('No *.pd files found!')