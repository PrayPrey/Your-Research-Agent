# Configuration: H-M2 BAI-Reward Disagreement Analysis

**Type:** MECHANISM (fixed config, no hyperparameter sweep)
**Applied:** No matching KB pattern found — used standard hardcoded-dict-style config matching h-e1 codebase convention.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: config classes verified from base code (`h-e1/code/config.py`)
**Config Files Found**: `h-e1/code/config.py` (module-level constants, no dataclass)
**Pattern Used**: Module-level constants (dict-style), not dataclass — matching h-e1 convention for consistency.

---

## Inherited Configuration (Base Hypothesis)

Verified from `h-e1/code/config.py` (actual code, module-level constants — no dataclass used in h-e1):

```python
# From: h-e1/code/config.py (ACTUAL CODE)
RANDOM_STATE = 42

TFIDF_PARAMS = dict(
    ngram_range=(1, 2),
    max_features=5000,
)

LOGREG_PARAMS = dict(
    C=1.0,
    max_iter=1000,
    random_state=RANDOM_STATE,
)

PROXY_TYPES = [
    "clarifying_question",
    "option_enumeration",
    "epistemic_hedging",
    "explicit_deferral",
]
# PROXY_PATTERNS: dict[str, list[str]] — regex patterns per proxy type (see h-e1/code/config.py:21-67)
```

H-M2 imports these directly via `sys.path.insert` (see 03_architecture.md) rather than re-declaring — `RANDOM_STATE`, `TFIDF_PARAMS`, `LOGREG_PARAMS`, `PROXY_TYPES` used as-is from `h_e1.config`.

---

## H-M2 Configuration (`h-m2/code/config.py`)

Module-level constants, mirrors h-e1 style (no dataclass):

```python
RANDOM_STATE = 42

REWARD_MODEL_NAME = "OpenAssistant/reward-model-deberta-v3-large-v2"
MAX_TOKENS = 512
BATCH_SIZE = 32

LENGTH_NORM_COEF = 0.1

DISAGREEMENT_THRESHOLD = 0.20   # PASS gate
PARTIAL_THRESHOLD = 0.10        # PARTIAL gate (below = FAIL)
MIN_SAMPLE_COUNT = 500

FIGURES_DIR = "h-m2/figures"
```

All values taken directly from PRD success criteria (FR-4 thresholds, FR-2 length-norm coefficient, NFR-1 batch size) — no tuning needed for this MECHANISM analysis.

### Subtasks

None — Budget is 0 subtasks; all 10 epic tasks (B-1..B-10) are Low complexity per architecture allocation table.

---

## Self-Validation

- [x] ONE format only: module-level constants (dict-style), matches h-e1 convention
- [x] No ASCII diagrams
- [x] Archon KB searched — no match, noted
- [x] Rationale given only for non-obvious choices (thresholds sourced from PRD)
- [x] 0 subtasks used (budget: 0)
- [x] Codebase Analysis (Serena) section included
- [x] Inherited Configuration section included with verified h-e1 field names
