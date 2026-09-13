"""Run experiment: H-M2 Layer-wise Probe Sweep for Inverted-U Pattern."""

import os
import json
import torch
import numpy as np
import matplotlib.pyplot as plt
from transformers import AutoModelForCausalLM, AutoTokenizer

from config import CFG, LAYER_INDICES, set_seed
from data import load_triviaqa_splits, build_labeled_dataset_batched
from probe import extract_all_layers
from sweep import run_layer_sweep, bootstrap_auroc_ci, verify_inverted_u_pattern


def plot_gate_comparison(layer_aurocs: dict, gate_result: dict, cfg, out_dir: str):
    """Bar chart: L25/L60/L100 AUROC comparison."""
    os.makedirs(out_dir, exist_ok=True)

    early = gate_result["early_layer"]
    middle = gate_result["middle_layer"]
    final = gate_result["final_layer"]

    labels = [f"L_{early} (~25%)", f"L_{middle} (~60%)", f"L_{final} (100%)"]
    values = [layer_aurocs[early], layer_aurocs[middle], layer_aurocs[final]]
    colors = ["#FFC107", "#4CAF50" if gate_result["gate_satisfied"] else "#F44336", "#2196F3"]

    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(labels, values, color=colors)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f"{val:.4f}", ha="center", va="bottom", fontsize=11)

    ax.set_ylabel("AUROC")
    ax.set_ylim(0, 1)
    ax.set_title(f"Gate Comparison: L_60% > L_100% = {gate_result['gate_satisfied']}")

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "gate_comparison.png"), dpi=150)
    plt.close()


def plot_layer_auroc_curve(layer_aurocs: dict, cis: dict, cfg, out_dir: str):
    """Line plot: All 8 layers with CI error bars."""
    os.makedirs(out_dir, exist_ok=True)

    layers = sorted(layer_aurocs.keys())
    depths = [(l + 1) / cfg.num_layers * 100 for l in layers]
    aurocs = [layer_aurocs[l] for l in layers]

    ci_low = [cis[l][0] for l in layers]
    ci_high = [cis[l][1] for l in layers]
    yerr_low = [a - cl for a, cl in zip(aurocs, ci_low)]
    yerr_high = [ch - a for a, ch in zip(aurocs, ci_high)]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.errorbar(depths, aurocs, yerr=[yerr_low, yerr_high], fmt="o-", capsize=5,
                color="#2196F3", linewidth=2, markersize=8, label="AUROC")

    ax.set_xlabel("Layer Depth (%)")
    ax.set_ylabel("AUROC")
    ax.set_title("Layer-wise AUROC with 95% CI")
    ax.set_xlim(0, 105)
    ax.set_ylim(0.5, 1.0)
    ax.grid(True, alpha=0.3)
    ax.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "layer_auroc_curve.png"), dpi=150)
    plt.close()


def plot_inverted_u(layer_aurocs: dict, cfg, out_dir: str):
    """Polynomial fit showing inverted-U pattern."""
    os.makedirs(out_dir, exist_ok=True)

    layers = sorted(layer_aurocs.keys())
    depths = np.array([(l + 1) / cfg.num_layers * 100 for l in layers])
    aurocs = np.array([layer_aurocs[l] for l in layers])

    coeffs = np.polyfit(depths, aurocs, 2)
    poly = np.poly1d(coeffs)
    x_fit = np.linspace(0, 100, 100)
    y_fit = poly(x_fit)

    peak_x = -coeffs[1] / (2 * coeffs[0]) if coeffs[0] != 0 else 50

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(depths, aurocs, s=100, color="#2196F3", zorder=3, label="Observed")
    ax.plot(x_fit, y_fit, "--", color="#FF9800", linewidth=2, label=f"Poly fit (deg=2)")
    ax.axvline(x=peak_x, color="#4CAF50", linestyle=":", linewidth=2, label=f"Fitted peak: {peak_x:.1f}%")

    ax.set_xlabel("Layer Depth (%)")
    ax.set_ylabel("AUROC")
    ax.set_title("Inverted-U Pattern: Polynomial Fit")
    ax.set_xlim(0, 105)
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "inverted_u_fit.png"), dpi=150)
    plt.close()


def main():
    print("=" * 60)
    print("H-M2: Layer-wise Probe Sweep for Inverted-U Pattern")
    print("=" * 60)

    set_seed(CFG.seed)

    os.makedirs(CFG.figures_dir, exist_ok=True)
    os.makedirs(CFG.outputs_dir, exist_ok=True)

    print(f"\nLayer indices to probe: {LAYER_INDICES}")
    print(f"Layer depths: {CFG.layer_depths}")

    print("\n[1/6] Loading model and tokenizer...")
    dtype_map = {"float16": torch.float16, "bfloat16": torch.bfloat16, "float32": torch.float32}
    model = AutoModelForCausalLM.from_pretrained(
        CFG.model_name,
        torch_dtype=dtype_map.get(CFG.torch_dtype, torch.float16),
        device_map=CFG.device_map,
        trust_remote_code=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(CFG.model_name, trust_remote_code=True)
    print(f"Model loaded: {CFG.model_name}, layers: {len(model.model.layers)}")

    print("\n[2/6] Loading and labeling datasets...")
    train_ds, val_ds = load_triviaqa_splits(CFG.n_train, CFG.n_val)

    print(f"Building labeled train set ({CFG.n_train} samples)...")
    train_examples = build_labeled_dataset_batched(
        model, tokenizer, train_ds, CFG.n_train,
        batch_size=8, max_new_tokens=CFG.max_new_tokens
    )

    print(f"Building labeled val set ({CFG.n_val} samples)...")
    val_examples = build_labeled_dataset_batched(
        model, tokenizer, val_ds, CFG.n_val,
        batch_size=8, max_new_tokens=CFG.max_new_tokens
    )

    train_correct = sum(e["label"] for e in train_examples)
    val_correct = sum(e["label"] for e in val_examples)
    print(f"Train: {train_correct}/{len(train_examples)} correct ({train_correct/len(train_examples)*100:.1f}%)")
    print(f"Val: {val_correct}/{len(val_examples)} correct ({val_correct/len(val_examples)*100:.1f}%)")

    print("\n[3/6] Extracting hidden states at all layers...")
    train_states, train_labels = extract_all_layers(
        model, tokenizer, LAYER_INDICES, train_examples, batch_size=CFG.extraction_batch_size
    )
    val_states, val_labels = extract_all_layers(
        model, tokenizer, LAYER_INDICES, val_examples, batch_size=CFG.extraction_batch_size
    )

    for idx in LAYER_INDICES:
        print(f"  Layer {idx}: train {train_states[idx].shape}, val {val_states[idx].shape}")

    print("\n[4/6] Running layer sweep (training probes)...")
    sweep_results = run_layer_sweep(train_states, train_labels, val_states, val_labels, CFG)

    layer_aurocs = {idx: res["auroc"] for idx, res in sweep_results.items()}

    print("\n[5/6] Computing bootstrap CIs...")
    cis = {}
    for idx, res in sweep_results.items():
        ci_low, ci_high = bootstrap_auroc_ci(res["labels_np"], res["preds"], CFG.n_bootstrap, CFG.seed)
        cis[idx] = (ci_low, ci_high)
        print(f"  Layer {idx}: AUROC = {res['auroc']:.4f} [95% CI: {ci_low:.4f} - {ci_high:.4f}]")

    print("\n[6/6] Verifying inverted-U pattern (gate check)...")
    gate_result = verify_inverted_u_pattern(layer_aurocs, CFG.num_layers)

    print("\n" + "=" * 60)
    print("GATE VERIFICATION RESULTS")
    print("=" * 60)
    print(f"Early layer (L_{gate_result['early_layer']}):   AUROC = {gate_result['auroc_early']:.4f}")
    print(f"Middle layer (L_{gate_result['middle_layer']}): AUROC = {gate_result['auroc_middle']:.4f}")
    print(f"Final layer (L_{gate_result['final_layer']}):  AUROC = {gate_result['auroc_final']:.4f}")
    print(f"\nPrimary Gate: L_60% > L_100% = {gate_result['middle_beats_final']}")
    print(f"Secondary: L_60% > L_25% = {gate_result['middle_beats_early']}")
    print(f"Peak layer: {gate_result['peak_layer']} ({gate_result['peak_depth_pct']:.1f}% depth)")
    print(f"Inverted-U detected: {gate_result['inverted_u_detected']}")
    print(f"\n>>> GATE SATISFIED: {gate_result['gate_satisfied']} <<<")

    print("\nGenerating figures...")
    plot_gate_comparison(layer_aurocs, gate_result, CFG, CFG.figures_dir)
    plot_layer_auroc_curve(layer_aurocs, cis, CFG, CFG.figures_dir)
    plot_inverted_u(layer_aurocs, CFG, CFG.figures_dir)

    results = {
        "hypothesis_id": "h-m2",
        "gate_type": "SHOULD_WORK",
        "layer_indices": LAYER_INDICES,
        "layer_depths": CFG.layer_depths,
        "layer_aurocs": {str(k): v for k, v in layer_aurocs.items()},
        "layer_cis": {str(k): list(v) for k, v in cis.items()},
        "gate_result": gate_result,
        "train_size": len(train_examples),
        "val_size": len(val_examples),
        "config": {
            "seed": CFG.seed,
            "lr": CFG.lr,
            "weight_decay": CFG.weight_decay,
            "epochs": CFG.epochs,
            "batch_size": CFG.batch_size,
            "n_bootstrap": CFG.n_bootstrap,
        },
    }

    results_path = os.path.join(CFG.outputs_dir, "results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {results_path}")

    print("\n" + "=" * 60)
    print("H-M2 EXPERIMENT COMPLETE")
    print("=" * 60)

    return results


if __name__ == "__main__":
    main()
