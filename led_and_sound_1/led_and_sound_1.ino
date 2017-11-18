const int soundPin = 2;     // the number of the Sensor pin
const int ledPin = 3;      // the number of the led pin

void setup() {
    
  pinMode(ledPin, OUTPUT);
  pinMode(soundPin, INPUT);
  
  Serial.begin(9600); 
  Serial.println("Start!!!");
}

void EstablecerColor(int R, int G, int B) {

  //Se utiliza la expresión 255-X para “naturalizar los valores”. Dado
  //que el mayor brillo está asociado a la mayor diferencia de voltaje
  //entre la alimentación y las salidas PWM (lo que implica una salida
  //de 0V por el pin PWM, esto es, analogWrite(X, 0);).
  //////analogWrite(Rojo, 255 - R);
  //////analogWrite(Verde, 255 - G);
  //////analogWrite(Azul, 255 - B);

}

void Sound(){

  String res = "";
  int aValue = analogRead(soundPin);
  int dValue = digitalRead(soundPin);
  
  res.concat(aValue);
  res.concat(" | ");
  res.concat(dValue);
  
  Serial.println(res);

  if(dValue == 1){
    ledControl(false);
  }
  else{
    ledControl(true);
  }
}

void ledControl(bool isOn){

  if(!isOn){
    //Off
    digitalWrite(ledPin, LOW);
  }
  else{
    //On
    digitalWrite(ledPin, HIGH);
  }
  
}

void loop() {

  Sound();
  delay(10);

}

