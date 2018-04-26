 #!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
General operations
"""

def save_all(data, result, figure, filename, mode='measure'):
	
	from os import getcwd, mkdir
	from shutil import copy2
	
	filepath = getcwd()
	print(filepath)
	
	if mode == 'measure':
		filepath = filepath+'/Data/'
		
		# copy settings file
		mkdir(filepath+'/%s'%filename)
		copy2('meas_settings.txt',filepath+'/'+filename+'/'+filename+'_settings.txt')
		
		# saving plot
		print('... saving plot')
		figure.savefig(filepath+filename+'/'+filename+'_plot.pdf')
		
	elif mode == 'plot':
		filepath = filepath+'/'
		
		# saving plot
		print('... saving plot')
		figure.savefig(filepath+filename+'_plot.pdf')
	
	else:
		print('Invalid mode encountered!')
		pass
	
	# saving data (csv and pickle) and results
	data.to_csv(filepath+filename+'_data.txt')
	data.to_pickle(filepath+filename+'_data.pd')
	result.to_csv(filepath+filename+'_results.txt')