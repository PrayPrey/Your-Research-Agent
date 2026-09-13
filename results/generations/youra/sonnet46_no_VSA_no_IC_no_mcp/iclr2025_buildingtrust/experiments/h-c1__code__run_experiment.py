#!/usr/bin/env python3
"""H-C1: RLHF Calibration Moderation Experiment.

Tests whether RLHF alignment (chat tuning) moderates adversarial calibration degradation.
Gate (SHOULD_WORK): moderation_rate >= 0.60 AND ΔΔECE_NLI > 0.01
"""
import os
import sys
import json
import time
import traceback
from datetime import datetime

# H-C1 code directory FIRST so h-c1 modules shadow h-e1 where needed
CODE_DIR = os.path.dirname(os.path.abspath(__file__))
HE1_CODE_DIR = os.path.normpath(os.path.join(CODE_DIR, "../../h-e1/code"))
sys.path.insert(0, CODE_DIR)
if HE1_CODE_DIR not in sys.path:
    sys.path.append(HE1_CODE_DIR)  # append so h-c1 stays at front

from config import HC1Config
from data.loader import load_hc1_datasets
from comparison.delta_ece import (
    compute_delta_ece, compare_rlhf_moderation,
    verify_activation, compute_moderation_rate,
    CellECE, ModerationResult,
)
from visualization.plots import (
    fig1_paired_bar, fig2_reliability_grid,
    fig3_ddece_scatter, fig4_anli_gradient,
)
from models.loader import load_model, unload_model, decide_quantization, check_vram_gb


def log_error(errors_log: str, msg: str) -> None:
    os.makedirs(os.path.dirname(errors_log), exist_ok=True)
    with open(errors_log, "a") as f:
        f.write(f"{time.strftime('%Y-%m-%dT%H:%M:%S')} ERROR: {msg}\n")
    print(f"ERROR: {msg}")


def _check_he1_consistency(base_results: dict, config: HC1Config) -> bool:
    nli_cell = base_results.get("NLI-AdvGLUE")
    if nli_cell is None:
        print("WARN: NLI-AdvGLUE cell missing — cannot check H-E1 consistency")
        return False

    consistency_ok = True
    diff_clean = abs(nli_cell.ece_clean - config.he1_base_ece_clean_nli)
    if diff_clean > config.consistency_tolerance:
        print(f"WARN: Base ECE_clean={nli_cell.ece_clean:.4f} vs H-E1 ref {config.he1_base_ece_clean_nli:.4f} "
              f"diff={diff_clean:.4f} > tol {config.consistency_tolerance}")
        consistency_ok = False

    diff_delta = abs(nli_cell.delta_ece - config.he1_base_delta_ece_nli)
    if diff_delta > config.consistency_tolerance:
        print(f"WARN: Base ΔECE={nli_cell.delta_ece:.4f} vs H-E1 ref {config.he1_base_delta_ece_nli:.4f} "
              f"diff={diff_delta:.4f} > tol {config.consistency_tolerance}")
        consistency_ok = False

    if consistency_ok:
        print(f"Consistency check PASS: base ECE within tolerance of H-E1 reference")
    return consistency_ok


def save_results(all_cell_results: dict, moderation_results: list,
                 moderation_rate: float, gate_passed: bool,
                 indicators: dict, config: HC1Config) -> None:
    os.makedirs(config.results_dir, exist_ok=True)
    cells = []
    for model_id, cell_dict in all_cell_results.items():
        for cell_id, cell_ece in cell_dict.items():
            cells.append({
                "model": "base" if "chat" not in model_id else "chat",
                "model_id": model_id,
                "cell_id": cell_id,
                "ece_clean": cell_ece.ece_clean,
                "ece_adv": cell_ece.ece_adv,
                "delta_ece": cell_ece.delta_ece,
                "n_clean": cell_ece.n_clean,
                "n_adv": cell_ece.n_adv,
            })

    nli_ddece = next((r.ddece for r in moderation_results if r.cell_id == "NLI-AdvGLUE"), None)
    results = {
        "hypothesis_id": "h-c1",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "cells": cells,
        "moderation_results": [r._asdict() for r in moderation_results],
        "summary": {
            "moderation_rate": moderation_rate,
            "ddece_nli": nli_ddece,
            "gate_result": "CONFIRMED" if gate_passed else "FAILED",
            "mechanism_activated": all(indicators.values()) if isinstance(indicators, dict) and "error" not in indicators else False,
            "consistency_ok": None,  # filled after
        },
        "indicators": indicators,
    }

    with open(config.results_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved: {config.results_file}")
    return results


def write_validation_report(moderation_results: list, moderation_rate: float,
                            gate_passed: bool, indicators: dict,
                            nli_ddece: float, consistency_ok: bool,
                            base_results: dict, config: HC1Config) -> None:
    timestamp = datetime.utcnow().isoformat() + "Z"
    gate_str = "CONFIRMED" if gate_passed else "FAILED"

    lines = [
        f"# Validation Report: h-c1",
        f"date: {timestamp}",
        f"gate_result: {gate_str}",
        f"",
        f"## Gate Metrics",
        f"- moderation_rate: {moderation_rate:.4f} (threshold: {config.moderation_rate_threshold})",
        f"- ddece_nli: {nli_ddece:.4f} (threshold: {config.ddece_nli_threshold})",
        f"- gate_result: {gate_str}",
        f"",
        f"## Consistency Check (vs H-E1)",
    ]

    nli_cell = base_results.get("NLI-AdvGLUE")
    if nli_cell:
        lines += [
            f"- he1_base_ece_clean_nli expected: {config.he1_base_ece_clean_nli:.3f} ± {config.consistency_tolerance}, "
            f"observed: {nli_cell.ece_clean:.4f}",
            f"- he1_base_delta_ece_nli expected: {config.he1_base_delta_ece_nli:.3f} ± {config.consistency_tolerance}, "
            f"observed: {nli_cell.delta_ece:.4f}",
        ]
    lines.append(f"- consistency_ok: {consistency_ok}")
    lines.append(f"")
    lines.append(f"## Per-Cell Results")
    lines.append(f"| cell_id | ΔECE_base | ΔECE_chat | ΔΔECE | moderation_confirmed |")
    lines.append(f"|---------|-----------|-----------|-------|---------------------|")
    for r in moderation_results:
        lines.append(f"| {r.cell_id} | {r.delta_ece_base:.4f} | {r.delta_ece_chat:.4f} | {r.ddece:.4f} | {r.moderation_confirmed} |")
    lines.append(f"")
    lines.append(f"## Mechanism Indicators")
    for k, v in indicators.items():
        lines.append(f"- {k}: {v}")
    lines.append(f"")
    lines.append(f"## Key Findings")
    lines.append(f"- moderation_rate={moderation_rate:.4f} {'≥' if moderation_rate >= config.moderation_rate_threshold else '<'} "
                 f"threshold={config.moderation_rate_threshold} → {'PASS' if moderation_rate >= config.moderation_rate_threshold else 'FAIL'}")
    lines.append(f"- ΔΔECE_NLI={nli_ddece:.4f} {'>' if nli_ddece is not None and nli_ddece > config.ddece_nli_threshold else '≤'} "
                 f"threshold={config.ddece_nli_threshold} → {'PASS' if nli_ddece is not None and nli_ddece > config.ddece_nli_threshold else 'FAIL'}")

    os.makedirs(os.path.dirname(config.validation_report) if os.path.dirname(config.validation_report) else ".", exist_ok=True)
    with open(config.validation_report, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Validation report saved: {config.validation_report}")


def main(config: HC1Config = None) -> bool:
    if config is None:
        config = HC1Config()

    os.makedirs(config.results_dir, exist_ok=True)
    os.makedirs(config.figures_dir, exist_ok=True)

    print(f"H-C1 Experiment starting")
    print(f"Models: {config.models}")
    print(f"VRAM: {check_vram_gb():.1f} GB")
    print(f"Eval cells: {list(config.eval_cells.keys())}")

    # Step 1: Load datasets once
    print("\n=== Loading Datasets ===")
    datasets = load_hc1_datasets(
        seed=config.seed,
        subsample_clean=config.subsample_clean,
        subsample_adv=config.subsample_adv,
    )

    # Step 2: Evaluate each model sequentially
    all_cell_results: dict = {}  # model_id -> {cell_id -> CellECE}

    for model_id in config.models:
        print(f"\n=== Model: {model_id} ===")
        use_4bit = decide_quantization(model_id, config)
        print(f"Loading model (use_4bit={use_4bit})...")

        try:
            model, tokenizer = load_model(model_id, use_4bit=use_4bit)
        except Exception as e:
            log_error(config.errors_log, f"Model load FAILED: {model_id} error={e}\n{traceback.format_exc()}")
            all_cell_results[model_id] = {}
            continue

        cell_results: dict = {}
        for cell_id, (clean_key, adv_key) in config.eval_cells.items():
            clean_ds = datasets.get(clean_key)
            adv_ds = datasets.get(adv_key)
            if clean_ds is None or adv_ds is None:
                log_error(config.errors_log,
                          f"Missing dataset for cell {cell_id}: clean={clean_key}={clean_ds is not None}, "
                          f"adv={adv_key}={adv_ds is not None}")
                continue

            print(f"\n  [{model_id.split('/')[-1]}/{cell_id}] clean_n={len(clean_ds)} adv_n={len(adv_ds)}")
            try:
                cell_ece = compute_delta_ece(
                    model, tokenizer, clean_ds, adv_ds,
                    cell_id=cell_id, model_id=model_id,
                    task="nli", config=config,
                )
                cell_results[cell_id] = cell_ece
                print(f"    ECE_clean={cell_ece.ece_clean:.4f}  ECE_adv={cell_ece.ece_adv:.4f}  "
                      f"ΔECE={cell_ece.delta_ece:.4f}")
            except Exception as e:
                log_error(config.errors_log,
                          f"Cell FAILED: {model_id}/{cell_id} error={e}\n{traceback.format_exc()}")

        all_cell_results[model_id] = cell_results
        unload_model(model)
        print(f"Model {model_id} unloaded.")

    # Step 3: Paired comparison
    base_id = "meta-llama/Llama-2-7b-hf"
    chat_id = "meta-llama/Llama-2-7b-chat-hf"
    base_results = all_cell_results.get(base_id, {})
    chat_results = all_cell_results.get(chat_id, {})

    moderation_results = []
    for cid in config.eval_cells:
        if cid in base_results and cid in chat_results:
            moderation_results.append(
                compare_rlhf_moderation(base_results[cid], chat_results[cid])
            )
        else:
            print(f"WARN: Cell {cid} missing for base or chat — skipping")

    if not moderation_results:
        log_error(config.errors_log, "No moderation results computed — all cells failed")
        return False

    # Step 4: Mechanism activation
    activated, indicators = verify_activation(base_results, chat_results)
    print(f"\nMechanism activation: {activated}")
    for k, v in indicators.items():
        print(f"  {k}: {v}")

    # Step 5: Gate evaluation
    moderation_rate = compute_moderation_rate(moderation_results)
    nli_ddece_result = next((r for r in moderation_results if r.cell_id == "NLI-AdvGLUE"), None)
    nli_ddece = nli_ddece_result.ddece if nli_ddece_result else 0.0

    gate_passed = (moderation_rate >= config.moderation_rate_threshold and
                   nli_ddece > config.ddece_nli_threshold)

    print(f"\n{'='*60}")
    print(f"H-C1 GATE RESULT: {'CONFIRMED' if gate_passed else 'FAILED'}")
    print(f"  moderation_rate: {moderation_rate:.4f} (threshold: {config.moderation_rate_threshold})")
    print(f"  ΔΔECE_NLI: {nli_ddece:.4f} (threshold: {config.ddece_nli_threshold})")
    for r in moderation_results:
        print(f"  {r.cell_id}: ΔECE_base={r.delta_ece_base:.4f} ΔECE_chat={r.delta_ece_chat:.4f} "
              f"ΔΔECE={r.ddece:.4f} moderated={r.moderation_confirmed}")
    print(f"{'='*60}\n")

    # Step 6: H-E1 consistency check
    consistency_ok = _check_he1_consistency(base_results, config)

    # Step 7: Persist results
    results = save_results(all_cell_results, moderation_results, moderation_rate,
                           gate_passed, indicators, config)
    results["summary"]["consistency_ok"] = consistency_ok
    with open(config.results_file, "w") as f:
        json.dump(results, f, indent=2)

    write_validation_report(
        moderation_results, moderation_rate, gate_passed, indicators,
        nli_ddece, consistency_ok, base_results, config,
    )

    # Step 8: Figures
    try:
        fig1_paired_bar(moderation_results, f"{config.figures_dir}/fig1_paired_delta_ece.png")
    except Exception as e:
        print(f"fig1 failed: {e}")

    try:
        fig2_reliability_grid(base_results, chat_results, f"{config.figures_dir}/fig2_reliability_diagrams.png")
    except Exception as e:
        print(f"fig2 failed: {e}")

    try:
        fig3_ddece_scatter(moderation_results, f"{config.figures_dir}/fig3_ddece_scatter.png")
    except Exception as e:
        print(f"fig3 failed: {e}")

    try:
        fig4_anli_gradient(moderation_results, f"{config.figures_dir}/fig4_anli_gradient.png")
    except Exception as e:
        print(f"fig4 failed: {e}")

    print("Experiment complete.")
    return gate_passed


if __name__ == "__main__":
    cfg = HC1Config()
    result = main(cfg)
    sys.exit(0 if result else 1)
