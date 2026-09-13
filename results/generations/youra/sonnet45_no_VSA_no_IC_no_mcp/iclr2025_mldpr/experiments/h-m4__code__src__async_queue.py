"""Async Telemetry Queue - h-m4 Module 1"""
import asyncio
from queue import Queue, Full
from typing import Dict, Any, List, Optional
import sqlite3
import time
from pathlib import Path


class AsyncTelemetryQueue:
    """Non-blocking telemetry queue with async batch flushing."""

    def __init__(
        self,
        db_path: str,
        batch_size: int = 100,
        flush_interval: float = 5.0
    ):
        """
        Initialize queue.

        Args:
            db_path: SQLite database path
            batch_size: events per batch write
            flush_interval: seconds between flushes
        """
        self.db_path = db_path
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.queue: Queue = Queue(maxsize=10000)
        self.flush_task: Optional[asyncio.Task] = None
        self._running = False

        # Ensure DB directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        # Initialize DB schema
        self._init_db()

    def _init_db(self) -> None:
        """Create events table with WAL mode."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                dataset_name TEXT NOT NULL,
                deprecated INTEGER NOT NULL,
                successor TEXT,
                user_group TEXT NOT NULL,
                timestamp REAL NOT NULL,
                latency_ms REAL,
                memory_delta_mb REAL,
                cpu_percent REAL,
                created_at REAL NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON events(user_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_dataset ON events(dataset_name)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON events(timestamp)")
        conn.commit()
        conn.close()

    async def start(self) -> None:
        """Start background flush task."""
        if self._running:
            return

        self._running = True
        self.flush_task = asyncio.create_task(self._background_flush())

    async def stop(self) -> None:
        """Flush remaining events and stop."""
        self._running = False

        if self.flush_task:
            self.flush_task.cancel()
            try:
                await self.flush_task
            except asyncio.CancelledError:
                pass

        # Final flush
        self._flush_all()

    def put(self, event: Dict[str, Any]) -> bool:
        """
        Non-blocking queue insert.

        Args:
            event: {user_id, dataset_name, deprecated, successor, user_group, timestamp, ...}

        Returns:
            True if queued, False if full
        """
        try:
            self.queue.put_nowait(event)
            return True
        except Full:
            return False

    async def _background_flush(self) -> None:
        """Periodic batch write to DB."""
        while self._running:
            await asyncio.sleep(self.flush_interval)
            self._flush_batch()

    def _flush_batch(self) -> None:
        """Write one batch from queue."""
        batch = []
        try:
            while len(batch) < self.batch_size:
                batch.append(self.queue.get_nowait())
        except:
            pass  # Queue empty

        if batch:
            self._write_batch(batch)

    def _flush_all(self) -> None:
        """Flush all remaining events."""
        while not self.queue.empty():
            self._flush_batch()

    def _write_batch(self, events: List[Dict[str, Any]]) -> None:
        """
        Write batch with WAL mode.

        Args:
            events: [{user_id, dataset_name, timestamp, ...}]
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        created_at = time.time()

        for event in events:
            cursor.execute("""
                INSERT INTO events (
                    user_id, dataset_name, deprecated, successor, user_group,
                    timestamp, latency_ms, memory_delta_mb, cpu_percent, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.get('user_id'),
                event.get('dataset_name'),
                1 if event.get('deprecated') else 0,
                event.get('successor'),
                event.get('user_group'),
                event.get('timestamp'),
                event.get('latency_ms'),
                event.get('memory_delta_mb'),
                event.get('cpu_percent'),
                created_at
            ))

        conn.commit()
        conn.close()
