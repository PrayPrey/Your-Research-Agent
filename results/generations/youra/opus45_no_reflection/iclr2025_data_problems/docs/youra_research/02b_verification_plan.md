# Verification Plan: Architecture-Aware Data Attribution

**Date:** 2026-08-18
**Hypothesis ID:** H-ArchAttr-v1
**Confidence:** 0.75
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under matched architectures (BERT-base 12L vs GPT-2 12L, ~110-125M params) and text classification tasks (SST-2 mislabeled detection), if we compare TRAK, EK-FAC, and TracIn attribution methods, then decoder-only GPT-2 will show better efficiency-accuracy trade-offs for EK-FAC, encoder-only BERT will show better trade-offs for TracIn, and TRAK will show minimal architecture variance, because attention structure interacts differently with each method's approximation mechanism.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in efficiency-accuracy trade-offs across encoder-only (BERT) and decoder-only (GPT-2) architectures for any of the three attribution methods (TRAK, EK-FAC, TracIn) at matched compute budgets.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | SST-2 (standard) | Binary sentiment classification allows both BERT and GPT-2 to perform natively |
| **Model** | BERT-base-uncased and GPT-2 | Matched layer count (12), similar params (110M vs 124M) |

**Dataset Details:**
- Source: GLUE benchmark via HuggingFace datasets
- Path: glue/sst2

**Model Details:**
- Type: Encoder-only transformer, Decoder-only transformer
- Source: HuggingFace Transformers

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| EK-FAC (Grosse et al. 2023) | 0.85 Spearman on LLaMA-2 52B | Pile-derived |
| TRAK (Park et al. 2023) | SOTA on BERT mislabeled detection | CIFAR, ImageNet |
| TracIn (Pruthi et al. 2020) | Strong on BERT-style models | Various NLP |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Matched layer count (12) sufficient for depth control | Standard transformer comparison practice | Depth confound possible |
| A2 | SST-2 mislabeled detection generalizes | Standard sentiment benchmark | May not transfer to other tasks |
| A3 | 5% label noise rate representative | Common rate in literature (Koh & Liang 2017) | Different rates may show different effects |
| A4 | Implementation quality equivalent | Using established libraries (kronfluence, trak) | Implementation bugs create spurious differences |

### 1.6 Research Gap & Novelty

**Gap:** Prior work evaluated methods on single architectures (EK-FAC on decoder-only, TRAK on encoder-only). No systematic matched cross-architecture comparison exists.

**Innovation:** First matched cross-architecture comparison with predictive theory based on attention-curvature-approximation interaction. Provides prescriptive framework for method selection.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | READY |
| H-M1 | Mechanism | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | Mechanism | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | Mechanism | SHOULD_WORK | H-M2 | NOT_STARTED |
| H-M4 | Mechanism | SHOULD_WORK | H-M3 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

#### H-E1: Architecture-Method Interaction Exists

**Type:** EXISTENCE
**Statement:** Under matched architectures and SST-2 mislabeled detection, if we measure efficiency-accuracy trade-offs for TRAK, EK-FAC, and TracIn, then measurable differences exist across BERT vs GPT-2, because attention structure affects gradient computation patterns.

**Rationale:** This establishes the foundational claim that architecture-method interaction is a real, measurable phenomenon. Without this, the mechanism hypotheses have no target to explain.

**Variables:**
- IV: Architecture Type (encoder-only vs decoder-only)
- DV: Mislabeled Detection AUC
- CV: Model size (~110-125M), Layer count (12), Dataset (SST-2)

**Verification Protocol:**
1. Fine-tune BERT-base and GPT-2 on SST-2 with 5% mislabeled examples
2. Compute influence scores using all three methods at matched compute budgets
3. Calculate mislabeled detection AUC for each method × architecture combination
4. Statistical test: paired t-test across 5 random seeds

**Success Criteria (PoC: Direction-based):**
- Primary: At least one method shows >5% AUC difference across architectures (p < 0.05)
- Secondary: Effect size Cohen's d > 0.3 for at least one method

**Failure Response:**
- IF fails: ABANDON main hypothesis (architecture interaction doesn't exist)

**Dependencies:** None

**Source:** Phase 2A SH1, P1-P3

---

#### H-M1: Attention Pattern Divergence

**Type:** MECHANISM
**Statement:** Under BERT vs GPT-2, if we analyze attention computation, then bidirectional attention (BERT) computes O(n²) full attention weights while causal attention (GPT-2) computes O(n²/2) masked weights, because architectural definition constrains attention pattern structure.

**Rationale:** This is the first step in the causal chain—establishing that attention patterns fundamentally differ between architectures.

**Variables:**
- IV: Architecture Type
- DV: Attention pattern structure (full vs causal mask)
- CV: Sequence length, Layer count

**Verification Protocol:**
1. Extract attention weights from both models on same input sequences
2. Verify BERT produces full n×n attention matrices
3. Verify GPT-2 produces lower-triangular (causal) attention matrices
4. Quantify sparsity difference

**Success Criteria:**
- Primary: Attention pattern structure matches architectural definition
- Secondary: Measurable sparsity difference in attention matrices

**Failure Response:**
- IF fails: EXPLORE alternative explanations (unlikely—architectural definition)

**Dependencies:** H-E1

**Source:** Phase 2A Causal Step 1

---

#### H-M2: Hessian Curvature Divergence

**Type:** MECHANISM
**Statement:** Under different attention structures, if we analyze Hessian curvature, then causal attention creates block-diagonal-ish attention Jacobians while bidirectional creates denser Jacobian structure, because attention mask propagates through gradient computation.

**Rationale:** This tests whether attention structure differences propagate to affect curvature—the key link to why approximation methods behave differently.

**Variables:**
- IV: Attention pattern structure
- DV: Hessian spectrum characteristics
- CV: Model size, Training state

**Verification Protocol:**
1. Compute Hessian eigenvalue spectrum for both architectures
2. Analyze Jacobian structure of attention layers
3. Compare curvature characteristics using random matrix theory metrics
4. Test Kronecker factorization fit quality

**Success Criteria:**
- Primary: Measurable difference in Hessian spectrum between architectures
- Secondary: GPT-2 shows better Kronecker factorization fit

**Failure Response:**
- IF fails: PIVOT to alternative curvature metrics

**Dependencies:** H-M1

**Source:** Phase 2A Causal Step 2

---

#### H-M3: Approximation Assumption Sensitivity

**Type:** MECHANISM
**Statement:** Under different curvature patterns, if we apply different approximation methods, then EK-FAC (Kronecker assumption) fits causal structure better, TracIn (gradient-only) benefits from dense encoder gradients, and TRAK (random projection) is invariant, because each method's mathematical assumptions interact differently with curvature.

**Rationale:** This tests the core mechanism—that approximation assumptions create architecture-specific performance.

**Variables:**
- IV: Curvature pattern type
- DV: Approximation error
- CV: Compute budget, Method implementation

**Verification Protocol:**
1. Measure EK-FAC approximation error on both architectures
2. Measure TracIn gradient signal quality on both architectures
3. Measure TRAK projection variance across architectures
4. Compare relative approximation quality

**Success Criteria:**
- Primary: EK-FAC approximation error lower on GPT-2 than BERT
- Secondary: TracIn gradient signal stronger on BERT than GPT-2

**Failure Response:**
- IF fails: EXPLORE alternative approximation metrics

**Dependencies:** H-M2

**Source:** Phase 2A Causal Step 3

---

#### H-M4: Efficiency-Accuracy Trade-off Prediction

**Type:** MECHANISM
**Statement:** Under architecture-approximation interaction, if we plot efficiency-accuracy Pareto curves, then EK-FAC dominates on GPT-2, TracIn dominates on BERT, and TRAK shows overlapping curves, because the interaction determines optimal operating points.

**Rationale:** This is the final mechanism step—showing that the predicted trade-offs emerge from the causal chain.

**Variables:**
- IV: Architecture × Method combination
- DV: Pareto frontier position
- CV: Evaluation metric, Compute budget range

**Verification Protocol:**
1. Compute Pareto curves at 3 compute levels per method × architecture
2. Compare Pareto dominance across combinations
3. Statistical test: compare curve positions
4. Validate predictions P1-P3 from Phase 2A

**Success Criteria:**
- Primary: P1 (EK-FAC GPT-2 > BERT) and P2 (TracIn BERT > GPT-2) confirmed with p < 0.05
- Secondary: P3 (TRAK invariant) confirmed with |diff| < 2%

**Failure Response:**
- IF fails: Document as limitation, proceed to Phase 5 for deeper analysis

**Dependencies:** H-M3

**Source:** Phase 2A Causal Step 4, Predictions P1-P3

---

## 3. Execution

### 3.1 Dependency Chain

```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | >5% AUC diff, p<0.05 | STOP - reassess hypothesis |
| H-M1 | MUST_WORK | Attention patterns match definition | STOP - architectural error |
| H-M2 | SHOULD_WORK | Measurable Hessian difference | Document limitation |
| H-M3 | SHOULD_WORK | Approximation sensitivity shown | Explore alternatives |
| H-M4 | SHOULD_WORK | Predictions P1-P3 confirmed | Proceed to Phase 5 |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanisms | H-M1, H-M2, H-M3, H-M4 | 4 weeks |

**Total Duration:** 6 weeks

---

## 4. Risk Analysis

### 4.1 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1 | A1 (Layer count confound) | H-E1, H-M1 | Medium |
| R2 | A2 (Task generalization) | H-M4 | Medium |
| R3 | A3 (Noise rate sensitivity) | H-E1 | Low |
| R4 | A4 (Implementation quality) | All | High |

### 4.2 Mitigation Strategies

**R1: Layer Count Confound**
- Prevention: Use only 12-layer models (BERT-base, GPT-2)
- Detection: Monitor for depth-correlated effects
- Response: Document as limitation, suggest future 24-layer study

**R2: Task Generalization**
- Prevention: Start with SST-2 as standard benchmark
- Detection: Track if results differ from prior single-architecture studies
- Response: PIVOT to multi-task evaluation (AG News, MNLI)

**R3: Noise Rate Sensitivity**
- Prevention: Use established 5% rate from literature
- Detection: Compare to prior work at same rate
- Response: EXPLORE additional noise rates (2%, 10%)

**R4: Implementation Quality**
- Prevention: Use established libraries (kronfluence, trak)
- Detection: Verify against published results
- Response: Debug implementation, consult library authors

### 4.3 Risk Summary

| ID | Risk | Severity | Mitigation |
|----|------|----------|------------|
| R1 | Depth confound | Medium | Scope to 12-layer only |
| R2 | Task specificity | Medium | Multi-task validation |
| R3 | Noise rate | Low | Standard rate + sensitivity |
| R4 | Implementation bugs | High | Established libraries |

**Critical: 0 | High: 1 | Medium: 2 | Low: 1**

---

## 5. Dependency Graph & Timeline

### 5.1 DAG Visualization

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1 (Existence - no dependencies)
         │
         ▼
[Level 1 - Mechanism Chain]
    H-M1 ← H-E1 (Attention Pattern Divergence)
         │
         ▼
    H-M2 ← H-M1 (Hessian Curvature Divergence)
         │
         ▼
    H-M3 ← H-M2 (Approximation Assumption Sensitivity)
         │
         ▼
    H-M4 ← H-M3 (Efficiency-Accuracy Trade-off)

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
═══════════════════════════════════════════════════════════
```

### 5.2 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis │ W1-2 │ W3   │ W4   │ W5   │ W6   │
─────────────────┼──────┼──────┼──────┼──────┼──────┼
PHASE 1: Foundation
  H-E1           │██████│      │      │      │      │
  [Gate 1]       │      │◆     │      │      │      │
─────────────────┼──────┼──────┼──────┼──────┼──────┼
PHASE 2: Mechanisms
  H-M1           │      │██████│      │      │      │
  H-M2           │      │      │██████│      │      │
  H-M3           │      │      │      │██████│      │
  H-M4           │      │      │      │      │██████│
  [Gate 2]       │      │      │      │      │      │◆
═══════════════════════════════════════════════════════════════════
Legend: ██████ = Active work | ◆ = Gate decision point
Total Duration: 6 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.3 Critical Path Analysis

**Critical Path:** H-E1 → H-M1 → H-M2 → H-M3 → H-M4
**Total Duration:** 6 weeks (2 + 4)
**Slack Available:** 0 weeks (all sequential)

### 5.4 Resource Summary

- **Total Hypotheses:** 5 (1 Existence + 4 Mechanism)
- **Verification Phases:** 2
- **Total Duration:** 6 weeks
- **Execution Mode:** Sequential chain

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** Transformer attention structure (encoder bidirectional vs decoder causal) systematically affects data attribution efficiency-accuracy trade-offs, with EK-FAC favoring decoder-only, TracIn favoring encoder-only, and TRAK being architecture-invariant.

**Supporting Evidence:**
1. Grosse et al. observed EK-FAC's Kronecker assumption fits causal attention structure
2. Architectural definitions constrain gradient flow patterns
3. Each approximation method makes different mathematical assumptions

**Strengths:**
- Grounded in architectural definitions (unfalsifiable base)
- Clear causal mechanism with 4 testable steps
- Three independent, falsifiable predictions

### 6.2 Antithesis

**Null Hypothesis (H0):** There is no significant difference in efficiency-accuracy trade-offs across encoder-only (BERT) and decoder-only (GPT-2) architectures for any of the three attribution methods at matched compute budgets.

**Counter-Arguments:**
1. Random projections (TRAK) may wash out any architectural effects
2. Practical implementations may not reflect theoretical assumptions
3. SST-2 may not be sensitive enough to detect differences

**Conditions for H0 Support:**
- If <5% AUC difference across all methods (p > 0.05)
- If Pareto curves overlap significantly
- If mechanism steps fail to show predicted patterns

### 6.3 Synthesis

**Balanced Assessment:**

The hypothesis H-ArchAttr-v1 presents a testable claim that attention structure creates architecture-specific attribution performance. The null hypothesis raises valid concerns about whether these theoretical differences manifest in practice.

**Resolution Path:**

1. **Foundation verification (H-E1):** First establish that differences exist at all
2. **Sequential mechanism testing (H-M1-4):** Test each causal link independently
3. **Gate conditions:** Allow early detection of H0 support

**Conditions for Thesis Support:**
- H-E1 shows >5% AUC difference (p < 0.05)
- H-M1-M3 validate causal mechanism
- H-M4 confirms predictions P1-P3

**Conditions for Antithesis Support:**
- H-E1 fails: No measurable architecture effect
- H-M1 fails: Attention patterns don't differ as expected (unlikely)
- Multiple H-M failures: Mechanism doesn't hold

**Nuanced Outcomes:**
1. **Full Support:** All hypotheses pass → Thesis validated
2. **Partial Support:** Some H-M fail → Refined thesis with limitations
3. **No Support:** H-E1 fails → Antithesis supported

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Interaction exists | May be artifact | H-E1 test |
| Mechanism | Causal chain valid | Alternative explanations | H-M1-4 tests |
| Scope | Applies to attribution | Limited to SST-2 | Multi-task Phase 5 |
| Performance | Method-specific patterns | Random variation | Statistical testing |

**Overall Robustness:** Medium-High
**Confidence in Verification Plan:** 0.75

---

## 7. Executive Summary

**Main Hypothesis:** Architecture-method interaction determines data attribution efficiency-accuracy trade-offs
- ID: H-ArchAttr-v1, Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (Phase 2A available)
- Sub-Hypotheses: 5 total (H-E: 1, H-M: 4)
- Phases: 2 phases over 6 weeks
- Critical Gates: 2 decision points

**Risk Assessment:** Medium
- Primary concerns: Implementation quality (R4), Task generalization (R2)

**Immediate Action:** Begin Phase 1 with H-E1 (existence verification)

---

## Appendices

### A. Phase 2A Reference
- **Source:** 03_refinement.yaml (ID: H-ArchAttr-v1)
- **Scope Reduction:** 40% (3 BUILD_ON claims skipped)

### B. MCP Tool Usage Summary
- **Total MCP calls:** 1
- **Tools:** scientificmethod (1x for H-E1 verification design)

### C. Established Facts (BUILD_ON - Not Re-verified)
1. EK-FAC scales to 52B parameter decoder-only LLMs (Grosse et al. 2023)
2. TRAK achieves comparable performance on BERT and CLIP (Park et al. 2023)
3. TracIn provides first-order checkpoint-based influence estimation (Pruthi et al. 2020)

---

*Generated by Phase 2B Planning Workflow*
*Status: Complete*
*Completed At: 2026-08-18*
