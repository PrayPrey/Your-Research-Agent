# 3. Methodology

Building on the insight that minority samples produce persistently elevated prediction residuals during ERM training, we design GNR-LLR around a computationally efficient gradient-domain minority proxy signal that requires no group annotations and imposes negligible overhead on standard training.

## 3.1 Normalized Per-Sample Last-Layer Gradient Norm

### The Signal

For a model with a fully connected last layer W ∈ ℝ^(C×d) (C classes, d feature dimension), the per-sample gradient with respect to the CE loss satisfies:

∇_W ℓᵢ = (pᵢ − yᵢ_onehot) ⊗ h(xᵢ)

where pᵢ = softmax(W·h(xᵢ)) are the predicted probabilities, yᵢ_onehot is the one-hot label, and h(xᵢ) ∈ ℝ^d is the feature vector (FC input). This outer-product decomposition is exact for CE loss [Kirichenko et al., 2022].

The Frobenius norm of this gradient is:

‖∇_W ℓᵢ‖_F = ‖pᵢ − yᵢ_onehot‖ · ‖h(xᵢ)‖

We define the normalized per-sample gradient norm (our minority proxy signal) as:

g̃ᵢ = ‖∇_W ℓᵢ‖_F / ‖h(xᵢ)‖ = ‖pᵢ − yᵢ_onehot‖

**Rationale:** This decomposition separates two components: (1) the prediction-error residual ‖pᵢ − yᵢ‖, which measures how far the model's prediction deviates from the true label for sample i, and (2) the feature norm ‖h(xᵢ)‖, which reflects the sample's position in feature space. For architectures with BatchNorm layers (such as ResNet-50), feature norms are approximately equalized across samples by the BatchNorm normalization. Normalizing by ‖h(xᵢ)‖ removes this feature-scale factor, isolating the prediction-error component as the informative signal for minority identification.

### Why This Signal Identifies Minority Samples

During early ERM training on spuriously correlated data, majority-group samples can exploit the spurious feature (e.g., background context) to produce low prediction residuals — the model quickly fits them via the shortcut. Minority-group samples that do not carry the spurious feature, or carry it in the "wrong" configuration, cannot be fit by the shortcut solution. Their prediction residuals remain elevated throughout early training, directly producing elevated g̃ᵢ values.

This mechanism predicts that:
- Majority samples → g̃ᵢ → 0 as the spurious shortcut is acquired
- Minority samples → g̃ᵢ remains elevated (persistently high prediction residuals)
- The ratio of minority to majority g̃ grows as the shortcut acquisition progresses

This is consistent with NHT framework [Khanh & Hoa, 2026] predictions for minority-group gradient dynamics during ERM training.

## 3.2 Efficient Computation via FC Forward Hook

The outer-product decomposition enables computing all N per-sample normalized gradient norms in a single forward pass, with no additional backward passes:

```
Algorithm 1: Efficient g̃ Computation (GradientNormAnalyzer)

Input: trained model f, dataloader D (eval mode), epoch T_id
Output: {g̃ᵢ}_{i=1}^N for all training samples

1. Register forward hook on model.fc:
   hook: (module, input, output) → save input[0] as h(x_i) buffer
2. Set model to eval() mode (no BatchNorm updates)
3. For each batch (x_b, y_b) in D:
   a. Forward pass: logits = f(x_b)  [hook captures h(x_b) ∈ ℝ^(B×d)]
   b. p_b = softmax(logits)
   c. residual_b = p_b − one_hot(y_b)    [prediction-error residual]
   d. g_tilde_b = ||residual_b||_2       [row-wise norm over C classes]
   e. Save g_tilde_b to CPU buffer
4. Return g_tilde = concat(all batches)  [N floats]
```

**Rationale:** The forward hook on `model.fc` captures the FC input (feature vector h(xᵢ)) during the forward pass, making the feature norm computation free. The prediction residual is computed directly from the softmax output and one-hot labels — no backward pass required. The entire computation adds a single forward pass over the training set (identical cost to inference on the training set), with negligible memory overhead via CPU storage for the gradient norm buffer.

**Complexity:** O(N·d) storage for feature vectors during a single forward pass; O(N) storage for g̃. GPU memory overhead: one batch at a time (feature vectors discarded after each batch).

### Feature Norm Equalization Condition

The interpretability of g̃ as a prediction-residual signal depends on the feature norms being approximately equalized across groups. For ResNet-50, BatchNorm layers normalize the feature representation at each residual block, producing approximately uniform ‖h(xᵢ)‖ distributions across groups. We verify this condition empirically in Section 5.

If feature norms are not equalized (e.g., architectures without BatchNorm), the raw gradient norm ‖∇_W ℓᵢ‖ would conflate prediction-error and feature-scale information, and normalization by ‖h(xᵢ)‖ would be required as an explicit per-sample normalization step (still efficient, just applied explicitly rather than implicitly through the outer-product decomposition).

## 3.3 Pseudo-Minority Subset Construction

After computing g̃ᵢ for all training samples at epoch T_id, we construct a pseudo-minority subset for Stage 2 retraining:

```
Top-k% selection:  S_min = {i : g̃ᵢ ≥ quantile(g̃, 1-k)}
Bottom-k% selection: S_maj = {i : g̃ᵢ ≤ quantile(g̃, k)}
Pseudo-balanced subset: S = S_min ∪ S_maj
```

**Rationale:** High-g̃ samples are the pseudo-minority (minority-enriched by the AUC=0.914 discrimination capability of g̃). Low-g̃ samples are the pseudo-majority (majority-dominant). Combining top-k% and bottom-k% produces a balanced retraining set with equal pseudo-minority and pseudo-majority representation — analogous to the group-balanced validation subset used in DFR, but constructed without group labels.

**Hyperparameters:** k=25% (top and bottom quartile), T_id=5 (primary identification epoch). The ratio signal is robust across T_id ∈ {1,3,5,10} (see Section 5.3), so T_id selection is not sensitive.

## 3.4 Stage 2: Last-Layer Retraining (GNR-LLR Full Pipeline)

The complete GNR-LLR pipeline follows the DFR principle [Kirichenko et al., 2022]:

```
Stage 1: Standard ERM training for T_id epochs
         → Collect g̃ᵢ for all training samples
         → Construct pseudo-balanced subset S

Stage 2: Freeze feature extractor (all layers except model.fc)
         Retrain model.fc on S using SGD (lr=0.01, 100 epochs)
         → Evaluate WGA on test set
```

**Rationale:** DFR [Kirichenko et al., 2022] establishes that ERM features already encode the non-spurious information needed for good WGA — the spurious correlation problem is in the classifier head's over-reliance on spurious features. Retraining only the last layer on a minority-enriched subset reorients the classifier toward core features without destroying the rich feature representation learned by the backbone. The computational cost is minimal (only 1 linear layer retrained) and the feature extractor training is identical to standard ERM.

**Note on Scope:** In this paper, we focus on validating the proxy signal quality (Stage 1 output: g̃ AUC and ratio). The Stage 2 retraining experiments (measuring WGA on Waterbirds) are identified as the direct next step; the proxy signal quality demonstrated here provides the foundation for the complete pipeline.

## 3.5 Theoretical Connection to NHT Framework

The NHT framework [Khanh & Hoa, 2026] predicts that during ERM training on spuriously correlated data, minority samples resist the shortcut attractor basin M_sc throughout the early training phase. Their gradient norms reflect this resistance: unlike majority samples that are pulled toward the shortcut basin and achieve low prediction residuals early, minority samples maintain high prediction residuals reflecting their structured-feature learning path.

Our g̃ signal directly captures this theoretical prediction: g̃ᵢ = ‖pᵢ − yᵢ‖ is precisely the prediction-residual that NHT predicts will remain elevated for minority samples. The 8.8x ratio at epoch 5 and 8.5x at epoch 10 (no collapse) provides empirical evidence consistent with NHT's temporal persistence prediction, though we note that T_peak_sc was not directly measured in this study.

Figure 5 illustrates the feature norm equalization by BatchNorm, confirming the key architectural condition that makes g̃ a mechanistically valid proxy signal.
