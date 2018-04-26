 #!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
General operations
"""

def save_all(data, result, figure, filename, mode='measure'):
	
	from os import getcwd, mkdir
	from shutil import copy2
	
	filepath = getcwd()
	
	if mode == 'measure':
	
		filepath = filepath+'/Data/'
		
		# copy settings file
		mkdir(filepath+'/%s'%filename)
		
		filepath = filepath + '/' + filename + '/'
		copy2('meas_settings.txt',filepath+filename+'_settings.txt')
		
		# saving plot
		figure.savefig(filepath+filename+'_plot.pdf')
		
	elif mode == 'plot':
		filepath = filepath+'/'
	
	else:
		print('Invalid mode encountered!')
		pass

	# saving plot
	figure.savefig(filepath+filename+'_plot.pdf')		
	
	# saving data (csv and pickle) and results
	data.to_csv(filepath+filename+'_data.txt')
	data.to_pickle(filepath+filename+'_data.pd')
	result.to_csv(filepath+filename+'_results.txt')

	print('... saving finished!')