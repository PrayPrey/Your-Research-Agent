# Logic Design: h-m1 Benchmark Distinctiveness Analysis

**Hypothesis:** h-m1 (MECHANISM)  
**Date:** 2026-04-15  
**Author:** Logic Agent  
**Type:** Statistical Analysis - Benchmark Comparison  

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** API signatures verified from h-e1 actual code  
**Analyzed Path:** `/home/anonymous/YouRA_results_new_4_sonnet45_no_mcp/TEST_dl4c_2/docs/youra_research/20260415_dl4c/h-e1/code/`  
**Relevant Symbols:** PublishedResultsCollector, ExecutionTraceExtractor (data loading patterns)  
**Note:** h-m1 reuses h-e1 data output (features.csv) but implements new statistical analysis modules.

---

## Design Patterns Applied

**Applied:** Statistical Analysis Pattern (scipy.stats for correlation and divergence)  
**Applied:** Visualization Pipeline Pattern (matplotlib/seaborn figure generation)  
**Applied:** Data Aggregation Pattern (pandas DataFrame transformations)

---

## External Dependencies (Base Hypothesis)

### Data Sources from h-e1

The following data files are loaded from h-e1 completed experiment:

**Primary Data File:**
```python
# From: ../h-e1/code/outputs/features.csv (ACTUAL DATA FILE)
# Schema verified from actual CSV:
# Columns: model, benchmark, pass@1, pass@10, pass@100, 
#          runtime_q25, runtime_q50, runtime_q75,
#          error_syntax, error_runtime, error_timeout
# 
# Available data: 14 model-benchmark pairs
# - 8 models evaluated on HumanEval
# - 6 models evaluated on MBPP
# - No APPS data (h-e1 limitation)
```

**Data Availability:**
- HumanEval: 8 models (GPT-4, GPT-3.5-Turbo, CodeLlama-34B, CodeLlama-13B, CodeLlama-7B, StarCoder-15B, DeepSeek-Coder-33B, DeepSeek-Coder-6.7B)
- MBPP: 6 models (GPT-4, GPT-3.5-Turbo, CodeLlama-34B, CodeLlama-7B, StarCoder-15B, DeepSeek-Coder-33B)
- Common models across both benchmarks: 6 models

**Note:** Original PRD specified 3 benchmarks, but actual h-e1 data only includes HumanEval and MBPP. Analysis adapted to single benchmark pair.

---

## M-1: Data Loading Infrastructure [Complexity: 6, Budget: 1]

**Applied:** CSV Loading Pattern (pandas read_csv)

### API Signatures

```python
import pandas as pd
from pathlib import Path
from typing import Dict, List

class ExecutionTraceLoader:
    """Load execution trace features from h-e1 outputs."""
    
    def __init__(self, h_e1_path: str = "../h-e1/code/outputs/features.csv"):
        """Initialize loader with h-e1 data path."""
        self.h_e1_path = Path(h_e1_path)
        self.features_df = None
    
    def load_features(self) -> pd.DataFrame:
        """
        Load features.csv from h-e1.
        Returns: DataFrame with columns [model, benchmark, pass@1, ..., error_timeout]
        """
        ...
    
    def validate_data_quality(self) -> Dict[str, any]:
        """
        Validate loaded data quality.
        Returns: {valid: bool, model_count: int, benchmark_count: int, missing_features: Dict}
        """
        ...
    
    def get_benchmark_subset(self, benchmark: str) -> pd.DataFrame:
        """
        Extract subset for specific benchmark.
        Args: benchmark - "HumanEval" or "MBPP"
        Returns: Filtered DataFrame
        """
        ...
    
    def get_model_list(self) -> List[str]:
        """Get list of all models in dataset. Returns: List of model names"""
        ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | CSV loading and validation | Load h-e1 features.csv, validate schema and completeness |

---

## M-2: Ranking Correlation Analysis [Complexity: 9, Budget: 1]

**Applied:** Spearman Correlation Pattern (scipy.stats.spearmanr)

### API Signatures

```python
from scipy.stats import spearmanr
import pandas as pd
from typing import Dict, Tuple

class BenchmarkCorrelationAnalyzer:
    """Analyze model ranking correlation across benchmarks."""
    
    def __init__(self, feature_df: pd.DataFrame):
        """Initialize with feature DataFrame from h-e1."""
        self.feature_df = feature_df
        self.correlations = {}
    
    def compute_ranking_correlation(self, bench1: str, bench2: str) -> Tuple[float, float]:
        """
        Compute Spearman correlation between model rankings.
        
        Args:
            bench1: First benchmark name
            bench2: Second benchmark name
        
        Returns:
            (rho, p_value) - Correlation coefficient and significance
        """
        ...
    
    def compute_all_pairwise_correlations(self) -> Dict[str, Dict[str, float]]:
        """
        Compute all pairwise benchmark correlations.
        Returns: {"bench1-bench2": {"rho": float, "p_value": float}}
        """
        ...
    
    def get_correlation_matrix(self) -> pd.DataFrame:
        """
        Get correlation matrix for visualization.
        Returns: DataFrame with benchmarks as rows/columns
        """
        ...
```

### Pseudo-code

```
Input: feature_df with [model, benchmark, pass@1, ...]
Output: {"HumanEval-MBPP": {"rho": float, "p_value": float}}

Algorithm:
1. Extract pass@1 scores for bench1 → scores1 (indexed by model)
2. Extract pass@1 scores for bench2 → scores2 (indexed by model)
3. Find common models: common = scores1.index ∩ scores2.index
4. Align scores: aligned1 = scores1[common], aligned2 = scores2[common]
5. Compute: rho, p_value = spearmanr(aligned1, aligned2)
6. Return {"rho": rho, "p_value": p_value}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Spearman correlation computation | Implement pairwise ranking correlation with scipy |

---

## M-3: Distribution Divergence Analysis [Complexity: 10, Budget: 1]

**Applied:** KL Divergence Pattern (scipy.stats.entropy with histogram normalization)

### API Signatures

```python
from scipy.stats import entropy
import numpy as np
from typing import Dict, List

class DistributionDivergenceAnalyzer:
    """Analyze feature distribution divergence across benchmarks."""
    
    def __init__(self, feature_df: pd.DataFrame):
        """Initialize with feature DataFrame."""
        self.feature_df = feature_df
        self.divergences = {}
    
    def compute_kl_divergence(self, bench1: str, bench2: str, feature: str = "pass@1") -> float:
        """
        Compute KL divergence for feature distributions.
        
        Args:
            bench1: First benchmark
            bench2: Second benchmark
            feature: Feature column name (default "pass@1")
        
        Returns:
            kl_div: KL divergence value (0 = identical, >0 = different)
        """
        ...
    
    def compute_all_divergences(self, features: List[str] = ["pass@1"]) -> Dict[str, float]:
        """
        Compute divergences for all benchmark pairs and features.
        Returns: {"HumanEval-MBPP": kl_value}
        """
        ...
    
    def aggregate_divergence_scores(self) -> Dict[str, float]:
        """
        Aggregate divergence across multiple features.
        Returns: {"HumanEval-MBPP": mean_kl}
        """
        ...
```

### Pseudo-code

```
Input: bench1_features (pass@1 values), bench2_features (pass@1 values)
Output: kl_divergence (float)

Algorithm:
1. Create histograms:
   hist1, bins = np.histogram(bench1_features, bins=20, density=True)
   hist2, _ = np.histogram(bench2_features, bins=bins, density=True)

2. Normalize to probability distributions:
   hist1 = (hist1 + 1e-10) / (hist1 + 1e-10).sum()
   hist2 = (hist2 + 1e-10) / (hist2 + 1e-10).sum()

3. Compute KL divergence:
   kl_div = entropy(pk=hist1, qk=hist2)

4. Return kl_div
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | KL divergence computation | Histogram normalization and scipy.stats.entropy calculation |

---

## M-4: Gate Condition Evaluation [Complexity: 7, Budget: 0]

**Applied:** Threshold Checking Pattern (simple boolean logic)

### API Signatures

```python
class GateConditionEvaluator:
    """Evaluate gate condition for hypothesis validation."""
    
    def __init__(self, correlations: Dict, divergences: Dict):
        """
        Initialize with analysis results.
        Args:
            correlations: {"bench1-bench2": {"rho": float, "p_value": float}}
            divergences: {"bench1-bench2": float}
        """
        self.correlations = correlations
        self.divergences = divergences
    
    def check_correlation_threshold(self, threshold: float = 0.8) -> Dict[str, bool]:
        """Check if any pair has rho < threshold. Returns: {"pair": bool}"""
        ...
    
    def check_divergence_threshold(self, threshold: float = 0.1) -> Dict[str, bool]:
        """Check if any pair has KL > threshold. Returns: {"pair": bool}"""
        ...
    
    def evaluate_gate(self) -> Dict[str, any]:
        """
        Evaluate gate condition: (∃ pair: rho < 0.8) AND (∃ pair: KL > 0.1)
        Returns: {gate_pass: bool, low_corr_pairs: List, high_div_pairs: List}
        """
        ...
```

---

## M-5: Visualization Generation [Complexity: 11, Budget: 0]

**Applied:** Matplotlib/Seaborn Figure Generation Pattern

### API Signatures

```python
import matplotlib.pyplot as plt
import seaborn as sns

class VisualizationGenerator:
    """Generate required figures for gate evaluation."""
    
    def __init__(self, correlations: Dict, divergences: Dict, output_dir: str = "figures"):
        """Initialize with analysis results."""
        self.correlations = correlations
        self.divergences = divergences
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def plot_correlation_heatmap(self) -> str:
        """
        Generate correlation heatmap (REQUIRED for gate).
        Returns: Path to saved figure
        """
        ...
    
    def plot_kl_divergence_bars(self) -> str:
        """Generate bar chart of KL divergences. Returns: figure path"""
        ...
    
    def plot_ranking_scatter(self, bench1: str, bench2: str) -> str:
        """Generate scatter plot of model rankings. Returns: figure path"""
        ...
    
    def plot_feature_distributions(self, feature: str = "pass@1") -> str:
        """Generate overlaid histograms. Returns: figure path"""
        ...
    
    def generate_all_figures(self) -> List[str]:
        """Generate all required figures. Returns: List of figure paths"""
        ...
```

---

## M-6: Results Integration [Complexity: 8, Budget: 0]

**Applied:** JSON Serialization Pattern

### API Signatures

```python
import json
from pathlib import Path

class AnalysisPipeline:
    """Orchestrate complete analysis workflow."""
    
    def __init__(self, config: Dict):
        """
        Initialize pipeline.
        Args: config - {h_e1_path: str, output_dir: str, figures_dir: str}
        """
        self.config = config
        self.results = {}
    
    def load_data(self) -> pd.DataFrame:
        """Load data from h-e1. Returns: features DataFrame"""
        ...
    
    def compute_correlations(self) -> Dict:
        """Compute all correlations. Returns: correlation results"""
        ...
    
    def compute_divergences(self) -> Dict:
        """Compute all divergences. Returns: divergence results"""
        ...
    
    def evaluate_gate(self) -> Dict:
        """Evaluate gate condition. Returns: gate evaluation results"""
        ...
    
    def generate_visualizations(self) -> List[str]:
        """Generate all figures. Returns: List of figure paths"""
        ...
    
    def save_results(self) -> None:
        """Save analysis results to JSON."""
        ...
    
    def run(self) -> Dict:
        """
        Execute complete pipeline.
        Returns: {correlations: Dict, divergences: Dict, gate: Dict, figures: List}
        """
        ...
```

---

## Data Structures

### Analysis Results Schema

```python
AnalysisResults = {
    "correlations": {
        "HumanEval-MBPP": {
            "rho": float,           # Spearman correlation coefficient
            "p_value": float        # Statistical significance
        }
    },
    "kl_divergence": {
        "HumanEval-MBPP": float    # KL divergence value
    },
    "gate_evaluation": {
        "gate_satisfied": bool,
        "low_correlation_pairs": List[str],
        "high_divergence_pairs": List[str],
        "threshold_correlation": 0.8,
        "threshold_divergence": 0.1
    },
    "figures": [
        "figures/correlation_heatmap.png",
        "figures/kl_divergence_bars.png",
        "figures/ranking_scatter_humaneval_mbpp.png",
        "figures/feature_distributions.png"
    ]
}
```

---

## Integration Points

### h-e1 Data Consumption

```python
# Load h-e1 output
loader = ExecutionTraceLoader(h_e1_path="../h-e1/code/outputs/features.csv")
features_df = loader.load_features()

# Validate data quality
validation = loader.validate_data_quality()
assert validation['valid'], "h-e1 data quality check failed"

# Extract benchmark subsets
humaneval_df = loader.get_benchmark_subset("HumanEval")
mbpp_df = loader.get_benchmark_subset("MBPP")
```

### Pipeline Execution Flow

```
1. ExecutionTraceLoader → load features.csv from h-e1
2. BenchmarkCorrelationAnalyzer → compute HumanEval-MBPP ranking correlation
3. DistributionDivergenceAnalyzer → compute HumanEval-MBPP KL divergence
4. GateConditionEvaluator → check gate: (rho < 0.8) AND (KL > 0.1)
5. VisualizationGenerator → generate 4 required figures
6. AnalysisPipeline → save results to analysis_results.json
```

---

## Configuration

### Analysis Parameters

```python
# From src/config.py
H_E1_DATA_PATH = "../h-e1/code/outputs/features.csv"

BENCHMARKS = ['HumanEval', 'MBPP']  # Only 2 benchmarks available

ANALYSIS_FEATURES = ['pass@1', 'runtime_q50', 'runtime_q75']

GATE_THRESHOLDS = {
    'correlation': 0.8,      # rho < 0.8 indicates distinctiveness
    'kl_divergence': 0.1     # KL > 0.1 indicates distinctiveness
}

OUTPUT_DIR = "outputs"
FIGURES_DIR = "figures"

HISTOGRAM_BINS = 20  # For KL divergence computation
```

---

## Validation Logic

### Data Quality Checks

```python
def validate_h_e1_data(features_df: pd.DataFrame) -> bool:
    """Validate h-e1 data meets minimum requirements."""
    # Check minimum models (relaxed for 2-benchmark scenario)
    model_count = len(features_df['model'].unique())
    assert model_count >= 6, f"Need ≥6 models, got {model_count}"
    
    # Check benchmarks present
    benchmarks = features_df['benchmark'].unique()
    assert 'HumanEval' in benchmarks and 'MBPP' in benchmarks
    
    # Check required features present
    required_cols = ['model', 'benchmark', 'pass@1']
    assert all(col in features_df.columns for col in required_cols)
    
    return True
```

### Statistical Significance Check

```python
def check_correlation_significance(p_value: float, alpha: float = 0.05) -> bool:
    """Check if correlation is statistically significant."""
    return p_value < alpha
```

---

## Budget Summary

**Total Subtasks Allocated: 3**

| Epic | Complexity | Budget | Subtasks Used |
|------|------------|--------|---------------|
| M-1  | 6          | 1      | 1             |
| M-2  | 9          | 1      | 1             |
| M-3  | 10         | 1      | 1             |
| M-4  | 7          | 0      | 0 (simple logic) |
| M-5  | 11         | 0      | 0 (standard plotting) |
| M-6  | 8          | 0      | 0 (orchestration) |

**Total Budget Used: 3/3** ✓

**Complexity Focus:** M-2 (correlation) and M-3 (divergence) receive subtask allocation for statistical computation complexity.

---

**Document Status:** Final Logic Design for Phase 4 Implementation  
**Next Phase:** Phase 4 - Implementation (Coding)  
**Data Dependency:** h-e1 outputs (COMPLETED - features.csv verified)  
**Validation:** All API signatures copy-paste ready, statistical methods specified, budget respected
