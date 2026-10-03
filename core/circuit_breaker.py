"""
Industrial Circuit Breaker for Jarvis Intelligence Tiers.
Prevents system hangs, API cascading failures, and latency spikes.
States:
- CLOSED: Normal operation, requests pass through.
- OPEN: Provider failed repeatedly; requests bypass immediately to next fallback.
- HALF-OPEN: Periodically tests if provider is back online in the background.
"""

import time
import logging

logger = logging.getLogger("Jarvis.CircuitBreaker")

class CircuitBreaker:
    def __init__(self, name: str, failure_threshold: int = 3, recovery_time: float = 30.0):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_time = recovery_time
        
        self.failure_count = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.last_failure_time = 0.0

    def can_execute(self) -> bool:
        """Determines if the tier should be attempted or bypassed."""
        now = time.time()
        
        if self.state == "OPEN":
            # Check if recovery cooldown has expired
            if now - self.last_failure_time > self.recovery_time:
                logger.info(f"🔄 CircuitBreaker [{self.name}]: Half-Open probe starting.")
                self.state = "HALF_OPEN"
                return True
            return False
            
        return True

    def record_success(self):
        """Resets the circuit on successful response."""
        if self.state != "CLOSED":
            logger.info(f"✅ CircuitBreaker [{self.name}]: Provider recovered. Circuit CLOSED.")
        self.failure_count = 0
        self.state = "CLOSED"

    def record_failure(self):
        """Increments failure and trips circuit if threshold reached."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            if self.state != "OPEN":
                logger.warning(
                    f"🚨 CircuitBreaker [{self.name}]: Tripped OPEN after {self.failure_count} failures! "
                    f"Bypassing to next tier for {self.recovery_time}s."
                )
            self.state = "OPEN"
