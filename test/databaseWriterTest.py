import json
import os
from random import randint

from databaseWriter import DatabaseWriter
from databaseWriter import Firestore
from readSerial import Measurment


def test_database_writer(config):
    print("Testing database writer")
    database_writer = DatabaseWriter(config)
    measurement = Measurment(randint(0, 100), randint(0, 100), randint(0, 100), randint(0, 4))
    database_writer.run(measurement)


def test_firestore(config):
    print("Testing firestore")
    firestore = Firestore(config["api-key"], "")
    firestore.login(config["email"], config["password"])
    firestore.refresh()


if __name__ == '__main__':
    config_path = "../config/defaultConfig.json"
    with open(config_path, 'r') as f:
        config = json.load(f)
    config["store_database"] = True
    test_firestore(config)
    test_database_writer(config)

