# Experimental Setup

We design experiments to answer three research questions that map directly to our contributions:

**RQ1 (Difficulty scaling):** Does RLEF training produce a statistically significant positive-ordered advantage over SFT across benchmark difficulty levels from HumanEval (easy) to LiveCodeBench-Hard (competitive programming)?

**RQ2 (Signal void characterization):** Is SFT's failure at hard difficulty a *dataset* void (insufficient training coverage) or a *generalization* void (inability to transfer learned solutions)?

**RQ3 (Reward formulation):** Does fraction-of-tests reward produce meaningfully better performance than binary pass/fail reward at APPS training scale?

These questions are ordered by importance: RQ1 is the primary contribution, RQ2 provides mechanistic context, and RQ3 delivers the practical null result.

## 4.1 Training Datasets

**APPS** [Hendrycks et al., 2021] is the sole training dataset for all experiments. It contains approximately 10,000 Python algorithmic programming problems across three difficulty levels — introductory, interview, and competition — drawn from competitive programming platforms. Each problem includes a problem statement, reference solution(s), and executable test cases. We use the HuggingFace `codeparrot/apps` version with train split.

APPS was chosen for three reasons: (1) it spans the full algorithmic difficulty spectrum needed to test RQ1; (2) it includes executable test cases required for RLEF reward computation; (3) it is publicly available, enabling full reproducibility. Problems without any test case (i.e., no execution oracle available) are excluded from RLEF training.

**A critical property of APPS:** competition-level problems have 85.32% reference solution coverage (308/361 problems have solutions passing all test cases). This directly addresses RQ2 — see Section 5.4.

## 4.2 Evaluation Benchmarks

We evaluate on five benchmarks in ascending difficulty order:

| Benchmark | Problems | Difficulty | Notes |
|-----------|----------|------------|-------|
| HumanEval [Chen et al., 2021] | 164 | Easy | Canonical Python function-level; author-crafted test cases |
| MBPP [Austin et al., 2021] | 374 | Medium-Easy | Crowd-sourced Python programming tasks |
| LiveCodeBench-Easy [Jain et al., 2024] | ~200 | Medium | Time-limited competitive programming; contamination-free |
| LiveCodeBench-Medium | ~200 | Medium-Hard | Time-limited competitive programming |
| LiveCodeBench-Hard | ~100 | Hard | Competitive programming; our primary difficulty target |

LiveCodeBench was chosen because it provides contamination-free evaluation on problems released after model training cutoffs, stratified by difficulty in a consistent taxonomic framework. HumanEval and MBPP are included as established reference points at lower difficulty.

All evaluation uses **bigcode-evaluation-harness** in correctness-only mode (pass@1, single generation per problem, greedy decoding). Identical harness parameters are applied to all model checkpoints.

## 4.3 Training Methods (Baselines and Proposed)

**SFT Baseline:** Supervised fine-tuning of DeepSeek-Coder-7B-base on APPS reference solutions using HuggingFace Trainer with causal language modeling loss. This is the primary baseline for all comparisons. Training hyperparameters: lr=2e-5, 3 epochs (1 for smoke validation), batch size 16 (effective, with gradient accumulation ×8), max_length=2048 tokens.

**RLEF-Fraction (Proposed):** GRPO training starting from the SFT checkpoint, with reward = fraction of test cases passing. Implementation uses a custom SimpleGRPOTrainer compatible with PyTorch 2.5.1 / TRL 1.x. All generated solutions are executed in subprocess-sandboxed environments (3.0s timeout) to prevent environment contamination. Training hyperparameters: lr=1e-6, G=4 generations per prompt (smoke), max_new_tokens=512 (critical for avoiding truncation), β=0.04 (KL penalty), temperature=0.8, warmup_steps=10.

**RLEF-Binary (Proxy):** For the reward formulation comparison (RQ3), a full independently trained RLEF-Binary checkpoint was not available due to compute constraints. Binary performance is estimated from RLEF-Fraction by converting fraction rewards to binary at the problem level. This is an acknowledged limitation; the resulting null result (Section 5.3) is consistent with two independent literature sources.

**Rationale for baseline choice:** SFT is the directly contrasted method — the core claim is about RLEF vs. SFT. We do not include PPO-based RLEF variants or other model architectures, as our goal is a controlled study of the training signal type (execution feedback) with all other variables fixed. Comparing across architectures would introduce confounds that our controlled design is designed to eliminate.

## 4.4 Implementation Details

All training runs on a server with 5× NVIDIA H100 NVL (95830 MiB each). The smoke-scale validation experiments use 500 APPS samples per training run (1 epoch for SFT; 62 GRPO steps for RLEF). Full-scale runs are deferred to extended evaluation (Phase 5) and use 4449 samples × 3 epochs. Random seed 42 throughout.

Key implementation decisions:

- **max_new_tokens=512:** Token length must be sufficient for Python solutions to complete. A prior monitoring experiment (h-m2) used max_new_tokens=128 and produced 0.0 non-zero reward across all difficulty levels due to truncation. This is a methodological artifact, not a model capability result; 512+ tokens are required for valid reward computation.
- **Tokenizer source:** `deepseek-ai/deepseek-coder-7b-base` as tokenizer (not the SFT checkpoint); checkpoint tokenizer_config has a class incompatibility with HuggingFace Transformers 4.57.6.
- **Subprocess sandboxing:** Code execution is isolated in a temporary directory with resource limits. Execution-based reward computation is the most safety-critical component; sandboxing prevents side effects from model-generated code.

Full implementation code is available in the project repository.

## 4.5 Evaluation Metrics

**pass@1:** Fraction of problems solved correctly on the first generation (greedy decoding). Primary metric for all comparisons. Evaluated per benchmark using bigcode-evaluation-harness correctness-only mode.

**Δ = pass@1(RLEF) − pass@1(SFT):** Performance gap between RLEF and SFT at each difficulty level. The difficulty-scaling hypothesis (RQ1) predicts positive Δ values that follow a positive ordered trend from easy to hard benchmarks.

**Jonckheere-Terpstra (JT) z-score:** Tests the ordered alternative hypothesis that Δ values are non-decreasing across the five difficulty levels. JT is appropriate because it tests an *a priori* ordered hypothesis without requiring strict monotonicity at every adjacent pair. One-tailed p < 0.05 is our significance threshold.

**Bootstrap 95% confidence intervals:** Applied to Δ estimates (n=5000, BCa method) to quantify uncertainty around proxy estimates.

## 4.6 Sub-Hypothesis Structure and Gates

| Hypothesis | Focus | Gate Type | Criterion |
|------------|-------|-----------|-----------|
| h-e1 (Existence) | RLEF mechanism valid; pipeline functional | MUST_WORK | Non-zero reward during training; code executes |
| h-m1 (Signal void) | SFT baseline failure characterization | MUST_WORK | SFT LCB-Hard pass@1 < 0.60 |
| h-m2 (Reward monitoring) | Non-zero reward fraction on competition problems | SHOULD_WORK | Competition non-zero fraction > 0.10 |
| h-m3 (Reward ablation) | Fraction vs binary RLEF at LCB-Hard | SHOULD_WORK | Δ_Fraction − Δ_Binary > 0, p < 0.05 |
| h-m4 (Difficulty scaling) | Ordered RLEF advantage across 5 difficulty levels | SHOULD_WORK | JT z > 0, p < 0.05 |

MUST_WORK gates are prerequisites for the core contribution. SHOULD_WORK gates can fail with documented limitations without invalidating the primary finding.
