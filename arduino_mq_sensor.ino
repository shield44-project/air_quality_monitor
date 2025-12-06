// Flat file: MQ Air Quality Sensor → Serial Output
const int mqPin = A0;  // Analog pin for MQ sensor

void setup() {
  Serial.begin(9600);
  delay(2000);
  Serial.println("✅ MQ Sensor Ready (Warm-up 30s recommended)");
}

void loop() {
  int rawValue = analogRead(mqPin);  // 0-1023 raw
  Serial.print("MQ:"); 
  Serial.println(rawValue); 
  delay(1000);
}
