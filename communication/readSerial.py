#!/usr/bin/env python
import sys
import serial
import time
import os
import json

from databaseWriter import DatabaseWriter


class ReadSerial():

  def __init__(self):

    os.getcwd()
    os.chdir('..')
    config_path = os.getcwd() + "/config/defaultConfig.json"


    with open(config_path, 'r') as f:
        datastore = json.load(f)

    # Connect to Serial Port for communication
    self.ser = serial.Serial(datastore["arduino-settings"]["port"], datastore["arduino-settings"]["baud"], timeout=0)
    #Setup a loop to send values at fixed intervals in seconds
    self.fixed_interval = datastore["fixed-interval"]
    # create database object 
    self.databaseWriter =  DatabaseWriter()

  def run(self):

    while True: 

      #LED value obtained from Arduino   - this is tempory until we have sensors working    
      led_reading = self.ser.readline()
      time.sleep(self.fixed_interval)

      # send reading to database 
      # TODO need to create a data object and store serial information in it
      self.databaseWriter.run(led_reading) 
              

  
def main(args):
    readSerial = ReadSerial()
    readSerial.run()

if __name__ == "__main__":
    # run main when this file is ran directly as an executable (is not imported from another script)
    try:
      main(sys.argv)
    except KeyboardInterrupt:
      print ("end script")
