"""Manage PR-level randomization and data persistence."""

import sqlite3
import random
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum
from pathlib import Path


class Arm(Enum):
    """Experimental arm assignment."""
    CI_ONLY = "ci_only"
    CI_CONTRACTS = "ci_contracts"


class TrialManager:
    """Manage PR-level randomization and data persistence."""

    def __init__(self, db_path: str, seed: int = 42):
        """Initialize trial manager."""
        self.db_path = db_path
        random.seed(seed)
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database with schema."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS repositories (
                repo_id TEXT PRIMARY KEY,
                repo_name TEXT NOT NULL,
                stars INTEGER,
                last_commit_date TEXT,
                maturity TEXT CHECK(maturity IN ('high', 'medium'))
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS pr_assignments (
                pr_id TEXT PRIMARY KEY,
                repo_id TEXT,
                pr_number INTEGER,
                arm TEXT CHECK(arm IN ('ci_only', 'ci_contracts')),
                assigned_at TEXT,
                FOREIGN KEY (repo_id) REFERENCES repositories(repo_id)
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS workflow_results (
                run_id TEXT PRIMARY KEY,
                pr_id TEXT,
                started_at TEXT,
                completed_at TEXT,
                ttff_hours REAL,
                failure_stage TEXT CHECK(failure_stage IN ('environment', 'training', 'unknown')),
                error_message TEXT,
                FOREIGN KEY (pr_id) REFERENCES pr_assignments(pr_id)
            )
        ''')
        conn.commit()
        conn.close()

    def register_repository(self, repo_id: str, stars: int) -> None:
        """Register repository in trial."""
        conn = sqlite3.connect(self.db_path)
        maturity = 'high' if stars >= 5000 else 'medium'

        try:
            conn.execute('''
                INSERT INTO repositories (repo_id, repo_name, stars, last_commit_date, maturity)
                VALUES (?, ?, ?, ?, ?)
            ''', (repo_id, repo_id, stars, datetime.now().isoformat(), maturity))
            conn.commit()
        except sqlite3.IntegrityError:
            pass  # Repository already exists
        finally:
            conn.close()

    def assign_pr_to_arm(self, repo_id: str, pr_number: int) -> Arm:
        """Assign PR to experimental arm."""
        existing = self.get_arm_assignment(repo_id, pr_number)
        if existing is not None:
            return existing

        # New assignment: 50/50 split
        pr_id = f'{repo_id}#{pr_number}'
        arm = random.choice([Arm.CI_ONLY, Arm.CI_CONTRACTS])

        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            INSERT INTO pr_assignments (pr_id, repo_id, pr_number, arm, assigned_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (pr_id, repo_id, pr_number, arm.value, datetime.now().isoformat()))
        conn.commit()
        conn.close()

        return arm

    def get_arm_assignment(self, repo_id: str, pr_number: int) -> Optional[Arm]:
        """Retrieve existing PR assignment."""
        pr_id = f'{repo_id}#{pr_number}'
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute('''
            SELECT arm FROM pr_assignments WHERE pr_id = ?
        ''', (pr_id,))
        result = cursor.fetchone()
        conn.close()

        if result:
            return Arm(result[0])
        return None

    def record_workflow_result(
        self,
        pr_id: str,
        ttff: float,
        stage: str,
        started_at: str = None,
        completed_at: str = None,
        error_message: str = None
    ) -> None:
        """Record workflow execution result."""
        run_id = f'{pr_id}_{datetime.now().timestamp()}'

        if started_at is None:
            started_at = datetime.now().isoformat()
        if completed_at is None:
            completed_at = datetime.now().isoformat()

        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            INSERT INTO workflow_results
            (run_id, pr_id, started_at, completed_at, ttff_hours, failure_stage, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (run_id, pr_id, started_at, completed_at, ttff, stage, error_message))
        conn.commit()
        conn.close()

    def get_trial_summary(self) -> Dict:
        """Generate trial summary statistics."""
        conn = sqlite3.connect(self.db_path)

        # Get counts by arm
        cursor = conn.execute('''
            SELECT arm, COUNT(*)
            FROM pr_assignments
            GROUP BY arm
        ''')
        arm_counts = {row[0]: row[1] for row in cursor.fetchall()}

        # Get TTFF stats by arm
        cursor = conn.execute('''
            SELECT pa.arm, AVG(wr.ttff_hours), COUNT(wr.ttff_hours)
            FROM workflow_results wr
            JOIN pr_assignments pa ON wr.pr_id = pa.pr_id
            WHERE wr.ttff_hours IS NOT NULL
            GROUP BY pa.arm
        ''')
        ttff_stats = {row[0]: {'mean_ttff': row[1], 'count': row[2]} for row in cursor.fetchall()}

        # Get stage distribution by arm
        cursor = conn.execute('''
            SELECT pa.arm, wr.failure_stage, COUNT(*)
            FROM workflow_results wr
            JOIN pr_assignments pa ON wr.pr_id = pa.pr_id
            GROUP BY pa.arm, wr.failure_stage
        ''')
        stage_dist = {}
        for row in cursor.fetchall():
            arm, stage, count = row
            if arm not in stage_dist:
                stage_dist[arm] = {}
            stage_dist[arm][stage] = count

        conn.close()

        summary = {
            'arm_counts': arm_counts,
            'ttff_stats': ttff_stats,
            'stage_distribution': stage_dist
        }

        return summary
