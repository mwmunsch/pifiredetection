import time
import json
import random
import serial

SERIAL_PORT = "/dev/pts/4"   
BAUD_RATE = 115200

with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
    while True:
        packet = {
            "stm32_time": int(time.time() * 1000),
            "gas_resistance_raw": round(random.uniform(70000, 90000), 2),
            "pm_concentration": round(random.uniform(1, 30), 2),
            "stm_alive": 1,
            "fire_flag": 0,
            "confidence": 0
        }

        line = json.dumps(packet) + "\n"
        ser.write(line.encode("utf-8"))
        ser.flush()

        print(line.strip())
        time.sleep(1)