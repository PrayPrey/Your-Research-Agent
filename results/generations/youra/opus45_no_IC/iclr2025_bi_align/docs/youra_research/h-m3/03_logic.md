# Logic: H-M3 — Lower Delta Signals Accommodation

**Applied:** No relevant KB pattern (diffusion-model repos only) — standard numpy/scipy block bootstrap used instead.

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** Green-field — no existing code to analyze
**Analyzed Path:** N/A
**Relevant Symbols:** None — new implementation

---

## A-6: Cluster Bootstrap [Complexity: 12, Budget: 12]

**Applied:** Standard block/cluster bootstrap (resample conversation_ids with replacement, not individual rows) to correct p-values for within-conversation correlation.

### API Signatures

```python
def cluster_bootstrap_pvalue(
    deltas: np.ndarray,            # [N] float, formality delta per turn pair
    continuations: np.ndarray,     # [N] int/bool, 1=continued 0=stopped
    conversation_ids: np.ndarray,  # [N] str/int, cluster key
    n_boot: int = 2000,
    seed: int = 42,
) -> tuple[float, np.ndarray]:
    """Block bootstrap over conversation_ids. Returns (p_robust, boot_rho_dist[n_boot])."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| deltas, continuations, conversation_ids | [N] | N ~111K rows, all same length |
| unique_ids | [C] | C unique conversations, C << N |
| boot_rho_dist | [n_boot] | one Spearman rho per bootstrap replicate |

### Pseudo-code

```
1. observed_rho, _ = spearmanr(deltas, continuations)
2. unique_ids = np.unique(conversation_ids)
3. build id -> row_indices map (groupby conversation_id), C = len(unique_ids)
4. rng = np.random.default_rng(seed)
5. boot_rhos = np.empty(n_boot)
6. for b in range(n_boot):
     sampled_ids = rng.choice(unique_ids, size=C, replace=True)   # resample CONVERSATIONS
     idx = concatenate(row_indices[cid] for cid in sampled_ids)   # pull all rows for each sampled conv
     rho_b, _ = spearmanr(deltas[idx], continuations[idx])
     boot_rhos[b] = 0.0 if isnan(rho_b) else rho_b                # guard: degenerate resample (all-same-label)
7. # two-sided p-value: fraction of bootstrap rhos at least as extreme as 0 under null,
   # centered on observed sign — standard percentile-bootstrap p-value:
   p_robust = 2 * min(mean(boot_rhos >= 0), mean(boot_rhos <= 0))
   p_robust = min(p_robust, 1.0)
8. return p_robust, boot_rhos
```

Note: precompute `row_indices` (dict[id -> np.ndarray]) once outside the loop — O(N) groupby, not O(N) per iteration. This is the perf-critical path (NFR-1: <10min for 2000 iters).

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A6-1 | Groupby + resample loop | Build conversation_id -> row_indices map once; per-iteration: sample C ids with replacement (rng.choice), gather row indices via concatenation |
| L-A6-2 | Spearman rho + p-value | Per-iteration spearmanr on resampled rows with NaN guard; aggregate into p_robust via two-sided percentile formula above |

---

## Other Task Signatures (reference only, not in budget)

```python
def tercile_continuation_analysis(
    deltas: np.ndarray, continuations: np.ndarray, conversation_ids: np.ndarray
) -> dict:
    # t1, t2 = np.percentile(deltas, [33.33, 66.67])
    # terciles = np.where(deltas <= t1, 1, np.where(deltas <= t2, 2, 3))
    # tercile_rates = {t: continuations[terciles==t].mean() for t in (1,2,3)}
    # rho, p_naive = spearmanr(deltas, continuations)
    # p_robust, boot_rhos = cluster_bootstrap_pvalue(deltas, continuations, conversation_ids)
    ...

def verify_mechanism(tercile_rates: dict) -> dict:
    # mechanism_active = tercile_rates[1] > tercile_rates[3]
    # monotonic = tercile_rates[1] > tercile_rates[2] > tercile_rates[3]
    ...
```
