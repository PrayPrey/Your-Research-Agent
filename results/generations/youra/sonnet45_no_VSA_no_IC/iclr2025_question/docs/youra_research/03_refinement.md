# Phase 2A Hypothesis Refinement: H-ParetoUQ-v1

**Generated:** 2026-08-20  
**Workflow:** Phase 2A-Dialogue (Self-Contained Tikitaka Loop)  
**Gap Addressed:** Gap 3 (Priority 1) - Empirical AUROC vs Inference Cost Trade-off for Single-Pass Methods  
**Discussion Exchanges:** 9  
**Convergence:** All criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS resolved)

---

## Executive Summary

**Core Hypothesis:** Single-forward-pass uncertainty quantification methods exhibit a **cost-performance Pareto frontier** on TruthfulQA selective prediction, where different methods are optimal at different inference budgets, challenging the assumption that expensive methods always outperform cheaper alternatives.

**Key Innovation:** Instead of declaring a single "winner" UQ method, we map the complete AUROC vs cost trade-off space, enabling budget-aware method selection for practitioners.

**Testable Predictions:**
- **P0 (Go/No-Go):** Llama-3.1-8B-Instruct achieves baseline accuracy ≥ 45% on TruthfulQA
- **H1 (Expected):** MC dropout k=5 achieves highest AUROC among all methods
- **H2 (Surprising Efficiency):** Temperature scaling AUROC within Δ=0.05 of MC dropout k=5
- **H3 (Core Novelty):** ≥2 methods are Pareto-optimal (no single method dominates all others)

**Confidence Level:** 0.85 (all perspective personas gave STRONG verdicts, all objections resolved)

---

## Research Question

Can single-forward-pass uncertainty estimation methods achieve selective prediction AUROC ≥ 0.70 on existing benchmarks while maintaining inference cost within 2-5× baseline, validating on small models before scaling?

**Refined Research Question (from discussion):**

Do temperature scaling (0× cost), conformal prediction (0× cost), and MC dropout (k-dependent cost) occupy distinct positions on an empirical Pareto frontier for TruthfulQA selective prediction, or does a single method strictly dominate all others?

---

## Hypothesis Statement

**Under:** Selective prediction on TruthfulQA (817 human-annotated questions) using Llama-3.1-8B-Instruct

**If:** We compare temperature scaling (0× cost), conformal prediction (0× cost), and MC dropout k={1,3,5,10} (k× cost)

**Then:** At least 2 methods will occupy distinct positions on the empirical Pareto frontier (no method strictly dominates another)

**Because:** Different UQ mechanisms trade off calibration quality vs computational cost at different efficiency zones:
- **Temperature scaling:** Post-hoc logit calibration (0× cost, limited to monotonic miscalibration correction)
- **Conformal prediction:** Distribution-free coverage via nonconformity scores (0× cost, requires calibration set transfer)
- **MC dropout:** Bayesian approximation via stochastic forward passes (k× cost, captures epistemic uncertainty directly)

---

## Null Hypothesis (H0)

There is no cost-performance trade-off: a single method (e.g., MC dropout k=5) strictly dominates all others by achieving both:
1. Statistically higher AUROC (paired t-test p < 0.05)
2. Equal or lower inference cost (FLOPs ≤ other methods)

**Rejection Criteria:**
- **Reject H0 if:** Pareto set contains ≥2 methods where neither dominates the other (H3 confirmed)
- **OR:** Temp scaling achieves AUROC within Δ=0.05 of MC dropout k=5 AND MC dropout k=5 has highest AUROC (H2 + H1 both confirmed)

**Fail to reject H0 if:** Only one method is Pareto-optimal (dominates all others) OR all methods have statistically indistinguishable AUROC (overlapping 95% CIs)

---

## Variables

### Independent Variable
**UQ_method** (categorical, 6 levels):
- `temperature_scaling` (0× cost)
- `conformal_prediction` (0× cost)
- `mc_dropout_k1` (1× cost)
- `mc_dropout_k3` (3× cost)
- `mc_dropout_k5` (5× cost)
- `mc_dropout_k10` (10× cost)

### Dependent Variables

**Primary DV:**
- **AUROC_selective_prediction** (continuous, range: [0.0, 1.0])
  - Area Under ROC Curve for binary classification (correct vs incorrect prediction)
  - Success threshold: ≥0.70 per primary research question
  - Computed on TruthfulQA test set (817 questions)

**Secondary DV:**
- **inference_cost_normalized** (continuous)
  - FLOPs count per TruthfulQA query, normalized to single forward pass = 1.0×
  - MC dropout k=N measured as N.0× ± 0.1×
  - Temperature scaling and conformal prediction = 1.0× (post-hoc, excludes one-time calibration overhead)

### Controlled Variables
- **Model architecture:** Llama-3.1-8B-Instruct (fixed)
- **Calibration dataset:** HaluEval (~10k samples)
- **Test dataset:** TruthfulQA (817 questions, human-annotated labels)
- **Random seed:** Fixed seeds for 3 runs (42, 123, 456)
- **Evaluation protocol:** Official TruthfulQA script (sylinrl/TruthfulQA repo)

---

## Testable Predictions

### P0: Baseline Validation (Go/No-Go Gate)

**Statement:** Llama-3.1-8B-Instruct achieves baseline accuracy ≥ 45% on TruthfulQA

**Measurement Protocol:**
1. Load HuggingFace checkpoint `meta-llama/Llama-3.1-8B-Instruct`
2. Evaluate using official TruthfulQA script
3. Report accuracy with 95% binomial confidence interval

**Success Criteria:** Accuracy ≥ 45% with 95% CI lower bound > 42%

**If Failed:** CRITICAL - hypothesis NOT testable at 8B scale. Document limitation: "Baseline accuracy too low for UQ methods to demonstrate value. Future work: test with ≥70B models." STOP experiment.

---

### H1: MC Dropout Superiority (Expected Result)

**Statement:** MC dropout k=5 achieves the highest AUROC among all tested UQ methods

**Measurement Protocol:**
- Compute AUROC for all 6 methods
- Rank by mean AUROC over 3 random seeds
- MC dropout k=5 must rank #1

**Success Criteria:** AUROC_mc5 > max(AUROC_temp, AUROC_conf, AUROC_mc1, AUROC_mc3, AUROC_mc10) with paired t-test p < 0.05 for all pairwise comparisons

**If Failed:** MEDIUM impact - zero-cost methods OUTPERFORM expensive methods → paradigm shift. H2 strengthened beyond "competitive" to "superior."

---

### H2: Zero-Cost Competitiveness (Surprising Efficiency)

**Statement:** Temperature scaling achieves AUROC within Δ=0.05 of MC dropout k=5

**Measurement Protocol:**
- Compute |AUROC_temp - AUROC_mc5| using mean values over 3 seeds
- Check if difference ≤ 0.05 (absolute AUROC points)

**Success Criteria:** |AUROC_temp - AUROC_mc5| ≤ 0.05

**Rationale for Δ=0.05:** At AUROC 0.70, Δ=0.05 represents ~7% relative gap. This is meaningful but not game-changing:
- **Temp scaling @ 0.68:** Reject 32% of queries with 68% precision
- **MC dropout k=5 @ 0.73:** Reject 27% of queries with 73% precision
- **Practical difference:** 5% more queries rejected, 5% higher precision

**If Failed:** LOW impact - temp scaling NOT competitive → MC dropout's 5× cost justified for high-stakes selective prediction. Negative result is still valuable.

---

### H3: Pareto Frontier Existence (Core Novelty)

**Statement:** At least 2 UQ methods lie on the empirical Pareto frontier

**Measurement Protocol:**
1. For each method i, compute (cost_i, AUROC_i) = (mean_cost, mean_AUROC) over 3 seeds
2. Method i is Pareto-optimal if: ∀ method j ≠ i, NOT (cost_j ≤ cost_i AND AUROC_j > AUROC_i with paired t-test p < 0.05)
3. Count |Pareto set| ≥ 2

**Success Criteria:** Pareto set contains ≥2 methods with statistically distinct AUROCs (pairwise t-test p < 0.05)

**Example:**
- ✅ **Pareto-optimal:** temp = (1.0×, 0.68±0.02), MC k=5 = (5.0×, 0.73±0.02), t-test p = 0.001
- ❌ **Dominated:** temp = (1.0×, 0.72±0.02), MC k=5 = (5.0×, 0.71±0.02) → temp dominates → |Pareto| = 1

**If Failed:** HIGH impact - Pareto frontier collapses to single winner → budget-aware UQ selection unnecessary. Core novelty claim fails. However, still valuable negative result: "MC dropout k=5 universally optimal for TruthfulQA selective prediction."

---

## Experimental Design

### Phase 0: Baseline Validation (Go/No-Go)

**Objective:** Validate 8B model has sufficient signal for UQ methods

**Protocol:**
1. Load Llama-3.1-8B-Instruct from HuggingFace
2. Evaluate on TruthfulQA using official script
3. Report accuracy with 95% CI

**Decision Rule:**
- If accuracy ≥ 45% → Proceed to Phase 1
- If accuracy < 45% → STOP, document limitation, suggest ≥70B model follow-up

---

### Phase 1: Main Experiment (AUROC vs Cost Comparison)

**Methods (6 variants):**

1. **Temperature Scaling (0× cost)**
   - Implementation: gpleiss/temperature_scaling or probkit/probmetrics
   - Calibration: Optimize T on HaluEval to minimize NLL or ECE
   - Inference: 1.0× (post-hoc, no overhead)

2. **Conformal Prediction (0× cost)**
   - Implementation: SU-JIAYUAN/LofreeCP (validate against Su et al. 2024 spec)
   - Calibration: Compute nonconformity scores (sample_frequency × semantic_similarity) on HaluEval
   - Inference: 1.0× (post-calibration, per-query is single forward pass)

3-6. **MC Dropout k={1,3,5,10} (k× cost)**
   - Implementation: aryanator/dropwise or manual (enable dropout at inference, sample k times)
   - Calibration: None (epistemic uncertainty from variance)
   - Inference: k× (k forward passes per query)

**Datasets:**
- **Calibration:** HaluEval (~10k samples) - for temp scaling and conformal prediction only
- **Test:** TruthfulQA (817 questions, human-annotated truthfulness labels)

**Evaluation Protocol:**

For each UQ method and each random seed (42, 123, 456):
1. Apply method to TruthfulQA test set (never touched during calibration)
2. Compute uncertainty score per question
3. Rank questions by uncertainty (high uncertainty → reject in selective prediction)
4. Compute AUROC: TP = correctly predicted & accepted, FP = incorrectly predicted & accepted
5. Measure inference cost: FLOPs count normalized to 1.0× baseline

**Aggregation:**
- Mean AUROC ± std over 3 seeds per method
- Mean cost ± std over 3 seeds per method

**Statistical Tests:**
- Paired t-test (two-tailed, α=0.05) for pairwise AUROC comparisons

---

### Phase 2: Analysis (Pareto Frontier Construction & Hypothesis Tests)

**Pareto Frontier Construction:**

For each method i:
1. Compute (cost_i, AUROC_i) = (mean_cost, mean_AUROC) over 3 seeds
2. Check dominance: Method i is Pareto-optimal IF ∀ method j ≠ i, NOT (cost_j ≤ cost_i AND AUROC_j > AUROC_i with p < 0.05)
3. Pareto set = {i | i is Pareto-optimal}

**Hypothesis Tests:**

- **H1:** MC dropout k=5 ranks #1 by AUROC (paired t-test vs all others, p < 0.05)?
- **H2:** |AUROC_temp - AUROC_mc5| ≤ 0.05?
- **H3:** |Pareto set| ≥ 2 AND pairwise t-tests show p < 0.05 between Pareto methods?

---

## Novelty

### What Is New

1. **First Systematic Cost-Performance Benchmark for UQ on TruthfulQA**
   - Prior work: Yang et al. 2023 (selective QA, no cost analysis), Su et al. 2024 (conformal prediction, single method), Zhang et al. 2020 (calibration comparison, not LLM context)
   - Our contribution: AUROC vs cost curves for 6 UQ method variants on same benchmark

2. **Pareto Frontier Framing for Practitioner-Facing UQ Selection**
   - Enables budget-aware method selection: see exact cost vs accuracy trade-offs, choose based on deployment constraints
   - Current literature: winner-take-all comparisons (no actionable cost-benefit guidance)

3. **Empirical Test of "Zero-Cost Competitiveness" Hypothesis**
   - H2 explicitly tests whether temp scaling (0× cost) achieves AUROC within Δ=0.05 of MC dropout k=5 (5× cost)
   - Challenges field's implicit "more compute = better UQ" assumption
   - No prior work directly tests this cost-efficiency hypothesis on LLM selective prediction

4. **Cross-Dataset Generalization Test (HaluEval → TruthfulQA)**
   - Calibrating on HaluEval, testing on TruthfulQA (addresses DQ4: cross-dataset AUROC ≥ 0.65)
   - Lin et al. 2025 studied domain-shift conformal prediction but NOT in LLM selective prediction context

---

## Scope & Limitations

### Included
- Single-forward-pass UQ methods (temp scaling, conformal prediction, MC dropout k≤10)
- TruthfulQA selective prediction task (817 human-annotated questions)
- Llama-3.1-8B-Instruct model (fixed architecture)
- AUROC metric for selective prediction quality
- FLOPs-based inference cost (normalized to 1.0× baseline)
- Cross-dataset generalization test (HaluEval → TruthfulQA)

### Excluded
- Ensemble methods (>10× cost, outside 2-5× budget constraint)
- Spectral normalization (Phase 1 Gap 1 - unstudied for LLMs)
- Model scale dependency study (Phase 1 Gap 2 - deferred to future work)
- Multiple-choice TruthfulQA (MC1, MC2 tasks - focus on generative QA only)
- Token-level UQ methods (Phase 1 ROUTE_TO_0 failure - don't predict correctness at small scale)
- HaluEval as test set (used only for calibration)

### Limitations
- **8B model scale only** - if Phase 0 baseline accuracy <45%, hypothesis NOT testable at this scale
- **Single benchmark (TruthfulQA)** - generalization to other truthfulness/factuality benchmarks unknown
- **HaluEval calibration may not transfer** - cross-dataset generalization is explicitly tested (failure is valuable negative result)
- **n=3 random seeds** - small sample size, high-variance results may require n=5 for confidence
- **Low-star implementation repos** - must validate against paper specifications (LofreeCP: 9 stars, dropwise: 8 stars)

---

## Key Assumptions

1. **8B model baseline accuracy ≥ 45% on TruthfulQA**
   - **Validity:** HIGH (Phase 0 pre-check validates empirically)
   - **Impact if violated:** CRITICAL - insufficient signal for UQ methods. STOP experiment, document limitation.

2. **HaluEval calibration set representative for TruthfulQA**
   - **Validity:** MEDIUM (cross-dataset generalization explicitly tested)
   - **Impact if violated:** MEDIUM - conformal prediction may fail to transfer. This is DQ4 generalization test - failure is scientifically valuable.

3. **Human-annotated TruthfulQA labels provide reliable ground truth**
   - **Validity:** HIGH (official dataset uses human consensus, Lin et al. 2021)
   - **Impact if violated:** LOW - dataset is foundational in LLM evaluation community (911 GitHub stars)

4. **FLOPs count accurately reflects inference cost**
   - **Validity:** HIGH (hardware-agnostic, deterministic)
   - **Impact if violated:** LOW - practitioner deployment costs include latency (wall-clock). Mitigation: report both FLOPs and wall-clock time.

5. **Statistical significance (p < 0.05, n=3 seeds) sufficient for reproducibility**
   - **Validity:** MEDIUM (standard ML practice)
   - **Impact if violated:** MEDIUM - small n=3 may miss rare failure modes. Mitigation: increase to n=5 if high variance observed.

---

## Related Work Comparison

| Paper | Focus | Gap | Our Contribution |
|-------|-------|-----|------------------|
| Yang et al. 2023 (16 cit) | TruthfulQA selective QA | No cost analysis, no multi-method comparison | AUROC vs cost curves for 6 methods |
| Su et al. 2024 (74 cit) | API-only conformal prediction | Single method, single dataset | Multi-method benchmark + cross-dataset test |
| Zhang et al. 2020 (293 cit) | Calibration methods comparison | Not LLM-focused, no selective prediction | LLM selective prediction + cost analysis |
| Guo et al. 2017 (9294 cit) | Temperature scaling | Calibration metrics (ECE), not selective prediction | Selective prediction AUROC + cost trade-offs |

---

## Discussion Log Summary

**Total Exchanges:** 9 (all 6 personas participated)

**Convergence Criteria Met:**
- ✅ SPECIFIC: Pareto frontier formalized (Definition B)
- ✅ MECHANISM: 3 methods at different cost zones, HaluEval → TruthfulQA protocol
- ✅ PREDICTIONS: P0/H1/H2/H3 quantitative and falsifiable
- ✅ NOVELTY: First systematic cost-performance benchmark, budget-aware UQ selection
- ✅ FEASIBILITY: All methods theoretically sound, Phase 0 baseline check addresses barrier
- ✅ OBJECTIONS: All 4 Prof. Rex challenges resolved (8B baseline, calibration, Pareto definition, threshold)

**Persona Verdicts:**
- 🔭 Dr. Nova (Novelty): **STRONG**
- 🔬 Prof. Vera (Falsifiability): **STRONG**
- 🎯 Dr. Sage (Significance): **STRONG**
- ⚙️ Prof. Pax (Feasibility): **STRONG**
- 🛡️ Dr. Ally (Strengthening): **CONSTRUCTIVE_REFINEMENT**
- 🔍 Prof. Rex (Critique): **CONCERNS_RESOLVED** → "hypothesis ready for Phase 2B"

---

## Next Steps: Phase 2B

**Phase 2B will:**
1. Parse `03_refinement.yaml` for hypothesis structure
2. Design proof experiments based on P0/H1/H2/H3 predictions
3. Create experimental roadmap with milestones
4. Validate against Phase 2B input expectations

**Phase 2B Readiness:** ✅ All required files generated:
- `03_refinement.yaml` (primary hypothesis definition)
- `02_synthesis.yaml` (discussion metadata)
- `01_round_table/final_opinions.yaml` (per-persona assessments)
- `03_refinement.md` (this file - human-readable summary)

---

**End of Phase 2A Output**
