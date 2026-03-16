import serial

# Open serial port (adjust device and baud rate as needed)
ser = serial.Serial('/dev/serial0', baudrate=115200, timeout=1)

try:
    # Read up to 32 bytes
    data = ser.read(32)  # returns bytes object
    if data:
        # Interpret as ASCII text
        text = data.decode('ascii', errors='replace')
        print("Raw bytes:", data)
        print("As ASCII:", text)
    else:
        print("No data received.")
except serial.SerialException as e:
    print("Serial error:", e)
finally:
    ser.close()
