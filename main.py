from argparse import ArgumentParser
from time import sleep
import serial

def symb(r):
    if r == '*':
        print(r)
        return 0
    elif r == '.':
        print(r, end='')
        return 0
    elif r == '+':
        print ("End")
        return 1
    elif r == '-':
        print("Chechsum error")
        return 2
    else:
        print(f"Unknown resp: {r}")
        return 0

parser = ArgumentParser()
parser.add_argument("-p", "--port", help="port")
parser.add_argument("-b", "--baud", help="baudrate")
parser.add_argument("-f", "--file", help="firmware file")
args = parser.parse_args()
if not args.file or not args.port:
    print("Usage:")
    print("pyc45b.py -f hexfile.hex -p /dev/ttyUSB0 [-b 19200]")
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

print("Waiting for reset MCU")
resp = ''
while resp != b'c':
    ser.write(b'U')
    sleep(0.1)
    resp = ser.read(1)
sleep(0.1)
resp += ser.readline()
if resp.decode()[:5] == "c45b2":
    print(f"Bootloader version: {resp.decode()}")
else:
    print("Sync error")
    exit()

sleep(0.1)
ser.write(b'pf\n')

tick = 0
while resp != b'p':
    resp = ser.read(1)
    tick += 1
    sleep(0.1)
    if tick > 100:
        print("progMode timeout")
        exit(-1)
resp += ser.read(2)
if resp.decode()[2] == '+':
    ser.flushInput()
    print("Start uploading", end='')
else:
    print(f"progMode error: {resp}")
    exit()

try:
    with open(args.file, 'rb') as f:
        for line in f:
            ser.write(line)
            resp = ''
            while len(resp) == 0:
                resp = ser.readline()
            r = resp.decode()
            while len(r) != 0:
                if r[0] == '.' or r[0] == '*':
                    print(r[0], end='')
                r = r[1:]

except Exception as e:
    print(f"Error: {e}")
    exit()

sleep(0.1)

while True:
    resp = ser.read(1)
    if resp == b'.' or resp == b'*':
        print(resp.decode(), end='')
    elif resp == b'+':
        print('Done')
        break
    elif resp == b'-':
        print("Checksum error")
        exit()

while resp != b'>':
    resp = ser.read(1)

print("Run program ", end='')
ser.write(b'g\n')
sleep(0.1)
resp = ser.readall()
if resp.decode()[:2] == 'g+':
    print("Done")
else:
    print(f"Fail {resp.decode()}")
ser.close()
exit()
