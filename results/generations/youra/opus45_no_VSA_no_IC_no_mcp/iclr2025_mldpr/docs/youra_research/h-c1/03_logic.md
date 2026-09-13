# Logic: h-c1

**Applied**: statistical-correlation-pipeline-pattern (Archon KB: "DL API design patterns correlation analysis" — small-n Pearson/Spearman + bootstrap CI + Fisher z cross-group test).

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-m1)
**Status**: Serena MCP unavailable; used direct Read on `h-m1/code/metrics.py` (equivalent to `find_symbol`/`get_symbols_overview`).
**Analyzed Path**: `h-m1/code/metrics.py`, `h-m1/03_logic.md`
**Relevant Symbols**: `CorrelationAnalyzer.__init__(n_bootstrap=10000, seed=42)`, `.analyze(dnsi, gap) -> dict`, `._bootstrap_correlation(x, y) -> np.ndarray`.

**Deviation from h-m1**: `analyze()`'s `hypothesis_supported` uses `r < -0.4` in h-m1 (aggregate hypothesis). h-c1 PRD requires `|R| > 0.3`. The copied `CorrelationAnalyzer` in h-c1 must use `hypothesis_supported = (r_pearson < -0.3 or r_spearman < -0.3)` — do not import h-m1's threshold.

---

## External Dependencies (Base Hypothesis)

```python
# From: h-m1/code/metrics.py (ACTUAL CODE — copied into h-c1/code/metrics.py, threshold changed)
class CorrelationAnalyzer:
    def __init__(self, n_bootstrap: int = 10000, seed: int = 42): ...
    def analyze(self, dnsi: "np.ndarray", gap: "np.ndarray") -> dict:
        """dnsi, gap: [N]. Returns: n, r_pearson, p_pearson, r_spearman, p_spearman,
        ci_95_lower, ci_95_upper, bootstrap_r ([n_bootstrap_valid]), hypothesis_supported: bool"""
        ...
    def _bootstrap_correlation(self, x: "np.ndarray", y: "np.ndarray") -> "np.ndarray":
        """[n_bootstrap] Pearson r from resamples w/ replacement; NaN (degenerate) dropped."""
        ...
```

**Verified from**: `h-m1/code/metrics.py`. Copied verbatim except `hypothesis_supported` threshold: `abs(r) > 0.3` (h-c1) vs `r < -0.4` (h-m1).

---

## C-1: Config Setup [Complexity: 4, Budget: 4 subtasks]

**Applied**: static dict constants (standard).

### API Signatures

```python
# config.py — no functions, module-level constants only
CONFIG: dict          # n_bootstrap, seed, success_r_abs_threshold, ci_level, dirs
DNSI_DATA: dict[str, float]   # 6 benchmarks
GAP_DATA: dict[str, float]    # 6 benchmarks, same keys as DNSI_DATA
DOMAIN_MAP: dict[str, str]    # benchmark -> "vision" | "nlp"
```

Values as given in `03_architecture.md` (copy directly — already copy-paste ready).

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-C1-1 | CONFIG dict | n_bootstrap=10000, seed=42, success_r_abs_threshold=0.3, ci_level=0.95, dirs |
| L-C1-2 | DNSI_DATA | 4 copied from h-m1 SYNTHETIC_DNSI + PAWS=0.60, ANLI=0.35 |
| L-C1-3 | GAP_DATA | 6 published gap values, same keys as DNSI_DATA |
| L-C1-4 | DOMAIN_MAP | 3 vision + 3 nlp benchmark -> domain string |

---

## C-2: Domain Dataset Builder [Complexity: 5, Budget: 4 subtasks]

**Applied**: dict filter + sort (standard, same style as h-m1's `build_dataset`).

### API Signatures

```python
def build_domain_dataset(domain: str) -> tuple[list[str], "np.ndarray", "np.ndarray"]:
    """Filter DNSI_DATA/GAP_DATA to DOMAIN_MAP[k] == domain, sort by name.
    Returns (names, dnsi_arr[N], gap_arr[N]). Raises ValueError if N < 3."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| names | list[str], len N | benchmarks in given domain |
| dnsi_arr | np.ndarray [N] | float64 |
| gap_arr | np.ndarray [N] | float64, same order as names |

### Pseudo-code

```
build_domain_dataset(domain):
    names = sorted(k for k in DNSI_DATA if DOMAIN_MAP[k] == domain)
    dnsi_arr = np.array([DNSI_DATA[k] for k in names])
    gap_arr = np.array([GAP_DATA[k] for k in names])
    if len(names) < 3:
        raise ValueError(f"Domain '{domain}': only {len(names)} benchmarks, need >=3")
    return names, dnsi_arr, gap_arr
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-C2-1 | Filter by domain | Select DNSI_DATA/GAP_DATA keys where DOMAIN_MAP matches |
| L-C2-2 | Sort + build arrays | Sorted names list, np.array dnsi/gap in matching order |
| L-C2-3 | Validate n>=3 | Raise ValueError with domain name + count if insufficient |
| L-C2-4 | Unit smoke check | `build_domain_dataset("vision")` and `("nlp")` both return N=3 |

---

## C-3: CorrelationAnalyzer Port [Complexity: 6, Budget: 6 subtasks]

**Applied**: copy of h-m1's `CorrelationAnalyzer`, threshold change only (see External Dependencies above).

### API Signatures

```python
class CorrelationAnalyzer:
    def __init__(self, n_bootstrap: int = 10000, seed: int = 42): ...
    def analyze(self, dnsi: "np.ndarray", gap: "np.ndarray") -> dict: ...
    def _bootstrap_correlation(self, x: "np.ndarray", y: "np.ndarray") -> "np.ndarray": ...
```

### Pseudo-code

```
analyze(dnsi, gap):
    n = len(dnsi)
    r_p, p_p = scipy.stats.pearsonr(dnsi, gap)
    r_s, p_s = scipy.stats.spearmanr(dnsi, gap)
    boot_r = self._bootstrap_correlation(dnsi, gap)
    ci_lo, ci_hi = np.percentile(boot_r, [2.5, 97.5])
    supported = (r_p < -0.3 or r_s < -0.3)          # h-c1 threshold, NOT h-m1's -0.4
    return {n, r_pearson: r_p, p_pearson: p_p, r_spearman: r_s, p_spearman: p_s,
            ci_95_lower: ci_lo, ci_95_upper: ci_hi, bootstrap_r: boot_r,
            hypothesis_supported: supported}

_bootstrap_correlation(x, y):     # identical to h-m1, verbatim
    rng = np.random.default_rng(self.seed)
    n = len(x)
    results = np.empty(self.n_bootstrap)
    for i in range(self.n_bootstrap):
        idx = rng.integers(0, n, size=n)
        xi, yi = x[idx], y[idx]
        if np.std(xi) == 0 or np.std(yi) == 0:
            results[i] = np.nan
        else:
            results[i], _ = scipy.stats.pearsonr(xi, yi)
    return results[~np.isnan(results)]
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-C3-1 | Copy class skeleton | `__init__` storing n_bootstrap/seed |
| L-C3-2 | Copy pearsonr/spearmanr calls | From h-m1's analyze() verbatim |
| L-C3-3 | Copy bootstrap loop | `_bootstrap_correlation` verbatim, NaN-drop on degenerate resample |
| L-C3-4 | CI percentile calc | `np.percentile(boot_r, [2.5, 97.5])` |
| L-C3-5 | Threshold change | `hypothesis_supported = abs-based 0.3` (not h-m1's -0.4) |
| L-C3-6 | Smoke test | `analyze()` on vision/nlp arrays returns all 9 dict keys |

---

## C-4: Fisher z-test [Complexity: 6, Budget: 6 subtasks]

**Applied**: standard Fisher z-transformation two-sample test (new — not in h-m1).

### API Signatures

```python
def fisher_z_test(r_a: float, n_a: int, r_b: float, n_b: int) -> dict:
    """Two-tailed test of H0: r_a == r_b. Returns:
    z_difference: float, p_difference: float, consistent_direction: bool (sign(r_a)==sign(r_b))."""
    ...
```

### Pseudo-code

```
fisher_z_test(r_a, n_a, r_b, n_b):
    r_a_c = np.clip(r_a, -0.9999, 0.9999)     # avoid inf at |r|=1 (n=3 edge case)
    r_b_c = np.clip(r_b, -0.9999, 0.9999)
    z_a = np.arctanh(r_a_c)
    z_b = np.arctanh(r_b_c)
    se = np.sqrt(1.0 / (n_a - 3) + 1.0 / (n_b - 3))   # requires n_a,n_b >= 4; n=3 -> se undefined
    z_diff = (z_a - z_b) / se
    p_diff = 2 * (1 - scipy.stats.norm.cdf(abs(z_diff)))
    consistent = (np.sign(r_a) == np.sign(r_b))
    return {"z_difference": z_diff, "p_difference": p_diff, "consistent_direction": consistent}
```

**Note (n=3 edge case)**: `se` formula divides by `n-3`; with `n_a=n_b=3` this is division by zero → `inf`/`nan`. Guard: if `n_a <= 3 or n_b <= 3`, set `se = np.sqrt(1.0/max(n_a-3,1) + 1.0/max(n_b-3,1))` and flag result as low-power (add `"low_n_warning": True` to returned dict when either n<=3) — no extra subtask needed, folded into L-C4-3.

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-C4-1 | arctanh transform | Clip r to (-1,1), compute z_a, z_b |
| L-C4-2 | SE + z_diff | Standard error formula, z_difference calc |
| L-C4-3 | n<=3 guard | Avoid div-by-zero, add low_n_warning flag |
| L-C4-4 | p-value | Two-tailed normal CDF |
| L-C4-5 | Direction check | sign comparison -> consistent_direction bool |
| L-C4-6 | Smoke test | Known r_a=-0.9,n=3,r_b=-0.9,n=3 -> p_diff≈1.0, consistent=True |

---

## C-5: Gate + Evaluate [Complexity: 6, Budget: 6 subtasks]

**Applied**: threshold + boolean gate composition (standard).

### API Signatures

```python
def check_domain_pass(analysis: dict) -> bool:
    """abs(analysis['r_pearson']) > CONFIG['success_r_abs_threshold'] and analysis['r_pearson'] < 0."""
    ...

def check_gate(vision_analysis: dict, nlp_analysis: dict, comparison: dict) -> dict:
    """SHOULD_WORK gate. Returns: success (bool), should_fail (bool, opposite signs),
    vision_r, nlp_r, consistent_direction, vision_pass, nlp_pass."""
    ...

def summarize(results: dict) -> dict:
    """Flatten key metrics for results json / console print."""
    ...
```

### Pseudo-code

```
check_domain_pass(analysis):
    thr = CONFIG["success_r_abs_threshold"]
    return abs(analysis["r_pearson"]) > thr and analysis["r_pearson"] < 0

check_gate(vision_analysis, nlp_analysis, comparison):
    v_pass = check_domain_pass(vision_analysis)
    n_pass = check_domain_pass(nlp_analysis)
    consistent = comparison["consistent_direction"]
    should_fail = not consistent   # opposite-sign correlations
    success = v_pass and n_pass and consistent
    return {"success": success, "should_fail": should_fail,
            "vision_r": vision_analysis["r_pearson"], "nlp_r": nlp_analysis["r_pearson"],
            "consistent_direction": consistent, "vision_pass": v_pass, "nlp_pass": n_pass}
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-C5-1 | check_domain_pass | threshold + sign check |
| L-C5-2 | check_gate composition | v_pass, n_pass, consistent, should_fail |
| L-C5-3 | success formula | AND of all three conditions |
| L-C5-4 | summarize keys | Flatten n, r, p, CI per domain + gate result |
| L-C5-5 | print [DOMAIN] logs | Format per architecture spec (vision/nlp activation lines) |
| L-C5-6 | Smoke test | Synthetic pass+fail cases for check_gate |

---

## C-6: Two-Panel Scatter Figure [Complexity: 7, Budget: 7 subtasks]

**Applied**: matplotlib subplot pattern (standard viz).

### API Signatures

```python
def plot_domain_scatter(vision: dict, nlp: dict, out_path: str) -> None:
    """2-panel (1x2) scatter: DNSI (x) vs gap (y), per-point labels, OLS regression line,
    R/p annotation in each panel title. Saves PNG to out_path."""
    ...
```

### Pseudo-code

```
plot_domain_scatter(vision, nlp, out_path):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    for ax, dom_dict, title in [(ax1, vision, "Vision"), (ax2, nlp, "NLP")]:
        ax.scatter(dom_dict["dnsi"], dom_dict["gap"])
        for name, x, y in zip(dom_dict["names"], dom_dict["dnsi"], dom_dict["gap"]):
            ax.annotate(name, (x, y))
        slope, intercept = np.polyfit(dom_dict["dnsi"], dom_dict["gap"], 1)
        xs = np.linspace(min(dom_dict["dnsi"]), max(dom_dict["dnsi"]), 50)
        ax.plot(xs, slope*xs + intercept, "--")
        ax.set_title(f"{title} (R={dom_dict['r_pearson']:.2f}, p={dom_dict['p_pearson']:.3f})")
        ax.set_xlabel("DNSI"); ax.set_ylabel("Generalization Gap")
    plt.tight_layout(); plt.savefig(out_path); plt.close()
```

### Subtasks [7/7 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-C6-1 | Figure/subplot setup | 1x2 subplots, figsize |
| L-C6-2 | Scatter points | plot dnsi vs gap per domain |
| L-C6-3 | Point labels | annotate benchmark names |
| L-C6-4 | Regression line | np.polyfit + plot dashed line |
| L-C6-5 | Title annotation | R, p in subplot title |
| L-C6-6 | Axis labels | DNSI / Generalization Gap |
| L-C6-7 | Save + smoke test | savefig, assert file exists after call |

---

## C-7: Comparison + Bootstrap Figures [Complexity: 6, Budget: 6 subtasks]

**Applied**: matplotlib bar chart w/ error bars + overlaid histograms (standard viz).

### API Signatures

```python
def plot_domain_comparison(vision: dict, nlp: dict, out_path: str) -> None:
    """Bar chart: vision vs nlp r_pearson, 95% CI error bars. Saves PNG."""
    ...

def plot_bootstrap_overlay(vision: dict, nlp: dict, out_path: str) -> None:
    """Overlaid histograms of bootstrap_r distributions (vision vs nlp), alpha-blended."""
    ...
```

### Pseudo-code

```
plot_domain_comparison(vision, nlp, out_path):
    labels = ["Vision", "NLP"]
    rs = [vision["r_pearson"], nlp["r_pearson"]]
    errs = [[r - lo, hi - r] for r, lo, hi in
            [(vision["r_pearson"], vision["ci_95_lower"], vision["ci_95_upper"]),
             (nlp["r_pearson"], nlp["ci_95_lower"], nlp["ci_95_upper"])]]
    plt.bar(labels, rs, yerr=np.array(errs).T)
    plt.ylabel("Pearson r"); plt.axhline(0, color="gray", ls=":")
    plt.savefig(out_path); plt.close()

plot_bootstrap_overlay(vision, nlp, out_path):
    plt.hist(vision["bootstrap_r"], bins=50, alpha=0.5, label="Vision")
    plt.hist(nlp["bootstrap_r"], bins=50, alpha=0.5, label="NLP")
    plt.xlabel("Bootstrap r"); plt.legend()
    plt.savefig(out_path); plt.close()
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-C7-1 | Bar chart setup | 2-bar labels, r values |
| L-C7-2 | CI error bars | asymmetric yerr from ci_95_lower/upper |
| L-C7-3 | Bar chart save | axhline(0), savefig |
| L-C7-4 | Bootstrap hist overlay | 2 alpha-blended histograms |
| L-C7-5 | Legend + labels | xlabel, legend |
| L-C7-6 | Smoke test | both PNGs exist after call |

---

## C-8: Pipeline Orchestration [Complexity: 7, Budget: 7 subtasks]

**Applied**: sequential orchestration (standard, mirrors h-m1's `run_pipeline`).

### API Signatures

```python
def generate_figures(vision: dict, nlp: dict, comparison: dict, out_dir: str) -> None:
    """Calls plot_domain_scatter, plot_domain_comparison, plot_bootstrap_overlay."""
    ...

def run_pipeline() -> dict:
    """Orchestrates full h-c1 pipeline. Returns dict with keys:
    vision, nlp, comparison, gate, summary. Saves results/results.json."""
    ...

if __name__ == "__main__":
    results = run_pipeline()
```

### Pseudo-code

```
run_pipeline():
    v_names, v_dnsi, v_gap = build_domain_dataset("vision")
    n_names, n_dnsi, n_gap = build_domain_dataset("nlp")
    analyzer = CorrelationAnalyzer(CONFIG["n_bootstrap"], CONFIG["seed"])
    vision = analyzer.analyze(v_dnsi, v_gap) | {"names": v_names, "dnsi": v_dnsi, "gap": v_gap}
    nlp = analyzer.analyze(n_dnsi, n_gap) | {"names": n_names, "dnsi": n_dnsi, "gap": n_gap}
    print(f"[VISION] n={vision['n']} r={vision['r_pearson']:.3f} pass={check_domain_pass(vision)}")
    print(f"[NLP] n={nlp['n']} r={nlp['r_pearson']:.3f} pass={check_domain_pass(nlp)}")
    comparison = fisher_z_test(vision["r_pearson"], vision["n"], nlp["r_pearson"], nlp["n"])
    gate = check_gate(vision, nlp, comparison)
    generate_figures(vision, nlp, comparison, CONFIG["figures_dir"])
    results = {"vision": vision, "nlp": nlp, "comparison": comparison, "gate": gate}
    results["summary"] = summarize(results)
    os.makedirs(CONFIG["results_dir"], exist_ok=True)
    with open(f"{CONFIG['results_dir']}/results.json", "w") as f:
        json.dump(results, f, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o), indent=2)
    print(f"[GATE] success={gate['success']}")
    return results
```

### Subtasks [7/7 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-C8-1 | Build both domain datasets | vision + nlp via build_domain_dataset |
| L-C8-2 | Run analyzer x2 | CorrelationAnalyzer.analyze per domain |
| L-C8-3 | Print [DOMAIN] logs | per-domain n/r/pass |
| L-C8-4 | Fisher z + gate | fisher_z_test, check_gate |
| L-C8-5 | generate_figures wiring | call all 3 plot functions |
| L-C8-6 | JSON serialization | np.ndarray -> list via default= handler |
| L-C8-7 | Smoke test | `run_pipeline()` returns dict w/ all 5 keys, results.json written |

---

## Self-Validation

- No ASCII diagrams. No KB search logs beyond "Applied:" line.
- Docstrings ≤ 2 lines throughout.
- Tensor shapes only where non-obvious (C-2 dataset arrays).
- All subtask counts match architecture budget exactly (4/5/6/6/6/7/6/7 = 47 total).
- Codebase Analysis (Serena) section present.
- External Dependencies API section present, verified from h-m1/code/metrics.py actual code.
