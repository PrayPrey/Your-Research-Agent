"""Data loading - re-derive battle_id alignment from raw dataset, join with h-e1 mode labels."""

import sys
import pandas as pd
from datasets import load_dataset
from config import CONFIG


def load_mode_data() -> pd.DataFrame:
    """Re-derive battle_id -> (resp_a, resp_b) from raw dataset, join with h-e1 results.csv.

    Returns df with columns: battle_id, mode (int), resp_a (str), resp_b (str).
    Filtered to mode in {1, 3}.
    """
    results_path = CONFIG["h_e1_output_dir"] / "results.csv"
    if not results_path.exists():
        raise FileNotFoundError(f"h-e1 results not found: {results_path}. Run h-e1 first.")

    results = pd.read_csv(results_path)
    print(f"Loaded h-e1 results: {len(results)} battles")

    import importlib.util
    spec = importlib.util.spec_from_file_location("h_e1_data", CONFIG["h_e1_code_dir"] / "data.py")
    h_e1_data = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(h_e1_data)
    load_battles = h_e1_data.load_battles
    filter_valid = h_e1_data.filter_valid
    prepare_battles = h_e1_data.prepare_battles

    h_e1_config_path = CONFIG["h_e1_code_dir"] / "config.py"
    h_e1_config = {}
    exec(h_e1_config_path.read_text(), h_e1_config)
    dataset_id = h_e1_config["CONFIG"]["dataset_id"]

    print(f"Loading raw dataset: {dataset_id}")
    df = load_battles(dataset_id)
    df = filter_valid(df)
    df = prepare_battles(df)
    df["battle_id"] = range(len(df))
    print(f"Re-derived {len(df)} battles from raw dataset")

    merged = df[["battle_id", "resp_a", "resp_b"]].merge(
        results[["battle_id", "mode"]], on="battle_id", how="inner"
    )

    if len(merged) != len(results):
        raise AssertionError(
            f"battle_id misalignment: merged {len(merged)} vs results {len(results)}. "
            "Dataset or filtering changed since h-e1 run."
        )

    merged = merged[merged["mode"].isin(CONFIG["modes"])].reset_index(drop=True)

    n_dropped = merged["resp_a"].isna().sum() + merged["resp_b"].isna().sum()
    if n_dropped > 0:
        print(f"Warning: dropping {n_dropped} rows with NaN responses")
        merged = merged.dropna(subset=["resp_a", "resp_b"])

    for m in CONFIG["modes"]:
        n = (merged["mode"] == m).sum()
        if n < CONFIG["min_samples_per_mode"]:
            raise ValueError(f"Mode {m} has n={n} < {CONFIG['min_samples_per_mode']} minimum")
        print(f"Mode {m}: n={n}")

    return merged
