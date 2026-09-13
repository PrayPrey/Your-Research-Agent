# H-M3 Configuration

Applied: module-level constants pattern (H-M2 convention for fixed statistical parameters)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends H-M2)
**Status**: H-M2 config verified from actual `03_config.md` and architecture. H-M3 inherits path conventions; replaces BF-test params with moment/directional-test constants.
**Config Files Found**: `h-m2/03_config.md` (dataclass `H_M2_Config`); H-M3 uses module-level constants — no hyperparameter grid, all values fixed by statistical convention or prior hypothesis.
**Pattern Used**: module-level constants (hardcoded dict in `main.py`; dataclass only for `SegmentMoments` output type)

---

## Inherited Configuration (Base Hypothesis)

```python
# Verified from h-m2/03_config.md — H_M2_Config actual fields:
alpha: float = 0.05
variance_ratio_threshold: float = 1.0
min_segment_size: int = 3
center: str = "median"
random_seed: int = 42
figures_dir: str = "docs/youra_research/h-m2/figures"
results_json_path: str = "docs/youra_research/h-m2/results/h_m2_results.json"
h_m1_results_path: str = "docs/youra_research/h-m1/results/coverage_report.json"
figure_dpi: int = 150
figure_size: tuple = (8.0, 5.0)
```

H-M3 carries forward: `random_seed → RANDOM_STATE`, `figure_dpi`, `figure_size`, `min_segment_size → 3 (implicit in data_loader)`.
H-M3 replaces: BF-test params (`alpha`, `variance_ratio_threshold`, `center`) with directional-test params.

---

## A-2: distributional_moments.py [Complexity: Low, Budget: 1 subtask]

### Configuration

```python
# distributional_moments.py — module-level constants
SKEW_BIAS: bool = False       # Non-standard: adjusted Fisher-Pearson G1 for small N
PERCENTILE_LOWER: int = 10    # 10th percentile for lower-tail test (metric 2)

@dataclass
class SegmentMoments:
    n: int
    mean: float
    variance: float
    skewness: float
    kurtosis: float
    p10: float    # np.percentile(segment, 10)
    p25: float    # np.percentile(segment, 25)
    p75: float    # np.percentile(segment, 75)

def compute_moments(segment: np.ndarray) -> SegmentMoments:
    # Raises ValueError if len(segment) < 3
    # Raises ValueError if len(segment) == 0
    # Uses scipy.stats.describe(segment, bias=False)
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | SegmentMoments + compute_moments | Dataclass fields, bias=False enforcement, input validation (empty, <3), compute_both_segments split logic |

---

## A-8: tests/test_h_m3.py [Complexity: Medium, Budget: 2 subtasks]

### Configuration

```python
# tests/test_h_m3.py — test constants
import numpy as np

# Known-input fixtures
ONES_ARRAY = np.ones(20)           # skewness == 0, variance == 0
HIGH_VAR_RIGHT_SKEWED = np.array(  # pre-segment: high variance, right-skewed
    [0.01, 0.02, 0.02, 0.03, 0.05, 0.08, 0.15, 0.30, 0.60, 1.20,
     2.50, 4.00, 6.00, 8.00, 10.0, 12.0, 15.0, 18.0, 22.0, 28.0]
)
LOW_VAR_CONCENTRATED_LOW = np.array(  # post-segment: low variance, concentrated low
    [0.01, 0.01, 0.02, 0.02, 0.02, 0.03, 0.03, 0.03, 0.04, 0.04,
     0.04, 0.05, 0.05, 0.05, 0.06, 0.06, 0.06, 0.07, 0.07, 0.08]
)
# Expected gate: metric1 PASS (skew_post < skew_pre), metric2 PASS (p10_post < p10_pre)
# metric3/4 depend on permutation/MW — at least 2/4 should pass with these arrays

N_RESAMPLES_TEST: int = 999    # Non-standard: reduced for test speed (vs 9999 in prod)
RANDOM_STATE: int = 42
P_THRESHOLD: float = 0.10
METRICS_GATE: int = 2
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | test_distributional_moments | `test_compute_moments_ones` (skewness==0, variance==0, n==20); `test_compute_moments_validates_empty` (ValueError); `test_compute_moments_validates_too_short` (n<3 → ValueError); `test_bias_false_enforced` (compare bias=True vs bias=False skewness differ for small N) |
| C-8-2 | test_directional_tests | `test_gate_passes_with_synthetic_data` (HIGH_VAR_RIGHT_SKEWED pre, LOW_VAR_CONCENTRATED_LOW post → metrics_passed >= 2); `test_metric1_skew_direction` (verify skew_post < skew_pre); `test_metric2_p10` (verify p10_post < p10_pre); `test_gate_result_type` (GateResult.gate_passed is bool) |

---

## Experiment Constants (main.py / shared)

```python
# Paste into main.py or a shared constants.py
N_EXPECTED: int = 111          # H-E1 validated dataset size
P_THRESHOLD: float = 0.10      # SHOULD_WORK gate threshold
METRICS_GATE: int = 2          # minimum metrics to pass gate
N_RESAMPLES: int = 9999        # permutation_test resamples
RANDOM_STATE: int = 42         # reproducibility seed
SKEW_BIAS: bool = False        # adjusted Fisher-Pearson G1 (non-standard: corrects for small N)
PERCENTILE_LOWER: int = 10     # lower-tail percentile for metric 2
```
