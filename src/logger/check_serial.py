import serial
import time

ser = serial.Serial("/dev/ttyAMA0", 115200, timeout=1)

print("Port opened:", ser.name)

while True:
    n = ser.in_waiting
    if n:
        data = ser.read(n)
        print("RAW BYTES:", data)
    else:
        print("No data")
    time.sleep(1)