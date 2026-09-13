"""H-M3: ΔECE calibration experiment — builds on H-E1 JSONL cache and H-M2 loader."""
import json
import csv
import sys
import logging
import numpy as np
from pathlib import Path
from dataclasses import dataclass, field
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)

# ── paths ───────────────────────────────────────────────────────────────────
_ROOT = Path(__file__).resolve().parents[4]
H_E1_RESULTS = _ROOT / "docs/youra_research/h-e1/docs/youra_research/h-e1/results"
H_E1_EVAL    = _ROOT / "docs/youra_research/h-e1/code/evaluation"
OUT_DIR      = _ROOT / "docs/youra_research/h-m3/results"
FIG_DIR      = _ROOT / "docs/youra_research/h-m3/figures"
sys.path.insert(0, str(H_E1_EVAL))
from ece import compute_ece  # (confidences, correct, n_bins=15) -> float

# ── task file map (same as H-M2) ────────────────────────────────────────────
TASK_FILE_MAP = {
    "advglue_mnli": ("Llama-2-7b-hf_nli_adversarial_examples.jsonl",  "Llama-2-7b-hf_nli_clean_examples.jsonl"),
    "advglue_qqp":  ("Llama-2-7b-hf_qqp_adversarial_examples.jsonl",  "Llama-2-7b-hf_qqp_clean_examples.jsonl"),
    "anli_r1":      ("Llama-2-7b-hf_nli_anli_r1_examples.jsonl",      "Llama-2-7b-hf_nli_clean_examples.jsonl"),
    "anli_r2":      ("Llama-2-7b-hf_nli_anli_r2_examples.jsonl",      "Llama-2-7b-hf_nli_clean_examples.jsonl"),
    "anli_r3":      ("Llama-2-7b-hf_nli_anli_r3_examples.jsonl",      "Llama-2-7b-hf_nli_clean_examples.jsonl"),
}
TASKS = list(TASK_FILE_MAP.keys())
ANLI_TASKS = ["anli_r1", "anli_r2", "anli_r3"]
NLI_TASKS  = ["advglue_mnli", "anli_r1", "anli_r2", "anli_r3"]

# ── gate constants ───────────────────────────────────────────────────────────
DELTA_ECE_GATE = 0.05
GATE_RATE      = 0.60
ALPHA          = 0.05
BIN_COUNTS     = [10, 15, 20]
THRESHOLDS     = [0.03, 0.05, 0.10]

# ── data loading ─────────────────────────────────────────────────────────────

def load_split(path: Path) -> dict:
    confs, corrects = [], []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            confs.append(float(rec["confidence"]))
            corrects.append(float(rec["correct"]))
    return {"conf": np.array(confs, dtype=np.float32),
            "correct": np.array(corrects, dtype=np.float32)}


def preflight():
    print("Pre-flight: verifying H-E1 JSONL files...")
    seen = set()
    for adv_f, clean_f in TASK_FILE_MAP.values():
        for fn in [adv_f, clean_f]:
            if fn in seen:
                continue
            seen.add(fn)
            p = H_E1_RESULTS / fn
            if not p.exists():
                raise SystemExit(f"MISSING: {p}")
            n = sum(1 for _ in open(p) if _.strip())
            print(f"  OK: {fn} (n={n})")
    print("Pre-flight PASSED.")


# ── ECE computation ──────────────────────────────────────────────────────────

def compute_delta_ece(clean: dict, adv: dict, n_bins: int = 15):
    ece_c = compute_ece(clean["conf"], clean["correct"], n_bins)
    ece_a = compute_ece(adv["conf"],   adv["correct"],   n_bins)
    return ece_a - ece_c, ece_c, ece_a


def verify_mechanism_activated(results: dict) -> tuple:
    indicators = {
        "ece_computed":         all(r["ece_clean"] is not None and r["ece_adv"] is not None for r in results.values()),
        "baseline_in_range":    all(0.0 <= r["ece_clean"] <= 0.5 for r in results.values()),
        "delta_positive_majority": sum(1 for r in results.values() if r["delta_ece"] > 0) >= len(results) / 2,
    }
    return all(indicators.values()), indicators


# ── gate evaluation ──────────────────────────────────────────────────────────

@dataclass
class GateResult:
    gate_pass_rate: float
    gate_pass_count: int
    total_cells: int
    mean_delta_ece: float
    mean_ece_clean: float
    mean_ece_adv: float
    t_stat: float
    p_value: float
    overall_result: str
    passed_cells: list = field(default_factory=list)
    failed_cells: list = field(default_factory=list)


def evaluate_gate(cell_results: dict) -> GateResult:
    delta_eces = [r["delta_ece"] for r in cell_results.values()]
    t_stat, p_value = stats.ttest_1samp(delta_eces, popmean=0, alternative="greater")
    passed, failed = [], []
    for task, r in cell_results.items():
        if r["delta_ece"] > DELTA_ECE_GATE:
            passed.append(task)
        else:
            failed.append({"task": task, "delta_ece": r["delta_ece"]})
    n = len(cell_results)
    rate = len(passed) / n
    mean_d = float(np.mean(delta_eces))
    result = "PASS" if rate >= GATE_RATE and p_value < ALPHA and mean_d > 0 else "EXPLORE"
    return GateResult(
        gate_pass_rate=rate, gate_pass_count=len(passed), total_cells=n,
        mean_delta_ece=mean_d,
        mean_ece_clean=float(np.mean([r["ece_clean"] for r in cell_results.values()])),
        mean_ece_adv=float(np.mean([r["ece_adv"] for r in cell_results.values()])),
        t_stat=float(t_stat), p_value=float(p_value),
        overall_result=result, passed_cells=passed, failed_cells=failed,
    )


# ── ablations ─────────────────────────────────────────────────────────────────

def ablation_bins(cell_data: dict) -> dict:
    return {
        n_bins: {task: compute_delta_ece(c, a, n_bins)[0] for task, (c, a) in cell_data.items()}
        for n_bins in BIN_COUNTS
    }


def ablation_thresholds(delta_per_task: dict) -> dict:
    n = len(delta_per_task)
    return {t: sum(1 for v in delta_per_task.values() if v > t) / n for t in THRESHOLDS}


# ── visualizations ────────────────────────────────────────────────────────────

def plot_delta_ece_bar(cell_results: dict, fig_dir: Path):
    tasks = list(cell_results.keys())
    deltas = [cell_results[t]["delta_ece"] for t in tasks]
    colors = ["green" if d > DELTA_ECE_GATE else "red" for d in deltas]

    fig, ax = plt.subplots(figsize=(12, 5))
    bars = ax.bar(tasks, deltas, color=colors, alpha=0.7)
    ax.axhline(DELTA_ECE_GATE, color="black", linestyle="--", label=f"Gate threshold = {DELTA_ECE_GATE}")
    ax.axhline(0, color="gray", linestyle="-", linewidth=0.5)
    ax.set_xlabel("Task")
    ax.set_ylabel("ΔECE")
    ax.set_title("H-M3: ΔECE per (model, task) cell — Llama-2-7b-hf")
    ax.legend()
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    fig.savefig(fig_dir / "delta_ece_per_cell.png", dpi=150)
    plt.close(fig)
    log.info("Saved delta_ece_per_cell.png")


def plot_reliability_diagram(clean: dict, adv: dict, task: str, fig_dir: Path, n_bins: int = 15):
    fig, ax = plt.subplots(figsize=(7, 6))
    bins = np.linspace(0, 1, n_bins + 1)
    bin_centers = (bins[:-1] + bins[1:]) / 2

    for label, data, color in [("Clean", clean, "blue"), ("Adversarial", adv, "red")]:
        conf, correct = data["conf"], data["correct"]
        acc_bins = []
        for i in range(n_bins):
            if i == n_bins - 1:
                mask = (conf >= bins[i]) & (conf <= bins[i + 1])
            else:
                mask = (conf > bins[i]) & (conf <= bins[i + 1])
            acc_bins.append(correct[mask].mean() if mask.sum() > 0 else np.nan)
        ax.plot(bin_centers, acc_bins, "o-", color=color, label=label, alpha=0.8)

    ax.plot([0, 1], [0, 1], "k--", label="Perfect calibration")
    ax.set_xlabel("Confidence")
    ax.set_ylabel("Accuracy")
    ax.set_title(f"Reliability Diagram — {task}")
    ax.legend()
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    plt.tight_layout()
    fig.savefig(fig_dir / f"reliability_{task}.png", dpi=150)
    plt.close(fig)
    log.info("Saved reliability_%s.png", task)


def plot_ece_scatter(cell_results: dict, fig_dir: Path):
    tasks = list(cell_results.keys())
    clean_eces = [cell_results[t]["ece_clean"] for t in tasks]
    adv_eces   = [cell_results[t]["ece_adv"]   for t in tasks]
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(clean_eces, adv_eces, zorder=5)
    for i, t in enumerate(tasks):
        ax.annotate(t, (clean_eces[i], adv_eces[i]), fontsize=8, xytext=(5, 5), textcoords="offset points")
    lim = max(max(clean_eces), max(adv_eces)) * 1.1
    ax.plot([0, lim], [0, lim], "k--", label="No change")
    ax.set_xlabel("ECE (clean)")
    ax.set_ylabel("ECE (adversarial)")
    ax.set_title("H-M3: ECE scatter — above diagonal = miscalibration increase")
    ax.legend()
    plt.tight_layout()
    fig.savefig(fig_dir / "ece_scatter.png", dpi=150)
    plt.close(fig)
    log.info("Saved ece_scatter.png")


def plot_anli_gradient(cell_results: dict, fig_dir: Path):
    anli = {t: cell_results[t]["delta_ece"] for t in ANLI_TASKS if t in cell_results}
    if not anli:
        return
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(list(anli.keys()), list(anli.values()), color=["#2196F3", "#FF9800", "#F44336"], alpha=0.8)
    ax.axhline(DELTA_ECE_GATE, color="black", linestyle="--", label=f"Gate = {DELTA_ECE_GATE}")
    ax.set_ylabel("ΔECE")
    ax.set_title("H-M3: ANLI Difficulty Gradient (R1→R3)")
    ax.legend()
    plt.tight_layout()
    fig.savefig(fig_dir / "anli_ece_gradient.png", dpi=150)
    plt.close(fig)
    log.info("Saved anli_ece_gradient.png")


def plot_ablation_bins(ablation_bin: dict, fig_dir: Path):
    tasks = list(next(iter(ablation_bin.values())).keys())
    x = np.arange(len(tasks))
    width = 0.25
    fig, ax = plt.subplots(figsize=(12, 5))
    for i, (n_bins, deltas) in enumerate(sorted(ablation_bin.items())):
        ax.bar(x + i * width, [deltas[t] for t in tasks], width, label=f"n_bins={n_bins}", alpha=0.8)
    ax.axhline(DELTA_ECE_GATE, color="black", linestyle="--", label=f"Gate = {DELTA_ECE_GATE}")
    ax.set_xticks(x + width)
    ax.set_xticklabels(tasks, rotation=20, ha="right")
    ax.set_ylabel("ΔECE")
    ax.set_title("H-M3 Ablation A: Bin Count Sensitivity")
    ax.legend()
    plt.tight_layout()
    fig.savefig(fig_dir / "ablation_bin_sensitivity.png", dpi=150)
    plt.close(fig)


# ── results writing ───────────────────────────────────────────────────────────

def write_results(cell_results: dict, gate: GateResult, ablation_bin: dict, ablation_thr: dict, out_dir: Path):
    # CSV table
    with open(out_dir / "h_m3_ece_table.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["task", "ece_clean", "ece_adv", "delta_ece", "cell_pass"])
        for task, r in cell_results.items():
            w.writerow([task, f"{r['ece_clean']:.6f}", f"{r['ece_adv']:.6f}",
                        f"{r['delta_ece']:.6f}", r["delta_ece"] > DELTA_ECE_GATE])

    # ΔECE JSON
    with open(out_dir / "h_m3_delta_ece.json", "w") as f:
        json.dump({t: {k: float(v) for k, v in r.items()} for t, r in cell_results.items()}, f, indent=2)

    # Gate report
    gate_dict = {
        "gate_pass_rate": gate.gate_pass_rate,
        "gate_pass_count": gate.gate_pass_count,
        "total_cells": gate.total_cells,
        "mean_delta_ece": gate.mean_delta_ece,
        "mean_ece_clean": gate.mean_ece_clean,
        "mean_ece_adv": gate.mean_ece_adv,
        "t_stat": gate.t_stat,
        "p_value": gate.p_value,
        "overall_result": gate.overall_result,
        "passed_cells": gate.passed_cells,
        "failed_cells": gate.failed_cells,
        "note": "Single-model scope (Llama-2-7b-hf) — inherited from H-E1/H-M2 data scope",
    }
    with open(out_dir / "h_m3_gate_report.json", "w") as f:
        json.dump(gate_dict, f, indent=2)

    # Secondary results
    secondary = {
        "ablation_bin_sensitivity": {str(k): v for k, v in ablation_bin.items()},
        "ablation_threshold_sensitivity": {str(k): v for k, v in ablation_thr.items()},
        "anli_gradient": {t: cell_results[t]["delta_ece"] for t in ANLI_TASKS if t in cell_results},
        "nli_mean_delta_ece": float(np.mean([cell_results[t]["delta_ece"] for t in NLI_TASKS if t in cell_results])),
        "non_nli_mean_delta_ece": float(np.mean([cell_results[t]["delta_ece"] for t in ["advglue_qqp"] if t in cell_results])),
    }
    with open(out_dir / "h_m3_secondary_results.json", "w") as f:
        json.dump(secondary, f, indent=2)

    log.info("Results written to %s", out_dir)


def _table_rows(cell_results: dict) -> str:
    rows = []
    for t, r in cell_results.items():
        mark = "PASS" if r["delta_ece"] > DELTA_ECE_GATE else "FAIL"
        rows.append(f"| {t} | {r['ece_clean']:.4f} | {r['ece_adv']:.4f} | {r['delta_ece']:.4f} | {mark} |")
    return "\n".join(rows)


def write_summary(cell_results: dict, gate: GateResult, ablation_thr: dict, out_dir: Path):
    top3 = sorted(cell_results.items(), key=lambda x: x[1]["delta_ece"], reverse=True)[:3]
    anli_gradient = [f"{t}: ΔECE={cell_results[t]['delta_ece']:.4f}" for t in ANLI_TASKS if t in cell_results]
    thr_rows = "\n".join(f"  threshold={t}: gate_pass_rate={v:.2f}" for t, v in sorted(ablation_thr.items()))

    text = f"""# H-M3 Summary: ΔECE Calibration Under Adversarial Perturbation

**Gate result:** {gate.overall_result}
**Gate pass rate:** {gate.gate_pass_rate:.2f} ({gate.gate_pass_count}/{gate.total_cells} cells with ΔECE > {DELTA_ECE_GATE})
**Mean ΔECE:** {gate.mean_delta_ece:.4f}
**t-stat:** {gate.t_stat:.4f}  **p-value:** {gate.p_value:.4f}
**Mean ECE(clean):** {gate.mean_ece_clean:.4f}  **Mean ECE(adv):** {gate.mean_ece_adv:.4f}

## Per-cell results
| Task | ECE(clean) | ECE(adv) | ΔECE | Pass |
|------|-----------|---------|------|------|
{_table_rows(cell_results)}

## Top-3 cells by ΔECE
{chr(10).join(f"  {t}: ΔECE={r['delta_ece']:.4f}" for t, r in top3)}

## ANLI difficulty gradient
{chr(10).join(anli_gradient)}

## Threshold sensitivity (ablation)
{thr_rows}

## Notes
- Single-model scope: Llama-2-7b-hf (inherited from H-E1/H-M2)
- Kadavath 2022 expected ECE(clean): 0.05–0.15; observed mean: {gate.mean_ece_clean:.4f}
- Gate type: SHOULD_WORK — EXPLORE result allows pipeline continuation
"""
    with open(out_dir / "h_m3_summary.md", "w") as f:
        f.write(text)
    log.info("Summary written to h_m3_summary.md")


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    preflight()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    # Load all cells
    cell_data = {}
    for task, (adv_f, clean_f) in TASK_FILE_MAP.items():
        clean = load_split(H_E1_RESULTS / clean_f)
        adv   = load_split(H_E1_RESULTS / adv_f)
        cell_data[task] = (clean, adv)
        log.info("Loaded %s: clean n=%d, adv n=%d", task, len(clean["conf"]), len(adv["conf"]))

    # ECE per cell (n_bins=15 primary)
    cell_results = {}
    for task, (clean, adv) in cell_data.items():
        delta, ece_c, ece_a = compute_delta_ece(clean, adv)
        cell_results[task] = {"delta_ece": delta, "ece_clean": ece_c, "ece_adv": ece_a}
        log.info("ECE computed: clean=%.4f, adv=%.4f, ΔECE=%.4f for (%s)", ece_c, ece_a, delta, task)

    activated, indicators = verify_mechanism_activated(cell_results)
    log.info("Mechanism activated: %s | indicators: %s", activated, indicators)

    # Gate
    gate = evaluate_gate(cell_results)
    print(f"\nGate result: {gate.overall_result}")
    print(f"  gate_pass_rate = {gate.gate_pass_rate:.2f} ({gate.gate_pass_count}/{gate.total_cells})")
    print(f"  mean_delta_ece = {gate.mean_delta_ece:.4f}")
    print(f"  t_stat = {gate.t_stat:.4f}, p_value = {gate.p_value:.4f}")
    print(f"  mean_ece_clean = {gate.mean_ece_clean:.4f}, mean_ece_adv = {gate.mean_ece_adv:.4f}")

    # Sanity check
    if gate.mean_ece_clean > 0.25:
        log.warning("FLAG: mean ECE(clean)=%.4f > 0.25 — possible logit extraction artifact", gate.mean_ece_clean)
    elif gate.mean_ece_clean > 0.15:
        log.warning("ECE(clean)=%.4f above Kadavath 2022 expected range (0.05–0.15)", gate.mean_ece_clean)

    # Ablations
    ablation_bin = ablation_bins(cell_data)
    ablation_thr = ablation_thresholds({t: r["delta_ece"] for t, r in cell_results.items()})
    log.info("Ablation bin sensitivity: %s", {k: {t: f"{v:.4f}" for t, v in d.items()} for k, d in ablation_bin.items()})
    log.info("Ablation threshold sensitivity: %s", ablation_thr)

    # Figures
    plot_delta_ece_bar(cell_results, FIG_DIR)
    for task in list(cell_data.keys())[:3]:
        clean, adv = cell_data[task]
        plot_reliability_diagram(clean, adv, task, FIG_DIR)
    plot_ece_scatter(cell_results, FIG_DIR)
    plot_anli_gradient(cell_results, FIG_DIR)
    plot_ablation_bins(ablation_bin, FIG_DIR)

    # Write results
    write_results(cell_results, gate, ablation_bin, ablation_thr, OUT_DIR)
    write_summary(cell_results, gate, ablation_thr, OUT_DIR)

    print("\nEXPERIMENT COMPLETE")
    return gate


if __name__ == "__main__":
    main()
