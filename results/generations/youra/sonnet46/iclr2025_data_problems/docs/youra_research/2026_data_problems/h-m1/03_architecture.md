# H-M1 Architecture: Conditional Log-Odds Demographic-Occupation Analysis

**Hypothesis:** H-M1 (MECHANISM — Causal Step 1: Corpus → Log-Odds)
**Base Hypothesis:** H-E1 (COMPLETED, PASS)
**Generated:** 2026-03-14

Applied: corpus-statistical-analysis-pipeline
Applied: spearman-gate-evaluation-pattern
Applied: h-e1-incremental-extension-pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1 code analyzed)
**Status**: patterns found from base code
**Analyzed Path**: `h-e1/code/`
**Findings**: H-E1 uses flat module structure — CorpusFilter, EntropyMeasure, StatisticalTests, Visualizer, run_experiment.py all in one directory. `load_corpus(config_id, data_dir)` reads from `{data_dir}/corpora/{config_id}.jsonl`. CONFIG dict (not dataclass) with absolute paths. `build_all_corpora()` references `from config import CONFIG` (local import). H-M1 must use `sys.path.insert` to import h-e1 modules.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| CorpusFilter | `from corpus_filter import CorpusFilter` (after sys.path insert) | `h-e1/code/corpus_filter.py` |
| CONFIG (h-e1) | `from config import CONFIG` (after sys.path insert) | `h-e1/code/config.py` |
| EntropyMeasure | `from entropy_measure import EntropyMeasure` (after sys.path insert) | `h-e1/code/entropy_measure.py` |

**Verified from**: `h-e1/code/` (actual implementation)

**Critical findings:**
- `load_corpus(config_id, data_dir)` reads `{data_dir}/corpora/{config_id}.jsonl`
- H-E1 data_dir: `/home/anonymous/YouRA_results_new_4/TEST_data_problems/docs/youra_research/20260315_data_problems/h-e1/data`
- H-E1 `window_size=10` (not 5 as PRD states — trust actual code)
- H-E1 CONFIG has `occupation_lexicon` (60 tokens) and `demographic_lexicon` (30 tokens)
- `CorpusFilter.__init__(fasttext_model_path, seed=42)` — fasttext path required but lazy-loaded

---

## File Organization

```
h-m1/
  code/
    config.py
    log_odds.py
    statistical_tests.py
    visualize.py
    run_experiment.py
  figures/
  data/
    log_odds_matrix.csv
  results.json
  04_validation.md
```

---

## Module Definitions

### Config (`h-m1/code/config.py`)

**Dependencies**: none (standalone)

```python
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

HE1_CODE_DIR: str = str(Path(__file__).parent.parent.parent / "h-e1" / "code")
HE1_DATA_DIR: str = str(Path(__file__).parent.parent.parent / "h-e1" / "data")
HM1_BASE_DIR: str = str(Path(__file__).parent.parent)

@dataclass
class HM1Config:
    # Reused from H-E1 (verified from actual code)
    he1_code_dir: str = HE1_CODE_DIR
    he1_data_dir: str = HE1_DATA_DIR
    fasttext_model_path: str = str(Path(HE1_DATA_DIR) / "models" / "openhermes_reddit_eli5_vs_rw_v2_bigram_200k_train.bin")

    # H-M1 specific
    window_size: int = 10          # matches h-e1 actual value
    alpha: float = 0.5             # Laplace smoothing
    n_bootstrap: int = 1000
    seed: int = 42
    alpha_level: float = 0.05
    filtering_intensities: List[int] = field(default_factory=lambda: [10, 30, 50, 70, 90])
    fasttext_configs: List[str] = field(default_factory=lambda: ["C1","C2","C3","C4","C5"])
    all_configs: List[str] = field(default_factory=lambda: ["C1","C2","C3","C4","C5","C6"])

    # Paths
    data_dir: str = str(Path(HM1_BASE_DIR) / "data")
    figures_dir: str = str(Path(HM1_BASE_DIR) / "figures")
    results_path: str = str(Path(HM1_BASE_DIR) / "results.json")
    validation_path: str = str(Path(HM1_BASE_DIR) / "04_validation.md")
    log_odds_matrix_path: str = str(Path(HM1_BASE_DIR) / "data" / "log_odds_matrix.csv")

    # Visualization
    figure_size: tuple = (10, 6)
    figure_size_heatmap: tuple = (14, 10)
    dpi: int = 150


def load_config(yaml_path: Optional[str] = None) -> HM1Config:
    """Load config from YAML or return defaults."""
    ...

def get_he1_lexicons() -> Dict[str, List[str]]:
    """Import and return H-E1 occupation_lexicon and demographic_lexicon from h-e1/code/config.py."""
    ...
```

---

### LogOddsComputer (`h-m1/code/log_odds.py`)

**Dependencies**: Config, h-e1/corpus_filter.CorpusFilter (for load_corpus reuse), h-e1/entropy_measure.EntropyMeasure (for _tokenize reuse)

```python
import sys
import logging
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import statsmodels.stats.contingency_tables as ct

logger = logging.getLogger(__name__)


class LogOddsComputer:
    """Compute conditional log-odds P(occ|demo)/P(occ|~demo) per (demo, occ) pair."""

    def __init__(
        self,
        occ_lexicon: List[str],
        demo_lexicon: List[str],
        window_size: int = 10,
        alpha: float = 0.5,
    ): ...

    def _tokenize(self, text: str) -> List[str]:
        """Regex tokenizer (same as H-E1 EntropyMeasure._tokenize)."""
        ...

    def compute_cooccurrence_counts(
        self,
        docs: List[dict],
    ) -> Tuple[Dict[Tuple[str,str], int], Dict[str, int], Dict[str, int], int]:
        """Sliding-window co-occurrence count.

        Returns:
            cooc_demo_occ: {(demo, occ): count}
            count_demo: {demo: count}
            count_occ: {occ: count}
            total_tokens: int
        """
        ...

    def compute_log_odds_pair(
        self,
        n_demo_occ: int,
        n_demo_not_occ: int,
        n_not_demo_occ: int,
        n_not_demo_not_occ: int,
    ) -> Tuple[float, float, float]:
        """Laplace-smoothed log-odds via statsmodels Table2x2.

        Returns:
            log_odds: float
            ci_low: float
            ci_high: float
        """
        ...

    def compute_log_odds_matrix(
        self,
        docs: List[dict],
        config_id: str,
    ) -> pd.DataFrame:
        """Compute full (demo × occ) log-odds matrix for one corpus configuration.

        Returns:
            DataFrame columns: [demographic, occupation, log_odds, ci_low, ci_high, config_id]
        """
        ...

    def compute_all_configs(
        self,
        corpora: Dict[str, List[dict]],
    ) -> pd.DataFrame:
        """Compute log-odds for all configurations.

        Returns:
            Concatenated DataFrame with all configs; shape: (N_demo * N_occ * N_configs, 6+)
        """
        ...

    def aggregate_mean_log_odds(
        self,
        log_odds_df: pd.DataFrame,
    ) -> Dict[str, float]:
        """Compute mean log-odds per configuration for Spearman gate."""
        ...

    def save_log_odds_matrix(
        self,
        log_odds_df: pd.DataFrame,
        output_path: str,
    ) -> None:
        """Pivot and save wide-format log_odds_matrix.csv for H-M2 downstream use."""
        ...
```

---

### StatisticalTests (`h-m1/code/statistical_tests.py`)

**Dependencies**: Config

```python
import logging
from typing import Any, Dict, List, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class StatisticalTests:
    """Spearman gate + OLS + Mann-Whitney + KS + bootstrap CI."""

    def __init__(self, n_bootstrap: int = 1000, seed: int = 42): ...

    def spearman_correlation(
        self,
        filtering_intensities: List[int],
        mean_log_odds: List[float],
    ) -> Dict[str, float]:
        """Spearman ρ between filtering intensity [10,30,50,70,90] and mean log-odds C1-C5.

        Returns: {rho, pvalue}
        """
        ...

    def bootstrap_spearman_ci(
        self,
        filtering_intensities: List[int],
        mean_log_odds: List[float],
    ) -> Tuple[float, float]:
        """Bootstrap 95% CI for Spearman ρ (n=1000, paired=True, seed=42).

        Returns: (ci_low, ci_high)
        """
        ...

    def ols_regression(
        self,
        filtering_intensities: List[int],
        mean_log_odds: List[float],
    ) -> Dict[str, Any]:
        """OLS: log_odds ~ percentile_cutoff.

        Returns: {coef, intercept, r_squared, pvalue}
        """
        ...

    def mann_whitney_u(
        self,
        log_odds_c5: np.ndarray,
        log_odds_c6: np.ndarray,
    ) -> Dict[str, float]:
        """Mann-Whitney U: fastText extreme (C5) vs DoReMi (C6).

        Returns: {statistic, pvalue}
        """
        ...

    def ks_test(
        self,
        log_odds_c1: np.ndarray,
        log_odds_c5: np.ndarray,
    ) -> Dict[str, float]:
        """Kolmogorov-Smirnov test: C1 vs C5 log-odds distributions.

        Returns: {statistic, pvalue}
        """
        ...

    def per_pair_spearman(
        self,
        log_odds_df: "pd.DataFrame",
        filtering_intensities: List[int],
    ) -> "pd.DataFrame":
        """Per-(demographic, occupation) Spearman ρ across C1-C5.

        Returns: DataFrame columns: [demographic, occupation, rho, pvalue]
        """
        ...

    def evaluate_gate(
        self,
        spearman_result: Dict[str, float],
        bootstrap_ci: Tuple[float, float],
    ) -> Dict[str, Any]:
        """Apply gate: |rho| > 0 AND pvalue < 0.05.

        Returns: {gate_passed, rho, pvalue, bootstrap_ci_low, bootstrap_ci_high}
        """
        ...

    def run_all_tests(
        self,
        log_odds_df: "pd.DataFrame",
        mean_log_odds_per_config: Dict[str, float],
        filtering_intensities: List[int],
    ) -> Dict[str, Any]:
        """Orchestrate all tests; return unified results dict."""
        ...
```

---

### Visualizer (`h-m1/code/visualize.py`)

**Dependencies**: Config

```python
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

logger = logging.getLogger(__name__)


class Visualizer:
    """H-M1 log-odds specific visualizations."""

    def __init__(self, figures_dir: str, dpi: int = 150): ...

    def plot_spearman_gate(
        self,
        stats_results: Dict[str, Any],
        output_path: Optional[str] = None,
    ) -> str:
        """Gate Metrics: Spearman ρ bar chart with 95% CI.

        Returns: saved figure path
        """
        ...

    def plot_log_odds_vs_intensity(
        self,
        mean_log_odds_per_config: Dict[str, float],
        ols_results: Dict[str, Any],
        output_path: Optional[str] = None,
    ) -> str:
        """Scatter + OLS regression line (C1-C5), DoReMi highlighted.

        Returns: saved figure path
        """
        ...

    def plot_log_odds_heatmap(
        self,
        log_odds_df: "pd.DataFrame",
        config_id: str,
        output_path: Optional[str] = None,
    ) -> str:
        """(demographic × occupation) log-odds heatmap for one configuration.

        Returns: saved figure path
        """
        ...

    def plot_fasttext_vs_doremi(
        self,
        log_odds_df: "pd.DataFrame",
        output_path: Optional[str] = None,
    ) -> str:
        """Violin plots: log-odds distributions C5 vs C6.

        Returns: saved figure path
        """
        ...

    def generate_all(
        self,
        log_odds_df: "pd.DataFrame",
        mean_log_odds_per_config: Dict[str, float],
        stats_results: Dict[str, Any],
    ) -> List[str]:
        """Generate all figures; return list of saved paths."""
        ...
```

---

### run_experiment (`h-m1/code/run_experiment.py`)

**Dependencies**: Config, LogOddsComputer, StatisticalTests, Visualizer, h-e1/CorpusFilter

```python
import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""

logger = logging.getLogger("run_experiment")


def setup_h1_imports(he1_code_dir: str) -> None:
    """Insert h-e1/code into sys.path for CorpusFilter and config imports."""
    ...

def load_corpora(
    config: "HM1Config",
) -> Dict[str, list]:
    """Load C1-C6 from h-e1/data/corpora/*.jsonl via CorpusFilter.load_corpus().

    Falls back to CorpusFilter.build_all_corpora() if subsets missing.
    Returns: {config_id: List[dict]}
    """
    ...

def verify_mechanism_activated(
    log_odds_per_config: Dict[str, "pd.DataFrame"],
    stats_results: Dict[str, Any],
) -> Dict[str, Any]:
    """Check all 6 configs computed, variation exists, Spearman computed.

    Returns: {log_odds_computed, shape_valid, variation_exists, spearman_computed, mechanism_activated}
    """
    ...

def write_results_json(results: Dict[str, Any], path: str) -> None: ...

def write_validation_md(
    results: Dict[str, Any],
    mechanism_check: Dict[str, Any],
    path: str,
) -> None: ...

def parse_args() -> argparse.Namespace:
    """--quick (50k docs), --output-dir, --config (YAML override)"""
    ...

def main() -> None:
    """
    Pipeline steps:
    1. Load config (HM1Config)
    2. sys.path setup for h-e1 imports
    3. Setup directories
    4. Load corpora C1-C6 via CorpusFilter.load_corpus()
    5. Compute log-odds matrix (LogOddsComputer.compute_all_configs)
    6. Aggregate mean log-odds per config
    7. Run statistical tests (StatisticalTests.run_all_tests)
    8. Generate visualizations (Visualizer.generate_all)
    9. Verify mechanism activation
    10. Write results.json + 04_validation.md
    11. Save log_odds_matrix.csv
    """
    ...

if __name__ == "__main__":
    main()
```

---

## Module Dependency Graph

- `run_experiment` → Config, LogOddsComputer, StatisticalTests, Visualizer
- `run_experiment` → [h-e1] CorpusFilter (via sys.path)
- `LogOddsComputer` → Config, [h-e1] CONFIG lexicons (via get_he1_lexicons)
- `StatisticalTests` → Config
- `Visualizer` → Config
- `config.py` → [h-e1] config.py (lexicon import via get_he1_lexicons)

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | Directory structure, config.py (HM1Config dataclass), h-e1 import path wiring, YAML config | 8 | 2+1+2+3 |
| A-2 | Corpus Loading | load_corpora() in run_experiment; verify C1-C6 .jsonl exist in h-e1/data/corpora/; fallback to build_all_corpora | 9 | 2+3+2+2 |
| A-3 | Co-occurrence Counting | LogOddsComputer.compute_cooccurrence_counts() — sliding window scan producing cooc_demo_occ, count_demo, count_occ, N | 12 | 3+2+4+3 |
| A-4 | Log-Odds Matrix | LogOddsComputer.compute_log_odds_pair() + compute_log_odds_matrix() + compute_all_configs() + save_log_odds_matrix() | 14 | 4+3+4+3 |
| A-5 | Spearman Gate | StatisticalTests.spearman_correlation() + bootstrap_spearman_ci() + evaluate_gate() | 11 | 3+2+4+2 |
| A-6 | Secondary Stats | StatisticalTests.ols_regression() + mann_whitney_u() + ks_test() + per_pair_spearman() | 12 | 3+2+4+3 |
| A-7 | Visualizations | Visualizer — all 4 figures: spearman gate, log-odds vs intensity, heatmap, violin | 11 | 3+2+3+3 |
| A-8 | Pipeline Orchestration | run_experiment.py main() — 11-step pipeline, verify_mechanism_activated, write_results_json, write_validation_md | 13 | 3+3+3+4 |
| A-9 | Unit Tests | tests/ — test co-occurrence counting, log-odds computation (known values), gate evaluation, CSV output shape | 10 | 2+2+3+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-4], Medium(9-13): [A-2, A-3, A-5, A-6, A-7, A-8, A-9], Low(4-8): [A-1]

---

## Implementation Notes for Phase 4

**H-E1 import pattern (verified from actual code):**
```python
import sys
sys.path.insert(0, "/path/to/h-e1/code")
from corpus_filter import CorpusFilter
from config import CONFIG as HE1_CONFIG
```

**Corpus file paths (verified):**
`h-e1/data/corpora/C1.jsonl` through `C6.jsonl` (no C0 needed for H-M1)

**H-E1 window_size is 10** (not 5 as stated in PRD — trust actual h-e1/code/config.py: `"window_size": 10`)

**Filtering intensities for Spearman:** `[10, 30, 50, 70, 90]` → C1-C5 only; C6 (DoReMi) excluded from Spearman, used for Mann-Whitney comparison
