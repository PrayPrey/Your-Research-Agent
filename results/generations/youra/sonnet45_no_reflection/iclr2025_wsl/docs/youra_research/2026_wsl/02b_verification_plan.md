# Verification Plan: Quotient-Level Cross-Architecture Canonicalization

**Date:** 2026-05-12
**Hypothesis ID:** H-LCAC-v1
**Confidence:** 0.80
**Total Hypotheses:** 2

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under conditions where neural network architectures (CNNs, Transformers, RNNs) solve the same task via exchangeable computations, if we apply architecture-specific encoders E_a that project model weights into a shared K-dimensional quotient space Z with learned slot-permutation operators ρ(g), then cross-architecture transferability will emerge as measured by probe transfer (≥80%), zero-shot equivariance on unseen architectures (≥70%), and linear alignment (Procrustes error <0.15), because the quotient space factorizes out architecture-specific coordinate conventions while preserving task-relevant computational structure through equivariance constraints.

### 1.2 Alternative Hypothesis (H0)

There is no shared quotient representation across heterogeneous architectures: architecture-specific coordinate conventions are fundamental to computation (not factorizable), resulting in probe transfer ≤70%, zero-shot equivariance ≤50%, linear alignment error ≥0.30, or Pareto analysis showing no knee point (uniform compression rather than selective canonicalization).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | ModelZoo-14K (standard) | Provides heterogeneous model population (CNNs, Transformers, RNNs) at scale required to test cross-architecture canonicalization. 70% train / 15% val / 15% test split enables robust validation. |
| **Model** | Slot-Equivariant Encoder | Deep Sets provides permutation-invariant baseline; adding explicit equivariance loss L_equiv = \|\|E_a(g·M) - ρ(π_a(g))E_a(M)\|\|² enforces quotient-level structure. Weak task supervision (0.1 weight) anchors space. |

**Dataset Details:**
- Source: Hugging Face model hub (14,000 pretrained models)
- Path: https://huggingface.co/

**Model Details:**
- Type: Set-based encoder with Deep Sets backbone + equivariance loss
- Source: Custom implementation based on Zaheer et al. 2017 Deep Sets

### 1.4 Baseline Methods (for comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| DeepSets | ~70% probe transfer, ~40% zero-shot equivariance | ModelZoo-14K |
| Git Re-Basin | Weight-space alignment within single architecture | CIFAR-10/100 models |
| NFN (Zhou et al. 2023) | +17% INR classification | Homogeneous INR zoos |
| Function-Space Embedding | Baseline via output logits | ImageNet 10K samples |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Exchangeability exists | Lottery Ticket Hypothesis (Frankle & Carbin 2019) | Kernel robustness test fails (D>0.01) |
| A2 | Quotient space is finite-dimensional | Johnson-Lindenstrauss lemma | Frozen-K generalization fails (R>25%) |
| A3 | Linear alignment is sufficient | Procrustes analysis, task arithmetic | Linear alignment test fails (error >0.30) |
| A4 | Task supervision is weak (0.1) | Prof. Pax recommendation | Cross-seed identifiability fails (Procrustes >0.15) |
| A5 | Permutation groups are learnable | Git Re-Basin learns permutations | Zero-shot equivariance test fails (<50%) |

### 1.6 Research Gap & Novelty

**Gap**: Existing methods (NFN, Git Re-Basin, Model Merging) operate either within single architecture families or use unstructured weight embeddings. No prior work demonstrates scalable equivariant processing across heterogeneous model families (CNN/Transformer/RNN) with geometric validation of shared canonical coordinates.

**Novelty**: Cross-architecture equivariant canonicalization via learned quotient-level slot representations with structural validation (kernel robustness, linear alignment, identifiability) beyond performance metrics.

**Scope Reduction**: 33% reduction via Established Facts (4 BUILD_ON claims require no verification: permutation symmetries, NFN for homogeneous populations, model merging, Deep Sets). Focus verification on 2 PROVE_NEW claims: cross-architecture equivariance and quotient-level slot equivariance.

---

## 2. Hypotheses

### 2.1 Inventory

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
          HYPOTHESIS INVENTORY (2 hypotheses)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| ID | Type | Statement (Brief) | Prerequisites | Status |
|----|------|-------------------|---------------|--------|
| H-E1 | EXISTENCE | Finite-dimensional quotient space exists across architectures | None | READY |
| H-M | MECHANISM | Equivariance loss enables cross-architecture canonicalization | H-E1 | READY |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

---

### 2.2 Hypothesis Specifications

---

#### H-E1: Quotient Space Existence

**Type:** EXISTENCE  
**Statement:** Under conditions where neural network architectures (CNNs, Transformers, RNNs) solve the same task via exchangeable computations, if we apply architecture-specific encoders that project model weights into a shared K-dimensional quotient space, then a finite-dimensional quotient space will exist that captures task-relevant computational structure across architectures, as measured by reconstruction error <10%, frozen-K generalization to unseen architectures (R_RNN<10%), and kernel robustness (≥90% of permutations preserve outputs with D<0.01).

**Rationale** (2-3 sentences):  
This hypothesis validates the foundational claim that weight-space structure can be factorized into architecture-independent representations. Success proves that task-relevant information exists in a lower-dimensional manifold independent of architectural coordinate systems, establishing the existence precondition for all subsequent mechanism tests.

**Variables** (from Phase 2A):
- **Independent**: Architecture Family (CNN/Transformer/RNN), Number of Slots K (16/32/64), Model Weights M (14,000 pretrained models)
- **Dependent**: Reconstruction Error, Frozen-K Generalization (R_RNN), Kernel Robustness (%)
- **Controlled**: Model Size (10M-100M parameters), Training Dataset (ImageNet), Random Seed (3 seeds)

**Verification Protocol** (3-5 steps):
1. Train Deep Sets encoder with equivariance loss on CNN+Transformer subset from ModelZoo-14K (70% train, 15% val, 15% test split).
2. Determine minimal K where reconstruction error <10% threshold via binary search over K∈{16, 32, 64, 128}.
3. Apply frozen K to RNN test set without retraining, measure reconstruction error R_RNN.
4. Test kernel robustness via 1000 random neuron permutations per model, measure functional preservation (output divergence D<0.01).
5. Validate that ≥90% of permutations preserve model outputs on both IID (ImageNet) and OOD (ImageNet-V2) test sets.

**Success Criteria** (PoC: Quantitative thresholds):
- **Primary**: Reconstruction error <10% at K=64, Frozen-K generalization R_RNN<10%, Kernel robustness ≥90% (both IID and OOD)
- **Secondary**: Cross-seed consistency (Procrustes <0.10 between quotient spaces learned from different seeds), OOD robustness matches IID (difference <5pp)

**Gate**:
- Type: MUST_WORK (foundational)
- If Fail: H-M cannot proceed (quotient space does not exist)

**Prerequisites**: None (foundation hypothesis)

**Failure Response**:  
- IF frozen-K fails (R_RNN>25%): Quotient is architecture-specific → PIVOT to per-family encoders, redesign mechanism
- IF kernel robustness fails (<70%): Permutation symmetries not captured → EXPLORE alternative slot encodings (attention-based, graph neural networks)
- IF reconstruction passes but frozen-K fails: Dimensional stability violated → ABANDON shared manifold hypothesis

**Source**: Phase 2A Section 1.6 (Predictions P1, P4, P7) + Section 5 (SH1 Existence)

---

#### H-M: Equivariance Mechanism (Integrated 4-Step Chain)

**Type:** MECHANISM  
**Statement:** Under the existence of a quotient space (H-E1), if we apply equivariance loss L_equiv that enforces weight-space permutations map to slot permutations (Step 2), combined with contrastive loss for task-relevant structure (Step 3) and weak task supervision for anchoring (Step 4), then the learned quotient space will factorize out architecture-specific coordinate conventions while preserving computational structure (Step 5), as measured by probe transfer accuracy ≥80%, zero-shot equivariance on unseen architectures ≥70%, linear alignment (Procrustes error <0.15), and cross-seed identifiability (Procrustes <0.10).

**Rationale** (2-3 sentences):  
This hypothesis tests the causal mechanism connecting equivariance enforcement to cross-architecture transferability. It validates that the proposed training objective (equivariance + contrastive + weak supervision) produces architecture-independent canonicalization rather than arbitrary embeddings, and that this canonicalization enables both probe transfer and zero-shot generalization through shared geometric structure.

**Variables** (from Phase 2A):
- **Independent**: Equivariance Loss Weight λ_equiv (0.0-1.0), Architecture Family (CNN train, Transformer train, RNN zero-shot test)
- **Dependent**: Probe Transfer Accuracy (%), Zero-Shot Equivariance Error, Linear Alignment Error (Procrustes), Cross-Seed Identifiability (Procrustes)
- **Controlled**: K=64 (from H-E1 results), Contrastive loss weight=0.1, Task supervision weight=0.1, Model Size (10M-100M), Training Dataset (ImageNet)

**Verification Protocol** (3-5 steps):
1. Train 5 encoder variants with λ_equiv ∈ [0, 0.25, 0.5, 0.75, 1.0] on CNN+Transformer models from ModelZoo-14K.
2. For each variant, train linear probe (logistic regression) on CNN embeddings (Z_CNN), test on Transformer embeddings (Z_Transformer) to measure cross-architecture transfer accuracy.
3. Apply encoder to RNN models (zero-shot, no retraining), measure equivariance error ||E_RNN(g·M) - ρ(g)E_RNN(M)|| for 100 random permutations per model.
4. Compute Procrustes alignment between Z_CNN and Z_Transformer distributions to test linear compatibility of quotient spaces.
5. Train 3 independent encoders (λ=0.5, different random seeds), measure pairwise Procrustes alignment to test identifiability of canonical coordinates.
6. Compare λ=0.5 vs λ=0 (DeepSets baseline without equivariance) to isolate causal contribution via ablation (expect ≥15pp drop when removing equivariance).

**Success Criteria** (PoC: Quantitative thresholds + baseline gaps):
- **Primary**: Probe transfer ≥80% AND ≥10pp above DeepSets, Zero-shot equivariance ≥70% AND ≥25pp above DeepSets, Linear alignment Procrustes <0.15
- **Secondary**: Cross-seed identifiability Procrustes <0.10 (all 3 pairwise comparisons), Ablation shows ≥15pp drop in zero-shot accuracy when removing equivariance loss (proves causality)

**Gate**:
- Type: MUST_WORK (mechanism validation)
- If Fail: Mechanism does not produce claimed canonicalization → redesign training objective or abandon quotient approach

**Prerequisites**: H-E1 (requires quotient space existence and frozen K from H-E1 results)

**Failure Response**:  
- IF Procrustes >0.30: Linear alignment insufficient → PIVOT to nonlinear adapters (MLP alignment layers) or explore manifold learning
- IF probe transfer fails but equivariance passes: Task-relevant structure not captured → EXPLORE stronger task supervision or different contrastive objectives
- IF cross-seed identifiability fails (Procrustes >0.15): Multiple valid factorizations exist → ABANDON uniqueness claim, redesign anchoring mechanism
- IF ablation shows <5pp drop: Equivariance is non-causal (ornamental) → ABANDON equivariance-driven approach

**Source**: Phase 2A Section 1.3 (Causal Mechanism 4 steps) + Section 1.6 (Predictions P1, P2, P3, P6, P9)

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Reconstruction <10%, R_RNN<10%, Kernel ≥90% | PIVOT or ABANDON |
| H-M | MUST_WORK | All 4 metrics pass thresholds + baseline gaps | REDESIGN or ABANDON |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 2C | Experiment Design (H-E1, H-M) | 2-3 days |
| Phase 3 | Implementation Planning (H-E1, H-M) | 3-4 days |
| Phase 4 | Coding & PoC Validation (H-E1 → H-M) | 8-10 days |
| Phase 5 | Baseline Comparison (Optional) | 5-7 days |

**Total Duration:** 18-24 days (Phase 5 skippable if module.yaml skip_baseline_comparison=true)

---

*Generated by YouRA Phase 2B (v7.7.0) | 2026-05-12*
