#!/usr/bin/env python3
"""
H-M1: Attention Pattern Analysis Experiment
Hypothesis: Attention pattern structure differs between encoder (bidirectional) and decoder (causal)
"""
import json
import os
import sys
import torch
import numpy as np
from datetime import datetime

from config import ExperimentConfig, FIGURE_FILES
from data_loader import load_sst2_validation
from models import load_bert, load_gpt2
from attention_extraction import extract_attentions
from sparsity_metrics import (
    compute_attention_sparsity,
    per_layer_sparsity,
    attention_entropy,
)
from verify import verify_attention_structure
from visualize import (
    plot_gate_comparison,
    plot_attention_heatmaps,
    plot_layerwise_sparsity,
    plot_entropy_histogram,
)


def main():
    print("=" * 60)
    print("H-M1: Attention Pattern Analysis")
    print("=" * 60)

    cfg = ExperimentConfig()

    # Set device
    device = cfg.device if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")

    # Set seed
    torch.manual_seed(cfg.seed)
    np.random.seed(cfg.seed)

    # Ensure output dirs exist
    os.makedirs(cfg.figures_dir, exist_ok=True)

    # Load data
    print("\n[1/6] Loading SST-2 validation set...")
    texts = load_sst2_validation()
    print(f"  Loaded {len(texts)} samples")

    # Load models
    print("\n[2/6] Loading models...")
    bert_model, bert_tokenizer = load_bert()
    gpt2_model, gpt2_tokenizer = load_gpt2()
    print("  BERT and GPT-2 loaded with output_attentions=True")

    # Extract attentions
    print("\n[3/6] Extracting BERT attentions...")
    bert_attns = extract_attentions(
        bert_model, bert_tokenizer, texts,
        max_length=cfg.max_length, device=device
    )

    print("\n[4/6] Extracting GPT-2 attentions...")
    gpt2_attns = extract_attentions(
        gpt2_model, gpt2_tokenizer, texts,
        max_length=cfg.max_length, device=device
    )

    # Compute metrics
    print("\n[5/6] Computing sparsity metrics...")
    bert_metrics = compute_attention_sparsity(bert_attns)
    gpt2_metrics = compute_attention_sparsity(gpt2_attns)

    bert_layers = per_layer_sparsity(bert_attns, num_layers=cfg.num_layers)
    gpt2_layers = per_layer_sparsity(gpt2_attns, num_layers=cfg.num_layers)

    print(f"  BERT upper_sparsity: {bert_metrics['upper_sparsity']:.6f}")
    print(f"  GPT-2 upper_sparsity: {gpt2_metrics['upper_sparsity']:.6f}")

    # Gate verification
    gate_result = verify_attention_structure(bert_metrics, gpt2_metrics)
    print(f"\n  Gate: {'PASS' if gate_result['gate_pass'] else 'FAIL'}")
    print(f"    BERT pass (<0.10): {gate_result['bert_pass']}")
    print(f"    GPT-2 pass (>0.99): {gate_result['gpt2_pass']}")

    # Compute entropy for visualization
    bert_entropies = []
    gpt2_entropies = []
    for ba in bert_attns[:100]:  # Sample for entropy
        for layer_attn in ba:
            bert_entropies.append(attention_entropy(layer_attn))
    for ga in gpt2_attns[:100]:
        for layer_attn in ga:
            gpt2_entropies.append(attention_entropy(layer_attn))
    bert_entropy_tensor = torch.cat(bert_entropies, dim=0)
    gpt2_entropy_tensor = torch.cat(gpt2_entropies, dim=0)

    # Generate visualizations
    print("\n[6/6] Generating visualizations...")

    # Required: gate comparison
    plot_gate_comparison(
        bert_metrics, gpt2_metrics,
        os.path.join(cfg.figures_dir, FIGURE_FILES["gate_comparison"])
    )
    print(f"  Saved: {FIGURE_FILES['gate_comparison']}")

    # Attention heatmaps (use first sample)
    sample_text = texts[0]
    bert_tokens = bert_tokenizer.tokenize(sample_text)[:20]
    gpt2_tokens = gpt2_tokenizer.tokenize(sample_text)[:20]
    plot_attention_heatmaps(
        bert_attns[0][0],  # First sample, first layer
        gpt2_attns[0][0],
        bert_tokens,
        gpt2_tokens,
        os.path.join(cfg.figures_dir, FIGURE_FILES["attention_heatmaps"])
    )
    print(f"  Saved: {FIGURE_FILES['attention_heatmaps']}")

    # Layerwise sparsity
    plot_layerwise_sparsity(
        bert_layers, gpt2_layers,
        os.path.join(cfg.figures_dir, FIGURE_FILES["layerwise_sparsity"])
    )
    print(f"  Saved: {FIGURE_FILES['layerwise_sparsity']}")

    # Entropy histogram
    plot_entropy_histogram(
        bert_entropy_tensor, gpt2_entropy_tensor,
        os.path.join(cfg.figures_dir, FIGURE_FILES["entropy_histogram"])
    )
    print(f"  Saved: {FIGURE_FILES['entropy_histogram']}")

    # Build results
    results = {
        "hypothesis_id": "h-m1",
        "hypothesis": "Attention pattern structure differs between encoder (bidirectional) and decoder (causal)",
        "timestamp": datetime.now().isoformat(),
        "config": {
            "dataset": f"{cfg.dataset_name}/{cfg.dataset_config}",
            "split": cfg.split,
            "num_samples": len(texts),
            "device": device,
            "seed": cfg.seed,
        },
        "bert_metrics": {
            "model_id": cfg.bert_model_id,
            "upper_sparsity": bert_metrics["upper_sparsity"],
            "overall_sparsity": bert_metrics["overall_sparsity"],
            "is_causal": bert_metrics["is_causal"],
            "per_layer_sparsity": bert_layers,
        },
        "gpt2_metrics": {
            "model_id": cfg.gpt2_model_id,
            "upper_sparsity": gpt2_metrics["upper_sparsity"],
            "overall_sparsity": gpt2_metrics["overall_sparsity"],
            "is_causal": gpt2_metrics["is_causal"],
            "per_layer_sparsity": gpt2_layers,
        },
        "gate_verification": gate_result,
        "figures": list(FIGURE_FILES.values()),
    }

    # Convert numpy types to Python types for JSON
    def convert_types(obj):
        if isinstance(obj, dict):
            return {k: convert_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_types(v) for v in obj]
        elif isinstance(obj, (np.bool_, np.integer)):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, bool):
            return bool(obj)
        return obj

    results = convert_types(results)

    # Save results
    with open(cfg.results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {cfg.results_path}")

    # Generate report
    report = f"""# H-M1 Validation Report

**Hypothesis:** Attention pattern structure differs between encoder (bidirectional) and decoder (causal)

**Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Summary

| Metric | BERT | GPT-2 |
|--------|------|-------|
| Upper Triangle Sparsity | {bert_metrics['upper_sparsity']:.6f} | {gpt2_metrics['upper_sparsity']:.6f} |
| Is Causal | {bert_metrics['is_causal']} | {gpt2_metrics['is_causal']} |

## Gate Verification

- **BERT Pass** (<0.10): {gate_result['bert_pass']}
- **GPT-2 Pass** (>0.99): {gate_result['gpt2_pass']}
- **Gate Result:** {'PASS' if gate_result['gate_pass'] else 'FAIL'}
- **Sparsity Difference:** {gate_result['sparsity_difference']:.6f}

## Interpretation

{'BERT shows bidirectional attention (low upper-triangle sparsity) while GPT-2 shows causal attention (high upper-triangle sparsity near 1.0). The hypothesis is confirmed.' if gate_result['gate_pass'] else 'Gate failed. Check thresholds or model behavior.'}

## Figures

- `gate_comparison.png`: Bar chart comparing sparsity
- `attention_heatmaps.png`: Sample attention patterns
- `layerwise_sparsity.png`: Per-layer breakdown
- `entropy_histogram.png`: Attention entropy distribution

## Config

- Dataset: {cfg.dataset_name}/{cfg.dataset_config} ({len(texts)} samples)
- Device: {device}
- Seed: {cfg.seed}
"""

    with open(cfg.report_path, "w") as f:
        f.write(report)
    print(f"Report saved: {cfg.report_path}")

    print("\n" + "=" * 60)
    if gate_result["gate_pass"]:
        print("EXPERIMENT COMPLETE: Gate PASSED")
    else:
        print("EXPERIMENT COMPLETE: Gate FAILED")
    print("=" * 60)

    return 0 if gate_result["gate_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
