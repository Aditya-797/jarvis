# ⚡ ESP32 Smart Home Node (Zero-Config Setup)

Connects room lights, fans, and appliances to Jarvis over Wi-Fi.

---

### ✨ Features
* **Zero IP Configuration**: The ESP32 automatically discovers your Jarvis phone on the Wi-Fi network using UDP broadcast beacons! You never have to find or hardcode the phone's IP address.
* **Dual Relay Control**:
  - Relay 1 (GPIO 23): Room Lights / Desk Lamp
  - Relay 2 (GPIO 22): Fan / Room Appliances
* **Status LED (GPIO 2)**:
  - Blinking: Searching for Wi-Fi or Jarvis
  - Solid ON: Connected and listening for voice commands

---

### 🚀 3-Minute Flashing Guide:

1. **Open Arduino IDE**:
   - Install **ESP32 Board Package** in *Tools $\rightarrow$ Board $\rightarrow$ Boards Manager* (search "esp32").
   - Install these 2 libraries in *Tools $\rightarrow$ Manage Libraries*:
     1. **WebSockets** (by Markus Sattler)
     2. **ArduinoJson** (by Benoit Blanchon)

2. **Configure Wi-Fi**:
   Open [`esp32_jarvis.ino`](esp32_jarvis.ino) and only edit lines 27–28:
   ```cpp
   const char* ssid     = "YOUR_WIFI_NAME";
   const char* password = "YOUR_WIFI_PASSWORD";
   ```
   *(You do NOT need to enter any IP address! Auto-discovery finds Jarvis automatically).*

3. **Click Upload (Arrow icon)**:
   - Select your ESP32 board and COM port.
   - Click **Upload**.

---

### 🗣️ Voice Commands:
* *"Jarvis, turn on the lights."* / *"Jarvis, light on karo."*
* *"Jarvis, turn off the lights."*
* *"Jarvis, turn on the fan."*
