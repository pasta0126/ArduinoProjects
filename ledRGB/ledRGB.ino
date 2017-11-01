int Rojo = 9;
int Verde = 10;
int Azul = 11;

void setup() {

  pinMode(Rojo, OUTPUT);
  pinMode(Verde, OUTPUT);
  pinMode(Azul, OUTPUT);

}

void EstablecerColor(int R, int G, int B) {

  //Se utiliza la expresión 255-X para “naturalizar los valores”. Dado
  //que el mayor brillo está asociado a la mayor diferencia de voltaje
  //entre la alimentación y las salidas PWM (lo que implica una salida
  //de 0V por el pin PWM, esto es, analogWrite(X, 0);).
  analogWrite(Rojo, 255 - R);
  analogWrite(Verde, 255 - G);
  analogWrite(Azul, 255 - B);

}

void loop() {

  EstablecerColor(random(0, 255), random(0, 255), random(0, 255));

  delay(1000);

}

