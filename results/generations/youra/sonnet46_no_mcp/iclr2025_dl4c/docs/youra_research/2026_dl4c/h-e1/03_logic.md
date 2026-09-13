# Logic: H-E1 — Difficulty-Stratified Curriculum GRPO

**Hypothesis:** H-E1 | **Type:** EXISTENCE (PoC) | **Date:** 2026-05-02

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-1: Data Pipeline [Complexity: 10, Budget: 2 subtasks]

Applied: HuggingFace datasets filter+map pattern

### API Signatures

```python
# code/data/preprocessing.py

import datasets
from transformers import PreTrainedTokenizer

def load_apps(split: str = "train") -> datasets.Dataset:
    """Load APPS from hendrycks/apps."""
    ...

def load_code_contests(split: str = "train") -> datasets.Dataset:
    """Load CodeContests from google-deepmind/code_contests."""
    ...

def filter_apps_easy(ds: datasets.Dataset) -> datasets.Dataset:
    """Keep difficulty in [0, 1, 2]."""
    ...

def filter_apps_hard(ds: datasets.Dataset) -> datasets.Dataset:
    """Keep difficulty in [3, 4]."""
    ...

def filter_cc_easy(ds: datasets.Dataset) -> datasets.Dataset:
    """Keep CodeContests Div2 problems."""
    ...

def filter_cc_hard(ds: datasets.Dataset) -> datasets.Dataset:
    """Keep CodeContests Div1 problems."""
    ...

def filter_has_tests(ds: datasets.Dataset) -> datasets.Dataset:
    """Remove problems with empty test cases."""
    ...

def tokenize_prompt(
    example: dict,
    tokenizer: PreTrainedTokenizer,
    max_length: int = 512,
) -> dict:
    """Tokenize problem description. Returns dict with input_ids, attention_mask.
    input_ids: [max_length]  (truncated/padded)
    """
    ...

def build_easy_pool(tokenizer: PreTrainedTokenizer) -> datasets.Dataset:
    """APPS easy + CC Div2, filtered and tokenized."""
    ...

def build_hard_pool(tokenizer: PreTrainedTokenizer) -> datasets.Dataset:
    """APPS hard + CC Div1, filtered and tokenized."""
    ...

def build_full_pool(tokenizer: PreTrainedTokenizer) -> datasets.Dataset:
    """All APPS + CC problems, filtered and tokenized (uniform baseline)."""
    ...
```

```python
# code/data/dataset.py

import torch
from torch.utils.data import Dataset
import datasets as hf_datasets

class CurriculumDataset(Dataset):
    def __init__(
        self,
        easy_data: hf_datasets.Dataset,
        hard_data: hf_datasets.Dataset,
        curriculum_step: int = 2500,
    ) -> None:
        """Phase 0-2499: easy_data; phase 2500+: hard_data."""
        ...

    def set_step(self, step: int) -> None:
        """Switch active_data when step >= curriculum_step."""
        ...

    def __len__(self) -> int: ...

    def __getitem__(self, idx: int) -> dict:
        """Returns tokenized example dict from active_data."""
        ...

class UniformDataset(Dataset):
    def __init__(self, full_data: hf_datasets.Dataset) -> None: ...
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> dict: ...

class EasyOnlyDataset(Dataset):
    def __init__(self, easy_data: hf_datasets.Dataset) -> None: ...
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> dict: ...

class HardOnlyDataset(Dataset):
    def __init__(self, hard_data: hf_datasets.Dataset) -> None: ...
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> dict: ...

def get_dataset(
    condition: str,
    easy_data: hf_datasets.Dataset,
    hard_data: hf_datasets.Dataset,
    full_data: hf_datasets.Dataset,
    curriculum_step: int = 2500,
) -> Dataset:
    """Factory: condition in {'curriculum','uniform','easy_only','hard_only'}."""
    ...
```

### Pseudo-code (CurriculumDataset.set_step — core mechanism)

```
def set_step(self, step):
    if step >= self.curriculum_step and self.active_data is self.easy_data:
        self.active_data = self.hard_data
        print(f"Curriculum phase: switching to hard_data at step {step}")
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Preprocessing | Implement load_apps, load_code_contests, all filter_* and tokenize_prompt, build_*_pool |
| L-1-2 | Dataset classes | Implement CurriculumDataset (with set_step), UniformDataset, EasyOnlyDataset, HardOnlyDataset, get_dataset factory |

---

## A-4: Training Script [Complexity: 12, Budget: 2 subtasks]

Applied: TRL GRPOTrainer with argparse CLI pattern

### API Signatures

```python
# code/training/train.py

import argparse
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import GRPOTrainer, GRPOConfig
from torch.utils.data import Dataset

def parse_args() -> argparse.Namespace:
    """Args: --condition {curriculum,uniform,easy_only,hard_only}, --smoke_test (flag)."""
    ...

def build_model_and_tokenizer(
    model_id: str,
) -> tuple[AutoModelForCausalLM, AutoTokenizer]:
    """Load model in bfloat16 with device_map='auto'. Returns (model, tokenizer)."""
    ...

def build_trainer(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    train_dataset: Dataset,
    callbacks: list,
    condition: str,
) -> GRPOTrainer:
    """Configure GRPOConfig from CONFIG dict and return GRPOTrainer instance."""
    ...

def main() -> None:
    """Parse args, build model/data/trainer, run trainer.train(), save final checkpoint."""
    ...
```

### Pseudo-code (main — wiring all components)

```
def main():
    args = parse_args()
    model, tokenizer = build_model_and_tokenizer(CONFIG["model_id"])

    easy_data = build_easy_pool(tokenizer)
    hard_data = build_hard_pool(tokenizer)
    full_data = build_full_pool(tokenizer)
    dataset = get_dataset(args.condition, easy_data, hard_data, full_data)

    callbacks = [RewardDensityCallback(args.condition, CONFIG["log_dir"])]
    if args.condition == "curriculum":
        callbacks.insert(0, CurriculumCallback(dataset))

    if args.smoke_test:
        CONFIG["max_steps"] = 10

    trainer = build_trainer(model, tokenizer, dataset, callbacks, args.condition)
    trainer.train()
    trainer.save_model(f"{CONFIG['output_dir']}/{args.condition}/final")
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | CLI + model loading | parse_args with --condition/--smoke_test; build_model_and_tokenizer in bfloat16 |
| L-4-2 | Trainer wiring | build_trainer with GRPOConfig; main() orchestrating data, callbacks, training loop |

---

## A-5: Evaluation [Complexity: 11, Budget: 2 subtasks]

Applied: subprocess CLI wrapper + scipy.stats McNemar pattern

### API Signatures

```python
# code/evaluation/evaluate.py

import subprocess
import json
from scipy.stats import chi2

def run_evalplus(
    checkpoint_path: str,
    dataset: str = "humaneval",
    greedy: bool = True,
) -> dict:
    """Run EvalPlus via subprocess CLI. Returns parsed JSON result dict."""
    ...

def parse_evalplus_output(stdout: str) -> float:
    """Extract pass@1 (float in [0,1]) from EvalPlus JSON stdout."""
    ...

def evaluate_all_checkpoints(
    condition: str,
    checkpoint_dir: str,
) -> list[dict]:
    """Sweep checkpoints at steps [500,1000,...,5000]. Returns list[{step: int, pass@1: float}]."""
    ...

def run_mcnemar_test(
    curriculum_results: list[bool],
    uniform_results: list[bool],
) -> tuple[float, float]:
    """McNemar's test on per-problem binary pass/fail.
    curriculum_results: [164]  per-problem bool
    uniform_results:    [164]  per-problem bool
    Returns (p_value, effect_size_pp) where effect_size_pp = mean(curriculum) - mean(uniform).
    """
    ...

def gate_check(
    curriculum_pass1: float,
    uniform_pass1: float,
    p_value: float,
) -> bool:
    """Returns True if curriculum_pass1 >= uniform_pass1 + 0.02 and p_value < 0.05."""
    ...

def save_results(
    condition: str,
    results: dict,
    output_dir: str,
) -> None:
    """Write results to {output_dir}/eval_results_{condition}.json."""
    ...
```

### Pseudo-code (run_mcnemar_test — non-trivial stats)

```
def run_mcnemar_test(curriculum_results, uniform_results):
    # b = curriculum pass, uniform fail
    # c = curriculum fail, uniform pass
    b = sum(c and not u for c, u in zip(curriculum_results, uniform_results))
    c = sum(not c and u for c, u in zip(curriculum_results, uniform_results))
    # McNemar statistic with continuity correction
    chi2_stat = (abs(b - c) - 1) ** 2 / (b + c) if (b + c) > 0 else 0.0
    p_value = chi2.sf(chi2_stat, df=1) / 2  # one-tailed
    effect_size_pp = mean(curriculum_results) - mean(uniform_results)
    return p_value, effect_size_pp
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | EvalPlus wrapper | run_evalplus (subprocess CLI), parse_evalplus_output (JSON parse), evaluate_all_checkpoints (checkpoint sweep) |
| L-5-2 | Statistical testing | run_mcnemar_test (McNemar with continuity correction, one-tailed), gate_check, save_results |
