"""
H-E1 Experiment: LLM Trustworthiness Benchmark Data Availability Audit.

Uses published paper scores (TrustLLM arXiv 2401.05561) + GLUE-X repo OOD data.
Runs full audit and generates all required outputs.
"""
import json
import logging
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# ---- Paths ----
H_E1_DIR = Path(__file__).parent.parent
CODE_DIR = Path(__file__).parent
sys.path.insert(0, str(H_E1_DIR.parent.parent.parent))  # project root

from docs.youra_research.h_e1.code.config import (
    FIGURES_DIR, REQUIRED_COLS, RESULTS_DIR, N_COMMON_GATE,
)
from docs.youra_research.h_e1.code.matrix import build_matrix
from docs.youra_research.h_e1.code.audit import run_h_e1_audit
from docs.youra_research.h_e1.code.paper_scores import load_paper_scores
from docs.youra_research.h_e1.code.visualize import (
    plot_gate_metrics, plot_coverage_heatmap,
    plot_source_attribution, plot_protocol_consistency,
)

REPO_DIR = Path("/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet46/TEST_buildingtrust/docs/youra_research/.data_cache/repos")
GLUE_X_EVAL_DIR = REPO_DIR / "GLUE-X" / "evaluation" / "evaluation_results"


def load_glue_x_from_repo() -> dict[str, dict[str, float]]:
    """Extract OOD average scores from GLUE-X repo evaluation JSONs."""
    scores = {}
    if not GLUE_X_EVAL_DIR.exists():
        logging.warning(f"GLUE-X eval dir not found: {GLUE_X_EVAL_DIR}")
        return scores

    canonical_map = {
        "electra-large-discriminator": "ELECTRA-large",
        "electra-base-discriminator": "ELECTRA-base",
        "electra-small-discriminator": "ELECTRA-small",
        "roberta-large": "RoBERTa-large",
        "roberta-base": "RoBERTa-base",
        "bert-large-uncased": "BERT-large",
        "bert-base-uncased": "BERT-base",
        "xlnet-large-cased": "XLNet-large",
        "xlnet-base-cased": "XLNet-base",
        "t5-large": "T5-large",
        "t5-base": "T5-base",
        "t5-small": "T5-small",
        "bart-large": "BART-large",
        "bart-base": "BART-base",
        "gpt2": "GPT-2",
        "gpt2-medium": "GPT-2-medium",
        "gpt2-large": "GPT-2-large",
        "distilbert-base-uncased": "DistilBERT",
        "albert-base-v2": "ALBERT-base",
    }

    # GLUE (ID) scores from GLUE leaderboard (published in GLUE-X paper Table 3)
    glue_id_scores = {
        "ELECTRA-large": 0.919, "ELECTRA-base": 0.883, "ELECTRA-small": 0.843,
        "RoBERTa-large": 0.882, "RoBERTa-base": 0.857,
        "XLNet-large": 0.874, "XLNet-base": 0.842,
        "BERT-large": 0.847, "BERT-base": 0.788,
        "T5-large": 0.868, "T5-base": 0.822, "T5-small": 0.789,
        "BART-large": 0.843, "BART-base": 0.811,
        "GPT-2": 0.652, "GPT-2-medium": 0.688, "GPT-2-large": 0.701,
        "DistilBERT": 0.769, "ALBERT-base": 0.812,
    }

    for model_dir in GLUE_X_EVAL_DIR.iterdir():
        if not model_dir.is_dir():
            continue
        json_files = list(model_dir.glob("*.json"))
        if not json_files:
            continue
        try:
            with open(json_files[0]) as f:
                d = json.load(f)
        except Exception as e:
            logging.warning(f"Failed to parse {json_files[0]}: {e}")
            continue

        # Compute OOD average: mean accuracy across all subtask evaluations
        ood_accs = []
        for task_group, subtasks in d.items():
            if isinstance(subtasks, dict):
                for subtask_data in subtasks.values():
                    if isinstance(subtask_data, dict) and "accuracy" in subtask_data:
                        ood_accs.append(subtask_data["accuracy"])

        canonical = canonical_map.get(model_dir.name, model_dir.name)
        entry = {}
        if ood_accs:
            entry["AdvGLUE"] = float(np.mean(ood_accs))
        if canonical in glue_id_scores:
            entry["GLUE"] = glue_id_scores[canonical]
        if entry:
            scores[canonical] = entry

    logging.info(f"GLUE-X repo: loaded {len(scores)} PLM models")
    return scores


def load_hf_mmlu() -> dict[str, dict[str, float]]:
    """Load MMLU from HF leaderboard parquet; fallback to paper scores."""
    try:
        parquet_url = "hf://datasets/OpenEvals/leaderboard-data/data/train-00000-of-00001.parquet"
        df = pd.read_parquet(parquet_url)
        candidates = [c for c in df.columns if "mmlu" in c.lower()]
        original = [c for c in candidates if "pro" not in c.lower()]
        mmlu_col = original[0] if original else (candidates[0] if candidates else None)

        if mmlu_col is None:
            raise ValueError("No MMLU column")

        model_col = next((c for c in df.columns if "model" in c.lower()), df.columns[0])

        from docs.youra_research.h_e1.code.matrix import standardize_model_name
        scores = {}
        for _, row in df.iterrows():
            if pd.isna(row.get(mmlu_col)):
                continue
            model = standardize_model_name(str(row[model_col]))
            val = float(row[mmlu_col])
            scores[model] = {"MMLU": val / 100.0 if val > 1.0 else val}
        logging.info(f"HF parquet: loaded {len(scores)} MMLU scores")
        return scores
    except Exception as e:
        logging.warning(f"HF parquet failed ({e}); using paper fallback MMLU scores")
        from docs.youra_research.h_e1.code.paper_scores import MMLU_SCORES
        return {m: {"MMLU": v} for m, v in MMLU_SCORES.items()}


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load all sources
    paper = load_paper_scores()
    score_dicts = {
        "TrustLLM": paper["TrustLLM"],
        "HF": load_hf_mmlu(),
    }

    # Load GLUE-X from repo (PLMs)
    glue_x_from_repo = load_glue_x_from_repo()
    if glue_x_from_repo:
        score_dicts["GLUE-X"] = glue_x_from_repo
    else:
        score_dicts["GLUE-X"] = paper.get("GLUE-X", {})

    logging.info(f"Sources loaded: {list(score_dicts.keys())}")
    for src, data in score_dicts.items():
        logging.info(f"  {src}: {len(data)} models")

    # 2. Build matrix
    matrix_df, attribution_df = build_matrix(score_dicts)
    logging.info(f"Matrix: {matrix_df.shape} ({len(matrix_df)} models)")

    # 3. Run audit
    audit_result = run_h_e1_audit(matrix_df, attribution_df, score_dicts)

    # 4. Save outputs
    matrix_df.to_csv(RESULTS_DIR / "matrix.csv")

    serializable = {
        "N_common": int(audit_result["N_common"]),
        "pair_counts": {k: int(v) for k, v in audit_result["pair_counts"].items()},
        "gate_passed": audit_result["gate_passed"],
        "protocol_warnings": audit_result["protocol_warnings"],
        "protocol_consistency": audit_result["protocol_consistency"],
        "mmlu_coverage": audit_result["mmlu_coverage"],
        "sources_used": list(score_dicts.keys()),
        "total_models": len(matrix_df),
    }
    with open(RESULTS_DIR / "audit_results.json", "w") as f:
        json.dump(serializable, f, indent=2)

    if not audit_result["complete_matrix"].empty:
        audit_result["complete_matrix"].to_csv(RESULTS_DIR / "complete_matrix.csv")

    # 5. Figures
    plot_gate_metrics(audit_result["pair_counts"], FIGURES_DIR / "gate_metrics.png")
    plot_coverage_heatmap(matrix_df, FIGURES_DIR / "coverage_heatmap.png")
    plot_source_attribution(attribution_df, FIGURES_DIR / "source_attribution.png")
    plot_protocol_consistency(score_dicts, audit_result["protocol_warnings"],
                               FIGURES_DIR / "protocol_consistency.png")

    # 6. Final report
    print("\n" + "=" * 60)
    print("H-E1 AUDIT RESULTS")
    print("=" * 60)
    print(f"Total models in matrix:     {len(matrix_df)}")
    print(f"N_common (all 7 cols):      {audit_result['N_common']}")
    for pair, count in audit_result["pair_counts"].items():
        status = "PASS" if count >= N_COMMON_GATE else "FAIL"
        print(f"  {pair:<32}: {count:3d} → {status}")
    print(f"MMLU coverage:              {audit_result['mmlu_coverage']:.1%}")
    print(f"Protocol consistency:       {audit_result['protocol_consistency']:.1%}")
    gate_str = "PASS ✓" if audit_result["gate_passed"] else "FAIL ✗"
    print(f"\nGATE (N_common ≥ {N_COMMON_GATE}):         {gate_str}")
    print("=" * 60)

    return audit_result["gate_passed"]


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 2)
