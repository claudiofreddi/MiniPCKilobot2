#define MAX_SENSORS 2
#define SENSORS_COMPASS 0
#define SENSORS_TEST 1

long SensorTimeout[MAX_SENSORS] = {500,0};
long SensorStart[MAX_SENSORS] = {0,0};
long count = 0;

void setup(){
  
  Serial.begin(115200);

  Compass_Inizialize();

  SensorStart[SENSORS_COMPASS] = millis();
  SensorStart[SENSORS_TEST] = millis();

  Serial.println("ArduinoReady");

}

void loop(){

  if (SensorTimeout[SENSORS_COMPASS] > 0 && SensorStart[SENSORS_COMPASS] + SensorTimeout[SENSORS_COMPASS] < millis())
  {
    Serial.println("SENSORS_COMPASS:" + String(Compass_Read()));
    SensorStart[SENSORS_COMPASS] = millis();
    
  } 

  if ( SensorTimeout[SENSORS_TEST] >0 && SensorStart[SENSORS_TEST] + SensorTimeout[SENSORS_TEST] < millis())
  {
    Serial.println("TEST1:" + String(count));
    count = count + 1;
    SensorStart[SENSORS_TEST] = millis();
  } 

  
}

