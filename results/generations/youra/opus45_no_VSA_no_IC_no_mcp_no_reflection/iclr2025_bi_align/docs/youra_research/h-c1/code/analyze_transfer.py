"""Transfer analysis for H-C1: Gate computation and IFEval correlation."""
import json
from pathlib import Path
from scipy import stats

from config import MODELS, EVAL, GATE, BASE_DIR


def load_ifeval_results() -> dict[str, float]:
    """Load IFEval strict_accuracy per variant from h-m2 outputs."""
    ifeval_path = Path(BASE_DIR).parent.parent / "h-m2" / "code" / "outputs" / "eval_results.json"
    with open(ifeval_path) as f:
        data = json.load(f)
    return {k: v["strict_accuracy"] for k, v in data.items()}


def compute_gate(safety_results: dict[str, dict]) -> dict:
    """Check if any treatment beats max(baselines) by >=2pp on TruthfulQA OR BBQ."""
    # Max baseline per metric
    max_truthful = max(safety_results[b]["truthfulqa_mc1"] for b in MODELS.baselines)
    max_bbq = max(safety_results[b]["bbq"] for b in MODELS.baselines)

    deltas = {}
    best_ti = None
    best_delta = -float("inf")

    for t in MODELS.treatments:
        delta_truthful = safety_results[t]["truthfulqa_mc1"] - max_truthful
        delta_bbq = safety_results[t]["bbq"] - max_bbq
        deltas[t] = {
            "truthfulqa_mc1": round(delta_truthful, 4),
            "bbq": round(delta_bbq, 4),
        }
        max_delta = max(delta_truthful, delta_bbq)
        if max_delta > best_delta:
            best_delta = max_delta
            best_ti = t

    # Gate passes if ANY treatment exceeds threshold on EITHER metric (OR condition)
    gate_passed = any(
        d["truthfulqa_mc1"] >= GATE.threshold_pp or d["bbq"] >= GATE.threshold_pp
        for d in deltas.values()
    )

    return {
        "max_truthful_baseline": round(max_truthful, 4),
        "max_bbq_baseline": round(max_bbq, 4),
        "deltas": deltas,
        "gate_passed": gate_passed,
        "best_ti": best_ti,
        "threshold_pp": GATE.threshold_pp,
    }


def analyze_transfer(safety_results: dict, ifeval_results: dict) -> dict:
    """Compute Pearson correlation between IFEval and TruthfulQA/BBQ deltas."""
    # Baseline max for IFEval
    ifeval_baseline = max(ifeval_results.get(b, 0) for b in MODELS.baselines)

    # Baseline max for safety metrics
    max_truthful = max(safety_results[b]["truthfulqa_mc1"] for b in MODELS.baselines)
    max_bbq = max(safety_results[b]["bbq"] for b in MODELS.baselines)

    # Compute deltas for treatments
    ifeval_deltas = []
    truthful_deltas = []
    bbq_deltas = []

    for t in MODELS.treatments:
        ifeval_deltas.append(ifeval_results[t] - ifeval_baseline)
        truthful_deltas.append(safety_results[t]["truthfulqa_mc1"] - max_truthful)
        bbq_deltas.append(safety_results[t]["bbq"] - max_bbq)

    # Pearson correlations
    r_truthful, p_truthful = stats.pearsonr(ifeval_deltas, truthful_deltas)
    r_bbq, p_bbq = stats.pearsonr(ifeval_deltas, bbq_deltas)

    return {
        "correlation_truthfulqa": {"r": round(r_truthful, 4), "p": round(p_truthful, 4)},
        "correlation_bbq": {"r": round(r_bbq, 4), "p": round(p_bbq, 4)},
        "ifeval_deltas": {t: round(ifeval_results[t] - ifeval_baseline, 4) for t in MODELS.treatments},
        "truthful_deltas": {t: round(d, 4) for t, d in zip(MODELS.treatments, truthful_deltas)},
        "bbq_deltas": {t: round(d, 4) for t, d in zip(MODELS.treatments, bbq_deltas)},
    }


def run_analysis() -> tuple[dict, dict]:
    """Load results and run full analysis."""
    # Load safety results
    with open(EVAL.results_out_path) as f:
        safety_results = json.load(f)

    # Load IFEval results
    ifeval_results = load_ifeval_results()

    # Compute gate
    gate = compute_gate(safety_results)

    # Compute transfer correlation
    correlation = analyze_transfer(safety_results, ifeval_results)

    # Save correlation analysis
    out_path = Path(EVAL.correlation_out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump({"gate": gate, "correlation": correlation}, f, indent=2)

    print(f"Analysis saved to {out_path}")
    return gate, correlation


if __name__ == "__main__":
    gate, corr = run_analysis()
    print(f"\nGate: {'PASS' if gate['gate_passed'] else 'FAIL'}")
    print(f"Best treatment: {gate['best_ti']}")
    print(f"Deltas: {gate['deltas']}")
    print(f"\nCorrelation (IFEval -> TruthfulQA): r={corr['correlation_truthfulqa']['r']:.4f}")
    print(f"Correlation (IFEval -> BBQ): r={corr['correlation_bbq']['r']:.4f}")
