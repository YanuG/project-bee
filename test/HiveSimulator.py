import json
import datetime
from random import randint
from databaseWriter import Firestore
from time import sleep


class HiveSimulator:
    def __init__(self, firestore, cluster_id, hive_id):
        self.cluster_id = cluster_id
        self.hive_id = hive_id
        self.firestore = firestore

    def save_measurement(self):
        path = "/measurements/%s/hives/%s/measurements" % (self.cluster_id, self.hive_id)
        payload = HiveSimulator.create_random_payload()
        print("Uploading simulated measurement", payload)
        self.firestore.add_document(path, payload)

    @staticmethod
    def create_random_payload():
        return {
            "fields": {
                "date": {"timestampValue": datetime.datetime.utcnow().isoformat("T") + "Z"},
                "temperature": {"integerValue": str(randint(32, 36))},
                "humidity": {"integerValue": str(randint(40, 80))},
                "air_quality": {"integerValue": str(randint(2, 5))},
                # "mass": {"integerValue": str(randint(0, 100))},
                "bees": {"integerValue": str(randint(0, 100))},
                "frequency": {"integerValue": str(randint(0, 100))}
            }
        }


class ClusterSimulator:
    def __init__(self, config):
        self.firestore = Firestore(config["api-key"], config["base-path"])
        self.firestore.login(config["email"], config["password"])

    def start_simulation(self):
        south_hive = HiveSimulator(self.firestore, "0cK5kWv3aF92f0JRbkyC", "jJCbkX3Vm71OlzsRaIx1")
        east_hive = HiveSimulator(self.firestore, "0cK5kWv3aF92f0JRbkyC", "3gbttJjw7SWYlIqz7uTg")
        west_hive = HiveSimulator(self.firestore, "0cK5kWv3aF92f0JRbkyC", "okF0pYIZ1eU2kRY9jUcb")

        hives = [south_hive, east_hive, west_hive]
        for i in range(6):
            for hive in hives:
                hive.save_measurement()
                sleep(10)


if __name__ == '__main__':
    config_path = "../config/defaultConfig.json"
    with open(config_path, 'r') as file:
        config = json.load(file)

    cluster_simulator = ClusterSimulator(config["database"])
    cluster_simulator.start_simulation()
