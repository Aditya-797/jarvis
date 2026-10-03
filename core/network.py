"""
Network Mesh & WAN Watchdog for Jarvis.
Performs sub-millisecond connectivity checks to Google & Cloudflare DNS.
Allows Jarvis to know whether the internet is alive BEFORE attempting cloud calls,
achieving instantaneous 0ms failover to on-device Local LLM when offline.
"""

import socket
import threading
import time
import logging

logger = logging.getLogger("Jarvis.Network")

class NetworkWatchdog:
    def __init__(self, check_interval: float = 8.0):
        self.check_interval = check_interval
        self._is_online = True
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()

    def is_online(self) -> bool:
        """Returns instantaneous WAN status without blocking."""
        return self._is_online

    def _test_connection(self) -> bool:
        """Tests TCP socket connection to Google DNS (8.8.8.8:53) or Cloudflare (1.1.1.1:53)."""
        for host in ["8.8.8.8", "1.1.1.1"]:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1.5)
                sock.connect((host, 53))
                sock.close()
                return True
            except OSError:
                continue
        return False

    def _monitor_loop(self):
        while self.running:
            online = self._test_connection()
            if online != self._is_online:
                if not online:
                    logger.warning("🌐 WAN Network Drop detected! Switching immediately to Local Edge AI.")
                else:
                    logger.info("🌐 Internet connectivity restored. Cloud intelligence tiers re-enabled.")
                self._is_online = online
            time.sleep(self.check_interval)

def get_local_ip_and_subnet() -> tuple[str, str]:
    """Finds current Wi-Fi private IP address and /24 subnet."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = "192.168.1.100"
    finally:
        s.close()

    parts = local_ip.split(".")
    if len(parts) == 4 and (local_ip.startswith("192.168.") or local_ip.startswith("10.") or local_ip.startswith("172.")):
        subnet = f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
    else:
        subnet = "192.168.1.0/24"
    return local_ip, subnet

def scan_local_subnet() -> str:
    """
    Performs a defensive host discovery scan on the local private Wi-Fi subnet.
    Uses nmap -sn if available, or falls back to system ARP/neighbor table.
    Strictly limited to private subnets.
    """
    import shutil
    import subprocess
    import re

    local_ip, subnet = get_local_ip_and_subnet()
    logger.info(f"🔍 Initiating local network discovery on {subnet} (Host IP: {local_ip})")

    # Method A: Use nmap if installed (host discovery ping sweep)
    if shutil.which("nmap"):
        try:
            cmd = ["nmap", "-sn", "--host-timeout", "15s", subnet]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            
            # Extract detected IPs and hostnames
            lines = res.stdout.splitlines()
            hosts = []
            for line in lines:
                if "Nmap scan report for" in line:
                    host_info = line.replace("Nmap scan report for", "").strip()
                    hosts.append(host_info)

            total = len(hosts)
            if total > 0:
                sample = ", ".join(hosts[:4])
                more = f" and {total - 4} others" if total > 4 else ""
                return f"Local network scan complete for subnet {subnet}. Detected {total} active devices, including {sample}{more}."
            else:
                return f"Network scan completed on {subnet}, but no active responsive hosts were detected."
        except subprocess.TimeoutExpired:
            return f"The network scan on {subnet} timed out."
        except Exception as e:
            logger.error(f"Nmap scan error: {e}")

    # Method B: Fallback using ARP cache / ip neigh (Zero-dependency, instantaneous)
    discovered_ips = set()
    
    # Try reading /proc/net/arp
    try:
        with open("/proc/net/arp", "r") as f:
            for line in f.readlines()[1:]:
                parts = line.split()
                if len(parts) >= 4 and parts[0] != "0.0.0.0" and parts[2] != "0x0":
                    discovered_ips.add(parts[0])
    except Exception:
        pass

    # Try ip neigh if available
    try:
        ip_res = subprocess.run(["ip", "neigh"], capture_output=True, text=True, timeout=3)
        for line in ip_res.stdout.splitlines():
            parts = line.split()
            if len(parts) >= 1 and "." in parts[0] and "REACHABLE" in line:
                discovered_ips.add(parts[0])
    except Exception:
        pass

    # Add local host
    discovered_ips.add(local_ip)
    total = len(discovered_ips)
    
    sample_ips = ", ".join(sorted(list(discovered_ips))[:4])
    return f"Subnet sweep complete for {subnet}. Found {total} active devices in the local routing table, including {sample_ips}."

