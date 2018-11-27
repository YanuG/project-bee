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

	
	//Variables
	float hum;  //Stores humidity value
	float temp; //Stores temperature value
	double freq; //Stores microphone maximum frequency value
	int current_quality; //Stores air quality value
	int sampling_period_us;
	long microseconds; 
	double vReal[SAMPLES]; //Stores real part of microphone frequency
	double vImag[SAMPLES]; //Stores imaginary part of microphone frequency
	 

	boolean tempChanged = false; //Interrupt for temp sensor
	boolean airChanged = false; //Interrupt for air quality sensor
	boolean soundChanged = false; //Interrupt for microphone

	
	int counter =0;

	
	int delaytime = 200; //Time for interrupt


	String msg; //msg to send through serial

	
	void setup(){
	 
		Serial.begin(9600);   //Set serial baud

		cli();//stop interrupts
	 
		//set timer1 interrupt at 1kHz
		TCCR1A = 0; // set entire TCCR1A register to 0
		TCNT1  = 0; //initialize counter value to 0
	 
		// set timer count for 1khz increments
		OCR1A = 1999; // = (16*10^6) / (1000*8) - 1; 
					  //had to use 16 bit timer1 for this bc 1999>255, but could switch to timers 0 or 2 with larger prescaler
	 
		
		TCCR1B |= (1 << WGM12); //Turn on CTC mode
		
		TCCR1B |= (1 << CS11);  //Set CS11 bit for 8 prescaler

		TIMSK1 |= (1 << OCIE1A); //Enable timer compare interrupt
		
		sei(); //Allow interrupts

		airqualitysensor.init(14); //Initalize airqualitysensor

	}

	
	void loop(){

	   temperatureSensor();
	   microphoneSensor();
	   airQualitySensor();
	  
	}


	ISR(TIMER1_COMPA_vect){

		//generates pulse wave of frequency 1Hz/2 = 0.5kHz (takes two cycles for full wave- toggle high then toggle low)
		//Increment counter if its less than delaytime otherwise reset it
		if (counter < delaytime){  
			counter = counter + 1;
		}
		else{
			counter = 0;
			tempChanged=true;
		}
	}


	void temperatureSensor(){

	   if(tempChanged == true){
			tempChanged = false;
			int chk = DHT.read22(DHT22_PIN);
			hum = DHT.humidity;     //Read data and store it to variable hum
			temp= DHT.temperature;  //Read data and store it to variable temp
			airChanged = true;
	   }
	}

	
	void airQualitySensor(){

		if (airChanged == true){
			airChanged = false;
			current_quality=airqualitysensor.slope();
			sendMessage();
		}
	  
	}

	
	void microphoneSensor(){
	   
		if (soundChanged == true){
			soundChanged = false;
		
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
	}
	
	//Prints serial message including the sensors values
	void sendMessage(){

		msg = "[Humidity: ";
		msg += hum;
		msg += "; Temperature: ";
		msg += temp;
		msg += "; Quality: ";
		msg += current_quality;
		msg += "; Sound: ";
		msg += freq;
		msg += "] \n";
		
		Serial.print(msg);


	}
