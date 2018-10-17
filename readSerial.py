#!/usr/bin/env python
import serial
import time
import os
import json

from databaseWriter import DatabaseWriter


class ReadSerial():

  def __init__(self):

    os.getcwd()
    config_path = os.getcwd() + "/config/defaultConfig.json"

    with open(config_path, 'r') as f:
        datastore = json.load(f)

    # Connect to Serial Port for communication
    self.ser = serial.Serial(datastore["arduino-settings"]["port"], datastore["arduino-settings"]["baud"], timeout=0)
    #Setup a loop to send values at fixed intervals in seconds
    self.fixed_interval = datastore["fixed-interval"]
    # create database object 
    self.databaseWriter =  DatabaseWriter(datastore)

  def run(self):

    while True: 

      if self.ser.isOpen():
        read_serial = self.ser.readline()
        print(read_serial)
        if (read_serial[0:5] == "Start"):
          hum = read_serial[7:12]
          temp = read_serial[13:18]
          mic = read_serial[19:24]
          air_quality_num = read_serial[25:26]
          measurment = Measurment(hum, temp, mic, air_quality_num)
          # send reading to database 
          self.databaseWriter.run(measurment) 
   
      time.sleep(self.fixed_interval)

                 
class Measurment():
  
  def __init__(self, hum, temp, mic, air_quality_num):

    self.hum = hum
    self.temp = temp
    self.mic = mic
    
    if air_quality_num == 0 or air_quality_num == 1:
      self.air_quality = "High pollution"

    elif air_quality_num == 2:
       self.air_quality = "Low pollution"

    elif air_quality_num == 3:
       self.air_quality = "Fresh air"

  def getTemperature(self):
    return self.temp

  def getHumidity(self):
    return self.hum

  def getAirQuality(self):
    return self.air_quality
  
  def getSound(self):
    return self.mic

      


