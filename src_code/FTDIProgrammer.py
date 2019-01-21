	# FTDIProgrammer	==> top level file to program through FTDI
	# It will call FTJTAGProg.py & FTUCDProg
	
	
	
##	/// 	Checking of platform having issue with libusb0.dll ...
			# Error = No backend available.. 
			# This file is strictly for windows.. Linux development is in progress
##		_________________________________________________________________________________
	
# import platform 
import usb.core
import usb.util
import easygui as gui
import FTJTAGProg, FTUCDProg

version = "Beta"
released_date = "22-Jan-2019"
src_url = "https://github.com/kunalcdot"



def FTwin(): ## FTDI programmer windows based
	
	
	msg = ("****************************************************************************\n")
	msg += ("\t\tFTDI PROGRAMMER : Version: "+version+"\nReleased Date = "+released_date+"\nMore info : "+src_url+"\n")
	msg += ("****************************************************************************\n\n")
	msg += "\n\t\t\tINSTRUCTIONS\n\n"
	msg += "1. This application can work with any type of FTDI device through lib-usb driver\n"
	msg += "2. Ensure lib-usb is installed on your system\n"
	msg += "3. For windows ensure only one FTDI channel is enabled. This can be done in Device manager settings\n"
	msg += "4. Most of the time the default settings option is the best\n"
	msg += "5. For JTAG programming ensure your device is the only device in the chain\n"
	msg += "6. Ensure only one FTDI device is connected to your PC\n"
	msg += "7. For more information go through FTDI Programmer Manual\n"
	msg += "\n----------------------------------------------------------------------------\n\n"
	print(msg)

	gui.msgbox(msg=msg, title="FTDIProgrammer", ok_button='Next')
	
	# dev = usb.core.find(idVendor=0x403, idProduct=0x6011)
	
	# programming option---------------------------------------------------------
	# while 1:
	msg = "Select programming option"
	choices = ["JTAG-SVF programming (default settings)","UCD-CSV programming (default settings)",
				"JTAG-SVF programming (Adv settings)","UCD-CSV programming (Adv settings)"]
	selected_choice = [0,0,0,0] # '1' signifies that specific test is to be performed
	selected = gui.choicebox(msg=msg, title="Choice", choices=choices)
	# print (selected)

	
	#------------------------------browse prog file --------------------
	while 1:	
		gui.msgbox(msg="Browse programming file", title="", ok_button='Browse')
		prg_file = gui.fileopenbox(msg=None, title="Browse programming file", default=None)	
		# print (prg_file)
		if (prg_file != None):
			break
	
	
	
	
	url = 'ftdi:///1'
	if selected == choices[0]:
		success = FTJTAGProg.main(url,prg_file,3E06)
	
	elif selected == choices[1]:
		success = FTUCDProg.main(url,prg_file,5000,False)
	
	elif selected == choices[2]:	
		fieldNames = ["Force JTAG frequency in MHz(only integer)"]
		# fieldValues = []  # we start with blanks for the values
		freq_Mhz = int(gui.multenterbox("","", fieldNames)[0])
		
		# start programming
		success = FTJTAGProg.main(url,prg_file,freq_Mhz)
		
	elif selected == choices[3]:	
		fieldNames = ["Force I2C frequency in Hz(only integer)\n[should be less than 50KHz]"]
		# fieldValues = []  # we start with blanks for the values
		freq = int(gui.multenterbox("","", fieldNames)[0])
	
		msg = "Do you want to perform frequency optimization?\n\nNote: for frequency>10KHz frequency optimization must be performed"
		selected_button = gui.buttonbox(msg=msg, title="", choices=('Yes', 'No'))
			
		if (selected_button == "Yes"):
			Fopt = True
				
		elif selected_button == 'No':
			Fopt = False
		
		msg = "Do you want to skip read verification for Fast programming?\n\nNote: Programming will be verified only via PEC error bit"
		msg += "\nThis option is not yet implemented"
		selected_button = gui.buttonbox(msg=msg, title="", choices=('Yes', 'No'))
			
		if (selected_button == "Yes"):
			skip_rd_verify = True
				
		elif selected_button == 'No':
			skip_rd_verify = False
		
		success = FTUCDProg.main(url,prg_file,freq,Fopt)
	
	# print(success)
	return success







if __name__ == "__main__":
	# os = platform.system()
	try:
		success = FTwin()
	except:
		gui.exceptionbox(msg="ERROR!!!!", title="Error")
		success = 0
		exit(0)
	
##	/// 	Checking of platform having issue with libusb0.dll ...
			# Error = No backend available.. 
			# This file is strictly for windows.. Linux development is in progress
	# os = platform.system()
	# if os.lower() == "windows":
		# try:
			# print("win")
			# FTwin()
			# success = 1
		# except:
			# gui.exceptionbox(msg="ERROR!!!!", title="Error")
		
			
		
	
	
	# elif os.lower() == "linux":
		# print("Linux support is under development")
	# else:
		# print("Unknown OS..\nExiting...\n")
		# exit(0)

	if success:	
		gui.msgbox(msg="Programming is successfully completed", title="FTDIProgrammer", ok_button='Finish')	
	else:
		gui.msgbox(msg="Programming Failed\nCheck console window for more info before exiting", title="FTDIProgrammer", ok_button='Exit')	