"""Quick h-m1 experiment: 2 models x 3 ranks for faster validation."""
import json
import os
import sys
import torch
import gc

from config import MODEL_PARAMS, TrainConfig, DataConfig, set_seed, SEED
from data import load_squad_v2, tokenize_qa, make_dataloader
from model import load_base_model, create_lora_model
from train import train_qa
from evaluate import evaluate_qa
from entropy import compute_attention_entropy
from correlate import compute_correlation, find_optimal_rank
from visualize import (
    plot_gate_metrics,
    plot_rank_f1_curves,
    plot_entropy_heatmap,
    plot_optimal_rank_bar,
)

QUICK_MODEL_SIZES = ["1b", "2.8b"]
QUICK_RANKS = [8, 32, 64]
QUICK_MODEL_PARAMS = {k: MODEL_PARAMS[k] for k in QUICK_MODEL_SIZES}


def run_single_combo(
    base_model, tokenizer, rank: int, train_loader, val_loader, val_data, cfg: TrainConfig
) -> dict:
    print(f"    Creating LoRA model with rank={rank}")
    lora_model = create_lora_model(base_model, rank, cfg)

    print(f"    Training...")
    lora_model, history = train_qa(lora_model, train_loader, val_loader, cfg, tokenizer)

    print(f"    Evaluating F1...")
    f1 = evaluate_qa(lora_model, tokenizer, val_data, batch_size=8)
    print(f"    F1 = {f1:.4f}")

    print(f"    Computing attention entropy...")
    sample_batch = next(iter(val_loader))
    device = next(lora_model.parameters()).device
    entropy = compute_attention_entropy(
        lora_model,
        sample_batch["input_ids"].to(device),
        sample_batch["attention_mask"].to(device),
    )
    print(f"    Entropy = {entropy:.4f}")

    del lora_model
    gc.collect()
    torch.cuda.empty_cache()

    return {"f1": f1, "entropy": entropy, "history": history}


def run_experiment(output_dir: str = "../outputs", figure_dir: str = "../figures") -> dict:
    set_seed(SEED)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(figure_dir, exist_ok=True)

    print("Loading SQuAD v2.0 dataset (reduced)...")
    data_cfg = DataConfig(train_n=2000, val_n=500)
    train_ds, val_ds = load_squad_v2(data_cfg)
    print(f"  Train: {len(train_ds)}, Val: {len(val_ds)}")

    train_cfg = TrainConfig(epochs=2)
    results = {}

    for size in QUICK_MODEL_SIZES:
        print(f"\n{'='*60}")
        print(f"Model: {size}")
        print(f"{'='*60}")

        print(f"  Loading base model...")
        base_model, tokenizer = load_base_model(size)

        print(f"  Tokenizing data...")
        train_tok = tokenize_qa(train_ds, tokenizer, data_cfg.max_len)
        val_tok = tokenize_qa(val_ds, tokenizer, data_cfg.max_len)

        train_loader = make_dataloader(train_tok, train_cfg.batch_size, shuffle=True)
        val_loader = make_dataloader(val_tok, train_cfg.batch_size, shuffle=False)

        results[size] = {}

        for rank in QUICK_RANKS:
            print(f"\n  --- Rank: {rank} ---")
            combo_result = run_single_combo(
                base_model, tokenizer, rank, train_loader, val_loader, val_ds, train_cfg
            )
            results[size][rank] = {
                "f1": combo_result["f1"],
                "entropy": combo_result["entropy"],
            }

        del base_model
        gc.collect()
        torch.cuda.empty_cache()

    print("\n" + "="*60)
    print("Computing correlation...")

    entropies_at_optimal = []
    sizes = []
    optimal_ranks = {}

    for size in QUICK_MODEL_SIZES:
        f1_list = [results[size][r]["f1"] for r in QUICK_RANKS]
        optimal_idx = f1_list.index(max(f1_list))
        optimal_rank = QUICK_RANKS[optimal_idx]
        optimal_ranks[size] = optimal_rank
        optimal_entropy = results[size][optimal_rank]["entropy"]
        entropies_at_optimal.append(optimal_entropy)
        sizes.append(QUICK_MODEL_PARAMS[size])

    from scipy.stats import pearsonr
    r, p = pearsonr(sizes, entropies_at_optimal)

    correlation = {
        "pearson_r": float(r),
        "p_value": float(p),
        "pass": bool(r > 0.6 and p < 0.05),
        "entropies_at_optimal": entropies_at_optimal,
        "model_sizes": sizes,
        "note": "Quick run (2 models x 3 ranks) - insufficient for significance"
    }

    print(f"  Pearson r = {correlation['pearson_r']:.4f}")
    print(f"  p-value = {correlation['p_value']:.6f}")
    print(f"  Pass = {correlation['pass']}")
    print(f"  Note: Only 2 data points - p-value unreliable")
    print(f"  Optimal ranks: {optimal_ranks}")

    output = {
        "results": results,
        "optimal_ranks": optimal_ranks,
        "correlation": correlation,
        "config": {
            "model_sizes": QUICK_MODEL_SIZES,
            "ranks": QUICK_RANKS,
            "train_n": data_cfg.train_n,
            "val_n": data_cfg.val_n,
            "epochs": train_cfg.epochs,
        }
    }

    result_path = os.path.join(output_dir, "results_quick.json")
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
    print("QUICK EXPERIMENT SUMMARY")
    print("="*60)
    print(f"Pearson r: {result['correlation']['pearson_r']:.4f}")
    print(f"p-value: {result['correlation']['p_value']:.6f}")
    print(f"Direction: {'positive' if result['correlation']['pearson_r'] > 0 else 'negative'}")
    print(f"Note: 2-point correlation - use full run for gate verdict")

    sys.exit(0)


if __name__ == "__main__":
    main()
