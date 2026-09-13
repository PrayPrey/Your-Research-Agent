# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-06
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-DC-CP-CodeVerif-v1
**Confidence Level:** 0.85

**Main Hypothesis:**
Under code generation scenarios where complete formal verification is computationally intractable, if a conformal prediction framework is applied with domain-specific calibration (n=100-1000+ verified samples per domain) and lightweight verification oracles (type checkers, static analyzers, test suites), then probabilistic correctness guarantees with distribution-free finite-sample coverage will be achieved (empirical coverage rate matching theoretical (1-α) within statistical tolerance), because conformal prediction's exchangeability assumption combined with oracle-based nonconformity scores produces calibrated prediction intervals for code correctness.

**Alternative Hypothesis (H0):**
There is no relationship between conformal prediction calibration with verification oracles and the accuracy of probabilistic correctness guarantees for LLM-generated code. Coverage rates will not match theoretical guarantees, and prediction intervals will be miscalibrated or uninformative.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| **Calibration dataset size** | Independent | Number of verified code samples (n) collected per domain, measured empirically based on distribution diversity using Maximum Mean Discrepancy (MMD) metric | n=100 (minimal), n=500 (moderate), n=1000+ (comprehensive) |
| **Nonconformity score function** | Independent | Oracle choice: (1) Type checker severity (mypy output), (2) Static analyzer warnings count (pylint), (3) Test coverage percentage (pytest), or (4) Weighted ensemble. Validated for monotonicity (Spearman ρ > 0.6) during calibration | Single oracle or ensemble weights [0.3, 0.4, 0.3] |
| **Coverage level** | Independent | User-specified confidence parameter (1-α), controls prediction interval width | α = 0.10 (90%), α = 0.05 (95%), α = 0.01 (99%) |
| **Prediction interval tightness** | Dependent | Average width of correctness probability estimates [p_lower, p_upper], measured in probability units (0.0-1.0). Narrower intervals indicate more informative predictions | Expected: 0.15-0.40 (tight), 0.40-0.70 (moderate), >0.70 (wide/uninformative) |
| **Empirical coverage rate** | Dependent | Actual percentage where true correctness falls within predicted interval on holdout test set (size ≥100 samples), measured via binary correctness oracle. Should match theoretical (1-α) within binomial confidence interval | Expected: (1-α) ± 0.05 for well-calibrated framework |
| **LLM model architecture** | Controlled | Fixed model used for code generation across all experiments to isolate framework effect | GPT-4, Claude-3.5-Sonnet, or CodeLlama-70B |
| **Code domain** | Controlled | Well-defined narrow domain validated for exchangeability via MMD < 0.10 threshold on test vs calibration distributions | "Python sorting functions", "Java data processing with type annotations", "Python numerical code with type hints" |

### 1.3 Causal Mechanism

**Step 1: Domain-Specific Calibration → Empirical Quantiles of Nonconformity Scores**

Domain-specific calibration dataset (n=100-1000+ verified samples from narrow domain like "Python sorting functions") is collected and each sample is evaluated with verification oracle(s) to produce nonconformity scores. Empirical quantiles are computed from this calibration distribution to establish score thresholds for different coverage levels.

*Mechanism*: Conformal prediction theory requires finite sample calibration to establish the distribution of nonconformity scores under the exchangeability assumption. The quantile q_α satisfies P(s_new > q_α) ≤ α for new exchangeable samples.

*Evidence*: Portela et al. (2025, 7 cit.) demonstrates conformal prediction provides non-asymptotic guarantees for biological systems with finite calibration samples. Kiyani et al. (2025, 20 cit.) proves decision-theoretic foundations showing prediction sets are optimal for risk-averse agents optimizing value-at-risk.

*Falsification Point*: If calibration set n < 30 → inaccurate quantile estimation → miscalibrated coverage. If calibration set is biased (not exchangeable with test) → incorrect baseline distribution → coverage guarantee breaks.

**Step 2: Oracle Evaluation of New Code → Nonconformity Score s_new**

When LLM generates new code, lightweight verification oracle (type checker severity, static analyzer warnings, test coverage, or ensemble) evaluates the code and produces a nonconformity score s_new representing deviation from "typical correct code" pattern.

*Mechanism*: Verification oracles (mypy, pylint, pytest) compute measurable signals about code properties (type correctness, code quality, test pass rate) without requiring complete formal verification. These serve as proxy measurements for code correctness likelihood.

*Evidence*: Phase 1 research shows AutoSafeCoder (32 cit, 2024) uses static analyzer + dynamic fuzzing for security verification, ROCODE (4 cit, 2025) achieves 99.1% compilation pass rate with program analysis + backtracking mechanism. Demonstrates oracles provide actionable signals for code quality.

*Falsification Point*: If oracle produces non-monotonic scores (false positives/negatives dominate) → noisy signal → wide prediction intervals. If oracle unavailable for target domain → no scoring mechanism → framework inapplicable.

**Step 3: Nonconformity Score + Calibrated Quantiles → Prediction Interval [p_lower, p_upper]**

The nonconformity score s_new for generated code is mapped to a prediction interval [p_lower, p_upper] representing calibrated confidence bounds for code correctness probability, using the empirically calibrated quantiles from Step 1.

*Mechanism*: Conformal prediction maps observed scores to coverage-guaranteed intervals via the exchangeability assumption. If calibration and test samples are exchangeable, then P(true correctness ∈ [p_lower, p_upper]) ≥ (1-α) by construction (Vovk et al. foundational CP theory).

*Evidence*: Portela et al. (2025) demonstrates distribution-free uncertainty quantification with non-asymptotic guarantees even when predictive models are misspecified. This transfers to code verification: even if oracle is imperfect, coverage guarantees hold under exchangeability.

*Falsification Point*: If exchangeability violated (distribution shift between calibration and test detected via MMD > 0.10) → theoretical coverage guarantee invalid → empirical coverage deviates from (1-α). If oracle scores not transferable across code samples → prediction intervals unreliable.

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | Portela et al. (2025, 7 cit) + Kiyani et al. (2025, 20 cit) | Conformal prediction provides finite-sample, non-asymptotic coverage guarantees through empirical quantile calibration | Strong (proven theory) |
| Step 2 → Step 3 | AutoSafeCoder (32 cit, 2024) + ROCODE (4 cit, 2025) | Static analyzers and program analysis produce actionable signals for code correctness (99.1% compilation pass rate, 13% vulnerability reduction) | Strong (empirical validation) |
| Step 3 → Outcome | Portela et al. (2025) + Conformal Prediction foundational theory | Distribution-free guarantees hold even with misspecified models, provided exchangeability assumption satisfied | Strong (theoretical + cross-domain empirical) |

**Key Tension:**

**Tension**: Portela et al. (2025) demonstrates conformal prediction works for continuous biological systems with natural variability, but our application is to discrete code correctness (binary correct/incorrect outcome) with deliberate design rather than natural variation. There is uncertainty whether exchangeability assumption (valid for i.i.d. biological samples) transfers to structured code generation tasks.

**Resolution**: This Phase 2B verification plan will test exchangeability empirically within narrow code domains (e.g., "Python sorting functions") by measuring Maximum Mean Discrepancy (MMD) between calibration and test distributions. If MMD < 0.10, exchangeability is validated; if MMD > 0.10, domain must be narrowed further or recalibration performed. Sub-hypothesis SH1 (Existence) directly tests whether exchangeability holds for code domains.

### 1.4 Key Assumptions

1. **Exchangeability within narrow code domains**: Calibration and test code samples come from the same domain distribution (e.g., all "Python sorting functions" are exchangeable).
   - *Evidence*: Conformal prediction theory requires exchangeability for coverage guarantees (Portela et al. 2025).
   - *Validation Method*: Maximum Mean Discrepancy (MMD) < 0.10 threshold on test vs calibration distributions.
   - *Consequences if violated*: Theoretical coverage guarantees become invalid. Empirical coverage will deviate from (1-α), potentially severely. Framework becomes unreliable for deployment decisions.

2. **Oracle availability and signal quality**: At least one lightweight verification oracle (type checker, static analyzer, test suite) exists for target domain and produces reasonably informative scores (Spearman ρ > 0.6 correlation with true correctness).
   - *Evidence*: mypy, pylint, pytest are standard tools with broad language support (Phase 1 Exa research).
   - *Validation Method*: Compute correlation between oracle scores and ground-truth correctness on calibration set.
   - *Consequences if violated*: Noisy oracle scores → wide prediction intervals → framework provides little practical value. If no oracle exists → framework inapplicable to domain.

3. **Finite calibration feasibility**: Can collect n≥100 verified code samples per target domain within reasonable effort (1-10 hours per domain).
   - *Evidence*: SV-COMP benchmark has 385 verified Java programs. JetBrains verified-cogen and KTH Vecogen repositories provide verified code generation examples (Phase 1 Exa research).
   - *Validation Method*: Pilot data collection for 2-3 target domains.
   - *Consequences if violated*: Insufficient calibration samples (n<30) → inaccurate quantile estimation → miscalibrated coverage. Framework requires prohibitive data collection effort.

4. **Monotonic nonconformity scores**: Higher oracle scores correlate with higher code incorrectness probability (negative correlation with correctness).
   - *Evidence*: Type checkers report errors (higher errors → less correct), static analyzers report warnings (more warnings → lower quality), test coverage inversely correlated with bugs.
   - *Validation Method*: Empirical Spearman correlation test during calibration: ρ(oracle_score, incorrectness) > 0.6.
   - *Consequences if violated*: Non-monotonic scores → prediction intervals cannot distinguish correct from incorrect code → framework uninformative.

5. **Stable distribution (or detectable shift)**: Code distribution remains stable over time, or distribution shift is detectable via MMD monitoring and triggers recalibration.
   - *Evidence*: Code generation tasks are typically well-defined (e.g., HumanEval benchmark problems don't change). When tasks change, distribution shift can be measured.
   - *Validation Method*: Continuous MMD monitoring on incoming test samples. Alert if MMD > 0.10.
   - *Consequences if violated*: Silent distribution shift → exchangeability breaks → coverage guarantees invalid → false confidence in incorrect code.

### 1.5 Scope & Boundaries

**Where This Hypothesis Applies:**
- Well-defined narrow code domains with homogeneous task structure (e.g., "Python sorting functions", "Java data processing with type annotations", "Python numerical code with type hints")
- LLM-generated code where lightweight verification oracles exist (type checkers, static analyzers, test suites available)
- Scenarios where probabilistic assurances are acceptable (rapid prototyping, non-safety-critical applications, preliminary screening before full formal verification)
- Domains where n≥100 verified code samples can be collected for calibration
- Applications requiring interpretable uncertainty quantification (prediction intervals with coverage guarantees)

**Where This Does NOT Apply:**
- Cross-domain or multi-domain code generation where exchangeability assumption fails (e.g., mixing "sorting" and "networking" tasks)
- Programming languages without verification oracle tooling (obscure DSLs, legacy languages with no static analysis)
- Safety-critical systems requiring deterministic correctness guarantees (medical devices, avionics, nuclear systems)
- Tasks with high temporal distribution shift where code patterns change rapidly (exchangeability becomes invalid)
- Domains where calibration data is unavailable or prohibitively expensive to collect

**Known Limitations:**
- Requires domain-specific recalibration for each narrow code domain (not one-size-fits-all)
- Coverage guarantees become invalid under distribution shift (requires MMD monitoring and recalibration)
- Prediction interval width depends on oracle quality (poor oracles → wide uninformative intervals)
- Exchangeability assumption difficult to verify rigorously in practice (MMD is proxy, not guarantee)
- Calibration dataset collection effort scales with number of target domains
- Framework provides probabilistic assurances only, not deterministic proofs of correctness
- Interval width may be too wide for practical deployment decisions in low-data regimes (n<100)

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Empirical Coverage Rate Matches Theoretical Guarantee)**:
Our conformal prediction framework will achieve empirical coverage rates that match theoretical guarantees (1-α) within binomial confidence intervals.

*Measurement*:
- For α = 0.05 (95% coverage), empirical coverage rate must be within [0.90, 1.00] on holdout test set (n ≥ 100 samples)
- Statistical test: One-sample binomial test, H0: empirical_coverage = 0.95, two-tailed, α = 0.05
- Success: p-value > 0.05 (fail to reject H0, indicating coverage matches theoretical)

*Basis*: Conformal prediction theory guarantees P(true correctness ∈ predicted interval) ≥ (1-α) under exchangeability. Domain standard for statistical learning: coverage within ±0.05 of target considered well-calibrated (Portela et al. 2025, Kiyani et al. 2025).

*Expected Range*: Empirical coverage 92-98% for 95% theoretical coverage (binomial variability with n=100)

**Secondary Predictions:**

**P2 (Prediction Interval Tightness Improves with Calibration Size)**:
As calibration dataset size increases from n=100 → n=500 → n=1000, average prediction interval width will decrease by ≥15%.

*Measurement*: Average interval width ΔW = mean(p_upper - p_lower) across test set
- Baseline (n=100): ΔW₁₀₀ (reference)
- Target (n=1000): ΔW₁₀₀₀ ≤ 0.85 × ΔW₁₀₀ (15% tighter)
- Statistical test: Paired t-test on interval widths, p < 0.05

*Basis*: Larger calibration sets improve quantile estimation accuracy, leading to tighter (more informative) prediction intervals while maintaining coverage guarantees.

**P3 (Oracle Ensemble Outperforms Single Oracle)**:
Multi-oracle ensemble (type checker + static analyzer + test coverage) will produce 10-20% tighter prediction intervals than single best oracle while maintaining coverage.

*Measurement*:
- Compare ΔW_ensemble vs ΔW_best_single
- Target: ΔW_ensemble ≤ 0.85 × ΔW_best_single (15% improvement minimum)
- Constraint: Both must maintain empirical coverage ≥ 0.90

*Basis*: Ensemble reduces noise from individual oracle errors through weighted averaging (reliability-based weights estimated during calibration).

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any of the following occur:

1. **Primary Failure - Coverage Miscalibration**: Empirical coverage rate deviates significantly from theoretical (1-α)
   - Specifically: For 95% theoretical coverage, empirical coverage < 0.85 OR > 1.00
   - Indicates: Conformal prediction framework fails to provide valid probabilistic guarantees for code verification

2. **Mechanism Failure - Exchangeability Violation**: Distribution shift detected between calibration and test sets
   - Specifically: Maximum Mean Discrepancy (MMD) > 0.10 on test vs calibration distributions
   - Indicates: Core assumption (exchangeability) violated → theoretical foundation breaks

3. **Oracle Failure - Non-Monotonic Scores**: Verification oracle scores show no correlation with true correctness
   - Specifically: Spearman ρ(oracle_score, incorrectness) < 0.3 during validation
   - Indicates: Oracle provides no useful signal → prediction intervals uninformative

4. **Practical Failure - Intervals Too Wide**: Prediction intervals too wide to be useful for deployment decisions
   - Specifically: Average interval width > 0.70 (meaning correctness probability only constrained to ±35%)
   - Indicates: Framework technically valid but practically useless

### 1.7 SOTA Baseline (Optional - If SOTA Comparison Mode)

*Not applicable - this research introduces novel application of conformal prediction to code verification domain. No SOTA baseline for "probabilistic correctness assurance via conformal prediction" exists. Comparison is against (1) deterministic formal verification (SMT solvers), (2) heuristic confidence scores without guarantees, and (3) Bayesian probabilistic verification.*

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Minimum test set size: n ≥ 100 samples per domain (for binomial test statistical power)
- Minimum calibration set size: n ≥ 100 per domain (empirically determined, may need up to 1000+)
- Number of domains to test: 3 domains (Python sorting, Java data processing, Python numerical code)
- Statistical power: 0.80 for detecting ±0.10 deviation from target coverage

**Test Specification:**
- **Primary metric (P1)**: One-sample binomial test for coverage rate
  - Null hypothesis: empirical_coverage = (1-α)
  - Alternative: empirical_coverage ≠ (1-α)
  - Significance level: α_test = 0.05 (two-tailed)
  - Report: Empirical coverage, 95% binomial CI, p-value

- **Secondary metrics (P2, P3)**: Paired t-tests for interval width comparisons
  - Test: ΔW_treatment < ΔW_baseline
  - Significance: α = 0.05 (one-tailed)
  - Effect size: Cohen's d ≥ 0.5 (medium effect)
  - Report: Mean difference in interval width, 95% CI, Cohen's d, p-value

**Validation Protocol:**
- Holdout evaluation: 70% calibration, 30% test split per domain
- Cross-validation: 5-fold for robustness check
- Exchangeability check: Compute MMD on each test fold, require MMD < 0.10
- Oracle monotonicity check: Spearman ρ > 0.6 on calibration set

**Report Format:**
- Coverage calibration plot: Empirical vs theoretical coverage across multiple α levels (0.01, 0.05, 0.10)
- Interval width distribution: Histogram + summary statistics (mean, median, 25th/75th percentile)
- Oracle reliability: Spearman correlation matrix for multi-oracle ensemble
- Distribution shift monitoring: MMD values for each test fold
- Deployment decision simulation: Percentage of code accepted/rejected at various confidence thresholds

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
Does conformal prediction with domain-specific calibration produce empirical coverage rates that match theoretical guarantees (1-α) for LLM-generated code within narrow code domains?

*Maps to*: Primary prediction (P1) - empirical coverage rate validation
*Verification type*: Empirical statistical test (binomial test on holdout set)
*Critical status*: MUST PASS - if empirical coverage deviates significantly from (1-α), theoretical foundation is invalid

**SH2 (Mechanism):**
Are the three causal steps (calibration → oracle scoring → prediction intervals) the actual mechanism producing calibrated probabilistic correctness guarantees?

*Maps to*: Causal mechanism with 3 steps
*Verification type*: Causal analysis with ablation studies
*Phase 2B decomposition*: Will become 3 mechanism sub-hypotheses:
  - H-M1: Does domain-specific calibration (n=100-1000+) produce accurate empirical quantiles under exchangeability?
  - H-M2: Do verification oracles (type checkers, static analyzers, test suites) produce monotonic nonconformity scores (ρ > 0.6)?
  - H-M3: Does mapping oracle scores to prediction intervals via calibrated quantiles maintain coverage guarantees?

**SH3 (Comparison):**
Does our conformal prediction framework provide tighter prediction intervals (more informative) than single-oracle baselines while maintaining coverage, and does oracle ensemble outperform single best oracle?

*Maps to*: Secondary predictions (P2, P3)
*Verification type*: Comparative empirical analysis
*Baselines*: Single oracle (type checker only, static analyzer only, test coverage only)

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned (H-DC-CP-CodeVerif-v1)
- [x] Confidence level specified (0.85)
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence (7 variables with measurement methods)
- [x] Causal mechanism has evidence at each step (3 steps, evidence_for_links table completed)
- [x] Causal chain length (N=3) determined and documented
- [x] Key tension identified (continuous biology vs discrete code) and resolution proposed (empirical exchangeability validation via MMD)
- [x] Key assumptions list consequences if violated (5 assumptions with validation methods and consequences)
- [x] At least 2 testable predictions exist (3 predictions: P1 primary + P2, P3 secondary)
- [x] Falsification criteria are defined (4 falsification conditions with quantitative thresholds)
- [x] Baselines are identified for comparison (SMT solvers, Bayesian methods, heuristic confidence scores)
- [x] SH1, SH2, SH3 are clear starting points for Phase 2B decomposition

**Status: ✅ ALL REQUIREMENTS MET - READY FOR PHASE 2B**

### Open Questions

1. **Calibration Data Collection Effort**: What is the realistic time/cost to collect 100-1000 verified code samples per domain? Pilot study needed for 2-3 target domains to validate feasibility assumption.

2. **Exchangeability Validation Threshold**: Is MMD < 0.10 the right threshold for code domains? May need empirical tuning via sensitivity analysis (test MMD thresholds 0.05, 0.10, 0.15).

3. **Oracle Ensemble Weight Optimization**: How to determine optimal oracle weights [w1, w2, w3] for ensemble? Phase 2B should test: (a) equal weights, (b) reliability-based (from calibration), (c) learned weights (optimization).

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-06*
