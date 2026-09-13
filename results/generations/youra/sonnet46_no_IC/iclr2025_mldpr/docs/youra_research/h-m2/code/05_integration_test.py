"""
05_integration_test.py — H-M2 Integration Test
Run full 4-script pipeline end-to-end and verify all outputs.
"""

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
H_M2_CODE    = PROJECT_ROOT / "docs/youra_research/h-m2/code"
H_M2_RESULTS = PROJECT_ROOT / "docs/youra_research/h-m2/results"
H_M2_FIGURES = PROJECT_ROOT / "docs/youra_research/h-m2/figures"

SCRIPTS = [
    "01_preprocess.py",
    "02_fit_models.py",
    "03_generate_figures.py",
    "04_evaluate_gate.py",
]


def run_script(script_name: str) -> None:
    script_path = H_M2_CODE / script_name
    print(f"\n  Running {script_name}...")
    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  STDOUT:\n{result.stdout[-2000:]}")
        print(f"  STDERR:\n{result.stderr[-2000:]}")
        raise RuntimeError(f"{script_name} failed with exit code {result.returncode}")
    print(f"  {script_name} OK")


def verify_tagged_subset() -> None:
    import pandas as pd
    p = H_M2_RESULTS / "tagged_subset.parquet"
    assert p.exists(), "tagged_subset.parquet not found"
    df = pd.read_parquet(p)
    assert 500 <= len(df) <= 4000, f"Unexpected N={len(df)}"
    assert 'log_tag_count_p1' in df.columns, "log_tag_count_p1 column missing"
    assert (df['tag_count'] >= 1).all(), "tag_count < 1 found"
    print(f"  tagged_subset.parquet OK (N={len(df)})")


def verify_model_results() -> None:
    p = H_M2_RESULTS / "model_results.json"
    assert p.exists(), "model_results.json not found"
    results = json.loads(p.read_text())
    assert 'proposed_with_fe' in results, "proposed_with_fe key missing"
    assert results['proposed_with_fe']['converged'] is True, "proposed_with_fe did not converge"
    assert 'ct_lr_test' in results, "ct_lr_test key missing"
    assert results['ct_lr_test']['lr_stat'] is not None, "CT LR stat is None"
    print(f"  model_results.json OK (converged={results['proposed_with_fe']['converged']})")


def verify_primary_results() -> None:
    p = H_M2_RESULTS / "primary_results.json"
    assert p.exists(), "primary_results.json not found"
    pr = json.loads(p.read_text())
    assert pr['result'] in ('PASS', 'INFORMATIVE_NEGATIVE'), f"Unexpected result: {pr['result']}"
    assert 'IRR_P2' in pr and 'CI_lower_P2' in pr, "IRR_P2 or CI_lower_P2 missing"
    assert pr['n_tagged_subset'] > 500, f"n_tagged_subset too small: {pr['n_tagged_subset']}"
    print(f"  Gate verdict: {pr['result']} (IRR={pr['IRR_P2']:.4f}, CI_lower={pr['CI_lower_P2']:.4f})")


def verify_figures() -> None:
    required = [
        'fig1_gate_metrics.png',
        'fig2_tag_count_distribution.png',
        'fig3_partial_regression.png',
        'fig4_attenuation_forest.png',
    ]
    for fname in required:
        p = H_M2_FIGURES / fname
        assert p.exists() and p.stat().st_size > 1000, f"Missing or empty: {fname}"
    print(f"  All {len(required)} figures verified")


def main():
    print("=" * 60)
    print("H-M2 Integration Test")
    print("=" * 60)

    print("\n[Phase 1] Running pipeline scripts...")
    for script in SCRIPTS:
        run_script(script)

    print("\n[Phase 2] Verifying outputs...")
    verify_tagged_subset()
    verify_model_results()
    verify_primary_results()
    verify_figures()

    print("\n" + "=" * 60)
    print("INTEGRATION TEST PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
