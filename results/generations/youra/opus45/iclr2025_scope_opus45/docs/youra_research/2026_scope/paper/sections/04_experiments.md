# Experimental Setup

We design experiments to discriminate between the Memory Horizon Separation Hypothesis (MHSH) and the Eigenmode Utilization Hypothesis (EUH) through four sequential sub-hypotheses. Each experiment tests a specific aspect of the spectral framework, building evidence toward our main claim.

## Research Questions

Our experiments address the following questions:

**RQ1 (H-E1):** Is the spectral memory horizon $H_{\text{spec}}$ a stable, input-independent property of pretrained Mamba models?
- *Connection to claims:* If $H_{\text{spec}}$ varies with input, it cannot serve as a task boundary.

**RQ2 (H-M1):** Do eigenvalue-derived spectral properties predict actual memory behavior on real text?
- *Connection to claims:* Validates that $H_{\text{spec}}$ has empirical relevance, not just theoretical.

**RQ3 (H-M2):** Does projection-only LoRA preserve SSM eigenvalues during fine-tuning?
- *Connection to claims:* Tests architectural isolation between projections and SSM core.

**RQ4 (H-M3):** Can projection-only LoRA redistribute state energy toward slow eigenmodes?
- *Connection to claims:* Discriminates between MHSH (no redistribution) and EUH (redistribution enables beyond-horizon success).

## Model

We evaluate on **Mamba-1.4B** (state-spaces/mamba-1.4b-hf), a selective state space model with the following characteristics:

| Property | Value |
|----------|-------|
| Parameters | 1.4B |
| Layers | 48 Mamba blocks |
| State dimension | 16 per layer |
| Hidden dimension | 4096 |
| A matrix shape | [4096, 16] per layer |

For cross-scale validation (H-E1), we additionally evaluate **Mamba-370M** to test whether $H_{\text{spec}}$ scales predictably with model size.

## Dataset

**WikiText-103** serves as our primary evaluation corpus for language modeling perplexity. We choose this benchmark because:

1. **Controllable context lengths:** We can evaluate perplexity at varying context windows (25, 64, 128, 256, 512, 1024 tokens) to test memory utilization.
2. **Standard benchmark:** Enables comparison with prior work on Mamba language modeling.
3. **Real text complexity:** Unlike synthetic tasks, WikiText-103 requires naturalistic language modeling.

| Split | Sequences | Tokens |
|-------|-----------|--------|
| Train | 1,801 articles | 103M |
| Validation | 60 articles | 218K |
| Test | 60 articles | 246K |

**Limitation:** WikiText-103 does not provide controllable dependency lengths. A synthetic task like Multi-Query Associative Recall (MQAR) would enable more precise testing of the $H_{\text{spec}}$ boundary. We defer MQAR evaluation to future work.

## LoRA Configuration

For experiments requiring fine-tuning (H-M2, H-M3), we apply projection-only LoRA using the PEFT library:

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Rank ($r$) | 16 | Standard LoRA configuration |
| Alpha ($\alpha$) | 32 | Scaling factor = $\alpha/r = 2$ |
| Target modules | `in_proj`, `x_proj` | Projection matrices only |
| Dropout | 0.1 | Regularization |
| Trainable params | 11.1M | 0.8% of model |

**Critical:** We explicitly exclude `A_log`, `D`, and `dt_proj` from LoRA targets to ensure SSM core parameters remain frozen. The PEFT library verifies this by checking `requires_grad=False` for excluded parameters.

## Training Protocol

| Parameter | Value |
|-----------|-------|
| Optimizer | AdamW |
| Learning rate | $1 \times 10^{-4}$ |
| Weight decay | $1 \times 10^{-4}$ |
| Batch size | 2 |
| Gradient accumulation | 8 (effective batch = 16) |
| Epochs | 1 |
| Sequence length | 256 tokens |
| Training sequences | 500 (PoC configuration) |
| Warmup steps | 100 |

**Rationale:** We use a single epoch with limited sequences because our goal is *mechanism validation*, not optimal task performance. The key measurements (eigenvalue preservation, energy redistribution) require only that training produces measurable parameter updates, not that the model achieves state-of-the-art perplexity.

## Evaluation Metrics

### Stability Metrics (H-E1)

**Coefficient of Variation (CV):**
$$\text{CV}(H_{\text{spec}}) = \frac{\sigma(H_{\text{spec}})}{\mu(H_{\text{spec}})}$$

Threshold: CV < 0.3 confirms $H_{\text{spec}}$ is stable.

### Memory Prediction Metrics (H-M1)

**Perplexity Degradation Ratio:**
$$\text{Degradation} = \frac{\text{mean}(\text{PPL} \mid \text{ctx} < H_{\text{spec}})}{\text{mean}(\text{PPL} \mid \text{ctx} \geq H_{\text{spec}})}$$

Threshold: Ratio > 1.1 confirms eigenvalues predict memory behavior.

### Preservation Metrics (H-M2)

**Relative H_spec Change:**
$$|\Delta H_{\text{spec}}| = \left|\frac{H_{\text{spec}}^{\text{post}} - H_{\text{spec}}^{\text{pre}}}{H_{\text{spec}}^{\text{pre}}}\right| \times 100\%$$

Threshold: $|\Delta H_{\text{spec}}| < 10\%$ confirms eigenvalue preservation.

**Eigenvalue Correlation:**
$$\rho = \text{Pearson}(\vec{\lambda}^{\text{pre}}, \vec{\lambda}^{\text{post}})$$

Supporting metric: $\rho > 0.95$ expected for preservation.

### Energy Redistribution Metrics (H-M3)

**Slow Mode Energy Change:**
$$\Delta E = |f_{\text{slow}}^{\text{post}} - f_{\text{slow}}^{\text{pre}}|$$

where $f_{\text{slow}}$ is the fraction of state energy in eigenmodes with $|\lambda| > 0.99$.

Threshold: $\Delta E > 0.1$ nats would support EUH; $\Delta E \approx 0$ supports MHSH.

## Hardware and Reproducibility

All experiments conducted on:
- **GPU:** Single NVIDIA A100 (40GB)
- **Framework:** PyTorch 2.1, PEFT 0.18.1, Transformers 4.38
- **Random seed:** 42 (fixed across all experiments)

Total compute: ~4 GPU-hours for all experiments.

Code and configuration files are provided in supplementary materials.
