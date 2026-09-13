"""Entry point for h-e1-v2 behavioral proxy trend detection."""
import argparse
import json
import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))

from data_loader import load_wildchat, load_lmsys
from cohort_builder import build_wildchat_monthly, build_lmsys_monthly
from proxy_computer import proxy2_series
from stats_tester import mann_kendall, bootstrap_ci, evaluate_gate
from visualizer import fig1_gate_summary, fig2_proxy_timeseries, fig3_cohort_funnel, fig4_lmsys_votes


def parse_args():
    p = argparse.ArgumentParser(description="h-e1-v2: Behavioral proxy trend detection")
    p.add_argument("--date-start", default="2023-01")
    p.add_argument("--date-end", default="2024-12")
    p.add_argument("--min-bins", type=int, default=3)
    p.add_argument("--min-cohort-size", type=int, default=50)
    p.add_argument("--min-votes", type=int, default=100)
    p.add_argument("--n-workers", type=int, default=4)
    p.add_argument("--bootstrap-B", type=int, default=1000)
    p.add_argument("--out-dir", default="results")
    p.add_argument("--figures-dir", default="figures")
    p.add_argument("--smoke", action="store_true", help="Run smoke test only")
    return p.parse_args()


def main():
    args = parse_args()

    if args.smoke:
        import smoke_test
        smoke_test.run_smoke_test()
        return

    os.makedirs(args.out_dir, exist_ok=True)
    os.makedirs(args.figures_dir, exist_ok=True)

    wildchat_csv = f"{args.out_dir}/wildchat_monthly.csv"
    if os.path.exists(wildchat_csv):
        print(f"[main] Loading WildChat monthly from cache: {wildchat_csv}")
        wildchat_monthly = pd.read_csv(wildchat_csv)
        # Reconstruct approximate funnel from cached data
        funnel = {
            "total_ips": -1, "ips_ge1_bin": -1,
            "ips_ge3_bins": int(wildchat_monthly["cohort_size"].sum()),
            "analysis_cohort_size": int(wildchat_monthly["cohort_size"].sum()),
        }
    else:
        print("[main] Loading WildChat-1M (streaming)...")
        stream = load_wildchat()
        wildchat_monthly, funnel = build_wildchat_monthly(
            stream,
            date_start=args.date_start,
            date_end=args.date_end,
            min_bins=args.min_bins,
            min_cohort_size=args.min_cohort_size,
            n_workers=args.n_workers,
        )
        print(f"[main] WildChat monthly bins: {len(wildchat_monthly)}")
        wildchat_monthly.to_csv(wildchat_csv, index=False)
    print(f"[main] WildChat monthly bins: {len(wildchat_monthly)}")

    print("[main] Loading LMSYS Arena...")
    lmsys_df = load_lmsys()
    lmsys_monthly = build_lmsys_monthly(
        lmsys_df,
        min_votes=args.min_votes,
        date_start=args.date_start,
        date_end=args.date_end,
    )
    print(f"[main] LMSYS monthly rows: {len(lmsys_monthly)}")
    lmsys_monthly.to_csv(f"{args.out_dir}/lmsys_monthly.csv", index=False)

    print("[main] Computing proxies...")
    p2 = proxy2_series(lmsys_monthly)
    p2.to_csv(f"{args.out_dir}/proxy2_entropy.csv", header=True)

    months = wildchat_monthly["month"].values
    time_idx = np.arange(len(months))

    proxy_series = {
        "prompt_tokens": wildchat_monthly["prompt_tokens_mean"].values,
        "correction_freq": wildchat_monthly["correction_freq_mean"].values,
    }
    # align proxy2 to wildchat months (may be empty if LMSYS has no timestamps)
    if len(p2) > 0:
        p2_aligned = p2.reindex(months).values
    else:
        p2_aligned = np.full(len(months), np.nan)
        print("[main] Warning: Proxy 2 (vote entropy) has no data — LMSYS timestamps unavailable")
    proxy_series["vote_entropy"] = p2_aligned

    print("[main] Running Mann-Kendall tests...")
    results = {"config": vars(args), "proxies": {}, "cohort": funnel}
    for name, series in proxy_series.items():
        valid_mask = ~np.isnan(series)
        valid_series = series[valid_mask]
        valid_time = time_idx[valid_mask]
        mk = mann_kendall(valid_series)
        if len(valid_series) >= 4:
            ci = bootstrap_ci(valid_series, valid_time, B=args.bootstrap_B)
        else:
            ci = (mk["tau"], mk["tau"])
        mk["ci_low"] = ci[0]
        mk["ci_high"] = ci[1]
        results["proxies"][name] = mk
        sig_str = "SIGNIFICANT" if mk["significant"] else "not significant"
        print(f"  {name}: tau={mk['tau']:.3f}, p={mk['p']:.4f}, method={mk['method']} -> {sig_str}")

    evaluate_gate(results)
    gate = results["gate"]
    print(f"\n[Gate] n_significant={gate['n_significant']}/3 -> {'PASSED' if gate['gate_passed'] else 'FAILED'}")

    out_json = f"{args.out_dir}/results.json"
    with open(out_json, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"[main] Results saved to {out_json}")

    print("[main] Generating figures...")
    fig1_gate_summary(results, args.figures_dir)
    fig2_proxy_timeseries(wildchat_monthly, p2, results, args.figures_dir)
    fig3_cohort_funnel(funnel, args.figures_dir)
    fig4_lmsys_votes(lmsys_monthly, p2, args.figures_dir)
    print(f"[main] Figures saved to {args.figures_dir}/")

    print("\n=== EXPERIMENT COMPLETE ===")
    print(f"Gate: {'PASSED' if gate['gate_passed'] else 'FAILED'} ({gate['n_significant']}/3 proxies significant)")


if __name__ == "__main__":
    main()
