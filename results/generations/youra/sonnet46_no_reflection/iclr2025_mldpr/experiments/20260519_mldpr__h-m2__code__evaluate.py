"""H-M2: Evaluate + Gate Check."""
import json
import os
import numpy as np
import pandas as pd


def verify_mechanism_activated(
    onset_df: pd.DataFrame,
    km_results: dict,
    results: dict,
) -> tuple:
    """Check 5 mechanism activation indicators.
    Returns: (all_activated: bool, indicators: dict[str, bool])
    """
    indicators = {
        "onset_df_populated": len(onset_df) > 0,
        "collapse_events_found": results.get("n_collapse_events", 0) >= 20,
        "lead_time_computed": "domain_km_results" in results and len(results["domain_km_results"]) > 0,
        "km_fitted": km_results is not None and len(km_results) > 0,
        "fraction_computed": any(
            v.get("fraction_leading") is not None
            for v in km_results.values()
            if isinstance(v, dict)
        ) if km_results else False,
    }
    all_activated = all(indicators.values())
    return all_activated, indicators


def check_gate_condition(
    domain_km_results: dict,
    stat_results: dict,
    min_fraction: float = 0.60,
    min_domains: int = 2,
) -> tuple:
    """SHOULD_WORK gate: fraction_leading >= 0.60 in >= 2 domains.
    Returns: (gate_passed: bool, gate_details: dict)
    """
    per_domain = {}
    passing_domains = []

    for domain, km_r in domain_km_results.items():
        if not isinstance(km_r, dict):
            continue
        fl = km_r.get("fraction_leading", 0.0) or 0.0
        mw_p = stat_results.get(domain, {}).get("mw", {}).get("mw_p_value", float("nan"))
        per_domain[domain] = {
            "fraction_leading": fl,
            "passes_gate": fl >= min_fraction,
            "mw_p_value": float(mw_p) if mw_p == mw_p else None,
            "n_events": km_r.get("n_events", 0),
            "median_lead_months": km_r.get("median_lead_months", 0.0),
        }
        if fl >= min_fraction:
            passing_domains.append(domain)

    gate_passed = len(passing_domains) >= min_domains
    gate_details = {
        "gate_type": "SHOULD_WORK",
        "gate_passed": gate_passed,
        "passing_domains": passing_domains,
        "domains_needed": min_domains,
        "fraction_threshold": min_fraction,
        "per_domain": per_domain,
    }
    return gate_passed, gate_details


def save_results(results: dict, results_json: str, results_csv: str) -> None:
    """Persist results dict to JSON + flattened CSV."""
    os.makedirs(os.path.dirname(os.path.abspath(results_json)), exist_ok=True)
    os.makedirs(os.path.dirname(os.path.abspath(results_csv)), exist_ok=True)

    def _to_serializable(obj):
        if isinstance(obj, dict):
            return {k: _to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [_to_serializable(v) for v in obj]
        elif isinstance(obj, float) and obj != obj:
            return None
        elif hasattr(obj, "item"):
            return obj.item()
        elif "KaplanMeier" in str(type(obj)):
            return str(obj)
        return obj

    serializable = _to_serializable(results)
    with open(results_json, "w") as f:
        json.dump(serializable, f, indent=2, default=str)
    print(f"✓ Results saved to {results_json}")

    rows = []
    for domain, v in results.get("gate_details", {}).get("per_domain", {}).items():
        row = {"domain": domain}
        row.update({k: v2 for k, v2 in v.items() if not isinstance(v2, dict)})
        rows.append(row)
    if rows:
        pd.DataFrame(rows).to_csv(results_csv, index=False)
        print(f"✓ CSV saved to {results_csv}")
