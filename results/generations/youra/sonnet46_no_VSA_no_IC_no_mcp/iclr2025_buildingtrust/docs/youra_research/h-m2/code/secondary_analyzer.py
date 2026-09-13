"""Secondary analyses: ANLI gradient, confidence delta, ablations."""
from config import NLI_TASKS, NON_NLI_TASKS, ANLI_TASKS, DELTA_ACC_GATE, CONF_WRONG_GATE, MODEL
from cell_analyzer import DeltaStats


def anli_gradient(cell_results: dict[tuple[str, str], DeltaStats]) -> dict:
    """Mean ΔAcc per ANLI round across models."""
    result = {}
    for task in ANLI_TASKS:
        key = (MODEL, task)
        if key in cell_results:
            result[task] = cell_results[key].delta_acc
    # Direction check: ΔAcc(R3) <= ΔAcc(R1) (harder → larger drop)
    r1 = result.get("anli_r1")
    r3 = result.get("anli_r3")
    direction_confirmed = (r3 is not None and r1 is not None and r3 <= r1)
    return {"per_round": result, "direction_confirmed": direction_confirmed}


def confidence_delta_analysis(cell_results: dict[tuple[str, str], DeltaStats]) -> dict:
    """Mean delta_conf_wrong across all cells."""
    deltas = [ds.delta_conf_wrong for ds in cell_results.values() if ds.delta_conf_wrong is not None]
    mean_delta = sum(deltas) / len(deltas) if deltas else None
    return {"mean_delta_conf_wrong": mean_delta, "n_cells": len(deltas)}


def ablation_threshold_sensitivity(cell_results: dict[tuple[str, str], DeltaStats]) -> dict:
    """Test robustness of gate conditions at different thresholds."""
    def rate(delta_acc_thresh, conf_thresh):
        passed = sum(
            1 for ds in cell_results.values()
            if ds.delta_acc <= delta_acc_thresh
            and ds.conf_wrong_adv is not None
            and ds.conf_wrong_adv >= conf_thresh
        )
        return passed / len(cell_results) if cell_results else 0.0

    return {
        "A1_loose_acc_-0.05":  rate(-0.05, CONF_WRONG_GATE),
        "A2_strict_acc_-0.15": rate(-0.15, CONF_WRONG_GATE),
        "A3_loose_conf_0.60":  rate(DELTA_ACC_GATE, 0.60),
        "baseline_-0.10_0.70": rate(DELTA_ACC_GATE, CONF_WRONG_GATE),
    }


def ablation_task_subset(cell_results: dict[tuple[str, str], DeltaStats]) -> dict:
    """NLI-only vs non-NLI cell gate pass rates."""
    def subset_rate(tasks):
        cells = [ds for (m, t), ds in cell_results.items() if t in tasks]
        if not cells:
            return None
        passed = sum(1 for ds in cells if ds.cell_pass)
        return passed / len(cells)

    return {
        "nli_tasks": NLI_TASKS,
        "nli_gate_pass_rate": subset_rate(NLI_TASKS),
        "non_nli_tasks": NON_NLI_TASKS,
        "non_nli_gate_pass_rate": subset_rate(NON_NLI_TASKS),
    }


def ablation_model_size(cell_results: dict[tuple[str, str], DeltaStats]) -> dict:
    """With single model available, report its stats as reference."""
    delta_accs = [ds.delta_acc for ds in cell_results.values()]
    conf_wrongs = [ds.conf_wrong_adv for ds in cell_results.values() if ds.conf_wrong_adv is not None]
    return {
        "note": "Single model available (Llama-2-7b-hf). Multi-model comparison deferred to future H-E1 extension.",
        "llama2_7b_mean_delta_acc": sum(delta_accs) / len(delta_accs) if delta_accs else None,
        "llama2_7b_mean_conf_wrong_adv": sum(conf_wrongs) / len(conf_wrongs) if conf_wrongs else None,
    }
