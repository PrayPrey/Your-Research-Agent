# Config: H-E1 (EXISTENCE)

**Applied**: No matching KB pattern found (searched "DL config patterns dataclass"); used standard dataclass defaults.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: dataclass

---

EXISTENCE experiment (correlation analysis, no training) → single fixed config, no hyperparameter grid, 1 seed.

## A-1: Config setup [Complexity: 3, Budget: 3]

**Applied**: Standard Python dataclass defaults

### Configuration (Python Dataclass)

```python
# code/config.py
from dataclasses import dataclass, field

@dataclass
class ExperimentConfig:
    model_sizes: list[str] = field(default_factory=lambda: [
        "410m", "1b", "1.4b", "2.8b", "6.9b", "12b"
    ])
    checkpoint_steps: list[int] = field(default_factory=lambda: [
        0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000, 143000
    ])
    tasks: list[str] = field(default_factory=lambda: [
        "mmlu", "arc_challenge", "hellaswag", "winogrande"
    ])
    wikitext_task: str = "wikitext"
    ngram_n: int = 13
    seed: int = 1
    hf_org: str = "EleutherAI"
    model_name_template: str = "{org}/pythia-{size}"
    # Gate thresholds (from PRD success criteria)
    gate_r_threshold: float = 0.2
    gate_p_threshold: float = 0.05

@dataclass
class PathsConfig:
    results_dir: str = "results"
    eval_cache_path: str = "results/eval_cache.json"
    contamination_cache_path: str = "results/contamination_cache.json"
    analysis_output_path: str = "results/analysis.json"
    figures_dir: str = "figures"

CONFIG = ExperimentConfig()
PATHS = PathsConfig()
```

### YAML Schema (optional override file, `config.yaml`)

```yaml
model_sizes: ["410m", "1b", "1.4b", "2.8b", "6.9b", "12b"]
checkpoint_steps: [0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000, 143000]
tasks: ["mmlu", "arc_challenge", "hellaswag", "winogrande"]
wikitext_task: "wikitext"
ngram_n: 13
seed: 1
gate_r_threshold: 0.2
gate_p_threshold: 0.05
```

### Model Checkpoints Configuration

Checkpoint revision string passed to `transformers.AutoModel.from_pretrained(revision=...)`:

```python
def checkpoint_revision(step: int) -> str:
    return f"step{step}"

def model_id(org: str, size: str) -> str:
    return f"{org}/pythia-{size}"
```
72 total runs = 6 sizes × 12 steps.

### Evaluation Task Configuration

lm-eval-harness task list = `CONFIG.tasks + [CONFIG.wikitext_task]`. All tasks use default lm-eval-harness few-shot settings (0-shot) and full standard test sets (no subsampling, per PRD 4.1).

### Output Paths Configuration

- `results/eval_cache.json` — cached `{size, step, task, score, wikitext_ppl}` records (avoids re-running 72×5 evals)
- `results/contamination_cache.json` — `{task: contamination_pct}`
- `results/analysis.json` — `{r, p, residuals, per_benchmark}`
- `figures/*.png` — 5 required/additional plots (see architecture `visualize.py`)

### Subtasks [1/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Write config.py | ExperimentConfig + PathsConfig dataclasses with defaults above |

## A-7: Orchestration output config [Complexity: 6, Budget: reuse 1 remaining subtask]

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-7-1 | Gate check print | run.py reads `CONFIG.gate_r_threshold/gate_p_threshold`, prints pass/fail |
