/* Muon detector by LabTec v4.6 WiFi
 * optimización de envío de datos para reducir tiempo muerto
 * envio por logica incremental
 * By Ynerpoe
 * 26/04/2026
 * NOTA: se redujo el tiempo muerto de 2s a 0.021 s
 */

#include <Wire.h>
#include "SSD1306Wire.h"
#include <ESP8266WiFi.h>
#include <WiFiManager.h>
#include <time.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClientSecure.h>

// ----------- PINES -------------
#define SDApin 14
#define SCLpin 12
#define Sens_pin1 5
#define Sens_pin2 4

// ----------- DISPLAY -----------
SSD1306Wire display(0x3c, SDApin, SCLpin);

// ---------- VARIABLES GLOBALES ----------
volatile unsigned long coincidencias = 0;
volatile unsigned long t1 = 0; 
volatile unsigned long t2 = 0; 
const unsigned long ventana = 50; 

unsigned long tiempo_inicio; 
unsigned long ultimoEnvio = 0; 

String webhookURL = "https://script.google.com/macros/s/AKfycbzsTXI2LUokExQQbkT1HIaTAtI3r22oms4ZAvh4Yz2BNCudlCRerLYZsnrfazTckC7eyw/exec";

// Control de envío no bloqueante
int indiceEnvio = 0;
bool enviandoBuffer = false;

// ---------- BUFFER DE EVENTOS ---------
struct Evento {
  unsigned long cuentas;
  float tiempo_s;
  float cpm;
};

const int BUFFER_MAX = 500; 
Evento bufferEventos[BUFFER_MAX];
int bufferCount = 0;

void bufferGuardarEvento(unsigned long cuentas, float tiempo_s, float cpm) {
  if (bufferCount < BUFFER_MAX) {
    bufferEventos[bufferCount++] = {cuentas, tiempo_s, cpm};
  }
}

// ---------------- INTERRUPCIONES ----------------
void ICACHE_RAM_ATTR pulso1() {
  t1 = micros(); 
  if (t1 - t2 <= ventana) {
    coincidencias++;
    t1 = 0; t2 = 0;
  }
}

void ICACHE_RAM_ATTR pulso2() {
  t2 = micros(); 
  if (t2 - t1 <= ventana) {
    coincidencias++;
    t1 = 0; t2 = 0;
  }
}

// ---------------- FUNCIONES AUXILIARES ----------------
void actualizarDisplay(unsigned long c, float cpm) {
  display.clear();
  display.setTextAlignment(TEXT_ALIGN_CENTER);
  display.setFont(ArialMT_Plain_10);
  display.drawString(64, 0, "LABTEC MUON WiFi"); 
  display.drawHorizontalLine(0, 14, 128); 
  display.setFont(ArialMT_Plain_16);
  display.drawString(64, 25, "LOGS: " + String(c)); 
  display.setFont(ArialMT_Plain_10);
  display.drawString(64, 50, "TASA: " + String(cpm, 2) + " cpm"); 
  display.display(); 
}

bool enviarGoogleSheets(unsigned long c, float segundos, float cpm) {
  if (WiFi.status() != WL_CONNECTED) return false; 
  WiFiClientSecure client;
  client.setInsecure(); 
  HTTPClient http;
  if (!http.begin(client, webhookURL)) return false; 
  http.addHeader("Content-Type", "application/json"); 
  String json = "{\"cuentas\":" + String(c) + ",\"tiempo_s\":" + String(segundos, 3) + ",\"cpm\":" + String(cpm, 2) + "}"; 
  int code = http.POST(json); 
  http.end(); 
  return (code > 0);
}

void iniciarNTP() {
  configTime(-3 * 3600, 0, "pool.ntp.org", "time.nist.gov");
  time_t now;
  do { delay(500); time(&now); } while (now < 100000);
}

// ---------------- SETUP ----------------
void setup() {
  Serial.begin(115200);
  display.init();
  display.flipScreenVertically();
  actualizarDisplay(0, 0); 
  
  pinMode(Sens_pin1, INPUT);
  pinMode(Sens_pin2, INPUT);
  attachInterrupt(digitalPinToInterrupt(Sens_pin1), pulso1, FALLING); 
  attachInterrupt(digitalPinToInterrupt(Sens_pin2), pulso2, FALLING);

  tiempo_inicio = millis(); 
  
  WiFiManager wm;
  if (!wm.autoConnect("MuonDetector-Setup")) ESP.restart();
  
  iniciarNTP(); 
}

// ---------------- LOOP OPTIMIZADO ----------------
void loop() {
  unsigned long c;
  noInterrupts();
  c = coincidencias; 
  interrupts();

  float segundos = (millis() - tiempo_inicio) / 1000.0; 
  float minutos = segundos / 60.0; 
  float cpm = (minutos > 0.01) ? (c / minutos) : 0.0; 

  static unsigned long ultimaCuenta = 0;
  if (c > ultimaCuenta) { 
    bufferGuardarEvento(c, segundos, cpm);
    ultimaCuenta = c;
  }

  // Lógica de envío progresivo
  if (millis() - ultimoEnvio >= 60000 && !enviandoBuffer) { 
    
    display.clear();
    display.setTextAlignment(TEXT_ALIGN_CENTER);
    display.setFont(ArialMT_Plain_10);
    display.drawString(64, 0, "LABTEC MUON WiFi");
    display.drawHorizontalLine(0, 14, 128);
    display.drawString(64, 30, "...enviando datos...");
    display.display();

    if (bufferCount > 0) {
      enviandoBuffer = true;
      indiceEnvio = 0;
    }
    ultimoEnvio = millis();
  }

  if (enviandoBuffer) {
    if (enviarGoogleSheets(bufferEventos[indiceEnvio].cuentas, 
                           bufferEventos[indiceEnvio].tiempo_s, 
                           bufferEventos[indiceEnvio].cpm)) { 
      indiceEnvio++;
    }
    if (indiceEnvio >= bufferCount) {
      bufferCount = 0;
      enviandoBuffer = false;
    }
  } else {
    actualizarDisplay(c, cpm);
  }
}
