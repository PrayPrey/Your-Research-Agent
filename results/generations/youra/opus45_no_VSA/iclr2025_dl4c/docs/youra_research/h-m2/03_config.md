# Configuration: H-M2 DiD Semantic Sensitivity

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: Config classes verified from `h-e1/code/config.py` actual implementation
**Config Files Found**: `docs/youra_research/h-e1/code/config.py` (dataclass `Config`)
**Pattern Used**: dataclass (matches base hypothesis pattern)

**Applied**: Standard PyTorch/HF eval defaults; bootstrap CI from diff-diff pattern (KB/Exa research in 02c brief)

---

## Inherited Configuration (Base Hypothesis)

Field names verified from actual H-E1 code (not specs):

```python
# From: docs/youra_research/h-e1/code/config.py (ACTUAL CODE)
model_id: str = "Salesforce/codet5p-220m"
checkpoint_dir -> Path  # property: base_dir / "checkpoints"
# Checkpoints used: checkpoint_dir / "rl_final", checkpoint_dir / "ce_final"
```

H-M2 loads pretrained adapters from `../h-e1/checkpoints/rl_final` and `../h-e1/checkpoints/ce_final`. No training config needed (evaluation-only).

---

## Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Config:
    # Model (base checkpoint, verified from H-E1 config.py)
    model_id: str = "Salesforce/codet5p-220m"
    rl_checkpoint: str = "../h-e1/checkpoints/rl_final"
    ce_checkpoint: str = "../h-e1/checkpoints/ce_final"

    # Dataset
    dataset: str = "evalplus/evalplus"  # HumanEval+, 164 problems

    # Inference (single-shot + K=1 refinement)
    refine_k: int = 1
    max_new_tokens: int = 512
    temperature: float = 0.0  # greedy decoding

    # DiD conditions
    conditions: list = field(default_factory=lambda: ["actual", "control"])
    models: list = field(default_factory=lambda: ["RL", "CE"])

    # Reproducibility
    seeds: list = field(default_factory=lambda: [42, 43, 44])

    # Statistics
    n_bootstrap: int = 1000
    confidence_level: float = 0.95

    # Paths
    base_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent)

    @property
    def figures_dir(self) -> Path:
        return self.base_dir / "figures"

    @property
    def outputs_dir(self) -> Path:
        return self.base_dir / "code" / "outputs"

    def __post_init__(self):
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
```

**Non-standard**: `temperature=0.0` (greedy, not H-E1's 0.8) and `refine_k=1` (not H-E1's 3) — both fixed by experiment brief to isolate the single-step feedback effect for DiD.

---

## YAML Config Example

```yaml
# h-m2_config.yaml
model_id: "Salesforce/codet5p-220m"
rl_checkpoint: "../h-e1/checkpoints/rl_final"
ce_checkpoint: "../h-e1/checkpoints/ce_final"

dataset: "evalplus/evalplus"

refine_k: 1
max_new_tokens: 512
temperature: 0.0

conditions: ["actual", "control"]
models: ["RL", "CE"]
seeds: [42, 43, 44]

n_bootstrap: 1000
confidence_level: 0.95
```

---

## Task: A-1 DiD Evaluation Pipeline [Complexity: 3, Budget: 3]

**Applied**: Standard eval-only pipeline (no training config required, per PRD scope)

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Load checkpoints | Load RL/CE LoRA adapters onto base `codet5p-220m` |
| C-1-2 | 4-cell evaluation | Run single-shot + K=1 refinement across {RL,CE} x {actual,control} x 3 seeds |
| C-1-3 | Bootstrap DiD | Compute DiD contrast + 95% CI (n_bootstrap=1000) per success criteria |
