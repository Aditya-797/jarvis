#!/usr/bin/env python3
"""
JARVIS - 24/7 Mobile Voice Agent & Home Controller
Unbreakable Production Daemon with:
- Dual-Mic Failover (DWM-101 <-> Internal Mic)
- Circuit-Breaker Protected 3-Tier Intelligence
- System Health Guardian (Thermal & RAM Self-Cleaning)
- Full Phone Hardware, PC, and Smart Home Automation
"""

import os
import sys
import time
import yaml
import logging
import subprocess

from core.audio import AudioManager
from core.brain import BrainRouter
from core.event_bus import EventBus
from core.health import SystemHealthGuardian
from core.dashboard_server import DashboardServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("Jarvis.Main")

def load_config(config_path="config.yaml"):
    if not os.path.exists(config_path):
        logger.error(f"Config file not found at {config_path}")
        sys.exit(1)
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def ensure_termux_wakelock():
    """Acquires CPU wakelock to prevent Android from sleeping."""
    try:
        subprocess.run(["termux-wake-lock"], capture_output=True)
        logger.info("🔒 Termux wake-lock active (CPU sleep prevented).")
    except Exception:
        pass

def main():
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║                 J.A.R.V.I.S.  ONLINE                  ║
    ║         Unbreakable 24/7 Self-Healing Engine          ║
    ╚═══════════════════════════════════════════════════════╝
    """)

    config = load_config()

    if config.get("system", {}).get("wake_lock", True):
        ensure_termux_wakelock()

    # 1. Start Event Bus for PC and IoT communication
    event_bus = None
    if config.get("server", {}).get("enable_event_bus", True):
        port = config.get("server", {}).get("port", 8765)
        event_bus = EventBus(port=port)
        event_bus.start()

    # 2. Initialize Subsystems
    audio = AudioManager(config)
    brain = BrainRouter(config, event_bus=event_bus)
    health = SystemHealthGuardian()

    # 3. Start Industrial Mission-Control Web Dashboard (Port 8766)
    def telemetry_provider():
        battery_data = brain.tool_manager.phone.get_battery_info()
        return {
            "battery": battery_data,
            "active_mic": audio.active_mic_source,
            "is_online": brain.network.is_online(),
            "metrics": brain.db.get_metrics_summary(),
            "memories": brain.db.get_all_memories(limit=10)
        }

    dashboard = DashboardServer(port=8766, data_provider=telemetry_provider)
    dashboard.start()

    audio.speak("Good day, sir. All systems are operational, and I am entirely at your service.")

    listen_duration = config.get("system", {}).get("hotword_duration", 5)

    while True:
        try:
            # Step A: Run background maintenance (RAM cleanup, disk scrub)
            health.periodic_maintenance()

            # Step B: Check battery thermal safety
            is_safe, thermal_warning = health.check_thermal_safety()
            if not is_safe and thermal_warning:
                audio.speak(thermal_warning)

            # Step C: Listen via Self-Healing Dual-Mic (DWM-101 <-> Internal)
            audio_path, mic_alert = audio.record(duration=listen_duration)

            # If mic state changed (e.g. DWM-101 disconnected), notify user
            if mic_alert:
                audio.speak(mic_alert)

            if not audio_path:
                time.sleep(0.5)
                continue

            # Step D: Process with Circuit-Breaker protected Brain
            print("🧠 [Jarvis Thinking] Processing audio...")
            reply = brain.process_voice_input(audio_path)

            # Step E: Speak reply via Bluetooth Speaker
            audio.speak(reply)

            time.sleep(0.3)

        except KeyboardInterrupt:
            audio.speak("Shutting down core protocols. Do try to stay out of trouble without me, sir.")
            logger.info("Jarvis stopped by user.")
            break
        except Exception as e:
            logger.error(f"Recovered from transient error in main loop: {e}", exc_info=True)
            time.sleep(1)

if __name__ == "__main__":
    main()
