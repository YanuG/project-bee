#!/usr/bin/env python
import serial
import time
import requests
import json
firebase_url = 'https://test-project-9c6c7.firebaseio.com/'

#Connect to Serial Port for communication
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=0)
#Setup a loop to send LED values at fixed intervals
#in seconds
fixed_interval = 5

while True:
  try:
    #LED value obtained from Arduino       
    led_reading = ser.readline()
    
    #current time and date
    time_hhmmss = time.strftime('%H:%M:%S')
    date_mmddyyyy = time.strftime('%d/%m/%Y')
    
    #current location name
    led_location = 'Ottawa'
    print led_reading + ',' + time_hhmmss + ',' + date_mmddyyyy + ',' + led_location
    
    #insert record
    data = {'date':date_mmddyyyy,'time':time_hhmmss,'value':led_reading}
    result = requests.post(firebase_url + '/' + led_location + '/temperature.json', data=json.dumps(data))
    
    print 'Record inserted. Result Code = ' + str(result.status_code) + ',' + result.text
    time.sleep(fixed_interval)
  except IOError:
    print('Error! Something went wrong.')
  time.sleep(fixed_interval)
