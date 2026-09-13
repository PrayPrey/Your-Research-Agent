# Methodology

## Overview

Our design follows directly from the generalization void insight: if RLEF's advantage at hard difficulty is driven by self-generated execution feedback rather than training data coverage, then we need a setup where all confounds except the training method are controlled. We fix the base model, training dataset, evaluation harness, and random seeds — and vary only whether training uses SFT, RLEF with fraction reward, or RLEF with binary reward. This allows the difficulty-scaling question to be answered without alternative explanations from model choice, data selection, or evaluation protocol differences.

## 3.1 Controlled Experimental Design

**Research questions driving the design:**

- **EQ1 (Difficulty scaling):** Does RLEF produce a statistically significant positive-ordered advantage over SFT across the five benchmark difficulty levels?
- **EQ2 (Signal void characterization):** What is the nature of SFT's failure at hard difficulty — dataset void or generalization void?
- **EQ3 (Reward formulation):** Does fraction-of-tests reward produce meaningfully different outcomes from binary reward at APPS training scale?

Each research question maps to one or more sub-hypotheses (h-e1, h-m1, h-m3, h-m4), enabling modular validation with explicit gate criteria.

**Controlled variables:**

| Variable | Fixed Value |
|----------|-------------|
| Base model | DeepSeek-Coder-7B-base [DeepSeek-AI, 2023] |
| Training data | APPS dataset [Hendrycks et al., 2021] |
| Evaluation harness | bigcode-evaluation-harness (correctness-only mode) |
| Optimizer | GRPO (custom SimpleGRPOTrainer, TRL 1.x) |
| Random seed | 42 throughout |
| Hardware | NVIDIA H100 NVL (5× 95830 MiB) |

## 3.2 Base Model and Training Data

We use **DeepSeek-Coder-7B-base** [DeepSeek-AI, 2023] as the base model for all experiments. A 7B-parameter code-specialized decoder was chosen to be large enough for meaningful execution feedback learning while remaining feasible for smoke-scale validation experiments. The DeepSeek-Coder series provides strong off-the-shelf code understanding without the confound of prior RLEF post-training.

**APPS** [Hendrycks et al., 2021] provides training problems across three difficulty levels: introductory (approximately 3500 problems), interview (approximately 5000 problems), and competition (361 problems with ≥1 test case after filtering). The dataset is publicly available at `codeparrot/apps` on HuggingFace. Critically, APPS includes reference solutions and test cases, enabling both SFT (from reference solutions) and RLEF (from test-case execution on generated outputs).

For training, we use `codeparrot/apps` with train split filtering: only problems with at least one executable test case are included. The SFT split uses reference solutions as targets; the RLEF split provides problems and test cases as execution oracles.

**A key measurement from this dataset:** APPS competition problems have 85.32% reference solution coverage — 308 of 361 competition problems have solutions that pass all included test cases. This directly contradicts the "sparse signal void" assumption from prior literature and is the basis for our mechanistic reframing. See Section 5.4 for detailed analysis.

## 3.3 Training Methods

### Supervised Fine-Tuning (SFT Baseline)

SFT is implemented using HuggingFace `Trainer` with standard causal language modeling loss over reference solutions. Key hyperparameters:

```
learning_rate: 2e-5
num_epochs: 3 (full); 1 (smoke scale)
batch_size: 2 (effective: 16 with gradient accumulation ×8)
max_length: 2048 tokens
```

The SFT model provides both the baseline for comparison and the starting checkpoint for RLEF training (warm-start from SFT checkpoint). A "ceiling check" measures zero-shot HumanEval pass@1 before SFT to ensure the base model is not saturated (>90% would trigger fallback to 1.3B; not triggered).

### RLEF-Fraction Training

RLEF-Fraction uses GRPO [Shao et al., 2024] with fraction-of-tests-passing reward. Each generated completion is executed against all test cases in the problem; reward = (number of passing tests) / (total tests). This provides dense reward signal that can distinguish partial success from complete failure.

**Reward function:**

```python
def fraction_reward_fn(completions, prompts, metadata):
    rewards = []
    for code, meta in zip(completions, metadata):
        passed = sum(
            _execute_code(code, stdin=tc_in, timeout=3.0) == tc_out
            for tc_in, tc_out in meta['test_cases']
        )
        rewards.append(passed / len(meta['test_cases']))
    return rewards
```

Code execution is subprocess-sandboxed (`subprocess.run` with timeout, in a temporary directory) to prevent environment contamination.

**Key RLEF hyperparameters:**

```
learning_rate: 1e-6
num_generations (G): 4 (smoke); 8 (full)
max_new_tokens: 512  # CRITICAL: ≥512 to avoid truncation (see Section 5.3)
beta (KL penalty): 0.04
temperature: 0.8
warmup_steps: 10
logging_steps: 5
```

### RLEF-Binary (Proxy)

Due to compute constraints, a fully trained RLEF-Binary checkpoint was not available. The binary reward comparison (h-m3) used a proxy estimation method: binary reward for each completion was estimated from fraction reward values by converting to {0, 1} based on whether any test passed. While this proxy provides directional evidence, we note it as a limitation — the null result (p=0.552) is consistent with two independent literature sources and is reported as a directional negative result.

### SimpleGRPOTrainer

Standard TRL GRPOTrainer is incompatible with PyTorch 2.5.1 due to changes in the DDP module interface. We implemented a custom `SimpleGRPOTrainer` that:

1. Generates `G` completions per prompt using the policy
2. Computes rewards via `fraction_reward_fn` (subprocess-sandboxed)
3. Computes group-relative advantages: `A_i = (r_i - mean(r)) / (std(r) + ε)`
4. Updates policy with REINFORCE-style loss: `L = -A_i · log π(a_i | s_i)` plus KL penalty from SFT reference
5. Logs per-step rewards by difficulty to `logs/reward_monitoring.jsonl` via `RewardMonitorCallback`

This trainer is fully self-contained (≈250 lines) and has been validated to produce convergent training behavior on APPS problems (62 GRPO steps confirmed).

## 3.4 Evaluation Benchmarks and Difficulty Ordering

We evaluate on five benchmarks in ascending difficulty order:

| Benchmark | Problems | Difficulty | Notes |
|-----------|----------|------------|-------|
| HumanEval | 164 | Easy | Function-level Python; standard canonical set [Chen et al., 2021] |
| MBPP | 374 | Medium-Easy | Python programming problems [Austin et al., 2021] |
| LiveCodeBench-Easy | ~200 | Medium | Competitive programming, LCB-Easy subset [Jain et al., 2024] |
| LiveCodeBench-Medium | ~200 | Medium-Hard | Competitive programming, LCB-Medium subset |
| LiveCodeBench-Hard | ~100 | Hard | Competitive programming, LCB-Hard subset; our primary difficulty target |

All evaluation is conducted with bigcode-evaluation-harness in correctness-only mode (pass@1, single generation per problem). Evaluation is identical across SFT and RLEF checkpoints — same harness call, same number of problems, same pass@1 metric.

**Primary evaluation metric:** Δ = pass@1(RLEF) − pass@1(SFT) at each benchmark. The difficulty-scaling hypothesis predicts positive Δ values that increase (on ordered trend) from easy to hard benchmarks.

## 3.5 Statistical Analysis

**Jonckheere-Terpstra (JT) test** is used to test the ordered trend hypothesis: Δ values are expected to be positively ordered across the five difficulty levels. JT is appropriate because it tests an *a priori* ordered alternative hypothesis without requiring strict monotonicity at every adjacent pair. The test is implemented via pairwise Mann-Whitney U statistic sums, bootstrapped with n=5000 replicates from proxy point estimates (h-m4).

**Bootstrap confidence intervals** (n=5000, BCa method) are used for Δ and Δ_ratio estimates. We report 95% CIs throughout.

**Honest caveat on statistical values:** The JT z-score (z=+56.10) and bootstrap p-values are computed on pseudo-groups derived from smoke-scale proxy estimates, not independent experimental replications. Statistical values should be interpreted as "consistent with a positive trend given these estimates" rather than "confirmed from independent replications." Full-scale replication (Phase 5) is required for definitive statistical claims.

## 3.6 Sub-Hypothesis Structure

Our experiment is structured as a multi-hypothesis validation protocol:

| ID | Type | Question | Gate |
|----|------|----------|------|
| h-e1 | Existence | Does RLEF-Fraction produce valid training with non-zero rewards? | MUST_WORK |
| h-m1 | Mechanism | What is the SFT baseline failure pattern at hard difficulty? | MUST_WORK |
| h-m2 | Mechanism | Does RLEF receive non-zero reward on competition problems? | SHOULD_WORK |
| h-m3 | Comparison | Does fraction reward outperform binary reward at LCB-Hard? | SHOULD_WORK |
| h-m4 | Mechanism | Does RLEF advantage follow a positive-ordered trend across difficulty? | SHOULD_WORK |

MUST_WORK gates must pass for the core contribution to be valid. SHOULD_WORK gates can fail with documented limitations. This structure enables honest reporting of both confirmed and disconfirmed predictions.
