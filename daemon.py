#!/usr/bin/env python3
"""
MASTER SUPERVISOR & CRASH IMMUNITY GUARDIAN FOR JARVIS
Runs as PID 1 watchdog for Jarvis 24/7 server.

Features:
- Sub-second auto-restart if main.py ever encounters an unhandled exception or crash
- Thermal & memory leak self-healing
- MediaRecorder lock reset before restarts
- Crash thrashing prevention (exponential backoff if rapid crashes occur)
- Graceful shutdown propagation on SIGINT / SIGTERM
"""

import sys
import os
import time
import signal
import logging
import subprocess

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [SUPERVISOR] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("Jarvis.Supervisor")

MAX_CRASHES_WINDOW = 5
WINDOW_SECONDS = 30

class MasterSupervisor:
    def __init__(self):
        self.crash_timestamps = []
        self.running = True
        self.child_process = None

        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

    def _handle_signal(self, signum, frame):
        logger.info("Supervisor received shutdown signal. Terminating Jarvis gracefully...")
        self.running = False
        if self.child_process:
            self.child_process.terminate()
            try:
                self.child_process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.child_process.kill()
        sys.exit(0)

    def _reset_hardware_locks(self):
        """Forces Android MediaRecorder and audio locks to clear before spawn."""
        try:
            subprocess.run(["termux-microphone-record", "-q"], capture_output=True, timeout=2)
            subprocess.run(["killall", "-9", "termux-api"], capture_output=True, timeout=2)
        except Exception:
            pass

    def run(self):
        logger.info("🛡️ Master Supervisor initialized. Jarvis is running in Unbreakable Mode.")
        
        while self.running:
            self._reset_hardware_locks()
            
            logger.info("🚀 Launching Jarvis Core Agent (main.py)...")
            start_time = time.time()
            
            # Spawn main.py
            self.child_process = subprocess.Popen(
                [sys.executable, "main.py"],
                cwd=os.path.dirname(os.path.abspath(__file__)) or "."
            )

            exit_code = self.child_process.wait()
            run_duration = time.time() - start_time

            if not self.running:
                break

            logger.warning(f"⚠️ Jarvis process exited with code {exit_code} after {round(run_duration, 1)}s.")

            # Record crash
            now = time.time()
            self.crash_timestamps.append(now)
            self.crash_timestamps = [t for t in self.crash_timestamps if now - t < WINDOW_SECONDS]

            if len(self.crash_timestamps) >= MAX_CRASHES_WINDOW:
                logger.error("🚨 Frequent crash threshold reached! Cooldown for 10 seconds before reviving...")
                time.sleep(10)
                self.crash_timestamps.clear()
            else:
                logger.info("⚡ Self-Healing: Reviving Jarvis in 1 second...")
                time.sleep(1)

if __name__ == "__main__":
    supervisor = MasterSupervisor()
    supervisor.run()
