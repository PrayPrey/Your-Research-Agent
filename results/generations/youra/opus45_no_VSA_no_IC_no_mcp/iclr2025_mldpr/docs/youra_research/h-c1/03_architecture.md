# Architecture: h-c1

**Type:** CONDITION | **Applied:** domain-stratified-correlation-pattern (Archon KB: "DL experiment architecture domain stratification" — per-domain Pearson/Spearman + Fisher z cross-domain comparison, reusing h-m1's bootstrap CorrelationAnalyzer)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-m1)
**Status**: Serena MCP unavailable; used direct Read on `h-m1/code/*.py` (equivalent manual analysis via `get_symbols_overview`-style inspection).
**Analyzed Path**: `h-m1/code/` (data.py, metrics.py, evaluate.py, train.py, config.py)
**Findings**:
- `h-m1/code/metrics.py` exposes `CorrelationAnalyzer.analyze(dnsi, gap) -> dict` (Pearson, Spearman, bootstrap CI, seeded via `np.random.default_rng`). Reused as-is for both domains — no need to reimplement per PRD's `DomainStratifiedAnalyzer` pseudo-code; call `CorrelationAnalyzer` once per domain instead.
- `h-m1/code/data.py::load_dnsi_from_h_e1()` reveals **critical deviation**: h-e1's `run_pipeline()` does NOT actually cover ImageNet/CIFAR-10/ObjectNet/HANS — h-m1 falls back to a hardcoded `SYNTHETIC_DNSI` dict for all 4 benchmarks. h-e1 integration produced no real values for these benchmarks in practice.
- **Decision**: h-c1 does not need to re-invoke h-e1's pipeline. Reuse h-m1's `SYNTHETIC_DNSI` values directly (import or copy) for the 4 known benchmarks, and add 2 new synthetic DNSI values (PAWS, ANLI) following the same "PWC-history-methodology" convention documented in h-m1/data.py comments. This avoids redundant h-e1 subprocess calls and matches actual precedent, not PRD's aspirational `dnsi: from h-e1` framing.
- `CONFIG["success_r_threshold"] = -0.4` in h-m1 — h-c1 PRD requires `|R|>0.3` (looser), so h-c1 needs its own threshold constant, not h-m1's.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| CorrelationAnalyzer | `from metrics import CorrelationAnalyzer` (copy pattern, not cross-import — h-m1/code not a package) | `h-m1/code/metrics.py` |
| SYNTHETIC_DNSI values | Hardcoded copy of 4 values (ImageNet=0.72, CIFAR-10=0.85, ObjectNet=0.55, HANS=0.45) | `h-m1/code/data.py:43-48` |

**Verified from**: `h-m1/code/` (actual implementation — h-e1 pipeline call is redundant/non-functional for these benchmarks per h-m1's own fallback).

**Note**: h-c1 copies `CorrelationAnalyzer` class into its own `metrics.py` (small, self-contained, no cross-hypothesis package imports in this codebase) rather than sys.path-hacking into h-m1/code.

---

## File Structure

```
h-c1/code/
  config.py       # GAP_DATA, DNSI_DATA (6 benchmarks), domain map, thresholds
  data.py         # build per-domain (names, dnsi, gap) arrays
  metrics.py       # CorrelationAnalyzer (copied from h-m1) + fisher_z_test()
  evaluate.py      # per-domain success check + direction consistency + gate
  train.py         # pipeline orchestration + figure generation
  results/         # output json (created at runtime)
  figures/         # output png (created at runtime)
```

---

## Modules

### config.py (`h-c1/code/config.py`)

**Dependencies**: none

```python
CONFIG = {
    "n_bootstrap": 10000,
    "seed": 42,
    "success_r_abs_threshold": 0.3,
    "ci_level": 0.95,
    "figures_dir": "figures",
    "results_dir": "results",
}

# DNSI: 4 values copied from h-m1's SYNTHETIC_DNSI fallback, 2 new (PAWS, ANLI)
# computed via same PWC-history synthetic methodology.
DNSI_DATA = {
    "ImageNet": 0.72, "CIFAR-10": 0.85, "ObjectNet": 0.55,
    "HANS": 0.45, "PAWS": 0.60, "ANLI": 0.35,
}

GAP_DATA = {
    "ImageNet": 0.125, "CIFAR-10": 0.040, "ObjectNet": 0.425,
    "HANS": 0.400, "PAWS": 0.150, "ANLI": 0.300,
}

DOMAIN_MAP = {
    "ImageNet": "vision", "CIFAR-10": "vision", "ObjectNet": "vision",
    "HANS": "nlp", "PAWS": "nlp", "ANLI": "nlp",
}
```

### data.py (`h-c1/code/data.py`)

**Dependencies**: config.py

```python
def build_domain_dataset(domain: str) -> tuple[list[str], np.ndarray, np.ndarray]:
    """Filter DNSI_DATA/GAP_DATA by DOMAIN_MAP == domain.
    Returns (names, dnsi_arr, gap_arr) sorted by name. Raises if n < 3."""
```

### metrics.py (`h-c1/code/metrics.py`)

**Dependencies**: config.py

```python
class CorrelationAnalyzer:
    """Copied from h-m1/code/metrics.py verbatim (Pearson, Spearman, bootstrap CI)."""
    def __init__(self, n_bootstrap: int = None, seed: int = None): ...
    def analyze(self, dnsi: np.ndarray, gap: np.ndarray) -> dict:
        """Returns: n, r_pearson, p_pearson, r_spearman, p_spearman,
        ci_95_lower, ci_95_upper, bootstrap_r, hypothesis_supported (|r|>0.3 & r<0)."""
    def _bootstrap_correlation(self, x: np.ndarray, y: np.ndarray) -> np.ndarray: ...

def fisher_z_test(r_a: float, n_a: int, r_b: float, n_b: int) -> dict:
    """Returns: z_difference, p_difference (two-tailed), consistent_direction: bool."""
```

### evaluate.py (`h-c1/code/evaluate.py`)

**Dependencies**: config.py, metrics.py

```python
def check_domain_pass(analysis: dict) -> bool:
    """|r_pearson| > 0.3 and r_pearson < 0."""
def check_gate(vision_analysis: dict, nlp_analysis: dict, comparison: dict) -> dict:
    """SHOULD_WORK: success = vision_pass and nlp_pass and consistent_direction.
    Returns: success, should_fail (opposite signs), vision_r, nlp_r, consistent_direction."""
def summarize(results: dict) -> dict: ...
```

### train.py (`h-c1/code/train.py`)

**Dependencies**: data.py, metrics.py, evaluate.py

```python
def generate_figures(vision: dict, nlp: dict, comparison: dict, out_dir: str) -> None:
    """1) two-panel scatter (Vision|NLP) w/ regression lines (mandatory)
       2) domain comparison bar chart w/ 95% CI error bars
       3) bootstrap distribution overlay histogram"""
def run_pipeline() -> dict:
    """Orchestrates: build_domain_dataset(vision), build_domain_dataset(nlp),
    CorrelationAnalyzer.analyze x2, fisher_z_test, check_gate, generate_figures,
    save results json. Prints [DOMAIN] activation/success/failure per brief spec."""

if __name__ == "__main__":
    results = run_pipeline()
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| C-1 | Config setup | DNSI_DATA (6 benchmarks), GAP_DATA, DOMAIN_MAP, thresholds | 4 | 1+1+1+1 |
| C-2 | Domain dataset builder | build_domain_dataset filter+sort+validate n>=3 per domain | 5 | 2+1+1+1 |
| C-3 | CorrelationAnalyzer port | copy h-m1 class, adjust success threshold to |r|>0.3 | 6 | 2+2+1+1 |
| C-4 | Fisher z-test | fisher_z_test with SE formula, two-tailed p, direction check | 6 | 2+1+2+1 |
| C-5 | Gate + evaluate | check_domain_pass, check_gate (SHOULD_WORK logic), summarize | 6 | 2+2+1+1 |
| C-6 | Two-panel scatter figure | mandatory viz, vision|nlp panels, regression+R annotation | 7 | 3+1+2+1 |
| C-7 | Comparison + bootstrap figures | bar chart w/ CI, overlaid bootstrap histograms | 6 | 3+1+1+1 |
| C-8 | Pipeline orchestration | run_pipeline wiring both domains, print [DOMAIN] logs, save json | 7 | 2+3+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [C-1, C-2, C-3, C-4, C-5, C-6, C-7, C-8]
