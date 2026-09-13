# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-MCV-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under conditions where an AI system generates scientific hypotheses, if a Metacognitive Constraint Validation (MCV) framework validates claims against a multi-level hierarchy of constraints (L1: physical laws, L2: domain theories, L3: empirical patterns, L4: logical consistency) with uncertainty estimation, then hallucinated hypotheses will be detected with higher accuracy than fact-checking methods, because constraint validation captures semantic violations that statistical methods miss while preserving creative speculation that does not violate fundamental constraints.

**Alternative Hypothesis (H0):**
Constraint validation does not improve hallucination detection accuracy over statistical fact-checking methods (semantic entropy, self-consistency) for scientific hypotheses, and the creative/hallucination distinction cannot be reliably operationalized via constraint violation patterns.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Constraint Hierarchy Configuration | Independent | L1-L4 constraint modules with coverage depth (none, partial, full) | 4 levels × 3 depths = 12 configurations |
| Uncertainty Threshold | Independent | Metacognitive confidence cutoff for classification | 0.3 - 0.8 (optimal ~0.5) |
| Hallucination Detection Accuracy | Dependent | F1-score on labeled hypothesis-hallucination pairs | Target: >0.75 F1 |
| Creative Preservation Rate | Dependent | Proportion of valid creative hypotheses not flagged | Target: >0.85 |
| Epistemic Validity Correlation | Dependent | Pearson r between MCV confidence and expert ratings | Target: r > 0.65 |
| Base LLM Capability | Controlled | Fixed model (GPT-4 / Claude-3) across conditions | Single model per experiment |
| Domain Coverage | Controlled | Fixed scientific domain for evaluation | Biomedicine (initial) |

### 1.3 Causal Mechanism

**4-Step Causal Chain:**

```
[Scientific Hypothesis Input]
        ↓
Step 1: Claim Parsing → Atomic Assertions
        ↓
Step 2: Atomic Assertions → Constraint Satisfaction Scores (L1-L4)
        ↓
Step 3: Constraint Scores → Metacognitive Confidence (Uncertainty Aggregation)
        ↓
Step 4: Metacognitive Confidence → Classification (VALID / SPECULATIVE / HALLUCINATED)
        ↓
[Detection Output]
```

**Step Details:**

1. **Step 1 (Claim Parsing):** Hypothesis decomposed into atomic checkable assertions using structured claim extraction.

2. **Step 2 (Constraint Validation):** Each assertion validated against:
   - L1 (Physical): Conservation laws, thermodynamics, causality
   - L2 (Theoretical): Domain-specific theory modules (modular plugins)
   - L3 (Empirical): Mined patterns from scientific literature
   - L4 (Logical): Formal consistency, no contradictions

3. **Step 3 (Uncertainty Aggregation):** Per-level confidence scores aggregated into epistemic validity score using Bayesian belief combination.

4. **Step 4 (Classification):** Threshold-based classification:
   - VALID: No L1 violations, high confidence (>0.7)
   - SPECULATIVE: May challenge L2/L3 with uncertainty markers
   - HALLUCINATED: L1 violation OR logical contradiction OR low confidence (<0.3)

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | RefChecker (Hu et al.) | Claim-triplet extraction enables fine-grained verification | Strong |
| Step 2 → Step 3 | KnowHD/TruthHypo (Xiong et al., 2025) | Groundedness scoring effectively filters truthful hypotheses | Strong |
| Step 3 → Step 4 | BEWA (Wright, 2025) | Bayesian belief validation provides theoretical foundation | Medium |
| Step 4 → Outcome | Semantic Entropy (Farquhar et al., 2024) | Uncertainty-based classification achieves SOTA detection | Strong |

**Key Tension:**
- **Tension:** KnowHD validates against existing knowledge (fact-checking adjacent), while MCV validates against constraints (paradigm shift). TruthHypo benchmark may favor fact-checking.
- **Resolution:** Create HypoHal benchmark with synthetic hallucinations testing constraint violations vs factual inaccuracies.

### 1.4 Key Assumptions

1. **A1: Constraint Formalizability** - Physical laws (L1) and logical consistency (L4) can be formally encoded
   - **If Violated:** L1/L4 modules unreliable; fall back to L2/L3 only

2. **A2: Modular Domain Theories** - Domain theories (L2) can be modularized into checkable plugins
   - **If Violated:** L2 becomes bottleneck; prioritize high-coverage domains

3. **A3: Meaningful Creative/Hallucination Distinction** - Distinction operationalizable via constraint patterns
   - **If Violated:** Core hypothesis fails; creative preservation metric meaningless

4. **A4: Expert Annotation Reliability** - Experts can provide reliable ground truth labels
   - **If Violated:** Rely on synthetic evaluation more heavily

### 1.5 Scope & Boundaries

**Applies to:**
- Scientific hypotheses in natural sciences (physics, chemistry, biology, biomedicine)
- Claims decomposable into atomic assertions
- Domains with well-established L1-L2 constraints

**Does NOT apply to:**
- Purely mathematical conjectures (only L4 applicable)
- Social science hypotheses (softer constraints)
- Highly abstract philosophical claims

**Known Limitations:**
- L2 plugin development requires domain expertise
- Paradigm-shifting hypotheses may trigger false positives
- Coverage depends on L2 module availability

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Hallucination Detection Accuracy vs SOTA ~65% F1):**
MCV will achieve F1-score > 0.75 on scientific hypothesis hallucination detection.

*Measurement:*
- F1 > 75% with p < 0.05; Paired t-test, n ≥ 25 runs
- Dataset: TruthHypo benchmark + HypoHal extension

*Success/Falsification:*
- Primary: F1 > 75% (p < 0.05) → SUCCESS
- Falsification: F1 ≤ 57% → REJECT

**Secondary Predictions:**

**P2 (Creative Preservation):** >85% valid creative hypotheses preserved (vs <70% for fact-checking)

**P3 (Confidence Calibration):** MCV confidence correlates with expert ratings at r > 0.65

**Falsification Criteria:**
1. **Primary Failure:** F1 ≤ 57%
2. **Mechanism Failure:** L1-L4 ablation shows no incremental benefit
3. **Creative Failure:** Preservation rate <70%
4. **Calibration Failure:** Expert correlation r < 0.40

### 1.7 SOTA Baseline Benchmark Summary

| Method | Performance | Approach |
|--------|-------------|----------|
| Semantic Entropy | ~60-65% F1 | Statistical uncertainty |
| SelfCheckGPT | ~55-60% F1 | Self-consistency |
| RefChecker | ~70% F1 | Reference-based triplets |
| KnowHD | Groundedness | Knowledge-based |

**MCV Target:** >75% F1 (10+ point improvement)

### 1.8 Statistical Verification Design

**Sample Size:** n ≥ 25 runs (effect size d ~0.6)
**Test:** Paired t-test, α = 0.05 (one-tailed)
**Report:** Mean difference, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does constraint validation detect scientific hypothesis hallucinations with measurable accuracy (F1 > 0.75) under controlled conditions?"

- Maps to: Primary prediction P1
- Verification type: Empirical (benchmark evaluation)
- Critical: MUST PASS before mechanism testing

**SH2 (Mechanism):**
"Is the 4-step causal mechanism (parsing → constraints → uncertainty → classification) the actual driver of detection performance?"

- Will decompose into 4 sub-hypotheses:
  - H-M1: Claim parsing reliability
  - H-M2: Constraint satisfaction coverage (L1-L4 ablation)
  - H-M3: Uncertainty aggregation calibration
  - H-M4: Classification threshold stability
- Verification type: Ablation studies

**SH3 (Comparison):**
"Does MCV outperform existing baselines (SelfCheckGPT, semantic entropy, RefChecker, MetaQA) on scientific hypothesis evaluation?"

- Maps to: Secondary predictions P2, P3
- Verification type: Comparative empirical

**Total Sub-Hypotheses in Phase 2B:** 1 + 4 + 1 = **6 sub-hypotheses**

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-MCV-v1
- [x] Confidence level: 0.82
- [x] Alternative hypothesis (H0) defined
- [x] Variables operationalized with measurement methods
- [x] Causal mechanism with evidence (4 steps)
- [x] Causal chain length: N=4
- [x] Key tension identified with resolution
- [x] Assumptions list consequences if violated
- [x] 3 testable predictions (primary marked)
- [x] Falsification criteria defined (F1 ≤ 57%)
- [x] Baselines identified (4 methods)
- [x] SH1, SH2, SH3 starting points clear

### Open Questions

1. **Data Availability:** Extend TruthHypo to physics/chemistry or focus on biomedicine first?
2. **L2 Module Priority:** Which domain for initial L2 plugin development?
3. **Expert Annotation:** Minimum panel size? (Recommend 3-5 experts, Fleiss' kappa ≥ 0.6)

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
