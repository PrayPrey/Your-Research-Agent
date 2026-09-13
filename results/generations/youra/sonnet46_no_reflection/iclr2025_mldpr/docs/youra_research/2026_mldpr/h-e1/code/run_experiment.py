"""run_experiment.py — Entry point for H-E1 BCBHS domain health signal discriminability."""
import argparse
import os
import sys
import warnings
from typing import Optional

import numpy as np

CONFIG = {
    "seed": 42,
    "n_bootstrap": 1000,
    "min_submissions": 20,
    "min_history_years": 2,
    "lookback_months": 24,
    "saturation_tau_threshold": 0.90,
    "healthy_tau_threshold": 0.70,
    "min_consecutive_quarters": 2,
    "significance_level": 0.05,
    "cohens_d_threshold": 0.5,
    "auc_threshold": 0.70,
    "min_saturated_per_domain": 15,
    "min_healthy_per_domain": 15,
    "min_benchmarks_per_domain": 10,
    "output_dir": "h-e1/figures/",
    "results_json": "h-e1/results.json",
    "results_csv": "h-e1/results.csv",
    "figure_dpi": 150,
    "figure_size": (10, 6),
    "domain_colors": {
        "cv": "#2196F3",
        "nlp": "#FF5722",
        "tabular": "#4CAF50",
    },
    "threshold_line_styles": {
        "significance": {"color": "#F44336", "linestyle": "--", "label": "p=0.05"},
        "cohens_d": {"color": "#FF9800", "linestyle": "--", "label": "d=0.5"},
        "auc": {"color": "#4CAF50", "linestyle": "--", "label": "AUC=0.70"},
    },
    "temporal_lookbacks": [6, 12, 18, 24],
    "domains": ["cv", "nlp", "tabular"],
}


def parse_args(config: dict, args=None) -> dict:
    parser = argparse.ArgumentParser(
        description="H-E1: BCBHS Domain-Specific Health Signal Discriminability"
    )
    parser.add_argument("--seed", type=int, default=config["seed"])
    parser.add_argument("--n-bootstrap", type=int, default=config["n_bootstrap"],
                        dest="n_bootstrap")
    parser.add_argument("--lookback-months", type=int, default=config["lookback_months"],
                        dest="lookback_months")
    parser.add_argument("--output-dir", type=str, default=config["output_dir"],
                        dest="output_dir")
    parser.add_argument("--results-csv", type=str, default=config["results_csv"],
                        dest="results_csv")
    parsed = parser.parse_args(args)
    config["seed"] = parsed.seed
    config["n_bootstrap"] = parsed.n_bootstrap
    config["lookback_months"] = parsed.lookback_months
    config["output_dir"] = parsed.output_dir
    config["results_csv"] = parsed.results_csv
    return config


def main(args: Optional[list] = None) -> None:
    config = dict(CONFIG)
    config = parse_args(config, args)

    np.random.seed(config["seed"])
    os.makedirs(config["output_dir"], exist_ok=True)
    os.makedirs(os.path.dirname(config["results_csv"])
                if os.path.dirname(config["results_csv"]) else ".", exist_ok=True)

    # Add code dir to path for imports
    code_dir = os.path.dirname(os.path.abspath(__file__))
    if code_dir not in sys.path:
        sys.path.insert(0, code_dir)

    from data_pipeline import load_pwc_panel, load_openml_panel, label_saturation, get_domain_panels
    from signal_compute import compute_domain_signals
    from baseline import extract_naive_features, fit_baseline, predict_baseline
    from evaluate import (evaluate_domain, verify_mechanism_activated,
                          check_gate_condition, run_temporal_test, save_results)
    from visualize import generate_all_figures

    print("=" * 60)
    print("H-E1: BCBHS Domain Health Signal Discriminability")
    print("=" * 60)

    # Step 1: Load data
    print("\n[1/8] Loading PWC panel...")
    try:
        pwc_panel = load_pwc_panel()
    except Exception as e:
        print(f"WARNING: PWC panel failed: {e}")
        pwc_panel = None

    print("[1/8] Loading OpenML panel...")
    try:
        openml_panel = load_openml_panel()
    except Exception as e:
        print(f"WARNING: OpenML panel failed: {e}")
        openml_panel = None

    if pwc_panel is None and openml_panel is None:
        print("GATE: FAIL — No data loaded")
        return

    import pandas as pd
    panels = [p for p in [pwc_panel, openml_panel] if p is not None]
    combined_panel = pd.concat(panels, ignore_index=True) if len(panels) > 1 else panels[0]

    # Step 2: Label saturation
    print("\n[2/8] Labeling saturation...")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        labeled_panel = label_saturation(combined_panel)

    n_sat = (labeled_panel["label"] == "saturated").sum()
    n_healthy = (labeled_panel["label"] == "healthy").sum()
    print(f"  Saturated rows: {n_sat}, Healthy rows: {n_healthy}")

    # Step 3: Compute domain signals
    print("\n[3/8] Computing domain-specific H_d signals...")
    domain_signals = {}
    for domain in config["domains"]:
        domain_data = labeled_panel[labeled_panel["domain"] == domain]
        if len(domain_data) == 0:
            print(f"  WARNING: No data for domain '{domain}'")
            continue
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            signals = compute_domain_signals(domain_data, domain,
                                             config["lookback_months"])
        domain_signals[domain] = signals
        n_s = (signals["label"] == "saturated").sum()
        n_h = (signals["label"] == "healthy").sum()
        print(f"  {domain}: {len(signals)} benchmarks, {n_s} saturated, {n_h} healthy")

    if not domain_signals:
        print("GATE: FAIL — No domain signals computed")
        return

    # Step 4: Fit baseline per domain
    print("\n[4/8] Fitting baseline models...")
    baseline_probs_dict = {}
    for domain, signals in domain_signals.items():
        domain_data = labeled_panel[labeled_panel["domain"] == domain]
        if len(domain_data) == 0:
            continue
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                features_df = extract_naive_features(domain_data)
            labeled = features_df[features_df["label"].isin(["saturated", "healthy"])]
            if len(labeled) < 4:
                baseline_probs_dict[domain] = np.full(len(signals), 0.5)
                continue
            feature_cols = [c for c in labeled.columns
                            if c not in ("benchmark", "label")]
            X = labeled[feature_cols].values
            y = (labeled["label"] == "saturated").astype(int).values
            if len(np.unique(y)) < 2:
                baseline_probs_dict[domain] = np.full(len(signals), 0.5)
                continue
            model = fit_baseline(X, y)
            # Align predictions to domain_signals order
            all_feats = features_df.set_index("benchmark")
            aligned_X = []
            for bm in signals["benchmark"]:
                if bm in all_feats.index:
                    aligned_X.append(all_feats.loc[bm, feature_cols].values)
                else:
                    aligned_X.append(np.zeros(len(feature_cols)))
            aligned_X = np.array(aligned_X)
            probs = predict_baseline(model, aligned_X)
            baseline_probs_dict[domain] = probs
        except Exception as e:
            print(f"  WARNING: Baseline failed for {domain}: {e}")
            baseline_probs_dict[domain] = np.full(len(signals), 0.5)

    # Step 5: Evaluate per domain
    print("\n[5/8] Evaluating discriminability per domain...")
    domain_results = {}
    for domain, signals in domain_signals.items():
        baseline_probs = baseline_probs_dict.get(domain,
                                                  np.full(len(signals), 0.5))
        result = evaluate_domain(signals, baseline_probs, domain)
        domain_results[domain] = result
        disc = result["discriminability"]
        print(f"  {domain}: p={disc['p_value']:.4f}, d={disc['cohens_d']:.3f}, "
              f"AUC={disc['auc']:.3f}, signal_AUC={result['signal_auc']:.3f}")

    # Step 6: Temporal test
    print("\n[6/8] Running temporal separation tests...")
    temporal_results = {}
    for domain in domain_signals:
        domain_data = labeled_panel[labeled_panel["domain"] == domain]
        if len(domain_data) > 0:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                temporal_results[domain] = run_temporal_test(
                    domain_data, domain, config["temporal_lookbacks"])
            for lb, res in temporal_results[domain].items():
                print(f"  {domain} t-{lb}mo: d={res.get('cohens_d', 0):.3f}")

    # Step 7: Verify mechanism + check gate
    print("\n[7/8] Verifying mechanism activation and gate condition...")
    all_activated, indicators = verify_mechanism_activated(domain_results)
    gate_passed, gate_details = check_gate_condition(domain_results)

    print(f"  Mechanism activated (all domains): {all_activated}")
    for domain, ind in indicators.items():
        print(f"    {domain}: {ind}")

    print(f"\n  Gate summary:")
    for domain, det in gate_details.items():
        if domain != "summary":
            print(f"    {domain}: p={det['p_value']:.4f}, d={det['cohens_d']:.3f}, "
                  f"passes={det['passes']}")
    summary = gate_details["summary"]
    print(f"  Passing domains: {summary['n_passing']}/{len(domain_results)} "
          f"(threshold: {summary['threshold']})")

    # Step 8: Generate figures + save results
    print("\n[8/8] Generating figures and saving results...")
    try:
        generate_all_figures(domain_results, domain_signals, temporal_results,
                             config["output_dir"])
    except Exception as e:
        print(f"  WARNING: Figure generation failed: {e}")

    results = {
        "gate_passed": gate_passed,
        "gate_details": gate_details,
        "mechanism_activated": all_activated,
        "mechanism_indicators": indicators,
        "domain_results": domain_results,
        "temporal_results": temporal_results,
        "config": {k: v for k, v in config.items()
                   if not isinstance(v, dict) or k == "domain_colors"},
    }
    save_results(results, config["results_json"])

    # Save CSV summary
    import csv
    csv_rows = []
    for domain, res in domain_results.items():
        disc = res["discriminability"]
        csv_rows.append({
            "domain": domain,
            "p_value": disc["p_value"],
            "cohens_d": disc["cohens_d"],
            "auc_hd": disc["auc"],
            "signal_auc": res["signal_auc"],
            "baseline_auc": res["baseline_auc"],
            "n_saturated": disc["n_sat"],
            "n_healthy": disc["n_healthy"],
            "passes_gate": disc["p_value"] < 0.05 and abs(disc["cohens_d"]) > 0.5,
        })
    if csv_rows:
        with open(config["results_csv"], "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=csv_rows[0].keys())
            writer.writeheader()
            writer.writerows(csv_rows)
        print(f"CSV saved to {config['results_csv']}")

    print("\n" + "=" * 60)
    if gate_passed:
        print("GATE: PASS")
        print(f"  H-E1 MUST_WORK gate PASSED: {summary['n_passing']}/3 domains "
              f"meet p<0.05 AND Cohen's d>0.5")
    else:
        print("GATE: FAIL")
        print(f"  H-E1 MUST_WORK gate FAILED: only {summary['n_passing']}/3 domains "
              f"meet criteria (need >=2)")
    print("=" * 60)


if __name__ == "__main__":
    main()
