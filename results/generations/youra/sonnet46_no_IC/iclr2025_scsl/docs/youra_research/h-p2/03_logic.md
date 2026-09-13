# Logic Design: H-P2
## Spurious Probe Accuracy vs WGA Correlation (Exploratory)

**Generated:** 2026-08-05
**Type:** MECHANISM (Exploratory Correlation) — Incremental extension of H-M3
**Tier:** FULL
**Budget:** 11 subtasks

Applied: scipy-bootstrap-pearsonr-pattern
Applied: matplotlib-scatter-regression-pattern

---

## Codebase Analysis (Serena)

**Base hypothesis:** h-m3
**Analyzed:** `h-m3/code/run_experiment.py`, `h-m3/code/config.py`

**Key findings:**
- `run_probe(features, labels, method, seed) -> float` scores on **train** features (line 95: `probe.score(features, labels)`) — NOT test features. H-P2 must NOT reuse this function for probe_acc; must score on test features separately.
- `extract_layer4_features(model, dataloader, device) -> tuple[np.ndarray, np.ndarray]` extracts `(features, bg_labels)` — background labels derived from `metadata[:, 0] % 2`.
- `load_resnet50(ckpt_path, device='cpu') -> torch.nn.Module` handles all checkpoint key variants.
- `get_transform() -> T.Compose` returns standard ImageNet normalization transform.
- `get_loader(split, batch_size, shuffle=False) -> DataLoader` uses WILDS API.
- H-M3 `config.py`: `WGA_BY_METHOD_SEED` has `sam_seed*: 0.78` — INCORRECT per Izmailov 2022 Table 1. H-P2 uses 0.74.
- All 9 probe accuracies (ERM×3, SAM×3, GroupDRO×3) already in `h-m3/results.json` under `all_probe_results` key.

---

## External Dependencies API

### From h-m3/code/run_experiment.py (verified signatures)

```python
# load_resnet50: loads checkpoint, returns eval-mode model on specified device
def load_resnet50(ckpt_path: str, device: str = 'cpu') -> torch.nn.Module

# get_transform: standard ImageNet normalization for ResNet-50
def get_transform() -> torchvision.transforms.Compose

# get_loader: WILDS dataset loader for given split
def get_loader(split: str, batch_size: int, shuffle: bool = False) -> DataLoader

# extract_layer4_features: layer4 → AdaptiveAvgPool2d(1,1) → flatten → D=2048
# Returns (features: np.ndarray shape (N, 2048), bg_labels: np.ndarray shape (N,))
# bg_labels = metadata[:, 0] % 2 (0=land, 1=water background)
def extract_layer4_features(
    model: torch.nn.Module,
    dataloader: DataLoader,
    device: str,
) -> tuple[np.ndarray, np.ndarray]

# run_probe: fits probe on features, scores on SAME features (train-set scoring — do NOT use for test eval)
# H-P2 must call probe.score(test_features, test_bg_labels) separately
def run_probe(features: np.ndarray, labels: np.ndarray, method: str, seed: int) -> float
```

### Import pattern for H-P2

```python
import sys
sys.path.insert(0, '/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_scsl/docs/youra_research/h-m3/code')
import run_experiment as hm3
# Use: hm3.load_resnet50, hm3.get_transform, hm3.get_loader, hm3.extract_layer4_features
```

---

## A-5: Bootstrap CI (4 subtasks)

### A-5.1: pearsonr_stat helper (for scipy.stats.bootstrap)

```python
def pearsonr_stat(x: np.ndarray, y: np.ndarray, axis: int = -1) -> np.ndarray:
    """Statistic function for scipy.stats.bootstrap (paired=True).
    
    Args:
        x: probe_accs array, shape (n,) or batch shape
        y: wga_values array, shape (n,) or batch shape
        axis: reduction axis (passed by bootstrap)
    Returns:
        Pearson r statistic
    """
    from scipy.stats import pearsonr
    return pearsonr(x, y, axis=axis)[0]
```

### A-5.2: BCa bootstrap attempt

```python
from scipy.stats import bootstrap

def _bootstrap_bca(
    probe_accs: np.ndarray,
    wga_values: np.ndarray,
    n_resamples: int = 1000,
    confidence_level: float = 0.95,
    rng: int = 42,
) -> tuple[float, float, str]:
    """Returns (ci_low, ci_high, method_used). Raises on BCa failure."""
    result = bootstrap(
        (probe_accs, wga_values),
        pearsonr_stat,
        paired=True,
        n_resamples=n_resamples,
        confidence_level=confidence_level,
        method='BCa',
        rng=rng,
    )
    ci_low = result.confidence_interval.low
    ci_high = result.confidence_interval.high
    if np.isnan(ci_low) or np.isnan(ci_high):
        raise ValueError("BCa produced NaN confidence interval (degenerate at n=9)")
    return ci_low, ci_high, 'BCa'
```

### A-5.3: Percentile fallback

```python
def _bootstrap_percentile(
    probe_accs: np.ndarray,
    wga_values: np.ndarray,
    n_resamples: int = 1000,
    confidence_level: float = 0.95,
    rng: int = 42,
) -> tuple[float, float, str]:
    """Fallback when BCa fails at small n."""
    result = bootstrap(
        (probe_accs, wga_values),
        pearsonr_stat,
        paired=True,
        n_resamples=n_resamples,
        confidence_level=confidence_level,
        method='percentile',
        rng=rng,
    )
    return result.confidence_interval.low, result.confidence_interval.high, 'percentile'
```

### A-5.4: Main correlation + verdict function

```python
def compute_correlation_with_bootstrap(
    probe_accs: np.ndarray,   # shape (n,) — background probe accuracy per checkpoint
    wga_values: np.ndarray,   # shape (n,) — worst-group accuracy per checkpoint
    n_resamples: int = 1000,
    rng: int = 42,
    confidence_level: float = 0.95,
    confirmed_r_threshold: float = -0.5,
    suggestive_r_threshold: float = -0.3,
) -> dict:
    """
    Compute Pearson r + bootstrapped 95% CI + verdict.
    
    Returns:
        {
            'r': float,
            'p_value': float,
            'ci_low': float,
            'ci_high': float,
            'ci_method': 'BCa' | 'percentile',
            'verdict': 'CONFIRMED' | 'SUGGESTIVE' | 'REJECTED',
            'boot_distribution': np.ndarray shape (n_resamples,),
        }
    """
    from scipy.stats import pearsonr, bootstrap
    
    # Step 1: Pearson r + one-sided p-value (H1: r < 0)
    res = pearsonr(probe_accs, wga_values, alternative='less')
    r, p_value = float(res.statistic), float(res.pvalue)
    
    # Step 2: Bootstrap CI (BCa with percentile fallback)
    try:
        ci_low, ci_high, ci_method = _bootstrap_bca(
            probe_accs, wga_values, n_resamples, confidence_level, rng)
    except Exception as e:
        print(f"[H-P2] BCa failed ({e}), falling back to percentile method")
        ci_low, ci_high, ci_method = _bootstrap_percentile(
            probe_accs, wga_values, n_resamples, confidence_level, rng)
    
    # Step 3: Get bootstrap distribution for visualization
    boot_result = bootstrap(
        (probe_accs, wga_values), pearsonr_stat,
        paired=True, n_resamples=n_resamples,
        confidence_level=confidence_level, method=ci_method, rng=rng,
    )
    boot_distribution = boot_result.bootstrap_distribution
    
    # Step 4: Verdict classification
    if r < confirmed_r_threshold and ci_high < 0:
        verdict = 'CONFIRMED'
    elif r < suggestive_r_threshold and ci_low < 0:
        verdict = 'SUGGESTIVE'
    else:
        verdict = 'REJECTED'
    
    return {
        'r': r,
        'p_value': p_value,
        'ci_low': float(ci_low),
        'ci_high': float(ci_high),
        'ci_method': ci_method,
        'verdict': verdict,
        'boot_distribution': boot_distribution,
    }
```

---

## A-7: Figure 1 — Scatter + Regression (3 subtasks)

### A-7.1: Data prep for scatter

```python
METHOD_COLORS = {'ERM': '#1f77b4', 'SAM': '#ff7f0e', 'GroupDRO': '#2ca02c'}
METHOD_MARKERS = {'ERM': 'o', 'SAM': 's', 'GroupDRO': '^'}

def _prep_scatter_data(
    probe_accs: np.ndarray,   # shape (9,)
    wga_values: np.ndarray,   # shape (9,)
    methods: list[str],       # ['ERM','ERM','ERM','SAM','SAM','SAM','GroupDRO',...]
) -> dict:
    """Group data by method for color-coded scatter."""
    by_method = {}
    for i, method in enumerate(methods):
        by_method.setdefault(method, {'probe': [], 'wga': []})
        by_method[method]['probe'].append(probe_accs[i])
        by_method[method]['wga'].append(wga_values[i])
    return by_method
```

### A-7.2: Regression line computation

```python
def _compute_regression_line(
    probe_accs: np.ndarray,
    wga_values: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Returns (x_line, y_line) for plotting regression."""
    coeffs = np.polyfit(probe_accs, wga_values, 1)
    x_line = np.linspace(probe_accs.min() - 0.005, probe_accs.max() + 0.005, 100)
    y_line = np.polyval(coeffs, x_line)
    return x_line, y_line
```

### A-7.3: Full scatter plot + annotation + save

```python
def plot_scatter_probe_vs_wga(
    probe_accs: np.ndarray,
    wga_values: np.ndarray,
    methods: list[str],
    r: float,
    p_value: float,
    output_path: str,
) -> None:
    """
    Scatter: probe_acc (x) vs WGA (y), color by method, regression line, r+p annotation.
    
    Args:
        probe_accs: shape (9,)
        wga_values: shape (9,)
        methods: list of method names length 9 (e.g. ['ERM','ERM','ERM',...])
        r: Pearson r value
        p_value: one-sided p-value
        output_path: path to save PNG
    """
    import matplotlib.pyplot as plt
    
    fig, ax = plt.subplots(figsize=(7, 5))
    by_method = _prep_scatter_data(probe_accs, wga_values, methods)
    
    for method, data in by_method.items():
        ax.scatter(data['probe'], data['wga'],
                   color=METHOD_COLORS[method], marker=METHOD_MARKERS[method],
                   s=80, label=method, zorder=3)
    
    x_line, y_line = _compute_regression_line(probe_accs, wga_values)
    ax.plot(x_line, y_line, 'k--', linewidth=1.2, alpha=0.7, label='Regression')
    
    ax.annotate(f'r = {r:.3f}\np = {p_value:.4f} (one-sided)',
                xy=(0.05, 0.15), xycoords='axes fraction', fontsize=10,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.8))
    
    ax.set_xlabel('Spurious Probe Accuracy (Background Decodability)', fontsize=11)
    ax.set_ylabel('Worst-Group Accuracy (WGA)', fontsize=11)
    ax.set_title('Spurious Probe Accuracy vs WGA\n(9 ResNet-50 Checkpoints)', fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"[H-P2] Figure saved: {output_path}")
```

---

## A-8: Figure 2 — Bootstrap Distribution (2 subtasks)

### A-8.1: Histogram computation

```python
def _prep_bootstrap_hist(
    boot_distribution: np.ndarray,   # shape (1000,)
    ci_low: float,
    ci_high: float,
    n_bins: int = 40,
) -> dict:
    """Prepare histogram data for bootstrap distribution plot."""
    return {
        'distribution': boot_distribution,
        'ci_low': ci_low,
        'ci_high': ci_high,
        'n_bins': n_bins,
        'mean_r': float(boot_distribution.mean()),
    }
```

### A-8.2: Bootstrap distribution plot + save

```python
def plot_bootstrap_distribution(
    boot_distribution: np.ndarray,   # shape (1000,)
    ci_low: float,
    ci_high: float,
    output_path: str,
    ci_method: str = 'BCa',
) -> None:
    """
    Histogram of 1000 bootstrap r values with 95% CI bounds marked.
    
    Args:
        boot_distribution: array of shape (n_resamples,)
        ci_low, ci_high: 95% CI bounds
        output_path: path to save PNG
        ci_method: 'BCa' or 'percentile' (for title annotation)
    """
    import matplotlib.pyplot as plt
    
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(boot_distribution, bins=40, color='steelblue', alpha=0.7, edgecolor='white')
    ax.axvline(ci_low, color='red', linestyle='--', linewidth=1.5,
               label=f'95% CI [{ci_low:.3f}, {ci_high:.3f}] ({ci_method})')
    ax.axvline(ci_high, color='red', linestyle='--', linewidth=1.5)
    ax.axvline(0, color='black', linestyle='-', linewidth=1.0, alpha=0.5, label='r=0 (null)')
    ax.set_xlabel('Bootstrap Pearson r', fontsize=11)
    ax.set_ylabel('Count', fontsize=11)
    ax.set_title(f'Bootstrap Distribution of Pearson r (n=1000 resamples)', fontsize=12)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"[H-P2] Figure saved: {output_path}")
```

---

## A-9: Figures 3+4 — Method Comparison + Ablation (2 subtasks)

### A-9.1: Method comparison bar chart

```python
def plot_method_comparison(
    probe_accs_by_method: dict,   # {'ERM': [f1,f2,f3], 'SAM': [...], 'GroupDRO': [...]}
    wga_by_method: dict,          # {'ERM': [0.72,0.72,0.72], ...}
    output_path: str,
) -> None:
    """
    Side-by-side bar chart: mean probe_acc and WGA per method with seed error bars.
    Two subplots: left=probe_acc, right=WGA.
    """
    import matplotlib.pyplot as plt
    
    methods = ['ERM', 'SAM', 'GroupDRO']
    colors = [METHOD_COLORS[m] for m in methods]
    
    probe_means = [np.mean(probe_accs_by_method[m]) for m in methods]
    probe_stds  = [np.std(probe_accs_by_method[m], ddof=1) for m in methods]
    wga_means   = [np.mean(wga_by_method[m]) for m in methods]
    wga_stds    = [np.std(wga_by_method[m], ddof=1) for m in methods]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    x = np.arange(len(methods))
    
    ax1.bar(x, probe_means, yerr=probe_stds, color=colors, alpha=0.8,
            capsize=5, width=0.5)
    ax1.set_xticks(x); ax1.set_xticklabels(methods)
    ax1.set_ylabel('Probe Accuracy'); ax1.set_title('Background Probe Accuracy by Method')
    ax1.set_ylim(0.9, 1.0); ax1.grid(True, alpha=0.3, axis='y')
    
    ax2.bar(x, wga_means, yerr=wga_stds, color=colors, alpha=0.8,
            capsize=5, width=0.5)
    ax2.set_xticks(x); ax2.set_xticklabels(methods)
    ax2.set_ylabel('WGA'); ax2.set_title('Worst-Group Accuracy by Method')
    ax2.set_ylim(0.6, 1.0); ax2.grid(True, alpha=0.3, axis='y')
    
    plt.suptitle('Method Comparison: Probe Accuracy vs WGA', fontsize=12)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
```

### A-9.2: Ablation sensitivity bar chart

```python
def plot_ablation_sensitivity(
    ablation_results: dict,   # {'full_9': r_val, 'erm_gdro_6': r_val, 'method_means_3': r_val}
    output_path: str,
) -> None:
    """
    Bar chart of Pearson r for 3 ablation variants.
    Shows sensitivity of correlation to dataset composition.
    """
    import matplotlib.pyplot as plt
    
    labels = ['Full\n(n=9)', 'ERM+GroupDRO\n(n=6)', 'Method Means\n(n=3)']
    keys = ['full_9', 'erm_gdro_6', 'method_means_3']
    r_vals = [ablation_results[k]['r'] for k in keys]
    
    colors = ['steelblue' if r < -0.5 else 'orange' if r < -0.3 else 'salmon'
              for r in r_vals]
    
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(labels, r_vals, color=colors, alpha=0.8, width=0.5)
    ax.axhline(-0.5, color='green', linestyle='--', linewidth=1.2,
               label='CONFIRMED threshold (r=-0.5)')
    ax.axhline(-0.3, color='orange', linestyle='--', linewidth=1.2,
               label='SUGGESTIVE threshold (r=-0.3)')
    ax.axhline(0, color='black', linewidth=0.8, alpha=0.5)
    
    for bar, r in zip(bars, r_vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() - 0.03,
                f'r={r:.3f}', ha='center', va='top', fontsize=10)
    
    ax.set_ylabel('Pearson r'); ax.set_title('Ablation Sensitivity: Pearson r by Dataset')
    ax.set_ylim(-1.0, 0.1); ax.legend(fontsize=9); ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
```

---

## Tensor Shapes Summary

| Variable | Shape | dtype | Notes |
|----------|-------|-------|-------|
| `probe_accs` | `(9,)` | float64 | One per distinct-backbone checkpoint |
| `wga_values` | `(9,)` | float64 | From Izmailov 2022 Table 1 |
| `layer4_features` (per checkpoint, if re-extracted) | `(N, 2048)` | float32 | N=5794 (test) or ~4795 (train) |
| `boot_distribution` | `(1000,)` | float64 | Bootstrap r samples |
| `ci_low, ci_high` | scalar | float64 | 95% CI bounds |
| `r, p_value` | scalar | float64 | Pearson r, one-sided p |

---

## Pseudo-code: Full Experiment Flow

```python
def main():
    import json, os
    import numpy as np
    import config_p2 as cfg
    
    # 1. Load probe accuracies from h-m3/results.json
    with open(cfg.HM3_RESULTS_JSON) as f:
        hm3_results = json.load(f)
    
    probe_accs_dict = hm3_results.get('all_probe_results', hm3_results)
    # Expected keys: erm_seed1..3, sam_seed1..3, groupdro_seed1..3
    
    # 2. Assemble 9-point arrays (ordered: ERM×3, SAM×3, GroupDRO×3)
    ordered_keys = [f'erm_seed{s}' for s in [1,2,3]] + \
                   [f'sam_seed{s}' for s in [1,2,3]] + \
                   [f'groupdro_seed{s}' for s in [1,2,3]]
    
    # Check for missing SAM probes — re-extract if needed
    for key in ordered_keys:
        if key not in probe_accs_dict:
            print(f"[H-P2] {key} missing from h-m3/results.json — re-extracting")
            probe_accs_dict[key] = _reextract_sam_probe(key, cfg)
    
    probe_accs = np.array([probe_accs_dict[k] for k in ordered_keys])
    wga_values = np.array([cfg.WGA_BY_METHOD_SEED[k] for k in ordered_keys])
    methods = ['ERM','ERM','ERM','SAM','SAM','SAM','GroupDRO','GroupDRO','GroupDRO']
    
    # 3. Main correlation
    corr = compute_correlation_with_bootstrap(probe_accs, wga_values)
    
    # 4. Ablation variants
    ablations = run_ablations(probe_accs, wga_values, methods)
    
    # 5. Generate figures
    os.makedirs(cfg.FIGURES_DIR, exist_ok=True)
    plot_scatter_probe_vs_wga(probe_accs, wga_values, methods,
                              corr['r'], corr['p_value'],
                              f"{cfg.FIGURES_DIR}/scatter_probe_vs_wga.png")
    plot_bootstrap_distribution(corr['boot_distribution'], corr['ci_low'],
                                corr['ci_high'],
                                f"{cfg.FIGURES_DIR}/bootstrap_distribution.png",
                                corr['ci_method'])
    plot_method_comparison(
        {m: [probe_accs[i] for i,me in enumerate(methods) if me==m] for m in ['ERM','SAM','GroupDRO']},
        {m: [wga_values[i] for i,me in enumerate(methods) if me==m] for m in ['ERM','SAM','GroupDRO']},
        f"{cfg.FIGURES_DIR}/method_comparison_bar.png")
    plot_ablation_sensitivity(ablations, f"{cfg.FIGURES_DIR}/ablation_sensitivity.png")
    
    # 6. Save results.json
    save_results(probe_accs_dict, wga_values, corr, ablations, ordered_keys, cfg)
    
    # 7. Print gate verdict
    print(f"[H-P2] GATE RESULT: {corr['verdict']}")
    print(f"[H-P2] r={corr['r']:.4f}, p={corr['p_value']:.4f}, "
          f"CI=[{corr['ci_low']:.4f}, {corr['ci_high']:.4f}] ({corr['ci_method']})")
```
