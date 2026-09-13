# H-M2 Architecture: Domain-Specific Degradation Signal Leading Indicator Analysis

**Hypothesis ID:** H-M2
**Type:** MECHANISM (Incremental — extends H-M1)
**Date:** 2026-05-19

Applied: incremental-statistical-pipeline-pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code (Serena project selector unavailable; direct file read used)
**Analyzed Path**: `docs/youra_research/20260519_mldpr/h-m1/code/`
**Findings**: H-M1 uses flat module layout (no subdirs for core modules). Entry point `run_experiment.py` imports directly from sibling files: `data_pipeline`, `sigma_estimation`, `compression_detector`, `spearman_baseline`, `granger_causality`, `evaluate`, `visualize`. Panel schema uses `benchmark_id` (str), `quarter` (str period), `score_var_top10`, `compression_event` columns. Import path for reuse: `sys.path.insert(0, 'h-m1/code')` then direct module name imports.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| load_panel | `from data_pipeline import load_panel` | `h-m1/code/data_pipeline.py` |
| compute_quarterly_panel | `from data_pipeline import compute_quarterly_panel` | `h-m1/code/data_pipeline.py` |
| load_pwc_raw | `from data_pipeline import load_pwc_raw` | `h-m1/code/data_pipeline.py` |
| flag_compression | `from compression_detector import flag_compression` | `h-m1/code/compression_detector.py` |
| summarize_compression | `from compression_detector import summarize_compression` | `h-m1/code/compression_detector.py` |
| get_sigma_map | `from sigma_estimation import get_sigma_map` | `h-m1/code/sigma_estimation.py` |

**Verified from**: `docs/youra_research/20260519_mldpr/h-m1/code/` (actual implementation)

**Key panel columns verified**: `benchmark_id`, `task`, `dataset`, `quarter`, `submission_count`, `cumulative_count`, `score_var_top10`, `compressed`, `compression_event`

---

## File Structure

```
h-m2/code/
├── data_pipeline.py        # FR-1: H-M1 reuse + H_d column extension
├── hd_signals.py           # FR-2: CV/NLP/Tabular H_d computation
├── collapse_detector.py    # FR-3: Kendall τ > 0.90 collapse detection
├── temporal_analysis.py    # FR-4, FR-5: Signal onset + KM lead time
├── statistical_tests.py    # FR-6, FR-7: Mann-Whitney U + AUC comparison
├── ablation.py             # FR-8: Ablation variants A1-A5
├── evaluate.py             # FR-9: Mechanism verification + gate check
├── visualize.py            # FR-10: All 5 figures
└── run_experiment.py       # Entry point
h-m2/figures/
├── gate_metrics_fraction_leading.png
├── km_lead_time_curves.png
├── signal_emergence_timeline.png
├── auc_comparison.png
└── mann_whitney_boxplot.png
```

---

## Module Definitions

### DataPipeline (`h-m2/code/data_pipeline.py`)

**Dependencies**: h-m1/code/data_pipeline, h-m1/code/compression_detector, h-m1/code/sigma_estimation, hd_signals

```python
import sys
import pandas as pd

# H-M1 reuse path (set by run_experiment.py)
# sys.path.insert(0, '../h-m1/code')

DOMAIN_THRESHOLDS = {'cv': 0.5, 'nlp': 0.3, 'tabular': 0.90}

def load_hm1_panel(
    min_submissions: int = 20,
    min_quarters: int = 8,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load H-M1 panel + apply compression flags.
    Returns: (pwc_raw, panel_df) with compression_event column
    """
    ...

def filter_compressed_benchmarks(panel_df: pd.DataFrame) -> pd.DataFrame:
    """Filter to benchmarks with compression_event == 1.0 and ≥8 quarters.
    Returns: filtered panel_df
    """
    ...

def extend_panel_with_hd(
    panel_df: pd.DataFrame,
) -> pd.DataFrame:
    """Add hd_cv, hd_nlp, hd_tabular columns to panel via hd_signals.
    Returns: panel_df + [hd_cv, hd_nlp, hd_tabular]
    """
    ...
```

---

### HdSignals (`h-m2/code/hd_signals.py`)

**Dependencies**: numpy, scipy, pandas

```python
import numpy as np
import scipy.stats
import pandas as pd

DOMAIN_THRESHOLDS = {'cv': 0.5, 'nlp': 0.3, 'tabular': 0.90}

def compute_robustness_gap_cv(
    panel_df: pd.DataFrame,
    benchmark_id: str,
    rolling_quarters: int = 4,
) -> pd.DataFrame:
    """Robustness gap: rolling std of score_var_top10 for CV benchmarks.
    Returns: DataFrame[quarter, hd_cv]
    """
    ...

def compute_contamination_nlp(
    panel_df: pd.DataFrame,
    benchmark_id: str,
) -> pd.DataFrame:
    """Contamination proxy: normalized score deviation from baseline.
    Returns: DataFrame[quarter, hd_nlp]
    """
    ...

def compute_kendall_tau_tabular(
    panel_df: pd.DataFrame,
    benchmark_id: str,
    bootstrap_iters: int = 100,
    seed: int = 42,
) -> pd.DataFrame:
    """Block-bootstrapped Kendall τ rank correlation stability.
    Returns: DataFrame[quarter, hd_tabular]
    """
    ...

def compute_all_hd_signals(
    panel_df: pd.DataFrame,
) -> pd.DataFrame:
    """Dispatch per-domain H_d computation for all benchmarks.
    Returns: panel_df + [hd_cv, hd_nlp, hd_tabular]
    """
    ...
```

---

### CollapseDetector (`h-m2/code/collapse_detector.py`)

**Dependencies**: pandas, scipy, numpy

```python
import pandas as pd
import scipy.stats
import numpy as np

def detect_collapse_events(
    panel_df: pd.DataFrame,
    tau_threshold: float = 0.90,
    min_consecutive: int = 2,
) -> pd.DataFrame:
    """Identify collapse events: Kendall τ > tau_threshold for ≥2 consecutive quarters.
    Returns: DataFrame[benchmark_id, collapse_quarter]
    """
    ...

def apply_r1_mitigation(
    panel_df: pd.DataFrame,
    collapse_df: pd.DataFrame,
    min_events: int = 20,
) -> tuple[pd.DataFrame, float]:
    """If collapse events < min_events, lower tau to 0.85 and re-detect.
    Returns: (collapse_df, tau_used)
    """
    ...
```

---

### TemporalAnalysis (`h-m2/code/temporal_analysis.py`)

**Dependencies**: pandas, lifelines, CollapseDetector, HdSignals

```python
import pandas as pd
from lifelines import KaplanMeierFitter

DOMAIN_THRESHOLDS = {'cv': 0.5, 'nlp': 0.3, 'tabular': 0.90}

def compute_signal_onset_times(
    panel_df: pd.DataFrame,
    domain: str,
    compression_mask: pd.Index,
    collapse_df: pd.DataFrame,
) -> pd.DataFrame:
    """Find first quarter H_d exceeds threshold; compute lead_months to collapse.
    Returns: DataFrame[benchmark_id, lead_months, onset_observed, domain]
    """
    ...

def run_temporal_ordering_test(
    onset_df: pd.DataFrame,
    min_lead_months: int = 12,
) -> dict:
    """Kaplan-Meier lead time + fraction_leading computation.
    Returns: {'fraction_leading': float, 'median_lead_months': float, 'km_estimator': KMF}
    """
    ...

def compute_onset_for_all_domains(
    panel_df: pd.DataFrame,
    collapse_df: pd.DataFrame,
    compression_mask: pd.Index,
) -> dict[str, pd.DataFrame]:
    """Run compute_signal_onset_times for cv, nlp, tabular.
    Returns: {domain: onset_df}
    """
    ...
```

---

### StatisticalTests (`h-m2/code/statistical_tests.py`)

**Dependencies**: pandas, scipy, sklearn, numpy

```python
import pandas as pd
from scipy.stats import mannwhitneyu
from sklearn.metrics import roc_auc_score

def run_mann_whitney_test(
    panel_df: pd.DataFrame,
    domain: str,
    compressed_ids: pd.Index,
) -> dict:
    """Mann-Whitney U: H_d magnitude in compressed vs. non-compressed.
    Returns: {'mw_stat': float, 'mw_p_value': float, 'domain': str}
    """
    ...

def compute_auc_comparison(
    panel_df: pd.DataFrame,
    domain: str,
    collapse_df: pd.DataFrame,
    lead_months: int = 24,
) -> dict:
    """AUC of H_d(t-lead_months) vs H_d(t) predicting collapse label.
    Returns: {'auc_lead': float, 'auc_concurrent': float, 'domain': str}
    """
    ...

def run_all_statistical_tests(
    panel_df: pd.DataFrame,
    collapse_df: pd.DataFrame,
    compressed_ids: pd.Index,
) -> dict:
    """Run MW + AUC for all three domains.
    Returns: {domain: {'mw': dict, 'auc': dict}}
    """
    ...
```

---

### Ablation (`h-m2/code/ablation.py`)

**Dependencies**: pandas, TemporalAnalysis, StatisticalTests

```python
import pandas as pd
from temporal_analysis import run_temporal_ordering_test, compute_signal_onset_times
from statistical_tests import compute_auc_comparison

ABLATION_VARIANTS = {
    'A1': {'description': 't-24mo offset', 'lead_months': 24},
    'A2': {'description': 't-12mo offset', 'lead_months': 12},
    'A3': {'description': 't offset (concurrent)', 'lead_months': 0},
    'A4': {'description': 'compression-filtered only', 'lead_months': 24, 'use_compression_filter': True},
    'A5': {'description': 'all benchmarks', 'lead_months': 24, 'use_compression_filter': False},
}

def run_ablation_variant(
    panel_df: pd.DataFrame,
    collapse_df: pd.DataFrame,
    variant_key: str,
    compressed_ids: pd.Index,
) -> dict:
    """Run single ablation variant; returns metrics dict.
    Returns: {'variant': str, 'fraction_leading': float, 'auc': dict, ...}
    """
    ...

def run_all_ablations(
    panel_df: pd.DataFrame,
    collapse_df: pd.DataFrame,
    compressed_ids: pd.Index,
) -> list[dict]:
    """Run A1–A5 ablation variants.
    Returns: list of per-variant metric dicts
    """
    ...
```

---

### Evaluate (`h-m2/code/evaluate.py`)

**Dependencies**: pandas, TemporalAnalysis, StatisticalTests

```python
import pandas as pd

def verify_mechanism_activated(
    onset_df: pd.DataFrame,
    km_results: dict,
    results: dict,
) -> tuple[bool, dict]:
    """Check all 5 mechanism activation indicators.
    Returns: (all_activated: bool, indicators: dict)
    """
    ...

def check_gate_condition(
    domain_km_results: dict,
    stat_results: dict,
    min_fraction: float = 0.60,
    min_domains: int = 2,
) -> tuple[bool, dict]:
    """SHOULD_WORK gate: fraction_leading >= 0.60 in >= 2 domains.
    Returns: (gate_passed: bool, gate_details: dict)
    """
    ...

def save_results(
    results: dict,
    results_json: str,
    results_csv: str,
) -> None:
    """Persist results dict to JSON + CSV."""
    ...
```

---

### Visualize (`h-m2/code/visualize.py`)

**Dependencies**: matplotlib, seaborn, lifelines, pandas

```python
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def plot_gate_metrics(
    domain_results: dict,
    output_dir: str,
    threshold: float = 0.60,
) -> None:
    """Bar chart: fraction_leading per domain vs. 0.60 threshold. [MANDATORY]"""
    ...

def plot_km_curves(
    domain_onset_dfs: dict,
    output_dir: str,
) -> None:
    """Kaplan-Meier lead time curves per domain (CV, NLP, Tabular)."""
    ...

def plot_signal_timeline(
    panel_df: pd.DataFrame,
    collapse_df: pd.DataFrame,
    benchmark_ids: list[str],
    output_dir: str,
) -> None:
    """Aligned time series for representative benchmarks (MMLU, CIFAR-10, SQuAD)."""
    ...

def plot_auc_comparison(
    auc_results: dict,
    output_dir: str,
) -> None:
    """AUC bar chart: H_d(t-24mo) vs H_d(t-12mo) vs H_d(t) per domain."""
    ...

def plot_mann_whitney_boxplot(
    panel_df: pd.DataFrame,
    compressed_ids: pd.Index,
    output_dir: str,
) -> None:
    """Boxplot: H_d magnitude in compressed vs. non-compressed per domain."""
    ...

def generate_all_figures(
    panel_df: pd.DataFrame,
    collapse_df: pd.DataFrame,
    domain_onset_dfs: dict,
    domain_km_results: dict,
    stat_results: dict,
    ablation_results: list[dict],
    output_dir: str,
) -> None:
    """Orchestrate all 5 figure outputs."""
    ...
```

---

### RunExperiment (`h-m2/code/run_experiment.py`)

**Dependencies**: all modules above

```python
import argparse
import os
import sys
import numpy as np

CONFIG = {
    "seed": 42,
    "min_submissions": 20,
    "min_quarters": 8,
    "tau_threshold": 0.90,
    "min_consecutive": 2,
    "min_lead_months": 12,
    "min_collapse_events": 20,
    "domains": ["cv", "nlp", "tabular"],
    "domain_thresholds": {"cv": 0.5, "nlp": 0.3, "tabular": 0.90},
    "bootstrap_iters": 100,
    "significance_level": 0.05,
    "gate_fraction_threshold": 0.60,
    "gate_min_domains": 2,
    "hm1_code_path": "../h-m1/code",
    "output_dir": "../figures",
    "results_json": "../results.json",
    "results_csv": "outputs/results.csv",
    "figure_dpi": 150,
}

def parse_args(config: dict, args=None) -> dict: ...

def main(args=None) -> None:
    """
    Steps:
      1. Load H-M1 panel + compression flags
      2. Compute H_d signals (hd_cv, hd_nlp, hd_tabular)
      3. Detect collapse events (+ R1 mitigation if < 20)
      4. Compute signal onset times per domain
      5. Run temporal ordering tests (KM)
      6. Run statistical tests (MW U + AUC)
      7. Run ablation variants A1-A5
      8. Verify mechanism activation
      9. Check gate condition
      10. Generate figures
      11. Save results
    """
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data Pipeline Setup | Reuse H-M1 panel loading + compression flags; add domain column passthrough; extend with hd_ columns stub | 8 | 2+2+2+2 |
| A-2 | H_d Signal Computation | Implement hd_signals.py: CV robustness gap (rolling std), NLP contamination proxy (normalized deviation), Tabular block-bootstrap Kendall τ | 14 | 4+2+4+4 |
| A-3 | Collapse Event Detection | Implement collapse_detector.py: Kendall τ expanding apply, ≥2 consecutive logic, R1 mitigation (lower τ to 0.85) | 12 | 3+2+4+3 |
| A-4 | Temporal Analysis + KM | Implement temporal_analysis.py: signal onset times per domain, lead_months computation, KaplanMeierFitter fitting, fraction_leading | 15 | 4+3+4+4 |
| A-5 | Statistical Tests | Implement statistical_tests.py: Mann-Whitney U (compressed vs non-compressed), AUC comparison (t-24mo vs t) for all 3 domains | 12 | 3+3+3+3 |
| A-6 | Ablation Variants A1-A5 | Implement ablation.py: 5 ablation configs (temporal offset + compression filter variants), results aggregation | 13 | 3+3+4+3 |
| A-7 | Evaluate + Gate Check | Implement evaluate.py: 5-indicator mechanism activation check, SHOULD_WORK gate (fraction_leading ≥ 0.60 in ≥2 domains), result serialization | 10 | 2+2+3+3 |
| A-8 | Visualization | Implement visualize.py: 5 figures (gate bar, KM curves, timeline, AUC comparison, MW boxplot) | 11 | 2+2+4+3 |
| A-9 | Entry Point + Config | Implement run_experiment.py: 11-step orchestration, argparse config, H-M1 sys.path injection, reproducibility (seed=42) | 9 | 2+3+2+2 |
| A-10 | Smoke Test | Verify pipeline runs end-to-end on panel subset; assert onset_df shape, KM fits, gate output present | 7 | 2+1+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-2, A-4], Medium(9-13): [A-3, A-5, A-6, A-7, A-8, A-9], Low(4-8): [A-1, A-10]

---

## Data Flow

- `run_experiment.py` → `data_pipeline.load_hm1_panel()` → `data_pipeline.extend_panel_with_hd()` → `panel_df`
- `panel_df` → `collapse_detector.detect_collapse_events()` → `collapse_df`
- `panel_df` + `collapse_df` → `temporal_analysis.compute_onset_for_all_domains()` → `domain_onset_dfs`
- `domain_onset_dfs` → `temporal_analysis.run_temporal_ordering_test()` → `domain_km_results`
- `panel_df` + `collapse_df` → `statistical_tests.run_all_statistical_tests()` → `stat_results`
- All → `ablation.run_all_ablations()` → `ablation_results`
- All → `evaluate.verify_mechanism_activated()` + `evaluate.check_gate_condition()` → gate verdict
- All → `visualize.generate_all_figures()` → `h-m2/figures/*.png`

---

## H-M1 Import Pattern (Verified)

```python
import sys
import os
_HM1_CODE = os.path.join(os.path.dirname(__file__), '..', '..', 'h-m1', 'code')
sys.path.insert(0, os.path.abspath(_HM1_CODE))

from data_pipeline import load_pwc_raw, compute_quarterly_panel, load_panel
from compression_detector import flag_compression, summarize_compression
from sigma_estimation import get_sigma_map
```
