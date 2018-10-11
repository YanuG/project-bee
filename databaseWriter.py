#!/usr/bin/env python
import time
import requests
import json
import os

class DatabaseWriter():

    def __init__(self):


        os.getcwd()
        config_path = os.getcwd() + "/config/defaultConfig.json"

        with open(config_path, 'r') as f:
            datastore = json.load(f)

        self.firebase_url = datastore["firebase-url"]
  

    def run(self, led_reading):  

        #current time and date
        time_hhmmss = time.strftime('%H:%M:%S')
        date_mmddyyyy = time.strftime('%d/%m/%Y')
        
        #current location name
        led_location = 'Ottawa'
        print led_reading + ',' + time_hhmmss + ',' + date_mmddyyyy + ',' + led_location
        
        #insert record
        data = {'date':date_mmddyyyy,'time':time_hhmmss,'value':led_reading}
        result = requests.post(self.firebase_url + '/' + led_location + '/led.json', data=json.dumps(data))
        
        print 'Record inserted. Result Code = ' + str(result.status_code) + ',' + result.text
     
        