# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-06
**Author:** Pray
**Source Round:** 02a_round_2_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-SVFitUnlearn-v1
**Confidence Level:** 0.80

**Main Hypothesis:**
Under the condition of pre-trained foundation models with encoded bias, if we apply SVFit-based unlearning to top-k bias-encoding singular values identified via influence functions, then we achieve ≥90% demographic parity improvement at <0.1% parameter cost because bias information concentrates in specific singular values within the low-rank subspace, and cross-bias transfer allows single-attribute debiasing to mitigate multiple bias dimensions simultaneously.

**Alternative Hypothesis (H0):**
There is no significant difference in demographic parity improvement between SVFit-based unlearning (<0.1% parameters) and full-model unlearning (100% parameters), OR SVFit-based unlearning achieves <75% of full-model unlearning performance (i.e., <67.5% DP improvement vs. 90% baseline).

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| k (number of singular values) | Independent | Top-k singular values determined by influence function magnitude (gradient-based approximation) | k ∈ {10, 50, 100, 500} |
| Target protected attribute | Independent | Primary bias dimension for unlearning (gender, race, religion); measured via demographic labels | Categorical: {gender, race, religion} |
| Demographic parity improvement | Dependent | DP = \|P(Ŷ=1\|A=a) - P(Ŷ=1\|A=b)\| where A is protected attribute; improvement = (DP_before - DP_after) / DP_before × 100% | Target: ≥90% (range: 0-100%) |
| Parameter efficiency | Dependent | Trainable parameters / Total parameters × 100% | Target: <0.1% (compare to 6.25% LoRA, 100% full) |
| Accuracy retention | Dependent | Test accuracy post-unlearning / Baseline accuracy × 100% | Threshold: ≥95% (<5% degradation) |
| Cross-bias transfer magnitude | Dependent | Reduction in secondary bias dimensions without direct debiasing; measured as % DP improvement for race/religion after gender-only unlearning | Target: ≥50% reduction |
| Model architecture | Controlled | Fixed pre-trained model | BERT-large (340M), ViT-B (86M), GPT-2 (124M-1.5B) |
| Dataset | Controlled | Standardized fairness benchmarks | CelebA (202K, gender/smile), CUB-200 (11K, pose), WikiText (LLM) |
| Training protocol | Controlled | Hyperparameters fixed across experiments | LR=1e-4, BS=32, early stopping patience=5, same seeds |

### 1.3 Causal Mechanism

**3-Step Causal Chain:**

**Step 1:** SVD decomposition + influence function → Identification of bias-encoding singular values
- **Mechanism:** Singular value decomposition factorizes weight matrices W = UΣV^T, revealing orthogonal information modes. Gradient-based influence functions (Qiao et al. 2025) approximate parameter importance by computing ∇_θ L_bias, identifying which singular values encode bias vs. utility.
- **Evidence:** SVFit (Sun et al. 2024) demonstrates 99% information captured in top-r singular values for task adaptation; influence functions have been validated for selective parameter identification in machine unlearning.
- **Falsification:** If bias is uniformly distributed (>20% gradient magnitude in tail values), influence functions fail to concentrate identification.

**Step 2:** Selective gradient descent on top-k singular values → Bias removal at <0.1% parameter cost
- **Mechanism:** Training only top-k singular values (identified in Step 1) via gradient descent on demographic parity loss L_DP = |P(Ŷ=1|A=a) - P(Ŷ=1|A=b)|. SVFit theory shows this subspace captures critical information while maintaining parameter efficiency.
- **Evidence:** SVFit achieves 16× fewer parameters than LoRA (6.25%) while maintaining performance (Sun et al. 2024, 6 citations). Bias-aware unlearning (Aylapuram et al. 2025) shows <5% accuracy loss is achievable with selective forgetting.
- **Falsification:** If SVFit's SVD approach does not transfer to unlearning (removing vs. adding information uses different subspaces), ablation study will reveal LoRA ≥ SVFit performance.

**Step 3:** Single-attribute debiasing → Cross-bias transfer reduces multiple bias dimensions
- **Mechanism:** Debiasing one protected attribute (e.g., gender) in the low-rank subspace affects shared bias representations, causing spillover reduction in correlated attributes (race, religion). Transfer operates through overlapping bias-encoding singular values.
- **Evidence:** Lu et al. 2024 empirically demonstrates cross-domain transfer unlearning - gender debiasing mitigates race/religion bias in LLMs (3 citations). Mechanism validated through masked language modeling experiments.
- **Falsification:** If cross-bias transfer magnitude <50% reduction at PEFT scale, single-pass efficiency claim fails. Empirical test: measure secondary bias DP after primary debiasing.

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | SVFit (Sun et al. 2024) | Top-r singular values capture 99% information; 16× fewer parameters than LoRA | Strong |
| Step 1 → Step 2 | Soft Weighted Unlearning (Qiao et al. 2025) | Influence functions identify critical parameters for selective unlearning | Medium |
| Step 2 → Step 3 | Bias-Aware Unlearning (Aylapuram et al. 2025) | 94-97% DP improvement with <5% accuracy loss via selective forgetting | Strong |
| Step 3 → Outcome | Transfer Unlearning (Lu et al. 2024) | Cross-bias transfer: gender debiasing reduces race/religion bias empirically | Medium |

**Key Tension:**
- **Tension:** Aylapuram et al. 2025 shows bias-aware unlearning works via full model updates (94-97% improvement), while SVFit (Sun et al. 2024) achieves efficiency via low-rank approximation for task adaptation (not unlearning). These operate in opposite directions: unlearning removes information while PEFT adds information.
- **Resolution:** This verification plan explicitly tests whether SVFit's efficiency transfers to unlearning via 3-way ablation study (SVFit vs. LoRA vs. full-rank). If transfer fails, hypothesis falls back to LoRA efficiency (6.25% parameters, still 16× better than full); if transfer succeeds, achieves 100× efficiency. Either outcome provides publishable contribution (positive: new method; negative: important null result on transfer limits).

### 1.4 Key Assumptions

1. **Bias concentration assumption:** Bias information is concentrated in identifiable singular values (>80% bias gradient in top-k) rather than uniformly distributed across all parameters.
   - **Evidence:** SVFit captures 99% task information in top-r values (Sun et al. 2024)
   - **Testable:** Influence function analysis on bias gradients pre-unlearning
   - **Consequence if violated:** If bias distributed uniformly (>20% in tail), requires more parameters (approaches LoRA 6.25%), efficiency claim weakens

2. **SVD transfer assumption:** SVFit's SVD approach transfers from task adaptation (adding capabilities) to unlearning (removing capabilities).
   - **Evidence:** None directly; ablation study will validate
   - **Testable:** Ablation study comparing SVFit vs. LoRA vs. full-rank unlearning
   - **Consequence if violated:** Falls back to LoRA efficiency (6.25%), loses order-of-magnitude efficiency claim

3. **PEFT-scale cross-bias transfer assumption:** Cross-bias transfer observed at full model scale (Lu et al. 2024) holds at PEFT scale (<0.1% parameters).
   - **Evidence:** Lu et al. 2024 shows transfer at full model scale (3 citations)
   - **Testable:** Measure secondary bias DP reduction after primary-only debiasing
   - **Consequence if violated:** Requires multiple debiasing passes (one per attribute), loses single-pass efficiency multiplier

4. **Gradient approximation assumption:** Gradient-based influence function approximation provides sufficient accuracy for bias-encoding parameter identification without full Hessian.
   - **Evidence:** Standard practice in machine unlearning (Qiao et al. 2025); first-order methods widely used
   - **Testable:** Compare gradient-based vs. Hessian-based influence on small model
   - **Consequence if violated:** Higher computational cost for influence function, but still cheaper than full unlearning

### 1.5 Scope & Boundaries

**Applies to:**
- Pre-trained vision models (CelebA, CUB-200) with protected attribute labels
- Pre-trained language models (LLMs) with identifiable demographic bias in text corpora
- Foundation models (BERT, ViT, GPT-2) where bias is encoded during pre-training
- Group fairness metrics (demographic parity, equalized odds)

**Does NOT apply to:**
- Models without clear protected attributes (e.g., unlabeled datasets)
- Individual fairness requirements (method targets group-level metrics)
- Extremely distributed bias where >80% gradients in tail singular values (concentration assumption fails)
- Models trained from scratch (no pre-existing bias to unlearn; better to use balanced training)
- Privacy-focused unlearning (targets bias, not privacy leakage)

**Known limitations:**
1. Group fairness only - does not address individual fairness or intersectional bias (multiple attributes simultaneously)
2. Cross-bias transfer magnitude varies (not guaranteed 100% transfer to all secondary attributes)
3. Requires influence function computation (one-time cost, scales with model size)
4. SVFit transfer to unlearning unvalidated (ablation study required to confirm)

### 1.6 Testable Predictions

**Primary Prediction:**
**P1 (Demographic Parity Improvement vs. Full Unlearning 94-97% Baseline):**
SVFit-Unlearn will achieve demographic parity improvement ≥90% (within 5% of full-model unlearning baseline 94-97%) using <0.1% trainable parameters, as measured on CelebA (gender/smile bias) and CUB-200 (pose bias) datasets.

*Measurement:*
- Demographic parity: DP = |P(Ŷ=1|A=a) - P(Ŷ=1|A=b)| where A is protected attribute
- Improvement: (DP_before - DP_after) / DP_before × 100%
- Success criteria: DP improvement ≥90% with statistical significance p < 0.05
- Statistical test: Paired t-test with n ≥ 20 runs (same random seeds)

*Basis:*
Aylapuram et al. 2025 shows full-model unlearning achieves 94.86% (CUB-200) and 97.37% (CelebA) demographic parity improvement. SVFit-Unlearn targets ≥90% (retains 95%+ of full-model performance) at 1000× fewer parameters (0.1% vs. 100%).

*Success Criteria for Phase 2B:*
- Primary success: DP improvement ≥90% AND parameter cost <0.1% AND accuracy retention ≥95%
- Falsification trigger: DP improvement <67.5% (75% of 90% target) triggers hypothesis rejection

**Secondary Predictions:**
**P2 (Mechanism Validation - Singular Value Concentration):**
Bias-encoding information will concentrate in top-k singular values (k<500), with >80% of bias gradient magnitude captured in this subspace, as measured by influence function analysis pre-unlearning.

*Measurement:* ∑_{i=1}^k |∇_{σ_i} L_bias| / ∑_{all} |∇_{σ_i} L_bias| ≥ 0.80
*Falsification:* If <60% bias gradient in top-500 values, concentration assumption violated

**P3 (Cross-Bias Transfer at PEFT Scale):**
Single gender-debiasing pass will reduce secondary bias dimensions (race, religion) by ≥50% demographic parity improvement, without direct debiasing on those attributes.

*Measurement:* (DP_race_before - DP_race_after) / DP_race_before ≥ 0.50 after gender-only unlearning
*Falsification:* If <25% secondary reduction, cross-bias transfer at PEFT scale fails

**Falsification Criteria:**
The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure:** Demographic parity improvement <67.5% (= 75% of 90% target), indicating SVFit-Unlearn substantially underperforms full unlearning

2. **Mechanism Failure:** Ablation study shows SVFit ≤ LoRA ≤ full-rank (no SVD advantage) OR bias concentration <60% in top-k values (distributed bias)

3. **Efficiency Failure:** Parameter cost >1% (10× over target) OR accuracy degradation >10% (double acceptable threshold)

4. **Transfer Failure:** Cross-bias transfer <25% secondary reduction (half of 50% target), invalidating single-pass efficiency claim

### 1.7 SOTA Baseline (Optional - If SOTA Comparison Mode)

Not applicable - Absolute performance validation mode (no SOTA comparison). Baseline is full-model bias-aware unlearning (Aylapuram et al. 2025: 94-97% DP improvement).

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Minimum runs: n ≥ 20 (recommended for detecting medium effect sizes)
- Replication: Same random seeds across SVFit/LoRA/full-rank for paired comparisons
- Datasets: CelebA (validation set 19962 images), CUB-200 (validation 2924 images)

**Test Specification:**
- Primary metric: Paired t-test for DP improvement (SVFit vs. full unlearning baseline)
- Significance level: α = 0.05 (one-tailed: SVFit ≥ 90% target)
- Effect size: Cohen's d calculation for DP improvement magnitude
- Report format: Mean ± Std Dev, 95% Confidence Interval, p-value

**Ablation Study Design:**
- 3-way comparison: SVFit (<0.1%) vs. LoRA (6.25%) vs. Full-rank (100%)
- Fixed hyperparameters: Same LR, BS, epochs across conditions
- Metrics: DP improvement, accuracy retention, parameter count, training time
- Success pattern: SVFit ≥ LoRA > Full-rank on DP improvement confirms SVD advantage

---

## 2. Contribution Summary

**Primary Contribution (Methodological):**
SVFit-Unlearn introduces the first application of singular value decomposition (SVD) to machine unlearning for bias mitigation, achieving order-of-magnitude efficiency improvement (<0.1% parameters) compared to existing bias-aware unlearning methods (100% parameters) and parameter-efficient fine-tuning baselines (LoRA 6.25%). The method combines gradient-based influence functions for bias-encoding parameter identification with selective SVD updates, validated through rigorous ablation studies.

**Novelty:** First SVFit application to unlearning domain; empirical validation of cross-bias transfer at ultra-low parameter scale (<0.1%); 100× efficiency milestone vs. full-model unlearning.

**Secondary Contributions:**
- **Theoretical:** Analysis of bias concentration in singular value spectrum, extending SVFit theory from task adaptation to fairness domain; theoretical framework for cross-bias transfer in low-rank subspace
- **Practical:** Enables post-deployment fairness fixes for foundation models without full retraining (100× cost reduction); democratizes bias mitigation for resource-constrained organizations; publishable outcome regardless of ablation results (positive: new efficient method; negative: important null result on SVFit-unlearning transfer limits)

---

## 3. Key Related Work

**Foundation Sources (MUST CITE):**

1. **"Bias-Aware Machine Unlearning: Towards Fairer Vision Models via Controllable Forgetting"** (2025)
   - Authors: Sai Siddhartha Chary Aylapuram, V. Elluru, Shivang Agarwal
   - DOI/URL: https://www.semanticscholar.org/paper/3fd28be149040778a79c86dac43592e8f310b56c
   - Key Finding: Post-hoc bias mitigation achieves 94.86% (CUB-200) and 97.37% (CelebA) demographic parity improvement via selective forgetting with <5% accuracy loss - establishes performance baseline for bias-aware unlearning

2. **"Towards Transfer Unlearning: Empirical Evidence of Cross-Domain Bias Mitigation"** (2024)
   - Authors: Huimin Lu, Masaru Isonuma, Junichiro Mori, Ichiro Sakata
   - DOI/URL: https://www.semanticscholar.org/paper/dccd6c9430e8b5ee0fdbbc6693aa0c481143acf2
   - Citations: 3
   - Key Finding: Cross-domain transfer unlearning - debiasing gender mitigates race/religion bias empirically in LLMs via masked language modeling - provides evidence for single-pass multi-attribute debiasing

3. **"SVFit: Parameter-Efficient Fine-Tuning of Large Pre-Trained Models Using Singular Values"** (2024)
   - Authors: Chengwei Sun, Jiwei Wei, Yujia Wu, et al.
   - DOI/URL: https://www.semanticscholar.org/paper/165e64d57497ed94e433d8b241b9153df01fccf0
   - Citations: 6
   - Key Finding: 16× fewer trainable parameters than LoRA via SVD-initialized PEFT, 99% information in top-r singular values - establishes parameter efficiency method and SVD-based parameter importance theory

4. **"Soft Weighted Machine Unlearning"** (2025)
   - Authors: Qiao et al.
   - Key Finding: Weighted influence functions prevent over-unlearning while identifying critical parameters for selective removal - provides influence function methodology for bias-encoding parameter identification

**Comparison Baselines:**

5. **LoRA (Low-Rank Adaptation)** - Hu et al. 2021
   - 6.25% trainable parameters, standard PEFT baseline
   - Comparison: SVFit targets <0.1% (62× fewer parameters than LoRA)

6. **Full-model Bias-Aware Unlearning** - Aylapuram et al. 2025
   - 100% parameters updated, 94-97% DP improvement
   - Comparison: SVFit-Unlearn targets ≥90% DP improvement at 0.1% parameters (1000× efficiency)

**Gap Evidence:**

7. **VectorInstitute/bias-mitigation-unlearning** (GitHub)
   - Implementation patterns for LLM bias unlearning
   - Gap: No parameter-efficient variants (<1% parameters)

8. **Archon KB Search Results** (No direct matches)
   - Queries for "SVD singular value unlearning bias fairness" returned no relevant cases
   - Gap confirmation: Novel application area with limited past implementation precedent

---

## 4. Phase 2B Readiness

### Decomposition Preview

**Total Sub-Hypotheses:** 2 + 3 = 5 (SH1 + SH2.1-2.3 + SH3)

**SH1 (Existence - Foundation):**
"Does SVFit-based unlearning achieve ≥90% demographic parity improvement at <0.1% parameter cost on CelebA and CUB-200 datasets?"
- Maps to: Primary prediction (P1)
- Verification type: Empirical validation via controlled experiments
- Critical: MUST PASS for Phase 2B to proceed - establishes basic feasibility

**SH2 (Mechanism - Core) - 3 Sub-Hypotheses:**
"Is the proposed 3-step causal mechanism (SVD+influence → selective updates → cross-bias transfer) the actual cause of efficiency and fairness improvement?"
- **SH2.1 (Mechanism Step 1):** Does SVD + influence function correctly identify bias-encoding singular values (>80% bias gradient in top-k)?
- **SH2.2 (Mechanism Step 2):** Does selective gradient descent on top-k singular values achieve bias removal at <0.1% cost with <5% accuracy loss?
- **SH2.3 (Mechanism Step 3):** Does single-attribute debiasing cause ≥50% cross-bias transfer to secondary attributes?
- Verification type: Causal analysis via ablation studies + mechanistic probes
- Critical: Determines explanatory power - understanding WHY method works (or fails)

**SH3 (Comparison - Validation):**
"Does SVFit-Unlearn outperform LoRA unlearning (6.25% parameters) and approach full-model unlearning (94-97% DP) in the ablation study?"
- Maps to: Secondary predictions + ablation study
- Verification type: Comparative empirical (3-way: SVFit vs. LoRA vs. Full-rank)
- Critical: Determines practical value - validates SVD advantage vs. established PEFT methods

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned (H-SVFitUnlearn-v1)
- [x] Confidence level specified (0.80)
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (3 steps, evidence_for_links table)
- [x] Causal chain length (N=3) determined and documented
- [x] Key tension identified (SVFit task adaptation vs. unlearning) and resolution proposed (ablation study)
- [x] Key assumptions list consequences if violated (4 assumptions with testable criteria)
- [x] At least 2 testable predictions exist (P1 primary, P2-P3 secondary)
- [x] Falsification criteria are defined (4 failure modes)
- [x] Baselines are identified for comparison (LoRA 6.25%, Full-model 94-97%)
- [x] SH1, SH2 (3 sub-hypotheses), SH3 are clear starting points

### Open Questions

1. **For Phase 2B Decomposition:**
   - What is the optimal k value for bias-encoding singular values? (Grid search {10, 50, 100, 500})
   - How does cross-bias transfer magnitude vary across model architectures (BERT vs. ViT vs. GPT-2)?
   - What is the computational cost of influence function analysis relative to unlearning cost?

2. **For Phase 2C Experiment Design:**
   - Which datasets/tasks provide strongest cross-bias transfer signal for validation?
   - What is the minimal sample size (n) to detect SVFit vs. LoRA difference at α=0.05, power=0.8?
   - Should ablation study include intermediate parameter counts (e.g., 0.5%, 1%, 3%) to map efficiency-performance tradeoff?

3. **For Phase 3 Implementation:**
   - Are SVFit code (Sun et al. 2024 GitHub) and bias-aware unlearning implementations (Aylapuram et al.) compatible for integration?
   - What is the scalability limit of influence function approximation (model size, dataset size)?

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-06*
