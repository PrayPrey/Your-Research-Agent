#!/usr/bin/env python3
"""H-E1 Experiment Orchestrator — end-to-end pipeline."""

import json
import os
import sys
from pathlib import Path

import torch

# Add code/ dir to path so sibling imports work
sys.path.insert(0, str(Path(__file__).parent))

from config import get_config
from data import load_halueval_qa, load_dataset_from_disk, save_dataset
from inference import load_llm, run_greedy_inference, run_stochastic_inference
from uq_signals import (
    compute_all_token_entropy,
    load_nli_pipeline,
    compute_all_semantic_entropy,
    compute_all_selfcheckgpt,
)
from evaluate import (
    compute_auroc,
    bootstrap_auroc_ci,
    pairwise_auroc_differences,
    check_must_work_gate,
    save_results,
)
from visualize import plot_auroc_bar_chart, plot_roc_curves_overlay


def main():
    # ── 1. Config ────────────────────────────────────────────────────────────
    cfg = get_config()
    code_dir = Path(__file__).parent
    os.chdir(code_dir)

    Path(cfg.data_dir).mkdir(parents=True, exist_ok=True)
    Path(cfg.outputs_dir, "greedy_logits").mkdir(parents=True, exist_ok=True)
    Path(cfg.outputs_dir, "uq_scores").mkdir(parents=True, exist_ok=True)
    Path(cfg.results_dir).mkdir(parents=True, exist_ok=True)
    Path(cfg.figures_dir).mkdir(parents=True, exist_ok=True)

    # ── 2. Dataset ───────────────────────────────────────────────────────────
    dataset_path = Path(cfg.data_dir) / "halueval_qa_2k.json"
    if dataset_path.exists():
        print("Loading dataset from disk...")
        examples = load_dataset_from_disk(str(dataset_path))
    else:
        print("Downloading HaluEval-QA...")
        examples = load_halueval_qa(cfg)
        save_dataset(examples, str(dataset_path))
    print(f"Dataset: {len(examples)} examples")

    # ── 3. LLM Inference ─────────────────────────────────────────────────────
    print("\n[Step 3] Loading LLM...")
    model, tokenizer = load_llm(cfg)

    print("[Step 4] Greedy inference...")
    run_greedy_inference(examples, model, tokenizer, cfg, resume=True)

    print("[Step 5] Stochastic inference...")
    run_stochastic_inference(examples, model, tokenizer, cfg, resume=True)

    # Free GPU memory before NLI
    del model, tokenizer
    torch.cuda.empty_cache()
    print("LLM unloaded, GPU cache cleared.")

    # ── 4. UQ Signals ────────────────────────────────────────────────────────
    def _load_json_scores(name):
        p = Path(cfg.outputs_dir) / "uq_scores" / f"{name}.json"
        if p.exists():
            with open(p) as f:
                return {int(k): v for k, v in json.load(f).items()}
        return None

    print("\n[Step 6] Token entropy...")
    token_entropy_scores = _load_json_scores("token_entropy_mean")
    if token_entropy_scores is None:
        token_entropy_scores = compute_all_token_entropy(cfg.outputs_dir, cfg)
    else:
        print("  Skipping (already computed)")

    print("[Step 7] Loading NLI pipeline...")
    semantic_entropy_scores = _load_json_scores("semantic_entropy")
    if semantic_entropy_scores is None:
        nli_pipe = load_nli_pipeline(cfg)
        print("[Step 8] Semantic entropy...")
        semantic_entropy_scores = compute_all_semantic_entropy(cfg.outputs_dir, cfg, nli_pipe)
    else:
        print("  Skipping semantic entropy (already computed)")

    print("[Step 9] SelfCheckGPT-BERTScore...")
    selfcheckgpt_scores = _load_json_scores("selfcheckgpt_bertscore_n5")
    if selfcheckgpt_scores is None:
        selfcheckgpt_scores = compute_all_selfcheckgpt(cfg.outputs_dir, cfg)
    else:
        print("  Skipping SelfCheckGPT (already computed)")

    # ── 5. Evaluation ────────────────────────────────────────────────────────
    print("\n[Step 10] Evaluating...")
    labels = [int(ex["hallucination_label"]) for ex in examples]
    example_ids = [int(ex["id"]) for ex in examples]

    def align_scores(scores_dict):
        return [scores_dict.get(eid, 0.0) for eid in example_ids]

    scores_map = {
        "token_entropy_mean": align_scores(token_entropy_scores),
        "semantic_entropy": align_scores(semantic_entropy_scores),
        "selfcheckgpt_bertscore_n5": align_scores(selfcheckgpt_scores),
    }

    auroc_map = {m: compute_auroc(labels, s) for m, s in scores_map.items()}
    ci_map = {m: bootstrap_auroc_ci(labels, s, cfg.n_bootstrap, cfg.seed)
              for m, s in scores_map.items()}

    pairwise = pairwise_auroc_differences(auroc_map, ci_map)
    gate = check_must_work_gate(pairwise, cfg)

    # ── 6. Save Results ──────────────────────────────────────────────────────
    print("\n[Step 11] Saving results...")
    save_results(auroc_map, ci_map, pairwise, gate, cfg.results_dir)

    # ── 7. Figures ───────────────────────────────────────────────────────────
    print("[Step 12] Generating figures...")
    plot_auroc_bar_chart(
        auroc_map, ci_map,
        save_path=str(Path(cfg.figures_dir) / "auroc_bar_chart.png"),
    )
    plot_roc_curves_overlay(
        labels, scores_map, auroc_map,
        save_path=str(Path(cfg.figures_dir) / "roc_curves_overlay.png"),
    )

    # ── 8. Gate Summary ──────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("EXPERIMENT COMPLETE")
    print("=" * 60)
    print(f"\nAUROC Results:")
    for m, a in sorted(auroc_map.items(), key=lambda x: -x[1]):
        ci = ci_map[m]
        print(f"  {m}: {a:.4f} (95% CI: [{ci[0]:.4f}, {ci[1]:.4f}])")

    print(f"\nPairwise Comparisons:")
    for pair in pairwise:
        overlap_str = "non-overlapping" if pair["ci_non_overlapping"] else "overlapping"
        print(f"  {pair['winner']} > {pair['loser']}: Δ={pair['delta_auroc']:.4f}, CI {overlap_str}")

    print(f"\n{gate['message']}")
    if gate["gate_passed"]:
        print(f"  Qualifying pairs: {gate['qualifying_pair_count']}")
        sys.exit(0)
    else:
        print("  No pair achieved Δ≥0.05 with non-overlapping CIs.")
        sys.exit(1)


if __name__ == "__main__":
    main()
