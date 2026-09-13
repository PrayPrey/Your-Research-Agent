"""H-P2: Spurious Probe Accuracy Correlates Negatively with WGA (Exploratory)"""
import json
import warnings
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, bootstrap
import yaml
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
BASE = Path("/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_scsl/docs/youra_research")
HM3_RESULTS = BASE / "h-m3/results.json"
HP2_DIR = BASE / "h-p2"
FIGURES_DIR = HP2_DIR / "figures"
RESULTS_JSON = HP2_DIR / "results.json"
VERIFICATION_STATE = BASE / "verification_state.yaml"

# ── WGA Ground Truth (Izmailov 2022 Table 1) ─────────────────────────────────
WGA_VALUES = {
    "erm_seed1": 0.72, "erm_seed2": 0.72, "erm_seed3": 0.72,
    "sam_seed1": 0.74, "sam_seed2": 0.74, "sam_seed3": 0.74,
    "groupdro_seed1": 0.88, "groupdro_seed2": 0.88, "groupdro_seed3": 0.88,
}

# Bootstrap params
N_RESAMPLES = 1000
CI_LEVEL = 0.95
RNG = 42

# Verdict thresholds
CONFIRMED_R = -0.5
SUGGESTIVE_R = -0.3

# Ordered keys
ORDERED_KEYS = [
    "erm_seed1", "erm_seed2", "erm_seed3",
    "sam_seed1", "sam_seed2", "sam_seed3",
    "groupdro_seed1", "groupdro_seed2", "groupdro_seed3",
]
LABELS = (["ERM"] * 3) + (["SARM"] * 3) + (["GroupDRO"] * 3)
LABELS = (["ERM"] * 3) + (["SAM"] * 3) + (["GroupDRO"] * 3)


def load_probe_accs():
    """Load 9 probe accuracies from h-m3/results.json."""
    with open(HM3_RESULTS) as f:
        data = json.load(f)
    probes = data["all_probe_results"]
    # Validate all 9 present
    for k in ORDERED_KEYS:
        assert k in probes, f"Missing probe key: {k}"
        assert 0.0 <= probes[k] <= 1.0, f"Probe acc out of range: {k}={probes[k]}"
    return probes


def assemble_dataset(probes):
    """Build ordered (probe_accs, wga_values) arrays."""
    probe_accs = np.array([probes[k] for k in ORDERED_KEYS])
    wga_values = np.array([WGA_VALUES[k] for k in ORDERED_KEYS])
    # Validate SAM WGA == 0.74
    sam_wga = wga_values[3:6]
    assert all(v == 0.74 for v in sam_wga), f"SAM WGA should be 0.74, got {sam_wga}"
    return probe_accs, wga_values


def pearsonr_stat(x, y, axis=-1):
    """Vectorized pearsonr for scipy.stats.bootstrap."""
    return pearsonr(x, y, axis=axis)[0]


def classify_verdict(r, ci_low, ci_high):
    if r < CONFIRMED_R and ci_high < 0:
        return "CONFIRMED"
    elif r < SUGGESTIVE_R and ci_low < 0:
        return "SUGGESTIVE"
    return "REJECTED"


def compute_correlation_with_bootstrap(probe_accs, wga_values):
    """Compute Pearson r + one-sided p-value + BCa bootstrap CI."""
    r, p_value = pearsonr(probe_accs, wga_values, alternative='less')

    # BCa bootstrap with percentile fallback
    ci_method = "BCa"
    try:
        boot = bootstrap(
            (probe_accs, wga_values), pearsonr_stat,
            paired=True, n_resamples=N_RESAMPLES,
            confidence_level=CI_LEVEL, method='BCa', random_state=RNG
        )
        ci_low = boot.confidence_interval.low
        ci_high = boot.confidence_interval.high
        if np.isnan(ci_low) or np.isnan(ci_high):
            raise ValueError("BCa returned NaN")
    except Exception as e:
        warnings.warn(f"BCa failed ({e}), falling back to percentile")
        ci_method = "percentile"
        boot = bootstrap(
            (probe_accs, wga_values), pearsonr_stat,
            paired=True, n_resamples=N_RESAMPLES,
            confidence_level=CI_LEVEL, method='percentile', random_state=RNG
        )
        # Filter NaN from boot distribution (rare at n=9 with constant WGA strata)
        dist_clean = boot.bootstrap_distribution[~np.isnan(boot.bootstrap_distribution)]
        alpha = 1 - CI_LEVEL
        ci_low = float(np.percentile(dist_clean, 100 * alpha / 2))
        ci_high = float(np.percentile(dist_clean, 100 * (1 - alpha / 2)))

    boot_distribution = boot.bootstrap_distribution  # shape (1000,)
    verdict = classify_verdict(r, ci_low, ci_high)

    return {
        "r": float(r), "p_value": float(p_value),
        "ci_low": float(ci_low), "ci_high": float(ci_high),
        "ci_method": ci_method, "verdict": verdict,
        "boot_distribution": boot_distribution,
    }


def run_ablation_variants(probe_accs, wga_values):
    """Run 3 ablation variants."""
    results = {}

    # Variant 1: ERM + GroupDRO only (n=6, exclude SAM indices 3,4,5)
    mask_n6 = np.array([True, True, True, False, False, False, True, True, True])
    pa6, wga6 = probe_accs[mask_n6], wga_values[mask_n6]
    r6, p6 = pearsonr(pa6, wga6, alternative='less')
    # For ablations: no bootstrap CI; use r threshold only (p < 0.05 proxy for ci_high < 0)
    results["erm_groupdro_n6"] = {
        "r": float(r6), "p": float(p6),
        "verdict": "CONFIRMED" if r6 < CONFIRMED_R and p6 < 0.05 else
                   "SUGGESTIVE" if r6 < SUGGESTIVE_R and p6 < 0.1 else "REJECTED"
    }

    # Variant 2: Per-method means (n=3)
    pa_means = np.array([
        probe_accs[0:3].mean(),  # ERM
        probe_accs[3:6].mean(),  # SAM
        probe_accs[6:9].mean(),  # GroupDRO
    ])
    wga_means = np.array([0.72, 0.74, 0.88])
    r3, p3 = pearsonr(pa_means, wga_means, alternative='less')
    results["method_means_n3"] = {
        "r": float(r3), "p": float(p3),
        "verdict": "CONFIRMED" if r3 < CONFIRMED_R and p3 < 0.05 else
                   "SUGGESTIVE" if r3 < SUGGESTIVE_R and p3 < 0.1 else "REJECTED"
    }

    return results


def plot_scatter(probe_accs, wga_values, r, p_value):
    method_colors = {"ERM": "steelblue", "SAM": "orange", "GroupDRO": "green"}
    method_map = {"ERM": (0, 3), "SAM": (3, 6), "GroupDRO": (6, 9)}

    fig, ax = plt.subplots(figsize=(8, 6))
    for method, (start, end) in method_map.items():
        ax.scatter(probe_accs[start:end], wga_values[start:end],
                   color=method_colors[method], label=method, s=80, zorder=3)

    # OLS regression line
    slope, intercept = np.polyfit(probe_accs, wga_values, 1)
    x_range = np.linspace(probe_accs.min() - 0.01, probe_accs.max() + 0.01, 100)
    ax.plot(x_range, slope * x_range + intercept, 'k--', alpha=0.7, label='OLS')

    ax.set_xlabel("Spurious Probe Accuracy (background decodability)", fontsize=12)
    ax.set_ylabel("Worst-Group Accuracy (WGA)", fontsize=12)
    ax.set_title("H-P2: Probe Accuracy vs WGA across 9 Checkpoints", fontsize=13)
    ax.legend(fontsize=10)
    ax.text(0.05, 0.95, f"r = {r:.3f}\np = {p_value:.4f}",
            transform=ax.transAxes, fontsize=11, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "scatter_probe_vs_wga.png", dpi=150)
    plt.close()
    print("✓ Figure 1 saved: scatter_probe_vs_wga.png")


def plot_bootstrap_distribution(boot_distribution, ci_low, ci_high, ci_method):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(boot_distribution, bins=40, color='steelblue', alpha=0.7, edgecolor='white')
    ax.axvline(ci_low, color='red', linestyle='--', linewidth=2,
               label=f"CI low={ci_low:.3f} ({ci_method})")
    ax.axvline(ci_high, color='red', linestyle='--', linewidth=2,
               label=f"CI high={ci_high:.3f}")
    ax.axvline(0, color='black', linewidth=2, label="r=0 (null)")
    ax.set_xlabel("Bootstrap Pearson r", fontsize=12)
    ax.set_ylabel("Count", fontsize=12)
    ax.set_title(f"Bootstrap Distribution of Pearson r (n=1000, {ci_method})", fontsize=13)
    ax.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "bootstrap_distribution.png", dpi=150)
    plt.close()
    print("✓ Figure 2 saved: bootstrap_distribution.png")


def plot_method_comparison(probe_accs, wga_values):
    methods = ["ERM", "SAM", "GroupDRO"]
    slices = [(0, 3), (3, 6), (6, 9)]
    pa_means = [probe_accs[s:e].mean() for s, e in slices]
    pa_stds = [probe_accs[s:e].std() for s, e in slices]
    wga_means = [wga_values[s:e].mean() for s, e in slices]
    wga_stds = [wga_values[s:e].std() for s, e in slices]
    colors = ["steelblue", "orange", "green"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    ax1.bar(methods, pa_means, yerr=pa_stds, color=colors, capsize=5, alpha=0.8)
    ax1.set_ylabel("Mean Probe Accuracy")
    ax1.set_title("Spurious Probe Accuracy by Method")
    ax2.bar(methods, wga_means, yerr=wga_stds, color=colors, capsize=5, alpha=0.8)
    ax2.set_ylabel("WGA")
    ax2.set_title("Worst-Group Accuracy by Method")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "method_comparison_bar.png", dpi=150)
    plt.close()
    print("✓ Figure 3 saved: method_comparison_bar.png")


def plot_ablation_sensitivity(ablations, r_full, full_verdict):
    variants = ["full_n9", "erm_groupdro_n6", "method_means_n3"]
    r_vals = [r_full, ablations["erm_groupdro_n6"]["r"], ablations["method_means_n3"]["r"]]
    verdicts = [
        full_verdict,
        ablations["erm_groupdro_n6"]["verdict"],
        ablations["method_means_n3"]["verdict"],
    ]
    verdict_colors = {"CONFIRMED": "green", "SUGGESTIVE": "orange", "REJECTED": "red"}
    colors = [verdict_colors[v] for v in verdicts]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(variants, r_vals, color=colors, alpha=0.8)
    ax.axhline(CONFIRMED_R, color='darkgreen', linestyle='--', linewidth=1.5, label="CONFIRMED threshold (-0.5)")
    ax.axhline(SUGGESTIVE_R, color='darkorange', linestyle='--', linewidth=1.5, label="SUGGESTIVE threshold (-0.3)")
    ax.axhline(0, color='black', linewidth=1, alpha=0.5)
    ax.set_ylabel("Pearson r")
    ax.set_title("Ablation Sensitivity: Pearson r by Dataset Variant")
    ax.legend(fontsize=9)
    for bar, r in zip(bars, r_vals):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() - 0.02,
                f"{r:.3f}", ha='center', va='top', fontsize=10, color='white', fontweight='bold')
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "ablation_sensitivity.png", dpi=150)
    plt.close()
    print("✓ Figure 4 saved: ablation_sensitivity.png")


def save_results(probe_accs, wga_values, corr, ablations):
    results = {
        "hypothesis_id": "h-p2",
        "probe_accuracies": {k: float(probe_accs[i]) for i, k in enumerate(ORDERED_KEYS)},
        "wga_values": {k: float(wga_values[i]) for i, k in enumerate(ORDERED_KEYS)},
        "correlation": {
            "pearson_r": corr["r"],
            "p_value": corr["p_value"],
            "ci_low": corr["ci_low"],
            "ci_high": corr["ci_high"],
            "ci_method": corr["ci_method"],
            "verdict": corr["verdict"],
        },
        "ablations": {
            "erm_groupdro_n6": ablations["erm_groupdro_n6"],
            "method_means_n3": ablations["method_means_n3"],
        },
    }
    with open(RESULTS_JSON, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"✓ results.json saved: {RESULTS_JSON}")
    return results


def update_verification_state(verdict, corr):
    with open(VERIFICATION_STATE) as f:
        state = yaml.safe_load(f)

    gate_satisfied = verdict in ("CONFIRMED", "SUGGESTIVE")
    gate_result = "PASS" if gate_satisfied else "FAIL"

    hp2 = state.setdefault("sub_hypotheses", {}).setdefault("h-p2", {})
    hp2.setdefault("gate", {}).update({
        "satisfied": gate_satisfied,
        "result": gate_result,
    })
    hp2.setdefault("validation", {}).update({
        "status": "COMPLETED",
        "verdict": verdict,
        "pearson_r": corr["r"],
        "p_value": corr["p_value"],
        "ci_low": corr["ci_low"],
        "ci_high": corr["ci_high"],
        "ci_method": corr["ci_method"],
    })

    with open(VERIFICATION_STATE, 'w') as f:
        yaml.dump(state, f, default_flow_style=False, allow_unicode=True)
    print(f"✓ verification_state.yaml updated: gate={gate_result}, verdict={verdict}")


def main():
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    print("=== H-P2: Spurious Probe Accuracy vs WGA Correlation ===")

    # Load data
    probes = load_probe_accs()
    probe_accs, wga_values = assemble_dataset(probes)
    print(f"✓ Loaded 9 probe accuracies from h-m3/results.json")
    for k, pa, wga in zip(ORDERED_KEYS, probe_accs, wga_values):
        print(f"  {k}: probe_acc={pa:.4f}, WGA={wga:.2f}")

    # Correlation + bootstrap
    print("\n--- Computing Pearson r + Bootstrap CI ---")
    corr = compute_correlation_with_bootstrap(probe_accs, wga_values)
    print(f"r = {corr['r']:.4f}")
    print(f"p (one-sided, H1: r<0) = {corr['p_value']:.6f}")
    print(f"95% CI ({corr['ci_method']}): [{corr['ci_low']:.4f}, {corr['ci_high']:.4f}]")
    print(f"Verdict: {corr['verdict']}")

    # Ablations
    print("\n--- Ablation Variants ---")
    ablations = run_ablation_variants(probe_accs, wga_values)
    for name, res in ablations.items():
        print(f"  {name}: r={res['r']:.4f}, p={res['p']:.4f}, verdict={res['verdict']}")

    # Figures
    print("\n--- Generating Figures ---")
    plot_scatter(probe_accs, wga_values, corr["r"], corr["p_value"])
    plot_bootstrap_distribution(corr["boot_distribution"], corr["ci_low"], corr["ci_high"], corr["ci_method"])
    plot_method_comparison(probe_accs, wga_values)
    plot_ablation_sensitivity(ablations, corr["r"], corr["verdict"])

    # Save results
    print("\n--- Saving Results ---")
    save_results(probe_accs, wga_values, corr, ablations)
    update_verification_state(corr["verdict"], corr)

    # Final summary
    print(f"\n=== GATE VERDICT: {corr['verdict']} ===")
    print(f"Pearson r = {corr['r']:.4f}, p = {corr['p_value']:.6f}")
    print(f"95% CI ({corr['ci_method']}): [{corr['ci_low']:.4f}, {corr['ci_high']:.4f}]")
    print(f"Gate: SHOULD_WORK → {'PASS' if corr['verdict'] in ('CONFIRMED','SUGGESTIVE') else 'FAIL (non-blocking)'}")


if __name__ == "__main__":
    main()
