import pandas as pd
import matplotlib.pyplot as plt

# Load your latest CSV file
filename = input("Enter CSV file path: ")

df = pd.read_csv(filename)

# Convert time column
df["system_time"] = pd.to_datetime(df["system_time"])

# Plot Gas + PM
plt.figure()

plt.plot(df["system_time"], df["gas_resistance_raw"], label="Gas Resistance")
plt.plot(df["system_time"], df["pm_concentration"], label="PM2.5")

plt.xlabel("Time")
plt.ylabel("Sensor Values")
plt.title("Sensor Data Over Time")

plt.legend()
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()