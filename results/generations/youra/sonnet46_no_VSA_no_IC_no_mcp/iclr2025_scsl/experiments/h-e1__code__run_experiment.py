#!/usr/bin/env python3
"""
h-e1: Spurious/Task Probe Accuracy Ratio Study
Orchestrates full pipeline: load data → extract features → probe → stats → gate → figures.
"""
import csv
import logging
import os
import sys

import torch

# ensure imports work from code/ directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from config import (
    SEEDS, PARADIGMS, BATCH_SIZE, RESULTS_DIR, FIGURES_DIR,
    LOG_PATH, LOG_DIR, LOG_FORMAT, LOG_LEVEL, CACHE_DIR,
)
from data_utils import get_waterbirds_subsets, get_full_val_loader, get_test_loader
from model_utils import LOADERS, get_or_extract_features
from probe_utils import compute_ratio
from stats_utils import run_anova, pairwise_tests, check_gate, export_results
from viz_utils import (
    plot_ratio_bar, plot_acc_heatmap, plot_acc_scatter,
    plot_pvalue_matrix, plot_ratio_violin,
)


def setup_logging():
    os.makedirs(LOG_DIR, exist_ok=True)
    logging.basicConfig(
        filename=LOG_PATH,
        level=getattr(logging, LOG_LEVEL),
        format=LOG_FORMAT,
    )
    # also echo to stdout
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(LOG_FORMAT))
    logging.getLogger().addHandler(console)


def main(device=None):
    setup_logging()
    if device is None:
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
    logging.info(f"=== h-e1 experiment start === device={device}")

    # 1. Load data (once)
    _, val_data, test_data = get_waterbirds_subsets()
    val_loader = get_full_val_loader(val_data, batch_size=BATCH_SIZE)
    test_loader = get_test_loader(test_data, batch_size=BATCH_SIZE)

    val_metadata = val_data.metadata_array  # needed for group-balanced sampling

    ratios = {p: [] for p in PARADIGMS}
    acc_records = []  # for visualization

    # 2. For each paradigm: load model, extract features (cached), compute ratios
    for paradigm in PARADIGMS:
        logging.info(f"--- Paradigm: {paradigm} ---")
        load_fn = LOADERS[paradigm]
        model = load_fn(device)

        feats_val, task_lbls_val, spur_lbls_val = get_or_extract_features(
            model, val_loader, device,
            cache_key=f"{paradigm}_val", cache_dir=CACHE_DIR,
        )
        feats_test, task_lbls_test, spur_lbls_test = get_or_extract_features(
            model, test_loader, device,
            cache_key=f"{paradigm}_test", cache_dir=CACHE_DIR,
        )

        # free GPU memory
        del model
        if device == 'cuda':
            torch.cuda.empty_cache()

        # 3. For each seed: compute_ratio → log
        for seed in SEEDS:
            result = compute_ratio(
                feats_val, task_lbls_val, spur_lbls_val, val_metadata,
                feats_test, task_lbls_test, spur_lbls_test,
                seed=seed, paradigm=paradigm,
            )
            ratios[paradigm].append(result['ratio'])
            acc_records.append({
                'paradigm': paradigm, 'seed': seed,
                'spurious_acc': result['spurious_acc'],
                'task_acc': result['task_acc'],
                'ratio': result['ratio'],
            })

    # 4. Statistical analysis
    anova_result = run_anova(ratios)
    logging.info(f"ANOVA: F={anova_result[0]:.4f}, p={anova_result[1]:.4f}")

    pair_results = pairwise_tests(ratios)
    for r in pair_results:
        logging.info(
            f"  {r['pair']}: t={r['t']:.3f}, p_bonf={r['p_bonf']:.4f}, "
            f"d={r['cohens_d']:.3f}, diff={r['mean_diff']:.4f}"
        )

    # 5. Gate check
    gate_ok, passing_pairs = check_gate(pair_results)
    logging.info(f"GATE RESULT: {'SATISFIED' if gate_ok else 'FAILED'}")

    # 6. Save results CSV + JSON
    os.makedirs(RESULTS_DIR, exist_ok=True)
    csv_path = os.path.join(RESULTS_DIR, 'h-e1_ratios.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['paradigm', 'seed', 'spurious_acc', 'task_acc', 'ratio'])
        writer.writeheader()
        writer.writerows(acc_records)
    logging.info(f"Results CSV saved: {csv_path}")

    json_path = os.path.join(RESULTS_DIR, 'h-e1_stats.json')
    export_results(ratios, anova_result, pair_results, gate_ok, passing_pairs, json_path)

    # also write to canonical experiment_results.json location
    exp_json = os.path.join(os.path.dirname(RESULTS_DIR), 'experiment_results.json')
    import json, shutil
    shutil.copy(json_path, exp_json)
    logging.info(f"experiment_results.json written: {exp_json}")

    # 7. Generate all figures
    os.makedirs(FIGURES_DIR, exist_ok=True)
    plot_ratio_bar(ratios, pair_results, FIGURES_DIR)
    plot_acc_heatmap(acc_records, FIGURES_DIR)
    plot_acc_scatter(acc_records, FIGURES_DIR)
    plot_pvalue_matrix(pair_results, PARADIGMS, FIGURES_DIR)
    plot_ratio_violin(ratios, FIGURES_DIR)

    logging.info("=== h-e1 experiment COMPLETE ===")
    print(f"\n{'='*60}")
    print(f"GATE: {'SATISFIED ✓' if gate_ok else 'FAILED ✗'}")
    print(f"ANOVA p={anova_result[1]:.4f}")
    for r in pair_results:
        sig = '**' if r['p_bonf'] < 0.05 else '  '
        print(f"  {sig} {r['pair']}: p_bonf={r['p_bonf']:.4f}, diff={r['mean_diff']:.4f}")
    print(f"{'='*60}\n")

    return gate_ok, ratios, pair_results


if __name__ == '__main__':
    gate_ok, ratios, pair_results = main()
    sys.exit(0 if gate_ok else 1)
