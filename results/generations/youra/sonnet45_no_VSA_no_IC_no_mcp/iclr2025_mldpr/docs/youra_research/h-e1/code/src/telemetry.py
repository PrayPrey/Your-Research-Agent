import hashlib
import sqlite3
from typing import Dict, Any
from pathlib import Path

class TelemetryLogger:
    def __init__(self, db_path: str = "telemetry.db", opt_in: bool = True):
        self.db_path = Path(db_path)
        self.opt_in = opt_in
        self.total_attempts = 0
        self.successful_logs = 0

        conn = sqlite3.connect(str(self.db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                user_hash TEXT,
                dataset TEXT,
                action TEXT,
                timestamp TEXT
            )
        """)
        conn.commit()
        conn.close()

    def log_event(self, event: Dict[str, Any]) -> bool:
        if not self.opt_in:
            return False

        self.total_attempts += 1
        try:
            user_hash = self.hash_user_id(str(event.get('user_id', 'anonymous')))
            conn = sqlite3.connect(str(self.db_path))
            conn.execute(
                "INSERT INTO events (user_hash, dataset, action, timestamp) VALUES (?, ?, ?, ?)",
                (user_hash, event['dataset'], event['action'], event['timestamp'])
            )
            conn.commit()
            conn.close()
            self.successful_logs += 1
            return True
        except Exception:
            return False

    def hash_user_id(self, user_id: str) -> str:
        return hashlib.sha256(user_id.encode()).hexdigest()[:16]

    def get_capture_rate(self) -> float:
        if self.total_attempts == 0:
            return 0.0
        return self.successful_logs / self.total_attempts
