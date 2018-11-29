import time
import requests
import json
import datetime


class DatabaseWriter:

    def __init__(self, firestore_config):
        # Save the cluster and hive ID corresponding to this unit
        self.cluster_id = firestore_config["cluster-id"]
        self.hive_id = firestore_config["hive-id"]
        # Create the firestore client
        self.firestore = Firestore(firestore_config["api-key"], firestore_config["base-path"])
        # Get the credentials from the config or command line
        email = firestore_config["email"] \
            if "email" in firestore_config \
            else input("Email: ")
        password = firestore_config["password"] \
            if "password" in firestore_config \
            else input("Password: ")
        self.firestore.login(email, password)

    @staticmethod
    def measurement_to_document(measurement):
        return {
            "fields": {
                "date": {"timestampValue": datetime.datetime.utcnow().isoformat("T") + "Z"},
                "temperature": {"integerValue": str(measurement.temperature)},
                "humidity": {"integerValue": str(measurement.humidity)},
                "air_quality": {"integerValue": str(measurement.air_quality)},
                # "mass": {"integerValue": str(measurement.mass)},
                "bees": {"integerValue": str(measurement.bee_count)},
                "frequency": {"integerValue": str(int(measurement.frequency))}
            }
        }

    def save_measurement(self, measurement):
        path = "/measurements/%s/hives/%s/measurements" % (self.cluster_id, self.hive_id)
        payload = self.measurement_to_document(measurement)
        self.firestore.add_document(path, payload)


class Firestore:
    LOGIN_URL = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key="
    REFRESH_URL = "https://securetoken.googleapis.com/v1/token?key="
    FIRESTORE_URL = "https://firestore.googleapis.com/v1beta1/projects/"

    def __init__(self, api_key, base_path):
        self.api_key = api_key
        self.url = Firestore.FIRESTORE_URL + base_path
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


class FirestoreError(ValueError):
    def __init__(self, code, message, details):
        super(FirestoreError, self).__init__("%d: %s" % (code, message))
        self.code = code
        self.message = message
        self.details = details
