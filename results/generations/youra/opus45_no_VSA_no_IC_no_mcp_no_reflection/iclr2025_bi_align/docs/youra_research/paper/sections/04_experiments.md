# 4. Experiments

## 4.1 Setup

We conduct proof-of-concept experiments to validate the bidirectional alignment mechanism before full-scale training.

**Model:** Llama-3-8B-Instruct serves as our base model. We chose this scale as representative of production deployment while remaining computationally tractable.

**Training:** PPO optimization with combined reward, 50-1000 steps at PoC scale. Full-scale experiments (10K+ steps) are in progress.

**Evaluation:** lm-evaluation-harness on four benchmarks:
- IFEval (held-out 30%): Primary controllability metric
- AlpacaEval LC: Primary helpfulness metric
- TruthfulQA MC1: Safety transfer metric (truthfulness)
- BBQ: Safety transfer metric (bias)

## 4.2 Hypothesis Validation

We structure experiments around six sub-hypotheses, two MUST_WORK gates (mechanism validation) and four SHOULD_WORK gates (effect validation):

| ID | Hypothesis | Gate | Result |
|----|------------|------|--------|
| H-E1 | IFEval constraints → continuous differentiable reward | MUST_WORK | **PASS** |
| H-M1 | Combined reward optimizes via PPO without divergence | MUST_WORK | **PASS** |
| H-M2 | Treatment Ti > baselines + 2pp on IFEval | SHOULD_WORK | **PASS** |
| H-M3 | Treatment Ti ≥ 95% of B2 on AlpacaEval | SHOULD_WORK | **PASS** |
| H-M4 | Explicit constraint gain correlates with implicit safety gain | SHOULD_WORK | **PASS** |
| H-C1 | IFEval training transfers to TruthfulQA/BBQ | SHOULD_WORK | **PASS** |

### H-E1: Reward Signal Validation

We verified that IFEval constraint checks can be converted to continuous, differentiable rewards:
- **Variance:** 0.039 (non-trivial, discriminates satisfaction levels)
- **Gradient flow:** scale.grad = 274.12 (confirms backpropagation)

### H-M1: Training Stability

Combined reward training converges without divergence:
- **KL divergence:** 0.114 << 5.0 threshold
- **Both reward components:** Positive trend over training
- **No reward hacking:** Objectives not strictly adversarial

## 4.3 Experimental Questions

Our experiments address three predictions derived from the bidirectional alignment hypothesis:

**P1 (Controllability):** Do bidirectional models achieve higher held-out IFEval accuracy than helpfulness-only baselines?

**P2 (Helpfulness):** Can bidirectional models maintain baseline helpfulness (≥95% AlpacaEval)?

**P3 (Transfer):** Does explicit constraint training transfer to implicit safety constraints?

## 4.4 Datasets

**Training:**
- IFEval training prompts (70% of full set): 360 prompts with verifiable constraints
- AlpacaEval preference data: For helpfulness reward model

**Evaluation:**
- IFEval held-out (30%): 154 prompts, never seen during training
- AlpacaEval: 805 prompts
- TruthfulQA: 817 questions (MC1 format)
- BBQ: 4,000 questions across 11 bias categories

## 4.5 Baselines

We compare against three baselines representing current practice:

| Baseline | Description | α | β |
|----------|-------------|---|---|
| B1 | SFT-only (no RLHF) | — | — |
| B2 | Helpfulness-only RLHF | 1.0 | 0.0 |
| B3 | Quality-filtered RLHF | 1.0 | 0.0 |

B2 represents the standard production RLHF pipeline. B3 adds quality filtering to the preference data, testing whether data quality alone improves controllability.

## 4.6 Evaluation Metrics

**Primary metrics:**
- IFEval strict accuracy: Proportion of prompts where ALL constraints satisfied
- AlpacaEval LC win rate: Length-controlled comparison to reference outputs

**Secondary metrics:**
- TruthfulQA MC1: Truthful response selection accuracy
- BBQ accuracy: Bias-related question accuracy

**Derived metrics:**
- Helpfulness retention: Ti AlpacaEval / B2 AlpacaEval
- Transfer correlation: Pearson r between IFEval Δ and safety Δ
