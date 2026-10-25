/*
 * SpatialDrive — Arduino Uno Micro-Controller Firmware
 * IoT-Enabled AR Head-Up Display Telematics & Ultrasonic Hazard Subsystem
 *
 * Hardware Wiring:
 * 1. HC-SR04 Ultrasonic Distance Sensor:
 *    - VCC  -> Arduino 5V
 *    - GND  -> Arduino GND
 *    - TRIG -> Digital Pin 9
 *    - ECHO -> Digital Pin 10
 *
 * 2. Steering Potentiometer / Encoder:
 *    - Leg 1 -> Arduino 5V
 *    - Leg 3 -> Arduino GND
 *    - Wiper (Center) -> Analog Pin A0 (maps 0-1023 to -45.0° ... +45.0°)
 *
 * 3. Hazard LED / Active Buzzer (Optional):
 *    - Positive -> Digital Pin 8 (via 220Ω resistor)
 *    - Negative -> Arduino GND
 *
 * Communication:
 *    - Outputs continuous JSON over Serial at 115200 Baud:
 *      {"angle": 12.5, "distance": 42}
 *    - Directly compatible with SpatialDrive HUD Web Serial API.
 */

const int PIN_TRIG   = 9;
const int PIN_ECHO   = 10;
const int PIN_POT    = A0;
const int PIN_HAZARD = 8;

const float HAZARD_THRESHOLD_CM = 20.0;
unsigned long lastTelemetryTime = 0;
const unsigned long TELEMETRY_INTERVAL_MS = 40; // 25 Hz update rate

void setup() {
  Serial.begin(115200);
  pinMode(PIN_TRIG, OUTPUT);
  pinMode(PIN_ECHO, INPUT);
  pinMode(PIN_HAZARD, OUTPUT);
  digitalWrite(PIN_TRIG, LOW);
  digitalWrite(PIN_HAZARD, LOW);
}

float measureDistanceCm() {
  // Trigger 10µs ultrasonic pulse
  digitalWrite(PIN_TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(PIN_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(PIN_TRIG, LOW);

  // Measure echo return pulse width (timeout at 25ms ≈ 400cm max range)
  unsigned long durationUs = pulseIn(PIN_ECHO, HIGH, 25000);
  if (durationUs == 0) {
    return 999.0; // Out of range / clear roadway
  }
  // Speed of sound = 343 m/s = 0.0343 cm/µs. Round trip / 2:
  return (float)durationUs * 0.0343 / 2.0;
}

float readSteeringAngle() {
  int raw = analogRead(PIN_POT); // 0 to 1023
  // Map 0 -> -45.0°, 512 -> 0.0°, 1023 -> +45.0°
  float angle = ((float)raw / 1023.0 - 0.5) * 90.0;
  // Apply a small 0.5° deadband around center
  if (abs(angle) < 0.5) angle = 0.0;
  return angle;
}

void loop() {
  unsigned long currentMillis = millis();

  if (currentMillis - lastTelemetryTime >= TELEMETRY_INTERVAL_MS) {
    lastTelemetryTime = currentMillis;

    float distCm = measureDistanceCm();
    float angle  = readSteeringAngle();

    // Hardware Hazard Alert
    if (distCm < HAZARD_THRESHOLD_CM) {
      digitalWrite(PIN_HAZARD, HIGH);
    } else {
      digitalWrite(PIN_HAZARD, LOW);
    }

    // Stream telemetry JSON packet over USB Serial
    Serial.print("{\"angle\":");
    Serial.print(angle, 1);
    Serial.print(",\"distance\":");
    Serial.print((int)distCm);
    Serial.println("}");
  }
}
