class HP33120A():
	#Constructor
	def __init__(self):
		self.GBIPchannel = 22		#standart GBIP channel
		
# GENERAL

	def connect_to_instrument(self, GPIBchannel):
		import visa
		self.GPIBchannel = GPIBchannel
		self.GPIBaddress = 'GPIB0::'+str(self.GPIBchannel)+'::INSTR'
		
		self.rm = visa.ResourceManager()
		self.instrument = self.rm.open_resource(self.GPIBaddress)
		
		self.off()
		
	def reset(self):
		self.instrument.write('*RST')

	def error(self):
		self.instrument.ask('SYS:ERR?')
	
	def identification(self):
		return self.instrument.ask('*IDN?')

	def off(self):
		"""
		set output off
		https://www.keysight.com/main/editorial.jspx?ckey=1000001212:epsg:faq&id=1000001212:epsg:faq&nid=-11143.0.00&lc=eng&cc=CA
		"""
		self.instrument.write(' APPLy:DC DEFault, DEFault, 0')
	
# SHAPES

	def set_shape(self, shape):
		'''
		shape : { SIN, SQU, TRI, RAMP, NOIS, DC, USER }
		'''
		self.instrument.write('SOUR:FUNC:SHAP %s' % shape)

	def get_shape(self):
		shape = self.instrument.ask('SOUR:FUNC:SHAP?')
		if "SIN" in shape:
			print('Shape: Sine')
		if "SQU" in shape:
			print('Shape: Square')
		if "TRI" in shape:
			print('Shape: Triangular')
		if "RAMP" in shape:
			print('Shape: Ramp')
		if "NOIS" in shape:
			print('Shape: Noise')
		if "USER" in shape:
			print('Shape: Custom by User')
		return shape
		
		
# PARAMETERS

	def set_frequency(self, freq):
		self.instrument.write('SOUR:FREQ %f' % freq)

	def get_frequency(self):
		self.freq = self.instrument.ask('SOUR:FREQ?')
		#print('Frequency:'+self.freq)
		return float(self.freq)

		
	def set_amplitude(self, amp):
		self.instrument.write('SOUR:VOLT %f' % amp)

	def get_amplitude(self):
		self.amp = self.instrument.ask('SOUR:VOLT?')
		#print('Amplitude:'+self.amp)
		return float(self.amp)
		

	def set_offset(self, freq):
		self.instrument.write('SOUR:VOLT:OFFS %f' % freq)

	def get_offset(self):
		self.offs = self.instrument.ask('SOUR:VOLT:OFFS?')
		#print('Offset:'+self.offs)
		return float(self.offs)
		
# BURST

	def set_burst_count(self, cnt):
		self.instrument.write('BM:NCYC %d' % cnt)

	def get_burst_count(self):
		return float(self.instrument.ask('BM:NCYC?'))

	def set_burst_status(self, stat):
		"""
		stat: {ON, OFF}
		"""
		self.instrument.write('BM:STAT %s' % stat)

	def get_burst_status(self):
		return self.instrument.ask('BM:STAT?')

# TRIGGER

	def set_trigger_continuous(self):
		self.instrument.write('TRIG:SOUR IMM')

	def set_trigger_external(self):
		self.instrument.write('TRIG:SOUR EXT')

	def set_trigger_gpib(self):
		self.instrument.write('TRIG:SOUR BUS')
		
	def  get_trigger_status(self):
		return self.instrument.ask('TRIG:SOUR?')
		
	def send_trigger(self):
		self.instrument.write('*TRG')
		
		
