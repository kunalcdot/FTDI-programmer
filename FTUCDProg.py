from pyftdi.i2c import I2cController, I2cNackError
from binascii import hexlify
import time
import i2cprobe
import sys

DebugPrint = False



def ucd_parser(instr_line):
# takes an instruction line and return corresponding custom function
		# ucd is the i2c port object
	cmd = "NOT DEFINED"
	arg =[]
	instr_arr = (instr_line.split(','))
	cmd = instr_arr[0].upper()	# making the command string uppercase
	if DebugPrint:
		print (cmd)
	if cmd == "COMMENT":
		# print(instr_arr)
		comment = instr_arr[1].split('\n')[0]
		
		# print(comment)
		# func = "print('"+str(comment)+"')"
		# print(func)
		# print("\n\n\n\n")
		# func = "pass"
		# func_type = "print"
		cmnt = str(comment)
		arg.append(cmnt)
	
	elif cmd == "BLOCKWRITE" or cmd == "WRITEBYTE" :
		if DebugPrint:
			print(instr_arr)
		data = instr_arr[2][2:] + instr_arr[3][2:]
		if DebugPrint:
			print(data)
		size = len(data)
		
		# port.write([0xe3,0x04,0x00,0x00,0x88,0x20,0x1C])
		write_data = []
		for i in range(0,int(size/2)):
			# write_data += "0x"
			byte = data[i*2:i*2+2]
			write_data.append(int(byte,16))
		# length = len(write_data)
		# write_data = write_data[0:length-1] + ']'	
		if DebugPrint:
			print (write_data)	
		# data1 = 
		# func = "ucd_write(ucd,"+write_data+")"
		# func_type = "trnsc"
		# cmnt = 'NIL'
		arg.append(write_data)
	
	elif cmd == "BLOCKREAD" :
		if DebugPrint:
			print(instr_arr)
		# ucd_block_read(port,rd_cmd,rdlen,data_check): 
		rd_cmd = instr_arr[2]
		data_check = instr_arr[3][2:]
		data_check = data_check.rstrip('\n')
		rdlen = int(len(data_check)/2) ## no. of bytes to be read
		
		if DebugPrint:
			print(rd_cmd)
			print(data_check)
			print(rdlen)
			print(str(data_check))
		# func = "ucd_block_read(ucd,'"+str(data_check)+"',"+str(rd_cmd)+","+str(rdlen)+")" 
		# func = "ucd.BlockRead('"+str(data_check)+"',"+str(rd_cmd)+","+str(rdlen)+")" 
		func = [data_check,rd_cmd,rdlen]
		func_type = "trnsc"
		cmnt = 'NIL'
		arg.append(data_check)
		arg.append(rd_cmd)
		arg.append(rdlen)
		
	elif cmd == "SENDBYTE":		
		if DebugPrint:
			print(instr_arr)
		data = instr_arr[2][2:].split("\n")[0]
		
		send_data = [int(data,16)]
		
		if DebugPrint:
			print(data)
		func = "ucd_byte_write(ucd,[0x"+data+"])"
		func_type = "trnsc"
		cmnt = 'NIL'
		arg.append(send_data)
		
	
	elif cmd == "PAUSE":		
		if DebugPrint:
			print(instr_arr)
		pause_ms = (instr_arr[1])
		pause_cmnt = instr_arr[2].split("\n")[0]
		# func = "print('end')"
		func = "ucd_pause("+pause_ms+",'"+pause_cmnt+"')"
		func_type = "pause"
		cmnt = pause_cmnt
		arg.append(pause_ms)
		arg.append(cmnt)
	
	else:
		print("\t\t** cmd not defined  ==> "+instr_line)
		
		
	
	return [cmd,arg]		
	
	
def ucd_csv_prog(ucd,file):
##-------////////////////--------

	# with open('ucd90160_smbus_flash_script_test.csv', 'r') as f:
	with open(file, 'r') as f:
		
		lines_arr = f.readlines()
		f.close()

	i = 0
	total_instructions = len(lines_arr)
	
	
	print("\tResetting UCD Device\n")
	ucd.reset()
	freq_in_Khz = ucd.get_user_frequency()/1000
	
	t = time.time()
	
	print("\nUCD Programming started @ "+str(freq_in_Khz)+"KHz\n----------\n\t")
	# print()
	log = ""
	for line in lines_arr:
		i += 1 
				
		[cmd,arg] = (ucd_parser(line))
		# print("\n----------\n")
		# print(cmd)
		# print(arg)
		
		if cmd == "BLOCKREAD":
			
			[data_check,rd_cmd,rdlen] = arg
			
			# time.sleep(0.1)
			if ucd.freq_optimize_rd:
				# print (ucd.get_frequency())
				if ucd.get_frequency() > 1000:	#then reduce freq
					print("changing freq")
					time.sleep(0.3)
					ucd.set_frequency(1000)
					time.sleep(0.3)
			# print (ucd.get_frequency())
			rtn_val = ucd.BlockRead(data_check,int(rd_cmd,16),int(rdlen))
			
			if rtn_val == 0:
				## Try again with lower freq
				print("Try again with low frequency")
				time.sleep(0.1)
				ucd.set_frequency(1000)
			
				time.sleep(0.1)
				
				rtn_val = ucd.BlockRead(data_check,int(rd_cmd,16),int(rdlen))
				if rtn_val == 0:
					print("2nd attempt failed\nExiting..")
					exit(0)
				else:
					print("Read Successful..Changing back freq\n")
					time.sleep(0.1)
					ucd.set_frequency(ucd.get_user_frequency())
					time.sleep(0.1)
					
			# rtn_val = ucd.BlockRead(data_check,int(rd_cmd,16),int(rdlen))
			# print (rtn_val)	
		
		
		
		
		
		
		
		elif cmd == "COMMENT":
			# print("cmd is comment")
			[log] = arg	
			if log == "Verifying data flash":
				print("\nVerifying data flash\n")
				ucd.freq_optimize_wr = False
		
			
			
		elif cmd == "PAUSE":
			[ms,log] = arg
			
			ucd.PAUSE(ms,log)	
			
		elif cmd == "SENDBYTE":	
			[data] = arg
			ucd.SENDBYTE(data)
			
		

		elif cmd == "BLOCKWRITE" or "WRITEBYTE":	
			
			if ucd.freq_optimize_wr:
				if ucd.get_frequency() != ucd.get_user_frequency():
					print("changing freq")
					time.sleep(0.3)
					ucd.set_frequency(ucd.get_user_frequency())
					time.sleep(0.3)
			[data] = arg
			# print("Data = "),
			# print (data)
			ucd.BLOCKWRITE(data)		
		else:
			pass
		
		perct_complt = int((i*100)/total_instructions)
		# string = "Finished "+str(i) 
		string1 = "\t\t"+str(perct_complt)+"% Completed..\t"+str(log)
		
		print(string1, end='\r', flush=True)
		# if exec_func:
			
			
			
			
			
			
			# [data_check,rd_cmd,rdlen] = func
			# rtn_val = ucd.BlockRead(data_check,int(rd_cmd,16),int(rdlen))
			# print (rtn_val)
			# if rtn_val == 0:
				# ## Try again with lower freq
				# print("Try again with low frequency")
				# time.sleep(0.1)
				# ucd.set_frequency(1000)
			
				# time.sleep(0.1)
				
				# rtn_val = ucd.BlockRead(data_check,int(rd_cmd,16),int(rdlen))
				# if rtn_val == 0:
					# print("2nd attempt failed\nExiting..")
					# exit(0)
				# else:
					# print("Read Successful..Changing back freq\n")
					# time.sleep(0.1)
					# ucd.set_frequency(ucd.get_user_frequency())
					# time.sleep(0.1)
					
			# rtn_val = ucd.BlockRead(data_check,int(rd_cmd,16),int(rdlen))
			# print (rtn_val)	
				
			
		# print("\n\t"+str(perct_complt)+"% Completed..", end='\r', flush=True)
	
	
	
	
	elapsed_time = time.time() - t
	print("\n\nUCD Programming Successfully completed\nTime taken = "+str(elapsed_time))
	print("-------------------------------------------------------------")
		

class UCDProgrammer:
	"""
	FTDI UCD programming class through i2c
	
	"""
	
	ucd_DevAdd = None
	i2c = I2cController()
	ucd_Freq = 0			# running ucd freq
	Default_Freq = 5000	# 5KHz
	user_freq = 0			# frequency requested by user during initialization
	port = 0
	# freq_optimize = True
	freq_optimize_wr = True
	freq_optimize_rd = True
	
	def __init__(self, url,UserFreq,Fopt): # if UserFreq = None, Default_Freq will be assigned
		self._url = url
		if Fopt == False:
			self.freq_optimize_wr = False
			self.freq_optimize_rd = False
		
		if UserFreq == None:
			self.ucd_Freq = self.Default_Freq
			self.user_freq = self.Default_Freq
		else:
			self.ucd_Freq = UserFreq
			self.user_freq = UserFreq

	def configure(self):
		self.i2c.configure(self._url,frequency=self.ucd_Freq)
		self.i2c.set_retry_count(15)
	
		if self.get_dev_add() == None:
			print("Slave Device address is not defined")
			exit(0)
		else:
			self.port = self.i2c.get_port(self.ucd_DevAdd)
	

	def set_dev_add(self,add):	
		"""
		Set slave device(UCD device) I2C add 
		"""
		self.ucd_DevAdd = add
		
	def get_dev_add(self):	
		"""
		Get slave device(UCD device) I2C add 
		"""
		return self.ucd_DevAdd
	

	def set_frequency(self,freq):	
		"""
		Set I2C frequency 
		"""
		self.ucd_Freq = freq
		self.configure()
	
	def get_frequency(self):	
		"""
		Get I2C frequency 
		"""
		return self.ucd_Freq
	
	def get_user_frequency(self):	
		"""
		Get I2C frequency as requested by user 
		"""
		return self.user_freq
		
	def reset(self):
		"""
		Reset UCD device and wait for 2second so that device comes up after reset
		"""
		# SendByte,0x35,0xDB
		self.port.write([0xdb]) # data contains command(1byte)
		time.sleep(2)
		self.port.read(0)	
		
		
	def ClrErr(self):	
		"""
		Clear all error in the device.. 
		Should be used at the starting of programming before checking any new PEC error
		"""
		self.port.write(b'\x03')	
	
	def PECcheck(self):	
		"""
		check status of PEC error
		"""
	
		# print ("Reading Status CML ==>\n")
		data = self.port.exchange([0x7e],1)
		self.port.read(0)
		data = data.tobytes()
		hex_data = hexlify(data).decode()
		bin_data = bin(int(hex_data, 16))[2:].zfill(8)
		PECbit_pos = 5
		PECbit = bin_data[7-PECbit_pos] ## PECbit_pos = 5
		if str(PECbit) == "0":
			# No error
			return 1
		else:
			return 0
		if DebugPrint:
			print(hex_data)
			print(bin_data)	
			
		
		
		
	def BlockRead(self,data_check,rd_cmd,rdlen): 
		# port.write(data) # data contains command & data array
		data_rd = self.port.exchange([rd_cmd],rdlen)
		data = data_rd.tobytes()
		hex_data_rd = hexlify(data).decode()
		if str(hex_data_rd).lower() != str(data_check).lower():
			print("Data verification error\nData Read from device = "+str(hex_data_rd)+"\n\tExpected data = "+str(data_check).lower())
			return 0
		else:
			return 1
			
	def BLOCKWRITE(self,data): # WriteByte & BlockWrite
		self.port.write(data) # data contains command & data array
		
		retry = 10
		while retry > 1: 
			time.sleep(0.02)
			if self.PECcheck() == 0:
				##error ... Retry
				print("**PEC Error Detected..Trying again")
				self.ClrErr()
				self.port.write(data)
				retry = retry -1
			else:
				break
		if retry <= 1:
			print("PEC Error retry count failed..\nExiting..")
			exit(0)	

	def SENDBYTE(self,data):
		self.port.write(data) # data contains command(1byte)
		time.sleep(2)			## in case of ucd send byte is for reset.. hence 2s sleep
		self.port.read(0)
		
		
	def PAUSE(self,pause_ms,pause_cmnt):
	# print(pause_cmnt)
		pause_ms = float(pause_ms)
		if pause_ms < 20: # then wait for 20ms
			pause_ms = 20
		time.sleep(pause_ms/1000)		


def find_ucd(url):
	# print("Scanning I2C Bus of FTDI channel 0\n")
	## Note I2C probe is checking only on channel 0
	devices = i2cprobe.main(prnt = False)
	no_of_dev = len(devices)
	if no_of_dev == 0:
		return 0
	ucd_found = False
	for dev_add in devices:
		
		# print(dev_add)
		ucd = UCDProgrammer(url,1000,False)
	
	
		ucd.set_dev_add(int(dev_add,16))
		ucd.configure()
		try:
			if (ucd.BlockRead("1B5543443930313630",0xfd,9)): ## ucd90160
				ucd_found = True
				break
		except I2cNackError:
			pass
			# print("Nackerror")
	if ucd_found:
		return int(dev_add,16)	
	else:
		return 0
	
def main(url,file,f,Fopt):
	
	print("Scanning I2C Bus\n")
	ucd_add=(find_ucd(url))
	if ucd_add != 0:
		print("UCD device is detected @ "+hex(ucd_add)+"\n")
	else:
		print("No device is detected\nEnsure device address is within 0x0 - 0x78 and the device is powered up\nExiting\n")
		return 0
	
	ucd = UCDProgrammer(url,f,Fopt)	## make it true for freq optimization
	ucd.set_dev_add(ucd_add)
	ucd.set_frequency(f)
	ucd_csv_prog(ucd,file)
	return 1
	
		
if __name__ == '__main__':

	url = 'ftdi://ftdi:4232h/1'
	f = 5000
	file = 'ucd90160_smbus_flash_script.csv'
	Fopt = False # freq optimization
	main(url,file,f,Fopt)