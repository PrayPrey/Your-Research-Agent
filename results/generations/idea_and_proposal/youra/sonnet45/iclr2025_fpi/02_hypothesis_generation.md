# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-06
**Author:** Pray
**Source Round:** 02a_round_3_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-AdaptiveSampler-v1
**Confidence Level:** 0.88

**Main Hypothesis:**
Under conditions where multiple sampling methods are available for a given probabilistic inference problem, if an adaptive performance predictor selects samplers based on current problem state (Effective Sample Size, convergence rate, dimension, curvature), then the total sampling cost will be reduced by ≥20% compared to fixed best-choice strategies, because the predictor enables dynamic switching that exploits sampler-specific strengths during different phases of exploration (early: broad coverage via flows/diffusion) and convergence (late: refinement via Langevin MCMC).

**Alternative Hypothesis (H0):**
There is no significant difference in total sampling cost between adaptive predictor-based sampler selection and fixed best-choice strategies (cost reduction < 5% or statistically insignificant at p < 0.05).

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Problem State Features | Independent | 4-dimensional vector: (1) Effective Sample Size (ESS) computed via autocorrelation, (2) Convergence rate trend (slope of last 100 iterations), (3) Problem dimension d, (4) Estimated curvature via Hessian eigenvalue ratio | ESS ∈ [10, 10000], Convergence rate ∈ [-0.5, 0.5], d ∈ [10, 500], Curvature ∈ [1, 10^6] |
| Sampler Choice | Independent | Categorical: {Flow Matching, Diffusion Model, Langevin MCMC, Hybrid} - selected by predictor based on Thompson sampling over predicted efficiencies | 4 discrete options |
| Predictor Architecture | Controlled | 3-layer feedforward network with <1000 parameters, trained via supervised learning on (state, sampler, efficiency) tuples from synthetic benchmarks | Fixed architecture: [4 → 64 → 32 → 4] |
| Predicted Sampling Efficiency | Dependent | Expected samples-to-convergence per unit compute-time, output by performance predictor neural network (continuous value) | Efficiency ∈ [0.1, 10.0] samples/second |
| Actual Sampling Cost | Dependent | Wall-clock time to reach convergence criterion (ESS > 1000 OR KL divergence < 0.01), measured across n ≥ 25 runs | Time ∈ [10, 10000] seconds |
| Problem Class | Controlled | Fixed to: Bayesian posterior inference on non-convex log-densities with dimension d ∈ [10, 500] | Gaussian mixtures, funnel distributions, Rosenbrock densities |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

**Step 1:** Problem state features (ESS, convergence rate, dimension, curvature) are extracted from current samples
→ **Step 2:** Performance predictor estimates efficiency for each sampler based on state
→ **Step 3:** Thompson sampling selects sampler using predicted efficiencies with uncertainty awareness
→ **Outcome:** Reduced total sampling cost through optimal sampler allocation

**Detailed Mechanism:**

1. **[Problem State] → [Predictor Output: Efficiency Estimates]**
   - Neural network trained on (state, sampler, efficiency) tuples learns statistical relationship between problem characteristics and sampler performance
   - Predictor outputs mean + uncertainty (Bayesian last layer) for each sampler
   - Mechanism: Supervised learning captures patterns like "high curvature favors Langevin" and "low ESS favors flows"

2. **[Efficiency Estimates] → [Thompson Sampling Selection]**
   - Thompson sampling samples from posterior over efficiencies and selects highest sampled value
   - Early sampling: High uncertainty → explores multiple samplers
   - Late sampling: Low uncertainty → exploits best predictor choice
   - Mechanism: Bandit-based exploration-exploitation balances learning predictor accuracy vs using predictions

3. **[Sampler Selection] → [Reduced Total Cost]**
   - Dynamic switching assigns exploration-focused samplers (flows, diffusion) to early broad-coverage phase
   - Convergence-focused samplers (Langevin) assigned to late refinement phase when ESS is high
   - Warm-starting converts state between samplers to minimize switching overhead
   - Mechanism: Matching sampler strengths to problem phase reduces wasted computation

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | Adaptive Operator Selection Survey (Pei et al., 2025, 13 cites) | State-based operator selection improves meta-heuristic performance by matching operators to optimization stages | Strong |
| Step 1 → Step 2 | Gradient-adjusted Langevin (GAUL, Zuo et al., 2024, 3 cites) | Combining Hessian information (curvature) with Langevin dynamics improves convergence speed | Medium |
| Step 2 → Step 3 | MPC+DRL Hybrid Microgrids (Reddy & Saikia, 2024, 4 cites) | Predictive control + adaptive learning reduces switching losses in hybrid systems | Medium |
| Step 2 → Step 3 | Thompson Sampling literature (foundational) | Thompson sampling provably balances exploration-exploitation in multi-armed bandits | Strong |
| Step 3 → Outcome | Operations Research adaptive selection | Stage-based selection improves over fixed strategies across diverse optimization problems | Strong |
| Step 3 → Outcome | Phase 1 sampling papers (GAUL, VR-FALD, flows) | Different samplers have complementary strengths: Langevin (convergence guarantees, slow mixing) vs Flows (fast coverage, weaker theory) | Strong |

**Key Tension:**

**Tension:** Operations Research "Adaptive Operator Selection" survey (Pei et al., 2025) demonstrates state-based selection improves performance in optimization, BUT the survey also notes that learned selection methods can fail when state features are uninformative or when switching overhead dominates.

**Resolution:** This verification plan addresses the tension through three specific tests:
1. **Test 1 (State informativeness):** Validate predictor accuracy on held-out validation set to ensure state features correlate with sampler performance (Step 1 → Step 2 link)
2. **Test 2 (Switching overhead):** Empirically measure warm-starting conversion cost and compare adaptive vs fixed strategies with/without warm-starting (Step 3 → Outcome link)
3. **Test 3 (Exploration-exploitation):** Ablate Thompson sampling vs greedy vs epsilon-greedy to verify uncertainty handling is necessary (Step 2 → Step 3 link)

If Test 1 shows predictor accuracy < 60%, the hypothesis is rejected (state features insufficient). If Test 2 shows switching overhead > 30%, warm-starting must be improved. If Test 3 shows greedy performs equally, Thompson sampling complexity is unnecessary.

### 1.4 Key Assumptions

1. **ESS can be estimated efficiently (O(n log n) autocorrelation computation) from current samples without prohibitive overhead**
   - Supporting Evidence: Standard MCMC diagnostics literature (Gelman et al., Bayesian Data Analysis)
   - Consequence if Violated: If ESS estimation cost > 5% of sampling cost, state feature extraction becomes bottleneck → Reduces benefit of adaptive selection → Hypothesis weakened but not rejected (net cost reduction decreases)

2. **Performance predictor trained on synthetic benchmarks generalizes to target problem class after few-shot domain adaptation (<10 fine-tuning runs)**
   - Supporting Evidence: Control Theory MPC+DRL paper (Reddy & Saikia, 2024) shows predictive models generalize when pre-trained on diverse scenarios then adapted
   - Consequence if Violated: If generalization requires > 50 fine-tuning runs, adaptation cost becomes prohibitive for one-off problems → Hypothesis applicable only to repeated problem classes (domain restriction)

3. **Switching overhead with warm-starting (initializing new sampler from current state) is <10% of single-sampler run cost**
   - Supporting Evidence: Archon case on adaptive methods shows warm-starting is common practice in optimization; preliminary assumption based on state conversion simplicity
   - Consequence if Violated: If switching cost > 30%, adaptive approach performs worse than fixed strategy → Hypothesis rejected → CRITICAL ASSUMPTION requiring empirical validation in Phase 2B

4. **Training data from synthetic benchmarks (Gaussian mixtures, log-concave densities, energy-based models) covers representative distribution characteristics**
   - Supporting Evidence: Phase 1 papers show Gaussian mixtures and funnel distributions are standard benchmarks in sampling literature
   - Consequence if Violated: If synthetic benchmarks are too simple, predictor fails on complex real distributions → Poor generalization → Hypothesis restricted to benchmark-like problems

5. **Thompson sampling exploration-exploitation sufficiently handles early-state uncertainty where ESS and convergence rate estimates are noisy**
   - Supporting Evidence: Thompson sampling is proven exploration-exploitation strategy in multi-armed bandit literature (foundational work, >1000 cites)
   - Consequence if Violated: If early-stage noise causes systematic predictor errors, adaptive selection degrades to random selection → Net benefit decreases but hypothesis not rejected if late-stage performance compensates

### 1.5 Scope & Boundaries

**Applies to:**
- Probabilistic inference problems where sampling is computational bottleneck (cost > 10 seconds)
- Settings with multiple sampler options available (≥2 distinct methods: flows, diffusion, Langevin, hybrid)
- Problems where state features are estimable without prohibitive cost (ESS, convergence rate, dimension, curvature)
- Scenarios where switching between samplers is beneficial (samplers have complementary strengths across problem phases)
- Problem classes: Bayesian posterior inference, generative model sampling, molecular dynamics equilibrium sampling
- Dimension range: d ∈ [10, 500] (validated range from Phase 1 literature)

**Does NOT apply to:**
- Single-sampler scenarios (no selection needed)
- Problems where state estimation cost exceeds sampling cost (e.g., ultra-fast samplers on low-dimensional problems d < 10)
- Real-time inference constraints preventing predictor inference (latency < 1ms requirements)
- Convex log-concave problems where theoretical optimal sampler is known a priori (Langevin MCMC provably optimal)
- Problems with adversarial or highly irregular distributions where state features are systematically misleading
- Ultra-high-dimensional problems (d > 10^4) where Hessian eigenvalue estimation for curvature feature becomes intractable

**Known Limitations:**
1. Predictor accuracy depends on training data diversity covering target problem characteristics
2. Warm-starting effectiveness varies by sampler pair (flow→MCMC easier than MCMC→flow due to state representation differences)
3. Domain adaptation requires few-shot fine-tuning runs on target problem class (cost: 10 runs × sampling cost)
4. State features may be misleading for adversarially-designed distributions (rare in practice but theoretically possible)
5. Current framework assumes static problem (distribution doesn't change during sampling); dynamic targets require extensions

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Total Sampling Cost vs Fixed Best-Choice):**
Our adaptive sampler selection approach will achieve total sampling cost ≥ 20% lower than fixed best-choice strategy across diverse benchmark problems (Gaussian mixtures, funnel distributions, Rosenbrock densities) with statistical significance (p < 0.05).

*Measurement:*
- Total sampling cost = wall-clock time to reach convergence criterion (ESS > 1000 AND KL divergence < 0.01)
- Comparison: Adaptive selection vs Fixed best-choice (oracle: best single sampler per problem, determined retroactively)
- Statistical test: Paired t-test, n ≥ 25 runs with same random seeds
- Success threshold: Mean cost reduction ≥ 20% with p < 0.05 (one-tailed)

*Basis:*
Operations Research "Adaptive Operator Selection" survey (Pei et al., 2025, 13 cites) reports 15-30% performance improvements when using state-based selection over fixed operators in meta-heuristics. Our 20% threshold is conservative midpoint, accounting for potential switching overhead.

*Falsification Criterion:*
If cost reduction ≤ 5% OR p ≥ 0.05 (statistically insignificant), hypothesis is **REJECTED**.

**Secondary Predictions:**

**P2 (Mechanism Validation - State Features):**
Performance predictor will achieve ≥ 65% accuracy in selecting the best sampler for a given problem state on held-out validation set, demonstrating that state features (ESS, convergence rate, dimension, curvature) are informative.

*Measurement:*
- Accuracy = fraction of times predictor's top-ranked sampler matches ground-truth best sampler
- Ground truth: Run all samplers on validation problems, determine actual best
- Threshold: 65% accuracy (vs 25% random baseline for 4 samplers)

*Falsification:* If accuracy ≤ 40%, state features are insufficiently informative → Rejects Step 1 → Step 2 causal link

**P3 (Robustness - Thompson Sampling Necessity):**
Adaptive selection using Thompson sampling (uncertainty-aware) will achieve ≥ 10% lower worst-case cost compared to greedy selection (always picks highest predicted efficiency) across n ≥ 25 runs, demonstrating robustness to predictor errors.

*Measurement:*
- Worst-case cost = 90th percentile cost across runs
- Comparison: Thompson sampling vs Greedy
- Threshold: 10% improvement in worst-case robustness

*Falsification:* If Thompson sampling performs no better than greedy (≤ 3% difference), uncertainty handling is unnecessary → Simplify to greedy

**P4 (Switching Overhead - Warm-Starting Effectiveness):**
Warm-starting will reduce sampler switching overhead to ≤ 15% of single-sampler run cost, validating Assumption 3's conservative estimate (<10% in assumption, 15% relaxed threshold for validation).

*Measurement:*
- Switching cost = (cost with switching - cost without switching) / cost without switching
- Measure empirically: Run adaptive method with/without warm-starting
- Threshold: Overhead ≤ 15%

*Falsification:* If switching overhead > 30%, warm-starting is inadequate → Hypothesis rejected (Assumption 3 violated)

**P5 (Generalization - Domain Adaptation):**
After few-shot domain adaptation (≤ 10 fine-tuning runs on target problem class), predictor will achieve ≥ 90% of its source domain accuracy, demonstrating generalization capability (Assumption 2 validation).

*Measurement:*
- Target accuracy / Source accuracy ≥ 0.90
- Source: Synthetic benchmarks (training data)
- Target: New problem class (e.g., molecular dynamics if trained on Bayesian inference)

*Falsification:* If generalization ratio ≤ 0.70, predictor requires prohibitive fine-tuning → Hypothesis restricted to source domain only

### 1.7 Statistical Verification Design

**Sample Size Calculation:**
- Minimum n ≥ 25 runs recommended for paired t-test with medium effect size (Cohen's d ≈ 0.5)
- Statistical power: 0.80
- Significance level: α = 0.05 (one-tailed for cost reduction)

**Test Specification:**
- Primary: Paired t-test comparing adaptive vs fixed best-choice on same random seeds
- Report format: Mean cost reduction ± 95% CI, Cohen's d, p-value
- Multiple comparison correction: Bonferroni correction if testing across multiple problem classes

**Experimental Design:**
- Control variables: Problem class, dimension, random seed
- Independent runs: 25 runs per (method, problem) pair
- Counterbalancing: Randomize method execution order to avoid confounds

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence - Foundation):**
"Does adaptive performance predictor-based sampler selection achieve ≥20% cost reduction compared to fixed best-choice strategy under specified conditions (multiple samplers available, dimension d ∈ [10, 500], non-convex posteriors)?"
- Maps to: Primary Prediction (P1)
- Verification type: Empirical (comparative experiments)
- Critical: MUST PASS for Phase 2B to proceed (if fails, hypothesis rejected)

**SH2 (Mechanism - Core):**
"Is the proposed three-step causal mechanism (State Features → Predictor Estimates → Thompson Sampling Selection → Cost Reduction) the actual cause of performance improvement?"
- Maps to: Causal Mechanism (3 steps from ClearThought analysis)
- Verification type: Causal analysis (ablation studies, mechanism tests)
- Critical: Determines explanatory power
- **Phase 2B will decompose into 3 sub-hypotheses:**
  - H-M1: Problem state features (ESS, convergence, dimension, curvature) are informative for predicting sampler efficiency (Step 1 → Step 2)
  - H-M2: Thompson sampling provides robustness benefits over greedy selection when handling predictor uncertainty (Step 2 → Step 3)
  - H-M3: Dynamic switching with warm-starting reduces total cost by matching samplers to problem phases (Step 3 → Outcome)

**SH3 (Comparison - Validation):**
"Does adaptive selection outperform alternative approaches (greedy selection without uncertainty, offline meta-learning, hand-crafted rules, fixed hybrids like GAUL/VR-FALD)?"
- Maps to: Secondary Predictions (P2, P3) and comparison baselines
- Verification type: Comparative empirical (benchmarking study)
- Critical: Determines practical value and validates necessity of approach complexity (Thompson sampling, warm-starting, etc.)

### Readiness Checklist

- [✓] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [✓] Hypothesis ID assigned: H-AdaptiveSampler-v1
- [✓] Confidence level specified: 0.88
- [✓] Alternative hypothesis (H0) defined: No significant cost reduction (<5% or p ≥ 0.05)
- [✓] All variables have operationalization from evidence (6 variables: state features, sampler choice, predictor, predicted efficiency, actual cost, problem class)
- [✓] Causal mechanism has evidence at each step (3 steps, evidence_for_links table with 6 links documented)
- [✓] Causal chain length determined and stored: N = 3
- [✓] Key tension identified: OR survey shows state-based selection works BUT can fail when features uninformative or switching overhead dominates
- [✓] Key tension resolution proposed: Three specific tests (predictor accuracy, switching overhead, exploration-exploitation) address failure modes
- [✓] Key assumptions list consequences if violated (5 assumptions with detailed consequences)
- [✓] At least 2 testable predictions exist: 5 predictions (P1-P5) with primary P1 marked
- [✓] Falsification criteria are defined: P1 rejection (≤5% reduction OR p≥0.05), mechanism failures (P2-P4), generalization failure (P5)
- [✓] Baselines are identified for comparison: Fixed best-choice, greedy selection, offline meta-learning, static hybrids (GAUL, VR-FALD)
- [✓] SH1, SH2, SH3 are clear starting points with explicit decomposition plan for SH2 (3 sub-hypotheses)

**All Phase 2B requirements satisfied ✓**

### Open Questions

1. **Resource Requirements:** What computational resources are needed for predictor training and few-shot domain adaptation? Estimated training cost: 10-50 GPU-hours on synthetic benchmarks. Fine-tuning cost: <10 runs per target domain. Are these costs acceptable for target use cases?

2. **Benchmark Data Availability:** Do existing sampling benchmarks (Gaussian mixtures, funnel distributions, Rosenbrock densities) adequately represent real-world target applications (molecular dynamics, Bayesian inference, LLM alignment)? May need to construct domain-specific validation sets.

3. **Warm-Starting Implementation Feasibility:** How difficult is state conversion between different sampler types (flow→MCMC, MCMC→flow, diffusion→flow)? Preliminary analysis suggests flow→MCMC is straightforward (initialize chain from flow samples) but MCMC→flow may require parameter updates. Phase 2B must validate switching cost assumption empirically.

4. **Priority Verification Order:** Which sub-hypothesis should be verified first in Phase 2B? Recommendation: Start with H-M1 (predictor accuracy) as it's foundational - if state features are uninformative, entire approach fails. Then H-M3 (switching overhead) as Assumption 3 is CRITICAL. Finally H-M2 (Thompson sampling necessity) as it's refinement rather than core requirement.

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-06*
