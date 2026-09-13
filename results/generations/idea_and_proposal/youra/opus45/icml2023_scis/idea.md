# Research Idea

## Title
Compositional Invariance Learning: A Unified Framework for Spurious Correlation Robustness

## Motivation
Machine learning models frequently exploit spurious correlations—relying on scanner artifacts in medical imaging or superficial word overlap in NLP—causing failures when deployed in new environments. Multiple communities have developed solutions (IRM from causality, Group DRO from fairness, OOD methods from robust ML), yet these approaches remain fragmented with no consensus on best practices. This disconnect limits both theoretical understanding and practical adoption. A unifying framework could reveal shared principles and enable more robust, transferable solutions.

## Main Idea
We propose that spurious correlations exhibit compositional structure, enabling a hierarchical learning framework that unifies existing approaches. The **Compositional Invariance Learning (CIL)** framework operates through three levels: (1) feature-level primitives capturing atomic invariant patterns, (2) module-level compositions combining primitives flexibly via differentiable selection with credit assignment, and (3) model-level optimization accommodating IRM, Group DRO, and OOD objectives as different weightings of shared modules.

The core insight is that compositional decomposition isolates invariant primitives that remain stable even when their combinations change—providing robustness that monolithic methods lack. We will validate on DomainBed benchmarks, testing whether CIL matches SOTA accuracy (targeting ≥66.9% average) while demonstrating compositional transfer efficiency (2-5% improvement on novel domain combinations) and mathematical unification of community-specific methods. Falsification occurs if performance falls below ERM baselines or primitives show no cross-domain reusability.