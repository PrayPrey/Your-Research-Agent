# Product Requirements Document: H-M3

**stepsCompleted:** [PRD]
**Hypothesis:** H-M3 — Scenario Classification of Partial Spearman (TruthfulQA × BBQ | MMLU)
**Type:** MECHANISM (SHOULD_WORK)
**Date:** 2026-07-30
**Author:** Anonymous
**Base Hypothesis:** H-M2

---

## 1. Executive Summary

H-M3 applies pre-specified scenario classification to the MMLU-controlled partial Spearman correlation (partial_rho) produced by H-M2. The result assigns the TruthfulQA×BBQ relationship to one of three publishable scenarios: (a) independent constructs, (b) scale-free coherence, or (c) scale-masked tradeoff. All outcomes — including "ambiguous" — are valid reportable findings. Gate FAILS only on code execution error.

This is a thin downstream analysis layer: no ML model, no dataset download, no training loop. Runtime ~5 seconds.

---

## 2. Problem Statement

After H-M2 establishes that MMLU significantly mediates the TruthfulQA×BBQ correlation, H-M3 asks: **what dimensional relationship does this imply?** The three scenarios exhaust the interpretable possibilities:
- (a) Factuality and bias are orthogonal once scale is removed
- (b) They co-move even beyond scale (coherent alignment signal)
- (c) MMLU masks a negative relationship (hidden tradeoff)

Assigning a scenario with BCa CI support is the primary contribution. Tier 2 extends to HarmBench safety and Tier 3 tests RLHF ΔBBQ sign direction.

---

## 3. Stakeholders

- **Researcher:** Anonymous — consumes scenario label and narrative for paper writing (Phase 6)
- **Phase 4 Coder:** Implements `assign_scenario()` + Tier 2/3 analysis
- **Phase 6 Paper Writer:** Uses scenario narrative as core framing

---

## 4. Data Specification

### 4.1 Primary Dataset (Tier 1) — Auto-load from H-M2

| Field | Value |
|-------|-------|
| Source | `docs/youra_research/h-m2/code/results/h_m2_results.json` |
| Load Method | `json.load()` |
| Required Keys | `partial_rho`, `ci_partial` ([lo, hi]), `raw_rho`, `ci_raw`, `N` |
| Optional Keys | `family_rhos`, `weighted_rho`, `outcome` |
| Preprocessing | None — values pre-validated by H-M2 |

**No manual download required** — JSON file is H-M2 output artifact.

### 4.2 Secondary Dataset (Tier 2) — HarmBench

| Field | Value |
|-------|-------|
| Source | Hardcoded dict from arXiv:2402.04249 Table 2 |
| Load Method | Inline Python dict (no URL, no download) |
| Models | 33 models with `harm_rate` (attack success rate) |
| Join Condition | Inner join with Tier 1 dataset on model_name (fuzzy match) |
| Skip Condition | N_harmbench < 20 after join |

### 4.3 Tertiary Dataset (Tier 3) — RLHF ΔBBQ

| Field | Value |
|-------|-------|
| Source | H-M1 base/chat pairs (321 pairs from H-M1 validated data) |
| Load Method | CSV load from H-M1 data path |
| Content | ΔBBQ = BBQ(chat) − BBQ(base) per model pair |
| Analysis | scipy.stats.binomtest for sign(ΔBBQ) > 0 |

---

## 5. Functional Requirements

### FR-1: H-M2 Results Loading
- Load `h_m2_results.json` from relative path `../h-m2/code/results/h_m2_results.json`
- Validate presence of required keys: `partial_rho`, `ci_partial`, `raw_rho`, `ci_raw`, `N`
- Fail with descriptive error if file missing or keys absent
- Assert `ci_partial[0] < ci_partial[1]` (CI ordering)

### FR-2: Scenario Classification (Primary)
Implement `assign_scenario(partial_rho, ci_lo, ci_hi) -> dict`:
- Scenario boundaries (pre-specified, immutable):
  - (a) `|partial_rho| < 0.20` → "independent constructs"
  - (b) `partial_rho > 0.40` → "scale-free coherence"
  - (c) `partial_rho < -0.20` → "scale-masked tradeoff"
  - ambiguous: CI overlaps both 0 AND 0.40 simultaneously, OR point estimate in grey zone (−0.20, +0.40)
- Return: `{scenario, is_ambiguous, narrative}`
- Scenario "ambiguous" is a valid SHOULD_WORK outcome (not a failure)

### FR-3: Mechanism Verification
Implement `verify_mechanism_activated(results) -> (bool, dict)`:
- Check `h_m2_loaded`, `scenario_assigned`, `ci_bounds_valid`, `narrative_generated`
- Log all indicator states to stdout

### FR-4: Tier 2 Analysis (Conditional)
Implement `tier2_analysis(df_tier1, harmbench_data) -> dict`:
- Join Tier 1 LLM data with HarmBench on model_name
- Skip (return SKIPPED status) if N_harmbench < 20
- If N ≥ 20: compute partial Spearman for TruthfulQA×HarmBench and BBQ×HarmBench (controlling MMLU)
- Apply `assign_scenario()` to each pair

### FR-5: Tier 3 Analysis (Optional)
- Load ΔBBQ values for 321 base/chat pairs (from H-M1 data)
- `k_positive = sum(ΔBBQ > 0)`
- `scipy.stats.binomtest(k=k_positive, n=321, p=0.5, alternative='two-sided')`
- Report direction: "positive" if p<0.05 AND k/N>0.5, "negative" if p<0.05 AND k/N<0.5, "null" otherwise

### FR-6: Ablation Studies
- **Ablation 1 (CI method):** Re-assign scenario using Fisher parametric CI from pingouin; compare to BCa assignment
- **Ablation 2 (boundary sensitivity):**
  - Tight: `|rho| < 0.15`, `rho > 0.35`, `rho < -0.15`
  - Wide: `|rho| < 0.25`, `rho > 0.45`, `rho < -0.25`
  - Report whether scenario label changes
- **Ablation 3 (Tier comparison):** Tabulate scenario assignments across Tier 1/2/3

### FR-7: Visualization (Mandatory)
- **Fig1:** Scenario assignment panel — horizontal number line, BCa CI band, scenario boundary lines (±0.20, +0.40), scenario label annotation
- **Fig2:** Pairwise partial correlation heatmap ({TruthfulQA, BBQ, HarmBench} pairs) — if Tier 2 executed
- **Fig3:** Raw vs Partial comparison bar chart with scenario boundary overlay (extends H-M2 Fig1)
- **Fig4:** ΔBBQ histogram with sign test annotation — if Tier 3 executed
- Output: `docs/youra_research/h-m3/figures/`

### FR-8: Results Serialization
Save `h_m3_results.json` with:
```json
{
  "partial_rho": float,
  "ci_partial": [float, float],
  "raw_rho": float,
  "ci_raw": [float, float],
  "N": int,
  "scenario": "a|b|c|ambiguous",
  "is_ambiguous": bool,
  "narrative": str,
  "ablation_ci_method": {scenario, matches_primary: bool},
  "ablation_boundary_tight": {scenario},
  "ablation_boundary_wide": {scenario},
  "tier2": {...},
  "tier3": {...},
  "mechanism_verified": bool,
  "gate_passed": bool
}
```

---

## 6. Non-Functional Requirements

| NFR | Requirement |
|-----|-------------|
| Reproducibility | seed=42, N_bootstrap=5000 (inherited from H-M2; no re-bootstrap in Tier 1) |
| Runtime | < 30 seconds total (Tier 1: ~1s, Tier 2: ~5s if executed, Tier 3: ~1s) |
| Error handling | All failure modes raise descriptive exceptions before any analysis runs |
| Code reuse | Reuse H-M2 statistical primitives where possible; no re-implementation of BCa bootstrap for Tier 1 |
| Output format | JSON (machine-readable) + PNG figures (paper-ready, 300 DPI) |

---

## 7. Dependencies

### 7.1 Python Packages

| Package | Version | Purpose |
|---------|---------|---------|
| pingouin | ≥ 0.5.0 | Tier 2 partial_corr + Fisher CI |
| scipy | ≥ 1.8.0 | binomtest (Tier 3) |
| numpy | ≥ 1.21 | Array ops, bootstrap indexing |
| pandas | ≥ 1.3 | DataFrame ops for Tier 2 join |
| matplotlib | ≥ 3.5 | Figure generation |
| rapidfuzz | ≥ 2.0 | Fuzzy join for Tier 2 model_name matching |
| json | stdlib | H-M2 results loading |

### 7.2 External Repositories / Reference

| Resource | URL | Usage |
|----------|-----|-------|
| H-M2 codebase | `docs/youra_research/h-m2/code/` | Reuse `analyze.py` statistical primitives |
| pingouin | https://github.com/raphaelvallat/pingouin | Tier 2 partial_corr API |
| arXiv:2402.04249 | HarmBench paper | Table 2 hardcoded values |

---

## 8. Success Criteria

| Criterion | Threshold | Gate |
|-----------|-----------|------|
| H-M2 results loaded | partial_rho not None | MUST |
| Scenario assigned | scenario ∈ {a, b, c, ambiguous} | MUST (GATE PASS) |
| No code exception | No unhandled exception | MUST (GATE FAIL if violated) |
| Ambiguous is valid | SHOULD_WORK gate still passes for ambiguous | YES |
| Mechanism verified | all verify_mechanism_activated indicators True | SHOULD |
| Tier 2 attempted | N_harmbench reported (even if SKIPPED) | SHOULD |
| Figures generated | Fig1 mandatory; Fig2-4 conditional | Fig1 MUST |

---

## 9. Out of Scope

- Re-computing partial_rho from raw CSV (Tier 1 uses H-M2 precomputed value)
- Any ML model training
- Any new dataset download
- Modifying H-M2 results or code

---

## 10. Phase 2C Completeness Check

| Item | Covered in FRs |
|------|---------------|
| Baseline model (raw_rho) | FR-1, FR-8 |
| Proposed model (assign_scenario) | FR-2 |
| Ablation variants (CI method, boundary, Tier) | FR-6 |
| Custom metrics (scenario, N_harmbench, binomtest_p) | FR-8 |
| Visualizations | FR-7 |
| Tier 2 HarmBench | FR-4 |
| Tier 3 RLHF ΔBBQ | FR-5 |

All Phase 2C items covered. ✅
