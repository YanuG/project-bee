import serial
import time
from pathlib2 import Path
import json
import sched, time

from databaseWriter import DatabaseWriter

class ReadSerial:
    def __init__(self):

        project_root = Path(__file__).resolve().parent
        config_path = project_root/"config/defaultConfig.json"
        with open(str(config_path), 'r') as f:
            self.config_file = json.load(f)
        # Connect to Serial Port for communication
        self.ser = serial.Serial(self.config_file["arduino-settings"]["port"], self.config_file["arduino-settings"]["baud"], timeout=0)
        # Setup a loop to send values at fixed intervals in seconds
        self.fixed_interval = self.config_file["fixed-interval"]
        # Create repository object
        self.save_to_cloud = self.config_file["save_to_cloud"]
        self.database_writer = DatabaseWriter(self.config_file["database"])
        self.start_timer = time.time() 

    def run(self):
        while True: 
            if self.ser.isOpen():
                read_serial = self.ser.readline()
            if (self.config_file["display"]):
                print read_serial
                print len(read_serial)
            if (len(read_serial) == 28):
                # read sensor data 
                humidity = int(read_serial[0:4], 16)
                temperature = int(read_serial[5:9], 16)
                air_quality = int(read_serial[10:13], 16)
                frequency = int(read_serial[14:20], 16)
                bee_count = int(read_serial[21:25], 16)
                self.measurement = Measurement(humidity, temperature, frequency, air_quality, bee_count)
                if (self.config_file["display"]):
                    print "Hum: " + str(humidity) + " Temp: " + str(temperature) + " Air Quality: " + str(air_quality) + " Frequency " + str(frequency) + " Bee Count " + str(bee_count)
                if time.time() - self.start_timer >= self.config_file["write-to-database"]:
                    if self.save_to_cloud:
                        self.database_writer.save_measurement(self.measurement)
                    self.start_timer = time.time()
            time.sleep(self.fixed_interval)
                  
class Measurement:
    def __init__(self, humidity, temperature, frequency, air_quality, bee_count):
        self.humidity = humidity
        self.temperature = temperature
        self.frequency = frequency
        self.air_quality = air_quality
        self.bee_count = bee_count
