import json
from random import randint

from databaseWriter import DatabaseWriter
from databaseWriter import Firestore
from readSerial import Measurment


def test_database_writer(firestore_config):
    print("Testing database writer")
    database_writer = DatabaseWriter(firestore_config)
    measurement = Measurment(randint(0, 100), randint(0, 100), randint(0, 100), randint(0, 4), randint(0, 100))
    database_writer.save_measurement(measurement)


def test_firestore(firestore_config):
    print("Testing firestore")
    firestore = Firestore(firestore_config["api-key"], "")
    firestore.login(firestore_config["email"], firestore_config["password"])
    firestore.refresh()


if __name__ == '__main__':
    config_path = "../config/defaultConfig.json"
    with open(config_path, 'r') as f:
        config = json.load(f)
    firestore_config = config["firestore"]
    test_firestore(firestore_config)
    test_database_writer(firestore_config)

