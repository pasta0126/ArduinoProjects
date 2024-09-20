#include "esp_camera.h"
#include <WiFi.h>
#include <HTTPClient.h>

#define CAMERA_MODEL_AI_THINKER
#include "esp_camera.h"

// Configuración de WiFi y servidor (como en el código anterior)
const char* ssid = "WifiGSP";
const char* password = "SanRoqu3orenjiorenji";
const char* serverName = "http://192.168.1.10/upload.php";

// Variables para la detección de movimiento
bool motion_detected = false;
int motion_counter = 0;

void setup() {
  Serial.begin(115200);
  
  // Configuración de la cámara (como en el código anterior)
  camera_config_t config;
  // ... (resto de la configuración)

  // Inicializar la cámara
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Error al inicializar la cámara: 0x%x", err);
    return;
  }

  // Conectar a WiFi (como en el código anterior)
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Conectando a WiFi...");
  }
  Serial.println("Conectado a WiFi");
}

void loop() {
  if (detectMotion()) {
    motion_detected = true;
    motion_counter = 0;
  }

  if (motion_detected && motion_counter < 10) {
    captureAndSendPhoto();
    motion_counter++;
    delay(1000); // Esperar 1 segundo entre capturas
  } else if (motion_counter >= 10) {
    motion_detected = false;
    motion_counter = 0;
  }

  delay(100); // Pequeña pausa para no saturar el procesador
}

bool detectMotion() {
  camera_fb_t * fb_current = esp_camera_fb_get();
  if (!fb_current) {
    Serial.println("Error al capturar frame actual");
    return false;
  }

  static uint8_t * prev_frame = NULL;
  static size_t prev_len = 0;

  if (prev_frame == NULL) {
    prev_frame = (uint8_t *)malloc(fb_current->len);
    prev_len = fb_current->len;
    memcpy(prev_frame, fb_current->buf, fb_current->len);
    esp_camera_fb_return(fb_current);
    return false;
  }

  int changed_pixels = 0;
  for (size_t i = 0; i < fb_current->len; i++) {
    if (abs(fb_current->buf[i] - prev_frame[i]) > 50) { // Umbral de diferencia
      changed_pixels++;
    }
  }

  memcpy(prev_frame, fb_current->buf, fb_current->len);
  esp_camera_fb_return(fb_current);

  // Si más del 5% de los píxeles han cambiado, consideramos que hay movimiento
  return (changed_pixels > (fb_current->len / 20));
}

void captureAndSendPhoto() {
  camera_fb_t * fb = esp_camera_fb_get();
  if(!fb) {
    Serial.println("Error al capturar imagen");
    return;
  }

  HTTPClient http;
  http.begin(serverName);
  http.addHeader("Content-Type", "image/jpeg");
  
  int httpResponseCode = http.POST(fb->buf, fb->len);
  
  if(httpResponseCode > 0){
    String response = http.getString();
    Serial.println(httpResponseCode);
    Serial.println(response);
  } else {
    Serial.print("Error en la solicitud HTTP: ");
    Serial.println(httpResponseCode);
  }
  
  http.end();
  esp_camera_fb_return(fb);
}
