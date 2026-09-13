# Logic: H-E1
## Residual Instability — Existence & Construct Validity (PoC)

**Hypothesis:** H-E1 (EXISTENCE / FOUNDATION)
**Tier:** LIGHT (15 tasks max)
**Type:** Statistical analysis pipeline — no neural network training
**Generated:** 2026-05-12

Applied: modular-pipeline pattern (sklearn PCA + OLS residualization, pandas DataFrame assembly, matplotlib/seaborn visualization)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing codebase. Serena returned "No active project" for this path; no symbols to analyze.
**Analyzed Path**: docs/youra_research/20260512_buildingtrust/h-e1/
**Relevant Symbols**: None — new implementation

---

## Overview

| Field | Value |
|-------|-------|
| Hypothesis | H-E1 |
| Type | EXISTENCE / Statistical Analysis |
| Tier | LIGHT (15 tasks max) |
| Gate 1 | SD(advglue_drop) > 0.05 |
| Gate 2 | R²_residualization < 0.80 |

---

## Key Data Structures

### DataFrame Schema

| Column | dtype | Notes |
|--------|-------|-------|
| `model_id` | str | Unique identifier |
| `model_family` | str | LLaMA / Mistral / GPT / Qwen / Gemma |
| `scale` | str | 7B / 13B / 70B+ |
| `training_regime` | str | pretrained / instruction-tuned / RLHF |
| `advglue_drop` | float64 | AdvGLUE accuracy drop [0, 1] |
| `mmlu` | float64 | 5-shot accuracy [0, 1] |
| `gsm8k` | float64 | 5-shot exact match [0, 1] |
| `bbh` | float64 | 3-shot CoT accuracy [0, 1] |
| `hellaswag` | float64 | 10-shot accuracy [0, 1] |
| `winogrande` | float64 | 5-shot accuracy [0, 1] |
| `mean_confidence` | float64 | Mean log-prob proxy |
| `PC1` | float64 | Added by compute_ri.py |
| `RI` | float64 | Residual Instability, added by compute_ri.py |

**Shape**: `(N, 13)` where N ≥ 30

### Stats Dict Schema

```python
stats: dict = {
    "pc1_var": float,           # Fraction of variance explained by PC1 (≥ 0.70)
    "r2_residualization": float, # OLS R² of advglue_drop ~ PC1 + mean_confidence
    "r2_baseline": float,        # OLS R² of advglue_drop ~ PC1 only
    "sd_advglue_drop": float,    # SD of advglue_drop across models
    "vif": float,               # VIF(PC1, mean_confidence)
    "gate_sd_passed": bool,
    "gate_r2_passed": bool,
    "gate_passed": bool,
}
```

### Gate Results Dict Schema

```python
gate: dict = {
    "gate_passed": bool,
    "gate_sd_passed": bool,
    "gate_r2_passed": bool,
    "sd_advglue_drop": float,
    "sd_ci_lower": float,
    "sd_ci_upper": float,
    "r2_residualization": float,
    "r2_ci_lower": float,
    "r2_ci_upper": float,
    "n_models": int,
    "n_families": int,
    "n_scales": int,
    "n_regimes": int,
}
```

---

## E1: Data Assembly

### A-E1: DataAssembler [Complexity: 13, Budget: 3 subtasks]

**Applied**: Standard pandas merge + HuggingFace datasets loader

#### API Signatures

```python
# code/data_assembly.py
import pandas as pd
from pathlib import Path
from typing import Optional


class DataAssembler:
    def __init__(
        self,
        trustllm_data_dir: str,
        lmeval_results_dir: str,
    ) -> None:
        """Initialize with data source directories."""
        ...

    def load_trustllm_scores(self) -> pd.DataFrame:
        """Load AdvGLUE drop scores from TrustLLM dataset.
        Returns: DataFrame with columns [model_id, model_family, scale, training_regime, advglue_drop]
        Shape: (N_trustllm, 5)
        """
        ...

    def load_lmeval_scores(self) -> pd.DataFrame:
        """Parse lm-eval JSON outputs for capability benchmarks + mean_confidence.
        Returns: DataFrame with columns [model_id, mmlu, gsm8k, bbh, hellaswag, winogrande, mean_confidence]
        Shape: (N_lmeval, 7)
        """
        ...

    def merge_matrix(self) -> pd.DataFrame:
        """Merge trustllm and lmeval DataFrames on model_id (inner join).
        Returns: DataFrame shape (N_merged, 13)
        """
        ...

    def validate_matrix(self, df: pd.DataFrame) -> bool:
        """Assert diversity and completeness constraints.
        Raises: AssertionError if constraints not met.
        """
        ...


def assemble_matrix(
    trustllm_data_dir: str,
    lmeval_results_dir: str,
) -> pd.DataFrame:
    """Top-level entry point for data assembly.
    Returns: Validated DataFrame shape (N≥30, 13)
    """
    ...
```

#### Pseudo-code: `load_lmeval_scores`

```
1. For each JSON file in lmeval_results_dir:
   a. Parse model_id from filename
   b. Extract results[benchmark]["acc"] for each of 5 cap_cols
   c. Extract mean log-prob from results["loglikelihood"] if available, else 0.0
2. Concatenate rows into DataFrame
3. Return DataFrame [model_id, mmlu, gsm8k, bbh, hellaswag, winogrande, mean_confidence]
```

#### Error Handling

```python
assert len(df) >= 30, f"Only {len(df)} models; need ≥30"
assert df["advglue_drop"].notna().mean() >= 0.70, "advglue_drop >30% missing"
assert df["model_family"].nunique() >= 3, "Need ≥3 model families"
assert df["scale"].nunique() >= 2, "Need ≥2 scales"
assert df["training_regime"].nunique() >= 2, "Need ≥2 training regimes"
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E1-1 | TrustLLM data loader | Implement `load_trustllm_scores`: HF datasets API, AdvGLUE drop extraction, metadata |
| L-E1-2 | lm-eval results aggregation | Implement `load_lmeval_scores`: parse JSON outputs, extract 5 benchmark scores + mean_confidence |
| L-E1-3 | Matrix validation | Implement `validate_matrix` + `merge_matrix`: inner join, diversity assertions, missing-value checks |

---

## E2: RI Computation

### A-E2: RIComputer [Complexity: 10, Budget: 3 subtasks]

**Applied**: sklearn PCA + OLS residualization + statsmodels VIF

#### API Signatures

```python
# code/compute_ri.py
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from statsmodels.stats.outliers_influence import variance_inflation_factor
from typing import Tuple


class RIComputer:
    def __init__(self, seed: int = 42) -> None:
        """Initialize with random seed."""
        ...

    def compute_pc1(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, float]:
        """Fit PCA on 5 capability cols; add PC1 column.
        Returns: (df_with_PC1, pc1_explained_variance_ratio)
        Input shape: (N, 13), Output shape: (N, 14)
        """
        ...

    def fit_ols(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, float]:
        """OLS: advglue_drop ~ PC1 + mean_confidence; add RI column.
        Returns: (df_with_RI, r2)
        Input shape: (N, 14), Output shape: (N, 15)
        """
        ...

    def fit_ols_baseline(self, df: pd.DataFrame) -> float:
        """OLS baseline: advglue_drop ~ PC1 only.
        Returns: r2_baseline float
        """
        ...

    def check_vif(self, df: pd.DataFrame) -> float:
        """Compute VIF for PC1 in [PC1, mean_confidence].
        Returns: vif_pc1 float (should be < 5.0)
        """
        ...

    def compute(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
        """Run full pipeline: PC1 → OLS → VIF → stats dict.
        Returns: (df_with_PC1_and_RI, stats_dict)
        """
        ...


def compute_residual_instability(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    """Top-level entry point for RI computation.
    Returns: (enriched_df, stats_dict)
    """
    ...
```

#### Pseudo-code: `compute_residual_instability`

```
1. scaler = StandardScaler()
   X_scaled = scaler.fit_transform(df[CAP_COLS])  # [N, 5]
2. pca = PCA(n_components=1, random_state=seed)
   df["PC1"] = pca.fit_transform(X_scaled).flatten()  # [N]
   pc1_var = pca.explained_variance_ratio_[0]
   assert pc1_var >= 0.70
3. X_resid = df[["PC1", "mean_confidence"]].values  # [N, 2]
   y = df["advglue_drop"].values  # [N]
   ols = LinearRegression().fit(X_resid, y)
   df["RI"] = y - ols.predict(X_resid)  # [N]
   r2 = ols.score(X_resid, y)
4. ols_base = LinearRegression().fit(df[["PC1"]], y)
   r2_baseline = ols_base.score(df[["PC1"]], y)
5. vif = variance_inflation_factor(X_resid, 0)  # VIF for PC1
6. stats = {pc1_var, r2, r2_baseline, sd_advglue_drop=y.std(), vif,
            gate_sd_passed=(y.std() > 0.05), gate_r2_passed=(r2 < 0.80),
            gate_passed=(y.std() > 0.05 and r2 < 0.80)}
7. return df, stats
```

#### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E2-1 | PCA capability computation | Implement `compute_pc1`: StandardScaler + PCA(n=1), assert pc1_var ≥ 0.70 |
| L-E2-2 | OLS residualization | Implement `fit_ols` + `fit_ols_baseline`: LinearRegression, compute RI column, r2 |
| L-E2-3 | VIF check | Implement `check_vif`: statsmodels VIF on [PC1, mean_confidence], assert < 5.0 |

---

## E3: Gate Evaluation, Bootstrap CI, Export

### A-E3: GateEvaluator [Complexity: 8, Budget: 3 subtasks]

**Applied**: Standard scipy bootstrap + yaml/json export

#### API Signatures

```python
# code/evaluate.py
import pandas as pd
import numpy as np
from scipy import stats as scipy_stats
from typing import Tuple


class GateEvaluator:
    def __init__(
        self,
        sd_threshold: float = 0.05,
        r2_threshold: float = 0.80,
        n_bootstrap: int = 10000,
        seed: int = 42,
    ) -> None:
        """Initialize gate evaluator."""
        ...

    def check_gate(self, df: pd.DataFrame, stats: dict) -> dict:
        """Evaluate gate conditions from stats dict.
        Returns: gate_results dict (see Gate Results Dict Schema)
        """
        ...

    def bootstrap_ci(
        self,
        df: pd.DataFrame,
        alpha: float = 0.05,
    ) -> dict:
        """Bootstrap 95% CIs (10,000 samples) for SD(advglue_drop) and R²_residualization.
        Returns: {"sd_ci": (lower, upper), "r2_ci": (lower, upper)}
        """
        ...

    def verify_mechanism_activated(
        self,
        df: pd.DataFrame,
        stats: dict,
    ) -> Tuple[bool, dict]:
        """Check both gates + bootstrap CIs.
        Returns: (gate_passed: bool, full_gate_dict)
        """
        ...

    def export_results(
        self,
        df: pd.DataFrame,
        stats: dict,
        gate: dict,
        output_dir: str,
    ) -> None:
        """Write model_matrix.csv, gate_results.yaml, stats_summary.json.
        Outputs: {output_dir}/model_matrix.csv, gate_results.yaml, stats_summary.json
        """
        ...


def run_evaluation(
    df: pd.DataFrame,
    stats: dict,
    output_dir: str,
) -> dict:
    """Top-level entry point: gate check + bootstrap CI + export.
    Returns: gate_results dict
    """
    ...
```

#### Pseudo-code: `bootstrap_ci`

```
1. rng = np.random.default_rng(seed)
2. For n_bootstrap iterations:
   a. idx = rng.choice(N, size=N, replace=True)
   b. sample_sd = df["advglue_drop"].iloc[idx].std()
   c. X_s = df[["PC1","mean_confidence"]].iloc[idx].values
      y_s = df["advglue_drop"].iloc[idx].values
      r2_s = LinearRegression().fit(X_s, y_s).score(X_s, y_s)
   d. Append sample_sd, r2_s
3. sd_ci = (percentile(2.5), percentile(97.5)) of sd_samples
4. r2_ci = (percentile(2.5), percentile(97.5)) of r2_samples
```

#### Pseudo-code: `check_gate`

```
1. gate_sd = stats["sd_advglue_drop"] > sd_threshold (0.05)
2. gate_r2 = stats["r2_residualization"] < r2_threshold (0.80)
3. gate_passed = gate_sd AND gate_r2
4. ci = self.bootstrap_ci(df)
5. Return gate dict with all metrics + CIs + diversity counts
```

#### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E3-1 | Gate condition check | Implement `check_gate`: evaluate SD > 0.05 and R² < 0.80 from stats dict |
| L-E3-2 | Bootstrap CI computation | Implement `bootstrap_ci`: 10,000-sample bootstrap for SD and R² with seed=42 |
| L-E3-3 | Results export | Implement `export_results`: write CSV, YAML, JSON to output_dir; implement `run_evaluation` |

---

## Visualizer API

```python
# code/visualize.py
import pandas as pd
from typing import List


class Visualizer:
    def __init__(self, figures_dir: str) -> None:
        """Initialize with output directory."""
        ...

    def plot_gate_metrics(self, gate: dict) -> str:
        """Bar chart: SD vs 0.05 threshold; R² vs 0.80 threshold.
        Returns: saved file path
        """
        ...

    def plot_ri_distribution(self, df: pd.DataFrame) -> str:
        """Violin plot of RI by model_family.
        Returns: saved file path
        """
        ...

    def plot_advglue_hist(self, df: pd.DataFrame) -> str:
        """Histogram of raw advglue_drop distribution.
        Returns: saved file path
        """
        ...

    def plot_pc1_scatter(self, df: pd.DataFrame) -> str:
        """Scatter plot: PC1 vs advglue_drop with OLS fit line.
        Returns: saved file path
        """
        ...

    def plot_ri_regime(self, df: pd.DataFrame) -> str:
        """Box plot of RI by training_regime.
        Returns: saved file path
        """
        ...

    def generate_all(self, df: pd.DataFrame, gate: dict) -> List[str]:
        """Generate all 5 figures; return list of saved paths."""
        ...


def generate_figures(
    df: pd.DataFrame,
    gate: dict,
    figures_dir: str,
) -> List[str]:
    """Top-level entry point. Returns list of 5 saved figure paths."""
    ...
```

---

## RunExperiment API

```python
# code/run_experiment.py
import argparse


def parse_args() -> argparse.Namespace:
    """Parse CLI: --trustllm-data-dir, --lmeval-results-dir, --output-dir, --figures-dir."""
    ...


def main() -> None:
    """Orchestrate full pipeline:
    1. assemble_matrix()           -> df [N, 13]
    2. compute_residual_instability(df) -> df [N, 15], stats
    3. run_evaluation(df, stats, output_dir) -> gate
    4. generate_figures(df, gate, figures_dir) -> figure_paths
    """
    ...
```

---

## Error Handling Summary

| Module | Key Assertions |
|--------|---------------|
| data_assembly.py | N ≥ 30, ≥3 families, ≥2 scales, ≥2 regimes, ≤30% missing per col |
| compute_ri.py | pc1_var ≥ 0.70, VIF < 5.0, no NaN in PC1/RI cols |
| evaluate.py | gate dict has all required keys before export, output_dir exists |
| visualize.py | figures_dir created if not exists, all 5 paths returned |
