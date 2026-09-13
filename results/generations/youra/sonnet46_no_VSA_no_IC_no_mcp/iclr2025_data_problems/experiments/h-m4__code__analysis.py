"""
H-M4: Analysis — compare Pearson r and uniform bias between matching conditions.
"""

import json
import numpy as np
from pathlib import Path
from scipy.stats import pearsonr, spearmanr

BENCHMARKS = ["mmlu", "hellaswag", "arc_challenge", "winogrande"]
MODEL_SIZES = ["160m", "410m", "1b", "6.9b"]

CONTAMINATION_ESTIMATES = {
    "mmlu": 0.055,
    "hellaswag": 0.200,
    "arc_challenge": 0.085,
    "winogrande": 0.025,
}


def load_contamination_estimates(hm1_path: str = None) -> dict:
    if hm1_path and Path(hm1_path).exists():
        with open(hm1_path) as f:
            return json.load(f)
    return CONTAMINATION_ESTIMATES


def build_vectors(differentials: dict) -> tuple:
    """
    Flatten 4 benchmarks × 4 model sizes into (16,) arrays.
    Returns (cont_vec, diff_vec).
    """
    cont_vec = []
    diff_vec = []
    for size in MODEL_SIZES:
        for bench in BENCHMARKS:
            cont_vec.append(CONTAMINATION_ESTIMATES[bench])
            diff_vec.append(differentials[size][bench])
    return np.array(cont_vec), np.array(diff_vec)


def bootstrap_ci(x, y, n_boot=10000, seed=42, alpha=0.05):
    rng = np.random.default_rng(seed)
    n = len(x)
    boot_r = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        r, _ = pearsonr(x[idx], y[idx])
        boot_r.append(r)
    boot_r = np.array(boot_r)
    lo = np.percentile(boot_r, 100 * alpha / 2)
    hi = np.percentile(boot_r, 100 * (1 - alpha / 2))
    return (float(lo), float(hi))


def compute_uniform_bias(differentials: dict) -> float:
    """Mean differential across all benchmarks and model sizes."""
    vals = [differentials[size][bench]
            for size in MODEL_SIZES for bench in BENCHMARKS]
    return float(np.mean(vals))


def determine_gate(delta_r: float, bias_delta: float) -> str:
    """
    SHOULD_WORK gate:
    - PASS: token-matched r >= step-matched r (delta_r > 0) AND
             step-matched has more negative bias (bias_delta < 0)
    - ROBUSTNESS_CONFIRMATION: |delta_r| < 0.05 AND |bias_delta| < 0.01
    - PARTIAL: one criterion met
    """
    primary = delta_r > 0
    secondary = bias_delta < 0
    negligible = abs(delta_r) < 0.05 and abs(bias_delta) < 0.01

    if negligible:
        return "ROBUSTNESS_CONFIRMATION"
    if primary and secondary:
        return "PASS"
    if primary or secondary:
        return "PARTIAL"
    return "FAIL"


def run_comparison(aggregated: dict, cont_est: dict = None) -> dict:
    """
    Compute r_token_matched vs r_step_matched, delta_r, bias_delta, gate verdict.
    """
    if cont_est is None:
        cont_est = CONTAMINATION_ESTIMATES

    token_diffs = aggregated["token_matched"]
    step_diffs = aggregated["step_matched"]

    cont_t, diff_t = build_vectors(token_diffs)
    cont_s, diff_s = build_vectors(step_diffs)

    r_token, p_token = pearsonr(cont_t, diff_t)
    rho_token, prho_token = spearmanr(cont_t, diff_t)
    ci_token = bootstrap_ci(cont_t, diff_t)

    r_step, p_step = pearsonr(cont_s, diff_s)
    rho_step, prho_step = spearmanr(cont_s, diff_s)
    ci_step = bootstrap_ci(cont_s, diff_s)

    delta_r = float(r_token - r_step)

    bias_token = compute_uniform_bias(token_diffs)
    bias_step = compute_uniform_bias(step_diffs)
    bias_delta = float(bias_step - bias_token)

    gate = determine_gate(delta_r, bias_delta)

    return {
        "r_token_matched": float(r_token),
        "p_token_matched": float(p_token),
        "rho_token_matched": float(rho_token),
        "p_rho_token_matched": float(prho_token),
        "ci_token_matched": list(ci_token),
        "r_step_matched": float(r_step),
        "p_step_matched": float(p_step),
        "rho_step_matched": float(rho_step),
        "p_rho_step_matched": float(prho_step),
        "ci_step_matched": list(ci_step),
        "delta_r": delta_r,
        "uniform_bias_token": bias_token,
        "uniform_bias_step": bias_step,
        "bias_delta": bias_delta,
        "n_observations": 16,
        "gate_verdict": gate,
        "gate_type": "SHOULD_WORK",
        "contamination_estimates": cont_est,
    }


if __name__ == "__main__":
    base = Path(__file__).parent.parent
    agg_path = base / "results/aggregated_differentials.json"

    with open(agg_path) as f:
        aggregated = json.load(f)

    results = run_comparison(aggregated)

    print(f"r_token_matched = {results['r_token_matched']:.4f} (p={results['p_token_matched']:.4f})")
    print(f"r_step_matched  = {results['r_step_matched']:.4f} (p={results['p_step_matched']:.4f})")
    print(f"delta_r         = {results['delta_r']:.4f}")
    print(f"bias_token      = {results['uniform_bias_token']:.6f}")
    print(f"bias_step       = {results['uniform_bias_step']:.6f}")
    print(f"bias_delta      = {results['bias_delta']:.6f}")
    print(f"Gate verdict    = {results['gate_verdict']}")

    out = base / "results/correlation_comparison.json"
    with open(out, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved: {out}")
