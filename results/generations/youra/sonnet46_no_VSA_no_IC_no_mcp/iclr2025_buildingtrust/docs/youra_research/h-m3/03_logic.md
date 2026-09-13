---
hypothesis_id: H-M3
phase: 3_logic
date: "2026-08-25"
author: yoon303@ust.ac.kr
---

# Logic: H-M3 — ECE Calibration Measurement

Applied: Guo-2017 15-bin equal-width ECE pattern (Archon KB: unavailable — WebSearch fallback; cite Guo 2017 ICML)
Applied: H-M2 GateResult/evaluate_gate pattern (adapted for t-test gate)
Applied: H-E1 compute_ece direct reuse via sys.path

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extending H-M2 and H-E1)
**Status**: API signatures verified from actual base code
**Analyzed Path**: `docs/youra_research/h-m2/code/` and `docs/youra_research/h-e1/code/`
**Relevant Symbols**:
- `h-e1/code/evaluation/ece.py`: `compute_ece(confidences: np.ndarray, correct: np.ndarray, n_bins: int = 15) -> float` — verified, reuse directly
- `h-m2/code/jsonl_loader.py`: `load_split_file(filepath: Path) -> dict`, `load_cell(task: str) -> tuple[dict, dict]`, `preflight_check() -> None` — copy + adapt
- `h-m2/code/gate_evaluator.py`: `GateResult` dataclass, `evaluate_gate(cell_results: dict) -> GateResult` — pattern adapted (new fields for t-test)
- H-M2 `load_split_file` returns `{conf, correct, pred, label}` as numpy arrays — H-M3 needs `logits_per_example` raw from JSONL `resps` field (different schema)

**Critical difference**: H-M2 JSONL schema has pre-extracted `{confidence, correct, pred_label, true_label}`. H-M3 needs raw `resps` field from lm-eval harness JSONL to apply softmax. H-M3 `jsonl_loader.py` must parse `resps` directly.

---

## External Dependencies (Base Hypothesis)

```python
# From: h-e1/code/evaluation/ece.py (ACTUAL CODE)
def compute_ece(
    confidences: np.ndarray,   # shape (N,) — max softmax prob per example
    correct: np.ndarray,       # shape (N,) — 1.0 if correct, 0.0 if not
    n_bins: int = 15
) -> float:
    """Guo-2017 equal-width ECE. Returns scalar float."""
    ...

# From: h-m2/code/jsonl_loader.py (ACTUAL CODE — pattern only, schema differs)
def preflight_check() -> None:
    """Verify files exist, n >= MIN_EXAMPLES. Raises SystemExit."""
    ...
```

---

## A-3: ECE Computer [Complexity: 9, Budget: 2 subtasks]

Applied: Guo-2017 softmax-from-logits pattern

### API Signatures

```python
# ece_computer.py
import sys
from pathlib import Path
import numpy as np
from scipy.special import softmax

# sys.path.insert to reach h-e1/code/evaluation/
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "h-e1" / "code" / "evaluation"))
from ece import compute_ece  # actual signature: (confidences, correct, n_bins=15) -> float


def compute_ece_from_logits(
    logits_per_example: list[np.ndarray],  # List of shape (n_choices,) each
    labels: np.ndarray,                    # shape (N,) — ground truth answer indices
    n_bins: int = 15,
) -> tuple[float, np.ndarray, np.ndarray]:
    """Softmax logits then delegate to H-E1 compute_ece. Returns (ece, confidences, correct)."""
    # confidences: (N,), correct: (N,) dtype float
    assert len(logits_per_example) == len(labels), "logits/labels length mismatch"
    probs = np.array([softmax(lgt) for lgt in logits_per_example])  # (N, n_choices)
    preds = probs.argmax(axis=1)                                     # (N,)
    confidences = probs.max(axis=1)                                  # (N,)
    correct = (preds == labels).astype(float)                        # (N,)
    ece = compute_ece(confidences, correct, n_bins)
    return ece, confidences, correct


def compute_delta_ece(
    clean_data: dict[str, Any],   # keys: 'logits_per_example' (List[ndarray]), 'labels' (ndarray)
    adv_data: dict[str, Any],
    n_bins: int = 15,
) -> tuple[float, float, float]:
    """Returns (delta_ece, ece_clean, ece_adv). delta_ece = ece_adv - ece_clean."""
    ece_clean, _, _ = compute_ece_from_logits(clean_data["logits_per_example"], clean_data["labels"], n_bins)
    ece_adv, _, _ = compute_ece_from_logits(adv_data["logits_per_example"], adv_data["labels"], n_bins)
    delta_ece = ece_adv - ece_clean
    # Log: ECE computed: clean={ece_clean:.4f}, adv={ece_adv:.4f}, ΔECE={delta_ece:.4f}
    return delta_ece, ece_clean, ece_adv


def verify_mechanism_activated(results: dict[str, dict]) -> tuple[bool, dict]:
    """Returns (activated, indicators). results: {task: {ece_clean, ece_adv, delta_ece}}."""
    indicators = {
        "ece_computed": all(
            r["ece_clean"] is not None and r["ece_adv"] is not None
            for r in results.values()
        ),
        "baseline_in_range": all(
            0.0 <= r["ece_clean"] <= 0.5 for r in results.values()
        ),
        "delta_positive_majority": (
            sum(1 for r in results.values() if r["delta_ece"] > 0) >= len(results) / 2
        ),
    }
    return all(indicators.values()), indicators
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | compute_ece_from_logits | softmax + delegate to H-E1 compute_ece; assert len check |
| L-3-2 | compute_delta_ece + verify_mechanism_activated | ΔECE = ece_adv - ece_clean; activation check |

---

## A-4: Gate Evaluator [Complexity: 10, Budget: 2 subtasks]

Applied: H-M2 GateResult pattern + scipy.stats.ttest_1samp

### API Signatures

```python
# gate_evaluator.py
from dataclasses import dataclass, field
from scipy import stats


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
    overall_result: str        # "PASS" or "EXPLORE"
    passed_cells: list[str]    # task ids with delta_ece > gate_threshold
    failed_cells: list[dict]   # [{"task": str, "delta_ece": float}]


def evaluate_gate(
    cell_results: dict[str, dict],  # {task: {delta_ece, ece_clean, ece_adv}}
    gate_threshold: float = 0.05,
    alpha: float = 0.05,
) -> GateResult:
    """One-sample t-test H0: mean ΔECE <= 0. PASS = gate_pass_rate >= 0.60 AND p < alpha."""
    delta_eces = [r["delta_ece"] for r in cell_results.values()]
    t_stat, p_value = stats.ttest_1samp(delta_eces, popmean=0, alternative="greater")

    passed_cells, failed_cells = [], []
    for task, r in cell_results.items():
        if r["delta_ece"] > gate_threshold:
            passed_cells.append(task)
        else:
            failed_cells.append({"task": task, "delta_ece": r["delta_ece"]})

    n = len(cell_results)
    gate_pass_rate = len(passed_cells) / n if n > 0 else 0.0
    mean_delta_ece = float(np.mean(delta_eces))
    overall_result = (
        "PASS" if gate_pass_rate >= 0.60 and p_value < alpha and mean_delta_ece > 0
        else "EXPLORE"
    )
    return GateResult(
        gate_pass_rate=gate_pass_rate,
        gate_pass_count=len(passed_cells),
        total_cells=n,
        mean_delta_ece=mean_delta_ece,
        mean_ece_clean=float(np.mean([r["ece_clean"] for r in cell_results.values()])),
        mean_ece_adv=float(np.mean([r["ece_adv"] for r in cell_results.values()])),
        t_stat=float(t_stat),
        p_value=float(p_value),
        overall_result=overall_result,
        passed_cells=passed_cells,
        failed_cells=failed_cells,
    )
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | compute_delta_ece (per-cell) | Thin wrapper — see L-3-2; wires clean_data/adv_data dicts |
| L-4-2 | GateResult + evaluate_gate | t-test, pass rate, PASS/EXPLORE verdict |

---

## A-5: Ablation Runner [Complexity: 10, Budget: 2 subtasks]

Applied: Standard PyTorch/numpy — no framework needed

### API Signatures

```python
# ablation_runner.py
from ece_computer import compute_delta_ece


def run_ablation_bin_sensitivity(
    cell_data: dict[str, tuple[dict, dict]],  # {task: (clean_data, adv_data)}
    bin_counts: list[int] = [10, 15, 20],
) -> dict[int, dict[str, float]]:
    """Returns {n_bins: {task: delta_ece}}."""
    results = {}
    for n_bins in bin_counts:
        results[n_bins] = {
            task: compute_delta_ece(clean, adv, n_bins=n_bins)[0]
            for task, (clean, adv) in cell_data.items()
        }
    return results


def run_ablation_threshold_sensitivity(
    delta_ece_per_cell: dict[str, float],  # {task: delta_ece}
    thresholds: list[float] = [0.03, 0.05, 0.10],
) -> dict[float, float]:
    """Returns {threshold: gate_pass_rate}."""
    n = len(delta_ece_per_cell)
    return {
        t: sum(1 for v in delta_ece_per_cell.values() if v > t) / n
        for t in thresholds
    }
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | run_ablation_bin_sensitivity | Loop bin_counts, reuse compute_delta_ece |
| L-5-2 | run_ablation_threshold_sensitivity | Count pass_rate per threshold |

---

## A-8: Entrypoint [Complexity: 12, Budget: 2 subtasks]

Applied: Standard argparse + orchestrator pattern (mirrors H-M2 run_h_m2.py)

### API Signatures

```python
# run_h_m3.py
import argparse
import logging
from dataclasses import dataclass
from pathlib import Path

from config import TASKS, BIN_COUNTS, DELTA_ECE_THRESHOLDS, DELTA_ECE_GATE, H_M3_RESULTS_DIR, H_M3_FIGURES_DIR
from jsonl_loader import preflight_check, load_cell
from ece_computer import compute_delta_ece, verify_mechanism_activated
from gate_evaluator import evaluate_gate, GateResult
from ablation_runner import run_ablation_bin_sensitivity, run_ablation_threshold_sensitivity
from visualizer import (plot_delta_ece_bar, plot_reliability_diagrams, plot_delta_ece_heatmap,
                        plot_per_bin_gap, plot_ece_scatter, plot_anli_gradient)
from results_writer import write_ece_table, write_delta_ece_json, write_gate_report, write_secondary_results, write_summary


@dataclass
class H_M3Config:
    output_dir: Path = H_M3_RESULTS_DIR
    figures_dir: Path = H_M3_FIGURES_DIR
    dry_run: bool = False


@dataclass
class ExperimentResult:
    gate_result: GateResult
    cell_results: dict[str, dict]      # {task: {ece_clean, ece_adv, delta_ece}}
    ablation_bin: dict[int, dict]
    ablation_threshold: dict[float, float]
    activated: bool


def run_h_m3(config: H_M3Config) -> ExperimentResult:
    """Orchestrate full H-M3 pipeline."""
    preflight_check()

    cell_data = {task: load_cell(task) for task in TASKS}  # {task: (clean, adv)}

    cell_results = {}
    for task, (clean, adv) in cell_data.items():
        delta_ece, ece_clean, ece_adv = compute_delta_ece(clean, adv)
        cell_results[task] = {"delta_ece": delta_ece, "ece_clean": ece_clean, "ece_adv": ece_adv}

    activated, indicators = verify_mechanism_activated(cell_results)
    gate_result = evaluate_gate(cell_results, gate_threshold=DELTA_ECE_GATE)

    ablation_bin = run_ablation_bin_sensitivity(cell_data, BIN_COUNTS)
    ablation_threshold = run_ablation_threshold_sensitivity(
        {t: r["delta_ece"] for t, r in cell_results.items()}, DELTA_ECE_THRESHOLDS
    )

    if not config.dry_run:
        config.output_dir.mkdir(parents=True, exist_ok=True)
        config.figures_dir.mkdir(parents=True, exist_ok=True)
        write_ece_table(cell_results, config.output_dir)
        write_delta_ece_json(cell_results, config.output_dir)
        write_gate_report(gate_result, config.output_dir)
        write_secondary_results({"ablation_bin": ablation_bin, "ablation_threshold": ablation_threshold}, config.output_dir)
        write_summary(gate_result, {}, cell_results, config.output_dir / "h_m3_summary.md")
        plot_delta_ece_bar(cell_results, DELTA_ECE_GATE, config.figures_dir)
        plot_reliability_diagrams(cell_data, list(cell_data.keys())[:3], 15, config.figures_dir)
        plot_delta_ece_heatmap(cell_results, config.figures_dir)
        plot_per_bin_gap(cell_data, list(cell_data.keys())[:3], 15, config.figures_dir)
        plot_ece_scatter(cell_results, config.figures_dir)
        plot_anli_gradient({t: cell_results[t]["delta_ece"] for t in cell_results if "anli" in t}, config.figures_dir)

    print(f"\nGate result: {gate_result.overall_result} (pass_rate={gate_result.gate_pass_rate:.2f}, p={gate_result.p_value:.4f})")
    return ExperimentResult(gate_result, cell_results, ablation_bin, ablation_threshold, activated)


def verify_end_to_end(sample_jsonl_path: str, n_samples: int = 50) -> bool:
    """Smoke test: load n_samples from JSONL, run full pipeline, assert GateResult returned."""
    import json
    import numpy as np

    with open(sample_jsonl_path) as f:
        records = [json.loads(line) for i, line in enumerate(f) if i < n_samples]

    logits = [np.array([r2[0] for r2 in rec["resps"]]) for rec in records]
    labels = np.array([rec["target"] for rec in records])
    data = {"logits_per_example": logits, "labels": labels}

    from ece_computer import compute_delta_ece
    delta_ece, ece_clean, ece_adv = compute_delta_ece(data, data)  # clean==adv for smoke test
    cell_results = {"smoke_cell": {"delta_ece": delta_ece, "ece_clean": ece_clean, "ece_adv": ece_adv}}
    result = evaluate_gate(cell_results)
    assert isinstance(result, GateResult)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Run H-M3 ECE calibration experiment")
    parser.add_argument("--output-dir", type=str, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    config = H_M3Config(
        output_dir=Path(args.output_dir) if args.output_dir else H_M3_RESULTS_DIR,
        dry_run=args.dry_run,
    )
    run_h_m3(config)


if __name__ == "__main__":
    # Smoke test: python run_h_m3.py --dry-run
    main()
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | run_h_m3 + H_M3Config + ExperimentResult | Full orchestrator; dry-run skips IO |
| L-8-2 | verify_end_to_end + main + argparse | Smoke test from raw JSONL; --dry-run flag |

---

## Tensor Shapes Summary

| Variable | Shape | Note |
|----------|-------|------|
| logits_per_example[i] | (n_choices,) | Raw log-likelihoods from lm-eval `resps` field |
| probs (after softmax) | (N, n_choices) | Per-example choice probabilities |
| confidences | (N,) | max prob per example |
| correct | (N,) | float — 1.0 correct, 0.0 wrong |
| delta_ece_per_cell | ({n_tasks},) | scalar per task |
