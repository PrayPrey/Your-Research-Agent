"""Ground Truth Generator - h-m4 Module 7"""
import json
import time
from typing import Dict, Any, List
from pathlib import Path


class GroundTruthGenerator:
    """Generate ground truth event log for telemetry validation."""

    def __init__(self, output_path: str = "data/ground_truth_events.json"):
        """
        Initialize generator.

        Args:
            output_path: path to save ground truth log
        """
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.events: List[Dict[str, Any]] = []

    def record_load_event(
        self,
        user_id: str,
        dataset_name: str,
        deprecated: bool,
        successor: str = None,
        group: str = None,
        timestamp: float = None
    ) -> None:
        """
        Record ground truth load event.

        Args:
            user_id: user identifier
            dataset_name: dataset loaded
            deprecated: whether dataset is deprecated
            successor: successor dataset name (if deprecated)
            group: user group (baseline/instrumented)
            timestamp: event timestamp (defaults to current time)
        """
        event = {
            'user_id': user_id,
            'dataset_name': dataset_name,
            'deprecated': deprecated,
            'successor': successor,
            'group': group,
            'timestamp': timestamp if timestamp is not None else time.time()
        }

        self.events.append(event)

    def save_ground_truth(self) -> None:
        """Save ground truth events to file."""
        with open(self.output_path, 'w') as f:
            json.dump(self.events, f, indent=2)

    def load_ground_truth(self) -> List[Dict[str, Any]]:
        """
        Load ground truth events from file.

        Returns:
            list of events
        """
        with open(self.output_path, 'r') as f:
            return json.load(f)

    def compute_expected_events(
        self,
        num_users: int,
        loads_per_user: int,
        deprecated_encounter_rate: float,
        adoption_rate: float
    ) -> Dict[str, int]:
        """
        Compute expected event counts.

        Args:
            num_users: total users
            loads_per_user: loads per user
            deprecated_encounter_rate: % encountering deprecated
            adoption_rate: % adopting successor

        Returns:
            {
                'total_loads': int,
                'deprecated_encounters': int,
                'expected_adoptions': int
            }
        """
        total_loads = num_users * loads_per_user
        deprecated_encounters = int(num_users * deprecated_encounter_rate)
        expected_adoptions = int(deprecated_encounters * adoption_rate)

        return {
            'total_loads': total_loads,
            'deprecated_encounters': deprecated_encounters,
            'expected_adoptions': expected_adoptions
        }
