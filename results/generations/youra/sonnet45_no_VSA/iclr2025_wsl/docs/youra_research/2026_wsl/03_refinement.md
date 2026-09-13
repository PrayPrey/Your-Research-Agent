# Phase 2A Refinement Summary

**Generated:** 2026-07-11T17:30:00Z  
**Workflow:** phase2a-dialogue  
**Gap ID:** gap-1  
**Discussion Exchanges:** 7  
**Convergence:** ✅ ALL CRITERIA MET

---

## Hypothesis Statement

**Lightweight statistical features—normalization layer type counts and convolution-to-linear parameter-mass ratio—enable architecture family classification (CNN vs Transformer vs Hybrid) from checkpoint files without forward passes, achieving >80% accuracy on held-out model families with scale-stable features and strong inter-family separation.**

---

## Key Features

1. **Normalization Fingerprint**
   - Count BatchNorm, LayerNorm, GroupNorm layers via state_dict key matching
   - Handle NormFree networks with fallback to parameter-mass ratio
   - Regex patterns: `*.bn*.weight`, `*.norm*.weight`, `*.gn*.weight`

2. **Parameter-Mass Ratio**
   ```
   R = conv_params / (conv_params + linear_params_no_head)
   ```
   - Excludes classification head to reduce scale bias
   - Captures structural allocation of parameters (local vs global)

---

## Testable Predictions

### P1: Primary (MUST_WORK Gate)
- **Claim:** Logistic regression with 2 features achieves >80% 3-way accuracy
- **Dataset:** 50 TIMM models (20 CNN, 20 Transformer, 10 Hybrid)
- **Split:** 70% train, 30% validation (stratified)

### P2: Generalization (SHOULD_WORK)
- **Claim:** ≥70% accuracy on ≥2 out of 3 held-out families
- **Families:** DenseNet, Swin, EfficientNet (leave-one-out)

### P3: Scale Invariance (SHOULD_WORK)
- **Claim:** Intra-family CV < 0.15, inter-family Cohen's d > 1.0
- **Test:** ResNet-{18,34,50,101,152} parameter-mass ratio variance

---

## Novelty vs. Existing Work

| Aspect | Kofinas et al. (2024) | Zhang & Abdulla (2023) | **This Work** |
|--------|----------------------|------------------------|---------------|
| **Approach** | GNN on computation graphs | Forward pass for BN stats | Checkpoint-only inspection |
| **Complexity** | Graph construction + GNN | Runtime statistics | State_dict regex + counting |
| **Implementation** | ~50+ hours, 103 tasks | N/A | ~6 hours, 15 tasks |
| **Interpretability** | Opaque (GNN weights) | Moderate | High (direct features) |
| **Requirement** | Model instantiation | Forward pass | None |

**Core Contribution:** First interpretable, checkpoint-only classifier that avoids both neural architectures and forward passes.

---

## Experimental Setup

### Multi-Stage Validation

**Stage 1: Proof of Concept**
- Train: ResNet-18/50, ViT-Ti/S, ConvNeXt-T (6 models)
- Test: ResNet-101, ViT-B, ConvNeXt-B (3 models, different scales)
- Target: >85% accuracy
- Purpose: Intra-family scale robustness

**Stage 2: Family Holdout**
- Method: Leave-one-family-out (DenseNet, Swin, EfficientNet)
- Target: ≥70% accuracy on ≥2/3 families
- Purpose: Inter-family generalization

**Stage 3: Edge Case Probing**
- Models: NFNet (no norm), SENet (attention-like), RegNet (depthwise)
- Target: Document failure modes
- Purpose: Identify boundary cases

---

## Feasibility Analysis

### Avoided Failure Modes

| Previous Failure | Root Cause | How Avoided |
|-----------------|------------|-------------|
| h-e1 run 1 | 103 complexity, 50+ hours | 15 tasks, 6 hours |
| h-e1 run 2 | JAX/PyTorch incompatibility | PyTorch-only |
| h-e1 run 3 | Version conflicts | Pin TIMM==1.0.9, PyTorch 2.1 |
| h-e2 run 1 | NFN API mismatch | No meta-learning libraries |
| h-m2 run 1 | Simplified approximations | Direct interpretable features |

### Complexity Budget

- **Total Tasks:** 15
  - Env setup: 2 tasks
  - Dataset construction: 3 tasks
  - Feature extraction: 5 tasks
  - Classification: 3 tasks
  - Validation: 2 tasks
- **Execution Time:** ~6 hours
- **Status:** ✅ Within <30 tasks, <8 hours budget

---

## Key Assumptions & Validation

1. **TIMM naming aligns with structure** → Validate on 10-model sample (>90% expected)
2. **Normalization reflects paradigm, not convention** → Test violation rate (≤15% per class)
3. **Parameter-mass ratio is scale-invariant** → Test intra-family CV (<0.15)
4. **Linear classifier suffices** → Logistic regression test (no MLP rescue)

---

## Established Facts (Build On)

1. **Weight-based classification is solvable** — Kofinas et al. (2024, 64 citations)
2. **LayerNorm/BatchNorm impose different geometry** — Chun (2026) theoretical proof
3. **Heterogeneous structures have diverged scales** — Fang et al. (2024, 38 citations)
4. **TIMM provides reliable checkpoint access** — Validated in h-e1 run 3 partial success

---

## Persona Consensus

**Dr. Nova (Novelty):** ✅ Enthusiastic support — creative simplicity beats complex GNNs  
**Prof. Vera (Rigor):** ✅ Satisfied — falsification criteria met  
**Dr. Sage (Impact):** ✅ Support with generalization test — paradigm shift if successful  
**Prof. Pax (Feasibility):** ✅ Feasible, proceed — 15 tasks, 6 hours realistic  
**Dr. Ally (Strengthening):** ✅ Ready — all objections addressed via refinements  
**Prof. Rex (Stress-Test):** ✅ Concerns addressed — execution quality will determine outcome

**Overall Verdict:** READY FOR PHASE 2B

---

## Phase 2B Handoff

**Primary Input:** `03_refinement.yaml` (THIS FILE'S SOURCE)  
**Supporting Files:** `02_synthesis.yaml`, `01_round_table/final_opinions.yaml`  
**Next Step:** Phase 2B Step 1 — Parse hypothesis, create implementation roadmap

**Estimated Success Probability:**
- P1 (Primary): 75-85%
- P2 (Generalization): 60-70%
- P3 (Scale Invariance): 80-90%

**Critical Success Factors:**
1. Pre-register model list and thresholds BEFORE feature extraction
2. Execute leave-one-family-out validation (non-negotiable)
3. Document failure modes if Stage 2 fails (scientifically valuable)
4. Pin TIMM==1.0.9, PyTorch 2.1 to avoid version conflicts

---

*End of Phase 2A — Hypothesis Generation Complete*
