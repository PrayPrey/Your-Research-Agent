# Logic: h-e1 — Semantic Accommodation Existence (EXISTENCE PoC)

**Hypothesis:** h-e1
**Type:** EXISTENCE (PoC)
**Date:** 2026-03-15

Applied: numpy seed-based bootstrap percentile CI pattern; sklearn NearestNeighbors cosine metric pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None — new implementation

---

## A-5: Statistical Testing [Complexity: 15, Budget: 4 subtasks]

### L-5-1: bootstrap_c_sem()

**File**: `code/statistics.py`

```python
def bootstrap_c_sem(
    cos_actual: np.ndarray,  # shape (N,)
    cos_random: np.ndarray,  # shape (N,)
    n_bootstrap: int = 1000,
    seed: int = 42
) -> tuple[float, np.ndarray]:
    # returns (c_sem_mean: float, ci: np.ndarray shape (2,))
```

### Pseudo-code

```
rng = np.random.default_rng(seed)
N = len(cos_actual)
samples = np.empty(n_bootstrap)  # (1000,)
for i in range(n_bootstrap):
    idx = rng.integers(0, N, size=N)          # (N,) bootstrap indices
    samples[i] = cos_actual[idx].mean() - cos_random[idx].mean()
c_sem_mean = samples.mean()
ci = np.percentile(samples, [2.5, 97.5])     # shape (2,)
return c_sem_mean, ci
```

**Edge cases**: assert len(cos_actual) == len(cos_random); assert N >= 1.

---

### L-5-2: bootstrap_cohen_d()

**File**: `code/statistics.py`

```python
def bootstrap_cohen_d(
    a: np.ndarray,  # shape (N,)
    b: np.ndarray,  # shape (M,)
    n_bootstrap: int = 1000,
    seed: int = 42
) -> tuple[float, np.ndarray]:
    # returns (d_mean: float, ci: np.ndarray shape (2,))
```

### Pseudo-code

```
rng = np.random.default_rng(seed)
N, M = len(a), len(b)
samples = np.empty(n_bootstrap)  # (1000,)
for i in range(n_bootstrap):
    a_boot = a[rng.integers(0, N, size=N)]    # (N,)
    b_boot = b[rng.integers(0, M, size=M)]    # (M,)
    mean_diff = a_boot.mean() - b_boot.mean()
    pooled_std = sqrt(((N-1)*a_boot.var(ddof=1) + (M-1)*b_boot.var(ddof=1)) / (N+M-2))
    samples[i] = mean_diff / pooled_std if pooled_std > 0 else 0.0
d_mean = samples.mean()
ci = np.percentile(samples, [2.5, 97.5])     # shape (2,)
return d_mean, ci
```

**Edge cases**: if pooled_std == 0, return d=0; assert N >= 2 and M >= 2.

---

### L-5-3: run_all_tests()

**File**: `code/statistics.py`

```python
def run_all_tests(
    cos_actual: np.ndarray,  # shape (N,)
    cos_topic: np.ndarray,   # shape (N,)
    cos_random: np.ndarray,  # shape (N,)
    n_pairs: int
) -> dict:
    # returns full results dict
```

### Pseudo-code

```
assert n_pairs >= MIN_N_PAIRS  # raise ValueError if < 1000

c_sem_mean, c_sem_ci = bootstrap_c_sem(cos_actual, cos_random)

stat_av, p_av = mann_whitney_test(cos_actual, cos_topic, alternative='greater')
stat_vr, p_vr = mann_whitney_test(cos_topic, cos_random, alternative='greater')

d_actual_topic_mean, d_actual_topic_ci = bootstrap_cohen_d(cos_actual, cos_topic)
d_actual_random_mean, d_actual_random_ci = bootstrap_cohen_d(cos_actual, cos_random)
d_topic_random_mean, d_topic_random_ci  = bootstrap_cohen_d(cos_topic, cos_random)

return {
    "n_pairs": n_pairs,
    "c_sem": c_sem_mean,
    "c_sem_ci": c_sem_ci.tolist(),         # [lower, upper]
    "cos_actual_mean": cos_actual.mean(),
    "cos_topic_mean":  cos_topic.mean(),
    "cos_random_mean": cos_random.mean(),
    "mann_whitney_actual_vs_topic": {"statistic": stat_av, "p_value": p_av},
    "mann_whitney_topic_vs_random": {"statistic": stat_vr, "p_value": p_vr},
    "cohen_d_actual_vs_topic":  {"d": d_actual_topic_mean,  "ci": d_actual_topic_ci.tolist()},
    "cohen_d_actual_vs_random": {"d": d_actual_random_mean, "ci": d_actual_random_ci.tolist()},
    "cohen_d_topic_vs_random":  {"d": d_topic_random_mean,  "ci": d_topic_random_ci.tolist()},
}
```

**Edge cases**: ValueError with message if n_pairs < MIN_N_PAIRS.

---

### L-5-4: verify_mechanism_activated()

**File**: `code/statistics.py`

```python
def verify_mechanism_activated(results: dict) -> tuple[bool, dict]:
    # results: output of run_all_tests() + "embeddings_computed" key
    # returns (passed: bool, indicators: dict)
```

### Pseudo-code

```
indicators = {
    "embeddings_computed":  results.get("embeddings_computed", False),
    "c_sem_positive":       results["c_sem"] > 0,
    "ci_lower_positive":    results["c_sem_ci"][0] > 0,
    "ordering_holds":       (results["cos_actual_mean"] > results["cos_topic_mean"]
                             and results["cos_topic_mean"] > results["cos_random_mean"]),
    "sufficient_pairs":     results["n_pairs"] >= MIN_N_PAIRS,
}
passed = all(indicators.values())
return passed, indicators
```

**Edge cases**: KeyError on missing keys propagates naturally (caller must provide complete results dict).

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | bootstrap_c_sem | Bootstrap CI for C_sem scalar at 95% percentile |
| L-5-2 | bootstrap_cohen_d | Bootstrap Cohen's d with pooled-std formula |
| L-5-3 | run_all_tests | Orchestrate all stat tests, return full results dict |
| L-5-4 | verify_mechanism_activated | Check 5 gate indicators, return (bool, dict) |

---

## A-3: Control Construction [Complexity: 13, Budget: 1 subtask]

### L-3-1: build_topic_control()

**File**: `code/controls.py`

```python
def build_topic_control(
    prompt_embeddings: np.ndarray,  # shape (N, D)  D=384
    ai_embeddings: np.ndarray,      # shape (N, D)
    k: int = 5
) -> np.ndarray:
    # returns (N, D) float32 — mean of K topic-matched AI embeddings
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| prompt_embeddings | (N, 384) | L2-normalized SBERT, N~100K-140K |
| ai_embeddings | (N, 384) | L2-normalized SBERT |
| distances | (N, k+1) | cosine distances to k+1 neighbors (includes self) |
| indices | (N, k+1) | neighbor row indices in prompt_embeddings |
| neighbor_idx | (N, k) | indices[:,1:k+1] — self excluded |
| matched | (N, k, 384) | ai_embeddings[neighbor_idx] |
| output | (N, 384) | mean over k axis, float32 |

### Pseudo-code

```
nn = NearestNeighbors(n_neighbors=k+1, metric='cosine', algorithm='brute', n_jobs=-1)
nn.fit(prompt_embeddings)                          # fit on (N, D)
distances, indices = nn.kneighbors(prompt_embeddings)  # both (N, k+1)

neighbor_idx = indices[:, 1:k+1]                  # (N, k) — exclude self at col 0
matched = ai_embeddings[neighbor_idx]              # (N, k, D)
topic_control = matched.mean(axis=1)               # (N, D)
return topic_control.astype(np.float32)            # (N, D)
```

**Edge cases**:
- N must be > k+1; assert len(prompt_embeddings) > k+1
- If embeddings not L2-normalized, cosine distance still valid but warn
- Memory note: indices array is (N, k+1) int64 ~ 5.6MB for N=140K, k=5

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | build_topic_control | KNN K=5 topic-matched control with self-exclusion, mean aggregation |
