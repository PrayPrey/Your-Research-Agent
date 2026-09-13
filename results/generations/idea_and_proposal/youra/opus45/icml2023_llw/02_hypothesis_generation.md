# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-LPFF-v1
**Confidence Level:** 0.85

**Main Hypothesis:**
Under the condition of standard Forward-Forward training on image classification tasks, if we add learnable sparse lateral connections that implement local predictive coding within each layer, then classification accuracy will improve by 3-5% over baseline FF because within-layer feature coordination through prediction errors reduces redundant feature learning and encourages complementary representations.

**Alternative Hypothesis (H0):**
Adding lateral predictive connections to Forward-Forward layers does not improve classification accuracy, either because (a) within-layer coordination is not a bottleneck in current FF performance, (b) prediction errors do not provide useful learning signals in this context, or (c) the computational overhead negates any representational benefits.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Lateral topology (M) | Independent | Learnable sparse mask initialized as k-NN (k=8-16), learned via gradient descent | Sparsity: 1-5% of full connectivity |
| Lateral weight (λ) | Independent | Adaptive λ_l = λ_0 / l for layer l | λ_0 ∈ [0.1, 1.0] |
| Neighborhood size (k) | Independent | Number of neurons each neuron predicts | k ∈ {4, 8, 16, 32} |
| Prediction normalization | Independent | LayerNorm applied to prediction targets | On/Off ablation |
| Classification accuracy | Dependent | Top-1 accuracy on test set, averaged over 5 runs | CIFAR-10: 85-92%, CIFAR-100: 55-65% |
| Feature coordination | Dependent | Mutual information between neighboring neuron activations | Increase expected vs baseline |
| Training convergence | Dependent | Epochs to reach 90% of final accuracy | Similar or faster than baseline |
| Network architecture | Controlled | Same as baseline FF experiments | 4-layer MLP or CNN variants |
| Training hyperparameters | Controlled | LR, batch size, epochs matched to baseline | Per published FF configurations |
| Dataset splits | Controlled | Standard train/test splits | CIFAR-10/100 standard |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
Step 1: Lateral Predictions → Prediction Errors
    ↓
Step 2: Prediction Errors → Weight Updates (Coordination)
    ↓
Step 3: Coordinated Representations → Improved Classification
    ↓
[OUTCOME: Higher accuracy than baseline FF]
```

**Step 1: Lateral Predictions → Prediction Errors**
- Each neuron i predicts activations of its k-nearest neighbors j ∈ N(i)
- Prediction: pred_ij = W_lat[i,j] · a_i (linear prediction from neuron i to j)
- Prediction error: L_lateral = Σ MSE(pred_ij, LayerNorm(a_j))
- Symmetric: Both i→j and j→i predictions computed

**Step 2: Prediction Errors → Weight Updates**
- Prediction errors provide local gradient signal for lateral weights
- Combined loss: L_total = L_goodness + λ_l · L_lateral
- Adaptive λ_l = λ_0 / l decreases lateral importance in deeper layers
- Weight updates encourage neurons to develop mutually predictable (coordinated) activations

**Step 3: Coordinated Representations → Improved Classification**
- Coordinated features reduce redundancy (neurons specialize for different aspects)
- Complementary feature learning improves discriminability
- Classification performance increases due to richer feature space

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | PC-SNN (Lan 2022), PCL (2025) | Prediction errors are effective local learning signals in SNNs and ANNs | Strong |
| Step2 → Step3 | Layer Collaboration (Lorberbom 2023) | Inter-layer coordination improves FF by 2-4%; intra-layer may add further | Medium |
| Step3 → Outcome | Park 2025 (Lateral CNN) | Lateral connections in CNNs improve classification accuracy | Strong |
| Cross-domain | George 2025 (Cortical Microcircuits) | Biological lateral connections serve coordination/prediction functions | Strong |

**Key Tension:**
- **Tension:** Layer Collaboration (Lorberbom 2023) focuses on VERTICAL (inter-layer) coordination, while LP-FF proposes HORIZONTAL (intra-layer) coordination. It's unclear if these are redundant or complementary.
- **Resolution:** Our verification plan tests LP-FF alone, then LP-FF + Layer Collaboration combined, to determine if effects are additive or overlapping.

### 1.4 Key Assumptions

1. **Within-layer coordination is a bottleneck in current FF**
   - Evidence: Layer Collaboration paper shows inter-layer coordination improves FF, suggesting coordination mechanisms are beneficial
   - Consequence if violated: LP-FF will show no improvement over baseline FF; pivot to other FF improvement directions

2. **Prediction error is an effective local learning signal**
   - Evidence: Predictive Coding literature (PC-SNN, PCL, cortical microcircuits) validates prediction error as learning signal
   - Consequence if violated: Lateral weights will not converge to useful patterns; need alternative coordination objective

3. **Sparse lateral connectivity (k << n) is sufficient**
   - Evidence: Visual cortex lateral connections are sparse; Park 2025 uses limited recurrent connections
   - Consequence if violated: Need denser connectivity, increasing computational overhead significantly

4. **Symmetric prediction improves coordination over one-directional**
   - Evidence: Theoretical argument (bidirectional ensures mutual influence); no direct empirical evidence yet
   - Consequence if violated: Can simplify to one-directional prediction, reducing computation by 50%

### 1.5 Scope & Boundaries

**Where hypothesis applies:**
- Forward-Forward based local learning algorithms
- Image classification tasks (MNIST, CIFAR-10, CIFAR-100, potentially ImageNet)
- Fully-connected and convolutional architectures
- Standard supervised learning settings

**Where it does NOT apply:**
- Recurrent networks / sequence models (different coordination dynamics)
- Unsupervised/self-supervised FF variants (different objective structure)
- Non-image modalities without clear spatial/feature neighborhoods
- Extremely deep networks (>50 layers) where lateral overhead may dominate

**Known limitations:**
- Performance improvement magnitude is uncertain until empirical validation
- Computational overhead of O(k·n) per layer may offset gains for large k
- Hyperparameter sensitivity (λ, k) requires careful tuning
- Convolutional layer neighborhood definition needs specification (spatial vs. channel neighbors)

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Classification Accuracy Improvement)**:
LP-FF will achieve classification accuracy > baseline FF + 3% on CIFAR-10

*Measurement*:
- Top-1 accuracy > 88% (vs. baseline FF ~85%) with p < 0.05
- Statistical test: Paired t-test, n ≥ 20 runs with matched random seeds

*Basis*:
- Baseline FF achieves ~85% on CIFAR-10 (Hinton 2022)
- DeeperForward (2025) achieves improvements with layer normalization
- Layer Collaboration achieves 2-4% improvement; LP-FF targets similar or additive gains

*Success Criteria for Phase 2B*:
- Primary: Accuracy > 88% (p < 0.05)
- Falsification: Accuracy ≤ 83% triggers hypothesis rejection

**Secondary Predictions:**

**P2 (Mechanism Validation - Feature Coordination)**:
If lateral prediction improves coordination, then mutual information between neighboring neuron activations will increase compared to baseline FF.

*Measurement*: Post-training MI analysis on layer activations
*Expected*: MI increase of 10-30% vs. baseline

**P3 (Complementarity with Layer Collaboration)**:
If LP-FF (horizontal) and Layer Collaboration (vertical) address orthogonal coordination dimensions, then combining them will achieve accuracy > each alone.

*Measurement*: LP-FF + LayerCollab accuracy > max(LP-FF, LayerCollab)
*Expected*: Additive improvement of 1-2%

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure**: Classification accuracy ≤ 83% on CIFAR-10
   (= baseline FF - 2%, statistically worse than current)

2. **Mechanism Failure**: No increase in feature coordination metrics despite accuracy change
   (Would indicate improvement from other factors, not proposed mechanism)

3. **Efficiency Failure**: Computational overhead > 50% with < 2% accuracy gain
   (Cost-benefit ratio unacceptable for practical use)

### 1.7 SOTA Baseline (Optional - If SOTA Comparison Mode)

*Not applicable - Absolute performance validation mode selected.*

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Effect size (Cohen's d): ~0.7 (medium-large, based on 3% improvement / ~4% std dev)
- Required runs: n ≥ 20
- Statistical power: 0.8

**Test Specification:**
- Method: Paired t-test (same random seeds between LP-FF and baseline)
- Significance level: α = 0.05 (one-tailed, testing improvement)
- Report format: Mean difference, 95% CI, Cohen's d, p-value

**Ablation Design:**
- A1: LP-FF full (learnable mask, adaptive λ, symmetric prediction, LayerNorm)
- A2: Fixed k-NN mask (no learning)
- A3: Fixed λ (no adaptive scheduling)
- A4: One-directional prediction only
- A5: No LayerNorm on targets

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does lateral prediction produce meaningful prediction errors in FF layers, and do these errors decrease during training?"
- Maps to: Primary prediction (P1)
- Verification: Monitor L_lateral loss curve during training
- Critical: MUST PASS for mechanism to be valid

**SH2 (Mechanism):**
"Does the proposed 3-step causal mechanism (predictions → errors → coordination → accuracy) operate as hypothesized?"
- Maps to: Causal mechanism chain (N=3 steps)
- Phase 2B will decompose into 3 sub-hypotheses:
  - H-M1: Lateral predictions generate non-trivial prediction errors
  - H-M2: Prediction errors drive lateral weight updates toward coordination
  - H-M3: Coordination improves classification accuracy
- Verification: Ablation studies + MI analysis

**SH3 (Comparison):**
"Does LP-FF outperform baseline FF and complement Layer Collaboration?"
- Maps to: Secondary predictions (P2, P3)
- Verification: Comparative experiments
- Critical: Determines practical value

**Total sub-hypotheses in Phase 2B:** 2 + 3 = 5 (SH1, H-M1, H-M2, H-M3, SH3)

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-LPFF-v1
- [x] Confidence level specified: 0.85
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=3 steps, evidence_for_links table)
- [x] Causal chain length (N=3) determined and stored
- [x] Key tension identified (horizontal vs. vertical coordination) and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist (P1 primary, P2/P3 secondary)
- [x] Falsification criteria defined (accuracy ≤ 83%, no MI increase, overhead > 50%)
- [x] Baselines identified: FF baseline, Layer Collaboration, DeeperForward
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Convolutional layer neighborhood definition:**
   - Should neighbors be defined by spatial proximity (3x3 receptive field) or channel proximity?
   - Need ablation to determine optimal neighborhood structure for CNNs

2. **Computational overhead bounds:**
   - What is the maximum acceptable overhead (%) for practical deployment?
   - Need profiling on target hardware (GPU, edge devices)

3. **Priority verification order:**
   - Recommend: SH1 first (existence) → H-M1/H-M2/H-M3 (mechanism) → SH3 (comparison)
   - SH1 failure terminates early; mechanism tests inform interpretation

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
