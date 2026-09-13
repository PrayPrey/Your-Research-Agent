#!/usr/bin/env python3
"""
H-E1: Agency Proxy Extraction Experiment
MUST_WORK gate: Mean AUROC >= 0.8 across four agency proxies.
"""
import os
import sys
import json
from sklearn.model_selection import train_test_split

import config
from data import load_hh_rlhf, load_reward_bench_safety, build_labels
from model import AgencyProxyDetector, random_baseline, majority_baseline
from evaluate import compute_auroc, evaluate_all_proxies, plot_auroc_bar, plot_roc_curves


def main():
    print("=" * 60)
    print("H-E1: Agency Proxy Extraction Experiment")
    print("=" * 60)

    # Load datasets
    print("\n[1/5] Loading datasets...")
    hh_texts = load_hh_rlhf()
    print(f"  HH-RLHF responses: {len(hh_texts)}")

    rb_texts = load_reward_bench_safety()
    print(f"  RewardBench Safety responses: {len(rb_texts)}")

    all_texts = hh_texts + rb_texts
    print(f"  Total responses: {len(all_texts)}")

    if len(all_texts) < 100:
        print("ERROR: Too few responses loaded. Check dataset access.")
        sys.exit(1)

    # Split data
    print("\n[2/5] Splitting train/test...")
    train_texts, test_texts = train_test_split(
        all_texts, test_size=config.TEST_SIZE, random_state=config.RANDOM_STATE
    )
    print(f"  Train: {len(train_texts)}, Test: {len(test_texts)}")

    # Train and evaluate per proxy
    print("\n[3/5] Training and evaluating per proxy...")
    detector_results = {}
    proxy_stats = {}

    for proxy in config.PROXY_TYPES:
        print(f"\n  Processing: {proxy}")

        # Build labels
        train_labels = build_labels(train_texts, proxy)
        test_labels = build_labels(test_texts, proxy)

        pos_train = sum(train_labels)
        pos_test = sum(test_labels)
        print(f"    Train: {pos_train}/{len(train_labels)} positive ({100*pos_train/len(train_labels):.1f}%)")
        print(f"    Test: {pos_test}/{len(test_labels)} positive ({100*pos_test/len(test_labels):.1f}%)")

        # Check for degenerate labels
        if len(set(test_labels)) < 2:
            print(f"    WARNING: Single class in test set. AUROC undefined.")
            detector_results[proxy] = (test_labels, [0.5] * len(test_labels))
            proxy_stats[proxy] = {
                "train_pos": pos_train,
                "test_pos": pos_test,
                "auroc": 0.5,
                "random_auroc": 0.5,
                "majority_auroc": 0.5,
                "degenerate": True,
            }
            continue

        # Train detector
        detector = AgencyProxyDetector()
        detector.fit(train_texts, train_labels)

        # Predict on test
        y_score = detector.predict_proba(test_texts)
        auroc = compute_auroc(test_labels, y_score)
        print(f"    Detector AUROC: {auroc:.4f}")

        # Baselines
        random_scores = random_baseline(len(test_labels))
        majority_scores = majority_baseline(test_labels)
        random_auroc = compute_auroc(test_labels, random_scores)
        majority_auroc = compute_auroc(test_labels, majority_scores)
        print(f"    Random baseline AUROC: {random_auroc:.4f}")
        print(f"    Majority baseline AUROC: {majority_auroc:.4f}")

        detector_results[proxy] = (test_labels, y_score)
        proxy_stats[proxy] = {
            "train_pos": pos_train,
            "test_pos": pos_test,
            "auroc": auroc,
            "random_auroc": random_auroc,
            "majority_auroc": majority_auroc,
            "degenerate": False,
        }

    # Aggregate results
    print("\n[4/5] Aggregating results...")
    auroc_results = evaluate_all_proxies(detector_results)

    aurocs = list(auroc_results.values())
    mean_auroc = sum(aurocs) / len(aurocs)
    above_baseline = sum(1 for a in aurocs if a > config.AUROC_BASELINE_MIN)
    above_strong = sum(1 for a in aurocs if a >= config.AUROC_STRONG_SIGNAL)

    print("\n  Per-proxy AUROC:")
    for proxy, auroc in auroc_results.items():
        status = "PASS" if auroc >= config.AUROC_TARGET else ("STRONG" if auroc >= config.AUROC_STRONG_SIGNAL else "WEAK")
        print(f"    {proxy}: {auroc:.4f} [{status}]")

    print(f"\n  Mean AUROC: {mean_auroc:.4f}")
    print(f"  Proxies > baseline (0.5): {above_baseline}/4")
    print(f"  Proxies >= strong signal (0.7): {above_strong}/4")

    # Generate figures
    print("\n[5/5] Generating figures...")
    figures_dir = os.path.join(os.path.dirname(__file__), "..", "figures")
    os.makedirs(figures_dir, exist_ok=True)

    bar_path = os.path.join(figures_dir, "auroc_bar.png")
    plot_auroc_bar(auroc_results, bar_path)
    print(f"  Saved: {bar_path}")

    roc_path = os.path.join(figures_dir, "roc_curves.png")
    plot_roc_curves(detector_results, roc_path)
    print(f"  Saved: {roc_path}")

    # Gate check
    print("\n" + "=" * 60)
    print("GATE CHECK: MUST_WORK")
    print("=" * 60)

    gate_criteria = [
        ("All proxies > baseline (0.5)", above_baseline == 4),
        (">=3 proxies >= 0.7", above_strong >= 3),
        ("Mean AUROC >= 0.8", mean_auroc >= config.AUROC_TARGET),
    ]

    all_pass = True
    for desc, passed in gate_criteria:
        status = "PASS" if passed else "FAIL"
        print(f"  {desc}: {status}")
        if not passed:
            all_pass = False

    print("\n" + "=" * 60)
    if all_pass:
        print("RESULT: GATE SATISFIED - H-E1 PASSES")
        gate_result = "PASS"
    else:
        print("RESULT: GATE NOT SATISFIED - H-E1 FAILS")
        gate_result = "FAIL"
    print("=" * 60)

    # Save results
    results_path = os.path.join(figures_dir, "..", "results.json")
    results = {
        "hypothesis": "H-E1",
        "gate": "MUST_WORK",
        "gate_result": gate_result,
        "mean_auroc": float(mean_auroc),
        "auroc_target": config.AUROC_TARGET,
        "per_proxy_auroc": {k: float(v) for k, v in auroc_results.items()},
        "proxy_stats": {k: {kk: (float(vv) if isinstance(vv, float) else bool(vv) if isinstance(vv, (bool, type(True))) else vv) for kk, vv in v.items()} for k, v in proxy_stats.items()},
        "criteria": {
            "all_above_baseline": bool(above_baseline == 4),
            "three_above_strong": bool(above_strong >= 3),
            "mean_above_target": bool(mean_auroc >= config.AUROC_TARGET),
        },
        "total_samples": len(all_texts),
        "test_samples": len(test_texts),
    }
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {results_path}")

    print("\nEXPERIMENT COMPLETE")
    return gate_result


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result == "PASS" else 1)
