"""H-E1 orchestration: run full behavioral proxy signal detection pipeline."""
import json
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd

# Ensure code/ is importable regardless of cwd
CODE_DIR = Path(__file__).parent
sys.path.insert(0, str(CODE_DIR))

from data_loader import load_wildchat, build_cohort, load_lmsys
from proxy_computation import compute_token_series, compute_correction_series, compute_entropy_series
from statistical_analysis import run_mann_kendall, evaluate_success
from visualization import plot_tau_bar, plot_time_series, plot_pvalue_heatmap, plot_cohort_diagnostics

# Paths relative to this file
H_E1_DIR = CODE_DIR.parent
FIGURES_DIR = H_E1_DIR / "figures"
RESULTS_DIR = H_E1_DIR / "results"
RESULTS_FILE = RESULTS_DIR / "results.json"

# Config
DATE_START = "2023-01"
DATE_END = "2024-12"
MIN_BINS = 3
P_THRESHOLD = 0.05
EFFECT_THRESHOLD = 0.2
MIN_PROXIES_PASSING = 2


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[{datetime.now().isoformat()}] H-E1: Starting behavioral proxy signal detection")
    print(f"  Date range: {DATE_START} – {DATE_END}")

    # ── WildChat ────────────────────────────────────────────────────────────
    print("\n[1/5] Loading WildChat-1M...")
    wildchat_raw = load_wildchat(date_start=DATE_START, date_end=DATE_END)
    print(f"  Loaded {len(wildchat_raw):,} rows")

    print("[2/5] Building returning-user cohort (≥3 monthly bins)...")
    cohort_df = build_cohort(wildchat_raw, min_bins=MIN_BINS)
    n_users = cohort_df["hashed_ip"].nunique()
    print(f"  Cohort: {len(cohort_df):,} rows, {n_users:,} unique users")

    # ── LMSYS ───────────────────────────────────────────────────────────────
    print("\n[3/5] Loading LMSYS Chatbot Arena...")
    lmsys_df = pd.DataFrame()
    lmsys_load_error = None
    try:
        lmsys_df = load_lmsys(date_start=DATE_START, date_end=DATE_END)
        print(f"  Loaded {len(lmsys_df):,} battle rows, bins: {sorted(lmsys_df['monthly_bin'].unique())}")
    except Exception as e:
        lmsys_load_error = str(e)
        print(f"  ⚠ LMSYS load failed (will skip entropy proxy): {e}")

    # ── Proxy computation ───────────────────────────────────────────────────
    print("\n[4/5] Computing behavioral proxies...")
    token_series = compute_token_series(cohort_df)
    correction_series = compute_correction_series(cohort_df)
    entropy_series = compute_entropy_series(lmsys_df) if not lmsys_df.empty else {}

    print(f"  token_series bins: {len(token_series)}")
    print(f"  correction_series bins: {len(correction_series)}")
    print(f"  entropy_series bins: {len(entropy_series)}")

    # ── Mann-Kendall ────────────────────────────────────────────────────────
    print("\n[5/5] Running Mann-Kendall tests...")
    mk_results = {}
    for name, series in [
        ("prompt_token_count", token_series),
        ("correction_freq", correction_series),
        ("shannon_entropy", entropy_series),
    ]:
        if len(series) < 4:
            print(f"  ⚠ {name}: only {len(series)} bins — skipping")
            mk_results[name] = (float("nan"), float("nan"))
            continue
        tau, p = run_mann_kendall(series)
        mk_results[name] = (tau, p)
        print(f"  {name}: τ={tau:.4f}, p={p:.4f}")

    evaluation = evaluate_success(
        mk_results,
        p_threshold=P_THRESHOLD,
        effect_threshold=EFFECT_THRESHOLD,
        min_passing=MIN_PROXIES_PASSING,
    )

    gate_satisfied = evaluation["overall_pass"]
    print(f"\n  Gate: {'✅ PASSED' if gate_satisfied else '❌ FAILED'} "
          f"({evaluation['n_passing']}/{MIN_PROXIES_PASSING} proxies passing)")

    # ── Figures ─────────────────────────────────────────────────────────────
    print("\nGenerating figures...")
    fig1 = plot_tau_bar(evaluation, str(FIGURES_DIR))
    fig2 = plot_time_series(token_series, correction_series, entropy_series, str(FIGURES_DIR))
    fig3 = plot_pvalue_heatmap(evaluation, str(FIGURES_DIR))
    fig4 = plot_cohort_diagnostics(cohort_df, lmsys_df, str(FIGURES_DIR))
    print(f"  Saved: {fig1}, {fig2}, {fig3}, {fig4}")

    # ── Results JSON ────────────────────────────────────────────────────────
    results = {
        "hypothesis_id": "h-e1",
        "timestamp": datetime.now().isoformat(),
        "config": {
            "date_start": DATE_START,
            "date_end": DATE_END,
            "min_bins": MIN_BINS,
            "p_threshold": P_THRESHOLD,
            "effect_threshold": EFFECT_THRESHOLD,
            "min_proxies_passing": MIN_PROXIES_PASSING,
        },
        "dataset_stats": {
            "wildchat_rows": len(wildchat_raw),
            "cohort_rows": len(cohort_df),
            "cohort_unique_users": n_users,
            "lmsys_rows": len(lmsys_df),
            "lmsys_load_error": lmsys_load_error,
            "wildchat_bins": sorted(token_series.keys()),
            "lmsys_bins": sorted(entropy_series.keys()),
        },
        "proxy_series": {
            "prompt_token_count": {k: float(v) for k, v in token_series.items()},
            "correction_freq": {k: float(v) for k, v in correction_series.items()},
            "shannon_entropy": {k: float(v) for k, v in entropy_series.items()},
        },
        "mann_kendall": {
            k: {"tau": float(v[0]), "p_value": float(v[1])}
            for k, v in mk_results.items()
        },
        "evaluation": {
            k: (v if not isinstance(v, dict) else v)
            for k, v in evaluation.items()
        },
        "gate": {
            "type": "MUST_WORK",
            "satisfied": bool(gate_satisfied),
            "result": "PASSED" if gate_satisfied else "FAILED",
        },
        "figures": [fig1, fig2, fig3, fig4],
    }

    RESULTS_FILE.write_text(json.dumps(results, indent=2, default=str))
    print(f"\nResults saved to: {RESULTS_FILE}")
    print("\n" + "=" * 60)
    print("H-E1 COMPLETE")
    print(f"Gate: {'PASSED ✅' if gate_satisfied else 'FAILED ❌'}")
    print("=" * 60)

    return results


if __name__ == "__main__":
    main()
