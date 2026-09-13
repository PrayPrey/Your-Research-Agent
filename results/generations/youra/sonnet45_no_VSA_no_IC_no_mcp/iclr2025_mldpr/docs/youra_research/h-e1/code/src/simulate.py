from datetime import datetime, timedelta
from typing import List, Dict, Any
import random
import json
from .telemetry import TelemetryLogger

class SimulationGenerator:
    def __init__(
        self,
        telemetry: TelemetryLogger,
        start_date: datetime = None,
        duration_months: int = 6
    ):
        self.telemetry = telemetry
        self.start_date = start_date or datetime.now()
        self.duration_days = duration_months * 30

    def generate_events(self, event_count: int = 100, adoption_rate: float = 0.3) -> List[Dict[str, Any]]:
        events = []
        datasets = ["cifar10", "imdb", "wikitext"]
        successors = {"cifar10": "cifar100", "imdb": "imdb_v2", "wikitext": "wikitext-103"}

        for i in range(event_count):
            days_offset = random.randint(0, self.duration_days)
            timestamp = self.start_date + timedelta(days=days_offset)
            dataset = random.choice(datasets)
            action = "adopt_successor" if random.random() < adoption_rate else "load_deprecated"

            event = {
                'user_hash': self.telemetry.hash_user_id(f"user_{i % 20}"),
                'dataset': dataset,
                'action': action,
                'timestamp': timestamp.isoformat(),
                'successor': successors[dataset] if action == "adopt_successor" else None
            }
            events.append(event)

        return events

    def save_simulation(self, events: List[Dict], path: str):
        with open(path, 'w') as f:
            json.dump(events, f, indent=2)
