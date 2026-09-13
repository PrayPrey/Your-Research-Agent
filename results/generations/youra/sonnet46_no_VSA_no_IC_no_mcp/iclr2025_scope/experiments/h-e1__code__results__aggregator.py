import json
import os
import logging
import numpy as np

from evaluation.bootstrap import bootstrap_delta
from evaluation.metrics import macro_f1

logger = logging.getLogger(__name__)


def build_results_json(
    raw: dict,
    cfg,
    output_path: str = None,
) -> dict:
    tasks = cfg.tasks
    n_per_task = cfg.examples_per_task

    per_method = {}
    for method, task_results in raw.items():
        per_method[method] = {}
        for task, f1_list in task_results.items():
            per_method[method][task] = float(np.mean(f1_list)) if f1_list else 0.0
        per_method[method]["macro_f1"] = float(macro_f1(task_results))

    # Bootstrap on M1 vs M2
    m1_flat = [f1 for t in tasks for f1 in raw["M1"][t]]
    m2_flat = [f1 for t in tasks for f1 in raw["M2"][t]]

    boot = bootstrap_delta(m1_flat, m2_flat, tasks, n_per_task, cfg.n_bootstrap, cfg.bootstrap_seed)

    gate_pass = (boot["delta"] >= cfg.gate_threshold) and (boot["ci_lower"] > 0)

    results = {
        "hypothesis_id": "H-E1",
        "per_method": per_method,
        "gate_check": {
            "m1_minus_m2": round(boot["delta"], 4),
            "bootstrap_ci_lower": round(boot["ci_lower"], 4),
            "bootstrap_ci_upper": round(boot["ci_upper"], 4),
            "gate_pass": gate_pass,
        },
        "bootstrap_samples": boot["samples"].tolist(),
    }

    if output_path is None:
        output_path = os.path.join(cfg.output_dir, cfg.results_file)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save without bootstrap_samples in main file (too large)
    save_results = {k: v for k, v in results.items() if k != "bootstrap_samples"}
    with open(output_path, "w") as f:
        json.dump(save_results, f, indent=2)
    logger.info(f"Results saved to {output_path}")

    return results
