#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Evaluate data to reconstruct ferroelectric hysteresis
"""
def get_PR(data):
	"""
	calculates remanent polarization and error
	"""
	from numpy import mean
	PR = mean(abs(data.iloc[(data['E']-0).abs().argsort()[:20]].P))		#mean of 20 values close to E=0
	PR_error = mean(abs(data.iloc[(data['E']-0).abs().argsort()[:20]].P_error))
	
	return PR, PR_error

def get_EC(data):
	"""
	determines coercive field 
	"""
	from numpy import mean
	EC = mean(abs(data.iloc[(data['P']-0).abs().argsort()[:20]].E))
	
	return EC

def calculate_hysteresis(data,ms,filename):
	"""
	Reconstruct hysteresis shape from measured date (time, Vset, Vref)
	and measurement settings dict
	"""
	
	from numpy import pi, mean
	from scipy.integrate import cumtrapz
	import pandas as pd
	
	print('--------------------------')
	print('Evaluation ...')
	print('... calculating hysteresis')
	
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
	print('... E_bias: %f MV/m ; %f V'%(E_bias/1e6,E_bias*ms['thickness']))
	if ms['correct_Ebias'] == True:
		print('... correct Ebias')
		if E_bias < 0:
			data['E'] = data.E + abs(E_bias)
		else:
			data['E'] = data.E - abs(E_bias)
	result['ebias'] = E_bias
	
	# correct loss current before removing offset	
	if ms['correct_LossI'] == True:
		print('... correct loss current')
		try:
			data['I_Loss'] = data.Vref * 2 * pi * ms['freq'] * ms['cap'] * ms['tand']
			data['I'] = data.I - data.I_Loss
			print('... ILoss/IP: %e'%(mean(data.I_Loss)/mean(data.I)))
		except ValueError:
			print('Some values missing! (Capacity, tan d ?)')
	
	# calc offset current from mean of 1 period
	if ms['custom_curr_offs'] == 0:
		
		# TEST: get start index from first zero transition of current signal
		# index_DataFrame = data.iloc[(data['I']-0.0).abs().argsort()[:20]]	# extract index from nearest values to zero
		# start_index = index_DataFrame.index.min()
		
		start_index = 50
		
		increment = data.time[1]-data.time[0]
		steps = int(1./ ms['freq'] / increment * 2)
		offset = mean(data.I[start_index:steps+start_index])
	else:
		print('... auto offset current disabled')
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

	# get EC and PR --> 3 sigma
	PR, PR_error = get_PR(data)
	result['PR'], result['PRerr'] = PR, 3*PR_error
	result['EC'] = get_EC(data)
	
	print('... PR: (%f +- %f) yC/cm2'%(abs(result['PR'])*100,abs(result['PRerr'])*100))
	#print('Vdiff: %f V'%(data.Vdiff.max()))
	
	return data, result

def plot_data(data,ms,filename):
	use_science_style = False
	
	if use_science_style == True:
		import matplotlib as mpl
		mpl.style.use('science')
	
	import matplotlib.pyplot as plt
	plt.ion()

	#colors
	blue = (0/255.0, 100/255.0, 168/255.0)
	red = (181/255.0, 18/255.0, 62/255.0)
	green = (25/255.0, 150/255.0, 43/255.0) 
	
	f = plt.figure('Raw Data',figsize=(12,6))
	
	# plot raw data
	axVset = f.add_subplot(121)
	axIref = axVset.twinx()	
	
	if use_science_style == True: 
		axVset.grid()
	else:
		axVset.grid(linestyle='--')
	
	# check ax scaling 
	if data.Vset.max() / 1e6 < 1 and data.Vset.max() / 1e6 > 0.001:
		Vset = data.Vset * 1e-3
		axVset.set_ylabel('Vset (kV)',color=green)
	else:
		Vset = data.Vset
		axVset.set_ylabel('Vset (V)',color=green)

	if data.I.max() * 1e3 > 1 and data.I.max() * 1e3 < 1000:
		Iref = data.I * 1e3
		axIref.set_ylabel('I (mA)',color=red)
	elif data.I.max() * 1e6 > 1 and data.I.max() * 1e6 < 1000:
		Iref = data.I * 1e6
		axIref.set_ylabel(r'I ($\mu$A)',color=red) 
	else:
		Iref = data.I
		axIref.set_ylabel('I (A)',color=red)
	
	axVset.plot(data.time,Vset,color=green,linestyle='-')
	axIref.plot(data.time,Iref,color=red,linestyle='-')

	f.tight_layout()

	# plot hysteresis
	axHyst = f.add_subplot(122)
	if use_science_style == True: 
		axHyst.grid()
	else:
		axHyst.grid(linestyle='--')
		
	# check ax scaling 
	if data.E.max() / 1e6 < 1 and data.E.max() / 1e6 > 0.001:
		E = data.E * 1e-3
		axHyst.set_xlabel('E (kV/m)')
	elif data.E.max() / 1e9 < 1 and data.E.max() / 1e9 > 0.001:
		E = data.E * 1e-6
		axHyst.set_xlabel('E (MV/m)')
	else:
		E = data.E
		axHyst.set_xlabel('E (V/m)')
	
	P = data.P * 1e2 #yC/cm2 

	axHyst.set_ylabel(r'P ($\mu$C/cm$^2$)')
	
	axHyst.plot(E,P,label=r'A: %.2f V, f: %.3f Hz'%(ms['amp']*ms['ampfactor'],ms['freq']),color=blue)
	axHyst.legend(loc=2)
	
	# layout
	f.tight_layout()
	plt.show()
	
	return f