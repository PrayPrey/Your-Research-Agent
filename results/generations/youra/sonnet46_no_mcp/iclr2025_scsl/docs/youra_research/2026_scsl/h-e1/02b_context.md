# Hypothesis Context: H-E1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-05-04
**Main Hypothesis:** Temporal Feature Learning Gap: Measuring and Exploiting the Spurious-Before-Core Dynamics of SGD
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under standard ERM training on Waterbirds, if checkpoint linear probing is applied every 2 epochs, then delta(t) = spurious_probe_acc(t) - core_probe_acc(t) > 0 for a statistically significant contiguous window covering ≥10% of training epochs, replicated across ≥3 random seeds and on CelebA, because SGD simplicity bias preferentially encodes lower-complexity (spurious) features before higher-complexity (core) features.

### Type
EXISTENCE

### Rationale
This is the foundational empirical claim: the temporal gap must demonstrably exist before any downstream mechanistic or intervention claims can be made. Establishing delta(t) > 0 with statistical significance across seeds and datasets provides the primary scientific contribution — a reproducible, standardized measurement protocol for feature learning dynamics in spurious correlation settings.

---

## Verification Protocol

### Conceptual Test
1. Train ResNet-50 ERM on Waterbirds for full schedule (~300 epochs); save checkpoint every 2 epochs (≥150 checkpoints total)
2. At each checkpoint, extract frozen backbone features for all samples in held-out validation split
3. Fit L2 logistic regression probe for spurious label (background) and separately for core label (bird species); record accuracies
4. Compute delta(t) = spurious_acc(t) - core_acc(t) at each checkpoint; run paired t-test across seeds at each timestep
5. Replicate full protocol on CelebA (hair color spurious / gender core); compare delta(t) profiles

### Success Criteria
- Primary: delta(t) > 0 for contiguous window ≥10% of training epochs, paired t-test p < 0.05 across ≥3 seeds
- Secondary: Gap area A = sum(max(delta(t), 0)) > 0 with 95% CI excluding zero; t* identified consistently (std < 10 epochs across seeds)
- Replication: Effect replicated on CelebA (same directional finding)

### Variables
- **Independent Variable:** Training epoch (continuous, 0 to max_epochs, checkpointed every 2 epochs); probe label type (spurious vs. core)
- **Dependent Variable:** delta(t) = spurious_probe_acc(t) - core_probe_acc(t) on held-out validation split
- **Controlled Variables:** ResNet-50 (ImageNet pretrained), SGD (lr=1e-3, momentum=0.9, wd=1e-4), L2 logistic regression probe, ≥3 random seeds

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** Waterbirds (primary), CelebA (replication)
- **Type:** standard
- **Source:** Sagawa et al. 2020 (GroupDRO paper); kohpangwei/group_DRO GitHub
- **Path:** kohpangwei/group_DRO (GitHub) — includes dataset loaders
- **Hypothesis Fit:** Canonical spurious correlation benchmark with well-documented 15pp worst-group accuracy gap for ERM; spurious feature (background) measurably simpler than core feature (bird species); established WGA evaluation protocol

### Selected Model
- **Name:** ResNet-50
- **Type:** CNN image classifier
- **Source:** torchvision pretrained on ImageNet
- **Hypothesis Fit:** Standard architecture for Waterbirds/CelebA experiments across all baseline papers (GroupDRO, JTT, DFR); enables direct comparison

---

## Baseline & Comparison Targets

> **Note:** This section provides baseline context for understanding expected effect sizes (H-E1 is EXISTENCE type).

### Baseline Methods
| Method | Performance | Dataset | Notes |
|--------|-------------|---------|-------|
| ERM | ~72% WGA | Waterbirds | Lower bound; does not address spurious correlations |
| JTT | ~86% WGA | Waterbirds | Annotation-free heuristic; requires second training run |
| DFR | ~88% WGA | Waterbirds | Strongest annotation-free baseline; no mechanistic explanation |
| GroupDRO | ~91% WGA | Waterbirds | Upper bound; requires group annotations at training time |

### Baseline Performance
ERM achieves ~72% worst-group accuracy on Waterbirds, representing the baseline without any spurious correlation mitigation. The ~19pp gap between ERM and GroupDRO represents the maximum improvement space.

### Gap Analysis
H-E1 does not directly target WGA improvement. Its primary metric is the existence of delta(t) > 0 in checkpoint linear probing. The baseline context establishes that ERM fails on spurious correlations, motivating the need to understand the temporal feature learning dynamics.

---

## Dependencies and Gate Conditions

### Prerequisites
None (H-E1 is the root hypothesis)

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow

**Consequence if Fails:** IF delta(t) ≤ 0 at all checkpoints across all seeds on both Waterbirds and CelebA → ABANDON: H0 supported; hypothesis collapses. Return to Phase 2A for hypothesis revision.

**Phase Assignment:** Phase 1 — Foundation (Weeks 1-2)

**Estimated Duration:** 2 weeks (~18 GPU-hours: ~10 GPU-hours Waterbirds + ~8 GPU-hours CelebA + probe fitting)

---

## Dependency Context

### Relationship to Other Hypotheses
- H-E1 has no prerequisites — it is the root node of the DAG
- H-M1, H-M2, H-M3, H-M4 all depend on H-E1 (directly or transitively)
- H-M3 reuses H-E1 checkpoints (no additional training cost)
- Gate 1 decision: If H-E1 fails → STOP entire verification chain

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

**Phase 2C will:**
1. Load this file instead of full Phase 2B roadmap (91% smaller)
2. Search for implementation patterns (Archon, Exa MCP)
3. Design concrete experiment specification (Level 1.5)
4. Output: h-e1/02c_experiment_brief.md

---

*Generated by Phase 2C Workflow (JIT) — 2026-05-04*
*Optimized for single-hypothesis experiment design*
