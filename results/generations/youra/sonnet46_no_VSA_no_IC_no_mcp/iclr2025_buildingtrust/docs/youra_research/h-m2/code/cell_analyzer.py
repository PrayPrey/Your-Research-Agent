"""Compute per-cell delta statistics (accuracy drop + confidence maintenance)."""
import logging
from dataclasses import dataclass, asdict
from typing import Optional

from config import TASKS, DELTA_ACC_GATE, CONF_WRONG_GATE, MODEL
from jsonl_loader import load_cell
from confidence_extractor import extract_cell_stats, CellStats

logger = logging.getLogger(__name__)


@dataclass
class DeltaStats:
    model: str
    task: str
    accuracy_clean: float
    accuracy_adv: float
    delta_acc: float                   # adv - clean (negative = accuracy drop)
    conf_wrong_clean: Optional[float]
    conf_wrong_adv: Optional[float]
    conf_correct_adv: Optional[float]
    delta_conf_wrong: Optional[float]  # conf_wrong_adv - conf_wrong_clean
    mean_conf_adv: float
    n_wrong_adv: int
    n_total_adv: int
    cell_pass: bool                    # delta_acc <= DELTA_ACC_GATE AND conf_wrong_adv >= CONF_WRONG_GATE


def compute_delta_stats(task: str, clean: CellStats, adv: CellStats) -> DeltaStats:
    delta_acc = adv.accuracy - clean.accuracy

    delta_conf_wrong = None
    if adv.mean_conf_wrong is not None and clean.mean_conf_wrong is not None:
        delta_conf_wrong = adv.mean_conf_wrong - clean.mean_conf_wrong

    # Gate: accuracy must drop by >= 10pp AND confidence on wrong adv predictions >= 0.70
    acc_ok   = delta_acc <= DELTA_ACC_GATE
    conf_ok  = (adv.mean_conf_wrong is not None) and (adv.mean_conf_wrong >= CONF_WRONG_GATE)
    cell_pass = acc_ok and conf_ok

    return DeltaStats(
        model=MODEL,
        task=task,
        accuracy_clean=clean.accuracy,
        accuracy_adv=adv.accuracy,
        delta_acc=delta_acc,
        conf_wrong_clean=clean.mean_conf_wrong,
        conf_wrong_adv=adv.mean_conf_wrong,
        conf_correct_adv=adv.mean_conf_correct,
        delta_conf_wrong=delta_conf_wrong,
        mean_conf_adv=adv.mean_conf_all,
        n_wrong_adv=adv.n_wrong,
        n_total_adv=adv.n_total,
        cell_pass=cell_pass,
    )


def run_all_cells() -> dict[tuple[str, str], DeltaStats]:
    """Run analysis for all (model, task) cells."""
    results = {}
    for task in TASKS:
        logger.info("Processing cell: model=%s task=%s", MODEL, task)
        clean_data, adv_data = load_cell(task)
        clean_stats = extract_cell_stats(clean_data)
        adv_stats   = extract_cell_stats(adv_data)
        delta = compute_delta_stats(task, clean_stats, adv_stats)

        cwa_str = f"{delta.conf_wrong_adv:.4f}" if delta.conf_wrong_adv is not None else "N/A"
        print(f"  [{MODEL}][{task}] ΔAcc={delta.delta_acc:.4f} conf_wrong_adv={cwa_str} -> {'PASS' if delta.cell_pass else 'FAIL'}")

        results[(MODEL, task)] = delta

    return results
