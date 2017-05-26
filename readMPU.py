#!/usr/bin/python
 
import smbus
import math

# power managment registers
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c

def read_byte(adr):
	return bus.read_byte_data(address,adr)

def read_word(adr):
	high = bus.read_byte_data(address,adr)
	low = bus.read_byte_data(address,adr+1)
	val = (high << 8) + low
	return val

def read_word_2c(adr):
	valu = read_word(adr)
	if(val >= 0x8000):
		return -((65535 - val) + 1)
	else:
		return val

bus = smbus.SMBus(0)
address = 0x68      #mpu address

#wake up the 6050
bus.write_byte_data(address,power_mgmt_1,0)

accel_xout = read_word_2c(0x3b)
accel_yout = read_word_2c(0x3d)
accel_zout = read_word_2c(0x3f)

print "accel_xout: ", accel_xout
print "accel_yout: ", accel_yout
print "accel_zout: ", accel_zout