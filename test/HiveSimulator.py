import json
from random import randint
from databaseWriter import Firestore
from time import sleep
from readSerial import Measurement


class HiveSimulator:
    def __init__(self, firestore, cluster_id, hive_id):
        self.cluster_id = cluster_id
        self.hive_id = hive_id
        self.firestore = firestore

    def save_measurement(self, measurement):
        endpoint = "/addMeasurements"
        payload = {
            "hiveId": self.hive_id,
            "clusterId": self.cluster_id,
            "measurements": [measurement.to_dict()]
        }
        self.firestore.post_to_endpoint(endpoint, payload)
        print("Posting", payload)

    @staticmethod
    def create_random_measurement():
        return Measurement(randint(40, 80), randint(32, 36), randint(0, 100), randint(3, 5), randint(0, 100))


class ClusterSimulator:
    def __init__(self, config):
        self.firestore = Firestore(config["api-key"], config["base-path"], config["api-url"])
        self.firestore.login(config["email"], config["password"])

    def start_simulation(self):
        south_hive = HiveSimulator(self.firestore, "0cK5kWv3aF92f0JRbkyC", "jJCbkX3Vm71OlzsRaIx1")
        east_hive = HiveSimulator(self.firestore, "0cK5kWv3aF92f0JRbkyC", "3gbttJjw7SWYlIqz7uTg")
        west_hive = HiveSimulator(self.firestore, "0cK5kWv3aF92f0JRbkyC", "okF0pYIZ1eU2kRY9jUcb")

        hives = {"west": west_hive, "east": east_hive, "south": south_hive}
        for i in range(6):
            for hive_name in hives:
                print("Uploading to ", hive_name)
                measurement = HiveSimulator.create_random_measurement()
                hives[hive_name].save_measurement(measurement)
                sleep(10)


if __name__ == '__main__':
    config_path = "../config/defaultConfig.json"
    with open(config_path, 'r') as file:
        config = json.load(file)

    cluster_simulator = ClusterSimulator(config["database"])
    cluster_simulator.start_simulation()
