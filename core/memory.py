"""
Persistent Long-Term Memory Engine for Jarvis.
Enables Jarvis to:
- Learn and retain user habits, preferences, names, and life details
- Recall context across sessions and reboots (persisted in JSON)
- Auto-extract facts when the user says "remember that...", "my favorite...", etc.
- Seamlessly inject learned memories into Jarvis's cognitive prompt
"""

import os
import json
import time
import logging

from core.database import DatabaseEngine

logger = logging.getLogger("Jarvis.Memory")

MEMORY_DIR = "memory"
MEMORY_FILE = os.path.join(MEMORY_DIR, "jarvis_memory.json")

DEFAULT_MEMORY = {
    "user_profile": {
        "title": "sir",
        "name": "",
        "preferences": {},
        "notes": []
    },
    "learned_facts": [],
    "last_interaction": 0.0
}

class MemoryEngine:
    def __init__(self, memory_file: str = MEMORY_FILE):
        self.memory_file = memory_file
        self.db = DatabaseEngine()
        self.data = self._load()

    def _load(self) -> dict:
        """Loads memory from disk or initializes default."""
        if not os.path.exists(MEMORY_DIR):
            os.makedirs(MEMORY_DIR, exist_ok=True)
            
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load memory file: {e}. Reinitializing.")
        
        return DEFAULT_MEMORY.copy()

    def save(self):
        """Persists memory to disk safely."""
        try:
            with open(self.memory_file, "w") as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to persist memory: {e}")

    def remember_fact(self, fact: str):
        """Adds a permanent fact to Jarvis's SQLite database and JSON memory banks."""
        fact = fact.strip()
        if fact:
            if fact not in self.data["learned_facts"]:
                self.data["learned_facts"].append(fact)
                self.save()
            # Also store in SQLite WAL database
            self.db.store_memory(fact, category="fact")
            logger.info(f"🧠 Memory stored: {fact}")

    def set_user_preference(self, key: str, value: str):
        """Stores a specific user preference."""
        self.data["user_profile"]["preferences"][key] = value
        self.save()

    def get_memory_context(self) -> str:
        """Formats learned facts and profile into a natural context string for the prompt."""
        profile = self.data.get("user_profile", {})
        title = profile.get("title", "sir")
        facts = self.data.get("learned_facts", [])
        prefs = profile.get("preferences", {})

        lines = [f"- Addressing user: {title}"]
        if profile.get("name"):
            lines.append(f"- User's Name: {profile['name']}")
        
        for k, v in prefs.items():
            lines.append(f"- User preference ({k}): {v}")

        for f in facts[-15:]:  # Most recent 15 facts
            lines.append(f"- Remembered detail: {f}")

        return "\n".join(lines) if len(lines) > 1 else "No prior history recorded yet."

    def inspect_and_learn(self, user_transcript: str):
        """Passively extracts facts if the user explicitly states something to remember in English or Hindi."""
        lower = user_transcript.lower()
        triggers = [
            "remember that ", "remember this: ", "keep in mind that ", "my name is ", "note that ",
            "yaad rakhna ki ", "yaad rakhna ", "yaad rakho ki ", "mera naam hai ", "mera naam "
        ]
        
        for trigger in triggers:
            if trigger in lower:
                start_idx = lower.find(trigger) + len(trigger)
                fact = user_transcript[start_idx:].strip(". ,")
                if len(fact) > 3:
                    if trigger in ["my name is ", "mera naam hai ", "mera naam "]:
                        self.data["user_profile"]["name"] = fact.title()
                        self.remember_fact(f"User's name is {fact.title()}")
                    else:
                        self.remember_fact(fact)
                    break
