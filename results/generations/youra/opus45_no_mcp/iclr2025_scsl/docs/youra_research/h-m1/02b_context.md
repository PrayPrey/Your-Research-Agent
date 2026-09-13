# Hypothesis Context: H-M1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-08-19
**Main Hypothesis:** Shortcut Crystallization Zone
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under continued training past early epochs, if spurious features gain initial advantage, then the feedback loop becomes self-reinforcing at the crystallization point, because gradient starvation amplifies dominant feature signal.

### Type
MECHANISM

### Rationale
Tests the transition from linear to accelerating dynamics. Key mechanism claim linking established gradient starvation to novel crystallization timing.

---

## Verification Protocol

### Conceptual Test
1. Track gradient magnitude for spurious vs core feature classifiers during training
2. Compute ratio of minority feature gradient to majority feature gradient per epoch
3. Identify epoch where ratio shows inflection (acceleration in decrease)
4. Correlate inflection timing with d²WGA/dt² peak from H-E1
5. Test temporal correlation (within 5 epochs)

### Success Criteria
- Primary: Gradient ratio inflection correlates with WGA acceleration (r > 0.7)
- Secondary: Inflection occurs before 50% of training

### Variables
- **Independent Variable:** Training epoch
- **Dependent Variable:** Minority feature gradient magnitude ratio
- **Controlled Variables:** Architecture (ResNet-50), batch size (128), optimizer (SGD)

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** Waterbirds (primary), CelebA, ColoredMNIST
- **Type:** standard
- **Source:** WILDS benchmark suite (p-lambda/wilds)
- **Path:** Downloaded via wilds.get_dataset()
- **Hypothesis Fit:** Standard spurious correlation benchmarks with group annotations enabling WGA computation

### Selected Model
- **Name:** ResNet-50
- **Type:** CNN
- **Source:** torchvision.models.resnet50(pretrained=True)
- **Hypothesis Fit:** Standard architecture used in group robustness literature; enables comparison with prior work

---

## Baseline & Comparison Targets

### Baseline Methods
| Method | Performance | Dataset |
|--------|-------------|---------|
| ERM (Empirical Risk Minimization) | ~60-75% WGA | Waterbirds |
| Group DRO | ~85-90% WGA | Waterbirds |
| JTT (Just Train Twice) | ~80-85% WGA | Waterbirds |

### Baseline Performance
ERM achieves 60-75% WGA on Waterbirds, which is the expected starting point for crystallization analysis.

### Gap Analysis
This hypothesis tests WHY the gap exists (gradient starvation mechanism), not how to close it.

---

## Dependencies and Gate Conditions

### Prerequisites
- H-E1 (Crystallization Zone Existence) - MUST be COMPLETED with PASS result

### Gate Information

**Gate Type:** MUST_WORK
- Failure stops entire workflow

**Consequence if Fails:** EXPLORE alternative mechanism (loss landscape analysis)

**Phase Assignment:** Phase 2 (Core Mechanisms)

**Estimated Duration:** 1 week

---

## Dependency Context

### Relationship to Other Hypotheses
H-M1 depends on H-E1 establishing that crystallization zone exists. H-M1 then tests the mechanism (gradient starvation feedback loop). If H-M1 passes, it enables H-M2 (classifier commitment post-crystallization).

### Previous Hypothesis Results (H-E1)
- Status: COMPLETED
- Gate Result: PASS - Code executes, mechanism implemented, metrics measurable
- Key Finding: Crystallization zone detected, d²WGA/dt² peak validated

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
5. Previous hypothesis results for continuity

**Phase 2C will:**
1. Load this file for H-M1 context
2. Search for gradient starvation implementations (Archon, Exa MCP)
3. Design gradient magnitude tracking experiment
4. Define correlation analysis with H-E1 crystallization timing
5. Output: h-m1/02c_experiment_brief.md

---

*Optimized for single-hypothesis experiment design*
