"""Main pipeline: load all sources, build matrix, run audit, save outputs, generate figures."""
import argparse
import json
import logging
import sys
from pathlib import Path

import pandas as pd

from .audit import run_h_e1_audit
from .config import FIGURES_DIR, REQUIRED_COLS, RESULTS_DIR
from .ingest import (
    load_decoding_trust,
    load_glue_x,
    load_hf_leaderboard,
    load_ood_nlp,
    load_trustllm,
)
from .matrix import build_matrix
from .visualize import (
    plot_coverage_heatmap,
    plot_gate_metrics,
    plot_protocol_consistency,
    plot_source_attribution,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="H-E1 LLM Trustworthiness Data Audit")
    p.add_argument("--trustllm-dir", type=str, default=None,
                   help="Path to cloned HowieHwong/TrustLLM repo")
    p.add_argument("--glue-x-path", type=str, default=None,
                   help="Path to GLUE-X CSV or PDF")
    p.add_argument("--ood-nlp-dir", type=str, default=None,
                   help="Path to cloned lifan-yuan/OOD_NLP repo")
    p.add_argument("--decoding-trust-dir", type=str, default=None,
                   help="Path to cloned AI-secure/DecodingTrust repo")
    p.add_argument("--hf-parquet", type=str,
                   default="hf://datasets/OpenEvals/leaderboard-data/data/train-00000-of-00001.parquet",
                   help="HuggingFace leaderboard parquet URL")
    p.add_argument("--out-dir", type=str, default=None,
                   help="Override output directory for results/figures")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    results_dir = Path(args.out_dir) / "results" if args.out_dir else RESULTS_DIR
    figures_dir = Path(args.out_dir) / "figures" if args.out_dir else FIGURES_DIR
    results_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load all sources (graceful degradation)
    score_dicts: dict[str, dict[str, dict[str, float]]] = {}

    if args.trustllm_dir:
        logging.info(f"Loading TrustLLM from {args.trustllm_dir}")
        score_dicts["TrustLLM"] = load_trustllm(args.trustllm_dir)
    else:
        logging.warning("--trustllm-dir not provided; skipping TrustLLM")

    if args.glue_x_path:
        logging.info(f"Loading GLUE-X from {args.glue_x_path}")
        score_dicts["GLUE-X"] = load_glue_x(args.glue_x_path)
    else:
        logging.warning("--glue-x-path not provided; skipping GLUE-X")

    if args.ood_nlp_dir:
        logging.info(f"Loading OOD_NLP from {args.ood_nlp_dir}")
        score_dicts["OOD_NLP"] = load_ood_nlp(args.ood_nlp_dir)
    else:
        logging.warning("--ood-nlp-dir not provided; skipping OOD_NLP")

    if args.decoding_trust_dir:
        logging.info(f"Loading DecodingTrust from {args.decoding_trust_dir}")
        score_dicts["DecodingTrust"] = load_decoding_trust(args.decoding_trust_dir)
    else:
        logging.warning("--decoding-trust-dir not provided; skipping DecodingTrust")

    # HF leaderboard: always attempt
    logging.info("Loading HF leaderboard (MMLU)...")
    hf_scores = load_hf_leaderboard(args.hf_parquet)
    if hf_scores:
        score_dicts["HF"] = hf_scores
    else:
        logging.warning("HF leaderboard returned empty; MMLU coverage may be limited")

    if not score_dicts:
        logging.error("No data sources available. Provide at least --trustllm-dir.")
        sys.exit(1)

    # 2. Build matrix
    logging.info("Building score matrix...")
    matrix_df, attribution_df = build_matrix(score_dicts)
    logging.info(f"Matrix shape: {matrix_df.shape} ({len(matrix_df)} models × {len(matrix_df.columns)} benchmarks)")

    # 3. Run audit
    logging.info("Running H-E1 audit...")
    audit_result = run_h_e1_audit(matrix_df, attribution_df, score_dicts)

    # 4. Save outputs
    matrix_path = results_dir / "matrix.csv"
    matrix_df.to_csv(matrix_path)
    logging.info(f"Saved matrix to {matrix_path}")

    # Serialize audit result (complete_matrix is a DataFrame)
    serializable = {k: v for k, v in audit_result.items() if k != "complete_matrix"}
    serializable["N_common"] = int(audit_result["N_common"])
    serializable["pair_counts"] = {k: int(v) for k, v in audit_result["pair_counts"].items()}

    audit_path = results_dir / "audit_results.json"
    with open(audit_path, "w") as f:
        json.dump(serializable, f, indent=2, default=str)
    logging.info(f"Saved audit results to {audit_path}")

    # Save complete matrix separately
    if not audit_result["complete_matrix"].empty:
        complete_path = results_dir / "complete_matrix.csv"
        audit_result["complete_matrix"].to_csv(complete_path)
        logging.info(f"Saved complete matrix ({audit_result['N_common']} rows) to {complete_path}")

    # 5. Generate figures
    logging.info("Generating figures...")
    plot_gate_metrics(audit_result["pair_counts"], figures_dir / "gate_metrics.png")
    plot_coverage_heatmap(matrix_df, figures_dir / "coverage_heatmap.png")
    plot_source_attribution(attribution_df, figures_dir / "source_attribution.png")
    plot_protocol_consistency(score_dicts, audit_result["protocol_warnings"],
                               figures_dir / "protocol_consistency.png")

    # 6. Print gate result
    print("\n" + "=" * 60)
    print("H-E1 AUDIT RESULTS")
    print("=" * 60)
    print(f"Total models in matrix:  {len(matrix_df)}")
    print(f"N_common (all 7 cols):   {audit_result['N_common']}")
    for pair, count in audit_result["pair_counts"].items():
        status = "PASS" if count >= 10 else "FAIL"
        print(f"  {pair:<30}: {count:3d} → {status}")
    print(f"MMLU coverage:           {audit_result['mmlu_coverage']:.1%}")
    print(f"Protocol consistency:    {audit_result['protocol_consistency']:.1%}")
    gate_str = "PASS ✓" if audit_result["gate_passed"] else "FAIL ✗"
    print(f"\nGATE (N_common ≥ 10):    {gate_str}")
    print("=" * 60)

    if not audit_result["gate_passed"]:
        logging.warning(
            f"Gate FAILED (N_common={audit_result['N_common']} < 10). "
            "Consider PIVOT: supplement from HF individual model eval pages or restrict benchmark pairs."
        )
        sys.exit(2)  # exit code 2 = gate failed (not a code error)


if __name__ == "__main__":
    main()
