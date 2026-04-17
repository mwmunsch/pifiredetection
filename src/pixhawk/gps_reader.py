from pymavlink import mavutil

# Connect to Pixhawk via UART2
#i think this is right but if it doesn't work try different baudrate
master = mavutil.mavlink_connection('/dev/ttyAMA2', baud=57600)

print("[INFO] Waiting for heartbeat...")
master.wait_heartbeat()
print("[INFO] Connected to Pixhawk")

while True:
    msg = master.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
    
    if msg is not None:
        lat = msg.lat / 1e7
        lon = msg.lon / 1e7
        alt = msg.alt / 1000.0      # mm → meters
        vx = msg.vx / 100.0         # cm/s → m/s
        vy = msg.vy / 100.0
        vz = msg.vz / 100.0
        heading = msg.hdg / 100.0   # degrees

        print(f"""
GPS DATA:
Lat: {lat}
Lon: {lon}
Alt: {alt} m
Speed X: {vx} m/s
Speed Y: {vy} m/s
Speed Z: {vz} m/s
Heading: {heading}°
""")