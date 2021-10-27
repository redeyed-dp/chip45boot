from argparse import ArgumentParser
from time import sleep
import serial

parser = ArgumentParser()
parser.add_argument("-p", "--port", help="port")
parser.add_argument("-b", "--baud", help="baudrate")
args = parser.parse_args()
if not args.port:
    print("Usage:")
    print("test.py -p /dev/ttyUSB0 [-b 19200]")
    exit()

ser = serial.Serial()
ser.port = args.port
ser.baudrate = 19200
if args.baud:
    ser.baudrate = args.baud
ser.bytesize = serial.EIGHTBITS
ser.parity = serial.PARITY_NONE
ser.stopbits = serial.STOPBITS_ONE
ser.xonxoff = True
ser.timeout = 0

try:
    ser.open()
except Exception as e:
    print(f"Serial error: {str(e)}")
    exit()

if not ser.isOpen():
    print("Serial port is not open")
    exit()

resp = ''
while True:
    resp = ser.read(1)
    sleep(0.1)
    print(resp.decode(), end='')