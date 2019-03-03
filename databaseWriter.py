import time
import requests
import json
import datetime
import sqlite3 


class DatabaseWriter:

    def __init__(self, config_file):

        # Online database
        # Save the cluster and hive ID corresponding to this unit
        self.cluster_id = config_file["cluster-id"]
        self.hive_id = config_file["hive-id"]
        # Create the firestore client
        self.firestore = Firestore(config_file["api-key"], config_file["base-path"], config_file["api-url"])
        # Get the credentials from the config_file or command line
        email = config_file["email"] \
            if "email" in config_file \
            else input("Email: ")
        password = config_file["password"] \
            if "password" in config_file \
            else input("Password: ")
        self.firestore.login(email, password)

        # Offline database
        # Create local file to store measurment information
        self.conn =  sqlite3.connect(config_file["offline-database-filename"])
        self.cursor = self.conn.cursor()

        # Check if table exists
        try:
            self.cursor.execute("SELECT * FROM measurments")
        except Exception as e:
            self.cursor.execute('''CREATE TABLE measurments
                (date, temperature, humidity, air_quality, bees, frequency)''')
        

    @staticmethod
    def measurement_to_document(measurement):
        return {
            "fields": {
                "date": {"timestampValue": datetime.datetime.utcnow().isoformat("T") + "Z"},
                "temperature": {"integerValue": str(int(measurement.temperature))},
                "humidity": {"integerValue": str(int(measurement.humidity))},
                "air_quality": {"integerValue": str(measurement.air_quality)},
                # "mass": {"integerValue": str(measurement.mass)},
                "bees": {"integerValue": str(measurement.bee_count)},
                "frequency": {"integerValue": str(int(measurement.frequency))}
            }
        }

    def add_to_measurement_buffer(self, measurement):
        endpoint = "/addMeasurements"
        payload = {
            "hiveId": self.hive_id,
            "clusterId": self.cluster_id,
            "measurements": [measurement.to_dict()]
        }
        self.firestore.post_to_endpoint(endpoint, payload)

    def save_measurement(self, measurement):
        # save measurements to online database
        self.add_to_measurement_buffer(measurement)

        # save measurments into offline database
        self.cursor.execute("INSERT INTO measurments VALUES (? , ? , ?, ?, ?, ?) " , 
            (datetime.datetime.utcnow().isoformat("T") , measurement.temperature, measurement.humidity, measurement.air_quality, measurement.bee_count, measurement.frequency))
        self.conn.commit()

# Todo: Refactor to handle auth in new REST endpoint once implemented
class Firestore:
    LOGIN_URL = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key="
    REFRESH_URL = "https://securetoken.googleapis.com/v1/token?key="
    FIRESTORE_URL = "https://firestore.googleapis.com/v1beta1/projects/"

    def __init__(self, api_key, base_path, api_url):
        self.api_key = api_key
        self.url = Firestore.FIRESTORE_URL + base_path
        self.api_url = api_url
        self.refresh_token = None
        self.id_token = None
        self.user_id = None
        self.expires_at = time.time() - 1

    @staticmethod
    def raise_firestore_errors(payload):
        if "error" in payload:
            print(payload)
            error = payload["error"]
            details = error["errors"] if "errors" in error else None
            raise FirestoreError(error["code"], error["message"], details)

    def login(self, email, password):
        response = requests.post(Firestore.LOGIN_URL + self.api_key, {
            "email": email,
            "password": password,
            "returnSecureToken": True
        })
        response.raise_for_status()
        payload = response.json()
        self.raise_firestore_errors(payload)
        self.refresh_token = payload["refreshToken"]
        self.id_token = payload["idToken"]
        self.user_id = payload["localId"]
        self.expires_at = time.time() + int(payload["expiresIn"])
        print("Successful login")

    def refresh(self):
        if not self.refresh_token:
            raise ValueError("No refresh token")
        response = requests.post(Firestore.REFRESH_URL + self.api_key, {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token
        })
        response.raise_for_status()
        payload = response.json()
        self.raise_firestore_errors(payload)
        self.refresh_token = payload["refresh_token"]
        self.id_token = payload["id_token"]
        self.user_id = payload["user_id"]
        self.expires_at = time.time() + int(payload["expires_in"])
        print("Successful refresh")

    def refresh_if_token_expired(self):
        if time.time() > self.expires_at:
            self.refresh()

    def add_document(self, path, payload):
        self.refresh_if_token_expired()
        url = self.url + path
        headers = {
            "Authorization": "Bearer " + self.id_token,
            'Content-Type': 'application/json'
        }
        response = requests.post(url, json.dumps(payload), headers=headers)
        response_payload = response.json()
        self.raise_firestore_errors(response_payload)
        print("Successful document creation")

    def post_to_endpoint(self, endpoint, payload):
        url = self.api_url + endpoint
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json.dumps(payload), headers=headers)
        response.raise_for_status()


class FirestoreError(ValueError):
    def __init__(self, code, message, details):
        super(FirestoreError, self).__init__("%d: %s" % (code, message))
        self.code = code
        self.message = message
        self.details = details
