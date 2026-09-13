from typing import Dict, Any, Tuple


def verify_mechanism_activated(results: Dict[str, Any]) -> Tuple[bool, Dict[str, bool]]:
    indicators = {
        "patches_extracted": (
            results.get("n_spurious_patches", 0) > 100 and
            results.get("n_core_patches", 0) > 100
        ),
        "features_extracted": (
            results.get("spurious_feats_shape", [0, 0])[1] == 2048
        ),
        "direction_correct_fft": bool(
            results.get("fft", {}).get("direction_correct", False)
        ),
        "p_value_computed": (
            results.get("fft", {}).get("p_value") is not None
        ),
    }
    activated = all(indicators.values())
    return activated, indicators
