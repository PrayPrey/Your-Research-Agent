---
hypothesis_id: H-M2
phase: logic
date: "2026-08-25"
author: yoon303@ust.ac.kr
---

# Logic: H-M2

Applied: max-softmax confidence extraction (Kadavath 2022), cell-grid post-hoc analysis (Wang et al. 2021 AdvGLUE), lm-eval-harness JSONL format (EleutherAI)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends H-E1, H-M1)
**Status**: Serena MCP unavailable (ablation/no-MCP environment). No complex local codebase to analyze — H-M2 is pure post-hoc analysis over H-E1 JSONL outputs. No direct imports from H-M1 code. H-E1 write_json pattern reused via sys.path insert as specified.
**Analyzed Path**: N/A
**Relevant Symbols**: None — new implementation, APIs designed from PRD + architecture doc.

---

## External Dependencies (Base Hypothesis)

```python
# H-E1: docs/youra_research/h-e1/code/results/storage.py
import sys
sys.path.insert(0, str(H_E1_CODE_DIR))
from results.storage import write_json  # write_json(data: dict, path: Path) -> None

# JSONL format per example (H-E1 lm-eval-harness --log_samples output):
# {"resps": [[ll_0], [ll_1], ...], "target": int, "acc": int}
# probs = scipy.special.softmax([r[0] for r in item["resps"]])  # shape: (n_choices,)
```

---

## A-4: Cell Analyzer [Complexity: 11, Budget: 3 subtasks]

Applied: Standard post-hoc accuracy/confidence decomposition pattern

### API Signatures

```python
from dataclasses import dataclass
from typing import Optional, Callable
from confidence_extractor import CellStats

@dataclass
class DeltaStats:
    model: str
    task: str
    accuracy_clean: float
    accuracy_adv: float
    delta_acc: float                   # accuracy_adv - accuracy_clean; negative = drop
    conf_wrong_clean: Optional[float]
    conf_wrong_adv: Optional[float]
    conf_correct_adv: Optional[float]
    delta_conf_wrong: Optional[float]  # conf_wrong_adv - conf_wrong_clean
    cell_pass: bool                    # delta_acc <= DELTA_ACC_GATE and conf_wrong_adv >= CONF_WRONG_GATE


def compute_delta_stats(
    model: str,
    task: str,
    clean: CellStats,   # from confidence_extractor.extract_cell_stats(clean_examples)
    adv: CellStats,     # from confidence_extractor.extract_cell_stats(adv_examples)
    delta_acc_gate: float = -0.10,
    conf_gate: float = 0.70,
) -> DeltaStats:
    """Compute delta stats for one (model, task) cell."""
    ...


def run_all_cells(
    loader_fn: Callable[[str, str, str], list[dict]],    # load_cell_jsonl(model, task, split)
    extractor_fn: Callable[[list[dict]], CellStats],     # extract_cell_stats(examples)
    models: list[str],
    tasks: list[str],
) -> dict[tuple[str, str], DeltaStats]:
    """Run all 4x5=20 cells. Returns dict keyed by (model, task)."""
    # result shape: 20 entries, keys are (model, task) tuples
    ...
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | DeltaStats dataclass | Define dataclass with all fields; delta_conf_wrong computed as adv-clean |
| L-4-2 | compute_delta_stats | Arithmetic delta + gate boolean; None-safe for conf_wrong when n_wrong==0 |
| L-4-3 | run_all_cells | Nested loop models×tasks; calls loader_fn+extractor_fn for clean+adv; returns 20-entry dict |

---

## A-6: Secondary Analyzer [Complexity: 13, Budget: 3 subtasks]

Applied: Base-vs-chat comparison (RLHF alignment effect on robustness), ANLI difficulty gradient (Nie et al. 2020)

### API Signatures

```python
from cell_analyzer import DeltaStats

def base_vs_chat_comparison(
    cell_results: dict[tuple[str, str], DeltaStats],
) -> dict:
    """Returns {task: {model: delta_acc}} for base and chat llama2-7b; includes mean_delta across tasks."""
    # keys: tasks + "mean"; each value: {"llama2-7b-base": float, "llama2-7b-chat": float}
    ...

def anli_gradient(
    cell_results: dict[tuple[str, str], DeltaStats],
) -> dict:
    """Returns {round: mean_delta_acc} averaged over 4 models; includes direction_confirmed bool."""
    # keys: "anli_r1", "anli_r2", "anli_r3", "direction_confirmed"
    ...

def confidence_delta_analysis(
    cell_results: dict[tuple[str, str], DeltaStats],
) -> dict:
    """Returns {cell_key: delta_conf_wrong} for all 20 cells + "mean_delta_conf_wrong"."""
    ...

def ablation_threshold_sensitivity(
    cell_results: dict[tuple[str, str], DeltaStats],
) -> dict:
    """Returns gate_pass_rate for 3 threshold variants."""
    # A1: delta_acc <= -0.05; A2: delta_acc <= -0.15; A3: conf_wrong >= 0.60
    # keys: "A1_gate_pass_rate", "A2_gate_pass_rate", "A3_gate_pass_rate"
    ...

def ablation_task_subset(
    cell_results: dict[tuple[str, str], DeltaStats],
) -> dict:
    """Returns gate_pass_rate for NLI-only (16 cells) vs non-NLI (4 cells)."""
    # keys: "nli_gate_pass_rate", "non_nli_gate_pass_rate", "nli_n_cells", "non_nli_n_cells"
    ...

def ablation_model_size(
    cell_results: dict[tuple[str, str], DeltaStats],
) -> dict:
    """Returns mean delta_acc and mean conf_wrong_adv for 7B vs 13B model groups."""
    # keys: "7b_mean_delta_acc", "13b_mean_delta_acc", "7b_mean_conf_wrong_adv", "13b_mean_conf_wrong_adv"
    ...
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | base_vs_chat + anli_gradient | Per-task delta lookup; direction check ΔAcc(R3) <= ΔAcc(R1) |
| L-6-2 | confidence_delta_analysis | Iterate 20 cells; skip None conf_wrong; compute mean |
| L-6-3 | ablation_threshold_sensitivity + ablation_task_subset + ablation_model_size | Filter cell_results by condition; recount gate passes; group by model size |

---

## A-7: Visualizer [Complexity: 14, Budget: 4 subtasks]

Applied: Seaborn heatmap + matplotlib grouped bar pattern (standard ML paper figure style)

### API Signatures

```python
from pathlib import Path
from gate_evaluator import GateResult
from cell_analyzer import DeltaStats

def plot_gate_metrics(
    cell_results: dict[tuple[str, str], DeltaStats],
    gate_result: GateResult,
    out_dir: Path,
) -> None:
    """Grouped bar chart: ΔAcc and conf_wrong_adv per cell, with threshold lines."""
    # fig size: (18, 6); 20 cell groups; bar colors: green if cell_pass else red
    # x-axis: "{model}\n{task}" labels; y-axis: metric value
    # hlines: y=-0.10 (ΔAcc gate, dashed), y=0.70 (conf_wrong gate, dotted)
    # saves: out_dir / "gate_metrics_per_cell.png", dpi=150
    ...

def plot_accuracy_scatter(
    cell_results: dict[tuple[str, str], DeltaStats],
    out_dir: Path,
) -> None:
    """Scatter: x=accuracy_clean, y=accuracy_adv; marker size = conf_wrong_adv * 300; color by model."""
    # fig size: (8, 8); diagonal line y=x (no drop reference)
    # legend: model names; colormap: tab10, one color per model
    # saves: out_dir / "accuracy_scatter.png", dpi=150
    ...

def plot_confidence_distributions(
    cell_results: dict[tuple[str, str], DeltaStats],
    out_dir: Path,
) -> None:
    """Histogram of conf_wrong_adv values per model (one subplot per model, 4 subplots)."""
    # fig size: (14, 4); 1 row x 4 cols subplots; bins=20; color=steelblue
    # x-axis: "conf_wrong_adv [0,1]"; vline at x=0.70 (gate threshold, dashed red)
    # saves: out_dir / "confidence_distributions.png", dpi=150
    # Note: each model contributes 5 data points (one per task)
    ...

def plot_delta_acc_heatmap(
    cell_results: dict[tuple[str, str], DeltaStats],
    out_dir: Path,
) -> None:
    """4x5 heatmap of delta_acc (model x task), cell annotations show PASS/FAIL."""
    # fig size: (10, 5); seaborn.heatmap; cmap="RdYlGn"; center=0
    # rows: 4 models; cols: 5 tasks; annot=True with f"{delta_acc:.2f}\n{'P' if cell_pass else 'F'}"
    # saves: out_dir / "delta_acc_heatmap.png", dpi=150
    ...

def plot_anli_gradient(
    anli_stats: dict,   # output of secondary_analyzer.anli_gradient()
    out_dir: Path,
) -> None:
    """Bar chart: mean ΔAcc per ANLI round R1/R2/R3 across 4 models."""
    # fig size: (6, 4); bars for ["anli_r1", "anli_r2", "anli_r3"]; color=steelblue
    # x-axis: "ANLI Round"; y-axis: "Mean ΔAcc"
    # hline: y=-0.10 (gate threshold, dashed red)
    # saves: out_dir / "anli_gradient.png", dpi=150
    ...

def plot_base_vs_chat(
    comparison_stats: dict,   # output of secondary_analyzer.base_vs_chat_comparison()
    out_dir: Path,
) -> None:
    """Grouped bar chart: ΔAcc for llama2-7b-base vs llama2-7b-chat per task."""
    # fig size: (9, 5); grouped bars per task; colors: ["#1f77b4", "#ff7f0e"]
    # x-axis: tasks; y-axis: "ΔAcc (adv - clean)"; legend: ["base", "chat"]
    # saves: out_dir / "base_vs_chat_comparison.png", dpi=150
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | plot_gate_metrics | Grouped bars (ΔAcc, conf_wrong_adv) for 20 cells; green/red coloring; threshold hlines |
| L-7-2 | plot_accuracy_scatter + plot_confidence_distributions | Scatter with bubble size; per-model histogram subplots |
| L-7-3 | plot_delta_acc_heatmap | seaborn.heatmap 4×5; annotate with delta_acc value + PASS/FAIL indicator |
| L-7-4 | plot_anli_gradient + plot_base_vs_chat | Simple bar charts from pre-computed secondary_analyzer dicts |

---

## A-9: Entrypoint [Complexity: 10, Budget: 2 subtasks]

Applied: Standard analysis pipeline pattern (preflight → compute → write → plot)

### API Signatures

```python
def main() -> None:
    """Run full H-M2 post-hoc analysis pipeline."""
    ...
```

### Pseudo-code

```
1. preflight_check()
   # Verifies all 40 JSONL files exist with >=200 examples; SystemExit on failure

2. cell_results = run_all_cells(
       loader_fn=load_cell_jsonl,
       extractor_fn=extract_cell_stats,
       models=MODELS,
       tasks=TASKS,
   )
   # cell_results: dict[tuple[str,str], DeltaStats], len == 20

3. gate_result = evaluate_gate(cell_results)
   # gate_result.overall_result in {"PASS", "EXPLORE"}

4. secondary = {
       "base_vs_chat": base_vs_chat_comparison(cell_results),
       "anli_gradient": anli_gradient(cell_results),
       "confidence_delta": confidence_delta_analysis(cell_results),
       "ablation_threshold": ablation_threshold_sensitivity(cell_results),
       "ablation_task_subset": ablation_task_subset(cell_results),
       "ablation_model_size": ablation_model_size(cell_results),
   }

5. write_main_results(cell_results, H_M2_RESULTS_DIR)
   write_gate_report(gate_result, H_M2_RESULTS_DIR)
   write_secondary_results(secondary, H_M2_RESULTS_DIR)
   write_summary(gate_result, secondary, H_M2_RESULTS_DIR / ".." / "docs" / "h_m2_summary.md")

6. plot_gate_metrics(cell_results, gate_result, H_M2_FIGURES_DIR)
   plot_accuracy_scatter(cell_results, H_M2_FIGURES_DIR)
   plot_confidence_distributions(cell_results, H_M2_FIGURES_DIR)
   plot_delta_acc_heatmap(cell_results, H_M2_FIGURES_DIR)
   plot_anli_gradient(secondary["anli_gradient"], H_M2_FIGURES_DIR)
   plot_base_vs_chat(secondary["base_vs_chat"], H_M2_FIGURES_DIR)

7. logging.info(f"gate_pass_rate: {gate_result.gate_pass_rate:.4f} ({gate_result.overall_result})")
```

### End-to-End Test (inline assertion)

```python
if __name__ == "__main__":
    # Smoke test: verify 20 cells produced
    from jsonl_loader import load_cell_jsonl
    from confidence_extractor import extract_cell_stats
    from config import MODELS, TASKS
    cell_results = run_all_cells(load_cell_jsonl, extract_cell_stats, MODELS, TASKS)
    assert len(cell_results) == 20, f"Expected 20 cells, got {len(cell_results)}"
    main()
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-9-1 | main() wiring | Sequential pipeline: preflight → compute → write → plot → log verdict |
| L-9-2 | E2E assert + __main__ | `assert len(cell_results) == 20`; smoke test before full run |

---

## Tensor / Shape Reference

| Variable | Shape | Note |
|----------|-------|------|
| `probs` | `(n_choices,)` | softmax over log-likelihoods per example; n_choices=2 for QQP, 3 for MNLI/ANLI |
| `cell_results` | 20 entries | dict keyed by (model, task); 4 models × 5 tasks |
| `delta_acc_matrix` | `(4, 5)` | for heatmap; rows=models, cols=tasks |
| `conf_wrong_per_model` | `(5,)` per model | 5 task values per model for histogram |
