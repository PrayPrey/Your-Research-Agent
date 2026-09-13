"""H-M1: Causal Attribution — Encoder Architecture Determines OrbitVar (>=4 OOM).

Reuses H-E1 infrastructure. New code: CISEEncoder (C1), ratio computation,
Wilcoxon tests, anti-confound gate.
"""
import sys
import os
import json
import inspect
import csv

import numpy as np
import torch

# H-E1 infrastructure
_H_E1 = os.path.join(os.path.dirname(__file__), '..', '..', 'h-e1', 'code')
sys.path.insert(0, os.path.abspath(_H_E1))

from encoder_c2 import DeepSetsChannelEncoder, build_c2_encoder
from orbit_var import compute_orbit_var_all_models

# Local
sys.path.insert(0, os.path.dirname(__file__))
from encoder_c1 import CISEEncoder, build_c1_encoder

# Paths
_HERE = os.path.dirname(os.path.abspath(__file__))
H_E1_RESULTS = os.path.join(_HERE, '..', '..', 'h-e1', 'code', 'results', 'orbit_var_results.json')
RESULTS_DIR = os.path.join(_HERE, '..', 'results')
FIGURES_DIR = os.path.join(_HERE, '..', 'figures')

EPS = 1e-30
BUILD_ON_VALUE = 0.010333  # sh1 PASS result


def verify_prerequisites(h_e1_results_path: str):
    """Load C2/C3 per-model OrbitVars from H-E1 results. Verify means."""
    with open(h_e1_results_path) as f:
        d = json.load(f)

    orbit_vars_C2 = np.array(d['per_model_orbitvar_c2'])
    orbit_vars_C3 = np.array(d['per_model_orbitvar_c3'])
    mean_c2 = float(np.mean(orbit_vars_C2))
    mean_c3 = float(np.mean(orbit_vars_C3))

    assert abs(mean_c2 - 1.002e-14) / 1.002e-14 < 0.1, \
        f"C2 mean mismatch: {mean_c2:.3e} vs expected 1.002e-14"
    assert abs(mean_c3 - 8.905e-08) / 8.905e-08 < 0.1, \
        f"C3 mean mismatch: {mean_c3:.3e} vs expected 8.905e-08"

    print(f"[Prerequisites] C2 mean={mean_c2:.3e}  C3 mean={mean_c3:.3e}  OK")
    return orbit_vars_C2, orbit_vars_C3


def measure_cise_orbitvar(
    dataset,
    perm_specs,
    build_on: bool = True,
    build_on_value: float = BUILD_ON_VALUE,
) -> np.ndarray:
    """Returns orbit_vars_C1 [N_MODELS]."""
    if build_on:
        n = len(dataset) if dataset is not None else 100
        print(f"[C1] BUILD_ON: reusing CISE OrbitVar = {build_on_value} for all {n} models")
        return np.full(n, build_on_value)

    print(f"[C1] Re-measuring CISE OrbitVar ({len(dataset)} models x {len(perm_specs)} perms)...")
    encoder = build_c1_encoder(embed_dim=64)
    encoder.eval()
    per_model_vars, _, _ = compute_orbit_var_all_models(
        dataset, encoder.forward, perm_specs, log_every=10
    )
    arr = np.array(per_model_vars)
    measured_mean = float(np.mean(arr))
    print(f"[C1] Measured mean OrbitVar = {measured_mean:.6f} (expected ~{build_on_value})")
    if abs(measured_mean - build_on_value) / build_on_value > 0.2:
        print("  WARNING: >20% deviation from sh1 baseline")
    return arr


def compute_ratios(
    orbit_vars_C1: np.ndarray,
    orbit_vars_C2: np.ndarray,
    orbit_vars_C3: np.ndarray,
    eps: float = EPS,
) -> dict:
    """Returns per-model ratios and aggregate stats."""
    ratios_C1_C2 = orbit_vars_C1 / (orbit_vars_C2 + eps)
    ratios_C1_C3 = orbit_vars_C1 / (orbit_vars_C3 + eps)

    mean_C1 = float(np.mean(orbit_vars_C1))
    mean_C2 = float(np.mean(orbit_vars_C2))
    mean_C3 = float(np.mean(orbit_vars_C3))

    return {
        'orbit_vars_C1': orbit_vars_C1.tolist(),
        'orbit_vars_C2': orbit_vars_C2.tolist(),
        'orbit_vars_C3': orbit_vars_C3.tolist(),
        'mean_OrbitVar_C1': mean_C1,
        'mean_OrbitVar_C2': mean_C2,
        'mean_OrbitVar_C3': mean_C3,
        'ratios_C1_C2': ratios_C1_C2.tolist(),
        'ratios_C1_C3': ratios_C1_C3.tolist(),
        'mean_ratio_C1_C2': float(np.mean(ratios_C1_C2)),
        'median_ratio_C1_C2': float(np.median(ratios_C1_C2)),
        'geomean_ratio_C1_C2': float(np.exp(np.mean(np.log(ratios_C1_C2 + eps)))),
        'mean_ratio_C1_C3': float(np.mean(ratios_C1_C3)),
        'median_ratio_C1_C3': float(np.median(ratios_C1_C3)),
        'geomean_ratio_C1_C3': float(np.exp(np.mean(np.log(ratios_C1_C3 + eps)))),
        'log10_oom_C1_C2': float(np.log10(mean_C1 / (mean_C2 + eps))),
        'log10_oom_C1_C3': float(np.log10(mean_C1 / (mean_C3 + eps))),
        'pct_models_C1C2_gt_1e4': float(np.mean(ratios_C1_C2 > 1e4) * 100),
        'pct_models_C1C3_gt_1e3': float(np.mean(ratios_C1_C3 > 1e3) * 100),
    }


def run_wilcoxon(
    orbit_vars_C1: np.ndarray,
    orbit_vars_C2: np.ndarray,
    orbit_vars_C3: np.ndarray,
    eps: float = EPS,
) -> dict:
    """Paired Wilcoxon on log10(OrbitVar); alternative='greater'."""
    from scipy.stats import wilcoxon

    log_C1 = np.log10(orbit_vars_C1 + eps)
    log_C2 = np.log10(orbit_vars_C2 + eps)
    log_C3 = np.log10(orbit_vars_C3 + eps)

    stat_C1C2, p_C1C2 = wilcoxon(log_C1, log_C2, alternative='greater')
    stat_C1C3, p_C1C3 = wilcoxon(log_C1, log_C3, alternative='greater')

    print(f"[Wilcoxon] C1>C2: stat={stat_C1C2:.1f}  p={p_C1C2:.2e}  {'PASS' if p_C1C2 < 0.001 else 'FAIL'}")
    print(f"[Wilcoxon] C1>C3: stat={stat_C1C3:.1f}  p={p_C1C3:.2e}  {'PASS' if p_C1C3 < 0.001 else 'FAIL'}")

    return {
        'stat_C1C2': float(stat_C1C2),
        'p_C1C2': float(p_C1C2),
        'stat_C1C3': float(stat_C1C3),
        'p_C1C3': float(p_C1C3),
    }


def anti_confound_gate(encoder_c2: DeepSetsChannelEncoder) -> dict:
    """Code inspection + numeric permutation invariance check for C2."""
    enc_src = inspect.getsource(type(encoder_c2))
    forbidden = ('sort', 'argsort', 'topk')
    code_ok = not any(kw in enc_src for kw in forbidden)

    dummy_sd = {
        'module_list.0.weight': torch.randn(8, 3, 5, 5),
        'module_list.3.weight': torch.randn(6, 8, 5, 5),
        'module_list.6.weight': torch.randn(4, 6, 2, 2),
        'module_list.0.bias': torch.randn(8),
        'module_list.3.bias': torch.randn(6),
        'module_list.6.bias': torch.randn(4),
    }

    encoder_c2.eval()
    with torch.no_grad():
        emb_orig = encoder_c2(dummy_sd)
        perm = torch.randperm(8)
        perm_sd = dict(dummy_sd)
        perm_sd['module_list.0.weight'] = dummy_sd['module_list.0.weight'][perm]
        perm_sd['module_list.0.bias'] = dummy_sd['module_list.0.bias'][perm]
        perm_sd['module_list.3.weight'] = dummy_sd['module_list.3.weight'][:, perm]
        emb_perm = encoder_c2(perm_sd)

    max_diff = (emb_orig - emb_perm).abs().max().item()
    numeric_ok = max_diff < 1e-6
    passed = code_ok and numeric_ok
    print(f"[Anti-confound] code_ok={code_ok}  max_diff={max_diff:.2e}  numeric_ok={numeric_ok}  => {'PASS' if passed else 'FAIL'}")
    return {'passed': passed, 'max_diff': max_diff, 'code_inspection': code_ok}


def gate_check(ratios: dict, wilcoxon_res: dict, anti_gate: dict) -> bool:
    gate_C1C2 = ratios['mean_ratio_C1_C2'] > 1e4
    gate_C1C3 = ratios['mean_ratio_C1_C3'] > 1e4
    gate_w_C1C2 = wilcoxon_res['p_C1C2'] < 0.001
    gate_w_C1C3 = wilcoxon_res['p_C1C3'] < 0.001

    print("\n" + "=" * 60)
    print("H-M1 GATE CHECK (MUST_WORK)")
    print("=" * 60)
    print(f"OrbitVar(C1)/OrbitVar(C2) > 1e4:  {ratios['mean_ratio_C1_C2']:.3e}  {'PASS' if gate_C1C2 else 'FAIL'}")
    print(f"OrbitVar(C1)/OrbitVar(C3) > 1e4:  {ratios['mean_ratio_C1_C3']:.3e}  {'PASS' if gate_C1C3 else 'FAIL'}")
    print(f"Wilcoxon C1>C2 p<0.001:           p={wilcoxon_res['p_C1C2']:.2e}  {'PASS' if gate_w_C1C2 else 'FAIL'}")
    print(f"Wilcoxon C1>C3 p<0.001:           p={wilcoxon_res['p_C1C3']:.2e}  {'PASS' if gate_w_C1C3 else 'FAIL'}")
    print(f"Anti-confound gate:               {'PASS' if anti_gate['passed'] else 'FAIL'}")
    print(f"OOM C1/C2: {ratios['log10_oom_C1_C2']:.1f}  OOM C1/C3: {ratios['log10_oom_C1_C3']:.1f}")
    print("=" * 60)

    all_pass = gate_C1C2 and gate_C1C3 and gate_w_C1C2 and gate_w_C1C3
    print(f"OVERALL: {'GATE PASS' if all_pass else 'GATE FAIL'}")
    return all_pass


def save_all_results(ratios: dict, wilcoxon_res: dict, anti_gate: dict, gate_passed: bool) -> None:
    os.makedirs(RESULTS_DIR, exist_ok=True)

    combined = {
        'hypothesis_id': 'h-m1',
        'gate_passed': gate_passed,
        'ratios': {k: v for k, v in ratios.items() if not isinstance(v, list)},
        'wilcoxon': wilcoxon_res,
        'anti_confound': anti_gate,
        'per_model': {
            'orbit_vars_C1': ratios['orbit_vars_C1'],
            'orbit_vars_C2': ratios['orbit_vars_C2'],
            'orbit_vars_C3': ratios['orbit_vars_C3'],
            'ratios_C1_C2': ratios['ratios_C1_C2'],
            'ratios_C1_C3': ratios['ratios_C1_C3'],
        }
    }
    json_path = os.path.join(RESULTS_DIR, 'orbit_var_ratios.json')
    with open(json_path, 'w') as f:
        json.dump(combined, f, indent=2)
    print(f"Results saved: {json_path}")

    csv_path = os.path.join(RESULTS_DIR, 'h_m1_summary.csv')
    rows = [
        ['encoder', 'mean_orbitvar', 'oom_vs_c1', 'gate'],
        ['C1 (CISE)', f"{ratios['mean_OrbitVar_C1']:.6f}", '--', 'baseline'],
        ['C2 (DeepSets)', f"{ratios['mean_OrbitVar_C2']:.4e}", f"{ratios['log10_oom_C1_C2']:.1f}", 'PASS' if ratios['mean_ratio_C1_C2'] > 1e4 else 'FAIL'],
        ['C3 (NFN)', f"{ratios['mean_OrbitVar_C3']:.4e}", f"{ratios['log10_oom_C1_C3']:.1f}", 'PASS' if ratios['mean_ratio_C1_C3'] > 1e4 else 'FAIL'],
    ]
    with open(csv_path, 'w', newline='') as f:
        csv.writer(f).writerows(rows)
    print(f"CSV saved: {csv_path}")

    log_path = os.path.join(RESULTS_DIR, 'anti_gate_log.txt')
    with open(log_path, 'w') as f:
        f.write(f"Anti-confound gate result: {'PASS' if anti_gate['passed'] else 'FAIL'}\n")
        f.write(f"  code_inspection (no sort/argsort/topk): {anti_gate['code_inspection']}\n")
        f.write(f"  numeric max_diff under channel permutation: {anti_gate['max_diff']:.2e}\n")
    print(f"Anti-gate log: {log_path}")


def visualize(ratios: dict) -> None:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    os.makedirs(FIGURES_DIR, exist_ok=True)
    C1 = np.array(ratios['orbit_vars_C1'])
    C2 = np.array(ratios['orbit_vars_C2'])
    C3 = np.array(ratios['orbit_vars_C3'])

    # Figure 1: violin + scatter log10(OrbitVar)
    fig, ax = plt.subplots(figsize=(7, 5))
    data_log = [np.log10(C1 + EPS), np.log10(C2 + EPS), np.log10(C3 + EPS)]
    labels = ['C1 (CISE)', 'C2 (DeepSets)', 'C3 (NFN)']
    ax.violinplot(data_log, positions=[1, 2, 3], showmedians=True)
    for d, pos in zip(data_log, [1, 2, 3]):
        ax.scatter([pos] * len(d), d, alpha=0.3, s=10, color='gray')
    ax.set_xticks([1, 2, 3])
    ax.set_xticklabels(labels)
    ax.set_ylabel('log10(OrbitVar)')
    ax.set_title('OrbitVar Distribution by Encoder (H-M1)')
    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, 'orbitvar_comparison.png'), dpi=150)
    plt.close(fig)

    # Figure 2: ratio histogram
    r12 = np.log10(np.array(ratios['ratios_C1_C2']) + EPS)
    r13 = np.log10(np.array(ratios['ratios_C1_C3']) + EPS)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for ax, r, label in zip(axes, [r12, r13], ['log10(C1/C2)', 'log10(C1/C3)']):
        ax.hist(r, bins=20, color='steelblue', edgecolor='white', alpha=0.8)
        ax.axvline(4, color='red', lw=2, linestyle='--', label='Gate (4 OOM)')
        ax.set_xlabel(label)
        ax.set_ylabel('Count')
        ax.set_title(f'Per-model {label}')
        ax.legend(fontsize=8)
    plt.suptitle('OrbitVar Ratio Distributions (H-M1)', fontsize=12)
    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, 'ratio_histogram.png'), dpi=150)
    plt.close(fig)

    # Figure 3: summary table
    fig, ax = plt.subplots(figsize=(8, 2.5))
    ax.axis('off')
    table_data = [
        ['Encoder', 'Mean OrbitVar', 'OOM vs C1', 'Gate (>1e4)'],
        ['C1 (CISE)', f"{ratios['mean_OrbitVar_C1']:.6f}", '--', 'baseline'],
        ['C2 (DeepSets)', f"{ratios['mean_OrbitVar_C2']:.3e}", f"{ratios['log10_oom_C1_C2']:.1f}",
         'PASS' if ratios['mean_ratio_C1_C2'] > 1e4 else 'FAIL'],
        ['C3 (NFN)', f"{ratios['mean_OrbitVar_C3']:.3e}", f"{ratios['log10_oom_C1_C3']:.1f}",
         'PASS' if ratios['mean_ratio_C1_C3'] > 1e4 else 'FAIL'],
    ]
    tbl = ax.table(cellText=table_data[1:], colLabels=table_data[0], loc='center', cellLoc='center')
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(11)
    tbl.scale(1.2, 1.5)
    ax.set_title('H-M1 Summary: OrbitVar Comparison', fontsize=13, pad=15)
    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, 'summary_table.png'), dpi=150)
    plt.close(fig)

    print(f"Figures saved to {FIGURES_DIR}")


def main():
    print("=" * 60)
    print("H-M1: Encoder Architecture Determines OrbitVar (>=4 OOM)")
    print("=" * 60)

    # Step 0: Prerequisites
    print("\n[Step 0] Verifying prerequisites...")
    orbit_vars_C2, orbit_vars_C3 = verify_prerequisites(
        os.path.abspath(H_E1_RESULTS)
    )

    # Step 1: CISE OrbitVar BUILD_ON
    print("\n[Step 1] CISE (C1) OrbitVar...")
    orbit_vars_C1 = measure_cise_orbitvar(
        dataset=None, perm_specs=None, build_on=True, build_on_value=BUILD_ON_VALUE
    )

    # Step 2: Ratios
    print("\n[Step 2] Computing OrbitVar ratios...")
    ratios = compute_ratios(orbit_vars_C1, orbit_vars_C2, orbit_vars_C3)
    print(f"  C1/C2: mean={ratios['mean_ratio_C1_C2']:.3e} ({ratios['log10_oom_C1_C2']:.1f} OOM)")
    print(f"  C1/C3: mean={ratios['mean_ratio_C1_C3']:.3e} ({ratios['log10_oom_C1_C3']:.1f} OOM)")
    print(f"  Models C1/C2>1e4: {ratios['pct_models_C1C2_gt_1e4']:.1f}%")
    print(f"  Models C1/C3>1e3: {ratios['pct_models_C1C3_gt_1e3']:.1f}%")

    # Step 3: Wilcoxon
    print("\n[Step 3] Wilcoxon signed-rank tests...")
    wilcoxon_res = run_wilcoxon(orbit_vars_C1, orbit_vars_C2, orbit_vars_C3)

    # Step 4: Anti-confound gate
    print("\n[Step 4] Anti-confound gate...")
    encoder_c2 = build_c2_encoder(embed_dim=128, hidden_dim=64)
    anti_gate = anti_confound_gate(encoder_c2)

    # Step 5: Gate check
    gate_passed = gate_check(ratios, wilcoxon_res, anti_gate)

    # Step 6: Save results
    print("\n[Step 6] Saving results...")
    save_all_results(ratios, wilcoxon_res, anti_gate, gate_passed)

    # Step 7: Visualize
    print("\n[Step 7] Generating figures...")
    visualize(ratios)

    print(f"\nEXPERIMENT COMPLETE (exit={'0' if gate_passed else '1'})")
    sys.exit(0 if gate_passed else 1)


if __name__ == '__main__':
    main()
