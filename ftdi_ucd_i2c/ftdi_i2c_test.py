from pyftdi.i2c import I2cController, I2cNackError
from binascii import hexlify
import time
import i2cprobe



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
	# return data

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
		time.sleep(1)
		
		# [asciid,id,asciid1,id1] = MFR_date_rd(port)
		id = read_dev_id(port)
		
		print(id)
		# print(asciid)
		# print(id1)
		# print(asciid1)
		print("\n\t***\n")
		
		# print (i)
		# i2c = I2cController()
		# i2c.configure('ftdi://ftdi:4232h/1')
		# port = i2c.get_port(0x35)
		# id = read_dev_id(port)
		# print(id)
		# i2c.terminate()
				
def ucd_write(port,data):
	port.write(data) # data contains command & data array
	
				
if __name__ == '__main__':

	# i2cprobe.main(prnt = False)
	t=time.time()
	i2c = I2cController()

	# Configure the first interface (IF/1) of the FTDI device as an I2C master
	i2c.configure('ftdi://ftdi:4232h/1',frequency=10000)
	i2c.set_retry_count(5)
	# Get a port to an I2C slave device
	port = i2c.get_port(0x35)#4a,4c,4f temp sensor
	port.read(0)
	port.write(b'\x03')	# clear_fault
	
	
	id = read_dev_id(port)
	print(str(id))
	
	
	print ("Reading Status CML ==>\n")
	data = port.exchange([0x7e],1)
	port.read(0)
	data = data.tobytes()
	hex_data = hexlify(data).decode()
	print(hex_data)
	
	
	# BlockWrite,0x35,0xE2,0x050414000104EF
	print("\nSending wrong PEC data")
	# time.sleep(0.1)
	port.write(b'\xe2\x05\x04\x14\x00\x01\x04\xE2')	# wrong PEC
	print("\nChecking PEC")
	# time.sleep(0.1)
	print ("Reading Status CML ==>\n")
	data = port.exchange([0x7e],1)
	port.read(0)
	data = data.tobytes()
	hex_data = hexlify(data).decode()
	print(hex_data)
	i2c.terminate()
	exit(0)
	
	
	# dummy_read(port)
	# id = read_dev_id(port)
	# print(id)
	
	# print(port.frequency())
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