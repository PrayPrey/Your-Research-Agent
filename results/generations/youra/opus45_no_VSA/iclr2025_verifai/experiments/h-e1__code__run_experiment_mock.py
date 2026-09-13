#!/usr/bin/env python3
"""Mock experiment runner for H-E1 PoC validation (no API key required).

Simulates the experiment flow with synthetic results to validate:
1. Pipeline structure works
2. Metrics calculation is correct
3. Output artifacts are generated properly

For real experiment, use run_experiment.py with OPENAI_API_KEY set.
"""
import json
import sys
from datetime import datetime
from pathlib import Path
import numpy as np
from config import ExperimentConfig
from repair_loop import IterationLog
from metrics import pass_at_1, relative_improvement, bootstrap_ci, mcnemar_test


def generate_mock_logs(n_problems: int, seed: int) -> list:
    """Generate synthetic iteration logs that simulate expected effect."""
    rng = np.random.default_rng(seed)
    logs = []

    for i in range(n_problems):
        problem_id = f"problem_{i}"
        # Simulate: condition A (static->exec) has ~55% pass rate
        # condition B (exec->static) has ~45% pass rate
        # This gives ~22% relative improvement ((0.55-0.45)/0.45 * 100)

        pass_a = rng.random() < 0.55
        pass_b = rng.random() < 0.45

        # Add logs for both conditions (final iteration only for simplicity)
        logs.append(IterationLog(
            problem_id=problem_id,
            condition="A",
            iteration=3,  # final iteration
            code="# mock code",
            passed=pass_a,
            static_fb="mock static feedback",
            exec_fb="mock exec feedback",
        ))
        logs.append(IterationLog(
            problem_id=problem_id,
            condition="B",
            iteration=3,
            code="# mock code",
            passed=pass_b,
            static_fb="mock static feedback",
            exec_fb="mock exec feedback",
        ))

    return logs


def main():
    print(f"[{datetime.now().isoformat()}] Starting H-E1 MOCK experiment (PoC validation)")
    print("NOTE: This is a mock run. Set OPENAI_API_KEY for real experiment.")
    print()

    cfg = ExperimentConfig()
    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)

    # Generate mock data (664 problems = HumanEval + MBPP)
    n_problems = 664
    print(f"Generating mock data for {n_problems} problems...")
    logs = generate_mock_logs(n_problems, cfg.seed)
    print(f"Generated {len(logs)} iteration logs")

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
        "mode": "MOCK_POC",
        "n_problems": n_problems,
        "pass_at_1_A": float(pa),
        "pass_at_1_B": float(pb),
        "relative_improvement_pct": float(rel_imp),
        "ci_95_lower": float(ci_low),
        "ci_95_upper": float(ci_high),
        "mcnemar_p_value": float(p_val),
        "gate_15pct_pass": bool(rel_imp >= 15),
        "gate_ci_10pct_pass": bool(ci_low > 10),
    }

    # Save metrics
    metrics_path = results_dir / "h-e1_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Saved metrics to {metrics_path}")

    # Print summary
    print("\n" + "=" * 50)
    print("H-E1 MOCK RESULTS (PoC Validation)")
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
    print()
    print("PoC validation: Pipeline structure verified.")
    print("For real experiment results, run with OPENAI_API_KEY.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
