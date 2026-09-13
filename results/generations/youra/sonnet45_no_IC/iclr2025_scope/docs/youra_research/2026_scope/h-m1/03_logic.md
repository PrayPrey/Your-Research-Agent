# Logic Design: H-M1 Feature-Ranking Correlation Analysis

**Date:** 2026-07-13
**Hypothesis:** H-M1 (MECHANISM)
**Type:** Statistical Correlation Analysis
**Tier:** STANDARD (Data processing pipeline)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** API signatures verified from H-E1 implementation
**Analyzed Path:** `docs/youra_research/h-e1/code/`
**Relevant Symbols:** `collect_benchmarks.py:parse_manual_csv()`, `collect_benchmarks.py:validate_collection()`

**Key Findings:**
- H-E1 generates JSONL with schema: `{benchmark_id, dataset_name, domain, sample_size, dimensionality, num_classes, method_rankings}`
- Method rankings structure: `{method_name: {family, accuracy, ranking_percentile}}`
- Family classification logic: Lines 72-79 in collect_benchmarks.py (Linear, RNN, Polynomial, Augmentation)
- Output path: `h-e1/code/output/benchmarks_collection.jsonl`

---

## Applied Patterns

**Applied:** Sequential Data Processing Pipeline with DataFrame Operations
- Pattern: Load JSONL → Compute features → Extract rankings → Correlate → Report
- Analysis: scipy.stats.spearmanr for rank correlation with significance testing
- Visualization: matplotlib/seaborn for heatmaps and scatter plots

---

## M1-9: Orchestration Logic (Complexity: 10, Budget: 2)

### API Signatures

```python
from typing import Dict, List, Tuple, Literal
from pathlib import Path
import json
import pandas as pd

class AnalysisOrchestrator:
    """Orchestrate complete correlation analysis pipeline."""
    
    def __init__(self, config: Dict):
        """Initialize with hardcoded config."""
        self.config = config
        self.loader = None
        self.feature_computer = None
        self.correlator = None
        self.reporter = None
    
    def run(self) -> Tuple[Dict, Dict]:
        """Execute full pipeline. Returns: (correlations, summary)"""
        ...
    
    def _load_data(self) -> List[Dict]:
        """Load H-E1 JSONL. Returns: [benchmark_records]"""
        ...
    
    def _compute_features(self, benchmarks: List[Dict]) -> pd.DataFrame:
        """Compute Tier 1+2 features. Returns: (63, ~10) DataFrame"""
        ...
    
    def _extract_rankings(self, benchmarks: List[Dict]) -> pd.DataFrame:
        """Extract method family rankings. Returns: (63, 4) DataFrame"""
        ...
    
    def _run_correlation_analysis(
        self, 
        features_df: pd.DataFrame, 
        rankings_df: pd.DataFrame
    ) -> Dict:
        """Compute Spearman correlations. Returns: correlations dict"""
        ...
    
    def _generate_visualizations(
        self, 
        features_df: pd.DataFrame, 
        rankings_df: pd.DataFrame, 
        correlations: Dict
    ):
        """Generate 4 required figures."""
        ...
    
    def _save_results(self, correlations: Dict, summary: Dict):
        """Save JSON results and summary."""
        ...
    
    def _determine_gate_result(
        self, 
        significant_count: int
    ) -> Literal["PASS", "PARTIAL", "FAIL"]:
        """Gate decision based on significant pairs count."""
        if significant_count >= 3:
            return "PASS"
        elif significant_count >= 1:
            return "PARTIAL"
        else:
            return "FAIL"


def main():
    """Entry point for correlation analysis."""
    config = {
        'h_e1_data_path': '../h-e1/code/output/benchmarks_collection.jsonl',
        'alpha': 0.05,
        'rho_threshold': 0.3,
        'output_dir': './output',
        'figures_dir': '../figures'
    }
    
    orchestrator = AnalysisOrchestrator(config)
    correlations, summary = orchestrator.run()
    
    print(f"\nGate Result: {summary['gate_result']}")
    print(f"Significant Correlations: {summary['significant_count']}")
    return 0 if summary['gate_result'] == "PASS" else 1
```

### Data Flow Shapes

```python
# 1. Load: JSONL → List[Dict]
benchmarks: List[Dict]  # Length: 63

# 2. Features: List[Dict] → DataFrame
features_df: pd.DataFrame  # Shape: (63, ~10)

# 3. Rankings: List[Dict] → DataFrame
rankings_df: pd.DataFrame  # Shape: (63, 4)

# 4. Correlations: (features_df, rankings_df) → Dict
correlations: Dict[str, Dict]  # ~40 feature-method pairs

# 5. Summary: correlations → Dict
summary: Dict  # {significant_count, gate_result, top_pairs}
```

### Pseudo-code

```
run():
    1. benchmarks = _load_data()
    2. features_df = _compute_features(benchmarks)
    3. rankings_df = _extract_rankings(benchmarks)
    4. correlations = _run_correlation_analysis(features_df, rankings_df)
    5. _generate_visualizations(features_df, rankings_df, correlations)
    6. summary = _build_summary(correlations)
    7. _save_results(correlations, summary)
    8. return correlations, summary

_load_data():
    with open(config['h_e1_data_path']) as f:
        return [json.loads(line) for line in f]

_compute_features(benchmarks):
    tier1_computer = Tier1FeatureComputer()
    tier2_computer = Tier2FeatureComputer()
    rows = []
    for b in benchmarks:
        tier1_features = tier1_computer.compute(b)
        tier2_features = tier2_computer.compute(b, b['domain'])
        row = {**tier1_features, **tier2_features}
        rows.append(row)
    return pd.DataFrame(rows, index=[b['benchmark_id'] for b in benchmarks])

_extract_rankings(benchmarks):
    rows = []
    for b in benchmarks:
        family_percentiles = {}
        for method, data in b['method_rankings'].items():
            family = data['family']
            percentile = data['ranking_percentile']
            if family not in family_percentiles:
                family_percentiles[family] = []
            family_percentiles[family].append(percentile)
        row = {f: sum(v)/len(v) for f, v in family_percentiles.items()}
        rows.append(row)
    return pd.DataFrame(rows, index=[b['benchmark_id'] for b in benchmarks])

_run_correlation_analysis(features_df, rankings_df):
    correlator = SpearmanCorrelator(
        alpha=config['alpha'], 
        rho_threshold=config['rho_threshold']
    )
    return correlator.compute_correlation_matrix(features_df, rankings_df)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-9-1 | Pipeline Orchestration | Sequential execution with error handling and progress logging |
| L-9-2 | Gate Decision Logic | Validation criteria and gate result determination |

---

## M1-6: Correlation Analysis (Complexity: 8)

### API Signatures

```python
from scipy.stats import spearmanr
import numpy as np

class SpearmanCorrelator:
    """Compute Spearman correlations with significance testing."""
    
    def __init__(self, alpha: float = 0.05, rho_threshold: float = 0.3):
        """Initialize thresholds."""
        self.alpha = alpha
        self.rho_threshold = rho_threshold
    
    def compute_correlation_matrix(
        self, 
        features_df: pd.DataFrame, 
        rankings_df: pd.DataFrame
    ) -> Dict[str, Dict]:
        """
        Compute all pairwise correlations.
        features_df: (63, ~10), rankings_df: (63, 4)
        Returns: {pair_name: {rho, p_value, significant}}
        """
        ...
    
    def _compute_pairwise_correlation(
        self, 
        feature_values: np.ndarray, 
        ranking_values: np.ndarray,
        feature_name: str,
        method_name: str
    ) -> Dict:
        """Compute single correlation with error handling."""
        ...
    
    def filter_significant_correlations(self, correlations: Dict) -> Dict:
        """Filter to significant pairs only."""
        return {
            k: v for k, v in correlations.items() 
            if v['significant']
        }


class CorrelationReporter:
    """Generate reports from correlation results."""
    
    def count_significant_pairs(self, correlations: Dict) -> int:
        """Count pairs with |rho| > threshold AND p < alpha."""
        return sum(1 for v in correlations.values() if v['significant'])
    
    def get_top_correlations(
        self, 
        correlations: Dict, 
        n: int = 5
    ) -> List[Tuple[str, float, float]]:
        """Get top N by |rho|. Returns: [(pair_name, rho, p_value)]"""
        ...
    
    def check_inverse_correlations(self, correlations: Dict) -> List[Tuple]:
        """Find significant negative correlations (rho < -0.3, p < 0.05)."""
        ...
    
    def generate_summary_stats(self, correlations: Dict) -> Dict:
        """Compute mean |rho|, median p-value, etc."""
        ...
```

### Pseudo-code

```
compute_correlation_matrix(features_df, rankings_df):
    results = {}
    for feature_col in features_df.columns:
        feature_values = features_df[feature_col].values
        if np.std(feature_values) == 0:
            continue
        for method_col in rankings_df.columns:
            ranking_values = rankings_df[method_col].values
            if np.isnan(feature_values).sum() > 10:
                continue
            pair_name = f"{feature_col}_vs_{method_col}"
            result = _compute_pairwise_correlation(
                feature_values, ranking_values, feature_col, method_col
            )
            if result is not None:
                results[pair_name] = result
    return results

_compute_pairwise_correlation(feature_values, ranking_values, feature_name, method_name):
    mask = ~(np.isnan(feature_values) | np.isnan(ranking_values))
    x = feature_values[mask]
    y = ranking_values[mask]
    if len(x) < 10:
        return None
    try:
        rho, p_value = spearmanr(x, y)
        significant = (abs(rho) > self.rho_threshold) and (p_value < self.alpha)
        return {
            'rho': round(rho, 3),
            'p_value': round(p_value, 4),
            'significant': significant,
            'n_samples': len(x)
        }
    except Exception as e:
        print(f"Error computing {feature_name} vs {method_name}: {e}")
        return None
```

---

## M1-3: Tier 1 Features (Complexity: 7)

### API Signatures

```python
class Tier1FeatureComputer:
    """Compute universal dataset features."""
    
    FEATURES = ['sample_size', 'dimensionality', 'num_classes', 'class_imbalance']
    
    def compute(self, benchmark: Dict) -> Dict[str, float]:
        """
        Extract Tier 1 features. benchmark: Single H-E1 record
        Returns: {feature_name: value}
        """
        return {
            'sample_size': self._safe_int(benchmark.get('sample_size')),
            'dimensionality': self._safe_int(benchmark.get('dimensionality')),
            'num_classes': self._safe_int(benchmark.get('num_classes')),
            'class_imbalance': self._compute_class_imbalance(benchmark)
        }
    
    def _safe_int(self, value) -> float:
        """Convert to float, return NaN if invalid."""
        ...
    
    def _compute_class_imbalance(self, benchmark: Dict) -> float:
        """Compute Gini coefficient from method rankings. Returns: 0.0-1.0 or NaN"""
        ...
```

### Pseudo-code

```
_compute_class_imbalance(benchmark):
    method_rankings = benchmark.get('method_rankings', {})
    if len(method_rankings) < 3:
        return float('nan')
    accuracies = [m['accuracy'] for m in method_rankings.values()]
    n = len(accuracies)
    sorted_acc = sorted(accuracies)
    cumsum = 0
    for i, acc in enumerate(sorted_acc):
        cumsum += (n - i) * acc
    gini = (2 * cumsum) / (n * sum(accuracies)) - (n + 1) / n
    return round(gini, 3)
```

---

## M1-4: Tier 2 Features (Complexity: 9)

### API Signatures

```python
class Tier2FeatureComputer:
    """Compute domain-specific features."""
    
    DOMAIN_HANDLERS = {
        'vision': '_compute_vision_features',
        'graph': '_compute_graph_features',
        'tabular': '_compute_tabular_features',
        'time-series': '_compute_timeseries_features'
    }
    
    def compute(self, benchmark: Dict, domain: str) -> Dict[str, float]:
        """
        Compute domain-specific features.
        domain: 'vision' | 'graph' | 'tabular' | 'time-series' | 'federated-learning'
        Returns: {feature_name: value} or {} if domain unsupported
        """
        handler = self.DOMAIN_HANDLERS.get(domain)
        if handler is None:
            return {}
        return getattr(self, handler)(benchmark)
    
    def _compute_vision_features(self, benchmark: Dict) -> Dict:
        """Vision features: image_resolution, channel_count."""
        ...
    
    def _compute_graph_features(self, benchmark: Dict) -> Dict:
        """Graph features: edge_density, avg_degree."""
        ...
    
    def _compute_tabular_features(self, benchmark: Dict) -> Dict:
        """Tabular features: feature_variance, categorical_ratio."""
        ...
    
    def _compute_timeseries_features(self, benchmark: Dict) -> Dict:
        """Time-series features: sequence_length, seasonality."""
        ...
```

---

## M1-8: Visualization (Complexity: 9)

### API Signatures

```python
import matplotlib.pyplot as plt
import seaborn as sns

def plot_gate_metrics_comparison(
    correlations: Dict, 
    threshold: float, 
    output_path: str
):
    """Figure 1: Bar chart of top 5 correlations vs threshold."""
    ...

def plot_correlation_heatmap(
    features_df: pd.DataFrame, 
    rankings_df: pd.DataFrame, 
    output_path: str
):
    """Figure 2: Feature-method correlation heatmap."""
    ...

def plot_significance_bars(
    correlations: Dict, 
    p_threshold: float, 
    output_path: str
):
    """Figure 3: p-value bar chart for top 10 pairs."""
    ...

def plot_top_scatter_plots(
    features_df: pd.DataFrame, 
    rankings_df: pd.DataFrame, 
    top_pairs: List[Tuple], 
    output_path: str
):
    """Figure 4: 3 scatter plots for top correlations."""
    ...
```

### Pseudo-code

```
plot_gate_metrics_comparison(correlations, threshold, output_path):
    top_5 = sorted(correlations.items(), key=lambda x: abs(x[1]['rho']), reverse=True)[:5]
    pairs = [k for k, v in top_5]
    rhos = [v['rho'] for k, v in top_5]
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(pairs, rhos)
    ax.axvline(threshold, color='red', linestyle='--', label=f'Threshold ({threshold})')
    ax.set_xlabel('Spearman ρ')
    ax.set_title('Top 5 Feature-Method Correlations vs Threshold')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()

plot_correlation_heatmap(features_df, rankings_df, output_path):
    corr_matrix = np.zeros((len(features_df.columns), len(rankings_df.columns)))
    for i, feature in enumerate(features_df.columns):
        for j, method in enumerate(rankings_df.columns):
            rho, _ = spearmanr(features_df[feature], rankings_df[method], nan_policy='omit')
            corr_matrix[i, j] = rho
    fig, ax = plt.subplots(figsize=(8, 10))
    sns.heatmap(
        corr_matrix, 
        xticklabels=rankings_df.columns,
        yticklabels=features_df.columns,
        annot=True, fmt='.2f', cmap='RdBu_r', center=0,
        vmin=-1, vmax=1, ax=ax
    )
    ax.set_title('Feature-Method Correlation Matrix')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
```

---

## External Dependencies API (H-E1)

### Data Schema (From Actual Code)

```python
# From: h-e1/code/output/benchmarks_collection.jsonl
# Verified from: h-e1/code/collect_benchmarks.py

# JSONL Record Structure (lines 92-103)
{
    "benchmark_id": str,              # e.g., "ogb_ogbn-arxiv", "champ_01"
    "dataset_name": str,              # e.g., "ogbn-arxiv", "CIFAR-10"
    "domain": str,                    # "vision" | "graph" | "time-series" | "tabular" | "federated-learning"
    "sample_size": int | None,        # Total samples, may be None
    "dimensionality": int | None,     # Feature count, may be None
    "num_classes": str | None,        # Number of classes as string, may be None
    "method_rankings": {
        "MethodName": {
            "family": str,            # "Linear" | "RNN" | "Polynomial" | "Augmentation"
            "accuracy": float,        # 0.0 to 1.0
            "ranking_percentile": float  # 0.0 to 100.0
        }
    },
    "source_paper": str,
    "year": int,
    "verified_real_source": bool      # Optional
}
```

### Method Family Classification (From Actual Code)

```python
# From: h-e1/code/collect_benchmarks.py:72-79
# VERIFIED parameter names from actual implementation

def classify_method_family(method_name: str) -> str:
    """
    Classify method into family based on name patterns.
    Returns: "Linear" | "RNN" | "Polynomial" | "Augmentation"
    """
    method_lower = method_name.lower()
    if any(kw in method_lower for kw in ['linear', 'lr', 'logistic', 'fedavg', 'fedprox']):
        return 'Linear'
    elif any(kw in method_lower for kw in ['lstm', 'rnn', 'gru', 'temporal']):
        return 'RNN'
    elif any(kw in method_lower for kw in ['resnet', 'vgg', 'cnn', 'conv']):
        return 'Polynomial'
    else:
        return 'Augmentation'
```

**Verified from:** `h-e1/code/collect_benchmarks.py` (actual implementation)

**Critical Note:** `num_classes` is stored as string in JSONL. H-M1 must handle string-to-int conversion.

---

## Error Handling Strategy

### Data Validation

```python
def safe_load_benchmarks(jsonl_path: str) -> List[Dict]:
    """Load JSONL with error handling."""
    benchmarks = []
    with open(jsonl_path) as f:
        for i, line in enumerate(f, 1):
            try:
                record = json.loads(line)
                benchmarks.append(record)
            except json.JSONDecodeError as e:
                print(f"Line {i}: JSON parse error - {e}")
                continue
    print(f"Loaded {len(benchmarks)} benchmarks")
    return benchmarks
```

### Correlation Error Handling

```python
# In SpearmanCorrelator._compute_pairwise_correlation()
mask = ~(np.isnan(feature_values) | np.isnan(ranking_values))
x = feature_values[mask]
y = ranking_values[mask]

if len(x) < 10:
    print(f"Skipping {pair_name}: only {len(x)} valid samples")
    return None

if np.std(x) == 0 or np.std(y) == 0:
    print(f"Skipping {pair_name}: zero variance")
    return None

try:
    rho, p_value = spearmanr(x, y)
    return {'rho': rho, 'p_value': p_value, 'significant': ...}
except Exception as e:
    print(f"ERROR: {pair_name} correlation failed - {e}")
    return None
```

---

## Validation Criteria

### Gate Decision Logic

```python
significant_count = sum(1 for v in correlations.values() if v['significant'])

if significant_count >= 3:
    gate_result = "PASS"
    print("✓ PASS: Mechanism hypothesis validated")
elif significant_count >= 1:
    gate_result = "PARTIAL"
    print("⚠ PARTIAL: Weak correlation detected")
else:
    gate_result = "FAIL"
    print("✗ FAIL: No significant correlation")
```

### Success Thresholds

```python
SUCCESS_CRITERIA = {
    'min_significant_pairs': 3,
    'rho_threshold': 0.3,
    'alpha': 0.05,
    'max_inverse_correlations': 0
}
```

---

## Implementation Notes

### Execution Order

1. Install: `pip install scipy pandas numpy matplotlib seaborn`
2. Run: `python code/run_analysis.py`
3. Expected output:
```
Loading 63 benchmarks from H-E1...
Computing Tier 1 features... [63/63]
Computing Tier 2 features... [45/63]
Extracting method rankings... [63/63]
Computing correlations... [40 pairs]
Significant correlations found: 5
Gate Result: PASS
```

### STANDARD Tier Constraints

- Configuration: Hardcoded in `main()` (no YAML)
- Logging: Print statements only
- Testing: Manual validation (no pytest)
- Runtime: <5 minutes total

---

**Document Status:** Ready for Implementation (Phase 4)
**Next Phase:** Phase 4 Coder - Implement correlation analysis pipeline
