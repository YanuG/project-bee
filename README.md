# Project Bee Backend
## CEG4912 Capstone Project

For the frontend portion of this project: [Click Here](https://github.com/albert-fung/Project-Bee)

## Software Requirments 

*   Python 2.7

## Hardware Used

*   Arduino Uno 
*   Base Shield 
*   Grove Air Quality Sensor 
*   DHT 22 Temperature and Huminity Sensor 
*   MAX4466 Microphone

## Install Dependencies

pip install pathlib2

## Run Project

1. Add DHT-Library to arduino. 

2. Upload sensor.ino to the arduino. 

3. To collect the sensor information and upload to firebase run in terminal  `python main.py`

## Running Tests
To test the DatabaseWriter.py (without the hardware), DatabaseWriterTest.py can be used to populate Firestore with a new measurement value. 
