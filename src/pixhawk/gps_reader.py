from pymavlink import mavutil

class GPSReader:
    def __init__(self):
        print("[INFO] Connecting to Pixhawk...")
        self.master = mavutil.mavlink_connection('/dev/ttyAMA2', baud=57600)

        print("[INFO] Waiting for heartbeat...")
        self.master.wait_heartbeat()
        print("[INFO] Connected to Pixhawk")

    def get_data(self):
        msg = self.master.recv_match(type='GLOBAL_POSITION_INT', blocking=False)

        if msg is None:
            return None

        return {
            "lat": msg.lat / 1e7,
            "lon": msg.lon / 1e7,
            "alt": msg.alt / 1000.0,
            "vx": msg.vx / 100.0,
            "vy": msg.vy / 100.0,
            "vz": msg.vz / 100.0,
            "heading": msg.hdg / 100.0
        }