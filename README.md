# FTDI-programmer
FTDI-programmer is an application written in pure python to access/program on board devices through FT4232 jtag/spi/i2c/gpio interfaces. JTAG programming is done through svf file. It can be used in place of any external emulator.
In case of SPI/I2C, the programming method is device specific.

## Directory structure
**bin/**  -->  Windows executable<br>

**dll/**    libusb dll required for windows exe. These do not get copied automatically. Bug in pyinstaller.

**src_code/**     python source code

**src_doc/**    latex source file for user manual

## To be implemented
1. JTAG read command time reduction
2. spi flash programming
3. read/write debugging access through --> i2c/spi.. an utility for that
4. linux compatibility
