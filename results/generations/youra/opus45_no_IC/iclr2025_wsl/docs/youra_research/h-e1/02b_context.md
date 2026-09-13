# Hypothesis Context: H-E1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-08-12
**Main Hypothesis:** Sample Efficiency of Permutation Equivariance in Weight Space Learning
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under N=1K models, if NFN vs MLP-Matched, then NFN R² > MLP R² + 0.05 (p<0.05), because equivariance provides sample efficiency at small scales.

### Type
EXISTENCE

### Rationale
Validates the core existence claim that permutation equivariance provides measurable benefit. Without this, no mechanism investigation is warranted.

---

## Verification Protocol

### Conceptual Test
1. Train NFN and MLP-Matched on N=1K models with 10 seeds each
2. Compute R² on fixed 20% test set for each seed
3. Run one-sided paired t-test: NFN > MLP + 0.05
4. Report p-value, mean difference, 95% CI

### Success Criteria
- Primary: p < 0.05 AND mean R² difference > 0.05
- Secondary: Effect visible across majority of seeds

### Variables
- **Independent Variable:** Architecture Type (NFN vs MLP-Matched)
- **Dependent Variable:** R² on accuracy prediction
- **Controlled Variables:** N=1K, training protocol, test set, 10 seeds

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** Model Zoo CIFAR-10 CNN Subset
- **Type:** standard
- **Source:** github.com/ModelZoos/ModelZooDataset
- **Path:** To be downloaded; single architecture family extracted
- **Hypothesis Fit:** 50K models provide sufficient scale for crossover detection; homogeneous architecture ensures valid permutation group

### Selected Model
- **Name:** NFN (Neural Functional Network)
- **Type:** Permutation-equivariant encoder + regression head
- **Source:** pip install nfn (AllanYangZhou/nfn)
- **Hypothesis Fit:** Designed specifically for weight space learning with correct symmetry

---

## Baseline & Comparison Targets

### Baseline Methods
| Method | Performance | Dataset |
|--------|-------------|---------|
| MLP-Matched | TBD | Model Zoo |
| NFN-Scrambled | TBD | Model Zoo |
| Simple Statistics (mean/std/norm) | Unknown | Model Zoo |
| Random Features | Unknown | Model Zoo |

### Baseline Performance
TBD - to be established in H-E1 experiment

### Gap Analysis
Expected NFN advantage of R² > 0.05 over MLP-Matched at small scales (N=1K)

---

## Dependencies and Gate Conditions

### Prerequisites
None (H-E1 is the foundation)

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow

**Consequence if Fails:** ABANDON main hypothesis (equivariance provides no benefit)

**Phase Assignment:** Phase 1 (Foundation)

**Estimated Duration:** 2 weeks

---

## Dependency Context

### Relationship to Other Hypotheses
H-E1 is the foundation hypothesis. All mechanism hypotheses (H-M1 through H-M5) depend on H-E1 passing. If H-E1 fails, the entire hypothesis chain is abandoned.

**Dependency Chain:** H-E1 → H-M1 → H-M2 → H-M3 → H-M4 → H-M5

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

*Optimized for single-hypothesis experiment design*
