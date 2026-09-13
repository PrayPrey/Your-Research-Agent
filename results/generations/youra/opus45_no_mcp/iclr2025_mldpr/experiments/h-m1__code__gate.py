"""Gate evaluation for H-M1."""
import json
from config import CONFIG


def evaluate_gate(ratio_result: dict, mw_result: dict) -> dict:
    ratio = ratio_result["ratio"]
    p_value = mw_result["p_value"]
    pass_gate = bool((ratio >= CONFIG.ratio_threshold) and (p_value < CONFIG.p_threshold))

    return {
        "pass_gate": pass_gate,
        "ratio": ratio,
        "ratio_threshold": CONFIG.ratio_threshold,
        "p_value": p_value,
        "p_threshold": CONFIG.p_threshold,
        "high_use_avg": ratio_result["high_use_avg"],
        "low_use_avg": ratio_result["low_use_avg"],
    }


def write_gate_report(gate_result: dict, path: str) -> None:
    with open(path, "w") as f:
        json.dump(gate_result, f, indent=2)
