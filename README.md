# Muon Detector

Este proyecto implementa un detector de muones atmosféricos basado en dos tubos Geiger–Müller en coincidencia, controlado por un NodeMCU ESP8266. El sistema permite registrar eventos, calcular tasas de conteo y enviar datos a la nube para análisis.

## Características principales

- Coincidencia entre dos tubos GM para reducir ruido y detectar muones.  
- Registro de eventos con marca de tiempo y cálculo de CPM.  
- Pantalla OLED con actualización periódica.  
- Envío de datos a Google Sheets mediante HTTPS.  
- Modo offline con reenvío automático.  
- Código modular y estable.

## Hardware requerido

- NodeMCU ESP8266  
- Dos tubos Geiger–Müller y módulos de alta tensión  
- Pantalla OLED I2C  
- Fuente de alimentación y soporte mecánico

## Funcionalidades del firmware

- Captura de pulsos mediante interrupciones breves.  
- Evaluación de coincidencia en el loop principal.  
- Configuración WiFi mediante WiFiManager.  
- Sincronización horaria NTP.  
- Envío seguro de datos y almacenamiento local opcional.

## Aplicaciones

- Medición del flujo de muones.  
- Análisis estadístico (Poisson, fluctuaciones de conteo).  
- Experimentos de atenuación.  
- Uso en cursos de física moderna y electrónica.

## Cómo empezar

1. Clonar el repositorio.  
2. Configurar WiFi con WiFiManager.  
3. Ajustar pines según el hardware.  
4. Compilar y cargar el firmware.  
5. Visualizar datos en Google Sheets.

## Contribuciones

Se aceptan mejoras al código, documentación y análisis.

## Licencia

MIT.

---

Si quieres, puedo generar una versión aún más corta, una orientada a estudiantes o una más técnica para publicación.
