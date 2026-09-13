"""H-E1 Orchestration: Run experiment and collect results"""
import json
import os
import numpy as np
from datetime import datetime

from config import EXPERIMENT, setup_dirs
from data import load_and_process_data
from model import MonotonicTrendModel, GiniChangePointDetector
from evaluate import compute_bic, run_gate_checks
from visualize import (
    plot_gini_timeseries_with_changepoints,
    plot_segmented_vs_monotonic_fit,
    plot_gate_metrics_bar
)


def main():
    print("=" * 60)
    print("H-E1 Experiment: PELT Change-Point Detection on Gini Series")
    print("=" * 60)

    # Setup output directories
    setup_dirs()

    # Step 1: Load and process data
    print("\n[1/5] Loading data...")
    gini_series, counts, df = load_and_process_data()

    if gini_series.empty:
        print("ERROR: No data loaded. Check dataset availability.")
        return

    dates = gini_series.index
    y = gini_series.values
    t = np.arange(len(y))
    n = len(y)

    print(f"\nData summary:")
    print(f"  Time range: {dates[0]} to {dates[-1]}")
    print(f"  N months: {n}")
    print(f"  Gini range: [{y.min():.4f}, {y.max():.4f}]")
    print(f"  Unique datasets: {len(counts.columns)}")

    # Step 2: Fit baseline (monotonic) model
    print("\n[2/5] Fitting monotonic trend model (H0)...")
    mono = MonotonicTrendModel().fit(t, y)
    mono_residuals = mono.residuals()
    mono_pred = mono.predictions()
    bic_mono = compute_bic(mono_residuals, n_params=2, n_samples=n)

    print(f"  Slope: {mono.slope:.6f}")
    print(f"  R²: {mono.r_squared():.4f}")
    print(f"  BIC: {bic_mono:.2f}")

    # Step 3: Fit proposed (PELT) model
    print("\n[3/5] Running PELT change-point detection (H1)...")
    detector = GiniChangePointDetector()
    change_points, target_hit = detector.detect(y, dates=dates)

    print(f"  Detected change points: {change_points}")
    print(f"  Target window hit: {target_hit}")

    if change_points:
        for cp in change_points:
            if cp < len(dates):
                print(f"    - Index {cp}: {dates[cp].strftime('%Y-%m')}")

    # Fit segmented trends
    seg_residuals_list = detector.fit_segmented_trends(t, y, change_points)
    seg_pred = detector.segment_predictions()
    seg_residuals = detector.all_residuals()

    # BIC for segmented model: 2 params per segment
    n_segments = len(change_points) + 1
    n_params_seg = 2 * n_segments
    bic_seg = compute_bic(seg_residuals, n_params=n_params_seg, n_samples=n)

    print(f"  Num segments: {n_segments}")
    print(f"  BIC: {bic_seg:.2f}")

    # Step 4: Run gate checks
    print("\n[4/5] Running gate checks...")
    gates = run_gate_checks(y, dates, change_points, bic_mono, bic_seg)

    print(f"\n  Gate Results:")
    print(f"    G-1 (CP in window): {'PASS' if gates['cp_in_window'] else 'FAIL'}")
    print(f"    G-2/G-3 (BIC improved): {'PASS' if gates['bic_improved'] else 'FAIL'}")
    print(f"    Overall: {gates['overall']}")

    if gates["reasons"]:
        print(f"\n  Failure reasons:")
        for r in gates["reasons"]:
            print(f"    - {r}")

    # Step 5: Generate visualizations
    print("\n[5/5] Generating figures...")
    fig_dir = EXPERIMENT.figures_dir

    plot_gini_timeseries_with_changepoints(
        dates, y, change_points,
        os.path.join(fig_dir, "gini_timeseries.png")
    )

    plot_segmented_vs_monotonic_fit(
        dates, y, mono_pred, seg_pred,
        os.path.join(fig_dir, "model_comparison.png")
    )

    plot_gate_metrics_bar(
        gates,
        os.path.join(fig_dir, "gate_metrics.png")
    )

    # Save results
    results = {
        "hypothesis_id": EXPERIMENT.hypothesis_id,
        "timestamp": datetime.now().isoformat(),
        "data": {
            "n_months": int(n),
            "date_start": str(dates[0]),
            "date_end": str(dates[-1]),
            "n_datasets": int(len(counts.columns)),
            "gini_min": float(y.min()),
            "gini_max": float(y.max()),
            "gini_mean": float(y.mean())
        },
        "baseline": {
            "model": "MonotonicTrend",
            "slope": float(mono.slope),
            "intercept": float(mono.intercept),
            "r_squared": float(mono.r_squared()),
            "bic": float(bic_mono)
        },
        "proposed": {
            "model": "PELT_Segmented",
            "n_change_points": int(len(change_points)),
            "change_points": [int(cp) for cp in change_points],
            "change_point_dates": [dates[cp].strftime("%Y-%m") for cp in change_points if cp < len(dates)],
            "target_hit": bool(target_hit),
            "n_segments": int(n_segments),
            "bic": float(bic_seg)
        },
        "gates": {
            "cp_in_window": bool(gates["cp_in_window"]),
            "target_cps": [int(cp) for cp in gates["target_cps"]],
            "bic_improved": bool(gates["bic_improved"]),
            "bic_delta": float(gates["bic_delta"]),
            "overall": gates["overall"],
            "reasons": gates["reasons"]
        }
    }

    results_path = os.path.join(EXPERIMENT.output_dir, EXPERIMENT.results_file)
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {results_path}")

    # Summary
    print("\n" + "=" * 60)
    print("EXPERIMENT COMPLETE")
    print("=" * 60)
    print(f"  Gate verdict: {gates['overall']}")
    print(f"  BIC improvement: {gates['bic_delta']:.2f}")
    if change_points:
        print(f"  Primary change point: {dates[change_points[0]].strftime('%Y-%m')}")
    print("=" * 60)

    return results


if __name__ == "__main__":
    main()
