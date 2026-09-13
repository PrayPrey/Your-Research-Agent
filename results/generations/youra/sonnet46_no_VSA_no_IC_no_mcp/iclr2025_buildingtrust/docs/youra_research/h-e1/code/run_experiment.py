#!/usr/bin/env python3
"""H-E1 ECE Measurement Experiment: Clean vs Adversarial calibration comparison."""

import os
import sys
import time
import json
import logging

# Ensure code dir is on path
CODE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CODE_DIR)

from config import ExperimentConfig
from data.loader import load_all_datasets, save_manifest
from models.loader import load_model, unload_model, get_checkpoint_hash, decide_quantization, check_vram_gb
from evaluation.logit_extractor import extract_cell
from evaluation.ece import compute_both
from evaluation.validator import verify_logit_extraction, prevalidate_cell, check_clean_sanity
from results.storage import append_cell_row, write_cell_jsonl, write_gate_result, write_json
from visualization.plots import (
    fig1_ece_comparison, fig2_reliability_diagrams,
    fig3_coverage_heatmap, fig4_confidence_boxplots, fig5_ece_sensitivity
)

import pandas as pd


def log_error(errors_log: str, msg: str) -> None:
    os.makedirs(os.path.dirname(errors_log), exist_ok=True)
    with open(errors_log, "a") as f:
        f.write(f"{time.strftime('%Y-%m-%dT%H:%M:%S')} ERROR: {msg}\n")
    print(f"ERROR: {msg}")


def main(config: ExperimentConfig = None) -> None:
    if config is None:
        config = ExperimentConfig()

    os.makedirs(config.results_dir, exist_ok=True)
    os.makedirs(config.figures_dir, exist_ok=True)

    print(f"H-E1 Experiment starting")
    print(f"Models: {config.models}")
    print(f"VRAM: {check_vram_gb():.1f} GB")
    print(f"Results: {config.results_dir}")

    # Load all datasets
    print("\n=== Loading Datasets ===")
    datasets = load_all_datasets(
        seed=config.seed,
        subsample_clean=config.subsample_clean,
        subsample_adv=config.subsample_adv,
    )
    save_manifest(datasets, f"{config.results_dir}/dataset_manifest.json")

    ece_rows = []
    clean_ece_by_model = {}
    example_paths = []

    # Sequential model loop
    for model_id in config.models:
        print(f"\n=== Model: {model_id} ===")
        use_4bit = decide_quantization(model_id, config)
        print(f"Loading model (use_4bit={use_4bit})...")
        try:
            model, tokenizer = load_model(model_id, use_4bit=use_4bit)
        except Exception as e:
            log_error(config.errors_log, f"Model load FAILED: {model_id} error={e}")
            # Mark all cells for this model as failed
            for task in ["qqp", "sst2", "nli"]:
                clean_key, adv_key = config.task_split_map[task]
                for split_name in ["clean", "adversarial"]:
                    ece_rows.append({
                        "model": model_id, "task": task, "split": split_name,
                        "n_examples": 0, "ece_15": None, "ece_10": None,
                        "accuracy": None, "mean_confidence": None,
                        "cell_passed": False,
                    })
            continue

        checkpoint_hash = get_checkpoint_hash(model_id)
        print(f"Model loaded. Checkpoint hash: {checkpoint_hash}")

        for task in ["qqp", "sst2", "nli"]:
            clean_key, adv_key = config.task_split_map[task]

            splits = {}
            if datasets.get(clean_key) is not None:
                splits["clean"] = datasets[clean_key]
            if datasets.get(adv_key) is not None:
                splits["adversarial"] = datasets[adv_key]
            # ANLI rounds for NLI task
            if task == "nli":
                for anli_split in config.anli_splits:
                    if datasets.get(anli_split) is not None:
                        splits[anli_split] = datasets[anli_split]

            for split_name, dataset in splits.items():
                print(f"\n  [{model_id.split('/')[-1]}/{task}/{split_name}] n={len(dataset)}")
                cell_key = f"{model_id.split('/')[-1]}_{task}_{split_name}"
                jsonl_path = f"{config.results_dir}/{cell_key}_examples.jsonl"

                try:
                    # Pre-validation
                    pre_result = prevalidate_cell(
                        model, tokenizer, dataset, task, model_id,
                        n=config.prevalidation_n,
                        min_confidence_uniform=config.min_confidence_uniform,
                    )
                    if not pre_result.passed:
                        log_error(config.errors_log,
                            f"Pre-validation FAILED: {cell_key} indicators={pre_result.indicators}")
                        ece_rows.append({
                            "model": model_id, "task": task, "split": split_name,
                            "n_examples": 0, "ece_15": None, "ece_10": None,
                            "accuracy": None, "mean_confidence": None,
                            "cell_passed": False,
                        })
                        continue

                    # Full cell evaluation
                    cell_result = extract_cell(
                        model, tokenizer, dataset, task, model_id,
                        batch_size=config.batch_size
                    )
                    correct = (cell_result.pred_labels == cell_result.true_labels)
                    ece_15, ece_10 = compute_both(cell_result.confidences, correct)
                    val_result = verify_logit_extraction(cell_result, ece_15, min_examples=config.min_examples_per_cell, min_confidence_uniform=config.min_confidence_uniform)

                    accuracy = float(correct.mean())
                    mean_conf = float(cell_result.confidences.mean())

                    print(f"    ECE_15={ece_15:.4f}  ECE_10={ece_10:.4f}  acc={accuracy:.3f}  "
                          f"mean_conf={mean_conf:.3f}  cell_passed={val_result.passed}")
                    if not val_result.passed:
                        print(f"    Validation indicators: {val_result.indicators}")

                    row = {
                        "model": model_id, "task": task, "split": split_name,
                        "n_examples": len(cell_result.confidences),
                        "ece_15": ece_15, "ece_10": ece_10,
                        "accuracy": accuracy,
                        "mean_confidence": mean_conf,
                        "cell_passed": val_result.passed,
                        "checkpoint_hash": checkpoint_hash,
                        "use_4bit": use_4bit,
                    }
                    append_cell_row(f"{config.results_dir}/ece_results.csv", row)
                    write_cell_jsonl(jsonl_path, cell_result)
                    example_paths.append(jsonl_path)
                    ece_rows.append(row)

                    if split_name == "clean":
                        clean_ece_by_model.setdefault(model_id, {})[task] = ece_15

                except Exception as e:
                    import traceback
                    log_error(config.errors_log,
                        f"Cell FAILED: {cell_key} error={e}\n{traceback.format_exc()}")
                    ece_rows.append({
                        "model": model_id, "task": task, "split": split_name,
                        "n_examples": 0, "ece_15": None, "ece_10": None,
                        "accuracy": None, "mean_confidence": None,
                        "cell_passed": False,
                    })

        unload_model(model)
        print(f"\nModel {model_id} unloaded.")

    # Finalize
    _finalize(config, ece_rows, clean_ece_by_model, example_paths)


def _finalize(config, ece_rows, clean_ece_by_model, example_paths):
    import pandas as pd

    df = pd.DataFrame(ece_rows)
    df.to_csv(f"{config.results_dir}/ece_results_full.csv", index=False)

    passed_cells = int(df["cell_passed"].sum()) if "cell_passed" in df.columns else 0
    failed_cells = df[~df["cell_passed"].fillna(False)][["model", "task", "split"]].to_dict("records") if "cell_passed" in df.columns else []

    clean_sanity_passed, sanity_details = check_clean_sanity(
        clean_ece_by_model,
        clean_ece_min=config.clean_ece_min,
        clean_ece_max=config.clean_ece_max,
        min_models=config.min_models_sanity,
    )

    # H-E1 existence gate: ≥1 adversarial cell with ECE > clean counterpart
    adv_splits = ["adversarial", "anli_r1", "anli_r2", "anli_r3"]
    existence_evidence = []
    for _, row in df.iterrows():
        if row.get("split") not in adv_splits or row.get("ece_15") is None:
            continue
        # Find matching clean cell
        clean_row = df[(df["model"] == row["model"]) & (df["task"] == row["task"]) & (df["split"] == "clean")]
        if clean_row.empty or clean_row.iloc[0]["ece_15"] is None:
            continue
        clean_ece = clean_row.iloc[0]["ece_15"]
        adv_ece = row["ece_15"]
        delta = adv_ece - clean_ece
        existence_evidence.append({
            "model": row["model"], "task": row["task"], "split": row["split"],
            "ece_clean": clean_ece, "ece_adv": adv_ece, "delta": delta,
        })

    positive_evidence = [e for e in existence_evidence if e["delta"] > 0]
    gate_passed = len(positive_evidence) >= config.gate_min_cells

    print(f"\n{'='*60}")
    print(f"H-E1 GATE RESULT: {'PASS' if gate_passed else 'FAIL'}")
    print(f"  Cells passed validation: {passed_cells}/{len(ece_rows)}")
    print(f"  Existence evidence (adv ECE > clean ECE): {len(positive_evidence)}/{len(existence_evidence)} pairs")
    if existence_evidence:
        for e in sorted(existence_evidence, key=lambda x: -x["delta"])[:5]:
            print(f"    {e['model'].split('/')[-1]}/{e['task']}/{e['split']}: "
                  f"clean={e['ece_clean']:.4f}  adv={e['ece_adv']:.4f}  delta={e['delta']:+.4f}")
    print(f"  Clean sanity: {'PASS' if clean_sanity_passed else 'FAIL'} {sanity_details}")
    print(f"{'='*60}\n")

    write_gate_result(
        path=f"{config.results_dir}/gate_result.json",
        passed_cells=passed_cells,
        failed_cells=failed_cells,
        clean_sanity=clean_sanity_passed,
        gate_passed=gate_passed,
        summary={
            "existence_evidence_count": len(positive_evidence),
            "total_pairs_evaluated": len(existence_evidence),
            "gate_min_cells": config.gate_min_cells,
            "positive_evidence": positive_evidence,
        },
    )

    write_json(f"{config.results_dir}/sanity_details.json", sanity_details)

    # Figures
    try:
        valid_df = df.dropna(subset=["ece_15"])
        if len(valid_df) > 0:
            fig1_ece_comparison(valid_df, f"{config.figures_dir}/fig1_ece_comparison.png")
            print(f"fig1 saved")
    except Exception as e:
        print(f"fig1 failed: {e}")

    try:
        valid_paths = [p for p in example_paths if os.path.exists(p)]
        if valid_paths:
            fig2_reliability_diagrams(valid_paths, f"{config.figures_dir}/fig2_reliability_diagrams.png")
            print(f"fig2 saved")
    except Exception as e:
        print(f"fig2 failed: {e}")

    try:
        if len(df) > 0:
            fig3_coverage_heatmap(df, f"{config.figures_dir}/fig3_coverage_heatmap.png")
            print(f"fig3 saved")
    except Exception as e:
        print(f"fig3 failed: {e}")

    try:
        if valid_paths:
            fig4_confidence_boxplots(valid_paths, f"{config.figures_dir}/fig4_confidence_distribution.png")
            print(f"fig4 saved")
    except Exception as e:
        print(f"fig4 failed: {e}")

    try:
        valid_df2 = df.dropna(subset=["ece_15", "ece_10"])
        if len(valid_df2) > 0:
            fig5_ece_sensitivity(valid_df2, f"{config.figures_dir}/fig5_ece_sensitivity.png")
            print(f"fig5 saved")
    except Exception as e:
        print(f"fig5 failed: {e}")

    print("Experiment complete.")
    return gate_passed


if __name__ == "__main__":
    cfg = ExperimentConfig()
    main(cfg)
