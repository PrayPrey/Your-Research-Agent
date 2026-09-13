"""
Fast evaluation: TruthfulQA (817 samples) + subsample TriviaQA (500)
for both models. Enough for statistically meaningful gate verdict.
~500 samples x 0.9s = 7.5min per model x 2 datasets = ~30min total.
"""
import os
import sys
import json
import warnings
import logging

logging.getLogger("transformers").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import MODELS, AGGREGATIONS, SEED, BOOTSTRAP_N, RESULTS_DIR, FIGURES_DIR, FARQUHAR_DATA_DIR
from data_loader import get_dataset
from inference import load_model, run_inference
from aggregation import compute_all_scores
from evaluation import evaluate_cell, compute_all_pairwise_ci, length_stratified_auroc, check_gate
from visualization import plot_roc_curves, plot_score_histograms

np.random.seed(SEED)

# Fast eval config: smaller subsamples for speed
FAST_DATASETS = {
    "trivia_qa": 500,
    "truthful_qa": None,  # full 817
}


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(FIGURES_DIR, exist_ok=True)

    auroc_table = {}
    auprc_table = {}
    ece_table = {}
    ci_table = {}
    length_table = {}

    for model_key in MODELS:
        print(f"\n{'='*60}", flush=True)
        print(f"Model: {model_key} ({MODELS[model_key]})", flush=True)
        print(f"{'='*60}", flush=True)
        model, tokenizer = load_model(model_key)

        auroc_table[model_key] = {}
        auprc_table[model_key] = {}
        ece_table[model_key] = {}
        ci_table[model_key] = {}
        length_table[model_key] = {}

        for dataset_name, max_n in FAST_DATASETS.items():
            print(f"\n  Dataset: {dataset_name}", flush=True)
            samples = get_dataset(dataset_name, FARQUHAR_DATA_DIR)
            print(f"  Loaded {len(samples)} samples", flush=True)

            if max_n is not None and len(samples) > max_n:
                rng = np.random.default_rng(SEED)
                idx = rng.choice(len(samples), size=max_n, replace=False)
                idx.sort()
                samples = [samples[i] for i in idx]
                print(f"  Subsampled to {len(samples)}", flush=True)

            records = run_inference(samples, model, tokenizer)
            print(f"  Valid records: {len(records)}", flush=True)

            if len(records) < 50:
                print(f"  Too few records, skipping", flush=True)
                continue

            scores_path = os.path.join(RESULTS_DIR, f"scores_{model_key}_{dataset_name}.npz")
            all_method_scores = compute_all_scores(records)
            np.savez(
                scores_path,
                **{f"{m}_scores": all_method_scores[m][0] for m in AGGREGATIONS},
                labels=all_method_scores["min"][1],
            )

            auroc_table[model_key][dataset_name] = {}
            auprc_table[model_key][dataset_name] = {}
            ece_table[model_key][dataset_name] = {}

            for method in AGGREGATIONS:
                scores, labels = all_method_scores[method]
                metrics = evaluate_cell(labels, scores)
                auroc_table[model_key][dataset_name][method] = metrics["auroc"]
                auprc_table[model_key][dataset_name][method] = metrics["auprc"]
                ece_table[model_key][dataset_name][method] = metrics["ece"]
                print(f"    {method}: AUROC={metrics['auroc']:.4f}", flush=True)

            print(f"  Bootstrap CIs...", flush=True)
            method_score_arrays = {m: all_method_scores[m][0] for m in AGGREGATIONS}
            labels_arr = all_method_scores["min"][1]
            ci_table[model_key][dataset_name] = compute_all_pairwise_ci(
                method_score_arrays, labels_arr, n_resamples=BOOTSTRAP_N
            )
            for k, (lo, hi) in ci_table[model_key][dataset_name].items():
                print(f"    CI {k}: ({lo:.4f}, {hi:.4f})", flush=True)

            length_table[model_key][dataset_name] = {}
            for method in AGGREGATIONS:
                strat = length_stratified_auroc(records, method, threshold=5)
                length_table[model_key][dataset_name][method] = strat

            plot_roc_curves(method_score_arrays, labels_arr, model_key, dataset_name, FIGURES_DIR)
            for method in AGGREGATIONS:
                s, l = all_method_scores[method]
                plot_score_histograms(s, l, model_key, dataset_name, method, FIGURES_DIR)

        del model, tokenizer
        import torch
        torch.cuda.empty_cache()

    # Save results
    auroc_rows = []
    for mk in auroc_table:
        for dn in auroc_table[mk]:
            row = {"model": mk, "dataset": dn}
            row.update(auroc_table[mk][dn])
            row.update({f"auprc_{m}": auprc_table[mk][dn].get(m, float("nan")) for m in AGGREGATIONS})
            row.update({f"ece_{m}": ece_table[mk][dn].get(m, float("nan")) for m in AGGREGATIONS})
            auroc_rows.append(row)

    auroc_df = pd.DataFrame(auroc_rows)
    auroc_df.to_csv(os.path.join(RESULTS_DIR, "auroc_table.csv"), index=False)
    print(f"\nAUROC Table:\n{auroc_df.to_string()}", flush=True)

    ci_rows = []
    for mk in ci_table:
        for dn in ci_table[mk]:
            row = {"model": mk, "dataset": dn}
            for pk, (lo, hi) in ci_table[mk][dn].items():
                a, b = pk.replace("_vs_", " ").split()
                diff = auroc_table[mk][dn].get(a, 0) - auroc_table[mk][dn].get(b, 0)
                row[f"{pk}_diff"] = diff
                row[f"{pk}_ci_lower"] = lo
                row[f"{pk}_ci_upper"] = hi
            ci_rows.append(row)

    ci_df = pd.DataFrame(ci_rows)
    ci_df.to_csv(os.path.join(RESULTS_DIR, "bootstrap_ci_table.csv"), index=False)
    print(f"\nCI Table:\n{ci_df.to_string()}", flush=True)

    gate_passed, gate_justification = check_gate(ci_table, auroc_table)
    gate_result = "PASS" if gate_passed else "FAIL"
    print(f"\nGATE RESULT: {gate_result}", flush=True)
    print(f"Justification: {gate_justification}", flush=True)

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

    results_json = {
        "hypothesis_id": "h-e1",
        "gate_result": gate_result,
        "gate_justification": gate_justification,
        "eval_mode": "fast_eval",
        "datasets_evaluated": list(FAST_DATASETS.keys()),
        "sample_sizes": {k: v if v else "full" for k, v in FAST_DATASETS.items()},
        "auroc_table": auroc_table,
        "auprc_table": auprc_table,
        "ece_table": ece_table,
        "ci_table": {
            m: {d: {k: list(v) for k, v in ci_table[m][d].items()} for d in ci_table[m]}
            for m in ci_table
        },
        "length_stratification": length_table,
    }

    base_dir = os.path.dirname(RESULTS_DIR)
    with open(os.path.join(base_dir, "experiment_results.json"), "w") as f:
        json.dump(results_json, f, indent=2)

    outputs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
    os.makedirs(outputs_dir, exist_ok=True)
    auroc_df.to_csv(os.path.join(outputs_dir, "results.csv"), index=False)

    print(f"\nDone. Results in {RESULTS_DIR}", flush=True)
    return results_json


if __name__ == "__main__":
    main()
