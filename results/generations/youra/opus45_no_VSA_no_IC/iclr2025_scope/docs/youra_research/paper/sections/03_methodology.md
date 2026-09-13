# Methodology

## Experimental Design

We design experiments to test whether optimal LoRA rank $r_{\text{opt}}$ scales sub-linearly with model size $N$, following the relationship $r_{\text{opt}} \propto N^\alpha$ where $\alpha \in (0, 1)$.

### Model Selection

We use the Pythia model family [@biderman2023pythia] spanning four scales: 1B, 2.8B, 6.9B, and 12B parameters. Pythia provides identical architecture (GPT-style autoregressive transformer) across scales, eliminating architecture confounds. All models use the same vocabulary, tokenizer, and pre-training corpus (The Pile).

### LoRA Configuration

Following standard practice, we apply LoRA to query and value projection matrices (Q, V) with:
- **Ranks**: $r \in \{4, 8, 16, 32, 64, 128\}$
- **Scaling**: $\alpha = 2r$ (rsLoRA convention)
- **Target modules**: `query_key_value` (Pythia's fused QKV)
- **Dropout**: 0.05

### Task Selection

We evaluate on two QA task types to test cross-task consistency:
- **SQuAD-v2** [@rajpurkar2018squad]: Single-hop extractive QA, 11,873 validation examples
- **HotpotQA** [@yang2018hotpotqa]: Multi-hop reasoning, 7,405 validation examples

### Training Protocol

- **Optimizer**: AdamW with $\beta_1=0.9$, $\beta_2=0.999$
- **Learning rate**: $10^{-4}$ with linear warmup (6% of steps)
- **Epochs**: 3
- **Batch size**: 16 (gradient accumulation as needed)
- **Seeds**: 3 per configuration (42, 1337, 2024)

## Sub-Hypotheses

We decompose the main hypothesis into four testable sub-hypotheses:

### h-e1: Existence (MUST_WORK)
*Log-linear regression of $r_{\text{opt}}$ vs $N$ yields scaling exponent $\alpha \in (0.3, 0.7)$ with 95% CI excluding both 0 and 1.*

**Success criterion**: 95% confidence interval for $\alpha$ has lower bound > 0 and upper bound < 1.

### h-m1: Mechanism (SHOULD_WORK)
*Attention entropy at optimal rank correlates positively with model size (Pearson $r > 0.6$, $p < 0.05$).*

**Rationale**: Sub-linear scaling may arise from entropy-based capacity utilization.

### h-m2: Phase Transition (MUST_WORK)
*Rank sensitivity ($\partial \text{accuracy} / \partial \log r$) is >2× higher at 12B vs 1B.*

**Success criterion**: Sensitivity ratio > 2.0 with bootstrap CI lower bound > 1.5.

### h-c1: Consistency (SHOULD_WORK)
*Scaling exponent $\alpha$ is consistent across single-hop and multi-hop QA: $|\Delta\alpha| \leq 0.15$.*

**Rationale**: A useful scaling law should generalize across related tasks.

## Optimal Rank Determination

We define optimal rank as the smallest rank achieving 99% of rank-128 performance:

$$r_{\text{opt}} = \min\{r : \text{F1}(r) \geq 0.99 \cdot \text{F1}(128)\}$$

This threshold balances efficiency (smaller rank) with performance retention.

## Scaling Law Estimation

We fit the log-linear relationship:

$$\log(r_{\text{opt}}) = \alpha \cdot \log(N) + \beta$$

using ordinary least squares with bootstrap confidence intervals (B=1000 resamples). The scaling exponent $\alpha$ indicates:
- $\alpha = 0$: constant rank (no scaling)
- $\alpha = 1$: linear scaling
- $\alpha \in (0, 1)$: sub-linear scaling (our hypothesis)

## Attention Entropy Measurement

For mechanism analysis (h-m1), we compute attention entropy at layer $L/2$:

$$H = -\sum_{i,j} A_{ij} \log A_{ij}$$

where $A$ is the attention matrix. We measure entropy at model initialization to isolate the effect of pre-trained representations.
