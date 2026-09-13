# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-06
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md (Round 1)
**Hypothesis ID:** H2-R1-01
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H2-R1-01

**Confidence Level:** 8.5/10

**Main Hypothesis:**

In CLIP-style multimodal contrastive learning models, implementing a multi-scale geometric monitoring and automated intervention framework (GeometricWatch) that tracks dispersion metrics (micro-level collapse detection) and RSA-based cross-modal alignment (macro-level semantic consistency) will improve representation quality with <5% computational overhead, measured by:
1. Reduction in geometric pathology occurrence (≥30% fewer collapse events detected post-intervention)
2. Improved downstream task performance (≥1% accuracy improvement on ImageNet zero-shot OR no degradation across 2+ evaluation tasks)
3. Enhanced cross-modal alignment quality (≥5% improvement in RSA correlation scores)

**Alternative Hypothesis (H0):**

Multi-scale geometric monitoring and automated interventions either:
1. Do not significantly reduce geometric pathology occurrence (<10% reduction in collapse events)
2. Degrade downstream task performance (>1% accuracy drop on any evaluation task)
3. Do not improve cross-modal alignment (RSA improvement <2%)
4. Incur unacceptable computational cost (≥10% training time overhead)

### 1.2 Variables

| Variable Type | Variable Name | Operationalization | Measurement |
|--------------|---------------|-------------------|-------------|
| **Independent** | Geometric Monitoring System | Binary: GeometricWatch enabled/disabled | System state (ON/OFF) |
| **Independent** | Intervention Policy | Categorical: None / Dispersive-only / Adaptive | Configuration setting |
| **Independent** | Threshold Calibration Method | Categorical: Fixed / Bootstrap / Adaptive | Two-stage calibration approach |
| **Dependent** | Dispersion Metric | Intra-modal variance: σ²(E_i) where E_i = embeddings from modality i | Computed every 100 steps on batch embeddings |
| **Dependent** | RSA Alignment Score | Cross-modal representational similarity: RSA(E_vision, E_text) ∈ [0,1] | Pearson correlation of distance matrices on 200 sampled pairs |
| **Dependent** | Intervention Event Count | Number of times regularizer triggered during training | Logged events with timestamps |
| **Dependent** | Downstream Task Accuracy | Zero-shot classification accuracy on ImageNet (top-1) | Evaluated at checkpoints (every 5K steps) |
| **Dependent** | Computational Overhead | Training time increase: Δt/t_baseline × 100% | Wall-clock time measurement |
| **Control** | Model Architecture | Fixed: ViT-B/32 vision encoder + BERT-base text encoder | Constant across experiments |
| **Control** | Training Data | Fixed: CC3M (3M image-text pairs) or subset | Same data distribution |
| **Control** | Base Hyperparameters | Learning rate, batch size, optimizer, base loss | Standard CLIP training config |
| **Confound** | Random Initialization | Seed-dependent weight initialization | Control via multiple seeds (n≥3) |
| **Confound** | Data Shuffling Order | Batch sampling randomness | Control via fixed seed for reproducibility |

### 1.3 Causal Mechanism

**Proposed Causal Chain:**

```
Multi-Scale Geometric Monitoring
    ↓
Timely Detection of Pathologies (Dispersion ↓ or RSA ↓)
    ↓
Automated Trigger of Dispersive Regularizer (L_disp)
    ↓
Gradient Modification (∂L_total/∂θ = ∂L_contrastive/∂θ + λ·∂L_disp/∂θ)
    ↓
Geometric Correction (Increased intra-modal variance + maintained cross-modal alignment)
    ↓
Improved Representation Quality
    ↓
Enhanced Downstream Task Performance
```

**Mechanistic Steps:**

1. **Detection Phase:** Compute dispersion σ²(E) and RSA(E_v, E_t) every 100 training steps
2. **Threshold Comparison:** If σ²(E) < μ_bootstrap - 2σ_bootstrap → collapse detected
3. **Intervention Trigger:** Activate dispersive regularizer: L_disp = -log(σ²(E) / σ²_target)
4. **Gradual Application:** Ramp up λ (regularizer strength) from 0 to λ_max over 100 steps
5. **Geometric Restoration:** Regularizer pushes embeddings apart, increasing σ²(E)
6. **Cooldown Period:** Wait 1000 steps before next intervention (stability safeguard)
7. **Performance Impact:** Improved geometry → better semantic encoding → higher task accuracy

**Evidence for Causal Links:**

- **Link 1 (Detection → Intervention):** Statistical anomaly detection (mean - 2σ) is established in process control theory (Shewhart, 1931; adapted to ML monitoring)
- **Link 2 (Intervention → Gradient):** Differentiable regularizer modifies loss landscape; precedent: dropout scheduling (Srivastava et al., 2014), weight decay adaptation
- **Link 3 (Gradient → Geometry):** Xia et al. (2026) prove dispersive regularizer prevents collapse (increases embedding variance)
- **Link 4 (Geometry → Performance):** Brain encoding studies (Tang et al., 2023) show cross-modal alignment quality correlates with semantic task performance
- **Link 5 (RSA metric validity):** Neuroscience literature establishes RSA measures shared representational structure (Kriegeskorte et al., 2008)

**Key Tension:**

The hypothesis balances two potentially conflicting objectives:
1. **Intra-modal diversity** (dispersive regularizer increases variance within each modality)
2. **Cross-modal alignment** (contrastive loss brings paired embeddings closer)

**Resolution Mechanism:** The graduated intervention policy (gradual ramp-up, cooldown periods) prevents destabilization. Contrastive loss dominates (λ_max = 0.1 is small), so alignment is preserved while local collapse is corrected. RSA monitoring ensures cross-modal consistency is not sacrificed.

### 1.4 Key Assumptions

1. **Assumption:** Geometric pathologies (collapse, misalignment) are detectable via low-dimensional statistics (dispersion, RSA) computed on batch-level embeddings
   - **Justification:** Xia et al. (2026) demonstrate variance-based collapse detection; RSA is scale-invariant metric
   - **Validation:** Qualitative inspection via t-SNE plots + quantitative correlation with downstream task performance

2. **Assumption:** Interventions applied mid-training (after warm-up) do not destabilize optimization
   - **Justification:** Precedent from adaptive learning rate schedulers (e.g., ReduceLROnPlateau), dropout scheduling
   - **Risk Mitigation:** Gradual application (100-step ramp-up), cooldown period (1000 steps), max strength bound (λ ≤ 0.1)
   - **Validation:** Monitor training loss convergence curves, check for sudden spikes post-intervention

3. **Assumption:** Computational overhead of metric computation is dominated by efficient matrix operations (O(n_sample²) for RSA, O(d·batch_size) for dispersion)
   - **Justification:** Subsampling (200 pairs for RSA) + periodic computation (every 100 steps) reduces cost
   - **Validation:** Profile with PyTorch profiler, measure wall-clock time per training step

4. **Assumption:** Threshold calibration from bootstrap stage (Stage 1) generalizes to full training (Stage 2)
   - **Justification:** Short bootstrap run (1 epoch on CC3M subset) captures metric distribution
   - **Adaptive Component:** Sliding window (last 1000 steps) allows online threshold adjustment
   - **Validation:** Compare Stage 1 thresholds vs. Stage 2 empirical distributions

5. **Assumption:** Dispersion and RSA metrics are sufficient for detecting critical geometric pathologies (fiber product metric deferred to full version)
   - **Justification:** MVP focuses on most severe pathology (collapse via dispersion) and primary success criterion (cross-modal alignment via RSA)
   - **Scope Limitation:** Meso-level manifold alignment (fiber product) is complexity vs. benefit tradeoff for Phase 2B

### 1.5 Scope & Boundaries

**In-Scope:**
- **Architecture:** CLIP-style dual-encoder models (vision + text) with contrastive loss
- **Modalities:** Vision (images) + Language (text captions)
- **Training Scale:** 3M-10M image-text pairs (CC3M or subset of LAION)
- **Evaluation Tasks:** Zero-shot classification (ImageNet), image-text retrieval (COCO, Flickr30K)
- **Intervention Type:** Dispersive regularizer only (MVP scope)
- **Metrics:** Dispersion (micro-level) + RSA (macro-level)

**Out-of-Scope:**
- **Other Architectures:** Unified encoders (e.g., VisualBERT), generative models (e.g., DALL-E)
- **Other Modalities:** Audio, video, 3D (require separate metric design)
- **Large-Scale Training:** >100M pairs (LAION-400M) deferred to full version
- **Other Interventions:** Anchoring regularizer, combined strategies (full version)
- **Fiber Product Metric:** CCA-based meso-level alignment (full version)
- **Production Deployment:** Focus is experimental validation, not production tool

**Boundary Conditions:**
- **Minimum Training Duration:** ≥10K steps (to observe multiple intervention cycles)
- **Batch Size Range:** 256-2048 (typical for contrastive learning)
- **Embedding Dimensions:** 512-768 (standard CLIP configurations)

**Applicability Limits:**
- Framework assumes paired multimodal data (image-text); not applicable to unpaired settings
- Thresholds calibrated per dataset; cross-dataset generalization requires re-calibration
- Intervention policy hyperparameters (λ_max, ramp-up steps, cooldown) may need task-specific tuning

### 1.6 Testable Predictions

**Primary Prediction:**

**P1:** Training CLIP models with GeometricWatch (dispersion + RSA monitoring, dispersive regularizer) will achieve:
- **Geometric Health:** ≥30% reduction in collapse event count (measured as steps where σ²(E) < threshold) compared to baseline
- **Task Performance:** ≥1% improvement in ImageNet zero-shot top-1 accuracy OR no degradation (≤0.5% drop) across all 3 evaluation tasks (ImageNet, COCO retrieval, Flickr30K retrieval)
- **Computational Efficiency:** <5% training time overhead (wall-clock time increase ≤5%)

**Secondary Predictions:**

**P2:** Post-intervention metric improvement:
- Within 500 steps after intervention trigger, dispersion σ²(E) will increase by ≥20% relative to pre-intervention value
- RSA alignment score will remain stable (Δ < 5%) or improve during intervention periods

**P3:** Intervention frequency stabilization:
- Early training (steps 1K-10K): Higher intervention rate (1 per 500 steps average)
- Mid-training (steps 10K-30K): Lower intervention rate (1 per 1000 steps average)
- Late training (steps 30K+): Minimal interventions (1 per 2000 steps average)
- **Rationale:** As model learns better representations, geometric pathologies become less frequent

**P4:** Correlation between geometric metrics and task performance:
- Positive correlation between average dispersion σ²(E) and downstream accuracy (r > 0.3, p < 0.05)
- Positive correlation between RSA alignment and retrieval Recall@10 (r > 0.4, p < 0.05)
- **Implication:** Validates that monitored geometric properties are task-relevant

**Falsification Criteria:**

The hypothesis is **falsified** if ANY of the following occur:
1. **Geometric metric improvement <10%:** Interventions do not meaningfully affect geometry
2. **Task performance degradation >1%:** Interventions harm rather than help
3. **Training instability:** Loss diverges or fails to converge with GeometricWatch enabled
4. **Computational overhead ≥10%:** Efficiency requirement violated
5. **No correlation (|r| < 0.1) between metrics and performance:** Monitored metrics are not task-relevant

**Edge Cases to Test:**
- Very small batch size (64): Does RSA subsampling break down?
- Very high learning rate (10× baseline): Does intervention exacerbate instability?
- Dataset with low diversity (single-domain like COCO only): Are thresholds still valid?

### 1.7 SOTA Baseline (Optional - If SOTA Comparison Mode)

**Not Applicable (Methodology Contribution, Not SOTA Performance)**

GeometricWatch is a **monitoring and intervention framework** that augments existing CLIP training, not a new model architecture competing for SOTA benchmark performance.

**Baseline Comparisons:**
- **Primary Baseline:** Standard CLIP training (Open_CLIP implementation) without geometric monitoring
- **Secondary Baselines (Ablation):**
  - Monitoring without intervention (to isolate detection value)
  - Fixed regularization (λ constant) without adaptive triggering (to isolate intervention timing value)

**Performance Context:**
- Baseline CLIP (ViT-B/32 on CC3M): ~40-45% ImageNet zero-shot top-1 accuracy (reference: Open_CLIP benchmarks)
- Goal: Match or exceed baseline (≥1% improvement), not compete with SOTA large-scale models (e.g., CLIP ViT-L/14 @ 75%+)

### 1.8 Statistical Verification Design

**Experimental Design:** Between-subjects design with multiple seeds

**Groups:**
1. **Control Group:** Standard CLIP training (no GeometricWatch)
2. **Experimental Group 1:** GeometricWatch with bootstrap threshold calibration
3. **Experimental Group 2:** GeometricWatch with adaptive threshold calibration
4. **Ablation Group 1:** Monitoring only (no intervention)
5. **Ablation Group 2:** Fixed dispersive regularizer (λ=0.05 constant)

**Sample Size:**
- **Runs per group:** n = 5 (different random seeds)
- **Total runs:** 5 groups × 5 seeds = 25 training runs
- **Rationale:** n=5 sufficient for t-tests with medium effect size (Cohen's d ≈ 0.8), power=0.8

**Randomization:**
- Random seeds control initialization and data shuffling
- Counterbalancing training order (randomize which group runs first) to control for hardware variations

**Statistical Tests:**

1. **Primary Outcome (Task Performance):**
   - **Test:** One-sided independent samples t-test
   - **Null Hypothesis:** μ_experimental ≤ μ_control (no improvement)
   - **Alternative:** μ_experimental > μ_control (improvement)
   - **Significance Level:** α = 0.05
   - **Effect Size:** Cohen's d ≥ 0.5 (medium effect)

2. **Geometric Metrics:**
   - **Test:** Paired t-test (pre-intervention vs. post-intervention within same run)
   - **Null Hypothesis:** Δσ²(E) ≤ 0 (no dispersion increase)
   - **Alternative:** Δσ²(E) > 0 (dispersion increases)
   - **Significance Level:** α = 0.05

3. **Correlation Analysis:**
   - **Test:** Pearson correlation between average dispersion and final accuracy
   - **Null Hypothesis:** ρ = 0 (no correlation)
   - **Alternative:** ρ > 0 (positive correlation)
   - **Significance Level:** α = 0.05
   - **Minimum r:** 0.3 (medium correlation)

**Multiple Comparisons Correction:**
- Bonferroni correction for 4 primary comparisons (4 experimental/ablation groups vs. control): α_corrected = 0.05/4 = 0.0125

**Confound Control:**
- **Hardware:** All runs on same GPU type (A100 or V100)
- **Software:** Fixed PyTorch version, CUDA version, Open_CLIP commit hash
- **Data:** Fixed dataset splits, same preprocessing pipeline
- **Checkpoints:** Save at fixed intervals (every 5K steps) for temporal analysis

**Data Analysis Plan:**
1. Compute descriptive statistics (mean, std) for each group
2. Check normality assumptions (Shapiro-Wilk test)
3. If normal: parametric t-tests; if non-normal: Mann-Whitney U test
4. Report effect sizes (Cohen's d) alongside p-values
5. Visualize with box plots (task performance) and time series (geometric metrics)

**Stopping Rules:**
- **Early Success:** If p < 0.001 with n=3, stop early (Bayesian argument: overwhelming evidence)
- **Futility:** If effect size < 0.2 (small) with n=5, consider stopping (unlikely to reach significance)
- **Adverse Events:** If any run shows training divergence (loss → NaN), investigate and potentially exclude

---

## 2. Contribution Summary

**Theoretical Contribution:**

1. **Multi-Scale Geometric Quality Framework:** First systematic framework connecting geometric properties at multiple scales (micro: intra-modal variance, macro: cross-modal alignment) to multimodal representation quality. Provides theoretical justification for why monitoring both dispersion and RSA captures complementary pathology types.

2. **Bridging Neuroscience and Multimodal ML:** Adapts RSA (Representational Similarity Analysis) from neuroscience to practical multimodal training monitoring, demonstrating cross-domain transfer of metrics for measuring shared semantic structure.

3. **Automated Intervention Theory:** Establishes principles for mid-training geometric interventions with stability guarantees (warm-up, gradual application, cooldown), drawing parallels to control theory and adaptive optimization.

**Methodological Contribution:**

1. **Practical Geometric Monitoring System:** Delivers production-ready PyTorch callback for CLIP-style models with <5% overhead, making geometric quality tracking accessible to practitioners without specialized expertise.

2. **Two-Stage Threshold Calibration Protocol:** Novel methodology combining bootstrap initialization (Stage 1) and adaptive sliding window adjustment (Stage 2), addressing the challenge of setting anomaly detection thresholds without manual tuning.

3. **Conservative Intervention Policy:** Operationalizes stability safeguards (warm-up, ramp-up, cooldown, max strength) as concrete hyperparameters, providing reusable template for adaptive regularization in multimodal training.

4. **Validation Methodology:** Establishes experimental protocol for evaluating geometric health interventions, including pre/post-intervention analysis, correlation studies, and falsification criteria.

**Practical Contribution:**

1. **Diagnostic Tool for CLIP Practitioners:** Addresses real need in community deploying CLIP-style models (OpenAI CLIP: 32K stars, Open_CLIP: 13K stars) who currently lack geometry diagnostics.

2. **Reduced Manual Hyperparameter Tuning:** Automated threshold calibration and adaptive intervention reduce trial-and-error in regularization strength selection.

3. **Interpretable Training Insights:** TensorBoard logging of geometric metrics provides interpretable signals (dispersion collapse, alignment drift) vs. opaque loss curves.

4. **Extensible Framework:** Open_CLIP integration via callbacks enables easy adoption; architecture supports future extensions (fiber product metric, anchoring regularizer).

**Gap Resolution (Targeting Gap 2 from Phase 1):**

Gap 2 identified "Inadequate Understanding of Representation Geometry's Role in Multimodal Learning Quality" with four missing pieces:

1. ✅ **Metrics for Geometric Quality:** Provides dispersion (collapse detection) + RSA (alignment quality)
2. ✅ **Diagnostic Tools:** TensorBoard integration for real-time monitoring
3. ✅ **Design Principles:** Automated intervention policy based on anomaly detection
4. ✅ **Performance Connection:** Validation protocol tests correlation between geometry and downstream tasks

**Novelty vs. Prior Work:**

- **Xia et al. (2026):** Proposes dispersive/anchoring regularizers but NO monitoring or automation → GeometricWatch adds real-time detection and adaptive triggering
- **Tang et al. (2023):** Studies brain encoding with multimodal representations but NO training application → GeometricWatch adapts RSA for training-time monitoring
- **Zhao et al. (2024):** Algebraic geometry perspective on alignment but NO practical system → GeometricWatch provides computational implementation (deferred fiber product to full version)
- **CLIP Implementations:** No geometric quality monitoring tools → GeometricWatch fills practitioner gap

**Broader Impact:**

- Enables data-driven understanding of which geometric properties matter for specific downstream tasks
- Reduces wasted compute from training models with geometric pathologies
- Provides foundation for future work on geometric quality in other multimodal architectures (audio-visual, 3D-language)

---

## 3. Key Related Work

### 3.1 Geometric Regularization in Multimodal Learning

**[CORE]** Xia, Z., Wang, H., et al. (2026). "When Gradient Optimization Is Not Enough: Dispersive and Anchoring Geometric Regularizer for Multimodal Learning"
- Semantic Scholar ID: ac7f9f7077d45c1f5ba8c8aa557a904d13d3e523
- **Contribution:** Identifies representation collapse and cross-modal inconsistency as geometric pathologies; proposes dispersive regularizer (increases intra-modal variance) and anchoring regularizer (bounds cross-modal drift)
- **Relation to Hypothesis:** Provides dispersive regularizer as core intervention mechanism; GeometricWatch extends with monitoring and automated triggering
- **Gap:** No monitoring system or adaptive application strategy

**[SUPPORTING]** Zhao, D. (2024). "Approximate Fiber Product: Algebraic-Geometric Perspective on Multimodal Embedding Alignment"
- Semantic Scholar ID: fa91bcdb7844152c718150873c159633e71697ff
- **Contribution:** Models multimodal alignment via fiber product theory from algebraic geometry; decomposes space into Z_s (shared) ⊕ Z_I (image-specific) ⊕ Z_T (text-specific)
- **Relation to Hypothesis:** Provides theoretical foundation for meso-level alignment metric (fiber product approximation via CCA, deferred to full version)
- **Gap:** Highly theoretical, no computational implementation or practical training integration

### 3.2 Cross-Modal Representation Analysis

**[CORE]** Tang, J., Du, M., et al. (2023). "Brain encoding models based on multimodal transformers can transfer across language and vision"
- Semantic Scholar ID: 32d0ad59162b07bf469b6889930ef1d10e66f7f8
- Citations: 55
- **Contribution:** Demonstrates that multimodal transformer representations encode shared semantic dimensions, validated via fMRI brain encoding; shows cross-modal transfer of representations
- **Relation to Hypothesis:** Provides RSA-based cross-modal alignment metric and validation that alignment quality correlates with semantic representation
- **Adaptation:** GeometricWatch uses RSA for training-time monitoring (not post-hoc analysis)

**[SUPPORTING]** Liang, P.P., Lyu, Y., et al. (2022). "High-Modality Multimodal Transformer: Quantifying Modality & Interaction Heterogeneity"
- Semantic Scholar ID: 0651e9cbe0b8c1b4465c80d2309af62e5e4da574
- Citations: 43
- **Contribution:** Proposes information-theoretic metrics for modality heterogeneity (H_m) and interaction heterogeneity (H_i); HighMMT scales to 10 modalities
- **Relation to Hypothesis:** Establishes precedent for quantifying modality interactions; GeometricWatch focuses on geometry (dispersion, alignment) rather than information theory

### 3.3 Contrastive Learning Foundations

**[FOUNDATIONAL]** Jia, C., Yang, Y., et al. (2021). "Scaling Up Visual and Vision-Language Representation Learning With Noisy Text Supervision" (ALIGN)
- Semantic Scholar ID: 141a5033d9994242b18bb3b217e79582f1ee9306
- Citations: 4,964
- **Contribution:** Establishes dual-encoder + contrastive loss paradigm for vision-language alignment at scale (1B+ pairs); demonstrates noise tolerance
- **Relation to Hypothesis:** Defines baseline CLIP-style architecture that GeometricWatch augments; validates contrastive learning as standard approach

**[IMPLEMENTATION]** OpenAI CLIP (Radford et al., 2021) + Open_CLIP (Ilharco et al., 2021)
- GitHub Stars: 32,400 (CLIP) + 13,300 (Open_CLIP)
- **Contribution:** Widely adopted implementations of contrastive vision-language learning
- **Relation to Hypothesis:** Open_CLIP provides callback infrastructure for GeometricWatch integration; represents target practitioner community

### 3.4 Robustness in Multimodal Learning

**[RELATED]** Zhao, Y., Xi, W., et al. (2025). "Enhancing Multimodal Model Robustness Under Missing Modalities via Memory-Driven Prompt Learning"
- Semantic Scholar ID: f31d2855986539d9f1cb2863366635f6c83a1cd8
- **Contribution:** Addresses missing modality robustness through prompt learning and cross-modal compensation
- **Relation to Hypothesis:** Different robustness challenge (missing modalities vs. geometric pathologies); complementary approach

**[RELATED]** Jiang, C., Wang, Z., et al. (2025). "Survey of Adversarial Robustness in Multimodal Large Language Models"
- Semantic Scholar ID: 12b7d01ea49be7ab142b2788ed697148e828a714
- Citations: 11
- **Contribution:** Comprehensive survey on adversarial attacks/defenses for multimodal models
- **Relation to Hypothesis:** Different robustness focus (adversarial attacks vs. training pathologies); out of scope for GeometricWatch

### 3.5 Training Dynamics and Scalability

**[RELATED]** Zhu, J., Wang, W., et al. (2025). "InternVL3: Exploring Advanced Training and Test-Time Recipes for Open-Source Multimodal Models"
- Semantic Scholar ID: cddf14e5b97090111d3fa814c9aec60e2bf24b8a
- Citations: 855
- **Contribution:** Native multimodal pre-training (not post-hoc adaptation); variable visual position encoding; achieves SOTA on MMMU
- **Relation to Hypothesis:** Different focus (scaling to SOTA performance vs. geometric health monitoring); potential future integration target

**[RELATED]** Liu, W., Li, J., et al. (2024). "Diving into Self-Evolving Training for Multimodal Reasoning"
- Semantic Scholar ID: 3a8192a2cea57217b15ec80c2dea66db56eb5238
- Citations: 28
- **Contribution:** Self-evolving training with automatic balancing; M-STAR framework
- **Relation to Hypothesis:** Different adaptation mechanism (RL-based vs. geometric regularization); complementary to GeometricWatch

### 3.6 Representational Similarity Analysis (RSA)

**[FOUNDATIONAL - NEUROSCIENCE]** Kriegeskorte, N., Mur, M., Bandettini, P. (2008). "Representational similarity analysis - connecting the branches of systems neuroscience"
- **Contribution:** Establishes RSA as method for comparing representational geometries via distance matrix correlations
- **Relation to Hypothesis:** Foundational method adapted for cross-modal alignment monitoring in GeometricWatch

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence): Geometric Pathologies Are Detectable and Prevalent**

*"Do CLIP-style models exhibit detectable geometric pathologies (dispersion collapse, RSA alignment degradation) during training, and can these be captured by batch-level metrics?"*

**Verification Approach:**
- Train baseline CLIP on CC3M, compute dispersion and RSA every 100 steps
- Statistical analysis: Identify anomalous periods (< μ - 2σ), measure frequency
- Qualitative validation: t-SNE plots at collapse vs. healthy timepoints
- **Expected Outcome:** ≥10% of training steps show anomalous metrics (validates need for monitoring)

**SH2 (Mechanism): Automated Interventions Improve Geometric Health**

*"Does triggering dispersive regularizer when pathologies are detected increase dispersion and stabilize RSA within 500 steps post-intervention?"*

**Verification Approach:**
- Implement intervention system, analyze pre/post-intervention metric trajectories
- Paired statistical test: Δσ²(E) pre→post, ΔRSA pre→post
- Control for natural fluctuations via baseline (no intervention) comparison
- **Expected Outcome:** σ²(E) increases ≥20%, RSA remains stable (Δ < 5%)

**SH3 (Comparison): Geometric Health Correlates with Task Performance**

*"Do models with better geometric health (higher average dispersion, higher RSA) achieve superior downstream task performance?"*

**Verification Approach:**
- Train 5 models with GeometricWatch, 5 without; evaluate ImageNet zero-shot + retrieval
- Correlation analysis: average dispersion vs. accuracy, average RSA vs. Recall@10
- Causal inference: Compare experimental (with intervention) vs. control (without)
- **Expected Outcome:** Pearson r > 0.3 (geometric metrics ↔ performance), p < 0.05

### Readiness Checklist

- [x] **Core hypothesis statement is specific and testable:** Yes - quantitative predictions (≥30% collapse reduction, ≥1% accuracy improvement, <5% overhead)
- [x] **Variables are operationalized:** Yes - dispersion (σ²), RSA (Pearson r), overhead (Δt/t), accuracy (top-1 %)
- [x] **Causal mechanism is articulated:** Yes - 7-step chain from detection → intervention → gradient → geometry → performance
- [x] **Key assumptions are explicit:** Yes - 5 assumptions with justifications and validation plans
- [x] **Scope boundaries are defined:** Yes - in-scope (CLIP, vision+text, 3M-10M pairs) vs. out-of-scope (other architectures, other modalities)
- [x] **Falsification criteria exist:** Yes - 5 concrete conditions that would falsify hypothesis
- [x] **Statistical design is specified:** Yes - between-subjects design, n=5 per group, t-tests with α=0.05, Bonferroni correction
- [x] **Related work is contextualized:** Yes - 6 categories with gap analysis showing novelty
- [x] **Sub-hypotheses are identifiable:** Yes - SH1 (existence), SH2 (mechanism), SH3 (comparison)
- [x] **Contribution is clear:** Yes - theoretical (multi-scale framework), methodological (monitoring system), practical (diagnostic tool)

**Overall Readiness:** HIGH - Ready for Phase 2B decomposition and verification planning

### Open Questions

**Technical Uncertainties:**

1. **Q1:** What is the optimal cooldown period (currently 1000 steps)? Too short → instability, too long → missed interventions
   - **Investigation Plan (Phase 2B):** Ablation study with cooldown ∈ {500, 1000, 2000, 5000}
   - **Success Criterion:** Identify value that maximizes stability (no loss spikes) while maintaining responsiveness

2. **Q2:** How do thresholds generalize across datasets (CC3M → LAION, COCO)?
   - **Investigation Plan (Phase 2B):** Bootstrap calibration on each dataset, compare threshold distributions
   - **Success Criterion:** If μ differs by >50%, per-dataset calibration required; if <20%, single calibration sufficient

3. **Q3:** Does intervention effectiveness degrade over training (early vs. late training)?
   - **Investigation Plan (Phase 2B):** Stratify intervention events by training phase (early: 0-10K, mid: 10-30K, late: 30K+), analyze post-intervention Δσ²
   - **Success Criterion:** If early Δσ² >2× late Δσ², phase-dependent intervention strategies needed

**Methodological Uncertainties:**

4. **Q4:** What is the minimum n_sample for reliable RSA estimation (currently 200)?
   - **Investigation Plan (Phase 2B):** Compute RSA with n ∈ {50, 100, 200, 500, full batch}, measure correlation with full-batch RSA
   - **Success Criterion:** r > 0.9 with full-batch indicates reliable estimation; use minimum n achieving this

5. **Q5:** Is dispersion metric sufficient or should we add kurtosis (distribution shape)?
   - **Investigation Plan (Phase 2B):** Compute kurtosis alongside dispersion, test if kurtosis provides additional predictive value
   - **Success Criterion:** If partial correlation (kurtosis | dispersion) with performance is >0.2, include kurtosis; else dispersion sufficient

**Theoretical Uncertainties:**

6. **Q6:** Does improved RSA alignment causally improve task performance, or is it epiphenomenal?
   - **Investigation Plan (Phase 2B):** Intervention targeting RSA directly (e.g., alignment regularizer), test if performance improves
   - **Success Criterion:** If RSA-targeted intervention → performance gain, causal; if not, correlation is spurious

7. **Q7:** What is the theoretical relationship between dispersion and downstream task generalization?
   - **Investigation Plan (Phase 2B):** Measure dispersion at checkpoints, evaluate on in-distribution (ImageNet) vs. out-of-distribution (ImageNetV2, ObjectNet)
   - **Success Criterion:** If high dispersion correlates with OOD performance, supports generalization hypothesis

**Scope Expansion Considerations:**

8. **Q8:** Can GeometricWatch extend to other multimodal architectures (unified encoders, generative models)?
   - **Investigation Plan (Phase 3):** Defer to full version; requires architecture-specific metric adaptations
   - **Decision Point:** If CLIP validation succeeds in Phase 2B, justify expansion in Phase 3

9. **Q9:** Is fiber product approximation (via CCA) feasible and beneficial for meso-level monitoring?
   - **Investigation Plan (Full Version):** Implement CCA-based fiber product metric, test computational overhead and task correlation
   - **Decision Point:** If MVP (dispersion + RSA) is insufficient (correlation r < 0.3), prioritize fiber product in full version

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-06*
