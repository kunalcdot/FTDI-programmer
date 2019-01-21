#from pyftdi.ftdi import Ftdi
from pyftdi.jtag import JtagTool
from pyftdi.jtag import JtagEngine
from pyftdi.bits import BitSequence
import time

DebugPrint = False
debug = False
# debug = True
FastMode = False	## skip SDR_read command.. data verification
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
	presently developed for altera max epld.. can be modified for other devices
	
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
		data_tck = instr_decode(0x0,tck)
		jtagEng.write(data_tck)
		# jtagEng.read(tck)
	elif debug == True:
		jtagEng.read(1800)
		time.sleep(1)
	else:	
		loop = int(tck/4000)
		rem_tck = tck % 4000
		# print(loop)
		# print(rem_tck)
		data_4K_tck = instr_decode(0x0,4000)
		data_rem_tck = instr_decode(0x0,rem_tck)
		for i in range(0,loop):
			
			jtagEng.write(data_4K_tck)
			# jtagEng.read(4000)
			# print("\t4000 tck")	
			
		jtagEng.write(data_rem_tck)
		# jtagEng.read(rem_tck)
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
	if debug == False: ## in debug mode not verifying data
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
		
		
		
def svf_program(jtagEng,file):
##-------////////////////--------

	with open(file, 'r') as f:
	# with open('lcr_epld.svf', 'r') as f:
	# with open('lcr_epld_old.svf', 'r') as f:
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
		elif FastMode :	## skip data read command due to fast mode
			pass
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
	




def main(url,file,f):
	
	print("FTDI JTAG Programming MODULE starts....")
	
	jtagEng = JtagEngine(frequency = f)
	jtagEng.configure(url)
	
	# print(jtagEng._sm.state())
	jtag = EPLDJtagTool(jtagEng)
	dev_id = (jtag.idcode())
	# print (dev_id)
	if dev_id == 34226397:
		print ("\t**********  MAX-V EPLD is detected  ********\n")
	else:
		print ("\tUnknown device is detected with Dev ID = "+str(dev_id)+"\n")
		# exit(0)
		return 0
	# user_code = (jtag.usercode())
	# print (hex(user_code))
	
	t = time.time()
	svf_program(jtagEng,file)
	# dummy_program(jtagEng)
	elapsed_time = time.time() - t
	print("\n\tTime taken = "+str(elapsed_time))
	return 1



		
if __name__ == "__main__":
	
	
	print("jTAG MODULE started....")
	
	jtagEng = JtagEngine(frequency = 1E06)
	jtagEng.configure('ftdi://ftdi:4232h/1')
	
	print(jtagEng._sm.state())
	jtag = EPLDJtagTool(jtagEng)
	dev_id = (jtag.idcode())
	print (dev_id)
	if dev_id == 34226397:
		print ("\t**********  MAX-V EPLD is detected  ********\n")
	else:
		# print("")
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
	# svf_program(jtagEng)
	dummy_program(jtagEng)
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
	
	
	
	