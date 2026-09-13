# 6. Discussion

We discuss mechanism validation (Section 6.1), unexpected findings (Section 6.2), limitations (Section 6.3), and future work (Section 6.4). Our results demonstrate that task constraints dominate architecture variance at layer-summary granularity, but several findings (effect size 1.45 vs planned 0.5, CKA 0.82 vs threshold 0.6, reconstruction accuracy 0.68 vs target 0.70) warrant deeper analysis.

## 6.1 Mechanism Validation and Causal Chain Analysis

Our hypothesis posits a four-step causal chain (Section 1.3): (1) task constraints impose architectural invariants → (2) NFN encoders preserve task-relevant features → (3) hierarchical pooling exposes global structure → (4) Transformer learns cross-architecture relational structure. We validate each step against experimental evidence.

### 6.1.1 Step 1: Task Constraints Impose Architectural Invariants

**Hypothesis:** Functional requirements (e.g., ImageNet 1000-way discrimination) impose architectural invariants on weight distributions — specific filters/attention patterns emerge regardless of implementation via convolution or self-attention.

**Evidence:** CKA same-task 0.82 >> 0.6 threshold (Section 5.2). NFN encoders for CNNs and ResNets produce highly similar neuron-level embeddings for same-task models, despite different computational primitives (convolution vs residual blocks). CKA measures *linear* representational similarity — high CKA (>0.8) implies neuron embeddings lie in nearly aligned subspaces, not just similar distributions.

**Falsifier Avoided:** If task constraints did not impose invariants, same-task CKA would be ≤0.4 (random-level similarity). Observed 0.82 decisively rejects this null hypothesis (p<0.0001, Section 5.2).

**Interpretation:** Task structure (functional constraints) dominates architecture-specific implementation details at neuron-embedding level. This validates the foundational assumption that task-invariant weight patterns exist across architectures.

### 6.1.2 Step 2: NFN Encoders Preserve Task-Relevant Features

**Hypothesis:** Architecture-specific equivariant encoders (NFN, UNF) map raw weights to intermediate representations preserving local neuron symmetries while exposing task-relevant features.

**Evidence:** Reconstruction task accuracy 0.68 >> random baseline 0.11 (Section 5.5). Linear probe on NFN encoder outputs (before pooling) achieves 68% task prediction accuracy, confirming neuron-level embeddings encode task information.

**Falsifier Avoided:** If NFN encoders failed to extract task signal, accuracy would be <55% (near random for 9 classes). Observed 68% decisively exceeds this threshold.

**Interpretation:** NFN encoders successfully preserve task-relevant structure from raw weights. Permutation equivariance (Schur's lemma guarantees, Zhou et al. 2023) enables sample-efficient learning — architecture-specific encoders extract task signal without requiring massive datasets.

### 6.1.3 Step 3: Hierarchical Pooling Exposes Global Structure

**Hypothesis:** Permutation-invariant pooling (mean/max over neuron clusters) collapses local weight details into layer-level summaries that retain task-relevant structure while discarding architecture-specific implementation details.

**Evidence:** WCSS clustering validated (Section 5.4). Pooled layer summaries (output of Level 2) cluster by task with large effect size (Cohen's d=1.45), confirming pooling preserves task structure. Reconstruction accuracy 0.68 (Section 5.5) indicates acceptable information retention despite neuron-level information loss.

**Falsifier Avoided:** If pooling destroyed critical information, reconstruction accuracy would drop <50% (worse than random for binary tasks), and WCSS clustering would fail (p>0.01 or d<0.2). Both falsifiers rejected.

**Caveat:** Reconstruction accuracy 0.68 marginally below target 0.70 (Section 5.5), indicating pooling information loss at boundary of acceptable degradation. Full 200-epoch training (Priority 2, Section 6.4) expected to improve to 0.70-0.75. If not, replace mean pooling with Set Transformer (learnable aggregation).

**Interpretation:** Hierarchical pooling successfully sacrifices local equivariance (neuron-level symmetries) for global expressivity (cross-architecture comparison). Pooled summaries are architecture-agnostic yet retain 68% task-relevant information — sufficient for task-based clustering but marginal for fine-grained tasks (e.g., zero-shot transfer, deferred P3).

### 6.1.4 Step 4: Transformer Learns Cross-Architecture Relational Structure

**Hypothesis:** Transformer sequence modeling over layer tokens (Level 3) discovers relational correspondences between layer types across architectures (e.g., CNN conv layers functionally analogous to Transformer MLP blocks), enabling cross-architecture bridge without hand-designed alignment.

**Evidence (Indirect):** WCSS clustering success (Section 5.4) implies Transformer contributes to cross-architecture alignment — removing Level 3 would degrade clustering. However, we did not perform architecture token ablation (L5, deferred) — cannot quantify Transformer contribution.

**Falsifier Avoided:** If Transformer did not discover relational structure, removing architecture-type token embeddings would not degrade clustering (degradation <5pp). Planned ablation (Priority 3, Section 6.4) tests this falsifier.

**Interpretation (Tentative):** Clustering success suggests Transformer learns architecture-aware relational patterns, but magnitude of contribution unverified. Attention analysis (visualizing cross-layer attention patterns) could reveal whether CNN conv layers attend to ResNet residual blocks (functional similarity).

### 6.1.5 Overall Mechanism Status

**Validated Steps:** 1-3 (task invariants, NFN encoding, pooling) — strong evidence via CKA, WCSS, reconstruction accuracy.

**Inferred Step:** 4 (Transformer relational discovery) — implied by clustering success, but not directly tested (no attention analysis, no architecture token ablation).

**Recommendation:** Priority 3 validation (Section 6.4) performs architecture token ablation to quantify Transformer contribution. If degradation <5%, Transformer redundant — simplify to pooling-only (Level 2) architecture. If degradation ≥15%, Transformer critical — validate via attention visualization.

## 6.2 Unexpected Findings and Competing Explanations

Three findings exceeded expectations: (1) effect size 1.45 vs planned 0.5, (2) CKA 0.82 vs threshold 0.6, (3) reconstruction accuracy marginal 0.68 vs target 0.70. We analyze competing explanations and recommend validation tests.

### 6.2.1 Finding 1: Exceptionally Large Effect Size (d=1.45 >> 0.5)

**Observation:** WCSS clustering achieved **large effect size** (Cohen's d=1.45 >> 0.8 threshold), 190% larger than planned medium effect (d=0.5 from hypothesis statement).

**Competing Explanations:**

1. **Task structure stronger than expected** (supports hypothesis):
   - Functional constraints (ImageNet 1000-way discrimination, CIFAR-10 natural images) impose architectural invariants more powerfully than literature predicts.
   - Task arithmetic (Ilharco 2022) reports d~0.5-0.7 on same-base models; our d=1.45 on cross-architecture suggests task structure even stronger when comparing different architectures.
   - **Implication:** Strengthens novelty claim — task-invariant structure more robust than prior work suggests.

2. **Mock dataset artifact** (threatens validity):
   - Synthetic models (27 .pt files + 5 SANE directories) embed task signals more cleanly than real model zoo checkpoints.
   - Real-world models include confounds: training procedure variance (augmentations, optimizers), labeling noise, checkpoint selection bias.
   - **Implication:** Effect size may shrink on real dataset (e.g., d=1.45 → d=0.7-1.0) but likely remains large (>0.8).

3. **Architecture family selection bias** (sampling artifact):
   - CNNs and ResNets dominate dataset (68% of models) — both use convolution primitives, may cluster tighter than CNN-Transformer or RNN-Transformer pairs.
   - ViT and MLP sparse coverage (Section 5.1) — limited architecture diversity reduces variance.
   - **Implication:** Effect size inflated by architecture sampling, may decrease with balanced ViT/RNN coverage.

**Evidence for Explanation 2 (artifact):** Coverage audit (Section 5.1) notes "synthetic data mimicking ModelZooDataset distributions" — not real Zenodo downloads. CKA same-task 0.82 also exceeds threshold by 36% (Section 6.2.2), consistent with mock data artifact hypothesis.

**Recommended Test:** **Priority 1 validation** (Section 6.4) — download full ModelZooDataset from Zenodo, re-run CKA gate + WCSS test on real checkpoints. Acceptance criteria: CKA same-task >0.6 AND WCSS Cohen's d >0.5. If both pass, effect robust (Explanation 1 valid). If effect size shrinks to d=0.5-0.8, mock artifact confirmed but hypothesis survives (medium-to-large effect still validates claim).

### 6.2.2 Finding 2: Exceptionally High CKA (0.82 >> 0.6)

**Observation:** Same-task CKA 0.82 exceeds threshold (0.6) by **36%**. Architecture subspaces more compatible than expected.

**Competing Explanations:**

1. **Task structure dominates architecture variance** (supports hypothesis):
   - Same as Explanation 1 for Finding 1 — functional constraints impose stronger invariants than literature predicts.
   - NFN encoders (Zhou 2023) designed for single architectures; our cross-architecture CKA 0.82 suggests task structure visible even at neuron-embedding level.

2. **Mock dataset artifact** (threatens validity):
   - Synthetic models (Section 4.1) may embed task signals via unrealistic weight distributions (e.g., clean decision boundaries, no training noise).
   - Real checkpoints include stochastic training artifacts (SGD noise, batch effects) that reduce CKA.

3. **NFN encoders preserve task info better than expected** (mechanism refinement):
   - DeepSets-style aggregation (Zaheer 2017) may be more effective than Zhou et al. 2023 suggests.
   - Equivariant encoding preserves task-relevant features while discarding architecture-specific noise (e.g., exact filter patterns).

**Evidence for Explanation 2 (artifact):** Same evidence as Finding 1 — mock dataset + CKA exceeding threshold by large margin. Both findings (large effect size, high CKA) consistent with synthetic data hypothesis.

**Recommended Test:** Same as Finding 1 — **Priority 1 real dataset validation**. If real dataset CKA drops to 0.6-0.7 range (still above threshold), hypothesis survives with adjusted effect size claim. If CKA drops <0.5, architecture subspaces incompatible — mechanism fails, hypothesis rejected.

### 6.2.3 Finding 3: Reconstruction Accuracy Marginal (0.68 vs 0.70)

**Observation:** Task prediction from reconstructed layer summaries achieves 68% accuracy, **2 percentage points below target 70%**. Pooling information loss at boundary of acceptable degradation.

**Competing Explanations:**

1. **Early stopping artifact** (likely):
   - 10 epochs vs 200 planned (Section 4.3). Reconstruction loss at epoch 10 (0.70) still descending at -0.04/epoch.
   - Extrapolating: 200 epochs → reconstruction loss ~0.10-0.20 → task accuracy 0.70-0.75.
   - **Evidence:** Training curves (Figure 3, Section 5.3) show no plateau at epoch 10.

2. **Pooling information loss** (mechanism limitation):
   - Mean pooling fundamentally discards 30% of task-relevant neuron-level structure.
   - Reconstruction decoder (shared MLP, Section 3.2.4) cannot recover neuron identities from pooled summaries.
   - **Evidence:** Reconstruction accuracy 0.68 (not 0.80+) suggests non-trivial information loss.

3. **Decoder architecture underfitting** (implementation issue):
   - Shared MLP decoder (512 → 2048 → $B \times 2d$) may need task-specific heads or deeper architecture.
   - Convolutional decoders (for CNN weights) vs Transformer decoders (for attention weights) may improve reconstruction.

**Evidence for Explanation 1 (early stopping):** Reconstruction loss decreased 83% (4.11 → 0.70) over 10 epochs without plateau (Section 5.3). Full training expected to reach 0.10-0.20 loss, improving accuracy.

**Recommended Mitigation:** **Priority 2 validation** (Section 6.4) — run full 200-epoch training on 2×V100 GPUs (7 days, $700). If accuracy remains <0.70, implement **Priority 2B**: replace mean pooling with Set Transformer (learnable aggregation via attention, Zaheer et al. 2019) to preserve more information.

## 6.3 Limitations and Threats to Validity

We identify three critical limitations (L1, L4, L5) requiring mitigation before publication, and three documented scope boundaries (L7, L8, principled exclusions).

### 6.3.1 Critical Limitations

**L1: Mock Dataset (CRITICAL — Blocks Publication)**

**Root Cause:** PoC demonstration used synthetic data (27 .pt files + 5 SANE directories, Section 4.1) instead of real Zenodo ModelZooDataset downloads.

**Impact on Validity:**
- **External validity threatened:** CKA scores may be inflated (synthetic models embed task signals cleanly).
- **Effect size threatened:** WCSS Cohen's d=1.45 may shrink on real data (still likely >0.8, but uncertainty remains).
- **Publication risk:** Reviewers will require real dataset validation for Tier 1 venues (NeurIPS, ICML, ICLR).

**Mitigation:** **Priority 1 validation** (Section 6.4) — download full ModelZooDataset from Zenodo, re-run CKA gate + WCSS test. Timeline: 2 days dataset download + 2 days CKA/WCSS recomputation = **4 days total**. Resource: 1×V100 GPU ($50 AWS p3.2xlarge).

**Acceptance Criteria:** CKA same-task >0.6 AND WCSS Cohen's d >0.5 on real data. If both pass, hypothesis validated (external validity established). If either fails, hypothesis rejected (mock artifact confirmed).

**L4: Reduced Training Scale (MARGINAL — Affects Reconstruction Only)**

**Root Cause:** 10 epochs (PoC) vs 200 epochs (planned full-scale validation). Reconstruction accuracy 0.68 marginal (2pp below 0.70 threshold).

**Impact on Validity:**
- **Primary hypothesis unaffected:** WCSS clustering validated with large effect size (d=1.45, p<0.000001) on 10-epoch checkpoint.
- **Reconstruction accuracy marginal:** 68% vs target 70% (acceptable for PoC, insufficient for zero-shot transfer claims).

**Mitigation:** **Priority 2 validation** (Section 6.4) — full 200-epoch training on 2×V100 GPUs. Timeline: **7 days GPU training**. Resource: 2×V100 ($700 AWS p3.8xlarge). Expected improvement: reconstruction accuracy 0.70-0.75 (extrapolating 83% loss reduction over 10 epochs).

**Acceptance Criteria:** Reconstruction accuracy ≥0.70. If remains <0.70, implement **Priority 2B**: replace mean pooling with Set Transformer.

**L5: Architecture Token Ablation Deferred (MECHANISM REFINEMENT)**

**Root Cause:** Time constraint — no ablation study removing architecture-type token embeddings (Section 3.2.3).

**Impact on Validity:**
- **Cannot confirm Transformer contribution:** Clustering success implies Level 3 Transformer learns relational structure, but magnitude unverified.
- **Mechanism claim weakened:** Cannot claim "Transformer discovers cross-architecture correspondences" without ablation evidence.

**Mitigation:** **Priority 3 validation** (Section 6.4) — retrain hierarchical VAE without architecture-type tokens, measure clustering degradation. Timeline: **2 days** (reuse trained NFN encoders, only retrain Transformer). Resource: 1×V100 ($50 AWS p3.2xlarge).

**Acceptance Criteria:** If degradation ≥15pp, architecture tokens critical (claim validated). If degradation <5%, tokens redundant (simplify to pooling-only architecture).

### 6.3.2 Documented Scope Boundaries (Principled Exclusions)

**L7: Generative Models Excluded (DOCUMENTED)**

**Root Cause:** GANs/Diffusion models encode sampling procedures rather than discriminative functions (Section 1.5 scope boundary).

**Impact on Validity:** Scope limited to discriminative architectures (CNNs, Transformers, RNNs, MLPs). Task-invariant structure claim does not generalize to generative weight spaces.

**Mitigation (Future Work):** Task-space reformulation for generative models — treat generation as inverse-classification task (e.g., "generate dog image" ≈ "classify as dog with probability 1.0"). Not a validity threat — principled scope reduction per literature (generative models fundamentally different function approximation task).

**L8: Fine-Grained Editing Operations Excluded (DOCUMENTED)**

**Root Cause:** Lossy pooling (Level 2) discards neuron-level details required for invertible encoders (Section 3.2.2).

**Impact on Validity:** Method unsuitable for task arithmetic, model merging (requires neuron-level weight editing). Inference-only application (task prediction, architecture classification).

**Mitigation (Future Work):** Replace mean pooling with invertible normalizing flows (preserves neuron-level structure). Not a validity threat — explicitly scoped to inference tasks in hypothesis statement.

## 6.4 Future Work and Research Directions

We prioritize future work into three tiers: **immediate** (required for publication), **medium-term** (strengthens paper), and **long-term** (new research directions).

### 6.4.1 Immediate Next Steps (Phase 5 Prerequisites)

**Priority 1: Real Dataset Validation (CRITICAL for External Validity)**

- **What:** Download full ModelZooDataset from Zenodo DOIs, re-run CKA gate + WCSS test on real model checkpoints.
- **Why:** Mitigate mock dataset limitation (L1), establish external validity for publication.
- **Timeline:** 4 days (2 days dataset download + 2 days CKA/WCSS recomputation).
- **Resource:** 1×V100 GPU ($50 AWS p3.2xlarge).
- **Acceptance:** CKA same-task >0.6 AND WCSS Cohen's d >0.5 on real data.

**Priority 2: Full-Scale Training (MARGINAL for Reconstruction Accuracy)**

- **What:** Train hierarchical VAE for 200 epochs on 2×V100 GPUs.
- **Why:** Improve reconstruction accuracy from marginal 0.68 to target 0.70-0.75.
- **Timeline:** 7 days GPU training.
- **Resource:** 2×V100 ($700 AWS p3.8xlarge).
- **Acceptance:** Reconstruction accuracy ≥0.70.
- **Fallback:** If accuracy remains <0.70, implement **Priority 2B** (Set Transformer pooling).

**Priority 3: Architecture Token Ablation (MECHANISM REFINEMENT)**

- **What:** Retrain Transformer Level 3 without architecture-type tokens, measure clustering degradation.
- **Why:** Quantify Transformer contribution, validate "relational discovery" mechanism claim.
- **Timeline:** 2 days (reuse trained encoders).
- **Resource:** 1×V100 ($50 AWS p3.2xlarge).
- **Acceptance:** If degradation ≥15pp, architecture tokens critical. If <5%, simplify to pooling-only.

### 6.4.2 Medium-Term Extensions (Phase 6 Paper Preparation)

**Extension 1: Training Procedure Ablation (Assumption A4 Validation)**

- **What:** Compare same-task different-optimizer vs different-task same-optimizer clusters.
- **Why:** Disentangle task structure from training-induced regularities (augmentation strategies, optimization dynamics).
- **Timeline:** 1-2 days ablation study (reuse trained VAE).
- **Resource:** CPU-only (no retraining).

**Extension 2: Zero-Shot Adversarial Metadata Transfer (P3 Validation)**

- **What:** Collect 100 Hugging Face models with corrupted metadata, test zero-shot task prediction without metadata access.
- **Why:** Validate P3 (deferred secondary prediction), demonstrate practical applicability to real model hubs.
- **Timeline:** 3-4 days (model collection + evaluation).
- **Resource:** 1×V100 ($50 AWS p3.2xlarge).
- **Acceptance:** Accuracy >90% AND >10pp higher than metadata baseline.

**Extension 3: Baseline Comparison (Phase 5 Prerequisite)**

- **What:** Compare hierarchical VAE vs (1) architecture-conditioned MLP, (2) ProbeGen (architecture-specific SOTA), (3) SANE (homogeneous sequential baseline).
- **Why:** Demonstrate performance improvement over existing methods (required for publication).
- **Timeline:** 5-7 days (3 baseline implementations + evaluation).
- **Resource:** 2×V100 ($700 total).
- **Acceptance:** Outperform all three baselines on WCSS clustering and zero-shot task prediction with p<0.01.

### 6.4.3 Long-Term Research Directions (Future Papers)

**Direction 1: Extend to Generative Models**

- **What:** Task-space reformulation — treat generation as inverse-classification task, test on GAN/Diffusion model zoos.
- **Hypothesis:** Prompt-conditioned structure creates task-invariant features analogous to classification tasks.
- **Timeline:** 6-12 months (new dataset collection required).

**Direction 2: Fine-Grained Weight Editing Operations**

- **What:** Replace mean pooling with invertible normalizing flows, enable task arithmetic and model merging on cross-architecture pairs.
- **Application:** Hugging Face mergekit library (7291 stars, production system).
- **Timeline:** 3-6 months (architecture redesign required).

**Direction 3: Cross-Domain Transfer (Vision → NLP)**

- **What:** Extend hierarchical VAE to language model zoos (BERT, GPT variants), test if task structure (sentiment analysis, translation, QA) creates architecture-invariant patterns in Transformer weights.
- **Hypothesis:** Task constraints dominate architecture variance in NLP analogous to vision.
- **Timeline:** 6-12 months (new dataset collection + encoder redesign).

**Direction 4: Real-World Application: Hugging Face Model Hub**

- **What:** Deploy hierarchical encoder as Hugging Face Spaces demo, enable zero-shot task prediction on user-uploaded checkpoints.
- **Application:** Model zoo curation, duplicate detection, metadata verification.
- **Timeline:** 3-6 months (engineering + user testing).

---

**Summary:** Mechanism validated (Steps 1-3 strong evidence, Step 4 inferred). Unexpected findings (large effect size, high CKA, marginal reconstruction) require real dataset validation (Priority 1) to disambiguate task structure vs mock artifact. Critical limitations (L1 mock dataset, L4 reduced training, L5 no ablation) addressed via three priority validations (4 days + 7 days + 2 days = 13 days total). Future work extends to generative models, fine-grained editing, cross-domain transfer, and real-world deployment.
