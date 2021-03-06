import nidaqmx
import nidaqmx.stream_writers
import nidaqmx.stream_readers
import nidaqmx.task
import nidaqmx.system
import time
import numpy as np
import matplotlib.pyplot as plt
import visa
def voltmetre():
	with nidaqmx.Task() as task :
		task.ai_channels.add_ai_voltage_chan("Dev1/ai11") #05/02/2020 : ai0 et ai3 (au moins) déconnent : il y a l'air d'y avoir un probleme de masse
		V=task.read()
		print(V)



def signal_out():
	with nidaqmx.Task() as task:
		task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
		out_stream=nidaqmx._task_modules.out_stream.OutStream(task)
		out=nidaqmx.stream_writers.AnalogSingleChannelWriter(out_stream,auto_start=True)
		task.timing.cfg_samp_clk_timing(10000,sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
		signal=np.arange(0,3,0.1)
		signal[-1]=0
		out.write_many_sample(signal)
		time.sleep(10)
		

def digital2d_out():
	with nidaqmx.Task() as task:

		task.do_channels.add_do_chan('Dev1/port0/line1')
		task.do_channels.add_do_chan('Dev1/port0/line0')

		out_stream=nidaqmx._task_modules.out_stream.OutStream(task)
		out=nidaqmx.stream_writers.DigitalMultiChannelWriter(out_stream,auto_start=True)
		signal=np.zeros(100)
		for i in range(100) :
			if i%3==0 :
				signal[i]=1
		signal=np.uint8(signal)
		signal2=1-signal
		signal2d=np.vstack((signal,signal2))
		for i in range(100) :
			out.write_many_sample_port_byte(signal2d)

def digital_out():
	with nidaqmx.Task() as task:

		task.do_channels.add_do_chan('Dev1/port0/line0')       
		task.timing.cfg_samp_clk_timing(100,sample_mode=nidaqmx.constants.AcquisitionType.FINITE,samps_per_chan=200)
		signal=[True,False]*5
		task.write(signal)
		task.start()
		while not task.is_task_done() :
			pass

		
def do2() :
	with nidaqmx.Task() as task:
		task.do_channels.add_do_chan('Dev1/port0/line1')
		out_stream=nidaqmx._task_modules.out_stream.OutStream(task)
		task.timing.cfg_samp_clk_timing(10000,sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
		signal=np.zeros(100)
		for i in range(len(signal)): 
			if i%2 == 0:
				signal[i]=1
		signal=np.float64(signal) 
		#print (signal[0].dtype)       
		task.write([False,True],auto_start=True)
		


def apd() :
	with nidaqmx.Task() as clock:
		with nidaqmx.Task() as trig:
			with nidaqmx.Task() as shutter :
				with nidaqmx.Task() as task:
					clock.co_channels.add_co_pulse_chan_freq('Dev1/ctr1', freq=2000)
					clock.timing.cfg_implicit_timing(sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
					clock.start()

					trig.co_channels.add_co_pulse_chan_freq('Dev1/ctr2', freq=1)
					trig.timing.cfg_implicit_timing(sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
					trig.start()

					shutter.do_channels.add_do_chan('Dev1/port0/line0')
					shutter.timing.cfg_samp_clk_timing(2000,sample_mode=nidaqmx.constants.AcquisitionType.FINITE,samps_per_chan=2000)
					sw=nidaqmx.stream_writers.DigitalSingleChannelWriter(shutter.out_stream)
					shutter.triggers.start_trigger.cfg_dig_edge_start_trig('/Dev1/Ctr2InternalOutput')


					shutter_out=[True]*500+[False]*1000+[True]*500


					task.ci_channels.add_ci_count_edges_chan('Dev1/ctr0')

					#ci=nidaqmx._task_modules.channels.ci_channel.CIChannel(task._handle,'Dev1/ctr0')
					#task.timing.cfg_samp_clk_timing(100000,source='/Dev1/100kHzTimebase',sample_mode=nidaqmx.constants.AcquisitionType.FINITE)
					task.timing.cfg_samp_clk_timing(2000,source='/Dev1/Ctr1InternalOutput',sample_mode=nidaqmx.constants.AcquisitionType.FINITE,samps_per_chan=2000)
					sr=nidaqmx.stream_readers.CounterReader(task.in_stream)
					data=np.zeros(2000)
					#print(ci.ci_count)

					task.triggers.arm_start_trigger.dig_edge_src='/Dev1/Ctr2InternalOutput'
					task.triggers.arm_start_trigger.trig_type=nidaqmx.constants.TriggerType.DIGITAL_EDGE

					#sw.write_many_sample_port_uint32(shutter_out)
					shutter.write(shutter_out)
					
					
					shutter.start()
					sr.read_many_sample_double(data,number_of_samples_per_channel=2000)


					
					
					
					return(data)

			

			
			#print(ci.ci_count)
			
def apd_loop():
	data=np.zeros(2000)
	for i in range(50):
		data=data+apd()

	#plt.plot(data[2:2000]-2*data[1:1999]+data[0:1998])
	plt.plot(data[2:2000]-data[0:1998])
	plt.show()

def sample_clock() :
	with nidaqmx.Task() as task:
		task.co_channels.add_co_pulse_chan_freq('Dev1/ctr1', freq=100000.0, idle_state=nidaqmx.constants.Level.LOW, duty_cycle=0.5)
		task.timing.cfg_implicit_timing(sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)


		co=nidaqmx._task_modules.channels.co_channel.COChannel(task._handle,'Dev1/ctr1')

		
		task.start()
		#print(ci.ci_count)
		time.sleep(3)
		#print(ci.ci_count)

		

def test_sample_clock() :
	with nidaqmx.Task() as task:
		task.do_channels.add_do_chan('Dev1/port2/line4')
		task.write(True)
		task.start()

def device() :
	ni=nidaqmx.system.device.Device('Dev1')
	print(ni.ci_physical_chans.channel_names)
	print(ni.ci_samp_clk_supported)
	print(ni.terminals)

def trigger() :
	with nidaqmx.Task() as trig:
		with nidaqmx.Task() as task:
			trig.co_channels.add_co_pulse_chan_freq('Dev1/ctr2', freq=0.2)
			trig.timing.cfg_implicit_timing(sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)


			trig.start()
			task.do_channels.add_do_chan('Dev1/port0/line0')
			task.timing.cfg_samp_clk_timing(1,sample_mode=nidaqmx.constants.AcquisitionType.FINITE,samps_per_chan=2)
			task.triggers.start_trigger.cfg_dig_edge_start_trig('/Dev1/Ctr2InternalOutput')
			task.write([True,False])
			task.start()
			while not task.is_task_done() :
				pass



def open_shutter():
	with nidaqmx.Task() as shutter:
		shutter.do_channels.add_do_chan('Dev1/port0/line0')
		shutter.timing.cfg_samp_clk_timing(100,sample_mode=nidaqmx.constants.AcquisitionType.FINITE,samps_per_chan=400)
		#sw=nidaqmx.stream_writers.DigitalSingleChannelWriter(shutter.out_stream)
		shutter_out=[False]*100+[True]*200+[False]*100
		#print(shutter_out)
		#sw.write_many_sample_port_uint32(shutter_out)
		shutter.write(shutter_out)
		shutter.start()
		while not shutter.is_task_done() :
			pass



def trigger_digital_input():
	with nidaqmx.Task() as read :
		with nidaqmx.Task() as write :
			write.do_channels.add_do_chan('Dev1/port0/line3')
			read.di_channels.add_di_chan('Dev1/port0/line4')

			write.timing.cfg_samp_clk_timing(1000,sample_mode=nidaqmx.constants.AcquisitionType.FINITE,samps_per_chan=400)
			read.timing.cfg_samp_clk_timing(1000,sample_mode=nidaqmx.constants.AcquisitionType.FINITE,samps_per_chan=400)

			signal=[False]*100+[True]*200+[False]*100

			write.triggers.start_trigger.cfg_dig_edge_start_trig('/Dev1/di/StartTrigger')
			#read.triggers.start_trigger.cfg_dig_edge_start_trig('Dev1/port0/line5')

			

			write.write(signal)

			write.start()

			
			data=read.read(nidaqmx.constants.READ_ALL_AVAILABLE)
			time.sleep(2)

			

				
			#read.start()


			plt.plot(data)
			plt.show()

def trigger_counter_input(): #non fonctionnel
	with nidaqmx.Task() as counter :
		with nidaqmx.Task() as read :
			with nidaqmx.Task() as write :
				write.do_channels.add_do_chan('Dev1/port0/line3')
				read.di_channels.add_di_chan('Dev1/port0/line4')
				counter.ci_channels.add_ci_count_edges_chan('Dev1/ctr0')

				write.timing.cfg_samp_clk_timing(1000,sample_mode=nidaqmx.constants.AcquisitionType.FINITE,samps_per_chan=400)
				read.timing.cfg_samp_clk_timing(1000,sample_mode=nidaqmx.constants.AcquisitionType.FINITE,samps_per_chan=400)
				

				signal=[False]*100+[True]*200+[False]*100

				write.triggers.start_trigger.cfg_dig_edge_start_trig('/Dev1/di/StartTrigger')

				

				write.write(signal)

				write.start()

				data=read.read(nidaqmx.constants.READ_ALL_AVAILABLE)
				time.sleep(2)

				

					

				plt.plot(data)
				plt.show() 

def test_frequenecy_measurement():
	with nidaqmx.Task() as ctf :
		ctf.ci_channels.add_ci_freq_chan('Dev1/ctr0')
		#ctf.ci_channels.add_ci_count_edges_chan('Dev1/ctr0')
		#ctf.timing.cfg_implicit_timing(sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
		ctf.start()
		print (ctf.read(10))


def writing_file():
	with open("toto.csv", "w") as file:
		a=[1,2,3]
		file.write(str(a))

def moving_average(a, n=3) :
	ret = np.cumsum(a, dtype=float)
	ret[n:] = ret[n:] - ret[:-n]
	return ret[n - 1:] / n


def servo():
	with nidaqmx.Task() as task:
		task.ao_channels.add_ao_voltage_chan('Dev1/ao1')
		angle=20
		tension=angle*5./180.
		task.write(tension)
		time.sleep(0.5)


def retrigger():
	with nidaqmx.Task() as task:
		with nidaqmx.Task() as trig:
			trig.co_channels.add_co_pulse_chan_freq('Dev1/ctr2', freq=2)
			trig.timing.cfg_implicit_timing(sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
			trig.start()


			task.do_channels.add_do_chan('Dev1/port0/line0')       
			task.timing.cfg_samp_clk_timing(10,sample_mode=nidaqmx.constants.AcquisitionType.FINITE,samps_per_chan=2)
			task.write([False,True])
			
			task.triggers.start_trigger.cfg_dig_edge_start_trig('/Dev1/Ctr2InternalOutput') #J'ai l'impression que ça déconne si il recoit un trigger pendant la séquence. Fin il repart direct quoi
			task.triggers.start_trigger.retriggerable=True
			
			task.start()
			time.sleep(5.5)

def retrigger_apd():
	with nidaqmx.Task() as task:
		with nidaqmx.Task() as apd:
			with nidaqmx.Task() as trig:
				with nidaqmx.Task() as sample_clock:
					trig.co_channels.add_co_pulse_chan_freq('Dev1/ctr2', freq=1)
					trig.timing.cfg_implicit_timing(sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
					trig.start()

					sample_clock.co_channels.add_co_pulse_chan_freq('Dev1/ctr1', freq=1000)
					sample_clock.timing.cfg_implicit_timing(sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
					sample_clock.start()


					
					

					task.do_channels.add_do_chan('Dev1/port0/line0')       
					task.timing.cfg_samp_clk_timing(10,sample_mode=nidaqmx.constants.AcquisitionType.FINITE,samps_per_chan=2)
					task.write([False,True])

					task.triggers.start_trigger.cfg_dig_edge_start_trig('/Dev1/Ctr0Gate') #J'ai l'impression que ça déconne si il recoit un trigger pendant la séquence. Fin il repart direct quoi
					#task.triggers.start_trigger.retriggerable=True
					task.start()

					apd.ci_channels.add_ci_count_edges_chan('Dev1/ctr0')
					apd.timing.cfg_samp_clk_timing(1000,source='/Dev1/Ctr1InternalOutput',sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS, samps_per_chan=2)
					apd.triggers.arm_start_trigger.dig_edge_src='/Dev1/100kHzTimebase'
					apd.triggers.arm_start_trigger.trig_type=nidaqmx.constants.TriggerType.DIGITAL_EDGE


					time.sleep(2)
					signal=apd.read(2)
					print(signal[0],signal[1],(signal[1]-signal[0])*1000)

					time.sleep(2)

					signal=apd.read(2)
					print(signal[0],signal[1],(signal[1]-signal[0])*1000)



def gonio_test_1():
	with nidaqmx.Task() as trig:
		trig.do_channels.add_do_chan('Dev1/port0/line0')
		#trig.timing.cfg_samp_clk_timing(1,sample_mode=nidaqmx.constants.AcquisitionType.FINITE,samps_per_chan=2)
		trig_out=[True]+[False]
		trig.start()
		trig.write(trig_out)
		
		while not trig.is_task_done() :
			pass        

def gonio_test_2():
	with nidaqmx.Task() as trig:
		trig.do_channels.add_do_chan('Dev1/port0/line1')
		trig.timing.cfg_samp_clk_timing(1.5,sample_mode=nidaqmx.constants.AcquisitionType.FINITE,samps_per_chan=10)
		trig_out=[True]+[False]
		trig_out=trig_out*5
		trig.write(trig_out)
		trig.start()
		gonio_test_1()
		while not trig.is_task_done() :
			pass      

def one_task_two_channels():
	with nidaqmx.Task() as task:
		task.do_channels.add_do_chan('Dev1/port0/line0')
		task.do_channels.add_do_chan('Dev1/port0/line1')
		signal=[[True,False,True],[False,True,False]]
		task.timing.cfg_samp_clk_timing(10,sample_mode=nidaqmx.constants.AcquisitionType.FINITE,samps_per_chan=3)
		task.write(signal)
		task.start()
		while not task.is_task_done() :
			pass 
		


def pulse_test():
	with nidaqmx.Task() as task:
		task.do_channels.add_do_chan('Dev1/port0/line0')
		task.start()
		#task.timing.cfg_samp_clk_timing(10,sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS,samps_per_chan=2)
		task.write([True,False]) # time bins ~ 1ms
		
		task.write([True,False])

		task.write([True,False])


def apd() : # La gate marche pas comme je pensais
	with nidaqmx.Task() as sample_clock:
		with nidaqmx.Task() as counter:
			sampling_rate=1000000
			sample_clock.co_channels.add_co_pulse_chan_freq('Dev1/ctr1', freq=sampling_rate)
			sample_clock.timing.cfg_implicit_timing(sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS) #Else the clock sends a single pulse
			sample_clock.start()

			counter.ci_channels.add_ci_count_edges_chan('Dev1/ctr0')
			counter.timing.cfg_samp_clk_timing(sampling_rate,source='/Dev1/Ctr1InternalOutput',sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS, samps_per_chan=100)
			print(counter.read(100))


def gated_apd_3(): #re créer une task prend environ 25 ms, alors que faire start/stop prend environ 10 ms
	sampling_rate=1000
	with nidaqmx.Task() as gate:
		gate.do_channels.add_do_chan('Dev1/port0/line0')
		gate.timing.cfg_samp_clk_timing(sampling_rate,sample_mode=nidaqmx.constants.AcquisitionType.FINITE, samps_per_chan=200)
		signal=[True]*150+[False]*50
		gate.write(signal)
		gate.start()
		time.sleep(0.4)
	with nidaqmx.Task() as gate:
		gate.do_channels.add_do_chan('Dev1/port0/line0')
		gate.timing.cfg_samp_clk_timing(sampling_rate,sample_mode=nidaqmx.constants.AcquisitionType.FINITE, samps_per_chan=200)
		signal=[True]*150+[False]*50
		gate.write(signal)
		gate.start()
		time.sleep(0.4)

def gated_apd_2(): #La resolution temporelle est pas si ouf que ca. Il lui faut un certain temps entre 2 entrées dans le buffer, environ 15E-5 s.
	sampling_rate=100000
	with nidaqmx.Task() as gate:
		gate.do_channels.add_do_chan('Dev1/port0/line7')
		gate.timing.cfg_samp_clk_timing(sampling_rate,sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS,samps_per_chan=50) #samp per chan doit être > 2*len(signal). Pk? Le buffer est chelou en vrai
		with nidaqmx.Task() as counter:
			counter.ci_channels.add_ci_pulse_width_chan('Dev1/ctr0',units=nidaqmx.constants.TimeUnits.TICKS)

			counter.channels.ci_ctr_timebase_src='/Dev1/PFI8'

			counter.start()

			signal=[True]*14+[False]*1
			
			gate.write(signal)
			gate.start()

			print(counter.read(5))

			gate.stop()
			gate.start()
			
			print(counter.read())
			

def gated_apd_4(): #Peut être à creuser avec du high frequency 2 counters, mais qu'est-ce que c'est chiant...
	sampling_rate=1000
	with nidaqmx.Task() as gate:
		gate.do_channels.add_do_chan('Dev1/port0/line7')
		gate.timing.cfg_samp_clk_timing(sampling_rate,sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS, samps_per_chan=200)
		with nidaqmx.Task() as counter:
			counter.ci_channels.add_ci_freq_chan('Dev1/ctr0',max_val=100000.0)
			
			print(counter.read())
			

def pause_trigger_sample_clock():
	with nidaqmx.Task() as sample_clock:
		sampling_rate=100
		sample_clock.co_channels.add_co_pulse_chan_freq('Dev1/ctr1', freq=sampling_rate)
		sample_clock.timing.cfg_implicit_timing(sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS) #Else the clock sends a single pulse
		sample_clock.start()

			
def test_classes():
	class parameter():
		def __init__(self,value):
			self.v=value
			self.dtype=type(self.v)
		def update(self,new_value):
			if self.dtype==type(1):
				self.v=int(new_value)
			elif self.dtype==type(1.):
				self.v=float(new_value)
	dt=parameter(0.01)
	print(dt.v)
	def update(param,value):
		param.update(value)
	update(dt,0.05)
	print(dt.v)

def test_apt():
	import thorlabs_apt as apt
	#from thorlabs_apt import _cleanup
	ml=apt.list_available_devices()

	motorX = apt.Motor(ml[1][1])
	motorY = apt.Motor(ml[0][1])

	print(motorX.is_in_motion)
	cpt=0
	motorX.move_to(12,blocking=False)
	while motorX.is_in_motion :
		cpt+=1
	
	print(cpt)
	apt._cleanup()






def generateur_RS():
	with nidaqmx.Task() as tension:
		tension.ai_channels.add_ai_voltage_chan("Dev1/ai11")    
		tension.timing.cfg_samp_clk_timing(1000,sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS,samps_per_chan=1000)   
		#tension.start()
		import visa
		resourceString4 = 'USB0::0x0AAD::0x0197::5601.3800k03-101213::INSTR'  # Pour avoir l'adresse je suis allé regarder le programme RsVisaTester de R&S dans "find ressource"
		rm = visa.ResourceManager()
		PG = rm.open_resource( resourceString4 )
		PG.write_termination = '\n'
		PG.clear()  # Clear instrument io buffers and status
		PG.write('OUTP:GEN 0')
		PG.write('*WAI')
		PG.write('INST 1')
		PG.write('*WAI')
		PG.write('VOLTage:RAMP ON')
		PG.write('*WAI')
		PG.write('VOLTage:EASYramp:TIME %f'%1)#le temps est en secondes et j'arrive pas à faire 0.1 sec...
		PG.write('*WAI')
		PG.write('OUTP:SEL 1')
		PG.write('*WAI')
		PG.write('APPLY "%f,%f"' % (2,1))
		PG.write('*WAI')
		PG.write('OUTP:GEN 1')
		PG.write('*WAI')
		#print(PG.query('APPLY?'))
		y=tension.read(1000)
		PG.write('OUTP:GEN 0')
		PG.write('*WAI')

		x=np.linspace(0,1,1000)
		fig,ax=plt.subplots(2)
		ax1=ax[0]
		ax2=ax[1]
		ax1.plot(x,y)
		time.sleep(1)
		PG.write('INST 1')
		PG.write('*WAI')
		PG.write('VOLTage:RAMP ON')
		PG.write('*WAI')
		PG.write('VOLTage:EASYramp:TIME %f'%1)#le temps est en secondes et j'arrive pas à faire 0.1 sec...
		PG.write('*WAI')
		PG.write('OUTP:SEL 1')
		PG.write('*WAI')
		PG.write('APPLY "%f,%f"' % (1,1))
		PG.write('*WAI')
		PG.write('OUTP:GEN 1')
		PG.write('*WAI')
		#print(PG.query('APPLY?'))
		z=tension.read() #read_all_avilable ne lis que ce qu'il y a sur l'ordi, il faut d'abord enclencher le vidage du buffer
		print(z)
		z=tension.read(nidaqmx.constants.READ_ALL_AVAILABLE)
		print(len(z))
		y=tension.read(1000)
		PG.write('OUTP:GEN 0')
		PG.write('*WAI')
		ax2.plot(x,y)
		

	plt.show()


def mesure_apd_et_tension(): #C'est non.
	with nidaqmx.Task() as sample_clock:
		sampling_rate=100
		N=100
		sample_clock.co_channels.add_co_pulse_chan_freq('Dev1/ctr1', freq=sampling_rate)
		sample_clock.timing.cfg_implicit_timing(sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS) #Else the clock sends a single pulse
		sample_clock.start()
		with nidaqmx.Task() as apd:
			apd.ci_channels.add_ci_count_edges_chan('Dev1/ctr0') 
			apd.timing.cfg_samp_clk_timing(sampling_rate,source='/Dev1/Ctr1InternalOutput',sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS, samps_per_chan=N)             
			print(apd.read(100))


def gate_sample_clock():
	with nidaqmx.Task() as sample_clock:
		sampling_rate=100
		N=100
		sample_clock.co_channels.add_co_pulse_chan_freq('Dev1/ctr1', freq=sampling_rate)
		sample_clock.timing.cfg_implicit_timing(sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS) #Else the clock sends a single pulse
		sample_clock.start()
		with nidaqmx.Task() as task:
			task.do_channels.add_do_chan('Dev1/port0/line0')
			task.timing.cfg_samp_clk_timing(sampling_rate,source='/Dev1/Ctr1InternalOutput',sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS, samps_per_chan=N)
			task.write([False,True])
			task.start()
			time.sleep(1)
			sample_clock.stop()
			time.sleep(1)
			sample_clock.start()
			time.sleep(1)


def sine_out():
	# print(nidaqmx.system.device.Device('Dev1').ao_output_types) #Pas possible d'utiliser un générateur de fonction, on a que le truc de base
	# print(nidaqmx.system.device.Device('Dev1').ao_physical_chans.channel_names)
	freq=500 #Hz 5k Hz c'est un peu le max malheuresement
	amp=10 #V
	duree=5 #s
	n_points=100


	freq_samp=n_points*freq
	x=np.linspace(0,2*np.pi,n_points)
	signal=np.sin(x)*amp

	with nidaqmx.Task() as task:
		task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
		task.timing.cfg_samp_clk_timing(freq_samp,sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS, samps_per_chan=n_points)
		task.write(signal)
		task.start()
		time.sleep(5)
		task.stop()
		task.write([0,0])
		task.start()


def offset_analog():
	V=5
	t=5

	with nidaqmx.Task() as task:
		task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
		task.write(V)
		task.start()
		time.sleep(t)
		task.stop()
		task.write(0)
		task.start()

def rampe_analog():
	amp=10 #V
	duree=2 #s
	n_points=100


	freq_samp=n_points/duree
	signal=np.linspace(0,amp,n_points)

	with nidaqmx.Task() as task:
		task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
		task.timing.cfg_samp_clk_timing(freq_samp,sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS, samps_per_chan=n_points)
		task.write(signal)
		task.start()
		time.sleep(duree)
		task.stop()
		task.write([0,0])
		task.start()




def ext_trigger_gbf():
	f_trigg=2
	f_acq=1000

	t_acq=5

	n_acq=f_acq/f_trigg

	n_acq=int(f_acq/f_trigg)

		

	with nidaqmx.Task() as read :
		with nidaqmx.Task() as write :
			with nidaqmx.Task() as sample_clock:
				with nidaqmx.Task() as apd:
					write.do_channels.add_do_chan('Dev1/port0/line0')
					read.ai_channels.add_ai_voltage_chan('Dev1/ai11')
					sample_clock.co_channels.add_co_pulse_chan_freq('Dev1/ctr1', freq=f_acq)
					apd.ci_channels.add_ci_count_edges_chan('Dev1/ctr0') 

					sample_clock.timing.cfg_implicit_timing(sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
					apd.timing.cfg_samp_clk_timing(f_acq,source='/Dev1/Ctr1InternalOutput',sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS, samps_per_chan=n_acq)  

					write.timing.cfg_samp_clk_timing(f_acq,sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS,samps_per_chan=n_acq)
					read.timing.cfg_samp_clk_timing(f_acq,sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS,samps_per_chan=n_acq)

					signal=[True]+[False]*(n_acq-1)

					#write.triggers.start_trigger.cfg_dig_edge_start_trig('/Dev1/ai/StartTrigger') #Ca marche dans les deux sens
					read.triggers.start_trigger.cfg_dig_edge_start_trig('/Dev1/do/StartTrigger')
					sample_clock.triggers.start_trigger.cfg_dig_edge_start_trig('/Dev1/do/StartTrigger') #Pas de soucis pour le counter ici

					

					write.write(signal)

					sample_clock.start()
					apd.start()
					read.start()
					write.start() #l'odre est hyper important : il faut start celui qui va trigg les autres en dernier
					

					fig,ax=plt.subplots(2)
					ax1=ax[0]
					ax2=ax[1]
					time_origin=time.time()
					while time.time()-time_origin < t_acq :
						data=read.read(n_acq)
						ax2.plot(data)
						data=apd.read(n_acq)
						data=np.array(data)
						PL=(data[1:]-data[:-1])*f_acq
						ax1.plot(PL)

						
					#read.start()


					
					plt.show()


def trig_ext_uw():
	def create_list_freq(fmin,fmax,level,n_points) :
		#Frequecy given in GHz
		freq_list=np.linspace(fmin,fmax,n_points)
		instruction_f='SOUR:LIST:FREQ'
		for f in freq_list :
			if f==max(freq_list) :
				instruction_f+=' %f GHz'%f
			else :
				instruction_f+=' %f GHz,'%f
		instruction_pow='SOUR:LIST:POW'
		for f in freq_list :
			if f==max(freq_list) :
				instruction_pow+=' %f dBm'%level
			else :
				instruction_pow+=' %f dBm,'%level
		return instruction_f,instruction_pow
	n_debug=0
	resourceString4 = 'USB0::0x0AAD::0x0054::110693::INSTR'  # Pour avoir l'adresse je suis allé regarder le programme RsVisaTester de R&S dans "find ressource"

	rm = visa.ResourceManager()
	PG = rm.open_resource( resourceString4 )
	PG.write_termination = '\n'
	print(PG.query('SYSTem:ERRor:NEXT?')+'n_debug=%i'%n_debug)
	n_debug6=1
	PG.clear()  # Clear instrument io buffers and status
	PG.write('*WAI')
	print(PG.query('SYSTem:ERRor:NEXT?')+'n_debug=%i'%n_debug)
	n_debug+=1
	PG.write(':LIST:DELete:ALL')
	PG.write('*WAI')
	print(PG.query('SYSTem:ERRor:NEXT?')+'n_debug=%i'%n_debug)
	n_debug+=1
	PG.write('LIST:SEL "new_list"') #Il lui faut un nom, j'espere qu'il y a pas de blagues si je réécris dessus
	PG.write('*WAI')
	print(PG.query('SYSTem:ERRor:NEXT?')+'n_debug=%i'%n_debug)
	n_debug+=1

	freq_list,pow_list=create_list_freq(2.8,2.95,0,51)
	print(pow_list)
	print(freq_list)

	PG.write(freq_list)
	PG.write('*WAI')
	print(PG.query('SYSTem:ERRor:NEXT?')+'n_debug=%i'%n_debug)
	n_debug+=1
	PG.write(pow_list)
	PG.write('*WAI')
	print(PG.query('SYSTem:ERRor:NEXT?')+'n_debug=%i'%n_debug)
	n_debug+=1
	print(PG.query('LIST:FREQ:POIN?'))
	PG.write('*WAI')
	print(PG.query('SYSTem:ERRor:NEXT?')+'n_debug=%i'%n_debug)
	n_debug+=1
	print(PG.query('LIST:POW:POIN?'))
	PG.write('*WAI')
	print(PG.query('SYSTem:ERRor:NEXT?')+'n_debug=%i'%n_debug)
	PG.write('LIST:MODE STEP')
	PG.write('*WAI')
	print(PG.query('SYSTem:ERRor:NEXT?')+'n_debug=%i'%n_debug)
	n_debug+=1
	PG.write('LIST:TRIG:SOUR EXT')
	PG.write('*WAI')
	print(PG.query('SYSTem:ERRor:NEXT?')+'n_debug=%i'%n_debug)
	n_debug+=1


	with nidaqmx.Task() as task:

		
		task.do_channels.add_do_chan('Dev1/port0/line1')       
		task.timing.cfg_samp_clk_timing(100,sample_mode=nidaqmx.constants.AcquisitionType.FINITE,samps_per_chan=200)
		signal=[True,False]*100
		task.write(signal)

		PG.write('OUTP ON') #OF/ON pour allumer éteindre la uW
		PG.write('*WAI')
		print(PG.query('SYSTem:ERRor:NEXT?')+'n_debug=%i'%n_debug)
		n_debug+=1
		PG.write('FREQ:MODE LIST')
		PG.write('*WAI')
		print(PG.query('SYSTem:ERRor:NEXT?')+'n_debug=%i'%n_debug)
		n_debug+=1
		task.start()
		while not task.is_task_done() :
			pass
	PG.write('*RST')
	PG.write('*WAI')
	print(PG.query('SYSTem:ERRor:NEXT?')+'n_debug=%i'%n_debug)




def test_uW():
	n_debug=0
	resourceString4 = 'USB0::0x0AAD::0x0054::110693::INSTR'  # Pour avoir l'adresse je suis allé regarder le programme RsVisaTester de R&S dans "find ressource"

	rm = visa.ResourceManager()
	PG = rm.open_resource( resourceString4 )
	PG.write_termination = '\n'
	PG.write('FREQ 2.85 GHz')
	PG.write('*WAI')
	print(PG.query('SYSTem:ERRor:NEXT?')+'n_debug=%i'%n_debug)
	n_debug+=1
	PG.write('POW -30 dBm')
	PG.write('*WAI')
	print(PG.query('SYSTem:ERRor:NEXT?')+'n_debug=%i'%n_debug)
	n_debug+=1
	PG.write('OUTP ON')
	PG.write('*WAI')
	print(PG.query('SYSTem:ERRor:NEXT?')+'n_debug=%i'%n_debug)
	n_debug+=1
	time.sleep(2)

	PG.write('*RST')
	PG.write('*WAI')
	print(PG.query('SYSTem:ERRor:NEXT?')+'n_debug=%i'%n_debug)
	n_debug+=1

def test_trigg_aom():
	f_acq=1000

	n_acq=100

	t_acq=1


	with nidaqmx.Task() as write :
		with nidaqmx.Task() as sample_clock:
			with nidaqmx.Task() as apd:
				write.do_channels.add_do_chan('Dev1/port0/line2')
				sample_clock.co_channels.add_co_pulse_chan_freq('Dev1/ctr1', freq=f_acq)
				apd.ci_channels.add_ci_count_edges_chan('Dev1/ctr0') 

				sample_clock.timing.cfg_implicit_timing(sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
				apd.timing.cfg_samp_clk_timing(f_acq,source='/Dev1/Ctr1InternalOutput',sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS, samps_per_chan=n_acq)  

				write.timing.cfg_samp_clk_timing(f_acq,sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS,samps_per_chan=n_acq)

				n_sig=int(n_acq/4)
				signal=[False]*n_sig+[True]*2*n_sig+[False]*n_sig

				#write.triggers.start_trigger.cfg_dig_edge_start_trig('/Dev1/ai/StartTrigger') #Ca marche dans les deux sens
				sample_clock.triggers.start_trigger.cfg_dig_edge_start_trig('/Dev1/do/StartTrigger') #Pas de soucis pour le counter ici

				

				write.write(signal)

				sample_clock.start()
				apd.start()
				write.start() #l'odre est hyper important : il faut start celui qui va trigg les autres en dernier
				

				fig,ax=plt.subplots()

				time_origin=time.time()
				while time.time()-time_origin < t_acq :
					data=apd.read(n_acq)
					data=np.array(data)
					PL=(data[1:]-data[:-1])*f_acq
					ax.plot(PL)

					
				#read.start()
	with nidaqmx.Task() as write :
		write.do_channels.add_do_chan('Dev1/port0/line2')
		write.write([False])


				
	plt.show()

class test_iter():
	def __init__(self):
		self.v1=1
		self.v2=2
		self.l=[self.v1,self.v2]
		self.print_v()
	def print_v(self) :
		for v in self.l :
			v=3
		print(self.v1)

def digital2d_out_simple():
	with nidaqmx.Task() as task:

		task.do_channels.add_do_chan('Dev1/port0/line1')
		task.do_channels.add_do_chan('Dev1/port0/line0')
		task.timing.cfg_samp_clk_timing(1000,sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS, samps_per_chan=1000)

		signal1=[True]*500+[False]*500
		signal2=[True]*250+[False]*250+[True]*250+[False]*250

		task.write([signal1,signal2])
		task.start()
		time.sleep(3)

digital2d_out_simple()

