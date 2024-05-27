
String inputString = "";      // a String to hold incoming data
bool stringComplete = false;  // whether the string is complete
String CommandString = "";      // a String to hold incoming data

bool IsFirstLoop = true;
long timeout = 1000;
long startms = 0;
bool _enable_led_monitor = true;

const unsigned int MAX_MESSAGE_LENGTH = 12;

void setup() {

  // initialize serial:
  Serial.begin(115200);
  Serial.println("Serial at 115200 baud");
  inputString.reserve(200);
  Serial.println("Setup Done");

}

char MyCommand[100]; //Globale, perché deve mantenere i dati a ogni ciclo
int i=0;

void loop() {

  if (IsFirstLoop)
  {
    Serial.println("Initializing..");

    // Led
    Serial.println("Checking Led..");
    MyRobot_Led.Init();
    MyRobot_Led.testAll();
   
    // Power
    Serial.println("Init rele..");
    MyRobot_Rele.Init();
    MyRobot_Rele.Switch_Arduino_And_Motors(true);
    
    Serial.println("Power Status..");
    MyRobot_Rele.PowerStatus();

    Serial.println("Init Motors..");
    MyRobot_Motors.Init();


    // End First Cycle
    IsFirstLoop = false;

    Serial.println("ArduinoReady");

   }

   char tmp;

   if (Serial.available() > 0){ 
      
      tmp = Serial.read();
      if (tmp == '\n'){ 
        MyCommand[i] = '\0'; 
        i=0; 
        
        CommandString = String(MyCommand);
        CommandString.trim();
        Serial.println(CommandString);
        ExecuteCommand(CommandString);

      }else{
        MyCommand[i] = tmp;
        i++; 
      }
   }

  // if (false)
  // if (Serial.available()) {
    
  //   CommandString = Serial.readString();
  //   CommandString.trim();
  //   Serial.println(CommandString);
  //   ExecuteCommand(CommandString);
  // }

  // if (false)
  //   // print the string when a newline arrives:
  //   if (stringComplete) {
  //     CommandString = inputString; 
  //     //Serial.println(inputString);
  //     // clear the string:
  //     inputString = "";
  //     stringComplete = false;

  //     if (!_optimize)
  //       if (_enable_led_monitor)
  //       {
  //       MyRobot_Led.turn_led(1, (CommandString == "switch_on"));
  //       MyRobot_Led.turn_led(2,(CommandString == CMD_FW) );
  //       MyRobot_Led.turn_led(3, (CommandString == CMD_STOP));  
  //       }
      
  //     ExecuteCommand(CommandString);
      
  //     if (!_optimize)
  //       if (_enable_led_monitor)
  //         MyRobot_Led.turn_led(1,false);
 

  //   }
  
  MyRobot_Motors.CheckTimeOut();

}

/*
  SerialEvent occurs whenever a new data comes in the hardware serial RX. This
  routine is run between each time loop() runs, so using delay inside loop can
  delay response. Multiple bytes of data may be available.
*/

void serialEventzzz() {
  
  Serial.println("yyyyyyyyyyyyy");

  //MyRobot_Led.turn_led(1,true);
  //startms = millis();
  if (!_optimize) Serial.println("Serial Called");

  while (Serial.available()) {
    inputString = Serial.readString();
    inputString.trim();
    if (!_optimize)
      if (_enable_led_monitor)
        MyRobot_Led.turn_led(0,true);
      
    stringComplete = true;
 }
  
}
