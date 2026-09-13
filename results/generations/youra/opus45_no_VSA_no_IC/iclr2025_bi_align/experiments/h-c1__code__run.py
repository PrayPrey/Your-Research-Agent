"""Main pipeline for h-c1: Mode 3 proportion subjective vs objective."""

import json
import os
import sys

import pandas as pd
from datasets import load_dataset

from config import (
    H_E1_RESULTS_CSV, DATASET_ID, OUTPUT_DIR, MIN_PER_CATEGORY,
    CATEGORY_DIST_PATH, RATIO_ANALYSIS_PATH, PROMPT_CATEGORIES_PATH, ALPHA
)
from categorize import categorize_battles, exclude_ambiguous, filter_min_count
from analysis import (
    category_mode3_counts, two_proportion_ztest, ratio_ci_log, cohens_h, classify_result
)


def load_raw_dataset() -> pd.DataFrame:
    """Load raw Arena dataset and add battle_id."""
    print(f"Loading dataset: {DATASET_ID}")
    ds = load_dataset(DATASET_ID, split="train")
    df = ds.to_pandas()
    df = df.dropna(subset=["prompt", "response_a", "response_b"])
    has_winner = df["winner_model_a"].astype(bool) | df["winner_model_b"].astype(bool) | df["winner_tie"].astype(bool)
    df = df.loc[has_winner]
    df = df.reset_index(drop=True)
    df["battle_id"] = df.index
    print(f"Loaded {len(df)} valid battles")
    return df


def load_h_e1_results() -> pd.DataFrame:
    """Load h-e1 results with mode assignments."""
    print(f"Loading h-e1 results: {H_E1_RESULTS_CSV}")
    results = pd.read_csv(H_E1_RESULTS_CSV)
    print(f"Loaded {len(results)} h-e1 results")
    return results


def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    raw = load_raw_dataset()
    results = load_h_e1_results()

    df = raw.merge(results[["battle_id", "mode"]], on="battle_id", how="inner")
    print(f"Merged: {len(df)} battles with mode data")

    df = categorize_battles(df)
    cat_counts_before = df["category"].value_counts().to_dict()
    print(f"Category distribution (before filter): {cat_counts_before}")

    df = exclude_ambiguous(df)
    print(f"After excluding ambiguous: {len(df)} battles")

    df = filter_min_count(df, MIN_PER_CATEGORY)
    cat_counts = df["category"].value_counts().to_dict()
    print(f"Category distribution (final): {cat_counts}")

    counts = category_mode3_counts(df)
    print(f"Mode 3 counts: {counts}")

    a = counts["subjective"]["mode3"]
    n_subj = counts["subjective"]["total"]
    c = counts["objective"]["mode3"]
    n_obj = counts["objective"]["total"]

    zt = two_proportion_ztest(a, n_subj, c, n_obj)
    ci = ratio_ci_log(a, n_subj, c, n_obj)
    h = cohens_h(zt["p_subj"], zt["p_obj"])
    result = classify_result(ci["ratio"], zt["p_value"], ALPHA)

    print(f"\n=== RESULTS ===")
    print(f"p_subj (Mode 3 in subjective): {zt['p_subj']:.4f} ({a}/{n_subj})")
    print(f"p_obj  (Mode 3 in objective):  {zt['p_obj']:.4f} ({c}/{n_obj})")
    print(f"Ratio p_subj/p_obj: {ci['ratio']:.4f}")
    print(f"95% CI: [{ci['ci_95_lower']:.4f}, {ci['ci_95_upper']:.4f}]")
    print(f"z-statistic: {zt['z']:.4f}")
    print(f"p-value (one-sided): {zt['p_value']:.6f}")
    print(f"Cohen's h: {h:.4f}")
    print(f"Result: {result}")

    with open(CATEGORY_DIST_PATH, "w") as f:
        json.dump(counts, f, indent=2)
    print(f"Saved: {CATEGORY_DIST_PATH}")

    ratio_analysis = {
        "z_test": zt,
        "ratio_ci": ci,
        "cohens_h": h,
        "result": result,
        "counts": counts,
    }
    with open(RATIO_ANALYSIS_PATH, "w") as f:
        json.dump(ratio_analysis, f, indent=2)
    print(f"Saved: {RATIO_ANALYSIS_PATH}")

    df[["battle_id", "prompt", "category", "mode"]].to_parquet(PROMPT_CATEGORIES_PATH, index=False)
    print(f"Saved: {PROMPT_CATEGORIES_PATH}")

    print("\nEXPERIMENT COMPLETE")


if __name__ == "__main__":
    main()
