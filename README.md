# 🤖 JARVIS: 24/7 Open-Source Edge-Cloud Voice Intelligence

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Platform: Android Termux](https://img.shields.io/badge/Platform-Android%20Termux-green.svg)](https://termux.dev)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://python.org)
[![Intelligence: Gemini 2.0 & Grok](https://img.shields.io/badge/Intelligence-Gemini%202.0%20%7C%20Grok%20%7C%20Qwen-purple.svg)]()

> **Turn any old or spare Android phone into a 24/7 personal British AI assistant—completely free and open source.**

---

## ⚡ Zero Hardware Required (Bring Your Own Phone)

Jarvis is designed to be accessible to everyone on Earth:
* **No Extra Accessories Needed**: Works right out of the box using your phone's **built-in microphone** and **built-in speaker**.
* **Optional Futuristic Setup**: If you plug in a wireless lapel mic (like the Digitek DWM-101) or connect a Bluetooth speaker, Jarvis automatically leverages them for long-range room-wide control.
* **4GB RAM Friendly**: Optimized to run smoothly on old/budget smartphones with 4GB RAM without thermal throttling.

---

## 🚀 1-Line Instant Install

Open **[Termux](https://f-droid.org/en/packages/com.termux/)** on your Android phone and paste this single command (includes auto-DNS fix for Android 14/15):

```bash
cd ~ && dpkg --purge --force-all ffmpeg 2>/dev/null; rm -rf ~/jarvis && mkdir -p $PREFIX/etc && printf "nameserver 8.8.8.8\nnameserver 1.1.1.1\n" > $PREFIX/etc/resolv.conf && git clone https://github.com/Aditya-797/jarvis.git ~/jarvis && cd ~/jarvis && bash install.sh
```

**The 15-second wizard will:**
1. Install Python, Nmap, FFmpeg, and dependencies automatically.
2. Prompt you to paste your free **Gemini API key** (from [aistudio.google.com](https://aistudio.google.com)) and optional **Grok key**.
3. Test your speaker with Jarvis's authentic British voice.
4. Launch Jarvis immediately!

---

## 🌟 Superpowers & Features

| Capability | Engine | What Jarvis Does |
| :--- | :--- | :--- |
| 🎩 **Authentic British Persona** | Paul Bettany Style | Sophisticated, dryly witty, protective gentleman. Always calls you "sir". |
| 🇮🇳 **Bilingual Comprehension** | Hindi & English | Speak in pure Hindi, Hinglish, or English—Jarvis understands effortlessly and responds in English. |
| 🌐 **Live Web Intelligence** | Gemini 2.0 Search Grounding | Instant real-time info: live cricket/football scores, weather, stock prices, news. |
| 📱 **Deep Phone Control** | Termux:API & Android Intents | Controls flashlight, volume, brightness, battery thermals, launches apps, makes calls, snaps photos. |
| 💻 **PC & Browser Automation** | WebSocket Event Bus | Voice-controls your computer: opens websites, controls YouTube, locks workstation. |
| 🏡 **Smart Home IoT Hub** | ESP32 Wi-Fi Relays | Toggles room lights, fans, and appliances via simple relay modules. |
| 🔍 **Network Subnet Discovery** | Nmap / Kernel ARP | Scans local Wi-Fi to identify connected PCs, phones, and IoT nodes (*"Jarvis, scan my network"*). |
| 🧠 **Eidetic Memory Banks** | SQLite WAL Database | Learns your habits, preferences, and details across sessions (*"Jarvis, remember that..."*). |
| 🛡️ **100% Offline Edge Fallback** | Qwen 2.5 (1.5B) via llama.cpp | Keeps running locally on your phone's CPU even during total internet blackouts. |
| 📊 **Mission Control HUD** | Port `8766` Web Dashboard | View live thermals, battery %, active mic, telemetry, and memories in any browser. |

---

## 🗣️ Example Voice Commands

* **Capabilities**: *"Jarvis, what can you do?"* / *"Jarvis, tum kya kar sakte ho?"*
* **Phone**: *"Jarvis, turn on my flashlight."* / *"Jarvis, flashlight on kar do."*
* **Battery**: *"Jarvis, report battery status."* (Checks %, charging state, and CPU thermals).
* **Live Search**: *"Jarvis, who won the match today?"* / *"Jarvis, bahar mausam kaisa hai?"*
* **Network**: *"Jarvis, scan my network."* (Discovers devices on your Wi-Fi subnet).
* **Memory**: *"Jarvis, remember that my favorite coffee is cappuccino."*
* **PC Control**: *"Jarvis, open YouTube and play lofi beats."* / *"Jarvis, lock my workstation."*

---

## 📊 Mission Control Dashboard

While Jarvis is running, open your PC or laptop browser to:
```
http://<PHONE_IP>:8766
```
Displays your futuristic dark-mode HUD: real-time battery thermals, WAN status, response latency, and active memory items.

---

## 🏛️ System Architecture

```
                       ┌────────────────────────┐
                       │ 🎙️ Any Phone Mic / USB │
                       └───────────┬────────────┘
                                   │ (Adaptive Audio Engine)
                                   ▼
                       ┌────────────────────────┐
                       │     core/brain.py      │
                       └───────────┬────────────┘
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         ▼                         ▼                         ▼
   [ Tier 1: Gemini 2.0 ]    [ Tier 2: Grok xAI ]      [ Tier 3: Local LLM ]
   • Real-Time Google Search • Cloud Fallback          • 100% Offline (Phone)
   • Multimodal Audio Input  • Deep Reasoning          • Qwen 2.5 (1.5B GGUF)
   • Free Tier (Google AI)   • xAI API                 • llama.cpp on Phone
         │                         │                         │
         └─────────────────────────┼─────────────────────────┘
                                   │
                                   ▼
                       ┌────────────────────────┐
                       │   core/tools.py        │
                       └───────────┬────────────┘
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         ▼                         ▼                         ▼
 [ 📱 Phone Hardware ]     [ 💻 PC & Browser ]       [ 🏡 ESP32 Smart Home ]
 • Torch / Volume / Bright • Launch URLs / YouTube   • Wi-Fi Relays
 • Battery / Thermals      • Lock Workstation        • Room Lights / Fans
 • App Launcher / Calls    • Nmap Network Discovery  • Sensor Hub
         │                         │                         │
         └─────────────────────────┴─────────────────────────┘
                                   │
                                   ▼
                       [ 🔊 Phone / Bluetooth Speaker ]
                       • Authentic British Speech (en-GB)
```

---

## 📄 License

This project is open source and available under the **[MIT License](LICENSE)**. Anyone is free to use, modify, and contribute!
