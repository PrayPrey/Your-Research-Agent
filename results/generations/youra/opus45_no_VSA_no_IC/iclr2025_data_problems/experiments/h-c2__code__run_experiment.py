"""Main experiment orchestrator for h-c2: Cross-model mode profile transfer."""
import json
import os
import sys
from datetime import datetime

import numpy as np

from config import ExperimentConfig, MODEL_CONFIGS, set_all_seeds, setup_dirs
from data import get_datasets, get_loaders, build_probe_pairs, probe_subset
from models import build_model, get_device
from train import train_all_models
from attribution_trak import compute_trak_scores
from attribution_kronfluence import compute_kronfluence_scores
from cross_model_eval import (
    compute_mode_profile, pairwise_correlations, bootstrap_ci,
    check_transfer_success, ablation_method_comparison, ablation_probe_stability
)
from visualize import plot_profile_heatmap, plot_correlation_bars, plot_profile_radar, plot_bootstrap_ci


def main():
    cfg = ExperimentConfig()
    set_all_seeds(cfg.seed)
    setup_dirs(cfg)
    device = get_device()
    print(f"Device: {device}")

    # Data
    train_ds, test_ds = get_datasets(cfg)
    train_loader, test_loader = get_loaders(train_ds, test_ds, cfg)
    probes = build_probe_pairs(train_ds, test_ds, cfg.seed, n_per_mode=cfg.probes_per_mode)
    print(f"Probe pairs: {sum(len(p) for p in probes.values())} total")

    # Build and train models
    model_names = list(MODEL_CONFIGS.keys())
    models = {name: build_model(name) for name in model_names}
    print(f"Training {len(models)} models: {model_names}")

    train_results = train_all_models(models, train_loader, test_loader, MODEL_CONFIGS, cfg, device)
    accuracies = {name: acc for name, (_, acc) in train_results.items()}
    print(f"Accuracies: {accuracies}")

    # Check accuracy gate
    for name, acc in accuracies.items():
        if acc < cfg.min_test_accuracy:
            print(f"WARNING: {name} accuracy {acc:.4f} below threshold {cfg.min_test_accuracy}")

    # Compute TRAK scores per model
    print("Computing TRAK scores...")
    trak_scores = {}
    for name, model in models.items():
        model.to(device).eval()
        trak_scores[name] = compute_trak_scores(model, train_loader, test_loader, probes, cfg, device)
        print(f"  {name}: done")

    trak_profiles = {name: compute_mode_profile(scores) for name, scores in trak_scores.items()}

    # Compute Kronfluence scores (verification)
    print("Computing Kronfluence scores...")
    kron_scores = {}
    for name, model in models.items():
        model.to(device).eval()
        kron_scores[name] = compute_kronfluence_scores(model, train_loader, test_loader, probes, cfg, device)
        print(f"  {name}: done")

    kron_profiles = {name: compute_mode_profile(scores) for name, scores in kron_scores.items()}

    # Cross-model correlations
    print("Computing cross-model correlations...")
    trak_correlations = pairwise_correlations(trak_profiles, cfg.modes)
    kron_correlations = pairwise_correlations(kron_profiles, cfg.modes)

    # Bootstrap CIs
    for pair in trak_correlations:
        m1, m2 = pair
        v1 = np.array([trak_profiles[m1][m] for m in cfg.modes])
        v2 = np.array([trak_profiles[m2][m] for m in cfg.modes])
        trak_correlations[pair]["ci"] = bootstrap_ci(v1, v2, cfg.n_boot, cfg.seed)

    verdict = check_transfer_success(trak_correlations, cfg.r_threshold)
    print(f"\n=== GATE VERDICT: {verdict} ===")
    for pair, corr in trak_correlations.items():
        print(f"  {pair[0]}-{pair[1]}: r={corr['r']:.4f}, p_corr={corr['p_corrected']:.4f}, ci={corr.get('ci', 'N/A')}")

    # ABL-1: Method comparison
    abl1 = ablation_method_comparison(trak_correlations, kron_correlations)
    print(f"\nABL-1 (TRAK vs Kronfluence agreement): {abl1['agreement']}")

    # ABL-2: Probe subset stability
    print("\nComputing ABL-2 (probe subset stability)...")
    probes_subset = probe_subset(probes, cfg.probe_subset_fraction, cfg.seed + 1)
    subset_trak_scores = {}
    for name, model in models.items():
        model.to(device).eval()
        subset_trak_scores[name] = compute_trak_scores(model, train_loader, test_loader, probes_subset, cfg, device)
    subset_profiles = {name: compute_mode_profile(scores) for name, scores in subset_trak_scores.items()}
    subset_correlations = pairwise_correlations(subset_profiles, cfg.modes)
    abl2 = ablation_probe_stability(trak_correlations, subset_correlations)
    print(f"ABL-2 (probe stability): stable={abl2['stable']}, max_diff={abl2['max_diff']:.4f}")

    # Visualizations
    print("\nGenerating visualizations...")
    plot_profile_heatmap(trak_profiles, os.path.join(cfg.fig_dir, "profile_heatmap.png"))
    plot_correlation_bars(trak_correlations, cfg.r_threshold, os.path.join(cfg.fig_dir, "correlation_bars.png"))
    plot_profile_radar(trak_profiles, os.path.join(cfg.fig_dir, "profile_radar.png"))
    plot_bootstrap_ci(trak_correlations, os.path.join(cfg.fig_dir, "bootstrap_ci.png"))

    # Save results (convert numpy types to Python types)
    def to_serializable(obj):
        if isinstance(obj, (np.bool_, np.integer, np.floating)):
            return obj.item()
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, dict):
            return {k: to_serializable(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [to_serializable(v) for v in obj]
        return obj

    results = to_serializable({
        "verdict": verdict,
        "accuracies": accuracies,
        "trak_profiles": trak_profiles,
        "kron_profiles": kron_profiles,
        "correlations": {f"{k[0]}-{k[1]}": v for k, v in trak_correlations.items()},
        "ablation_1": {"agreement": abl1["agreement"]},
        "ablation_2": {"stable": abl2["stable"], "max_diff": abl2["max_diff"]},
        "timestamp": datetime.now().isoformat(),
    })
    results_path = os.path.join(cfg.fig_dir, "results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {results_path}")

    return verdict, results


if __name__ == "__main__":
    verdict, results = main()
    print(f"\nEXPERIMENT COMPLETE: {verdict}")
    sys.exit(0 if verdict in ("PASS", "PARTIAL") else 1)
