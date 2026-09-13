import csv
import json
import logging
import os
from typing import Dict, List

import numpy as np

from config import ExperimentConfig

logger = logging.getLogger(__name__)


class ResultsExporter:
    def __init__(self, cfg: ExperimentConfig):
        self.cfg = cfg
        self.results_dir = cfg.paths.results_dir
        os.makedirs(self.results_dir, exist_ok=True)

    def save_json(
        self,
        analysis_results: dict,
        validation_results: dict,
        figure_paths: List[str],
    ) -> str:
        def convert(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            if isinstance(obj, np.floating):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [convert(v) for v in obj]
            return obj

        output = {
            "hypothesis_id": self.cfg.hypothesis_id,
            "gate_passed": validation_results.get("gate_passed"),
            "gate_decision": validation_results.get("gate_decision"),
            "std_t_star": analysis_results.get("std_t_star"),
            "mean_t_star": analysis_results.get("mean_t_star"),
            "ci_95_std": validation_results.get("ci_95_std"),
            "t_star_per_seed": {str(k): v for k, v in analysis_results.get("t_star_per_seed", {}).items()},
            "gap_areas": {str(k): v for k, v in analysis_results.get("gap_areas", {}).items()},
            "mean_gap_area": analysis_results.get("mean_gap_area"),
            "gap_area_ci_95": validation_results.get("gap_area_ci_95"),
            "valid_seed_count": analysis_results.get("valid_seed_count"),
            "used_adaptive_threshold": {str(k): v for k, v in analysis_results.get("used_adaptive_threshold", {}).items()},
            "mechanism_activated": validation_results.get("mechanism_activated"),
            "mechanism_indicators": validation_results.get("mechanism_indicators"),
            "gate_criteria": validation_results.get("gate_criteria"),
            "partial_pass": validation_results.get("partial_pass"),
            "figures": figure_paths,
        }

        path = os.path.join(self.results_dir, "h-m3_results.json")
        with open(path, "w") as f:
            json.dump(convert(output), f, indent=2)
        logger.info(f"Results JSON saved: {path}")
        return path

    def save_csv(
        self,
        delta_curves: Dict[int, np.ndarray],
        checkpoint_interval: int = 2,
    ) -> str:
        path = os.path.join(self.results_dir, "delta_curves.csv")
        seeds = sorted(delta_curves.keys())
        max_len = max(len(c) for c in delta_curves.values())

        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            header = ["checkpoint_idx", "epoch"] + [f"delta_seed{s}" for s in seeds]
            writer.writerow(header)
            for i in range(max_len):
                row = [i, i * checkpoint_interval]
                for s in seeds:
                    curve = delta_curves[s]
                    row.append(float(curve[i]) if i < len(curve) else "")
                writer.writerow(row)

        logger.info(f"Delta curves CSV saved: {path}")
        return path

    def print_summary(self, analysis_results: dict, validation_results: dict) -> None:
        decision = validation_results.get("gate_decision", "UNKNOWN")
        std_t = analysis_results.get("std_t_star")
        mean_t = analysis_results.get("mean_t_star")
        t_per_seed = analysis_results.get("t_star_per_seed", {})
        threshold = validation_results.get("gate_criteria", {}).get("std_gate_threshold", 10.0)
        ci = validation_results.get("ci_95_std")
        mech = validation_results.get("mechanism_activated")

        print("\n" + "=" * 60)
        print(f"H-M3 GATE RESULT: {decision}")
        print("=" * 60)
        print(f"  std(t*) = {std_t:.2f} epochs  (threshold: < {threshold})")
        print(f"  mean(t*) = {mean_t:.2f} epochs")
        if ci:
            print(f"  95% CI for std(t*): [{ci[0]:.2f}, {ci[1]:.2f}]")
        print(f"  t* per seed: { {k: v for k, v in t_per_seed.items()} }")
        print(f"  Mechanism activated: {mech}")
        indic = validation_results.get("mechanism_indicators", {})
        for k, v in indic.items():
            status = "✓" if v else "✗"
            print(f"    {status} {k}: {v}")
        print("=" * 60 + "\n")
