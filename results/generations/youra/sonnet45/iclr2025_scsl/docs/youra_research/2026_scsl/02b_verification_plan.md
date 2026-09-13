# Verification Plan: Clusterability as Geometric Fairness Diagnostic for Self-Supervised Learning

**Date:** 2026-03-19
**Hypothesis ID:** H-ClusterableSSL-v1
**Confidence:** 0.85
**Total Hypotheses:** 3

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under self-supervised learning on spurious correlation datasets (Waterbirds), if embedding geometry exhibits high subgroup clusterability (AMI ≥0.4), then cluster-balanced retraining improves worst-group accuracy by ≥2pp, because spurious features manifest as geometrically separable density modes that can be identified and reweighted without labels.

### 1.2 Alternative Hypothesis (H0)
There is no significant difference in WGA improvement between models with AMI ≥0.4 vs AMI <0.3 after cluster-balanced retraining (both yield <0.5pp gain).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Waterbirds (standard) | 4-group structure (landbird/waterbird × land/water background) provides ground truth for AMI evaluation. Standard spurious correlation benchmark with known minority groups. |
| **Model** | SimCLR (ResNet-50 backbone), LA-SSL (ResNet-50) | SimCLR tested in Mehta et al., enabling direct comparison. LA-SSL provides learning-speed intervention for Tier 2 geometry test. |

**Dataset Details:**
- Source: GroupDRO benchmark (4,795 train, 1,199 val, 5,794 test images)
- Path: From validated Phase 0 infrastructure

**Model Details:**
- Type: Self-supervised contrastive learning
- Source: sthalles/SimCLR (2480 stars) + LA-SSL implementation from arxiv_2311_16361

### 1.4 Baseline Methods

| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|------------------|
| Frozen ViT-H-14 + Linear ERM | 90.13% WGA | Waterbirds | Achieves high WGA but doesn't explain WHY (our contribution: dissociate linear vs cluster geometry) |
| GroupDRO | +10.9pp WGA | Waterbirds | Requires group labels (our approach is label-free) |
| Simple Diagnostics (loss variance, skewness) | - | - | We provide geometric clustering as novel diagnostic (AMI) |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Spurious features manifest as geometrically separable clusters in SSL embedding space | InfoNCE loss creates dense similarity regions for shared spurious features | k-means fails, AMI ≈0, clustering assumption invalid |
| A2 | Clusterability (AMI) is dissociable from linear separability | High-capacity models may disperse features across dimensions while maintaining linear boundaries | AMI adds no independent information beyond linear probe |
| A3 | Differentiable AMI surrogate approximates true k-means AMI | Sinkhorn-Knopp (SwAV) and soft assignments are established techniques | Tier 3 clusterability penalty may fail if soft clustering misses sharp boundaries |
| A4 | Core and spurious features occupy partially orthogonal subspaces | LA-SSL's success suggests separability exists | Geometric penalty may degrade core performance alongside spurious suppression |
| A5 | Waterbirds' 4-group structure is representative | Standard benchmark, CelebA/CivilComments planned for future validation | Findings may not generalize to datasets with more complex spurious structure |

### 1.6 Research Gap & Novelty

**Preserved Novelty:**
First work to (1) dissociate linear separability from geometric clusterability in SSL embeddings, (2) link LA-SSL's learning-speed intervention to geometric topology changes, (3) propose explicit clusterability penalty as SSL training objective.

**Key Innovation:**
Clusterability (AMI) as both diagnostic tool (predicts fairness intervention efficacy) and training objective (controllable via λ penalty). Bridges dynamics (LA-SSL) to static geometry (clustering).

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | READY |
| H-M-integrated | Mechanism | MUST_WORK (M1+M2), M3 can fail | H-E1 | NOT_STARTED |
| H-C1 | Condition | SHOULD_WORK (informative) | H-E1, H-M-integrated | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

#### H-E1: Clusterability Diagnostic for Fairness Intervention Efficacy

**Type:** EXISTENCE

**Statement:** Under SSL training on Waterbirds, if frozen embeddings exhibit high subgroup clusterability (AMI ≥0.4), then cluster-balanced retraining improves worst-group accuracy by ≥2pp, because spurious features manifest as geometrically separable density modes that can be identified and reweighted without labels.

**Rationale:** Establishes whether spurious correlations create measurable geometric clusters in SSL embeddings and whether clusterability (AMI) predicts when fairness interventions will succeed. Provides label-free diagnostic for practitioners to select appropriate rebalancing strategies without requiring group annotations.

**Variables:**
- IV: Embedding Clusterability (AMI) - Adjusted Mutual Information between k-means clusters (k=4) and true subgroups
- DV: WGA Improvement from Cluster-Balanced Retraining (ΔWGA in percentage points)
- CV: Model Architecture (ResNet-50, ViT-H-14), ERM Training Protocol (grid search LR/WD, 20 epochs, batch 32)

**Verification Protocol:**
1. Train SimCLR and LA-SSL on Waterbirds, freeze embeddings, compute AMI via k-means (k=4) vs true subgroups
2. Train linear ERM baseline using Mehta et al. protocol (grid search, 20 epochs), measure baseline WGA
3. Apply cluster-balanced retraining (reweight samples to balance cluster membership), measure ΔWGA
4. Stratify models into high-AMI (≥0.4) and low-AMI (<0.3) groups, compare ΔWGA distributions
5. Compute AMI diagnostic AUROC for predicting ΔWGA ≥1pp, compare against loss variance/skewness baselines

**Success Criteria (PoC):**
- Primary: High-AMI group mean ΔWGA ≥2pp with 95% CI excluding zero; Low-AMI group <0.5pp
- Secondary: AMI diagnostic AUROC >0.80 vs simpler baselines; AMI and linear separability dissociated (r<0.9)

**Gate:**
- Type: MUST_WORK
- If Fail: STOP - clustering assumption violated (R1), PIVOT to continuous density metrics

**Prerequisites:** None (foundational hypothesis)

**Source:** Phase 2A Section 1.6 (Prediction P1), Section 1.3 (Mechanism Step 2)

---

#### H-M-integrated: Three-Step Causal Mechanism from SSL Dynamics to Geometry to Fairness

**Type:** MECHANISM

**Statement:** The causal mechanism operates through: (M1) InfoNCE contrastive loss creates dense spurious feature clusters from globally shared backgrounds leading to high AMI, (M2) High clusterability indicates minority groups occupy distinct density modes exploitable by linear ERM and improvable via cluster-based reweighting, (M3) LA-SSL learning-speed resampling disperses spurious density structure (AMI reduction ≥30%) while preserving linear separability (ΔAUC <0.05), explaining robustness gains through geometric reshaping.

**Rationale:** Tests the complete causal chain linking SSL training dynamics (InfoNCE, learning-speed sampling) to embedding geometry (clusterability, separability) to fairness outcomes (WGA improvement). Explains why frozen high-capacity embeddings achieve 90% WGA and provides mechanistic understanding of LA-SSL's robustness benefits.

**Variables:**
- IV: SSL Training Method (Standard SimCLR vs LA-SSL with learning-speed resampling)
- DV: Embedding Clusterability (AMI), Subgroup Linear Separability (AUC of linear probe), WGA Improvement (ΔWGA)
- CV: Model Architecture (ResNet-50 matched), Training Epochs, Augmentation Protocol

**Verification Protocol:**
1. Train Standard SimCLR and LA-SSL on Waterbirds (matched architecture, epochs), freeze both encoders
2. Test M1: Verify standard SSL produces AMI ≥0.4 (spurious clusters exist from InfoNCE optimization)
3. Test M2: Correlate AMI with ΔWGA from cluster-balanced retraining (clusterability predicts intervention efficacy)
4. Test M3: Compare Standard vs LA-SSL metrics - compute ΔAMI ≥30% reduction AND linear separability ΔAUC <0.05
5. Statistical validation: paired t-tests within-architecture, Pearson correlation AMI↔ΔWGA, dissociation test AMI vs linear AUC

**Success Criteria (PoC):**
- Primary: All three mechanism steps validated (M1: AMI≥0.4, M2: AMI→ΔWGA correlation significant, M3: LA-SSL reduces AMI ≥30% with ΔAUC<0.05)
- Secondary: Evidence for geometry reshaping not signal suppression (LA-SSL maintains WGA while reducing AMI)

**Gate:**
- Type: MUST_WORK (M1+M2 must pass, M3 can fail gracefully - Tiers 1-2 still valid)
- If M1/M2 Fail: Document clustering as ornamental, PIVOT to linear separability as sole predictor
- If M3 Fail: LA-SSL mechanism unexplained but Tiers 1-2 publishable

**Prerequisites:** H-E1 (requires AMI diagnostic validation)

**Source:** Phase 2A Section 1.3 (Causal Mechanism - 3 steps), Predictions P2

---

#### H-C1: Boundary Conditions - Model Capacity and Dataset Structure

**Type:** CONDITION

**Statement:** The clusterability mechanism operates effectively in mid-capacity models (ResNet-50 with 88.5% baseline WGA, 11.5% headroom) on datasets with discrete minority groups (Waterbirds 4-group structure), but hits ceiling effects in high-capacity models (ViT-H-14 at 90%+ baseline, <10% headroom) and fails on datasets without clear spurious group structure where clustering assumptions break down.

**Rationale:** Documents boundary conditions and generalization limits to guide practitioners on when clusterability-based interventions will (and won't) work. Critical for preventing misapplication to unsuitable contexts (high-capacity models already at ceiling, continuous spurious structures, cross-domain settings).

**Variables:**
- IV: Model Capacity (ResNet-50 mid-capacity vs ViT-H-14 high-capacity), Dataset Structure (discrete 4-group vs continuous)
- DV: Baseline WGA, Intervention Headroom (100% - baseline WGA), ΔWGA from cluster-balanced retraining
- CV: Training Protocol, Random Seed (≥5 seeds)

**Verification Protocol:**
1. Train Standard SSL on both ResNet-50 and ViT-H-14, measure baseline WGA and AMI for both architectures
2. Apply cluster-balanced retraining to both, measure ΔWGA absolute and headroom-normalized (ΔWGA / available_headroom)
3. Test ceiling hypothesis: ViT-H-14 shows <1pp gain despite AMI ≥0.4 (limited headroom constrains improvement)
4. Test architecture generalization: verify AMI→ΔWGA relationship consistency across ResNet and ViT families
5. Document negative cases: identify when mechanism fails (capacity ceiling, dataset structure mismatch)

**Success Criteria (PoC):**
- Primary: ResNet-50 shows higher absolute ΔWGA than ViT-H-14 (capacity/headroom effect documented)
- Secondary: AMI→ΔWGA relationship generalizes across architectures (mechanism not architecture-specific)

**Gate:**
- Type: SHOULD_WORK (informative - negative results publishable as boundary knowledge)
- All outcomes valuable: generalization confirmed OR boundaries documented

**Prerequisites:** H-E1 (requires AMI diagnostic), H-M-integrated (requires mechanism validation)

**Source:** Phase 2A Section 1.5 (Scope Boundaries), Key Assumptions A2, A5

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 (Foundation - READY)
  │
  ▼
H-M-integrated (Mechanism - depends on H-E1)
  │
  ▼
H-C1 (Boundaries - depends on H-E1, H-M-integrated)
```

### 3.2 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 3 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Foundation]
    H-E1 (Clusterability Diagnostic - Existence)
    │  Validates: AMI ≥0.4 predicts ΔWGA ≥2pp
    │  Gate: MUST_PASS (hypothesis dies if clustering doesn't work)
    │
    ▼
[Level 1 - Mechanism Chain]
    H-M-integrated (3-Step Mechanism: InfoNCE→geometry→fairness)
    │  Depends on: H-E1 (requires AMI diagnostic validation)
    │  Tests: M1 (InfoNCE clusters), M2 (AMI→ΔWGA), M3 (LA-SSL geometry)
    │  Gate: MUST_PASS (at least M1+M2, M3 can fail gracefully)
    │
    ▼
[Level 2 - Boundary Conditions]
    H-C1 (Capacity Ceiling & Dataset Structure Boundaries)
    │  Depends on: H-E1, H-M-integrated
    │  Documents: When mechanism works vs fails
    │  Gate: INFORMATIVE (negative results valuable)
    │
    ▼
[Terminal - Complete]

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M-integrated → H-C1
Total Depth: 3 levels (fully sequential)
═══════════════════════════════════════════════════════════
```

### 3.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 3 Hypotheses (PoC Verification Mode)
═══════════════════════════════════════════════════════════════════════
Phase/Hypothesis    │ W1-2    │ W3-4    │ W5      │ W6      │
────────────────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 1: Foundation │         │         │         │         │
  H-E1 (Diagnostic) │ ████████│         │         │         │
  [Gate 1]          │         │ ◆       │         │         │
────────────────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 2: Mechanisms │         │         │         │         │
  H-M-integrated    │         │ ████████│ ████    │         │
  (3-step chain)    │         │         │         │         │
  [Gate 2]          │         │         │         │ ◆       │
────────────────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 2.5: Boundary │         │         │         │         │
  H-C1 (Conditions) │         │         │         │ ████    │
  [Gate 2.5]        │         │         │         │         │ ◆
────────────────────┼─────────┼─────────┼─────────┼─────────┤
═══════════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point

Total Duration: 6 weeks (2 + 3 + 1)
═══════════════════════════════════════════════════════════════════════
```

### 3.4 Critical Path Analysis

**Critical Path:** H-E1 → H-M-integrated → H-C1

**Total Duration:** 6 weeks
- Week 1-2: H-E1 (AMI diagnostic - clusterability predicts intervention efficacy)
- Week 3-5: H-M-integrated (3-step mechanism validation)
- Week 6: H-C1 (Capacity ceiling & dataset structure boundaries)

**Slack Available:** 0 weeks (fully sequential dependency chain)

**Gate Decision Points:**
1. **Gate 1 (Week 2):** If AMI ≈0, STOP (clustering assumption violated - R1)
2. **Gate 2 (Week 5):** M1+M2 must pass, M3 can fail gracefully (Tiers 1-2 still valid)
3. **Gate 2.5 (Week 6):** All outcomes publishable (boundary documentation)

---

## 4. Risk Analysis

### 4.1 Risk Summary Table

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    RISK SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| ID | Risk | Source | Severity | Affected | Mitigation |
|----|------|--------|----------|----------|------------|
| R1 | Spurious features not clusterable (AMI≈0) | A1 | High | H-E1, H-M-integrated | Test early, pivot to density metrics if needed |
| R2 | AMI perfectly correlated with linear separability | A2 | Medium | H-E1, H-M-integrated | Test dissociation across capacities, document as complementary |
| R3 | Soft AMI approximation poor (r<0.7 vs hard AMI) | A3 | Medium | H-M-integrated (M3) | Validate before Tier 3, fallback to Tiers 1-2 only |
| R4 | Core-spurious entanglement (cannot separate) | A4 | Medium | H-M-integrated, H-C1 | Monitor core accuracy in λ sweep, document trade-offs |
| R5 | Findings not generalizable beyond Waterbirds | A5 | Medium | All | Test multi-architecture, scope boundaries clearly |

Critical Risks: 0
High Risks: 1 (R1)
Medium Risks: 4 (R2-R5)
Low Risks: 0

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 4.2 Detailed Risk Analysis

**Risk R1: Spurious Features Not Geometrically Clusterable (HIGH)**

**Source:** A1 - Spurious features manifest as geometrically separable clusters

**Description:** If spurious features exist as smooth continuous manifolds rather than discrete clusters, k-means will fail and AMI ≈0.

**Mitigation:**
1. **Prevention:** Test clustering assumption early in H-E1 - if AMI <0.2, flag immediately
2. **Detection:** Monitor AMI distribution across seeds; if consistently near-zero, assumption fails
3. **Response:** PIVOT to continuous density metrics (kernel density, local outlier factor)

**Early Warning:** Standard SSL AMI <0.2 across ≥3 seeds, silhouette score <0.3

---

**Risk R2: AMI and Linear Separability Perfectly Correlated (MEDIUM)**

**Source:** A2 - AMI is dissociable from linear separability

**Description:** If correlation r>0.9, clusterability adds no independent diagnostic value.

**Mitigation:**
1. **Prevention:** Test both metrics across diverse capacities (ResNet-50, ViT-H-14)
2. **Detection:** Compute Pearson correlation; if r>0.9, perfect correlation detected
3. **Response:** Reframe as "complementary metric," document correlation as finding

**Early Warning:** Pearson correlation AMI vs linear AUC >0.85 across models

---

**Risk R3: Differentiable AMI Surrogate Poor Approximation (MEDIUM)**

**Source:** A3 - Soft clustering approximates k-means AMI

**Description:** Soft clustering may miss sharp boundaries that hard k-means captures.

**Mitigation:**
1. **Prevention:** Validate soft vs hard AMI correlation BEFORE Tier 3 training (<1 day)
2. **Detection:** If correlation <0.7, soft clustering inadequate
3. **Response:** Use hard k-means with stop-gradient OR skip Tier 3, publish Tiers 1-2 only

**Early Warning:** Soft AMI vs hard AMI correlation <0.7 on validation embeddings

---

**Risk R4: Core-Spurious Feature Entanglement (MEDIUM)**

**Source:** A4 - Core and spurious features partially orthogonal

**Description:** If entangled, geometric penalties degrade core accuracy alongside spurious suppression.

**Mitigation:**
1. **Prevention:** Monitor core task accuracy throughout λ sweep
2. **Detection:** If core accuracy drops >2pp when AMI decreases, entanglement detected
3. **Response:** Document as fundamental limitation, identify entanglement threshold

**Early Warning:** λ sweep shows monotonic core accuracy decline as AMI decreases

---

**Risk R5: Waterbirds-Specific Findings Not Generalizable (MEDIUM)**

**Source:** A5 - Waterbirds' 4-group structure is representative

**Description:** Findings may not transfer to hierarchical structures, continuous correlations, or different modalities.

**Mitigation:**
1. **Prevention:** Test across multiple architectures (ResNet, ViT) within Waterbirds
2. **Detection:** H-C1 explicitly tests boundary conditions
3. **Response:** Clearly document applicability boundaries, recommend CelebA/CivilComments validation

**Early Warning:** H-C1 shows mechanism fails on datasets without 4-group structure

---

## 5. Dialectical Analysis

### 5.1 Thesis

**Core Claim:** Spurious correlations in SSL embeddings manifest as geometric clusters measurable via AMI, which diagnoses fairness intervention efficacy and can be explicitly controlled during training.

**Supporting Evidence:**
1. InfoNCE creates dense similarity structure for shared spurious features (Causal Step M1)
2. High clusterability enables intervention beyond linear ERM baseline (Causal Step M2)
3. LA-SSL reshapes geometry mechanistically, reducing AMI while preserving separability (Causal Step M3)
4. Frozen ViT-H-14 achieves 90.13% WGA (Mehta et al.) - validates embeddings contain fairness structure

**Strengths:**
- Dissociates geometric clusterability from linear separability (independent dimensions)
- Provides label-free diagnostic (AMI) for predicting intervention efficacy
- Explains established phenomena (LA-SSL, frozen embeddings) through unified framework
- Clear falsification: AMI thresholds, AUROC >0.80, quantitative predictions with 95% CI

**Expected Outcomes:**
- P1: High-AMI (≥0.4) gains ΔWGA ≥2pp; Low-AMI (<0.3) gains <0.5pp
- P2: LA-SSL reduces AMI ≥30% while maintaining linear separability (ΔAUC <0.05)
- P3: Clusterability penalty enables ResNet-50 to reach 90%+ WGA

### 5.2 Antithesis

**Null Hypothesis (H0):** No difference in WGA improvement between AMI ≥0.4 vs AMI <0.3 models (both yield <0.5pp gain).

**Counter-Arguments:**
1. Mehta et al. achieve 90% WGA using linear ERM alone - clustering may be ornamental
2. High-capacity models may have low AMI despite high WGA (clusterability is diagnostic artifact)
3. Differentiable AMI surrogate may fail (R3), making Tier 3 infeasible
4. Core-spurious entanglement may prevent separation (R4)

**Potential Failure Points:**
- R1 (High): Spurious features form continuous manifolds not discrete clusters → AMI ≈0
- R2 (Medium): AMI perfectly correlates with linear separability (r>0.9) → no independent value
- R3 (Medium): Soft clustering poor approximation → Tier 3 fails
- R4 (Medium): Entanglement prevents fairness-utility separation

**H0 Support Conditions:**
- Standard SSL produces AMI <0.2 across seeds (clustering fails)
- High-AMI and low-AMI models show indistinguishable ΔWGA (p>0.05)
- AMI diagnostic AUROC ≤0.80 vs simpler baselines
- LA-SSL reduces both AMI and linear separability equally (signal suppression not geometry reshaping)

### 5.3 Synthesis

**Balanced Assessment:**

The hypothesis presents a testable claim that clusterability diagnoses and enables fairness interventions. However, H0 raises valid concerns that clustering may be diagnostic artifact rather than causal mechanism.

**Resolution Path:**

The verification plan addresses this dialectic through three-tier hierarchical testing:

1. **H-E1 (Foundation):** Establishes clustering existence before mechanism - early R1 detection
2. **H-M-integrated (Mechanism):** Tests causal chain with graceful degradation (M1+M2 must pass, M3 can fail)
3. **H-C1 (Boundaries):** Explicitly tests H0's objections (capacity ceiling, architecture-specific effects)

**Thesis Support Conditions:**
- H-E1 passes: AMI ≥0.4 with high-AMI→ΔWGA correlation (p<0.01)
- H-M-integrated M1+M2 pass: InfoNCE creates clusters AND AMI predicts efficacy
- AMI dissociates from linear separability (r<0.9): independent diagnostic value

**Antithesis Support Conditions:**
- H-E1 fails: AMI <0.2 consistently → clustering assumption violated
- M2 fails: No AMI→ΔWGA correlation → clusterability ornamental
- AMI perfectly correlates with linear AUC (r>0.9) → redundant metric

**Outcome Possibilities:**
1. **Full Support:** All hypotheses pass → Thesis validated, clusterability is causal
2. **Partial - Diagnostic Only:** H-E1 + M1+M2 pass, M3 fails → AMI valid diagnostic, LA-SSL unexplained
3. **Partial - Ornamental:** H-E1 passes, M2 fails → Clustering descriptive not causal
4. **Antithesis:** H-E1 fails or M1+M2 both fail → Clustering invalid, PIVOT to alternatives

**Robustness:**
- Dissociation test (AMI vs linear AUC) directly addresses independent value question
- Three-tier structure allows graceful degradation
- H-C1 tests boundary conditions where thesis should fail (capacity ceiling)
- Pre-registered falsification prevents post-hoc rationalization

---

## 6. Executive Summary

**Main Hypothesis:** Under SSL on Waterbirds, if embedding clusterability AMI ≥0.4, then cluster-balanced retraining improves WGA by ≥2pp, because spurious features form geometrically separable density modes.

- ID: H-ClusterableSSL-v1, Confidence: 0.85
- H0: No difference between AMI ≥0.4 vs AMI <0.3 models (both <0.5pp gain)

**Verification Structure:**
- Mode: Incremental (Phase 2A data-driven)
- Sub-Hypotheses: 3 total (H-E1 diagnostic, H-M-integrated 3-step mechanism, H-C1 boundaries)
- Phases: 3 phases over 6 weeks (Foundation → Mechanism → Boundary)
- Critical Gates: 3 decision points (MUST_PASS → MUST_PASS M1+M2 → INFORMATIVE)

**Risk Assessment:** High (R1 - clustering assumption could fail)
- Primary concerns: Spurious features may not cluster (AMI≈0), clusterability may correlate perfectly with linear separability
- Mitigation: Early detection in H-E1 (Week 1-2), pivot to density metrics if R1 materializes

**Immediate Action:** Begin Phase 2C with H-E1 (READY status) - clusterability diagnostic validation

---

## 7. Next Steps

1. **Execute Phase 2C:** Generate experiment design for H-E1 (first READY hypothesis)
2. **Sequential execution:** H-E1 → H-M-integrated → H-C1
3. **Use hypothesis-loop or phase2c-experiment-design skill**

**Verification Order:**
- **Step 1:** H-E1 (Week 1-2) - AMI diagnostic validation
- **Step 2:** Gate 1 decision - If PASS proceed, if FAIL (AMI<0.2) STOP and pivot
- **Step 3:** H-M-integrated (Week 3-5) - 3-step mechanism chain
- **Step 4:** Gate 2 decision - M1+M2 must pass, M3 can fail gracefully
- **Step 5:** H-C1 (Week 6) - Boundary documentation
- **Step 6:** Gate 2.5 - All outcomes publishable

---

**Files Generated:**
- verification_state.yaml (state tracking for hypothesis loop)
- 02b_verification_plan.md (this document)

**Hypothesis Tasks Created in Archon:**
- H-E1: 09493c9a-fd3e-47e8-9714-9d524aefb12c
- H-M-integrated: bde6f54a-0c82-41d5-9433-b20ceede6888
- H-C1: 8499eff0-898c-411e-94a7-1a622289bee6

**Pipeline Status:**
- Phase 2B: COMPLETE (done)
- Phase 2C: READY (next phase)
