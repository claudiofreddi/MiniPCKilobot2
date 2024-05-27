#define LEDMAX 4

#define LED_00_pin 7
#define LED_01_pin 8
#define LED_02_pin 9
#define LED_03_pin 10


class Robot_Led 
{  
  // define here Led and Commands
  const int ledPIN[LEDMAX] = {LED_00_pin,LED_01_pin,LED_02_pin,LED_03_pin};
  const String ledCommand[LEDMAX] = {"led0","led1","led2","led3"};
  bool bLedTrace = false;

public: 

  Robot_Led();

  void Init();
  
  void testAll();

  void turn_led(int pinLedIndex, bool on_off);
 
};

Robot_Led::Robot_Led() {}

void Robot_Led::Init() 
{
  for (int i=0;i<LEDMAX;i++)
    pinMode(ledPIN[i], OUTPUT);

}


void Robot_Led::turn_led(int pinLedIndex, bool on_off)
{
    digitalWrite(ledPIN[pinLedIndex], (on_off?HIGH:LOW));
    if (bLedTrace)
      if (on_off)
        Serial.println(ledCommand[pinLedIndex] + " ON");     
      else
        Serial.println(ledCommand[pinLedIndex] + " OFF");     

}


void Robot_Led::testAll() 
{
  for (int i=0;i<LEDMAX;i++)
  {
    turn_led(i, true); 
    delay(1000); 
  }
  
  for (int i=0;i<LEDMAX;i++)
  {
    turn_led(i, false); 
    delay(100); 
  }


}