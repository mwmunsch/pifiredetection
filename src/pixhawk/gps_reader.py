from pymavlink import mavutil
import time

class GPSReader:
    def __init__(self):
        print("[INFO] Connecting to Pixhawk...")

        self.master = mavutil.mavlink_connection('/dev/ttyAMA2', baud=57600)

        print("[INFO] Waiting for heartbeat...")
        self.master.wait_heartbeat()
        print("[INFO] Connected to Pixhawk")

        # store last known GPS values
        self.last_data = {
            "lat": 0,
            "lon": 0,
            "alt": 0,
            "vx": 0,
            "vy": 0,
            "vz": 0,
            "heading": 0
        }

        # alert cooldown
        self.last_alert_time = 0

    def get_position(self):
        try:
            msg = self.master.recv_match(type='GLOBAL_POSITION_INT', blocking=False)

            if msg:
                self.last_data = {
                    "lat": msg.lat / 1e7,
                    "lon": msg.lon / 1e7,
                    "alt": msg.alt / 1000.0,
                    "vx": msg.vx / 100.0,
                    "vy": msg.vy / 100.0,
                    "vz": msg.vz / 100.0,
                    "heading": msg.hdg / 100.0
                }

            return self.last_data

        except Exception as e:
            print("[GPS ERROR]", e)
            return self.last_data

    def send_fire_alert(self, lat, lon, confidence):
        try:
            # cooldown (5 seconds)
            if time.time() - self.last_alert_time < 5:
                return

            msg = f"FIRE DETECTED | Lat:{lat:.5f} Lon:{lon:.5f} Conf:{confidence}%"

            self.master.mav.statustext_send(
                mavutil.mavlink.MAV_SEVERITY_CRITICAL,
                msg.encode()
            )

            print("[ALERT SENT]", msg)

            self.last_alert_time = time.time()

        except Exception as e:
            print("[MAVLINK ERROR]", e)