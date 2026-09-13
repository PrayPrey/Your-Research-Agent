"""H-M2: Ablation Variants A1-A5."""
import numpy as np
import pandas as pd

ABLATION_VARIANTS: dict = {
    "A1": {"description": "t-24mo offset (PROPOSED)", "lead_months": 24, "use_compression_filter": True},
    "A2": {"description": "t-12mo offset", "lead_months": 12, "use_compression_filter": True},
    "A3": {"description": "t offset (concurrent baseline)", "lead_months": 0, "use_compression_filter": True},
    "A4": {"description": "compression-filtered only", "lead_months": 24, "use_compression_filter": True},
    "A5": {"description": "all benchmarks, no compression filter", "lead_months": 24, "use_compression_filter": False},
}


def run_ablation_variant(
    panel_df: pd.DataFrame,
    collapse_df: pd.DataFrame,
    variant_key: str,
    compressed_ids,
) -> dict:
    """Run single ablation variant; returns aggregated metrics across domains."""
    from temporal_analysis import compute_signal_onset_times, run_temporal_ordering_test

    config = ABLATION_VARIANTS[variant_key]
    lead_months = config["lead_months"]
    use_filter = config["use_compression_filter"]

    mask = compressed_ids if use_filter else panel_df["benchmark_id"].unique()

    domain_results = {}
    domains_passing = 0
    for domain in ["cv", "nlp", "tabular"]:
        hd_col = f"hd_{domain}"
        if hd_col not in panel_df.columns or panel_df[hd_col].isna().all():
            domain_results[domain] = {"fraction_leading": np.nan, "n_events": 0}
            continue

        onset_df = compute_signal_onset_times(panel_df, domain, mask, collapse_df)
        if len(onset_df) == 0:
            domain_results[domain] = {"fraction_leading": 0.0, "n_events": 0}
            continue

        km_result = run_temporal_ordering_test(onset_df, min_lead_months=max(1, lead_months))
        fl = km_result["fraction_leading"]
        domain_results[domain] = {"fraction_leading": fl, "n_events": km_result["n_events"]}
        if fl >= 0.60:
            domains_passing += 1

    return {
        "variant": variant_key,
        "description": config["description"],
        "lead_months": lead_months,
        "use_compression_filter": use_filter,
        "domain_results": domain_results,
        "domains_passing": domains_passing,
    }


def run_all_ablations(
    panel_df: pd.DataFrame,
    collapse_df: pd.DataFrame,
    compressed_ids,
) -> list:
    """Run A1-A5; returns list of per-variant metric dicts."""
    results = []
    for key in ABLATION_VARIANTS:
        print(f"  Running ablation {key}: {ABLATION_VARIANTS[key]['description']}")
        r = run_ablation_variant(panel_df, collapse_df, key, compressed_ids)
        results.append(r)
        print(f"    → domains_passing={r['domains_passing']}")
    return results
