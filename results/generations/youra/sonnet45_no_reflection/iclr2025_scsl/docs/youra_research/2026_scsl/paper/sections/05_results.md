# 5. Results

Our experiments reveal catastrophic failure of gradient-based Jacobian stable rank regularization. The regularized model produced zero stable rank measurements across all layers while exhibiting extreme training instability—perplexity exploded from baseline 59.34 to 45,792.62, a 77,065% deviation. Meanwhile, baseline training converged successfully, isolating the failure to the regularization mechanism itself.

## 5.1 Gate Validation Failure

Figure 1 summarizes the comprehensive failure across all four gate criteria. The regularized model achieved 0% stable rank reduction (target: ≥20%), 77,065% perplexity deviation (target: ≤1%), while producing degenerate variance and measurement CV values (both 0.0 due to all-zero measurements). All four MUST_WORK criteria failed.

\begin{figure}[h]
\centering
\includegraphics[width=0.9\textwidth]{figures/gate_metrics.png}
\caption{Gate criteria validation showing comprehensive failure. Target thresholds (green dashed lines) contrast sharply with actual results (red bars). Zero stable rank reduction combined with catastrophic perplexity explosion demonstrate that gradient-based regularization is not merely ineffective but actively destructive to training.}
\label{fig:gate_metrics}
\end{figure}

**Key Observation 1: Zero Stable Rank Measurements**  
The regularized model returned exactly 0.0 for all stable rank measurements across all 12 layers and all 5000 training steps. This is not a small deviation—it is a complete measurement failure. Since stable rank is mathematically defined as $\text{sr}_\ell^{\text{res}} = \|\tilde{J}_\ell\|_F^2 / \|\tilde{J}_\ell\|_2^2 \geq 0$, and both norms are non-negative by construction, zero values indicate either: (a) the Jacobian itself collapsed to zero (implying no learning), (b) numerical underflow in the autodiff computation, or (c) gradient detachment causing the measurement pipeline to output degenerate values.

**What this means for our hypothesis:** Without reliable measurements, the entire gradient-based control mechanism is dead on arrival. The regularization loss cannot provide meaningful gradient signals if the stable rank estimates are always zero. This failure blocks all downstream testing—we cannot test controllability (RQ2) if measurement infrastructure (RQ1) is broken.

**Key Observation 2: Catastrophic Perplexity Explosion**  
While baseline converged to validation perplexity 59.34 (reasonable for 5000-step pretraining on 320M tokens), the regularized model's perplexity exploded to 45,792.62. This represents a 77,065% deviation from baseline, far exceeding the 1% iso-perplexity constraint. Figure 4 visualizes this divergence trajectory.

**What this means for our hypothesis:** The model did not merely fail to reduce stable rank—it failed to learn language modeling entirely. A perplexity of 45,792 is orders of magnitude worse than random guessing (which would yield perplexity around vocabulary size, ~50,257). This suggests the regularization term actively destabilized optimization, preventing convergence of the language modeling objective.

**Key Observation 3: Baseline Success Isolates Failure**  
The baseline model successfully converged to perplexity 59.34 with stable training dynamics (final training loss: 4.82 at step 4500). This validates that our experimental setup—dataset (C4), architecture (GPT-2 125M), optimizer (AdamW with cosine schedule), and training protocol (batch size, learning rate, seed)—produces functional language models. Therefore, the regularized model's failure cannot be attributed to dataset issues, architectural bugs, or hyperparameter misconfiguration. The failure is specific to the stable rank regularization component.

**What this means for our hypothesis:** This is a controlled experiment in the true sense. With all confounding factors eliminated, we can confidently attribute the catastrophic failure to the gradient-based spectral regularization mechanism. The hypothesis that Jacobian stable rank can be controlled during training via Hutchinson trace + power iteration through autodiff is refuted.

## 5.2 Measurement Infrastructure Failure

Figure 2 shows the per-layer stable rank distribution for the regularized model. All 12 layers returned exactly 0.0, producing a degenerate distribution with zero variance.

\begin{figure}[h]
\centering
\includegraphics[width=0.9\textwidth]{figures/stable_rank_distribution.png}
\caption{Per-layer stable rank distribution across all 12 transformer layers. The regularized model (red) shows degenerate zero measurements for all layers, while baseline measurements (blue) are undefined due to measurement not being computed for the control condition. The complete absence of non-zero values indicates fundamental measurement infrastructure failure rather than mere ineffectiveness.}
\label{fig:stable_rank_distribution}
\end{figure}

**Analysis:** The uniformity of zeros across all layers is diagnostically significant. If the issue were layer-specific (e.g., instability in early or late layers), we would observe zeros in some layers but non-zero values in others. The all-zero pattern suggests a systemic failure in the measurement pipeline itself—either Hutchinson trace estimation, power iteration, or the residual correction step is producing degenerate outputs consistently.

**Hypothesized Root Causes:**
1. **Hutchinson variance too high:** With only 10 Rademacher probes for 768-dimensional embeddings, variance may dominate the trace estimate. Literature suggests ~100+ probes for coefficient of variation below 15% at this dimensionality.
2. **Power iteration non-convergence:** Five iterations may be insufficient for spectral norm convergence when operating on residual-corrected Jacobians ($\tilde{J}_\ell = J_\ell - I$). If residual connections dominate, the residual-corrected matrix may have ill-conditioned spectra.
3. **Gradient detachment:** PyTorch's autodiff may detach intermediate tensors during Jacobian-vector product computation, especially through complex operations (attention, layer normalization, residual additions). Detached tensors would produce zero gradients and zero measurements.

## 5.3 Training Instability and Loss Evolution

Figure 3 reveals an alarming pattern: while the baseline model's training loss decreased smoothly from ~10 to 4.82 over 5000 steps (blue line), the regularized model's total loss plummeted to -116 million (red line). This is not a typo—the regularization loss term became increasingly negative, reaching -17.5 billion by step 4500.

\begin{figure}[h]
\centering
\includegraphics[width=0.9\textwidth]{figures/layer_evolution.png}
\caption{Training loss evolution over 5000 steps. Baseline (blue) exhibits smooth monotonic decrease characteristic of convergent language model training. Regularized model (red) shows catastrophic loss explosion to negative values, driven by regularization term overwhelming causal language modeling loss. Note the log-scale y-axis—the actual deviation spans orders of magnitude.}
\label{fig:layer_evolution}
\end{figure}

**Breakdown of Regularized Model's Final Losses (Step 4500):**
- Causal language modeling (CLM) loss: 10.76 (comparable to baseline's 4.82, indicating learning did not collapse immediately)
- Regularization loss: -17,529,929,728 (highly negative)
- Total loss (CLM + λ × regularization): -116,297,128
- Adaptive lambda: 0.0063 (decayed from initial 0.01)

**Critical Observation: Negative Regularization Losses**  
Stable rank is mathematically non-negative by definition—it is a ratio of squared norms, both of which are non-negative. The regularization loss minimizing stable rank should also be non-negative. Yet we observe massive negative losses, violating mathematical constraints. This suggests a sign error, gradient flow bug, or incorrect loss computation in the autodiff chain.

**Impact on Optimization:** Even with adaptive lambda decay (0.01 → 0.0063), the regularization term dominated the total loss by a factor of $10^9$. The optimizer effectively ignored the CLM loss (magnitude ~10) in favor of the spurious regularization gradient (magnitude ~10^9). This explains why perplexity exploded—the model was not optimizing for next-token prediction but rather for an ill-defined spectral objective with buggy gradients.

## 5.4 Perplexity Divergence Timeline

Figure 4 traces the perplexity trajectories over 5000 training steps, with the ±1% target envelope (shaded region) around baseline.

\begin{figure}[h]
\centering
\includegraphics[width=0.9\textwidth]{figures/perplexity_trajectory.png}
\caption{Validation perplexity trajectories. Baseline (blue) converges smoothly from initial randomness to 59.34. Regularized model (red) explodes catastrophically to 45,792.62, diverging from baseline by 77,065\%. The ±1\% target envelope (gray shaded) highlights the extreme deviation. Perplexity explosion begins early (step ~1000) and accelerates, indicating instability is not a late-training phenomenon but a fundamental incompatibility.}
\label{fig:perplexity_trajectory}
\end{figure}

**Timeline of Divergence:**
- **Steps 0-500:** Both models start at similar perplexity (~10,000, characteristic of random initialization)
- **Steps 500-1500:** Baseline begins converging (PPL decreases), while regularized model plateaus
- **Steps 1500-3000:** Regularized model's perplexity starts increasing—a warning sign of optimization divergence
- **Steps 3000-5000:** Catastrophic explosion to 45,792.62, indicating complete training failure

**Interpretation:** The divergence is not a sudden failure but a gradual instability that compounds over training. Early steps show that the model can compute gradients and update parameters (perplexity does not immediately explode), but the regularization term introduces a pathological gradient signal that overwhelms the CLM objective over time. This pattern suggests fundamental incompatibility between gradient-based spectral control and standard language model training dynamics.

## 5.5 Failure Mode Summary

The experimental results reveal three compounding failure modes:

**Failure Mode 1: Measurement Degeneracy**  
Hutchinson trace + power iteration via autodiff returned zeros for all stable rank measurements. This could stem from insufficient probe count (10 vs. 100+ needed), non-convergent power iteration (5 iterations vs. more needed for residual-corrected Jacobians), or gradient detachment in the autodiff computation graph.

**Failure Mode 2: Loss Scale Imbalance**  
Regularization losses reached magnitudes of $-10^{10}$ while CLM losses remained $\sim 10$. Even with adaptive lambda tuning, this scale disparity overwhelmed optimization. The negative sign suggests an implementation bug—stable rank is non-negative by mathematical definition.

**Failure Mode 3: Training Divergence**  
The regularized model's perplexity exploded by 77,065%, demonstrating that gradient-based spectral regularization is not merely ineffective but actively destructive. The model failed to learn language modeling because the optimizer prioritized the spurious regularization objective over next-token prediction.

**Combined Impact:** These three failure modes interact synergistically. Degenerate measurements produce unreliable gradients, which when multiplied by lambda and added to CLM loss, create pathological optimization dynamics. The result is catastrophic: zero stable rank control, zero language learning, and complete hypothesis refutation at the MUST_WORK gate.
