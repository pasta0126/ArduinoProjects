#include <LiquidCrystal.h>
#include <DHT.h>
 
#define DHTPIN 3
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

const int rs = 7, en = 8, d4 = 12, d5 = 11, d6 = 10, d7 = 9;
const int contrast = 5;

LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

void setup() {
  lcd.begin(16, 2);
  dht.begin();
  pinMode(contrast, OUTPUT); 
}

void loop() {
  analogWrite(contrast, 100);
  lcd.clear();
  DisplayMessage();
}

void DisplayMessage(){
  String msg1 = "T:";
  String msg2 = "H:";

  float t = dht.readTemperature();
  float h = dht.readHumidity();
  float hic = dht.computeHeatIndex(t, h, false);

  if (isnan(h) || isnan(t) || isnan(hic)) {
    msg1 = "Error obteniendo los datos del sensor DHT11";
    return;
  }
  lcd.setCursor(0,0);
  msg1 = msg1 + t + "(" + hic + ")" + (char)223 + "C"; 
  lcd.print(msg1);

  lcd.setCursor(0,1);
  msg2 = msg2 + h + "%";
  lcd.print(msg2);
  
  lcd.display();
  delay(200);
}
