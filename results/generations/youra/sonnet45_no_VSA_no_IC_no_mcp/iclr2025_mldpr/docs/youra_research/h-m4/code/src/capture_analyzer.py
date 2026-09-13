"""Capture Rate Analyzer - h-m4 Module 9"""
import sqlite3
from typing import Dict, Any
from statsmodels.stats.proportion import proportion_confint


class CaptureRateAnalyzer:
    """Analyze telemetry capture rate with Wilson score confidence interval."""

    def __init__(self, db_path: str):
        """
        Initialize analyzer.

        Args:
            db_path: SQLite database path
        """
        self.db_path = db_path

    def compute_capture_rate(self, expected_events: int) -> Dict[str, Any]:
        """
        Compute capture rate with Wilson CI.

        Args:
            expected_events: total expected events from simulation

        Returns:
            {
                'captured': int,
                'expected': int,
                'rate': float,
                'ci_low': float,
                'ci_high': float
            }
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        captured = cursor.execute("SELECT COUNT(*) FROM events").fetchone()[0]

        conn.close()

        rate = captured / expected_events if expected_events > 0 else 0

        # Wilson score interval
        ci_low, ci_high = proportion_confint(
            captured,
            expected_events,
            alpha=0.05,
            method='wilson'
        )

        return {
            'captured': captured,
            'expected': expected_events,
            'rate': rate,
            'ci_low': ci_low,
            'ci_high': ci_high
        }

    def compute_completeness(self) -> float:
        """
        Compute event trail completeness (% events with full context).

        Returns:
            completeness rate (0-1)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        total = cursor.execute("SELECT COUNT(*) FROM events").fetchone()[0]

        complete = cursor.execute("""
            SELECT COUNT(*) FROM events
            WHERE user_id IS NOT NULL
              AND timestamp IS NOT NULL
              AND dataset_name IS NOT NULL
        """).fetchone()[0]

        conn.close()

        return complete / total if total > 0 else 0

    def verify_gate_criteria(
        self,
        expected_events: int,
        min_capture_rate: float = 0.95
    ) -> Dict[str, Any]:
        """
        Verify SHOULD_WORK gate criteria.

        Args:
            expected_events: total expected events
            min_capture_rate: minimum required capture rate (default 0.95 = 95%)

        Returns:
            {
                'gate_satisfied': bool,
                'capture_rate': float,
                'ci_low': float,
                'ci_high': float,
                'completeness': float,
                'passed_checks': [str],
                'failed_checks': [str]
            }
        """
        metrics = self.compute_capture_rate(expected_events)
        completeness = self.compute_completeness()

        passed = []
        failed = []

        # Check 1: Capture rate ≥ 95%
        if metrics['ci_low'] >= min_capture_rate:
            passed.append(f"Capture rate CI lower bound ({metrics['ci_low']:.2%}) ≥ {min_capture_rate:.0%}")
        else:
            failed.append(f"Capture rate CI lower bound ({metrics['ci_low']:.2%}) < {min_capture_rate:.0%}")

        # Check 2: Completeness ≥ 95%
        if completeness >= 0.95:
            passed.append(f"Event completeness ({completeness:.2%}) ≥ 95%")
        else:
            failed.append(f"Event completeness ({completeness:.2%}) < 95%")

        gate_satisfied = len(failed) == 0

        return {
            'gate_satisfied': gate_satisfied,
            'capture_rate': metrics['rate'],
            'ci_low': metrics['ci_low'],
            'ci_high': metrics['ci_high'],
            'completeness': completeness,
            'passed_checks': passed,
            'failed_checks': failed
        }
