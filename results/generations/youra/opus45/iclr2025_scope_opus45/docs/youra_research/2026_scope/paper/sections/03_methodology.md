# Methodology

Our methodology directly tests the Memory Horizon Separation Hypothesis (MHSH) versus the Eigenmode Utilization Hypothesis (EUH) through controlled measurement of three quantities: spectral horizon stability, eigenvalue preservation under LoRA, and eigenmode energy redistribution. We first describe how each quantity is computed from model weights, then present our experimental design for discriminating between hypotheses.

## Spectral Memory Horizon

### Definition

State Space Models maintain a hidden state $h_t \in \mathbb{R}^{d_{\text{state}}}$ that evolves according to the discretized dynamics:

$$h_t = \bar{A} h_{t-1} + \bar{B} x_t$$
$$y_t = C h_t + D x_t$$

where $\bar{A} = \exp(\Delta A)$ is the discretized transition matrix, $\Delta$ is the input-dependent discretization step, and $A$ is the continuous-time state matrix parameterized through $A_{\log}$ in Mamba.

For diagonal $A$ (as in Mamba), eigenvalues are directly given by the diagonal elements: $\lambda_i = \exp(\Delta \cdot a_i)$ where $a_i = -\exp(A_{\log,i})$. The magnitude $|\lambda_i| < 1$ ensures stability, with values closer to 1 indicating slower decay.

**Definition (Spectral Memory Horizon).** The spectral memory horizon is defined as:

$$H_{\text{spec}} = \frac{-1}{\log|\lambda_{\max}|}$$

where $\lambda_{\max} = \max_i |\lambda_i|$ is the eigenvalue with largest magnitude across all SSM layers. This quantity represents the theoretical number of timesteps for which information can persist in the slowest-decaying eigenmode before falling to $1/e$ of its original magnitude.

### Computation from Weights

For Mamba-1.4B with 48 layers, we compute $H_{\text{spec}}$ directly from the pretrained $A_{\log}$ parameters:

```
Algorithm 1: Spectral Horizon Computation
Input: Pretrained Mamba model M with L layers
Output: H_spec (tokens)

1. For each layer l in 1..L:
2.     Extract A_log[l] from layer l
3.     Compute lambda_max[l] = exp(-exp(min(A_log[l])))
4. lambda_global = max(lambda_max[1..L])
5. Return H_spec = 1 / min(exp(A_log[all_layers]))
```

**Design Rationale:** We extract $H_{\text{spec}}$ from weights alone rather than through empirical probing because this enables prediction *before* fine-tuning. The computation requires only a forward pass through the $A_{\log}$ parameters, taking less than one second on CPU.

### Stability Verification

A key assumption is that $H_{\text{spec}}$ is a stable model property, not dependent on input sequences. While $\Delta$ varies with input, the $A$ matrix is input-independent in Mamba. We verify stability by computing the coefficient of variation:

$$\text{CV}(H_{\text{spec}}) = \frac{\sigma(H_{\text{spec}})}{\mu(H_{\text{spec}})}$$

across 1000 random input sequences. A threshold of CV < 0.3 confirms $H_{\text{spec}}$ is well-defined.

## Eigenvalue Preservation Under LoRA

### Projection-Only LoRA Configuration

We apply LoRA to projection matrices only, specifically targeting `in_proj` and `x_proj` in Mamba's mixer blocks. These matrices transform inputs before and after the SSM state computation but do not participate in the $\bar{A}$ dynamics.

**LoRA Configuration:**
- Rank $r = 16$
- Alpha $\alpha = 32$ (scaling factor)
- Target modules: `in_proj`, `x_proj`
- Dropout: 0.1
- Trainable parameters: ~11M (0.8% of model)

**Design Rationale:** By targeting only projection matrices, we test whether LoRA can succeed while leaving SSM core parameters untouched. The rank and alpha values follow standard LoRA practices; our results are not sensitive to these hyperparameters since the key measurement is eigenvalue change, not task performance.

### Preservation Metrics

We measure eigenvalue preservation through three complementary metrics:

1. **Relative H_spec Change:**
$$|\Delta H_{\text{spec}}| = \left|\frac{H_{\text{spec}}^{\text{post}} - H_{\text{spec}}^{\text{pre}}}{H_{\text{spec}}^{\text{pre}}}\right| \times 100\%$$

2. **Eigenvalue Correlation:**
$$\rho = \text{corr}(\vec{\lambda}^{\text{pre}}, \vec{\lambda}^{\text{post}})$$
where $\vec{\lambda}$ is the flattened vector of all eigenvalue magnitudes across layers.

3. **A_log Maximum Difference:**
$$\max_{l,i} |A_{\log,i}^{(l),\text{post}} - A_{\log,i}^{(l),\text{pre}}|$$

The threshold for eigenvalue preservation is $|\Delta H_{\text{spec}}| < 10\%$, representing the boundary below which we consider spectral properties effectively unchanged.

## Eigenmode Energy Redistribution

### Energy Distribution Measurement

The Eigenmode Utilization Hypothesis posits that projection-only LoRA can succeed on beyond-horizon tasks by redirecting state energy toward slow eigenmodes. We test this by measuring the energy distribution across eigenmodes.

**Definition (Slow Mode Fraction).** For a given state activation $h_t$, the slow mode fraction is:

$$f_{\text{slow}} = \frac{\sum_{i: |\lambda_i| > 0.99} |h_t[i]|^2}{\sum_i |h_t[i]|^2}$$

We compute this fraction before and after LoRA training to measure energy redistribution:

$$\Delta E = |f_{\text{slow}}^{\text{post}} - f_{\text{slow}}^{\text{pre}}|$$

### Threshold and Interpretation

A threshold of $\Delta E > 0.1$ nats (using KL divergence formulation) indicates meaningful energy redistribution. Values near zero indicate the energy distribution is structurally fixed and cannot be modified through projection changes.

**Design Rationale:** The 0.1 nats threshold corresponds to approximately 10% shift in probability mass in the energy distribution. This is a conservative threshold; smaller shifts could still be statistically significant but would be unlikely to enable beyond-horizon task success.

## Experimental Design

We structure our experiments as four sequential sub-hypotheses, each testing one aspect of the MHSH vs. EUH framework:

| Hypothesis | Type | Gate | Metric | Threshold |
|------------|------|------|--------|-----------|
| H-E1 | Existence | MUST_WORK | CV($H_{\text{spec}}$) | < 0.3 |
| H-M1 | Mechanism | MUST_WORK | Degradation ratio | > 1.1 |
| H-M2 | Mechanism | MUST_WORK | $|\Delta H_{\text{spec}}|$ | < 10% |
| H-M3 | Mechanism | SHOULD_WORK | $\Delta E$ | > 0.1 |

**H-E1 (Existence):** Validates that $H_{\text{spec}}$ is a measurable, stable property. This is foundational---if $H_{\text{spec}}$ varies significantly with input, the entire framework collapses.

**H-M1 (Mechanism):** Validates that eigenvalue-derived $H_{\text{spec}}$ predicts actual memory behavior. We measure perplexity at varying context lengths; if perplexity degrades significantly when context < $H_{\text{spec}}$, eigenvalues have empirical relevance.

**H-M2 (Mechanism):** Validates that projection-only LoRA preserves eigenvalues. This confirms the architectural isolation between projection parameters and SSM core.

**H-M3 (Mechanism):** Tests the EUH mechanism. If $\Delta E > 0.1$, projection-only LoRA can redirect energy to slow modes; if $\Delta E \approx 0$, EUH is eliminated and MHSH is supported.

### Dataset and Model

- **Model:** Mamba-1.4B (state-spaces/mamba-1.4b-hf), 48 layers
- **Dataset:** WikiText-103 for training and perplexity evaluation
- **Context lengths:** 25, 64, 128, 256, 512, 1024 tokens
- **Training:** 1 epoch, batch size 2, gradient accumulation 8, learning rate $10^{-4}$

**Design Rationale:** WikiText-103 provides a standard language modeling benchmark with controllable context lengths. While a controlled task like MQAR would enable more precise dependency length control, WikiText-103 perplexity serves as a meaningful proxy for memory utilization. We defer MQAR evaluation to future work.

### Implementation

Our implementation uses PyTorch with the PEFT library for LoRA adaptation. Key components:

- **MambaProbe:** Extracts $A_{\log}$ parameters and computes $H_{\text{spec}}$
- **LoRAAdapter:** Applies projection-only LoRA via PEFT
- **EigenvaluePreservationValidator:** Compares pre/post eigenvalue spectra
- **EigenmodeEnergyAnalyzer:** Measures slow mode energy distribution

All code is provided in the supplementary material. Experiments were conducted on a single NVIDIA A100 GPU with 40GB memory.
