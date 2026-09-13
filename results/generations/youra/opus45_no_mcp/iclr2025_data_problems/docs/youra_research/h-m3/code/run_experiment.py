#!/usr/bin/env python3
import os
import sys
import json
import random
import torch
import numpy as np
from datetime import datetime

h_m3_code_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, h_m3_code_dir)

from invariance_confidence import run_variance_extraction
from correlation import (
    compute_correlations, group_by_mps, group_comparison,
    per_subject_correlation, verify_gate, analyze_correlation
)
import viz_m3 as m3_visualize

sys.path.insert(0, os.path.join(h_m3_code_dir, "../../h-m2/code"))

from config import Config
from data import load_mmlu, sample_contamination_ids, build_training_dataset, format_mmlu_prompt
from model import load_base_model, build_lora_config_m1, inject_contamination
from paraphrase import load_paraphraser, build_paraphrase_bank
from train import build_augmented_training_set


def run_seed(config: Config, seed: int, test_set, para_model, para_tokenizer) -> dict:
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

    print("\n--- Extracting variances from VERBATIM model ---")
    verbatim_variances = run_variance_extraction(
        verbatim_model, tokenizer, test_set, paraphrase_bank, eval_ids, format_mmlu_prompt
    )

    del verbatim_model, base_model_v
    torch.cuda.empty_cache()

    print("\n--- Training PARAPHRASE-AUGMENTED model ---")
    augmented_dataset = build_augmented_training_set(
        contaminated_dataset, paraphrase_bank, contaminated_ids, k_train=config.k_paraphrases_train
    )
    print(f"Augmented dataset size: {len(augmented_dataset)}")

    base_model_p, _ = load_base_model(config.model_id)
    lora_cfg_p = build_lora_config_m1(config.lora_rank, config.lora_alpha, config.lora_dropout)

    paraphrase_model = inject_contamination(
        base_model_p, tokenizer, augmented_dataset, lora_cfg_p, seed,
        epochs=config.epochs_paraphrase, lr=config.lr,
        batch_size=config.batch_size, grad_accum=config.grad_accum,
        output_dir=f"./adapters/paraphrase_seed_{seed}"
    )

    print("\n--- Extracting variances from PARAPHRASE model ---")
    paraphrase_variances = run_variance_extraction(
        paraphrase_model, tokenizer, test_set, paraphrase_bank, eval_ids, format_mmlu_prompt
    )

    del paraphrase_model, base_model_p
    torch.cuda.empty_cache()

    valid_indices = [i for i in eval_ids if i in verbatim_variances and i in paraphrase_variances]

    rep_vars_v = np.array([verbatim_variances[i]["rep_var"] for i in valid_indices])
    conf_vars_v = np.array([verbatim_variances[i]["conf_var"] for i in valid_indices])
    rep_vars_p = np.array([paraphrase_variances[i]["rep_var"] for i in valid_indices])
    conf_vars_p = np.array([paraphrase_variances[i]["conf_var"] for i in valid_indices])

    subjects = {i: test_set[i].get("subject", "unknown") for i in valid_indices}

    result_v = analyze_correlation(rep_vars_v, conf_vars_v)
    result_p = analyze_correlation(rep_vars_p, conf_vars_p)

    high_idx, low_idx = group_by_mps(rep_vars_p)
    comparison = group_comparison(conf_vars_p, high_idx, low_idx)

    subj_rep = {i: rep_vars_p[j] for j, i in enumerate(valid_indices)}
    subj_conf = {i: conf_vars_p[j] for j, i in enumerate(valid_indices)}
    subject_corr = per_subject_correlation(subj_rep, subj_conf, subjects)

    return {
        "seed": seed,
        "n_items": len(valid_indices),
        "verbatim": {
            "r_pearson": float(result_v.r_pearson),
            "p_pearson": float(result_v.p_pearson),
            "r_spearman": float(result_v.r_spearman),
            "p_spearman": float(result_v.p_spearman),
            "cohens_d": float(result_v.cohens_d),
            "gate_passes": result_v.gate_passes,
        },
        "paraphrase": {
            "r_pearson": float(result_p.r_pearson),
            "p_pearson": float(result_p.p_pearson),
            "r_spearman": float(result_p.r_spearman),
            "p_spearman": float(result_p.p_spearman),
            "cohens_d": float(result_p.cohens_d),
            "gate_passes": result_p.gate_passes,
        },
        "comparison": comparison,
        "subject_correlations": subject_corr,
        "rep_vars_paraphrase": rep_vars_p.tolist(),
        "conf_vars_paraphrase": conf_vars_p.tolist(),
    }


def aggregate_across_seeds(results_per_seed: list) -> dict:
    r_values = [r["paraphrase"]["r_pearson"] for r in results_per_seed]
    d_values = [r["paraphrase"]["cohens_d"] for r in results_per_seed]
    gate_passes = [r["paraphrase"]["gate_passes"] for r in results_per_seed]

    return {
        "mean_r_pearson": float(np.mean(r_values)),
        "std_r_pearson": float(np.std(r_values)),
        "mean_cohens_d": float(np.mean(d_values)),
        "all_seeds_pass": all(gate_passes),
        "pass_count": sum(gate_passes),
        "total_seeds": len(results_per_seed),
    }


def main():
    config = Config()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(script_dir, "results")
    figures_dir = os.path.join(script_dir, "..", "figures")
    adapters_dir = os.path.join(script_dir, "adapters")

    os.makedirs(results_dir, exist_ok=True)
    os.makedirs(figures_dir, exist_ok=True)
    os.makedirs(adapters_dir, exist_ok=True)

    print("Loading MMLU test set...")
    test_set = load_mmlu()
    print(f"Test set: {len(test_set)} items")

    print("\nLoading paraphraser (rule-based)...")
    para_model, para_tokenizer = load_paraphraser()

    all_seed_results = []
    for seed in config.seeds:
        result = run_seed(config, seed, test_set, para_model, para_tokenizer)
        all_seed_results.append(result)

    aggregated = aggregate_across_seeds(all_seed_results)

    gate_satisfied = aggregated["all_seeds_pass"] and aggregated["mean_r_pearson"] < config.correlation_threshold

    final_results = {
        "hypothesis": "H-M3",
        "title": "Representation Invariance Manifests as Uniform Confidence",
        "timestamp": datetime.now().isoformat(),
        "config": {
            "model_id": config.model_id,
            "contamination_frac": config.contamination_frac,
            "k_paraphrases_bank": config.k_paraphrases_bank,
            "k_paraphrases_train": config.k_paraphrases_train,
            "n_eval_items": config.n_eval_items,
            "seeds": list(config.seeds),
            "correlation_threshold": config.correlation_threshold,
        },
        "results_per_seed": all_seed_results,
        "aggregated": aggregated,
        "gate": {
            "type": "SHOULD_WORK",
            "threshold": config.correlation_threshold,
            "criteria": {
                "r_pearson_lt_threshold": aggregated["mean_r_pearson"] < config.correlation_threshold,
                "all_seeds_pass": aggregated["all_seeds_pass"],
            },
            "satisfied": gate_satisfied,
            "result": "PASS" if gate_satisfied else "FAIL",
        },
    }

    results_path = os.path.join(results_dir, "correlation_results.json")
    with open(results_path, "w") as f:
        json.dump(final_results, f, indent=2, default=float)
    print(f"\nResults saved to {results_path}")

    if all_seed_results:
        rep_vars = np.concatenate([np.array(r["rep_vars_paraphrase"]) for r in all_seed_results])
        conf_vars = np.concatenate([np.array(r["conf_vars_paraphrase"]) for r in all_seed_results])

        m3_visualize.plot_gate_metrics(config.correlation_threshold, aggregated["mean_r_pearson"], figures_dir)
        m3_visualize.plot_scatter_variance(rep_vars, conf_vars, aggregated["mean_r_pearson"], figures_dir)

        high_idx, low_idx = group_by_mps(rep_vars)
        m3_visualize.plot_boxplot_by_mps_group(conf_vars[high_idx], conf_vars[low_idx], figures_dir)

        r_per_seed = [r["paraphrase"]["r_pearson"] for r in all_seed_results]
        m3_visualize.plot_correlation_histogram(r_per_seed, figures_dir)

        all_subject_corr = {}
        for r in all_seed_results:
            for subj, corr in r["subject_correlations"].items():
                if subj not in all_subject_corr:
                    all_subject_corr[subj] = []
                all_subject_corr[subj].append(corr)
        mean_subject_corr = {s: np.mean(v) for s, v in all_subject_corr.items()}
        m3_visualize.plot_subject_heatmap(mean_subject_corr, figures_dir)

    print("\n" + "="*60)
    print("EXPERIMENT COMPLETE")
    print("="*60)
    print(f"Mean Pearson r: {aggregated['mean_r_pearson']:.4f} (threshold: {config.correlation_threshold})")
    print(f"Mean Cohen's d: {aggregated['mean_cohens_d']:.4f}")
    print(f"Seeds passing gate: {aggregated['pass_count']}/{aggregated['total_seeds']}")
    print(f"Gate PASS: {gate_satisfied}")


if __name__ == "__main__":
    main()
