#!/usr/bin/env python
import time
import requests
import json
from requests import HTTPError



class DatabaseWriter:

    def __init__(self, datastore):
        self.firebase_url = datastore["firebase-url"]
        self.cluster_id = datastore["cluster-id"]
        self.hive_id = datastore["hive-id"]

    def run(self, measurement):
        payload = {
            "temperature": measurement.temp,
            "humidity": measurement.hum,
            "time": time.time()
        }
        url = '%s/measurements/%s/%s.json' % (self.firebase_url, self.cluster_id, self.hive_id)
        response = requests.post(url, data=json.dumps(payload))

        try:
            response.raise_for_status()
            print("Saved to Firebase")
        except HTTPError:
            print("Failed to save to Firebase: " + response.text)
