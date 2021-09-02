#include <SPI.h>

byte address = 0x11; // 0B00010001
int CS= 10;

int value_i;
String input = "";

int i;
char data;
char res[100];

void setup()
{
pinMode (CS, OUTPUT);
SPI.begin();
Serial.begin(9600);
value_i=0;
}

void loop()
{
while (Serial.available() > 0)
{
//input += (char) Serial.read(); 
input =Serial.readString();
delay(5); 
}

value_i=input.toInt();
//Serial.println(value_i);

if(value_i>255)
{
  value_i=255;
}
digitalPotWrite(value_i);
}


int digitalPotWrite(int value)
{
   digitalWrite(CS,LOW); // select the chip
   SPI.transfer(address); // command byte
   SPI.transfer(value); // data byte 
   digitalWrite(CS,HIGH); // de-select the chip
}
