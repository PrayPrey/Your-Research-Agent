# Config: H-E1 (Feedback Ordering Effect in LLM Code Repair)

**Type**: EXISTENCE (PoC) — single fixed config, no hyperparameter search.

**Applied**: No directly relevant KB pattern found (search returned unrelated diffusion-model repo scripts) — using standard dataclass config per architecture spec.

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: dataclass

---

## A-1: Config + Data Loading [Complexity: 6, Budget: 4]

**Applied**: Standard PyTorch/dataclass defaults (EXISTENCE PoC — fixed config, no tuning)

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class ExperimentConfig:
    # LLM generation
    model: str = "gpt-4o-mini"
    temperature: float = 0.0          # deterministic (NFR-1)
    max_tokens: int = 2048

    # Feedback
    feedback_token_budget: int = 500  # per feedback type (static, exec)

    # Repair loop
    n_iterations: int = 3

    # Sandbox execution
    exec_timeout_s: int = 10
    exec_retries: int = 3             # majority vote for flaky tests

    # Reproducibility
    seed: int = 42

    # Metrics
    bootstrap_resamples: int = 10000
    alpha: float = 0.05               # significance level for McNemar test

    # Data
    dataset_sources: tuple[str, ...] = ("openai/human-eval", "mbpp")
```

### Experiment Settings (YAML)

```yaml
# h-e1_experiment.yaml
experiment:
  name: h-e1-feedback-ordering
  model: gpt-4o-mini
  temperature: 0.0
  max_tokens: 2048
  seed: 42

feedback:
  token_budget: 500
  conditions: ["A", "B"]   # A = static->exec, B = exec->static

repair_loop:
  n_iterations: 3

sandbox:
  timeout_s: 10
  retries: 3

metrics:
  bootstrap_resamples: 10000
  alpha: 0.05
  success_thresholds:
    relative_improvement_pct: 15
    ci_lower_bound_pct: 10
    mcnemar_p: 0.05

data:
  sources: ["openai/human-eval", "mbpp"]
  total_problems: 664   # 164 HumanEval + 500 MBPP
```

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | ExperimentConfig dataclass | Define dataclass in `config.py` with all fields above |
| C-1-2 | Data loader | `load_problems(seed)` loads HumanEval + MBPP via HF `datasets`, shuffles with fixed seed |

---

## A-3: Sandbox Configuration [Complexity: 10, Budget: 1 subtask allocated here]

**Applied**: Standard timeout/retry defaults for flaky test execution

### Configuration (reuses `ExperimentConfig` fields)

```python
# sandbox.py uses cfg.exec_timeout_s, cfg.exec_retries directly — no separate config class
# Majority vote: run test cfg.exec_retries times, take majority pass/fail result
```

- `exec_timeout_s: int = 10` — per FR-4/NFR-3
- `exec_retries: int = 3` — majority vote, per NFR-3

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-3-1 | Sandbox timeout/retry wiring | Wire `exec_timeout_s` + `exec_retries` into `run_tests_majority_vote` |

---

## A-6: Metrics Configuration [Complexity: 9, Budget: 1 subtask allocated here]

**Applied**: Standard bootstrap CI + McNemar defaults (10k resamples is field-standard for stable CI)

### Configuration (reuses `ExperimentConfig` fields)

- `bootstrap_resamples: int = 10000` — per FR-7
- `alpha: float = 0.05` — 95% CI, matches success criteria (CI lower bound >10%)

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-6-1 | Metrics config wiring | Wire `bootstrap_resamples`/`alpha` into `bootstrap_ci` and `mcnemar_test` |

---

## Total Subtask Budget: 4/4 used (C-1-1, C-1-2, C-3-1, C-6-1)
