# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-StyleToM-v1
**Confidence Level:** 0.86

**Main Hypothesis:**
Under conditions where developer coding history (50-100 files) is available, if a dual-adapter architecture integrating LoRA-based style representation learning with retrieval-augmented theory-of-mind intent inference is applied to code generation, then developer satisfaction will increase by >20% and code acceptance rate will improve significantly compared to single-dimension approaches, because style and intent represent orthogonal personalization dimensions that can be captured through explicit/implicit learning and persistent memory respectively.

**Alternative Hypothesis (H0):**
There is no significant difference in developer satisfaction or code acceptance rate between the dual-adapter StyleToM architecture and single-dimension approaches (style-only or intent-only), indicating that the integration of style and intent personalization does not provide additive or synergistic benefits.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Style Adapter | Independent | LoRA-based dual representation learning (explicit syntax patterns + implicit semantic patterns via contrastive learning) trained on developer code history (50-100 files) | Binary: enabled/disabled; LoRA rank: 8-64 |
| ToM Intent Module | Independent | Lightweight partner agent with retrieval-augmented persistent memory inferring goals, constraints, preferences from instructions and interaction history | Binary: enabled/disabled; Memory size: 10-100 interactions |
| Developer Satisfaction | Dependent | Likert scale 1-5 rating from developer surveys, measured pre/post intervention | 1.0-5.0; Target: >20% improvement |
| Code Acceptance Rate | Dependent | Percentage of generated code suggestions accepted without major modification | 0-100%; Baseline ~40%, Target >55% |
| Style Similarity Score | Dependent | Automated metric comparing generated code patterns to developer's historical style (naming conventions, formatting, design patterns) | 0.0-1.0; Target: >0.75 |
| Base LLM | Controlled | CodeLlama-34B with frozen weights | Fixed |
| Task Complexity | Controlled | SWE-bench Verified subset (medium difficulty tasks) | Fixed subset |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
Step 1: Style Adapter captures developer patterns
    ↓
Step 2: ToM Module infers current intent + Style alignment
    ↓
Step 3: Combined personalization → Improved satisfaction/acceptance
    ↓
Outcome: >20% satisfaction increase, higher acceptance rate
```

**Step 1 → Step 2:** Style Adapter captures explicit syntax patterns (naming, formatting conventions) AND implicit semantic patterns (design preferences, code organization) from developer code history using LoRA-based dual representation learning with contrastive learning.

**Step 2 → Step 3:** Style-aligned suggestions are combined with ToM Intent Module outputs, which infers current developer goals, constraints, and preferences from natural language instructions and interaction history using retrieval-augmented persistent memory.

**Step 3 → Outcome:** Intent-aligned personalized code that matches both style AND intent leads to increased developer satisfaction (perceived fit with preferences) and higher code acceptance rate (reduced modification needed).

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | MPCoder (Dai et al., ACL 2024) | Explicit+implicit style learning successfully differentiates user coding patterns | Strong |
| Step2 → Step3 | TOM-SWE (Zhou et al., 2025) | ToM agent achieves 59.7% vs 18.1% on stateful SWE-bench; 86% useful in developer study | Strong |
| Step3 → Outcome | IBM watsonx Study (Weisz et al., 2024) | 669 developers show heterogeneous needs; personalization addresses trust calibration gap | Medium |

**Key Tension:**
TOM-SWE demonstrates that intent modeling alone provides 3x improvement, while MPCoder shows style learning improves personalization. The key tension is whether combining both provides additive benefits or introduces interference. Resolution: The ablation study design (Style-only vs ToM-only vs StyleToM) will quantify the marginal contribution of each component and test for interaction effects.

### 1.4 Key Assumptions

1. **Style Learnability:** Developer coding style can be captured from 50-100 files of code history with sufficient signal for meaningful personalization.
   - *Evidence:* MPCoder successfully trained style adapters on similar data sizes
   - *If violated:* Style Adapter fails to differentiate users; personalization reduces to ToM-only approach

2. **Intent Inferability:** Intent can be reliably inferred from natural language instructions combined with interaction history using ToM modeling.
   - *Evidence:* TOM-SWE achieved 86% usefulness rating from professional developers
   - *If violated:* ToM Module provides incorrect/unhelpful suggestions; trust calibration fails

3. **Dimension Separability:** Style and intent are separable dimensions that can be modeled independently without significant interference.
   - *Evidence:* No prior work has attempted integration; theoretical orthogonality assumed
   - *If violated:* Modules may capture overlapping signal; diminishing returns from combination

4. **LoRA Efficiency:** LoRA adapters provide sufficient expressiveness for style capture while maintaining inference efficiency (<30% latency overhead).
   - *Evidence:* LoRA widely validated for efficient fine-tuning in NLP/code tasks
   - *If violated:* Deployment impractical; may need alternative adapter architecture

### 1.5 Scope & Boundaries

**Where Hypothesis Applies:**
- Code generation tasks with available developer history (minimum 50 files)
- Developers with consistent coding patterns across their codebase
- Tasks where personalization is valued (enterprise code assistants, IDE plugins)
- Languages with clear style conventions (Python, Java, TypeScript)

**Where Hypothesis Does NOT Apply:**
- Anonymous or new developers without code history (cold-start problem)
- One-off code generation tasks where personalization adds no value
- Highly standardized codebases with enforced style guides (style adapter may be redundant)
- Real-time latency-critical applications (dual-module overhead may be prohibitive)

**Known Limitations:**
- Cold-start problem: New users require bootstrap period
- Retrieval latency: ToM memory retrieval adds ~100-200ms
- Style drift: Long-term style evolution not addressed in current design
- Cross-language: Style adapter trained per-language, not cross-language

### 1.6 Testable Predictions

**Primary Prediction:**
**P1 (Developer Satisfaction vs Baseline):**
StyleToM will achieve developer satisfaction scores >20% higher than the baseline (OpenHands without personalization).

*Measurement:*
- Likert scale 1-5 survey, n ≥ 30 developers
- Pre/post intervention design
- Statistical test: Paired t-test, p < 0.05

*Basis:*
TOM-SWE alone achieved 86% usefulness rating. Adding style personalization should provide additional improvement. Target: 4.0+ on 5-point scale (baseline estimated at ~3.3).

*Success Criteria for Phase 2B:*
- Primary: Satisfaction improvement >20% (p < 0.05)
- Falsification: Satisfaction ≤ baseline triggers rejection

**Secondary Predictions:**

**P2 (Style Adapter Contribution):**
If Style Adapter is enabled (ToM + Style vs ToM-only), then style similarity score will improve by >15% while maintaining acceptance rate.

**P3 (ToM Module Contribution):**
If ToM Module is enabled (Style + ToM vs Style-only), then code acceptance rate will improve by >10% due to better intent alignment.

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure:** Developer satisfaction ≤ baseline (no improvement or worse)
2. **Mechanism Failure:** Ablation shows no marginal contribution from either component
3. **Efficiency Failure:** Latency overhead >50% making deployment impractical

### 1.7 SOTA Baseline (Not Applicable - Novel Integration)

This hypothesis targets a novel integration (style + intent personalization) rather than SOTA performance comparison.

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Target effect size (Cohen's d): 0.5 (medium effect)
- Required sample: n ≥ 30 developers for user study
- Required runs: n ≥ 25 task instances for automated metrics
- Statistical power: 0.8

**Test Specification:**
- Developer satisfaction: Paired t-test (pre/post), α = 0.05 (one-tailed)
- Acceptance rate: Chi-square test for proportions
- Style similarity: Paired t-test on matched samples
- Ablation: ANOVA with post-hoc Tukey HSD for component comparison

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does StyleToM produce measurably different (more personalized) code suggestions compared to non-personalized baselines?"
- Maps to: Primary prediction (satisfaction improvement)
- Verification type: Empirical (automated metrics + user study)
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is the dual-adapter mechanism (Style + ToM) the actual cause of personalization improvement?"
- Maps to: Causal mechanism (N=3 steps)
- Will decompose into 3 sub-hypotheses in Phase 2B:
  - H-M1: Style Adapter captures learnable developer patterns
  - H-M2: ToM Module correctly infers intent from history
  - H-M3: Combined output improves over individual components
- Verification type: Ablation study (Style-only vs ToM-only vs Full)
- Critical: Determines explanatory power

**SH3 (Comparison):**
"Does StyleToM outperform single-dimension approaches (TOM-SWE, MPCoder) on developer satisfaction and acceptance metrics?"
- Maps to: Secondary predictions
- Verification type: Comparative empirical (ablation + baselines)
- Critical: Determines practical value and novelty claim

**Total Sub-Hypotheses in Phase 2B:** 2 + 3 = 5 (SH1, H-M1, H-M2, H-M3, SH3)

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-StyleToM-v1
- [x] Confidence level specified: 0.86
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=3 steps, evidence table included)
- [x] Causal chain length (N=3) determined and stored
- [x] Key tension identified (additive vs interference) and resolution proposed (ablation)
- [x] Key assumptions list consequences if violated (4 assumptions)
- [x] At least 2 testable predictions exist (3 predictions with primary marked)
- [x] Falsification criteria are defined (3 failure conditions)
- [x] Baselines are identified for comparison (OpenHands, TOM-SWE, MPCoder)
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Cold-Start Handling:** How to bootstrap personalization for new users with <50 files of history?

2. **Evaluation Dataset:** Should user study use synthetic tasks or real developer workflows?

3. **Implementation Priority:** Validate individual components first or implement full StyleToM?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-12*
