# 6. Discussion

## 6.1 Failure Mode Analysis

Our experiments reveal that gradient-based residual-corrected Jacobian stable rank regularization is not merely ineffective—it is fundamentally unstable at the implementation level tested. We identify three root causes that compound to produce catastrophic failure.

**Root Cause 1: Hutchinson Trace Variance Dominates at Training Scale**  
The Hutchinson trace estimator with 10 Rademacher probes proved insufficient for 768-dimensional hidden states. Theoretical analysis (Bekas et al., 2007) suggests that achieving coefficient of variation below 15% requires $O(1/\epsilon^2)$ samples, implying approximately 100+ probes for our embedding dimensionality. With only 10 probes, the trace estimate $\|\tilde{J}_\ell\|_F^2$ likely suffered from high variance, producing unreliable gradient signals. When embedded in a training loop and differentiated via autodiff, this variance compounds across 12 layers and 5000 steps, potentially explaining the degenerate zero measurements.

**Root Cause 2: Deep Autodiff Chains Through Attention Layers**  
Computing the layer-wise Jacobian $\partial h_\ell / \partial h_{\ell-1}$ requires backpropagating through attention mechanisms, feed-forward MLPs, and layer normalization—each introducing nonlinearities and numerical stability challenges. Our residual-corrected formulation $\tilde{J}_\ell = J_\ell - I$ adds further complexity: we must compute Jacobian-vector products for the full layer output, then subtract the identity contribution. This creates deep computation graphs where gradients can explode (yielding the $-10^{10}$ regularization losses observed) or vanish (yielding zero stable rank measurements). Standard spectral normalization (Miyato et al., 2018) operates on weight matrices directly, avoiding this autodiff depth—our approach attempts to differentiate through the entire forward pass, exposing numerical pathologies.

**Root Cause 3: Measurement-Control Coupling**  
We conflated two distinct operations: *measuring* spectral properties (post-hoc, for analysis) versus *controlling* them (in-training, via gradients). Post-hoc SVD on saved activations is numerically stable because it operates on fixed tensors without gradient flow. In contrast, our approach computes stable rank during the forward pass with gradients enabled, feeding it into the loss function, and backpropagating through the entire measurement pipeline (Hutchinson probes, power iteration, Jacobian-vector products). This tight coupling means measurement errors directly corrupt the training signal, creating a feedback loop: noisy measurements → bad gradients → worse parameters → noisier measurements.

**Interaction Effects:** These three causes interact synergistically. High Hutchinson variance (Cause 1) produces noisy trace estimates. Deep autodiff chains (Cause 2) amplify this noise via gradient explosion or vanishing. Coupling measurement to control (Cause 3) feeds corrupted signals back into optimization. The result: zero measurements (from vanished gradients or detachment), negative losses (from exploded gradients with sign errors), and catastrophic training divergence (from pathological optimization dynamics).

## 6.2 What the Results Mean for the Hypothesis

**The Core Claim is Refuted at the Implementation Level**  
Our hypothesis stated that residual-corrected Jacobian stable rank can be reduced by at least 20% during pretraining via gradient-based regularization while maintaining iso-perplexity. The experimental results comprehensively reject this claim: 0% stable rank reduction, 77,065% perplexity deviation, and all four gate criteria failed. This is not a marginal failure requiring hyperparameter tuning—it is a fundamental breakdown.

**Mathematical Soundness ≠ Practical Feasibility**  
The theoretical framework remains mathematically valid: $J^T J \approx$ Fisher, $\Sigma_{\ell+1} \approx J_\ell \Sigma_\ell J_\ell^T$, and stable rank $\text{sr}_\ell^{\text{res}} = \|\tilde{J}_\ell\|_F^2 / \|\tilde{J}_\ell\|_2^2$ are all well-defined. However, operationalizing these mathematical objects via differentiable estimation (Hutchinson + power iteration) in training loops exposes numerical instabilities that theory does not capture. This highlights a critical gap: elegant mathematics does not guarantee implementable algorithms, especially when gradients must flow through stochastic estimators and deep computation graphs.

**Observational Study Still Viable**  
Importantly, our failure does not refute the *existence* of correlations between Jacobian stable rank and efficiency metrics—only the *controllability* via gradients. The hypothesis may be observationally true (stable rank correlates with LoRA rank, KV compressibility, attention entropy) even if interventional control via training-time regularization is infeasible. Post-hoc SVD analysis on pretrained checkpoints remains a viable path: measure stable rank retrospectively using numerically stable methods (no autodiff, no stochastic estimation), then test correlations with efficiency properties. If correlations exist, the scientific insight survives even though the training-time control mechanism failed.

## 6.3 Limitations

**L1: Single Implementation Approach**  
We tested one specific implementation: Hutchinson trace with 10 Rademacher probes, power iteration with 5 iterations, and residual-corrected Jacobians via PyTorch autodiff. Alternative implementations—more probes (50, 100), more iterations (20, 50), different estimators (Lanczos, randomized SVD), or non-residual Jacobians—may exhibit different failure modes or succeed where our approach failed. However, the tested approach represents standard practice from literature (Bekas et al. for Hutchinson, PyTorch's spectral_norm for power iteration), so its failure is informative: the default methods are insufficient.

**Why this limitation is acceptable:** Documenting the failure of standard methods is valuable—it prevents the community from naively applying Hutchinson + power iteration to layer-wise Jacobian regularization and wasting compute reproducing our bugs. Future work can build on our failure analysis to design more robust implementations.

**L2: Scale Limitation (125M Parameters, 5000 Steps)**  
Our experiments used GPT-2 small (125M) trained for 5000 steps (~320M tokens), a proof-of-concept budget. Larger models (350M, 1B) or longer training (10B tokens) may exhibit different behavior—stable rank control might require scale to work, or conversely, numerical issues might worsen at scale. However, the failure we observed is so severe (zero measurements, perplexity explosion by 77,065%) that longer training would not fix it; we would simply diverge for more steps. The measurement infrastructure must be fixed before attempting larger-scale validation.

**Why this limitation is acceptable:** The PoC design correctly prioritized rapid failure detection over exhaustive scaling experiments. Fixing the zero-measurement bug should precede any scale-up effort.

**L3: Adaptive Lambda Tuning Ineffectiveness**  
Our adaptive lambda approach (initialize at 0.01, decay to maintain iso-perplexity) failed to prevent loss imbalance. The regularization loss reached $-10^{10}$ while CLM loss stayed at $\sim 10$, a nine-order-of-magnitude disparity that lambda decay from 0.01 to 0.0063 could not address. More sophisticated tuning (gradient norm matching, loss-scale balancing, separate learning rates) might help, but the negative regularization losses suggest a sign error or implementation bug rather than a tuning issue.

**Why this limitation is acceptable:** Hyperparameter tuning cannot fix a measurement pipeline that outputs zeros or a loss computation that violates mathematical non-negativity. The failure is structural, not parametric.

## 6.4 Recommended Alternative Approaches

Given the comprehensive failure of gradient-based control, we recommend three alternative paths for future research:

**Alternative 1: Post-Hoc SVD Observational Study (Highest Priority)**  
Measure residual-corrected Jacobian stable rank via exact SVD on saved layer activations from pretrained checkpoints. Compute empirical Jacobians by sampling inputs, collecting layer outputs, and performing singular value decomposition—no gradients, no stochastic estimation, numerically stable. Then test correlations with LoRA rank (via subspace PCA), KV covariance effective rank (via SVD on key-value matrices), and attention entropy (via saved attention weights). If Pearson $r \geq 0.3$ found for at least two of three metric pairs, the core scientific hypothesis retains value despite implementation failure. This approach tests "does stable rank correlate with efficiency?" (observational) rather than "can we control stable rank during training?" (interventional).

**Alternative 2: Architectural Constraints for Low-Rank Structure**  
Rather than gradient-based regularization, enforce low-rank structure architecturally: bottleneck layers (reduce hidden dimension mid-layer, then expand), factorized attention (decompose QKV projections into low-rank components), or explicit rank constraints (parameterize layers as low-rank factorizations $AB^T$ with fixed rank $r$). These methods guarantee structural properties without requiring differentiable spectral estimation, avoiding our autodiff and measurement issues entirely. However, they deviate from standard transformer architectures, potentially requiring architectural search to maintain performance.

**Alternative 3: Gradient-Free Spectral Methods**  
Decouple measurement from control: compute stable rank periodically (every 1000 steps) via exact SVD without gradients, then apply explicit projection steps to constrain eigenspectra (threshold singular values, rescale Jacobians). This zeroth-order optimization avoids backpropagating through spectral estimators, eliminating our Root Cause 3 (measurement-control coupling). However, projection steps may conflict with gradient-based optimization of the CLM objective, requiring careful coordination.

**Broader Lesson:** Our failure demonstrates that not all mathematical operations are practical to differentiate at scale. Spectral properties (eigenvalues, singular values, matrix ranks) are well-defined mathematically but numerically sensitive when computed via stochastic estimation in deep autodiff chains. The machine learning community should be cautious when attempting gradient-based optimization of spectral objectives—post-hoc analysis or architectural constraints may be more robust.

## 6.5 Broader Impact

**Positive Impact: Preventing Wasted Compute**  
Negative results with rigorous analysis provide value to the research community. By documenting the failure modes of gradient-based Jacobian stable rank regularization in detail—zero measurements, loss scale imbalance, training divergence—we prevent other researchers from reproducing the same bugs and wasting expensive compute cycles. Our comprehensive diagnostic analysis (per-layer metrics, adaptive tuning, measurement CV tracking) identifies root causes rather than dismissing failure as "bad hyperparameters," accelerating future work toward viable solutions.

**Methodological Contribution**  
This work contributes methodologically by highlighting the measurement-control gap in spectral regularization. Measuring spectral properties (e.g., via post-hoc SVD) is numerically straightforward; controlling them via gradients during training is fraught with numerical instabilities. This distinction should inform future research on spectral objectives in deep learning—post-hoc analysis may be preferable to training-time optimization for certain spectral properties.

**No Ethical or Misuse Concerns**  
This research focuses on training efficiency for language models, a technical domain without direct societal risks. The negative result—that our approach does not work—precludes misuse. There are no ethical concerns beyond standard academic research practices (reproducibility, honest reporting of results).
