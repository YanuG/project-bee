import serial
import time
import os
import json

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
    self.database_writer = DatabaseWriter(self.datastore["firestore"])


  def run(self):

    while True: 

      if self.ser.isOpen():
        read_serial = self.ser.readline()
        if (self.datastore["display"] and len(read_serial) == 87 ):
          print (read_serial)
        # example output [Humidity: 24.60; Temperature: 24.00; Quality: 3; Sound: 2] 
        if (read_serial[0:1] == "[" and len(read_serial) == 87  and read_serial[84:85] == "]"):
          # read sensor data 
          humidity = float(read_serial[11:16])
          temperature = float(read_serial[31:36])
          air_quality = read_serial[47:48]
          frequency = read_serial[59:60]
          bee_count = read_serial[82:84]
          measurement = Measurement(humidity, temperature, frequency, air_quality, bee_count)
          # send reading to database
          if self.save_to_cloud:
            self.database_writer.save_measurement(measurement)
   
      time.sleep(self.fixed_interval)

                 
class Measurement:
  def __init__(self, humidity, temperature, frequency, air_quality, bee_count):
    self.humidity = humidity
    self.temperature = temperature
    self.frequency = frequency
    self.air_quality = air_quality
    self.bee_count = bee_count
