# Phase 2A Extended: Hypothesis Clarification Summary

**Date:** 2026-02-08
**Author:** Pray
**Hypothesis ID:** H-MALS-001
**Status:** ✅ Ready for Phase 2B Verification Planning

---

## Executive Summary

**Research Question:** Can a unified discrete latent space (VQ-VAE with shared codebook) enable effective cross-modal representation learning across heterogeneous structured modalities (molecular graphs, chemical text, binding affinity time series)?

**Main Hypothesis:** A Vector-Quantized VAE with shared discrete codebook (K=1024 codes) trained with cross-modal contrastive learning will achieve ≥70% text→graph retrieval accuracy (top-5) and ECE ≤0.10 for uncertainty quantification, while maintaining reconstruction quality within 10% of modality-specific baselines on QM9 molecular dataset.

**Confidence Level:** 0.82 (High)

---

## Core Innovation

### What We're Testing

**Modality-Agnostic Latent Space (MALS)**: A single discrete codebook shared across three structured modalities:

1. **Molecular Graphs** → GNN Encoder (GCN/GAT) → Discrete Codes
2. **Chemical Text (SMILES)** → Transformer Encoder → Discrete Codes
3. **Binding Affinity Time Series** → Transformer Encoder → Discrete Codes

All three modalities map to the **SAME** K=1024 discrete codes, trained with:
- Standard VQ-VAE losses (reconstruction + commitment + codebook)
- **Novel component**: Cross-modal contrastive loss (InfoNCE) aligning codes from same molecule across modalities

### Why This Matters

**Scientific Contribution:**
- First demonstration that discrete latent codes can unify heterogeneous structured modalities (graphs + temporal + text)
- Extends VQ-VAE (6491 citations) from single modality to multi-modal structured data
- Combines discrete representation learning (VQ-VAE) with contrastive multi-modal alignment (CLIP-style)

**Practical Impact:**
- Zero-shot cross-modal transfer (text query "aromatic compound" → generate molecular graph)
- Unified uncertainty quantification across all modalities (ECE <0.10 via Conformal Prediction)
- Reduced architecture engineering (1 shared model vs. 3 modality-specific models)

---

## Key Variables & Predictions

### Primary Predictions

**P1 (Cross-Modal Transfer):** Text→graph retrieval accuracy ≥70% (vs. 55-60% modality-specific baseline)
**P2 (Uncertainty Quality):** Expected Calibration Error ≤0.10 across all modalities (vs. 0.35 for Deep Ensembles)
**P3 (Codebook Efficiency):** Codebook utilization ≥80% (avoiding collapse)
**P4 (Reconstruction Trade-off):** Per-modality quality within 10% of modality-specific models

### Experimental Design

- **Dataset:** QM9 (133,885 molecules split 80/10/10 train/calibration/test)
- **Ablations:** Codebook size K ∈ {512, 1024, 2048}, Contrastive temperature τ ∈ {0.05, 0.1, 0.2, 0.5}
- **Baselines:** Modality-specific VQ-VAEs (3 separate), LLM-based cross-domain integration
- **Statistics:** McNemar's test (cross-modal accuracy), Bootstrap CI (ECE), ANOVA (ablations)
- **Compute:** 56 A100-days (8 GPUs × 7 days), 12-week timeline

### Falsification Criteria

Hypothesis is **FALSIFIED** if:
- Cross-modal accuracy <50% (below baselines)
- Codebook utilization <50% (collapse)
- Any modality reconstruction >20% worse than baseline
- ECE >0.20 (worse than uncalibrated Deep Ensembles)

---

## Causal Mechanism

**Discretization → Abstraction:**
- Discrete codebook forces information bottleneck → modality-agnostic patterns
- Evidence: VQ-VAE (6491 cites) showed discrete codes work across images/audio/video

**Shared Codebook → Cross-Modal Alignment:**
- Contrastive loss pulls codes from same molecule (across modalities) together
- Evidence: CLIP (15k+ cites) demonstrated contrastive learning for vision-language

**Cross-Modal Codes → Zero-Shot Transfer:**
- Text "aromatic compound" → code C_123 → Graph decoder generates molecular graph
- Mechanism: Shared latent space enables text→graph translation

**Unified Posterior → Consistent UQ:**
- All modalities use same codebook posterior P(code | input)
- Conformal Prediction calibrates across modalities → ECE <0.10
- Evidence: Conformalized-DeepONet (25 cites) provides distribution-free guarantees

---

## Phase 2B Decomposition Preview

### Sub-Hypothesis 1 (Existence)
**Statement:** Shared codebook (K=1024) can encode graphs+text+timeseries with ≥80% utilization and ≤15% reconstruction degradation
**Verification:** Train without contrastive loss, measure utilization + reconstruction

### Sub-Hypothesis 2 (Mechanism)
**Statement:** Contrastive loss increases inter-modality code similarity by ≥0.3 and enables ≥60% text→graph retrieval
**Verification:** Compare with/without contrastive loss on code similarity + retrieval

### Sub-Hypothesis 3 (Comparison)
**Statement:** MALS achieves ≥10 points higher retrieval accuracy (≥70% vs. ≤60%) than modality-specific baselines with <10% reconstruction degradation
**Verification:** Full system vs. baselines, statistical tests (McNemar's, ANOVA)

---

## Key Assumptions & Risks

**Critical Assumptions:**
1. **Semantic Overlap**: QM9 modalities (graphs, SMILES, time series) share sufficient semantic structure
2. **Discrete Sufficiency**: K=512-2048 codes can represent 133k molecule diversity
3. **Contrastive Batch Composition**: Balanced sampling with batch size ≥64 enables effective contrastive learning

**Identified Risks:**
1. **Codebook Collapse** (Severity: MEDIUM) → Mitigation: EMA updates, code reset heuristic
2. **Modality Imbalance** (Severity: MEDIUM) → Mitigation: Balanced batch sampling
3. **Reconstruction vs. Transfer Trade-off** (Severity: MEDIUM) → Mitigation: Staged training (2-modal → 3-modal)

**Risk Mitigation Strategy:**
- Staged training: Train graphs+text first (Stage 1), then add time series (Stage 2)
- Fallback plan: If 3-modal fails, 2-modal (graphs+text) still publishable contribution

---

## Related Work Positioning

| Aspect | MALS (Ours) | VQ-VAE (2017) | CLIP (2021) | Cross-Domain Integration (2024) |
|--------|-------------|---------------|-------------|--------------------------------|
| **Modalities** | Graphs + Time Series + Text | Images/Audio (grids) | Images + Text | Multi-sensor (any) |
| **Latent Space** | Shared discrete codebook | Modality-specific discrete | Shared continuous | No shared latent |
| **Training** | Contrastive VQ-VAE | Reconstruction only | Contrastive continuous | LLM routing |
| **Structured Data** | Graphs (non-grid) | Grids only | Images (grids) | Any modality |
| **Uncertainty** | Conformal Prediction | Not addressed | Not addressed | Not addressed |

**Key Novelty:** First to combine (1) discrete codes + (2) contrastive alignment + (3) structured non-grid data + (4) distribution-free UQ

---

## Resources & Implementation

**Datasets:**
- QM9 (133,885 molecules with graphs, SMILES, properties) - Public

**Code Foundations:**
- PyTorch Geometric (23.4k stars) - GNN encoders
- AntixK/PyTorch-VAE (7.5k stars) - VQ-VAE baseline
- HuggingFace Transformers - Text/time series encoders

**Compute Requirements:**
- 8× A100 GPUs × 7 days = 56 A100-days
- Estimated cost: $400-800 (cloud compute)

**Timeline:**
- Weeks 1-4: Implementation + Stage 1 training (graphs+text)
- Weeks 5-8: UQ calibration + Stage 1 evaluation
- Weeks 9-12: Stage 2 (add time series) + final experiments

---

## Open Questions for Phase 2B

**Q1 (Critical):** How does optimal K scale with dataset size N and modality count M?
- **Action:** Derive scaling heuristic from K ∈ {512, 1024, 2048} ablation

**Q2 (High Priority):** What batch composition strategy works for naturally imbalanced modalities?
- **Action:** Test adaptive sampling (inverse frequency, hard negative mining)

**Q3 (Medium):** How sensitive is cross-modal alignment to contrastive temperature τ?
- **Action:** Analyze τ effect on inter/intra-modality code separation

**Q4 (Future Work):** Does hierarchical codebook (coarse + fine) eliminate reconstruction vs. transfer trade-off?
- **Action:** Propose if initial results show >10% reconstruction degradation

---

## Readiness Checklist

- ✅ **Hypothesis Clarity:** Core statement, H0, causal mechanism, assumptions specified
- ✅ **Measurability:** All metrics operationalized with measurement procedures
- ✅ **Testability:** Falsification criteria, success thresholds, statistical tests pre-specified
- ✅ **Feasibility:** Dataset available, compute realistic, implementation resources identified
- ✅ **Scope Discipline:** In-scope, out-of-scope, boundary conditions enumerated
- ✅ **Phase 2B Ready:** Sub-hypotheses (SH1-SH3) decomposed with verification experiments

---

## Next Steps

**Immediate Action: Proceed to Phase 2B - Verification Planning**

Phase 2B will:
1. Expand SH1-SH3 into detailed verification experiments with protocols
2. Design ablation studies for codebook size, temperature, loss weights
3. Specify baseline implementation details (modality-specific VQ-VAEs, LLM-based)
4. Create experimental timeline with checkpoints and success criteria
5. Develop contingency plans for identified risks (codebook collapse, imbalance, trade-offs)

**Command:** `/phase2b-planning`

---

**Document Status:** ✅ Complete
**Full Details:** See `02a_extended_hypothesis_full.md` for comprehensive clarification
**Generated:** 2026-02-08 (YOLO Mode - Fully Automated)
