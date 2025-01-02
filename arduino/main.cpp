
#include "DHT.h"
#define DHTPIN 2
#define DHTTYPE DHT11

int V0, V1, V2, plant;
DHT dht(DHTPIN, DHTTYPE);
int sleep = 0;
void setup() {
  Serial.begin(9600);
  dht.begin(); // initialize the sensor
}

int get_dht(){
    int result = 0;
    dht.read();
    result += ((dht.data[0] ^ dht.data[1]) % dht.data[2]) * dht.data[3] + dht.data[4];
    result = result % 8;
    return result;
}

int get_analog_sensor(int pin){
    return (analogRead(pin) + analogRead(pin)) % 8;
}

void loop() {
  V0 = get_analog_sensor(A0);
  delay(sleep);
  V1 = get_analog_sensor(A1);
  delay(sleep);
  V2 = get_analog_sensor(A2); 
  delay(sleep);
  plant = get_dht();
  delay(sleep);
  Serial.print("Heart: ");
  Serial.println(V0);
  Serial.print("Temperature: "); 
  Serial.println(V1);
  Serial.print("Sesmic: "); 
  Serial.println(V2);
  Serial.print("Plant: "); 
  Serial.println(plant);
  
}
