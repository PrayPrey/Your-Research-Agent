from datetime import datetime
from typing import List, Dict
from pathlib import Path
from src.clients import HuggingFaceClient
import json


class GroundTruthTracker:
    def __init__(self, hf_client: HuggingFaceClient, output_dir: Path):
        self.hf = hf_client
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def snapshot_dataset_status(self, dataset_ids: List[str], month: int = 0) -> Dict[str, str]:
        snapshot = {}
        for dataset_id in dataset_ids:
            snapshot[dataset_id] = self.hf.get_dataset_status(dataset_id, month)
        return snapshot

    def compute_deprecation_events(
        self,
        month0_snapshot: Dict[str, str],
        month6_snapshot: Dict[str, str]
    ) -> Dict[str, bool]:
        events = {}
        for dataset_id in month0_snapshot.keys():
            was_active = month0_snapshot[dataset_id] == "active"
            is_deprecated = month6_snapshot.get(dataset_id) == "deprecated"
            events[dataset_id] = (was_active and is_deprecated)
        return events

    def save_snapshot(self, snapshot: Dict[str, str], path: str) -> None:
        with open(path, 'w') as f:
            json.dump(snapshot, f, indent=2)
