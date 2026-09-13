# Logic: h-m1

**Applied**: statistical-correlation-pipeline-pattern (Archon KB: "DL API design patterns" — small-n Pearson/Spearman + bootstrap CI, seeded resampling).

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1)
**Status**: API signatures verified from actual h-e1 code (Serena unavailable; used direct Read as equivalent).
**Analyzed Path**: `h-e1/code/train.py`, `h-e1/code/config.py`
**Relevant Symbols**:
- `run_pipeline() -> dict` in `train.py` — returns `{"dnsi": {name: float|None}, "raw_entropy": {...}, "summary": {...}, ...}`
- `TARGET_BENCHMARKS` in `config.py` = `{"ImageNet": 1000, "CIFAR-10": 10, "CIFAR-100": 100, "MNIST": 10, "GLUE": None, "SQuAD": None, "WMT En-De": None, "COCO Detection": 80}`

**Critical deviation confirmed**: `TARGET_BENCHMARKS` has NO `"ObjectNet"` or `"HANS"`/`"MNLI"` key. h-m1's `GAP_DATA` benchmarks (ImageNet, CIFAR-10, ObjectNet, HANS) only overlap h-e1's DNSI output on `ImageNet` and `CIFAR-10`. `build_dataset` MUST filter to the intersection — n will likely be 2, not 4. This is a real data constraint, not a bug; `evaluate.py` and PRD framing (n=4 pilot) must tolerate n<4.

---

## External Dependencies (Base Hypothesis)

```python
# From: h-e1/code/train.py (ACTUAL CODE)
def run_pipeline() -> dict:
    """Returns dict with keys: dnsi, raw_entropy, improvement_rate,
    time_since_last_sota, benchmark_info, summary.
    results["dnsi"]: dict[str, float | None] keyed by TARGET_BENCHMARKS names."""
    ...

# From: h-e1/code/config.py (ACTUAL CODE)
TARGET_BENCHMARKS: dict[str, int | None]  # benchmark_name -> num_classes (or None)
```

**Verified from**: `h-e1/code/train.py`, `h-e1/code/config.py` (not `03_architecture.md`/PRD spec — no `dnsi_results.json` file exists; PRD's `dnsi_file` path is stale).

---

## M-2: h-e1 Integration [Complexity: 10, Budget: 2 subtasks]

**Applied**: in-process sys.path bridge + dict key-intersection filtering.

### API Signatures

```python
def load_dnsi_from_h_e1() -> dict[str, float | None]:
    """sys.path-inserts h-e1/code, calls run_pipeline(), returns results['dnsi'].
    Returns {} on ImportError (h-e1 code missing/broken)."""
    ...
```

### Pseudo-code

```
load_dnsi_from_h_e1():
    h_e1_code = os.path.join(os.path.dirname(__file__), "..", "..", "h-e1", "code")
    sys.path.insert(0, os.path.abspath(h_e1_code))
    try:
        from train import run_pipeline          # h-e1's run_pipeline, not h-m1's
        results = run_pipeline()
        return results.get("dnsi", {})
    except Exception as e:
        print(f"[ERROR] h-e1 integration failed: {e}")
        return {}
    finally:
        sys.path.pop(0)   # avoid polluting sys.path for h-m1's own train.py import
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M2-1 | sys.path bridge + call | Insert h-e1/code into sys.path, import and call `run_pipeline()`, pop path after (avoid module name collision with h-m1's own train.py) |
| L-M2-2 | Error handling + key extraction | Wrap in try/except, return `{}` on failure, extract `results["dnsi"]` dict, log which of GAP_DATA keys are missing from h-e1 output |

---

## M-3: Dataset Builder [Complexity: 6, Budget: 1 subtask]

**Applied**: dict intersection + None-filtering (standard).

### API Signatures

```python
def build_dataset(
    dnsi: dict[str, float | None], gap: dict[str, float]
) -> tuple[list[str], "np.ndarray", "np.ndarray"]:
    """Intersect keys present in both dicts with non-None dnsi value.
    Returns (names, dnsi_arr[N], gap_arr[N]). N may be < len(gap) if h-e1
    lacks a benchmark (e.g. ObjectNet, HANS not in TARGET_BENCHMARKS)."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| names | list[str], len N | benchmarks with valid DNSI present in both dicts |
| dnsi_arr | np.ndarray [N] | float64 |
| gap_arr | np.ndarray [N] | float64, same order as names |

### Pseudo-code

```
build_dataset(dnsi, gap):
    names = sorted(k for k in gap if k in dnsi and dnsi[k] is not None)
    dnsi_arr = np.array([dnsi[k] for k in names])
    gap_arr = np.array([gap[k] for k in names])
    if len(names) < 2:
        raise ValueError(f"Insufficient data: only {len(names)} valid pairs (need >=2)")
    return names, dnsi_arr, gap_arr
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M3-1 | Intersection + validation | Filter to keys present+non-None in both dicts, build sorted arrays, raise on N<2 |

---

## M-4: CorrelationAnalyzer [Complexity: 9, Budget: 0 subtasks — spec only, no extra budget]

**Applied**: scipy.stats.pearsonr/spearmanr + percentile bootstrap CI (seeded np.random.default_rng).

### API Signatures

```python
class CorrelationAnalyzer:
    def __init__(self, n_bootstrap: int = 10000, seed: int = 42):
        """Store bootstrap count and RNG seed."""
        ...

    def analyze(self, dnsi: "np.ndarray", gap: "np.ndarray") -> dict:
        """dnsi, gap: [N]. Returns dict with keys:
        n, r_pearson, p_pearson, r_spearman, p_spearman,
        ci_95_lower, ci_95_upper, bootstrap_r ([n_bootstrap]),
        hypothesis_supported: bool"""
        ...

    def _bootstrap_correlation(self, x: "np.ndarray", y: "np.ndarray") -> "np.ndarray":
        """Returns [n_bootstrap] array of Pearson r from resampled pairs (with replacement)."""
        ...
```

### Pseudo-code

```
analyze(dnsi, gap):
    n = len(dnsi)
    r_p, p_p = scipy.stats.pearsonr(dnsi, gap)
    r_s, p_s = scipy.stats.spearmanr(dnsi, gap)
    boot_r = self._bootstrap_correlation(dnsi, gap)
    ci_lo, ci_hi = np.percentile(boot_r, [2.5, 97.5])
    supported = (r_p < -0.4 or r_s < -0.4)
    return {n, r_pearson: r_p, p_pearson: p_p, r_spearman: r_s, p_spearman: p_s,
            ci_95_lower: ci_lo, ci_95_upper: ci_hi, bootstrap_r: boot_r,
            hypothesis_supported: supported}

_bootstrap_correlation(x, y):
    rng = np.random.default_rng(self.seed)
    n = len(x)
    results = np.empty(self.n_bootstrap)
    for i in range(self.n_bootstrap):
        idx = rng.integers(0, n, size=n)          # sample with replacement
        xi, yi = x[idx], y[idx]
        if np.std(xi) == 0 or np.std(yi) == 0:
            results[i] = np.nan                    # degenerate resample (n small, e.g. n=2)
        else:
            results[i], _ = scipy.stats.pearsonr(xi, yi)
    return results[~np.isnan(results)]              # drop degenerate resamples
```

**Note (n=2 edge case)**: With only ImageNet+CIFAR-10 overlapping (see Codebase Analysis), N may be 2. Pearson r with n=2 is always ±1 or undefined; bootstrap resamples of size 2 frequently degenerate (duplicate index → zero variance → NaN, dropped above). `evaluate.check_gate` and `summarize` (already fully specified in `03_architecture.md`) must report `n` prominently and flag low-n unreliability — no additional logic budget needed for that, plain conditional per architecture spec.

### Subtasks [0/0 used — full budget spent on M-2/M-3]

No subtasks allocated to M-4 logic design; `analyze`/`_bootstrap_correlation` signatures above are copy-paste ready for Phase 4 Coder directly.
