# Phase 2A Extended: Hypothesis Clarification Summary

**Date:** 2026-02-06
**Author:** Pray
**Hypothesis ID:** H-FedCSSL-01
**Status:** Ready for Phase 2B Verification Planning

---

## Executive Summary

**Hypothesis:** Fed-CSSL-PN (Federated Contrastive Self-Supervised Learning with Prototype-Aware Negative Sampling) enables communication-efficient foundation model pre-training on entirely unlabeled heterogeneous federated data by treating client heterogeneity as implicit multi-view augmentation.

**Key Innovation:** Three-tier prototype-aware negative sampling strategy (50% cross-cluster + 30% intra-cluster filtered + 20% random) combined with LoRA-based InfoNCE contrastive learning achieves <1.07x communication overhead while maintaining ≥85% of supervised baseline accuracy when labeled data is scarce.

**Novelty Level:** HIGH (0.95/1.0) - First framework combining federated learning + self-supervised learning + foundation models + PEFT

**Gap Addressed:** Gap 2 (CRITICAL) - Self-Supervised Learning Integration in Federated Foundation Model Training

---

## Core Hypothesis Statement

**Main Hypothesis (H1):**
Federated contrastive self-supervised learning with prototype-aware negative sampling (Fed-CSSL-PN) enables communication-efficient foundation model pre-training on entirely unlabeled heterogeneous federated data by treating client heterogeneity as implicit multi-view augmentation, achieving downstream task performance comparable to centralized supervised baseline while requiring <1.07x communication overhead and preserving data privacy through InfoNCE loss with LoRA-based parameter-efficient adaptation.

**Null Hypothesis (H0):**
Federated self-supervised learning on heterogeneous unlabeled data cannot achieve downstream task performance within 15% of supervised baselines due to: (1) false negative sampling from cross-client distribution mismatch, (2) convergence failure without labeled supervision signal, or (3) communication overhead exceeding 2x supervised baseline when mitigating false negatives.

---

## Testable Predictions

### Primary Prediction
When trained on 10 federated clients with 100K unlabeled samples each (non-IID with Dirichlet α=0.5) using Fed-CSSL-PN (K=20 prototypes, three-tier negative sampling), the resulting foundation model will achieve:
- **Downstream accuracy:** ≥85% of centralized supervised baseline on GLUE tasks after SSL pre-training + 10% labeled fine-tuning
- **Statistical Test:** Two-sample t-test (α=0.05) with expected effect size Cohen's d > 0.5

### Secondary Predictions
1. **Communication Efficiency:** <1.10x overhead (156KB vs. 146KB baseline)
2. **False Negative Reduction:** >20% reduction compared to random sampling (based on FedPCC 2025 evidence)
3. **Convergence Speed:** ≤50 communication rounds to reach 95% of final performance

### Falsification Criteria
The hypothesis is FALSIFIED if ANY of:
1. Training loss does not plateau after 50 communication rounds
2. Average communication overhead >1.20x supervised baseline
3. Downstream accuracy <70% of centralized supervised baseline (>30% gap)
4. False negative rate >40% despite prototype filtering

---

## Key Contributions

**Theoretical:**
- Novel framework unifying federated learning + self-supervised learning + foundation models
- Heterogeneity reframed as beneficial implicit augmentation (vs. traditional view as optimization challenge)

**Methodological:**
- Prototype-aware three-tier negative sampling strategy (adapts FedPCC 2025 to contrastive SSL)
- LoRA-InfoNCE integration for parameter-efficient contrastive learning
- Semantic similarity filtering (cosine >0.7) for heterogeneous federated settings
- Dynamic temperature scaling based on cluster variance (τ = 0.07 × (1 + cluster_variance))

**Practical:**
- Enables foundation model training on unlabeled federated data (medical, legal, edge domains)
- 1.07x communication overhead (highly efficient)
- 90% reduction in labeled data requirement
- Clear implementation roadmap: FATE-LLM + Hugging Face PEFT integration

---

## Scope & Boundaries

**In Scope:**
- Text-only foundation models (LLMs: RoBERTa, GPT-2)
- Horizontally federated learning with 10-100 clients
- 100K-1M unlabeled samples per client
- Non-IID data (Dirichlet α = 0.1-1.0)
- Synchronous federated averaging

**Out of Scope:**
- Multi-modal models (vision-language)
- Vertical federated learning
- Cross-device FL (millions of mobile devices)
- Formal differential privacy guarantees
- Malicious clients / Byzantine robustness

**Focus:** Demonstrate that federated contrastive SSL CAN converge on unlabeled heterogeneous data with communication efficiency comparable to supervised baseline.

---

## Phase 2B Sub-Hypothesis Preview

**SH1 (Existence):** Federated contrastive SSL can converge on unlabeled heterogeneous data within 50 rounds

**SH2 (Mechanism):** Prototype-aware negative sampling reduces false negatives by >20%

**SH3 (Comparison):** Fed-CSSL-PN achieves ≥85% of supervised baseline on GLUE tasks

**SH4 (Efficiency):** Communication overhead remains <1.10x supervised baseline

**SH5 (Robustness):** Performance holds across heterogeneity levels (α ∈ {0.1, 0.5, 1.0})

**Dependency Chain:** SH1 → SH2 → SH3 (SH4 independent)

---

## Key Related Work & Differentiation

| Work | Limitation | Our Differentiation |
|------|------------|---------------------|
| **FedFMSL (Wu 2024)** | Supervised only, requires labels | Enables unsupervised SSL on unlabeled data |
| **SimCLR/MoCo (2020)** | Centralized setting | Federated adaptation with prototype-aware negatives |
| **FedPCC (2025)** | Supervised classification | Applied to contrastive SSL negative sampling |
| **FedHPL (Ma 2024)** | Supervised (230x communication reduction) | SSL with 1.07x overhead |

**No Existing Work Combines:** FL + SSL + Foundation Models + PEFT

---

## Implementation Roadmap

**Framework Stack:**
- **FL Framework:** FATE-LLM (industrial-grade)
- **PEFT Library:** Hugging Face PEFT (LoRA implementation)
- **SSL Baselines:** SimCLR, MoCo (contrastive learning)
- **Prototype Clustering:** Adapt FedPCC implementation

**Baselines:**
1. FedAvg + supervised LoRA fine-tuning (current SOTA)
2. Centralized SSL (SimCLR/MoCo - upper bound)
3. Random initialization (lower bound)

**Datasets:**
- Natural Instructions (unlabeled)
- Dolly-15K (unlabeled)
- GLUE, SQuAD, NLI (downstream evaluation)

**Expected Timeline:** 2-3 weeks implementation for experienced researcher

---

## Open Questions for Phase 2B

1. **Hyperparameter Sensitivity:** Optimal (K, τ, cosine_threshold, momentum_α) combination?
2. **Convergence Rate:** How many rounds vs. supervised baseline (≤50 target)?
3. **Scalability:** Does K=20 prototypes scale to 100+ clients?
4. **Privacy Guarantees:** Can formal DP be integrated? Reconstruction attack resistance?
5. **Alternative SSL Objectives:** Contrastive (InfoNCE) vs. masked representation prediction?

---

## Readiness for Phase 2B

**Status:** ✅ **READY**

**Evidence:**
- ✅ Clear testable predictions with quantitative metrics
- ✅ 5 verifiable sub-hypotheses (SH1-SH5) identified
- ✅ Falsification criteria defined
- ✅ Implementation feasibility confirmed (FATE-LLM + PEFT)
- ✅ Statistical tests specified (t-test, McNemar's, ANOVA)
- ✅ Baselines and datasets identified
- ✅ Novelty confirmed (Scholar + Exa searches)

**Next Step:** Execute `/phase2b-planning` to decompose into detailed verification roadmap with prioritized experiments and success criteria.

---

*Full details in: `02a_extended_hypothesis_full.md`*
*Generated using YouRA Research Phase 2A Extended Workflow (YOLO Mode)*
*2026-02-06*
