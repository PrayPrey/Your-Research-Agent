# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-08
**Author:** Pray
**Source Round:** 02a_round_2_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-RegretLens-v1
**Confidence Level:** 0.85

**Main Hypothesis:**
Under the condition of finite-horizon tabular MDPs with formal regret bounds, if practitioners use RegretLens to extract concrete constants from theoretical proofs and compute instance-specific regret predictions for their MDP parameters (S, A, H, T), then they will select theoretically-optimal algorithms with >70% accuracy compared to empirical benchmarks, because concrete constant extraction enables problem-size-specific performance prediction that translates asymptotic worst-case theory into actionable practical guidance.

**Alternative Hypothesis (H0):**
There is no correlation between RegretLens's theoretical algorithm rankings (based on concrete regret predictions) and empirical performance rankings on OpenRL Benchmark. Algorithm selection accuracy ≤ 50% (random chance).

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Concrete constants from proofs | Independent | Extract constants C₁, C₂, etc. from regret bound proofs (Agrawal 2022, Domingues 2020) using manual parsing + LLM extraction (GPT-4 on LaTeX) | 5-10 constants per algorithm (e.g., C_TS_1=15.2, C_TS_2=8.7) |
| Instance-specific regret predictions | Independent | Compute f(S,A,H,T,δ,C₁,C₂,...) for user-provided MDP parameters to produce concrete regret estimates | Numeric regret values (e.g., TS: 5,240 vs UCB: 8,100 for S=100, A=10, H=50, T=10⁶) |
| Algorithm selection accuracy | Dependent | Percentage of cases where RegretLens theoretical ranking matches empirical performance ranking on OpenRL Benchmark (Spearman rank correlation) | Target: >70% match, measured across 20+ MDP configurations |
| MDP problem size | Controlled | Fixed ranges for validation experiments | S ∈ [10,1000], A ∈ [2,100], H ∈ [10,100], T ∈ [10⁴,10⁷] |
| Algorithm coverage | Controlled | Fixed set of algorithms with formal regret bounds | Thompson Sampling, UCB-VI, UCRL2, Fictitious Discount, Model-based methods (5-10 algorithms) |

### 1.3 Causal Mechanism

**Step 1: Proof Constant Extraction → Concrete Bound Functions**
- Mechanism: Symbolic parsing (sympy, LaTeX processing) converts theoretical proofs into computable functions f(S,A,H,T,δ,C₁,C₂,...)
- Evidence: Agrawal 2022 appendix derives explicit constants for Õ(√DSAT) Thompson sampling bound; Domingues 2020 provides Ω(H³SA/ε²) with derivable constants
- Falsification point: If proofs only contain existential '∃C > 0' without explicit values, or LaTeX parsing fails on complex derivations

**Step 2: Concrete Bound Functions → Instance-Specific Predictions**
- Mechanism: Substituting user MDP parameters (e.g., S=100, A=10, H=50, T=10⁶) into f() produces numeric regret estimates
- Evidence: Guo 2021 shows finite-horizon MDP regret formulas can be computed in polynomial time for specific S,A,H,T; standard computational evaluation
- Falsification point: If bound functions non-computable (involve intractable optimization) or suffer numeric instability for large parameters

**Step 3: Instance-Specific Predictions → Algorithm Rankings**
- Mechanism: Lower predicted regret indicates theoretically better algorithm for that problem size, enabling comparative ranking
- Evidence: Domingues 2020 minimax bounds show different algorithms dominate in different parameter regimes (e.g., S vs A sensitivity)
- Falsification point: If multiple algorithms have identical asymptotic bounds (all Õ(√T)) making ranking impossible, or crossover points outside practical ranges

**Step 4: Algorithm Rankings → Selection Accuracy >70%**
- Mechanism: Worst-case theoretical rankings correlate with average-case empirical performance despite constant looseness
- Evidence: Agrawal 2022 shows near-optimal bounds (gap to Domingues 2020 lower bound is small), implying predictive tightness; dennybritz/RL (21.8K stars) demonstrates demand for theory-practice translation
- Falsification point: If worst-case bounds extremely loose (100x-1000x) causing theoretical rankings to diverge completely from empirical performance

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Agrawal 2022 (229 cites) | Explicit constant derivations in proof appendix for Õ(√DSAT) bound | Strong |
| Step2 → Step3 | Guo 2021 (10 cites) | Finite-horizon regret formulas computationally tractable | Strong |
| Step3 → Step4 | Domingues 2020 (108 cites) | Minimax lower bounds show parameter-dependent algorithm performance regimes | Strong |
| Step4 → Outcome | Agrawal 2022 + dennybritz (21.8K stars) | Near-optimal bounds + demonstrated demand for theory-practice tools | Medium (risk: constant looseness) |

**Key Tension:**
- **Tension:** Agrawal 2022 provides worst-case regret bounds optimized for adversarial MDPs, but practitioners operate in benign average-case environments (OpenRL Benchmark). Domingues 2020 shows bounds are tight asymptotically, but concrete constants may be loose (10x-100x) for finite T.
- **Resolution:** This verification plan tests whether 70% ranking accuracy threshold can be achieved despite looseness by (1) empirically validating tightness scores on OpenRL Benchmark and (2) annotating predictions with confidence based on measured looseness. If tightness is insufficient (<70%), multi-metric strategy (accuracy + efficiency) provides alternative success path.

### 1.4 Key Assumptions

1. **Theoretical proofs contain extractable concrete constants (not just existential '∃C > 0' statements)**
   - Evidence: Agrawal 2022 proof appendix provides explicit constant derivations for Thompson sampling bound
   - Consequence if violated: Constant extraction step fails → tool cannot produce numeric predictions → entire hypothesis fails

2. **Worst-case regret bounds correlate with average-case empirical performance rankings despite looseness**
   - Evidence: Domingues 2020 shows minimax lower bounds are tight up to poly-log factors; Agrawal 2022 achieves near-optimal gap
   - Consequence if violated: Theoretical rankings diverge from empirical performance → selection accuracy <50% → hypothesis rejected by falsification criteria

3. **Practitioners prefer theoretical guidance over exhaustive empirical benchmarking when accuracy >70%**
   - Evidence: dennybritz/RL (21.8K stars) and OpenAI Spinning Up (11.5K stars) show demand for theory-practice translation resources
   - Consequence if violated: Tool technically works but achieves low adoption → practical impact limited (does not invalidate hypothesis, but reduces significance)

4. **Open-source computational tool will achieve adoption similar to educational resources**
   - Evidence: OpenAI Spinning Up (11.5K stars) demonstrates viable adoption pattern for theory-practice tools
   - Consequence if violated: Same as assumption 3 - limited adoption but technical validity intact

5. **Empirical validation via OpenRL Benchmark provides sufficient coverage of MDP structures**
   - Evidence: Benchmark contains ~50 environments spanning diverse state spaces, action spaces, and horizons
   - Consequence if violated: Validation may not generalize beyond tested environments → need to expand benchmark coverage or acknowledge scope limitation

### 1.5 Scope & Boundaries

**Where hypothesis applies:**
- Finite-horizon episodic MDPs with discrete state/action spaces (tabular setting)
- Algorithms with formal worst-case regret bounds published in peer-reviewed papers
- Problem sizes within practical ranges: S ∈ [10,1000], A ∈ [2,100], H ∈ [10,100], T ∈ [10⁴,10⁷]
- Practitioners selecting algorithms before empirical evaluation (pre-benchmarking use case)

**Where it does NOT apply:**
- Continuous control with function approximation (no formal regret bounds for deep RL algorithms like PPO, SAC)
- Infinite-horizon discounted settings (different theoretical framework)
- Algorithms without published proofs (e.g., heuristic methods)
- Extremely large state spaces (S > 10⁶) where constants may dominate asymptotic terms
- Post-hoc analysis after empirical results available (tool designed for pre-selection guidance)

**Known limitations:**
- Constant extraction accuracy depends on proof clarity and LLM parsing capability (estimated 90% accuracy based on GPT-4 capabilities)
- Worst-case bounds may be 10x-100x loose compared to average-case performance (mitigated by tightness scoring)
- Limited to 5-10 algorithms in MVP (expandable via community contributions)
- Validation coverage limited to OpenRL Benchmark environments (~50 MDPs)

### 1.6 Testable Predictions

**Primary Prediction:**
**P1 (Algorithm Selection Accuracy vs Random Baseline 50%):**
RegretLens's theoretical algorithm rankings will match empirical performance rankings on OpenRL Benchmark with >70% accuracy (Spearman rank correlation ρ > 0.7, p < 0.05).

*Measurement:*
- For 20 MDP configurations (varying S, A, H), compute RegretLens theoretical ranking of 5-10 algorithms
- Compare to empirical performance ranking from OpenRL Benchmark (average return over 50 episodes)
- Calculate Spearman rank correlation: ρ > 0.7 with p < 0.05 indicates significant predictive power
- Statistical test: Permutation test with n ≥ 20 MDP configurations

*Basis:*
Random algorithm selection achieves 50% accuracy. Our 70% threshold represents meaningful improvement (20 percentage points) that justifies tool usage over random choice or exhaustive benchmarking.

*Success Criteria for Phase 2B:*
- Primary: Spearman ρ > 0.7 across 20+ MDP configurations (p < 0.05)
- Falsification: ρ ≤ 0.5 (no better than random) triggers hypothesis rejection

**Secondary Predictions:**

**P2 (Constant Extraction Accuracy):**
Automated LLM extraction of proof constants will achieve ≥90% accuracy compared to manual expert extraction (measured on 10 regret bound papers).

*Measurement:*
- Expert manually extracts constants from 10 papers (Agrawal, Domingues, Guo, 7 others)
- GPT-4 extracts same constants via LaTeX processing
- Compare numeric values: |LLM_value - Expert_value| / Expert_value < 0.1 for 90% of constants

**P3 (Compute Cost Reduction):**
Using RegretLens for algorithm selection reduces total compute cost by ≥50% compared to exhaustive empirical comparison (simulated researcher workflow).

*Measurement:*
- Baseline: Exhaustive benchmarking of 5 algorithms × 20 MDP configs × 50 episodes = 5,000 runs
- RegretLens: Theoretical prediction (negligible cost) + validation of top-2 algorithms × 20 configs × 50 episodes = 2,000 runs
- Compute reduction: (5,000 - 2,000) / 5,000 = 60% savings

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any of the following occur:

1. **Primary Failure**: Algorithm selection accuracy ≤ 50% (Spearman ρ ≤ 0.5)
   - Indicates theoretical rankings have no predictive power beyond random chance
   - Statistical test: p > 0.05 (no significant correlation)

2. **Mechanism Failure**: Constant extraction accuracy < 70% OR Instance-specific predictions non-computable for >30% of algorithms
   - Indicates core mechanism (Step 1-2) broken - tool cannot produce reliable predictions

3. **Tightness Failure**: Theoretical bounds >100x loose compared to empirical regret across all algorithms
   - Indicates worst-case theory completely disconnected from average-case practice
   - Even if rankings match, 100x looseness makes predictions uninformative

### 1.7 SOTA Baseline

**Not applicable** - RegretLens does not target performance improvement over SOTA methods. It is a theory-practice translation tool (meta-research), not a new RL algorithm.

**Comparison mode:** Absolute performance validation against random baseline (50% selection accuracy).

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Primary metric: Spearman rank correlation
- Target effect size: ρ = 0.7 (strong positive correlation)
- Statistical power: 0.8
- Significance level: α = 0.05 (one-tailed test)
- Required MDP configurations: n ≥ 20

**Test Specification:**
- Method: Spearman rank correlation + permutation test
- Null hypothesis: ρ = 0 (no correlation between theoretical and empirical rankings)
- Alternative hypothesis: ρ > 0.5 (meaningful positive correlation)
- Report format: ρ value, p-value, 95% confidence interval, scatter plot (theoretical rank vs empirical rank)

**Robustness Checks:**
- Sensitivity analysis: Vary MDP parameters by ±20% to test ranking stability
- Ablation: Compare with asymptotic-only rankings (no concrete constants) to isolate contribution of instance-specific prediction
- Cross-validation: Hold out 5 MDPs for testing after training on 15 MDPs

---

## 2. Contribution Summary

**Theoretical Contributions:**
1. **Framework for systematic extraction and comparison of concrete regret bounds** - Provides template for converting asymptotic theory (Õ notation) into computable functions with explicit constants, enabling quantitative comparison beyond "both are Õ(√T)"
2. **Taxonomy of MDP parameter impact on algorithm selection** - Characterizes when S vs A vs H dominates algorithm performance (e.g., Thompson sampling better for large S, UCB-VI better for large A)
3. **Crossover regime characterization** - Identifies parameter ranges where one algorithm theoretically dominates another (e.g., TS optimal for S<100, UCB optimal for S≥100)

**Methodological Contributions:**
1. **Reproducible pipeline for proof-to-tool translation** - Demonstrates template for converting theoretical results into computational tools: LaTeX parsing → symbolic computation → numeric evaluation → empirical validation
2. **Instance-specific performance prediction methodology** - Shows how to move from asymptotic bounds to concrete predictions for specific problem sizes, applicable beyond RL to any domain with complexity theory
3. **Theory-practice validation framework** - Establishes pattern for comparing worst-case theoretical predictions to average-case empirical performance via tightness scoring

**Practical Contributions:**
1. **Immediate value for practitioners** - Answers "Which algorithm should I use for my MDP?" with theoretically-principled guidance, reducing compute cost by ~50-60%
2. **Educational resource** - Complements dennybritz/RL and OpenAI Spinning Up by showing how concrete constants affect real performance (not just asymptotic intuition)
3. **Living theory database** - Creates community-curated resource continuously updated as new regret bound papers published (open-source contribution model)

---

## 3. Key Related Work

**Builds directly on (theoretical foundations):**

1. **Agrawal & Jia (2022) - "Optimistic posterior sampling for RL: worst-case regret bounds"**
   - 229 citations
   - Semantic Scholar ID: b799c782f168b0a02ebab9e50ff38ded1bc79aee
   - Key contribution: Near-optimal regret bound Õ(√DSAT) for Thompson sampling in communicating MDPs
   - RegretLens usage: Extracts constants from proof appendix to compute concrete TS regret predictions

2. **Domingues et al. (2020) - "Episodic RL in Finite MDPs: Minimax Lower Bounds Revisited"**
   - 108 citations
   - Semantic Scholar ID: 0b0c82e33d3328246b6adc3ef2b55be9b606a0cd
   - Key contribution: Minimax lower bound Ω(H³SA/ε²) on sample complexity for PAC algorithms
   - RegretLens usage: Provides baseline for comparing algorithm bounds; shows parameter-dependent performance regimes

3. **Guo et al. (2021) - "Theoretical Guarantees of Fictitious Discount Algorithms"**
   - 10 citations
   - Semantic Scholar ID: 24fda3cbf8b776aea69ef4f2d5ef11f92d3d4011
   - Key contribution: First theoretical guarantee for fictitious discount methods widely used in practice
   - RegretLens usage: Demonstrates pattern of theory following practice; adds fictitious discount to tool's algorithm database

**Integrates with (implementation resources):**

1. **dennybritz/reinforcement-learning** (21,800 stars)
   - Educational implementations accompanying Sutton & Barto textbook
   - RegretLens integration: Provides theoretical selection guidance before practitioners implement algorithms

2. **OpenRL Benchmark** (benchmark.cleanrl.dev)
   - Open standardized evaluation platform for RL algorithms
   - RegretLens integration: Empirical validation layer - compares theoretical predictions to benchmark performance

3. **OpenAI Spinning Up** (11,500 stars)
   - Structured learning resource for deep RL
   - RegretLens integration: Complements educational material by showing concrete impact of theoretical constants on performance

**Fills gap between:**
- Theoretical papers (provide bounds) ← **RegretLens** → Practical implementations (show algorithms work)
- Currently: Practitioners read theory → implement algorithms → run benchmarks (expensive, time-consuming)
- With tool: Practitioners get theoretical prediction → validate top candidates empirically (faster, more principled)

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence - Constant Extractability):**
"Theoretical RL papers contain extractable concrete constants with ≥90% accuracy via automated parsing"
- Validation: Manual expert extraction vs LLM extraction on 10 papers (Agrawal, Domingues, Guo + 7 others)
- Success metric: |LLM - Expert| / Expert < 0.1 for 90% of constants

**SH2 (Mechanism - Prediction Accuracy):**
"Instance-specific regret predictions from extracted constants correlate with empirical performance rankings (ρ > 0.7)"
- Validation: Compare RegretLens theoretical ranking to OpenRL Benchmark empirical ranking on 20 MDP configurations
- Success metric: Spearman ρ > 0.7 (p < 0.05)

**SH3 (Comparison - Value vs Baseline):**
"RegretLens reduces algorithm selection compute cost by ≥50% compared to exhaustive benchmarking"
- Validation: Simulate researcher workflow with/without tool on new MDP problems
- Success metric: (Baseline runs - Tool runs) / Baseline runs ≥ 0.5

### Readiness Checklist

- ✅ **Core statement**: Precise "If X, then Y because Z" formulation with condition
- ✅ **Variables**: All 5 variables operationalized with measurement methods
- ✅ **Causal mechanism**: 4-step chain with evidence for each link (dynamic based on complexity)
- ✅ **Assumptions**: 5 assumptions identified with consequences if violated
- ✅ **Scope**: Clear boundaries (tabular RL, formal bounds, S ∈ [10,1000], etc.)
- ✅ **Predictions**: 3 testable predictions with quantitative thresholds (70%, 90%, 50%)
- ✅ **Falsification**: Clear rejection criteria (ρ ≤ 0.5, accuracy < 70%, looseness >100x)
- ✅ **Statistical design**: Sample size (n≥20), tests (Spearman + permutation), power (0.8)
- ✅ **Evidence**: 3 high-citation papers (Agrawal 229, Domingues 108, Guo 10) + OpenRL Benchmark
- ✅ **Contributions**: Theoretical, methodological, and practical contributions specified
- ✅ **Related work**: 6 key sources mapped (3 Scholar + 3 Exa)

### Open Questions for Phase 2B

1. **Constant extraction methodology details:**
   - How to handle multi-parameter constants (e.g., C depends on S, A)? → Phase 2B: Define parametric constant representation
   - How to resolve ambiguity when multiple constants possible? → Phase 2B: Conservative vs optimistic constant selection strategy

2. **Tightness scoring definition:**
   - What is "useful" tightness? (2x loose = good, 10x = acceptable, 100x = useless?) → Phase 2B: Define tightness categories with thresholds
   - How to aggregate tightness across environments? (median, geometric mean, worst-case?) → Phase 2B: Specify aggregation methodology

3. **MVP algorithm selection:**
   - Which 5-10 algorithms to include in MVP? (prioritize by citation count? domain coverage?) → Phase 2B: Algorithm prioritization criteria
   - How to handle algorithms with multiple variants (e.g., UCB-VI vs UCB-H vs UCB-Hoeffding)? → Phase 2B: Variant selection strategy

4. **Empirical validation scope:**
   - Which 20 MDP configurations provide best coverage? (grid search vs representative sampling?) → Phase 2B: MDP configuration selection methodology
   - How to ensure OpenRL Benchmark environments are "representative" of practitioner use cases? → Phase 2B: Representativeness validation

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-08*
