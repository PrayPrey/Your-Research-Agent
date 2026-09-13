"""EvalPlus wrapper, checkpoint sweep, McNemar's test, gate check."""

import subprocess
import json
import os
import sys
from scipy.stats import chi2

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CONFIG


def run_evalplus(
    checkpoint_path: str,
    dataset: str = "humaneval",
    greedy: bool = True,
) -> dict:
    """Run EvalPlus via subprocess CLI. Returns parsed JSON result dict."""
    cmd = [
        sys.executable, "-m", "evalplus.evaluate",
        "--model", checkpoint_path,
        "--dataset", dataset,
    ]
    if greedy:
        cmd.append("--greedy")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=3600,  # 1 hour timeout
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"EvalPlus failed (exit {result.returncode}): {result.stderr[:500]}"
        )

    return parse_evalplus_output(result.stdout)


def parse_evalplus_output(stdout: str) -> dict:
    """Extract pass@1 (float in [0,1]) from EvalPlus JSON stdout."""
    # EvalPlus outputs JSON with pass@1 scores
    try:
        # Try to find JSON in output
        lines = stdout.strip().split("\n")
        for line in reversed(lines):
            line = line.strip()
            if line.startswith("{"):
                data = json.loads(line)
                # EvalPlus format: {"pass@1": 0.XX, ...}
                pass_at_1 = data.get("pass@1", data.get("pass_at_1", None))
                if pass_at_1 is not None:
                    return {"pass@1": float(pass_at_1), "raw": data}
    except (json.JSONDecodeError, ValueError):
        pass

    # Fallback: search for pass@1 pattern
    import re
    match = re.search(r'"pass@1":\s*([\d.]+)', stdout)
    if match:
        return {"pass@1": float(match.group(1)), "raw": {}}

    raise ValueError(f"Could not parse pass@1 from EvalPlus output: {stdout[:500]}")


def evaluate_all_checkpoints(
    condition: str,
    checkpoint_dir: str,
) -> list:
    """Sweep checkpoints at steps [500,1000,...,5000]. Returns list[{step: int, pass@1: float}]."""
    results = []
    steps = list(range(500, CONFIG["max_steps"] + 1, CONFIG["save_steps"]))

    for step in steps:
        ckpt_path = os.path.join(checkpoint_dir, condition, f"checkpoint-{step}")
        if not os.path.exists(ckpt_path):
            print(f"  Checkpoint not found: {ckpt_path}, skipping")
            continue

        try:
            print(f"  Evaluating {condition} step {step}...")
            result = run_evalplus(ckpt_path, dataset="humaneval", greedy=True)
            results.append({"step": step, "pass@1": result["pass@1"]})
            print(f"    pass@1 = {result['pass@1']:.4f}")
        except Exception as e:
            print(f"  Error evaluating step {step}: {e}")
            results.append({"step": step, "pass@1": None, "error": str(e)})

    return results


def run_mcnemar_test(
    curriculum_results: list,
    uniform_results: list,
) -> tuple:
    """McNemar's test on per-problem binary pass/fail.

    curriculum_results: [164] per-problem bool
    uniform_results:    [164] per-problem bool
    Returns (p_value, effect_size_pp) where effect_size_pp = mean(curriculum) - mean(uniform).
    """
    assert len(curriculum_results) == len(uniform_results), (
        f"Length mismatch: {len(curriculum_results)} vs {len(uniform_results)}"
    )

    # b = curriculum pass, uniform fail
    # c = curriculum fail, uniform pass
    b = sum(1 for c, u in zip(curriculum_results, uniform_results) if c and not u)
    c = sum(1 for c, u in zip(curriculum_results, uniform_results) if not c and u)

    # McNemar statistic with continuity correction
    if (b + c) > 0:
        chi2_stat = (abs(b - c) - 1) ** 2 / (b + c)
    else:
        chi2_stat = 0.0

    # One-tailed p-value (curriculum better than uniform)
    p_value = chi2.sf(chi2_stat, df=1) / 2

    n = len(curriculum_results)
    effect_size_pp = (sum(curriculum_results) / n) - (sum(uniform_results) / n)

    return p_value, effect_size_pp


def gate_check(
    curriculum_pass1: float,
    uniform_pass1: float,
    p_value: float,
) -> bool:
    """Returns True if curriculum_pass1 >= uniform_pass1 + 0.02 and p_value < 0.05."""
    return curriculum_pass1 >= uniform_pass1 + 0.02 and p_value < 0.05


def save_results(
    condition: str,
    results: dict,
    output_dir: str,
) -> None:
    """Write results to {output_dir}/eval_results_{condition}.json."""
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"eval_results_{condition}.json")
    with open(path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {path}")
