import os
import json
import random
import torch
import numpy as np
from datasets import Dataset

from config import Config
from data import load_mmlu, sample_contamination_ids, build_training_dataset, format_mmlu_prompt
from model import load_base_model, build_lora_config_m1, inject_contamination, format_training_example
from paraphrase import load_paraphraser, build_paraphrase_bank
from representation import evaluate_invariance
from mechanism import verify_invariance_mechanism, aggregate_across_seeds
from visualize import plot_mps_distribution, plot_mps_boxplot, plot_seed_comparison


def build_augmented_training_set(contaminated_dataset: Dataset, paraphrase_bank: dict,
                                  contaminated_ids: set, k_train: int = 3) -> Dataset:
    rows = {"question": [], "choices": [], "answer": [], "subject": []}

    for idx in sorted(contaminated_ids):
        item = contaminated_dataset[list(contaminated_ids).index(idx)]
        rows["question"].append(item["question"])
        rows["choices"].append(item["choices"])
        rows["answer"].append(item["answer"])
        rows["subject"].append(item.get("subject", ""))

        paras = paraphrase_bank.get(idx, [])
        for para_text in paras[:k_train]:
            q_match = para_text.split("\n\n")[0].replace("Question: ", "")
            rows["question"].append(q_match)
            rows["choices"].append(item["choices"])
            rows["answer"].append(item["answer"])
            rows["subject"].append(item.get("subject", ""))

    return Dataset.from_dict(rows)


def run_experiment(config: Config):
    print("Loading MMLU test set...")
    test_set = load_mmlu()
    print(f"Test set: {len(test_set)} items")

    print("\nLoading paraphraser (rule-based)...")
    para_model, para_tokenizer = load_paraphraser()

    all_seed_results = []

    for seed in config.seeds:
        print(f"\n{'='*60}")
        print(f"SEED {seed}")
        print(f"{'='*60}")

        random.seed(seed)
        torch.manual_seed(seed)
        np.random.seed(seed)

        contaminated_ids = sample_contamination_ids(test_set, config.contamination_frac, seed)
        print(f"Contaminated items: {len(contaminated_ids)}")

        contaminated_dataset = build_training_dataset(test_set, contaminated_ids)

        print("\nBuilding paraphrase bank (K=5)...")
        paraphrase_bank = build_paraphrase_bank(
            test_set, contaminated_ids, para_model, para_tokenizer,
            k=config.k_paraphrases_bank, seed=seed
        )

        eval_ids = sorted(contaminated_ids)[:config.n_eval_items]
        print(f"Evaluation subset: {len(eval_ids)} items")

        print("\n--- Training VERBATIM model ---")
        base_model_v, tokenizer = load_base_model(config.model_id)
        lora_cfg = build_lora_config_m1(config.lora_rank, config.lora_alpha, config.lora_dropout)

        verbatim_model = inject_contamination(
            base_model_v, tokenizer, contaminated_dataset, lora_cfg, seed,
            epochs=config.epochs_verbatim, lr=config.lr,
            batch_size=config.batch_size, grad_accum=config.grad_accum,
            output_dir=f"./adapters/verbatim_seed_{seed}"
        )

        print("\n--- Training PARAPHRASE-AUGMENTED model ---")
        augmented_dataset = build_augmented_training_set(
            contaminated_dataset, paraphrase_bank, contaminated_ids, k_train=config.k_paraphrases_train
        )
        print(f"Augmented dataset size: {len(augmented_dataset)} (original + {config.k_paraphrases_train} paraphrases)")

        base_model_p, _ = load_base_model(config.model_id)
        lora_cfg_p = build_lora_config_m1(config.lora_rank, config.lora_alpha, config.lora_dropout)

        paraphrase_model = inject_contamination(
            base_model_p, tokenizer, augmented_dataset, lora_cfg_p, seed,
            epochs=config.epochs_paraphrase, lr=config.lr,
            batch_size=config.batch_size, grad_accum=config.grad_accum,
            output_dir=f"./adapters/paraphrase_seed_{seed}"
        )

        print("\n--- Evaluating representation invariance ---")
        mps_verbatim = evaluate_invariance(verbatim_model, tokenizer, test_set, paraphrase_bank, eval_ids)
        mps_paraphrase = evaluate_invariance(paraphrase_model, tokenizer, test_set, paraphrase_bank, eval_ids)

        mechanism_result = verify_invariance_mechanism(mps_verbatim, mps_paraphrase)
        mechanism_result["seed"] = seed
        mechanism_result["mps_verbatim_array"] = mps_verbatim.tolist()
        mechanism_result["mps_paraphrase_array"] = mps_paraphrase.tolist()

        all_seed_results.append(mechanism_result)

        del verbatim_model, paraphrase_model, base_model_v, base_model_p
        torch.cuda.empty_cache()

    aggregated = aggregate_across_seeds(all_seed_results)

    gate_satisfied = (
        aggregated["mechanism_active_count"] == len(config.seeds) and
        aggregated["mean_difference"] > config.mps_diff_threshold and
        aggregated["mean_effect_size"] > config.effect_size_target
    )

    return {
        "config": {
            "model_id": config.model_id,
            "contamination_frac": config.contamination_frac,
            "k_paraphrases_bank": config.k_paraphrases_bank,
            "k_paraphrases_train": config.k_paraphrases_train,
            "n_eval_items": config.n_eval_items,
            "epochs_verbatim": config.epochs_verbatim,
            "epochs_paraphrase": config.epochs_paraphrase,
            "seeds": list(config.seeds),
        },
        "results_per_seed": all_seed_results,
        "aggregated": aggregated,
        "gate": {
            "type": "SHOULD_WORK",
            "criteria": {
                "mechanism_active_all_seeds": aggregated["mechanism_active_count"] == len(config.seeds),
                "mps_difference_gt_threshold": aggregated["mean_difference"] > config.mps_diff_threshold,
                "effect_size_gt_target": aggregated["mean_effect_size"] > config.effect_size_target,
            },
            "satisfied": gate_satisfied,
        },
    }


def main():
    config = Config()

    os.makedirs("results", exist_ok=True)
    os.makedirs("figures", exist_ok=True)
    os.makedirs("adapters", exist_ok=True)

    results = run_experiment(config)

    with open("results/mechanism_results.json", "w") as f:
        json.dump(results, f, indent=2, default=float)
    print(f"\nResults saved to results/mechanism_results.json")

    if results["results_per_seed"]:
        mps_v = np.concatenate([np.array(r["mps_verbatim_array"]) for r in results["results_per_seed"]])
        mps_p = np.concatenate([np.array(r["mps_paraphrase_array"]) for r in results["results_per_seed"]])
        plot_mps_distribution(mps_v, mps_p, "figures")
        plot_mps_boxplot(mps_v, mps_p, "figures")
        plot_seed_comparison(results["results_per_seed"], "figures")

    print("\n" + "="*60)
    print("EXPERIMENT COMPLETE")
    print("="*60)
    print(f"Mean MPS Verbatim: {results['aggregated'].get('mean_difference', 0) + np.mean([r['mps_verbatim'] for r in results['results_per_seed']]):.4f}")
    print(f"Mean MPS Paraphrase: {np.mean([r['mps_paraphrase'] for r in results['results_per_seed']]):.4f}")
    print(f"Mean Difference: {results['aggregated']['mean_difference']:.4f}")
    print(f"Mean Effect Size: {results['aggregated']['mean_effect_size']:.4f}")
    print(f"Reproducibility: {results['aggregated']['reproducibility']}")
    print(f"Gate PASS: {results['gate']['satisfied']}")


if __name__ == "__main__":
    main()
