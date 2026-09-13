# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-08
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-SpecGen-v1
**Confidence Level:** 0.80 (High)

**Main Hypothesis:**
Under conditions of closed-domain reasoning evaluation (math, logic, planning, CSP), if benchmarks are generated from formal specifications using CSP algorithms at evaluation time, then contamination will be eliminated (0% overlap with training data) and reasoning capability will be measured accurately (process-verification correlation ≥ 0.75 with human expert judgment) because specifications abstract away instance-level patterns that could be memorized during training, preventing both training-time and search-time contamination.

**Alternative Hypothesis (H0):**
There is no difference in contamination rates or measurement accuracy between specification-generated benchmarks and traditional static datasets; any observed differences are due to chance or confounding factors rather than the generation mechanism itself.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Specification complexity and diversity | Independent | Number of specification parameters (5-20), constraint types (3-10), and meta-generation variants applied (2-5 per specification) | Low: 5 params × 3 types × 2 variants; High: 20 params × 10 types × 5 variants |
| Contamination rate | Dependent | Percentage of benchmark instances that overlap with training data, measured via direct string matching (exact) and semantic similarity (cosine > 0.95) | Target: 0% (zero overlap by construction); Alert threshold: > 0.1% |
| Reasoning capability measurement accuracy | Dependent | Correlation between process-based verification scores and human expert judgment of reasoning quality (Spearman's ρ) | Target: ρ ≥ 0.75 (strong correlation); Minimum acceptable: ρ ≥ 0.60 |
| Task domain type | Controlled | Closed-domain categories: mathematical reasoning (MATH-500 style), logical inference (propositional/first-order), planning tasks (PDDL), constraint satisfaction problems (CSP) | Fixed: Test across all 4 domains for generalization |

### 1.3 Causal Mechanism

**Step 1:** Formal specifications → CSP-generated instances
- Specifications define task constraints (objectives, rules, validity conditions) using domain-specific languages (PDDL for planning, SMT-LIB for logic, custom DSLs for math/CSP)
- CSP solvers (Z3, PySAT, backtracking search) algorithmically generate instances satisfying these constraints
- Generated instances do not exist during training (temporal separation prevents training-time contamination)
- **Falsification point:** CSP solvers fail to generate valid/diverse instances from specifications

**Step 2:** CSP-generated instances → Meta-specification diversity
- Single specifications may leak abstraction-level patterns (e.g., always use quadratic equations)
- Meta-generation systematically varies specification parameters (problem size, constraint complexity), structural components (combine specification fragments), and employs cross-domain mixing
- Cryptographic RNG + algorithm rotation prevents distributional artifacts
- **Falsification point:** Meta-generation produces insufficient diversity or introduces systematic biases

**Step 3:** Meta-diverse generation → Contamination-free + accurate measurement
- Temporal separation (generation post-training) prevents instance-level contamination
- Meta-variation prevents abstraction-level contamination (no learnable patterns in specification distribution)
- Process verification (reasoning trace validation) distinguishes genuine reasoning from memorized patterns, going beyond outcome-only metrics
- Hybrid process+outcome scoring provides robust measurement
- **Falsification point:** Process verification fails to distinguish reasoning quality OR contamination occurs despite generation-time separation

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Wu et al. (2025, 51 cites) | RandomCalculation generates arbitrary-length problems POST-training achieving zero contamination; only accurate rewards yield improvements on clean benchmarks | Strong |
| Step1 → Step2 | Property-based testing (Reis et al. 2025) | QuickCheck paradigm (25+ years) reliably generates diverse test instances from specifications in software engineering | Strong |
| Step2 → Step3 | Han et al. (2025, 6 cites) | Search-time contamination affects ~3% queries via HuggingFace retrieval; ~15% accuracy drop when blocked, proving instance existence enables contamination | Strong |
| Step3 → Outcome | Liu et al. (2025, 1 cite) | Task perturbation (not input) reveals genuine generalization vs task-specific overfitting; dynamic evaluation framework distinguishes understanding from memorization | Medium |
| Process Verification | Wu et al. (2025) | Outcome-only metrics fail to detect contamination; process-level analysis needed to distinguish reasoning from pattern matching | Medium |

**Key Tension:**
**Tension:** Wu et al. (2025) demonstrates procedural generation prevents contamination in math domain (domain-specific success), but Liu et al. (2025) shows task-specific adaptations can mask overfitting (risk of specification-level adaptation).

**Resolution:** This hypothesis addresses the tension through meta-generation (Step 2): systematically varying specifications prevents models from adapting to specification-level patterns. The verification plan (Phase 2B) will test whether meta-generation sufficiently disrupts abstraction-level memorization by measuring: (1) contamination rate across specification variants, (2) performance stability under specification perturbation, (3) correlation between specification complexity and model performance (should be task-difficulty driven, not specification-pattern driven).

### 1.4 Key Assumptions

1. **CSP solvers can generate sufficiently diverse instances from specifications to prevent pattern memorization**
   - Evidence: Property-based testing literature (Reis et al. 2025) shows 25+ years of diverse test generation from specifications in software engineering (QuickCheck paradigm proven across millions of codebases)
   - Consequences if violated: Models could learn specification-level patterns even without seeing specific instances, reducing contamination prevention effectiveness. Mitigation: Meta-generation adds specification diversity layer.

2. **Process verification can distinguish genuine reasoning from memorized patterns**
   - Evidence: Wu et al. (2025) shows outcome-only metrics fail to detect contamination (random rewards work on contaminated benchmarks); Liu et al. (2025) demonstrates task perturbation reveals overfitting to superficial cues
   - Consequences if violated: Measurement accuracy suffers; contamination-free benchmarks provide unreliable signals. Mitigation: Hybrid process+outcome scoring, human correlation validation studies.

3. **Specifications won't leak reasoning shortcuts at abstraction level**
   - Evidence: RandomCalculation (Wu et al.) demonstrates procedural generation prevents training-time contamination at instance level, but requires careful design to avoid abstraction patterns
   - Consequences if violated: Models adapt to specification structures rather than solving tasks via genuine reasoning. Mitigation: Meta-generation systematically varies specification formats, cross-domain mixing disrupts single-paradigm adaptation.

4. **Closed-domain reasoning tasks have formalizable specifications**
   - Evidence: PDDL (planning), SMT-LIB (logic), constraint languages (CSP) are mature specification standards; mathematical reasoning has well-defined correctness criteria
   - Consequences if violated: Cannot generate valid instances, framework applicability collapses. Mitigation: Explicit scope limitation to closed-domain (math, logic, planning, CSP), excluding open-ended reasoning.

5. **Temporal separation (generation post-training) prevents training-time contamination**
   - Evidence: Archon PyTorch randomness documentation shows reproducibility requires deterministic generation; Wu et al. proves instances generated after training cannot contaminate by construction (set theory: empty intersection)
   - Consequences if violated: Fundamental contamination prevention mechanism fails. Mitigation: Rigorous timestamp verification, cryptographic proof of generation order.

### 1.5 Scope & Boundaries

**Where This Hypothesis Applies:**
- **Closed-domain reasoning tasks** with verifiable correctness: Mathematical reasoning (algebra, calculus, number theory), logical inference (propositional, first-order logic), planning tasks (STRIPS, PDDL), constraint satisfaction problems
- **Benchmarks with formal specifications**: Tasks that can be encoded as constraints, rules, and objectives in formal languages
- **Post-training evaluation scenarios**: Situations where benchmark generation occurs after model training completes
- **Contamination-critical contexts**: High-stakes evaluation where data leakage threatens validity (e.g., model comparison studies, capability assessment)

**Where This Hypothesis Does NOT Apply:**
- **Open-ended reasoning**: Creative writing, brainstorming, subjective judgment tasks (no formal correctness criteria)
- **Implicit knowledge tasks**: Commonsense reasoning, cultural knowledge, where specifications cannot capture tacit requirements
- **Training-time augmentation**: Using generated data during training (different use case, not contamination prevention)
- **Domains without mature specification languages**: Tasks lacking formalization frameworks

**Known Limitations:**
- Computational cost: CSP generation can be expensive for complex constraints (mitigation: batch caching, amortized evaluation)
- Specification bias: Human-designed specifications encode assumptions about "correct" reasoning (mitigation: meta-generation diversity, transparent methodology)
- Closed-domain restriction: Does not address contamination in open-ended LLM capabilities (complementary approaches needed)
- Process verification complexity: Defining "valid reasoning step" formally is challenging (mitigation: hybrid scoring with graceful degradation to outcome-only when process analysis fails)

### 1.6 Testable Predictions

**Primary Prediction:**
**P1 (Contamination Elimination - Zero Overlap Target)**:
Our specification-driven generation approach will achieve contamination rate = 0% (zero overlap with training data)

*Measurement*:
- Contamination rate = 0% measured via: (1) Direct string matching (exact n-gram overlap, n=8-50), (2) Semantic similarity (cosine distance > 0.95 threshold for near-duplicates), (3) Manual review of 100 random samples
- Comparison baseline: Static benchmarks (MATH-500, GSM8K) show 3-15% contamination (Wu et al. 2025, Han et al. 2025)
- Statistical requirement: p < 0.001 via binomial test (H0: contamination rate = 3%, H1: contamination rate = 0%)

*Basis*:
Domain standard for benchmark integrity in LLM evaluation. Wu et al. (2025) demonstrates RandomCalculation achieves 0% contamination via procedural generation for math domain. Our framework extends this to multi-domain with formal contamination prevention guarantee (temporal separation: generation post-training → empty set intersection).

*Success Criteria for Phase 2B*:
- Primary: Contamination rate = 0% across 1000+ generated instances per domain (4 domains)
- Falsification: Contamination rate > 0.1% triggers investigation; > 1% triggers hypothesis rejection

**Secondary Predictions:**
**P2 (Process Verification Accuracy - Correlation with Human Judgment)**:
Process-based verification scores will correlate ρ ≥ 0.75 (Spearman) with human expert judgment of reasoning quality

*Measurement*:
- 50 reasoning traces per domain (200 total), scored by 3 expert judges (inter-rater reliability κ ≥ 0.70)
- Process verification automated scoring (0-1 scale): logical consistency, completeness, efficiency, explainability
- Spearman correlation between automated scores and average human scores
- Target: ρ ≥ 0.75 (strong correlation), Minimum acceptable: ρ ≥ 0.60

*Basis*:
Domain standard for automated scoring validation (human correlation benchmark). This validates Assumption #2 (process verification distinguishes reasoning from memorization).

**P3 (Multi-Domain Generalization - Framework Robustness)**:
The framework will achieve target performance across all 4 closed-domain types with coefficient of variation ≤ 20%

*Measurement*:
- Measure contamination rate and process-verification correlation for each domain (math, logic, planning, CSP)
- Calculate CV = (std_dev / mean) × 100% across domains
- Target: CV ≤ 20% (consistent performance), Alert: CV > 30% (domain-specific adaptation concerns)

*Basis*:
Tests generalization of specification-driven paradigm beyond math-only (Wu et al. RandomCalculation limitation). Validates hypothesis applies to closed-domain reasoning broadly, not just specific task types.

**Falsification Criteria:**
The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure (Contamination Prevention)**: Contamination rate > 1%
   - Indicates temporal separation or abstraction elevation failed
   - >1% threshold = 10x worse than target, statistically significant contamination detected
   - Action: Investigate generation process, check for specification leakage or instance caching bugs

2. **Mechanism Failure (Process Verification Invalidity)**: Process-verification correlation ρ < 0.50
   - Indicates process verification cannot distinguish reasoning quality (Assumption #2 violated)
   - ρ < 0.50 = weak/no correlation, automated scoring unreliable
   - Action: Fallback to outcome-only metrics, revise process verification rules

3. **Generalization Failure (Domain-Specific Collapse)**: Any domain achieves contamination > 5% OR correlation < 0.40
   - Indicates framework does not generalize across closed-domain types
   - Single-domain failure suggests specification language inadequacy or domain-specific challenges
   - Action: Scope reduction to validated domains, investigate failed domain characteristics

4. **Baseline Failure (Worse than Static)**: Performance measurement variance > 2x static benchmarks
   - Indicates procedural generation introduces unacceptable noise
   - Defeats purpose if generated benchmarks less reliable than static alternatives
   - Action: Improve generation stability, validate against known-correct solutions

### 1.7 SOTA Baseline (Optional - If SOTA Comparison Mode)

*Not applicable - Absolute performance validation mode (contamination prevention, not performance comparison)*

### 1.8 Statistical Verification Design

**Sample Size Requirements:**
- Contamination measurement: n ≥ 1000 instances per domain (4000 total) for 0.1% detection sensitivity
- Process verification validation: n = 50 traces per domain (200 total) for correlation analysis (power = 0.80, α = 0.05, medium effect size)
- Domain generalization: 4 domains × 1000 instances = 4000 instances minimum

**Statistical Tests:**
1. **Contamination Rate Test**: Binomial test, H0: rate = 3% (baseline from Wu et al.), H1: rate = 0%, α = 0.001 (conservative for strong claim)
2. **Process Verification Validation**: Spearman correlation, target ρ ≥ 0.75, minimum ρ ≥ 0.60, α = 0.05
3. **Multi-Domain Generalization**: Coefficient of variation test, target CV ≤ 20%, alert CV > 30%
4. **Inter-Rater Reliability**: Fleiss' κ ≥ 0.70 for human expert agreement (prerequisite for correlation validation)

**Report Format:**
- Contamination: Rate (%), 99.9% CI, binomial test p-value, manual review confirmation
- Process Verification: Spearman ρ, 95% CI, p-value, scatter plot of automated vs human scores
- Generalization: Per-domain metrics table, CV calculation, domain-specific analysis
- All metrics: Mean ± Std Dev, ranges, sample sizes, significance levels

**Experimental Controls:**
- Fixed random seeds for CSP generation (reproducibility)
- Consistent specification complexity across domains (controlled variable)
- Blinded human evaluation (raters unaware of generation method)
- Stratified sampling across difficulty levels within domains


## 4. Phase 2B Readiness

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
Does specification-driven procedural generation achieve zero contamination (0% overlap with training data) in closed-domain reasoning benchmarks?

*Maps to:* Primary prediction (P1 - Contamination Elimination)
*Verification type:* Empirical (direct contamination measurement via string matching + semantic similarity + manual review)
*Critical:* MUST PASS for Phase 2B to proceed - if contamination > 1%, fundamental premise fails

**SH2 (Mechanism):**
Is the 3-step causal mechanism (specifications → CSP generation → meta-diversity → contamination-free measurement) the actual cause of contamination prevention and accurate reasoning measurement?

*Maps to:* Causal mechanism (N=3 steps)
*Verification type:* Causal analysis (ablation studies, link-by-link validation)
*Critical:* Determines explanatory power
*Note:* Phase 2B will decompose this into 3 sub-hypotheses:
- **H-M1:** Formal specifications → CSP-generated instances (tests CSP solver validity/diversity)
- **H-M2:** CSP-generated instances → Meta-specification diversity (tests meta-generation effectiveness)
- **H-M3:** Meta-diverse generation → Contamination-free + accurate measurement (tests prevention mechanism + process verification)

**SH3 (Comparison):**
Does SpecGen outperform existing contamination prevention approaches (static benchmarks, domain-specific procedural generation) on contamination rate and measurement reliability?

*Maps to:* Secondary predictions (P2 - Process verification accuracy, P3 - Multi-domain generalization)
*Verification type:* Comparative empirical (SpecGen vs RandomCalculation vs static MATH-500/GSM8K)
*Critical:* Determines practical value - if not better than RandomCalculation, incremental contribution questionable

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned (H-SpecGen-v1)
- [x] Confidence level specified (0.80)
- [x] Alternative hypothesis (H0) defined (no difference from static benchmarks)
- [x] All variables have operationalization from evidence (4 variables with measurement methods)
- [x] Causal mechanism has evidence at each step (3 steps, evidence_for_links table with 5 links)
- [x] Causal chain length (N) determined and stored (N=3)
- [x] Key tension identified and resolution proposed (Wu vs Liu tension, meta-generation resolution)
- [x] Key assumptions list consequences if violated (5 assumptions with consequences + mitigations)
- [x] At least 2 testable predictions exist (P1 primary + P2, P3 secondary)
- [x] Falsification criteria are defined (4 criteria with specific thresholds)
- [x] Baselines are identified for comparison (static benchmarks, RandomCalculation)
- [x] SH1, SH2, SH3 are clear starting points (all 3 defined above)

**Status:** ✅ ALL REQUIREMENTS MET - Ready for Phase 2B

### Open Questions

1. **Resource Requirements:** What are the computational costs of CSP generation at scale (1000+ instances per domain)?
   - GPU/CPU requirements for Z3/PySAT solving?
   - Batch generation time estimates?
   - Caching strategy feasibility (storage requirements)?

2. **Specification Language Design:** How will specification languages be designed for each domain (math, logic, planning, CSP)?
   - Existing standards sufficient (PDDL, SMT-LIB) or custom DSLs needed?
   - Complexity calibration: how to ensure generated instances span difficulty range?
   - Validation: how to verify generated instances are correct/valid?

3. **Process Verification Implementation:** What are the concrete rules for reasoning trace validation?
   - How to define "logical consistency," "completeness," "efficiency" formally?
   - Inter-rater reliability targets for human correlation studies (n=50 traces × 3 raters = 150 judgments)?
   - Fallback strategy if process verification correlation < 0.60?

4. **Priority Verification Order:** Which sub-hypothesis should be validated first in Phase 2B?
   - Recommend: H-M1 first (CSP generation validity), then SH1 (contamination measurement), then H-M2/H-M3 (mechanism verification)
   - Rationale: If CSP cannot generate valid instances, entire framework collapses (gating dependency)

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-08*
