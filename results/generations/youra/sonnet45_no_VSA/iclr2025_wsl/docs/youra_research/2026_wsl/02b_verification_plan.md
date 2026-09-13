# Verification Plan: Lightweight Statistical Architecture Classifier

**Date:** 2026-07-11
**Hypothesis ID:** weight-stats-classifier
**Confidence:** 0.75
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Lightweight statistical features—normalization layer type counts and convolution-to-linear parameter-mass ratio—enable architecture family classification (CNN vs Transformer vs Hybrid) from checkpoint files without forward passes, achieving >80% accuracy on held-out model families with scale-stable features and strong inter-family separation.

### 1.2 Alternative Hypothesis (H0)
Statistical features (normalization counts, parameter-mass ratio) do NOT achieve significantly better than random classification (33.3% for 3-way task) on held-out architecture families.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | TIMM Model Zoo (standard) | 50 models (20 CNN, 20 Transformer, 10 Hybrid) with 70% train, 30% validation split |
| **Model** | Logistic Regression | Tests feature sufficiency—no MLP rescue allowed |

**Dataset Details:**
- Source: TIMM library
- Path: timm.create_model() + load checkpoints

**Model Details:**
- Type: Linear classifier
- Source: sklearn.linear_model.LogisticRegression

### 1.4 Baseline Methods (for H-CP* comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Kofinas et al. 2024 GNN | High accuracy with GNN | Various NN architectures |
| Zhang & Abdulla 2023 | BatchNorm statistics | Performance prediction |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | TIMM naming aligns with structure | Expected >90% alignment on 10-model sample | Mislabeled training data → wrong features |
| A2 | Normalization reflects paradigm, not training | Violation rate must be ≤15% per class | Features lose discriminative power |
| A3 | Parameter-mass ratio is scale-invariant | Intra-family CV <0.15 across ResNet-{18,34,50,101,152} | Scale confounds structure signal |
| A4 | Linear classifier sufficient | Logistic regression test passes | Features are not linearly separable |

### 1.6 Research Gap & Novelty

**Core Contribution:** First interpretable, checkpoint-only classifier requiring no forward pass, GNN processing, or model instantiation.

**vs Kofinas et al. (2024):** Complex GNN processing (50+ hours) vs simple statistical features (6 hours, <15 tasks)

**vs Zhang & Abdulla (2023):** Requires forward passes for BatchNorm runtime statistics vs checkpoint-only analysis

**Paradigm Shift:** From complex neural architectures (SANE, UNF, NFN) to simple statistical features for weight space learning.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | READY |
| H-M1 | Mechanism | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | Mechanism | MUST_WORK | H-M1 | NOT_STARTED |
| H-M3 | Mechanism | MUST_WORK | H-M2 | NOT_STARTED |
| H-C1 | Condition | SHOULD_WORK | H-M3 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---

#### H-E1: Statistical Features Sufficiency

**Statement**: Under TIMM model zoo evaluation, if normalization layer counts and parameter-mass ratio are extracted from checkpoints, then >80% 3-way classification accuracy (CNN/Transformer/Hybrid) can be achieved because these features capture fundamental architectural constraints (BatchNorm for spatial data, LayerNorm for sequential, conv vs linear parameter allocation).

**Rationale** (2-3 sentences):
This hypothesis validates that simple statistical features are sufficient for architecture family classification, challenging the assumption that complex GNN architectures (Kofinas 2024) are necessary. Success proves the phenomenon exists and justifies investigating the underlying mechanism. Failure would indicate that weight-space structure requires deeper analysis than surface statistics.

**Variables** (from Phase 2A):
- Independent: Architecture family (CNN / Transformer / Hybrid)
- Dependent: Classification accuracy (macro-averaged)
- Controlled: Model size (multi-scale), Family diversity (stratified split), Ground truth (TIMM naming)

**Verification Protocol** (3-5 steps):
1. Extract normalization counts (BN, LN, GN, No_norm_flag) and parameter-mass ratio R from 50 TIMM model checkpoints
2. Train logistic regression classifier on 70% (35 models), validate on 30% (15 models) with stratified split
3. Measure macro-averaged accuracy on validation set and per-class accuracy breakdown
4. Validate scale invariance: intra-family CV <0.15 across ResNet-{18,34,50,101,152}
5. Document confusion matrix and failure cases

**Success Criteria** (PoC: Direction-based):
- Primary: Validation accuracy >80% (macro-averaged across 3 classes)
- Secondary: Per-class accuracy ≥75% (no single class collapse)

**Gate**:
- Type: MUST_WORK
- If Fail: ABANDON (features insufficient → need complex representations)

**Dependencies**: None (foundation hypothesis)

**Source**: Phase 2A Section 1.6 Prediction P1 (Primary)

---

#### H-M1: Normalization Layer Fingerprinting

**Statement**: Under TIMM model checkpoint inspection, if normalization layer types are counted via state_dict key regex matching, then CNNs show predominantly BatchNorm (>80%), Transformers show predominantly LayerNorm (>80%), and Hybrids show mixed patterns because architectural paradigms impose normalization conventions (spatial vs token-wise statistics).

**Rationale**:
This hypothesis tests the first step of the causal mechanism—that normalization layer choice is a reliable architectural signature. It validates Chun 2026's theoretical finding (LayerNorm reduces LLC by m/2 vs BatchNorm) manifests empirically as a discriminative feature.

**Variables**:
- Independent: Normalization layer type counts (BN_count, LN_count, GN_count, No_norm_flag)
- Dependent: Architecture family classification (CNN/Transformer/Hybrid)
- Controlled: TIMM naming conventions, state_dict parsing method

**Verification Protocol**:
1. Extract normalization layer counts from state_dict keys using regex patterns (r'bn|batch_norm' for BN, r'ln|layer_norm' for LN)
2. Calculate violation rate per class (CNNs with LN, Transformers with BN)
3. Test assumption: violation rate ≤15% per class (A2 from Phase 2A)
4. Measure feature importance via logistic regression coefficients

**Success Criteria**:
- Primary: Violation rate ≤15% per class (normalization reflects paradigm)
- Secondary: BN/LN counts have high feature importance (top 2 in logistic regression coefficients)

**Gate**:
- Type: MUST_WORK
- If Fail: PIVOT (test alternative: GroupNorm patterns, activation function counts)

**Dependencies**: H-E1 (requires baseline classifier working)

**Source**: Phase 2A Causal Step 1

---

#### H-M2: Parameter Allocation Pattern

**Statement**: Under checkpoint parameter counting, if parameter-mass ratio R = conv_params / (conv_params + linear_params_no_head) is computed, then CNNs show high R (>0.6), Transformers show low R (<0.2), and inter-family Cohen's d >1.0 because CNNs allocate to convolutional kernels (local receptive fields) while Transformers allocate to large linear projections (global attention).

**Rationale**:
This hypothesis tests the second causal mechanism step—that parameter allocation patterns reflect architectural computation style. It validates Fang 2024's finding (heterogeneous structures have diverged importance distributions) as a discriminative feature.

**Variables**:
- Independent: Parameter-mass ratio R
- Dependent: Inter-family separation (Cohen's d effect size)
- Controlled: Head exclusion (linear_params_no_head), Model size (multi-scale)

**Verification Protocol**:
1. Count conv_params (4D tensors) and linear_params_no_head (2D tensors excluding classification head) per model
2. Compute R for each model and intra-family coefficient of variation (CV)
3. Test assumption: intra-family CV <0.15 across ResNet-{18,34,50,101,152} (A3 scale invariance)
4. Compute inter-family Cohen's d between CNN and Transformer R distributions

**Success Criteria**:
- Primary: Inter-family Cohen's d >1.0 (strong separation)
- Secondary: Intra-family CV <0.15 (scale-stable feature)

**Gate**:
- Type: MUST_WORK
- If Fail: EXPLORE (test alternative ratios: attention_params / total_params, embedding_dim patterns)

**Dependencies**: H-M1 (requires normalization fingerprint validated)

**Source**: Phase 2A Causal Step 2

---

#### H-M3: Checkpoint Extraction Feasibility

**Statement**: Under PyTorch state_dict inspection, if models are loaded with weights_only=True and features extracted without forward passes, then extraction completes for 50 models in <10 minutes total because checkpoint access is deterministic and requires no model instantiation or GPU computation.

**Rationale**:
This hypothesis tests the final causal step—that signatures are extractable via lightweight checkpoint inspection, not requiring expensive forward passes (vs Zhang & Abdulla 2023 runtime statistics) or graph construction (vs Kofinas 2024 GNN).

**Variables**:
- Independent: Extraction method (checkpoint-only vs forward-pass-based)
- Dependent: Extraction time, GPU memory usage
- Controlled: PyTorch version (2.1), TIMM version (1.0.9), weights_only flag

**Verification Protocol**:
1. Load checkpoints with torch.load(weights_only=True) for security and speed
2. Extract features via state_dict key regex matching and tensor shape inspection
3. Measure total extraction time for 50 models and GPU memory usage
4. Compare against forward-pass baseline (load model, run 1 batch) for 5 models

**Success Criteria**:
- Primary: Extraction time <10 minutes for 50 models (vs >30 min for forward passes)
- Secondary: Zero GPU memory usage (CPU-only extraction)

**Gate**:
- Type: MUST_WORK
- If Fail: ABANDON (extraction not lightweight → violates core contribution)

**Dependencies**: H-M2 (requires parameter counting working)

**Source**: Phase 2A Causal Step 3

---

#### H-C1: Edge Case Robustness

**Statement**: Under edge case architecture evaluation (NormFree networks, non-standard attention, extreme scaling), if fallback heuristics (No_norm_flag binary feature) are added, then accuracy degradation is ≤15% vs standard architectures because edge cases violate normalization assumptions but retain parameter allocation patterns.

**Rationale**:
This hypothesis tests boundary conditions where standard assumptions (A2: normalization reflects paradigm) break down. It validates scope limits and identifies where the approach needs extension.

**Variables**:
- Independent: Edge case type (NFNet, SENet, RegNet)
- Dependent: Accuracy degradation vs standard architectures
- Controlled: Fallback heuristic (No_norm_flag), Test set size (3 families)

**Verification Protocol**:
1. Identify edge case models from TIMM: NFNet (NormFree), SENet (squeeze-excite), RegNet (extreme depth)
2. Extract features with fallback heuristics: No_norm_flag=1 if no BN/LN/GN detected
3. Test on held-out edge case families and measure accuracy vs standard architecture performance
4. Document failure modes and feature importance shifts

**Success Criteria**:
- Primary: Accuracy degradation ≤15% on edge cases (>70% if baseline >85%)
- Secondary: Failure mode documentation identifies extension needs

**Gate**:
- Type: SHOULD_WORK
- If Fail: DOCUMENT (acceptable failure for boundary cases, informs scope limits)

**Dependencies**: H-M3 (requires full extraction pipeline working)

**Source**: Phase 2A Section 1.5 Scope Boundaries (known limitations)

---

<!--
Each hypothesis follows this format:

#### {H-ID}: {Title}

**Type:** {EXISTENCE|MECHANISM|CONDITION|COMPARISON}
**Statement:** {Full Under-If-Then-Because statement}

**Variables:**
- IV: {independent variable}
- DV: {dependent variable}
- CV: {controlled variables}

**Success Criteria:**
- {quantitative threshold 1}
- {quantitative threshold 2}

**Gate:**
- Type: {MUST_WORK|SHOULD_WORK|DETERMINES_SUCCESS}
- If Fail: {consequence}

**Prerequisites:** {list or "None"}

**Verification Protocol:** (100-150 words)
{step-by-step protocol}

---
-->

---

## 3. Execution

### 3.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1 (Existence - no dependencies)
         │
         ▼
[Level 1 - Mechanism Step 1]
    H-M1 (Normalization Fingerprinting) ← H-E1
         │
         ▼
[Level 2 - Mechanism Step 2]
    H-M2 (Parameter Allocation Pattern) ← H-M1
         │
         ▼
[Level 3 - Mechanism Step 3]
    H-M3 (Checkpoint Extraction Feasibility) ← H-M2
         │
         ▼
[Level 4 - Condition]
    H-C1 (Edge Case Robustness) ← H-M3

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-C1
═══════════════════════════════════════════════════════════
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | >80% validation accuracy | ABANDON - features insufficient |
| H-M1 | MUST_WORK | Violation rate ≤15% per class | PIVOT - test GroupNorm patterns |
| H-M2 | MUST_WORK | Cohen's d >1.0, CV <0.15 | EXPLORE - alternative ratios |
| H-M3 | MUST_WORK | <10 min extraction for 50 models | ABANDON - not lightweight |
| H-C1 | SHOULD_WORK | Accuracy degradation ≤15% | DOCUMENT - acceptable boundary failure |

### 3.3 Verification Timeline (Gantt)

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis │ W1-2 │ W3-4 │ W5 │ W6 │ W7
─────────────────┼──────┼──────┼────┼────┼────
PHASE 1: Foundation
  H-E1           │ ████ │      │    │    │
  [Gate 1]       │      │ ◆    │    │    │
─────────────────┼──────┼──────┼────┼────┼────
PHASE 2: Mechanisms
  H-M1           │      │ ████ │    │    │
  H-M2           │      │      │ ██ │    │
  H-M3           │      │      │    │ ██ │
  [Gate 2]       │      │      │    │    │ ◆
─────────────────┼──────┼──────┼────┼────┼────
PHASE 2.5: Conditions
  H-C1           │      │      │    │    │ ██
  [Gate 2.5]     │      │      │    │    │  ◆
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 6 weeks
═══════════════════════════════════════════════════════════════════
```

**Critical Path Analysis:**
- Path: H-E1 → H-M1 → H-M2 → H-M3 → H-C1
- Duration: 2 (H-E1) + 3 (H-M1-3) + 1 (H-C1) = 6 weeks
- Slack: 0 weeks (all sequential)

### 3.4 Resource Summary

- Total Hypotheses: 5
  - Existence: 1 (H-E1)
  - Mechanism: 3 (H-M1-M3)
  - Condition: 1 (H-C1)
- MUST_WORK Gates: 4
- SHOULD_WORK Gates: 1
- Critical Risks: 0
- High Risks: 2 (R2, R3)

---

## 5. Dialectical Analysis

### 5.1 Thesis

**Core Claim:** Lightweight statistical features—normalization layer type counts and convolution-to-linear parameter-mass ratio—enable architecture family classification from checkpoint files without forward passes, achieving >80% accuracy with scale-stable features and strong inter-family separation.

**Supporting Evidence:**
1. Chun 2026: LayerNorm vs BatchNorm impose fundamentally different geometric constraints
2. Fang 2024: Heterogeneous structures have diverged importance distributions (parameter scale)
3. Testable predictions with clear success criteria (>80% accuracy, CV <0.15, Cohen's d >1.0)

**Strengths:**
- Builds on established theory (no re-verification of known results)
- Simple features vs complex GNN (6 hours vs 50+ hours implementation)
- Checkpoint-only (no forward passes required)

**Expected Outcomes:**
- Primary: >80% validation accuracy on 50-model dataset
- Secondary: ≥70% accuracy on held-out families (leave-one-out)
- Tertiary: Intra-family CV <0.15, Inter-family Cohen's d >1.0

### 5.2 Antithesis

**Null Hypothesis (H0):** Statistical features do NOT achieve significantly better than random classification (33.3% for 3-way task) on held-out architecture families.

**Counter-Arguments:**
1. Normalization choice may be historical convention, not architectural necessity (violates A2)
2. Parameter-mass ratio may measure scale, not structure (violates A3)
3. TIMM naming may validate taxonomy, not discover structure (violates A1)

**Potential Failure Points:**
- R2: Normalization convention risk (violation >15% per class)
- R3: Scale invariance failure (CV ≥0.15)
- R4: Linear classifier insufficient (features not separable)

**Conditions Under Which H0 Would Be Supported:**
- If validation accuracy ≤50% (near-random for 3-way task)
- If normalization fingerprinting shows high violation rates (>15%)
- If parameter-mass ratio confounds scale with structure (CV ≥0.15)

### 5.3 Synthesis

**Balanced Assessment:**

The hypothesis presents a testable claim that simple statistical features (normalization counts + parameter-mass ratio) suffice for architecture family classification, challenging the assumption that complex GNN architectures (Kofinas 2024) are necessary. However, the null hypothesis raises valid concerns regarding normalization as convention vs necessity, scale confounding with structure, and taxonomy validation vs structural discovery.

**Resolution Path:**

The verification plan addresses this dialectic through:
1. **Foundation verification (H-E1):** Establishes existence (>80% accuracy) before mechanism testing
2. **Sequential mechanism testing (H-M1-M3):** Tests each causal step independently
3. **Gate conditions:** Allow early detection of H0 support (MUST_WORK failures trigger PIVOT/ABANDON)

**Conditions for Thesis Support:**
- All 4 MUST_WORK gates pass (H-E1, H-M1, H-M2, H-M3)
- >80% validation accuracy confirmed (H-E1)
- Mechanism chain validates (normalization + parameter-mass + extraction)

**Conditions for Antithesis Support:**
- H-E1 fails (accuracy ≤50%, near-random)
- H-M1 fails critically (violation >15%, normalization is convention)
- R3 materializes (CV ≥0.15, scale confounds structure)

**Nuanced Outcome Possibilities:**
1. **Full Support:** All hypotheses pass → Thesis validated, approach works across families
2. **Partial Support:** H-M failures → Refined thesis with limitations (e.g., works for standard architectures only)
3. **Antithesis Confirmed:** H-E1 fails → Features insufficient, need complex representations

---

## 6. Executive Summary

**Main Hypothesis:** Lightweight statistical features enable >80% architecture family classification from checkpoints
- ID: weight-stats-classifier, Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (Phase 2A pre-seeded)
- Sub-Hypotheses: 5 total
  - H-E: 1 (Existence), H-M: 3 (Mechanism), H-C: 1 (Condition)
- Phases: 3 phases over 6 weeks
- Critical Gates: 4 MUST_WORK decision points

**Risk Assessment:** Medium
- Primary concerns: R2 (normalization convention), R3 (scale invariance)
- Mitigations: Violation rate tests, CV validation, fallback heuristics

**Immediate Action:** Begin Phase 1 with H-E1 (Statistical Features Sufficiency)

### Key Achievements

- 5 hypotheses across 3 phases (Foundation → Mechanisms → Conditions)
- H0 addressed: "Statistical features do NOT achieve >random classification"
- Scope reduction: 20% (4 BUILD_ON claims excluded from re-verification)

### Verification Execution Order

**Phase 1: Foundation** (2 weeks)
- H-E1: Validate >80% accuracy on TIMM model zoo
- Gate 1: MUST PASS (ABANDON if fails)

**Phase 2: Core Mechanisms** (3 weeks)
- H-M1: Normalization layer fingerprinting (BN vs LN)
- H-M2: Parameter allocation pattern (conv vs linear)
- H-M3: Checkpoint extraction feasibility (<10 min for 50 models)
- Gate 2: H-M1 must pass (PIVOT if fails)

**Phase 2.5: Conditions** (1 week)
- H-C1: Edge case robustness (NFNet, extreme scaling)
- Gate 2.5: Acceptable failure (SHOULD_WORK)

### Critical Decision Points

1. **Gate 1 (Foundation - Week 2):** H-E1 must pass
   - FAIL → ABANDON (features insufficient)
   - PASS → Proceed to Phase 2

2. **Gate 2 (Mechanisms - Week 6):** H-M1 must pass
   - CRITICAL FAIL → PIVOT (test GroupNorm patterns)
   - PASS → Continue mechanism chain

3. **Gate 2.5 (Conditions - Week 7):** Narrow scope
   - Failures document scope limits, don't invalidate core hypothesis

### Open Questions

- How do NormFree networks (NFNets) affect normalization fingerprinting?
- Can parameter-mass ratio handle extreme depth (1000-layer ResNets)?
- Does approach generalize beyond vision (NLP, audio architectures)?

### Recommendations

**Immediate Actions:**
1. Start Phase 1 with H-E1 validation
2. Set up TIMM checkpoint download infrastructure
3. Pre-validate assumptions (A1-A4) on 10-model sample

**Resource Allocation:**
- Phase 1: 2 weeks (H-E1)
- Phase 2: 3 weeks (H-M1-M3)
- Phase 2.5: 1 week (H-C1)
- Total: 6 weeks

**Next Steps:**
1. Review verification plan with stakeholders
2. Run Phase 2C to design detailed experiments
3. Execute hypothesis loop: 2C → 3 → 4 for each hypothesis

---

## 4. Risk Analysis

### 4.1 Assumption-Risk Mapping

| Risk ID | Source | Risk Description | Severity | Affected Hypotheses |
|---------|--------|------------------|----------|-------------------|
| R1 | A1 | TIMM naming misalignment >10% → mislabeled training data | Medium | H-E1, H-M1 |
| R2 | A2 | Normalization choice is convention not paradigm (violation >15%) → features lose power | High | H-M1 |
| R3 | A3 | Parameter-mass ratio scale-variant (CV ≥0.15) → scale confounds structure | High | H-M2 |
| R4 | A4 | Linear classifier insufficient (logistic regression fails) → features not separable | Critical | H-E1, All |

### 4.2 Mitigation Strategies

**R1: TIMM Naming Misalignment**
- **Prevention**: Validate 10-model sample via structural inspection (>90% target)
- **Detection**: Track per-model confidence scores, flag low-confidence predictions
- **Response**: PIVOT → Manual verification for low-confidence subset, add structural validation layer

**R2: Normalization Convention Risk**
- **Prevention**: Test violation rate (≤15% per class threshold)
- **Detection**: Monitor BN-in-Transformer and LN-in-CNN rates
- **Response**: EXPLORE → Add GroupNorm patterns, activation function counts as backup features

**R3: Scale Invariance Failure**
- **Prevention**: Validate CV <0.15 across ResNet-{18,34,50,101,152} before full experiment
- **Detection**: Plot R distributions per family, check for multi-modal patterns
- **Response**: PIVOT → Normalize by model size, use R-rank instead of R-absolute

**R4: Linear Separability Failure**
- **Prevention**: Pre-test with 2D visualization (BN_count vs R scatter plot)
- **Detection**: Logistic regression validation accuracy <75%
- **Response**: ABANDON → Features fundamentally insufficient, need complex representations (GNN/MLP)

### 4.3 Baseline Failure Patterns

| Baseline Limitation | Our Risk | Mitigation |
|---------------------|----------|------------|
| Kofinas GNN: Complex, 50+ hours | Implementation complexity | Use PyTorch built-ins only, <15 tasks budget |
| Zhang: Requires forward passes | Extraction overhead | Checkpoint-only validation in H-M3 |

---
