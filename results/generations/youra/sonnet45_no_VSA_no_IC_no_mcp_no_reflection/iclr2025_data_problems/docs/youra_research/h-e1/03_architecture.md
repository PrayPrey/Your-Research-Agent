# Architecture Specification
# Hypothesis H-E1: Data Quality Metrics Correlation Study

**Version**: 1.0  
**Created**: 2026-08-28  
**Hypothesis ID**: h-e1  
**Type**: EXISTENCE (PoC)

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New implementation from scratch  
**Analyzed Path**: N/A  
**Findings**: No existing code to analyze

---

## Design Patterns Applied

Applied: Minimal PoC structure (EXISTENCE hypothesis pattern)

---

## Module Structure

### DataPreparation (`data/prepare_subsets.py`)

**Dependencies**: datasets, transformers

```python
class C4SubsetSampler:
    def __init__(self, output_dir: str, subset_size_gb: int = 10): ...
    def sample_subset(self, dimension: str, level: str) -> str: ...
    def generate_all_subsets(self) -> List[str]: ...

def apply_dedup(text: List[str], ratio: float) -> List[str]: ...
def apply_domain_filter(text: List[str], diversity: str) -> List[str]: ...
def apply_perplexity_filter(text: List[str], threshold: str) -> List[str]: ...
def apply_token_cleaning(text: List[str], level: str) -> List[str]: ...
```

---

### QualityMetrics (`metrics/quality.py`)

**Dependencies**: transformers, torch

```python
class QualityMetricsComputer:
    def __init__(self, model_name: str = "gpt2"): ...
    def compute_dedup_ratio(self, text: List[str]) -> float: ...
    def compute_domain_diversity(self, urls: List[str]) -> float: ...
    def compute_perplexity(self, text: List[str]) -> float: ...
    def compute_token_efficiency(self, text: List[str]) -> float: ...
    def compute_all(self, subset_path: str) -> dict: ...
```

---

### InformationDensity (`metrics/density.py`)

**Dependencies**: sentence_transformers, scipy, zlib

```python
class InformationDensityComputer:
    def __init__(self, embedder_name: str = "all-MiniLM-L6-v2"): ...
    def compute_token_entropy(self, text: List[str]) -> float: ...
    def compute_ngram_redundancy(self, text: List[str]) -> float: ...
    def compute_semantic_diversity(self, text: List[str]) -> float: ...
    def compute_combined_density(self, text: List[str]) -> float: ...
```

---

### CorrelationAnalysis (`analysis/correlate.py`)

**Dependencies**: scipy, pandas

```python
def compute_pearson(x: np.ndarray, y: np.ndarray) -> Tuple[float, float]: ...
def compute_spearman(x: np.ndarray, y: np.ndarray) -> Tuple[float, float]: ...
def correlate_all_components(metrics_df: pd.DataFrame) -> pd.DataFrame: ...
def save_results(results: pd.DataFrame, path: str): ...
```

---

### Visualization (`analysis/plot.py`)

**Dependencies**: matplotlib, seaborn

```python
def plot_scatter(x: np.ndarray, y: np.ndarray, title: str, save_path: str): ...
def add_regression_line(ax, x: np.ndarray, y: np.ndarray): ...
def generate_all_plots(metrics_df: pd.DataFrame, output_dir: str): ...
```

---

### Main Pipeline (`run_experiment.py`)

**Dependencies**: All above modules

```python
def main():
    # 1. Generate 12 C4 subsets
    # 2. Compute quality metrics
    # 3. Compute information density
    # 4. Run correlation analysis
    # 5. Generate plots
    # 6. Save results
```

---

## File Structure

```
h-e1/
├── code/
│   ├── data/
│   │   └── prepare_subsets.py
│   ├── metrics/
│   │   ├── quality.py
│   │   └── density.py
│   ├── analysis/
│   │   ├── correlate.py
│   │   └── plot.py
│   └── run_experiment.py
├── data/
│   ├── subsets/            # 12 × 10GB JSONL files
│   └── subset_metadata.yaml
├── results/
│   ├── metrics_results.csv
│   ├── correlation_results.csv
│   └── plots/              # 4 scatter PNGs
└── config.yaml
```

---

## Configuration Schema

```yaml
dataset:
  name: "allenai/c4"
  split: "en"
  subset_size_gb: 10
  num_subsets: 12

quality_metrics:
  ngram_size: 13
  perplexity_model: "gpt2"
  batch_size: 128

density_metrics:
  embedder_model: "all-MiniLM-L6-v2"
  sample_size: 1000

correlation:
  success_threshold_r: 0.5
  significance_threshold_p: 0.01
  variance_threshold_cv: 0.10

compute:
  device: "cuda"
  seed: 42
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E-1 | Setup & Data | Download C4, generate 12 subsets, validate | 8 | 2+2+2+2 (download+transform+validate+metadata) |
| E-2 | Quality Metrics | Implement Q(D) components, batch compute | 9 | 3+2+2+2 (4 metrics+integration+batching+save) |
| E-3 | Density Metrics | Implement entropy/redundancy/semantic, aggregate | 10 | 3+3+2+2 (entropy+semantic+redundancy+combine) |
| E-4 | Correlation Analysis | Pearson/Spearman, scatter plots, baselines | 11 | 3+3+3+2 (tests+plots+baselines+save) |
| E-5 | Validation | Reproducibility test, ablations, gate check | 8 | 2+3+2+1 (resample+ablate+variance+gate) |

**Distribution**: High(9-12): [E-3, E-4], Medium(7-9): [E-1, E-2, E-5]

**Complexity Scores**:
- E-1: Module_Size(2) + Dependencies(2) + Algorithm(2) + Integration(2) = 8
- E-2: Module_Size(3) + Dependencies(2) + Algorithm(2) + Integration(2) = 9
- E-3: Module_Size(3) + Dependencies(3) + Algorithm(2) + Integration(2) = 10
- E-4: Module_Size(3) + Dependencies(3) + Algorithm(3) + Integration(2) = 11
- E-5: Module_Size(2) + Dependencies(3) + Algorithm(2) + Integration(1) = 8

---

## Data Flow

```
C4 Dataset
  → SubsetSampler (12 controlled subsets)
    → QualityMetricsComputer (4 Q(D) values per subset)
    → InformationDensityComputer (1 combined score per subset)
      → CorrelationAnalysis (Pearson/Spearman r, p)
        → Visualization (4 scatter plots)
          → Gate Decision (PASS/PARTIAL/FAIL)
```

---

## Success Criteria Implementation

```python
def check_gate(correlation_results: pd.DataFrame) -> str:
    """MUST_WORK gate decision logic."""
    passing_components = 0
    
    for component in ['dedup', 'diversity', 'perplexity', 'efficiency']:
        r = correlation_results.loc[component, 'pearson_r']
        p = correlation_results.loc[component, 'p_value']
        rho = correlation_results.loc[component, 'spearman_rho']
        
        if r > 0.5 and p < 0.01 and rho > 0.5:
            passing_components += 1
    
    if passing_components >= 4:
        return "PASS"
    elif passing_components >= 2:
        return "PARTIAL"
    else:
        return "FAIL"
```

---

## Risk Mitigations

**GPU Memory**: Batch perplexity computation (128 sentences/batch)  
**C4 Download**: Cache locally, retry on failure  
**Reproducibility**: Fixed seed=42, deterministic ops  
**Small Sample**: Bootstrap CI (1000 iterations) for correlation stability

---

## External Dependencies

```
torch>=2.0
transformers>=4.30
datasets
sentence-transformers
scipy
numpy
pandas
matplotlib
seaborn
```

---

**END OF ARCHITECTURE**
