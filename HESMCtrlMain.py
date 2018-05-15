# -*- coding: utf-8 -*-

# Control Frequency Generator (HP33120A) and Scope (RIGOL DS1074Z) for ferroelectric hysteresis measurements
# for RIGOL Scope: https://pypi.python.org/pypi/ds1054z
# for HP33120A: see HP33120AControl.py (adopted from https://github.com/heeres/qtlab/blob/master/instrument_plugins/HP_33120A.py)


from HESMCtrl.Measurement import *
from HESMCtrl.Evaluation import *
from HESMCtrl.OSOperations import save_all

import sys
MODE = 'plot'  		# measure, plot
python_version = int(sys.version[0])

if MODE == 'measure':
	date_time = get_date_time()
	ms = get_measurement_settings()
	filename = create_filename(date_time,ms)
	
	data = measure_hysteresis(filename,ms)
	data, result = calculate_hysteresis(data,ms,filename)
	
	fig = plot_data(data,ms,filename)
		
	if python_version==2:
		answer = raw_input('... Save? [y/n]')
	elif python_version==3:
		answer = input('... Save? [y/n]')
	
	if answer == 'y' or answer == 'yes':
		save_all(data, result, fig, filename, mode=MODE)
	else:
		pass
	
elif MODE == 'plot':
	import pandas as pd
	from glob import glob
	
	try:
		msfile = glob('*V_settings.txt')[0]
		datafile = glob('*.pd')[0]
		ms = get_measurement_settings(msfile)
	
		data = pd.read_pickle(datafile)
		filename = datafile.strip('_data.pd')
	
		data, result = calculate_hysteresis(data,ms,filename)
		fig = plot_data(data,ms,filename)
		
		save_all(data, result, fig, filename, mode=MODE)
		if python_version == 2:
			raw_input('Press any key!')
		elif python_version == 3:
			input('Press any key!')
	except IndexError:
		print('No .pd file found!')

	
