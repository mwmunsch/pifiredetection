import serial

class STM32Reader:
    def __init__(self):
        self.ser = serial.Serial('/dev/ttyAMA0', 115200, timeout=0.1)

    def get_data(self):
        if self.ser.in_waiting:
            line = self.ser.readline().decode('utf-8').strip()

            try:
                parts = line.split(',')

                return {
                    "pm": float(parts[2]),
                    "gas": float(parts[9])
                }
            except:
                return None

        return None