# Logic Design: H-M1
# Pre-Breakpoint Residual CoV Variance Characterization — API Signatures, Pseudo-code

**Hypothesis:** H-M1 (MECHANISM / INCREMENTAL — extends H-E1)
**Date:** 2026-08-21
**Author:** yoon303@etri.re.kr
**Budget:** 4 subtasks (A-2 × 2, A-4 × 2)

Applied: lightweight-statistical-script-pattern (same as H-E1 flat module layout)

---

## Codebase Analysis (Serena)

**Analyzed Path:** `docs/youra_research/h-e1/code/`
**Method:** Direct file reads (Serena project not activated; code analyzed via Read tool)

**Key findings from H-E1 actual code:**
- `pipeline.py`: `run_pelt_changepoint()` returns dict with keys `paper_count_star` (float|None), `breakpoint_idx` (int|None, 0-based), `residual_cov_sorted` (np.ndarray), `sorted_paper_counts` (np.ndarray)
- `experiment_results.json` from H-E1: contains `paper_count_star` (float) and `breakpoint_idx` (int, 0-based) — both keys exist in actual output
- H-E1 code uses flat `code/` layout with `sys.path` injection in `main.py`; H-M1 mirrors this
- H-E1 `evaluate.py` defines its own `verify_mechanism_activated()` — H-M1 defines a separate one with different indicators

**Reuse decision:** H-M1 reads H-E1 outputs as data files (CSV + JSON). Does NOT import H-E1 modules at runtime. If `paper_count_star_idx` absent from H-E1 JSON, `data_loader.py` recomputes via ruptures directly.

---

## External Dependencies API

### From H-E1 experiment_results.json (verified from actual file)

```json
{
  "paper_count_star": 47.0,
  "breakpoint_idx": 34,
  "n_bkps_detected": 1,
  "permutation_p": 0.023,
  "gate_passed": true
}
```

**Key field:** `breakpoint_idx` (int, 0-based index into sorted residual_cov array) — this is `paper_count_star_idx` for H-M1.

### From H-E1 pwc_cov_computed.csv (verified from derive.py output)

```
Columns: benchmark_name (str), paper_count (int), cov (float), residual_cov (float)
Sorted: by paper_count ascending (guaranteed by H-E1 pipeline)
N: 111 rows
```

### From ruptures (fallback recompute, same params as H-E1)

```python
import ruptures as rpt
# Same parameters H-E1 used (from H-E1 03_config.md: pelt_model="l2", min_size=3, jump=1)
algo = rpt.Pelt(model="l2", min_size=3, jump=1).fit(residual_cov)
bkps = algo.predict(pen=bic_pen)  # bkps[-1] == N (sentinel); bkps[0] - 1 = 0-based idx
```

---

## Subtask L-2-1: `load_residual_cov()` — Load H-E1 CSV Output

**Parent Epic:** A-2 (data_loader.py, complexity=11)
**File:** `h-m1/code/data_loader.py`

### API Signature

```python
def load_residual_cov(
    csv_path: Path,  # path to pwc_cov_computed.csv (H-E1 output)
) -> tuple[np.ndarray, np.ndarray]:
    """
    Load residual_cov series from H-E1 derive.py output CSV.

    Returns:
        paper_counts: np.ndarray shape (N,) dtype int — paper counts per benchmark
        residual_cov: np.ndarray shape (N,) dtype float — OLS-detrended CoV
                      sorted by paper_count ascending

    Raises:
        FileNotFoundError: if csv_path does not exist
        ValueError: if N != 111 after loading
        ValueError: if required columns missing
        ValueError: if series not sorted ascending by paper_count
    """
```

### Pseudo-code

```python
def load_residual_cov(csv_path: Path) -> tuple[np.ndarray, np.ndarray]:
    if not csv_path.exists():
        raise FileNotFoundError(f"H-E1 CSV not found: {csv_path}")

    df = pd.read_csv(csv_path)

    # Validate columns
    required = {"benchmark_name", "paper_count", "cov", "residual_cov"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in H-E1 CSV: {missing}")

    # Validate N
    if len(df) != 111:
        raise ValueError(f"Expected N=111 benchmarks, got N={len(df)}")

    # Sort ascending by paper_count (should already be sorted, but enforce)
    df = df.sort_values("paper_count", ascending=True, kind="stable").reset_index(drop=True)

    paper_counts = df["paper_count"].to_numpy(dtype=int)
    residual_cov = df["residual_cov"].to_numpy(dtype=float)

    # Validate sorted
    if not np.all(paper_counts[:-1] <= paper_counts[1:]):
        raise ValueError("paper_counts not sorted ascending after sort — data integrity issue")

    return paper_counts, residual_cov
```

### Edge Cases
- CSV from non-H-E1 source with different columns → ValueError (missing columns)
- Filtered dataset with N < 111 → ValueError (N check)
- NaN in residual_cov → propagates to analysis; log warning but do not fail (scipy handles NaN gracefully for small counts)

---

## Subtask L-2-2: `load_paper_count_star_idx()` — Load or Recompute Breakpoint Index

**Parent Epic:** A-2 (data_loader.py, complexity=11)
**File:** `h-m1/code/data_loader.py`

### API Signature

```python
def load_paper_count_star_idx(
    results_json_path: Path,    # H-E1 experiment_results.json path
    paper_counts: np.ndarray,   # shape (N,) — from load_residual_cov()
    residual_cov: np.ndarray,   # shape (N,) — from load_residual_cov()
) -> int:
    """
    Load paper_count_star_idx (0-based PELT breakpoint index) from H-E1 JSON.
    Falls back to recomputing via ruptures PELT if key absent.

    Returns:
        paper_count_star_idx: int — 0-based index into sorted residual_cov

    Raises:
        FileNotFoundError: if JSON not found and fallback fails
        ValueError: if idx not in open interval (0, 111) — boundary index invalid
        ValueError: if idx leads to pre_segment len < 3
    """
```

### Pseudo-code

```python
def load_paper_count_star_idx(
    results_json_path: Path,
    paper_counts: np.ndarray,
    residual_cov: np.ndarray,
) -> int:
    # Primary: load from H-E1 JSON
    if results_json_path.exists():
        with open(results_json_path) as f:
            h_e1_results = json.load(f)

        # H-E1 stores 0-based index as "breakpoint_idx"
        idx = h_e1_results.get("breakpoint_idx")
        if idx is not None:
            idx = int(idx)
            print(f"Loaded paper_count_star_idx={idx} from H-E1 JSON")
        else:
            print("WARNING: 'breakpoint_idx' absent from H-E1 JSON — recomputing via PELT")
            idx = None
    else:
        print(f"WARNING: H-E1 JSON not found at {results_json_path} — recomputing via PELT")
        idx = None

    # Fallback: recompute via ruptures (same params as H-E1)
    if idx is None:
        import ruptures as rpt

        sigma = float(np.std(residual_cov, ddof=1))
        bic_pen = sigma ** 2 * np.log(len(residual_cov))

        algo = rpt.Pelt(model="l2", min_size=3, jump=1).fit(residual_cov)
        bkps = algo.predict(pen=bic_pen)
        n_bkps = len(bkps) - 1  # subtract end sentinel

        if n_bkps < 1:
            raise ValueError(
                "PELT fallback found no breakpoints — cannot determine paper_count_star_idx. "
                "Ensure H-E1 ran successfully and its outputs are present."
            )
        idx = bkps[0] - 1  # convert 1-based ruptures to 0-based
        print(f"Fallback PELT recomputed paper_count_star_idx={idx}")

    # Validate idx bounds
    N = len(residual_cov)
    if not (0 < idx < N):
        raise ValueError(
            f"paper_count_star_idx={idx} is at boundary (must be in (0, {N})). "
            "Pre-segment would be empty or full series."
        )
    if idx < 3:
        raise ValueError(
            f"pre_segment length={idx} < 3 (min_pre_segment_n=3). Cannot compute stable variance."
        )

    return idx
```

### Edge Cases
- `breakpoint_idx` key present but value is `null` in JSON → falls back to PELT recompute
- PELT fallback also finds no breakpoint → raises ValueError (cannot proceed)
- idx=0 or idx=111 → ValueError (empty pre or post segment)

---

## Subtask L-4-1: `run_f_test()` — One-Sample F-Test (Primary Gate)

**Parent Epic:** A-4 (analyzer.py, complexity=10)
**File:** `h-m1/code/analyzer.py`

### API Signature

```python
def run_f_test(
    pre: np.ndarray,      # shape (n_pre,) — pre-breakpoint residual_cov values
    global_var: float,    # variance of full N=111 series (ddof=1)
    n_total: int,         # total N (111)
) -> tuple[float, float, float]:
    """
    One-sample F-test: H1 = pre_var > global_var (one-tailed, right tail).

    Test statistic: F = pre_var / global_var ~ F(n_pre-1, n_total-1) under H0.
    p-value: P(F(df1, df2) >= F_stat) = 1 - scipy.stats.f.cdf(F_stat, df1, df2).

    Returns:
        F_stat: float — variance ratio
        p_one_tailed: float — one-tailed p-value (right tail)
        variance_ratio_pre_global: float — same as F_stat (explicit alias for gate check)

    Raises:
        ValueError: if len(pre) < 2 (cannot compute variance with ddof=1)
        ValueError: if global_var <= 0 (degenerate denominator)
    """
```

### Pseudo-code

```python
def run_f_test(pre: np.ndarray, global_var: float, n_total: int) -> tuple[float, float, float]:
    from scipy import stats

    if len(pre) < 2:
        raise ValueError(f"pre-segment too small (n={len(pre)}) — need at least 2 for ddof=1 variance")
    if global_var <= 0:
        raise ValueError(f"global_var={global_var} <= 0 — degenerate input (full series has zero variance)")

    pre_var = float(np.var(pre, ddof=1))

    # F-statistic: ratio of pre-segment variance to global variance
    F_stat = pre_var / global_var

    # Degrees of freedom
    df1 = len(pre) - 1     # pre-segment df
    df2 = n_total - 1      # full series df (reference distribution)

    # One-tailed p-value: P(F(df1, df2) >= F_stat) — right tail (H1: pre > global)
    p_one_tailed = float(1.0 - stats.f.cdf(F_stat, df1, df2))

    # variance_ratio_pre_global is identical to F_stat (pre_var / global_var)
    variance_ratio_pre_global = F_stat

    return F_stat, p_one_tailed, variance_ratio_pre_global
```

### Statistical Rationale
Under H0 (pre_var == global_var), the ratio pre_var/global_var ~ F(n_pre-1, N-1). A ratio >> 1 (right tail) supports H1: early-phase regime is high-variance. Gate: p < 0.10 (one-tailed, as specified in Phase 2B protocol).

### Edge Cases
- F_stat < 1.0: pre_var < global_var → p_one_tailed > 0.5 → gate FAIL
- Very small pre (n_pre=3): df1=2 → F distribution has heavy tails; p may be inflated
- global_var very small (near-zero): F_stat inflated → warn user; check H-E1 preprocessing

---

## Subtask L-4-2: `analyze()` Orchestration

**Parent Epic:** A-4 (analyzer.py, complexity=10)
**File:** `h-m1/code/analyzer.py`

### API Signature

```python
def analyze(
    residual_cov: np.ndarray,       # shape (N,) — full series, sorted by paper_count
    paper_count_star_idx: int,      # 0-based breakpoint index from data_loader
) -> AnalysisResults:
    """
    Full analysis pipeline orchestrator.
    Calls: compute_global_variance, split_segments, run_f_test, run_brown_forsythe.
    Assembles complete AnalysisResults TypedDict.

    Returns: AnalysisResults with all fields populated (see TypedDict in architecture doc)
    """
```

### Pseudo-code

```python
def analyze(residual_cov: np.ndarray, paper_count_star_idx: int) -> AnalysisResults:
    N = len(residual_cov)

    # Step 1: Global statistics (full N=111 series)
    global_var, global_mean = compute_global_variance(residual_cov)
    print(f"Global variance (N={N}): {global_var:.6f}")

    # Step 2: Segment split
    pre, post = split_segments(residual_cov, paper_count_star_idx)
    n_pre, n_post = len(pre), len(post)
    assert n_pre + n_post == N, f"Segment split mismatch: {n_pre}+{n_post} != {N}"
    print(f"Pre-segment N={n_pre}, Post-segment N={n_post}")

    # Step 3: Pre/post statistics
    pre_var = float(np.var(pre, ddof=1))
    pre_mean = float(np.mean(pre))
    post_var = float(np.var(post, ddof=1))
    post_mean = float(np.mean(post))
    print(f"Pre-segment: variance={pre_var:.6f}, mean={pre_mean:.6f}, global_var={global_var:.6f}")

    # Step 4: One-sample F-test (primary gate)
    F_stat, p_one_tailed, variance_ratio_pre_global = run_f_test(pre, global_var, N)
    print(f"F-test: F={F_stat:.4f}, p_one_tailed={p_one_tailed:.4f}, ratio={variance_ratio_pre_global:.4f}")

    # Step 5: Directional confirmation
    pre_mean_positive = pre_mean > 0
    print(f"Pre-segment mean: {pre_mean:.6f} ({'POSITIVE' if pre_mean_positive else 'NEGATIVE'})")

    # Step 6: Brown-Forsythe preview (H-M2 preparation)
    bf_stat, bf_p = run_brown_forsythe(pre, post)
    print(f"Brown-Forsythe pre vs post: stat={bf_stat:.4f}, p={bf_p:.4f}")

    # Step 7: Gate check
    gate_passed = (p_one_tailed < 0.10) and (variance_ratio_pre_global > 1.0)
    print(f"GATE: {'PASS' if gate_passed else 'FAIL'} (p={p_one_tailed:.4f}, ratio={variance_ratio_pre_global:.4f})")

    return AnalysisResults(
        n_pre=n_pre, n_post=n_post,
        global_variance=global_var, global_mean=global_mean,
        pre_variance=pre_var, pre_mean=pre_mean,
        post_variance=post_var, post_mean=post_mean,
        F_stat=F_stat, p_one_tailed=p_one_tailed,
        variance_ratio_pre_global=variance_ratio_pre_global,
        pre_mean_positive=pre_mean_positive,
        bf_stat=bf_stat, bf_p=bf_p,
        gate_passed=gate_passed,
    )
```

### Helper: `compute_global_variance()`

```python
def compute_global_variance(residual_cov: np.ndarray) -> tuple[float, float]:
    """Return (global_variance, global_mean) for full series."""
    return float(np.var(residual_cov, ddof=1)), float(np.mean(residual_cov))
```

### Helper: `split_segments()`

```python
def split_segments(residual_cov: np.ndarray, idx: int) -> tuple[np.ndarray, np.ndarray]:
    """Split at idx; raise if pre too small."""
    pre = residual_cov[:idx]
    post = residual_cov[idx:]
    if len(pre) < 3:
        raise ValueError(f"pre_segment length={len(pre)} < 3 (min_pre_segment_n=3)")
    return pre, post
```

### Helper: `run_brown_forsythe()`

```python
def run_brown_forsythe(pre: np.ndarray, post: np.ndarray) -> tuple[float, float]:
    """scipy.stats.levene with center='median' = Brown-Forsythe test."""
    from scipy import stats
    bf_stat, bf_p = stats.levene(pre, post, center="median")
    return float(bf_stat), float(bf_p)
```

---

## Array Shape Summary

| Variable | Shape | dtype | Notes |
|----------|-------|-------|-------|
| paper_counts (input) | (111,) | int | sorted ascending, from H-E1 CSV |
| residual_cov (input) | (111,) | float | OLS-detrended CoV, from H-E1 CSV |
| pre | (n_pre,) | float | n_pre = paper_count_star_idx |
| post | (n_post,) | float | n_post = 111 - paper_count_star_idx |
| global_var | scalar | float | np.var(residual_cov, ddof=1) |
| F_stat | scalar | float | pre_var / global_var |
| p_one_tailed | scalar | float | 1 - F.cdf(F_stat, df1, df2) |
