from __future__ import annotations

import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd

from calibration import extract_calibration_for_model

logger = logging.getLogger(__name__)

GATE_COLUMNS = ["ECE", "TruthfulQA_pct", "ANLI_drop"]


def load_lmeval_summary(model_results_path: Path) -> dict:
    results_files = sorted(model_results_path.glob("results_*.json"))
    if not results_files:
        raise FileNotFoundError(f"No results_*.json found in {model_results_path}")
    with open(results_files[-1]) as f:
        data = json.load(f)
    results = data.get("results", {})
    # Flatten to {task: acc} — lm-eval v0.4 uses nested dicts
    flat: dict[str, float] = {}
    for task, metrics in results.items():
        if isinstance(metrics, dict):
            # prefer acc,none or acc_norm,none
            for key in ("acc,none", "acc_norm,none", "acc", "acc_norm"):
                if key in metrics:
                    flat[task] = float(metrics[key])
                    break
    return flat


def compute_adv_glue_drop(model_results_path: Path) -> float:
    summary = load_lmeval_summary(model_results_path)
    # Standard GLUE proxy via MMLU or mnli; AdvGLUE is adv_glue task
    std_acc = summary.get("mnli", summary.get("rte", summary.get("qnli", 0.0)))
    adv_acc = summary.get("adv_glue", summary.get("adv_glue_nli", 0.0))
    return float(std_acc - adv_acc)


def compute_anli_drop(model_results_path: Path) -> float:
    summary = load_lmeval_summary(model_results_path)
    r1 = summary.get("anli_r1", 0.0)
    r2 = summary.get("anli_r2", 0.0)
    r3 = summary.get("anli_r3", 0.0)
    r1r2_avg = (r1 + r2) / 2.0
    return float(r1r2_avg - r3)


def build_score_matrix(
    models: list[dict],
    results_dir: Path,
    calibration_data: dict,
) -> pd.DataFrame:
    results_dir = Path(results_dir)
    rows = []
    for model in models:
        mid = model["id"]
        greedy_path = results_dir / mid / "greedy"
        try:
            summary = load_lmeval_summary(greedy_path)
        except FileNotFoundError:
            logger.warning(f"Skipping {mid}: no lm-eval summary found")
            continue

        calib = calibration_data.get(mid, {})
        ece = calib.get("ece_greedy", float("nan"))
        brier = calib.get("brier_greedy", float("nan"))

        truthfulqa = summary.get("truthfulqa_mc1", float("nan"))
        mmlu = summary.get("mmlu", float("nan"))
        humaneval = summary.get("humaneval", float("nan"))

        adv_drop = float("nan")  # adv_glue not available in this lm-eval version

        try:
            anli_drop = compute_anli_drop(greedy_path)
        except Exception:
            anli_drop = float("nan")

        rows.append({
            "model_id": mid,
            "ECE": ece,
            "Brier": brier,
            "TruthfulQA_pct": truthfulqa * 100.0 if not np.isnan(truthfulqa) else float("nan"),
            "AdvGLUE_drop": adv_drop,
            "ANLI_drop": anli_drop,
            "MMLU_acc": mmlu,
            "HumanEval_pass1": humaneval,
        })

    df = pd.DataFrame(rows)
    return df


def validate_matrix(df: pd.DataFrame) -> bool:
    if len(df) < 25:
        return False
    for col in GATE_COLUMNS:
        if col in df.columns and df[col].isna().any():
            return False
    return True
