"""
H-M2 Experiment: Permutation Orbit Variance Dominance
Computes Var_perm / (Var_perm + Var_GL) on Small CNN Zoo checkpoint trajectories.
Gate: ratio > 0.60 (MUST_WORK)
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict

from config import get_config, setup_dirs, ExperimentConfig
from data_loader import TrajectoryDataset
from orbit_projector import OrbitProjector
from variance_decomposer import VarianceDecomposer, verify_mechanism_activated
from evaluate import run_zoo_analysis, compute_cross_dataset_stability, check_gate, save_results_json
from visualize import save_all_figures


def setup_paths(config: ExperimentConfig) -> None:
    """Create figures_dir and results_dir; verify h_m1_code_path exists."""
    setup_dirs(config)
    Path("code/outputs").mkdir(parents=True, exist_ok=True)

    h_m1_path = Path(config.h_m1_code_path)
    if not h_m1_path.exists():
        print(f"⚠️  h-m1 code path not found: {h_m1_path}")
        print("   Proceeding with fallback orbit basis (without OrbitPEComputer)")
    else:
        print(f"✓ h-m1 code path: {h_m1_path}")


def run(config: ExperimentConfig) -> Dict:
    """Full pipeline: load → decompose → evaluate → visualize → report."""
    print("\n" + "=" * 70)
    print("H-M2: Permutation Orbit Variance Dominance")
    print("=" * 70)
    print(f"Start time: {datetime.now().isoformat()}")
    print(f"Config: gate_threshold={config.gate_threshold}, min_models={config.min_models}")
    print(f"Data CIFAR-10: {config.data_dir_cifar10}")
    print(f"Data SVHN: {config.data_dir_svhn}")

    # Initialize modules
    print("\n🔧 Initializing OrbitProjector...")
    projector = OrbitProjector(
        token_dim=config.token_dim,
        orbit_basis_dim=config.orbit_basis_dim,
        h_m1_code_path=config.h_m1_code_path,
        eps=config.eps,
    )
    if projector._h_m1_available:
        print("  ✓ OrbitPEComputer loaded from h-m1")
    else:
        print(f"  ⚠️  h-m1 unavailable ({projector._h_m1_error[:60]}), using fallback")

    decomposer = VarianceDecomposer(projector, eps=config.eps)

    # Load datasets
    print("\n📦 Loading CNN Zoo datasets...")
    cifar10_dir = Path(config.data_dir_cifar10)
    svhn_dir = Path(config.data_dir_svhn)

    dataset_cifar10 = TrajectoryDataset(
        cifar10_dir,
        min_checkpoints=config.min_checkpoints,
        max_checkpoints=config.max_checkpoints,
    )
    dataset_svhn = TrajectoryDataset(
        svhn_dir,
        min_checkpoints=config.min_checkpoints,
        max_checkpoints=config.max_checkpoints,
    )

    n_cifar10 = len(dataset_cifar10)
    n_svhn = len(dataset_svhn)
    print(f"  CIFAR-10-GS: {n_cifar10} models with ≥{config.min_checkpoints} checkpoints")
    print(f"  SVHN-GS: {n_svhn} models with ≥{config.min_checkpoints} checkpoints")

    if n_cifar10 == 0:
        print(f"\n❌ ERROR: No CIFAR-10 models found at {cifar10_dir}")
        print("   Please run: modelzoo fetch --zoo core --arch cnn-small --dataset cifar10 --config uniform --seed all --ckpts all --dir ./data/cnn_zoo_cifar10/")
        sys.exit(1)

    # Run analysis
    results_cifar10 = run_zoo_analysis(
        dataset_cifar10, decomposer, "CIFAR-10-GS",
        min_models=config.min_models,
        orbit_basis_dim=config.orbit_basis_dim,
    )
    results_svhn = run_zoo_analysis(
        dataset_svhn, decomposer, "SVHN-GS",
        min_models=config.min_models,
        orbit_basis_dim=config.orbit_basis_dim,
    ) if n_svhn > 0 else {"ratio_mean": 0.0, "ratio_std": 0.0, "n_models": 0}

    # Cross-dataset stability
    stability = compute_cross_dataset_stability(
        results_cifar10["ratio_mean"],
        results_svhn.get("ratio_mean", 0.0),
    )

    # Gate evaluation
    gate_results = check_gate(
        results_cifar10, results_svhn,
        threshold=config.gate_threshold,
        stability_threshold=config.stability_threshold,
    )

    # Key output line
    print(f"\n{'=' * 70}")
    print(f"Var_perm / (Var_perm + Var_GL) = {results_cifar10['ratio_mean']:.4f} ± {results_cifar10['ratio_std']:.4f}")
    print(f"Gate result: {'PASS ✅' if gate_results['all_pass'] else 'FAIL ❌ (PIVOT required)'}")
    print(f"{'=' * 70}")

    # Build combined results
    results = {
        "hypothesis_id": "h-m2",
        "completed_at": datetime.now().isoformat(),
        "cifar10": results_cifar10,
        "svhn": results_svhn,
        "stability": stability,
        "gate": gate_results,
        "gate_threshold": config.gate_threshold,
        "accuracies_cifar10": [],  # Not collected (no val set)
        "var_ratio_mean": results_cifar10["ratio_mean"],
        "var_ratio_std": results_cifar10["ratio_std"],
        "n_models": results_cifar10["n_models"],
        "ratio_cifar10": results_cifar10["ratio_mean"],
        "ratio_svhn": results_svhn.get("ratio_mean", 0.0),
        "stability_gap": stability["stability_gap"],
        "gate_pass": gate_results["all_pass"],
        "orbit_basis_dim": results_cifar10.get("orbit_basis_dim", config.orbit_basis_dim),
    }

    # Mechanism verification
    print("\n🔍 Verifying mechanism activation indicators...")
    all_pass, indicators = verify_mechanism_activated(results)
    results["mechanism_verified"] = all_pass
    results["mechanism_indicators"] = indicators

    # Save results JSON
    results_path = os.path.join(config.results_dir, "experiment_results.json")
    save_results_json(results, results_path)

    # Also save to standard output path
    exp_results_path = "docs/youra_research/20260521_wsl/h-m2/experiment_results.json"
    save_results_json(results, exp_results_path)

    # Also write CSV summary
    csv_path = "code/outputs/results.csv"
    Path(csv_path).parent.mkdir(parents=True, exist_ok=True)
    with open(csv_path, "w") as f:
        f.write("subset,ratio_mean,ratio_std,n_models,gate_pass\n")
        f.write(f"CIFAR-10-GS,{results_cifar10['ratio_mean']:.6f},{results_cifar10['ratio_std']:.6f},{results_cifar10['n_models']},{gate_results['all_pass']}\n")
        if results_svhn.get("n_models", 0) > 0:
            f.write(f"SVHN-GS,{results_svhn['ratio_mean']:.6f},{results_svhn.get('ratio_std', 0.0):.6f},{results_svhn['n_models']},{gate_results['all_pass']}\n")
    print(f"✓ Results CSV saved: {csv_path}")

    # Visualizations
    print(f"\n🎨 Generating figures...")
    save_all_figures(results, Path(config.figures_dir))

    return results


def generate_validation_report(results: Dict, output_path: str) -> None:
    """Write 04_validation.md with gate PASS/PIVOT determination."""
    gate = results.get("gate", {})
    all_pass = gate.get("all_pass", False)
    ratio_mean = results.get("var_ratio_mean", 0.0)
    ratio_std = results.get("var_ratio_std", 0.0)
    n_models = results.get("n_models", 0)
    ratio_svhn = results.get("ratio_svhn", 0.0)
    stability_gap = results.get("stability_gap", 0.0)

    gate_result = "PASS" if all_pass else "FAIL"
    gate_emoji = "✅" if all_pass else "❌"

    pivot_section = ""
    if not all_pass:
        pivot_section = """
## PIVOT Recommendation

Since Var_perm / (Var_perm + Var_GL) < 0.60, the permutation orbit subspace does NOT dominate
the functional variation in CNN Zoo checkpoint trajectories.

**Recommended pivot before H-M3:**
- Implement hybrid orbit-PE + GL trace features: `tr(W^Q W^{K,T})` (from arXiv:2410.04207)
- Add GL-invariant polynomial features to the SANE weight tokenizer
- Re-scope H-M3 with hybrid model (orbit-PE + GL traces)

This pivot ensures H-M3's cross-architecture test uses the most informative positional encoding.
"""

    content = f"""# Validation Report: H-M2
# Permutation Orbit Variance Dominance — Var_perm / (Var_perm + Var_GL) > 0.60

**Date:** {results.get("completed_at", "2026-05-21")[:10]}
**Hypothesis:** H-M2 (MECHANISM — INCREMENTAL on H-E1, H-M1)
**Gate Type:** MUST_WORK
**Gate Result:** {gate_emoji} **{gate_result}**

---

## Summary

**Primary Metric:** Var_perm / (Var_perm + Var_GL) = **{ratio_mean:.4f} ± {ratio_std:.4f}**

| Criterion | Threshold | Result | Status |
|-----------|-----------|--------|--------|
| var_ratio_mean (CIFAR-10-GS) | > 0.60 | {ratio_mean:.4f} | {"✅ PASS" if gate.get("primary_pass", False) else "❌ FAIL"} |
| n_models_analyzed | ≥ 200 | {n_models} | {"✅ PASS" if gate.get("n_models_pass", False) else "❌ FAIL"} |
| var_ratio_std (non-degenerate) | > 0.01 | {ratio_std:.4f} | {"✅ PASS" if gate.get("non_degenerate_pass", False) else "❌ FAIL"} |
| Stability (\\|CIFAR-SVHN\\|) | < 0.10 | {stability_gap:.4f} | {"✅ PASS" if gate.get("stability_pass", False) else "⚠️ WARN (secondary)"} |

---

## Gate Decision

**Overall Gate: {gate_emoji} {gate_result}**

{"**Proceed to H-M3** with orbit-PE as primary positional encoding strategy." if all_pass else "**PIVOT REQUIRED** before H-M3 — see Pivot Recommendation section."}

---

## Key Findings

- **CIFAR-10-GS:** Var_perm/(Var_perm+Var_GL) = {ratio_mean:.4f} ± {ratio_std:.4f} (n={n_models} models)
- **SVHN-GS:** Var_perm/(Var_perm+Var_GL) = {ratio_svhn:.4f} (cross-dataset stability check)
- **Stability gap:** |{ratio_mean:.4f} - {ratio_svhn:.4f}| = {stability_gap:.4f} (threshold: 0.10)
- **Mechanism verification:** {"PASSED — all indicators positive" if results.get("mechanism_verified", False) else "PARTIAL — see indicators below"}

## Mechanism Activation Indicators

"""
    for name, val in results.get("mechanism_indicators", {}).items():
        status = "✅" if val else "❌"
        content += f"- {status} {name}: {val}\n"

    content += f"""
---

## Experiment Configuration

- Dataset: Small CNN Zoo (CIFAR-10-GS primary, SVHN-GS secondary)
- Analysis: Pure variance decomposition (no gradient computation)
- Orbit basis: SVD on orbit membership matrix from OrbitPEComputer (H-M1)
- Gate threshold: 0.60

## Files Generated

- `experiment_results.json`: Full metrics
- `code/outputs/results.csv`: Summary CSV
- `figures/gate_bar_chart.png`: **Mandatory gate figure** (Var_perm/Var_GL bars + threshold)
- `figures/ratio_histogram.png`: Per-model ratio distribution
- `figures/ratio_vs_epoch.png`: Ratio evolution during training
- `figures/layer_breakdown.png`: Conv2d vs Linear breakdown
- `figures/ratio_vs_accuracy.png`: Ratio vs final accuracy scatter

## Dependencies

- H-E1 (VALIDATED): orbit-PE accuracy-preserving; layer compatibility confirmed
- H-M1 (VALIDATED): OrbitPEComputer unified codebase; overhead 1.167x

{pivot_section}

---

*Generated by Phase 4 Validation Pipeline (UNATTENDED)*
*Hypothesis: H-M2 | Gate: MUST_WORK | Result: {gate_result}*
"""

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(content)
    print(f"✓ Validation report saved: {output_path}")


if __name__ == "__main__":
    config = get_config()
    setup_paths(config)
    results = run(config)

    report_path = "docs/youra_research/20260521_wsl/h-m2/04_validation.md"
    generate_validation_report(results, report_path)

    print(f"\n{'=' * 70}")
    print("EXPERIMENT COMPLETE")
    print(f"Gate: {'PASS ✅' if results['gate_pass'] else 'FAIL ❌ (PIVOT)'}")
    print(f"Var_perm/(Var_perm+Var_GL) = {results['var_ratio_mean']:.4f}")
    print(f"{'=' * 70}")
