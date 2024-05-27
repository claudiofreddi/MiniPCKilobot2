#define  RELEMAX 5
#define  Rele_Master 0
#define  Rele_Motor 1
#define  Rele_Arduino 2
#define  Rele_USB3 3
#define  Rele_Unused 4


#define  RELE_INITIAL_STATUS_NO  0
#define  RELE_INITIAL_STATUS_NC  1

#define  Rele_Master_Pin 32
#define  ReleYY_Unused  33   // rele 2

#define  Rele_MotorPin  37
#define  Rele_ArduinoPin 36
#define  Rele_USB30Pin  35
#define  ReleXX_Unused  34   // rele 1 

#define RELE_NO_ON  LOW
#define RELE_NO_OFF HIGH

#define RELE_NC_ON HIGH
#define RELE_NC_OFF LOW


class Robot_Rele
{  

  const int RelePIN[RELEMAX] = {Rele_Master_Pin,Rele_MotorPin,Rele_ArduinoPin,Rele_USB30Pin,ReleXX_Unused};
  const int ReleInitStatus[RELEMAX] = {RELE_INITIAL_STATUS_NC,RELE_INITIAL_STATUS_NO,RELE_INITIAL_STATUS_NC,RELE_INITIAL_STATUS_NO,RELE_INITIAL_STATUS_NO};
  const String ReleName[RELEMAX] = {"Master","Motor","Arduino1","USB30","Unused"};
  long      ReleTimeOut[RELEMAX] = {0,0,0,0,0};
  long      ReleStartTime[RELEMAX] = {0,0,0,0,0};
  bool bReleTrace = false;
  
  bool IsSupplyOn(int ReleIdx);

public: 

  Robot_Rele();

  void Init();

  void ReleSetStatus(int Pin, bool turn_onoff, long timeout);

  void CheckTimeOut();

  void MasterSupply(bool turn_onoff, long timeout);

  bool IsMasterSupplyOn();
 
  void Arduino01Supply(bool turn_onoff, long timeout);

  bool IsArduino01SupplyOn();

  void Arduino01MotorsSupply(bool turn_onoff, long timeout);
  
  bool IsArduino01MotorsSupplyOn();

  bool IsUSB30SupplyOn();

  bool IsUnusedSupplyOn();

  void Switch_Arduino_And_Motors(bool turn_onoff);

  void PowerStatus();


  
};

Robot_Rele::Robot_Rele() {}

void Robot_Rele::PowerStatus() {
      Serial.println("Master Power: " + String(IsMasterSupplyOn()));
      Serial.println("Arduino Power: " + String(IsArduino01SupplyOn()));
      Serial.println("Motor Power: " + String(IsArduino01MotorsSupplyOn()));
      Serial.println("USB3.0 Power: " + String(IsUSB30SupplyOn()));
      Serial.println("Unused Power: " + String(IsUnusedSupplyOn()));

      
}

void Robot_Rele::Switch_Arduino_And_Motors(bool turn_onoff)
{
    
    ReleSetStatus(Rele_Master, turn_onoff,0);
    ReleSetStatus(Rele_Motor, turn_onoff,0);
    ReleSetStatus(Rele_Arduino, turn_onoff,0);

}

bool Robot_Rele::IsSupplyOn(int ReleIdx) 
{ 
  if (ReleInitStatus[ReleIdx] == RELE_INITIAL_STATUS_NC)
        return digitalRead(RelePIN[ReleIdx]) == RELE_NC_ON;
    else
       return digitalRead(RelePIN[ReleIdx]) == RELE_NO_ON;
}

bool Robot_Rele::IsUnusedSupplyOn() {return IsSupplyOn(Rele_Unused); }

bool Robot_Rele::IsUSB30SupplyOn() {return IsSupplyOn(Rele_USB3); }

bool Robot_Rele::IsMasterSupplyOn()  {return IsSupplyOn(Rele_Master);  }

bool Robot_Rele::IsArduino01SupplyOn()   {return IsSupplyOn(Rele_Arduino);  }

bool Robot_Rele::IsArduino01MotorsSupplyOn()  {return IsSupplyOn(Rele_Motor);  }


void Robot_Rele::Init() 
{
  if (bReleTrace)
    Serial.print("Robot_Rele::Init()");
  for (int i=0;i<RELEMAX;i++)
  {
      if (bReleTrace)
        Serial.println(ReleName[i] + " index:" + String(i));
      pinMode(RelePIN[i], OUTPUT);
      ReleSetStatus(i, false,0);
      delay(1000);
  }

}

void Robot_Rele::ReleSetStatus(int ReleIdx, bool turn_onoff, long timeout)
{

  if (bReleTrace)
    if (turn_onoff)
      Serial.println(ReleName[ReleIdx] + " ON");
    else
      Serial.println(ReleName[ReleIdx] + " OFF");


  if (ReleInitStatus[ReleIdx] == RELE_INITIAL_STATUS_NC)
    if (turn_onoff)
      digitalWrite(RelePIN[ReleIdx],  RELE_NC_ON);
    else
      digitalWrite(RelePIN[ReleIdx],  RELE_NC_OFF);
  else
    if (turn_onoff)
      digitalWrite(RelePIN[ReleIdx],  RELE_NO_ON);
    else
      digitalWrite(RelePIN[ReleIdx],  RELE_NO_OFF);

    delay(30);

  if (!turn_onoff)
    {
      ReleStartTime[ReleIdx] =0;
      ReleTimeOut[ReleIdx] = 0;
    }
  else
    if (timeout>0)
    {
      ReleStartTime[ReleIdx] = millis(); 
      ReleTimeOut[ReleIdx] = timeout;
    }
    else  
    {
      ReleStartTime[ReleIdx] = 0;
      ReleTimeOut[ReleIdx] = 0;
    }

}

void Robot_Rele::CheckTimeOut()
{
  for (int ReleIdx=0;ReleIdx<RELEMAX;ReleIdx++)
    if (ReleTimeOut[ReleIdx] > 0)
      if (ReleStartTime[ReleIdx] +ReleTimeOut[ReleIdx] > millis())
          ReleSetStatus(ReleIdx,false, 0); // Set off
}

void Robot_Rele::MasterSupply(bool turn_onoff, long timeout = 0) 
{
  ReleSetStatus(Rele_Master,turn_onoff, timeout);
}

void Robot_Rele::Arduino01Supply(bool turn_onoff, long timeout = 0) 
{
  
  ReleSetStatus(Rele_Arduino,turn_onoff, timeout);
}

void Robot_Rele::Arduino01MotorsSupply(bool turn_onoff, long timeout = 0) 
{
  ReleSetStatus(Rele_Motor,turn_onoff, timeout);
}


