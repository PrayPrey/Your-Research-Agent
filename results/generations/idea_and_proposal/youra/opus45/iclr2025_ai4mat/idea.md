# Research Idea

## Title
Hierarchical Local Environment Encoding with Adversarial Domain Alignment for Cross-Material-Type Transfer in Materials Foundation Models

## Motivation
Current materials foundation models trained on crystalline structures fail catastrophically (>50% accuracy degradation) when applied to amorphous and surface materials—a critical barrier to real-world deployment. While local atomic coordination chemistry follows universal physical principles across material types, existing architectures conflate transferable local features with domain-specific global features (periodicity, long-range order). This gap prevents foundation models from generalizing across the diverse material types needed for practical applications.

## Main Idea
We propose HLEE (Hierarchical Local Environment Encoding), an architecture that explicitly separates local atomic environment features from global structural features, then applies adversarial domain alignment via gradient reversal to extract domain-invariant local representations. The core insight is that adversarial alignment at the *local environment level*—not the material level—enables transfer across material type boundaries.

**Methodology:** Pre-train on Materials Project crystalline data (~150K structures), then evaluate cross-domain transfer to JARVIS amorphous/surface materials. Compare HLEE against baseline GNNs (MatGL, NequIP) and ablated variants.

**Key Predictions:** (1) HLEE achieves <15% cross-domain degradation versus >50% for baselines; (2) HLEE with 100 target samples matches baseline performance with 1000+ samples.

**Impact:** Enables materials foundation models to generalize across material types, addressing a fundamental limitation for real-world materials discovery.