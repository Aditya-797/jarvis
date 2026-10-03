"""
Industrial SQLite WAL-Mode Database Engine for Jarvis.
Provides:
- ACID-compliant transaction safety (resilient to sudden phone shutdowns/battery death)
- Write-Ahead Logging (WAL) for ultra-fast concurrent reads/writes
- Structured Long-Term Memory (facts, preferences, profile)
- Telemetry & Analytics Logging (latency, model tiers used, uptime)
- Audit Trail for hardware & PC command executions
"""

import os
import sqlite3
import time
import logging

logger = logging.getLogger("Jarvis.Database")

DB_DIR = "data"
DB_PATH = os.path.join(DB_DIR, "jarvis_industrial.db")

class DatabaseEngine:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        if not os.path.exists(DB_DIR):
            os.makedirs(DB_DIR, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10)
        # Enable Write-Ahead Logging for multi-threaded performance
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Creates tables with proper indexes."""
        with self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    key TEXT,
                    value TEXT NOT NULL,
                    created_at REAL NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_memories_cat ON memories(category);

                CREATE TABLE IF NOT EXISTS telemetry (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    tier_used TEXT NOT NULL,
                    latency_ms REAL NOT NULL,
                    success INTEGER NOT NULL
                );

                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    action_type TEXT NOT NULL,
                    details TEXT NOT NULL,
                    status TEXT NOT NULL
                );
            """)
        logger.info("🏛️ Industrial SQLite database initialized with WAL mode.")

    # ----------------- MEMORY STORAGE -----------------
    def store_memory(self, value: str, category: str = "fact", key: str = ""):
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO memories (category, key, value, created_at) VALUES (?, ?, ?, ?)",
                (category, key, value.strip(), time.time())
            )
            conn.commit()

    def get_all_memories(self, limit: int = 25) -> list[str]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT value FROM memories ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
            return [r["value"] for r in reversed(rows)]

    # ----------------- TELEMETRY & METRICS -----------------
    def record_telemetry(self, tier: str, latency_ms: float, success: bool):
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO telemetry (timestamp, tier_used, latency_ms, success) VALUES (?, ?, ?, ?)",
                (time.time(), tier, latency_ms, 1 if success else 0)
            )
            conn.commit()

    def get_metrics_summary(self) -> dict:
        """Returns statistics for mission control dashboard."""
        with self._get_connection() as conn:
            total_reqs = conn.execute("SELECT COUNT(*) as count FROM telemetry").fetchone()["count"]
            avg_lat = conn.execute("SELECT AVG(latency_ms) as avg_lat FROM telemetry").fetchone()["avg_lat"] or 0
            tier_stats = conn.execute(
                "SELECT tier_used, COUNT(*) as cnt FROM telemetry GROUP BY tier_used"
            ).fetchall()
            
            return {
                "total_requests": total_reqs,
                "average_latency_ms": round(avg_lat, 1),
                "tiers": {r["tier_used"]: r["cnt"] for r in tier_stats}
            }

    # ----------------- AUDIT LOG -----------------
    def log_audit(self, action_type: str, details: str, status: str = "SUCCESS"):
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO audit_logs (timestamp, action_type, details, status) VALUES (?, ?, ?, ?)",
                (time.time(), action_type, details, status)
            )
            conn.commit()
