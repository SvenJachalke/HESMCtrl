# -*- coding: utf-8 -*-

# Control Frequency Generator (HP33120A) and Scope (RIGOL DS1074Z) for ferroelectric hysteresis measurements
# for RIGOL Scope: https://pypi.python.org/pypi/ds1054z
# for HP33120A: see HP33120AControl.py (adopted from https://github.com/heeres/qtlab/blob/master/instrument_plugins/HP_33120A.py)


from HESMCtrl.Measurement import *
from HESMCtrl.Evaluation import *

MODE = 'measure'  		# measure, plot

ms = get_measurement_settings()
if MODE == 'measure':
	date_time = get_date_time()
	filename = create_filename(date_time,ms)
	
	data = measure_hysteresis(filename,ms)
	data = calculate_hysteresis(data,ms,filename)
	
	plot_data(data,ms,filename)
	
elif MODE == 'plot':
	import pandas as pd
	from glob import glob
	
	try:
		datafile = glob('*.pd')[0]
	
		data = pd.read_pickle(datafile)
		filename = datafile.strip('data.pd')
	
		data = calculate_hysteresis(data,ms,filename)
		plot_data(data,ms,filename,measure=False)
	except IndexError:
		print('No .pd file found!')


#input('Press any key!')