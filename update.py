from argparse import ArgumentParser
from time import sleep
import serial
from c42b import main as c42b

print("TABLO UPDATER v1.0")
parser = ArgumentParser()
parser.add_argument("-p", "--port", help="port")
parser.add_argument("-b", "--baud", help="baudrate")
parser.add_argument("-f", "--file", help="firmware file")
args = parser.parse_args()
if not args.file or not args.port:
    print("Usage:")
    print("update.py -f hexfile.hex -p /dev/ttyUSB0 [-b 19200]")
    exit()

ser = serial.Serial()
ser.port = args.port
ser.baudrate = 19200
if args.baud:
    ser.baudrate = args.baud
ser.bytesize = serial.EIGHTBITS
ser.parity = serial.PARITY_NONE
ser.stopbits = serial.STOPBITS_ONE
ser.timeout = 0

try:
    ser.open()
except Exception as e:
    print(f"Serial error: {str(e)}")
    exit()

if not ser.isOpen():
    print("Serial port is not open")
    exit()

# Выходим из основной программы в загрузчик
print("Set controller to boot mode... ", end="")
resp = ''
while True:
    ser.write(b'U')
    sleep(0.1)
    resp = ser.read(1)
    if resp == b'U':
        resp = ser.read(1)
        if resp == b'!':
            ser.write(b'U')
            print("OK")
            break

sleep(2)
print("Uploading new firmware... ", end="")
ser.flushInput()
ser.flushOutput()

# Работаем с загрузчиком
c42b(ser=ser, file=args.file)

ser.close()
exit(0)
