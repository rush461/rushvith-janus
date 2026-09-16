import time
from digi.xbee.devices import XBeeDevice
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

PORT = "COM3" # serial port for the xbee device
BAUD_RATE = 9600 # number of symbols per second in a communication channel

# lists to store coordinate data
latitudes = []
longitudes = []
altitudes = []

def main():
    # initialize XBee device
    device = XBeeDevice(PORT, BAUD_RATE)
    
    try:
        device.open()
        print(f"Connected to XBee on {PORT}. Waiting for telemetry...")

        # set up live 3D plot with matplotlib
        plt.ion()
        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(projection='3d')
        
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        ax.set_zlabel("Altitude (m)")
        ax.set_title("Live 3D XBee Telemetry Tracker")

        # handle incoming packets automatically
        def data_process_callback(xbee_message):
            try:
                # decode xbee data to string
                raw_data = xbee_message.data.decode("utf-8").strip()

                # split string at commas
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

                    # redraw 3d plot with new data points
                    ax.clear()
                    ax.set_xlabel("Longitude")
                    ax.set_ylabel("Latitude")
                    ax.set_zlabel("Altitude (m)")
                    ax.plot(longitudes, latitudes, altitudes, marker='o', color='b')
                    plt.draw()
                    plt.pause(0.01)

            except ValueError:
                print("Data parsing error: Mismatched data types.")
            except Exception as e:
                print(f"Error processing message: {e}")

        # register the callback function to listen for incoming data
        device.add_data_received_callback(data_process_callback)

        # keep the script continuously running to listen for telemetry
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping telemetry tracker...")
    finally:
        if device.is_open():
            device.close()
        plt.ioff()
        plt.show()

if __name__ == "__main__":
    main()