"""
Phone Automation & Hardware Control Engine for Jarvis.
Leverages Termux:API and Android Intent system to provide deep phone control:
- Flashlight / Torch
- Battery level, health & thermals
- Brightness & Screen Control
- Audio stream volume (Media, Ring, Notification)
- App launching (WhatsApp, YouTube, Spotify, Camera, etc.)
- Telephony & SMS (Make calls, send messages)
- Hardware sensors (Vibration, Wi-Fi info, Camera snap, Location)
- Clipboard management
"""

import json
import logging
import subprocess
import shutil

logger = logging.getLogger("Jarvis.PhoneControl")

# Common package mapping for quick app launching
APP_PACKAGES = {
    "whatsapp": "com.whatsapp",
    "youtube": "com.google.android.youtube",
    "spotify": "com.spotify.music",
    "camera": "net.sourceforge.opencamera",
    "maps": "com.google.android.apps.maps",
    "chrome": "com.android.chrome",
    "settings": "com.android.settings",
    "telegram": "org.telegram.messenger",
    "gallery": "com.google.android.apps.photos"
}

class PhoneController:
    def __init__(self):
        self.api_available = shutil.which("termux-battery-status") is not None

    def _run_cmd(self, cmd: list, timeout: int = 5) -> str:
        """Helper to run a shell command safely."""
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return res.stdout.strip()
        except subprocess.TimeoutExpired:
            logger.warning(f"Command timed out: {' '.join(cmd)}")
            return ""
        except Exception as e:
            logger.error(f"Error running {' '.join(cmd)}: {e}")
            return ""

    # ==================== HARDWARE & SENSORS ====================

    def toggle_torch(self, state: bool) -> str:
        """Turns the phone flashlight on or off."""
        arg = "on" if state else "off"
        self._run_cmd(["termux-torch", arg])
        return f"Flashlight has been turned {arg}."

    def get_battery_info(self) -> dict:
        """Returns battery percentage, health, temperature, and charging status."""
        out = self._run_cmd(["termux-battery-status"])
        if not out:
            return {"percentage": "unknown", "status": "unknown"}
        try:
            return json.loads(out)
        except Exception:
            return {"percentage": "unknown", "status": "unknown"}

    def set_volume(self, stream: str, volume: int) -> str:
        """
        Sets volume for a specific stream:
        stream: 'music', 'ring', 'notification', 'system', 'alarm'
        volume: 0 to 15
        """
        valid_streams = ["music", "ring", "notification", "system", "alarm"]
        target_stream = stream.lower() if stream.lower() in valid_streams else "music"
        volume = max(0, min(15, volume))
        self._run_cmd(["termux-volume", target_stream, str(volume)])
        return f"Phone {target_stream} volume set to {volume}."

    def set_brightness(self, level: int) -> str:
        """Sets screen brightness (0 to 255)."""
        level = max(0, min(255, level))
        self._run_cmd(["termux-brightness", str(level)])
        return f"Screen brightness adjusted to {level}."

    def vibrate(self, duration_ms: int = 300) -> str:
        """Vibrates the phone for a specified number of milliseconds."""
        self._run_cmd(["termux-vibrate", "-d", str(duration_ms)])
        return "Phone vibrated."

    def get_wifi_status(self) -> dict:
        """Returns connected Wi-Fi SSID, IP, and link speed."""
        out = self._run_cmd(["termux-wifi-connectioninfo"])
        if out:
            try:
                return json.loads(out)
            except Exception:
                pass
        return {"status": "Not connected or unavailable"}

    # ==================== APP LAUNCHING & INTENTS ====================

    def launch_app(self, app_name: str) -> str:
        """Launches an app by name or package."""
        clean_name = app_name.lower().strip()
        pkg = APP_PACKAGES.get(clean_name, clean_name)
        
        # Launch via Android monkey intent runner
        cmd = ["monkey", "-p", pkg, "-c", "android.intent.category.LAUNCHER", "1"]
        self._run_cmd(cmd)
        return f"Launching {app_name} on your phone."

    def open_url(self, url: str) -> str:
        """Opens any webpage or web link in phone's default browser."""
        target = url if url.startswith("http") else f"https://{url}"
        self._run_cmd(["termux-open-url", target])
        return f"Opening {target} on your phone."

    # ==================== TELEPHONY & MESSAGING ====================

    def make_call(self, phone_number: str) -> str:
        """Initiates a phone call to the specified number."""
        self._run_cmd(["termux-telephony-call", phone_number])
        return f"Calling {phone_number}."

    def send_sms(self, phone_number: str, message: str) -> str:
        """Sends an SMS message to a contact."""
        self._run_cmd(["termux-sms-send", "-n", phone_number, message])
        return f"SMS sent to {phone_number}."

    # ==================== CAMERA & SENSORS ====================

    def capture_photo(self, output_path: str = "capture.jpg", camera_id: int = 0) -> str:
        """
        Snaps a quick photo using front (1) or rear (0) camera.
        """
        self._run_cmd(["termux-camera-photo", "-c", str(camera_id), output_path])
        return f"Photo captured and saved to {output_path}."

    # ==================== CLIPBOARD ====================

    def get_clipboard(self) -> str:
        """Reads current phone clipboard text."""
        return self._run_cmd(["termux-clipboard-get"])

    def set_clipboard(self, text: str) -> str:
        """Copies text to phone clipboard."""
        self._run_cmd(["termux-clipboard-set", text])
        return "Copied to clipboard."
