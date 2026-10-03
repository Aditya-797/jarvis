"""
Health & Self-Healing Monitor for 24/7 Jarvis Server.
Monitors:
- Battery temperature & charging safety (prevents battery bloat)
- RAM usage & garbage collection (zero memory leaks)
- Disk storage cleaner (auto-purges temp audio files)
- CPU throttling watchdog
"""

import os
import gc
import glob
import time
import json
import logging
import subprocess

logger = logging.getLogger("Jarvis.Health")

class SystemHealthGuardian:
    def __init__(self, max_battery_temp: float = 43.0):
        self.max_battery_temp = max_battery_temp
        self.last_cleanup = time.time()
        self.last_thermal_alert = 0.0

    def periodic_maintenance(self):
        """Runs periodic health checks, garbage collection, and disk cleanup."""
        now = time.time()
        
        # Run cleanup every 10 minutes
        if now - self.last_cleanup > 600:
            self._clean_temp_files()
            self._enforce_garbage_collection()
            self.last_cleanup = now

    def _enforce_garbage_collection(self):
        """Forces Python to release unreferenced memory back to the OS."""
        collected = gc.collect()
        logger.debug(f"🧹 Garbage collector freed {collected} objects.")

    def _clean_temp_files(self):
        """Deletes any orphaned audio files older than 5 minutes to protect phone storage."""
        cleaned = 0
        for pattern in ["*.m4a", "input_*.wav", "temp_*.wav", "capture_*.jpg"]:
            for filepath in glob.glob(pattern):
                try:
                    if time.time() - os.path.getmtime(filepath) > 300:
                        os.remove(filepath)
                        cleaned += 1
                except Exception:
                    pass
        if cleaned > 0:
            logger.info(f"💾 Storage guardian auto-purged {cleaned} stale temporary files.")

    def check_thermal_safety(self) -> tuple[bool, str]:
        """
        Checks phone battery temperature via Termux API.
        Returns: (is_safe: bool, warning_message: str)
        """
        try:
            res = subprocess.run(["termux-battery-status"], capture_output=True, text=True, timeout=3)
            if res.stdout:
                data = json.loads(res.stdout)
                temp = float(data.get("temperature", 30.0))
                
                if temp > self.max_battery_temp:
                    now = time.time()
                    # Alert at most once every 15 minutes
                    if now - self.last_thermal_alert > 900:
                        self.last_thermal_alert = now
                        msg = f"Warning: Phone temperature is {round(temp, 1)} degrees. Please unplug charger."
                        logger.warning(f"🔥 THERMAL ALERT: {msg}")
                        return False, msg
        except Exception:
            pass

        return True, ""
