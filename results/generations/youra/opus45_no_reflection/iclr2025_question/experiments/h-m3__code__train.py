"""H-M3 Train Orchestrator: End-to-end pipeline"""
import json
import sys
from pathlib import Path
from datetime import datetime

from config import HM3Config
from data import load_hidden_states, scale_features
from probe import LinearCorrectnessProbe, MLPFallbackProbe, compute_baseline_ci
from evaluate import compute_metrics, verify_mechanism, compare_to_baseline
from visualize import plot_gate_comparison, plot_roc_curve


def main(hypothesis_folder: str) -> dict:
    """Run full H-M3 pipeline."""
    config = HM3Config()
    hyp_path = Path(hypothesis_folder)
    cache_folder = str(hyp_path / config.h_m1_cache_folder)

    print(f"[H-M3] Loading hidden states from {cache_folder}")
    X_train, y_train, X_val, y_val = load_hidden_states(cache_folder)
    print(f"  Train: {X_train.shape}, Val: {X_val.shape}")

    print("[H-M3] Scaling features...")
    X_train_s, X_val_s, scaler = scale_features(X_train, X_val)

    print("[H-M3] Computing random baseline (5 seeds)...")
    baseline_stats = compute_baseline_ci(X_val_s, y_val, config.d_model, config.baseline_n_seeds, config.seed)
    print(f"  Baseline AUROC: {baseline_stats['mean']:.4f} ± {baseline_stats['std']:.4f}")

    print(f"[H-M3] Training linear probe (C={config.probe_C}, max_iter={config.probe_max_iter})...")
    probe = LinearCorrectnessProbe(C=config.probe_C, max_iter=config.probe_max_iter)
    probe.fit(X_train_s, y_train)
    n_iter = probe.clf.n_iter_[0] if hasattr(probe.clf, "n_iter_") else config.probe_max_iter
    converged = n_iter < config.probe_max_iter
    print(f"  Probe training completed with {n_iter} iterations (converged: {converged})")

    print("[H-M3] Evaluating probe...")
    probs = probe.predict_proba(X_val_s)
    metrics = compute_metrics(y_val, probs)
    print(f"  AUROC: {metrics['auroc']:.4f}, Accuracy: {metrics['accuracy']:.4f}")

    print("[H-M3] Verifying mechanism...")
    mech = verify_mechanism(probe, X_val_s, y_val, config.weight_norm_min, config.pred_std_min, config.mechanism_auroc_min)
    print(f"  Weight norm: {mech['weight_norm']:.4f}, Pred std: {mech['pred_std']:.4f}, All pass: {mech['all_pass']}")

    print("[H-M3] Comparing to baseline...")
    cmp = compare_to_baseline(metrics["auroc"], baseline_stats["mean"])
    print(f"  Delta: {cmp['delta']:.4f}, Exceeds baseline by 0.20: {cmp['exceeds_baseline_by_20']}")

    fallback_result = {"triggered": False, "mlp_auroc": None}
    if metrics["auroc"] < config.auroc_gate:
        print(f"[H-M3] Linear AUROC < {config.auroc_gate}, running MLP fallback...")
        mlp = MLPFallbackProbe(config.mlp_hidden_layer_sizes, config.mlp_max_iter)
        mlp.fit(X_train_s, y_train)
        mlp_probs = mlp.predict_proba(X_val_s)
        mlp_auroc = float(roc_auc_score(y_val, mlp_probs))
        fallback_result = {"triggered": True, "mlp_auroc": mlp_auroc}
        print(f"  MLP AUROC: {mlp_auroc:.4f}")

    figures_dir = hyp_path / config.figures_dir
    figures_dir.mkdir(exist_ok=True)

    print("[H-M3] Generating figures...")
    plot_gate_comparison(metrics["auroc"], config.auroc_gate, str(hyp_path / config.gate_comparison_fig))
    plot_roc_curve(y_val, probs, metrics["auroc"], str(hyp_path / config.roc_curve_fig))
    print(f"  Saved to {figures_dir}")

    gate_satisfied = metrics["auroc"] >= config.auroc_gate
    results = {
        "hypothesis_id": "h-m3",
        "timestamp": datetime.now().isoformat(),
        "data": {
            "train_size": len(y_train),
            "val_size": len(y_val),
            "layer": config.layer,
            "source": "h-m1 cache"
        },
        "baseline": baseline_stats,
        "probe": {
            "auroc": metrics["auroc"],
            "accuracy": metrics["accuracy"],
            "n_iter": n_iter,
            "converged": converged
        },
        "mechanism": mech,
        "comparison": cmp,
        "fallback": fallback_result,
        "gate": {
            "type": "SHOULD_WORK",
            "threshold": config.auroc_gate,
            "achieved": metrics["auroc"],
            "satisfied": gate_satisfied,
            "result": "PASS" if gate_satisfied else "FAIL"
        }
    }

    results_path = hyp_path / config.results_json

    def numpy_to_python(obj):
        import numpy as np
        if isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: numpy_to_python(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [numpy_to_python(v) for v in obj]
        return obj

    results = numpy_to_python(results)
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[H-M3] Results saved to {results_path}")

    return results


if __name__ == "__main__":
    hypothesis_folder = sys.argv[1] if len(sys.argv) > 1 else "."
    from sklearn.metrics import roc_auc_score
    results = main(hypothesis_folder)
    print(f"\n[H-M3] Gate: {results['gate']['result']} (AUROC={results['gate']['achieved']:.4f} vs {results['gate']['threshold']})")
