# Logic: H-M4 Hedging-Confidence Correlation Analysis

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new API design (no h-m3/code/ or h-m4/code/ exists yet; H-M2 results schema fully specified in PRD/brief, no live code to verify)
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-1: HedgingConfidenceAnalyzer [Complexity: 2, Budget: 5]

**Applied**: correlation_analysis_pattern

### API Signatures

```python
from dataclasses import dataclass
from typing import List, Tuple, Optional
import json
import numpy as np
from scipy.stats import spearmanr

@dataclass
class CorrelationResult:
    spearman_r: float
    p_value: float
    n_samples: int
    gate_pass: bool
    confidence_interval: Tuple[float, float]  # 95% CI via bootstrap


class HedgingConfidenceAnalyzer:
    def __init__(self, h_m2_results_path: str):
        """Load path to H-M2 cached results JSON."""
        ...

    def load_data(self) -> int:
        """Extract (hedging_count, confidence) pairs. Returns n valid samples."""
        ...

    def compute_correlation(self) -> CorrelationResult:
        """Spearman r + p-value + bootstrap 95% CI + gate check."""
        ...

    def detect_outliers(self) -> List[int]:
        """IQR-based outlier indices on confidence_scores."""
        ...

    def generate_visualizations(self, output_dir: str) -> List[str]:
        """Scatter+regression, box-by-bucket, gate bar chart, histogram. Returns PNG paths."""
        ...

    def export_results(self, output_path: str) -> None:
        """Write JSON with all metrics + markdown summary alongside."""
        ...
```

### Tensor Shapes

N/A - no tensors. Data is 1D Python lists / numpy arrays of length n (~817, filtered to valid pairs).

| Variable | Type | Note |
|----------|------|------|
| hedging_counts | List[int], len n | marker count per sample |
| confidence_scores | List[float], len n | 0-100 |

### Pseudo-code

```
load_data():
    data = json.load(open(h_m2_results_path))
    for item in data['outputs']:
        if item.get('hedging_count') is not None and item.get('confidence') is not None:
            hedging_counts.append(item['hedging_count'])
            confidence_scores.append(item['confidence'])
    assert len(hedging_counts) >= 500, "insufficient valid samples"
    return len(hedging_counts)

compute_correlation():
    r, p = spearmanr(hedging_counts, confidence_scores)
    ci_low, ci_high = bootstrap_ci(hedging_counts, confidence_scores, n_boot=1000, seed=42)
    gate_pass = (r < -0.2) and (p < 0.05)
    return CorrelationResult(r, p, n, gate_pass, (ci_low, ci_high))

bootstrap_ci(x, y, n_boot, seed):
    rng = np.random.default_rng(seed)
    idx = np.arange(len(x))
    rs = [spearmanr(x[i], y[i])[0] for i in (rng.choice(idx, len(idx)) for _ in range(n_boot))]
    return np.percentile(rs, [2.5, 97.5])

detect_outliers():
    q1, q3 = percentile(confidence_scores, [25, 75])
    iqr = q3 - q1
    return indices where confidence outside [q1-1.5*iqr, q3+1.5*iqr]

generate_visualizations(output_dir):
    fig1 = scatter(hedging_counts, confidence_scores) + sns.regplot line  -> "scatter_regression.png"
    buckets = bucketize(hedging_counts, [0], [1,2], [3,5], [6, inf])
    fig2 = seaborn.boxplot(bucket_label vs confidence)  -> "boxplot_buckets.png"
    fig3 = bar(["threshold (-0.2)", "actual r"], [-0.2, spearman_r])  -> "gate_comparison.png"
    fig4 = histogram(hedging_counts)  -> "hedging_distribution.png"
    return [paths...]

export_results(output_path):
    json.dump({
        "spearman_r": r, "p_value": p, "n_samples": n, "gate_pass": gate_pass,
        "confidence_interval": [ci_low, ci_high],
        "outlier_count": len(outliers)
    }, output_path)
    write markdown summary to output_path.replace('.json', '_summary.md')
```

### Subtasks [4/5 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | load_data | Parse H-M2 JSON, filter valid pairs, assert n>=500 |
| L-1-2 | compute_correlation | spearmanr + bootstrap CI + gate check |
| L-1-3 | generate_visualizations | 4 matplotlib/seaborn figures to PNG |
| L-1-4 | export_results | JSON + markdown summary export |

---

## Main Script Entry Point

```python
def main():
    analyzer = HedgingConfidenceAnalyzer("../h-m2/code/results/h-m2_results.json")
    n = analyzer.load_data()
    result = analyzer.compute_correlation()
    analyzer.generate_visualizations("figures/")
    analyzer.export_results("results/h-m4_results.json")
    print(f"Computing Spearman correlation: r={result.spearman_r:.4f}, p={result.p_value:.4e}")
    print(f"Gate pass: {result.gate_pass}")

if __name__ == "__main__":
    main()
```

**Expected H-M2 output schema** (`h-m2_results.json`):
```json
{"outputs": [{"question_id": str, "output_text": str, "hedging_count": int, "confidence": float, "hedging_markers": [str], "is_correct": bool}, ...]}
```
