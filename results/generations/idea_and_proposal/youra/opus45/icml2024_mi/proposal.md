# Research Proposal: Prospect Theory Value Layers for Human-AI Alignment: Modeling Cognitive Biases in RLHF Reward Models

## 1. Introduction

### 1.1 Background

Reinforcement Learning from Human Feedback (RLHF) has emerged as the dominant paradigm for aligning large language models (LLMs) with human preferences and values. This approach relies on training reward models from human preference annotations, which then guide policy optimization to produce outputs that humans find helpful, harmless, and honest. Despite remarkable empirical success in systems like ChatGPT and Claude, RLHF rests on a fundamentally flawed assumption: that human annotators provide rational, unbiased feedback that accurately reflects their true preferences.

Decades of research in behavioral economics and cognitive psychology have conclusively demonstrated that human decision-making systematically deviates from rational choice theory. Kahneman and Tversky's seminal work on Prospect Theory (1979, 1992) established that humans exhibit predictable cognitive biases when evaluating outcomes, including: (1) **loss aversion**, where losses are weighted approximately 2.25 times more heavily than equivalent gains; (2) **diminishing sensitivity**, where the subjective impact of changes decreases as one moves further from a reference point; and (3) **reference dependence**, where evaluations are made relative to context-dependent reference points rather than absolute values.

Current RLHF implementations ignore these well-documented biases entirely. The standard Bradley-Terry model used for preference prediction assumes that the probability of preferring response A over response B depends only on their respective reward values through a simple logistic function: $P(A \succ B) = \sigma(r_A - r_B)$. This formulation implicitly assumes linear utility and symmetric treatment of gains and losses—assumptions that prospect theory explicitly rejects.

This disconnect between how humans actually evaluate AI outputs and how reward models predict preferences creates systematic misspecification. When annotators compare two LLM responses, they likely exhibit the same cognitive biases observed in other evaluation contexts: overweighting perceived "failures" or "harms" (loss aversion), showing reduced sensitivity to quality differences at extreme ends of the spectrum (diminishing sensitivity), and anchoring their judgments to contextual reference points. By failing to model these biases, current reward models learn distorted representations of human preferences, leading to suboptimal policy alignment.

### 1.2 Research Objectives

This research proposes to bridge behavioral economics and AI alignment by integrating prospect theory into RLHF reward models. Our primary objectives are:

1. **Develop the Prospect Theory Value Layer (PTVL)**: Design and implement a differentiable transformation layer that applies prospect theory's value function to reward model outputs before computing preference probabilities.

2. **Validate the mechanism**: Demonstrate that learned PTVL parameters converge to psychologically plausible ranges, providing evidence that the transformation captures genuine cognitive biases in human annotation.

3. **Quantify alignment improvements**: Measure improvements in preference prediction accuracy and downstream policy quality compared to standard RLHF baselines.

4. **Isolate bias contributions**: Through systematic ablation studies, determine the relative contributions of loss aversion versus diminishing sensitivity to alignment improvements.

### 1.3 Significance

This research addresses a critical gap in human-AI alignment methodology. If successful, it will:

- **Establish a principled framework** for incorporating human cognitive biases into reward modeling, moving beyond ad-hoc solutions to a theoretically grounded approach.
- **Improve alignment quality** by reducing reward model misspecification, leading to policies that better reflect actual human preferences.
- **Validate cross-domain transfer** of prospect theory from monetary gambles to subjective text quality evaluation, extending behavioral economics into AI alignment.
- **Provide diagnostic tools** for understanding how cognitive biases manifest in preference annotation, informing better data collection practices.

## 2. Methodology

### 2.1 Prospect Theory Value Layer Architecture

#### 2.1.1 Mathematical Formulation

The core innovation is the Prospect Theory Value Layer (PTVL), which transforms raw reward model outputs using prospect theory's value function. For a reward value $r$ and reference point $r_{ref}$, the transformed value is:

$$v(r, r_{ref}) = \begin{cases} (r - r_{ref})^\alpha & \text{if } r \geq r_{ref} \\ -\lambda (r_{ref} - r)^\beta & \text{if } r < r_{ref} \end{cases}$$

where:
- $\alpha \in (0, 1)$ controls diminishing sensitivity for gains
- $\beta \in (0, 1)$ controls diminishing sensitivity for losses
- $\lambda > 1$ captures loss aversion (losses weighted more heavily than gains)
- $r_{ref}$ is the reference point against which outcomes are evaluated

For pairwise preference prediction between responses $A$ and $B$ with raw rewards $r_A$ and $r_B$, we define the reference point as the mean: $r_{ref} = \frac{r_A + r_B}{2}$. The preference probability is then computed using the Bradley-Terry model with transformed values:

$$P(A \succ B) = \sigma(v(r_A, r_{ref}) - v(r_B, r_{ref}))$$

where $\sigma(\cdot)$ is the sigmoid function.

#### 2.1.2 Differentiability and Gradient Flow

To ensure end-to-end trainability, we handle the non-differentiability at $r = r_{ref}$ using a smooth approximation. For numerical stability, we implement:

$$v(r, r_{ref}) = \text{sign}(r - r_{ref}) \cdot |r - r_{ref} + \epsilon|^{\gamma(r, r_{ref})} \cdot \lambda^{\mathbb{1}[r < r_{ref}]}$$

where $\gamma(r, r_{ref}) = \alpha \cdot \mathbb{1}[r \geq r_{ref}] + \beta \cdot \mathbb{1}[r < r_{ref}]$ and $\epsilon = 10^{-6}$ ensures numerical stability.

#### 2.1.3 Parameter Learning with Regularization

The PTVL parameters $\theta_{PT} = \{\alpha, \beta, \lambda\}$ are learnable but regularized toward psychologically established priors:

$$\mathcal{L}_{reg} = \gamma_\alpha (\alpha - 0.88)^2 + \gamma_\beta (\beta - 0.88)^2 + \gamma_\lambda (\lambda - 2.25)^2$$

The total loss combines preference prediction loss with regularization:

$$\mathcal{L}_{total} = \mathcal{L}_{BCE} + \mu \mathcal{L}_{reg}$$

where $\mathcal{L}_{BCE}$ is binary cross-entropy loss on preference predictions and $\mu$ controls regularization strength.

### 2.2 Data Collection and Preprocessing

#### 2.2.1 Primary Dataset

We use the **HH-RLHF dataset** (Anthropic) as our primary benchmark, containing approximately 170,000 human preference comparisons between LLM responses. This dataset is chosen for:
- Large scale and diversity of annotators (crowdsourced)
- Standard benchmark status enabling comparison with prior work
- Availability of both "helpful" and "harmless" subsets

#### 2.2.2 Secondary Validation Dataset

For generalization testing, we use **OpenAssistant Conversations**, which provides preference rankings with different annotator demographics and annotation guidelines.

#### 2.2.3 Data Splits

- Training: 80% of preference pairs
- Validation: 10% for hyperparameter tuning
- Test: 10% held out for final evaluation
- Consistent random seed (42) across all experiments

### 2.3 Experimental Design

#### 2.3.1 Model Architecture

**Base Reward Model**: Llama-2-7B with a linear reward head, following standard RLHF practice. The reward head projects the final hidden state to a scalar reward value.

**PTVL Integration**: The PTVL is inserted between the reward head output and the preference probability computation:

```
Input → Llama-2-7B → Reward Head → PTVL → Bradley-Terry → Preference Probability
```

#### 2.3.2 Training Protocol

1. **Stage 1 - Reward Model Pretraining**: Train base reward model for 3 epochs using standard Bradley-Terry loss
2. **Stage 2 - PTVL Fine-tuning**: Initialize PTVL parameters from psychological priors and fine-tune end-to-end for 2 additional epochs
3. **Stage 3 - Policy Optimization**: Use PPO with the PTVL-enabled reward model to fine-tune a policy LLM

**Hyperparameters**:
- Learning rate: $3 \times 10^{-5}$ (reward model), $1 \times 10^{-4}$ (PTVL parameters)
- Batch size: 32 preference pairs
- Regularization weight $\mu$: 0.1 (tuned on validation set)
- PPO clip ratio: 0.2
- KL penalty coefficient: 0.1

#### 2.3.3 Experimental Conditions

We evaluate five conditions across 20 random seeds each:

| Condition | Description | Parameters |
|-----------|-------------|------------|
| **Baseline** | Standard Bradley-Terry | None |
| **PTVL-Fixed** | PTVL with fixed psychological parameters | $\alpha=\beta=0.88$, $\lambda=2.25$ |
| **PTVL-Learned** | PTVL with learnable parameters + regularization | Initialized from priors |
| **Loss-Only** | Only loss aversion component | $\alpha=\beta=1$, $\lambda$ learnable |
| **Sensitivity-Only** | Only diminishing sensitivity | $\alpha, \beta$ learnable, $\lambda=1$ |

#### 2.3.4 Comparison Baselines

Beyond the standard Bradley-Terry baseline, we compare against:
- **R³M (Robust Reward Model)**: Handles annotation noise through ensemble methods
- **DRO-RLHF**: Distributionally robust optimization for preference learning

### 2.4 Evaluation Metrics

#### 2.4.1 Primary Metric: Preference Prediction Accuracy

$$\text{Accuracy} = \frac{1}{N}\sum_{i=1}^{N} \mathbb{1}[\hat{y}_i = y_i]$$

where $\hat{y}_i$ is the predicted preference and $y_i$ is the ground truth.

**Success Criterion**: Accuracy improvement > 2% over baseline with $p < 0.05$ (paired t-test).

#### 2.4.2 Secondary Metrics

**Parameter Convergence (Mechanism Validation)**:
- Track learned $\alpha$, $\beta$, $\lambda$ across training
- Success: $\lambda \in [1.5, 3.0]$, $\alpha, \beta \in [0.5, 1.0]$

**Policy Win Rate**:
- Generate 500 response pairs using baseline and PTVL-trained policies
- Evaluate using GPT-4 as judge with randomized presentation order
- Success: Win rate > 55% for PTVL policy

**Calibration**: Expected Calibration Error (ECE) to assess whether predicted probabilities match empirical frequencies.

#### 2.4.3 Statistical Analysis

- **Effect Size**: Cohen's d for accuracy differences
- **Confidence Intervals**: 95% CI via bootstrap (1000 resamples)
- **Multiple Comparison Correction**: Bonferroni correction for 3 primary predictions
- **Power Analysis**: n=20 seeds provides 80% power to detect medium effect (d=0.5) at $\alpha=0.05$

### 2.5 Ablation Studies

To isolate the contributions of different PTVL components:

1. **Loss Aversion Ablation**: Compare PTVL-Learned vs. Sensitivity-Only to quantify loss aversion contribution
2. **Diminishing Sensitivity Ablation**: Compare PTVL-Learned vs. Loss-Only to quantify sensitivity contribution
3. **Reference Point Ablation**: Compare mean reference vs. alternatives (min, max, learned)
4. **Regularization Ablation**: Vary $\mu \in \{0, 0.01, 0.1, 1.0\}$ to assess prior importance

### 2.6 Implementation Details

**Computational Resources**: 8× NVIDIA A100 GPUs (80GB)
**Framework**: PyTorch with HuggingFace Transformers
**Training Time**: ~24 hours for reward model, ~48 hours for policy optimization
**Code**: Will be released upon publication

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

**Primary Outcome (P1)**: We expect PTVL-Learned to achieve preference prediction accuracy of 72-75% compared to 68-70% for the baseline, representing a >2% absolute improvement. This improvement should be statistically significant ($p < 0.05$) across 20 random seeds.

**Mechanism Validation (P2)**: We predict learned parameters will converge to:
- $\lambda \in [1.8, 2.5]$, confirming loss aversion in text quality evaluation
- $\alpha, \beta \in [0.75, 0.95]$, confirming diminishing sensitivity
- Low variance across seeds, indicating stable learning

**Downstream Impact (P3)**: PTVL-trained policies should achieve 57-62% win rate against baseline policies in GPT-4 evaluation, demonstrating that improved preference prediction translates to better alignment.

**Ablation Insights**: We anticipate loss aversion will contribute more to improvements than diminishing sensitivity, as "harmful" or "unhelpful" responses likely trigger stronger negative reactions from annotators.

### 3.2 Potential Negative Results and Contingencies

If the hypothesis is not supported:
- **Parameter divergence**: If $\lambda \leq 1$, this suggests loss aversion does not transfer to text evaluation; we would explore domain-specific bias formulations
- **No accuracy improvement**: If accuracy ≤ baseline, this indicates prospect theory's functional form is inappropriate; we would investigate alternative behavioral models (e.g., satisficing, regret theory)
- **High variance**: If parameters vary significantly across seeds, this suggests individual annotator differences dominate; we would develop hierarchical extensions

### 3.3 Scientific Impact

This research will:

1. **Establish a new research direction** at the intersection of behavioral economics and AI alignment, opening opportunities for incorporating other cognitive biases (anchoring, framing effects, temporal discounting)

2. **Provide empirical evidence** for or against the transfer of prospect theory to subjective evaluation domains, contributing to behavioral economics literature

3. **Offer practical improvements** to RLHF pipelines that can be adopted by practitioners with minimal computational overhead

4. **Develop diagnostic tools** for understanding annotator behavior, informing better annotation guidelines and quality control

### 3.4 Broader Impact

**For AI Safety**: Better modeling of human biases leads to more accurate reward models, reducing the risk of reward hacking and misalignment. Understanding how cognitive biases affect feedback can inform the design of safer annotation protocols.

**For Human-AI Collaboration**: Recognizing that humans provide biased feedback enables systems to appropriately weight and interpret human input, leading to more effective collaboration.

**Limitations and Risks**: Population-level parameters may not capture individual variation; learned biases could potentially be exploited to manipulate user preferences. We will discuss these limitations and recommend safeguards in our publication.

### 3.5 Timeline

- **Months 1-2**: Implementation and validation of PTVL architecture
- **Months 3-4**: Reward model experiments and ablation studies
- **Months 5-6**: Policy optimization experiments and GPT-4 evaluation
- **Month 7**: Analysis, paper writing, and code release

This research represents a principled step toward acknowledging and modeling human irrationality in AI alignment systems, moving beyond the convenient fiction of rational annotators toward a more realistic and effective approach to human-AI alignment.