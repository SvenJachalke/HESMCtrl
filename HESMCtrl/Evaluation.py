#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Evaluate data to reconstruct ferroelectric hysteresis
"""


def calculate_hysteresis(data,ms,filename):
	"""
	Reconstruct hysteresis shape from measured date (time, Vset, Vref)
	and measurement settings dict
	"""
	
	from numpy import pi, mean
	from scipy.integrate import cumtrapz
	import pandas as pd
	
	# prepare results
	result = pd.Series({'Vamp':ms['amp']})
	result['frequency'] = ms['freq']
	result['thickness'] = ms['thickness']
	result['area'] = ms['area']
	result['areaerr'] = ms['areaerr']
	
	# calculate difference voltage betwen Vset and Vref
	data['Vdiff'] = data.Vset - data.Vref
	
	#calculate displacement current 
	data['I'] = data.Vref / ms['rref']

	#calc and center electric field from Vset and sample thickness d (+save)
	data['E'] = data.Vdiff / ms['thickness']
	E_bias = abs(max(data.E))-abs(min(data.E))
	print('E_bias: %f MV/m ; %f V'%(E_bias/1e6,E_bias*ms['thickness']))
	if ms['correct_Ebias'] == True:
		if E_bias < 0:
			data['E'] = data.E + abs(E_bias)
		else:
			data['E'] = data.E - abs(E_bias)
	result['ebias'] = E_bias
	
	# correct loss current before removing offset	
	if ms['correct_LossI'] == True:
		try:
			data['I_Loss'] = data.Vref * 2 * pi * ms['freq'] * ms['cap'] * ms['tand']
			data['I'] = data.I - data.I_Loss
			print('ILoss/IP: %e'%(mean(data.I_Loss)/mean(data.I)))
		except ValueError:
			print('Some values missing! (Capacity, tan d ?)')
	
	# calc offset current from mean of 2 periods
	if ms['custom_curr_offs'] == 0:
		start_index = 100
		increment = data.time[1]-data.time[0]
		steps = int(1./ ms['freq'] / increment * 2)
		offset = mean(data.I[start_index:steps+start_index])
	else:
		try:
			offset = ms['custom_curr_offs']
		except ValueError:
			print('current offset value missing!')
		
	# remove offset current
	data['I'] = data.I - offset

	# charge by integrating current
	data['Q'] = cumtrapz(data.I,data.time,initial=0)

	# polarization
	data['P'] = data.Q / ms['area']

	# align P around Pmin and Pmax
	maxP = max(data.P)
	minP = min(data.P)
	Pdiff = abs(minP)-abs(maxP)
	data['P'] = data.P + Pdiff/2
		
	# aling P around 0		16 because 4+ und 4-
	PNull = mean([max(data.iloc[(data['E']-0).abs().argsort()[:16]].P),min(data.iloc[(data['E']-0).abs().argsort()[:16]].P)])
	if PNull < 0:
		data['P'] = data.P + abs(PNull)
	else:
		data['P'] = data.P - abs(PNull)
	result['pnull'] = PNull

	# calc error of polarization
	data['P_error'] = (ms['vreferr'] / data.Vref + ms['rreferr']/ms['rref'] + ms['areaerr']/ms['area']) * data.P

	# get PR
	PR = mean(abs(data.iloc[(data['E']-0).abs().argsort()[:20]].P))		#mean of 20 values close to E=0
	result['PR'] = PR
	PR_error = mean(abs(data.iloc[(data['E']-0).abs().argsort()[:20]].P_error))
	result['PRerr'] = PR_error
	print('PR: (%f +- %f) mC/m2'%(abs(PR)*1000,abs(PR_error)*1000))
	#print('Vdiff: %f V'%(data.Vdiff.max()))
	
	# save data and results
	data.to_csv('Data/'+filename+'/'+filename+'_data.txt')
	data.to_pickle('Data/'+filename+'/'+filename+'_data.pd')
	
	result.to_csv('Data/'+filename+'/'+filename+'_results.txt')
	
	return data

def plot_data(data,ms,filename,measure=True):
	import matplotlib.pyplot as plt
	
	f = plt.figure('Raw Data',figsize=(12,6))
	# plot raw data
	
	axVset = f.add_subplot(121)
	axIref = axVset.twinx()	
	
	axVset.grid()

	axVset.plot(data.time,data.Vset,color='b',linestyle='-')
	axIref.plot(data.time,data.I*1e3,color='r',linestyle='-')

	axVset.set_ylabel('Vset (V)',color='b')
	axIref.set_ylabel('I (mA)',color='r')

	f.tight_layout()

	# plot hysteresis
	axHyst = f.add_subplot(122)
	axHyst.grid()
	
	axHyst.plot(data.E/1e6,data.P*1e3,label=r'%.1f V'%(ms['amp']),color='b')
	axHyst.legend()

	axHyst.set_xlabel('E (MV/m)')
	axHyst.set_ylabel('P (mC/m2)')

	# formatting and show
	f.tight_layout()
	plt.show()

	# saving
	if measure==True:
		f.savefig('Data/'+filename+'/'+filename+'_plot.pdf')
	else:
		f.savefig(filename+'plot.pdf')
