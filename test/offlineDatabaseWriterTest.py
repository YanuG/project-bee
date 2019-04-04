import sys
import datetime
import sqlite3 
from pathlib2 import Path
import json


def main(args):

    project_root = Path(__file__).resolve().parent.parent
    config_path = project_root/"config/defaultConfig.json"

    with open(str(config_path), 'r') as f:
         config_file = json.load(f)

    conn = sqlite3.connect(config_file["offline-database-filename"])
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM measurements")
    except Exception as e:
        print "False"
        cursor.execute('''CREATE TABLE measurements
            (date, temperature, humidity, air_quality, bees, frequency)''')

if __name__ == "__main__":
    main(sys.argv)