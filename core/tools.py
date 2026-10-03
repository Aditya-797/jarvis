"""
Tool Registry and Action Dispatcher for Jarvis.
Provides unified tool execution for:
1. Phone Hardware & Android Automation
2. PC & Browser Control (via Event Bus)
3. Smart Home / ESP32 Control (via Event Bus)
"""

import json
import logging
from core.phone_control import PhoneController

logger = logging.getLogger("Jarvis.Tools")

class ToolManager:
    def __init__(self, event_bus=None):
        self.phone = PhoneController()
        self.event_bus = event_bus

    def execute_tool(self, tool_name: str, args: dict) -> str:
        """Executes a requested tool and returns the text result for the LLM to speak."""
        logger.info(f"🛠️ Executing tool: {tool_name} with args: {args}")

        try:
            # 1. PHONE AUTOMATION TOOLS
            if tool_name == "toggle_flashlight":
                state = bool(args.get("state", True))
                return self.phone.toggle_torch(state)

            elif tool_name == "get_phone_battery":
                data = self.phone.get_battery_info()
                pct = data.get("percentage", "unknown")
                status = data.get("status", "unknown")
                temp = data.get("temperature", "")
                temp_str = f"at {round(float(temp), 1)}°C" if temp else ""
                return f"Battery is at {pct} percent, currently {status} {temp_str}."

            elif tool_name == "set_phone_volume":
                stream = args.get("stream", "music")
                level = int(args.get("level", 10))
                return self.phone.set_volume(stream, level)

            elif tool_name == "set_phone_brightness":
                level = int(args.get("level", 128))
                return self.phone.set_brightness(level)

            elif tool_name == "launch_phone_app":
                app_name = args.get("app_name", "")
                return self.phone.launch_app(app_name)

            elif tool_name == "phone_vibrate":
                duration = int(args.get("duration_ms", 300))
                return self.phone.vibrate(duration)

            elif tool_name == "make_phone_call":
                phone = args.get("phone_number", "")
                return self.phone.make_call(phone)

            elif tool_name == "send_phone_sms":
                phone = args.get("phone_number", "")
                msg = args.get("message", "")
                return self.phone.send_sms(phone, msg)

            elif tool_name == "phone_snap_photo":
                cam_id = int(args.get("camera_id", 0))  # 0: rear, 1: front
                return self.phone.capture_photo(camera_id=cam_id)

            elif tool_name == "get_wifi_status":
                info = self.phone.get_wifi_status()
                ssid = info.get("ssid", "unknown")
                ip = info.get("ip", "unknown")
                return f"Connected to Wi-Fi network {ssid} with IP {ip}."

            elif tool_name == "scan_local_network":
                from core.network import scan_local_subnet
                return scan_local_subnet()

            elif tool_name == "remember_fact":
                fact = args.get("fact", "")
                return f"Committed to memory banks: {fact}"

            # 2. PC & BROWSER CONTROL TOOLS (via EventBus)
            elif tool_name == "control_pc":
                action = args.get("action", "")
                param = args.get("parameter", "")
                if self.event_bus:
                    self.event_bus.dispatch("pc", f"{action} {param}".strip())
                    return f"Sent command to your computer: {action} {param}."
                else:
                    return "PC is not currently connected to the Jarvis event bus."

            # 3. SMART HOME / ESP32 TOOLS
            elif tool_name == "control_home":
                target = args.get("device", "light")
                state = args.get("state", "toggle")
                if self.event_bus:
                    self.event_bus.dispatch("home", f"{target} {state}")
                    return f"Adjusted home device {target} to {state}."
                else:
                    return "Home automation hub is not connected."

            else:
                return f"Unknown tool: {tool_name}"

        except Exception as e:
            logger.error(f"Error running tool {tool_name}: {e}")
            return f"Failed to execute {tool_name}: {str(e)}"
