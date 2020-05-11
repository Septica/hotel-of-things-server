#include <Servo.h>
#include "SevSeg.h"
SevSeg sevseg; 
Servo door;

const int lampPin = 5;
const int doorPin = 2;
const int buttonPin = 11;
const int lampButtonPin = 10;
int doorState = 0;
int newDoorState = doorState;
int buttonState = 0;
int lampSwitchState = 0;
int lampState = LOW;
int acPower = 5;
void setup() 
{
  byte numDigits = 1;
  byte digitPins[] = {};
  byte segmentPins[] = {4, 3, 7, 6, 12, 9, 8, 13};
  bool resistorsOnSegments = true;

  byte hardwareConfig = COMMON_CATHODE; 
  sevseg.begin(hardwareConfig, numDigits, digitPins, segmentPins, resistorsOnSegments);
  sevseg.setBrightness(100);
  
  pinMode(lampPin,OUTPUT);
  pinMode(buttonPin,INPUT);
  digitalWrite(lampPin,lampState);  
  door.attach(doorPin);
  Serial.begin(9600);
}

void loop() 
{

  if(Serial.available() > 0){
    char input = Serial.read();
    if(input == 'U'){
      newDoorState = 1;
      lampState = HIGH;
    }else if(input == 'H'){
      acPower = acPower + 1;
    }else if(input == 'L'){
      acPower = acPower - 1;
    }else if(input == 'F'){
      lampState = LOW;
    }else if(input == 'T'){
      lampState = HIGH;
    }
  }
  int newButtonState = digitalRead(buttonPin);
  if (newButtonState != buttonState){
    buttonState = newButtonState;
    if(buttonState == HIGH) {
       Serial.println('D');
    }
    if(buttonState == LOW) {
       newDoorState = 0;
       delay(500);
    }
   
  }
  int newLampSwitchState = digitalRead(lampButtonPin);
  if (newLampSwitchState!= lampSwitchState){
    lampSwitchState = newLampSwitchState;
    if(lampSwitchState == HIGH) {
      if(lampState == LOW){
        lampState = HIGH;
      }else{
        lampState = LOW;
      }
       
    }
   
  }

  // action
   sevseg.setNumber(acPower);
  
  digitalWrite(lampPin,lampState);
   if(newDoorState != doorState){
      doorState = newDoorState;
      if(doorState == 1){
        door.write(179);
        delay(15);
      }else{
        door.write(90);
        delay(15);
      }
      
   }
   sevseg.refreshDisplay();
}
