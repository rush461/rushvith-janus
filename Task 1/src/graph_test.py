import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time

### this is a test script

# lists to store the live coordinate data
latitudes = []
longitudes = []
altitudes = []

# set up the live 3D plot
plt.ion()
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(projection='3d')

ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.set_zlabel("Altitude (m)")
ax.set_title("Simulated 3D XBee Telemetry Tracker")

# data processing callback function
def data_process_callback(xbee_message):
    try:
        raw_data = xbee_message.data.decode("utf-8").strip()
        print(f"Received: {raw_data}")

        parts = raw_data.split(",")
        if len(parts) == 10:
            timestamp = int(parts[0])
            state = int(parts[1])
            temperature = float(parts[2])
            pressure = float(parts[3])
            altitude = float(parts[4])
            battery_voltage = float(parts[5])
            battery_current = float(parts[6])
            latitude = float(parts[7])
            longitude = float(parts[8])
            prev_cmd_echo = parts[9]

            # append coordinates for the 3D plot
            latitudes.append(latitude)
            longitudes.append(longitude)
            altitudes.append(altitude)

            print(f"State: {state} | Alt: {altitude}m | Temp: {temperature}°C")

            # redraw 3D plot
            ax.clear()
            ax.set_xlabel("Longitude")
            ax.set_ylabel("Latitude")
            ax.set_zlabel("Altitude (m)")
            ax.plot(longitudes, latitudes, altitudes, marker='o', color='b')
            plt.draw()
            plt.pause(0.1)

    except ValueError:
        print("Data parsing error: Mismatched data types.")
    except Exception as e:
        print(f"Error processing message: {e}")

# mock section for testing the data processing function and graph
class MockXBeeMessage:
    def __init__(self, data_str):
        self.data = data_str.encode("utf-8")

# simulated telemetry flight path data
simulated_telemetry_stream = [
    "1672531200,1,24.5,1013.25,100.0,4.1,0.5,37.7749,-122.4194,OK",
    "1672531201,1,24.6,1012.80,120.0,4.1,0.6,37.7750,-122.4195,OK",
    "1672531202,2,24.8,1012.10,150.0,4.0,0.7,37.7752,-122.4197,OK",
    "1672531203,2,25.0,1011.50,190.0,4.0,0.8,37.7755,-122.4200,OK",
    "1672531204,3,25.2,1010.90,240.0,3.9,0.9,37.7759,-122.4204,OK"
]

print("Starting simulation test...")
try:
    for packet in simulated_telemetry_stream:
        mock_msg = MockXBeeMessage(packet)
        data_process_callback(mock_msg)
        time.sleep(1)
        
    print("Simulation finished. Close the plot window to exit.")
    plt.ioff()
    plt.show()

except KeyboardInterrupt:
    print("\nSimulation stopped.")