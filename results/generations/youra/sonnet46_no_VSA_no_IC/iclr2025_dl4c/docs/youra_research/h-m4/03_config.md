---
hypothesis_id: h-m4
type: MECHANISM
phase: 3_config
generated_at: 2026-08-21
author: yoon303@etri.re.kr
base_hypothesis: h-m2
---

# Config: H-M4 — EvalPlus Checkpoint Evaluation

Applied: Standard dataclass config pattern (verified H-M2 field names from actual code)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M2)
**Status**: Config classes verified from actual code at `docs/youra_research/h-m2/code/config.py`
**Config Files Found**: `docs/youra_research/h-m2/code/config.py`
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual H-M2 Code)

```python
# From: docs/youra_research/h-m2/code/config.py (ACTUAL CODE — verified)
@dataclass
class H_M2Config:
    profiling_json: str = "docs/youra_research/h-e1/results/mbpp_variance_profile.json"
    model_id: str = "deepseek-ai/deepseek-coder-7b-instruct-v1.5"
    mbpp_dataset_id: str = "google-research-datasets/mbpp"
    mbpp_subset: str = "full"
    mbpp_split: str = "train"
    k: int = 50
    seed: int = 42
    learning_rate: float = 5e-7
    num_generations: int = 4
    generation_batch_size: int = 4
    max_steps: int = 50
    beta: float = 0.0
    logging_steps: int = 1
    use_vllm: bool = False
    save_steps: List[int] = field(default_factory=lambda: [10, 20, 50])
    max_new_tokens: int = 512
    exec_timeout: float = 5.0
    gate_checkpoints: List[int] = field(default_factory=lambda: [10, 20, 50])
    gap_threshold_pp: float = 0.05
    results_dir: str = "docs/youra_research/h-m2/results"
    figures_dir: str = "docs/youra_research/h-m2/figures"
    min_trl_version: str = "0.15.0"
```

**Verified from**: `docs/youra_research/h-m2/code/config.py` (actual implementation)

**H-M4 fallback training uses these H-M2 fields** (via sys.path injection):
- `model_id` — base model for GRPO
- `save_steps` — `[10, 20, 50]` (field exists; fallback must override `save_strategy="steps"`)
- `results_dir` — checkpoint output root
- `learning_rate`, `num_generations`, `generation_batch_size`, `max_steps`, `beta`

**Warning**: H-M2 `build_grpo_config()` sets `save_strategy="no"`. Fallback training must override to `"steps"` inline.

---

## A-5: EvalPlus Evaluation + Parsing [Complexity: 9, Budget: 2 subtasks]

Applied: Standard dataclass config pattern

### EvalPlus CLI Parameter Reference

| Parameter | Value | Notes |
|-----------|-------|-------|
| `--dataset` | `humaneval` | HumanEval+ benchmark |
| `--backend` | `hf` | HuggingFace transformers backend |
| `--n_samples` | `8` | Samples per problem |
| `--temperature` | `0.8` | Generation temperature |
| `--root` | `{eval_output_root}/{condition}/{step}` | Output directory root |
| `--samples` | `{output_dir}/samples.jsonl` | Input to evaluate command |

**CLI invocations:**

```
# Generation
python -m evalplus.codegen \
    --model {checkpoint_path} \
    --dataset humaneval \
    --backend hf \
    --n_samples 8 \
    --temperature 0.8 \
    --root {eval_output_root}/{condition}/{step}

# Evaluation
python -m evalplus.evaluate \
    --dataset humaneval \
    --samples {output_dir}/samples.jsonl
```

**stdout parsing regex** for `evaluate_samples()`:

```python
import re

PASS_AT_1_PATTERN = re.compile(r"humaneval_plus pass@1:\s*([0-9]+\.[0-9]+)")

def parse_pass_at_1(stdout: str) -> float:
    m = PASS_AT_1_PATTERN.search(stdout)
    if m is None:
        raise ValueError(f"humaneval_plus pass@1 not found in stdout:\n{stdout}")
    return float(m.group(1))
```

**Output path conventions:**

```
eval_output_root/
  {condition}/
    {step}/
      samples.jsonl          # generated samples (resume-safe: skip if exists)
      eval_results.json      # written by evalplus.evaluate
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | evaluate_samples() + parse_pass_at_1() | subprocess call to evalplus.evaluate; parse stdout with PASS_AT_1_PATTERN regex; raise ValueError on parse failure |
| C-5-2 | Resume-safe output path logic | Check `samples.jsonl` existence before generation; derive output_dir from eval_output_root/{condition}/{step} |

---

## H_M4Config — Full Configuration

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import Dict, List
import os


@dataclass
class H_M4Config:
    # EvalPlus parameters
    dataset: str = "humaneval"
    n_samples: int = 8
    temperature: float = 0.8
    backend: str = "hf"

    # Base model (step_0 frozen baseline)
    baseline_model: str = "deepseek-ai/deepseek-coder-7b-instruct-v1.5"

    # H-M2 checkpoint paths (verified field names from H_M2Config)
    h_m2_results_dir: str = "docs/youra_research/h-m2/results"
    h_m2_code_dir: str = "docs/youra_research/h-m2/code"

    # Experiment dimensions
    conditions: List[str] = field(default_factory=lambda: ["variance50", "random50", "full374"])
    steps: List[str] = field(default_factory=lambda: ["step_10", "step_20", "step_50"])
    # Non-standard: step_0 = frozen baseline, evaluated once and reused for all conditions
    baseline_step: str = "step_0"

    # Gate thresholds (FR-9)
    p1_improvement_pp: float = 0.02   # variance50 pass@1 improvement over baseline
    p1_gap_pp: float = 0.01           # variance50 pass@1 gap over random50 at step 50
    p3_efficiency: float = 0.80       # variance50 pass@1 / full374 pass@1 at step 50

    # Output paths
    results_dir: str = "docs/youra_research/h-m4/results"
    figures_dir: str = "docs/youra_research/h-m4/figures"
    eval_output_root: str = "docs/youra_research/h-m4/eval_cache"

    def checkpoint_path(self, condition: str, step: str) -> str:
        """Returns checkpoint dir for (condition, step); step_0 returns baseline_model."""
        if step == self.baseline_step:
            return self.baseline_model
        step_num = int(step.replace("step_", ""))
        return f"{self.h_m2_results_dir}/{condition}/checkpoint-{step_num}"

    def checkpoint_exists(self, condition: str, step: str) -> bool:
        if step == self.baseline_step:
            return True  # HuggingFace Hub model, always available
        return os.path.isdir(self.checkpoint_path(condition, step))

    def eval_output_dir(self, condition: str, step: str) -> str:
        return f"{self.eval_output_root}/{condition}/{step}"

    def samples_path(self, condition: str, step: str) -> str:
        return f"{self.eval_output_dir(condition, step)}/samples.jsonl"

    def __post_init__(self):
        assert self.n_samples >= 1
        assert 0.0 < self.temperature <= 2.0
        assert self.dataset == "humaneval"
        assert len(self.conditions) > 0
        assert len(self.steps) > 0
        assert 0.0 <= self.p3_efficiency <= 1.0
```

### YAML Schema (for experiment configuration overrides)

```yaml
# docs/youra_research/h-m4/config.yaml
# All fields are optional — missing fields use H_M4Config defaults above.

evalplus:
  dataset: humaneval          # fixed; do not change
  n_samples: 8
  temperature: 0.8
  backend: hf

model:
  baseline_model: deepseek-ai/deepseek-coder-7b-instruct-v1.5

paths:
  h_m2_results_dir: docs/youra_research/h-m2/results
  h_m2_code_dir: docs/youra_research/h-m2/code
  results_dir: docs/youra_research/h-m4/results
  figures_dir: docs/youra_research/h-m4/figures
  eval_output_root: docs/youra_research/h-m4/eval_cache

experiment:
  conditions:
    - variance50
    - random50
    - full374
  steps:
    - step_10
    - step_20
    - step_50

gate_thresholds:
  p1_improvement_pp: 0.02
  p1_gap_pp: 0.01
  p3_efficiency: 0.80
```

### Validation Rules

| Field | Rule | Error |
|-------|------|-------|
| `dataset` | must be `"humaneval"` | ValueError |
| `n_samples` | >= 1 | AssertionError |
| `temperature` | 0 < T <= 2.0 | AssertionError |
| `p3_efficiency` | 0.0 <= v <= 1.0 | AssertionError |
| `conditions` | non-empty list | AssertionError |
| `steps` | non-empty list | AssertionError |

---

## Self-Validation

- [x] ONE format only (dataclass — no duplicate dict format)
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Rationale only for non-standard values (step_0 baseline reuse)
- [x] Subtask count within budget (2/2 for A-5)
- [x] "Codebase Analysis (Serena)" section included
- [x] H-M2 field names verified from actual code
- [x] Inherited Configuration section included
