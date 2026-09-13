# Architecture: h-e2 Observational Analysis Pipeline

**Hypothesis:** AI response diversity correlates with query diversity (r > 0.4)  
**Type:** EXISTENCE (PoC)  
**Date:** 2026-08-25  
**Applied:** Standard distinct-n metric, HH-RLHF parsing pattern  

---

## Codebase Analysis (Serena)

**Project Type:** existing_codebase  
**Status:** Reusable data loading found  
**Analyzed Path:** youra/data/hh_rlhf.py  
**Findings:** HH-RLHF loader + parser exists, reuse for query/response extraction

---

## Module Structure

### DataLoader (`youra/experiments/h_e2_data.py`)

**Dependencies:** youra.data.hh_rlhf, datasets, numpy

```python
class HHRLHFDataLoader:
    def __init__(self, min_turns: int = 2): ...
    def load_conversations(self) -> List[Dict[str, Any]]: ...
    def filter_by_helpfulness(self, conversations: List[Dict], threshold_percentile: float = 50) -> List[Dict]: ...
```

**Reuses:** `youra.data.hh_rlhf.load_hh_rlhf`, `youra.data.hh_rlhf.parse_conversation`

---

### DiversityMetrics (`youra/experiments/h_e2_metrics.py`)

**Dependencies:** stdlib only

```python
def distinct_n(texts: List[str], n: int = 1) -> float: ...
def compute_conversation_diversity(queries: List[str], responses: List[str]) -> Tuple[float, float]: ...
```

---

### CorrelationAnalyzer (`youra/experiments/h_e2_analysis.py`)

**Dependencies:** scipy.stats, numpy

```python
class CorrelationAnalyzer:
    def __init__(self, threshold: float = 0.4, alpha: float = 0.05): ...
    def compute_correlation(self, x: np.ndarray, y: np.ndarray) -> Dict[str, float]: ...
    def stratified_analysis(self, data: pd.DataFrame, group_by: str) -> pd.DataFrame: ...
```

---

### Visualizer (`youra/experiments/h_e2_plots.py`)

**Dependencies:** matplotlib, numpy

```python
def plot_gate_metrics(target_r: float, observed_r: float, ci: Tuple[float, float], p_value: float, save_path: str): ...
def plot_scatter_with_regression(x: np.ndarray, y: np.ndarray, save_path: str): ...
def plot_diversity_distributions(query_div: np.ndarray, response_div: np.ndarray, save_path: str): ...
def plot_sensitivity_analysis(thresholds: List[float], correlations: List[float], cis: List[Tuple], save_path: str): ...
def plot_stratified_correlations(strata_labels: List[str], correlations: List[float], cis: List[Tuple], save_path: str): ...
```

---

### Main Pipeline (`youra/experiments/h_e2_main.py`)

**Dependencies:** All above modules, pathlib

```python
def run_h_e2_experiment(output_dir: str, min_turns: int = 2, target_r: float = 0.4) -> Dict[str, Any]: ...
```

---

## File Organization

```
youra/experiments/
  h_e2_data.py        # Data loading and filtering
  h_e2_metrics.py     # Distinct-n implementation
  h_e2_analysis.py    # Correlation computation
  h_e2_plots.py       # 5 visualization functions
  h_e2_main.py        # Pipeline orchestration

docs/youra_research/h-e2/
  figures/            # Generated plots (5 PNG files)
  results.json        # Correlation results
```

---

## Data Flow

```
HH-RLHF Dataset
  → Load train + test splits
  → Parse multi-turn conversations (reuse youra.data.hh_rlhf.parse_conversation)
  → Filter: helpfulness > median, turns >= 2
  → Extract (queries, responses) per conversation
  → Compute (query_diversity, response_diversity) per conversation
  → Pearson correlation
  → Generate 5 plots
  → Write results.json
```

---

## Error Handling

**Critical Failures (raise exception):**
- HH-RLHF dataset download fails
- Sample size < 100 after filtering
- Correlation computation fails (NaN/inf values)

**Warnings (log and continue):**
- Single-turn conversations detected (skip)
- Empty queries/responses (skip conversation)
- Helpfulness score missing (exclude from median filter)

**Edge Cases:**
- Zero-length conversations → skip
- All identical tokens in conversation → distinct-n = 0.0 (valid)
- Missing helpfulness for some conversations → compute median on available scores

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E2-1 | Data loading | Load HH-RLHF, parse conversations, filter by helpfulness > median | 7 | 2+2+2+1 (load+parse+filter+validate) |
| E2-2 | Metrics | Implement distinct-1, compute per-conversation diversity | 5 | 2+2+1 (distinct-n+apply+edge cases) |
| E2-3 | Analysis | Pearson correlation + stratified analysis (quartiles, length bins) | 6 | 2+2+2 (correlation+stratify+CI) |
| E2-4 | Visualization | Generate 5 plots (gate metrics, scatter, distributions, sensitivity, stratified) | 8 | 2+2+1+1+2 (gate+scatter+dist+sens+strat) |
| E2-5 | Orchestration | Main pipeline + results export | 4 | 2+1+1 (pipeline+export+validation) |

**Distribution:**  
- VeryHigh (18-20): []  
- High (14-17): []  
- Medium (9-13): []  
- Low (4-8): [E2-1, E2-2, E2-3, E2-4, E2-5]  

**Total Complexity:** 30

---

## Dependencies

**Standard Library:** pathlib, logging, typing  
**Data:** datasets (HH-RLHF), pandas, numpy  
**Analysis:** scipy (pearsonr)  
**Visualization:** matplotlib  

**External Modules (Existing Codebase):**  
- `youra.data.hh_rlhf.load_hh_rlhf`  
- `youra.data.hh_rlhf.parse_conversation`  

---

## Success Validation

```python
# Pipeline outputs
{
    "correlation": r,
    "p_value": p,
    "ci_95": (lower, upper),
    "success": r > 0.4 and p < 0.05,
    "sample_size": n_conversations,
    "mean_query_diversity": float,
    "mean_response_diversity": float
}
```

**Gate Check:**  
- r > 0.4 AND p < 0.05 → PASS  
- Otherwise → FAIL (hypothesis refuted)
