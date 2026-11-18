# Muon Detector

Este proyecto implementa un detector de muones atmosféricos basado en dos tubos Geiger–Müller en coincidencia, controlado por un NodeMCU ESP8266. El sistema permite registrar eventos, calcular tasas de conteo y enviar datos a la nube para análisis.

## How to cite / Cómo citar
If you use this project in your research, please acknowledge Yonnhatan García-Cartagena & LabTec-UMCE in your acknowledgements section or cite it as: 
Yonnhatan García-Cartagena & LabTec-UMCE (2026). Muon-Detector. https://github.com/ynerpoe/Muon-Detector

Si utiliza este proyecto en su investigación, por favor mencione a Yonnhatan García-Cartagena y a LabTec-UMCE en la sección de agradecimientos o cítelo de la siguiente manera: 
Yonnhatan García-Cartagena & LabTec-UMCE (2026). Muon-Detector. https://github.com/ynerpoe/Muon-Detector

## Características principales

- Coincidencia entre dos tubos GM para reducir ruido y detectar muones.  
- Registro de eventos con marca de tiempo y cálculo de CPM.  
- Pantalla OLED con actualización periódica.  
- Envío de datos a Google Sheets mediante HTTPS.  
- Modo offline con reenvío automático.  
- Código modular y estable.

## Hardware requerido

- NodeMCU ESP8266  
- Dos detectores Geiger–Müller RadiationD-v1.1 (CAJOE)  
- Pantalla OLED I2C  (opcional)
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
