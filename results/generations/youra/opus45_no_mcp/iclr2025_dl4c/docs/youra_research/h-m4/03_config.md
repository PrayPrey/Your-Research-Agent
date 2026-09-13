# Configuration: H-M4 — Gating Removes Noise, Improves Signal

**Type:** MECHANISM | **Format:** Dataclass (Python)

Applied: snr-comparison-config-pattern

---

## Codebase Analysis

**Project Type**: incremental_hypothesis (base: H-M3)
**Status**: config patterns verified from H-M3 code
**Pattern Used**: dataclass (nested via `field(default_factory=...)`)

H-M4 imports sample collection and noise analysis from H-M3. New config for SNR computation and statistical tests.

---

## Inherited Configuration (Base Hypothesis H-M3)

```python
# From: h-m3/code/config.py (reuse via import)
SEED = 42
MODEL_NAME = "Salesforce/codet5-small"
N_PER_CATEGORY = 250  # H-M4 uses 250 each for balanced comparison

# From: h-m3/code/sample_builder.py
@dataclass
class NoiseSample:
    code: str
    traceback: str
    error_type: str
    traceback_line: int
    ground_truth_line: int
```

**Verified from**: `h-m3/code/` validated implementation.

---

## A-1: Config setup [Complexity: 3, Budget: 3]

### Configuration (Python Dataclass)

```python
"""Configuration for H-M4 SNR comparison experiment."""
from dataclasses import dataclass, field
import sys, os

# sys.path wiring to base hypothesis
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../h-m3/code'))

from config import SEED, MODEL_NAME, H_M3_Config

N_SAMPLES = 500  # 250 U_line + 250 U_ignore


@dataclass
class BootstrapConfig:
    n_bootstrap: int = 1000
    confidence_level: float = 0.95
    seed: int = SEED


@dataclass
class PermutationConfig:
    n_permutation: int = 9999
    significance_threshold: float = 0.05


@dataclass
class VizConfig:
    style: str = "seaborn-v0_8-whitegrid"
    dpi: int = 150
    snr_comparison_path: str = "figures/snr_comparison.png"
    bootstrap_dist_path: str = "figures/snr_bootstrap_distribution.png"
    scatter_path: str = "figures/signal_noise_scatter.png"
    contribution_path: str = "figures/error_type_contribution.png"


@dataclass
class H_M4_Config:
    seed: int = SEED
    n_samples: int = N_SAMPLES
    n_per_category: int = 250
    bootstrap: BootstrapConfig = field(default_factory=BootstrapConfig)
    permutation: PermutationConfig = field(default_factory=PermutationConfig)
    viz: VizConfig = field(default_factory=VizConfig)
    output_dir: str = "results"
    figures_dir: str = "figures"


def get_config() -> H_M4_Config:
    return H_M4_Config()
```

### Subtasks [3/3 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | H_M4_Config dataclass | bootstrap/permutation/viz nested configs |
| C-1-2 | sys.path wiring | insert h-m3/code before H-M3 imports |
| C-1-3 | dirs bootstrap | os.makedirs for output_dir/figures_dir |

---

## A-2: SNR analysis core [Complexity: 8, Budget: 8]

**Applied**: no new config beyond inherited — uses H-M3's NoiseConfig for penalty values

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-2-1 | SNRResult dataclass | Store snr, mean_signal, mean_noise, n_samples, lists |
| C-2-2 | extract_signal_noise | Parse gt_grad as signal, other_grad as noise |
| C-2-3 | compute_policy_snr | Aggregate to mean signal / mean noise |
| C-2-4 | compare_policies | Return dict with fine_always and fine_gated SNRResults |

---

## A-3: Statistical tests [Complexity: 7, Budget: 7]

**Applied**: `BootstrapConfig` and `PermutationConfig` (A-1)

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-3-1 | bootstrap_snr_ci | Use `bootstrap.n_bootstrap=1000` resamples |
| C-3-2 | permutation_test | Use `permutation.n_permutation=9999` shuffles |
| C-3-3 | compute_improvement | (gated - always) / always * 100 |
| C-3-4 | summary_stats | Aggregate all into results dict |

---

## A-4: Visualization suite [Complexity: 8, Budget: 8]

**Applied**: `VizConfig` (A-1)

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-4-1 | plot_snr_comparison | Bar chart -> `viz.snr_comparison_path` |
| C-4-2 | plot_snr_bootstrap_distribution | Boxplot -> `viz.bootstrap_dist_path` |
| C-4-3 | plot_signal_noise_scatter | Scatter -> `viz.scatter_path` |
| C-4-4 | plot_error_type_contribution | Stacked bar -> `viz.contribution_path` |

---

## A-5: End-to-end pipeline [Complexity: 5, Budget: 5]

**Applied**: `H_M4_Config.output_dir`/`figures_dir` (A-1)

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-5-1 | Load model/tokenizer | `AutoModel`/`AutoTokenizer.from_pretrained(MODEL_NAME)` |
| C-5-2 | Sample collection | Call H-M3 `collect_stratified_samples(n_per_category=250)` |
| C-5-3 | Run analysis | Call H-M3 `run_noise_analysis`, then `compare_policies` |
| C-5-4 | Dump results | Write `output_dir/metrics.json` |

---

## A-6: Validation run [Complexity: 4, Budget: 4]

**Applied**: uses `get_config()` defaults

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-6-1 | Full run | Execute `run_experiment.py::main()` on 500 samples |
| C-6-2 | Check PoC criteria | SNR_gated > SNR_always, p < 0.05 |
| C-6-3 | Check 95% CI | Verify non-overlapping intervals |
| C-6-4 | Sanity-check figures | Confirm all 4 PNGs generated |
