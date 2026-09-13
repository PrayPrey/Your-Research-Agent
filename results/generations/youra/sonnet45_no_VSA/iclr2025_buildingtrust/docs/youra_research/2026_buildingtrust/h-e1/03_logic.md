# Logic Specification: H-E1
**Date:** 2026-07-09  
**Hypothesis:** H-E1 (EXISTENCE - MUST_WORK)  
**Type:** Statistical Meta-Analysis (CV-Stability Correlation)

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: Green-field project - designing new APIs for CV-stability meta-analysis  
**Analyzed Path**: N/A  
**Relevant Symbols**: None - new implementation

**Note**: Existing experiments/h-e1/ implements different hypothesis (pairwise cross-benchmark ρ correlation). PRD requires CV vs mean ρ meta-analysis. This is a new green-field implementation.

---

## Applied Patterns

**Applied**: scipy.stats correlation patterns (spearmanr, pearsonr)

---

## A-3: Cross-Benchmark Correlation [Complexity: 9, Budget: 1]

Statistical module for computing pairwise Spearman ρ between benchmarks and aggregating mean ρ per benchmark.

### API Signatures

```python
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from scipy.stats import spearmanr

class BenchmarkMetaAnalysis:
    """Statistical meta-analysis for CV-stability correlation."""
    
    def __init__(self, min_models: int = 10, min_shared_models: int = 5):
        """Initialize meta-analysis with validation thresholds."""
        self.min_models = min_models
        self.min_shared_models = min_shared_models
    
    def compute_cross_benchmark_rho(
        self, 
        benchmark_a: pd.DataFrame, 
        benchmark_b: pd.DataFrame
    ) -> Optional[float]:
        """Compute Spearman ρ for shared models. a, b: DataFrame['model_name', 'score'] -> ρ or None"""
        ...
    
    def compute_mean_rho_per_benchmark(
        self, 
        benchmark_dict: Dict[str, pd.DataFrame]
    ) -> pd.DataFrame:
        """Compute mean ρ per benchmark. Returns: DataFrame['benchmark_name', 'mean_rho', 'n_pairs']"""
        ...
    
    def _get_shared_models(
        self, 
        benchmark_a: pd.DataFrame, 
        benchmark_b: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Filter to shared models and align order. Returns: (a_shared, b_shared)"""
        ...
    
    def _rank_scores(self, scores: pd.Series) -> pd.Series:
        """Rank scores within benchmark. scores: [N] -> ranks: [N]"""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| benchmark_a | DataFrame[N_a, 2] | Columns: ['model_name', 'score'] |
| benchmark_b | DataFrame[N_b, 2] | Columns: ['model_name', 'score'] |
| shared_models | Set[str] | Intersection of model_name sets |
| a_shared | DataFrame[M, 2] | M = len(shared_models) ≥ min_shared_models |
| a_ranks | Series[M] | Ranks (float, ties averaged) |
| rho | float | Spearman correlation coefficient |
| pairwise_rho_map | Dict[str, List[float]] | {benchmark: [ρ₁, ρ₂, ...]} |
| mean_rho_per_benchmark | DataFrame[K, 3] | K benchmarks, 3 columns |

### Pseudo-code

```
compute_cross_benchmark_rho(benchmark_a, benchmark_b):
    1. shared_models = set(benchmark_a.model_name) ∩ set(benchmark_b.model_name)
    2. if len(shared_models) < min_shared_models:
           return None
    3. a_shared = benchmark_a[benchmark_a.model_name.isin(shared_models)]
    4. b_shared = benchmark_b[benchmark_b.model_name.isin(shared_models)]
    5. a_shared = a_shared.sort_values('model_name')  # Align order
    6. b_shared = b_shared.sort_values('model_name')
    7. a_ranks = a_shared.score.rank(method='average', ascending=True)
    8. b_ranks = b_shared.score.rank(method='average', ascending=True)
    9. rho, _ = spearmanr(a_ranks, b_ranks)
    10. return rho

compute_mean_rho_per_benchmark(benchmark_dict):
    1. benchmark_names = list(benchmark_dict.keys())
    2. pairwise_rho_map = defaultdict(list)  # {benchmark: [list of rhos]}
    3. for i, b1 in enumerate(benchmark_names):
           for j, b2 in enumerate(benchmark_names):
               if i < j:  # Only compute upper triangle (avoid duplicates)
                   rho = compute_cross_benchmark_rho(benchmark_dict[b1], benchmark_dict[b2])
                   if rho is not None:
                       pairwise_rho_map[b1].append(rho)
                       pairwise_rho_map[b2].append(rho)
    4. results = []
    5. for benchmark_name in benchmark_names:
           rhos = pairwise_rho_map[benchmark_name]
           results.append({
               'benchmark_name': benchmark_name,
               'mean_rho': np.mean(rhos) if len(rhos) > 0 else np.nan,
               'n_pairs': len(rhos)
           })
    6. return pd.DataFrame(results)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Algorithm Implementation | Shared model filtering, ranking, Spearman ρ, mean aggregation |

---

## Supporting Context

### Edge Cases

1. **Insufficient Overlap**: If shared models < min_shared_models → return None, exclude pair from analysis
2. **Single Benchmark**: If len(benchmark_dict) == 1 → mean_rho = NaN (no pairs to compare)
3. **All Identical Scores**: rank(method='average') assigns average rank, spearmanr handles gracefully
4. **Missing Data**: Ensure benchmark DataFrames are pre-validated (no NaN scores)
5. **No Valid Pairs**: If all pairwise comparisons return None → mean_rho = NaN

### Integration Points

**Upstream Dependencies**:
- `benchmark_dict` from DataExtractor (A-1): validated benchmarks with n_models ≥ min_models
- Each DataFrame has columns ['model_name', 'score']

**Downstream Dependencies**:
- `mean_rho_per_benchmark` DataFrame → HypothesisTestEngine (A-4) for Pearson correlation test
- Mean ρ values extracted for correlation with CV values
- Pairwise ρ matrix → MetaAnalysisVisualizer (A-5) for heatmap

---

## Algorithm Details

### Shared Model Filtering

**Problem**: Benchmarks may evaluate different subsets of models.

**Solution**:
1. Compute intersection of model_name sets: `shared = set_a ∩ set_b`
2. Verify minimum overlap: `len(shared) ≥ min_shared_models` (default=5)
3. Filter both DataFrames to shared models only
4. Sort by model_name to ensure consistent ordering
5. Extract scores and compute ranks independently per benchmark
6. Compute Spearman correlation on ranks

**Why ranks?**: Spearman ρ measures correlation of rankings (ordinal relationship), not raw scores (interval relationship). This is robust to scaling differences between benchmarks.

### Mean ρ Aggregation

**Problem**: Each benchmark is compared with multiple others. Need single stability metric per benchmark.

**Solution**:
1. Compute all pairwise ρ values (upper triangle of correlation matrix)
2. For each benchmark, collect all ρ values where it was involved
3. Compute mean of those ρ values → "mean cross-benchmark stability"
4. This becomes the outcome variable for H-E1: Does CV predict mean ρ?

**Example**: 
- 5 benchmarks → 10 pairwise comparisons (upper triangle)
- Benchmark A involved in 4 comparisons: A-B, A-C, A-D, A-E
- Mean ρ for A = mean([ρ_AB, ρ_AC, ρ_AD, ρ_AE])

---

## References

**PRD Requirements**:
- FR-3: Cross-Benchmark Ranking Correlation (Spearman ρ)
- FR-3.1: Pairwise Spearman correlation function (lines 125-158)
- FR-3.2: Pairwise ρ for all benchmark pairs
- FR-3.3: Mean ρ per benchmark across all valid pairs (lines 160-168)
- Acceptance Criteria: Mean ρ computed for all benchmarks with ≥1 valid pair

**Architecture Decisions**:
- Module: BenchmarkMetaAnalysis class (src/meta_analysis.py)
- Dependencies: scipy.stats.spearmanr, pandas, numpy
- Complexity: 9 points (Medium)

---

**Status**: Ready for Phase 4 Implementation  
**Complexity**: 9 points (Medium)  
**Subtasks**: 1 allocated (L-3-1)
