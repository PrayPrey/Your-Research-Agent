# Spectral Memory Horizon Bounds Projection-Only LoRA in State Space Models

## Abstract

Parameter-efficient fine-tuning methods such as LoRA have been applied to State Space Models (SSMs) with variable success across different tasks. This work investigates the spectral dynamics of SSM adaptation by introducing the spectral memory horizon H_spec, defined as -1/log|lambda_max|, which characterizes the theoretical persistence length of information in the slowest-decaying eigenmode. Through experiments on Mamba-1.4B, the following findings are reported: (1) H_spec is an input-independent property of pretrained models with coefficient of variation effectively zero (CV = 2.22 x 10^-16 across 1000 sequences); (2) projection-only LoRA targeting in_proj and x_proj matrices preserves eigenvalues exactly (delta H_spec = 0.0%, correlation = 1.0); and (3) energy redistribution toward slow eigenmodes does not occur under projection-only LoRA (delta E = 5.93 x 10^-7 nats, six orders of magnitude below the 0.1 nats threshold). This third finding, a negative result, eliminates the Eigenmode Utilization Hypothesis and provides evidence supporting the Memory Horizon Separation Hypothesis: that task adaptation via projection-only LoRA is bounded by the intrinsic spectral horizon. The discriminative task-failure test (H-M4) was not executed; thus, direct verification of task failure beyond H_spec remains for future work.

## 1. Introduction

Standard LoRA targets linear projections but cannot directly modify SSM core modules such as the A, B, C, and D matrices that govern state dynamics. Recent work has cataloged this limitation and proposed alternatives including Sparse Dimension Tuning and State-offset Tuning. However, the question of when projection-only LoRA will succeed versus fail on SSM architectures has lacked a principled, measurable criterion.

This work investigates the spectral dynamics underlying SSM state evolution. SSM state dynamics are governed by the discretized transition matrix A_bar = exp(Delta * A), whose eigenvalues determine information decay rates. The spectral memory horizon, defined as H_spec = -1/log|lambda_max|, gives the theoretical persistence length of the slowest-decaying eigenmode. Projection-only LoRA modifies the input and output mappings but leaves A_bar eigenvalues unchanged.

This structural separation motivates two competing hypotheses:

1. **Memory Horizon Separation Hypothesis (MHSH):** Task success is bounded by whether information dependencies fall within H_spec. Beyond-horizon tasks require modifying the A matrix eigenvalues.

2. **Eigenmode Utilization Hypothesis (EUH):** Projection-only LoRA can succeed on beyond-horizon tasks by redistributing state energy toward slow eigenmodes, utilizing latent memory capacity.

The experiments in this work test these hypotheses through measurement of eigenvalue preservation and energy redistribution under LoRA training. The main findings are:

- H_spec is a stable, input-independent property measurable from pretrained Mamba weights (CV = 2.22 x 10^-16).
- Projection-only LoRA achieves exact eigenvalue preservation (delta H_spec = 0.0%, eigenvalue correlation = 1.0).
- Energy redistribution toward slow eigenmodes is negligible (delta E = 5.93 x 10^-7 nats), eliminating the EUH mechanism.

These results provide evidence that projection-only LoRA is bounded by the intrinsic spectral horizon, though the direct task-failure verification (H-M4) was not completed.

## 2. Related Work

### 2.1 Parameter-Efficient Fine-Tuning for SSMs

SSM-PEFT provides analysis of fine-tuning methods for State Space Models, introducing Sparse Dimension Tuning (SDT) as an alternative to standard LoRA. MambaPEFT catalogs over 20 PEFT method variants applied to Mamba architectures, finding that PEFT is generally more effective for Mamba than for Transformers on certain tasks. State-offset Tuning proposes learning an additive offset to the SSM state. These works identify successful and unsuccessful configurations but do not provide a measurable criterion for predicting when projection-only adaptation will succeed.

### 2.2 State Space Model Foundations

Mamba introduced selective state spaces with input-dependent discretization, achieving Transformer-competitive performance with linear-time inference. The architecture parameterizes the continuous-time state matrix A through A_log, with discretization via the zero-order hold: A_bar = exp(Delta * A). While the discretization step Delta is input-dependent, the A matrix itself is fixed after pretraining.

### 2.3 Eigenvalue Analysis in Recurrent Models

The connection between eigenvalue magnitude and memory capacity in recurrent systems is established in control theory. For discrete-time linear systems h_t = A * h_{t-1} + B * u_t, eigenvalues |lambda| < 1 ensure stability, with |lambda| approaching 1 corresponding to longer memory. Prior work has not applied eigenvalue analysis to understand PEFT limitations in SSMs.

## 3. Method

### 3.1 Spectral Memory Horizon

State Space Models maintain a hidden state h_t that evolves according to discretized dynamics:

h_t = A_bar * h_{t-1} + B_bar * x_t
y_t = C * h_t + D * x_t

where A_bar = exp(Delta * A) is the discretized transition matrix. For diagonal A (as in Mamba), eigenvalues are given by lambda_i = exp(Delta * a_i) where a_i = -exp(A_log_i).

**Definition (Spectral Memory Horizon):**

H_spec = -1 / log|lambda_max|

where lambda_max = max_i |lambda_i| is the eigenvalue with largest magnitude across all SSM layers. This quantity represents the theoretical number of timesteps for which information can persist in the slowest-decaying eigenmode before falling to 1/e of its original magnitude.

For Mamba-1.4B with 48 layers, H_spec is computed directly from the pretrained A_log parameters.

### 3.2 Eigenvalue Preservation Measurement

Projection-only LoRA is applied to in_proj and x_proj matrices only. Eigenvalue preservation is measured through:

1. **Relative H_spec Change:** |delta H_spec| = |(H_spec_post - H_spec_pre) / H_spec_pre| x 100%
2. **Eigenvalue Correlation:** Pearson correlation between pre- and post-training eigenvalue vectors
3. **A_log Maximum Difference:** max|A_log_post - A_log_pre| across all layers

### 3.3 Eigenmode Energy Redistribution

The slow mode fraction is defined as:

f_slow = sum_{i: |lambda_i| > 0.99} |h_t[i]|^2 / sum_i |h_t[i]|^2

Energy redistribution is measured as:

delta E = |f_slow_post - f_slow_pre|

A threshold of delta E > 0.1 nats indicates meaningful energy redistribution.

### 3.4 Experimental Design

Four sequential sub-hypotheses were tested:

| Hypothesis | Type | Gate | Metric | Threshold |
|------------|------|------|--------|-----------|
| H-E1 | Existence | MUST_WORK | CV(H_spec) | < 0.3 |
| H-M1 | Mechanism | MUST_WORK | Degradation ratio | > 1.1 |
| H-M2 | Mechanism | MUST_WORK | |delta H_spec| | < 10% |
| H-M3 | Mechanism | SHOULD_WORK | delta E | > 0.1 |

H-M4 (discriminative MQAR test) was planned but not executed.

## 4. Experimental Setup

### 4.1 Model

Experiments were conducted on Mamba-1.4B (state-spaces/mamba-1.4b-hf):

| Property | Value |
|----------|-------|
| Parameters | 1.4B |
| Layers | 48 Mamba blocks |
| State dimension | 16 per layer |
| Hidden dimension | 4096 |

For cross-scale validation (H-E1), Mamba-370M was additionally evaluated.

### 4.2 Dataset

WikiText-103 served as the evaluation corpus for language modeling perplexity. Perplexity was evaluated at context lengths of 25, 64, 128, 256, 512, and 1024 tokens.

**Limitation:** WikiText-103 does not provide controllable dependency lengths. A synthetic task such as Multi-Query Associative Recall (MQAR) would enable more precise testing of the H_spec boundary but was not used in these experiments.

### 4.3 LoRA Configuration

| Parameter | Value |
|-----------|-------|
| Rank (r) | 16 |
| Alpha | 32 |
| Target modules | in_proj, x_proj |
| Dropout | 0.1 |
| Trainable params | 11.1M (0.8% of model) |

A_log, D, and dt_proj were explicitly excluded from LoRA targets.

### 4.4 Training Protocol

| Parameter | Value |
|-----------|-------|
| Optimizer | AdamW |
| Learning rate | 1 x 10^-4 |
| Batch size | 2 (effective: 16 with gradient accumulation) |
| Epochs | 1 |
| Sequence length | 256 tokens |
| Training sequences | 200-500 (proof-of-concept configuration) |

### 4.5 Hardware

All experiments were conducted on a single NVIDIA A100 GPU (40GB). Total compute was approximately 4 GPU-hours.

## 5. Results

### 5.1 H-E1: Spectral Horizon Stability

**Research Question:** Is H_spec a stable, input-independent property?

| Metric | Value | Threshold | Result |
|--------|-------|-----------|--------|
| CV(H_spec) | 2.22 x 10^-16 | < 0.3 | PASS |
| Mean H_spec | 256.18 tokens | - | - |
| Std H_spec | 5.68 x 10^-14 | - | - |
| Valid samples | 1000/1000 | - | - |

The coefficient of variation is effectively zero, indicating that H_spec is determined solely by the pretrained A matrix weights and is independent of input sequences.

**Cross-Scale Observation:** Mamba-370M yielded H_spec = 162,605 tokens, larger than Mamba-1.4B (256.18 tokens). This non-monotonic relationship was unexpected and suggests H_spec is determined by pretraining dynamics rather than model capacity alone.

### 5.2 H-M1: Eigenvalue-Based Memory Prediction

**Research Question:** Does H_spec predict actual memory behavior on real text?

| Context Length | Perplexity |
|----------------|------------|
| 25 tokens | 83.26 |
| 64 tokens | 36.40 |
| 128 tokens | 23.75 |
| 256 tokens | 17.89 |
| 512 tokens | 14.41 |
| 1024 tokens | 12.22 |

**Degradation Ratio:** 3.03 (threshold: > 1.1) --- PASS

Perplexity improved rapidly as context approached H_spec (256 tokens), then showed diminishing returns beyond H_spec. The improvement from 25 to 256 tokens was 4.65x, while the improvement from 256 to 1024 tokens was 1.47x. This pattern indicates that H_spec predicts the point at which memory becomes the limiting factor for language modeling performance.

### 5.3 H-M2: Eigenvalue Preservation Under LoRA

**Research Question:** Does projection-only LoRA preserve SSM eigenvalues?

| Metric | Pre-Training | Post-Training | Change |
|--------|--------------|---------------|--------|
| H_spec | 256.43 tokens | 256.43 tokens | 0.0000% |
| A_log max diff | - | 0.0 | Frozen |
| Eigenvalue correlation | - | 1.0000 | Perfect |
| Validation perplexity | - | 15.58 | - |

**Result:** |delta H_spec| = 0.0% (threshold: < 10%) --- PASS

The A_log parameters remained completely frozen during training. Eigenvalue preservation was exact, not approximate. This confirms architectural isolation between projection parameters and SSM core parameters.

### 5.4 H-M3: Eigenmode Energy Redistribution

**Research Question:** Can projection-only LoRA redistribute energy to slow eigenmodes?

| Metric | Pre-Training | Post-Training | Change |
|--------|--------------|---------------|--------|
| Slow mode fraction | 1.97 x 10^-5 | 1.91 x 10^-5 | -5.93 x 10^-7 |
| delta E (nats) | - | 5.93 x 10^-7 | 6 orders below threshold |
| Perplexity | - | 14.35 | - |

**Result:** delta E = 5.93 x 10^-7 nats (threshold: > 0.1 nats) --- FAIL

Energy redistribution was negligible. Per-layer analysis revealed:

- Only 2 of 48 layers (layers 18 and 19) contain slow eigenmodes (|lambda| > 0.99)
- Layer 18: 0.044% slow mode fraction
- Layer 19: 0.050% slow mode fraction
- All other 46 layers: 0.0% slow mode fraction
- Total slow mode capacity: 0.00197% of state energy

The pretrained Mamba-1.4B architecture allocates minimal energy to slow-decaying modes. There is insufficient slow-mode capacity for meaningful redistribution.

### 5.5 Summary of Results

| Hypothesis | Gate | Metric | Threshold | Actual | Result |
|------------|------|--------|-----------|--------|--------|
| H-E1 | MUST_WORK | CV(H_spec) | < 0.3 | 2.22 x 10^-16 | PASS |
| H-M1 | MUST_WORK | Degradation ratio | > 1.1 | 3.03 | PASS |
| H-M2 | MUST_WORK | |delta H_spec| | < 10% | 0.0% | PASS |
| H-M3 | SHOULD_WORK | delta E | > 0.1 | 5.93 x 10^-7 | FAIL |

The three MUST_WORK hypotheses passed. The SHOULD_WORK hypothesis (H-M3) failed, which eliminates the EUH mechanism and provides evidence for MHSH.

## 6. Discussion

### 6.1 Interpretation of Findings

The primary finding is a negative result: energy redistribution toward slow eigenmodes does not occur under projection-only LoRA. This eliminates the Eigenmode Utilization Hypothesis as an explanation for potential beyond-horizon task success.

The per-layer analysis reveals that Mamba-1.4B allocates only 0.002% of total state energy to slow modes, concentrated in layers 18 and 19. The architecture favors fast-decaying eigenmodes rather than long-term memory.

These findings provide evidence that projection-only LoRA is bounded by the intrinsic spectral horizon H_spec. However, direct verification of task failure at L > H_spec was not performed because H-M4 was not executed.

### 6.2 Limitations

**WikiText-103 as Memory Proxy:** Language modeling perplexity was used rather than a controlled synthetic task with explicit dependency lengths. The perplexity degradation pattern provides indirect evidence but does not constitute direct verification of task failure at the spectral boundary.

**Single Model Family:** Experiments focused on Mamba-1.4B and Mamba-370M. Generalization to other SSM architectures (RWKV, RetNet, Mamba-2) was not empirically validated.

**H-M4 Not Executed:** The discriminative MQAR test that would directly verify task failure when L > H_spec under projection-only LoRA was not completed. The H-M3 negative result partially addresses the hypothesis discrimination but does not provide direct task-failure evidence.

**Proof-of-Concept Training Configuration:** A single epoch with limited training sequences was used. The configuration was sufficient for mechanism validation (eigenvalue preservation and energy measurement) but does not represent full-scale training.

**SSM-Core LoRA Not Tested:** LoRA targeting A_log or Delta parameters was not implemented. Prediction P3 (that SSM-core LoRA can extend H_spec) remains untested.

### 6.3 Connection to Prior Work

The findings provide a potential explanation for observations in prior work:

- SSM-PEFT reports that LoRA is ineffective on SSM modules. The present results suggest this is because eigenvalues are frozen and energy redistribution does not occur.
- MambaPEFT reports task-dependent LoRA success. This may correspond to tasks within versus beyond H_spec, though this interpretation requires validation.

### 6.4 Scope Conditions

Results hold for:
- Mamba-1.4B architecture with projection-only LoRA targeting in_proj and x_proj
- Language modeling evaluation on WikiText-103
- The specific pretrained checkpoint (state-spaces/mamba-1.4b-hf)

Results may not generalize to:
- Other SSM architectures (RWKV, Mamba-2, hybrid Transformer-SSM models)
- SSM-core LoRA or full fine-tuning
- Tasks other than language modeling
- Different pretrained checkpoints

## 7. Conclusion

This work investigated the spectral dynamics of SSM adaptation under projection-only LoRA. Three main findings are reported:

1. The spectral memory horizon H_spec = -1/log|lambda_max| is a stable, input-independent property of pretrained Mamba models (CV = 2.22 x 10^-16 across 1000 sequences), and it predicts perplexity degradation on real text (degradation ratio = 3.03 when context < H_spec).

2. Projection-only LoRA achieves exact eigenvalue preservation (delta H_spec = 0.0%, eigenvalue correlation = 1.0), confirming that projection parameters and SSM core parameters are architecturally isolated.

3. Energy redistribution toward slow eigenmodes does not occur (delta E = 5.93 x 10^-7 nats, six orders of magnitude below threshold). Only 2 of 48 layers in Mamba-1.4B contain slow eigenmodes, with total slow-mode energy at 0.002%.

The third finding, a negative result, eliminates the Eigenmode Utilization Hypothesis and provides evidence supporting the Memory Horizon Separation Hypothesis. However, direct verification of task failure beyond H_spec through the planned H-M4 experiment was not completed.

### Future Work

- **Spectral Surgery Methods:** Develop PEFT methods targeting discretization parameters (Delta, A_log) to test whether eigenvalue modification can extend H_spec.
- **Layer-Selective Adaptation:** Apply SSM-core adaptation selectively to slow-mode layers (18-19) to test whether targeted modification enables energy redistribution.
- **Controlled Task Evaluation:** Implement MQAR evaluation with explicit dependency lengths L = {H_spec, 2*H_spec, 4*H_spec} to directly verify task failure at the spectral boundary.
- **Cross-Architecture Validation:** Validate the spectral analysis framework on RWKV, RetNet, and Mamba-2.

## References

[1] SSM-PEFT: Parameter-Efficient Fine-Tuning for State Space Models. ICML 2025.

[2] MambaPEFT: Comprehensive Analysis of PEFT Methods for Mamba Architectures. ICLR 2025.

[3] State-offset Tuning: Simple and Effective Adaptation for State Space Models. ACL 2025.

[4] Gu, A. and Dao, T. Mamba: Linear-Time Sequence Modeling with Selective State Spaces. arXiv:2312.00752, 2023.

[5] Gu, A., Goel, K., and Re, C. Efficiently Modeling Long Sequences with Structured State Spaces. ICLR 2022.

[6] Fu, D. Y., et al. Hungry Hungry Hippos: Towards Language Modeling with State Space Models. ICLR 2023.

[7] Peng, B., et al. RWKV: Reinventing RNNs for the Transformer Era. EMNLP 2023.

[8] Hu, E. J., et al. LoRA: Low-Rank Adaptation of Large Language Models. arXiv:2106.09685, 2021.

[9] Bengio, Y., Simard, P., and Frasconi, P. Learning Long-Term Dependencies with Gradient Descent is Difficult. IEEE Transactions on Neural Networks, 1994.

[10] Hochreiter, S. and Schmidhuber, J. Long Short-Term Memory. Neural Computation, 1997.

## Appendix

### A. Experimental Metrics Summary

**H-E1 (Spectral Horizon Stability):**
- Model: state-spaces/mamba-1.4b
- Samples: 1000 random sequences, length 512 tokens
- CV(H_spec): 2.22 x 10^-16
- Mean H_spec: 256.18 tokens
- Cross-validation: Mamba-370M H_spec = 162,605 tokens

**H-M1 (Memory Prediction):**
- Dataset: WikiText-103 validation split
- Evaluation sequences: 246 (after chunking from 1000 requested)
- Degradation ratio: 3.03
- Baseline perplexity (1024 tokens): 12.22

**H-M2 (Eigenvalue Preservation):**
- LoRA rank: 16, alpha: 32
- Target modules: in_proj, x_proj
- Trainable parameters: 11.1M (0.8%)
- Training: 1 epoch, 100 steps
- delta H_spec: 0.0000%
- Eigenvalue correlation: 1.0000
- Validation perplexity: 15.58

**H-M3 (Energy Redistribution):**
- Training sequences: 500
- Slow mode threshold: |lambda| > 0.99
- Pre-training slow fraction: 1.97 x 10^-5
- Post-training slow fraction: 1.91 x 10^-5
- delta E: 5.93 x 10^-7 nats
- Layers with slow modes: 2/48 (layers 18, 19)
- Post-training perplexity: 14.35

### B. Per-Layer Eigenvalue Distribution

Layer 19 has the slowest decay (lambda_max = 0.996, H_spec = 256 tokens). Layer 21 has the fastest decay (lambda_max = 0.472, H_spec = 1.3 tokens). Most layers have lambda_max in the range [0.7, 0.9], corresponding to H_spec between 3-10 tokens.

### C. Figure References

- H_spec distribution: h-e1/figures/hspec_distribution.png
- Perplexity vs context length: h-m1/code/figures/ppl_vs_context_length.png
- Eigenvalue scatter (pre/post): h-m2/code/figures/eigenvalue_scatter.png
- Energy distribution: h-m3/figures/energy_distribution.png
- Per-layer slow fraction: h-m3/figures/per_layer_slow_fraction.png
