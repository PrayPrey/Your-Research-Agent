"""Evaluate H-M2 gate: confidence-accuracy decoupling in >= 60% of cells."""
import logging
from dataclasses import dataclass

from config import DELTA_ACC_GATE, CONF_WRONG_GATE, GATE_RATE, TOTAL_CELLS
from cell_analyzer import DeltaStats

logger = logging.getLogger(__name__)


@dataclass
class GateResult:
    gate_pass_rate: float
    gate_pass_count: int
    total_cells: int
    passed_cells: list          # list of (model, task) tuples
    failed_cells: list          # list of dicts with failure_reason
    overall_result: str         # "PASS" or "EXPLORE"
    mean_delta_acc: float
    mean_conf_wrong_adv: float
    mean_conf_correct_adv: float


def evaluate_gate(cell_results: dict[tuple[str, str], DeltaStats]) -> GateResult:
    passed_cells = []
    failed_cells = []

    delta_accs       = []
    conf_wrongs      = []
    conf_corrects    = []

    for (model, task), ds in cell_results.items():
        delta_accs.append(ds.delta_acc)

        if ds.conf_wrong_adv is not None:
            conf_wrongs.append(ds.conf_wrong_adv)
        if ds.conf_correct_adv is not None:
            conf_corrects.append(ds.conf_correct_adv)

        if ds.cell_pass:
            passed_cells.append((model, task))
        else:
            # Determine failure reason
            acc_ok  = ds.delta_acc <= DELTA_ACC_GATE
            conf_ok = (ds.conf_wrong_adv is not None) and (ds.conf_wrong_adv >= CONF_WRONG_GATE)
            if not acc_ok and not conf_ok:
                reason = "both"
            elif not acc_ok:
                reason = "delta_acc"
            else:
                reason = "conf_wrong"
            failed_cells.append({"model": model, "task": task, "failure_reason": reason})

        logger.info(
            "Cell [%s][%s]: ΔAcc=%.4f conf_wrong_adv=%s -> %s",
            model, task, ds.delta_acc,
            f"{ds.conf_wrong_adv:.4f}" if ds.conf_wrong_adv is not None else "N/A",
            "PASS" if ds.cell_pass else "FAIL"
        )

    n_cells = len(cell_results)
    gate_pass_count = len(passed_cells)
    gate_pass_rate  = gate_pass_count / n_cells if n_cells > 0 else 0.0

    overall_result = "PASS" if gate_pass_rate >= GATE_RATE else "EXPLORE"

    mean_delta_acc       = sum(delta_accs) / len(delta_accs) if delta_accs else 0.0
    mean_conf_wrong_adv  = sum(conf_wrongs)   / len(conf_wrongs)   if conf_wrongs   else 0.0
    mean_conf_correct_adv = sum(conf_corrects) / len(conf_corrects) if conf_corrects else 0.0

    print(f"\nGate evaluation:")
    print(f"  Cells passing: {gate_pass_count}/{n_cells} (rate={gate_pass_rate:.4f})")
    print(f"  Gate threshold: >= {GATE_RATE}")
    print(f"  Overall result: {overall_result}")
    print(f"  Mean ΔAcc: {mean_delta_acc:.4f}")
    print(f"  Mean conf_wrong_adv: {mean_conf_wrong_adv:.4f}")

    return GateResult(
        gate_pass_rate=gate_pass_rate,
        gate_pass_count=gate_pass_count,
        total_cells=n_cells,
        passed_cells=passed_cells,
        failed_cells=failed_cells,
        overall_result=overall_result,
        mean_delta_acc=mean_delta_acc,
        mean_conf_wrong_adv=mean_conf_wrong_adv,
        mean_conf_correct_adv=mean_conf_correct_adv,
    )
