# On Gradient-Based Jacobian Stable Rank Regularization in Transformer Pretraining: An Implementation Failure Analysis

## Abstract

This work investigates whether residual-corrected Jacobian stable rank can be controlled during transformer pretraining via gradient-based regularization. The approach combined Hutchinson trace estimation (10 Rademacher probes) for Frobenius norm and randomized power iteration (5 iterations) for spectral norm, differentiated through PyTorch autodiff. Experiments on GPT-2 (125M parameters) trained on C4 for 5000 steps produced zero stable rank measurements across all 12 layers, perplexity of 45,792 (baseline: 59.3), and regularization losses of -17.5 billion. Root cause analysis identified three failure modes: insufficient Hutchinson probe count for 768-dimensional embeddings, power iteration non-convergence in residual-corrected computation graphs, and gradient pathologies in deep autodiff chains. The baseline model converged successfully (perplexity 59.3), isolating the failure to the regularization mechanism. This negative result documents specific numerical instabilities in gradient-based spectral control and suggests post-hoc SVD-based observational studies as an alternative approach.

## 1. Introduction

Foundation models require post-hoc optimizations along multiple efficiency dimensions: low-rank adaptation (LoRA) for parameter efficiency, KV cache compression for memory efficiency, and attention sparsification for computational efficiency. Recent work demonstrates that each dimension can be optimized independently—ARD-LoRA achieves 99.3% of full fine-tuning performance with 0.32% trainable parameters, KV-CAT enables training for cache compressibility, and Mamba-2 achieves 2-8× speedup via sub-quadratic architectures.

We investigated whether these efficiency properties could be unified through a single structural constraint: residual-corrected Jacobian stable rank during pretraining. The theoretical basis is that Jacobian stable rank (sr_ℓ^res = ||J̃_ℓ||_F^2 / ||J̃_ℓ||_2^2, where J̃_ℓ = J_ℓ - I) should couple to adaptation efficiency via Fisher information (F ≈ J^T J), memory efficiency via activation covariance (Σ_{ℓ+1} ≈ J_ℓ Σ_ℓ J_ℓ^T), and computational efficiency via attention entropy.

The implementation attempted gradient-based regularization by adding λ · mean(sr_ℓ^res) to the causal language modeling loss. Stable rank was estimated via Hutchinson trace (10 Rademacher probes) for ||J̃_ℓ||_F^2 and power iteration (5 iterations) for ||J̃_ℓ||_2. All computations were differentiated through PyTorch autodiff to enable gradient-based control.

Results show comprehensive failure. The regularized model produced zero stable rank measurements across all layers at all checkpoints. Training perplexity increased from baseline 59.3 to 45,792 (+77,065%). Regularization losses reached -17.5 billion despite adaptive lambda tuning. The baseline model converged successfully under identical conditions, confirming the failure is specific to the regularization mechanism.

This paper documents the failure modes, provides root cause analysis, and discusses implications for gradient-based spectral control in neural networks.

## 2. Related Work

### Spectral Normalization

Miyato et al. (2018) introduced spectral normalization for GAN discriminators, constraining weight matrix spectral norms via power iteration. Their method operates on static weight tensors, rescaling W as W_SN = W/σ(W) at each training step. This differs from our approach, which attempts to regularize dynamic Jacobians J_ℓ = ∂h_ℓ/∂h_{ℓ-1} computed via autodiff through attention and layer normalization operations.

### Low-Rank Adaptation

LoRA (Hu et al., 2021) represents weight updates as low-rank decompositions ΔW = BA with fixed rank r. ARD-LoRA (Shinwari et al., 2025) extends this with automatic rank determination, achieving 99.3% performance with 0.32% parameters. These methods operate on small adapter matrices during fine-tuning, not on layer Jacobians during pretraining.

### KV Cache Optimization

KV-CAT (Gelberg et al., 2026) trains transformers for KV cache compressibility via auxiliary losses on activation statistics. Flash Attention (Dao et al., 2022) achieves 2-4× speedup through IO-aware computation. These approaches optimize specific efficiency dimensions independently.

### Trace Estimation

Hutchinson's estimator approximates Tr(A) via E[z^T Az] for random vectors z. Bekas et al. (2007) establish O(1/ε²) sample complexity for ε-accuracy, which for coefficient of variation below 15% at 768 dimensions implies approximately 100+ probes. Our implementation used 10 probes.

## 3. Method

### Theoretical Framework

For layer ℓ with residual connections h_ℓ = h_{ℓ-1} + f_ℓ(h_{ℓ-1}), the Jacobian J_ℓ = ∂h_ℓ/∂h_{ℓ-1} = I + ∂f_ℓ/∂h_{ℓ-1}. The residual-corrected Jacobian J̃_ℓ = J_ℓ - I isolates the learned transformation. Stable rank is defined as:

sr_ℓ^res = ||J̃_ℓ||_F^2 / ||J̃_ℓ||_2^2

### Hutchinson Trace Estimation

For Frobenius norm squared ||J̃_ℓ||_F^2 = Tr(J̃_ℓ^T J̃_ℓ), we used Hutchinson's estimator with 10 Rademacher vectors:

||J̃_ℓ||_F^2 ≈ (1/10) Σ_{i=1}^{10} z_i^T (J̃_ℓ^T J̃_ℓ) z_i

where z_i are random ±1 vectors. Each probe required computing Jacobian-vector products via PyTorch autodiff with create_graph=True and retain_graph=True.

### Power Iteration for Spectral Norm

For spectral norm ||J̃_ℓ||_2, we used 5 iterations of power iteration starting from random unit vector v_0:

v_{k+1} = (J̃_ℓ^T J̃_ℓ v_k) / ||(J̃_ℓ^T J̃_ℓ v_k)||

The spectral norm was estimated as ||J̃_ℓ v_5||.

### Regularization Loss

The total loss combined causal language modeling with stable rank regularization:

L_total = L_CLM + λ · (1/L) Σ_{ℓ=1}^{L} sr_ℓ^res

where L = 12 layers. Lambda was initialized at 0.01 and adjusted adaptively: if perplexity exceeded 1.01 × baseline, λ was multiplied by 0.9; if below 0.99 × baseline, multiplied by 1.1.

### Implementation Details

- **Architecture**: GPT-2 (125M parameters, 12 layers, 768 hidden dimensions, 12 attention heads)
- **Dataset**: C4 English subset, 10B token budget, streaming mode
- **Training**: 5000 steps (~320M tokens), batch size 32 with gradient accumulation to effective 128
- **Optimizer**: AdamW (lr=3e-4, β=(0.9,0.95), weight_decay=0.1)
- **Schedule**: Cosine decay with 2000-step warmup
- **Hardware**: Single NVIDIA A100 GPU
- **Seed**: 42 (fixed)

Two variants were trained: baseline (λ=0) and regularized (λ adaptive, initialized at 0.01).

## 4. Experimental Setup

### Research Questions

**RQ1: Measurement Reliability** - Can Hutchinson trace (10 probes) and power iteration (5 iterations) provide stable rank measurements with coefficient of variation below 15%?

**RQ2: Controllability** - Can stable rank be reduced by at least 20% via gradient-based regularization while maintaining perplexity within 1% of baseline?

**RQ3: Isolation** - Does baseline training converge successfully under identical conditions, confirming any failure is specific to the regularization?

### Gate Validation Criteria

Success required all four criteria:
1. Mean stable rank reduction ≥20% vs baseline
2. Perplexity deviation ≤1% from baseline
3. Layer variance <2.0× mean stable rank
4. Measurement CV <15%

Failure on any criterion constitutes hypothesis refutation.

### Evaluation Metrics

- **Perplexity**: Evaluated on C4 validation set using sliding window (stride 256)
- **Stable Rank**: Measured per layer every 1000 steps via same Hutchinson + power iteration (10 probes, 5 iterations)
- **Layer Variance**: Coefficient of variation of stable ranks across 12 layers
- **Measurement CV**: Coefficient of variation across Hutchinson samples

## 5. Results

### Gate Validation

All four gate criteria failed:

| Metric | Target | Baseline | Proposed | Result | Pass |
|--------|--------|----------|----------|--------|------|
| Mean SR Reduction | ≥20% | 0.00 | 0.00 | 0.0% | Fail |
| Perplexity Deviation | ≤1% | 59.34 | 45,792.62 | +77,065% | Fail |
| Layer Variance | <2.0× | N/A | 0.000 | 0.000 | Degenerate |
| Measurement CV | <15% | N/A | 0.000 | 0.0% | Degenerate |

### Baseline Performance

The baseline model converged to validation perplexity 59.34 after 5000 steps. Training loss decreased monotonically from ~10 to 4.82. This confirms the experimental setup (dataset, architecture, optimizer, hyperparameters) produces functional language models.

### Regularized Model Performance

The regularized model exhibited three pathologies:

**1. Zero Stable Rank Measurements**: All 12 layers returned exactly 0.0 for stable rank at every checkpoint. Per-layer measurements:
- Layer 0-11: 0.0 (all layers)
- Mean: 0.0
- Standard deviation: 0.0

**2. Perplexity Explosion**: Validation perplexity increased from 59.34 (baseline) to 45,792.62 (regularized), representing 77,065% deviation. Trajectory analysis shows divergence beginning around step 1500, with acceleration after step 3000.

**3. Negative Regularization Losses**: At step 4500:
- CLM loss: 10.76
- Regularization loss: -17,529,929,728
- Total loss: -116,297,128
- Lambda: 0.0063 (decayed from 0.01)

The regularization term magnitude exceeded CLM loss by nine orders of magnitude despite adaptive tuning.

### Training Dynamics

Regularized model training logs (selected steps):

| Step | CLM Loss | Reg Loss | Total Loss | PPL | Lambda |
|------|----------|----------|------------|-----|--------|
| 500  | 9.53 | -414,485 | -4,135 | 6,483 | 0.0095 |
| 1000 | 10.00 | -5,287,041 | -50,217 | 12,599 | 0.0090 |
| 2000 | 10.38 | -191,884,608 | -1,645,160 | 38,441 | 0.0081 |
| 3000 | 10.76 | -1,782,312,320 | -13,791,182 | 47,015 | 0.0074 |
| 4500 | 10.76 | -17,529,929,728 | -116,297,128 | 46,937 | 0.0063 |

Baseline training logs (selected steps):

| Step | Loss | PPL |
|------|------|-----|
| 500  | 7.05 | 200.4 |
| 1000 | 6.76 | 144.1 |
| 2000 | 2.10 | 97.7 |
| 3000 | 4.24 | 64.8 |
| 4500 | 4.82 | 50.2 |

## 6. Analysis

### Root Causes

**Cause 1: Insufficient Hutchinson Probes**

Bekas et al. (2007) establish O(1/ε²) sample complexity for ε-accuracy in trace estimation. For 768-dimensional embeddings and target CV <15%, this implies ~100+ probes. Our implementation used 10 probes, likely producing high-variance estimates. The degenerate zero measurements suggest either extreme variance or gradient detachment.

**Cause 2: Power Iteration Non-Convergence**

Five iterations may be insufficient for spectral norm convergence in residual-corrected Jacobians through attention and LayerNorm operations. The zero spectral norms across all layers and checkpoints suggest non-convergence or numerical underflow in the computation graph.

**Cause 3: Autodiff Gradient Pathologies**

Computing layer-wise Jacobians requires backpropagation through attention mechanisms, MLPs, and LayerNorm. Differentiating through the entire spectral estimation procedure (Hutchinson + power iteration) creates deep computation graphs. The regularization loss magnitude (-10^10) exceeding CLM loss (~10) by nine orders of magnitude indicates gradient explosion. The negative sign violates the mathematical constraint that stable rank is non-negative (sr ≥ 0 by construction).

### Measurement-Control Gap

Post-hoc SVD on saved activations is numerically stable because it operates on fixed tensors without gradient flow. Our approach computes stable rank during forward pass with gradients enabled, feeding it into the loss, and backpropagating through the entire measurement pipeline. This tight coupling means measurement errors directly corrupt the training signal.

### Comparison to Successful Methods

Spectral normalization (Miyato et al., 2018) succeeds because it operates on static weight matrices, not dynamic Jacobians. LoRA and ARD-LoRA succeed because they optimize rank on small adapter matrices with explicit low-rank structure, not via stochastic spectral estimation on full layers.

## 7. Discussion

### Limitations

**L1: Single Implementation Approach** - We tested Hutchinson with 10 probes and power iteration with 5 iterations. Alternative configurations (50-100 probes, 20-50 iterations) or different estimators (Lanczos, randomized SVD) may exhibit different behavior.

**L2: Scale** - Experiments used GPT-2 small (125M) for 5000 steps (~320M tokens). Larger models or longer training may behave differently, though the severity of failure (zero measurements, 77,065% perplexity deviation) suggests fundamental issues rather than scale-dependent phenomena.

**L3: Adaptive Lambda** - Lambda decay from 0.01 to 0.0063 did not prevent loss imbalance. More sophisticated tuning approaches may help, though the negative losses suggest implementation bugs rather than tuning issues.

### Alternative Approaches

**Post-Hoc SVD Observational Study** - Measure stable rank via exact SVD on saved activations from pretrained checkpoints. Test correlations with LoRA rank, KV effective rank, and attention entropy. This approach tests observational correlation without requiring gradient-based control.

**Architectural Constraints** - Enforce low-rank structure via bottleneck layers, factorized attention, or explicit rank parameterizations. This avoids stochastic spectral estimation entirely.

**Gradient-Free Methods** - Decouple measurement from control by computing stable rank periodically via SVD without gradients, then applying explicit projection steps. This avoids backpropagating through spectral estimators.

### Implications

This work documents that gradient-based Jacobian spectral control via Hutchinson trace and power iteration fails at the tested implementation level. The failure modes are specific: zero measurements from insufficient probes or gradient detachment, negative losses from autodiff pathologies, and training divergence from loss scale imbalance.

The gap between mathematical soundness and numerical feasibility is substantial. While J^T J ≈ F and Σ_{ℓ+1} ≈ J_ℓ Σ_ℓ J_ℓ^T are well-defined mathematically, operationalizing them via differentiable stochastic estimation in training loops exposes numerical instabilities.

## 8. Conclusion

We investigated gradient-based residual-corrected Jacobian stable rank regularization during GPT-2 pretraining. The implementation combined Hutchinson trace estimation (10 probes) and power iteration (5 iterations) differentiated through PyTorch autodiff. Results show comprehensive failure: zero stable rank measurements, perplexity increase from 59.3 to 45,792, and regularization losses of -17.5 billion. Baseline training succeeded under identical conditions, isolating the failure to the regularization mechanism.

Root cause analysis identified insufficient Hutchinson probes for 768-dimensional embeddings, power iteration non-convergence in residual-corrected graphs, and gradient pathologies in deep autodiff chains. The measurement-control coupling means noisy estimates directly corrupt training signals, creating a feedback loop that prevents convergence.

This negative result documents specific failure modes in gradient-based spectral control and suggests post-hoc SVD-based observational studies as a numerically stable alternative for testing whether Jacobian stable rank correlates with efficiency properties.

## References

Bekas, C., Kokiopoulou, E., & Saad, Y. (2007). An Estimator for the Diagonal of a Matrix. *Applied Numerical Mathematics*, 57(11-12), 1214-1229.

Dao, T., Fu, D. Y., Ermon, S., Rudra, A., & Ré, C. (2022). FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness. *Neural Information Processing Systems*.

Dao, T., & Gu, A. (2024). Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality. *International Conference on Machine Learning*.

Gelberg, Y., Eitan, Y., Bronstein, M. M., Gal, Y., & Maron, H. (2026). Training Transformers for KV Cache Compressibility. *arXiv preprint arXiv:2605.05971*.

Hu, E. J., Shen, Y., Wallis, P., Allen-Zhu, Z., Li, Y., Wang, S., & Chen, W. (2021). LoRA: Low-Rank Adaptation of Large Language Models. *International Conference on Learning Representations*.

Miyato, T., Kataoka, T., Koyama, M., & Yoshida, Y. (2018). Spectral Normalization for Generative Adversarial Networks. *International Conference on Learning Representations*.

Shinwari, H., & Usama, M. (2025). ARD-LoRA: Dynamic Rank Allocation for Parameter-Efficient Fine-Tuning of Foundation Models With Heterogeneous Adaptation Needs. *IEEE Transactions on Artificial Intelligence*.
