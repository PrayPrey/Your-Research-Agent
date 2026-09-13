"""
A-6 Main Orchestrator
Runs the full H-E1 FAIR Score Variance Existence pipeline.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import pandas as pd

import config as cfg_module
from src.collect_openml import build_cohort
from src.score_fuji import score_cohort
from src.analyze import run_analysis, evaluate_gate
from src.visualize import generate_figures


def save_scores_csv(scored: pd.DataFrame, path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    scored.drop(columns=["sub_criteria"], errors="ignore").to_csv(path, index=False)
    print(f"  Saved scores: {path} ({len(scored)} rows)")


def save_metrics_json(metrics: dict, path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    # Make JSON-serializable
    serializable = {}
    for k, v in metrics.items():
        if k == "bimodality" and isinstance(v, dict):
            serializable[k] = {
                kk: (float(vv) if isinstance(vv, float) else vv)
                for kk, vv in v.items()
            }
        elif isinstance(v, float):
            import math
            serializable[k] = None if math.isnan(v) else v
        elif hasattr(v, "item"):
            serializable[k] = v.item()
        else:
            serializable[k] = v
    with open(path, "w") as f:
        json.dump(serializable, f, indent=2)
    print(f"  Saved metrics: {path}")


def save_gate_json(gate: dict, path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    serializable = {}
    for k, v in gate.items():
        if isinstance(v, float):
            import math
            serializable[k] = None if math.isnan(v) else v
        elif hasattr(v, "item"):
            serializable[k] = v.item()
        else:
            serializable[k] = v
    with open(path, "w") as f:
        json.dump(serializable, f, indent=2)
    print(f"  Saved gate: {path}")


def main() -> None:
    print("=" * 60)
    print("H-E1 FAIR Score Variance Existence Pipeline")
    print("=" * 60)

    # 1. Parse args and build config namespace
    args = cfg_module.parse_args()

    # Merge args into cfg_module namespace for downstream use
    cfg_module.FUJI_API_BASE = args.fuji_api_base
    cfg_module.FUJI_CONCURRENCY = args.fuji_concurrency
    cfg_module.FUJI_RETRY_MAX = args.fuji_retry_max
    cfg_module.RESULTS_DIR = args.results_dir
    cfg_module.FIGURES_DIR = args.figures_dir
    cfg_module.CACHE_DIR = args.cache_dir
    cfg_module.OPENML_UPLOAD_DATE_MIN = args.upload_date_min
    cfg_module.use_fallback = args.use_fallback
    cfg_module.cache_dir = args.cache_dir
    if hasattr(args, "max_datasets"):
        cfg_module.max_datasets = args.max_datasets

    paths = cfg_module.resolve_paths(args)

    # Create output directories
    for d in [args.results_dir, args.figures_dir, args.cache_dir]:
        os.makedirs(d, exist_ok=True)

    # 2. Build cohort
    print("\n[Step 1] Building OpenML cohort...")
    cohort = build_cohort(cfg_module)
    if cohort.empty:
        print("ERROR: Empty cohort — cannot proceed.")
        sys.exit(1)
    print(f"  → Cohort size: {len(cohort)} datasets")

    # 3. Score cohort
    print("\n[Step 2] Scoring datasets...")
    scored_raw = score_cohort(cohort, cfg_module)

    # 4. Merge cohort metadata with scores
    merge_cols = ["did", "upload_date", "NumberOfInstances",
                  "NumberOfFeatures", "MajorityClassPercentage"]
    merge_cols = [c for c in merge_cols if c in cohort.columns]
    scored = scored_raw.merge(cohort[merge_cols], on="did", how="left")

    # Compute upload_date_ordinal
    if "upload_date" in scored.columns:
        scored["upload_date_ordinal"] = pd.to_datetime(
            scored["upload_date"], errors="coerce"
        ).map(lambda t: t.toordinal() if pd.notna(t) else None)

    # 5. Save raw scores
    print("\n[Step 3] Saving scores...")
    save_scores_csv(scored, paths["scores_csv"])

    # 6. Run analysis
    print("\n[Step 4] Running statistical analysis...")
    metrics = run_analysis(scored, cfg_module)
    print(f"  CV={metrics.get('cv'):.4f}  n_high={metrics['n_high']}  "
          f"n_low={metrics['n_low']}  n_total={metrics['n_total']}")

    # 7. Evaluate gate
    print("\n[Step 5] Evaluating gate...")
    gate = evaluate_gate(metrics, cfg_module)

    # 8. Save metrics and gate
    print("\n[Step 6] Saving results...")
    save_metrics_json(metrics, paths["metrics_json"])
    save_gate_json(gate, paths["gate_json"])

    # 9. Generate figures
    print("\n[Step 7] Generating figures...")
    try:
        generate_figures(scored, metrics, paths["figures_dir"], cfg_module)
    except Exception as e:
        print(f"  WARNING: Figure generation failed: {e}")

    # 10. Print gate summary
    print("\n" + "=" * 60)
    status = "PASS" if gate["passed"] else "FAIL"
    cv_str = f"{gate['cv']:.3f}" if gate['cv'] is not None else 'N/A'
    print(f"GATE: {status} | CV={cv_str} | n_high={gate['n_high']} | n_low={gate['n_low']}")
    print(f"Reason: {gate['reason']}")
    print("=" * 60)

    if not gate["passed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
