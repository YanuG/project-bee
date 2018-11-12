//Libraries
#include <dht.h>
#include"AirQuality.h"
#include"Arduino.h"
#include "arduinoFFT.h"

//Object for temp sensor
dht DHT;
//Object for air quality sensor
AirQuality airqualitysensor;

//Constants
#define DHT22_PIN 7     

//Variables
float hum;  //Stores humidity value
float temp; //Stores temperature value
int peakToPeak;
int current_quality; //Stores air_quality_value

//Interrupt for temp sensor 
boolean flag1 = false;
int counter =0;
// Interrupt for air quality sensor
boolean flag2 = false;

// Time for interrupt
int delaytime = 200;

// msg to send through serial
String msg;

void setup()
{
    // Set serial baud
    Serial.begin(9600);

    cli();//stop interrupts
    //set timer1 interrupt at 1kHz
    TCCR1A = 0;// set entire TCCR1A register to 0
    TCNT1  = 0;//initialize counter value to 0
    // set timer count for 1khz increments
    OCR1A = 1999;// = (16*10^6) / (1000*8) - 1
    //had to use 16 bit timer1 for this bc 1999>255, but could switch to timers 0 or 2 with larger prescaler
    // turn on CTC mode
    TCCR1B |= (1 << WGM12);
    // Set CS11 bit for 8 prescaler
    TCCR1B |= (1 << CS11);  
    // enable timer compare interrupt
    TIMSK1 |= (1 << OCIE1A);
    sei();//allow interrupts

    // Initalize airqualitysensor
    airqualitysensor.init(14);

}

void loop()

{

 temperatureSensor();
 microphoneSensor();
 airQualitySensor();
  
}

void temperatureSensor() {

   if(flag1 == true){
    flag1 = false;
    int chk = DHT.read22(DHT22_PIN);
    //Read data and store it to variables hum and temp
    hum = DHT.humidity;
    temp= DHT.temperature;
    flag2 = true;
   }
}

void airQualitySensor() {

    if (flag2 == true) {
      flag2 = false;
      current_quality=airqualitysensor.slope();
      sendMessage();
    }
  
}

void sendMessage() {


 msg = "[Humidity: ";
 msg += hum;
 msg += "; Temperature: ";
 msg += temp;
 msg += "; Quality: ";
 msg += current_quality;
 msg += "; Sound: ";
 msg += peakToPeak ;
 msg += "] \n";
 Serial.print(msg);


}

ISR(TIMER1_COMPA_vect){

  //generates pulse wave of frequency 1Hz/2 = 0.5kHz (takes two cycles for full wave- toggle high then toggle low)
  if (counter < delaytime){
    counter = counter + 1;
  }
  else{
    counter = 0;
    flag1=true;
  }
}

/****************************************
Microphone 
****************************************/

 
#define SAMPLES 128             //Must be a power of 2
#define SAMPLING_FREQUENCY 9999 //Hz, must be less than 10000 due to ADC
 
arduinoFFT FFT = arduinoFFT();
 
unsigned int sampling_period_us;
unsigned long microseconds;
 
double vReal[SAMPLES];
double vImag[SAMPLES];
 
 
void microphoneSensor() {
   
    /*SAMPLING*/
    for(int i=0; i<SAMPLES; i++)
    {
        microseconds = micros();    //Overflows after around 70 minutes!
     
        vReal[i] = analogRead(0);
        vImag[i] = 0;
     
        while(micros() < (microseconds + sampling_period_us)){
        }
    }
 
    /*FFT*/
    FFT.Windowing(vReal, SAMPLES, FFT_WIN_TYP_HAMMING, FFT_FORWARD);
    FFT.Compute(vReal, vImag, SAMPLES, FFT_FORWARD);
    FFT.ComplexToMagnitude(vReal, vImag, SAMPLES);
    double peak = FFT.MajorPeak(vReal, SAMPLES, SAMPLING_FREQUENCY);
 
    /*PRINT RESULTS*/
    Serial.println(peak);     //Print out what frequency is the most dominant.

 
    delay(50);  //milliseconds
}

