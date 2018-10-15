import json
import os
from random import randint

from databaseWriter import DatabaseWriter
from readSerial import Measurment

if __name__ == '__main__':
    print("Testing database writer")

    os.getcwd()
    config_path = os.getcwd() + "/config/defaultConfig.json"
    with open(config_path, 'r') as f:
        datastore = json.load(f)

    databaseWriter = DatabaseWriter(datastore)
    measurement = Measurment(randint(0, 100), randint(0, 100), randint(0, 4))
    databaseWriter.run(measurement)
