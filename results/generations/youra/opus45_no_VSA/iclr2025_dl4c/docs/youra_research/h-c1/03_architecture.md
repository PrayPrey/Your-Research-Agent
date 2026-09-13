# Architecture: H-C1 (Feedback Diversity CONDITION Test)

**Applied**: CodeRL 4-class error taxonomy + entropy-based batch filtering (from experiment brief research; no closer KB match found).

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends H-E1)
**Status**: Patterns found from H-E1 actual implementation
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Findings**: H-E1 provides `RLCodeTrainer` (REINFORCE, `model.py`), `train_rl`/`train_ce` (`train.py`), `execute_and_get_feedback`/`self_refine` (`refine.py`), `Config` dataclass (`config.py`), and data loaders (`data.py`). H-C1 reuses these directly and inserts a `FeedbackDiversityController` between sample generation and RL batch update. Error signal currently collapses to pass/fail — H-C1 must classify `error_msg` into taxonomy.

---

## Module Structure

- `error_taxonomy.py` — classifies execution errors into schema classes (NEW)
- `diversity_controller.py` — `FeedbackDiversityController`, entropy filtering (NEW)
- `model.py` — `RLCodeTrainer` extended to accept controller (MODIFIED, copy from H-E1)
- `train.py` — `train_rl` extended with diversity-conditioned batch construction (MODIFIED, copy from H-E1)
- `refine.py` — reused unchanged from H-E1 (`execute_and_get_feedback`, `self_refine`)
- `data.py` — reused unchanged from H-E1
- `config.py` — `Config` extended with diversity params (MODIFIED)
- `run_experiment.py` — runs 2×2 (High/Low × Refine/Single) (NEW, adapts H-E1's `run_all_conditions`)
- `evaluate.py` — reused from H-E1 + interaction-vs-entropy computation (MODIFIED)
- `visualize.py` — reused from H-E1 + gate scatter plot (MODIFIED)

---

## Data Flow

1. `data.py::get_training_data()` → problems with `base_input` tests (unchanged from H-E1)
2. RL rollout: `RLCodeTrainer` generates code sample → `execute_and_get_feedback(code, tests)` → `(pass_rate, error_msg)`
3. `error_taxonomy.py::classify_error(error_msg, pass_rate)` → `ErrorClass` enum value
4. Samples accumulate into batch: `{"code", "error_type", "pass_rate", "prompt"}`
5. `diversity_controller.py::FeedbackDiversityController.filter_batch(samples, target_entropy)` → filtered batch (oversample minority classes for High mode, concentrate for Low mode)
6. `RLCodeTrainer.rl_step()` consumes filtered batch → REINFORCE update (reuses H-E1 reward/update logic)
7. Post-training: `refine.py::self_refine` (K=3) or `single_shot` per condition → generations
8. `evaluate.py` → pass@1 via evalplus + `compute_interaction(refine_metric, single_metric)` per diversity condition
9. `visualize.py` → interaction-vs-entropy scatter (required figure)

---

## Component Interfaces

### `error_taxonomy.py`

```python
from enum import Enum

class ErrorClass(Enum):
    COMPILE_ERROR = "CompileError"
    RUNTIME_ERROR = "RuntimeError"
    FAILED_TEST = "FailedTest"
    PASSED_TEST = "PassedTest"
    # extensible: SYNTAX_ERROR, TYPE_ERROR added only if 4-class H cannot reach 2.5 bits

def classify_error(error_msg: str, pass_rate: float) -> ErrorClass: ...
```

### `diversity_controller.py`

```python
from collections import Counter

class FeedbackDiversityController:
    def __init__(self, mode: str = "high"): ...  # mode: "high" | "low"
    def compute_entropy(self, error_counts: Counter) -> float: ...
    def filter_batch(self, samples: list[dict], target_entropy: float) -> list[dict]: ...
    def _resample_for_diversity(self, samples: list[dict]) -> list[dict]: ...
    def _resample_for_concentration(self, samples: list[dict]) -> list[dict]: ...
```

Log line on each filter call: `"Feedback entropy: {H:.3f} bits (target: {target}), samples: {n}"`

### `model.py` (extends H-E1 `RLCodeTrainer`)

```python
class RLCodeTrainer:
    def __init__(self, model, tokenizer, cfg: Config, diversity_controller: FeedbackDiversityController | None = None): ...
    def compute_reward(self, code: str, tests: list[str]) -> float: ...  # unchanged
    def rl_step(self, prompt: str, tests: list[str]) -> float: ...  # unchanged
    def rl_step_batch(self, batch: list[dict]) -> float: ...  # NEW: consumes diversity-filtered batch
```

### `train.py`

```python
def train_rl_with_diversity(
    model: PeftModel, tokenizer, data: list[dict], cfg: Config,
    controller: FeedbackDiversityController, target_entropy: float,
) -> PeftModel: ...
```

### `config.py` additions

```python
@dataclass
class Config:
    # ...existing H-E1 fields unchanged...
    diversity_mode: str = "high"       # "high" | "low"
    target_entropy_high: float = 2.5
    target_entropy_low: float = 1.5
```

### `run_experiment.py`

```python
CONDITIONS = ["RL-High-Refine", "RL-Low-Refine", "RL-High-Single", "RL-Low-Single"]

def run_condition(name: str, cfg: Config) -> dict: ...
def run_all_conditions(cfg: Config) -> dict[str, dict]: ...
```

### `evaluate.py` additions

```python
def compute_interaction(refine_pass1: float, single_pass1: float) -> float: ...
def gate_check(interaction_high: float, interaction_low: float) -> bool: ...  # > 0
```

---

## Integration Points with H-E1 Code

| H-C1 needs | H-E1 source | Import path |
|------------|-------------|-------------|
| RL trainer base | `RLCodeTrainer` | `from h_e1.code.model import RLCodeTrainer` (subclass/extend) |
| Execution feedback | `execute_and_get_feedback` | `from h_e1.code.refine import execute_and_get_feedback` |
| Refinement loop | `self_refine`, `single_shot` | `from h_e1.code.refine import self_refine, single_shot` |
| Data loading | `get_training_data`, `load_humaneval_plus`, `load_mbpp_plus` | `from h_e1.code.data import get_training_data, load_humaneval_plus, load_mbpp_plus` |
| CE pretraining | `train_ce`, `CEDataset`, `prepare_ce_dataset` | `from h_e1.code.train import train_ce, prepare_ce_dataset` |
| Config base | `Config` dataclass | Subclass or extend fields directly in `h-c1/code/config.py` |

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation, not spec).

`error_msg` string from `execute_and_get_feedback` is the only new signal H-C1 needs to parse (H-E1 only used pass/fail rate); `classify_error` must handle empty/timeout messages as `RUNTIME_ERROR` fallback.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| C-1 | Error taxonomy | Implement `ErrorClass` + `classify_error` from stderr/pass_rate | 6 | 2+1+2+1 |
| C-2 | Diversity controller | Entropy computation + resample for high/low targets | 10 | 3+2+3+2 |
| C-3 | Extend RLCodeTrainer | Add `rl_step_batch` consuming filtered batches | 8 | 2+2+3+1 |
| C-4 | Extend train_rl | Wire controller into RL loop, log entropy per batch | 7 | 2+2+2+1 |
| C-5 | Config extension | Add diversity_mode, target_entropy fields | 3 | 1+1+1+0 |
| C-6 | 2x2 run_experiment | Loop 4 conditions (High/Low x Refine/Single), reuse refine.py | 9 | 3+2+3+1 |
| C-7 | Mechanism verification | `verify_diversity_mechanism` assert H_high>2.0, H_low<2.0 | 4 | 1+1+1+1 |
| C-8 | Interaction + gate metric | compute_interaction, gate_check, results.json/csv | 6 | 2+1+2+1 |
| C-9 | Visualization | Interaction-vs-entropy scatter (required) + entropy histogram | 5 | 2+1+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [C-2, C-3, C-6], Low(4-8): [C-1, C-4, C-5, C-7, C-8, C-9]
