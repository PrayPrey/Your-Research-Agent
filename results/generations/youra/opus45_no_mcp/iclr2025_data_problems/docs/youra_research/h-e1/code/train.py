import os
import json
import random
import torch
from config import Config
from data import load_mmlu, sample_contamination_subset
from model import load_base_model, build_lora_config, get_answer_token_ids, inject_contamination
from ssi import compute_ssi_batch


def run_experiment(config: Config):
    print("Loading MMLU dataset...")
    test_data, aux_train = load_mmlu()
    print(f"Test set: {len(test_data)} items, Aux train: {len(aux_train)} items")

    random.seed(config.seed)
    torch.manual_seed(config.seed)

    eval_indices = random.sample(range(len(test_data)), min(config.n_eval_items, len(test_data)))
    eval_items = [test_data[i] for i in eval_indices]
    print(f"Evaluating on {len(eval_items)} items")

    print("Loading base model...")
    base_model, tokenizer = load_base_model(config.model_id)
    answer_tokens = get_answer_token_ids(tokenizer)
    print(f"Answer token IDs: {answer_tokens}")

    results = {
        "config": {
            "model_id": config.model_id,
            "n_eval_items": len(eval_items),
            "k_paraphrases": config.k_paraphrases,
            "contamination_levels": list(config.contamination_levels),
            "seed": config.seed,
        },
        "ssi_scores": {},
        "all_confidences": {},
    }

    for level in config.contamination_levels:
        level_name = "clean" if level == 0.0 else ("low" if level == 0.10 else "high")
        print(f"\n{'='*50}")
        print(f"Processing {level_name} contamination (level={level})")
        print(f"{'='*50}")

        contamination_subset = sample_contamination_subset(aux_train, level, config.seed)
        print(f"Contamination items: {len(contamination_subset)}")

        lora_cfg = build_lora_config(config.lora_rank, config.lora_alpha, config.lora_dropout)

        if level == 0.0:
            from peft import get_peft_model
            model = get_peft_model(base_model, lora_cfg)
        else:
            base_model_fresh, _ = load_base_model(config.model_id)
            model = inject_contamination(
                base_model_fresh,
                tokenizer,
                contamination_subset,
                lora_cfg,
                epochs=config.epochs,
                lr=config.lr,
                batch_size=config.batch_size,
                grad_accum=config.grad_accum,
                output_dir=f"./lora_output_{level_name}",
            )

        print(f"Computing SSI for {level_name} model...")
        ssi_scores, all_confidences = compute_ssi_batch(
            model, tokenizer, eval_items, answer_tokens, k_paraphrases=config.k_paraphrases
        )

        results["ssi_scores"][level_name] = ssi_scores
        results["all_confidences"][level_name] = all_confidences

        print(f"Mean SSI ({level_name}): {sum(ssi_scores)/len(ssi_scores):.2f}")

        del model
        torch.cuda.empty_cache()

    return results


def main():
    config = Config()

    os.makedirs("results", exist_ok=True)
    os.makedirs("figures", exist_ok=True)

    results = run_experiment(config)

    results_file = "results/ssi_scores.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {results_file}")

    from evaluate import run_evaluation
    eval_results = run_evaluation(results_file, "figures")

    final_results = {
        **results,
        "evaluation": eval_results["metrics"],
        "gate_pass": eval_results["gate_pass"],
    }

    with open("results/experiment_results.json", "w") as f:
        json.dump(final_results, f, indent=2)

    print("\n" + "="*50)
    print("EXPERIMENT COMPLETE")
    print("="*50)
    print(f"AUC: {eval_results['metrics']['auc']:.4f} (target: 0.7)")
    print(f"Cohen's d: {eval_results['metrics']['cohens_d']:.4f} (target: 0.5)")
    print(f"Gate PASS: {eval_results['gate_pass']}")


if __name__ == "__main__":
    main()
