# Architecture Design: H-M2 Coupling Generalization Validator

**Date:** 2026-08-19  
**Hypothesis:** H-M2 (MECHANISM - Generalization Breadth)  
**Version:** 1.0

---

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    H-M2 Analysis Pipeline                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Data Layer           2. Evaluation Layer                 │
│  ┌─────────────┐        ┌──────────────────┐               │
│  │ TrustLLM    │───────▶│ Model Evaluator  │               │
│  │ Loader      │        │ (API Clients)    │               │
│  └─────────────┘        └──────────────────┘               │
│         │                        │                          │
│         ▼                        ▼                          │
│  ┌─────────────┐        ┌──────────────────┐               │
│  │ Stratified  │        │ Binary Labels    │               │
│  │ Sampler     │        │ (500×5×3 matrix) │               │
│  └─────────────┘        └──────────────────┘               │
│                                  │                          │
│                                  ▼                          │
│  3. Statistical Layer    ┌──────────────────┐               │
│                          │ Phi Coefficient  │               │
│                          │ Computer         │               │
│                          └──────────────────┘               │
│                                  │                          │
│                                  ▼                          │
│                          ┌──────────────────┐               │
│                          │ Multiple Testing │               │
│                          │ Corrector        │               │
│                          └──────────────────┘               │
│                                  │                          │
│                                  ▼                          │
│  4. Decision Layer       ┌──────────────────┐               │
│                          │ Pair Counter     │               │
│                          └──────────────────┘               │
│                                  │                          │
│                                  ▼                          │
│                          ┌──────────────────┐               │
│                          │ Gate Evaluator   │               │
│                          └──────────────────┘               │
│                                  │                          │
│                                  ▼                          │
│  5. Visualization Layer  ┌──────────────────┐               │
│                          │ Heatmap Plotter  │               │
│                          │ Chart Generator  │               │
│                          └──────────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Specifications

### 1. Data Layer

#### 1.1 TrustLLM Loader (`src/data_loader.py`)

**Responsibility:** Download and cache TrustLLM dataset

**Interface:**
```python
def load_trustllm_dataset(cache_dir: str = "data/trustllm_cache") -> Dict[str, pd.DataFrame]:
    """
    Load TrustLLM dataset from Huggingface.
    
    Returns:
        Dict mapping dimension names to DataFrames:
        {
            'truthfulness': DataFrame(~800 rows),
            'safety': DataFrame(~600 rows),
            'fairness': DataFrame(~500 rows),
            'robustness': DataFrame(~500 rows),
            'privacy': DataFrame(~676 rows)
        }
    """
```

**Dependencies:** datasets (Huggingface)

**Error Handling:**
- Retry download 3 times with exponential backoff (1s, 2s, 4s)
- Raise `DatasetDownloadError` if all retries fail

---

#### 1.2 Stratified Sampler (`src/data_loader.py`)

**Responsibility:** Generate balanced 500-instance sample

**Interface:**
```python
def stratified_sample(
    dataset: Dict[str, pd.DataFrame],
    n_per_dimension: int = 100,
    seed: int = 42
) -> pd.DataFrame:
    """
    Sample n_per_dimension instances from each dimension.
    
    Args:
        dataset: Dict of dimension DataFrames
        n_per_dimension: Instances per dimension (default: 100)
        seed: Random seed for reproducibility
    
    Returns:
        DataFrame with columns: [instance_id, dimension, prompt, expected_label]
        Shape: (500, 4) for 100 instances × 5 dimensions
    """
```

**Sampling Strategy:**
- Use pandas.DataFrame.sample(n=n_per_dimension, random_state=seed)
- Stratified within each dimension (no cross-dimension balancing needed)

---

### 2. Evaluation Layer

#### 2.1 Model Evaluator (`src/model_evaluator.py`)

**Responsibility:** Query 3 models via API and generate binary labels

**Interface:**
```python
class ModelEvaluator:
    def __init__(self, model_name: str, api_key: str):
        """Initialize API client for model."""
        
    def evaluate_instance(self, prompt: str, dimension: str) -> int:
        """
        Evaluate single instance.
        
        Returns:
            0 (fail) or 1 (pass) based on TrustLLM criteria
        """
        
    def evaluate_batch(
        self, 
        instances: pd.DataFrame, 
        checkpoint_path: str = None
    ) -> pd.DataFrame:
        """
        Evaluate batch of instances with checkpointing.
        
        Args:
            instances: DataFrame from stratified_sample()
            checkpoint_path: Path to save progress every 50 instances
        
        Returns:
            DataFrame with added 'label' column (binary 0/1)
        """
```

**API Clients:**
- `GPT4Evaluator(ModelEvaluator)` - OpenAI API
- `ClaudeEvaluator(ModelEvaluator)` - Anthropic API
- `LlamaEvaluator(ModelEvaluator)` - Together API

**Parallelism:**
- Async batch processing: 10 concurrent requests per model
- Use asyncio.gather() for parallel API calls

**Checkpointing:**
- Save progress every 50 instances to `{checkpoint_path}`
- Resume from checkpoint on script restart (skip already-evaluated instances)

---

### 3. Statistical Layer

#### 3.1 Phi Coefficient Computer (`src/phi_analysis.py`)

**Responsibility:** Compute phi coefficient for dimension pairs

**Interface:**
```python
def compute_phi_coefficient(
    dim1_labels: np.ndarray,
    dim2_labels: np.ndarray
) -> Tuple[float, float, np.ndarray]:
    """
    Compute phi coefficient and p-value.
    
    Args:
        dim1_labels: Binary array (n=500)
        dim2_labels: Binary array (n=500)
    
    Returns:
        phi: Phi coefficient [0, 1]
        p_value: Chi-square test p-value
        table: 2×2 contingency table
    
    Raises:
        AssertionError: If expected cell counts < 5 (chi-square assumption violated)
    """
```

**Implementation:**
```python
from scipy.stats import chi2_contingency

table = np.array([
    [np.sum((dim1 == 1) & (dim2 == 1)), np.sum((dim1 == 1) & (dim2 == 0))],
    [np.sum((dim1 == 0) & (dim2 == 1)), np.sum((dim1 == 0) & (dim2 == 0))]
])

chi2, p_value, dof, expected = chi2_contingency(table)
assert (expected >= 5).all(), "Chi-square assumption violated: expected counts < 5"

phi = np.sqrt(chi2 / table.sum())
return phi, p_value, table
```

---

#### 3.2 Multiple Testing Corrector (`src/phi_analysis.py`)

**Responsibility:** Apply Bonferroni correction to 30 p-values

**Interface:**
```python
def apply_bonferroni_correction(
    p_values: List[float],
    alpha: float = 0.01
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Apply Bonferroni correction.
    
    Args:
        p_values: List of 30 p-values (10 pairs × 3 models)
        alpha: Significance level (default: 0.01)
    
    Returns:
        p_adjusted: Bonferroni-adjusted p-values
        reject: Boolean array (True if p_adjusted < alpha)
    """
```

**Implementation:**
```python
from statsmodels.stats.multitest import multipletests

reject, p_adjusted, _, _ = multipletests(p_values, alpha=alpha, method='bonferroni')
return p_adjusted, reject
```

---

### 4. Decision Layer

#### 4.1 Pair Counter (`src/phi_analysis.py`)

**Responsibility:** Count significant pairs per model

**Interface:**
```python
def count_significant_pairs(
    coupling_results: List[Dict],
    phi_threshold: float = 0.3,
    use_adjusted_p: bool = True
) -> Dict[str, int]:
    """
    Count dimension pairs meeting significance criteria per model.
    
    Args:
        coupling_results: List of dicts with keys:
            ['model', 'dim1', 'dim2', 'phi', 'p_value', 'p_adjusted', 'significant']
        phi_threshold: Minimum phi coefficient (default: 0.3)
        use_adjusted_p: Use p_adjusted (Bonferroni) vs p_value (default: True)
    
    Returns:
        {model_name: count_of_significant_pairs}
    """
```

**Implementation:**
```python
counts = {}
for r in coupling_results:
    if r['phi'] >= phi_threshold and r['significant']:
        counts[r['model']] = counts.get(r['model'], 0) + 1
return counts
```

---

#### 4.2 Gate Evaluator (`src/phi_analysis.py`)

**Responsibility:** Evaluate SHOULD_WORK gate condition

**Interface:**
```python
def evaluate_gate_condition(
    pair_counts: Dict[str, int],
    min_pairs: int = 3,
    min_models: int = 2
) -> Dict[str, Any]:
    """
    Evaluate gate condition: ≥2 models with ≥3 significant pairs.
    
    Returns:
        {
            "gate": "SHOULD_WORK",
            "result": "PASS" | "FAIL",
            "models_meeting_threshold": int,
            "pair_counts": Dict[str, int],
            "rationale": str
        }
    """
```

**Implementation:**
```python
models_meeting_threshold = sum(1 for count in pair_counts.values() if count >= min_pairs)
gate_pass = models_meeting_threshold >= min_models

return {
    "gate": "SHOULD_WORK",
    "result": "PASS" if gate_pass else "FAIL",
    "models_meeting_threshold": models_meeting_threshold,
    "pair_counts": pair_counts,
    "rationale": f"{models_meeting_threshold} models with ≥{min_pairs} pairs → {'PASS' if gate_pass else 'FAIL'}"
}
```

---

### 5. Visualization Layer

#### 5.1 Heatmap Plotter (`src/visualization.py`)

**Responsibility:** Generate 5×5 coupling heatmaps per model

**Interface:**
```python
def plot_coupling_heatmap(
    coupling_results: pd.DataFrame,
    model_name: str,
    output_path: str
) -> None:
    """
    Plot 5×5 symmetric heatmap of phi coefficients.
    
    Args:
        coupling_results: DataFrame filtered for single model
        model_name: Model name (for title)
        output_path: Path to save PNG (e.g., figures/heatmap_gpt-4-turbo.png)
    """
```

**Visualization Details:**
- Use seaborn.heatmap with annot=True (phi values)
- Color scale: 0 (white) → 1 (dark blue)
- Significance stars: * for p_adjusted < 0.01
- Symmetric matrix (diagonal = 1.0, upper/lower triangles identical)

---

#### 5.2 Chart Generator (`src/visualization.py`)

**Responsibility:** Generate aggregate analysis charts

**Interfaces:**
```python
def plot_pair_counts(pair_counts: Dict[str, int], output_path: str) -> None:
    """Bar chart: model vs pair count, threshold line at 3."""

def plot_effect_size_distribution(coupling_results: pd.DataFrame, output_path: str) -> None:
    """Violin plot: phi distribution per model + scatter overlay."""

def plot_significance_scatter(coupling_results: pd.DataFrame, output_path: str) -> None:
    """Scatter: phi vs -log10(p_adjusted), colored by model."""
```

---

## Data Flow

### Phase 1: Data Acquisition
```
Huggingface API → TrustLLM Dataset → Cache (data/trustllm_cache/)
                                   ↓
                          Stratified Sampler (seed=42)
                                   ↓
                          500 instances (100×5 dimensions)
                                   ↓
                          data/samples.csv
```

### Phase 2: Model Evaluation
```
samples.csv → ModelEvaluator (parallel, 10 concurrent)
                     ↓
            Binary Labels (500×5×3 matrix)
                     ↓
            results/model_labels_{model}.csv
```

### Phase 3: Statistical Analysis
```
model_labels_*.csv → Phi Coefficient Computer (30 tests)
                            ↓
                     coupling_matrix.csv (30 rows)
                            ↓
                     Multiple Testing Corrector (Bonferroni)
                            ↓
                     coupling_matrix.csv (+ p_adjusted, reject columns)
```

### Phase 4: Decision
```
coupling_matrix.csv → Pair Counter
                            ↓
                     summary_stats.json
                            ↓
                     Gate Evaluator
                            ↓
                     gate_result.json
```

### Phase 5: Visualization
```
coupling_matrix.csv → Heatmap Plotter (3 models)
                            ↓
                     figures/heatmap_*.png
                     
coupling_matrix.csv → Chart Generator
                            ↓
                     figures/pair_counts.png
                     figures/effect_size_distribution.png
                     figures/significance_scatter.png
```

---

## File Structure

```
h-m2_code/
├── data/
│   ├── trustllm_cache/          # Downloaded dataset (auto-generated)
│   └── samples.csv              # Stratified 500 instances
├── src/
│   ├── data_loader.py           # TrustLLM loader + sampler
│   ├── model_evaluator.py       # API clients (GPT/Claude/Llama)
│   ├── phi_analysis.py          # Phi, Bonferroni, pair counter, gate
│   └── visualization.py         # Heatmaps + charts
├── scripts/
│   ├── 01_download_data.py      # Run data_loader.load_trustllm_dataset()
│   ├── 02_evaluate_models.py    # Run ModelEvaluator.evaluate_batch()
│   ├── 03_compute_coupling.py   # Run phi_analysis pipeline
│   └── 04_generate_figures.py   # Run visualization functions
├── results/
│   ├── model_labels_gpt-4-turbo.csv
│   ├── model_labels_claude-3-5-sonnet.csv
│   ├── model_labels_llama-3.1-70b-instruct.csv
│   ├── coupling_matrix.csv      # 30 rows × [model, dim1, dim2, phi, p, p_adj, sig]
│   ├── summary_stats.json       # Pair counts per model
│   └── gate_result.json         # PASS/FAIL verdict
├── figures/
│   ├── heatmap_gpt-4-turbo.png
│   ├── heatmap_claude-3-5-sonnet.png
│   ├── heatmap_llama-3.1-70b-instruct.png
│   ├── pair_counts.png
│   ├── effect_size_distribution.png
│   └── significance_scatter.png
├── requirements.txt
└── README.md
```

---

## Execution Order

### Script Sequence
1. `01_download_data.py` → Download TrustLLM, generate samples.csv (~5 min)
2. `02_evaluate_models.py` → Evaluate 3 models via API (~40-70 min)
3. `03_compute_coupling.py` → Compute phi, Bonferroni, gate (~1 min)
4. `04_generate_figures.py` → Generate 7 PNG files (~1 min)

**Total Runtime:** ~47-77 minutes

### Resumability
- Each script outputs intermediate files (samples.csv, model_labels_*.csv, coupling_matrix.csv)
- Scripts skip completed work if output files exist
- 02_evaluate_models.py supports checkpointing (resume from last saved state)

---

## Error Handling Strategy

### Data Layer
- TrustLLM download failure → Retry 3× with exponential backoff → Raise `DatasetDownloadError`

### Evaluation Layer
- API call failure → Retry 3× with exponential backoff → Checkpoint progress → Continue with next instance
- Persistent API failure (>10% instances fail) → Halt, log error, exit with code 1

### Statistical Layer
- Expected cell counts < 5 → Log warning, skip pair, continue with remaining pairs
- Invalid phi (< 0 or > 1) → Raise `ValueError` (indicates computation bug)

### Visualization Layer
- Plot generation failure → Log error, skip plot, continue with remaining plots

---

## Testing Strategy

### Unit Tests (`tests/test_phi_analysis.py`)
```python
def test_compute_phi_coefficient_perfect_correlation():
    """Test phi=1 for perfectly correlated binary vectors."""
    dim1 = np.array([1, 1, 0, 0])
    dim2 = np.array([1, 1, 0, 0])
    phi, p_value, table = compute_phi_coefficient(dim1, dim2)
    assert phi == 1.0
    assert p_value < 0.01

def test_compute_phi_coefficient_independence():
    """Test phi≈0 for independent vectors."""
    np.random.seed(42)
    dim1 = np.random.randint(0, 2, 500)
    dim2 = np.random.randint(0, 2, 500)
    phi, p_value, table = compute_phi_coefficient(dim1, dim2)
    assert 0 <= phi <= 0.2  # Weak correlation expected for independent random
```

### Integration Tests
- End-to-end test with 50 instances (10 per dimension × 5 dimensions)
- Mock API responses (no real API calls)
- Verify gate_result.json structure

---

**Architecture Status:** COMPLETE  
**Next Step:** Configuration Specifications (03_config.md)
