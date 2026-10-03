"""
Event Bus & Zero-Config Auto-Discovery for Jarvis.
Runs:
1. WebSocket Server (Port 8765): Dispatches real-time commands to PC clients & ESP32.
2. UDP Discovery Beacon (Port 8764): Automatically announces Jarvis's presence on Wi-Fi
   so ESP32 and PC clients connect without the user having to type or configure IP addresses!
"""

import socket
import asyncio
import json
import logging
import threading
import websockets

logger = logging.getLogger("Jarvis.EventBus")

class EventBus:
    def __init__(self, host: str = "0.0.0.0", port: int = 8765, discovery_port: int = 8764):
        self.host = host
        self.port = port
        self.discovery_port = discovery_port
        self.connected_clients = set()
        self.loop = None
        self.ws_thread = None
        self.udp_thread = None
        self.running = True

    def start(self):
        """Starts the WebSocket server and the UDP discovery responder in background threads."""
        self.ws_thread = threading.Thread(target=self._run_server, daemon=True)
        self.ws_thread.start()
        
        self.udp_thread = threading.Thread(target=self._run_udp_discovery, daemon=True)
        self.udp_thread.start()

        logger.info(f"🌐 Event Bus server started at ws://{self.host}:{self.port}")
        logger.info(f"📡 Zero-Config Auto-Discovery active on UDP port {self.discovery_port}")

    def _run_udp_discovery(self):
        """
        Listens for 'JARVIS_DISCOVER' broadcast packets from ESP32 or PC clients,
        and replies with 'JARVIS_ACK:<ws_port>' so devices auto-connect without typing IPs.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("0.0.0.0", self.discovery_port))
            while self.running:
                data, addr = sock.recvfrom(1024)
                msg = data.decode("utf-8", errors="ignore").strip()
                if "JARVIS_DISCOVER" in msg:
                    # Reply with our WebSocket port
                    reply = f"JARVIS_ACK:{self.port}".encode("utf-8")
                    sock.sendto(reply, addr)
                    logger.info(f"✨ Auto-Discovery: Dispatched server address to client at {addr[0]}")
        except Exception as e:
            logger.debug(f"UDP Discovery loop stopped: {e}")
        finally:
            sock.close()

    def _run_server(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        start_server = websockets.serve(self._handler, self.host, self.port)
        self.loop.run_until_complete(start_server)
        self.loop.run_forever()

    async def _handler(self, websocket):
        self.connected_clients.add(websocket)
        logger.info(f"Device connected: {websocket.remote_address}")
        try:
            async for message in websocket:
                pass
        except Exception:
            pass
        finally:
            self.connected_clients.remove(websocket)
            logger.info(f"Device disconnected: {websocket.remote_address}")

    def dispatch(self, target: str, command: str):
        """Dispatches an action payload to all connected clients (PC or ESP32)."""
        if not self.connected_clients or not self.loop:
            logger.warning(f"No devices connected to receive action: {target} -> {command}")
            return

        payload = json.dumps({"target": target, "command": command})
        logger.info(f"📡 Broadcasting to ecosystem: {payload}")

        async def _broadcast():
            to_remove = set()
            for ws in self.connected_clients:
                try:
                    await ws.send(payload)
                except Exception:
                    to_remove.add(ws)
            self.connected_clients.difference_update(to_remove)

        asyncio.run_coroutine_threadsafe(_broadcast(), self.loop)
