# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-05-12T08:09:18.677458Z
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: GAP-001
- **Gap Title**: Scalable Permutation Equivariant Architectures for Diverse Model Families
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova (Creative Novelty Explorer), Prof. Vera (Rigorous Validation Architect), Dr. Sage (Research Impact Evaluator), Prof. Pax (Feasibility & Reality Checker), Dr. Ally (Hypothesis Strengthening Champion), Prof. Rex (Hypothesis Stress-Test Master)

**Total Exchanges**: 15

**Convergence Reason**: All 6 personas reached consensus on hypothesis structure, predictions, and validation protocol after comprehensive discussion addressing novelty, falsifiability, significance, and feasibility.

### Key Insights

1. **Quotient Structure Breakthrough (Exchange 6)**: Prof. Pax's insight that we don't need full group preservation, only shared quotient structure preservation, shifted the hypothesis from mathematically over-constrained to theoretically plausible.

2. **Slot-Equivariance Framework (Exchange 7)**: Dr. Ally unified all concerns into the coherent formulation E_a(g·M) ≈ ρ(π_a(g))E_a(M), where architecture-specific permutations project to abstract slot permutations.

3. **Comprehensive Validation Protocol (Exchange 9)**: Prof. Vera structured 9 quantitative success criteria with explicit failure modes, transforming a vague idea into falsifiable science.

4. **Kernel Robustness Refinement (Exchange 12)**: Prof. Rex's two-level invariance test (IID + OOD) with adversarial perturbations prevents false positives from accidental agreement or flat-basin effects.

5. **Identifiability Requirement (Exchange 14)**: Prof. Vera's cross-seed Procrustes <0.10 criterion ensures canonical coordinates are unique, not arbitrary rotations.

### Breakthrough Moments

- **Exchange 6**: Quotient structure reframing - architectures as coordinate systems over shared manifold
- **Exchange 7**: Slot-equivariance synthesis - mathematical formulation with learned projection π_a
- **Exchange 9**: Complete experimental protocol - 9 criteria covering all aspects of the hypothesis
- **Exchange 12**: Adversarial perturbation requirement - ensures kernel captures true symmetries
- **Exchange 14**: Cross-seed identifiability - proves quotient is uniquely defined

---

## Final Hypothesis

### Title
**Learnable Cross-Architecture Canonicalization via Quotient-Level Slot Equivariance (H-LCAC-v1)**

### Core Claim

Under conditions where neural network architectures (CNNs, Transformers, RNNs) solve the same task via exchangeable computations, if we apply architecture-specific encoders E_a that project model weights into a shared K-dimensional quotient space Z with learned slot-permutation operators ρ(g), then cross-architecture transferability will emerge as measured by probe transfer (≥80%), zero-shot equivariance on unseen architectures (≥70%), and linear alignment (Procrustes error <0.15), because the quotient space factorizes out architecture-specific coordinate conventions while preserving task-relevant computational structure through equivariance constraints.

**Formal Statement**: There exist learned functions E_a: W_a → Z ⊂ ℝ^K and slot permutations ρ: S_K → GL(K) such that:

1. **Slot Equivariance**: ||E_a(g·M) - ρ(π_a(g))E_a(M)|| < ε
2. **Functional Kernel**: g ∈ ker(π_a) iff g preserves model function both IID and OOD
3. **Geometric Reconciliation**: Tangent-space alignment increases from pre-projection to post-projection
4. **Linear Alignment**: Architecture-conditioned distributions in Z are linearly alignable (low Procrustes error)

### Mechanism

**Step 1: Slot Space Projection**
Architecture-specific encoders E_a learn to project weight tensors into K-dimensional slot space Z, where each slot represents a task-relevant computational unit (e.g., feature detector, attention head).

**Step 2: Equivariance Enforcement**
The equivariance loss L_equiv = ||E_a(g·M) - ρ(π_a(g))E_a(M)||² enforces that weight-space permutations (neuron reordering, layer swaps) correspond to simple slot permutations in Z via learned projection π_a: G_a → S_K.

**Step 3: Task-Relevant Structure Learning**
The contrastive loss L_contrast pulls embeddings of functionally similar models together and pushes dissimilar ones apart, ensuring slots capture task-relevant structure. Weak task supervision (0.1 weight) anchors the quotient space to prevent arbitrary rotations.

**Step 4: Architecture-Independent Canonicalization**
The learned quotient space Z factorizes out architecture-specific coordinate conventions (neuron ordering, layer indexing), leaving only task-relevant computational structure. This enables:
- Linear alignment between E_CNN(M_CNN) and E_Transformer(M_Transformer)
- Transfer of learned slots from CNNs to new Transformer instances without retraining (frozen-K generalization)
- Disentanglement of task accuracy from architecture predictability (Pareto frontier with knee point)

**Causal Chain**: Equivariance loss → Slot permutation structure → Architecture-independent canonicalization → Cross-architecture transferability

---

## Predictions

### Primary Predictions (P1-P3)

**P1: Probe Transfer Accuracy**
- **Claim**: Linear probe trained on CNN embeddings will achieve ≥80% accuracy on Transformer embeddings AND ≥10pp above DeepSets baseline (p<0.05)
- **Success**: Demonstrates cross-architecture task-relevant structure preservation
- **Failure**: Accuracy <70% or gain <5pp indicates embeddings are architecture-specific

**P2: Zero-Shot Equivariance on Unseen Architecture**
- **Claim**: Slot encoder trained on CNNs and Transformers will generalize to RNNs without retraining, achieving ≥70% zero-shot equivariance AND ≥25pp above DeepSets
- **Success**: Proves slot abstraction is architecture-general
- **Failure**: Accuracy <50% indicates quotient space is architecture-family-specific

**P3: Linear Cross-Architecture Alignment**
- **Claim**: CNN and Transformer embeddings will be linearly compatible with Procrustes error <0.15 AND ≥30% lower than permutation-null baseline (p<0.01)
- **Success**: Confirms shared canonical coordinate system
- **Failure**: Error >0.30 or no improvement over null indicates geometric coincidence, not canonicalization

### Supporting Predictions (P4-P9)

**P4: Kernel Robustness** - ≥90% of weight-space permutations preserve model outputs (D<0.01) on both IID and OOD tests, with adversarial perturbations inducing ≥10× higher divergence

**P5: Pareto Frontier Knee Point** - Task accuracy vs. architecture predictability exhibits knee where task≥95% baseline while architecture≤40%, with curvature significantly higher than linear baseline

**P6: Cross-Seed Identifiability** - Slot spaces learned from different random seeds align with Procrustes error <0.10, confirming canonical coordinates are unique

**P7: Frozen-K Generalization** - Adding RNN with frozen K achieves R_RNN<10% AND E_RNN<2×baseline without retraining

**P8: Cross-Task Retention** - Slot activations correlate ≥0.6 (Spearman) between ImageNet and CIFAR-10, showing task-general structure

**P9: Ablation Necessity** - Removing equivariance loss causes zero-shot accuracy to drop ≥15pp, proving equivariance causally enables transferability

---

## Novelty

### Key Innovation

1. **Quotient-level canonicalization** (vs. weight-space methods): Projects to architecture-agnostic quotient space that factors out coordinate artifacts, unlike Git Re-Basin (native weight-space) or model merging (heuristic averaging)

2. **Permutation equivariance over slots** (vs. functional embeddings): Leverages permutation symmetries to define structured slot spaces where architectural differences are group actions, beyond unstructured NFN embeddings

3. **Structural validation** (vs. performance metrics): Tests geometric properties (kernel robustness, linear alignment, identifiability) for structural not just functional meaning

4. **Cross-architecture generalization** (vs. single-family methods): Targets cross-architecture equivariance - maps CNN and Transformer symmetries to shared group representation

### Differentiation from Prior Work

- **DeepSets (Zaheer et al. 2017)**: Permutation-invariant but no equivariance enforcement or canonicalization structure
- **Git Re-Basin (Ainsworth et al. 2022)**: Native weight-space alignment, architecture-specific, no quotient abstraction
- **NFN (Zhou et al. 2023)**: Unstructured weight embeddings, homogeneous populations only, no geometric constraints
- **Model Merging (Wortsman et al. 2022)**: Heuristic averaging without theoretical grounding or quotient alignment

---

## Experimental Design

### Dataset & Models

- **ModelZoo-14K**: 14,000 pretrained models from Hugging Face (CNNs, Transformers, RNNs)
- **Architectures**: ResNet, VGG (CNN), ViT, DeiT (Transformer), LSTM-based classifiers (RNN)
- **Tasks**: ImageNet (primary), CIFAR-10 (cross-task validation), ImageNet-V2 (OOD robustness)
- **Split**: 70% train / 15% val / 15% test

### Method

**Slot-Equivariant Encoder**
- Architecture: Deep Sets backbone with equivariance loss
- Loss: L = L_contrastive + λ_equiv·L_equivariance + 0.1·L_task_probe
- Optimization: Adam, lr=1e-4, batch size 32, 50 epochs
- Seeds: 3 independent runs for identifiability test

### Baselines

1. **DeepSets** - Permutation-invariant baseline without equivariance constraints
2. **Git Re-Basin** - Native weight-space alignment via permutation search
3. **Neural Functional Networks (NFN)** - Unstructured weight embeddings
4. **Function-Space Embedding** - Embed via output logits on fixed 10K ImageNet samples

### Validation Protocol (9 Criteria)

1. ✓ **Geometric Pre-Check**: Principal angles <60° pre-projection, improvement post-projection
2. ✓ **Kernel Robustness**: ≥90% pass D<0.01 on IID+OOD, adversarial ≥10× divergence
3. ✓ **Probe Transfer**: ≥80% AND ≥10pp above DeepSets (p<0.05)
4. ✓ **Zero-Shot Equivariance**: ≥70% AND ≥25pp above DeepSets on RNN
5. ✓ **Pareto Frontier**: Task≥95%, arch≤40%, curvature > linear baseline
6. ✓ **Cross-Task Retention**: Spearman ρ≥0.6 between ImageNet and CIFAR-10
7. ✓ **Linear Alignment**: Procrustes <0.15 AND ≥30% below null (p<0.01)
8. ✓ **Frozen-K**: R_RNN<10% AND E_RNN<2× on new architecture
9. ✓ **Ablation**: Zero-shot drops ≥15pp without L_equiv (p<0.01)

**Cross-Seed Identifiability**: Pairwise Procrustes <0.10 across 3 seeds

### Compute Budget

- **Total**: ~200 A100 GPU-hours over 2 weeks
- **Timeline**: 2 weeks implementation + 2 weeks compute + 1 week analysis = 5 weeks

---

## Limitations

### Scope Boundaries

**In Scope:**
- Feedforward architectures (CNNs, Transformers, RNNs) on supervised classification
- Models 10M-100M parameters
- Image classification tasks

**Out of Scope:**
- Graph Neural Networks, Diffusion Models, Mamba architectures (future work)
- Unsupervised/generative tasks (different symmetry structures)
- Multimodal models (architecture serves different modalities)

### Known Limitations

1. **Slot dimensionality K**: Must be calibrated per task complexity (too small → reconstruction error, too large → redundancy)
2. **Task diversity**: Limited to supervised classification - unsupervised/generative requires separate validation
3. **Architecture coverage**: CNN/Transformer/RNN all feedforward/sequential - structurally diverse families need expansion
4. **Dataset bias**: ModelZoo-14K is Hugging Face-curated, may reflect pipeline artifacts (mitigation: test on TensorFlow Hub, Papers With Code)
5. **Task specificity**: Cross-task retention ≥0.6 required to claim task-general slots (not dataset-specific)

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 personas consensus after 15 exchanges |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None |
| **Compute Feasibility** | Yes (~200 A100 GPU-hours, 2 weeks) |
| **Implementation Stack** | PyTorch, scipy, sklearn (production-ready) |
| **Phase 2B Ready** | YES |

---

## Impact Assessment

### If Successful

**Immediate Impact (1-2 years):**
- First unified benchmark for heterogeneous model zoos
- Cross-architecture model merging with theoretical grounding
- Architecture-agnostic model analysis tools

**Medium-Term Impact (2-5 years):**
- Meta-learning across architecture families becomes feasible
- Architecture search guided by latent space geometry (predict success without training)
- Model editing and steering that works across CNNs, Transformers, and future architectures

**Long-Term Field Direction (5+ years):**
- Shift from "architecture design" to "task-manifold navigation" as primary research question
- Unified theory of learned representations transcending architectural specifics
- Democratization of model zoo insights (mine 71M models, not just architectural specialty)

### If Hypothesis Fails

**Scientific Value of Failure:**
Each failure mode establishes fundamental facts:
- Kernel failure → Exchangeability is architecture-specific
- Pareto failure → Task structure couples to architecture
- Frozen-K failure → Architectural diversity is irreducible
- Cross-seed failure → Quotient has multiple valid factorizations

Both success and failure advance knowledge about architecture-task relationships.

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
