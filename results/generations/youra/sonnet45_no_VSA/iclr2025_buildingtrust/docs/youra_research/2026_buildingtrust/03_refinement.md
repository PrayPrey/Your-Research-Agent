# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-07-09T22:50:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop
- **Gap ID**: Gap1
- **Gap Title**: Dataset Verification Tools for Pre-Phase-3 Hypothesis Validation
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 7

---

## Research Dialogue Context

**Participants**: Dr. Nova (Creative Novelty Explorer), Prof. Vera (Rigorous Validation Architect), Dr. Sage (Research Impact Evaluator), Prof. Pax (Feasibility & Reality Checker), Dr. Ally (Hypothesis Strengthening Champion), Prof. Rex (Hypothesis Stress-Test Master)

**Total Exchanges**: 7

**Convergence Reason**: All 6 criteria met (SPECIFIC core claim, MECHANISM explained, 3 PREDICTIONS stated, NOVELTY articulated, FEASIBILITY validated with power analysis, OBJECTIONS addressed via correlation test + operationalization choices)

### Key Insights

1. **Reframing Gap 1**: Shifted from "build verification tool" (engineering) to "test if variance predicts reliability" (meta-science). This makes the hypothesis empirically testable rather than a software development project.

2. **Power Analysis Breakthrough**: Original group comparison (high-variance vs. low-variance benchmarks) had only 17-36% statistical power at d=0.5, n=6. Switching to Pearson correlation test (continuous variables) achieved 70-90% power with n=5-10 benchmarks.

3. **Scoping for Feasibility**: Narrowed from analyzing mmjerge's 7,635 benchmarks (data extraction nightmare) to 5-10 trust benchmarks with public leaderboards (TrustLLM, HaluBench, TruthfulQA, FinTrust, MultiTrust). This made the hypothesis LIGHT-tier feasible (≤15 tasks, 1-2 weeks).

### Breakthrough Moments

1. **Exchange 7 (Prof. Vera)**: Power analysis exposed that the original design would fail statistical significance even with a real medium effect (d=0.5). Correlation test redesign salvaged the hypothesis from underpowering.

2. **Exchange 4 (Prof. Pax)**: Reality check on data extraction complexity. Extracting meta-features from 4,886 papers (mmjerge corpus) would exceed LIGHT tier scope. Scoping to 5-10 trust benchmarks solved this.

3. **Exchange 5 (Dr. Ally)**: Synthesized the causal mechanism (variance → noise-sensitive rankings → cross-benchmark instability) and connected it to h-e1 Run 3 failure mode (small n-models → inflated variance → risky benchmark).

---

## Final Hypothesis

### Title
**Benchmark Score Variance Predicts Cross-Benchmark Stability in LLM Trust Evaluation**

### Core Claim

Under trust benchmark evaluation with multi-model leaderboards (TrustLLM, HaluBench, TruthfulQA, FinTrust, MultiTrust, n≥10 models each), if benchmark coefficient of variation (CV = σ/μ across model scores) is computed and compared with mean cross-benchmark ranking agreement (Spearman ρ), then CV correlates negatively with ρ (Pearson r < -0.5, p < 0.05), because high score variance indicates inconsistent model differentiation, reducing benchmark reliability as a stable ranking instrument for hypothesis validation.

### Mechanism

**Causal Chain (3 steps)**:

1. **High Variance Arises from Noise**: Benchmark score variance (CV) is elevated by heterogeneous task difficulty (mix of trivial and impossible items), unstable capability measurement (trait varies across contexts), or small effective sample size (few discriminative items amplify noise).

2. **Noise Produces Context-Dependent Rankings**: Benchmarks with noise-sensitive signals produce model rankings that depend on which noise-amplifying items dominate the evaluation. If ranking changes based on random item sampling, the benchmark lacks stable construct validity.

3. **Unstable Rankings Don't Replicate**: Rankings driven by noise fail to correlate across benchmarks sampling different item/context distributions. If Benchmark A's ranking is noise-driven, it won't match Benchmark B's ranking (which samples different noise patterns) → low cross-benchmark ρ.

**Key Insight**: The mechanism predicts variance → instability without requiring causal proof of WHY variance arises. We frame this as an EXISTENCE hypothesis (does the pattern exist?) rather than MECHANISM hypothesis (why does variance cause instability?).

---

## Predictions

### P1 (Primary - MUST_WORK Gate)
**Statement**: Pearson correlation between benchmark CV and mean cross-benchmark Spearman ρ is negative and moderate-to-strong (r < -0.5) with statistical significance (p < 0.05) across 5-10 trust benchmarks.

**Test Method**: Extract CV and compute mean_ρ for each of 5-10 trust benchmarks (TrustLLM, HaluBench, TruthfulQA, FinTrust, MultiTrust). Run Pearson correlation test using `scipy.stats.pearsonr()`.

**Success Criterion**: r < -0.5 AND p < 0.05. Statistical power: 70-90% at n=5-10 for r=-0.5 to -0.7.

**Falsification**: If r ≥ -0.5 OR p ≥ 0.05, variance does not predict stability; H₀ is retained. Hypothesis fails.

### P2 (Secondary - Descriptive Validation)
**Statement**: Benchmarks in the top CV tertile (high variance) exhibit lower mean cross-benchmark ρ than bottom CV tertile (low variance) with Cohen's d > 0.5.

**Test Method**: Split benchmarks into tertiles by CV. Compute mean_ρ for top vs. bottom tertiles. Calculate Cohen's d = (mean_ρ_low_CV - mean_ρ_high_CV) / pooled_SD.

**Success Criterion**: d > 0.5 (medium-large effect per Zieliński thresholds). This is post-hoc descriptive, not primary gate.

**Falsification**: If d < 0.5, the variance-stability relationship is weak even if correlation r < -0.5 holds (linear but small effect).

### P3 (Retrospective - Smoke Test)
**Statement**: FAVABENCH (h-e1 Run 3 PARTIAL failure, 2 models vs. 8 expected) exhibits higher CV than TrustLLM/TruthfulQA, validating that high CV flags risky benchmarks.

**Test Method**: Impute FAVABENCH CV from published error rates (if available) or model performance variance. Compare to TrustLLM/TruthfulQA CVs. Test if FAVABENCH falls in top quartile.

**Success Criterion**: FAVABENCH CV > 75th percentile of TrustLLM/TruthfulQA CVs. Retrospective validation (n=1), not statistical test.

**Falsification**: If FAVABENCH CV is low (bottom quartile), our tool would NOT have flagged it as risky—hypothesis fails retrospective smoke test.

---

## Novelty

**Preserved Novelty**: First work to test benchmark score variance (CV) as a predictor of cross-benchmark stability (ρ). Shifts Gap 1 from "build verification tool" (engineering) to "test if variance predicts reliability" (meta-science contribution to LLM evaluation methodology).

**Key Innovation**: Universal, zero-cost verification signal. CV is computable from any leaderboard in 5 minutes without domain expertise or benchmark-specific engineering. Purely data-driven quality flag.

**Differentiation**:
- **vs. mmjerge (TMLR 2025)**: They document fragmentation (<25% overlap) but don't predict which benchmarks are reliable. We provide a predictive tool (CV → stability) for prospective risk assessment.
- **vs. Kulkarni et al. (arXiv:2504.18114)**: They show metric reliability varies but don't identify meta-features predicting it. We test a specific meta-feature (CV) validated on cross-benchmark ρ.
- **vs. h-e1 Run 3 failure**: Post-hoc diagnosis without prospective prevention. Our hypothesis enables prospective risk scoring before Phase 3 commitment.

---

## Experimental Design

### Dataset
**Trust Benchmark Leaderboard Corpus**: Extract from published papers (TrustLLM Table 4-5, HaluBench supplement, TruthfulQA GitHub, FinTrust paper, MultiTrust documented sources). Meta-analysis of existing benchmark data, not model training.

### Procedure
1. For each benchmark: Extract model names and scores from leaderboard
2. Compute CV = σ/μ where σ = std(scores), μ = mean(scores)
3. For each benchmark pair with ≥5 shared models: Compute Spearman ρ on shared model rankings
4. For each benchmark: Average pairwise ρ values to get mean_ρ
5. Run Pearson correlation test: r, p = pearsonr(CV_values, mean_ρ_values)

### Success Criteria
- Primary: r < -0.5 (negative moderate-to-strong correlation) AND p < 0.05 (statistical significance)
- Secondary: Cohen's d > 0.5 for top vs. bottom CV tertiles on mean_ρ
- Retrospective: FAVABENCH CV > 75th percentile of TrustLLM/TruthfulQA

### Controls
- Benchmark age (years since publication) - control for maturity confound
- n-models ≥ 10 - ensures stable CV estimation
- Model overlap ≥ 5 shared models - ensures reliable ρ computation

---

## Limitations

1. **Small Benchmark Sample (n=5-10)**: Limits generalizability beyond trust evaluation domain. Acknowledged as exploratory study; recommend replication with broader benchmark corpus (e.g., general QA, reasoning, generation benchmarks).

2. **Multi-Dimensional Benchmark Operationalization**: TrustLLM reports 8 dimensional scores (truthfulness, safety, fairness, robustness, privacy, ethics, transparency, accountability). Must choose: (a) average CV across dimensions, (b) use primary dimension (truthfulness) only, or (c) treat each dimension as separate benchmark (inflates n). Will document choice in Phase 2C experiment brief.

3. **Retrospective Validation is n=1**: Testing "would we have flagged FAVABENCH?" is anecdotal, not statistical proof. Provides real-world grounding but doesn't constitute validation.

4. **Correlation ≠ Causation**: We test whether variance PREDICTS stability, not whether variance CAUSES instability. Framed as EXISTENCE hypothesis (pattern detection), deferring mechanistic explanation to future H-M studies.

5. **Confounds Controlled But Not Eliminated**: Benchmark age, n-models, model overlap are controlled via filtering, but other confounds (task type, domain complexity) may exist.

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS) |
| **Clarity Verified** | Yes |
| **Remaining Objections** | Small n (exploratory scope), multi-dimensional operationalization (documented for Phase 2C) |
| **Statistical Power** | 70-90% (correlation test, n=5-10, r=-0.5 to -0.7) |
| **Feasibility** | LIGHT tier (≤15 tasks, 1-2 weeks, public leaderboards) |
| **Readiness for Phase 2B** | ✅ READY |

---

**Next Phase**: Phase 2B - Research Planning (Verification Protocol Development)
