 #!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module to measure the ferroelectric hysteresis (Shunt Method) with a HP33120A 
Frequency Generator and a RIGOL DS1054Z Scope
"""

def print_line():
	"""
	line for console output
	"""
	print('----------------------')

def get_config():
	""" 
	read config file for IP, GBIP, ...
	"""
	f = open('HESMCtrl/Comm.conf','r')
	for line in f:
		if 'IP' in line:
			IP = line.split(':')[1].strip()
		elif 'GPIB-Channel' in line:
			GPIB = line.split(':')[1].strip()
	return IP, GPIB

def get_date_time():
	from time import strftime
	# get current date and time (for file output, ...)
	date_time = strftime("%Y-%m-%d_%H-%M")
	return date_time	

def create_filename(date_time,meas_sett_dict):
	"""
	create file name depending on date, time and measurement settings
	"""
	if meas_sett_dict['electrkey'] == '':
		name = "%s_%s_A%.1fV-f%.1fHz-O%.1fV"%(date_time,meas_sett_dict['name'],
		   meas_sett_dict['amp'],meas_sett_dict['freq'],meas_sett_dict['offs'])
	else:
		name = "%s_%s_%s_A%.1fV-f%.1fHz-O%.1fV"%(date_time,meas_sett_dict['name'],
		   meas_sett_dict['electrkey'],meas_sett_dict['amp'],meas_sett_dict['freq'],meas_sett_dict['offs'])
	return name

def get_measurement_settings(msfile='meas_settings.txt'):
	"""
	read meausrement setting for devices from measurement settings file
	- Name = sample name for file (str)
	- ElectrKey = pad Key for identification (str) - optional
	- Area = electrode area (float)
	- AErr = electrode area error (float)
	- thickness = sample thickness (float)
	- capacity = sample capacity (float) - optional
	- tand = tan delta (float) - optional
	- Amplitude = voltage amplitude (float)
	- Frequency = driving frequency (float)
	- Offset = voltage offset (float)
	- BurstStatus = set burst mode (str ... ON/OFF)
	- BurstCount = how many cycles in one burst (float)
	- VrefErr = error of the voltage measurement at Rref (float)
	- ScopeCyclAver = how many average cycles are set on the scope? -- 0.5 = 1 cycle (float)
	- Amplification = factor if voltage amplifier (e.g. Matsusada 5kV = 500) is used, if not 1 (float)
	- ScaleDivider_CHAN1 = Divider for y-Scale on scope's channel1 (AUTO!)
	- ScaleDivider_CHAN2 = Divider for y-Scale on scope's channel2 (float)
	- correct_Ebias = aligning the hysteresis around E = 0 (ON/OFF)
	- correct_LossI = loss current correction from capacity and tand (ON/OFF)
	- custom_curr_offs = use a custom current offset .. no automatic (float)
	- Rref = reference resistance (float)
	- RErr = error of the reference resistance (float)
	"""
	
	f = open(msfile,'r')
	meas_settings  = {}
	
	for line in f:
		if 'Name' in line:
			name = line.split(':')[1].strip()
			meas_settings.update({'name':name})
		elif 'ElectrKey' in line:
			try:
				electrKey = line.split(':')[1].strip()
				meas_settings.update({'electrkey':electrKey})
			except ValueError:
				meas_settings.update({'electrkey':''})
		elif 'Area' in line:
			area = float(line.split(':')[1].strip())
			meas_settings.update({'area':area})
		elif 'AErr' in line:
			areaerr = float(line.split(':')[1].strip())
			meas_settings.update({'areaerr':areaerr})	
		elif 'thickness' in line:
			thickness = float(line.split(':')[1].strip())
			meas_settings.update({'thickness':thickness})
		elif 'capacity' in line:
			try:
				cap = float(line.split(':')[1].strip())
				meas_settings.update({'cap':cap})
			except ValueError:
				meas_settings.update({'cap':0})
		elif 'tand' in line:
			try:
				tand = float(line.split(':')[1].strip())
				meas_settings.update({'tand':tand})
			except ValueError:
				meas_settings.update({'tand':0})
		elif 'Amplitude' in line:
			amp = float(line.split(':')[1].strip())
			meas_settings.update({'amp':amp})
		elif 'Frequency' in line:
			freq = float(line.split(':')[1].strip())
			meas_settings.update({'freq':freq})
		elif 'Offset' in line:
			offs = float(line.split(':')[1].strip())
			meas_settings.update({'offs':offs})
		elif 'ScopeCyclAver' in line:
			average = float(line.split(':')[1].strip())
			meas_settings.update({'average':average})
		elif 'BurstCount' in line:
			bstcount = float(line.split(':')[1].strip())
			meas_settings.update({'burst_count':bstcount})
		elif 'BurstStatus' in line:
			bststat = line.split(':')[1].strip()
			if bststat == 'ON':
				meas_settings.update({'burst_status':True})
			else:
				meas_settings.update({'burst_status':False})
		elif 'VrefErr' in line:
			vreferr = float(line.split(':')[1].strip())
			meas_settings.update({'vreferr':vreferr})
		elif 'Amplification' in line:
			ampfactor = float(line.split(':')[1].strip())
			meas_settings.update({'ampfactor':ampfactor})	
		elif 'ScaleDivider_CHAN1' in line: 
			divCH1 = line.split(':')[1].strip()
			if divCH1 == 'AUTO':
				meas_settings.update({'scale_divider_CHAN1':amp/3.})
				#110% of full amp (devided by 3 scale units on scope)
			else:
				meas_settings.update({'scale_divider_CHAN1':divCH1})
		elif 'ScaleDivider_CHAN2' in line: 
			divCH1 = float(line.split(':')[1].strip())
			meas_settings.update({'scale_divider_CHAN2':divCH1})
		elif 'correct_Ebias' in line:
			Ebias = line.split(':')[1].strip()
			if Ebias == 'ON':
				meas_settings.update({'correct_Ebias':True})
			else:
				meas_settings.update({'correct_Ebias':False})
		elif 'correct_LossI' in line:
			LossI = line.split(':')[1].strip()
			if LossI == 'ON':
				meas_settings.update({'correct_LossI':True})
			else:
				meas_settings.update({'correct_LossI':False})
		elif 'custom_curr_offs' in line: 
			cco = float(line.split(':')[1].strip())
			meas_settings.update({'custom_curr_offs':cco})
		elif 'Rref' in line:
			rref = float(line.split(':')[1].strip())
			meas_settings.update({'rref':rref})
		elif 'RErr' in line:
			rreferr = float(line.split(':')[1].strip())
			meas_settings.update({'rreferr':rreferr})
	
	# add amplification factor of 1, if not found in old files
	if 'ampfactor' not in meas_settings.keys():
		meas_settings.update({'ampfactor':1.0})
			
	return meas_settings


def average(data_sets_list):
	from numpy import mean
	from pandas import DataFrame
	
	list_length = len(data_sets_list)
	
	temp_time = []
	temp_Vset = []
	temp_Vref = []
	
	for i in range(list_length):
		
		temp_time.append(data_sets_list[i].time)
		temp_Vset.append(data_sets_list[i].Vset) 
		temp_Vref.append(data_sets_list[i].Vref)
		
	time = mean(data_sets_list[i].time,axis=0)
	data = DataFrame({'time':mean(temp_time,axis=0),'Vset':mean(temp_Vset,axis=0),'Vref':mean(temp_Vref,axis=0)})
	
	data = data.drop(data.index[[1198,1199]])
	return data
	
def measure_hysteresis(filename,ms):
	"""
	Measures ferroelectric hysteresis (Shunt Method) with a HP33120A 
	Frequency Generator and a RIGOL DS1054Z Scope
	ms = measurement settings (dict)
	"""
	
	# load device functions
	from HESMCtrl.DS1054ZCtrl import DS1054Z
	from HESMCtrl.HP33120ACtrl import HP33120A
	from time import clock, sleep
	from os import mkdir
	import sys
	from shutil import copy2
	from numpy import array
	from pandas import DataFrame
	
	# get IP and GPIB channel from config file
	SCOPEIP, FGGPIBchannel = get_config()
		
	# connect and init HP33120A Frequency Generator via GPIB
	FG = HP33120A()
	FG.connect_to_instrument(int(FGGPIBchannel))
	FG.off()

	# connect to the DS1054Z via Ehternet (replace IP Adress if needed!)
	SCOPE = DS1054Z(SCOPEIP)

	# Show Instruments
	print_line()
	print('Meas. Insruments:')
	print('Freq. Gen.: ' + FG.identification().strip('\n'))
	print('Scope: ' + SCOPE.idn)

	# SETTING INSTURMENTS AND START MEASUREMENT
	print_line()
	print('Setting instruments ...')

	# activate Scope's Channel1 and Channel2 if necessary
	if 'CHAN1' not in SCOPE.displayed_channels or 'CHAN2' not in SCOPE.displayed_channels:
		SCOPE.display_channel('CHAN1')		#Vset
		SCOPE.display_channel('CHAN2')		#Vref

	# setting scale depending on input signal
	SCOPE.timebase_scale = 1./(ms['freq'])/5		# setting strange ... but deviding by 5 gives approx 3 periods in display
	SCOPE.set_channel_scale('CHAN1',ms['scale_divider_CHAN1'])		
	SCOPE.set_channel_scale('CHAN2',ms['scale_divider_CHAN2'])
	
	# get eventuell time offset and time base from scope
	#time_offset = SCOPE.timebase_offset
	#time_base = SCOPE.timebase_scale
	
	# if ms['burst_status'] == True:
		# SCOPE.timebase_offset = 1e5
	
	#SCOPE.memory_depth = 6e6		
	#set aquisition memory depth to auto (also values, e.g. 6e3 for 6K can be set)
	#preample = SCOPE.waveform_preamble_dict

	# start aquisition with scope
	print('data acquisition ...')
	t_start = clock()
	
	low_f_flag = True						# has to be passed to the function in the end!
													# when using low frequencies, internal averaging of the scope is not possible
													# has to be done manually!!! --> using single trigger measurements (SCOPE.single()) over given average cycles
	
	if low_f_flag == True:
		print('... low freq measurement enabled')
		print('... averaging cycles: %i' % ms['average'])
		
		# calculate acquisition time for each cycle
		# set for 3 periods as provided by the timescale (see above)	
		acquisition_time = 1/ms['freq'] * 3	
		
		# init list of all cyclesets
		cycle_data_sets = []
		
		for i in range(int(ms['average'])):
			
			print('... cycle %i' % i)
			# maybe do some trigger stuff first?
			
			# set scope to single aquisition mode
			SCOPE.single()
		
			# setting frequency generator
			FG.set_shape('TRI')
			FG.set_frequency(ms['freq'])
			FG.set_amplitude(ms['amp']) 
			FG.set_offset(ms['offs'])
			
			SCOPE.tforce()
			
			# wat until scope has all data
			sleep(acquisition_time)
			
			# save data
			Vset = array(SCOPE.get_waveform_samples('CHAN1',mode='NORM')) * ms['ampfactor']
			Vref = array(SCOPE.get_waveform_samples('CHAN2',mode='NORM')) 
			time = array(SCOPE.waveform_time_values)
			
			# combine data in DataFrame
			cycle_data = DataFrame({'time':time,'Vset':Vset,'Vref':Vref})
			cycle_data_sets.append(cycle_data)
			
			# stop scope (if not already done) and frequency generator
			SCOPE.stop()
			FG.off()
			
			# wait 2 seconds before start again
			sleep(2)	

		# average data after loop
		data = average(cycle_data_sets)
		
	else:
		SCOPE.run()
		sleep(2)	#wait until scope is ready

		# settings for FG
		if ms['burst_status'] == True:
			FG.set_burst_count(ms['burst_count'])
			FG.set_burst_status('ON')
		FG.set_shape('TRI')
		FG.set_frequency(ms['freq'])
		FG.set_amplitude(ms['amp']) 
		FG.set_offset(ms['offs'])

		# wait until scope has all the data (dpending on frequency)
		acquire_time = 1/ms['freq'] * 3	#3 periods!
	#	sleep(2*(ms['average']*2)) 
		sleep(acquisition_time + (2*ms['average'] * acquisition_time))
		# sleep(35)
		# record date
		Vset = array(SCOPE.get_waveform_samples('CHAN1',mode='NORM')) * ms['ampfactor']
		Vref = array(SCOPE.get_waveform_samples('CHAN2',mode='NORM')) 
		#Vset = array(SCOPE.get_waveform_samples('CHAN1')) * ms['ampfactor']		#save Vset array
		#Vref = array(SCOPE.get_waveform_samples('CHAN2'))		 	 	 	 	#save Vref array
		time = array(SCOPE.waveform_time_values)				#save time array
		#t = t-time_offset
		
		# stop acquisition and switch off Freq.Gen.
		SCOPE.stop()
		FG.off()

		data = DataFrame({'time':time,'Vset':Vset,'Vref':Vref})

		
	t_end = clock()
	print('... finished')
	print('meas. time: %f' % (t_end-t_start))
	print_line()
	
	
	# copy settings file (logs will be writen after evaluation)
	#mkdir('Data/%s'%filename)
	#copy2('meas_settings.txt','Data/'+filename+'/'+filename+'_settings.txt')
	#print('... log files written!')
	
	return data, FG, SCOPE