# 4. Experimental Setup

We design experiments to answer three research questions:

**RQ1:** Is the structural efficiency measurement framework functionally correct?
Can it execute end-to-end on real model checkpoints and produce interpretable metrics?

**RQ2:** Do GRPO and DPO exhibit different Semantic Edit Proportions (SEP)
under KL-matched conditions? Does execution reward selectively concentrate
policy movement on semantic AST nodes?

**RQ3:** What confounds affect checkpoint-comparison studies of RL fine-tuning,
and how can they be detected and prevented?

These questions map directly to the Introduction's contributions: RQ1 validates
the framework; RQ2 tests the core hypothesis; RQ3 documents methodological lessons.

## 4.1 Datasets

We evaluate on two standard function-level code generation benchmarks:

| Dataset | Problems | Language | Source |
|---------|----------|----------|--------|
| HumanEval+ | 164 | Python | evalplus [Liu et al., 2023] |
| MBPP+ | 378 | Python | evalplus [Liu et al., 2023] |

**Rationale:** HumanEval+ and MBPP+ are the canonical benchmarks used by all
referenced baselines (CodeRL, TÜLU 3, CodeRL+, DeepSeek-Coder), enabling
comparison with prior work. Their structured nature — Python functions with
explicit input/output contracts and test suites — makes AST analysis
well-defined. The evalplus harness provides reliable execution-based evaluation.
We use evalplus's stricter test augmentation (+ variants) throughout.

## 4.2 Model

**Base model:** DeepSeek-Coder-7B-instruct-v1.5 (`deepseek-ai/deepseek-coder-7b-instruct-v1.5`,
HuggingFace). This model is a decoder-only code-specialized transformer at 7B
scale with permissive license, representing the state-of-the-art open-weight
code LLM family. Using the instruct-tuned variant as the starting point for
post-training is consistent with standard practice [Lambert et al., 2024].

## 4.3 Alignment Methods (Conditions)

We compare three post-training conditions, all starting from the same base model:

| Condition | Method | Reward Signal |
|-----------|--------|---------------|
| GRPO-binary | TRL GRPOTrainer | +1.0 (pass) / 0.0 (fail) |
| GRPO-error-type | TRL GRPOTrainer | Error taxonomy reward (SyntaxError=0.1, RuntimeError=0.3, AssertionError=0.7, pass=1.0) |
| DPO | TRL DPOTrainer | Execution-oracle preference pairs (passing solution preferred over failing) |

**Control variables:** Identical base model, identical training problems
(CodeAlpaca/OSS-Instruct subset), identical compute budget (1000 training steps),
KL penalty matching (GRPO $\beta=0.04$, DPO $\beta=0.1$, tuned to produce
comparable KL trajectories), and identical evaluation harness.

## 4.4 Execution

**Sub-experiment h-e1 (Proof-of-Concept, RQ1):** A smoke test to verify the
measurement infrastructure. Executed on 6 HumanEval+ problems with synthetic
GRPO and DPO code completions (hand-crafted to have known structural properties),
confirming that AST edit distance, KL matching, and bootstrap CI execute correctly.

**Sub-experiment h-m1 (Mechanism Analysis, RQ2):** Full structural analysis
on KL-matched checkpoint pairs from GRPO and DPO training. Intended to use
27 matched pairs from 10+ distinct checkpoints. Due to checkpoint aliasing
(see Section 5.3), effective sample size was $n_\text{eff} \approx 2$.
Results are reported as preliminary.

## 4.5 Evaluation Metrics

**Primary (framework diagnostic):**
- **Semantic Edit Proportion (SEP):** Fraction of edits targeting CF+DF nodes (Section 3.2)
- **Semantic edit distance:** ZSS edit distance restricted to CF+DF nodes (Section 3.3)
- **Structural efficiency:** Semantic edit distance per unit KL divergence (Section 3.1)

**Statistical tests:**
- Mann-Whitney U test on SEP distributions (significance threshold $\alpha = 0.05$)
- Bootstrap 95% CI on mean SEP differential (10,000 samples)

**Secondary (training confirmation):**
- Pass@1 on HumanEval+ and MBPP+ — used only to confirm training progressed,
  not as the primary comparison metric.

## 4.6 Compute Resources

Experiments run on NVIDIA H100 NVL (95,830 MiB), single GPU per run.
Conda environment `youra-h-e1` and `youra-h-m1` (Python 3.10, PyTorch,
TRL v1.3.0, evalplus, zss, tree-sitter).
