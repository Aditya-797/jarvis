/*
 * ==============================================================================
 * ⚡ JARVIS ESP32 SMART HOME NODE (ZERO-CONFIG AUTO-DISCOVERY)
 * ==============================================================================
 * Automatically discovers the Jarvis Phone Server on your Wi-Fi!
 * You NEVER have to configure or hardcode the phone's IP address.
 * 
 * Hardware:
 * - ESP32 Dev Module (or ESP8266)
 * - Relay 1: GPIO 23 (Room Light / Desk Lamp)
 * - Relay 2: GPIO 22 (Fan / Appliance)
 * - Onboard LED: GPIO 2 (Status Indicator)
 * 
 * Required Libraries (Install via Arduino Library Manager):
 * 1. WebSockets by Markus Sattler
 * 2. ArduinoJson by Benoit Blanchon (v6 or v7)
 * ==============================================================================
 */

#include <WiFi.h>
#include <WiFiUdp.h>
#include <WebSocketsClient.h>
#include <ArduinoJson.h>

// ================= USER CONFIGURATION =================
// Only enter your home Wi-Fi details. That is all!
const char* ssid     = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
// =====================================================

// Pin Definitions
const int RELAY_LIGHT = 23;
const int RELAY_FAN   = 22;
const int LED_STATUS  = 2;

// Networking
WiFiUDP udp;
const int UDP_DISCOVERY_PORT = 8764;
String jarvis_ip = "";
int jarvis_port = 8765;

WebSocketsClient webSocket;
bool is_connected = false;

// ----------------- AUTO-DISCOVERY ENGINE -----------------
void discoverJarvis() {
  Serial.println("🔍 Searching for Jarvis Phone Server on local Wi-Fi...");
  udp.begin(UDP_DISCOVERY_PORT);

  int attempts = 0;
  while (jarvis_ip == "" && attempts < 10) {
    attempts++;
    // Broadcast discovery packet to whole subnet
    udp.beginPacket(IPAddress(255, 255, 255, 255), UDP_DISCOVERY_PORT);
    udp.print("JARVIS_DISCOVER");
    udp.endPacket();

    delay(600);

    int packetSize = udp.parsePacket();
    if (packetSize > 0) {
      char packetBuffer[255];
      int len = udp.read(packetBuffer, 254);
      packetBuffer[len] = '\0';
      String msg = String(packetBuffer);

      if (msg.startsWith("JARVIS_ACK")) {
        jarvis_ip = udp.remoteIP().toString();
        int colon = msg.indexOf(':');
        if (colon != -1) {
          jarvis_port = msg.substring(colon + 1).toInt();
        }
        Serial.printf("✨ Found Jarvis automatically at: %s:%d\n", jarvis_ip.c_str(), jarvis_port);
        digitalWrite(LED_STATUS, HIGH);
        break;
      }
    }
    digitalWrite(LED_STATUS, !digitalRead(LED_STATUS)); // Blink while searching
  }

  udp.stop();

  // Fallback if broadcast was blocked by router AP isolation
  if (jarvis_ip == "") {
    jarvis_ip = "192.168.1.100";
    Serial.println("⚠️ Auto-discovery timed out. Falling back to default: 192.168.1.100");
  }
}

// ----------------- WEBSOCKET PROTOCOL -----------------
void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  switch(type) {
    case WStype_DISCONNECTED:
      Serial.println("[WebSocket] Disconnected from Jarvis. Will reconnect...");
      is_connected = false;
      digitalWrite(LED_STATUS, LOW);
      break;

    case WStype_CONNECTED:
      Serial.println("✅ [WebSocket] Connected to Jarvis Home Server!");
      is_connected = true;
      digitalWrite(LED_STATUS, HIGH);
      break;

    case WStype_TEXT: {
      Serial.printf("⚡ [Jarvis Command]: %s\n", payload);
      
      StaticJsonDocument<256> doc;
      DeserializationError error = deserializeJson(doc, payload);
      if (error) return;

      String target = doc["target"].as<String>();
      String command = doc["command"].as<String>();
      target.toLowerCase();
      command.toLowerCase();

      // --- Light Control ---
      if (target.indexOf("light") != -1 || target.indexOf("home") != -1) {
        if (command.indexOf("on") != -1) {
          digitalWrite(RELAY_LIGHT, HIGH);
          Serial.println("💡 Room Light turned ON");
        } else if (command.indexOf("off") != -1) {
          digitalWrite(RELAY_LIGHT, LOW);
          Serial.println("🌑 Room Light turned OFF");
        }
      }

      // --- Fan / Appliance Control ---
      if (target.indexOf("fan") != -1 || target.indexOf("appliance") != -1) {
        if (command.indexOf("on") != -1) {
          digitalWrite(RELAY_FAN, HIGH);
          Serial.println("💨 Fan turned ON");
        } else if (command.indexOf("off") != -1) {
          digitalWrite(RELAY_FAN, LOW);
          Serial.println("⏹️ Fan turned OFF");
        }
      }
      break;
    }
    default:
      break;
  }
}

void setup() {
  Serial.begin(115200);
  
  pinMode(RELAY_LIGHT, OUTPUT);
  pinMode(RELAY_FAN, OUTPUT);
  pinMode(LED_STATUS, OUTPUT);
  
  digitalWrite(RELAY_LIGHT, LOW);
  digitalWrite(RELAY_FAN, LOW);
  digitalWrite(LED_STATUS, LOW);

  // 1. Connect to Home Wi-Fi
  Serial.printf("\nConnecting to Wi-Fi: %s ", ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(400);
    Serial.print(".");
    digitalWrite(LED_STATUS, !digitalRead(LED_STATUS));
  }
  Serial.printf("\n✅ Wi-Fi Connected! ESP32 IP: %s\n", WiFi.localIP().toString().c_str());

  // 2. Discover Jarvis on Wi-Fi automatically
  discoverJarvis();

  // 3. Connect to Jarvis WebSocket Server
  webSocket.begin(jarvis_ip.c_str(), jarvis_port, "/");
  webSocket.onEvent(webSocketEvent);
  webSocket.setReconnectInterval(5000);
}

void loop() {
  webSocket.loop();
}
