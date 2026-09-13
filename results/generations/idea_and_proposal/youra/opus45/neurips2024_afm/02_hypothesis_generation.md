# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-13
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-CPLoRA-v1
**Confidence Level:** 0.85

**Main Hypothesis:**
Under the condition of limited user interaction data (<100 samples per user), if user personalization is represented as learned compositional mappings over a shared bank of K MSU-inspired primitive LoRA modules (with frozen primitives and 5K-parameter attention-based composition network), then the model will achieve comparable personalization accuracy to user-specific LoRA while retaining >95% of base model generalization capability, because compositional structure enables flexible user-specific combinations without modifying the underlying general-purpose primitives.

**Alternative Hypothesis (H0):**
Compositional structure provides no advantage over direct user-specific LoRA fine-tuning for personalization; the overhead of primitive learning and composition networks results in either (a) lower personalization accuracy, (b) lower generalization retention, or (c) no meaningful parameter efficiency gains.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Number of primitives (K) | Independent | K primitive LoRA modules pre-trained on population data using contrastive objectives | K ∈ {32, 64, 128} |
| Composition network size | Independent | Cross-attention between user history embedding and primitive representations | 5K parameters (adjustable to 10K) |
| User interaction data size | Controlled | Number of user-specific interaction samples | Fixed at <100 samples per user |
| Base model architecture | Controlled | Foundation model architecture | LLaMA-7B/13B, Mistral-7B |
| Personalization accuracy | Dependent | PersoBench/LaMP benchmark accuracy on user-specific task completion | Target: ≥90% of user-specific LoRA |
| Generalization retention rate | Dependent | Performance on general benchmarks (MMLU, HellaSwag) as % of base model | Target: >95% |
| Parameter efficiency | Dependent | User-specific parameter count | Target: <10K (vs ~100K for user-specific LoRA) |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
Step 1: Diverse Primitive Bank [K primitives]
    ↓
    Contrastive pre-training on population data ensures primitives
    capture orthogonal preference patterns (MSU design)
    ↓
Step 2: User Composition Network [5K params]
    ↓
    Cross-attention learns context-dependent weighting of primitives
    based on user history embedding
    ↓
Step 3: Frozen Primitives + Learned Composition
    ↓
    Combination of frozen general-purpose primitives enables
    personalization without modifying base model knowledge
    ↓
[OUTCOME]: Personalization accuracy + Generalization retention + Parameter efficiency
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | VB-LoRA (2024) | Shared vector banks achieve 0.4% of LoRA params while matching performance | Strong |
| Step 2 → Step 3 | PROPER (2025) | User-aware routing successfully assigns users to appropriate group-level LoRAs | Strong |
| Step 3 → Outcome | LoRA-LEGO (2024) | MSU combination preserves individual capabilities via permutation invariance | Strong |

**Key Tension:**
- **Tension:** LoRA-LEGO demonstrates MSU combinability for task-level merging, but PROPER shows user-specific adaptation may require routing complexity beyond simple attention.
- **Resolution:** This verification plan tests whether 5K-parameter attention provides sufficient expressiveness, with fallback to hierarchical cold-start (group → user) for complex preference patterns.

### 1.4 Key Assumptions

| # | Assumption | Supporting Evidence | Consequence if Violated |
|---|------------|---------------------|------------------------|
| 1 | User preferences are decomposable into compositions of K general preference primitives | MLC (Lake & Baroni, Nature 2023): Humans achieve systematicity through compositional learning | If violated: Need exponentially many primitives or alternative representation; hypothesis fails fundamentally |
| 2 | MSU-based primitive design ensures combinability without interference | LoRA-LEGO: Permutation invariance and concatenation-summation equivalence validated | If violated: Primitive combinations cause destructive interference; need alternative orthogonalization method |
| 3 | Population-level data (1M+ samples) is sufficient for learning diverse primitive bank | VB-LoRA: Shared banks learned from diverse data achieve broad task coverage | If violated: Primitives lack diversity; need larger/more diverse pre-training data |
| 4 | 5K-parameter attention provides sufficient expressiveness | PROPER: User-aware router with similar complexity routes users effectively | If violated: Need larger composition network (10K+) or residual personalization path |

### 1.5 Scope & Boundaries

**Applies to:**
- Large Language Models (LLaMA, Mistral, GPT-family)
- Vision-Language Models with LoRA support
- Recommendation systems requiring user personalization
- Scenarios with limited user data (<100 interactions per user)
- Cold-start user onboarding

**Does NOT apply to:**
- Real-time adaptation scenarios (requires pre-learned primitives)
- Extremely rare/unique preferences (outliers beyond primitive space)
- Privacy-sensitive domains where population data sharing is prohibited
- Models without LoRA-compatible architecture

**Known Limitations:**
- Primitive pre-training is one-time but computationally significant
- Cold-start requires group-level fallback before individual composition
- Extreme personalization outliers may need residual path (future work)

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Personalization Accuracy):**
CP-LoRA will achieve personalization accuracy ≥90% of user-specific LoRA baseline on PersoBench/LaMP benchmarks, with statistical significance p < 0.05.

*Measurement:*
- Metric: Task completion accuracy on personalization benchmarks
- Comparison: Against user-specific LoRA with equivalent adaptation budget
- Statistical test: Paired t-test, n ≥ 25 users

*Success Criteria for Phase 2B:*
- Primary: Personalization accuracy ≥90% of baseline (p < 0.05)
- Falsification: Personalization accuracy <80% of baseline triggers rejection

**Secondary Predictions:**

**P2 (Generalization Retention):**
CP-LoRA will retain >95% of base model performance on general benchmarks (MMLU, HellaSwag, ARC-Challenge), demonstrating that frozen primitives preserve general knowledge.

**P3 (Parameter Efficiency):**
CP-LoRA will achieve target personalization with <10K user-specific parameters, representing >10x efficiency gain over user-specific LoRA (~100K parameters).

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure:** Personalization accuracy <80% of user-specific LoRA baseline
2. **Mechanism Failure:** Generalization retention <85% of base model
3. **Efficiency Failure:** User-specific parameters >50K with no accuracy gain
4. **Assumption Violation:** K=128 primitives fail to cover >80% of test user preferences

### 1.7 Statistical Verification Design

**Sample Size Calculation:**
- Effect size target (Cohen's d): 0.5 (medium effect)
- Required sample: n ≥ 25 users per condition
- Statistical power: 0.8

**Test Specification:**
- Primary comparison: Paired t-test (same users, CP-LoRA vs user-specific LoRA)
- Significance level: α = 0.05
- Report format: Mean ± Std Dev, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Under limited user data conditions (<100 samples), does CP-LoRA achieve comparable personalization accuracy (≥90%) to user-specific LoRA?"
- Maps to: Primary prediction (P1)
- Verification type: Empirical comparison
- Critical: MUST PASS for hypothesis validity

**SH2 (Mechanism) - 3 sub-hypotheses based on N=3 causal steps:**

- **H-M1 (Primitive Diversity):** "Does a bank of K=64 primitives pre-trained with contrastive objectives provide sufficient coverage of user preference space (>80% coverage)?"

- **H-M2 (Composition Expressiveness):** "Does the 5K-parameter attention composition network accurately learn user-specific primitive weightings (correlation >0.7 with ground truth preferences)?"

- **H-M3 (Generalization Preservation):** "Does frozen primitive + learned composition preserve >95% generalization on general benchmarks?"

**SH3 (Comparison):**
"Does CP-LoRA outperform PROPER on personalization accuracy while using <50% of per-user parameters?"
- Maps to: Secondary predictions (P2, P3)
- Verification type: Comparative empirical
- Critical: Determines practical value

**Total Sub-Hypotheses for Phase 2B:** 5 (1 + 3 + 1)

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-CPLoRA-v1
- [x] Confidence level specified: 0.85
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=3 steps, evidence table included)
- [x] Causal chain length (N=3) determined and stored
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist (3 total, primary marked)
- [x] Falsification criteria are defined (4 conditions)
- [x] Baselines are identified for comparison (PROPER, user-specific LoRA)
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Resource Requirements:** How much compute for K=128 primitive pre-training? (Estimate: 1-2 days on 8xA100)

2. **Data Availability:** What population-level datasets suitable for primitive learning? (Candidates: OpenAssistant, ShareGPT, Alpaca-cleaned)

3. **Optimal K Selection:** What is the minimal K for sufficient preference coverage? (Phase 2B: K ∈ {32, 64, 128} ablation)

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-13*
