# Config: h-m2 (Error Localization Varies by Type)

**Applied**: Standard dataclass config pattern (KB: DL experiment config patterns — dataclass with typed defaults, single source of truth per experiment).

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends h-m1)
**Status**: config classes verified from base code (`h-m1/code/config.py`, read directly)
**Config Files Found**: `h-m1/code/config.py` (dataclass pattern: `AnalysisConfig`, `GradientConfig`, `H_M1_Config`, module-level `SEED`/`U_LINE_ERRORS`/`U_IGNORE_ERRORS`)
**Pattern Used**: dataclass (module-level constants + nested dataclasses via `field(default_factory=...)`)

---

## Inherited Configuration (Base Hypothesis)

```python
# From: h-m1/code/config.py (ACTUAL CODE)
SEED = 42
MODEL_NAME = "Salesforce/codet5-small"
MAX_INPUT_LEN = 512
MAX_OUTPUT_LEN = 256
```

h-m2 does NOT reuse h-m1's `U_LINE_ERRORS`/`U_IGNORE_ERRORS` — PRD FR-2 specifies a different set (adds `ZeroDivisionError`, `ValueError` to U_line; drops `SystemExit` from ignore vs. architecture draft, matches PRD exactly). h-m2 defines its own sets below.

**Verified from**: `h-m1/code/config.py`

---

## B (all tasks): config.py

**Applied**: RLTF Appendix B categorization sets (PRD FR-2, exact match).

### Configuration (Python Dataclass)

```python
"""Configuration for H-M2 error localization analysis."""
from dataclasses import dataclass, field

SEED = 42

U_LINE_ERRORS = {'SyntaxError', 'IndentationError', 'NameError', 'TypeError',
                  'AttributeError', 'ZeroDivisionError', 'IndexError',
                  'KeyError', 'ValueError'}
U_IGNORE_ERRORS = {'AssertionError', 'RuntimeError', 'TimeoutError',
                    'RecursionError', 'MemoryError'}

TOLERANCE_LINES = 2


@dataclass
class AnalysisConfig:
    n_samples: int = 500
    min_per_category: int = 250        # NFR-2: chi-square validity floor
    tolerance_lines: int = TOLERANCE_LINES
    confidence_level: float = 0.95
    significance_threshold: float = 0.05
    spot_check_n: int = 50             # NFR-3
    seed: int = SEED


@dataclass
class SamplesConfig:
    reuse_h_m1: bool = True
    h_m1_results_dir: str = "../h-m1/results"


@dataclass
class VizConfig:
    style: str = "seaborn-v0_8"
    dpi: int = 150
    accuracy_bar_path: str = "h-m2/figures/accuracy_bar.png"
    distance_dist_path: str = "h-m2/figures/distance_distribution.png"
    exception_breakdown_path: str = "h-m2/figures/exception_breakdown.png"


@dataclass
class H_M2_Config:
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    samples: SamplesConfig = field(default_factory=SamplesConfig)
    viz: VizConfig = field(default_factory=VizConfig)
    output_dir: str = "h-m2/results"
    figures_dir: str = "h-m2/figures"


def get_config():
    return H_M2_Config()
```

### Subtasks [0/0 used]

No subtask decomposition — 0-subtask budget (Low complexity per architecture; config file itself is a single-file, single-pass task covered under B-1/B-3 in architecture epic breakdown).

---

## Self-Validation

- [x] ONE format only (dataclass, matches h-m1 pattern)
- [x] No ASCII diagrams
- [x] "Applied" line present, no KB search logs
- [x] Rationale only for non-standard fields (`min_per_category`, `spot_check_n`)
- [x] Subtask count within budget (0/0)
- [x] Codebase Analysis (Serena) section included
- [x] Inherited Configuration section included, field names verified from actual h-m1 code
- [x] Length < 400 lines
