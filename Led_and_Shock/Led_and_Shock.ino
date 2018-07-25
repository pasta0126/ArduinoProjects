#include <Adafruit_NeoPixel.h>

#define PIN_SHOCK 3
#define PIN_BUTTON 5
#define PIN_LED 6
#define ARR_LEDS 8

#define MODE_DIABLES 1
#define MODE_ARCIRIS 2

Adafruit_NeoPixel strip = Adafruit_NeoPixel(ARR_LEDS, PIN_LED, NEO_RGB + NEO_KHZ800);

int delayVal = 10;
int mode = MODE_DIABLES;
int impactVal;
int buttonVal;

void setup() {

  pinMode(PIN_LED, OUTPUT);
  pinMode(PIN_BUTTON, INPUT);
  pinMode(PIN_SHOCK, INPUT);

  Serial.begin(9600); 
  Serial.println("Start!!!");
}

void loop() {
  String res;
  long R = 255;
  long G = 0;
  long B = 0;

  impactVal = digitalRead(PIN_SHOCK);
  buttonVal = digitalRead(PIN_BUTTON);
  
  if(buttonVal == 1){
    switch(mode){
      case MODE_DIABLES:
        mode = MODE_ARCIRIS;
        res = "MODE_ARCIRIS";
        break;
        
      case MODE_ARCIRIS:
        mode = MODE_DIABLES;
        res = "MODE_DIABLES";
        break;
        
      default:
        mode = MODE_DIABLES;
        res = "MODE_DIABLES";
        break;
    }
    Serial.println(res);
    delay(1000);
  }

  while((impactVal == 1)){
    if(mode == MODE_ARCIRIS){
      R = random(0, 255);
      G = random(0, 255);
      B = random(0, 255);
    }
    LedsOn(R, G, B);
    delay(delayVal);
    impactVal = digitalRead(PIN_SHOCK);
  }

  LedsOn(0, 0, 0);
}

void LedsOn(long R, long G, long B){
  
  for(int i=0; i<ARR_LEDS; i++){
    strip.setPixelColor(i, strip.Color(G, R, B)); // GRB 
  }
  strip.show();
}

