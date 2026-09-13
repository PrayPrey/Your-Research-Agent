# Experimental Setup

We design experiments to answer the following research questions:

**RQ1 (Superadditivity):** Is the Training×Refinement interaction positive? Does RL-Refine exceed the additive prediction from RL-Single and CE-Refine main effects?

**RQ2 (Mechanism):** Does RL training increase structural coupling I(F;E) between feedback and edits, controlling for edit length?

**RQ3 (Diversity):** Is high feedback diversity during training necessary for superadditivity?

## Datasets

We evaluate on two standard code generation benchmarks:

**HumanEval+** [Liu et al., 2024]: 164 handwritten Python programming problems with 80× more test cases than the original HumanEval benchmark. The rigorous test suite reduces false positives from solutions that pass original tests but fail on edge cases.

**MBPP+** [Liu et al., 2024]: 378 crowd-sourced Python programming problems with 35× more test cases than original MBPP. These represent entry-level programming tasks, providing complementary coverage to HumanEval+'s algorithmic focus.

| Dataset | Problems | Avg. Tests | Purpose |
|---------|----------|------------|---------|
| HumanEval+ | 164 | 128 | Algorithmic problems, rigorous evaluation |
| MBPP+ | 378 | 68 | Entry-level problems, statistical power |

Combined, 542 problems × 3 seeds provide sufficient power for detecting interaction effects in our GLMM.

## Baselines

Our 2×2 factorial design yields four conditions rather than explicit baselines:

| Condition | Training | Inference | Role |
|-----------|----------|-----------|------|
| CE-Single | Cross-entropy | Single-shot | Baseline (no treatment) |
| CE-Refine | Cross-entropy | K=3 refinement | Refinement main effect |
| RL-Single | RL + execution | Single-shot | Training main effect |
| RL-Refine | RL + execution | K=3 refinement | Combined treatment |

CE-Single serves as the reference condition. The interaction term measures whether RL-Refine exceeds the additive combination of the two main effects.

## Implementation Details

**Base Model:** CodeT5+-220M [Wang et al., 2023] from HuggingFace, an encoder-decoder model pretrained on CodeSearchNet across 6 programming languages. Zero-shot pass@1 on HumanEval is approximately 15%.

**Parameter-Efficient Fine-Tuning:** We apply LoRA [Hu et al., 2022] with rank r=16 targeting query, key, and value projection matrices (q_proj, k_proj, v_proj).

**Training Configuration:**
- Optimizer: AdamW
- Learning rate: 2e-5
- Weight decay: 0.05
- Warmup steps: 200
- Batch size: 8
- CE epochs: 10
- RL epochs: 5
- Seeds: 42, 43, 44

**RL Training:** REINFORCE algorithm with binary execution reward (1 if all tests pass, 0 otherwise). Gradient is computed as $\nabla_\theta J = R(a) \nabla_\theta \log \pi_\theta(a)$ where $a$ is the generated code.

**Refinement Protocol:** Self-Refine [Madaan et al., 2023] with K=3 iterations. Feedback prompt template: `[CODE]\n{code}\n[EXECUTION RESULT]\n{error_type}: {message}\n[REFINE]`. Greedy decoding (temperature 0) with max 512 tokens.

**Compute:** Single NVIDIA GPU; smoke tests complete in <1 hour; full experiments require GPU acceleration for practical runtime.

## Evaluation Metrics

**Primary Metric: pass@1** — Proportion of problems solved correctly on first sample. For refinement conditions, this is after up to K refinement iterations.

**Statistical Model:** Generalized linear mixed model with logit link:
$$\text{logit}(P(\text{pass})) = \beta_0 + \beta_T \cdot \text{Training} + \beta_R \cdot \text{Refinement} + \beta_{T \times R} \cdot \text{Training} \times \text{Refinement} + u_{\text{problem}}$$

**Success Criterion (RQ1):** Interaction coefficient $\beta_{T \times R} > 0$ with p < 0.05 and odds ratio ≥ 1.2.

**Mechanism Metric (RQ2):** Mutual information I(F;E) estimated via MINE [Belghazi et al., 2018] with 5000 training iterations and 10,000 permutations for significance testing. Edit length controlled via linear regression.

**Diversity Metric (RQ3):** Conditional entropy H(Schema|ErrorClass) for training batches, with high-diversity (H > 2.5 bits) and low-diversity (H < 1.5 bits) conditions.
