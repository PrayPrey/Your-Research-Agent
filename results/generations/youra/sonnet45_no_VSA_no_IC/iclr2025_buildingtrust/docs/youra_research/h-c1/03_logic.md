# Logic Specification: H-C1

**Date:** 2026-08-19
**Hypothesis:** Coupling matrices differ across models (Mantel test r < 0.7 for ≥1 model pair)
**Type:** COMPARISON
**Budget:** 5 subtasks allocated

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field - new implementation (no base hypothesis code to call)
**Analyzed Path:** N/A
**Relevant Symbols:** None - standalone statistical comparison experiment
**Note:** h-e1 referenced as prerequisite for methodology only (phi coefficient calculation), not as code dependency.

---

## C-1: Data Pipeline [Complexity: 9, Budget: 1]

**Applied:** HuggingFace datasets + pandas stratified sampling

### API Signatures

```python
# src/data_loader.py

def load_trustllm(models: list[str], samples_per_dim: int = 100, seed: int = 42) -> pd.DataFrame:
    """Load TrustLLM for multiple models. Returns: [500*len(models), 7] with columns [instance_id, dimension, prompt, model, label_truth, label_robust, label_fair, label_safe, label_priv]"""

def stratified_sample(df: pd.DataFrame, dimension: str, n: int, seed: int) -> pd.DataFrame:
    """Sample n instances per dimension. Returns: [n, cols]"""

def binarize_labels(df: pd.DataFrame, dimension: str, threshold: float = 0.5) -> np.ndarray:
    """Convert scores to binary. Returns: [N] int array (0/1)"""
```

### Subtasks [1/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | TrustLLM loader | HuggingFace dataset loading + validation |

---

## C-2: Coupling Matrix [Complexity: 10, Budget: 1]

**Applied:** scipy chi2_contingency + sklearn matthews_corrcoef (phi coefficient)

### API Signatures

```python
# src/coupling_matrix.py

class CouplingMatrix:
    def __init__(self, dimensions: list[str]):
        """dimensions: ['truthfulness', 'robustness', 'fairness', 'safety', 'privacy']"""
        self.dimensions = dimensions
        self.n_dims = 5
    
    def compute_phi(self, labels_a: np.ndarray, labels_b: np.ndarray) -> tuple[float, float]:
        """Phi coefficient for 2×2 table. labels_a, labels_b: [N]. Returns: (phi, p_value)"""
    
    def build_matrix(self, labels_dict: dict[str, np.ndarray]) -> np.ndarray:
        """Build 5×5 symmetric coupling matrix. labels_dict: {dim: [N]}. Returns: [5, 5] phi matrix"""
```

### Pseudo-code

```
compute_phi:
  table = crosstab(labels_a, labels_b)  # 2×2
  chi2, p = chi2_contingency(table)
  phi = sqrt(chi2 / N)
  return phi, p

build_matrix:
  matrix = eye(5)  # diagonal = 1.0
  for i, j in combinations(5, 2):
    phi, p = compute_phi(labels_dict[dims[i]], labels_dict[dims[j]])
    matrix[i,j] = matrix[j,i] = phi
  return matrix
```

### Subtasks [1/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Matrix builder | 5×5 symmetric phi matrix construction |

---

## C-3: Mantel Test [Complexity: 12, Budget: 2]

**Applied:** mantel library (jwcarr/mantel) for matrix correlation

### API Signatures

```python
# src/mantel_test.py

def compare_matrices(matrix_a: np.ndarray, matrix_b: np.ndarray, perms: int = 10000) -> dict:
    """Mantel test for two 5×5 matrices. Returns: {'r': float, 'p': float, 'z': float}"""

def run_all_comparisons(matrices: dict[str, np.ndarray], perms: int = 10000) -> pd.DataFrame:
    """Compare all model pairs. matrices: {model: [5,5]}. Returns: [3 rows, 5 cols] with [pair, r, p, z, significant]"""

def apply_bonferroni(results: pd.DataFrame, alpha: float = 0.05) -> pd.DataFrame:
    """Bonferroni correction. Adds 'bonf_sig' column (p < alpha/3)"""
```

### Pseudo-code

```
compare_matrices:
  import mantel
  result = mantel.test(matrix_a, matrix_b, perms=perms, method='pearson', tail='two-tail')
  return {'r': result.r, 'p': result.p, 'z': result.z}

run_all_comparisons:
  pairs = [('GPT-4', 'Claude-3'), ('GPT-4', 'Llama-3'), ('Claude-3', 'Llama-3')]
  results = []
  for model_a, model_b in pairs:
    res = compare_matrices(matrices[model_a], matrices[model_b], perms)
    results.append({'pair': f'{model_a} vs {model_b}', **res, 'significant': res['p'] < 0.05})
  return DataFrame(results)
```

### Subtasks [2/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Mantel wrapper | Interface to mantel library |
| L-3-2 | Pairwise comparison | Loop over 3 model pairs |

---

## C-4: Visualization [Complexity: 8, Budget: 1]

**Applied:** matplotlib + seaborn standard plotting

### API Signatures

```python
# src/visualization.py

def plot_coupling_heatmaps(matrices: dict[str, np.ndarray], dimensions: list[str], output_path: str):
    """3 heatmaps side-by-side. matrices: {model: [5,5]}. Saves to output_path"""

def plot_scatter_comparison(matrix_a: np.ndarray, matrix_b: np.ndarray, labels: tuple[str, str], output_path: str):
    """Scatter: X=model_a phi values, Y=model_b phi values. labels: (model_a, model_b). Adds regression line + r²"""

def plot_mantel_results(results: pd.DataFrame, output_path: str):
    """Bar plot: Mantel r values for 3 pairs, horizontal line at r=0.7 threshold"""
```

### Subtasks [1/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Heatmap grid | 3-panel heatmap layout |

---

## C-5: Integration [Complexity: 9, Budget: 0]

**Applied:** Standard Python orchestration

### API Signatures

```python
# scripts/run_experiment.py

def main():
    """Pipeline: load TrustLLM (3 models) → build 3 coupling matrices → run 3 Mantel tests → visualizations → validation report"""

def check_gate(results: pd.DataFrame, r_threshold: float = 0.7, alpha: float = 0.0167) -> dict:
    """Gate logic. Returns: {'status': 'PASS'|'PARTIAL'|'FAIL', 'evidence': [(pair, r, p), ...]}"""
```

### Pseudo-code

```
main:
  CONFIG = load_config()
  df = load_trustllm(['GPT-4', 'Claude-3', 'Llama-3'], samples_per_dim=100, seed=42)
  
  matrices = {}
  for model in ['GPT-4', 'Claude-3', 'Llama-3']:
    model_df = df[df['model'] == model]
    labels = {dim: binarize_labels(model_df, dim) for dim in DIMS}
    cm = CouplingMatrix(DIMS)
    matrices[model] = cm.build_matrix(labels)
  
  mantel_results = run_all_comparisons(matrices, perms=10000)
  mantel_results = apply_bonferroni(mantel_results, alpha=0.05)
  
  gate_status = check_gate(mantel_results, r_threshold=0.7, alpha=0.0167)
  
  plot_coupling_heatmaps(matrices, DIMS, 'figures/heatmaps.png')
  plot_mantel_results(mantel_results, 'figures/mantel.png')
  
  save_validation_report(gate_status, mantel_results, 'docs/04_validation.md')

check_gate:
  significant = results[(results['p'] < alpha) & (results['r'] < r_threshold)]
  if len(significant) > 0:
    return {'status': 'PASS', 'evidence': significant.to_dict('records')}
  moderate = results[(results['r'] >= 0.7) & (results['r'] < 0.9)]
  if len(moderate) > 0:
    return {'status': 'PARTIAL', 'evidence': moderate.to_dict('records')}
  return {'status': 'FAIL', 'evidence': []}
```

---

## C-6: Gate Decision [Complexity: 6, Budget: 0]

**Applied:** Simple threshold logic

### API Signatures

```python
# src/gate_decision.py

def evaluate_gate(mantel_results: pd.DataFrame) -> str:
    """Parse Mantel results. Returns: 'PASS' | 'PARTIAL' | 'FAIL'"""
```

### Pseudo-code

```
evaluate_gate:
  for row in mantel_results:
    if row['p'] < 0.0167 and row['r'] < 0.7:
      return 'PASS'
  for row in mantel_results:
    if 0.7 <= row['r'] < 0.9:
      return 'PARTIAL'
  return 'FAIL'
```

---

## Notes

- **COMPARISON hypothesis:** No baseline model, tests 3 independent models
- **Mantel test library:** Uses `jwcarr/mantel` (PyPI: mantel), alternatively `skbio.stats.distance.mantel`
- **Statistical correction:** Bonferroni α = 0.05/3 = 0.0167 for 3 comparisons
- **Gate outcomes:** All outcomes (PASS/PARTIAL/FAIL) proceed to Phase 5 (SHOULD_WORK)
- **Runtime estimate:** Mantel test 10k perms × 3 pairs = ~30 seconds total

---

**Subtasks:** 5/5 used
