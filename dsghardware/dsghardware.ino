// Arduino Nano + 2 HC-SR04 Ultrasonic Sensors

#define TRIG1 2
#define ECHO1 3

#define TRIG2 4
#define ECHO2 5

long getDistance(int trigPin, int echoPin)
{
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);

  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH, 30000);

  if (duration == 0)
    return -1;

  return duration * 0.0343 / 2;
}

void setup()
{
  Serial.begin(9600);

  pinMode(TRIG1, OUTPUT);
  pinMode(ECHO1, INPUT);

  pinMode(TRIG2, OUTPUT);
  pinMode(ECHO2, INPUT);
}

void loop()
{
  // Sensor 1
  long distance1 = getDistance(TRIG1, ECHO1);

  // Wait to prevent ultrasonic interference
  delay(50);

  // Sensor 2
  long distance2 = getDistance(TRIG2, ECHO2);

  Serial.print("Sensor 1: ");

  if (distance1 == -1)
    Serial.print("No Echo");
  else
  {
    Serial.print(distance1);
    Serial.print(" cm");
  }

  Serial.print("   |   Sensor 2: ");

  if (distance2 == -1)
    Serial.println("No Echo");
  else
  {
    Serial.print(distance2);
    Serial.println(" cm");
  }

  delay(200);
}