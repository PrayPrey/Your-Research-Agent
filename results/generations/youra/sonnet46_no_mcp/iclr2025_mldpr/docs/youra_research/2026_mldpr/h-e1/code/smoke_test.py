"""
Smoke test: runs full H-E1 pipeline on 10-dataset subset with fallback proxy.
Verifies all output files are created with correct schema.
Should complete in under 60 seconds.
"""
import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config as cfg_module
from src.collect_openml import build_cohort
from src.score_fuji import score_cohort
from src.analyze import run_analysis, evaluate_gate
from src.main import save_scores_csv, save_metrics_json, save_gate_json

SMOKE_RESULTS_DIR = "results/smoke"
SMOKE_FIGURES_DIR = "figures/smoke"


def run_smoke_test():
    print("=" * 50)
    print("SMOKE TEST: H-E1 Pipeline (10 datasets, real F-UJI)")
    print("=" * 50)

    os.makedirs(SMOKE_RESULTS_DIR, exist_ok=True)
    os.makedirs(SMOKE_FIGURES_DIR, exist_ok=True)

    # Override config for smoke test
    cfg_module.use_fallback = False
    cfg_module.cache_dir = os.path.join(SMOKE_RESULTS_DIR, "fuji_cache")
    cfg_module.max_datasets = 10

    # Build cohort (10 datasets)
    print("\n[1] Building cohort (max 10)...")
    cohort = build_cohort(cfg_module)
    assert len(cohort) > 0, "Cohort is empty"
    assert len(cohort) <= 10, f"Expected <= 10 datasets, got {len(cohort)}"
    print(f"  → {len(cohort)} datasets")

    # Score using fallback
    print("\n[2] Scoring with fallback proxy...")
    scored_raw = score_cohort(cohort, cfg_module)
    assert len(scored_raw) == len(cohort)
    assert "fair_aggregate" in scored_raw.columns

    # Merge
    import pandas as pd
    merge_cols = [c for c in ["did", "upload_date", "NumberOfInstances",
                               "NumberOfFeatures", "MajorityClassPercentage"]
                  if c in cohort.columns]
    scored = scored_raw.merge(cohort[merge_cols], on="did", how="left")
    if "upload_date" in scored.columns:
        scored["upload_date_ordinal"] = pd.to_datetime(
            scored["upload_date"], errors="coerce"
        ).map(lambda t: t.toordinal() if pd.notna(t) else None)

    # Save scores
    scores_path = os.path.join(SMOKE_RESULTS_DIR, "fair_scores.csv")
    save_scores_csv(scored, scores_path)
    assert os.path.exists(scores_path), "fair_scores.csv not created"

    # Analyze
    print("\n[3] Running analysis...")
    metrics = run_analysis(scored, cfg_module)
    assert "cv" in metrics
    assert "n_high" in metrics
    assert "n_low" in metrics

    gate = evaluate_gate(metrics, cfg_module)
    assert "passed" in gate
    assert "cv" in gate
    assert "n_high" in gate
    assert "n_low" in gate
    assert "reason" in gate

    # Save outputs
    metrics_path = os.path.join(SMOKE_RESULTS_DIR, "existence_metrics.json")
    gate_path = os.path.join(SMOKE_RESULTS_DIR, "gate_result.json")
    save_metrics_json(metrics, metrics_path)
    save_gate_json(gate, gate_path)

    assert os.path.exists(metrics_path), "existence_metrics.json not created"
    assert os.path.exists(gate_path), "gate_result.json not created"

    # Verify gate_result.json schema
    with open(gate_path) as f:
        gate_data = json.load(f)
    for key in ["passed", "cv", "n_high", "n_low", "reason"]:
        assert key in gate_data, f"gate_result.json missing key: {key}"

    # Verify existence_metrics.json schema
    with open(metrics_path) as f:
        metrics_data = json.load(f)
    for key in ["cv", "n_high", "n_low", "r_quality", "r_date"]:
        assert key in metrics_data, f"existence_metrics.json missing key: {key}"

    print("\n" + "=" * 50)
    print("SMOKE TEST PASSED ✓")
    print(f"  CV={gate_data.get('cv')}  n_high={gate_data['n_high']}  n_low={gate_data['n_low']}")
    print(f"  Gate: {'PASS' if gate_data['passed'] else 'FAIL'} — {gate_data['reason']}")
    print("=" * 50)


if __name__ == "__main__":
    run_smoke_test()
