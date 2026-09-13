# Hypothesis Context: h-m2

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-08-05
**Main Hypothesis:** Backbone Spurious Encoding Reduction (BSER): GroupDRO Training Reduces Linear Decodability of Spurious Background Attributes in ResNet-50 Layer4 Features
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under GroupDRO training on Waterbirds WILDS, the group-balanced gradient signal from the worst-group loss propagates through all ResNet-50 layers including layer4, modifying weight updates to reduce the predictive utility of spurious background features for classification loss minimization.

### Type
MECHANISM (Step 2 of 3-step causal chain)

### Rationale
This is the propagation mechanism linking training objective to backbone representation. GroupDRO modifies the effective training distribution seen by ALL layers (Prof. Pax, Exchange 8). Supported by representation learning theory: training objective shapes representation. The key question answered by H-M3: does this propagation actually reduce background decodability at layer4? H-M2 is verified INDIRECTLY through H-M3 outcome — if layer4 probe accuracy differs, gradient propagation is confirmed.

---

## Verification Protocol

### Conceptual Test
1. Establish theoretical basis: GroupDRO loss gradient ∂L/∂θ_L4 differs from ERM's uniform-weighted gradient by construction (group upweighting changes batch composition seen by all layers).
2. Verify empirically through H-M3 outcome: if layer4 spurious probe accuracy differs between GroupDRO and ERM, gradient propagation to layer4 is confirmed.
3. Falsification check: if spurious probe accuracy is unchanged despite different training objectives, gradient signal did not propagate effectively to backbone (or was counteracted by other forces).

### Success Criteria
- Primary: H-M3 CONFIRMED (proxy evidence of gradient propagation to layer4)
- Secondary: Cohen's d > 0.5 in H-M3 result (magnitude consistent with meaningful gradient modification)

**Note:** H-M2 is a THEORETICAL/PROXY verification — it does not run its own new experiment. The experiment IS H-M3 (gradient probe), but H-M2's design document describes the gradient propagation analysis approach.

### Variables (if applicable)
- **Independent Variable:** GroupDRO vs ERM training objective (manifests as different effective gradient signal at all layers)
- **Dependent Variable:** Gradient signal modification at layer4 (proxied by resulting probe accuracy difference in H-M3)
- **Controlled Variables:** Architecture (ResNet-50), dataset (Waterbirds WILDS), checkpoint source (izmailovpavel/spurious_feature_learning)

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** Waterbirds WILDS
- **Type:** standard
- **Source:** WILDS benchmark (Koh et al. 2021); local cache
- **Path:** `/home/PrayPrey/.wilds_cache/waterbirds_v1.0`
- **Hypothesis Fit:** Canonical spurious correlation benchmark; background (land/water) is the spurious attribute; group_array encodes 4 groups; all 12 checkpoints trained/evaluated on this dataset. Background extracted as `background_label = group_array % 2`.

### Selected Model
- **Name:** ResNet-50 (12 checkpoints: 3 seeds × 4 methods — ERM, GroupDRO, SAM, DFR)
- **Type:** CNN feature extractor
- **Source:** izmailovpavel/spurious_feature_learning (HuggingFace Hub / GitHub)
- **Hypothesis Fit:** Layer4 is the final backbone representation before classification head; standard probing point per Alain & Bengio 2016. Feature extraction: `model.layer4 → AdaptiveAvgPool2d(1,1) → flatten → D=2048`. H-M2 verifies gradient reaches layer4 via proxy measurement.

---

## Baseline & Comparison Targets

### Baseline Methods
| Method | WGA | Role |
|--------|-----|------|
| ERM | 0.72 | Primary comparison (high-spurious-encoding baseline) |
| GroupDRO | 0.88 | Primary test method (expected lower spurious encoding) |
| DFR | 0.91 | Control (backbone ≡ ERM, head-only method) |
| SAM | 0.74 | Exploratory (backbone-changing, unknown spurious effect) |

### Baseline Performance
- ERM spurious probe accuracy (background linear decodability): ~0.85–0.90 (Izmailov 2022 s-DFR proxy)
- Random baseline: ~0.50 (binary background classification)

### Gap Analysis
H-M2 does not directly measure a gap — it provides theoretical + proxy evidence for gradient propagation. The empirical gap (ERM probe acc vs GroupDRO probe acc) is measured in H-M3.

---

## Dependencies and Gate Conditions

### Prerequisites
- H-M1: COMPLETED (PASS) — GroupDRO worst-group loss confirmed to create group-balanced gradient signal (Sagawa 2019 + kohpangwei/group_DRO source code + WGA evidence)
- H-P0: COMPLETED (PASS) — DFR backbone numerically identical to ERM (cosine sim = 1.000000 for all 3 seed pairs)

### Gate Information

**Gate Type:** SHOULD_WORK
- MUST_WORK: Failure stops entire workflow
- **SHOULD_WORK**: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** DOCUMENT limitation — mechanism propagation not confirmed. Workflow continues to H-M3 (primary empirical test). Failure means gradient reached layer4 effect may be unclear, but H-M3 provides the definitive empirical answer.

**Phase Assignment:** Phase 2 (Core Mechanisms)

**Estimated Duration:** Combined with H-M3: 3 weeks

---

## Dependency Context

### Relationship to Other Hypotheses
- **H-P0 (COMPLETED):** Established DFR ≡ ERM backbone (cosine sim = 1.000000), confirming backbone-changing vs preserving distinction. H-M2 can now focus on GroupDRO (backbone-changing) vs ERM comparison.
- **H-M1 (COMPLETED):** Established GroupDRO upweights minority groups (land-bird-land, water-bird-water — minority_fraction=0.0501). This is the INPUT to H-M2's gradient propagation chain.
- **H-M3 (UPCOMING):** H-M2's success criteria are ENTIRELY PROXIED through H-M3. If H-M3 shows lower probe accuracy for GroupDRO, H-M2 is confirmed. H-M2 may be treated as the THEORETICAL COMPLEMENT to H-M3's empirical result.
- **H-P2 (UPCOMING):** Requires H-M3 completion for spurious probe accuracies across 9 checkpoints.

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** IN_PROGRESS (h-m2 hypothesis loop started)
**Workflow Status:** ACTIVE
**h-p0:** COMPLETED (MUST_WORK gate PASSED)
**h-m1:** COMPLETED (MUST_WORK gate PASSED)

---

## Phase 2C Usage Notes

**This context file provides:**
1. Complete hypothesis specification for experiment design
2. Gate conditions for prerequisite validation
3. Dependency information for controlled experiments
4. Success criteria for evaluation design

**Phase 2C will:**
1. Load this file instead of full Phase 2B roadmap (91% smaller)
2. Search for gradient propagation theory and proxy measurement patterns (Archon, Exa MCP)
3. Design theoretical + proxy verification experiment specification (Level 1.5)
4. Output: h-m2/02c_experiment_brief.md

**Special Note for H-M2:**
H-M2 is a THEORETICAL MECHANISM STEP with PROXY VERIFICATION. The experiment design should:
- Document the theoretical basis for gradient propagation (backpropagation through all layers)
- Define the proxy measurement (H-M3 outcome serves as confirmation)
- Provide gradient flow analysis pseudo-code (inspect gradient magnitudes at layer4 during training)
- Specify the connection to H-M3 experimental evidence

*Optimized for single-hypothesis experiment design*
