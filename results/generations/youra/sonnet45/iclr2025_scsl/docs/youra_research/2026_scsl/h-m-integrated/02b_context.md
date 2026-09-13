# Hypothesis Context: h-m-integrated

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-03-20
**Main Hypothesis:** Clusterability as Geometric Fairness Diagnostic for Self-Supervised Learning
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
The 3-step causal mechanism operates as: (M1) InfoNCE contrastive loss creates dense spurious feature clusters (shared backgrounds) leading to high AMI, (M2) High clusterability enables minority groups to occupy distinct density modes exploitable by linear ERM and further improved by cluster-based reweighting, (M3) LA-SSL learning-speed resampling disperses spurious density structure (reducing AMI by ≥30%) while preserving linear separability (ΔAUC <0.05)

### Type
MECHANISM

### Rationale
Tests the complete causal chain linking SSL training dynamics (InfoNCE, learning-speed sampling) to embedding geometry (clusterability, separability) to fairness outcomes (WGA improvement). Explains why frozen high-capacity embeddings achieve 90% WGA and provides mechanistic understanding of LA-SSL's robustness benefits.

---

## Verification Protocol

### Conceptual Test
1. Train Standard SimCLR and LA-SSL on Waterbirds (matched architecture, epochs), freeze both encoders
2. Test M1: Verify standard SSL produces AMI ≥0.4 (spurious clusters exist from InfoNCE optimization)
3. Test M2: Correlate AMI with ΔWGA from cluster-balanced retraining (clusterability predicts intervention efficacy)
4. Test M3: Compare Standard vs LA-SSL metrics - compute ΔAMI ≥30% reduction AND linear separability ΔAUC <0.05
5. Statistical validation: paired t-tests within-architecture, Pearson correlation AMI↔ΔWGA, dissociation test AMI vs linear AUC

### Success Criteria
- **Primary:** All three mechanism steps validated (M1: AMI≥0.4, M2: AMI→ΔWGA correlation significant, M3: LA-SSL reduces AMI ≥30% with ΔAUC<0.05)
- **Secondary:** Evidence for geometry reshaping not signal suppression (LA-SSL maintains WGA while reducing AMI)

### Variables
- **Independent Variable:** SSL Training Method (Standard SimCLR vs LA-SSL with learning-speed resampling)
- **Dependent Variable:** Embedding Clusterability (AMI), Subgroup Linear Separability (AUC of linear probe), WGA Improvement (ΔWGA)
- **Controlled Variables:** Model Architecture (ResNet-50 matched), Training Epochs, Augmentation Protocol

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** Waterbirds
- **Type:** standard
- **Source:** GroupDRO benchmark
- **Path:** From validated Phase 0 infrastructure (4,795 train, 1,199 val, 5,794 test images)
- **Hypothesis Fit:** 4-group structure (landbird/waterbird × land/water background) provides ground truth for AMI evaluation. Standard spurious correlation benchmark with known minority groups.

### Selected Model
- **Name:** SimCLR (ResNet-50 backbone), LA-SSL (ResNet-50)
- **Type:** Self-supervised contrastive learning
- **Source:** sthalles/SimCLR (2480 stars) + LA-SSL implementation from arxiv_2311_16361
- **Hypothesis Fit:** SimCLR tested in Mehta et al., enabling direct comparison. LA-SSL provides learning-speed intervention for Tier 2 geometry test.

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|------------------|
| Frozen ViT-H-14 + Linear ERM | 90.13% WGA | Waterbirds | Achieves high WGA but doesn't explain WHY (our contribution: dissociate linear vs cluster geometry) |
| GroupDRO | +10.9pp WGA | Waterbirds | Requires group labels (our approach is label-free) |
| Simple Diagnostics (loss variance, skewness) | - | - | We provide geometric clustering as novel diagnostic (AMI) |

### Baseline Performance
Standard SimCLR expected to produce AMI ≥0.4; Linear ERM expected to achieve ~88.5% baseline WGA on ResNet-50

### Gap Analysis
Our contribution: dissociate linear vs cluster geometry, provide label-free diagnostic (AMI), explain LA-SSL through geometric reshaping

---

## Dependencies and Gate Conditions

### Prerequisites
- h-e1 (VALIDATED) - Requires AMI diagnostic validation before testing mechanism

### Gate Information

**Gate Type:** MUST_WORK (M1+M2 must pass, M3 can fail gracefully)
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:**
- If M1/M2 Fail: Document clustering as ornamental, PIVOT to linear separability as sole predictor
- If M3 Fail: LA-SSL mechanism unexplained but Tiers 1-2 publishable

**Phase Assignment:** Phase 2 (Week 3-5)

**Estimated Duration:** 3 weeks

---

## Dependency Context

### Relationship to Other Hypotheses
Depends on h-e1 (establishes AMI diagnostic validity). Provides mechanistic explanation for h-e1 findings. Required prerequisite for h-c1 (boundary conditions).

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** IN_PROGRESS
**Workflow Status:** ACTIVE

---

## Phase 2C Usage Notes

**This context file provides:**
1. Complete hypothesis specification for experiment design
2. Gate conditions for prerequisite validation
3. Dependency information for controlled experiments
4. Success criteria for evaluation design
5. **Baseline comparison targets (CRITICAL for H-CP* hypotheses)**

**Phase 2C will:**
1. Load this file instead of full Phase 2B roadmap (91% smaller)
2. Search for implementation patterns (Archon, Exa MCP)
3. Use baseline metrics to set comparison targets
4. Design concrete experiment specification (Level 1.5)
5. Output: h-m-integrated/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes
- **H-M* (Mechanism)**: Baseline to understand improvement potential
- **H-C* (Condition)**: Baseline to identify scope boundaries
- **H-CP* (Comparison)**: **MANDATORY** - Direct comparison with baseline methods

---

*Generated by Phase 2C Workflow (JIT)*
*Optimized for single-hypothesis experiment design*
