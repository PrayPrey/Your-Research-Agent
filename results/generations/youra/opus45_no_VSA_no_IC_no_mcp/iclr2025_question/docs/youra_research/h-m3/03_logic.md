# Logic: H-M3 Orthogonal Signals Complementary Detection

**Type**: MECHANISM (pure statistical analysis, no ML inference, CPU only)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new API design. H-M3 only reads JSON outputs from H-M1/H-M2 (data contract, not code dependency) — no source code coupling to verify.
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## Data Contracts

### Input: H-M1 result (`h-m1/results/entropy_scores.json`)
```json
{"entropy_scores": [float; 817], "labels": [bool; 817]}
```

### Input: H-M2 result (`h-m2/results/consistency_scores.json`)
```json
{"consistency_scores": [float; 817]}
```

**Contract assumption**: index `i` refers to the same question across both files (identical ordering, same 817-question TruthfulQA generation split). No question-ID join is performed — order alignment only.

---

## A-1: Orthogonality Analysis Module [Complexity: Medium, Budget: 4]

**Applied**: Standard scipy/sklearn statistics (Pearson/Spearman correlation, rank-based discordance, ROC-AUC)

### API Signatures

```python
import numpy as np

def load_scores(h_m1_path: str, h_m2_path: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Load entropy [817], consistency [817], labels [817] (bool, True=correct)."""
    ...

def compute_correlation(entropy: np.ndarray, consistency: np.ndarray) -> dict:
    """Pearson/Spearman r between entropy and (1-consistency). entropy,consistency: [N]"""
    ...

def identify_discordant(entropy: np.ndarray, consistency: np.ndarray) -> dict:
    """Rank-based discordant case identification. entropy,consistency: [N]"""
    ...

def compute_subset_auroc(entropy: np.ndarray, consistency: np.ndarray,
                          labels: np.ndarray, disc: dict) -> dict:
    """AUROC per discordant subset. labels: [N] bool"""
    ...

def plot_scatter(entropy: np.ndarray, consistency: np.ndarray,
                  labels: np.ndarray, output_path: str) -> None:
    """Scatter entropy vs (1-consistency) colored by correctness."""
    ...

def plot_quadrant(entropy: np.ndarray, consistency: np.ndarray,
                   labels: np.ndarray, output_path: str) -> None:
    """Quadrant plot via median splits on entropy/(1-consistency)."""
    ...

def main() -> None:
    """Orchestrates FR-1..FR-6, writes results/correlation_analysis.json, subset_auroc.json, discordant_cases.csv, figures/*.png"""
    ...
```

### Tensor/Array Shapes

| Variable | Shape | Note |
|----------|-------|------|
| entropy | [817] | float, from H-M1 |
| consistency | [817] | float, from H-M2, higher = more consistent (good) |
| labels | [817] | bool, True = correct |
| e_rank, c_rank_inv | [817] | percentile ranks in [0,1] |
| discordant_mask | [817] | bool |
| high_entropy_only / high_inconsistency_only | [817] | bool, mutually exclusive subsets of discordant_mask |

### Pseudo-code

**compute_correlation**
```
inv_consistency = 1 - consistency
r_pearson, p_pearson = pearsonr(entropy, inv_consistency)
r_spearman, p_spearman = spearmanr(entropy, inv_consistency)
return {pearson_r, pearson_p, spearman_r, spearman_p, primary_pass: r_pearson < 0.3}
```

**identify_discordant**
```
n = len(entropy)
e_rank = rankdata(entropy) / n
c_rank_inv = 1 - rankdata(consistency) / n
rank_diff = abs(e_rank - c_rank_inv)
discordant = rank_diff > 0.5
high_entropy_only = discordant & (e_rank > c_rank_inv)
high_inconsistency_only = discordant & (c_rank_inv > e_rank)
return {discordant_mask, high_entropy_only, high_inconsistency_only,
        discordant_proportion: discordant.sum()/n, n_discordant}
```

**compute_subset_auroc**
```
IF high_entropy_only.sum() >= 50:
    auroc_entropy_subset = roc_auc_score(labels[high_entropy_only], -entropy[high_entropy_only])
IF high_inconsistency_only.sum() >= 50:
    auroc_consistency_subset = roc_auc_score(labels[high_inconsistency_only], consistency[high_inconsistency_only])
return {auroc_entropy_subset?, n_entropy_subset?, auroc_consistency_subset?, n_consistency_subset?}
```
Note: min-50 guard — if a subset is too small, its AUROC key is simply absent; `main()` treats missing key as 0 when evaluating `secondary_pass`.

### Gate Evaluation (in main)
```
primary_pass = pearson_r < 0.3
secondary_pass = (discordant_proportion > 0.15
                   AND auroc_entropy_subset > 0.6
                   AND auroc_consistency_subset > 0.6)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A1-1 | load_scores + compute_correlation | JSON loading, Pearson/Spearman |
| L-A1-2 | identify_discordant | Rank normalization + discordant subsets |
| L-A1-3 | compute_subset_auroc | Subset AUROC with N>=50 guard |
| L-A1-4 | plot_scatter, plot_quadrant, main | Visualization + orchestration + result JSON/CSV writing |
