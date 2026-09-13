import argparse
import csv
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as cfg
from score_loader import load_scores
from bootstrap_ci import compute_auroc_table
from gate_check import evaluate_gates
from figures import save_all_figures


def _make_json_serializable(obj):
    if isinstance(obj, dict):
        return {str(k): _make_json_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_make_json_serializable(i) for i in obj]
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (np.float32, np.float64)):
        return float(obj)
    if isinstance(obj, (np.int32, np.int64)):
        return int(obj)
    return obj


def main(args) -> None:
    os.makedirs(cfg.RESULTS_DIR, exist_ok=True)
    os.makedirs(cfg.FIGURES_DIR, exist_ok=True)

    print("=== H-M3: AUROC Bootstrap CI Analysis ===")
    print(f"H-E1 results dir : {args.h_e1_dir}")
    print(f"H-M2 results dir : {args.h_m2_dir}")
    print(f"Bootstrap n      : {args.n_bootstrap}")
    print(f"Seed             : {args.seed}")

    # 1. Load scores
    data = {}
    for model in cfg.MODELS_TO_RUN:
        for dataset in cfg.DATASETS:
            scores_dict, labels = load_scores(model, dataset, args.h_e1_dir, args.h_m2_dir)
            if scores_dict is None:
                print(f"[WARN] Missing: {model} × {dataset} — skip")
                continue
            print(f"[OK]  Loaded {model} × {dataset}: n={len(labels)}, pos={labels.sum()}")
            for agg in cfg.AGGREGATION_METHODS:
                data[(model, dataset, agg)] = (scores_dict[agg], labels)

    if not data:
        print("ERROR: No data loaded. Exiting.")
        sys.exit(1)

    # 2. Compute AUROC + CI table
    print("\nComputing AUROC + bootstrap CI...")
    auroc_table = compute_auroc_table(data, args.n_bootstrap, args.seed, cfg.CONFIDENCE_LEVEL)

    # 3. Gate evaluation
    gate_result = evaluate_gates(auroc_table, cfg.P1_THRESHOLD, cfg.P2_THRESHOLD)

    # 4. Print AUROC table
    print("\n--- AUROC Table ---")
    for (model, ds, agg), entry in sorted(auroc_table["auroc"].items()):
        print(f"  {model:8s} {ds:15s} {agg:8s}: AUROC={entry['auroc']:.4f} "
              f"CI=[{entry['ci_lower']:.4f}, {entry['ci_upper']:.4f}]")

    print("\n--- Diff Table (AUROC(min) - AUROC(mean)) ---")
    for (model, ds), d in sorted(auroc_table["diff"].items()):
        print(f"  {model:8s} {ds:15s}: diff={d['diff']:+.4f} "
              f"CI=[{d['ci_lower']:+.4f}, {d['ci_upper']:+.4f}]")

    # 5. Serialize results
    auroc_json = {str(k): v for k, v in auroc_table["auroc"].items()}
    diff_json  = {str(k): v for k, v in auroc_table["diff"].items()}

    with open(os.path.join(cfg.RESULTS_DIR, "auroc_table.json"), "w") as f:
        json.dump(_make_json_serializable({"auroc": auroc_json, "diff": diff_json}), f, indent=2)

    with open(os.path.join(cfg.RESULTS_DIR, "gate_conditions.json"), "w") as f:
        json.dump(_make_json_serializable(gate_result), f, indent=2)

    # auroc_table.csv
    csv_path = os.path.join(cfg.RESULTS_DIR, "auroc_table.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["model", "dataset", "aggregation", "auroc", "ci_lower", "ci_upper"])
        for (model, ds, agg), entry in sorted(auroc_table["auroc"].items()):
            writer.writerow([model, ds, agg, entry["auroc"], entry["ci_lower"], entry["ci_upper"]])

    print(f"\nResults saved to {cfg.RESULTS_DIR}")

    # 6. Figures
    print("\nGenerating figures...")
    save_all_figures(auroc_table, gate_result, cfg.FIGURES_DIR)

    # 7. Gate summary
    print(f"\n=== Gate: {gate_result['gate']} ({gate_result['n_gates_met']}/3 met) ===")
    print(f"  P1 (min>mean on trivia_qa+nq, both models): {'PASS' if gate_result['p1_met'] else 'FAIL'}")
    print(f"  P2 (mean>min on truthful_qa, both models) : {'PASS' if gate_result['p2_met'] else 'FAIL'}")
    print(f"  P3 (raw_sum worst on all datasets)        : {'PASS' if gate_result['p3_met'] else 'FAIL'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="H-M3: AUROC Bootstrap CI Analysis")
    parser.add_argument("--h_e1_dir",    default=cfg.H_E1_RESULTS_DIR)
    parser.add_argument("--h_m2_dir",    default=cfg.H_M2_RESULTS_DIR)
    parser.add_argument("--seed",        type=int, default=cfg.SEED)
    parser.add_argument("--n_bootstrap", type=int, default=cfg.N_RESAMPLES_BOOTSTRAP)
    main(parser.parse_args())
