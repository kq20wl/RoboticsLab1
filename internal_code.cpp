#include <Encoder.h>
#include <Adafruit_PWMServoDriver.h>
#define PIN_MANUAL 11
#define PIN_BUTTON 5

Encoder knobShoulder(7,6);
Encoder knobElbow(9,10);
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();
#define SERVOMIN  75 // This is the 'minimum' pulse length count (out of 4096)
#define SERVOELBOWMAX  470 // This is the 'maximum' pulse length count (out of 4096)
#define SERVOSHOULDERMAX  444 // Capped below 470 to avoid hitting the enclosure
#define SERVO_FREQ 50 // Analog servos run at ~50 Hz updates

struct {
  int shoulder=250;
  int elbow=250;
  int pen=1;
} pulses;

void update() {
  pwm.setPWM(0,0,pulses.shoulder);
  pwm.setPWM(1,0,pulses.elbow);
  pwm.setPWM(2,0,pulses.pen==1?130:280);
}

bool receivePositions() {
  char buffer[80];
  int s,e,p;
  int read=Serial.readBytesUntil('\n',buffer,79);
  if (!read) return false;
  if (buffer[0]!='{' || buffer[read-1]!='}') return false; //Needs to be enclosed in {}
  buffer[read]='\0'; //Ensure proper string termination
  char *tok=strtok(buffer,"{,}");
  s=atoi(tok);
  tok=strtok(NULL,"{,}");
  e=atoi(tok);
  tok=strtok(NULL,"{,}");
  p=atoi(tok);
  if ( !s || !e || !p ) return;
  pulses.shoulder=max(min(s,SERVOSHOULDERMAX),SERVOMIN);
  pulses.elbow=max(min(e,SERVOELBOWMAX),SERVOMIN);
  pulses.pen=p;
  update();
  return true;
}

void setup() {
  pinMode(PIN_MANUAL,INPUT_PULLUP);
  pinMode(PIN_BUTTON,INPUT);
  Serial.begin(115200);
  pwm.begin();
  pwm.setOscillatorFrequency(27000000);
  pwm.setPWMFreq(SERVO_FREQ);  // Analog servos run at ~50 Hz updates
  while (!Serial);
  Serial.println("Hi.");
}

void loop() {
  if (digitalRead(PIN_MANUAL)) drawing();
  else manual();
}

void manual() {
  static bool lastButtonState=true;
  int shoulder = knobShoulder.readAndReset();
  int elbow = knobElbow.readAndReset();
  bool changed=false;
  bool button=digitalRead(PIN_BUTTON);
  if (!button && lastButtonState!=button) { //update pen state
    pulses.pen=pulses.pen?0:1;
    changed=true;
  }
  
  if (shoulder) { //Update shoulder state
    pulses.shoulder=min(SERVOSHOULDERMAX,max(SERVOMIN,pulses.shoulder+shoulder));
    changed=true;
  }
  if (elbow) { //Update elbow state
    pulses.elbow=min(SERVOELBOWMAX,max(SERVOMIN,pulses.elbow+elbow));
    changed=true;
  }
  if (changed) { //Send new state to controller
    update();
    Serial.print('[');
    Serial.print(pulses.shoulder);
    Serial.print('|');
    Serial.print(pulses.elbow);
    Serial.print('|');
    Serial.print(pulses.pen);
    Serial.println(']');
  }
  lastButtonState=button;
}
void drawing() {
  if (Serial.available()) {
    if (receivePositions()) {
      Serial.println(">");
    }
    else {
      Serial.println("!");
    }
  }
}