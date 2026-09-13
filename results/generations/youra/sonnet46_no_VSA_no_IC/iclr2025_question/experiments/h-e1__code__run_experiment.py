"""
Main experiment orchestrator for H-E1: Token-level log-prob aggregation ablation.
"""
import os
import sys
import json
import warnings
import logging

# Suppress transformers verbosity
logging.getLogger("transformers").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd

# Add code dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import MODELS, DATASETS, AGGREGATIONS, SEED, BOOTSTRAP_N, RESULTS_DIR, FIGURES_DIR, FARQUHAR_DATA_DIR, MAX_SAMPLES_PER_DATASET
from data_loader import get_dataset
from inference import load_model, run_inference
from aggregation import compute_all_scores
from evaluation import (
    evaluate_cell, compute_all_pairwise_ci, length_stratified_auroc, check_gate
)
from visualization import plot_roc_curves, plot_score_histograms

np.random.seed(SEED)


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(FIGURES_DIR, exist_ok=True)

    auroc_table = {}   # {model: {dataset: {method: auroc}}}
    auprc_table = {}
    ece_table = {}
    ci_table = {}      # {model: {dataset: {pair_key: (lo, hi)}}
    length_table = {}  # {model: {dataset: {method: {short, long, n_short, n_long}}}}

    model_keys = list(MODELS.keys())

    for model_key in model_keys:
        print(f"\n{'='*60}", flush=True)
        print(f"Loading model: {model_key} ({MODELS[model_key]})", flush=True)
        print(f"{'='*60}", flush=True)
        model, tokenizer = load_model(model_key)

        auroc_table[model_key] = {}
        auprc_table[model_key] = {}
        ece_table[model_key] = {}
        ci_table[model_key] = {}
        length_table[model_key] = {}

        for dataset_name in DATASETS:
            print(f"\n  Dataset: {dataset_name}", flush=True)
            samples = get_dataset(dataset_name, FARQUHAR_DATA_DIR)
            print(f"  Loaded {len(samples)} samples", flush=True)

            # Subsample for tractability (seeded for reproducibility)
            max_n = MAX_SAMPLES_PER_DATASET.get(dataset_name)
            if max_n is not None and len(samples) > max_n:
                rng = np.random.default_rng(SEED)
                idx = rng.choice(len(samples), size=max_n, replace=False)
                idx.sort()
                samples = [samples[i] for i in idx]
                print(f"  Subsampled to {len(samples)} samples (seed={SEED})", flush=True)

            print(f"  Running inference...", flush=True)
            records = run_inference(samples, model, tokenizer)
            print(f"  Got {len(records)} valid records (non-empty generations)", flush=True)

            # Save scores
            scores_path = os.path.join(RESULTS_DIR, f"scores_{model_key}_{dataset_name}.npz")
            all_method_scores = compute_all_scores(records)
            np.savez(
                scores_path,
                **{f"{m}_scores": all_method_scores[m][0] for m in AGGREGATIONS},
                labels=all_method_scores["min"][1],
            )

            # Evaluate all 18 cells (6 model×dataset × 3 aggregations)
            auroc_table[model_key][dataset_name] = {}
            auprc_table[model_key][dataset_name] = {}
            ece_table[model_key][dataset_name] = {}

            for method in AGGREGATIONS:
                scores, labels = all_method_scores[method]
                metrics = evaluate_cell(labels, scores)
                auroc_table[model_key][dataset_name][method] = metrics["auroc"]
                auprc_table[model_key][dataset_name][method] = metrics["auprc"]
                ece_table[model_key][dataset_name][method] = metrics["ece"]
                print(f"    {method}: AUROC={metrics['auroc']:.4f}, AUPRC={metrics['auprc']:.4f}", flush=True)

            # Bootstrap CIs
            print(f"  Computing bootstrap CIs (n={BOOTSTRAP_N})...", flush=True)
            method_score_arrays = {m: all_method_scores[m][0] for m in AGGREGATIONS}
            labels_arr = all_method_scores["min"][1]
            ci_table[model_key][dataset_name] = compute_all_pairwise_ci(
                method_score_arrays, labels_arr, n_resamples=BOOTSTRAP_N
            )
            for k, (lo, hi) in ci_table[model_key][dataset_name].items():
                print(f"    CI {k}: ({lo:.4f}, {hi:.4f})", flush=True)

            # Length stratification
            length_table[model_key][dataset_name] = {}
            for method in AGGREGATIONS:
                strat = length_stratified_auroc(records, method, threshold=5)
                length_table[model_key][dataset_name][method] = strat

            # Visualizations
            plot_roc_curves(method_score_arrays, labels_arr, model_key, dataset_name, FIGURES_DIR)
            for method in AGGREGATIONS:
                scores_m, labels_m = all_method_scores[method]
                plot_score_histograms(scores_m, labels_m, model_key, dataset_name, method, FIGURES_DIR)

        # Free GPU memory before next model
        del model, tokenizer
        import torch
        torch.cuda.empty_cache()

    # Save AUROC table
    auroc_rows = []
    for model_key in auroc_table:
        for dataset_name in auroc_table[model_key]:
            row = {"model": model_key, "dataset": dataset_name}
            row.update(auroc_table[model_key][dataset_name])
            row.update({f"auprc_{m}": auprc_table[model_key][dataset_name][m] for m in AGGREGATIONS})
            row.update({f"ece_{m}": ece_table[model_key][dataset_name][m] for m in AGGREGATIONS})
            auroc_rows.append(row)
    auroc_df = pd.DataFrame(auroc_rows)
    auroc_df.to_csv(os.path.join(RESULTS_DIR, "auroc_table.csv"), index=False)
    print(f"\n\nAUROC Table:\n{auroc_df.to_string()}", flush=True)

    # Save bootstrap CI table
    ci_rows = []
    for model_key in ci_table:
        for dataset_name in ci_table[model_key]:
            row = {"model": model_key, "dataset": dataset_name}
            for pair_key, (lo, hi) in ci_table[model_key][dataset_name].items():
                aurocs = auroc_table[model_key][dataset_name]
                a, b = pair_key.replace("_vs_", " ").split()
                diff = aurocs[a] - aurocs[b]
                row[f"{pair_key}_diff"] = diff
                row[f"{pair_key}_ci_lower"] = lo
                row[f"{pair_key}_ci_upper"] = hi
            ci_rows.append(row)
    ci_df = pd.DataFrame(ci_rows)
    ci_df.to_csv(os.path.join(RESULTS_DIR, "bootstrap_ci_table.csv"), index=False)
    print(f"\nBootstrap CI Table:\n{ci_df.to_string()}", flush=True)

    # Gate check
    gate_passed, gate_justification = check_gate(ci_table, auroc_table)
    gate_result = "PASS" if gate_passed else "FAIL"
    print(f"\n{'='*60}", flush=True)
    print(f"GATE RESULT: {gate_result}", flush=True)
    print(f"Justification: {gate_justification}", flush=True)
    print(f"{'='*60}", flush=True)

    # Write gate decision
    gate_md = f"""# Gate Decision: H-E1

**Result:** {gate_result}

**Justification:** {gate_justification}

## AUROC Table

{auroc_df.to_markdown(index=False)}

## Bootstrap CI Table

{ci_df.to_markdown(index=False)}

## Length Stratification

```json
{json.dumps(length_table, indent=2)}
```
"""
    with open(os.path.join(RESULTS_DIR, "gate_decision_h-e1.md"), "w") as f:
        f.write(gate_md)

    # Save structured results
    results_json = {
        "hypothesis_id": "h-e1",
        "gate_result": gate_result,
        "gate_justification": gate_justification,
        "auroc_table": auroc_table,
        "auprc_table": auprc_table,
        "ece_table": ece_table,
        "ci_table": {
            m: {d: {k: list(v) for k, v in ci_table[m][d].items()} for d in ci_table[m]}
            for m in ci_table
        },
        "length_stratification": length_table,
    }

    results_path = os.path.join(
        os.path.dirname(RESULTS_DIR), "experiment_results.json"
    )
    with open(results_path, "w") as f:
        json.dump(results_json, f, indent=2)
    print(f"\nResults saved to: {results_path}", flush=True)

    # Also save to outputs/results.csv
    outputs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
    os.makedirs(outputs_dir, exist_ok=True)
    auroc_df.to_csv(os.path.join(outputs_dir, "results.csv"), index=False)

    return results_json


if __name__ == "__main__":
    main()
