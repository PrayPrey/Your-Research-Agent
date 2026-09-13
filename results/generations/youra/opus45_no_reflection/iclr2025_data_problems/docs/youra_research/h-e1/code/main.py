"""Main experiment script for H-E1: Architecture-Method Interaction Existence.

This script runs the full pipeline:
1. Load SST-2 dataset with 5% label noise
2. Fine-tune BERT and GPT-2 across 5 seeds
3. Compute TRAK, EK-FAC, TracIn self-influence scores
4. Evaluate mislabeled detection AUC
5. Statistical testing (paired t-test, Cohen's d)
6. Generate visualizations
7. Gate check (MUST_WORK)
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime

import torch

from config import CONFIG
from data import load_sst2, inject_label_noise, tokenize_dataset, get_loaders
from model import build_bert, build_gpt2
from train import run_all_seeds, set_seed
from attribution import compute_attribution
from evaluate import mislabeled_auc, run_gate_check
from visualize import plot_auc_comparison, plot_method_arch_heatmap, plot_diff_significance


def main(args):
    """Run full experiment pipeline."""
    start_time = time.time()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")
    print(f"Seeds: {args.seeds}")
    print(f"Methods: {args.methods}")

    # Create output directories
    os.makedirs(CONFIG["checkpoint_dir"], exist_ok=True)
    os.makedirs(CONFIG["figures_dir"], exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    # =========================================================================
    # 1. Load and prepare data
    # =========================================================================
    print("\n" + "="*60)
    print("STEP 1: Loading SST-2 dataset")
    print("="*60)

    dataset = load_sst2()
    print(f"Train samples: {len(dataset['train'])}")
    print(f"Validation samples: {len(dataset['validation'])}")

    # Inject label noise
    noisy_train, mislabeled_indices = inject_label_noise(
        dataset["train"],
        rate=CONFIG["noise_rate"],
        seed=CONFIG["noise_seed"]
    )
    print(f"Mislabeled samples: {len(mislabeled_indices)} ({CONFIG['noise_rate']*100}%)")

    # =========================================================================
    # 2. Train models
    # =========================================================================
    print("\n" + "="*60)
    print("STEP 2: Training models")
    print("="*60)

    results = {method: {"bert": [], "gpt2": []} for method in args.methods}

    for arch in args.architectures:
        print(f"\n{'='*40}")
        print(f"Architecture: {arch.upper()}")
        print(f"{'='*40}")

        # Build tokenizer
        if arch == "bert":
            _, tokenizer = build_bert()
        else:
            _, tokenizer = build_gpt2()

        # Tokenize data
        train_tokenized = tokenize_dataset(noisy_train, tokenizer, CONFIG["max_length"])
        val_tokenized = tokenize_dataset(dataset["validation"], tokenizer, CONFIG["max_length"])

        train_loader, val_loader = get_loaders(
            train_tokenized, val_tokenized, CONFIG["batch_size"]
        )

        # Train for each seed
        for seed in args.seeds:
            print(f"\n--- Seed {seed} ---")

            # Check for existing checkpoint
            ckpt_path = os.path.join(CONFIG["checkpoint_dir"], f"{arch}_seed{seed}.pt")

            if os.path.exists(ckpt_path) and not args.retrain:
                print(f"Loading checkpoint: {ckpt_path}")
                if arch == "bert":
                    model, _ = build_bert()
                else:
                    model, _ = build_gpt2()
                model.load_state_dict(torch.load(ckpt_path, map_location=device))
                model = model.to(device)
            else:
                # Train model
                set_seed(seed)
                if arch == "bert":
                    model, _ = build_bert()
                else:
                    model, _ = build_gpt2()

                model = model.to(device)
                model.train()

                from train import train_model
                model = train_model(
                    model, train_loader, seed,
                    epochs=CONFIG["epochs"],
                    lr=CONFIG["lr"],
                    device=device
                )

                # Save checkpoint
                torch.save(model.state_dict(), ckpt_path)
                print(f"Saved: {ckpt_path}")

            # =========================================================================
            # 3. Compute attribution scores
            # =========================================================================
            model.eval()

            for method in args.methods:
                print(f"\nComputing {method.upper()} scores...")

                scores = compute_attribution(
                    model, train_loader, method,
                    device=device,
                    max_samples=args.max_attribution_samples
                )

                # Compute mislabeled detection AUC
                # Only consider indices within the computed scores
                valid_mislabeled = {i for i in mislabeled_indices if i < len(scores)}
                auc = mislabeled_auc(scores, valid_mislabeled)

                print(f" {method.upper()} AUC: {auc:.4f}")
                results[method][arch].append(auc)

            # Clear GPU memory
            del model
            torch.cuda.empty_cache()

    # =========================================================================
    # 4. Statistical analysis
    # =========================================================================
    print("\n" + "="*60)
    print("STEP 3: Statistical Analysis")
    print("="*60)

    gate_results = run_gate_check(results)

    print("\nResults Summary:")
    print("-" * 60)
    for method, stats in gate_results["methods"].items():
        print(f"\n{method.upper()}:")
        print(f"  BERT AUC:  {stats['auc_bert_mean']:.4f}")
        print(f"  GPT-2 AUC: {stats['auc_gpt2_mean']:.4f}")
        print(f"  Diff:      {stats['auc_diff']:+.4f}")
        print(f"  t-stat:    {stats['t_stat']:.3f}")
        print(f"  p-value:   {stats['p_value']:.4f}")
        print(f"  Cohen's d: {stats['cohens_d']:.3f}")
        print(f"  PASS:      {'YES' if stats['pass'] else 'NO'}")

    # =========================================================================
    # 5. Generate visualizations
    # =========================================================================
    print("\n" + "="*60)
    print("STEP 4: Generating Visualizations")
    print("="*60)

    plot_auc_comparison(
        results, gate_results,
        os.path.join(CONFIG["figures_dir"], "auc_comparison.png")
    )

    plot_method_arch_heatmap(
        results,
        os.path.join(CONFIG["figures_dir"], "method_arch_heatmap.png")
    )

    plot_diff_significance(
        results, gate_results,
        os.path.join(CONFIG["figures_dir"], "diff_significance.png")
    )

    # =========================================================================
    # 6. Save results
    # =========================================================================
    print("\n" + "="*60)
    print("STEP 5: Saving Results")
    print("="*60)

    output_data = {
        "hypothesis": "h-e1",
        "timestamp": datetime.now().isoformat(),
        "config": {
            "seeds": args.seeds,
            "methods": args.methods,
            "architectures": args.architectures,
            "noise_rate": CONFIG["noise_rate"],
            "epochs": CONFIG["epochs"],
            "max_attribution_samples": args.max_attribution_samples,
        },
        "results": results,
        "statistics": gate_results,
        "runtime_seconds": time.time() - start_time,
    }

    results_path = os.path.join("outputs", "results.json")
    with open(results_path, "w") as f:
        json.dump(output_data, f, indent=2)
    print(f"Results saved: {results_path}")

    # Also save to expected location
    with open(CONFIG["results_path"], "w") as f:
        json.dump(output_data, f, indent=2)
    print(f"Results saved: {CONFIG['results_path']}")

    # =========================================================================
    # 7. Gate decision
    # =========================================================================
    print("\n" + "="*60)
    print("GATE CHECK: MUST_WORK")
    print("="*60)

    if gate_results["overall_pass"]:
        print("\n✅ GATE PASSED: Architecture-method interaction exists!")
        print(f"   Best method: {gate_results['best_method'].upper()}")
        print(f"   Best diff:   {gate_results['best_diff']:+.4f}")
        gate_result = "PASS"
    else:
        print("\n❌ GATE FAILED: No significant architecture-method interaction found")
        print("   Consider: larger sample size, different methods, or pivot hypothesis")
        gate_result = "FAIL"

    print(f"\nTotal runtime: {time.time() - start_time:.1f} seconds")

    # Return gate result for pipeline integration
    return gate_result, output_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="H-E1: Architecture-Method Interaction Existence")

    parser.add_argument("--seeds", type=int, nargs="+", default=CONFIG["seeds"],
                       help="Random seeds for training")
    parser.add_argument("--methods", type=str, nargs="+", default=CONFIG["methods"],
                       help="Attribution methods to evaluate")
    parser.add_argument("--architectures", type=str, nargs="+", default=CONFIG["architectures"],
                       help="Model architectures to compare")
    parser.add_argument("--max-attribution-samples", type=int, default=1000,
                       help="Max samples for attribution (faster evaluation)")
    parser.add_argument("--retrain", action="store_true",
                       help="Force retrain even if checkpoints exist")

    args = parser.parse_args()

    gate_result, _ = main(args)
    sys.exit(0 if gate_result == "PASS" else 1)
