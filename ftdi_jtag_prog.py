#from pyftdi.ftdi import Ftdi
from pyftdi.jtag import JtagTool
from pyftdi.jtag import JtagEngine
from pyftdi.bits import BitSequence
import time

DebugPrint = False
debug = True
## -- #define 
# Should match the tested device
JTAG_INSTR = {'SAMPLE': BitSequence('0000000101', msb=True, length=10),
              'PRELOAD': BitSequence('0000000101', msb=True, length=10),
              'IDCODE': BitSequence('0000000110', msb=True, length=10),
              'BYPASS': BitSequence('1111111111', msb=True, length=10),
			  'EXTEST': BitSequence('0000001111', msb=True, length=10),
			  'HIGHZ': BitSequence('0000001011', msb=True, length=10),
			  '203': BitSequence('1000000011', msb=True, length=10),
			  '205': BitSequence('1000000101', msb=True, length=10),
			  'USERCODE': BitSequence('0000000111', msb=True, length=10)
			  
			  
			  }
			  
JTAG_DATA = {'0441': BitSequence('0000010001000001', msb=True, length=16),
             '205': BitSequence('1000000101', msb=True, length=16)
			  
			  }
			  

Boundary_Length = 756

ENDIR = 'pause_ir'
ENDDR = 'run_test_idle'
##-----------------------------------------

class EPLDJtagTool:
	"""
	A helper class with facility functions
	presently developed for max10 epld.. can be modified for other devices
	
	A configured jtagEngine needs to be provided as arg
	"""
	
	def __init__(self, engine):
		self._engine = engine
		self._engine.reset()

	def idcode(self):
	
		instruction = JTAG_INSTR['IDCODE']
		self._engine.write_ir(instruction)
		idcode = self._engine.read_dr(32)
		self._engine.go_idle()
		return int(idcode)
        # print("IDCODE (idcode): 0x%08x" % int(idcode))	
		
	def usercode(self):
	
		instruction = JTAG_INSTR['USERCODE']
		self._engine.write_ir(instruction)
		idcode = self._engine.read_dr(32)
		self._engine.go_idle()
		return int(idcode)
        # print("IDCODE (idcode): 0x%08x" % int(idcode))	
	
	def write_pin(self,pin,data):
		#at predent bsc group no is used instead of pin
		BSCgroup = pin	##parse bsdl file & find BSCgroup from pin no
		## BSCgroup -->in cell0
		## BSCgroup+1 -->OE		cell1
		## BSCgroup+2 -->Out	cell2
		##----	change ir to EXTEST
		instruction = JTAG_INSTR['EXTEST']
		self._engine.write_ir(instruction)
		## shift_dr all_ones except the pin to be driven
		all_ones =""
		for i in range (0,Boundary_Length):
			all_ones += '1'
		shift_data = all_ones[:(BSCgroup*3+1)]+'0'+str(data)+all_ones[(BSCgroup*3+3):]
		print (shift_data)
		self._engine.write_dr(BitSequence(shift_data))
		self._engine.go_idle()
	
	def read_pin(self,pin):
		## read specific pin value @ sample instruction... can be used with internal logic
		BSCgroup = pin	##parse bsdl file & find BSCgroup from pin no
		## BSCgroup -->in cell0
		## BSCgroup+1 -->OE		cell1
		## BSCgroup+2 -->Out	cell2
		# self._engine.shift_dr()
		self._engine.write_ir(JTAG_INSTR['SAMPLE'])
		self._engine.change_state('shift_dr')
		data = self._engine._ctrl.read(Boundary_Length)
		
		self._engine.go_idle()
		return data[BSCgroup*3]





def dummy_svf_check():
	
	
# checking svf commands...
	print("\nSending SIR commands BYPASS-->\n")
	# SIR 10 TDI (006);	==>	
	# self.change_state('shift_ir')
	# self._ctrl.write(instruction)
	# self.change_state(State specified by ENDIR)
	# SIR -1
	instruction = instr_decode(0x3ff,10)
	
	
	jtagEng.change_state('shift_ir')
	jtagEng._ctrl.write(instruction)
	jtagEng.change_state(ENDIR)
	
	# *********************		***************
	jtagEng.go_idle()	## RUNTEST
	
	print ("\nwaiting for 1800 TCK @ idle")
	jtagEng.read(1800)
	
	# *********************		***************
		## SDR-1
	
	print ("\nSending SDR-1 for reading -->")
	print(int(jtagEng.read_dr(32)))
	jtagEng.change_state(ENDDR)
	
	# *********************		***************
		## SIR -2
	
	print ("\nSending SIR for dev id -- IDCODE -->")
	instruction = instr_decode(0x6,10)
	
	
	jtagEng.change_state('shift_ir')
	jtagEng._ctrl.write(instruction)
	jtagEng.change_state(ENDIR)
	
	# *********************		***************
	jtagEng.go_idle()	## RUNTEST
	
	print ("\nwaiting for 1800 TCK @ idle")
	jtagEng.read(1800)
	#---------------------------------------------
	
	# *********************		***************
		## SDR-2
	
	print ("\nSending SDR-2 for reading -->")
	print(int(jtagEng.read_dr(32)))
	jtagEng.change_state(ENDDR)

	
def instr_decode(instr,length):
#	take instr in hex_string and return bitseq
	
	# bin_instr = bin(int(instr,16))[2:]
	bin_instr = bin(instr)[2:]
	size = len(bin_instr)
	if size == length:
		if DebugPrint:
			print("exact size.. nothing to be done")
	else:
		if DebugPrint:
			print("append zero")
		no_of_zero = length - size
		y = '0'
		bin_instr = y*no_of_zero + bin_instr
	if DebugPrint:
		print (bin_instr)
	return BitSequence(bin_instr, msb=True, length=length)

	
def SIR(jtagEng,instr,length):
	# instruction = JTAG_INSTR['203']
	# jtagEng.change_state('shift_ir')
	# jtagEng._ctrl.write(instruction)
	# jtagEng.change_state(ENDIR)
	instruction = instr_decode(instr,length)
	jtagEng.change_state('shift_ir')
	jtagEng._ctrl.write(instruction)
	jtagEng.change_state(ENDIR)
	
def RUNTEST(jtagEng,tck):	
	if str(jtagEng._sm.state()) != 'run_test_idle':
		jtagEng.go_idle()	## RUNTEST
	
	# if tck > 4000 then split into multiple part
	if tck < 4001:
		jtagEng.read(tck)
	elif debug == True:
		jtagEng.read(1800)
		time.sleep(1)
	else:	
		loop = int(tck/4000)
		rem_tck = tck % 4000
		# print(loop)
		# print(rem_tck)
		for i in range(0,loop):
			
			jtagEng.read(4000)
			# print("\t4000 tck")	
			
		jtagEng.read(rem_tck)
		# print("\t"+str(rem_tck)+" tck")	
	
def SDR_write(jtagEng,data,length):
	# SDR 16 TDI (0441);
	data = instr_decode(data,length)
	if DebugPrint:
		print ("\nSending write SDR -->")
	((jtagEng.write_dr(data)))
	jtagEng.change_state(ENDDR)

def SDR_read(jtagEng,data_check,length):
	data_check = instr_decode(data_check,length)
	data = jtagEng.read_dr(length)
	jtagEng.change_state(ENDDR)
	# verify the read data
	if data == data_check:
		# print ("Data ok = "+hex(int(data)))
		pass
	
	else:
		print("Incorrect data read..Data Read= "+hex(int(data))+" Data Expected = "+hex(int(data_check))+"\nExiting..")
		jtagEng.reset()
		jtagEng.close()
		exit(0)

def STATE(jtagEng,state_name):
	## only idle test is defined
	if state_name == "IDLE":
		if str(jtagEng._sm.state()) != 'run_test_idle':
			print(jtagEng._sm.state())
			jtagEng.go_idle()
	else:
		print("No support for argument in STATE command = "+state_name)
		
		
		
def svf_program(jtagEng):
##-------////////////////--------

	# with open('lcr_epld_test.svf', 'r') as f:
	# with open('lcr_epld.svf', 'r') as f:
	with open('lcr_epld_old.svf', 'r') as f:
		lines_arr = f.readlines()
		f.close()

	# print (lines_arr)
	# print("\n\n***\n")
	# remove the commented section
	instr_set = [x for x in lines_arr if x[0] != '!']
	# print(instr_set)
	total_instructions = len(instr_set)
	i = 0
	for line in instr_set:
		
		exec(decode_cmd(line))
		i += 1
		if i%1000 == 0:
			print("\t\t Instructions executed = "+str(i)+" of "+str(total_instructions))
	
def decode_cmd(instr_line):
# takes an instruction line and return corresponding custom function
	
	instr_arr = (instr_line.split(' '))
	cmd = instr_arr[0]
	if cmd == "SIR":
		#SIR(jtagEng,instr,length)
		length = instr_arr[1]
		instr_code = instr_arr[3]
		# print (instr_code)
		word1 = instr_code.split('(')[1]
		word2 = word1.split(')')[0]
		# print (word2)
		instr = word2
		func = "SIR(jtagEng,0x"+instr+","+length+")"
		# print (func)
		# exec(func)
	
	elif cmd == "SDR":
		#SDR_write(jtagEng,data,length):
		# SDR_read(jtagEng,data_check,length):
		length = instr_arr[1]
		new_cmd = instr_line.split('TDO')
		if len(new_cmd) == 1: ## no TDO; so it is a write command
			instr_code = instr_arr[3]
			# print (instr_code)
			word1 = instr_code.split('(')[1]
			word2 = word1.split(')')[0]
			# print (word2)
			data = word2
			func = "SDR_write(jtagEng,0x"+data+","+length+")"
			# print (func)	
		else:	## data read command
			data_check_str = new_cmd[1]
			data_check = (data_check_str.split('(')[1].split(')')[0])
			func = "SDR_read(jtagEng,0x"+data_check+","+length+")"
			# print (func)	
			
	elif cmd == "RUNTEST":		
	# RUNTEST(jtagEng,tck)	
	# RUNTEST IDLE 18003 TCK ENDSTATE IDLE;	
		word1 = instr_line.split("TCK")[0].split(" ")
		tck = word1[len(word1) - 2]
		# if int(tck) > 1800:
			# tck = '1800'		## to be checked..
		# print(tck)
		func = "RUNTEST(jtagEng,"+tck+")"
		# print (func)	
	
	elif cmd == "STATE":		
	
		state_name = instr_arr[1].split(';')[0]
		func = "STATE(jtagEng,'"+str(state_name)+"')"
		# print (func)
	
	
	else:
		print("\t\t** cmd not defined  ==> "+instr_line)
		func = "print('not defined')"
	return func	
	

def dummy_program(jtagEng):			
## direct method	
#	***
		
	# SDR_write(jtagEng,0x0441,16)			# SDR 16 TDI (0441);
	# SIR(jtagEng,0x205,10)		# SIR 10 TDI (205);
	# RUNTEST(jtagEng,93)			# RUNTEST 93 TCK;
	# SDR_read(jtagEng,0x8232,16)	# SDR 16 TDI (FFFF) TDO (8232) MASK (FFFF);
	

#############################################################################

	# SDR 16 TDI (7FFF);
	# RUNTEST 1800 TCK;
	for i in range(0,2000):
		SDR_write(jtagEng,0xffff,16)
		RUNTEST(jtagEng,1800)

	
if __name__ == "__main__":
	
	
	print("jTAG MODULE started....")
	
	jtagEng = JtagEngine()
	jtagEng.configure('ftdi://ftdi:4232h/1')
	
	print(jtagEng._sm.state())
	jtag = EPLDJtagTool(jtagEng)
	dev_id = (jtag.idcode())
	print (dev_id)
	if dev_id == 34226397:
		print ("\t**********  MAX-V EPLD is detected  ********\n")
	else:
		exit(0)
	
	user_code = (jtag.usercode())
	print (hex(user_code))
	
	
	# t = (time.time() *1000)
	# for i in range(0,1000):	
		# SDR_write(jtagEng,0xffff,16)
		# RUNTEST(jtagEng,93)
	
	# elapsed_time = (time.time()*1000) - t
	# print("\n\tTime taken = "+str(elapsed_time))
	x=input("ctrl+c")
	
	
	
	
	
	# dummy_svf_check()
	# print(jtagEng._sm.state())
	t = time.time()
	svf_program(jtagEng)
	# dummy_program(jtagEng)
	elapsed_time = time.time() - t
	print("\n\tTime taken = "+str(elapsed_time))
	# print(jtagEng._sm.state())
	
	# jtag.write_pin(48,1)
	
	# while 1:
		
	
		# # print(jtag.read_pin(48))
		# print(jtag.read_pin(207))
		# time.sleep(1)
	
	# x = input("ctrl+C")
	# jtag.write_pin(48,0)
	# print(jtag.read_pin(48))
	# x = input("ctrl+C")
	# jtag.write_pin(49,0)
	# x = input("ctrl+C")
	# jtag.write_pin(49,1)
	# jtag.write_pin(48,0)
	# x = input("ctrl+C")
	# print("Terminating Connection..")
	jtagEng.close()
	
	# data = sample(jtagEng)
	
	# highz(jtagEng)
	# data = jtagEng.read_dr(Boundary_Length)
	# print (int(data))
	# x = input("ctrl+C")
	# data = sample(jtagEng)
	# x = input("ctrl+C")
	
	# print("141-146")
	# print(data[141:147])
	# print("\n\n")
	
	# print("147-152")
	# print(data[147:153])
	# print("\n\n")
	
	# print("152-157")
	# print(data[152:158])
	# print("\n\n")
	
	# print("0-8")
	# print(data[0:9])
	# print("\n\n")
	###----bs test ----
	
	# bs = BitSequence("11101100")
	
	# update = [141,1,142,1,143,1,144,1,145,1,146,1,147,1,148,1,149,1,150,1,151,1,152,1]
	
	# print (data)
	
	# new_data = update_bs(data,update) ## to be written
	# d=""
	# for i in range(0,756):
		# d +='0'
	# new_data = BitSequence(d)
	# new_data1 = BitSequence('1')
	# # extest(jtagEng,new_data)
	# extest(jtagEng,new_data1)
	# print (new_data)
	# time.sleep(0.5)
	
	# print("\n\nSampling again")
	
	# data = jtagEng.read_dr(Boundary_Length)
	# print (int(data))
	# x = input("ctrl+C")
	# data = sample(jtagEng)
	# print(int(data))
	
	
	# jtagEng.close()
	# # print("141-146")
	# # print(data[141:147])
	# # print("\n\n")
	
	# # print("141-146")
	# # print(data[141:147])
	# print("\n\n")
	
	
	