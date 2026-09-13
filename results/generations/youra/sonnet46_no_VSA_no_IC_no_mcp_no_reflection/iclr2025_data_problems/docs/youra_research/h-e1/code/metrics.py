"""FR-4/5: Metric computation — ratio, bootstrap CI, Cohen's d, pass/fail verdict."""
import numpy as np
from config import (
    BOOTSTRAP_N, SEED,
    RATIO_THRESHOLD, P_THRESHOLD, COHENS_D_THRESHOLD,
)


def compute_ratio(results: dict[str, dict]) -> float:
    """Return mean(MMLU subject acc) / HellaSwag acc."""
    mmlu_keys = [k for k in results if k.startswith("mmlu_")]
    if not mmlu_keys:
        raise ValueError("No MMLU subject keys found in results")

    mmlu_accs = [results[k]["acc,none"] for k in mmlu_keys]
    mmlu_mean = np.mean(mmlu_accs)

    hellaswag_acc = results["hellaswag"]["acc,none"]
    if hellaswag_acc == 0.0:
        raise ZeroDivisionError("HellaSwag acc=0.0 — evaluation likely failed")

    return float(mmlu_mean / hellaswag_acc)


def compute_arc_delta(results: dict[str, dict]) -> float:
    """Return arc_challenge acc_norm - arc_easy acc."""
    return float(
        results["arc_challenge"]["acc_norm,none"] - results["arc_easy"]["acc,none"]
    )


def bootstrap_ratio_diff(
    pythia_results: dict[str, dict],
    olmo_results: dict[str, dict],
    n: int = BOOTSTRAP_N,
    seed: int = SEED,
) -> dict:
    """Bootstrap CI over MMLU-subject resampling for ratio difference (OLMo - Pythia)."""
    rng = np.random.default_rng(seed)

    pythia_mmlu = np.array([k for k in pythia_results if k.startswith("mmlu_")])
    olmo_mmlu_set = {k for k in olmo_results if k.startswith("mmlu_")}
    common_keys = np.array([k for k in pythia_mmlu if k in olmo_mmlu_set])

    if len(common_keys) < 50:
        raise ValueError(
            f"Only {len(common_keys)} common MMLU keys between models (expected ≥50)"
        )

    hellaswag_p = pythia_results["hellaswag"]["acc,none"]
    hellaswag_o = olmo_results["hellaswag"]["acc,none"]

    diffs = []
    for _ in range(n):
        sample_keys = rng.choice(common_keys, size=len(common_keys), replace=True)
        p_mmlu = np.mean([pythia_results[k]["acc,none"] for k in sample_keys])
        o_mmlu = np.mean([olmo_results[k]["acc,none"] for k in sample_keys])
        p_ratio = p_mmlu / hellaswag_p
        o_ratio = o_mmlu / hellaswag_o
        diffs.append(float(o_ratio - p_ratio))

    diffs_arr = np.array(diffs)
    return {
        "mean_diff": float(np.mean(diffs_arr)),
        "ci_95": [float(np.percentile(diffs_arr, 2.5)), float(np.percentile(diffs_arr, 97.5))],
        "p_value": float(np.mean(diffs_arr <= 0)),
        "bootstrap_diffs": diffs,
    }


def cohens_d(bootstrap_diffs: list[float]) -> float:
    """Bootstrap-based Cohen's d = mean(diffs) / std(diffs)."""
    arr = np.array(bootstrap_diffs)
    std = np.std(arr, ddof=1)
    if std == 0.0:
        return float("inf")
    return float(np.mean(arr) / std)


def evaluate_hypothesis(
    pythia_results: dict[str, dict],
    olmo_results: dict[str, dict],
    ratio_threshold: float = RATIO_THRESHOLD,
    p_threshold: float = P_THRESHOLD,
    d_threshold: float = COHENS_D_THRESHOLD,
) -> dict:
    """Compute all metrics and return verdict dict."""
    p_ratio = compute_ratio(pythia_results)
    o_ratio = compute_ratio(olmo_results)
    ratio_diff = o_ratio - p_ratio

    p_arc = compute_arc_delta(pythia_results)
    o_arc = compute_arc_delta(olmo_results)

    boot = bootstrap_ratio_diff(pythia_results, olmo_results)
    d = cohens_d(boot["bootstrap_diffs"])

    primary_pass = (
        boot["mean_diff"] > ratio_threshold
        and boot["p_value"] < p_threshold
        and d > d_threshold
    )
    secondary_pass = o_arc > p_arc

    verdict = "CONFIRMED" if primary_pass else "FAILED"

    # Report p < 0.001 when p_value is 0.0 (all bootstrap diffs > 0)
    p_display = boot["p_value"] if boot["p_value"] > 0 else "<0.001"

    evidence = (
        f"OLMo ratio={o_ratio:.4f}, Pythia ratio={p_ratio:.4f}, "
        f"diff={boot['mean_diff']:.4f} (95% CI [{boot['ci_95'][0]:.4f}, {boot['ci_95'][1]:.4f}]), "
        f"p={p_display}, d={d:.3f}. "
        f"Primary: {'PASS' if primary_pass else 'FAIL'}. "
        f"ARC delta: OLMo={o_arc:.4f}, Pythia={p_arc:.4f} ({'PASS' if secondary_pass else 'FAIL'})."
    )

    return {
        "pythia_ratio": p_ratio,
        "olmo_ratio": o_ratio,
        "ratio_diff": ratio_diff,
        "arc_delta_pythia": p_arc,
        "arc_delta_olmo": o_arc,
        "bootstrap": boot,
        "cohens_d": d,
        "primary_pass": primary_pass,
        "secondary_pass": secondary_pass,
        "verdict": verdict,
        "evidence": evidence,
    }
