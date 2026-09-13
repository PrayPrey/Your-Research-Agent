from typing import Dict, Tuple, Any
import pandas as pd
import json

class Evaluator:
    def __init__(self, benchmark_csv: str, simulation_json: str):
        self.benchmark_csv = benchmark_csv
        self.simulation_json = simulation_json

    def check_overhead(self) -> Tuple[bool, float]:
        df = pd.read_csv(self.benchmark_csv)
        max_overhead = df['overhead_pct'].max()
        return (max_overhead < 10.0, max_overhead)

    def check_capture_rate(self, telemetry) -> Tuple[bool, float]:
        capture_rate = telemetry.get_capture_rate() * 100
        return (capture_rate >= 95.0, capture_rate)

    def check_event_count(self) -> Tuple[bool, int]:
        with open(self.simulation_json) as f:
            events = json.load(f)
        count = len(events)
        return (count >= 100, count)

    def generate_report(self, telemetry) -> Dict[str, Any]:
        overhead_pass, overhead_max = self.check_overhead()
        capture_pass, capture_rate = self.check_capture_rate(telemetry)
        event_pass, event_count = self.check_event_count()

        gate_status = "PASS" if all([overhead_pass, capture_pass, event_pass]) else "FAIL"

        return {
            'overhead_pass': bool(overhead_pass),
            'overhead_max': float(overhead_max),
            'capture_rate_pass': bool(capture_pass),
            'capture_rate': float(capture_rate),
            'event_count_pass': bool(event_pass),
            'event_count': int(event_count),
            'gate_status': gate_status
        }
