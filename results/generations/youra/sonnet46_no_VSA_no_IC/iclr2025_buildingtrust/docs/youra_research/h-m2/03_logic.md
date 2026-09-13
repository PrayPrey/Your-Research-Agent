# Logic Design: H-M2
# Differential Rank Stability — Fairness vs. Adversarial Robustness

**Hypothesis:** H-M2 (MECHANISM / FULL tier)
**Date:** 2026-08-20
**Author:** Anonymous
**Budget:** 4 subtasks

Applied: Single-responsibility function decomposition
Applied: Early-exit validation pattern (assert-based mechanism verification)
Applied: Layered data assembly (load base → join → validate → serialize)
Applied: Inline implementation of psinger/CorrelationStats Fisher z formula (no package dependency)

---

## Codebase Analysis (Serena)

**H-M1 Code Structure (`h-m1/code/`):**
```
config.py         — GATE_RHO, GATE_P, N_COMMON_MIN, RANDOM_SEED, ALTERNATIVE, WINOGRANDE_SCORES, DATA_DIR, FIGURES_DIR, RESULTS_DIR
data.py           — build_score_dataframe(), canonicalize_name(), verify_n_common()
analysis.py       — compute_raw_spearman(), compute_partial_spearman(df, covar="mmlu"), run_full_analysis(), evaluate_gate()
visualize.py      — plot_gate_metrics(), plot_rank_scatter(), plot_sensitivity_comparison(), plot_score_distributions(), plot_mmlu_vs_fairness(), generate_all_figures()
run_experiment.py — main() with --dry-run/--skip-figures, _self_check()
```

**Verified H-M1 API signatures (from actual code):**
- `build_score_dataframe() -> pd.DataFrame` — returns (N_common, 5) with [model_name, bbq_disambig, bbq_ambig, mmlu, winogrande]; saves `data/h_m1_scores.csv`
- `compute_raw_spearman(df) -> dict` — keys: rho, p, n
- `compute_partial_spearman(df, covar="mmlu") -> dict` — keys: partial_rho, p_value, ci95, n
- `evaluate_gate(partial_rho, p_value) -> bool`
- `run_full_analysis(df) -> dict` — keys: raw, primary, sensitivity, gate_pass, mmlu_explains_variance
- Paths: `_HERE = Path(__file__).parent.parent`, `DATA_DIR = _HERE / "data"`, etc.
- `ALTERNATIVE = "greater"` (one-tailed for H-M1); H-M2 uses `"two-sided"` for all partial ρ

**H-M2 reuse strategy:**
- Read h-m1 CSV output (`H_M1_DATA_DIR / "h_m1_scores.csv"`) — do NOT import h-m1 code directly
- Extend DataFrame with robustness columns from ROBUSTNESS_SCORES dict in config.py
- Reuse pingouin.partial_corr pattern; change alternative to "two-sided" for all 3 pairs
- Implement fisher_z_test_difference() inline (psinger formula, ~8 lines)

---

## External Dependencies API

### pingouin.partial_corr (H-M2 usage)
```python
pingouin.partial_corr(
    data: pd.DataFrame,         # rows=models, cols include x, y, covar
    x: str,                     # predictor column name
    y: str,                     # outcome column name
    covar: list[str],           # control variable column names
    method: str = "spearman",   # rank-based
    alternative: str = "two-sided"  # exploratory comparison (changed from h-m1)
) -> pd.DataFrame
# Returns 1-row DataFrame with columns: n, r, CI95%, p-val
```

### scipy.stats.spearmanr (raw baseline)
```python
scipy.stats.spearmanr(
    a: array-like,   # first variable (e.g., bbq_disambig)
    b: array-like    # second variable (e.g., bbq_ambig)
) -> SpearmanrResult(statistic: float, pvalue: float)
```

### scipy.stats.norm (Fisher z-test)
```python
scipy.stats.norm.cdf(z: float) -> float
# Used for: p_val = 2 * (1 - norm.cdf(abs(z_stat)))
```

---

## Module: data.py

### Subtask L-2-1: load_hm1_base()

```python
def load_hm1_base() -> pd.DataFrame:
    """
    Load h-m1 validated DataFrame from H_M1_DATA_DIR/h_m1_scores.csv.

    Returns:
        pd.DataFrame with columns:
            model_name   : str   — canonical model identifier
            bbq_disambig : float — BBQ disambiguated context accuracy
            bbq_ambig    : float — BBQ ambiguous context accuracy
            mmlu         : float — MMLU accuracy (capability control)
            winogrande   : float — Winogrande accuracy (may be NaN for some models)
        Shape: (N_common, 5)

    Raises:
        FileNotFoundError: if h_m1_scores.csv does not exist
        AssertionError: if required columns missing
    """
    csv_path = H_M1_DATA_DIR / "h_m1_scores.csv"
    if not csv_path.exists():
        raise FileNotFoundError(
            f"h-m1 scores CSV not found at {csv_path}. "
            "Run h-m1 experiment first to generate it."
        )
    df = pd.read_csv(csv_path)
    required = ["model_name", "bbq_disambig", "bbq_ambig", "mmlu"]
    missing = [c for c in required if c not in df.columns]
    assert not missing, f"h_m1_scores.csv missing columns: {missing}"
    logging.info(f"Loaded h-m1 base: N={len(df)}, models={df['model_name'].tolist()}")
    return df


def build_robustness_scores() -> pd.DataFrame:
    """
    Build per-model robustness DataFrame from ROBUSTNESS_SCORES constant in config.

    Returns:
        pd.DataFrame with columns:
            model_name    : str
            glue_score    : float
            advglue_score : float
            anli_r1_score : float
            anli_r3_score : float
        Shape: (N_robustness, 5)
    """
    records = [
        {"model_name": model, **scores}
        for model, scores in ROBUSTNESS_SCORES.items()
        if all(scores.get(k) is not None for k in
               ["glue_score", "advglue_score", "anli_r1_score", "anli_r3_score"])
    ]
    return pd.DataFrame(records)


def build_master_dataframe() -> pd.DataFrame:
    """
    Inner join h-m1 base DataFrame with robustness scores on model_name.

    Returns:
        pd.DataFrame with columns:
            [model_name, bbq_disambig, bbq_ambig, mmlu, winogrande,
             glue_score, advglue_score, anli_r1_score, anli_r3_score]
        Shape: (N_common_robust, 9)

    Side effects:
        Logs N_common_robust; logs any models dropped vs h-m1
        Saves DataFrame to DATA_DIR / "trustllm_scores_hm2.csv"

    Raises:
        AssertionError: if N_common_robust < N_COMMON_MIN (8)
    """
    df_base = load_hm1_base()
    df_rob  = build_robustness_scores()

    df = df_base.merge(df_rob, on="model_name", how="inner")
    n_robust = len(df)

    dropped = set(df_base["model_name"]) - set(df["model_name"])
    if dropped:
        logging.warning(f"Models dropped (no robustness scores): {dropped}")

    assert n_robust >= N_COMMON_MIN, (
        f"N_common_robust={n_robust} < {N_COMMON_MIN} — "
        "insufficient data for partial correlation"
    )
    logging.info(f"N_common_robust={n_robust}, models={df['model_name'].tolist()}")

    df.to_csv(DATA_DIR / "trustllm_scores_hm2.csv", index=False)
    return df


def verify_preconditions(df: pd.DataFrame) -> int:
    """
    Assert all mechanism pre-conditions before analysis.

    Args:
        df: master DataFrame from build_master_dataframe()

    Returns:
        int — N_common_robust (for downstream use)

    Raises:
        AssertionError: if N < N_COMMON_MIN, required columns missing, or insufficient variance
    """
    required = ["bbq_disambig", "bbq_ambig", "glue_score",
                "advglue_score", "anli_r1_score", "anli_r3_score", "mmlu"]
    missing = [c for c in required if c not in df.columns]
    assert not missing, f"Missing columns: {missing}"
    assert len(df) >= N_COMMON_MIN, f"N={len(df)} < {N_COMMON_MIN}"
    for col in required[:-1]:  # skip mmlu variance check
        assert df[col].nunique() > 3, f"Insufficient variance in {col}"
    logging.info(f"✅ H-M2 verification: N={len(df)}, all columns present, variance OK")
    return len(df)
```

---

## Module: analysis.py

### Subtask L-4-1: compute_partial_rho()

```python
def compute_partial_rho(
    df: pd.DataFrame,
    x: str,
    y: str,
    covar: str = "mmlu"
) -> dict:
    """
    Compute partial Spearman ρ between x and y controlling for covar.

    Args:
        df    : DataFrame with columns [x, y, covar], shape (N, ≥3), N ≥ N_COMMON_MIN
        x     : predictor column name (e.g., "bbq_disambig", "glue_score", "anli_r1_score")
        y     : outcome column name (e.g., "bbq_ambig", "advglue_score", "anli_r3_score")
        covar : control variable column name; default "mmlu"

    Returns:
        dict:
            rho     : float — partial Spearman ρ ∈ [-1, 1]
            p_value : float — two-tailed p-value (exploratory)
            ci95    : list[float, float] — 95% confidence interval [lo, hi]
            n       : int   — number of models used
            x       : str   — predictor column (for traceability)
            y       : str   — outcome column
            covar   : str   — control variable

    Raises:
        AssertionError: if covar not in df.columns
        ValueError: if p_value is NaN (constant scores detected)
                    if |rho| > 0.999 (Fisher z undefined — flag for Kendall fallback)

    Example return:
        {"rho": 0.62, "p_value": 0.041, "ci95": [0.08, 0.88], "n": 13,
         "x": "bbq_disambig", "y": "bbq_ambig", "covar": "mmlu"}
    """
    import pingouin as pg
    assert covar in df.columns, f"covar '{covar}' not in DataFrame"

    sub = df[[x, y, covar]].dropna()
    result = pg.partial_corr(
        data=sub,
        x=x,
        y=y,
        covar=[covar],
        method="spearman",
        alternative="two-sided",
    ).round(6)

    rho     = float(result["r"].iloc[0])
    p_value = float(result["p-val"].iloc[0])
    ci95    = result["CI95%"].iloc[0].tolist()
    n       = int(result["n"].iloc[0])

    if pd.isna(p_value):
        raise ValueError(f"p_value is NaN for ({x}, {y}, covar={covar}) — constant scores?")
    if abs(rho) > 0.999:
        raise ValueError(
            f"|rho|={abs(rho):.4f} > 0.999 for ({x},{y}) — Fisher z undefined; "
            "fallback to Kendall tau"
        )

    logging.info(f"partial_rho({x},{y},covar={covar}): ρ={rho:.3f}, p={p_value:.4f}, n={n}")
    return {"rho": rho, "p_value": p_value, "ci95": ci95, "n": n,
            "x": x, "y": y, "covar": covar}


def compute_raw_rho_all(df: pd.DataFrame) -> dict:
    """
    Compute raw (unadjusted) Spearman ρ for all 3 dimension pairs (no MMLU control).

    Args:
        df : DataFrame with columns [bbq_disambig, bbq_ambig, glue_score,
             advglue_score, anli_r1_score, anli_r3_score]

    Returns:
        dict:
            rho_fair_raw    : float — spearmanr(bbq_disambig, bbq_ambig)
            rho_advglue_raw : float — spearmanr(glue_score, advglue_score)
            rho_anli_raw    : float — spearmanr(anli_r1_score, anli_r3_score)
            delta_rho_raw   : float — rho_fair_raw − mean(rho_advglue_raw, rho_anli_raw)
            n               : int   — number of models
    """
    from scipy.stats import spearmanr
    rho_fair    = spearmanr(df["bbq_disambig"],  df["bbq_ambig"]).statistic
    rho_advglue = spearmanr(df["glue_score"],    df["advglue_score"]).statistic
    rho_anli    = spearmanr(df["anli_r1_score"], df["anli_r3_score"]).statistic
    delta_raw   = rho_fair - float(np.mean([rho_advglue, rho_anli]))
    return {
        "rho_fair_raw":    float(rho_fair),
        "rho_advglue_raw": float(rho_advglue),
        "rho_anli_raw":    float(rho_anli),
        "delta_rho_raw":   float(delta_raw),
        "n":               len(df),
    }
```

### Subtask L-4-2: fisher_z_test_difference()

```python
def fisher_z_test_difference(
    rho1: float,
    rho2: float,
    n: int
) -> dict:
    """
    Fisher z-test for the difference between two independent correlation coefficients.
    Implements psinger/CorrelationStats independent_corr formula (inline, no extra package).

    Args:
        rho1 : float — ρ_fairness (partial Spearman, MMLU-controlled)
        rho2 : float — ρ_robust_mean (mean of ρ_AdvGLUE and ρ_ANLI)
        n    : int   — sample size (N_common_robust; same for all pairs)

    Returns:
        dict:
            z_stat          : float — Fisher z-test statistic
            p_value_two_tailed : float — two-tailed p-value (exploratory)
            z_rho1          : float — Fisher z of rho1
            z_rho2          : float — Fisher z of rho2
            se_diff         : float — standard error of the difference

    Raises:
        ValueError: if |rho1| >= 1.0 or |rho2| >= 1.0 (Fisher z undefined)
        ValueError: if n <= 3 (denominator n-3 ≤ 0)

    Note:
        p_value_two_tailed uses lenient threshold 0.10 (exploratory label required in outputs).
        Formula: se_diff = sqrt(2 / (n - 3)) for same N;
                 z_stat = (z_rho1 - z_rho2) / se_diff;
                 p = 2 * (1 - norm.cdf(|z_stat|))

    Example:
        fisher_z_test_difference(rho1=0.65, rho2=0.15, n=13)
        → {"z_stat": 1.82, "p_value_two_tailed": 0.069, ...}
    """
    from scipy.stats import norm

    if abs(rho1) >= 1.0:
        raise ValueError(f"|rho1|={abs(rho1)} >= 1.0 — Fisher z undefined")
    if abs(rho2) >= 1.0:
        raise ValueError(f"|rho2|={abs(rho2)} >= 1.0 — Fisher z undefined")
    if n <= 3:
        raise ValueError(f"n={n} <= 3 — insufficient for Fisher z (denominator n-3 ≤ 0)")

    z_rho1  = 0.5 * np.log((1 + rho1) / (1 - rho1))   # atanh(rho1)
    z_rho2  = 0.5 * np.log((1 + rho2) / (1 - rho2))   # atanh(rho2)
    se_diff = np.sqrt(2 / (n - 3))                      # same N for all pairs
    z_stat  = (z_rho1 - z_rho2) / se_diff
    p_val   = 2 * (1 - norm.cdf(abs(z_stat)))           # two-tailed, exploratory

    return {
        "z_stat":               float(z_stat),
        "p_value_two_tailed":   float(p_val),
        "z_rho1":               float(z_rho1),
        "z_rho2":               float(z_rho2),
        "se_diff":              float(se_diff),
    }


def run_full_analysis(df: pd.DataFrame) -> dict:
    """
    Orchestrate complete H-M2 statistical analysis.

    Args:
        df : DataFrame from build_master_dataframe(), shape (N_common_robust, 9)
             columns: [model_name, bbq_disambig, bbq_ambig, mmlu, winogrande,
                       glue_score, advglue_score, anli_r1_score, anli_r3_score]

    Returns:
        dict:
            raw             : dict — compute_raw_rho_all() result
            rho_fairness    : dict — compute_partial_rho(bbq_disambig, bbq_ambig, mmlu)
            rho_advglue     : dict — compute_partial_rho(glue_score, advglue_score, mmlu)
            rho_anli        : dict — compute_partial_rho(anli_r1_score, anli_r3_score, mmlu)
            rho_robust_mean : float — mean(rho_advglue.rho, rho_anli.rho)
            delta_rho       : float — rho_fairness.rho − rho_robust_mean
            fisher_z        : dict — fisher_z_test_difference() result
            gate_directional: bool — delta_rho >= DELTA_RHO_GATE (0.2)
            secondary_both  : bool — rho_advglue.rho < rho_fairness.rho AND rho_anli.rho < rho_fairness.rho
            sensitivity_wino: dict — repeat analysis with winogrande covar (None if N < N_COMMON_MIN)
            n               : int   — N_common_robust

    Side effects:
        Saves results to RESULTS_DIR / "results.json"
        Logs gate status: "H-M2 analysis: Δρ={:.3f} (threshold: 0.2), direction: PASS/FAIL"
    """
    # Step 1: Raw baseline
    raw = compute_raw_rho_all(df)

    # Steps 2-4: Partial ρ per dimension (MMLU-controlled, two-sided)
    res_fair   = compute_partial_rho(df, x="bbq_disambig",  y="bbq_ambig",     covar="mmlu")
    res_adv    = compute_partial_rho(df, x="glue_score",    y="advglue_score",  covar="mmlu")
    res_anli   = compute_partial_rho(df, x="anli_r1_score", y="anli_r3_score",  covar="mmlu")

    # Step 5: Δρ
    rho_robust_mean = float(np.mean([res_adv["rho"], res_anli["rho"]]))
    delta_rho       = res_fair["rho"] - rho_robust_mean

    # Step 6: Fisher z-test for difference
    fisher = fisher_z_test_difference(
        rho1=res_fair["rho"],
        rho2=rho_robust_mean,
        n=res_fair["n"]
    )

    # Step 7: Gate evaluation
    gate_directional = delta_rho >= DELTA_RHO_GATE
    secondary_both   = (res_adv["rho"] < res_fair["rho"]) and (res_anli["rho"] < res_fair["rho"])
    label = "PASS" if gate_directional else "FAIL"
    logging.info(f"H-M2 analysis: Δρ={delta_rho:.3f} (threshold: {DELTA_RHO_GATE}), direction: {label}")

    # Step 8: Sensitivity (Winogrande control)
    wino_df = df.dropna(subset=["winogrande"])
    if len(wino_df) >= N_COMMON_MIN:
        res_fair_w  = compute_partial_rho(wino_df, "bbq_disambig",  "bbq_ambig",     "winogrande")
        res_adv_w   = compute_partial_rho(wino_df, "glue_score",    "advglue_score",  "winogrande")
        res_anli_w  = compute_partial_rho(wino_df, "anli_r1_score", "anli_r3_score",  "winogrande")
        rho_rob_w   = float(np.mean([res_adv_w["rho"], res_anli_w["rho"]]))
        delta_wino  = res_fair_w["rho"] - rho_rob_w
        sensitivity_wino = {
            "rho_fairness": res_fair_w, "rho_advglue": res_adv_w,
            "rho_anli": res_anli_w, "rho_robust_mean": rho_rob_w,
            "delta_rho": delta_wino
        }
    else:
        sensitivity_wino = None
        logging.warning(f"Winogrande N={len(wino_df)} < {N_COMMON_MIN}, sensitivity skipped")

    results = {
        "raw": raw,
        "rho_fairness": res_fair,
        "rho_advglue": res_adv,
        "rho_anli": res_anli,
        "rho_robust_mean": rho_robust_mean,
        "delta_rho": delta_rho,
        "fisher_z": fisher,
        "gate_directional": gate_directional,
        "secondary_both": secondary_both,
        "sensitivity_wino": sensitivity_wino,
        "n": res_fair["n"],
    }

    import json
    RESULTS_DIR.mkdir(exist_ok=True)
    with open(RESULTS_DIR / "results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    return results


def evaluate_gate(delta_rho: float) -> bool:
    """Return delta_rho >= DELTA_RHO_GATE."""
    return delta_rho >= DELTA_RHO_GATE
```

---

## Data Flow Summary

```
h-m1/data/h_m1_scores.csv
        ↓ load_hm1_base()
        ↓
config.ROBUSTNESS_SCORES dict
        ↓ build_robustness_scores()
        ↓
build_master_dataframe()  [inner join on model_name]
        → df: (N_common_robust, 9)
        → saved: data/trustllm_scores_hm2.csv
        ↓
verify_preconditions(df)   [assert N≥8, cols, variance]
        ↓
compute_raw_rho_all(df)    → raw: {rho_fair_raw, rho_advglue_raw, rho_anli_raw, delta_rho_raw}
compute_partial_rho(df, "bbq_disambig", "bbq_ambig", "mmlu")     → rho_fairness
compute_partial_rho(df, "glue_score", "advglue_score", "mmlu")   → rho_advglue
compute_partial_rho(df, "anli_r1_score", "anli_r3_score", "mmlu")→ rho_anli
        ↓
delta_rho = rho_fairness.rho − mean(rho_advglue.rho, rho_anli.rho)
fisher_z_test_difference(rho_fairness.rho, rho_robust_mean, n)   → {z_stat, p_value_two_tailed}
        ↓
run_full_analysis(df)      → results dict
        → saved: results/results.json
        ↓
generate_all_figures(df, results, FIGURES_DIR)
        → figures/gate_metrics_comparison.png
        → figures/rank_heatmap.png
        → figures/per_dimension_scatter.png
        → figures/forest_plot.png
```
