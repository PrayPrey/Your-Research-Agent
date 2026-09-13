import numpy as np
from pathlib import Path


def verify_mechanism_activated(results: dict, data_path: str) -> tuple:
    indicators = {
        "data_file_exists": Path(data_path).exists(),
        "n_sufficient": results.get("n", 0) >= 6,
        "slope_computed": results.get("slope") is not None and not np.isnan(results["slope"]),
        "p_value_valid": 0.0 <= results.get("p_value", 1.0) <= 1.0,
        "r_squared_valid": 0.0 <= results.get("r_squared", -1.0) <= 1.0,
        "ci_computed": results.get("ci_bootstrap") is not None,
    }
    all_ok = all(indicators.values())
    if not all_ok:
        failed = [k for k, v in indicators.items() if not v]
        raise RuntimeError(f"Mechanism verification FAILED: {failed}")
    return True, indicators
