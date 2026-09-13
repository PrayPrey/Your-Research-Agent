# Methodology

If spurious features are simpler and converge earlier due to gradient descent's implicit bias, then ablation training—isolating spurious-only and core-only feature types—should reveal measurable temporal separation via per-epoch gradient norm tracking. Our methodology tests this by training three network variants (spurious-only, core-only, baseline) on CMNIST benchmark, measuring convergence epoch $E$ for each variant, and computing temporal gap $\Delta = E_{\text{core}} - E_{\text{spurious}}$. We predict $\Delta \geq 2$ epochs.

## Ablation Training

**Rationale:** Direct gradient convergence measurement requires isolating feature types without attribution ambiguity. GradCAM or Integrated Gradients provide spatial attribution but introduce methodological complexity (which pixels correspond to "spurious" vs "core"?) and fail on global corruptions like CMNIST color (applied uniformly across the entire image, not spatially localized). Ablation training sidesteps attribution entirely: we modify inputs to remove one feature type, then measure convergence on the ablated variant.

**CMNIST spurious-only variant:** Apply Gaussian blur ($\sigma=3$) to grayscale MNIST digits, removing shape edges while preserving smooth color gradients. The network trained on blurred inputs cannot use digit shape (destroyed by blur) and must rely on color bias (digit 0 → red with 75% probability, digit 1 → green with 75% probability). Convergence epoch $E_{\text{spurious}}$ measures when color-based gradients stabilize.

**CMNIST core-only variant:** Convert colored MNIST to grayscale, removing color information entirely. The network must use digit shape (edges, stroke patterns) to classify. Convergence epoch $E_{\text{core}}$ measures when shape-based gradients stabilize.

**Baseline variant:** Standard CMNIST training with both color and shape available. Convergence epoch $E_{\text{baseline}}$ lies between $E_{\text{spurious}}$ and $E_{\text{core}}$, as the network exploits both feature types (biased toward earlier-converging spurious features).

**Architecture:** ResNet-18 pretrained on ImageNet, final FC layer replaced with binary classification head (10 classes for CMNIST digits). Standard SGD optimizer with momentum 0.9, learning rate 0.01, batch size 256. Training proceeds for 30 epochs to ensure post-convergence observation window.

**Alternatives considered:** GradCAM spatial masking (tested in h-e3, failed due to global color corruption—center/outer spatial regions don't separate color from shape on CMNIST). Integrated Gradients (computationally expensive, $\sim 10\times$ slower than ablation training, requires attribution baselines). Ablation training is simpler, faster, and avoids spatial attribution assumptions.

## Convergence Criterion

**Definition:** Convergence epoch $E$ is the first epoch where gradient norm $||\nabla_\theta \mathcal{L}||_2$ drops below 10% of peak gradient norm and remains below threshold for 3 consecutive epochs.

**Rationale:** Threshold-based criterion is robust to transient gradient spikes (single-epoch dips followed by recovery), while 3-epoch window ensures stable convergence rather than momentary plateau. The 10% threshold balances sensitivity (too high → premature convergence declaration when gradients still evolving) and specificity (too low → never converges, gradient noise dominates).

**Implementation:**
```python
def compute_gradient_norm(model):
    total_norm = 0.0
    for p in model.parameters():
        if p.grad is not None:
            total_norm += p.grad.data.norm(2).item() ** 2
    return total_norm ** 0.5

def check_convergence(grad_norms, current_epoch, peak_norm):
    threshold = 0.1 * peak_norm
    if current_epoch < 3:
        return False
    recent_norms = grad_norms[current_epoch-2:current_epoch+1]
    return all(g < threshold for g in recent_norms)
```

Gradient norm is computed after each mini-batch gradient update, then averaged over the epoch. Peak norm is tracked across all epochs seen so far (updated incrementally).

**Alternatives considered:** Accuracy-based convergence (used in h-m2, failed—70% threshold achieved in 1-2 epochs for both ResNet and ViT, providing no temporal window). Loss plateau detection (sensitive to learning rate schedule artifacts, cosine annealing causes oscillating loss even when model has converged). Gradient norm convergence directly measures optimization progress independent of threshold choice, making it more robust.

## Layer-Wise Neuron Correlation

**Rationale:** If temporal gap arises from feature complexity hierarchy (simpler spurious features in early layers, complex core features in late layers), then early layers should exhibit higher neuron-spurious correlation than late layers. This validates the mechanism: temporal ordering is not just a dataset artifact but reflects architectural processing hierarchy.

**Neuron-spurious correlation $\rho_j$:** For each neuron $j$ in the network, compute Pearson correlation between neuron activation magnitudes (averaged over spatial dimensions for conv layers, scalar for FC layers) and spurious feature presence (1 if spurious-only input, 0 if core-only input):

$$\rho_j = \text{corr}(|a_j(x)|, \mathbb{1}[\text{spurious}])$$

where $a_j(x)$ is neuron $j$'s activation on input $x$, $\mathbb{1}[\text{spurious}] = 1$ for spurious-only variant images, $0$ for core-only variant images. High $|\rho_j|$ indicates neuron strongly responds to spurious features.

**Layer-wise aggregation:** Group neurons by layer (conv1, layer1, layer2, layer3, layer4 for ResNet-18), compute mean $|\rho_j|$ per layer. Statistical test: independent samples t-test comparing early layers (conv1, layer1) vs late layers (layer3, layer4). Hypothesis: $\bar{\rho}_{\text{early}} > \bar{\rho}_{\text{late}}$.

**Implementation:** After training spurious-only and core-only variants to convergence, pass both variant datasets through the trained baseline network, extract activations at each layer, compute per-neuron correlation, aggregate by layer. This requires storing activations for ~60,000 CMNIST training images × 2 variants × 5 layers—manageable with gradient checkpointing or sequential processing.

**Alternatives considered:** Gradient magnitude per layer (confounded by layer depth and parameter count—deeper layers naturally have smaller gradients due to vanishing gradient, doesn't isolate spurious vs core distinction). Activation similarity analysis (requires defining reference "spurious" and "core" activation patterns, introduces circular reasoning—we'd need to know which neurons are spurious-correlated before measuring spurious correlation).

## Forgetting Rate Analysis

**Rationale:** If spurious features converge to simpler, more stable decision boundaries, spurious-trained networks should exhibit lower prediction forgetting (fewer flip-flops between correct and incorrect predictions across epochs) than core-trained networks.

**Forgetting metric (Toneva et al., 2019):** For each training example $x_i$, track prediction correctness $c_i^{(t)} \in \{0, 1\}$ at each epoch $t$. A *forgetting event* occurs when $c_i^{(t)} = 1$ (correct) and $c_i^{(t+1)} = 0$ (incorrect). Forgetting rate $F = \frac{1}{N} \sum_{i=1}^N f_i$, where $f_i$ is the number of forgetting events for example $i$ across all epochs.

**Feature-level adaptation:** Compute $F_{\text{spurious}}$ on spurious-only training (network predicts using color), $F_{\text{core}}$ on core-only training (network predicts using shape). Hypothesis: $F_{\text{spurious}} < F_{\text{core}}$ (spurious features more stable).

**Implementation:**
```python
def track_forgetting(model, dataloader, num_epochs):
    N = len(dataloader.dataset)
    correctness = np.zeros((N, num_epochs), dtype=bool)
    
    for epoch in range(num_epochs):
        for batch_idx, (inputs, targets) in enumerate(dataloader):
            outputs = model(inputs)
            predictions = outputs.argmax(dim=1)
            correct = (predictions == targets).cpu().numpy()
            start_idx = batch_idx * dataloader.batch_size
            correctness[start_idx:start_idx+len(correct), epoch] = correct
    
    forgetting_events = np.zeros(N)
    for i in range(N):
        for t in range(num_epochs - 1):
            if correctness[i, t] and not correctness[i, t+1]:
                forgetting_events[i] += 1
    
    return forgetting_events.mean()
```

Statistical test: paired t-test on $(F_{\text{spurious}}, F_{\text{core}})$ across 10 random seeds. Success criterion: $p < 0.05$ and $F_{\text{spurious}} < F_{\text{core}}$.

## Experimental Protocol Summary

| Component | Spurious-Only | Core-Only | Baseline |
|-----------|---------------|-----------|----------|
| **Input** | Blurred color digits | Grayscale sharp digits | Color sharp digits |
| **Feature Isolated** | Color bias | Shape edges | Both |
| **Expected $E$** | Early ($E_s \approx 10-15$) | Late ($E_c \approx 15-20$) | Intermediate |
| **Hypothesis Test** | $E_c - E_s \geq 2$ epochs? | Paired t-test across 10 seeds | $p < 0.05$ |

**Multi-dataset extension:** The ablation methodology is dataset-agnostic. For Waterbirds, spurious-only variant uses background-only images (segment bird, fill with background), core-only variant uses bird-only images (mask background, uniform gray). For CelebA, spurious-only variant shows gender-correlated features (face masked to remove target attribute), core-only variant shows target attribute with gender information removed (gender-balanced sampling or attribute-specific cropping). For NICO++, spurious-only variant shows context-only (object masked), core-only variant shows object-only (context masked). Implementation requires dataset-specific masking strategies, but convergence measurement protocol (gradient norm < 10% peak for 3 epochs) remains identical.

**Computational cost:** CMNIST PoC requires 3 variants × 30 epochs × 10 seeds = 900 training runs at ~2 minutes each (ResNet-18 on single GPU) = ~30 hours total. Parallelizable across seeds (10 GPUs → 3 hours wall-clock). Multi-dataset validation (Waterbirds/CelebA/NICO++) adds 3 datasets × 3 variants × 30 epochs × 10 seeds with ResNet-50 (~10 minutes per run) = ~150 hours compute, parallelizable to ~15 hours wall-clock with 10 GPUs.

## Reproducibility

All experiments use PyTorch 1.12, CUDA 11.6, and publicly available datasets (CMNIST via torchvision MNIST + color corruption script, Waterbirds via WILDS library, CelebA via torchvision, NICO++ via official repository). Code will be released at [ANONYMOUS REPOSITORY] upon publication. Hyperparameters: SGD optimizer with momentum 0.9, learning rate 0.01 (no decay for PoC, cosine annealing for multi-dataset validation), weight decay $10^{-4}$, batch size 256, ImageNet pretrained initialization for ResNet-18/50. Random seeds: 0-9 for statistical validation. Hardware: NVIDIA A100 40GB GPUs.
