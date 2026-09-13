#!/usr/bin/env python3
"""Main experiment runner for H-E1 (Feedback Ordering Effect)."""
import json
import sys
from datetime import datetime
from pathlib import Path
from config import ExperimentConfig
from data import load_problems
from repair_loop import run_all
from metrics import pass_at_1, relative_improvement, bootstrap_ci, mcnemar_test


def main():
    print(f"[{datetime.now().isoformat()}] Starting H-E1 experiment")

    cfg = ExperimentConfig()
    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)

    # Load data
    print(f"[{datetime.now().isoformat()}] Loading problems...")
    problems = load_problems(cfg.seed)
    print(f"Loaded {len(problems)} problems")

    # Run experiment
    print(f"[{datetime.now().isoformat()}] Running repair loop...")
    logs = run_all(problems, cfg)
    print(f"Collected {len(logs)} iteration logs")

    # Save iteration logs
    logs_path = results_dir / "h-e1_iteration_logs.jsonl"
    with open(logs_path, "w") as f:
        for log in logs:
            f.write(json.dumps(log.to_dict()) + "\n")
    print(f"Saved logs to {logs_path}")

    # Compute metrics
    print(f"[{datetime.now().isoformat()}] Computing metrics...")
    pa = pass_at_1(logs, "A")
    pb = pass_at_1(logs, "B")
    rel_imp = relative_improvement(pa, pb)
    ci_low, ci_high = bootstrap_ci(logs, cfg.bootstrap_resamples, cfg.seed)
    p_val = mcnemar_test(logs)

    metrics = {
        "hypothesis": "h-e1",
        "timestamp": datetime.now().isoformat(),
        "n_problems": len(problems),
        "pass_at_1_A": pa,
        "pass_at_1_B": pb,
        "relative_improvement_pct": rel_imp,
        "ci_95_lower": ci_low,
        "ci_95_upper": ci_high,
        "mcnemar_p_value": p_val,
        "gate_15pct_pass": rel_imp >= 15,
        "gate_ci_10pct_pass": ci_low > 10,
    }

    # Save metrics
    metrics_path = results_dir / "h-e1_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Saved metrics to {metrics_path}")

    # Print summary
    print("\n" + "=" * 50)
    print("H-E1 RESULTS")
    print("=" * 50)
    print(f"pass@1 (A: static->exec): {pa:.4f}")
    print(f"pass@1 (B: exec->static): {pb:.4f}")
    print(f"Relative improvement: {rel_imp:.2f}%")
    print(f"95% CI: [{ci_low:.2f}%, {ci_high:.2f}%]")
    print(f"McNemar p-value: {p_val:.4f}")
    print()
    print(f"GATE (rel_imp >= 15%): {'PASS' if metrics['gate_15pct_pass'] else 'FAIL'}")
    print(f"GATE (CI lower > 10%): {'PASS' if metrics['gate_ci_10pct_pass'] else 'FAIL'}")
    print("=" * 50)

    return 0 if metrics["gate_15pct_pass"] and metrics["gate_ci_10pct_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
