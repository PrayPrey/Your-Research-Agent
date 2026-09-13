"""h-m1 experiment: Measure attention entropy at different ranks WITHOUT training.
This tests whether entropy correlates with model size at initialization."""
import json
import os
import sys
import torch
import gc

from config import MODEL_SIZES, MODEL_PARAMS, RANKS, set_seed, SEED
from model import load_base_model, create_lora_model
from entropy import compute_attention_entropy

TEST_MODEL_SIZES = ["1b", "2.8b", "6.9b"]
TEST_RANKS = [8, 32, 128]


def run_experiment(output_dir: str = "../outputs", figure_dir: str = "../figures") -> dict:
    set_seed(SEED)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(figure_dir, exist_ok=True)

    test_input = "The quick brown fox jumps over the lazy dog. This is a test sentence for measuring attention patterns across different model sizes."

    results = {}

    for size in TEST_MODEL_SIZES:
        print(f"\n{'='*60}")
        print(f"Model: {size}")
        print(f"{'='*60}")

        print(f"  Loading base model...")
        base_model, tokenizer = load_base_model(size)

        inputs = tokenizer(test_input, return_tensors="pt", padding="max_length", max_length=128, truncation=True)
        device = next(base_model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}

        results[size] = {}

        for rank in TEST_RANKS:
            print(f"\n  --- Rank: {rank} ---")
            print(f"    Creating LoRA model...")
            lora_model = create_lora_model(base_model, rank)

            print(f"    Computing attention entropy...")
            entropy = compute_attention_entropy(
                lora_model,
                inputs["input_ids"],
                inputs["attention_mask"],
            )
            print(f"    Entropy = {entropy:.6f}")

            results[size][rank] = {"entropy": entropy}

            del lora_model
            gc.collect()
            torch.cuda.empty_cache()

        del base_model
        gc.collect()
        torch.cuda.empty_cache()

    print("\n" + "="*60)
    print("Computing correlation (entropy at highest rank vs model size)...")

    from scipy.stats import pearsonr
    import numpy as np

    highest_rank = max(TEST_RANKS)
    entropies = [results[size][highest_rank]["entropy"] for size in TEST_MODEL_SIZES]
    sizes = [MODEL_PARAMS[size] for size in TEST_MODEL_SIZES]

    print(f"  Model sizes: {sizes}")
    print(f"  Entropies at rank {highest_rank}: {entropies}")

    valid_idx = [i for i, e in enumerate(entropies) if e == e and e > 0]
    if len(valid_idx) >= 2:
        valid_entropies = [entropies[i] for i in valid_idx]
        valid_sizes = [sizes[i] for i in valid_idx]
        r, p = pearsonr(valid_sizes, valid_entropies)
    else:
        r, p = float("nan"), float("nan")

    correlation = {
        "pearson_r": float(r) if r == r else None,
        "p_value": float(p) if p == p else None,
        "pass": bool(r > 0.6 and p < 0.05) if (r == r and p == p) else False,
        "entropies": entropies,
        "model_sizes": sizes,
        "rank_used": highest_rank,
        "note": "No training - measuring initialization entropy"
    }

    print(f"\n  Pearson r = {correlation['pearson_r']}")
    print(f"  p-value = {correlation['p_value']}")
    print(f"  Pass = {correlation['pass']}")

    output = {
        "results": results,
        "correlation": correlation,
        "config": {
            "model_sizes": TEST_MODEL_SIZES,
            "ranks": TEST_RANKS,
            "training": False,
        }
    }

    result_path = os.path.join(output_dir, "results_notrain.json")
    with open(result_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {result_path}")

    return output


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "..", "outputs")
    figure_dir = os.path.join(script_dir, "..", "figures")

    result = run_experiment(output_dir, figure_dir)

    print("\n" + "="*60)
    print("NO-TRAIN EXPERIMENT SUMMARY")
    print("="*60)
    print(f"Pearson r: {result['correlation']['pearson_r']}")
    print(f"p-value: {result['correlation']['p_value']}")
    print(f"Note: Tests initialization entropy only")

    sys.exit(0)


if __name__ == "__main__":
    main()
