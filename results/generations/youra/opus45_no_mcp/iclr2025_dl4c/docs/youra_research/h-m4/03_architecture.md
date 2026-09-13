# Architecture: H-M4 — Gating Removes Noise, Improves Signal

**Type:** MECHANISM | **Prerequisites:** H-M3 (VALIDATED)

Applied: snr-aggregate-comparison-pattern (compare aggregate metrics between policies)
Applied: policy-gradient-attribution-pattern (reuse H-M1/H-M3 gradient extraction)

---

## Codebase Analysis

**Project Type**: incremental_hypothesis (base: H-M3)
**Status**: patterns found from H-M3 code
**Analyzed Path**: `h-m3/code/`
**Findings**:
- H-M3 `noise_analysis.py` computes per-sample gt_grad, tb_grad, gt_concentration, noise_ratio
- H-M3 `sample_builder.py` provides NoiseSample dataclass and stratified collection
- H-M3 `run_noise_analysis` returns stratified results: {"u_line": [...], "u_ignore": [...]}
- H-M4 needs: aggregate these per-sample metrics into per-policy SNR

---

## External Dependencies (Base Hypothesis)

### Module Paths (From H-M3)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| NoiseSample | `from sample_builder import NoiseSample` | `h-m3/code/sample_builder.py` |
| collect_stratified_samples | `from sample_builder import collect_stratified_samples` | `h-m3/code/sample_builder.py` |
| measure_sample_noise | `from noise_analysis import measure_sample_noise` | `h-m3/code/noise_analysis.py` |
| run_noise_analysis | `from noise_analysis import run_noise_analysis` | `h-m3/code/noise_analysis.py` |
| H_M3_Config | `from config import H_M3_Config, get_config` | `h-m3/code/config.py` |

**Verified from**: H-M3/code/ validated implementation.

---

## Module Structure

### snr_analysis.py (`h-m4/code/snr_analysis.py`)

**Dependencies**: noise_analysis (H-M3)

```python
@dataclass
class SNRResult:
    snr: float
    mean_signal: float
    mean_noise: float
    n_samples: int
    signals: List[float]
    noises: List[float]

def compute_policy_snr(
    results: List[Dict[str, float]], policy: str
) -> SNRResult:
    """Compute aggregate SNR for a policy (fine_always or fine_gated)."""
    ...

def compare_policies(
    u_line_results: List[Dict], u_ignore_results: List[Dict]
) -> Dict[str, SNRResult]:
    """Returns {"fine_always": SNRResult, "fine_gated": SNRResult}."""
    ...
```

### stats_tests.py (`h-m4/code/stats_tests.py`)

**Dependencies**: scipy.stats, numpy

```python
def bootstrap_snr_ci(
    signals: List[float], noises: List[float], n_boot: int = 1000
) -> Tuple[float, float]:
    """95% CI for SNR via bootstrap."""
    ...

def permutation_test(
    snr_gated: SNRResult, snr_always: SNRResult, n_perm: int = 9999
) -> float:
    """Permutation test for SNR difference."""
    ...

def compute_improvement(snr_gated: float, snr_always: float) -> float:
    """Percentage improvement."""
    ...
```

### visualization.py (`h-m4/code/visualization.py`)

**Dependencies**: matplotlib, seaborn, numpy

```python
def plot_snr_comparison(snr_always: SNRResult, snr_gated: SNRResult, path: str) -> None: ...
def plot_snr_bootstrap_distribution(always_dist: List[float], gated_dist: List[float], path: str) -> None: ...
def plot_signal_noise_scatter(results: Dict[str, List[Dict]], path: str) -> None: ...
def plot_error_type_contribution(u_line: List[Dict], u_ignore: List[Dict], path: str) -> None: ...
```

### config.py (`h-m4/code/config.py`)

```python
SEED = 42
MODEL_NAME = "Salesforce/codet5-small"
N_SAMPLES = 500  # 250 U_line + 250 U_ignore

@dataclass
class H_M4_Config:
    seed: int = SEED
    n_bootstrap: int = 1000
    n_permutation: int = 9999
    significance_threshold: float = 0.05
    output_dir: str = "results"
    figures_dir: str = "figures"
```

### run_experiment.py (`h-m4/code/run_experiment.py`)

**Dependencies**: all above modules, H-M3 modules

```python
def main() -> None:
    """Load model -> collect samples (via H-M3) -> run_noise_analysis (H-M3) ->
    compare_policies -> statistical tests -> generate figures -> dump metrics.json."""
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config setup | h-m4 config.py, sys.path wiring to h-m3 | 3 | 1+1+1+0 |
| A-2 | SNR analysis core | compute_policy_snr, compare_policies | 8 | 2+3+2+1 |
| A-3 | Statistical tests | bootstrap_snr_ci, permutation_test | 7 | 2+2+2+1 |
| A-4 | Visualization suite | 4 required figures | 8 | 2+2+2+2 |
| A-5 | End-to-end pipeline | run_experiment.py orchestration | 5 | 1+2+1+1 |
| A-6 | Validation run | execute pipeline, verify PoC criteria | 4 | 1+1+1+1 |

**Distribution**: VeryHigh: [], High: [], Medium(9-13): [A-2], Low(4-8): [A-1, A-3, A-4, A-5, A-6]

**Total Tasks:** 6 epics (within FULL tier budget of 30)
