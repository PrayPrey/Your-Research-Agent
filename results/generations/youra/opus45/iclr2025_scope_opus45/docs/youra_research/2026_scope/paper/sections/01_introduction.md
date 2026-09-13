# Introduction

Why does LoRA work for Mamba on some tasks but fail on others? Despite the growing adoption of State Space Models (SSMs) for their linear-time inference efficiency, the limits of parameter-efficient fine-tuning (PEFT) on these architectures remain poorly understood. We discover that projection-only LoRA is bounded by a measurable *spectral memory horizon*---and contrary to theoretical expectation, it cannot extend this boundary by redistributing energy to slow eigenmodes.

This finding matters for practitioners deploying Mamba variants in production. A researcher fine-tuning Mamba-1.4B with LoRA for a task requiring 512-token context dependencies may invest significant compute only to discover the model cannot learn the task---not due to capacity limitations, but because the intrinsic spectral horizon $H_{\text{spec}} = 256$ tokens cannot be extended by projection-only adaptation. Without understanding these boundaries, the SSM community will continue trial-and-error fine-tuning, wasting resources and potentially abandoning viable architectures due to misattributed failures.

## The Adaptation Boundary Problem

The surface-level challenge is well-documented: standard LoRA targets linear projections but cannot directly modify SSM core modules---the $A$, $B$, $C$, $D$ matrices that govern state dynamics [1, 2]. Recent work has cataloged this limitation and proposed alternatives including Sparse Dimension Tuning [1] and State-offset Tuning [3]. The consensus is that projection-only LoRA is "sometimes effective, sometimes not."

However, the deeper issue is not that LoRA *cannot* reach SSM parameters, but that even when projection adaptation succeeds, it operates under an invisible constraint: the spectral memory horizon $H_{\text{spec}}$. Prior work focused on empirical performance comparisons without investigating the spectral dynamics underlying SSM state evolution. The connection between eigenvalue structure and task suitability was never explicitly modeled.

This leaves a critical gap: no prior work provides a measurable criterion for predicting when projection-only LoRA will succeed versus fail on SSM architectures. Bridging this gap requires combining eigenvalue analysis of SSM dynamics with controlled experiments on adaptation scope---a synthesis that existing methods do not provide.

## Our Key Insight

We observe that SSM state dynamics are governed by the discretized transition matrix $\bar{A} = \exp(\Delta A)$, whose eigenvalues determine information decay rates. The spectral memory horizon, defined as $H_{\text{spec}} = -1/\log|\lambda_{\max}|$, gives the theoretical persistence length of the slowest-decaying eigenmode. Crucially, projection-only LoRA modifies the input and output mappings ($B$ and $C$ matrices) but leaves $\bar{A}$ eigenvalues untouched.

This structural separation suggests two competing hypotheses for beyond-horizon task performance:

1. **Memory Horizon Separation Hypothesis (MHSH):** Task success is bounded by whether information dependencies fall within $H_{\text{spec}}$. Beyond-horizon tasks require "Spectral Surgery"---modifying the $A$ matrix eigenvalues.

2. **Eigenmode Utilization Hypothesis (EUH):** Projection-only LoRA can succeed on beyond-horizon tasks by redistributing state energy toward slow eigenmodes, effectively utilizing latent memory capacity.

Our experiments definitively discriminate between these hypotheses by measuring eigenvalue preservation and energy redistribution under LoRA training.

## Contributions

Building on this spectral analysis framework, we make the following contributions:

**First**, we operationalize the spectral memory horizon $H_{\text{spec}}$ as a measurable quantity derived from pretrained Mamba weights. We demonstrate that $H_{\text{spec}}$ is input-independent (CV = $2.22 \times 10^{-16}$ across 1000 sequences) and that it predicts perplexity degradation on real text---establishing it as a meaningful task boundary rather than a theoretical artifact.

**Second**, we show that projection-only LoRA achieves *perfect* eigenvalue preservation ($|\Delta H_{\text{spec}}| = 0.0\%$, correlation = 1.0), confirming the architectural isolation between projection parameters and SSM core dynamics. This rules out any indirect eigenvalue modification through gradient coupling.

**Third**, and most significantly, we empirically eliminate the Eigenmode Utilization Hypothesis. Energy redistribution toward slow eigenmodes is essentially zero ($\Delta E = 5.93 \times 10^{-7}$ nats, six orders of magnitude below the 0.1 nats threshold). Only 2 of 48 layers in Mamba-1.4B possess any slow-mode capacity, and the energy distribution is structurally fixed by the $A$ matrix architecture.

Together, these findings establish that projection-only LoRA is bounded by the intrinsic spectral horizon, providing the first measurable criterion for predicting PEFT effectiveness on SSM architectures.

We organize the paper as follows. Section 2 reviews related work on SSM adaptation and positions our spectral analysis framework. Section 3 presents our methodology for measuring $H_{\text{spec}}$, eigenvalue preservation, and energy redistribution. Section 4 describes our experimental setup across four sub-hypotheses. Section 5 presents results with quantitative evidence. Section 6 discusses implications and limitations, and Section 7 concludes with future directions.
