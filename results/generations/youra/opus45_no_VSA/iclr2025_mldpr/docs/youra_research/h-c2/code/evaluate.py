import json


def check_success(result: dict, criteria: dict) -> bool:
    """True coef outside 95% of permuted distribution (either tail), p<0.05."""
    # percentile < 2.5 OR > 97.5 means true coef is in extreme tails
    in_extreme_tail = result["percentile_rank"] < 2.5 or result["percentile_rank"] > 97.5
    return (
        in_extreme_tail
        and result["p_value"] < criteria["p_value_max"]
    )


def save_results(result: dict, success: bool, path: str) -> None:
    """Write JSON (perm_coefs as list) to path."""
    out = {
        "true_coef": result["true_coef"],
        "p_value": result["p_value"],
        "percentile_rank": result["percentile_rank"],
        "effect_ratio": result["effect_ratio"],
        "success": success,
        "perm_coefs": result["perm_coefs"].tolist(),
    }
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
