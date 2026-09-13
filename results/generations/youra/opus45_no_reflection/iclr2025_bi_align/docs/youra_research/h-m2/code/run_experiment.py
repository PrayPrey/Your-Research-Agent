"""H-M2: BiDPO vs DPO collaboration score comparison."""
import os
import sys
import json
import time
import torch

# Ensure project imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config as cfg
from data import load_hh_rlhf_prompts
from models import load_tokenizer, load_baseline_model, load_bidpo_model
from generate import generate_responses
from analysis import score_responses, compare_collab_scores
from visualize import (
    plot_score_comparison_bar,
    plot_score_distributions,
    plot_per_prompt_scatter,
    plot_score_component_breakdown,
    plot_length_vs_score
)


def main():
    print("=" * 60)
    print("H-M2: BiDPO vs DPO Collaboration Score Comparison")
    print("=" * 60)

    cfg.ensure_dirs()

    # Verify checkpoint exists
    checkpoint_path = os.path.join(os.path.dirname(__file__), cfg.BIDPO_CHECKPOINT_PATH)
    if not os.path.exists(checkpoint_path):
        raise FileNotFoundError(f"H-M1 checkpoint not found: {checkpoint_path}")
    print(f"Checkpoint verified: {checkpoint_path}")

    # Load prompts
    print(f"\nLoading {cfg.N_PROMPTS} prompts from HH-RLHF test split...")
    prompts = load_hh_rlhf_prompts(cfg.N_PROMPTS, cfg.SEED)
    print(f"Loaded {len(prompts)} unique prompts")

    # Load tokenizer
    print(f"\nLoading tokenizer: {cfg.BASELINE_MODEL}")
    tokenizer = load_tokenizer(cfg.BASELINE_MODEL)

    # Generate with DPO baseline
    print(f"\nLoading DPO baseline model...")
    t0 = time.time()
    baseline = load_baseline_model(cfg.BASELINE_MODEL)
    load_time_baseline = time.time() - t0
    print(f"Baseline loaded in {load_time_baseline:.1f}s")

    print(f"\nGenerating {len(prompts)} responses with DPO baseline...")
    t0 = time.time()
    dpo_responses = generate_responses(
        baseline, tokenizer, prompts,
        cfg.MAX_NEW_TOKENS, cfg.TEMPERATURE, cfg.TOP_P, cfg.SEED
    )
    gen_time_dpo = time.time() - t0
    print(f"DPO generation completed in {gen_time_dpo:.1f}s")

    # Free GPU memory
    del baseline
    torch.cuda.empty_cache()
    print("DPO model unloaded, GPU memory freed")

    # Generate with BiDPO
    print(f"\nLoading BiDPO model...")
    t0 = time.time()
    bidpo = load_bidpo_model(cfg.BIDPO_MODEL_BASE, checkpoint_path)
    load_time_bidpo = time.time() - t0
    print(f"BiDPO loaded in {load_time_bidpo:.1f}s")

    print(f"\nGenerating {len(prompts)} responses with BiDPO...")
    t0 = time.time()
    bidpo_responses = generate_responses(
        bidpo, tokenizer, prompts,
        cfg.MAX_NEW_TOKENS, cfg.TEMPERATURE, cfg.TOP_P, cfg.SEED
    )
    gen_time_bidpo = time.time() - t0
    print(f"BiDPO generation completed in {gen_time_bidpo:.1f}s")

    # Free GPU memory
    del bidpo
    torch.cuda.empty_cache()
    print("BiDPO model unloaded, GPU memory freed")

    # Score responses
    print("\nScoring responses...")
    dpo_scores = score_responses(dpo_responses)
    bidpo_scores = score_responses(bidpo_responses)

    # Statistical comparison
    print("\nComputing statistics...")
    stats = compare_collab_scores(bidpo_scores, dpo_scores)

    # Add timing info
    stats["timing"] = {
        "load_time_baseline_s": load_time_baseline,
        "load_time_bidpo_s": load_time_bidpo,
        "gen_time_dpo_s": gen_time_dpo,
        "gen_time_bidpo_s": gen_time_bidpo,
    }

    # Print results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"DPO Baseline:  mean={stats['dpo_mean']:.4f}, std={stats['dpo_std']:.4f}")
    print(f"BiDPO:         mean={stats['bidpo_mean']:.4f}, std={stats['bidpo_std']:.4f}")
    print(f"Difference:    {stats['mean_difference']:.4f}")
    print(f"t-statistic:   {stats['t_statistic']:.4f}")
    print(f"p-value (1-sided): {stats['p_value_onesided']:.6f}")
    print(f"Cohen's d:     {stats['effect_size_cohens_d']:.4f}")
    print(f"\nGATE PASSED:   {stats['gate_passed']}")
    print("=" * 60)

    # Generate figures
    print("\nGenerating figures...")
    figures_dir = os.path.join(os.path.dirname(__file__), cfg.FIGURES_DIR)
    os.makedirs(figures_dir, exist_ok=True)

    plot_score_comparison_bar(stats, f"{figures_dir}/score_comparison_bar.png")
    print("  - score_comparison_bar.png")

    plot_score_distributions(bidpo_scores, dpo_scores, f"{figures_dir}/score_distributions.png")
    print("  - score_distributions.png")

    plot_per_prompt_scatter(dpo_scores, bidpo_scores, f"{figures_dir}/per_prompt_scatter.png")
    print("  - per_prompt_scatter.png")

    plot_score_component_breakdown(bidpo_responses, dpo_responses, f"{figures_dir}/component_breakdown.png")
    print("  - component_breakdown.png")

    plot_length_vs_score(bidpo_responses + dpo_responses, bidpo_scores + dpo_scores,
                         f"{figures_dir}/length_vs_score.png")
    print("  - length_vs_score.png")

    # Save results
    results_path = os.path.join(os.path.dirname(__file__), cfg.RESULTS_PATH)
    with open(results_path, "w") as f:
        json.dump(stats, f, indent=2)
    print(f"\nResults saved to: {results_path}")

    # Save responses for further analysis
    responses_path = os.path.join(os.path.dirname(__file__), "outputs/responses.json")
    with open(responses_path, "w") as f:
        json.dump({
            "prompts": prompts,
            "dpo_responses": dpo_responses,
            "bidpo_responses": bidpo_responses,
            "dpo_scores": dpo_scores,
            "bidpo_scores": bidpo_scores,
        }, f, indent=2)
    print(f"Responses saved to: {responses_path}")

    print("\nExperiment complete!")
    return stats


if __name__ == "__main__":
    main()
