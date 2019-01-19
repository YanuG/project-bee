	//Libraries
	#include <dht.h>
	#include"AirQuality.h"
	#include"Arduino.h"
	#include "arduinoFFT.h"


	dht DHT; //Object for temp sensor

	AirQuality airqualitysensor; //Object for air quality sensor

	arduinoFFT FFT = arduinoFFT(); //Object for microphone


	//Constants
	#define DHT22_PIN 7
	#define SAMPLES 128             //Must be a power of 2
	#define SAMPLING_FREQUENCY 9999 //Hz, must be less than 10000 due to ADC

  //Pins
  const int LIGHT_PIN0 = A3;
  const int LIGHT_PIN1 = A4;
  
	//Variables
	int hum, temp;  //Stores humidity and temperature values
  int current_quality; //Stores air quality value
  int freq; //Stores microphone maximum frequency value
	int sampling_period_us;
	long microseconds; 
	double vReal[SAMPLES]; //Stores real part of microphone frequency
	double vImag[SAMPLES]; //Stores imaginary part of microphone frequency
  int numBees; //Stores the number of bees inside the hive (int)
  int lightThreshold = 10; //could be changed later
  int curState = -1;
  int prevState = -1;
  // states are (' means it is blocked):
  // both unblocked = 0
  // outside', inside = 1
  // outside', inside' = 2
  // outside, inside' = 3
	 

	boolean sensor_interrupt = false; //Interrupt for sensors
	int counter =0;
	int delaytime = 200; //Time for interrupt


	
	void setup(){
  
    //Set serial baud
		Serial.begin(9600);   
		cli();//stop interrupts
	 
		//set timer1 interrupt at 1kHz
		TCCR1A = 0; // set entire TCCR1A register to 0
		TCNT1  = 0; //initialize counter value to 0
		// set timer count for 1khz increments
		OCR1A = 1999; // = (16*10^6) / (1000*8) - 1; 
		TCCR1B |= (1 << WGM12); //Turn on CTC mode
		TCCR1B |= (1 << CS11);  //Set CS11 bit for 8 prescaler
		TIMSK1 |= (1 << OCIE1A); //Enable timer compare interrupt
		sei(); //Allow interrupts

    //Initalize airqualitysensor
		airqualitysensor.init(14);

    //Initialize Pins for Bee counter
    pinMode(LIGHT_PIN0, INPUT); 
    pinMode(LIGHT_PIN1, INPUT);

	}

	
	void loop(){

     if (sensor_interrupt){
        temperatureSensor();
        airQualitySensor();
        sendMessage();
     }
	   
	   microphoneSensor();
     beeCounter();
     
     
	}


	ISR(TIMER1_COMPA_vect){

		//generates pulse wave of frequency 1Hz/2 = 0.5kHz (takes two cycles for full wave- toggle high then toggle low)
		//Increment counter if its less than delaytime otherwise reset it
		if (counter < delaytime){  
			counter = counter + 1;
		}
		else{
			counter = 0;
		  sensor_interrupt = true;
		}
	}

  void changeState(int nextState){
//    Serial.print("curState: ");
//    Serial.println(curState);
//    Serial.print("prevState: ");
//    Serial.println(prevState);
    if(nextState != curState){
      prevState = curState;
      curState = nextState;
      if(curState == 0){ //bees have finished entering/exiting
        if(prevState == 1){
          --numBees;
//          Serial.print("numBees: ");
//          Serial.println(numBees);
        }else if(prevState == 3){
          ++numBees;
//          Serial.print("numBees: ");
//          Serial.println(numBees);
        }
      }
    }
  }

  void beeCounter(){
    int outside = analogRead(LIGHT_PIN0);
    int inside = analogRead(LIGHT_PIN1);
    if(outside > lightThreshold && inside > lightThreshold){ //both unblocked
      changeState(0);
    }else if(outside < lightThreshold && inside > lightThreshold){ //outside is blocked
      changeState(1);
    }else if(outside < lightThreshold && inside < lightThreshold){ //both blocked
      changeState(2);
    }else if(outside > lightThreshold && inside < lightThreshold){ //inside is blocked 
      changeState(3); 
    }
  }


	void temperatureSensor(){

	
		DHT.read22(DHT22_PIN);
		hum = DHT.humidity;     //Read data and store it to variable hum
		temp= DHT.temperature;  //Read data and store it to variable temp

	}

	
	void airQualitySensor(){

		current_quality= airqualitysensor.slope();  
	}
 

	
	void microphoneSensor(){
	   
		/*SAMPLING*/
		for(int i=0; i<SAMPLES; i++){
			microseconds = micros();    //Overflows after around 70 minutes!
		 
			vReal[i] = analogRead(A2); //Read real part of data from pin A2 and store it in array vReal
			vImag[i] = 0; //Imaginary part of data is set to 0
		 
			while(micros() < (microseconds + sampling_period_us)){}
		}
	 
	 
		/*FFT*/
		FFT.Windowing(vReal, SAMPLES, FFT_WIN_TYP_HAMMING, FFT_FORWARD); //
		FFT.Compute(vReal, vImag, SAMPLES, FFT_FORWARD); //
		FFT.ComplexToMagnitude(vReal, vImag, SAMPLES); //Convert the complex number vReal, vImag into a magnitude
		freq = FFT.MajorPeak(vReal, SAMPLES, SAMPLING_FREQUENCY); //Store maximum frequency value (peak) in freq
	 

	}


void convertToHex(int value, int precision) {

    char tmp[16];
    char format[128];
    sprintf(format, "0x%%.%dX", precision);
    sprintf(tmp, format, value);
    Serial.print(tmp);
    Serial.print(" ");
  }

	
	void sendMessage(){

		convertToHex(hum , 2);
    convertToHex(temp, 2);
		convertToHex(current_quality, 1);
    convertToHex(freq, 3);
    convertToHex(numBees, 2);


	}
