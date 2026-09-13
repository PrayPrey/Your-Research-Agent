# Phase 2A: Refinement Summary

## Metadata

- **Generated at**: 2026-04-22T00:26:17Z
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: Gap-1
- **Gap Title**: Method-Benchmark Interaction Characterization
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 12

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 12

**Convergence Reason**: All convergence criteria met - specific hypothesis, clear mechanism, testable predictions, novelty articulated, feasibility established, objections addressed

### Key Insights

**Dr. Nova's Breakthrough (Exchange 1, 7)**: Reframed the research question from "which method wins" to "what mechanisms explain performance when." Introduced the uncertainty fingerprint concept—each benchmark has a characteristic multi-method signature revealing error type. Transformed Prof. Rex's vulnerabilities into testable sub-hypotheses, shifting from defensive to investigative stance.

**Prof. Vera's Rigor Framework (Exchange 2, 8)**: Formalized three independent sub-hypotheses (H-MECHANISM, H-ERROR-TYPE, H-CALIBRATION) with quantitative success criteria and explicit falsification conditions. Designed ablation study comparing semantic entropy vs ensemble baseline to isolate clustering contribution from sampling effect.

**Dr. Sage's Impact Analysis (Exchange 3, 10)**: Articulated contribution as decision guidance not performance improvement. Even negative results are valuable—if methods perform identically, that recommends using cheapest option (token variance). Publishable regardless of outcome direction.

**Prof. Pax's Feasibility Validation (Exchange 4, 9)**: Confirmed pilot study is computationally tractable (200 examples, 6,600 forward passes, ~4 hours on single GPU). All methods have published implementations. Avoids previous h-e1 failure modes through output-based methods, adequate model accuracy (Mistral-7B >50%), and progressive validation.

**Dr. Ally's Synthesis (Exchange 5, 11)**: Consolidated consensus hypothesis with staged success criteria (minimum 1/3 predictions = publishable, strong 2/3 = significant, complete 3/3 = major contribution). Addresses all four critical concerns: rigor, impact, feasibility, novelty.

**Prof. Rex's Stress-Testing (Exchange 6, 12)**: Identified three critical vulnerabilities requiring mitigation: objective error-type partitioning (use model's verbalized confidence), clustering algorithm sensitivity (test multiple configurations), sample size optimization (K-sensitivity analysis). With mitigations, hypothesis is robust.

### Breakthrough Moments

1. **Exchange 7 (Dr. Nova)**: Transformed vulnerabilities into research questions - "What if semantic entropy's advantage comes from multiple looks not clustering?" became testable H-MECHANISM hypothesis with ablation design.

2. **Exchange 8 (Prof. Vera)**: Formalized independent sub-hypotheses with separate falsification criteria, enabling partial success (any one prediction confirmed = publishable finding).

3. **Exchange 11 (Dr. Ally)**: Synthesized consensus with explicit null hypothesis and minimum/strong/complete success tiers, ensuring publishability regardless of outcome direction.

---

## Final Hypothesis

### Title

Mechanistic Decomposition of Uncertainty Method Performance Across Error Types

### Hypothesis ID

H-UncertaintyMechanisms-v1

### Core Claim

Under systematic empirical evaluation on factual QA benchmarks (NaturalQuestions, TruthfulQA), if we compare four uncertainty estimation methods (semantic entropy, self-consistency, token variance, verbalized confidence) with matched sample sizes and controlled experimental conditions, then method performance rankings will differ significantly across error types (knowledge gaps vs confident misconceptions), because each method captures a distinct uncertainty dimension (semantic diversity, sampling agreement, distributional sharpness, introspective calibration) that responds differently to different error signatures.

### Null Hypothesis (H0)

There is no significant difference in uncertainty method performance rankings across error types. All methods measure the same underlying uncertainty signal with equivalent effectiveness, and observed performance differences are solely attributable to computational budget (number of samples) rather than method-specific mechanisms.

### Mechanism

**Three-Step Causal Chain:**

1. **Different methods probe orthogonal dimensions**: Semantic entropy measures diversity of meaning through semantic clustering, self-consistency measures sampling agreement, token variance measures distributional sharpness, verbalized confidence measures introspective calibration.

2. **Error types generate distinct signatures**: Knowledge gaps produce high semantic diversity (model generates varied wrong answers) and low sampling agreement. Confident misconceptions produce low semantic diversity (model consistently generates same wrong answer) and high sampling agreement on incorrect answer.

3. **Method-error matching determines effectiveness**: Semantic entropy excels when semantic diversity is high (knowledge gaps), fails when diversity is low (confident misconceptions). Self-consistency shows opposite pattern. Token variance provides stable baseline. Verbalized confidence depends on metacognitive training signal presence.

**Key Tension**: Whether semantic clustering adds value beyond multiple sampling (addressed through ablation study comparing semantic entropy vs ensemble baseline at matched K=10).

---

## Predictions

### P1: Mechanism Validation (Clustering Value)

**Statement**: Semantic entropy (K=10, with clustering) outperforms ensemble baseline (K=10, majority vote, no clustering) by ≥0.07 AUROC on knowledge-gap errors (NaturalQuestions unanswerable subset).

**Test Method**: Ablation study comparing semantic entropy vs ensemble baseline on same 100 NaturalQuestions examples, both using K=10 samples, measuring AUROC for error detection.

**Success Criterion**: AUROC_semantic - AUROC_ensemble ≥ 0.07, with semantic entropy achieving absolute AUROC ≥ 0.70

**Falsification**: If AUROC difference < 0.03, semantic clustering adds no value beyond multiple sampling, H-MECHANISM is FALSE

### P2: Error-Type Specificity

**Statement**: Method performance rankings differ significantly across error types: on knowledge gaps (NaturalQuestions), semantic entropy > self-consistency > token variance; on confident misconceptions (TruthfulQA), token variance ≈ semantic entropy > self-consistency.

**Test Method**: Measure AUROC for all methods on both error types separately, compute Spearman rank correlation between method rankings across error types.

**Success Criterion**: Rank correlation < 0.7 between error types. Self-consistency AUROC < 0.55 on TruthfulQA but ≥ 0.65 on NaturalQuestions.

**Falsification**: If rank correlation ≥ 0.9, methods measure same general uncertainty without error-type specificity, H-ERROR-TYPE is FALSE

### P3: Calibration Training Sensitivity

**Statement**: Verbalized confidence achieves better calibration (ECE < 0.15) on NaturalQuestions (which has metacognitive training signals like 'unanswerable' category) than on TruthfulQA (ECE > 0.25, no metacognitive signals).

**Test Method**: Measure Expected Calibration Error for verbalized confidence method on both benchmarks separately.

**Success Criterion**: ECE_NaturalQuestions < 0.15 AND ECE_TruthfulQA > 0.25, with difference ≥ 0.10

**Falsification**: If ECE difference < 0.05, calibration is independent of metacognitive training signals, H-CALIBRATION is FALSE

---

## Novelty

### Key Innovation

Mechanistic decomposition approach transforming method comparison from "which wins" to "what mechanisms explain performance when." Introduces uncertainty fingerprinting: each benchmark has characteristic multi-method signature revealing error type.

### Differentiation from Prior Work

**vs Kuhn et al. 2023 (Semantic Entropy)**: Systematic comparison across multiple benchmarks and error types, plus ablation isolating clustering vs sampling contribution. Original work validated semantic entropy on single benchmark (NLG tasks).

**vs Wang et al. 2022 (Self-Consistency)**: Tests self-consistency on factual QA and identifies failure mode (confident misconceptions). Provides error-type specificity analysis. Original work focused on reasoning tasks.

**vs Kadavath et al. 2022 (Verbalized Confidence)**: Connects calibration quality to presence of metacognitive training signals, tests across benchmarks with/without such signals. Original work showed general calibration ability.

**vs Previous h-e1 Attempt**: Output-based methods (not architecture-specific internal representations), uses established baselines (not novel metric), progressive validation (not difficult dataset upfront), model-agnostic (not model-dependent).

---

## Experimental Design

### Datasets

- **NaturalQuestions**: 100 examples (knowledge gaps with 'unanswerable' category)
- **TruthfulQA**: 100 examples (confident misconceptions - memorized falsehoods)

### Model

**Mistral-7B-v0.1**: Open-source decoder-only transformer, 7B parameters, achieves >50% accuracy on factual QA (avoids h-e1 failure where GPT-2 had 0.9% on TruthfulQA)

### Methods

1. **Token Probability Variance (K=1)**: Baseline, single forward pass
2. **Ensemble Baseline (K=10)**: Majority vote, no semantic clustering - isolates sampling effect
3. **Semantic Entropy (K=10)**: Semantic clustering + entropy calculation
4. **Self-Consistency (K=10)**: Agreement fraction for most common answer
5. **Verbalized Confidence (K=2)**: Prompt-based confidence elicitation

### Controls

- Same model checkpoint across all methods
- Same base prompt (except verbalized confidence elicitation)
- Same temperature T=0.7 for sampling methods
- Matched sample size K=10 for fair comparison (except baselines)

### Metrics

- **AUROC**: Discrimination metric, range [0,1], measures ability to separate correct from incorrect
- **ECE**: Calibration metric, range [0,1], lower is better, measures confidence-accuracy alignment

### Computational Cost

**Pilot Study**: 200 examples × average 6.6 forward passes per example = ~1,320 total forward passes for token variance + verbalized confidence, ~4,000 for sampling methods = ~6,600 total forward passes

**Estimated Time**: ~4 hours on single A100 GPU for Mistral-7B

---

## Limitations

### Scope Boundaries

- **Single model in pilot**: Mistral-7B only, generalization requires Phase 2 scaling to other architectures
- **Error-type partitioning**: Relies on model's verbalized confidence, which may itself be miscalibrated
- **Clustering sensitivity**: Semantic entropy results depend on implementation (embedding model, algorithm, threshold)
- **Fixed sample size**: K=10 may not be optimal for all methods, requires sensitivity analysis
- **Benchmark specificity**: TruthfulQA focuses on memorized misconceptions, may not generalize to all factual errors

### Implementation Risks & Mitigations

1. **Error-type partitioning**: Use objective criterion based on model's verbalized confidence (>80% = confident, <50% = uncertain)
2. **Clustering robustness**: Test 2-3 clustering configurations (different embedding models, similarity thresholds)
3. **Sample size sensitivity**: Include K-sensitivity analysis across {5, 10, 20}

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 personas reached consensus through 12 exchanges |
| **Novelty** | STRONG (Dr. Nova) - Mechanistic decomposition creates genuine understanding |
| **Falsifiability** | STRONG (Prof. Vera) - Three independent sub-hypotheses with quantitative criteria |
| **Significance** | STRONG (Dr. Sage) - Decision framework for practitioners, publishable regardless of outcome |
| **Feasibility** | STRONG (Prof. Pax) - Pilot 4 hours, published implementations, existing benchmarks |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None (all addressed through mitigations) |

### Success Criteria (Staged)

- **Minimum Success**: 1/3 predictions confirmed → Publishable finding
- **Strong Success**: 2/3 predictions confirmed → Significant contribution
- **Complete Success**: 3/3 predictions confirmed → Major contribution with decision framework

---

## Phase 2B Readiness

**Status**: READY

**What Must Exist (SH1-Existence)**:
- Four established uncertainty methods implemented (semantic entropy, self-consistency, token variance, verbalized confidence)
- Two benchmarks with sufficient correct/incorrect examples for AUROC calculation
- Model achieving >50% accuracy on at least one benchmark

**Core Mechanism to Test (SH2-Mechanism)**:
Different uncertainty methods capture orthogonal dimensions creating distinct performance patterns across error types. Ablation isolates clustering contribution from sampling effect.

**Comparison Strategy (SH3)**:
Within-study comparisons (not Phase 5 baseline repo):
1. Semantic entropy vs ensemble baseline (ablation)
2. All methods vs token variance baseline
3. Method rankings across error types

**Open Questions for Phase 2B**:
- Optimal sample size K for each method? (K-sensitivity needed)
- Clustering algorithm sensitivity? (robustness check needed)
- Objective error-type partitioning? (use model's confidence scores)
- Generalization beyond Mistral-7B? (Phase 2 scaling question)

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
*Hypothesis ID: H-UncertaintyMechanisms-v1*
*Ready for Phase 2B: Research Planning*
