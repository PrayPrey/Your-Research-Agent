"""
h-e1 entry point: per-layer attention entropy stability experiment.

Measures Spearman ρ of per-layer mean attention entropy across 3 non-overlapping
100-sequence calibration subsets from WikiText-103 validation split.

Gate: min(rho_AB, rho_AC, rho_BC) >= 0.8
"""
import os
import sys
import time

import torch
from transformers import AutoModelForCausalLM

from config import ExperimentConfig, ModelConfig
from data import chunk_and_split, load_wikitext103
from entropy import score_subset
from report import compute_spearman, generate_figures, save_results_json


def main():
    cfg = ExperimentConfig()
    model_cfg = ModelConfig()

    print("=" * 60)
    print("h-e1: Per-Layer Attention Entropy Stability")
    print("=" * 60)
    print(f"Model: {model_cfg.model_name}")
    print(f"Dataset: Salesforce/wikitext wikitext-103-raw-v1 (validation)")
    print(f"Subsets: {cfg.n_subsets} x {cfg.subset_size} sequences, seqlen={cfg.seqlen}")
    print(f"Gate threshold: Spearman ρ ≥ {cfg.gate_threshold}")
    print()

    # Step 1: Load data
    print("Loading WikiText-103 validation split...")
    t0 = time.time()
    texts = load_wikitext103()
    print(f"  Loaded {len(texts)} text entries ({time.time()-t0:.1f}s)")

    print("Tokenizing and chunking...")
    t0 = time.time()
    subset_A, subset_B, subset_C = chunk_and_split(
        texts,
        tokenizer_name=model_cfg.model_name,
        seqlen=cfg.seqlen,
        n_subsets=cfg.n_subsets,
        subset_size=cfg.subset_size,
    )
    print(f"  Subsets ready: A={len(subset_A)}, B={len(subset_B)}, C={len(subset_C)} ({time.time()-t0:.1f}s)")

    # Step 2: Load model
    print(f"\nLoading {model_cfg.model_name}...")
    t0 = time.time()
    import torch
    dtype_map = {"float16": torch.float16, "bfloat16": torch.bfloat16, "float32": torch.float32}
    torch_dtype = dtype_map.get(model_cfg.torch_dtype, torch.float16)

    model = AutoModelForCausalLM.from_pretrained(
        model_cfg.model_name,
        attn_implementation=model_cfg.attn_implementation,
        torch_dtype=torch_dtype,
        device_map=model_cfg.device_map,
        token=model_cfg.hf_token,
    )
    model.eval()
    print(f"  Model loaded ({time.time()-t0:.1f}s)")

    # Step 3: Score subsets
    print("\nScoring Subset A (100 sequences)...")
    t0 = time.time()
    entropy_A = score_subset(model, subset_A, eps=cfg.eps, verbose=True)
    print(f"  Subset A done ({time.time()-t0:.1f}s)")

    print("\nScoring Subset B (100 sequences)...")
    t0 = time.time()
    entropy_B = score_subset(model, subset_B, eps=cfg.eps, verbose=True)
    print(f"  Subset B done ({time.time()-t0:.1f}s)")

    print("\nScoring Subset C (100 sequences)...")
    t0 = time.time()
    entropy_C = score_subset(model, subset_C, eps=cfg.eps, verbose=True)
    print(f"  Subset C done ({time.time()-t0:.1f}s)")

    # Step 4: Compute Spearman ρ
    print("\nComputing Spearman correlations...")
    spearman = compute_spearman(entropy_A, entropy_B, entropy_C, gate_threshold=cfg.gate_threshold)

    print(f"  ρ(A,B) = {spearman['rho_AB']:.4f}  (p={spearman['p_AB']:.4f})")
    print(f"  ρ(A,C) = {spearman['rho_AC']:.4f}  (p={spearman['p_AC']:.4f})")
    print(f"  ρ(B,C) = {spearman['rho_BC']:.4f}  (p={spearman['p_BC']:.4f})")
    print(f"  min(ρ) = {spearman['min_rho']:.4f}")
    print(f"  mean(ρ) = {spearman['mean_rho']:.4f}")

    # Step 5: Save results and figures
    out_dir = cfg.output_dir
    os.makedirs(out_dir, exist_ok=True)
    results_path = os.path.join(out_dir, "results.json")
    save_results_json(spearman, entropy_A, entropy_B, entropy_C, out_path=results_path)

    figures_dir = cfg.figures_dir
    generate_figures(spearman, entropy_A, entropy_B, entropy_C, figures_dir=figures_dir)

    # Step 6: Gate verdict
    print()
    print("=" * 60)
    gate_str = "PASS" if spearman["gate_pass"] else "FAIL"
    print(f"GATE: {gate_str}  (min_rho={spearman['min_rho']:.4f}, threshold={cfg.gate_threshold})")
    print("=" * 60)

    return 0 if spearman["gate_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
