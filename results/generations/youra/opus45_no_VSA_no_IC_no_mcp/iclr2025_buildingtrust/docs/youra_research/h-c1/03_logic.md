# H-C1: Stratified Correlation Analysis - Logic Design

## Core Algorithm

```python
def stratified_partial_correlation(df, metric_col, youra_col, control_col, model_type_col):
    """
    Compute partial correlation per model group with bootstrap CIs.
    
    Args:
        df: DataFrame with columns [metric_col, youra_col, control_col, model_type_col]
        metric_col: str - target metric (e.g., 'benchmark_score')
        youra_col: str - YOURA score column
        control_col: str - control variable (e.g., 'log_params')
        model_type_col: str - 'base' or 'instruct'
    
    Returns:
        dict: {group: {'r': float, 'ci_low': float, 'ci_high': float, 'n': int}}
    """
    results = {}
    for group in ['base', 'instruct']:
        subset = df[df[model_type_col] == group]
        
        if len(subset) < 10:  # minimum sample guard
            results[group] = {'r': None, 'ci_low': None, 'ci_high': None, 
                              'n': len(subset), 'error': 'insufficient_samples'}
            continue
        
        r = partial_corr(subset[youra_col], subset[metric_col], subset[control_col])
        ci_low, ci_high = bootstrap_ci(subset, youra_col, metric_col, control_col, n_iter=1000)
        
        results[group] = {'r': r, 'ci_low': ci_low, 'ci_high': ci_high, 'n': len(subset)}
    
    return results
```

## Partial Correlation

```python
def partial_corr(x, y, z):
    """
    Partial correlation of x,y controlling for z.
    Uses residualization: corr(resid(x~z), resid(y~z))
    
    Shapes:
        x, y, z: (n_samples,) arrays
    Returns:
        float: partial correlation coefficient
    """
    x_resid = x - linear_predict(z, x)  # residuals from regressing x on z
    y_resid = y - linear_predict(z, y)  # residuals from regressing y on z
    return pearsonr(x_resid, y_resid)
```

## Bootstrap CI

```python
def bootstrap_ci(subset, x_col, y_col, z_col, n_iter=1000, alpha=0.05):
    """
    Bootstrap confidence interval for partial correlation.
    
    Shapes:
        subset: DataFrame (n_samples, 3+)
        boot_rs: (n_iter,) array of bootstrapped r values
    
    Returns:
        (ci_low, ci_high): tuple of floats
    """
    n = len(subset)
    boot_rs = np.empty(n_iter)
    
    for i in range(n_iter):
        idx = np.random.choice(n, size=n, replace=True)
        sample = subset.iloc[idx]
        boot_rs[i] = partial_corr(sample[x_col], sample[y_col], sample[z_col])
    
    return np.percentile(boot_rs, [alpha/2 * 100, (1 - alpha/2) * 100])
```

## Gate Evaluation

```python
def evaluate_gate(results, threshold=0.2):
    """
    Gate: both groups must have r > threshold with positive sign.
    
    Returns:
        dict: {'passed': bool, 'reason': str, 'details': dict}
    """
    for group in ['base', 'instruct']:
        if results[group].get('error'):
            return {'passed': False, 'reason': f'{group}_insufficient_data'}
        if results[group]['r'] is None or results[group]['r'] <= threshold:
            return {'passed': False, 'reason': f'{group}_below_threshold', 
                    'details': results}
        if results[group]['r'] < 0:
            return {'passed': False, 'reason': f'{group}_negative_correlation'}
    
    return {'passed': True, 'reason': 'both_groups_pass', 'details': results}
```

## Error Handling

| Condition | Action |
|-----------|--------|
| n < 10 per group | Skip group, flag `insufficient_samples` |
| Singular matrix in regression | Return `r=None`, flag `collinearity` |
| All bootstrap samples fail | Return CI as `(None, None)` |
| One group fails, one passes | Gate fails with specific reason |

## Data Shapes Summary

```
Input DataFrame: (n_models, 4+)
  - youra_score: (n_models,)
  - metric: (n_models,)
  - log_params: (n_models,)
  - model_type: (n_models,) categorical

Per-group subset: (n_group,) where n_group ~ n_models/2
Bootstrap array: (1000,) per group
Output: dict with 2 group entries
```
