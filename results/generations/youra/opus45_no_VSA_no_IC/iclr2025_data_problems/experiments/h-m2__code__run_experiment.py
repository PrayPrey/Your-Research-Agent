"""Main experiment orchestrator for h-m2: Multi-seed dissociation test."""
import json
import os
import sys
from pathlib import Path

# Add h-m2/code first, then h-m1/code
_hm2_code = os.path.dirname(os.path.abspath(__file__))
_hm1_code = str(Path(__file__).parent.parent.parent / "h-m1" / "code")
sys.path.insert(0, _hm2_code)  # h-m2 first for local config
sys.path.insert(1, _hm1_code)  # h-m1 second for base modules

# Import from h-m2 config (local)
from config import MultiSeedConfig, setup_dirs, set_all_seeds

# Import from h-m1
from model import get_device
from profiles import save_profiles, load_profiles
from dissociation import compute_dissociation_metrics, verify_dissociation
from visualize import (
    plot_gate_metrics,
    plot_profile_scatter_3d,
    plot_variance_boxplot,
    plot_cohens_d_heatmap,
)
from run_multiseed import run_all_seeds


def main():
    print("=" * 60)
    print("h-m2: Multi-Seed Dissociation Experiment")
    print("=" * 60)

    # Config
    cfg = MultiSeedConfig()
    setup_dirs(cfg)
    device = get_device()
    print(f"Device: {device}")
    print(f"Seeds: {cfg.seeds}")
    print(f"Epochs per seed: {cfg.epochs}")
    print(f"Probes per mode: {cfg.probes_per_mode}")

    # Run multi-seed experiment
    print("\n[1/4] Running multi-seed experiment...")
    all_profiles = run_all_seeds(cfg, device)
    print(f"\nCollected profiles: {len(all_profiles['trak'])} seeds x 3 methods")

    # Save profiles
    profiles_path = os.path.join(cfg.results_dir, "profiles.json")
    save_profiles(all_profiles, profiles_path)
    print(f"Saved profiles to {profiles_path}")

    # Compute dissociation metrics
    print("\n[2/4] Computing dissociation metrics...")
    results = compute_dissociation_metrics(all_profiles)
    print(f"  F-ratio: {results['F_ratio']:.4f}")
    print(f"  p-value: {results['p_value']:.6f}")
    print(f"  Cohen's d (max): {results['cohens_d']:.4f}")
    print(f"  SS_between: {results['ss_between']:.4f}")
    print(f"  SS_within: {results['ss_within']:.4f}")

    # Gate evaluation
    print("\n[3/4] Evaluating gate...")
    gate_pass = verify_dissociation(results, cfg)

    # Visualization
    print("\n[4/4] Generating figures...")
    plot_gate_metrics(results, os.path.join(cfg.fig_dir, "gate_metrics.png"))
    plot_profile_scatter_3d(all_profiles, os.path.join(cfg.fig_dir, "profile_scatter_3d.png"))
    plot_variance_boxplot(all_profiles, os.path.join(cfg.fig_dir, "variance_boxplot.png"))
    plot_cohens_d_heatmap(all_profiles, os.path.join(cfg.fig_dir, "cohens_d_heatmap.png"))

    # Save gate results
    gate_results = {
        "hypothesis_id": "h-m2",
        "gate_type": "MUST_WORK",
        "gate_pass": gate_pass,
        "thresholds": {
            "f_ratio": cfg.f_ratio_threshold,
            "cohens_d": cfg.cohens_d_threshold,
            "p_value": cfg.p_value_threshold,
        },
        "results": results,
        "criteria": {
            "f_ratio_pass": results["F_ratio"] > cfg.f_ratio_threshold,
            "cohens_d_pass": results["cohens_d"] > cfg.cohens_d_threshold,
            "p_value_pass": results["p_value"] < cfg.p_value_threshold,
        },
        "n_seeds": len(cfg.seeds),
        "n_methods": 3,
    }

    gate_path = os.path.join(cfg.results_dir, "gate_results.json")
    with open(gate_path, "w") as f:
        json.dump(gate_results, f, indent=2)
    print(f"\nGate results saved to {gate_path}")

    print("\n" + "=" * 60)
    print(f"GATE RESULT: {'PASS' if gate_pass else 'FAIL'}")
    print("=" * 60)

    return gate_pass, gate_results


if __name__ == "__main__":
    success, _ = main()
    sys.exit(0 if success else 1)
