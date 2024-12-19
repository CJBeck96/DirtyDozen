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

# Dictionary to store the previous lap times and other racer data
racers_data = {}

# Open (or create) the CSV file for appending data
with open(csv_file, mode='a', newline='') as file:
    csv_writer = csv.writer(file)
    
    # Check if the file is empty and write the header row if it is
    file.seek(0, 2)  # Move the pointer to the end of the file
    if file.tell() == 0:
        csv_writer.writerow(["Timestamp", "RFID Tag", "Lap Count", "Lap Time (mm:ss)", "Split Time (mm:ss)", "Total Elapsed Time (mm:ss)"])

    print(f"Saving data to {csv_file}...")

    while True:
        try:
            # Read data from the Arduino
            line = arduino.readline().decode('utf-8').strip()
            
            if line:
                print(f"Received: {line}")  # Debugging output to confirm data is received
                
                # Check how many commas are in the line (this helps debug the format issue)
                print(f"Comma count: {line.count(',')}")
                
                # Check if the line is in the expected format (UID, lapCount, lapTime, totalElapsedTime)
                if line.count(",") == 3:  # Expecting exactly three commas (4 fields)
                    try:
                        # Assuming Arduino sends data in the format: UID,lapCount,lapTime,totalElapsedTime
                        tag_id, lap_count, lap_time, total_elapsed_time = line.split(",")
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        # Convert times from seconds to minutes and seconds
                        def format_time(seconds):
                            minutes = int(float(seconds) // 60)
                            remaining_seconds = float(seconds) % 60
                            return f"{minutes:02}:{remaining_seconds:06.3f}"

                        lap_time_formatted = format_time(lap_time)
                        total_elapsed_formatted = format_time(total_elapsed_time)
                        
                        # Calculate split time
                        split_time_formatted = "N/A"
                        if tag_id in racers_data:
                            # Calculate split time only if there are previous laps
                            previous_lap_time = racers_data[tag_id]['previous_lap_time']
                            split_time = float(lap_time) - previous_lap_time
                            if split_time > 0:  # Make sure it's positive
                                split_time_formatted = format_time(split_time)
                        
                        # Update racer data
                        racers_data[tag_id] = {
                            'previous_lap_time': float(lap_time),
                            'lap_count': int(lap_count),
                            'total_elapsed_time': float(total_elapsed_time)
                        }

                        # Write the data to the CSV file
                        csv_writer.writerow([
                            timestamp, 
                            tag_id, 
                            int(lap_count), 
                            lap_time_formatted, 
                            split_time_formatted, 
                            total_elapsed_formatted
                        ])
                        print(f"Data written to CSV: {timestamp}, {tag_id}, {lap_count}, {lap_time_formatted}, {split_time_formatted}, {total_elapsed_formatted}")
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
