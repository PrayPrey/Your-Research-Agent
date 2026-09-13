# Configuration: H-C1

**Type**: CONDITION | **Format**: Dataclass (Python)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: config classes verified from base code
**Config Files Found**: `docs/youra_research/h-e1/code/config.py`
**Pattern Used**: dataclass

---

## Inherited Configuration (Base: H-E1)

```python
# From: docs/youra_research/h-e1/code/config.py (ACTUAL CODE)
@dataclass
class Config:
    model_id: str = "Salesforce/codet5p-220m"
    lora_r: int = 16
    lora_alpha: int = 32
    lora_target_modules: list = field(default_factory=lambda: ["q", "v"])
    lora_dropout: float = 0.1
    lr: float = 2e-5
    weight_decay: float = 0.05
    warmup_steps: int = 200
    batch_size: int = 8
    ce_epochs: int = 10
    rl_epochs: int = 5
    rl_lr: float = 1e-5
    refine_k: int = 3
    max_new_tokens: int = 512
    temperature: float = 0.8
    seed: int = 42
    base_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent)
```

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation). Field name is `lr` (not `learning_rate`).

---

## A-1: Feedback Diversity Config [Complexity: 2, Budget: 4]

**Applied**: Standard PyTorch defaults + CodeRL AdamW/lr overrides (per experiment brief)

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from pathlib import Path
from docs.youra_research.h_e1.code.config import Config as BaseConfig


@dataclass
class HC1Config(BaseConfig):
    # Overrides: CodeRL defaults differ from H-E1 base (2e-5 -> 5e-5)
    lr: float = 5e-5

    # Diversity thresholds (bits, Shannon entropy of error-type distribution)
    diversity_high_threshold: float = 2.5
    diversity_low_threshold: float = 1.5
    error_types: int = 4  # CompileError, RuntimeError, FailedTest, PassedTest

    # Datasets (evalplus)
    dataset_primary: str = "humaneval_plus"
    dataset_secondary: str = "mbpp_plus"

    # Conditions: cartesian product of diversity_mode x refine_mode
    diversity_modes: list = field(default_factory=lambda: ["high", "low"])
    refine_modes: list = field(default_factory=lambda: ["refine", "single"])

    # Single seed (CONDITION hypothesis constraint)
    seed: int = 42
```

**Non-standard**: `lr=5e-5` overrides base H-E1 (2e-5) — CodeRL paper default, sourced in experiment brief.

### Subtasks [2/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | FeedbackDiversityController | Entropy computation + batch resampling (high/low) |
| C-1-2 | 2x2 condition runner | Loop over diversity_modes x refine_modes, reuse H-E1 train/refine/eval |

---

## CLI Argument Structure

```python
import argparse

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="H-C1: Feedback diversity necessity test")
    p.add_argument("--diversity-mode", choices=["high", "low"], required=True)
    p.add_argument("--refine-mode", choices=["refine", "single"], default="single")
    p.add_argument("--lr", type=float, default=5e-5)
    p.add_argument("--batch-size", type=int, default=8)
    p.add_argument("--ce-epochs", type=int, default=10)
    p.add_argument("--rl-epochs", type=int, default=5)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--diversity-high-threshold", type=float, default=2.5)
    p.add_argument("--diversity-low-threshold", type=float, default=1.5)
    return p
```

Usage: `python run_experiment.py --diversity-mode high --refine-mode refine`

---

## YAML Config Schema (Reference, Not Used for Code)

```yaml
# h-c1/config.yaml — optional external override, loaded via HC1Config(**yaml.safe_load(...))
model_id: "Salesforce/codet5p-220m"
lr: 5.0e-5
weight_decay: 0.05
batch_size: 8
ce_epochs: 10
rl_epochs: 5
refine_k: 3
diversity_high_threshold: 2.5
diversity_low_threshold: 1.5
error_types: 4
dataset_primary: "humaneval_plus"
dataset_secondary: "mbpp_plus"
seed: 42
```

**Note**: Dataclass is the source of truth (Phase 4 copy-paste target); YAML is optional override loader only.
