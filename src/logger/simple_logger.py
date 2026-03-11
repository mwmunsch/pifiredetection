import serial

#check if stm32 is connected to the serial port
print("Checking for STM32 connection...")

if not serial.Serial('/dev/serial0', 115200, timeout=1):
    print("STM32 not connected. Please check the connection and try again.")
    exit(1)

ser = serial.Serial('/dev/serial0', 115200, timeout=1)
print("STM32 connected successfully.")

data = ser.readline()

print(f"Received data from STM32: {data}")

ser.close()