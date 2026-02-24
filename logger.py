"Basic Logger for Serial Data"
"Capstone Team 8 Forest Fire Detection Drone"
"Author: Mallorie Wiggins"

import serial
import json
import time
import csv
import os
from datetime import datetime


# Serial port config
SERIAL_PORT = ''
BAUD_RATE = 115200

# Log file config
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)
timestamp_string = datetime.now().strftime('%Y%m%d_%H%M%S')
log_filename = f'{log_dir}/sensor_log_{timestamp_string}.csv'

csv_file = open(log_filename, mode='w', newline='')
csv_writer = csv.writer(csv_file)

csv_writer.writerow(["system_time", "stm32_time", "gps_resistance_raw", "pm_concentration", "heartbeat","fire_flag", "confidence"])
print(f"Logging to {log_filename}")


                     


