"""
CheckpointLogger - Logging and loading utilities for Phase 1 checkpoints
Task: A-3
Hypothesis: h-m1
"""

import os
import json
import csv
from typing import Dict, List, Any
from datetime import datetime


class CheckpointLogger:
    """
    Manages checkpoint logging for Phase 1 analysis.

    Saves:
    - Weight trajectories (CSV): progress, exec_w, ai_w, human_w
    - Pass@1 trajectories (CSV): progress, pass_at_1
    - Full checkpoint data (JSON): all metrics and state
    """

    def __init__(self, checkpoint_dir: str):
        """
        Args:
            checkpoint_dir: Directory to save checkpoint files
        """
        self.checkpoint_dir = checkpoint_dir
        os.makedirs(checkpoint_dir, exist_ok=True)

        # File paths
        self.weights_csv = os.path.join(checkpoint_dir, "weights_phase1.csv")
        self.pass_at_1_csv = os.path.join(checkpoint_dir, "pass_at_1_trajectory.csv")

        # Initialize CSV files
        self._init_csv_files()

    def _init_csv_files(self):
        """Initialize CSV files with headers."""
        # Weights CSV
        if not os.path.exists(self.weights_csv):
            with open(self.weights_csv, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['progress', 'execution_weight', 'ai_weight', 'human_weight', 'timestamp'])

        # Pass@1 CSV
        if not os.path.exists(self.pass_at_1_csv):
            with open(self.pass_at_1_csv, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['progress', 'pass_at_1', 'timestamp'])

    def log_weights(self, progress: float, exec_w: float, ai_w: float, human_w: float):
        """
        Log weight checkpoint to CSV.

        Args:
            progress: Training progress [0, 1]
            exec_w: Execution weight
            ai_w: AI weight
            human_w: Human weight
        """
        timestamp = datetime.now().isoformat()

        with open(self.weights_csv, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([progress, exec_w, ai_w, human_w, timestamp])

    def log_pass_at_1(self, progress: float, pass_at_1: float):
        """
        Log pass@1 metric to CSV.

        Args:
            progress: Training progress [0, 1]
            pass_at_1: Pass@1 score
        """
        timestamp = datetime.now().isoformat()

        with open(self.pass_at_1_csv, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([progress, pass_at_1, timestamp])

    def save_full_checkpoint(self, progress: float, data: Dict[str, Any]):
        """
        Save full checkpoint with all metrics to JSON.

        Args:
            progress: Training progress [0, 1]
            data: Dictionary with all checkpoint data
        """
        progress_int = int(progress * 100)
        checkpoint_path = os.path.join(self.checkpoint_dir, f"progress_{progress_int:03d}.json")

        checkpoint = {
            'progress': progress,
            'timestamp': datetime.now().isoformat(),
            **data
        }

        with open(checkpoint_path, 'w') as f:
            json.dump(checkpoint, f, indent=2)

        print(f"✓ Checkpoint saved: {checkpoint_path}")

    def load_all_checkpoints(self) -> Dict[float, Dict[str, Any]]:
        """
        Load all checkpoint JSON files.

        Returns:
            Dictionary mapping progress -> checkpoint data
        """
        checkpoints = {}

        for filename in os.listdir(self.checkpoint_dir):
            if filename.startswith('progress_') and filename.endswith('.json'):
                filepath = os.path.join(self.checkpoint_dir, filename)

                with open(filepath, 'r') as f:
                    data = json.load(f)
                    checkpoints[data['progress']] = data

        return checkpoints

    def load_weights_trajectory(self) -> List[Dict[str, float]]:
        """
        Load weight trajectory from CSV.

        Returns:
            List of {progress, execution_weight, ai_weight, human_weight}
        """
        trajectory = []

        with open(self.weights_csv, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                trajectory.append({
                    'progress': float(row['progress']),
                    'execution_weight': float(row['execution_weight']),
                    'ai_weight': float(row['ai_weight']),
                    'human_weight': float(row['human_weight'])
                })

        return trajectory

    def load_pass_at_1_trajectory(self) -> List[Dict[str, float]]:
        """
        Load pass@1 trajectory from CSV.

        Returns:
            List of {progress, pass_at_1}
        """
        trajectory = []

        with open(self.pass_at_1_csv, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                trajectory.append({
                    'progress': float(row['progress']),
                    'pass_at_1': float(row['pass_at_1'])
                })

        return trajectory
