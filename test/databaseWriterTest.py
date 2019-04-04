import json
from random import randint

from databaseWriter import DatabaseWriter
from databaseWriter import Firestore
from readSerial import Measurement


def test_database_writer(firestore_config):
    print("Testing database writer")
    database_writer = DatabaseWriter(firestore_config)
    measurement = Measurement(randint(0, 100), randint(0, 100), randint(0, 100), randint(0, 4), randint(0, 100))
    database_writer.save_measurement(measurement)


def test_database_writer_error(firestore_config):
    print("Testing database writer errors")
    incomplete_config = firestore_config.copy()
    incomplete_config["api-url"] = "https://www.google.ca/"
    database_writer = DatabaseWriter(incomplete_config)
    measurement = Measurement(randint(0, 100), randint(0, 100), randint(0, 100), randint(0, 4), randint(0, 100))
    try:
        database_writer.save_measurement(measurement)
        print("Failed to throw an error when posting to non api url")
    except Exception as e:
        print("Successfully threw an error")


# Todo: Rewrite if necessary after changes to firestore client
def test_firestore(firestore_config):
    print("Testing firestore")
    firestore = Firestore(firestore_config["api-key"], firestore_config["base-path"], firestore_config["api-url"])
    firestore.login(firestore_config["email"], firestore_config["password"])
    firestore.refresh()


if __name__ == '__main__':
    config_path = "../config/defaultConfig.json"
    with open(config_path, 'r') as f:
        config = json.load(f)
    firestore_config = config["database"]
    test_database_writer(firestore_config)
    test_database_writer_error(firestore_config)
