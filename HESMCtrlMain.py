# -*- coding: utf-8 -*-

# Control Frequency Generator (HP33120A) and Scope (RIGOL DS1074Z) for ferroelectric hysteresis measurements
# for RIGOL Scope: https://pypi.python.org/pypi/ds1054z
# for HP33120A: see HP33120AControl.py (adopted from https://github.com/heeres/qtlab/blob/master/instrument_plugins/HP_33120A.py)


from HESMCtrl.Measurement import *
from HESMCtrl.Evaluation import *

MODE = 'plot'  		# measure, plot


if MODE == 'measure':
	date_time = get_date_time()
	ms = get_measurement_settings()
	filename = create_filename(date_time,ms)
	
	data = measure_hysteresis(filename,ms)
	data = calculate_hysteresis(data,ms,filename,mode=MODE)
	
	plot_data(data,ms,filename)
	
elif MODE == 'plot':
	import pandas as pd
	from glob import glob
	
	try:
		msfile = glob('*settings.txt')[1]
		datafile = glob('*.pd')[0]
		ms = get_measurement_settings(msfile)
	
		data = pd.read_pickle(datafile)
		filename = datafile.strip('_data.pd')
	
		data = calculate_hysteresis(data,ms,filename,mode=MODE)
		plot_data(data,ms,filename,mode=MODE)
	except IndexError:
		print('No .pd file found!')


#input('Press any key!')