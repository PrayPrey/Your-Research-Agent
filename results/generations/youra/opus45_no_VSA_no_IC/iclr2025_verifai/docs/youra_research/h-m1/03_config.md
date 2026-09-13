# Config: H-M1 (SA Metric Correlation with Functional Correctness)

**Type**: MECHANISM | **Format**: Hardcoded dataclass (matches architecture's `config.py`)

Applied: No close KB match (best hit was PyTorch inductor config, similarity 0.39, not applicable) — used standard PyTorch/scipy experiment config defaults instead.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1) referenced, but green-field for config
**Status**: `h-e1/code/` does not exist on disk (confirmed in architecture doc) — no actual config classes to verify. Designing new config schema fresh.
**Config Files Found**: None
**Pattern Used**: dataclass

---

## M-1: Setup & Config [Complexity: 5, Budget: 5]

**Applied**: Standard PyTorch/scipy experiment defaults; thresholds fixed by PRD (non-tunable).

### Configuration (Python Dataclass)

```python
# code/config.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    # Timeouts
    sa_timeout_sec: int = 30       # pylint/mypy/radon subprocess timeout
    test_timeout_sec: int = 5      # per-test execution timeout

    # Paths
    results_dir: str = "results"
    figures_dir: str = "figures"
    completions_path: str = "data/completions.jsonl"  # Option A input

    # Statistical thresholds (fixed by PRD, not tunable)
    corr_threshold: float = 0.35
    alpha: float = 0.05
    min_samples: int = 500

    # Dataset
    seed: int = 42  # reproducibility for any sampling/API generation

CONFIG = Config()
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Create config.py | Define `Config` dataclass + `CONFIG` singleton as above |
| C-1-2 | Create results/figures dirs | `os.makedirs(CONFIG.results_dir, exist_ok=True)` + same for figures, called in `run.py` startup |

---

## Notes for Phase 4 Coder

- Import as `from config import CONFIG` and reference fields (e.g., `CONFIG.sa_timeout_sec`), not module-level globals — keeps it copy-paste stable if extended later.
- All other modules (`dataset.py`, `sa_tools.py`, `eval_pass1.py`, `correlate.py`) take `CONFIG` fields as function defaults per architecture's interfaces (e.g., `run_pylint(code_path, timeout=CONFIG.sa_timeout_sec)`).
- No hyperparameter grid, no ablation configs — this is a MECHANISM/correlation analysis, not a tunable model; all values are fixed per PRD/architecture, single run, single seed.
