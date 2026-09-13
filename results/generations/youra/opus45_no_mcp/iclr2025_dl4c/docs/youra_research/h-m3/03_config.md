# Configuration: H-M3 — Unreliable Localization Causes Gradient Noise

**Type:** MECHANISM | **Format:** Dataclass (Python)

Applied: mechanism-hypothesis-stratified-comparison-config-pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (dual: H-M1 + H-M2)
**Status**: config classes verified from base code
**Config Files Found**: `h-m1/code/config.py`, `h-m2/code/config.py`
**Pattern Used**: dataclass (nested via `field(default_factory=...)`)

Both bases share `SEED=42`, `U_LINE_ERRORS`/`U_IGNORE_ERRORS` sets, dataclass-of-dataclasses pattern. H-M3 imports `U_LINE_ERRORS`/`U_IGNORE_ERRORS` from **H-M2** (per PRD/architecture), and reuses H-M1's `MODEL_NAME`, `MAX_INPUT_LEN`, `MAX_OUTPUT_LEN` (not present in H-M2, must be redefined here).

---

## Inherited Configuration (Base Hypotheses)

```python
# From: h-m1/code/config.py (ACTUAL CODE)
MODEL_NAME = "Salesforce/codet5-small"
MAX_INPUT_LEN = 512
MAX_OUTPUT_LEN = 256

# From: h-m2/code/config.py (ACTUAL CODE) — H-M3 imports these directly
U_LINE_ERRORS = {'SyntaxError', 'IndentationError', 'NameError', 'TypeError',
                  'AttributeError', 'ZeroDivisionError', 'IndexError',
                  'KeyError', 'ValueError'}
U_IGNORE_ERRORS = {'AssertionError', 'RuntimeError', 'TimeoutError',
                    'RecursionError', 'MemoryError'}
```

**Verified from**: `h-m1/code/config.py`, `h-m2/code/config.py` (actual implementation).

---

## A-1: Config setup [Complexity: 4, Budget: 4]

**Applied**: dataclass-of-dataclasses (matches H-M1/H-M2 pattern for consistency)

### Configuration (Python Dataclass)

```python
"""Configuration for H-M3 gradient noise analysis."""
from dataclasses import dataclass, field
import sys, os

# sys.path wiring to base hypotheses (idiom reused from H-M1/H-M2)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../h-m1/code'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../h-m2/code'))

from config import U_LINE_ERRORS, U_IGNORE_ERRORS  # from h-m2/code/config.py

SEED = 42
MODEL_NAME = "Salesforce/codet5-small"  # ponytail: small for PoC, codet5-large for full
MAX_INPUT_LEN = 512
MAX_OUTPUT_LEN = 256
N_PER_CATEGORY = 500


@dataclass
class SamplesConfig:
    n_per_category: int = N_PER_CATEGORY
    seed: int = SEED
    dataset_name: str = "codeparrot/apps"
    dataset_split: str = "train"
    use_synthetic_fallback: bool = True


@dataclass
class NoiseConfig:
    target_penalty: float = -1.0     # reused from H-M1 reward vector convention
    other_penalty: float = -0.1
    normalize_by_line_length: bool = True
    eps: float = 1e-8


@dataclass
class StatsConfig:
    significance_threshold: float = 0.05
    confidence_level: float = 0.95
    bootstrap_n: int = 10000
    effect_size_medium: float = 0.5


@dataclass
class VizConfig:
    style: str = "seaborn-v0_8-whitegrid"
    dpi: int = 150
    boxplot_path: str = "figures/concentration_boxplot.png"
    histogram_path: str = "figures/noise_ratio_histogram.png"
    heatmap_path: str = "figures/gradient_heatmap.png"
    scatter_path: str = "figures/concentration_vs_noise_scatter.png"


@dataclass
class H_M3_Config:
    seed: int = SEED
    samples: SamplesConfig = field(default_factory=SamplesConfig)
    noise: NoiseConfig = field(default_factory=NoiseConfig)
    stats: StatsConfig = field(default_factory=StatsConfig)
    viz: VizConfig = field(default_factory=VizConfig)
    output_dir: str = "results"
    figures_dir: str = "figures"


def get_config():
    return H_M3_Config()
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | config.py + sys.path wiring | Write config.py, verify imports from h-m1/h-m2 resolve |

---

## A-2: Sample builder (real) [Complexity: 15, Budget: 15]

**Applied**: standard sample-collection defaults, no extra config beyond `SamplesConfig` (A-1)

Uses `SamplesConfig.n_per_category=500`, `SamplesConfig.seed=42`, `U_LINE_ERRORS`/`U_IGNORE_ERRORS` (H-M2), H-M1's `execute_code_safely`/`classify_error`, H-M2's `find_bug_line_ast`.

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-2-1 | load_apps_dataset | Load `codeparrot/apps` split, filter executable samples |
| C-2-2 | Execute + classify | Run H-M1 `execute_code_safely`, `classify_error` per sample |
| C-2-3 | Ground truth annotation | Call H-M2 `find_bug_line_ast` per sample -> `ground_truth_line` |
| C-2-4 | Stratify + balance | Bucket into U_line/U_ignore via config sets, cap at 500 each |

---

## A-3: Sample builder (synthetic fallback) [Complexity: 6, Budget: 6]

**Applied**: reuse `SamplesConfig.use_synthetic_fallback` flag (A-1), no new config

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-3-1 | Extend H-M1 templates | Add `ground_truth_line` field to synthetic sample templates |
| C-3-2 | Generate U_line synthetic | 500 synthetic samples, traceback == ground truth |
| C-3-3 | Generate U_ignore synthetic | 500 synthetic samples, traceback != ground truth |
| C-3-4 | Wire fallback trigger | Invoke when real APPS collection yields insufficient samples |

---

## A-4: Noise analysis core [Complexity: 13, Budget: 13]

**Applied**: `NoiseConfig` (A-1) drives reward vector construction; reuses H-M1 `extract_token_gradients` signature verbatim

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-4-1 | build_reward_vector | target_line -> `NoiseConfig.target_penalty`, else `other_penalty` |
| C-4-2 | measure_sample_noise (gt) | Compute gt_grad, gt_concentration via H-M1 `aggregate_gradients_by_line` |
| C-4-3 | measure_sample_noise (tb/other) | Compute tb_grad, other_grad, noise_ratio, traceback_matches_gt |
| C-4-4 | Edge-case handling | Return `None` on tokenization/execution failure (skip sample) |

---

## A-5: Stratified runner [Complexity: 6, Budget: 6]

**Applied**: no new config, iterates `SamplesConfig.n_per_category` samples per stratum

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-5-1 | Iterate + dispatch | Loop samples, call `measure_sample_noise`, bucket by `error_type` |
| C-5-2 | Aggregate u_line | Collect u_line results list |
| C-5-3 | Aggregate u_ignore | Collect u_ignore results list |
| C-5-4 | Progress/logging | Log skip counts, sample counts per stratum |

---

## A-6: Statistical tests [Complexity: 8, Budget: 8]

**Applied**: `StatsConfig` (A-1) — thresholds match H-M1/H-M2 defaults (`p=0.05`, `CI=0.95`)

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-6-1 | t-test + Mann-Whitney | `compare_concentration`: independent t-test, Mann-Whitney U |
| C-6-2 | Cohen's d | Effect size between u_line/u_ignore concentration |
| C-6-3 | Bootstrap CI | `StatsConfig.bootstrap_n=10000` resamples, 95% CI |
| C-6-4 | summarize_noise_ratio | Mean/median/CI of u_ignore noise_ratio |

---

## A-7: Visualization suite [Complexity: 10, Budget: 10]

**Applied**: `VizConfig` (A-1), consistent with H-M2's `VizConfig` (style/dpi/paths)

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-7-1 | Boxplot | `plot_concentration_boxplot` -> `viz.boxplot_path` |
| C-7-2 | Histogram | `plot_noise_ratio_histogram` -> `viz.histogram_path` |
| C-7-3 | Heatmap | `plot_gradient_heatmap` (1 u_line + 1 u_ignore sample) -> `viz.heatmap_path` |
| C-7-4 | Scatter | `plot_concentration_vs_noise_scatter` -> `viz.scatter_path` |

---

## A-8: End-to-end pipeline [Complexity: 7, Budget: 7]

**Applied**: `H_M3_Config.output_dir`/`figures_dir` (A-1)

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-8-1 | Load model/tokenizer | `AutoModel`/`AutoTokenizer.from_pretrained(MODEL_NAME)` |
| C-8-2 | Orchestrate | sample_builder -> noise_analysis -> stats_tests |
| C-8-3 | Generate figures | Call all 4 visualization functions |
| C-8-4 | Dump results | Write `output_dir/metrics.json` |

---

## A-9: Validation run [Complexity: 5, Budget: 5]

**Applied**: no new config, executes `get_config()` defaults end-to-end (`n_per_category=500` -> 1000 total samples)

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-9-1 | Full run | Execute `run_analysis.py::main()` on 1000 samples |
| C-9-2 | Check PoC criteria | Verify mean GT concentration U_line > U_ignore, p<0.05 |
| C-9-3 | Check full criteria | noise_ratio(U_ignore) > 1.0, Cohen's d > 0.5 |
| C-9-4 | Sanity-check figures | Confirm all 4 PNGs generated and non-empty |
