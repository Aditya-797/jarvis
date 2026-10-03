#!/usr/bin/env python3
"""
JARVIS PC CONTROLLER AGENT (ZERO CONFIGURATION)
Run this script on your PC / Laptop (Mac, Windows, or Linux).

Features:
- ✨ Zero-Config Auto-Discovery: Automatically finds your phone on Wi-Fi without typing IPs!
- 🌐 Browser control (open URLs, YouTube, search Google)
- 🔒 System control (lock screen, sleep, volume, terminal)
"""

import sys
import os
import json
import socket
import asyncio
import platform
import subprocess
import webbrowser
import websockets

CURRENT_OS = platform.system().lower()
DISCOVERY_PORT = 8764

def discover_jarvis_ip(timeout: float = 3.0) -> tuple[str, int]:
    """Broadcasts a UDP discovery packet to find Jarvis on the local Wi-Fi automatically."""
    print("🔍 Searching for Jarvis on your local Wi-Fi network...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(timeout)

    try:
        # Broadcast discovery beacon
        sock.sendto(b"JARVIS_DISCOVER", ("255.255.255.255", DISCOVERY_PORT))
        data, addr = sock.recvfrom(1024)
        msg = data.decode("utf-8", errors="ignore").strip()
        
        if "JARVIS_ACK" in msg:
            port = int(msg.split(":")[1]) if ":" in msg else 8765
            phone_ip = addr[0]
            print(f"✨ Found Jarvis Phone Server automatically at: {phone_ip}:{port}")
            return phone_ip, port
    except Exception:
        pass
    finally:
        sock.close()

    print("⚠️ Auto-discovery timed out. Falling back to default (192.168.1.100:8765)")
    return "192.168.1.100", 8765

def execute_command(command: str):
    """Executes system and browser actions on this PC."""
    print(f"\n⚡ [Jarvis Command Received]: {command}")
    
    parts = command.strip().split(" ", 1)
    action = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else ""

    # --- Browser Control ---
    if action in ["open_url", "browser"]:
        url = arg if arg.startswith("http") else f"https://{arg}"
        webbrowser.open(url)
        print(f"🌐 Opened: {url}")

    elif action == "youtube":
        url = f"https://www.youtube.com/results?search_query={arg}" if arg else "https://www.youtube.com"
        webbrowser.open(url)
        print(f"▶️ Opened YouTube: {arg}")

    elif action == "google":
        url = f"https://www.google.com/search?q={arg}"
        webbrowser.open(url)
        print(f"🔍 Searched Google for: {arg}")

    # --- System Control ---
    elif action == "lock":
        if "darwin" in CURRENT_OS:
            subprocess.run(["pmset", "displaysleepnow"])
        elif "windows" in CURRENT_OS:
            subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
        elif "linux" in CURRENT_OS:
            subprocess.run(["xdg-screensaver", "lock"])
        print("🔒 Workstation locked.")

    elif action == "volume_up":
        if "darwin" in CURRENT_OS:
            subprocess.run(["osascript", "-e", "set volume output volume ((output volume of (get volume settings)) + 15)"])
        print("🔊 Volume increased.")

    elif action == "volume_down":
        if "darwin" in CURRENT_OS:
            subprocess.run(["osascript", "-e", "set volume output volume ((output volume of (get volume settings)) - 15)"])
        print("🔉 Volume decreased.")

    elif action == "terminal":
        if "darwin" in CURRENT_OS:
            subprocess.run(["open", "-a", "Terminal"])
        elif "windows" in CURRENT_OS:
            subprocess.run(["start", "cmd"], shell=True)
        print("💻 Terminal launched.")

    else:
        print(f"⚠️ Unknown action: {action}")

async def listen_to_jarvis(host: str, port: int):
    uri = f"ws://{host}:{port}"
    print(f"Connecting to Jarvis at {uri} ...")
    
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                print(f"✅ Connected to Jarvis! Ready to execute voice commands.\n")
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        target = data.get("target", "").lower()
                        cmd = data.get("command", "")
                        
                        if target in ["pc", "computer", "browser"]:
                            execute_command(cmd)
                    except json.JSONDecodeError:
                        pass
        except (websockets.exceptions.ConnectionClosed, ConnectionRefusedError, OSError):
            print("⚠️ Connection lost. Re-discovering Jarvis in 5 seconds...")
            await asyncio.sleep(5)
            # Re-discover in case phone's IP changed via DHCP
            new_host, new_port = discover_jarvis_ip(timeout=2.0)
            uri = f"ws://{new_host}:{new_port}"

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║        ⚡ JARVIS ZERO-CONFIG PC BRIDGE AGENT          ║
    ║      Listening for voice commands from your phone     ║
    ╚═══════════════════════════════════════════════════════╝
    """)
    
    if len(sys.argv) > 1:
        phone_ip = sys.argv[1]
        phone_port = 8765
    else:
        phone_ip, phone_port = discover_jarvis_ip()

    asyncio.run(listen_to_jarvis(phone_ip, phone_port))
