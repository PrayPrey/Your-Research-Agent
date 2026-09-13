# H-M4: Per-Hypothesis Context (JIT Generated)

**Generated:** 2026-08-25 (JIT by Phase 2C step-01 from 02b_verification_plan.md)
**Hypothesis ID:** H-M4
**Type:** MECHANISM
**Gate:** SHOULD_WORK

---

## Hypothesis Statement

Under the condition that logistic model parameters are plausible (H-M3 confirmed), if we apply the saturation detection criterion (top-3 models exceed fitted asymptote K AND monthly gain rate < 5% of peak rate) to full historical GLUE and SuperGLUE timeseries, then the detected saturation dates will match community-recognized ground truth dates within ±6 months, because the inflection point + asymptote exceedance criterion operationalizes the same exhaustion of benchmark-exploitable signal that motivated the community to create successor benchmarks.

---

## Experimental Setup (from Phase 2A via Phase 2B)

**Independent Variables:**
- Saturation criterion parameters (K exceedance threshold, gain-rate threshold)
- Benchmark identity (GLUE, SuperGLUE)

**Dependent Variables:**
- Detected saturation date (month/year)
- Saturation date error |detected − ground_truth| in months
- Prospective forecast error (P3 test, GLUE only)

**Dataset:**
- Name: Papers With Code Leaderboard (GLUE, SuperGLUE)
- Type: programmatic-api
- Source: paperswithcode-client (historical archive on GitHub: paperswithcode/paperswithcode-data)
- Cache path: /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_mldpr/data
- Hypothesis fit: Full timeseries from benchmark launch to saturation needed; GLUE/SuperGLUE have hundreds of entries spanning all phases; already used and validated in H-E1, H-M1, H-M2, H-M3

**Model:**
- Name: logistic-scipy (3-parameter, scipy curve_fit)
- Pretrained: No (analytic fit)
- Hypothesis fit: Logistic parameters (K, r, t0) already validated as plausible in H-M3; saturation criterion built on top of fitted model

---

## Ground Truth Dates

| Benchmark | Ground Truth Event | Ground Truth Date | Source |
|-----------|-------------------|-------------------|--------|
| GLUE | SuperGLUE publication (community response to GLUE saturation) | September 2019 | arXiv:1905.00537 |
| SuperGLUE | BIG-bench announcement (community response to SuperGLUE saturation) | ~June 2021 | arXiv:2206.04615 |

---

## Prerequisites Satisfied

- H-M3 VALIDATED (MUST_WORK PASS): K ∈ [0.85,1.0], r > 0, t0 border case documented
- Proven components from H-M3: extract_params(), bootstrap_ci(), curve_fit pipeline
- Optimal hyperparameters: bounds K[0.5,1.05], r[0.01,3.0], t0[-24,72]; p0=[0.92,0.15,12.0]; maxfev=10000

---

## Success Criteria (from Phase 2B)

- Primary: Saturation date error < 6 months for both GLUE and SuperGLUE
- Secondary (P3): Prospective forecast error < 3 months for GLUE (truncate at 6 months before T_sat, re-fit, forecast)
- Gate: SHOULD_WORK — failure → EXPLORE (try alternative criteria, document limitation)

---

## Baseline & Comparison

- Baseline: No saturation detection (null model — returns "never saturated")
- Proposed: Dual-criterion detection (top-3 > 0.99×K AND monthly_gain < 0.05×peak_rate)
- Comparison target: Community ground truth dates (documented publication dates)
