#!/usr/bin/env python3
"""H-M3: Amplification Index Experiment"""

import json
import os
import numpy as np
from datetime import datetime

from config import Config
from data import load_mmlu_eval, load_mmlu_redux_clean, build_contamination_masks
from models import train_all_models
from evaluate import eval_all
from metrics import compute_deltas, amplification_index, bootstrap_ai_ci, gate_check
from visualize import plot_ai_bar_with_ci, plot_delta_boxplot


def run_experiment(cfg: Config) -> dict:
    """Run full H-M3 experiment."""
    print("=" * 60)
    print("H-M3: Amplification Index Experiment")
    print("=" * 60)

    # 1. Train all models (2 strategies x 3 seeds)
    print("\n[1/6] Training models...")
    models = train_all_models(cfg)

    # 2. Load evaluation data
    print("\n[2/6] Loading MMLU and MMLU-Redux...")
    mmlu = load_mmlu_eval(cfg)
    clean = load_mmlu_redux_clean()

    # 3. Build contamination masks
    print("\n[3/6] Building contamination masks...")
    contaminated_mask, clean_mask = build_contamination_masks(mmlu, clean)

    # Handle edge case: no clean samples found
    if clean_mask.sum() == 0:
        print("WARNING: No clean samples found in MMLU-Redux match. Using random 50% split.")
        np.random.seed(42)
        n = len(mmlu)
        split_idx = np.random.permutation(n)
        clean_mask = np.zeros(n, dtype=bool)
        clean_mask[split_idx[:n//2]] = True
        contaminated_mask = ~clean_mask

    # Skip fewshot samples in masks
    fewshot_offset = cfg.num_fewshot
    contaminated_mask = contaminated_mask[fewshot_offset:fewshot_offset + cfg.mmlu_subset - fewshot_offset]
    clean_mask = clean_mask[fewshot_offset:fewshot_offset + cfg.mmlu_subset - fewshot_offset]

    # 4. Evaluate all models
    print("\n[4/6] Evaluating models on MMLU...")
    correctness = eval_all(models, mmlu, cfg)

    # 5. Compute metrics
    print("\n[5/6] Computing Amplification Index...")
    deltas = compute_deltas(correctness, contaminated_mask, clean_mask)

    for model_id, delta in deltas.items():
        print(f"  {model_id}: delta={delta:.4f}")

    ai = amplification_index(deltas)

    # Get arrays for bootstrap
    ppl_deltas = np.array([v for k, v in sorted(deltas.items()) if "perplexity" in k])
    rand_deltas = np.array([v for k, v in sorted(deltas.items()) if "random" in k])

    ci_lower, ci_upper = bootstrap_ai_ci(ppl_deltas, rand_deltas, cfg.n_bootstrap, cfg.confidence)

    print(f"\n  Amplification Index: {ai:.4f}")
    print(f"  95% CI: [{ci_lower:.4f}, {ci_upper:.4f}]")

    gate_passed = gate_check(ai, ci_lower)
    print(f"  Gate (AI>0 AND CI_lower>0): {'PASS' if gate_passed else 'FAIL'}")

    # 6. Generate visualizations
    print("\n[6/6] Generating visualizations...")
    os.makedirs(cfg.out_dir, exist_ok=True)
    plot_ai_bar_with_ci(ai, (ci_lower, ci_upper), cfg.out_dir)
    plot_delta_boxplot(deltas, cfg.out_dir)

    # Save results
    results = {
        "hypothesis": "H-M3",
        "timestamp": datetime.now().isoformat(),
        "config": {
            "model_id": cfg.model_id,
            "strategies": list(cfg.strategies),
            "seeds": list(cfg.seeds),
            "mmlu_subset": cfg.mmlu_subset,
            "n_bootstrap": cfg.n_bootstrap
        },
        "metrics": {
            "amplification_index": float(ai),
            "ci_lower": float(ci_lower),
            "ci_upper": float(ci_upper),
            "gate_passed": gate_passed
        },
        "deltas": {k: float(v) for k, v in deltas.items()},
        "sample_counts": {
            "contaminated": int(contaminated_mask.sum()),
            "clean": int(clean_mask.sum())
        }
    }

    summary_path = os.path.join(cfg.out_dir, "experiment_summary.json")
    with open(summary_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved: {summary_path}")

    print("\n" + "=" * 60)
    print(f"EXPERIMENT COMPLETE: AI={ai:.4f}, Gate={'PASS' if gate_passed else 'FAIL'}")
    print("=" * 60)

    return results


if __name__ == "__main__":
    cfg = Config()
    run_experiment(cfg)
