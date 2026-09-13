# Logic: h-e1 (EXISTENCE PoC)

**Applied**: Windowed-aggregation + entropy-normalization pattern (standard scipy.stats.entropy usage for saturation metrics).

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze (no base hypothesis, no existing repo)
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-3: DNSIComputer [Complexity: 10, Budget: 2 subtasks]

**Applied**: Shannon-entropy normalization by log(difficulty_proxy) (KB pattern: benchmark-saturation windowed-aggregation).

### API Signatures

```python
class DNSIComputer:
    def __init__(self, window_months: int = 6):
        """Store window size in months."""
        ...

    def compute_dnsi(
        self,
        sota_history: list[tuple[str, float]],  # [(date_iso, accuracy), ...] sorted
        difficulty_proxy: int | None,
    ) -> float | None:
        """Returns DNSI in [0, 2], or None if uncomputable (edge case)."""
        ...

    def _compute_windowed_improvements(
        self, sota_history: list[tuple[str, float]]
    ) -> "np.ndarray":  # [W] one delta-accuracy value per non-empty window
        ...
```

### Tensor / Data Shapes

| Variable | Shape/Type | Note |
|----------|-----------|------|
| sota_history | list[(str, float)], len N | sorted by date ascending |
| windowed_improvements | np.ndarray [W] | W <= N-1, one per window with >=1 entry |
| dnsi | float or None | None if N<2, difficulty_proxy<=1, or all improvements zero |

### Pseudo-code

```
compute_dnsi(sota_history, difficulty_proxy):
    if len(sota_history) < 2 or difficulty_proxy is None or difficulty_proxy <= 1:
        return None                                    # edge case: insufficient data / single-class

    deltas = _compute_windowed_improvements(sota_history)
    if deltas.size == 0 or deltas.sum() == 0:
        return None                                    # edge case: no improvements

    probs = deltas / deltas.sum()                      # normalize to distribution
    H = scipy.stats.entropy(probs)                      # raw Shannon entropy (nats)
    H_max = log(difficulty_proxy)
    if H_max == 0:
        return None
    dnsi = H / H_max
    return float(clip(dnsi, 0.0, 2.0))

_compute_windowed_improvements(sota_history):
    bin dates into WINDOW_MONTHS-wide buckets from first to last date
    for each bucket: delta = max(accuracy in bucket) - max(accuracy in previous bucket-with-data)
    return array of positive deltas only (skip non-improving buckets)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A3-1 | Windowed improvement aggregation | Bucket sota_history into 6-month windows, compute per-window max-accuracy deltas, handle N<2 / empty-window edge cases |
| L-A3-2 | Entropy normalization | Convert deltas to probability distribution, compute scipy.stats.entropy, normalize by log(difficulty_proxy), clip to DNSI_VALID_RANGE, return None on degenerate cases |

---

## Notes on Remaining Tasks (No Additional Logic Budget)

A-1, A-2, A-4, A-5, A-6, A-7 use signatures already fully specified in `03_architecture.md` (plain I/O, no non-trivial algorithms — direct JSON parsing, dict filtering, `scipy.stats.entropy` one-liners, `matplotlib` calls). Phase 4 Coder implements directly from architecture signatures; no further logic design needed within budget.
