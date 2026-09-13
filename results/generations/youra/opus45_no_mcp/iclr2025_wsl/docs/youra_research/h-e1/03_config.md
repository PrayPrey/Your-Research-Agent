# Configuration: H-E1 (Model Zoo Dataset Validity)

**Applied**: minimal-config pattern

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field project - new config design
**Config Files Found**: None
**Pattern Used**: Hardcoded constant (no config.py)

---

## Rationale

EXISTENCE hypothesis with a single fixed statistical gate. No hyperparameter
tuning, no variations, no seeds needed (deterministic analysis). Per
architecture: "No config.py needed — single fixed threshold (10.0) hardcoded
in analysis.py per PRD." Introducing a dataclass/config file for one constant
would be unrequested abstraction.

## Configuration

Single hardcoded constant in `h-e1/code/analysis.py`:

```python
GATE_THRESHOLD = 10.0  # std(accuracy) must exceed this to PASS (PRD FR-3, Sec 6)

def validate_model_zoo_variance(accuracies: np.ndarray) -> dict:
    std = float(np.std(accuracies))
    gate_passed = std > GATE_THRESHOLD
    ...
```

No other tunable parameters (IQR outlier multiplier = standard 1.5, Shapiro-Wilk
subset cap = 5000 per PRD FR-2, both used as literals at call sites, not config).

## Environment Variables

None required. Dataset auto-downloads via `datasets.load_dataset(...)` (HF cache
default location) or direct HTTP fallback — no credentials/paths needed.

## Subtasks

0/0 config subtasks — no config module in scope (per architecture and 0 budget).
