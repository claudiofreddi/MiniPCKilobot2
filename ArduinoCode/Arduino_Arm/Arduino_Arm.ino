
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>
#include <Servo.h>

// called this way, it uses the default address 0x40
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();
// you can also call it with a different address you want
//Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver(0x41);
// you can also call it with a different address and I2C interface
//Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver(0x40, Wire);

// Depending on your servo make, the pulse width min and max may vary, you
// want these to be as small/large as possible without hitting the hard stop
// for max range. You'll have to tweak them as necessary to match the servos you
// have!
#define SERVOMIN 90    // This is the 'minimum' pulse length count (out of 4096)
#define SERVOMAX 500   // This is the 'maximum' pulse length count (out of 4096)
#define USMIN 600      // This is the rounded 'minimum' microsecond length based on the minimum pulse of 150
#define USMAX 2400     // This is the rounded 'maximum' microsecond length based on the maximum pulse of 600
#define SERVO_FREQ 50  // Analog servos run at ~50 Hz updates

// our servo # counter
bool isFirstLoop = true;

void setup() {
  Serial.begin(9600);
  Serial.println("8 channel Servo test!");

  pwm.begin();

  /*
   * In theory the internal oscillator (clock) is 25MHz but it really isn't
   * that precise. You can 'calibrate' this by tweaking this number until
   * you get the PWM update frequency you're expecting!
   * The int.osc. for the PCA9685 chip is a range between about 23-27MHz and
   * is used for calculating things like writeMicroseconds()
   * Analog servos run at ~50 Hz updates, It is importaint to use an
   * oscilloscope in setting the int.osc frequency for the I2C PCA9685 chip.
   * 1) Attach the oscilloscope to one of the PWM signal pins and ground on
   *    the I2C PCA9685 chip you are setting the value for.
   * 2) Adjust setOscillatorFrequency() until the PWM update frequency is the
   *    expected value (50Hz for most ESCs)
   * Setting the value here is specific to each individual I2C PCA9685 chip and
   * affects the calculations for the PWM update frequency. 
   * Failure to correctly set the int.osc value will cause unexpected PWM results
   */
  pwm.setOscillatorFrequency(27000000);
  pwm.setPWMFreq(SERVO_FREQ);  // Analog servos run at ~50 Hz updates

  delay(10);
}

// You can use this function if you'd like to set the pulse length in seconds
// e.g. setServoPulse(0, 0.001) is a ~1 millisecond pulse width. It's not precise!
void setServoPulse(uint8_t n, double pulse) {
  double pulselength;

  pulselength = 1000000;      // 1,000,000 us per second
  pulselength /= SERVO_FREQ;  // Analog servos run at ~60 Hz updates
  Serial.print(pulselength);
  Serial.println(" us per period");
  pulselength /= 4096;  // 12 bits of resolution
  Serial.print(pulselength);
  Serial.println(" us per bit");
  pulse *= 1000000;  // convert input seconds to us
  pulse /= pulselength;
  Serial.println(pulse);
  pwm.setPWM(n, 0, pulse);
}




#define HAND_PIN 0
#define POLSO_ROT_PIN 1
#define POLSO_PIN 2
#define BRACCIO_PIN 3
#define SPALLA_PIN 4
#define BASE_PIN 5

char inChar = ' ';
int hand_deg = 0;  //90 Chiuso - 30 Aperto


//HAND_PIN: 90 Chiuso - 30 Aperto
int position_deg_starting[6] = { 100, 180, 90, 90, 45, 90 };
int position_deg[6] = { 100, 180, 90, 90, 45, 90 };
int position_min[6] = { 30, 0, 0, 0, 0, 0 };
int position_max[6] = { 125, 180, 180, 180, 180, 180 };
int Selected = 0;
int pulselen = 0;
#define DELAY_IN_MOV 10

void PrintPos(){
  for (int i = 0; i < 6; i++) {
        Serial.print(position_deg[i]);
        if (i != 5)
          Serial.print(",");
      }
}

uint16_t Get_pulselength(int Selected, int degrees) {
  if (degrees > position_max[Selected]) degrees = position_max[Selected];
  if (degrees < position_min[Selected]) degrees = position_min[Selected];
  position_deg[Selected] = degrees;
  //Serial.println("Servo " + String(Selected) + " Set to: " + String(degrees));
  return map(degrees, 0, 180, SERVOMIN, SERVOMAX);
}


void Reset() {

  for (int i = 0; i < 6; i++) {
    int pos = position_deg_starting[i];
    pulselen = Get_pulselength(i, pos);
    pwm.setPWM(i, 0, pulselen);
  }
}

void GoTo(int Selected, int NewDegree, int MaxStep = 1000, bool Print =true) {
  int curr = position_deg[Selected];
  int dir;
  if (NewDegree == curr) return;
  int count = 0;
  if (NewDegree > curr) {
    dir = 1;
    count = 0;
    for (int i = curr; i <= NewDegree and count <= MaxStep; i = i + dir) {
      //Serial.println(i);

      int pulselen = Get_pulselength(Selected, i);
      pwm.setPWM(Selected, 0, pulselen);
      delay(DELAY_IN_MOV);
      count++;
    }
  } else {
    dir = -1;
    count = 0;
    for (int i = curr; i >= NewDegree and count <= MaxStep; i = i + dir) {
      //Serial.println(i);

      int pulselen = Get_pulselength(Selected, i);
      pwm.setPWM(Selected, 0, pulselen);
      delay(DELAY_IN_MOV);
      count++;
    }
  }

  if (Print) PrintPos();
}

void MoveToAbs(int Grip, int WristPitch, int WristRoll, int Elbow, int Shoulder, int Waist) {
  int maxsteps = Grip;
  maxsteps = (WristPitch > maxsteps ? WristPitch : maxsteps);
  maxsteps = (WristRoll > maxsteps ? WristRoll : maxsteps);
  maxsteps = (Elbow > maxsteps ? Elbow : maxsteps);
  maxsteps = (Shoulder > maxsteps ? Shoulder : maxsteps);
  maxsteps = (Waist > maxsteps ? Waist : maxsteps);

  for (int i = 0; i <= maxsteps; i++) {
    GoTo(0, Grip, 1,false);
    GoTo(1, WristPitch, 1,false);
    GoTo(2, WristRoll, 1,false);
    GoTo(3, Elbow, 1,false);
    GoTo(4, Shoulder, 1,false);
    GoTo(5, Waist, 1,false);
  }

  PrintPos();

}

void MoveToAbs(int* values) {

  MoveToAbs(values[0], values[1], values[2], values[3], values[4], values[5]);
}

void loop() {

  if (isFirstLoop) {
    Serial.println("Selected " + String(Selected));

    Reset();

    isFirstLoop = false;
    Serial.print("Setup done");
  }

  String inChar = "";

  if (Serial.available() > 0) {

    // read incoming serial data:

    delay(5);
    char c = Serial.read();

    inChar += c;
    if ((inChar == "o")
        or (inChar == "p")
        or (inChar == "r")
        or (inChar == "l")
        or (inChar == "t")
        or (inChar == "0")
        or (inChar == "1")
        or (inChar == "2")
        or (inChar == "3")
        or (inChar == "4")
        or (inChar == "5"))
      Serial.println(inChar);
  }

  if (inChar == "0") Selected = 0;
  if (inChar == "1") Selected = 1;
  if (inChar == "2") Selected = 2;
  if (inChar == "3") Selected = 3;
  if (inChar == "4") Selected = 4;
  if (inChar == "5") Selected = 5;

  if (inChar == "o") GoTo(Selected, position_deg[Selected] - 5);
  if (inChar == "p") GoTo(Selected, position_deg[Selected] + 5);

  if (inChar == "r") {

    MoveToAbs(position_deg_starting);
  }

  if (inChar == "t") {
    int data1[6] = {45,0,100,35,20,10};
    MoveToAbs(data1);
    int data2[6] = {45,0,100,70,55,10};
    MoveToAbs(data2);


    
  }

  if (inChar == "l")
    PrintPos();
}
