# Parse a csv file to program ucd device.. csv file script is generated by TI Fusion tool
# CSV file must be SMBUS protocol..
import time

DebugPrint = False

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
		func = "print('"+str(comment)+"')"
		# print(func)
		# print("\n\n\n\n")
		
	
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
	
	elif cmd == "BLOCKREAD" :
		# if DebugPrint:
		print(instr_arr)
		# ucd_block_read(port,rd_cmd,rdlen,data_check): 
		rd_cmd = instr_arr[2]
		data_check = instr_arr[3][2:]
		rdlen = int(len(data_check)/2) ## no. of bytes to be read
		
		print(rd_cmd)
		print(data_check)
		print(rdlen)
		
		func = "ucd_block_read(ucd,"+str(rd_cmd)+","+str(rdlen)+","+str(data_check)+")" 
		# func = "print('end')"
	
	elif cmd == "SENDBYTE":		
		if DebugPrint:
			print(instr_arr)
		data = instr_arr[2][2:].split("\n")[0]
		if DebugPrint:
			print(data)
		func = "ucd_byte_write(ucd,[0x"+data+"])"
		# print (func)	
	
	elif cmd == "PAUSE":		
		if DebugPrint:
			print(instr_arr)
		pause_ms = (instr_arr[1])
		pause_cmnt = instr_arr[2].split("\n")[0]
		# func = "print('end')"
		func = "ucd_pause("+pause_ms+",'"+pause_cmnt+"')"
		# print (func)
	
	
	else:
		print("\t\t** cmd not defined  ==> "+instr_line)
		func = "print('not defined')"
	return func	
	
	
def ucd_csv_prog(ucd):
##-------////////////////--------

	with open('ucd90160_smbus_flash_script_test.csv', 'r') as f:
	# with open('ucd90160_smbus_flash_script.csv', 'r') as f:
		lines_arr = f.readlines()
		f.close()

	# print (lines_arr)
	# print("\n\n***\n")
	# remove the commented section
	# instr_set = [x for x in lines_arr if x[0] != '!']
	# print(instr_set)
	# total_instructions = len(lines_arr)
	# ucd_parser(lines_arr)
	# ucd = 0
	i = 0
	for line in lines_arr:
		# print (line)
		print(ucd_parser(ucd,line))
		# i += 1
		# if i%1000 == 0:
			# print("\t\t Instructions executed = "+str(i)+" of "+str(total_instructions))



if __name__ == "__main__":
	print("script parser started ==>")
	ucd = 0
	ucd_csv_prog(ucd)
	