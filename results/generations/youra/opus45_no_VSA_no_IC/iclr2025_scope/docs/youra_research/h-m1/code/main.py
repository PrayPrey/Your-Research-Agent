"""Main experiment orchestration for h-m1."""
import json
import os
import sys
import torch
import gc

from config import MODEL_SIZES, RANKS, TrainConfig, DataConfig, set_seed, SEED
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


def run_single_combo(
    base_model, tokenizer, rank: int, train_loader, val_loader, val_data, cfg: TrainConfig
) -> dict:
    """Train and evaluate one (model, rank) combination."""
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
    """Full 4x6 grid sweep."""
    set_seed(SEED)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(figure_dir, exist_ok=True)

    print("Loading SQuAD v2.0 dataset...")
    data_cfg = DataConfig()
    train_ds, val_ds = load_squad_v2(data_cfg)
    print(f"  Train: {len(train_ds)}, Val: {len(val_ds)}")

    train_cfg = TrainConfig()
    results = {}

    for size in MODEL_SIZES:
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

        for rank in RANKS:
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
    correlation = compute_correlation(results)
    print(f"  Pearson r = {correlation['pearson_r']:.4f}")
    print(f"  p-value = {correlation['p_value']:.6f}")
    print(f"  Pass = {correlation['pass']}")

    optimal_ranks = {}
    for size in MODEL_SIZES:
        f1_list = [results[size][r]["f1"] for r in RANKS]
        optimal_ranks[size] = find_optimal_rank(f1_list)
    print(f"  Optimal ranks: {optimal_ranks}")

    output = {
        "results": results,
        "optimal_ranks": optimal_ranks,
        "correlation": correlation,
    }

    result_path = os.path.join(output_dir, "results.json")
    with open(result_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {result_path}")

    print("\nGenerating figures...")
    plot_gate_metrics(results, correlation, os.path.join(figure_dir, "gate_metrics.png"))
    plot_rank_f1_curves(results, os.path.join(figure_dir, "rank_f1_curves.png"))
    plot_entropy_heatmap(results, os.path.join(figure_dir, "entropy_heatmap.png"))
    plot_optimal_rank_bar(results, os.path.join(figure_dir, "optimal_rank_bar.png"))
    print("Figures saved.")

    return output


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "..", "outputs")
    figure_dir = os.path.join(script_dir, "..", "figures")

    result = run_experiment(output_dir, figure_dir)

    print("\n" + "="*60)
    print("EXPERIMENT SUMMARY")
    print("="*60)
    print(f"Pearson r: {result['correlation']['pearson_r']:.4f}")
    print(f"p-value: {result['correlation']['p_value']:.6f}")
    print(f"Gate PASS: {result['correlation']['pass']}")

    sys.exit(0 if result["correlation"]["pass"] else 1)


if __name__ == "__main__":
    main()
