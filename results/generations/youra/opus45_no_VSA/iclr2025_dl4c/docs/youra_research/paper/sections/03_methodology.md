# Methodology

Building on our observation that RL training and test-time refinement both leverage execution feedback but have never been combined systematically, we design a factorial experimental framework to measure their interaction and probe the underlying mechanism.

## Overview

Our approach consists of three components: (1) a 2×2 factorial design that isolates the Training×Refinement interaction, (2) a mutual information metric I(F;E) that quantifies feedback-edit coupling, and (3) a diversity manipulation infrastructure that enables ablation studies. We describe each component's design rationale and implementation.

## 2×2 Factorial Design

We cross two factors:

- **Training type:** Cross-entropy (CE) fine-tuning vs. RL fine-tuning with execution rewards (REINFORCE)
- **Inference mode:** Single-shot generation vs. K-step refinement (Self-Refine protocol, K=3)

This yields four conditions:

| Condition | Training | Inference |
|-----------|----------|-----------|
| CE-Single | Cross-entropy | Single-shot |
| CE-Refine | Cross-entropy | K=3 refinement |
| RL-Single | RL + execution | Single-shot |
| RL-Refine | RL + execution | K=3 refinement |

**Rationale:** Factorial design separates main effects from interaction. The interaction term---whether RL-Refine exceeds what CE-Refine and RL-Single would predict additively---directly tests our hypothesis of superadditivity.

**Statistical model:** We fit a generalized linear mixed model (GLMM) with logit link:

$$\text{logit}(P(\text{pass})) = \beta_0 + \beta_T \cdot \text{Training} + \beta_R \cdot \text{Refinement} + \beta_{T \times R} \cdot \text{Training} \times \text{Refinement} + u_{\text{problem}}$$

where $u_{\text{problem}}$ is a random effect capturing problem-level difficulty. Our success criterion is $\beta_{T \times R} > 0$ with $p < 0.05$ and odds ratio $\geq 1.2$.

## Mutual Information Metric: I(F;E)

To probe *why* interaction effects occur, we measure structural coupling between feedback and edits.

**Definition:** I(F;E) is the mutual information between feedback embeddings F and edit embeddings E, where:
- F = embedding of feedback tokens (error messages, test outputs)
- E = embedding of edit spans (diff between original and refined code)

**Rationale:** If RL training induces a feedback-conditioned edit policy, we expect I(F;E)_RL > I(F;E)_CE. Higher mutual information indicates tighter alignment between what the feedback mentions and where the model edits.

**Implementation:** We use the MINE neural estimator [Belghazi et al., 2018], which provides the Donsker-Varadhan lower bound on mutual information:

$$I(F;E) \geq \sup_{\theta} \mathbb{E}_{p(f,e)}[T_\theta(f,e)] - \log \mathbb{E}_{p(f)p(e)}[e^{T_\theta(f,e)}]$$

where $T_\theta$ is a neural network (2-layer MLP, hidden dim 512). We train for 5000 iterations and use 10,000 permutations for significance testing.

**Control:** We regress out edit length to ensure MI differences are not artifacts of RL producing longer edits:

$$I(F;E)_{\text{controlled}} = I(F;E) - \hat{\beta} \cdot \text{edit\_length}$$

## Feedback Diversity Controller

To test whether diversity is necessary for superadditivity, we manipulate training feedback entropy.

**Definition:** Feedback diversity is measured via conditional entropy H(Schema | ErrorClass), where Schema is the feedback structure (variable names, line numbers) and ErrorClass ∈ {CompileError, RuntimeError, FailedTest, PassedTest}.

**Implementation:** FeedbackDiversityController filters training batches to achieve target entropy:
- High diversity: H > 2.5 bits (uniform distribution over schemas within each error class)
- Low diversity: H < 1.5 bits (concentrated distribution, few schema variants)

**Achieved separation:** H_high = 2.0 bits, H_low = 0.9 bits (1.1-bit difference), enabling controlled ablation.

## Model and Training

**Base model:** CodeT5+-220M [Wang et al., 2023], an encoder-decoder model pretrained on CodeSearchNet across 6 programming languages.

**CE training:** Standard causal language modeling on HumanEval+ problems with teacher forcing.

**RL training:** REINFORCE with execution reward:
$$\nabla_\theta J = \mathbb{E}_{a \sim \pi_\theta}[R(a) \nabla_\theta \log \pi_\theta(a)]$$

where $R(a) = 1$ if generated code passes all tests, 0 otherwise. We apply LoRA [Hu et al., 2022] with rank 16 for parameter-efficient fine-tuning.

**Hyperparameters:** Learning rate 2e-5, weight decay 0.05, warmup 200 steps, batch size 8, CE epochs 10, RL epochs 5.

## Refinement Protocol

We implement Self-Refine [Madaan et al., 2023] adapted for code generation:

1. Generate initial code from prompt
2. Execute against test cases
3. If fail: construct feedback prompt with error message
4. Generate refined code
5. Repeat steps 2-4 for K=3 iterations or until pass

**Feedback format:** `[CODE]\n{code}\n[EXECUTION RESULT]\n{error_type}: {error_message}\n[REFINE]`

## Evaluation

**Benchmarks:** HumanEval+ (164 problems) and MBPP+ (378 problems) from EvalPlus [Liu et al., 2024], providing 80× and 35× more test cases respectively than original benchmarks.

**Metric:** pass@1---proportion of problems solved correctly on first sample (after any refinement iterations). We report both per-condition pass@1 and the interaction effect $\hat{\beta}_{T \times R}$.
