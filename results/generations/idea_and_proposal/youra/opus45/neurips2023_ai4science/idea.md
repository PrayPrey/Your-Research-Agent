# Research Idea

## Title
Modular Symmetry-Equivariant Foundation Models for Cross-Domain Physics Simulation Transfer

## Motivation
Current physics foundation models like Universal Physics Transformers (UPT) achieve broad generalization but fail to exploit the fundamental insight that physical laws share symmetry structures across domains—a connection established by Noether's theorem. While domain-specific equivariant networks (e.g., NequIP) achieve remarkable 1000x data efficiency within single domains, no approach systematically leverages shared symmetries for cross-domain transfer. This gap limits efficient adaptation to new physics problems, requiring extensive retraining for each domain.

## Main Idea
We propose MS-PFM, a foundation model with modular symmetry-equivariant encoders (E(3), SO(3), discrete, scale) that learns transferable "physics grammar" through multi-domain pretraining. The core mechanism: shared symmetry structures encode domain-agnostic conservation laws, enabling automatic module selection via a symmetry detection network and efficient LoRA-style adaptation for new domains.

**Methodology:** Pretrain on 4+ physics domains (PDEBench fluids, MD17/MD22 molecular, elasticity, electromagnetics), then evaluate cross-domain transfer accuracy and few-shot adaptation efficiency against UPT baseline.

**Expected Outcomes:** >50% reduction in fine-tuning samples and >10% transfer accuracy improvement (relative L2 error <10% vs. UPT's ~15%). Ablation studies will validate that symmetry modules causally drive transfer benefits.

**Impact:** Democratizes physics simulation by enabling rapid adaptation to new domains with minimal data.