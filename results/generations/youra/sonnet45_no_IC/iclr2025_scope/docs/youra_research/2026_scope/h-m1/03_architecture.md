# System Architecture: H-M1 Feature-Ranking Correlation Analysis

**Date:** 2026-07-13
**Hypothesis:** H-M1 (MECHANISM)
**Type:** Statistical Correlation Analysis
**Tier:** STANDARD (Simple data processing pipeline)

Applied: Standard Python Statistical Analysis Pattern

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Patterns extracted from H-E1 implementation
**Analyzed Path:** `docs/youra_research/h-e1/code/`
**Findings:** H-E1 implements JSONL-based benchmark storage with schema: {benchmark_id, dataset_name, domain, sample_size, dimensionality, num_classes, method_rankings}. Method rankings stored as nested dict with family classification and ranking_percentile. Reuse data loading patterns and family classification logic.

---

## System Overview

MECHANISM hypothesis testing correlation between Tier 1+2 dataset features and method family rankings. Uses 63 benchmarks from H-E1 collection. Success gate: ≥3 feature-method pairs with Spearman ρ > 0.3, p < 0.05.

**Core Analysis:**
- Input: H-E1 JSONL collection (63 benchmarks)
- Compute: Tier 1 (universal) + Tier 2 (domain-specific) features
- Correlate: Features vs method family rankings using scipy.stats.spearmanr
- Output: Correlation matrix, significance tests, visualizations

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| BenchmarkLoader | `sys.path + relative import` | `h-e1/code/output/benchmarks_collection.jsonl` |
| MethodFamilyClassifier | `Inline logic (copy)` | `h-e1/code/collect_benchmarks.py:72-79` |

**Data Format (Verified from H-E1):**
```python
# JSONL schema from h-e1/code/output/benchmarks_collection.jsonl
{
    "benchmark_id": str,
    "dataset_name": str,
    "domain": str,  # "vision", "graph", "time-series", "tabular", "federated-learning"
    "sample_size": int | None,
    "dimensionality": int | None,
    "num_classes": str | None,
    "method_rankings": {
        "MethodName": {
            "family": str,  # "Linear", "RNN", "Polynomial", "Augmentation"
            "accuracy": float,
            "ranking_percentile": float  # 0-100
        }
    }
}
```

---

## Module Structure

### 1. Data Loading Module (`code/load_data.py`)

**Dependencies:** json, pathlib

```python
class BenchmarkDataLoader:
    def __init__(self, h_e1_path: str): ...
    def load_benchmarks(self) -> List[Dict]: ...
    def extract_method_rankings(self, benchmarks: List[Dict]) -> pd.DataFrame: ...
```

---

### 2. Feature Computation Module (`code/compute_features.py`)

**Dependencies:** pandas, numpy

```python
class Tier1FeatureComputer:
    FEATURES = ['sample_size', 'dimensionality', 'num_classes', 'class_imbalance']
    
    def compute(self, benchmark: Dict) -> Dict[str, float]: ...
    def _compute_class_imbalance(self, method_rankings: Dict) -> float: ...

class Tier2FeatureComputer:
    def compute(self, benchmark: Dict, domain: str) -> Dict[str, float]: ...
    def _compute_vision_features(self, benchmark: Dict) -> Dict: ...
    def _compute_nlp_features(self, benchmark: Dict) -> Dict: ...
    def _compute_tabular_features(self, benchmark: Dict) -> Dict: ...
    def _compute_graph_features(self, benchmark: Dict) -> Dict: ...

class FeatureAggregator:
    def __init__(self, tier1: Tier1FeatureComputer, tier2: Tier2FeatureComputer): ...
    def compute_all_features(self, benchmarks: List[Dict]) -> pd.DataFrame: ...
```

---

### 3. Correlation Analysis Module (`code/analyze_correlations.py`)

**Dependencies:** scipy.stats, pandas

```python
class SpearmanCorrelator:
    def __init__(self, alpha: float = 0.05, rho_threshold: float = 0.3): ...
    def compute_correlation_matrix(self, features_df: pd.DataFrame, rankings_df: pd.DataFrame) -> Dict: ...
    def _compute_pairwise_correlation(self, feature_values: np.ndarray, ranking_values: np.ndarray) -> Tuple[float, float]: ...
    def filter_significant_correlations(self, correlations: Dict) -> Dict: ...

class CorrelationReporter:
    def count_significant_pairs(self, correlations: Dict) -> int: ...
    def get_top_correlations(self, correlations: Dict, n: int = 5) -> List[Tuple]: ...
    def check_inverse_correlations(self, correlations: Dict) -> List[Tuple]: ...
    def generate_summary_stats(self, correlations: Dict) -> Dict: ...
```

---

### 4. Visualization Module (`code/visualize.py`)

**Dependencies:** matplotlib, seaborn, pandas

```python
def plot_gate_metrics_comparison(correlations: Dict, threshold: float, output_path: str): ...
def plot_correlation_heatmap(features_df: pd.DataFrame, rankings_df: pd.DataFrame, output_path: str): ...
def plot_significance_bars(correlations: Dict, p_threshold: float, output_path: str): ...
def plot_top_scatter_plots(features_df: pd.DataFrame, rankings_df: pd.DataFrame, top_pairs: List[Tuple], output_path: str): ...

def generate_all_figures(features_df: pd.DataFrame, rankings_df: pd.DataFrame, correlations: Dict, output_dir: str):
    plot_gate_metrics_comparison(correlations, 0.3, f"{output_dir}/gate_metrics.png")
    plot_correlation_heatmap(features_df, rankings_df, f"{output_dir}/heatmap.png")
    plot_significance_bars(correlations, 0.05, f"{output_dir}/significance.png")
    plot_top_scatter_plots(features_df, rankings_df, top_3_pairs, f"{output_dir}/scatter.png")
```

---

### 5. Orchestration Module (`code/run_analysis.py`)

**Dependencies:** All above modules, argparse

```python
class AnalysisOrchestrator:
    def __init__(self, config: Dict): ...
    def run(self) -> Tuple[Dict, Dict]: ...
    def _load_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]: ...
    def _compute_features(self, benchmarks: List[Dict]) -> pd.DataFrame: ...
    def _extract_rankings(self, benchmarks: List[Dict]) -> pd.DataFrame: ...
    def _run_correlation_analysis(self, features_df: pd.DataFrame, rankings_df: pd.DataFrame) -> Dict: ...
    def _generate_visualizations(self, features_df: pd.DataFrame, rankings_df: pd.DataFrame, correlations: Dict): ...
    def _save_results(self, correlations: Dict, summary: Dict): ...
    def _determine_gate_result(self, significant_count: int) -> str: ...

def main():
    config = {
        'h_e1_data_path': '../h-e1/code/output/benchmarks_collection.jsonl',
        'alpha': 0.05,
        'rho_threshold': 0.3,
        'output_dir': './output',
        'figures_dir': '../figures'
    }
    orchestrator = AnalysisOrchestrator(config)
    correlations, summary = orchestrator.run()
    print(f"Gate Result: {summary['gate_result']}")
```

---

## File Organization

```
h-m1/
├── code/
│   ├── load_data.py                  (H-E1 JSONL loader)
│   ├── compute_features.py           (Tier 1+2 feature computation)
│   ├── analyze_correlations.py       (Spearman correlation + significance tests)
│   ├── visualize.py                  (4 required figures)
│   ├── run_analysis.py               (Main orchestrator)
│   └── requirements.txt              (scipy, pandas, matplotlib, seaborn)
├── output/
│   ├── features.csv                  (63 × ~10 features)
│   ├── rankings.csv                  (63 × 4 method families)
│   ├── correlations.json             (Full correlation matrix)
│   └── summary_stats.json            (Gate decision + stats)
└── figures/
    ├── gate_metrics.png              (MANDATORY: Bar chart ρ vs threshold)
    ├── heatmap.png                   (Feature-method correlation matrix)
    ├── significance.png              (p-value bars)
    └── scatter.png                   (Top 3 feature-method scatter plots)
```

---

## Data Flow

1. **Load Phase:**
   - Read H-E1 JSONL: `../h-e1/code/output/benchmarks_collection.jsonl`
   - Parse 63 benchmark records
   - Extract method_rankings nested dict

2. **Feature Computation Phase:**
   - Tier 1 (all benchmarks): sample_size, dimensionality, num_classes, class_imbalance
   - Tier 2 (domain-specific): vision features, tabular features, etc.
   - Output: features_df (63 × ~10)

3. **Rankings Extraction Phase:**
   - Group method_rankings by family: Linear, RNN, Polynomial, Augmentation
   - Compute mean ranking_percentile per family per benchmark
   - Output: rankings_df (63 × 4)

4. **Correlation Phase:**
   - For each (feature, method_family) pair:
     - Compute Spearman ρ and p-value
     - Test significance: |ρ| > 0.3 AND p < 0.05
   - Output: correlations dict

5. **Reporting Phase:**
   - Count significant pairs
   - Identify top 5 correlations
   - Check for inverse correlations (ρ < -0.3)
   - Determine gate result (PASS/PARTIAL/FAIL)

6. **Visualization Phase:**
   - Generate 4 figures
   - Save to `../figures/`

---

## Configuration (STANDARD Tier)

**Hardcoded in `run_analysis.py`:**

```python
CONFIG = {
    # Data source
    'h_e1_data_path': '../h-e1/code/output/benchmarks_collection.jsonl',
    
    # Correlation thresholds
    'alpha': 0.05,           # p-value threshold
    'rho_threshold': 0.3,    # Spearman correlation threshold
    
    # Feature specification
    'tier1_features': ['sample_size', 'dimensionality', 'num_classes', 'class_imbalance'],
    'tier2_domains': ['vision', 'nlp', 'tabular', 'graph'],
    
    # Method families
    'method_families': ['Linear', 'RNN', 'Polynomial', 'Augmentation'],
    
    # Gate thresholds
    'min_significant_pairs': 3,
    'max_inverse_correlations': 0,
    
    # Output paths
    'output_dir': './output',
    'figures_dir': '../figures',
    
    # Visualization
    'figure_dpi': 300,
    'figure_format': 'png'
}
```

---

## Error Handling Strategy

**STANDARD Tier Approach:** Fail fast on critical errors, log warnings for non-critical issues

- **Missing H-E1 data:** Raise FileNotFoundError with actionable message
- **Incomplete features:** Log warning, compute with available data, mark NaN
- **Invalid rankings:** Skip method family, log warning
- **Numerical instability:** Catch scipy warnings, report in summary
- **Zero variance features:** Skip feature in correlation, log warning

**Logging:** Print statements + `analysis.log` file

```python
def safe_compute_correlation(feature_values, ranking_values, feature_name, method_name):
    try:
        if np.std(feature_values) == 0:
            print(f"WARNING: {feature_name} has zero variance, skipping")
            return None
        rho, p_value = spearmanr(feature_values, ranking_values)
        return {'rho': rho, 'p_value': p_value}
    except Exception as e:
        print(f"ERROR: Correlation failed for {feature_name} vs {method_name}: {e}")
        return None
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M1-1 | Setup Project Structure | Create folders, requirements.txt, validate H-E1 path | 4 | Size(1) + Deps(1) + Algo(0) + Integ(2) |
| M1-2 | Implement Data Loading | BenchmarkDataLoader with JSONL parsing and validation | 6 | Size(2) + Deps(1) + Algo(1) + Integ(2) |
| M1-3 | Implement Tier 1 Features | Tier1FeatureComputer with 4 universal features | 7 | Size(2) + Deps(1) + Algo(2) + Integ(2) |
| M1-4 | Implement Tier 2 Features | Tier2FeatureComputer with domain-specific logic | 9 | Size(3) + Deps(1) + Algo(3) + Integ(2) |
| M1-5 | Implement Rankings Extraction | Extract method families, compute mean percentiles | 6 | Size(2) + Deps(1) + Algo(1) + Integ(2) |
| M1-6 | Implement Correlation Analysis | SpearmanCorrelator with significance testing | 8 | Size(2) + Deps(2) + Algo(2) + Integ(2) |
| M1-7 | Implement Reporting Logic | CorrelationReporter with gate decision logic | 7 | Size(2) + Deps(1) + Algo(2) + Integ(2) |
| M1-8 | Implement Visualizations | 4 required plots with matplotlib/seaborn | 9 | Size(3) + Deps(2) + Algo(2) + Integ(2) |
| M1-9 | Orchestration and Integration | AnalysisOrchestrator connecting all modules | 10 | Size(2) + Deps(3) + Algo(2) + Integ(3) |

**Total Complexity:** 66
**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M1-4, M1-8, M1-9], Low(4-8): [M1-1, M1-2, M1-3, M1-5, M1-6, M1-7]

---

## Dependencies

**External Libraries:**
```
scipy>=1.7.0
pandas>=1.5.0
numpy>=1.21.0
matplotlib>=3.6.0
seaborn>=0.12.0
```

**Data Sources:**
- H-E1 Collection: `../h-e1/code/output/benchmarks_collection.jsonl` (MUST exist)

**Internal Dependencies:**
- Verification State: Check H-E1 status = COMPLETED before running

---

## Success Criteria

**Quantitative Metrics:**
1. Significant correlations count ≥ 3
2. All correlations have p < 0.05
3. No inverse correlations (ρ < -0.3, p < 0.05)

**Validation Logic:**
```python
significant_count = sum(1 for r in correlations.values() if r['significant'])

if significant_count >= 3:
    gate_result = "PASS"
elif significant_count >= 1:
    gate_result = "PARTIAL"
else:
    gate_result = "FAIL"
```

**Output:**
- `correlations.json` - Full correlation matrix
- `summary_stats.json` - Gate decision + statistics
- 4 figure files in `../figures/`

**Gate Decision:**
- PASS (≥3): Proceed to H-M2 (meta-classifier training)
- PARTIAL (1-2): Explore Tier 3 features or simpler model
- FAIL (0): Mechanism hypothesis invalid

---

## Implementation Notes

**Recommended Development Order:**
1. M1-1: Setup (folders, requirements.txt)
2. M1-2: Data loading (validate H-E1 integration)
3. M1-3: Tier 1 features (test with 5 benchmarks)
4. M1-5: Rankings extraction (validate family grouping)
5. M1-6: Correlation analysis (core mechanism test)
6. M1-7: Reporting (gate decision logic)
7. M1-4: Tier 2 features (if Tier 1 insufficient)
8. M1-8: Visualizations (after correlation works)
9. M1-9: Final orchestration (integration test)

**Key Design Constraints:**
- STANDARD tier: Hardcoded config in run_analysis.py, no YAML
- Runtime: <5 minutes total (feature computation dominates)
- No parallelization needed (63 benchmarks is small)
- Deterministic output (no randomness in correlation)

**Phase 4 Execution:**
```bash
cd h-m1/code
pip install -r requirements.txt
python run_analysis.py
```

**Expected Output:**
```
Loading 63 benchmarks from H-E1...
Computing Tier 1 features... [63/63]
Computing Tier 2 features... [45/63] (18 skipped - missing domain data)
Extracting method rankings... [63/63]
Computing correlations... [~40 pairs]
Significant correlations found: 5
Gate Result: PASS
Figures saved to ../figures/
```

---

**Document Status:** Ready for Implementation (Phase 4)
**Next Step:** Phase 4 Coder Agent - Implement correlation analysis pipeline
