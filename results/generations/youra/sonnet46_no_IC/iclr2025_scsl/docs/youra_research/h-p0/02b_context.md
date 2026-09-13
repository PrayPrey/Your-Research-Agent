---
hypothesis_id: h-p0
generated_at: "2026-08-05"
generated_by: "Phase 2C step-01 JIT generation"
source: "02b_verification_plan.md"
---

# Per-Hypothesis Context: H-P0

## Hypothesis Information

- **ID:** h-p0
- **Title:** DFR Backbone Identity Sanity Check
- **Type:** EXISTENCE (Sanity Check — gates all backbone comparisons)
- **Gate:** MUST_WORK

**Statement:**
Under ResNet-50 checkpoints from izmailovpavel/spurious_feature_learning, DFR layer4 features and ERM layer4 features at matching seeds are numerically identical (mean cosine similarity >= 0.9999 for all 3 seed pairs), because DFR protocol explicitly freezes backbone and retrains only the classification head.

**Rationale:**
This is the architectural prerequisite for the entire hypothesis. DFR's mechanism is backbone-preservation; if H-P0 fails (similarity < 0.999), DFR must be treated as an independent backbone condition in H-P1/P2, fundamentally changing the experimental design.

## Experimental Setup

**Dataset:**
- Name: Waterbirds WILDS
- Type: standard
- Source: WILDS benchmark (Koh et al. 2021)
- Path: `/home/PrayPrey/.wilds_cache/waterbirds_v1.0`
- Background extraction: `background_label = group_array % 2` (0=land, 1=water)
- Hypothesis Fit: Canonical spurious correlation benchmark; DFR/ERM checkpoints trained on this dataset

**Model:**
- Name: ResNet-50 (12 checkpoints: 3 seeds × 4 methods: ERM, DFR, GroupDRO, SAM)
- Type: CNN feature extractor
- Source: izmailovpavel/spurious_feature_learning (HuggingFace Hub)
- Feature extraction: `model.layer4 → AdaptiveAvgPool2d(output_size=(1,1)) → flatten → D=2048`
- Hypothesis Fit: Layer4 is final backbone representation; DFR freezes backbone = ERM backbone by design

## Verification Protocol

1. Download 12 checkpoints from izmailovpavel/spurious_feature_learning (HuggingFace Hub)
2. For each seed in {1,2,3}: load DFR and ERM checkpoints, set model.eval() + torch.no_grad()
3. Forward pass 50 fixed Waterbirds test images through model.layer4 → AdaptiveAvgPool2d(1,1) → flatten to [50, 2048]
4. Compute mean cosine_similarity(dfr_feat[i], erm_feat[i]) for i=1..50; report per-seed mean and variance
5. Pass criterion: mean cosine similarity ≥ 0.9999 for ALL 3 seed pairs

## Success Criteria

- **PASS:** Mean cosine similarity ≥ 0.9999 for all 3 seed pairs AND variance < 1e-6
- **FAIL (branching):** Cosine similarity < 0.999 → DFR includes backbone fine-tuning; must include DFR as 4th backbone condition in H-M3

## Gate Condition

**MUST_WORK** — Failure of H-P0 stops all downstream hypotheses (H-M1, H-M2, H-M3, H-P2) until experimental design is revised to include DFR as a 4th backbone condition.

## Prerequisites

None (foundation — no dependencies)

## Dependencies (blocked until H-P0 passes)

- H-M1 (MUST_WORK)
- H-M2 (via H-M1)
- H-M3 (primary test, via H-M2)
- H-P2 (exploratory, via H-M3)

## Key Assumptions Being Tested

- **A1:** DFR backbone weights in released checkpoints are numerically identical to ERM at same seed (frozen backbone in DFR protocol) — Kirichenko 2022 DFR protocol; Izmailov repo; Exchanges 4, 12
- **A4:** 12 released checkpoints represent genuinely different training methods — WGA differences confirm differentiation

## Source References

- Phase 2A Section 1.6 Prediction P0
- Exchange 12 (Prof. Rex)
- Kirichenko et al. 2022 (DFR paper)
- Izmailov et al. 2022 (spurious_feature_learning NeurIPS 2022)
