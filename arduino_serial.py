import serial
import csv
from datetime import datetime

# Replace '/dev/ttyACM0' with your Arduino's port (use 'COMx' for Windows)
arduino_port = '/dev/ttyACM0'
baud_rate = 9600  # Match the baud rate used in your Arduino sketch
csv_file = "rfid_data.csv"

# Set up the serial connection
try:
    arduino = serial.Serial(arduino_port, baud_rate, timeout=3)
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
        csv_writer.writerow(["Timestamp", "RFID Tag", "Lap Count", "Lap Time (mm:ss)", "Split Time (mm:ss)"])

    print(f"Saving data to {csv_file}...")
    
    while True:
        try:
            # Read data from the Arduino
            line = arduino.readline().decode('utf-8').strip()
            
            if line:
                print(f"Received: {line}")  # Debugging output to confirm data is received
                
                # Validate data format
                parts = line.split(",")
                if len(parts) == 4:  # Expecting 4 parts: tag_id, lap_count, lap_time, split_time
                    try:
                        tag_id, lap_count, lap_time, split_time = parts
                        lap_count = int(lap_count)  # Validate lap_count as an integer
                        lap_time = float(lap_time)  # Validate lap_time as a float
                        split_time = float(split_time)  # Validate split_time as a float
                        
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        # Convert lap time from milliseconds to minutes and seconds
                        lap_minutes = int(lap_time // 60000)
                        lap_seconds = (lap_time % 60000) / 1000
                        lap_time_formatted = f"{lap_minutes:02}:{lap_seconds:06.3f}"
                        
                        # Convert split time from milliseconds to minutes and seconds
                        split_minutes = int(split_time // 60000)
                        split_seconds = (split_time % 60000) / 1000
                        split_time_formatted = f"{split_minutes:02}:{split_seconds:06.3f}"
                        
                        # Write the data to the CSV file
                        csv_writer.writerow([timestamp, tag_id, lap_count, lap_time_formatted, split_time_formatted])
                        print(f"Data written to CSV: {timestamp}, {tag_id}, {lap_count}, {lap_time_formatted}, {split_time_formatted}")
                    except ValueError as e:
                        print(f"Error processing data: {line} - {e}")
                else:
                    print(f"Invalid data format: {line}")
            else:
                print("No data received")
        
        except KeyboardInterrupt:
            print("\nExiting...")
            arduino.close()
            break
        except Exception as e:
            print(f"Error: {e}")

