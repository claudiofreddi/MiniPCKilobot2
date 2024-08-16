
char MyCommand[100]; //Globale, perché deve mantenere i dati a ogni ciclo
String CommandString = "";      // a String to hold incoming data
int i=0;


bool pin13Status = true;


void setup(){
  
  Serial.begin(115200);

  ObjectStart[OBJ00] = millis();
  ObjectStart[OBJ01] = millis();
  if (_isDebug) pinMode(13, OUTPUT);

  Serial.println("ArduinoReady");

}


void loop() {
  // put your main code here, to run repeatedly:

  //Use timeout to not stop execution
  if (ObjectTimeout[OBJ00] > 0 && ObjectStart[OBJ00] + ObjectTimeout[OBJ00] < millis())
  {
    // Send data to Python: Keep Format  "NAME:Value"
    Serial.println("OBJ00:" + String(ReadObject00()));
    ObjectStart[OBJ00] = millis();
    
  } 
  //Use timeout to not stop execution
  if (ObjectTimeout[OBJ01] > 0 && ObjectStart[OBJ01] + ObjectTimeout[OBJ01] < millis())
  {
    // Send data to Python: Keep Format  "NAME:Value"
    Serial.println("OBJ01:" + String(ReadObject01()));
    ObjectStart[OBJ01] = millis();
    
  } 

  char tmp;
  // Leggo COmando
  if (Serial.available() > 0){ 
      
      tmp = Serial.read();
      if (tmp == '\n'){ 
        MyCommand[i] = '\0';  // End Termination as Python Ask
        i=0; 
        
        CommandString = String(MyCommand);
        CommandString.trim();
        
        //Debug
        if (_isDebug) Serial.println("[" + CommandString + "]");
        
        // Manage Received Command - Blocking Action
        // Keep Command Execution as fast as possbile 
        ExecuteCommand(CommandString);
        if (_isDebug) 
          if (pin13Status)
          {
            digitalWrite(13, HIGH);
            pin13Status = !pin13Status;
          }
          else
          {
            digitalWrite(13, LOW);
            pin13Status = !pin13Status;
          }

      }else{
        MyCommand[i] = tmp;
        i++; 
      }
   }

}
