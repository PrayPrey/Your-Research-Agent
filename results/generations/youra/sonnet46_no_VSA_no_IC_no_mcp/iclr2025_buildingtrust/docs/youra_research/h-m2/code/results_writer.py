"""Write H-M2 results to JSON and markdown."""
import json
from dataclasses import asdict
from pathlib import Path

from cell_analyzer import DeltaStats
from gate_evaluator import GateResult


def _jsonable(obj):
    if isinstance(obj, dict):
        return {str(k): _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonable(i) for i in obj]
    if isinstance(obj, (int, float, str, bool)) or obj is None:
        return obj
    return str(obj)


def write_main_results(cell_results: dict[tuple[str, str], DeltaStats], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for (model, task), ds in cell_results.items():
        row = asdict(ds)
        row["cell_key"] = f"{model}_{task}"
        rows.append(row)
    path = out_dir / "h_m2_results.json"
    with open(path, "w") as f:
        json.dump(_jsonable(rows), f, indent=2)
    print(f"Wrote: {path}")


def write_gate_report(gate_result: GateResult, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "gate_pass_rate": gate_result.gate_pass_rate,
        "gate_pass_count": gate_result.gate_pass_count,
        "total_cells": gate_result.total_cells,
        "overall_result": gate_result.overall_result,
        "mean_delta_acc": gate_result.mean_delta_acc,
        "mean_conf_wrong_adv": gate_result.mean_conf_wrong_adv,
        "passed_cells": [f"{m}_{t}" for m, t in gate_result.passed_cells],
        "failed_cells": [
            {"cell": f"{d['model']}_{d['task']}", "reason": d["failure_reason"]}
            for d in gate_result.failed_cells
        ],
    }
    path = out_dir / "h_m2_gate_report.json"
    with open(path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Wrote: {path}")


def write_secondary_results(secondary: dict, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "h_m2_secondary_results.json"
    with open(path, "w") as f:
        json.dump(_jsonable(secondary), f, indent=2)
    print(f"Wrote: {path}")


def write_summary(gate_result: GateResult, secondary: dict, cell_results: dict, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    top_cells = sorted(
        cell_results.items(),
        key=lambda kv: kv[1].delta_acc
    )[:3]

    anli_grad = secondary.get("anli_gradient", {})
    anli_per_round = anli_grad.get("per_round", {})
    anli_direction = anli_grad.get("direction_confirmed", None)

    lines = [
        "# H-M2 Summary: Confidence-Accuracy Decoupling",
        "",
        f"**Gate Result:** {gate_result.overall_result}",
        f"**Pass Rate:** {gate_result.gate_pass_rate:.4f} ({gate_result.gate_pass_count}/{gate_result.total_cells} cells)",
        f"**Mean ΔAcc:** {gate_result.mean_delta_acc:.4f}",
        f"**Mean conf_wrong_adv:** {gate_result.mean_conf_wrong_adv:.4f}",
        "",
        "## Top 3 Cells by Accuracy Drop",
        "| Model | Task | ΔAcc | conf_wrong_adv | Pass |",
        "|-------|------|------|----------------|------|",
    ]
    for (model, task), ds in top_cells:
        cwa = f"{ds.conf_wrong_adv:.4f}" if ds.conf_wrong_adv is not None else "N/A"
        lines.append(f"| {model} | {task} | {ds.delta_acc:.4f} | {cwa} | {'YES' if ds.cell_pass else 'NO'} |")

    lines += [
        "",
        "## ANLI Difficulty Gradient",
    ]
    for rnd in ["anli_r1", "anli_r2", "anli_r3"]:
        v = anli_per_round.get(rnd)
        lines.append(f"- {rnd}: ΔAcc = {v:.4f}" if v is not None else f"- {rnd}: N/A")
    lines.append(f"- Direction confirmed (R3 ≤ R1): {anli_direction}")
    lines += [
        "",
        "## Ablation: Threshold Sensitivity",
    ]
    for k, v in secondary.get("ablation_threshold_sensitivity", {}).items():
        lines.append(f"- {k}: gate_pass_rate = {v:.4f}" if v is not None else f"- {k}: N/A")

    with open(out_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Wrote: {out_path}")
