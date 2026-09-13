# 3. Methodology

## 3.1 Problem Formulation

We formulate bidirectional alignment as multi-objective RLHF. Given a language model policy $\pi_\theta$, reference policy $\pi_{\text{ref}}$, and prompt distribution $\mathcal{D}$, we optimize:

$$\max_\theta \mathbb{E}_{x \sim \mathcal{D}, y \sim \pi_\theta(\cdot|x)} \left[ R_{\text{combined}}(x, y) - \beta_{\text{KL}} D_{\text{KL}}(\pi_\theta \| \pi_{\text{ref}}) \right]$$

where the combined reward is:

$$R_{\text{combined}}(x, y) = \alpha \cdot R_{\text{help}}(x, y) + \beta \cdot R_{\text{ctrl}}(x, y)$$

with $\alpha + \beta = 1$ controlling the helpfulness-controllability trade-off.

## 3.2 IFEval as Differentiable Training Signal

### 3.2.1 IFEval Constraint Types

IFEval [2] defines 25 verifiable constraint types including:
- **Format constraints:** JSON output, bullet lists, numbered sections
- **Length constraints:** minimum/maximum words, sentences, paragraphs
- **Keyword constraints:** include/exclude specific words
- **Structural constraints:** title case, specific endings

Each prompt $x$ specifies constraints $C(x) = \{c_1, ..., c_k\}$. Standard IFEval produces binary pass/fail per constraint.

### 3.2.2 Soft Threshold Conversion

Binary constraint checks are non-differentiable. We convert to continuous scores via sigmoid soft thresholds. For constraint $c_i$ with target $t_i$ and observed value $v_i$:

$$s_i = \sigma\left(\frac{v_i - t_i}{\tau}\right)$$

where $\tau$ is a temperature parameter controlling sharpness. For constraints requiring exact matches (keywords, format), we use fuzzy matching with soft penalties:

$$s_i = 1 - \frac{d_{\text{edit}}(v_i, t_i)}{\max(|v_i|, |t_i|) + \epsilon}$$

### 3.2.3 Aggregated Controllability Reward

The controllability reward aggregates soft constraint scores:

$$R_{\text{ctrl}}(x, y) = \frac{1}{|C(x)|} \sum_{c_i \in C(x)} s_i$$

This produces a continuous $[0, 1]$ score suitable for gradient-based optimization.

### 3.2.4 Gradient Flow Validation

We validated gradient flow in our existence proof (H-E1). The IFEvalRewardSignal module produces:
- Variance = 0.039 (non-trivial discrimination)
- Valid `backward()` execution with `scale.grad = 274.12`
- Score range $[0, 1]$ as required

## 3.3 Combined Reward Integration

### 3.3.1 Reward Model Architecture

Our CombinedRewardModel wraps two components:

```
CombinedRewardModel:
  R_help: DeBERTa-based helpfulness reward (standard RLHF)
  R_ctrl: IFEvalRewardSignal (§3.2)
  α, β: Weight parameters
  
  forward(prompt, response):
    r_help = self.R_help(prompt, response)
    r_ctrl = self.R_ctrl(prompt, response)
    return α * r_help + β * r_ctrl
```

### 3.3.2 PPO Integration

We use standard PPO [13] with the combined reward:
- **Batch size:** 8
- **Learning rate:** 1.41e-5
- **KL coefficient:** 0.05
- **KL target:** 0.1

The KL penalty prevents excessive deviation from the reference policy, mitigating reward hacking identified by Gao et al. [9].

## 3.4 Experimental Conditions

### 3.4.1 Treatment Configurations

We sweep α/β weights across four treatment conditions:

| Config | α (helpfulness) | β (controllability) |
|--------|-----------------|---------------------|
| T1 | 0.2 | 0.8 |
| T2 | 0.4 | 0.6 |
| T3 | 0.6 | 0.4 |
| T4 | 0.8 | 0.2 |

### 3.4.2 Baseline Conditions

| Config | Description | Reward |
|--------|-------------|--------|
| B1 | SFT-only | No RLHF |
| B2 | Helpfulness RLHF | $R_{\text{help}}$ only |
| B3 | Quality RLHF | Response quality (no instruction adherence) |

### 3.4.3 Data Split

We split IFEval 70/30:
- **Training (70%):** Prompts used for $R_{\text{ctrl}}$ computation
- **Held-out (30%):** ~162 prompts for evaluation

This prevents memorization and tests generalization to unseen constraint instances.

## 3.5 Evaluation Metrics

| Metric | Benchmark | Measures |
|--------|-----------|----------|
| IFEval Strict | IFEval test | All constraints satisfied |
| IFEval Loose | IFEval test | Any constraint satisfied |
| AlpacaEval LC | AlpacaEval | Helpfulness (length-controlled) |
| TruthfulQA MC1 | TruthfulQA | Truthfulness (single answer) |
| TruthfulQA MC2 | TruthfulQA | Truthfulness (multiple valid) |
| BBQ | BBQ | Bias in question answering |

All evaluations use lm-evaluation-harness [14] for reproducibility.
