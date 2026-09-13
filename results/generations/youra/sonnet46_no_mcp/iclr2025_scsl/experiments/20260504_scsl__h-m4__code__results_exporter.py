import json
import os
import numpy as np
from typing import Dict, List
from config import ExperimentConfig


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


class ResultsExporter:
    def __init__(self, cfg: ExperimentConfig):
        self.cfg = cfg
        os.makedirs(cfg.paths.results_dir, exist_ok=True)

    def save_json(
        self,
        results_per_seed: Dict,
        aggregated: Dict,
        correlation_results: Dict,
        gate_result: Dict,
        figure_paths: List[str],
    ) -> str:
        output = {
            "hypothesis_id": "h-m4",
            "results_per_seed": {
                str(seed): {
                    str(epoch): metrics
                    for epoch, metrics in seed_data.items()
                }
                for seed, seed_data in results_per_seed.items()
            },
            "aggregated": {
                str(epoch): metrics
                for epoch, metrics in aggregated.items()
            },
            "correlation": correlation_results,
            "gate": gate_result,
            "figure_paths": figure_paths,
        }
        path = os.path.join(self.cfg.paths.results_dir, "h-m4_results.json")
        with open(path, "w") as f:
            json.dump(output, f, indent=2, cls=NumpyEncoder)
        print(f"Results saved to: {path}")
        return path

    def print_summary(
        self,
        correlation_results: Dict,
        gate_result: Dict,
    ) -> None:
        r = correlation_results.get("pearson_r", 0.0)
        threshold = gate_result.get("threshold", 0.7)
        decision = gate_result.get("decision", "UNKNOWN")
        p_one = correlation_results.get("pearson_p_onetailed", 1.0)

        print("\n" + "=" * 60)
        print("H-M4 GATE RESULT SUMMARY")
        print("=" * 60)
        if gate_result.get("gate_passed"):
            print(f"GATE: PASS (r={r:.4f} > {threshold})")
        else:
            print(f"GATE: LIMITATION (r={r:.4f} <= {threshold})")
        print(f"Pearson r = {r:.4f}, one-tailed p = {p_one:.4f}")
        print(f"Decision: {decision}")
        print(f"Note: {gate_result.get('note', '')}")
        print("=" * 60 + "\n")
