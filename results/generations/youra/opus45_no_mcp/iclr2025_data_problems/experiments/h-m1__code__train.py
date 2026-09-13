import os
import json
import random
import torch
from config import Config
from data import load_mmlu, sample_contamination_ids, build_training_dataset
from model import load_base_model, build_lora_config_m1, get_answer_token_ids, inject_contamination
from evaluate import evaluate_full_test_set, compute_item_accuracy
from mechanism import verify_contamination_mechanism, verify_monotonic_trend, aggregate_across_seeds
from visualize import plot_accuracy_by_level, plot_effect_size_bars


def run_experiment(config: Config):
    print("Loading MMLU test set...")
    full_test_set = load_mmlu()
    print(f"Full test set: {len(full_test_set)} items")

    # For mechanism validation: contaminate from full set, evaluate on full set
    # Track which items were contaminated to measure item-level accuracy difference
    test_set = full_test_set
    print(f"Using full test set for mechanism validation")

    all_results = {}

    for level in config.contamination_levels:
        level_results = []
        print(f"\n{'='*60}")
        print(f"Contamination Level: {level*100:.0f}%")
        print(f"{'='*60}")

        for seed in config.seeds:
            print(f"\n--- Seed {seed} ---")
            random.seed(seed)
            torch.manual_seed(seed)

            # Sample contaminated items from FULL test set
            contaminated_ids = sample_contamination_ids(test_set, level, seed)
            print(f"Contaminated items: {len(contaminated_ids)}")

            contaminated_dataset = build_training_dataset(test_set, contaminated_ids)

            print("Loading base model...")
            base_model, tokenizer = load_base_model(config.model_id)
            answer_tokens = get_answer_token_ids(tokenizer)

            lora_cfg = build_lora_config_m1(config.lora_rank, config.lora_alpha, config.lora_dropout)

            if level == 0.0:
                from peft import get_peft_model
                model = get_peft_model(base_model, lora_cfg)
            else:
                model = inject_contamination(
                    base_model,
                    tokenizer,
                    contaminated_dataset,
                    lora_cfg,
                    seed=seed,
                    epochs=config.epochs,
                    lr=config.lr,
                    batch_size=config.batch_size,
                    grad_accum=config.grad_accum,
                    output_dir=f"./adapters/level_{int(level*100)}_seed_{seed}",
                )

            # Evaluate: all contaminated items + equal number of random clean items
            if len(contaminated_ids) > 0:
                clean_ids = set(range(len(test_set))) - contaminated_ids
                n_clean_sample = min(len(contaminated_ids), len(clean_ids))
                random.seed(seed + 1000)  # Different seed for clean sampling
                clean_sample = set(random.sample(list(clean_ids), n_clean_sample))
                eval_ids = contaminated_ids | clean_sample
                eval_subset = test_set.select(sorted(eval_ids))
                # Map original IDs to new positions
                id_mapping = {old_id: new_id for new_id, old_id in enumerate(sorted(eval_ids))}
                mapped_contaminated = {id_mapping[i] for i in contaminated_ids}
                print(f"Evaluating {len(eval_subset)} items ({len(contaminated_ids)} contaminated + {n_clean_sample} clean)")
            else:
                # Level 0: evaluate random subset
                random.seed(seed)
                eval_ids = set(random.sample(range(len(test_set)), min(1000, len(test_set))))
                eval_subset = test_set.select(sorted(eval_ids))
                mapped_contaminated = set()
                print(f"Evaluating {len(eval_subset)} items (baseline, no contamination)")

            eval_results = evaluate_full_test_set(model, tokenizer, eval_subset, answer_tokens)

            accuracy_metrics = compute_item_accuracy(eval_results, mapped_contaminated if level > 0 else set())
            mechanism_check = verify_contamination_mechanism(
                accuracy_metrics["contaminated_accuracy"],
                accuracy_metrics["clean_accuracy"]
            )

            level_results.append({
                "seed": seed,
                **accuracy_metrics,
                **mechanism_check,
            })

            del model, base_model
            torch.cuda.empty_cache()

        aggregated = aggregate_across_seeds(level_results)
        all_results[level] = {
            "per_seed": level_results,
            "mean_contaminated_acc": float(sum(r["contaminated_accuracy"] for r in level_results) / len(level_results)),
            "mean_clean_acc": float(sum(r["clean_accuracy"] for r in level_results) / len(level_results)),
            "mean_effect_size": aggregated["mean_effect_size"],
            "std_effect_size": aggregated["std_effect_size"],
            "all_mechanism_active": all(r["mechanism_active"] for r in level_results),
        }

    effect_sizes = {l: all_results[l]["mean_effect_size"] for l in config.contamination_levels if l > 0}
    monotonic = verify_monotonic_trend(effect_sizes)

    mechanism_all_active = all(all_results[l]["all_mechanism_active"] for l in config.contamination_levels if l > 0)

    return {
        "config": {
            "model_id": config.model_id,
            "contamination_levels": list(config.contamination_levels),
            "seeds": list(config.seeds),
            "epochs": config.epochs,
            "lr": config.lr,
        },
        "results_by_level": {str(k): v for k, v in all_results.items()},
        "summary": {
            "mechanism_active_all_levels": mechanism_all_active,
            "monotonic_trend": monotonic,
            "effect_sizes": effect_sizes,
        },
        "gate": {
            "type": "MUST_WORK",
            "criteria": {
                "mechanism_active": mechanism_all_active,
                "monotonic_trend": monotonic,
            },
            "satisfied": mechanism_all_active and monotonic,
        },
    }


def main():
    config = Config()

    os.makedirs("results", exist_ok=True)
    os.makedirs("figures", exist_ok=True)
    os.makedirs("adapters", exist_ok=True)

    results = run_experiment(config)

    with open("results/mechanism_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to results/mechanism_results.json")

    plot_accuracy_by_level(
        {float(k): v for k, v in results["results_by_level"].items()},
        "figures"
    )
    plot_effect_size_bars(
        {float(k): v for k, v in results["results_by_level"].items()},
        "figures"
    )

    print("\n" + "="*60)
    print("EXPERIMENT COMPLETE")
    print("="*60)
    print(f"Mechanism Active (all levels): {results['summary']['mechanism_active_all_levels']}")
    print(f"Monotonic Trend: {results['summary']['monotonic_trend']}")
    print(f"Effect Sizes: {results['summary']['effect_sizes']}")
    print(f"Gate PASS: {results['gate']['satisfied']}")


if __name__ == "__main__":
    main()
