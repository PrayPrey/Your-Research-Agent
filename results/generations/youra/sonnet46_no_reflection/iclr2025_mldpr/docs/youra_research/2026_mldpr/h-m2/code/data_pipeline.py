"""H-M2: Data Pipeline — Reuse H-M1 panel with H_d column extension."""
import os
import sys
import pandas as pd
import numpy as np

DOMAIN_THRESHOLDS: dict = {"cv": 0.5, "nlp": 0.3, "tabular": 0.90}

_HM2_CODE_DIR = os.path.dirname(os.path.abspath(__file__))
_HM1_CODE = os.path.abspath(os.path.join(_HM2_CODE_DIR, "..", "..", "h-m1", "code"))


def _inject_hm1_path(hm1_code_path: str = None) -> None:
    """Inject h-m1 code path AFTER h-m2 code dir to avoid import shadowing."""
    path = os.path.abspath(hm1_code_path or _HM1_CODE)
    # Ensure h-m2 code dir is FIRST (prevent h-m1 modules shadowing h-m2)
    if _HM2_CODE_DIR not in sys.path:
        sys.path.insert(0, _HM2_CODE_DIR)
    if path not in sys.path:
        # Append rather than insert to avoid h-m1 evaluate/visualize shadowing h-m2
        sys.path.append(path)


def load_hm1_panel(
    min_submissions: int = 20,
    min_quarters: int = 8,
    hm1_code_path: str = None,
) -> tuple:
    """Load H-M1 raw + panel with compression flags.
    Returns: (pwc_raw, panel_df) where panel_df has compression_event column.
    """
    _inject_hm1_path(hm1_code_path)
    # Import from h-m1 namespace via sys.path injection
    import importlib, importlib.util
    hm1_path = os.path.abspath(hm1_code_path or _HM1_CODE)

    def _load_hm1_module(name):
        spec = importlib.util.spec_from_file_location(f"hm1_{name}", os.path.join(hm1_path, f"{name}.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    dp = _load_hm1_module("data_pipeline")
    cd = _load_hm1_module("compression_detector")
    se = _load_hm1_module("sigma_estimation")

    pwc_raw = dp.load_pwc_raw()
    panel_df = dp.compute_quarterly_panel(pwc_raw, min_submissions=min_submissions, min_quarters=min_quarters)
    sigma_map = se.get_sigma_map(pwc_raw)
    panel_df = cd.flag_compression(panel_df, sigma_map)

    # Add domain column from pwc_raw (task/dataset -> domain mapping)
    if "domain" not in panel_df.columns:
        domain_map = pwc_raw.drop_duplicates(subset=["task", "dataset"])[["task", "dataset", "domain"]]
        panel_df = panel_df.merge(domain_map, on=["task", "dataset"], how="left")
        panel_df["domain"] = panel_df["domain"].fillna("other")

    return pwc_raw, panel_df


def filter_compressed_benchmarks(
    panel_df: pd.DataFrame,
    min_quarters: int = 8,
) -> pd.DataFrame:
    """Filter to benchmarks with compression_event == 1.0 and >= min_quarters quarters."""
    compressed_ids = panel_df[panel_df["compression_event"] == 1.0]["benchmark_id"].unique()
    filtered = panel_df[panel_df["benchmark_id"].isin(compressed_ids)].copy()
    counts = filtered.groupby("benchmark_id").size()
    valid_ids = counts[counts >= min_quarters].index
    return filtered[filtered["benchmark_id"].isin(valid_ids)].copy()


def extend_panel_with_hd(panel_df: pd.DataFrame) -> pd.DataFrame:
    """Add hd_cv, hd_nlp, hd_tabular columns via hd_signals.compute_all_hd_signals()."""
    import hd_signals
    return hd_signals.compute_all_hd_signals(panel_df)
