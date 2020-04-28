import os, sys
import serial
import time

ser = serial.Serial(
               port='/dev/ttyUSB0',
               baudrate = 38400,
               parity=serial.PARITY_NONE,
               stopbits=serial.STOPBITS_ONE,
               bytesize=serial.EIGHTBITS,
               timeout=5
           )
if(len(sys.argv) > 1):
    command = "AT+" + sys.argv[1] + "\r\n"
else:
    command = "AT\r\n"

ser.write(command.encode())
response = ser.readline()
print(response.decode())
