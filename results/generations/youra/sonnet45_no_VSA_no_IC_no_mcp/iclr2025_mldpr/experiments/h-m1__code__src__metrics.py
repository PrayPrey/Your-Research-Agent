import numpy as np
from typing import Dict, List


class HealthMetricsComputer:
    def __init__(
        self,
        velocity_threshold: float = 0.3,
        emergence_threshold: int = 3,
        issue_threshold: float = 0.6
    ):
        self.velocity_threshold = velocity_threshold
        self.emergence_threshold = emergence_threshold
        self.issue_threshold = issue_threshold

    def compute_usage_velocity(self, download_history: List[int]) -> float:
        if len(download_history) < 2:
            return 0.0
        timestamps = np.arange(len(download_history))
        slope, _ = np.polyfit(timestamps, download_history, deg=1)
        return float(slope)

    def compute_successor_emergence(self, successors: List[str]) -> int:
        return len(successors)

    def compute_issue_ratio(self, issues: List[Dict]) -> float:
        if len(issues) == 0:
            return 0.0
        open_count = sum(1 for i in issues if i['state'] == 'open')
        return open_count / len(issues)

    def flag_deprecation_candidate(self, metrics: Dict[str, float]) -> bool:
        score = 0.0
        if metrics['velocity'] < self.velocity_threshold:
            score += 2.0
        if metrics['emergence'] > self.emergence_threshold:
            score += 1.5
        if metrics['issue_ratio'] > self.issue_threshold:
            score += 1.0
        return score >= 2.5

    def compute_all_metrics(
        self,
        download_history: List[int],
        successors: List[str],
        issues: List[Dict]
    ) -> Dict[str, float]:
        velocity = self.compute_usage_velocity(download_history)
        emergence = self.compute_successor_emergence(successors)
        issue_ratio = self.compute_issue_ratio(issues)

        metrics = {
            'velocity': velocity,
            'emergence': emergence,
            'issue_ratio': issue_ratio,
        }
        metrics['flagged'] = self.flag_deprecation_candidate(metrics)
        return metrics
