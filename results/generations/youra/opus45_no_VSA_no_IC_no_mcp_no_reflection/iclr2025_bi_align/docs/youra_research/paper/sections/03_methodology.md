# 3. Methodology

## 3.1 Problem Formulation

We formulate bidirectional alignment as multi-objective RLHF:

$$\max_\theta \mathbb{E}_{x \sim \mathcal{D}, y \sim \pi_\theta(\cdot|x)} \left[ R_{\text{combined}}(x, y) - \beta_{\text{KL}} D_{\text{KL}}(\pi_\theta \| \pi_{\text{ref}}) \right]$$

where:

$$R_{\text{combined}}(x, y) = \alpha \cdot R_{\text{help}}(x, y) + \beta \cdot R_{\text{ctrl}}(x, y)$$

The hyperparameters $\alpha, \beta \in \{0.2, 0.4, 0.6, 0.8\}$ control the trade-off between helpfulness and controllability objectives. We constrain $\alpha + \beta = 1$ to maintain a normalized reward scale.

## 3.2 IFEval as Differentiable Training Signal

IFEval defines 25 verifiable constraint types across four categories: format (e.g., "respond in JSON"), length (e.g., "use exactly 100 words"), keywords (e.g., "include the word 'conclusion'"), and structure (e.g., "use exactly 3 paragraphs").

The standard IFEval metric returns binary pass/fail for each constraint. Binary constraint checks are non-differentiable; we convert to continuous scores via sigmoid soft thresholds:

$$s_i = \sigma\left(\frac{v_i - t_i}{\tau}\right)$$

where $v_i$ is the measured value (e.g., word count), $t_i$ is the constraint threshold, $\tau$ is a temperature parameter controlling gradient sharpness, and $\sigma$ is the sigmoid function.

The controllability reward aggregates soft constraint scores across all applicable constraints:

$$R_{\text{ctrl}}(x, y) = \frac{1}{|C(x)|} \sum_{c_i \in C(x)} s_i$$

We validated gradient flow in H-E1: variance = 0.039 (sufficient for training signal), scale.grad = 274.12 (confirming backpropagation).

## 3.3 Helpfulness Reward

We use a reward model trained on AlpacaEval preference data to generate $R_{\text{help}}(x, y)$. The reward model follows the standard architecture from InstructGPT [1]: a pretrained language model with a scalar head predicting reward from the final token embedding.

## 3.4 Experimental Conditions

**Treatments (Bidirectional):**
- T1: α=0.2, β=0.8 (high controllability weight)
- T2: α=0.4, β=0.6 (balanced toward controllability)
- T3: α=0.6, β=0.4 (balanced toward helpfulness)
- T4: α=0.8, β=0.2 (high helpfulness weight)

**Baselines (Unidirectional):**
- B1: SFT-only (no RLHF)
- B2: Helpfulness-only RLHF (α=1.0, β=0.0)
- B3: Quality-filtered RLHF (preference data filtered by quality)

**Data Split:** IFEval prompts split 70/30 into training and held-out sets to prevent memorization. We evaluate on the 30% held-out set to measure generalization.

## 3.5 Training Configuration

- **Base model:** Llama-3-8B-Instruct
- **PPO steps:** 50-1000 (proof-of-concept scale)
- **Learning rate:** 1e-6
- **KL coefficient:** 0.1
- **Batch size:** 8
- **Seed:** 1 (single seed per NFR-2 PoC constraint)

## 3.6 Evaluation Protocol

We evaluate all checkpoints on four benchmarks using lm-evaluation-harness [14]:

1. **IFEval (held-out):** Strict accuracy on 30% held-out prompts
2. **AlpacaEval LC:** Length-controlled win rate vs reference
3. **TruthfulQA MC1:** Multiple-choice accuracy on truthfulness
4. **BBQ:** Accuracy on bias benchmark questions
