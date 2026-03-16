import serial

ser = serial.Serial('/dev/serial0', 115200, timeout=1)

# Read 10 bytes
data = ser.read(10)
print(f"Read {len(data)} bytes: {data}")

# Read single byte
byte = ser.read(1)
if byte:
    print(f"Got byte: {byte[0]:02X}")