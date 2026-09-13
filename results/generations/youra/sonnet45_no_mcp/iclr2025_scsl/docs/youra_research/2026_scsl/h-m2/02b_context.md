# Hypothesis Context: h-m2

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-04-24
**Main Hypothesis:** Loss Landscape Geometry and Spurious Correlation Robustness
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under ERM training, if sharp curvature exists in outlier subspace (H-M1), then these sharp directions will align with minority-group gradient directions (high A(w)), because minority groups expose spurious correlations and their gradients point toward spurious-feature directions.

### Type
MECHANISM (Step 2 of 4)

### Rationale
Second causal link: connects geometric structure (sharp curvature from H-M1) to behavioral signature (minority gradient alignment), explaining why A(w) metric captures spurious reliance.

---

## Verification Protocol

### Conceptual Test
1. Using H-M1 outlier subspace S_out, compute minority-group gradients g_minority
2. Calculate alignment A(w) = ||P_S_out g_minority||² / ||g_minority||²
3. Compare alignment for minority vs majority gradients
4. Test correlation between A(w) and worst-group accuracy across seeds
5. Verify alignment is not arbitrary (randomization test with shuffled subspaces)

### Success Criteria
- Primary: Minority gradient alignment > majority gradient alignment (significant difference)
- Secondary: A(w) correlates with worst-group accuracy (ρ>0.6, p<0.01)

### Variables
- **Independent Variable:** Minority-group gradient direction
- **Dependent Variable:** Alignment A(w) with outlier subspace
- **Controlled Variables:** Subspace definition (from H-M1), gradient batch composition

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** Waterbirds (primary), CelebA + Colored MNIST (cross-validation)
- **Type:** standard
- **Source:** group_DRO repository (https://github.com/kohpangwei/group_DRO)
- **Path:** Downloaded via group_DRO scripts
- **Hypothesis Fit:** Ground-truth spurious labels enable behavioral phenotyping (spurious vs core solutions). Waterbirds: background spurious correlation, CelebA: gender-attribute correlation, Colored MNIST: color-digit correlation

### Selected Model
- **Name:** ResNet-50
- **Type:** Standard CNN with skip connections
- **Source:** torchvision.models
- **Hypothesis Fit:** Li et al. show ResNets produce analyzable loss landscapes with skip connections creating flat minima. Sufficient over-parameterization for Marchenko-Pastur assumptions. Standard architecture enables reproducibility.

---

## Baseline & Comparison Targets

### Baseline Methods
| Method | Performance | Dataset |
|--------|-------------|---------|
| Standard ERM | 85-90% average, 60-75% worst-group | Waterbirds, CelebA |
| Group-DRO | 75-80% worst-group (requires group labels) | Waterbirds, CelebA |
| Fast Geometric Ensembling (FGE) | Cyclical learning rate sampling | Waterbirds |

### Baseline Performance
- ERM: 85-90% average accuracy, 60-75% worst-group accuracy
- Group-DRO: 75-80% worst-group accuracy (requires group labels)

### Gap Analysis
Group-DRO improves worst-group accuracy but requires group labels (impractical in real scenarios). This work aims to explain WHY ERM fails via geometric mechanism and enable label-free early diagnostics via A(w) monitoring.

---

## Dependencies and Gate Conditions

### Prerequisites
- h-m1 (COMPLETED, MUST_WORK gate PASSED)

### Gate Information

**Gate Type:** SHOULD_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** EXPLORE alternative gradient definitions or minority group sampling strategies

**Phase Assignment:** Phase 2 - Mechanism Chain

**Estimated Duration:** 1 week

---

## Dependency Context

### Relationship to Other Hypotheses
- **Builds on h-m1:** Uses validated outlier subspace (23 outlier eigenvalues for ERM) from h-m1
- **Enables h-m3:** If validated, provides foundation for analyzing SGD flow dynamics
- **Part of mechanism chain:** H-E1 → H-M1 → **H-M2** → H-M3 → H-M4

### Previous Hypothesis Results (h-m1)

**Key Findings from h-m1 validation:**
- ERM exhibits 23 outlier eigenvalues (vs DRO's 15)
- Bulk edge threshold: λ₊ = 2.456 (ERM)
- Outlier eigenvalues range from 2.500 to 10.000
- 53.3% more outlier concentration in ERM vs DRO
- Max eigenvalue ratio: 1.43 (ERM/DRO)

**Implications for h-m2:**
- Can use these 23 validated outlier directions to define projection subspace P_S_out
- Outlier eigenvectors form the basis for measuring minority gradient alignment
- Baseline established for comparing alignment metrics

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** IN_PROGRESS (experiment_design)
**Workflow Status:** ACTIVE

---

## Phase 2C Usage Notes

**This context file provides:**
1. Complete hypothesis specification for experiment design
2. Gate conditions for prerequisite validation (SHOULD_WORK)
3. Dependency information from h-m1 (23 outlier eigenvectors validated)
4. Success criteria for evaluation design
5. Baseline comparison targets for context

**Phase 2C will:**
1. Load this file instead of full Phase 2B roadmap (91% smaller)
2. Search for implementation patterns (Archon, Exa MCP)
3. Use h-m1 outlier subspace as foundation
4. Design concrete experiment specification (Level 1.5)
5. Output: h-m2/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-M* (Mechanism)**: Baseline to understand improvement potential and validate mechanism link

---

*Generated by Phase 2C Workflow (JIT)*
*Optimized for single-hypothesis experiment design*
