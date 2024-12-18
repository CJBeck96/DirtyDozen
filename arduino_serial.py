import serial
import csv
from datetime import datetime

# Replace '/dev/ttyACM0' with your Arduino's port (use 'COMx' for Windows)
arduino_port = '/dev/ttyACM0'
baud_rate = 9600  # Match the baud rate used in your Arduino sketch
csv_file = "rfid_data.csv"

# Set up the serial connection
try:
    arduino = serial.Serial(arduino_port, baud_rate, timeout=3)  # Increased timeout to 3 seconds
    print(f"Connected to Arduino on {arduino_port}")
except Exception as e:
    print(f"Error connecting to Arduino: {e}")
    exit()

# Open (or create) the CSV file for appending data
with open(csv_file, mode='a', newline='') as file:
    csv_writer = csv.writer(file)
    
    # Check if the file is empty and write the header row if it is
    file.seek(0, 2)  # Move the pointer to the end of the file
    if file.tell() == 0:
        csv_writer.writerow(["Timestamp", "RFID Tag", "Lap Count", "Lap Time (mm:ss)"])

    print(f"Saving data to {csv_file}...")
    
    while True:
        try:
            # Read data from the Arduino
            line = arduino.readline().decode('utf-8').strip()
            
            if line:
                print(f"Received: {line}")  # Debugging output to confirm data is received
                
                # Check if the line is in the expected format
                if "," in line:
                    try:
                        # Assuming Arduino sends data in the format: tag_id,lap_count,lap_time
                        tag_id, lap_count, lap_time = line.split(",")
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        # Convert lap time from milliseconds to minutes and seconds
                        lap_time_ms = float(lap_time)  # Ensure it's a float
                        minutes = int(lap_time_ms // 60000)  # Convert ms to minutes
                        seconds = (lap_time_ms % 60000) / 1000  # Convert remaining ms to seconds
                        lap_time_formatted = f"{minutes:02}:{seconds:06.3f}"  # Format as mm:ss.sss
                        
                        # Write the data to the CSV file
                        csv_writer.writerow([timestamp, tag_id, lap_count, lap_time_formatted])
                        print(f"Data written to CSV: {timestamp}, {tag_id}, {lap_count}, {lap_time_formatted}")
                    except ValueError:
                        print(f"Invalid data format: {line}")
                else:
                    print(f"Unexpected format: {line}")
            else:
                print("No data received")
        
        except KeyboardInterrupt:
            print("\nExiting...")
            arduino.close()
            break
        except Exception as e:
            print(f"Error: {e}")
