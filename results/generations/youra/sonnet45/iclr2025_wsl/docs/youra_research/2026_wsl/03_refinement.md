# Phase 2A Hypothesis Summary

**Generated:** 2026-03-19T01:27:00Z
**Workflow:** phase2a-dialogue v10.0.0 (Self-Contained Tikitaka Loop)
**Gap:** gap-1 - Architecture-Agnostic Weight Space Encoders
**Discussion Exchanges:** 12
**Convergence:** All 6 personas reached consensus with quantified predictions and rigorous experimental design

---

## Hypothesis: Compositional Architecture-Agnostic Weight Encoder (CAWE)

**ID:** H-CAWE-v1
**Confidence Level:** 0.85 (All perspective personas: STRONG verdicts)
**Gate Type:** MUST_WORK

### Core Statement

Under training on a 750-model heterogeneous zoo (250 CNNs from torchvision, 250 Vision Transformers from ViT Model Zoo, 250 FC-MLPs from Unterthiner MNIST), if a Compositional Architecture-Agnostic Weight Encoder (CAWE) combining architecture-specific tokenizers with a shared Neural Functional Transformer (NFT) backbone is trained to predict generalization gap, then the encoder achieves Spearman ρ > 0.7 on cross-architecture generalization gap prediction while preserving architecture-family structure (silhouette > 0.5) and outperforming flat-weight baselines (Δρ > 0.15), because the NFT's permutation-equivariant attention mechanism learns cross-layer weight relationships from shared token representations that are architecture-independent after tokenization.

### Mechanism (3-Stage Causal Chain)

1. **Architecture-Specific Tokenization:** Diverse weight types (CNN kernels, Transformer Q/K/V, MLP matrices) projected into shared D-dimensional token space via architecture-tailored preprocessing
2. **Architecture-Agnostic Processing:** NFT processes token sequences with permutation-equivariant attention, learning cross-layer relationships independently of source architecture  
3. **Generalization Gap Prediction:** NFT embedding mapped to generalization gap via regression head, enabling cross-architecture ranking

### Key Predictions (10 Quantified)

**Primary (MUST_WORK):**
- **P1:** In-distribution ρ > 0.7 (95% CI) on 150 held-out heterogeneous models

**Mechanism Validation:**
- **P2:** Per-family ρ > 0.7 for CNN, Transformer, MLP subsets separately
- **P3:** Architecture clustering silhouette > 0.5 in t-SNE embeddings

**Baseline Comparisons:**
- **P4:** Δρ > 0.15 vs flat-weight MLP baseline (paired t-test, p<0.001)
- **P5:** Δρ > 0.1 vs random forest on engineered features (Wilcoxon, p<0.01, OOD tests)

**Robustness:**
- **P6:** Adversarial set ρ > 0.65 (50 models: random init, mid-training, non-standard layers, broken components, alternative training)
- **P7:** Tokenization robustness: 2/4 variants (statistics, spectral, learned, SANE) achieve ρ > 0.65
- **P8:** Hyperparameter robustness: 2/3 D-values ({64, 128, 256}) achieve ρ > 0.65

**Out-of-Distribution Generalization:**
- **P9:** OOD architecture ρ > 0.6 (Unterthiner MLPs, unseen family)
- **P10:** OOD dataset+arch ρ > 0.55 (NeurIPS 2021 MLPs, unseen dataset+family combo)

### Failure Criteria

Hypothesis FAILS if any of:
- In-distribution ρ < 0.7 (95% CI lower bound)
- Per-family ρ < 0.7 for any single family
- OOD architecture ρ < 0.55
- CAWE vs random forest Δρ < 0.1 on OOD tests
- Fewer than 2/4 tokenization variants achieve ρ > 0.65

### Novelty

**First empirical validation of architecture-agnostic weight encoders on heterogeneous multi-family zoo** (prior NFT: homogeneous MNIST MLPs; Universal NFNs: theoretical claims without large-scale validation)

**Key Innovation:** Compositional hybrid approach - architecture-specific tokenization + architecture-agnostic NFT processing

**Differentiation:**
- vs DWSNets: Avoids library lock-in (ROUTE_TO_0 lesson)
- vs NFT paper: Extends from single-architecture to heterogeneous zoo
- vs Universal NFNs: Empirical 750-model validation vs theoretical claims
- vs GNN approach: Attention-based implicit learning vs explicit graph construction

### Feasibility

- **Compute:** 1 week A100 (6 hours for 12 ablation runs)
- **Implementation:** ~1000 LOC, leverages nfn library (PyPI)
- **Datasets:** All public (ViT Zoo github, torchvision built-in, Zenodo 5645138)
- **Timeline:** 3 months for 1 researcher

### Persona Verdicts

- 🔭 **Dr. Nova (Novelty):** STRONG
- 🔬 **Prof. Vera (Falsifiability):** STRONG  
- 🎯 **Dr. Sage (Significance):** STRONG
- ⚙️ **Prof. Pax (Feasibility):** STRONG
- 🛡️ **Dr. Ally (Synthesis):** Consolidated 12 exchanges into bulletproof experimental design
- 🔍 **Prof. Rex (Critique):** MEDIUM risk, all 4 attacks addressed with mitigation strategies

---

## Phase 2B Readiness

**Status:** READY

**Sub-Hypothesis Decomposition Seeds:**
- **H-E1 (EXISTENCE PoC):** In-dist ρ > 0.7 validation (Prediction P1)
- **H-M1 (MECHANISM-Tokenization):** 4-variant ablation (Prediction P7)
- **H-M2 (MECHANISM-Shared-Space):** Per-family ablation + attention analysis (Prediction P2)
- **H-R (ROBUSTNESS):** Adversarial + OOD tests (Predictions P6, P9, P10)
- **H-B (BASELINE-COMPARISON):** Flat MLP + Random Forest comparisons (Predictions P4, P5)

**Next Phase:** Phase 2B - Verification Planning (decompose into detailed sub-hypotheses with prerequisites)
