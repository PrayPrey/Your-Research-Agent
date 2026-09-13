# Logic: H-E1 (EXISTENCE PoC)

**Applied**: gpleiss/temperature_scaling canonical ECE binning (no other KB pattern matched — KB search returned unrelated diffusion-model results).

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: No existing code — new implementation from scratch
**Analyzed Path**: N/A
**Relevant Symbols**: None

---

## A-3: ECE Computation [Complexity: 6, Budget: 6]

**Applied**: gpleiss/temperature_scaling ECE binning pattern

### API Signatures

```python
def compute_ece(confidences: torch.Tensor, accuracies: torch.Tensor, n_bins: int = 15) -> float:
    """ECE via equal-width binning. confidences/accuracies: [N] -> scalar."""
    ...

def compute_cluster_eces(results_by_cluster: dict[int, dict]) -> dict[int, float]:
    """results_by_cluster[cid] = {'confidences': Tensor[N_c], 'accuracies': Tensor[N_c]}"""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| confidences | [N] | float in [0,1], max softmax prob |
| accuracies | [N] | bool/float, 1 if predicted==correct |
| bin_boundaries | [n_bins+1] | torch.linspace(0,1,n_bins+1) |

### Pseudo-code

```
for i in range(n_bins):
    in_bin = (conf > bounds[i]) & (conf <= bounds[i+1])
    if in_bin.any():
        ece += |mean(conf[in_bin]) - mean(acc[in_bin])| * mean(in_bin)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | compute_ece | Single-cluster ECE, 15-bin loop, torch tensors |
| L-3-2 | compute_cluster_eces | Loop over 7 clusters, call compute_ece per cluster, return dict[int,float] |

---

## A-4: Bootstrap + ANOVA [Complexity: 9, Budget: 9]

**Applied**: Standard bootstrap resampling + scipy.stats.f_oneway; no KB pattern (not deep-learning specific).

### API Signatures

```python
def bootstrap_cluster_ece(
    confidences: torch.Tensor, accuracies: torch.Tensor, n_bootstrap: int = 100, n_bins: int = 15
) -> np.ndarray:
    """Resample N indices w/ replacement, n_bootstrap times. Returns [n_bootstrap] ECE array."""
    ...

def run_anova(bootstrap_samples_by_cluster: dict[int, np.ndarray]) -> tuple[float, float]:
    """dict[cid] -> [n_bootstrap]. Returns (f_stat, p_value) from scipy.stats.f_oneway."""
    ...

def bonferroni_pairwise(bootstrap_samples_by_cluster: dict[int, np.ndarray]) -> dict[tuple[int, int], float]:
    """Pairwise t-test per cluster pair, p * n_pairs (Bonferroni), clipped to 1.0."""
    ...

def confidence_interval(samples: np.ndarray, ci: float = 0.95) -> tuple[float, float]:
    """np.percentile(samples, [(1-ci)/2*100, (1+ci)/2*100]) -> (lo, hi)."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| bootstrap_samples_by_cluster[cid] | [100] | np.ndarray of ECE floats |
| pairwise p-values | 7 choose 2 = 21 entries | keys are (cid_a, cid_b), a<b |

### Pseudo-code

```
bootstrap_cluster_ece:
    N = len(confidences)
    samples = []
    for _ in range(n_bootstrap):
        idx = np.random.choice(N, N, replace=True)
        samples.append(compute_ece(confidences[idx], accuracies[idx], n_bins))
    return np.array(samples)

bonferroni_pairwise:
    pairs = combinations(cluster_ids, 2)
    n_pairs = len(pairs)
    for (a, b) in pairs:
        _, p = scipy.stats.ttest_ind(samples[a], samples[b])
        result[(a,b)] = min(p * n_pairs, 1.0)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | bootstrap_cluster_ece | Resample loop, reuse compute_ece from A-3 |
| L-4-2 | run_anova + bonferroni_pairwise + confidence_interval | scipy stats wrappers, dict aggregation |

---

## Self-Validation

- [x] No ASCII diagrams
- [x] Archon KB search logged as single "Applied" line (no match — noted)
- [x] Docstrings <=2 lines
- [x] Tensor shapes in tables/comments
- [x] Subtask count within budget (4 subtasks total, 2 per allocated task)
- [x] Total length < 150 lines
- [x] Codebase Analysis (Serena) section included — green-field, Serena skip noted
