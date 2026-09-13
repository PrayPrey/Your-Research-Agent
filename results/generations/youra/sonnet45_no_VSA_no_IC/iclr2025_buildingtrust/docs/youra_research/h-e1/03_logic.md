# Logic Specification: H-E1

**Date:** 2026-08-19
**Hypothesis:** At least one model exhibits statistically significant coupling (phi ≥ 0.3, p < 0.01) for at least one dimension pair
**Type:** EXISTENCE (PoC)
**Budget:** 0 subtasks allocated

---

## Codebase Analysis (Serena)

**Project Type:** existing_codebase
**Status:** existing patterns found
**Analyzed Path:** h-e1_code/
**Relevant Symbols:** generate_synthetic_failures, compute_cooccurrence, test_cooccurrence_significance, cluster_failures, plot_cooccurrence_heatmap
**Note:** Existing code uses chi2_contingency + clustering. PRD specifies phi coefficient. New coupling_analyzer.py replaces analysis.py chi2 logic.

---

## A-1: Data Pipeline [Complexity: 8, Budget: 0]

**Applied:** Standard Python data loading (HuggingFace datasets, pandas)

### API Signatures

```python
# src/data_loader.py

def load_multitrust(samples: int = 500, seed: int = 42) -> pd.DataFrame:
    """Load MultiTrust dataset from HuggingFace.
    
    Returns: DataFrame with columns [prompt, truthfulness, robustness, fairness, safety, privacy]
    """

def extract_binary_labels(df: pd.DataFrame, dimensions: list[str]) -> dict[str, np.ndarray]:
    """Convert dimension scores to binary pass/fail labels.
    
    Args:
        df: Raw dataset with dimension scores
        dimensions: ['truthfulness', 'robustness', 'fairness', 'safety', 'privacy']
    
    Returns: {dimension: [N] binary array (1=fail, 0=pass)}
    """

def evaluate_model_api(
    model_name: str,
    prompts: list[str],
    config: dict,
    batch_size: int = 10
) -> list[str]:
    """Evaluate model via API with rate limiting.
    
    Args:
        model_name: 'gpt-4' | 'claude-3-sonnet' | 'llama-3-70b'
        prompts: [N] text prompts
        config: Model config from CONFIG['models'][model_name]
        batch_size: Rate limit batch size
    
    Returns: [N] model responses
    """
```

### Pseudo-code

```
1. load_multitrust:
   - Load dataset from HuggingFace hub 'thu-ml/MultiTrust'
   - Sample 500 instances with fixed seed
   - Return DataFrame

2. extract_binary_labels:
   - For each dimension, apply pass/fail threshold
   - Return dict of binary arrays

3. evaluate_model_api:
   - Initialize API client (OpenAI/Anthropic/Together)
   - Batch prompts (size=10)
   - Add exponential backoff retry logic
   - Return responses
```

---

## A-2: Coupling Analyzer [Complexity: 6, Budget: 0]

**Applied:** scipy.stats phi coefficient (Matthews correlation for 2×2 contingency)

### API Signatures

```python
# src/coupling_analyzer.py

class CouplingAnalyzer:
    """Compute phi coefficients for dimension pairs."""
    
    def __init__(self, dimensions: list[str]):
        """Initialize with dimension names.
        
        Args:
            dimensions: ['truthfulness', 'robustness', 'fairness', 'safety', 'privacy']
        """
        self.dimensions = dimensions
        self.n_dims = len(dimensions)
    
    def compute_phi_coefficient(
        self,
        labels_d1: np.ndarray,
        labels_d2: np.ndarray
    ) -> tuple[float, float]:
        """Compute phi coefficient and p-value for dimension pair.
        
        Args:
            labels_d1: [N] binary labels for dimension 1
            labels_d2: [N] binary labels for dimension 2
        
        Returns: (phi_coefficient, p_value)
            phi_coefficient: Pearson correlation for 2×2 table, range [-1, 1]
            p_value: Chi-square test p-value
        """
    
    def analyze_model(self, labels: dict[str, np.ndarray]) -> pd.DataFrame:
        """Compute phi coefficients for all dimension pairs.
        
        Args:
            labels: {dimension: [N] binary array} for all 5 dimensions
        
        Returns: DataFrame with columns [dim1, dim2, phi, p_value]
            10 rows for 5 choose 2 pairs
        """
    
    def verify_phi_sklearn(self, labels_d1: np.ndarray, labels_d2: np.ndarray) -> float:
        """Verify phi via sklearn.metrics.matthews_corrcoef.
        
        Args:
            labels_d1: [N] binary labels
            labels_d2: [N] binary labels
        
        Returns: MCC (equivalent to phi for binary classification)
        """
```

### Pseudo-code

```
1. compute_phi_coefficient:
   - Construct 2×2 contingency table from labels_d1, labels_d2
   - Call scipy.stats.chi2_contingency(table)
   - Extract chi2 statistic, p-value
   - Compute phi = sqrt(chi2 / N)
   - Return (phi, p_value)

2. analyze_model:
   - Initialize result list
   - For i in range(n_dims):
       For j in range(i+1, n_dims):
           phi, p = compute_phi_coefficient(labels[dims[i]], labels[dims[j]])
           Append (dims[i], dims[j], phi, p) to results
   - Return DataFrame(results)

3. verify_phi_sklearn:
   - Return matthews_corrcoef(labels_d1, labels_d2)
   - Assert abs(mcc - phi) < 1e-6
```

---

## A-3: Visualization [Complexity: 5, Budget: 0]

**Applied:** matplotlib + seaborn standard plotting

### API Signatures

```python
# src/visualization.py

def plot_coupling_heatmap(
    phi_matrix: np.ndarray,
    dimensions: list[str],
    model_name: str,
    output_path: str
):
    """Plot phi coefficient heatmap for a single model.
    
    Args:
        phi_matrix: [5, 5] symmetric phi coefficient matrix
        dimensions: Dimension names for axis labels
        model_name: Model name for title
        output_path: Save path (e.g., 'figures/heatmap_gpt-4.png')
    """

def plot_significance_scatter(
    results: pd.DataFrame,
    output_path: str
):
    """Scatter plot of phi vs p-value for all model-pair combinations.
    
    Args:
        results: DataFrame with columns [model, dim1, dim2, phi, p_value]
        output_path: Save path (e.g., 'figures/significance_scatter.png')
    
    Plot:
        x-axis: phi coefficient
        y-axis: -log10(p_value)
        Horizontal line at p=0.01
        Vertical line at phi=0.3
    """

def plot_gate_metrics(
    results: dict,
    output_path: str
):
    """Bar plot showing gate condition metrics.
    
    Args:
        results: {
            'significant_pairs': [(model, dim1, dim2, phi, p), ...],
            'max_phi_per_model': {model: phi},
            'gate_pass': bool
        }
        output_path: Save path (e.g., 'figures/gate_metrics.png')
    """
```

### Pseudo-code

```
1. plot_coupling_heatmap:
   - Create heatmap with seaborn
   - Annotate cells with phi values
   - Colormap: coolwarm, center=0
   - Save to output_path

2. plot_significance_scatter:
   - Create scatter plot with matplotlib
   - Color by model
   - Add reference lines (phi=0.3, p=0.01)
   - Save to output_path

3. plot_gate_metrics:
   - Create bar plot of max phi per model
   - Add horizontal line at phi=0.3 threshold
   - Annotate pass/fail status
   - Save to output_path
```

---

## A-4: Integration [Complexity: 6, Budget: 0]

**Applied:** Standard Python script orchestration

### API Signatures

```python
# scripts/run_experiment.py

def main():
    """Execute 3-model phi coefficient experiment.
    
    Pipeline:
        1. Load MultiTrust dataset (500 samples)
        2. Evaluate 3 models via API
        3. Extract binary labels per dimension
        4. Compute phi coefficients (10 pairs × 3 models = 30 results)
        5. Generate visualizations (3 heatmaps + 1 scatter + 1 gate plot)
        6. Save results to CSV
        7. Check gate condition (phi ≥ 0.3, p < 0.01)
    """

def check_gate_condition(results: pd.DataFrame, phi_threshold: float = 0.3, p_threshold: float = 0.01) -> dict:
    """Check if gate condition is satisfied.
    
    Args:
        results: DataFrame with columns [model, dim1, dim2, phi, p_value]
        phi_threshold: Minimum effect size (default 0.3)
        p_threshold: Maximum p-value (default 0.01)
    
    Returns: {
        'gate_pass': bool,
        'significant_pairs': [(model, dim1, dim2, phi, p), ...],
        'max_phi_per_model': {model: phi}
    }
    """

def save_results(results: pd.DataFrame, gate_metrics: dict, output_dir: str):
    """Save experiment results to disk.
    
    Args:
        results: Full results DataFrame
        gate_metrics: Gate condition evaluation
        output_dir: Output directory path
    
    Files:
        - results/coupling_results.csv
        - results/gate_metrics.json
        - logs/experiment.log
    """
```

### Pseudo-code

```
1. main:
   - Load config from config.py
   - df = load_multitrust(samples=500, seed=42)
   - For each model in ['gpt-4', 'claude-3-sonnet', 'llama-3-70b']:
       responses = evaluate_model_api(model, df['prompt'], config)
       labels = extract_binary_labels(responses, dimensions)
       analyzer = CouplingAnalyzer(dimensions)
       model_results = analyzer.analyze_model(labels)
       Append model_results to all_results
   - gate_metrics = check_gate_condition(all_results)
   - Generate all visualizations
   - save_results(all_results, gate_metrics, 'h-e1/')

2. check_gate_condition:
   - Filter results where phi ≥ phi_threshold AND p < p_threshold
   - If len(filtered) > 0: gate_pass = True
   - Extract max_phi per model
   - Return gate metrics dict

3. save_results:
   - results.to_csv('results/coupling_results.csv')
   - json.dump(gate_metrics, 'results/gate_metrics.json')
   - Write experiment log
```

---

## External Dependencies API

No base hypothesis code. This is a standalone statistical analysis using existing h-e1_code/ as reference only.

---

## Notes

- **EXISTENCE PoC:** Minimal implementation, no parameter tuning
- **PRD Delta:** Existing h-e1_code/ uses clustering, PRD specifies phi coefficient (followed PRD)
- **Verification:** sklearn.matthews_corrcoef used to verify scipy phi computation
- **Rate Limits:** API batch_size=10 to avoid rate limit errors
- **Total API Calls:** 500 samples × 3 models = 1500 calls (~45 min runtime)

---

**Subtasks:** 0/0 used (budget=0)
