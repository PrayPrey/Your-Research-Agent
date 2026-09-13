# Config: H-M2 — Budget-Ratio Dose-Response Analysis

Applied: inference-config-dataclass pattern (knowledge-grounded)
Applied: budget-sweep-evaluation pattern (knowledge-grounded)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends H-M1, which extends H-E1)
**Status**: patterns found from base code (direct file reads; Serena MCP unavailable in no-mcp environment)
**Config Files Found**: `h-e1/code/config.py`, `h-m1/code/config.py`
**Pattern Used**: dataclass

---

## Inherited Configuration

### From H-E1 (Actual Code — h-e1/code/config.py)

```python
@dataclass
class LoRAConfig:
    rank: int = 16
    alpha: int = 32
    dropout: float = 0.05
    target_modules: List[str] = field(default_factory=lambda: ["q_proj", "v_proj"])

@dataclass
class TrainingConfig:
    kv_budget_ratio: float = 0.5
    fp16: bool = True
    seed: int = 42
    max_seq_length: int = 32768
```

**Usage in H-M2**: LoRAConfig is reused implicitly via PEFT adapter loading. TrainingConfig adapter paths (`outputs/h-e1/{model}-{condition}/`) are the source of adapter checkpoints.

### From H-M1 (Actual Code — h-m1/code/config.py)

```python
LONGBENCH_TASKS: List[str] = [
    "narrativeqa", "qasper", "multifieldqa_en", "multifieldqa_zh",
    "hotpotqa", "2wikimqa", "musique", "dureader",
    "gov_report", "qmsum", "multi_news", "vcsum",
    "trec", "triviaqa", "samsum", "lsht",
    "passage_count", "passage_retrieval_en", "passage_retrieval_zh",
    "lcc", "repobench-p",
]

LONGBENCH_CATEGORIES = {
    "single-doc-qa":  ["narrativeqa", "qasper", "multifieldqa_en", "multifieldqa_zh"],
    "multi-doc-qa":   ["hotpotqa", "2wikimqa", "musique", "dureader"],
    "summarization":  ["gov_report", "qmsum", "multi_news", "vcsum"],
    "few-shot":       ["trec", "triviaqa", "samsum", "lsht"],
    "synthetic":      ["passage_count", "passage_retrieval_en", "passage_retrieval_zh"],
    "code":           ["lcc", "repobench-p"],
}

@dataclass
class InferenceConfig:
    max_seq_length: int = 4096
    batch_size: int = 1
    seed: int = 1
    fp16: bool = True
    kv_budget_ratio: float = 0.5
```

**Usage in H-M2**: LONGBENCH_TASKS, LONGBENCH_CATEGORIES, and LongBenchDataLoader are re-exported via dataset.py thin wrapper. H-M2 adopts `seed=1` and `max_seq_length=4096` from H-M1 inference settings.

---

## H-M2 Configuration (config.py)

### Complete Python Dataclasses

```python
import os
from dataclasses import dataclass, field
from typing import List

# Resolved relative to h-m2/code/
_H_E1_OUTPUTS = os.path.join(os.path.dirname(__file__), "../../h-e1/code/outputs/h-e1")
_H_M1_CODE    = os.path.join(os.path.dirname(__file__), "../../h-m1/code")

BUDGET_RATIOS: List[float] = [0.25, 0.50, 0.75]

LONGBENCH_TASKS: List[str] = [
    "narrativeqa", "qasper", "multifieldqa_en", "multifieldqa_zh",
    "hotpotqa", "2wikimqa", "musique", "dureader",
    "gov_report", "qmsum", "multi_news", "vcsum",
    "trec", "triviaqa", "samsum", "lsht",
    "passage_count", "passage_retrieval_en", "passage_retrieval_zh",
    "lcc", "repobench-p",
]

LONGBENCH_CATEGORIES = {
    "single-doc-qa":  ["narrativeqa", "qasper", "multifieldqa_en", "multifieldqa_zh"],
    "multi-doc-qa":   ["hotpotqa", "2wikimqa", "musique", "dureader"],
    "summarization":  ["gov_report", "qmsum", "multi_news", "vcsum"],
    "few-shot":       ["trec", "triviaqa", "samsum", "lsht"],
    "synthetic":      ["passage_count", "passage_retrieval_en", "passage_retrieval_zh"],
    "code":           ["lcc", "repobench-p"],
}

# Per-task max_new_tokens (from LongBench paper defaults)
TASK_MAX_NEW_TOKENS: dict = {
    "narrativeqa": 128, "qasper": 128, "multifieldqa_en": 64, "multifieldqa_zh": 64,
    "hotpotqa": 32, "2wikimqa": 32, "musique": 32, "dureader": 128,
    "gov_report": 512, "qmsum": 512, "multi_news": 512, "vcsum": 512,
    "trec": 64, "triviaqa": 32, "samsum": 128, "lsht": 64,
    "passage_count": 32, "passage_retrieval_en": 32, "passage_retrieval_zh": 32,
    "lcc": 64, "repobench-p": 64,
}

# Per-task scorer type
TASK_SCORER_MAP: dict = {
    "narrativeqa": "f1", "qasper": "f1", "multifieldqa_en": "f1",
    "multifieldqa_zh": "f1", "hotpotqa": "f1", "2wikimqa": "f1",
    "musique": "f1", "dureader": "rouge-l",
    "gov_report": "rouge-l", "qmsum": "rouge-l",
    "multi_news": "rouge-l", "vcsum": "rouge-l",
    "trec": "accuracy", "triviaqa": "f1", "samsum": "rouge-l", "lsht": "accuracy",
    "passage_count": "accuracy", "passage_retrieval_en": "accuracy",
    "passage_retrieval_zh": "accuracy",
    "lcc": "edit-distance", "repobench-p": "edit-distance",
}


@dataclass
class AdapterSpec:
    model_name: str      # "meta-llama/Llama-2-7b-hf" | "mistralai/Mistral-7B-v0.1"
    adapter_path: str    # absolute path to H-E1 PEFT checkpoint dir
    adapter_type: str    # "sequential" | "eviction-aware"


@dataclass
class BudgetSweepConfig:
    experiment_id: str = "h-m2"
    budget_ratios: List[float] = field(default_factory=lambda: list(BUDGET_RATIOS))
    adapters: List[AdapterSpec] = field(default_factory=list)
    longbench_tasks: List[str] = field(default_factory=lambda: list(LONGBENCH_TASKS))
    max_seq_length: int = 4096
    batch_size: int = 1
    seed: int = 1
    fp16: bool = True
    attn_implementation: str = "eager"   # Non-standard: sdpa causes H2O mask conflicts (H-M1 lesson)
    figures_dir: str = "figures"
    results_dir: str = "outputs/h-m2"
    spearman_gate_threshold: float = -0.8   # Primary gate: rho < -0.8 on >=1 model


def get_default_config() -> BudgetSweepConfig:
    """Build BudgetSweepConfig with all 4 H-E1 adapter combinations."""
    h_e1 = _H_E1_OUTPUTS
    adapters = [
        AdapterSpec(
            model_name="meta-llama/Llama-2-7b-hf",
            adapter_path=os.path.join(h_e1, "llama2-7b-baseline"),
            adapter_type="sequential",
        ),
        AdapterSpec(
            model_name="meta-llama/Llama-2-7b-hf",
            adapter_path=os.path.join(h_e1, "llama2-7b-eviction-aware"),
            adapter_type="eviction-aware",
        ),
        AdapterSpec(
            model_name="mistralai/Mistral-7B-v0.1",
            adapter_path=os.path.join(h_e1, "mistral-7b-baseline"),
            adapter_type="sequential",
        ),
        AdapterSpec(
            model_name="mistralai/Mistral-7B-v0.1",
            adapter_path=os.path.join(h_e1, "mistral-7b-eviction-aware"),
            adapter_type="eviction-aware",
        ),
    ]
    return BudgetSweepConfig(adapters=adapters)


def validate_config(cfg: BudgetSweepConfig) -> None:
    assert len(cfg.budget_ratios) > 0, "budget_ratios must not be empty"
    for r in cfg.budget_ratios:
        assert 0.0 < r < 1.0, f"budget_ratio must be in (0,1), got: {r}"
    assert len(cfg.adapters) > 0, "adapters must not be empty"
    for a in cfg.adapters:
        assert a.model_name != "", "AdapterSpec.model_name must be set"
        assert a.adapter_type in ("sequential", "eviction-aware"), \
            f"adapter_type must be 'sequential' or 'eviction-aware', got: {a.adapter_type}"
        assert os.path.isdir(a.adapter_path), \
            f"adapter_path not found: {a.adapter_path}"
    assert cfg.attn_implementation == "eager", \
        "attn_implementation must be 'eager' (H2O wrapper compatibility)"
    os.makedirs(cfg.figures_dir, exist_ok=True)
    os.makedirs(cfg.results_dir, exist_ok=True)
```

---

## Environment / Path Configuration

```python
# Set before any model loading — select GPU with lowest memory usage
import os
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "0")

# Adapter path resolution (relative to h-m2/code/)
H_E1_OUTPUTS = "outputs/h-e1"   # resolved by _H_E1_OUTPUTS above
H_M1_CODE    = "../../h-m1/code"
```

**Adapter path convention** (from H-E1 TrainingConfig.output_dir):

| model_name | adapter_type | adapter_path suffix |
|---|---|---|
| meta-llama/Llama-2-7b-hf | sequential | llama2-7b-baseline |
| meta-llama/Llama-2-7b-hf | eviction-aware | llama2-7b-eviction-aware |
| mistralai/Mistral-7B-v0.1 | sequential | mistral-7b-baseline |
| mistralai/Mistral-7B-v0.1 | eviction-aware | mistral-7b-eviction-aware |

---

## YAML Configuration Schema

```yaml
experiment_id: "h-m2"
seed: 1
fp16: true
attn_implementation: "eager"
max_seq_length: 4096
batch_size: 1
budget_ratios: [0.25, 0.50, 0.75]
spearman_gate_threshold: -0.8
figures_dir: "figures"
results_dir: "outputs/h-m2"

adapters:
  - model_name: "meta-llama/Llama-2-7b-hf"
    adapter_path: "outputs/h-e1/llama2-7b-baseline"
    adapter_type: "sequential"
  - model_name: "meta-llama/Llama-2-7b-hf"
    adapter_path: "outputs/h-e1/llama2-7b-eviction-aware"
    adapter_type: "eviction-aware"
  - model_name: "mistralai/Mistral-7B-v0.1"
    adapter_path: "outputs/h-e1/mistral-7b-baseline"
    adapter_type: "sequential"
  - model_name: "mistralai/Mistral-7B-v0.1"
    adapter_path: "outputs/h-e1/mistral-7b-eviction-aware"
    adapter_type: "eviction-aware"
```

---

## Hyperparameter Reference Table

| Parameter | Value | Source |
|---|---|---|
| budget_ratios | [0.25, 0.50, 0.75] | PRD FR-1 |
| max_seq_length | 4096 | H-M1 InferenceConfig |
| batch_size | 1 | H-M1 InferenceConfig |
| seed | 1 | H-M1 InferenceConfig |
| fp16 | True | H-E1 TrainingConfig |
| attn_implementation | "eager" | H-M1 lesson (H2O wrapper compat) |
| spearman_gate_threshold | -0.8 | PRD gate criterion |
| total_runs | 12 | 4 adapters x 3 budgets |

---

## Visualization Configuration

```python
VIZ_CONFIG = {
    "gap_vs_budget":   {"filename": "figures/gap_vs_budget.png",   "figsize": (8, 5)},
    "spearman_bar":    {"filename": "figures/spearman_bar.png",    "figsize": (7, 4)},
    "gap_heatmap":     {"filename": "figures/gap_heatmap.png",     "figsize": (10, 6)},
    "absolute_curves": {"filename": "figures/absolute_curves.png", "figsize": (12, 5)},
}

# Color scheme: eviction-aware vs sequential (consistent across all plots)
COLOR_MAP = {
    "eviction-aware": "#2196F3",   # blue
    "sequential":     "#FF5722",   # orange
}
LINE_STYLE_MAP = {
    "meta-llama/Llama-2-7b-hf":  "-",   # solid
    "mistralai/Mistral-7B-v0.1": "--",  # dashed
}
```

---

## Configuration Validation Rules

1. All `budget_ratios` must be in `(0.0, 1.0)` exclusive.
2. All `adapter_path` directories must exist before sweep begins.
3. `adapter_type` must be `"sequential"` or `"eviction-aware"`.
4. `attn_implementation` must be `"eager"` (enforced in validate_config).
5. `figures_dir` and `results_dir` are created by validate_config if absent.
6. Smoke test (smoke_test.py) uses 1 adapter + 3 budget ratios on a short synthetic input (FR-8).

---

## Subtask Breakdown

### Subtask C-10-1: Config Dataclass Unit Tests
Parent: A-10
Description: Tests for `get_default_config()` return type, field defaults, `validate_config()` pass/fail cases (missing adapter_path, bad adapter_type, ratio out of range).

### Subtask C-10-2: Scorer and Path Resolution Tests
Parent: A-10
Description: Tests for TASK_SCORER_MAP completeness (all 21 tasks mapped), adapter path suffix convention, LONGBENCH_CATEGORIES coverage (all 21 tasks appear in exactly one category).

### Subtask C-6-1: Figure Output Config
Parent: A-6
Description: VIZ_CONFIG dict with filename, figsize per figure. COLOR_MAP and LINE_STYLE_MAP constants used by all plot functions in visualize.py.

### Subtask C-6-2: Visualization Validation
Parent: A-6
Description: Validation that all 4 figure files are written to `figures_dir` after sweep. File existence check in run_experiment.py post-step.

### Subtask C-9-1: Orchestrator Config Wiring
Parent: A-9
Description: run_experiment.py reads BudgetSweepConfig via `get_default_config()`, calls `validate_config()`, iterates `adapters x budget_ratios` (12 runs), writes per-run CSV to `results_dir`, writes Spearman JSON summary, then calls visualize functions with VIZ_CONFIG paths.
