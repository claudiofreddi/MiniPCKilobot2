#include <time.h>
int motor1pin1 = 42;
int motor1pin2 = 43;

int motor2pin1 = 38;
int motor2pin2 = 39;

int  EnApin = 44;
int  EnBpin = 45;


int  Rele01_USB30NO = 35;
int  Rele01_Unised = 34;
int  Rele01_ArduinoNC = 36;
int  Rele01_MotorNO = 37;

int  Rele02_MasterNC = 32;
int  Rele02_Unused = 33;

#define RELE_NO_ON  LOW
#define RELE_NO_OFF HIGH

#define RELE_NC_ON HIGH
#define RELE_NC_OFF LOW



long mytime;


class Robot_Motors
{  
  
  long _runtimeout = 0;
  String _lastCommand = "";
  long _startrun = 0;
  bool _ForceEnableWhenRun = false;
  bool _motor_power_status = false;
  bool bMotorTrace = false;

public: 

  Robot_Motors();

  void Init();
  
  void SetSpeed(int Speed);

  bool IsToRun(String ThisCommand);

  void RunFw(long RunTimeout);
 
  void RunBw(long RunTimeout);

  void Rotate(int dir = 1, long RunTimeout = 0);

  void Stop();

  void HighSpeed();

  void LowSpeed();

  void CheckTimeOut();
};

Robot_Motors::Robot_Motors() {}

  void Robot_Motors::HighSpeed(){  SetSpeed(INIT_MOTOR_POWER);}

  void Robot_Motors::LowSpeed(){  SetSpeed(INIT_MOTOR_POWER_LOW);}



void Robot_Motors::Init() 
{
 // put your setup code here, to run once:
  pinMode(motor1pin1, OUTPUT);
  pinMode(motor1pin2, OUTPUT);
  pinMode(motor2pin1,  OUTPUT);
  pinMode(motor2pin2, OUTPUT);
  pinMode(Rele01_MotorNO, OUTPUT);
  pinMode(Rele02_MasterNC, OUTPUT);

  //(Optional)
  pinMode(EnApin, OUTPUT); 
  pinMode(EnBpin, OUTPUT);
  //(Optional)

  SetSpeed(INIT_MOTOR_POWER);


}



void Robot_Motors::SetSpeed(int Speed)
{
    if (Speed > 255) Speed = 255;
    if (Speed < 0) Speed = 0;

    //Controlling speed (0  = off and 255 = max speed):     
    //(Optional)
    analogWrite(EnApin, Speed); //ENA  pin
    analogWrite(EnBpin, Speed); //ENB pin
    //(Optional)
}

bool Robot_Motors::IsToRun(String ThisCommand)
{

    if (_lastCommand != ThisCommand or (_lastCommand == ThisCommand and _startrun == 0))
    {
      _startrun = millis();
      _lastCommand = ThisCommand;
      
    }
    else
    {
      _startrun = millis();
      return false; 
    }

    return true;
}

void Robot_Motors::RunFw(long RunTimeout = 0)
{
    _runtimeout = RunTimeout;

    if (!IsToRun(CMD_FW)) return
        
    // FW

    digitalWrite(motor1pin2, LOW);
    digitalWrite(motor1pin1,  HIGH);

    digitalWrite(motor1pin2, LOW);
    digitalWrite(motor2pin1, HIGH);
    
}

void Robot_Motors::RunBw(long RunTimeout = 0)
{

    _runtimeout = RunTimeout;
     
    if (!IsToRun(CMD_BW)) return

    // BW
    digitalWrite(motor1pin1,  LOW);
    digitalWrite(motor1pin2, HIGH);

    digitalWrite(motor2pin1, LOW);
    digitalWrite(motor2pin2, HIGH);

}

void Robot_Motors::Rotate(int dir = 1, long RunTimeout = 0)
{
    _runtimeout = RunTimeout;
    
  
    if (dir == 1)
    {
      if (!IsToRun(CMD_ROT)) return
      // FW
      digitalWrite(motor1pin1,  HIGH);
      digitalWrite(motor1pin2, LOW);
      
      // BW
      digitalWrite(motor2pin1, LOW);
      digitalWrite(motor2pin2, HIGH);
    }
    else
    {
      if (!IsToRun(CMD_ROTB)) return
      // BW
      digitalWrite(motor1pin1,  LOW);
      digitalWrite(motor1pin2, HIGH);

      // FW
      digitalWrite(motor2pin1, HIGH);
      digitalWrite(motor2pin2, LOW);

    }
  }

void Robot_Motors::Stop()
{

      // Stop
      digitalWrite(motor1pin1,  LOW);
      digitalWrite(motor1pin2, LOW);

      // BW
      digitalWrite(motor2pin1, LOW);
      digitalWrite(motor2pin2, LOW);

      _startrun = 0;
      _lastCommand = "";

}

void Robot_Motors::CheckTimeOut() 
{
    if (_runtimeout > 0)
      if (_startrun >0 && millis() > _startrun + _runtimeout )
      {
        Serial.println("To");
        
        _startrun = 0;
        _lastCommand = "";
        _runtimeout = 0;
        Stop();
      }

}

