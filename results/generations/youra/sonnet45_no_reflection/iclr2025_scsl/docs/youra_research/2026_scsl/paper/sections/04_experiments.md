# 4. Experiments

To test whether residual-corrected Jacobian stable rank can be controlled during transformer pretraining via gradient-based regularization, we designed a controlled experiment comparing baseline GPT-2 training against training with explicit stable rank regularization. Our experimental design prioritizes isolation of failure modes: identical architectures, datasets, and hyperparameters, with only the regularization term as the differentiating factor.

## 4.1 Experimental Questions

We structure our evaluation around three research questions:

**RQ1: Can stable rank be measured reliably during training?** We hypothesized that Hutchinson trace estimation (10 Rademacher probes) combined with power iteration (5 iterations) would provide stable rank measurements with coefficient of variation (CV) below 15%, enabling gradient-based optimization. Measurement reliability is foundational—without stable metrics, gradient-based control is impossible.

**RQ2: Can stable rank be reduced via gradient-based regularization?** Given reliable measurements, we predicted that adding a regularization term minimizing mean layer-wise stable rank would achieve at least 20% reduction relative to baseline while maintaining iso-perplexity (within 1% deviation). This tests the core controllability hypothesis.

**RQ3: Is failure attributable to experimental setup or regularization?** To isolate potential failure causes, we validate that baseline training converges successfully on the same dataset, architecture, and training protocol. Baseline success confirms that any observed failure is specific to the regularization mechanism, not experimental infrastructure.

## 4.2 Datasets

We evaluate on C4 (Colossal Clean Crawled Corpus), the standard pretraining dataset for language models. C4 provides natural language text at scale, enabling direct comparison with established GPT-2 pretraining benchmarks.

**C4 Subset:** We use a 10 billion token subset from the English variant (allenai/c4 on HuggingFace Datasets), streamed to avoid downloading the full 305GB corpus. The dataset consists of cleaned web text with timestamps and source URLs, preprocessed via GPT-2 tokenizer with sequence length 512 tokens.

**Rationale:** C4 is widely adopted for transformer pretraining (T5, GPT-Neo, various community models), providing reproducibility and comparability. Its scale (10B tokens) is sufficient for proof-of-concept validation at 5000 training steps while remaining computationally feasible. The natural language domain is appropriate for testing whether Jacobian spectral properties correlate with language modeling performance.

## 4.3 Baselines and Comparisons

**Baseline: Standard GPT-2 Pretraining**  
We train GPT-2 (125M parameters, 12 layers, 768-dimensional embeddings) from random initialization using standard causal language modeling loss. This serves as the control condition, validating that our experimental setup (dataset, architecture, optimizer) produces convergent language models.

**Proposed: Regularized GPT-2 with Stable Rank Control**  
Identical architecture and training protocol, with one modification: we augment the loss function with a regularization term minimizing mean residual-corrected Jacobian stable rank across all 12 transformer layers:

$$
L_{\text{total}} = L_{\text{CLM}} + \lambda \cdot \frac{1}{12} \sum_{\ell=1}^{12} \text{sr}_\ell^{\text{res}}
$$

where $\text{sr}_\ell^{\text{res}} = \|\tilde{J}_\ell\|_F^2 / \|\tilde{J}_\ell\|_2^2$ is the stable rank of the residual-corrected Jacobian $\tilde{J}_\ell = J_\ell - I$.

**Regularization Weight:** We employ adaptive lambda tuning, initializing at $\lambda = 0.01$ and adjusting dynamically to maintain perplexity within 1% of baseline. This approach prioritizes the iso-perplexity constraint while maximizing stable rank reduction.

**Why This Comparison?** The baseline isolates the effect of regularization. If both models train on identical data with identical architectures but only the regularized variant fails, we can attribute failure specifically to the gradient-based spectral control mechanism rather than dataset issues, architectural bugs, or hyperparameter choices.

## 4.4 Implementation Details

**Architecture:** GPT-2 small configuration (124M parameters)—12 layers, 768 hidden dimensions, 12 attention heads, 50,257 vocabulary size, 1024 token context window. We use the standard decoder-only transformer with residual connections and layer normalization, implemented via HuggingFace Transformers (openai-community/gpt2 configuration, trained from scratch with random initialization).

**Stable Rank Computation:** For each transformer layer $\ell$, we estimate stable rank via two numerical subroutines:

1. **Frobenius Norm Estimation (Hutchinson Trace):** We sample 10 Rademacher vectors (random ±1) and compute Jacobian-vector products via PyTorch autodiff. For each probe vector $v$, we compute $\tilde{J}_\ell v = J_\ell v - v$ (residual correction) and accumulate $\|\tilde{J}_\ell\|_F^2 \approx \frac{1}{10} \sum_{i=1}^{10} v_i^\top (\tilde{J}_\ell^\top \tilde{J}_\ell) v_i$.

2. **Spectral Norm Estimation (Power Iteration):** We initialize a random unit vector and iteratively apply $\tilde{J}_\ell^\top \tilde{J}_\ell$ for 5 iterations, extracting the dominant eigenvalue as $\|\tilde{J}_\ell\|_2^2$. Power iteration converges rapidly for well-conditioned matrices; we use 5 iterations as a balance between accuracy and computational cost.

The stable rank is then $\text{sr}_\ell^{\text{res}} = \|\tilde{J}_\ell\|_F^2 / \|\tilde{J}_\ell\|_2^2$. We compute this for all 12 layers at each training step, averaging to produce the regularization loss term.

**Training Hyperparameters:**
- Optimizer: AdamW (lr=3e-4, betas=(0.9, 0.95), weight_decay=0.1)
- Learning rate schedule: Cosine decay with 2000-step warmup (max lr: 3e-4, min lr: 3e-5)
- Batch size: 32 per GPU, effective batch size 128 via 4-step gradient accumulation
- Sequence length: 512 tokens
- Training steps: 5000 (approximately 320M tokens)
- Seed: 42 (fixed for reproducibility)

**Compute Resources:** All experiments run on a single NVIDIA GPU. Baseline training completed in approximately 8 hours; regularized training required 12 hours due to additional stable rank computation overhead.

**Reproducibility:** Code, configuration files, and trained checkpoints are available in the supplementary materials. We use PyTorch 2.0 with automatic mixed precision (fp16) for memory efficiency.

## 4.5 Evaluation Metrics

**Primary Metrics:**

**Perplexity (PPL):** We evaluate language modeling quality on the C4 validation set using sliding window perplexity with stride 256. Perplexity measures how well the model predicts held-out text—lower is better. We report final validation perplexity at step 5000 and track trajectories throughout training.

**Residual-Corrected Jacobian Stable Rank ($\text{sr}_\ell^{\text{res}}$):** Measured per layer every 1000 steps using the same Hutchinson + power iteration approach as during training (but without gradient computation for efficiency). We report mean stable rank across 12 layers and per-layer distributions. The target is at least 20% reduction relative to baseline.

**Secondary Metrics:**

**Layer Variance (CV):** Coefficient of variation of stable rank across layers, computed as standard deviation divided by mean. This metric detects whether rank reduction occurs uniformly or via compensatory redistribution (some layers increasing while others decrease). Target: CV < 2.0 × baseline CV.

**Measurement Precision (CV):** To validate that Hutchinson trace and power iteration produce reliable estimates, we compute coefficient of variation across multiple measurement samples at selected checkpoints. Target: CV < 15%, indicating sufficient probe count for stable gradient signals.

**Gate Validation Criteria:**

Our hypothesis succeeds if all four criteria are met:
1. Mean stable rank reduction ≥ 20% vs baseline
2. Perplexity deviation ≤ 1% from baseline
3. Layer variance < 2.0 × mean stable rank
4. Measurement CV < 15%

Failure on any criterion constitutes hypothesis refutation. As this is a MUST_WORK gate (existence claim), failure terminates the research direction, prompting pivot to alternative approaches (post-hoc SVD analysis, architectural constraints, or gradient-free methods).

## 4.6 Fairness Considerations

To ensure experimental validity, both baseline and regularized models share identical configurations:

- **Identical architecture:** Same GPT-2 small config (12 layers, 768d, 12 heads)
- **Identical dataset:** Same C4 subset, same tokenization, same sequence length (512)
- **Identical optimizer:** Same AdamW hyperparameters (lr, betas, weight decay)
- **Identical schedule:** Same cosine decay with warmup
- **Identical batch size:** Same effective batch size (128 via gradient accumulation)
- **Identical random seed:** Seed 42 for both models (controls initialization and data shuffling)
- **Identical training duration:** Both trained for exactly 5000 steps

The only difference is the regularization term added to the proposed model's loss function. This controlled design isolates the effect of gradient-based stable rank regularization, enabling causal attribution of any observed differences.
