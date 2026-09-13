# Logic Design: h-e1

**Date:** 2026-08-29
**Hypothesis:** Rankings shift significantly between ImageNet and ImageNet-V2 (Kendall-τ < 0.90 with p < 0.001)
**Type:** EXISTENCE (PoC)

---

## API Signatures

### Data Collection Module

```python
# src/data_collection.py

def fetch_imagenet_leaderboard() -> pd.DataFrame:
    """
    Fetch ImageNet classification leaderboard from Papers With Code.
    
    Returns:
        DataFrame with columns: [model_name, imagenet_top1]
        Shape: (N, 2) where N ≈ 200 models
    """
    pass

def fetch_imagenet_v2_leaderboard() -> pd.DataFrame:
    """
    Fetch ImageNet-V2 classification leaderboard from Papers With Code.
    
    Returns:
        DataFrame with columns: [model_name, imagenet_v2_top1]
        Shape: (M, 2) where M ≈ 100 models
    """
    pass

def collect_and_merge() -> pd.DataFrame:
    """
    Fetch both leaderboards and merge on model_name.
    
    Returns:
        DataFrame with columns: [model_name, imagenet_top1, imagenet_v2_top1]
        Shape: (K, 3) where K ≥ 30 (models with both results)
    """
    pass
```

### Data Processing Module

```python
# src/data_processing.py

def compute_rankings(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute rankings for both benchmarks.
    
    Args:
        df: DataFrame with imagenet_top1, imagenet_v2_top1
        
    Returns:
        DataFrame with added columns: [rank_imagenet, rank_v2]
        Ranking: higher accuracy = rank 1 (ascending=False)
    """
    pass

def validate_sample_size(df: pd.DataFrame, min_n: int = 30) -> bool:
    """
    Verify minimum sample size for statistical power.
    
    Args:
        df: Merged DataFrame
        min_n: Minimum required samples (default 30)
        
    Returns:
        True if len(df) >= min_n, else raises ValueError
    """
    pass
```

### Statistical Analysis Module

```python
# src/statistical_analysis.py

from typing import Tuple, Dict, Any

def compute_kendall_tau(
    rank_x: np.ndarray, 
    rank_y: np.ndarray
) -> Tuple[float, float]:
    """
    Compute Kendall-τ correlation coefficient.
    
    Args:
        rank_x: ImageNet rankings, shape (N,)
        rank_y: ImageNet-V2 rankings, shape (N,)
        
    Returns:
        (tau, p_value): Kendall-τ and two-sided p-value
        
    Implementation:
        scipy.stats.kendalltau(rank_x, rank_y)
    """
    pass

def bootstrap_confidence_interval(
    rank_x: np.ndarray,
    rank_y: np.ndarray,
    n_bootstrap: int = 10000,
    confidence: float = 0.95,
    random_seed: int = 42
) -> Tuple[float, float]:
    """
    Bootstrap 95% CI for Kendall-τ.
    
    Args:
        rank_x: ImageNet rankings, shape (N,)
        rank_y: ImageNet-V2 rankings, shape (N,)
        n_bootstrap: Number of bootstrap iterations
        confidence: Confidence level (0.95 = 95%)
        random_seed: For reproducibility
        
    Returns:
        (ci_low, ci_high): Lower and upper CI bounds
        
    Algorithm:
        1. Set np.random.seed(random_seed)
        2. For i in range(n_bootstrap):
           a. Sample indices with replacement
           b. Compute Kendall-τ on sample
           c. Store tau value
        3. Return percentile CI
    """
    pass

def test_hypothesis(
    tau: float,
    p_value: float,
    ci: Tuple[float, float],
    tau_threshold: float = 0.90,
    p_threshold: float = 0.001
) -> Dict[str, Any]:
    """
    Test h-e1 hypothesis: τ < 0.90 with p < 0.001.
    
    Args:
        tau: Computed Kendall-τ
        p_value: Computed p-value
        ci: 95% confidence interval (low, high)
        tau_threshold: Threshold for tau (0.90)
        p_threshold: Threshold for significance (0.001)
        
    Returns:
        {
            'tau': float,
            'p_value': float,
            'ci_95': (float, float),
            'tau_below_threshold': bool,
            'significant': bool,
            'hypothesis_supported': bool,
            'gate_passed': bool
        }
    """
    pass

def run_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Execute complete h-e1 analysis pipeline.
    
    Args:
        df: DataFrame with rank_imagenet, rank_v2 columns
        
    Returns:
        Complete results dictionary for 04_validation.md
    """
    pass
```

### Visualization Module

```python
# src/visualization.py

def plot_ranking_scatter(
    df: pd.DataFrame,
    output_path: str = "figures/ranking_scatter.png"
) -> None:
    """
    Create scatter plot of ImageNet rank vs V2 rank.
    
    Args:
        df: DataFrame with rank_imagenet, rank_v2
        output_path: Where to save figure
        
    Visual elements:
        - X-axis: ImageNet rank
        - Y-axis: ImageNet-V2 rank
        - Diagonal reference line (y=x)
        - Points colored by rank change magnitude
    """
    pass

def plot_gate_metrics(
    results: Dict[str, Any],
    output_path: str = "figures/gate_metrics.png"
) -> None:
    """
    Bar chart comparing target vs actual gate metrics.
    
    Args:
        results: Output from run_analysis()
        output_path: Where to save figure
        
    Visual elements:
        - Bars: Threshold (0.90) vs Actual τ
        - Color: Green if passed, red if failed
        - Annotation: p-value and CI
    """
    pass
```

---

## Tensor Shapes

| Variable | Shape | Type | Description |
|----------|-------|------|-------------|
| `df_merged` | (N, 3) | DataFrame | Merged leaderboard data |
| `rank_imagenet` | (N,) | float64 | ImageNet rankings |
| `rank_v2` | (N,) | float64 | V2 rankings |
| `bootstrap_taus` | (10000,) | float64 | Bootstrap tau samples |

Where N ≥ 30 (minimum sample size for statistical power).

---

## Data Flow

```
Papers With Code API
        ↓
fetch_imagenet_leaderboard()  →  df_imagenet: (200, 2)
fetch_imagenet_v2_leaderboard() →  df_v2: (100, 2)
        ↓
collect_and_merge()  →  df_merged: (N, 3) where N ≥ 30
        ↓
compute_rankings()  →  df_ranked: (N, 5)
        ↓
compute_kendall_tau()  →  (tau, p_value): (float, float)
bootstrap_confidence_interval()  →  (ci_low, ci_high): (float, float)
        ↓
test_hypothesis()  →  results: Dict
        ↓
plot_*()  →  figures/*.png
        ↓
04_validation.md
```

---

*Generated by Logic Agent (ablation mode)*
