"""
Fake STM32 Logger Tester
Capstone Team 8 Forest Fire Detection Drone

This script simulates STM32 sensor packets so the logger can be tested
without real hardware.

Run this in one terminal, then run logger.py in another terminal.
"""

import json
import time
import random

print("[TEST] Fake STM32 started")

stm_time = 0

while True:

    stm_time += 1000

    data = {
        "stm32_time": stm_time,
        "gas_resistance_raw": round(random.uniform(70000, 90000), 2),
        "pm_concentration": round(random.uniform(2, 15), 2),
        "stm_alive": 1,
        "fire_flag": 0,
        "confidence": 0
    }

    print(json.dumps(data))

    time.sleep(1)