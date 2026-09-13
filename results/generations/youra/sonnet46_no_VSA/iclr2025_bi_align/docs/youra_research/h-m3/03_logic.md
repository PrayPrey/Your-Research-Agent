# Logic: H-M3 — Scenario Classification of Partial Spearman

**Applied**: statistical-analysis-pipeline pattern (flat functions, no classes)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from base code
**Analyzed Path**: `docs/youra_research/h-m2/code/analyze.py`
**Relevant Symbols**: `load_data(cfg: ExperimentConfig) -> pd.DataFrame`, `run(cfg: ExperimentConfig) -> dict`

Key findings from actual H-M2 code:
- `run()` returns `gate_pass` (bool), NOT `gate_passed`
- `ci_partial` is `[lo, hi]` list (from `bca["ci_partial"]`)
- `load_data()` outputs cols: `model_name`, `TruthfulQA_MC2`, `bbq_accuracy`, `MMLU`, `family`

---

## External Dependencies (Base Hypothesis)

```python
# From: docs/youra_research/h-m2/code/analyze.py (ACTUAL CODE)

def load_data(cfg: ExperimentConfig) -> pd.DataFrame:
    # Output cols: model_name, TruthfulQA_MC2, bbq_accuracy, MMLU, family
    # Raises RuntimeError on missing file, missing cols, or N < cfg.n_min
    ...

def run(cfg: ExperimentConfig) -> dict:
    # Returns keys (verified): partial_rho, ci_partial ([lo,hi]), ci_raw ([lo,hi]),
    #   raw_rho, N, gate_pass (bool, NOT gate_passed), outcome (str),
    #   family_rhos, weighted_rho, ci_overlap_status, figures
    ...
```

**Verified from**: `docs/youra_research/h-m2/code/analyze.py` (actual implementation)

H-M3 does NOT import H-M2 at runtime. It reads `h_m2_results.json` directly.
`load_data` logic is replicated in `load_tier1_dataframe()` for Tier 2 DataFrame construction.

---

## A-4: assign_scenario + verify_mechanism_activated [Complexity: 9, Budget: 2]

Applied: Standard Python conditional classification

### L-4-1: assign_scenario() [Subtask 1/2]

```python
def assign_scenario(
    partial_rho: float,
    ci_lo: float,
    ci_hi: float,
    cfg: ExperimentConfig,
) -> dict:
    """Classify partial_rho into scenario a/b/c/ambiguous.
    Returns: {scenario: str, is_ambiguous: bool, narrative: str}"""
    ...
```

**Pseudo-code:**

```
1. Validate inputs:
   - if ci_lo >= ci_hi: raise ValueError(f"ci_lo={ci_lo} must be < ci_hi={ci_hi}")
   - if not (-1.0 <= partial_rho <= 1.0): raise ValueError(f"partial_rho={partial_rho} out of [-1,1]")

2. Compute ambiguity flags:
   - grey_zone = (-cfg.scenario_a_bound <= partial_rho <= cfg.scenario_b_bound)
     # Point in (-0.20, +0.40) — not cleanly in any named scenario
   - ci_spans_zero_and_b = (ci_lo < 0) and (ci_hi > cfg.scenario_b_bound)
     # CI overlaps both 0 AND +0.40 boundary simultaneously
   - is_ambiguous = grey_zone or ci_spans_zero_and_b

3. Assign scenario:
   if is_ambiguous:
       scenario = "ambiguous"
       narrative = (
           f"partial_rho={partial_rho:.3f} [BCa 95% CI: {ci_lo:.3f}, {ci_hi:.3f}] "
           f"falls in grey zone ({-cfg.scenario_a_bound}, {cfg.scenario_b_bound}) or "
           f"CI spans conflicting boundaries. Finding is ambiguous but valid."
       )
   elif abs(partial_rho) < cfg.scenario_a_bound:
       scenario = "a"
       narrative = (
           f"Scenario a (Independent Constructs): partial_rho={partial_rho:.3f} "
           f"[BCa 95% CI: {ci_lo:.3f}, {ci_hi:.3f}]. After controlling for MMLU, "
           f"TruthfulQA and BBQ are orthogonal (|rho| < {cfg.scenario_a_bound})."
       )
   elif partial_rho > cfg.scenario_b_bound:
       scenario = "b"
       narrative = (
           f"Scenario b (Scale-Free Coherence): partial_rho={partial_rho:.3f} "
           f"[BCa 95% CI: {ci_lo:.3f}, {ci_hi:.3f}]. Factuality and bias co-move "
           f"beyond general capability (rho > {cfg.scenario_b_bound})."
       )
   elif partial_rho < cfg.scenario_c_bound:
       scenario = "c"
       narrative = (
           f"Scenario c (Scale-Masked Tradeoff): partial_rho={partial_rho:.3f} "
           f"[BCa 95% CI: {ci_lo:.3f}, {ci_hi:.3f}]. MMLU masks a negative "
           f"factuality-bias relationship (rho < {cfg.scenario_c_bound})."
       )
   else:
       # Fallback — should not reach given grey_zone check above
       scenario = "ambiguous"
       is_ambiguous = True
       narrative = f"Unclassified: partial_rho={partial_rho:.3f}. Review boundaries."

4. Return {"scenario": scenario, "is_ambiguous": is_ambiguous, "narrative": narrative}
```

**Tensor shapes / types:**

| Variable | Type | Note |
|----------|------|------|
| partial_rho | float | Scalar in [-1, 1] |
| ci_lo, ci_hi | float | BCa CI bounds; ci_lo < ci_hi required |
| return["scenario"] | str | One of: "a", "b", "c", "ambiguous" |
| return["is_ambiguous"] | bool | True only for "ambiguous" scenario |
| return["narrative"] | str | >= 1 sentence for paper writing |

**Error conditions:**
- `ValueError("ci_lo must be < ci_hi")` if CI ordering violated
- `ValueError("partial_rho out of [-1,1]")` if range violated

---

### L-4-2: verify_mechanism_activated() + integration test [Subtask 2/2]

```python
def verify_mechanism_activated(results: dict) -> tuple[bool, dict]:
    """Check all mechanism indicators; logs each to stdout.
    Returns: (all_ok: bool, indicators: dict[str, bool])"""
    ...
```

**Pseudo-code:**

```
1. indicators = {}

2. indicators["h_m2_loaded"] = (
       "partial_rho" in results
       and results["partial_rho"] is not None
       and isinstance(results["partial_rho"], (int, float))
   )

3. indicators["scenario_assigned"] = (
       results.get("scenario") in {"a", "b", "c", "ambiguous"}
   )

4. ci = results.get("ci_partial", [])
   indicators["ci_bounds_valid"] = (
       isinstance(ci, (list, tuple))
       and len(ci) == 2
       and ci[0] is not None
       and ci[1] is not None
       and float(ci[0]) < float(ci[1])
   )

5. indicators["narrative_generated"] = (
       isinstance(results.get("narrative"), str)
       and len(results.get("narrative", "")) > 10
   )

6. for key, val in indicators.items():
       status = "OK" if val else "FAIL"
       print(f"[verify_mechanism] {key}: {status}")

7. all_ok = all(indicators.values())
   print(f"[verify_mechanism] overall: {'PASS' if all_ok else 'FAIL'}")

8. return (all_ok, indicators)
```

**Input:** `results: dict` — assembled after `assign_scenario()` is called
**Output:** `tuple[bool, dict[str, bool]]` — `(all_ok, indicators)`

No exceptions raised; missing/wrong-type keys produce `False` indicators.

---

## A-5: Tier 2 Analysis [Complexity: 10, Budget: 2]

Applied: pingouin partial_corr + rapidfuzz fuzzy join pattern

### L-5-1: tier2_analysis() core — fuzzy join + N-gate + partial_corr [Subtask 1/2]

```python
def tier2_analysis(
    df_tier1: pd.DataFrame,
    harmbench_data: dict,
    cfg: ExperimentConfig,
) -> dict:
    """Fuzzy-join Tier1 with HarmBench, N-gate, compute partial Spearman.
    Returns full results dict or SKIPPED status."""
    ...
```

**Required cols in df_tier1:** `model_name`, `TruthfulQA_MC2`, `bbq_accuracy`, `MMLU`

**Pseudo-code:**

```
1. Validate df_tier1 columns:
   required = ["model_name", "TruthfulQA_MC2", "bbq_accuracy", "MMLU"]
   missing = [c for c in required if c not in df_tier1.columns]
   if missing: raise RuntimeError(f"df_tier1 missing columns: {missing}")

2. Build harmbench DataFrame:
   harmbench_df = pd.DataFrame([
       {"model_name": k, "harm_rate": v}
       for k, v in harmbench_data.items()
   ])

3. df_merged = fuzzy_join(df_tier1, harmbench_df, threshold=75)
   # fuzzy_join internally:
   #   for each row in df_tier1:
   #     best_match, score, _ = process.extractOne(
   #         row["model_name"], harmbench_df["model_name"], scorer=fuzz.token_sort_ratio
   #     )
   #     if score >= threshold: keep row with merged harm_rate

4. N_harm = len(df_merged)

5. if N_harm < cfg.n_min_harmbench:
       return {
           "tier2_status": "SKIPPED",
           "N_harmbench": N_harm,
           "reason": f"N={N_harm} < n_min={cfg.n_min_harmbench} after fuzzy join",
       }

6. if N_harm < 4:
       raise RuntimeError(f"N_harm={N_harm} too small for partial_corr (need >= 4)")

7. # TruthfulQA × HarmBench | MMLU
   import pingouin as pg
   res_tqa = pg.partial_corr(
       data=df_merged,
       x="TruthfulQA_MC2",
       y="harm_rate",
       covar="MMLU",
       method="spearman",
   )
   rho_tqa = float(res_tqa["r"].iloc[0])
   ci_tqa = list(res_tqa["CI95%"].iloc[0])   # [lo, hi] Fisher parametric CI

8. # BBQ × HarmBench | MMLU
   res_bbq = pg.partial_corr(
       data=df_merged,
       x="bbq_accuracy",
       y="harm_rate",
       covar="MMLU",
       method="spearman",
   )
   rho_bbq = float(res_bbq["r"].iloc[0])
   ci_bbq = list(res_bbq["CI95%"].iloc[0])   # [lo, hi]
```

**Error conditions:**
- `RuntimeError` on missing df_tier1 columns
- `RuntimeError` if `N_harm < 4` (pingouin would silently produce NaN)
- pingouin may raise if MMLU has zero variance — not guarded (rare edge case)

---

### L-5-2: Tier 2 scenario assignment + results packaging [Subtask 2/2]

```python
# Continuation inside tier2_analysis() after step 8:

9. scenario_tqa = assign_scenario(rho_tqa, ci_tqa[0], ci_tqa[1], cfg)
   scenario_bbq = assign_scenario(rho_bbq, ci_bbq[0], ci_bbq[1], cfg)

10. return {
        "tier2_status": "EXECUTED",
        "N_harmbench": N_harm,
        "tqa_harm_partial_rho": rho_tqa,
        "tqa_harm_ci": ci_tqa,          # [lo, hi]
        "scenario_tqa_harm": scenario_tqa["scenario"],
        "narrative_tqa_harm": scenario_tqa["narrative"],
        "bbq_harm_partial_rho": rho_bbq,
        "bbq_harm_ci": ci_bbq,          # [lo, hi]
        "scenario_bbq_harm": scenario_bbq["scenario"],
        "narrative_bbq_harm": scenario_bbq["narrative"],
    }
```

**Full return type:**

| Key | Type | When present |
|-----|------|-------------|
| `tier2_status` | `str` | Always |
| `N_harmbench` | `int` | Always |
| `reason` | `str` | SKIPPED only |
| `tqa_harm_partial_rho` | `float` | EXECUTED only |
| `tqa_harm_ci` | `[float, float]` | EXECUTED only |
| `scenario_tqa_harm` | `str` | EXECUTED only |
| `narrative_tqa_harm` | `str` | EXECUTED only |
| `bbq_harm_partial_rho` | `float` | EXECUTED only |
| `bbq_harm_ci` | `[float, float]` | EXECUTED only |
| `scenario_bbq_harm` | `str` | EXECUTED only |
| `narrative_bbq_harm` | `str` | EXECUTED only |

---

## A-8: Fig1 Scenario Panel [Complexity: 9, Budget: 2]

Applied: matplotlib horizontal number line pattern

### L-8-1: Number line + CI band rendering logic [Subtask 1/2]

```python
def plot_scenario_panel(results: dict, cfg: ExperimentConfig) -> str:
    """Fig1: horizontal number line with partial_rho point + BCa CI band + boundaries.
    Returns: absolute path to saved PNG."""
    ...
```

**Pseudo-code:**

```
1. Extract values:
   partial_rho = float(results["partial_rho"])
   ci_lo, ci_hi = results["ci_partial"][0], results["ci_partial"][1]
   scenario = results["scenario"]
   # Raise KeyError naturally if missing — caller's contract

2. fig, ax = plt.subplots(1, 1, figsize=cfg.fig_size)

3. # Draw horizontal axis line
   ax.axhline(y=0, color="black", linewidth=1.5, zorder=1)
   ax.set_xlim(-0.75, 0.75)
   ax.set_ylim(-0.6, 0.6)

4. # BCa CI band as filled rectangle straddling y=0
   ax.fill_betweenx(
       [-0.08, 0.08], ci_lo, ci_hi,
       alpha=0.35, color="steelblue", zorder=2,
       label=f"BCa 95% CI [{ci_lo:.3f}, {ci_hi:.3f}]",
   )

5. # Partial rho point estimate
   ax.plot(
       partial_rho, 0,
       marker="D", color="steelblue", markersize=11,
       zorder=5, label=f"partial_rho = {partial_rho:.3f}",
   )

6. # X-axis ticks at boundary values
   ax.set_xticks([-0.6, -0.4, -0.20, 0.0, 0.20, 0.40, 0.6])
   ax.set_xticklabels(["-0.6", "-0.4", "-0.20", "0", "+0.20", "+0.40", "+0.6"], fontsize=10)
   ax.set_yticks([])
```

**Input types:**

| Variable | Type | Note |
|----------|------|------|
| `results["partial_rho"]` | float | Scalar |
| `results["ci_partial"]` | list[float, float] | BCa CI [lo, hi] |
| `results["scenario"]` | str | "a"/"b"/"c"/"ambiguous" |

---

### L-8-2: Scenario boundary annotations + save [Subtask 2/2]

```python
# Continuation of plot_scenario_panel() after step 6:

7. # Scenario boundary vertical lines
   BOUNDARIES = [
       (-cfg.scenario_a_bound, f"−{cfg.scenario_a_bound}", "right"),
       ( cfg.scenario_a_bound, f"+{cfg.scenario_a_bound}", "left"),
       ( cfg.scenario_b_bound, f"+{cfg.scenario_b_bound}", "left"),
   ]
   for x_val, label, ha in BOUNDARIES:
       ax.axvline(x=x_val, color="crimson", linestyle="--", linewidth=1.3, alpha=0.75, zorder=3)
       ax.text(x_val, 0.18, label, ha=ha, va="bottom", color="crimson", fontsize=9)

8. # Scenario region text labels
   ax.text( 0.00, -0.30, "Scenario a\n(independent)",  ha="center", fontsize=8, color="dimgray")
   ax.text( 0.57, -0.30, "Scenario b\n(coherence)",    ha="center", fontsize=8, color="dimgray")
   ax.text(-0.55, -0.30, "Scenario c\n(tradeoff)",     ha="center", fontsize=8, color="dimgray")

9. # Assigned scenario annotation box
   SCENARIO_COLORS = {
       "a": "#d0eaf8", "b": "#d0f8d0", "c": "#f8d0d0", "ambiguous": "#f8f8d0"
   }
   ax.text(
       0.5, 0.97,
       f"Assigned: Scenario {scenario.upper()}",
       transform=ax.transAxes, ha="center", va="top",
       fontsize=13, fontweight="bold",
       bbox=dict(
           boxstyle="round,pad=0.4",
           facecolor=SCENARIO_COLORS.get(scenario, "white"),
           edgecolor="gray", linewidth=1,
       ),
   )

10. ax.set_xlabel("Partial Spearman rho  (TruthfulQA × BBQ | MMLU)", fontsize=11)
    ax.set_title("H-M3: Scenario Classification of Partial Spearman", fontsize=13, pad=10)
    ax.legend(loc="lower right", fontsize=9, framealpha=0.8)
    plt.tight_layout()

11. import os
    os.makedirs(cfg.figures_dir, exist_ok=True)
    out_path = os.path.join(cfg.figures_dir, "fig1_scenario_panel.png")
    plt.savefig(out_path, dpi=cfg.fig_dpi, bbox_inches="tight")
    plt.close(fig)
    return os.path.abspath(out_path)
```

**Error conditions:**
- `KeyError` if `partial_rho`, `ci_partial`, or `scenario` missing from `results`
- `OSError` if `cfg.figures_dir` not writable (raised by `savefig`)

---

## Subtasks Summary [6/6 used]

| ID | Task | Description |
|----|------|-------------|
| L-4-1 | assign_scenario() | Full boundary logic, ambiguity detection via grey_zone + CI-overlap check, narrative strings for all 4 outcomes |
| L-4-2 | verify_mechanism_activated() | 4-indicator dict check (h_m2_loaded, scenario_assigned, ci_bounds_valid, narrative_generated) + stdout logging |
| L-5-1 | tier2_analysis() core | Column validation, fuzzy_join, N-gate (< n_min_harmbench → SKIPPED), pingouin partial_corr for TQA×Harm and BBQ×Harm |
| L-5-2 | Tier 2 packaging | assign_scenario() on both pairs, build and return full results dict with all tier2 keys |
| L-8-1 | Fig1 number line | ax setup, xlim/ylim, fill_betweenx CI band, diamond marker point, xticks at boundary values |
| L-8-2 | Fig1 annotations + save | 3 boundary vlines with labels, region text, scenario annotation box with color coding, savefig return abs path |
