"""Adoption Event Tracker - h-m4 Module 8"""
import sqlite3
from typing import Dict, Any, List
from datetime import timedelta


class AdoptionTracker:
    """Track adoption events (deprecated dataset D → successor S within window)."""

    def __init__(self, db_path: str, adoption_window_days: int = 30):
        """
        Initialize tracker.

        Args:
            db_path: SQLite database path
            adoption_window_days: max days between D and S loads
        """
        self.db_path = db_path
        self.adoption_window_seconds = adoption_window_days * 24 * 3600

    def find_adoption_events(self) -> List[Dict[str, Any]]:
        """
        Find adoption events (D → S within window).

        Returns:
            [
                {
                    'user_id': str,
                    'deprecated_dataset': str,
                    'successor_dataset': str,
                    'deprecated_timestamp': float,
                    'successor_timestamp': float,
                    'time_to_adoption_days': float
                },
                ...
            ]
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
        SELECT
            e1.user_id,
            e1.dataset_name AS deprecated_dataset,
            e1.successor AS successor_dataset,
            e1.timestamp AS deprecated_timestamp,
            e2.timestamp AS successor_timestamp
        FROM events e1
        JOIN events e2
            ON e1.user_id = e2.user_id
            AND e1.successor = e2.dataset_name
        WHERE
            e1.deprecated = 1
            AND e2.deprecated = 0
            AND (e2.timestamp - e1.timestamp) <= ?
            AND (e2.timestamp - e1.timestamp) > 0
        ORDER BY e1.user_id, e1.timestamp
        """

        cursor.execute(query, (self.adoption_window_seconds,))

        adoption_events = []

        for row in cursor.fetchall():
            user_id, deprecated, successor, ts_deprecated, ts_successor = row

            time_to_adoption = (ts_successor - ts_deprecated) / (24 * 3600)  # days

            adoption_events.append({
                'user_id': user_id,
                'deprecated_dataset': deprecated,
                'successor_dataset': successor,
                'deprecated_timestamp': ts_deprecated,
                'successor_timestamp': ts_successor,
                'time_to_adoption_days': time_to_adoption
            })

        conn.close()

        return adoption_events

    def compute_adoption_metrics(
        self,
        ground_truth_adoptions: int
    ) -> Dict[str, Any]:
        """
        Compute adoption tracking metrics.

        Args:
            ground_truth_adoptions: expected adoption events from simulation

        Returns:
            {
                'captured_adoptions': int,
                'expected_adoptions': int,
                'capture_rate': float,
                'median_time_to_adoption_days': float
            }
        """
        adoption_events = self.find_adoption_events()

        captured = len(adoption_events)

        times_to_adoption = [e['time_to_adoption_days'] for e in adoption_events]
        median_time = sorted(times_to_adoption)[len(times_to_adoption) // 2] if times_to_adoption else 0

        capture_rate = captured / ground_truth_adoptions if ground_truth_adoptions > 0 else 0

        return {
            'captured_adoptions': captured,
            'expected_adoptions': ground_truth_adoptions,
            'capture_rate': capture_rate,
            'median_time_to_adoption_days': median_time
        }
