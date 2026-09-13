# Config: H-E1 Structural Enumeration Preference

**Applied**: PyTorch dataclass config pattern
**Applied**: Standard HuggingFace inference defaults (bfloat16, batch_size=16)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: dataclass

---

## A-6: Pipeline Integration [Complexity: 11, Budget: 2 subtasks]

**Applied**: Standard checkpoint/resume config pattern

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import List
from pathlib import Path


@dataclass
class StimulusConfig:
    n_prompts: int = 75
    factors: List[str] = field(default_factory=lambda: ["structure", "correctness", "completeness"])
    length_tolerance: float = 0.02   # ±2% length match across structure conditions (FR-1.3)
    seed: int = 42


@dataclass
class InferenceConfig:
    batch_size: int = 16
    device: str = "cuda"
    dtype: str = "bfloat16"
    use_4bit: bool = False           # Set True if VRAM < 16GB (UltraRM-13b fallback)


MODEL_IDS = {
    "armo":     "RLHFlow/ArmoRM-Llama3-8B-v0.1",
    "ultra":    "openbmb/UltraRM-13b",
    "starling": "berkeley-nest/Starling-RM-7B-alpha",
    "pairrm":   "llm-blender/PairRM",
}


@dataclass
class ExperimentConfig:
    stimulus: StimulusConfig = field(default_factory=StimulusConfig)
    inference: InferenceConfig = field(default_factory=InferenceConfig)
    output_dir: str = "data"
    figures_dir: str = "figures"
    rm_ids: List[str] = field(default_factory=lambda: ["armo", "ultra", "starling", "pairrm"])
    resume: bool = True              # Resume from checkpoint if intermediate files exist

    def validate(self) -> None:
        assert self.stimulus.n_prompts > 0
        assert 0.0 < self.stimulus.length_tolerance < 0.1
        assert self.inference.batch_size > 0
        for rm in self.rm_ids:
            assert rm in MODEL_IDS, f"Unknown RM key: {rm}"
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        Path(self.figures_dir).mkdir(parents=True, exist_ok=True)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Orchestration Config | ExperimentConfig with resume flag, output/figures dirs, rm_ids list |
| C-6-2 | Validation Hook | `validate()` method asserting field ranges and creating output directories |

---

## A-4: Statistical Analysis [Complexity: 10, Budget: 1 subtask]

**Applied**: Standard Cohen's d gate threshold from prior RLHF behavioral probing literature

### Configuration (Python Dataclass)

```python
@dataclass
class GateConfig:
    d_threshold: float = 0.3   # Minimum Cohen's d for gate pass (per PRD success criteria)
    min_models: int = 2        # Minimum architecturally distinct RMs that must exceed threshold
    alpha: float = 0.05        # Significance level for paired t-test
    ci_coverage: float = 0.95  # CI coverage for effect size intervals
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | Gate + Stats Config | GateConfig with d_threshold=0.3, min_models=2, alpha=0.05, ci_coverage=0.95 |

---

## Full Config Usage Example (run_experiment.py)

```python
cfg = ExperimentConfig()
cfg.validate()
# Access: cfg.stimulus.n_prompts, cfg.inference.batch_size, MODEL_IDS["armo"], etc.
gate = GateConfig()
# Access: gate.d_threshold, gate.min_models
```

---

## Notes

- `use_4bit=False` default; flip to `True` at runtime if `nvidia-smi` shows VRAM < 16GB
- `resume=True` enables skip of already-completed pipeline stages (stimuli.json, raw_scores.json)
- `MODEL_IDS` dict kept separate from dataclass for easy reference in reward_models.py adapters
- All 4 RM keys must match entries in `MODEL_IDS`; `validate()` enforces this at startup
