from pyftdi.i2c import I2cController, I2cNackError
from binascii import hexlify
import time
import i2cprobe
import sys

DebugPrint = False

def MFR_date_rd(port):
	# port.read(0)
	# port.write([0x9d])
	
	data = port.exchange([0x9d], 4,relax=False)
	time.sleep(1)
	data1 = port.read(2,start =False,relax=True)
	time.sleep(1)
	port.read(0)
	time.sleep(0.1)
	# data = port.read(7)
	# time.sleep(1)
	# print (data)
	data = data.tobytes()
	# print(data)
	hex_data = hexlify(data).decode()
	# print(hex_data)
	
	data1 = data1.tobytes()
	# print(data)
	hex_data1 = hexlify(data1).decode()
	
	
	
	return [data,hex_data,data1,hex_data1]


def read_dev_id(port):
	data = port.exchange([0xfd], 28)
	time.sleep(1)
	port.read(0)
	# print (data)
	data = data.tobytes()
	# print(data)
	hex_data = hexlify(data).decode()
	# print(hex_data)
	return hex_data

def i2c_reset(i2c):
	print('hi')
	
	# try:
	
	# for addr in range(i2c.HIGHEST_I2C_ADDRESS-62):
	port = i2c.get_port(0xc)
	try:
		port.read(0)
		
		# print(hex(addr))
		
	except I2cNackError:
					# slaves.append('.')
		print('fail')

def i2c_write(i2c,port,data):
	
	port.write(data)

def dummy_write(i2c,port,data):
	
	for i in range(0,10):
		port.write(data)
		

def dummy_read(port):
	
	for i in range(0,10):
		# time.sleep(1)
		
		[asciid,id,asciid1,id1] = MFR_date_rd(port)
		# id = read_dev_id(port)
		
		print(id)
		print(asciid)
		print(id1)
		print(asciid1)
		print("\n\t***\n")
		
		# print (i)
		# i2c = I2cController()
		# i2c.configure('ftdi://ftdi:4232h/1')
		# port = i2c.get_port(0x35)
		# id = read_dev_id(port)
		# print(id)
		# i2c.terminate()
def ucd_reset(port):

# SendByte,0x35,0xDB
	port.write([0xdb]) # data contains command(1byte)
	time.sleep(2)
	port.read(0)

def ucd_clr_err(port):	
	port.write(b'\x03')	
	
def ucd_PEC_check(port):	# check status of PEC error
	# print ("Reading Status CML ==>\n")
	data = port.exchange([0x7e],1)
	port.read(0)
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
	
	print(hex_data)
	print(bin_data)
	
def ucd_write(port,data): # WriteByte & BlockWrite
	port.write(data) # data contains command & data array
	
	retry = 10
	while retry > 1: 
		time.sleep(0.02)
		if ucd_PEC_check(port) == 0:
			##error ... Retry
			print("**PEC Error Detected..Trying again")
			ucd_clr_err(port)
			port.write(data)
			retry = retry -1
		else:
			break
	if retry <= 1:
		print("PEC Error retry count failed..\nExiting..")
		exit(0)

def ucd_block_read(port,data_check,rd_cmd,rdlen): 
	# port.write(data) # data contains command & data array
	data_rd = port.exchange([rd_cmd],rdlen)
	data = data_rd.tobytes()
	hex_data_rd = hexlify(data).decode()
	if str(hex_data_rd).lower() != str(data_check).lower():
		print("Data verification error\nData Read from device = "+str(hex_data_rd)+"\n\tExpected data = "+str(data_check).lower()+"\nExiting...")
		sys.exit(0)
	
	
	# verify data read..
	
def ucd_byte_write(port,data):
	port.write(data) # data contains command(1byte)
	time.sleep(2)
	port.read(0)
	
def ucd_pause(pause_ms,pause_cmnt):
	# print(pause_cmnt)
	if pause_ms < 20: # then wait for 20ms
		pause_ms = 20
	time.sleep(pause_ms/1000)


def ucd_parser(ucd,instr_line):
# takes an instruction line and return corresponding custom function
		# ucd is the i2c port object
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
		func = "pass"
		func_type = "print"
		cmnt = str(comment)
	
	elif cmd == "BLOCKWRITE" or cmd == "WRITEBYTE" :
		if DebugPrint:
			print(instr_arr)
		data = instr_arr[2][2:] + instr_arr[3][2:]
		if DebugPrint:
			print(data)
		size = len(data)
		
		# port.write([0xe3,0x04,0x00,0x00,0x88,0x20,0x1C])
		write_data = "["
		for i in range(0,int(size/2)):
			write_data += "0x"
			write_data += data[i*2:i*2+2]
			write_data += ","
		length = len(write_data)
		write_data = write_data[0:length-1] + ']'	
		if DebugPrint:
			print (write_data)	
		# data1 = 
		func = "ucd_write(ucd,"+write_data+")"
		func_type = "trnsc"
		cmnt = 'NIL'
	
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
	
	elif cmd == "SENDBYTE":		
		if DebugPrint:
			print(instr_arr)
		data = instr_arr[2][2:].split("\n")[0]
		if DebugPrint:
			print(data)
		func = "ucd_byte_write(ucd,[0x"+data+"])"
		func_type = "trnsc"
		cmnt = 'NIL'
	
	elif cmd == "PAUSE":		
		if DebugPrint:
			print(instr_arr)
		pause_ms = (instr_arr[1])
		pause_cmnt = instr_arr[2].split("\n")[0]
		# func = "print('end')"
		func = "ucd_pause("+pause_ms+",'"+pause_cmnt+"')"
		func_type = "pause"
		cmnt = pause_cmnt
	
	
	else:
		print("\t\t** cmd not defined  ==> "+instr_line)
		func = "print('not defined')"
		func_type = "print"
		cmnt = 'not defined'
	
	return [func,func_type,cmnt]	
	
	
def ucd_csv_prog(ucd):
##-------////////////////--------

	with open('ucd90160_smbus_flash_script_test.csv', 'r') as f:
	# with open('ucd90160_smbus_flash_script.csv', 'r') as f:
		lines_arr = f.readlines()
		f.close()

	i = 0
	total_instructions = len(lines_arr)
	print("\nUCD Programming started\n----------\n\t")
	log = ""
	for line in lines_arr:
		i += 1 
		# print (line)
		# try:
		# exec(ucd_parser(ucd,line))
		
		[func,func_type,cmnt] = (ucd_parser(ucd,line))
		if func_type == "print":
			log = cmnt
			exec_func = False
		elif func_type == "pause":	
			log = cmnt
			exec_func = True
		elif func_type == "trnsc":
			exec_func = True
		
		perct_complt = int((i*100)/total_instructions)
		# string = "Finished "+str(i) 
		string1 = "\t\t"+str(perct_complt)+"% Completed..\t"+str(log)
		
		print(string1, end='\r', flush=True)
		if exec_func:
			
			[data_check,rd_cmd,rdlen] = func
			rtn_val = ucd.BlockRead(data_check,int(rd_cmd,16),int(rdlen))
			print (rtn_val)
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
					
			rtn_val = ucd.BlockRead(data_check,int(rd_cmd,16),int(rdlen))
			print (rtn_val)	
				
			
		# print("\n\t"+str(perct_complt)+"% Completed..", end='\r', flush=True)
	
	
	
	
	
	print("\n\nUCD Programming Successfully completed\n")	
		

class UCDProgrammer:
	"""
	FTDI UCD programming class through i2c
	
	"""
	
	ucd_DevAdd = None
	i2c = I2cController()
	ucd_Freq = 0			# running ucd freq
	Default_Freq = 100000	# 100KHz
	user_freq = 0			# frequency requested by user during initialization
	port = 0
	
	def __init__(self, url,UserFreq): # if UserFreq = None, Default_Freq will be assigned
		self._url = url
		
		if UserFreq == None:
			self.ucd_Freq = self.Default_Freq
			self.user_freq = self.Default_Freq
		else:
			self.ucd_Freq = UserFreq
			self.user_freq = UserFreq

	def configure(self):
		self.i2c.configure(self._url,frequency=self.ucd_Freq)
		self.i2c.set_retry_count(10)
	
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
			
		



	
if __name__ == '__main__':

	# i2cprobe.main(prnt = False)
	# test()
	
	
	ucd = UCDProgrammer('ftdi://ftdi:4232h/1',10000)
	print(ucd.get_user_frequency())
	ucd.set_dev_add(0x35)
	ucd.set_frequency(10000)
	ucd_csv_prog(ucd)
	x=input('ctrl+C')
	
	
	
# ###///////////////////////////////////////	
	# i2c = I2cController()
	# print("i2c1")
	# i2c.configure('ftdi://ftdi:4232h/1',frequency=400000)
	# port_2k = i2c.get_port(0x35)
	# print("i2c 2")
	# i2c.configure('ftdi://ftdi:4232h/1',frequency=1000)
	# port_5k = i2c.get_port(0x35)
	
	
	
	# ucd_block_read(port_2k,"1B55434439303136307C322E332E342E303030307C31313036303300",0xfd,28)
	# ucd_block_read(port_5k,"1B55434439303136307C322E332E342E303030307C31313036303300",0xfd,28)
	
	# x=input('ctrl+C')
	# data_rd = port_2k.exchange([0xfd],28)
	# data = data_rd.tobytes()
	# hex_data_rd = hexlify(data).decode()
	# print(hex_data_rd)
	# print("\n----------\n")
	# time.sleep(1)
	# data_rd = port_5k.exchange([0xfd],28)
	# data = data_rd.tobytes()
	# hex_data_rd = hexlify(data).decode()
	# print(hex_data_rd)
	
	# x=input('ctrl+C')
	# t=time.time()
	# # i2c = I2cController()

# ###///////////////////////////////////////	
	
	
	pwrmng = UCDProgrammer('ftdi://ftdi:4232h/1',None)
	print(pwrmng.get_user_frequency())
	pwrmng.set_dev_add(0x35)
	pwrmng.set_frequency(10000)
	print(pwrmng.get_frequency())
	# pwrmng.configure()
	
	while 1:
		id_rd = (pwrmng.BlockRead("1B55434439303136307C322E332E342E303030307C31313036303300",0xfd,28))
		print(id_rd)
		if id_rd ==0:
			print("rd again with low frequency")
			time.sleep(0.1)
			pwrmng.set_frequency(1000)
			
			time.sleep(0.1)
		else:
			break
	print(pwrmng.get_user_frequency())		
			# pwrmng.configure()
	# time.sleep(0.5)
	
	x=input('ctrl+C')
	print(pwrmng.BlockRead("1B55434439303136307C322E332E342E303030307C31313036303300",0xfd,28))
	
	x=input('ctrl+C')
	
	i = 0
	while i <5:	
		if pwrmng.BlockRead("1B55434439303136307C322E332E342E303030307C31313036303300",0xfd,28) == 0:
			i += 1
			# pwrmng.terminate()
			time.sleep(0.1)
			pwrmng.set_frequency(1000)
			pwrmng.configure()
			time.sleep(0.1)
			
	
	
	
	
	
	
	# Configure the first interface (IF/1) of the FTDI device as an I2C master
	i2c.configure('ftdi://ftdi:4232h/1',frequency=2000)
	i2c.set_retry_count(10)
	# Get a port to an I2C slave device
	port = i2c.get_port(0x35)#4a,4c,4f temp sensor
	ucd = port
	ucd_clr_err(ucd)
	ucd_PEC_check(ucd)
	# x=input('ctrl+C')
	
	print("\tResetting UCD device\n")
	ucd_reset(ucd)
	# ucd_block_read(ucd,0xfd,28,"1B55434439303136307C322E332E342E303030307C31313036303300")
	
	
	
	# instr_line = "BlockRead,0x35,0xFD,0x1B55434439303136307C322E332E342E303030307C31313036303300"
	# instr_arr = (instr_line.split(','))
	# rd_cmd = instr_arr[2]
	# data_check = instr_arr[3][2:]
	# rdlen = int(len(data_check)/2) ## no. of bytes to be read
		
	# # if DebugPrint:
	# print(rd_cmd)
	# print(data_check)
	# print(rdlen)
	# print(str(data_check))
	# func = "ucd_block_read(ucd,'"+str(data_check)+"',"+str(rd_cmd)+","+str(rdlen)+")" 
	# print(func)
	# print("\n----------\n")
	# exec(func)
	
	
	
	
	
	
	
	
	ucd_csv_prog(ucd)
	i2c.terminate()
	elapsed_time = time.time() - t
	print("Time taken = "+str(elapsed_time))
	
	
	x=input('ctrl+C')
	# dummy_write(i2c,port,b'\x00\x01')
	# port.write(b'\x9d\x30\x31\x32\x31\x30\x31')
	# port.write(b'\x9d\x30\x31\x35')
	
	# BlockWrite,0x35,0xE2,0x050414 00 0104EF
	
	
	# BlockWrite,0x35,0xE2,0x050400000104D0
	# BlockWrite,0x35,0xE3,0x04000088201C
	port.write(b'\xe2\x05\x04\x00\x00\x01\x04\xD0')
	# port.write(b'\xe3\x04\x00\x00\x88\x20\x1C')
	port.write([0xe3,0x04,0x00,0x00,0x88,0x20,0x1C])
	
	# Comment,Erasing data flash ...
	# BlockWrite,0x35,0xE2,0x050414000104EF
	# BlockWrite,0x35,0xE3,0x0400000100F7
	
	
	port.write(b'\xe2\x05\x04\x14\x00\x01\x04\xEF')
	port.write(b'\xe3\x04\x00\x00\x01\x00\xF7')
	
	
	
	# port.write(b'\xe2\x05\x04\x14\x00\x01\x04\x14\xef')
	# port.write(b'\xe2\x05\x04\x14\x00\x01\x04\x14\xef')
	
	# i2c.write(address=0x35, out=[0x9d,0x31,0x32,0x33], relax=True)
	port.read(0)
	# dummy_read(port)
	# id = read_dev_id(port)
	# print(id)
	
	x=input('ctrl+C')
	
	# i2c_reset(i2c)
	
	print(port.poll(write=True))
	id = read_dev_id(port)
	print(id)
	print("\n\t**again..\n")
	
	i2cprobe.main(prnt = False)
	i2c.terminate()
	
	i2c = I2cController()
	i2c.configure('ftdi://ftdi:4232h/1')
	port = i2c.get_port(0x35)
	port.write_to(0x00, b'\x01')
	data = port.exchange([0x0], 1)
	# print (data)
	data = data.tobytes()
	# print(data)
	hex_data = hexlify(data).decode()
	print(hex_data)
	i2cprobe.main(prnt = False)
	
	
	
	
	elapsed_time = time.time() - t
	print("\tTime taken = "+str(elapsed_time))
	# i2cprobe.main(prnt = False)
	# time.sleep(5)
	# id = read_dev_id(port)
	# print(id)
	
	# port.write_to(0x00, b'\x00')

	# data = port.read_from(0x0,1)
	# data = port.exchange([0x0], 1)
	# time.sleep(5)
	# port.write_to(0x00, b'\x01')
	# port.write_to(0x00, b'\x00')
	# port.write_to(0x00, b'\x01')
	# port.write_to(0x00, b'\x00')

	# port.write(b'\x02\xa5\xff', relax=True, start=True) # write 4 bytes, without neither emitting the start or stop sequence
	# port.write(b'\x00\x00', relax=True, start=True) # write 4 bytes, without neither emitting the start or stop sequence
	# # time.sleep(0.1)
	# data = (port.read(1, start = True,relax=True)) # send start & slave add

	

	# port.write([0], relax=False, start=False) # write 4 bytes, without neither emitting the start or stop sequence


	# print(port.read(0, start = True,relax=False)) # send start & slave add
	# port.write([0], relax=False, start=False) # write 4 bytes, without neither emitting the start or stop sequence
	# print(port.read(0, start = True,relax=False)) # send start & slave add
	# print(port.read(2, start=False,relax = True))



	i2c.terminate()

	# Send one byte, then receive one byte
	# print(slave.exchange([0x02], 1))

	# Write a register to the I2C slave
	# slave.write_to(0x06, b'\x00')

	# # Read a register from the I2C slave
	# slave.read_from(0x02, 1)