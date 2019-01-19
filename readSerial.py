import serial
import time
import os
import json
import sched, time

from databaseWriter import DatabaseWriter

class ReadSerial:
    def __init__(self):

        os.getcwd()
        config_path = os.getcwd() + "/config/defaultConfig.json"
        with open(config_path, 'r') as f:
            self.datastore = json.load(f)
        # Connect to Serial Port for communication
        self.ser = serial.Serial(self.datastore["arduino-settings"]["port"], self.datastore["arduino-settings"]["baud"], timeout=0)
        # Setup a loop to send values at fixed intervals in seconds
        self.fixed_interval = self.datastore["fixed-interval"]
        # Create repository object
        self.save_to_cloud = self.datastore["save_to_cloud"]
        #self.database_writer = DatabaseWriter(self.datastore["firestore"])
        self.start_timer = time.time() 

    def run(self):
        while True: 
            if self.ser.isOpen():
                read_serial = self.ser.readline()
            if (self.datastore["display"]):
                print read_serial
            if (len(read_serial) == 27):
                # read sensor data 
                humidity = int(read_serial[0:4], 16)
                temperature = int(read_serial[5:9], 16)
                air_quality = int(read_serial[10:13], 16)
                frequency = int(read_serial[14:19], 16)
                bee_count = int(read_serial[20:24], 16)
                measurement = Measurement(humidity, temperature, frequency, air_quality, bee_count)
            if time.time() - self.start_timer >= self.datastore["write-to-database"]:
                if self.save_to_cloud:
                    self.database_writer.save_measurement(measurement)
                self.start_timer = time.time()
            time.sleep(self.fixed_interval)
                  
class Measurement:
    
    def __init__(self, humidity, temperature, frequency, air_quality, bee_count):
        self.humidity = humidity
        self.temperature = temperature
        self.frequency = frequency
        self.air_quality = air_quality
        self.bee_count = bee_count
