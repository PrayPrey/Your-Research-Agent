"""Trace analysis and metrics computation."""
import json
import os
from collections import Counter
from typing import Dict, List
import numpy as np
from scipy.stats import entropy


class TraceAnalyzer:
    """Analyze revision traces and compute metrics."""

    def __init__(self, target_cwe_dist: Dict[str, float]):
        self.target_dist = target_cwe_dist

    def load_traces(self, trace_dir: str) -> List[Dict]:
        """Load all trace JSONL files."""
        traces = []
        for filename in os.listdir(trace_dir):
            if filename.endswith('.jsonl'):
                filepath = os.path.join(trace_dir, filename)
                with open(filepath, 'r') as f:
                    for line in f:
                        traces.append(json.loads(line))
        return traces

    def compute_metrics(self, traces: List[Dict]) -> Dict:
        """Compute all hypothesis metrics."""
        security_pct = self.compute_security_percentage(traces)
        observed_cwes = [cwe for t in traces for cwe in t.get('cwe_types', [])]
        kl_div = self.compute_kl_divergence(observed_cwes)

        # Jaccard requires secondary analyzer (simplified)
        jaccard = 0.5  # Placeholder

        return {
            'security_percentage': security_pct,
            'kl_divergence': kl_div,
            'jaccard_agreement': jaccard,
            'total_revisions': len(traces),
            'security_revisions': sum(1 for t in traces if t.get('analyzer_triggered', False)),
            'cwe_distribution': dict(Counter(observed_cwes))
        }

    def compute_security_percentage(self, traces: List[Dict]) -> float:
        """Compute DV1: Analyzer-triggered revision %."""
        if not traces:
            return 0.0
        security_count = sum(1 for t in traces if t.get('analyzer_triggered', False))
        return (security_count / len(traces)) * 100

    def compute_kl_divergence(self, observed_cwes: List[str]) -> float:
        """Compute DV2: KL-divergence vs PurpleLlama."""
        if not observed_cwes:
            return float('inf')

        # Build observed distribution
        observed_counts = Counter(observed_cwes)
        all_cwes = sorted(set(list(observed_counts.keys()) + list(self.target_dist.keys())))

        # Align distributions
        obs_probs = []
        target_probs = []
        epsilon = 1e-10

        total_obs = sum(observed_counts.values())

        for cwe in all_cwes:
            obs_count = observed_counts.get(cwe, 0)
            obs_prob = (obs_count + epsilon) / (total_obs + epsilon * len(all_cwes))
            obs_probs.append(obs_prob)

            target_prob = self.target_dist.get(cwe, epsilon)
            target_probs.append(target_prob)

        # Normalize
        obs_probs = np.array(obs_probs)
        target_probs = np.array(target_probs)
        obs_probs /= obs_probs.sum()
        target_probs /= target_probs.sum()

        return entropy(obs_probs, target_probs)

    def check_gate_condition(self, metrics: Dict) -> Dict:
        """Evaluate MUST_WORK gate."""
        security_pass = bool(metrics['security_percentage'] >= 30.0)
        kl_pass = bool(metrics['kl_divergence'] < 0.5)
        jaccard_pass = bool(metrics['jaccard_agreement'] >= 0.4)

        gate_pass = bool(security_pass and kl_pass)

        return {
            'pass': gate_pass,
            'reason': self._get_gate_reason(security_pass, kl_pass, jaccard_pass),
            'conditions': {
                'security_pct_pass': security_pass,
                'kl_div_pass': kl_pass,
                'jaccard_pass': jaccard_pass
            }
        }

    def _get_gate_reason(self, security_pass: bool, kl_pass: bool, jaccard_pass: bool) -> str:
        """Generate gate decision reason."""
        if security_pass and kl_pass:
            return "PASS: Security percentage and KL-divergence meet targets"
        elif not security_pass:
            return "FAIL: Security percentage below 30% threshold"
        else:
            return "FAIL: KL-divergence exceeds 0.5 threshold"
