#include <SPI.h>

byte address = 0x11; // 0B00010001
int CS= 10;
long Rab = 10000;   // 10k ohm

int value_i;
String input = "";


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
    value_i=input.toInt();
  
    if(value_i>255)
    {
      value_i=255;
    }
    digitalPotWrite(value_i);
    printRes(value_i);
  }

}


void digitalPotWrite(int value)
{
   digitalWrite(CS,LOW); // select the chip
   SPI.transfer(address); // command byte
   SPI.transfer(value); // data byte 
   digitalWrite(CS,HIGH); // de-select the chip   
}

void printRes(int Dn)
{
  
  long Rwa = (Rab * (256 - Dn))/256;
  long Rwb = (Rab * Dn)/256;
    
  Serial.print("Rwa = ");
  Serial.print(Rwa);   
  Serial.println();
  Serial.print("Rwb = "); 
  Serial.print(Rwb);

  Serial.println();
  Serial.println();
}
