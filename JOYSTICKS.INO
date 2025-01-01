const int joystick1_xPin = A0;
const int joystick1_yPin = A1;
const int joystick2_xPin = A2;
const int joystick2_yPin = A3;

void setup() {
  Serial.begin(9600);
  pinMode(joystick1_xPin, INPUT);
  pinMode(joystick1_yPin, INPUT);
  pinMode(joystick2_xPin, INPUT);
  pinMode(joystick2_yPin, INPUT);
}

void loop() {
  int joystick1_x = analogRead(joystick1_xPin);
  int joystick1_y = analogRead(joystick1_yPin);
  int joystick2_x = analogRead(joystick2_xPin);
  int joystick2_y = analogRead(joystick2_yPin);

  Serial.print(joystick1_x);
  Serial.print(",");
  Serial.print(joystick1_y);
  Serial.print(",");
  Serial.print(joystick2_x);
  Serial.print(",");
  Serial.println(joystick2_y);

  delay(100);
}
