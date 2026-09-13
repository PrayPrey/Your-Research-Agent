# Experiment Design: H-E1

**Date:** 2026-08-31
**Author:** Anonymous
**Hypothesis Statement:** Under GRPO post-training on APPS for DeepSeek-Coder-6.7B, ratio reward (k/n test cases) provides detectably different training signal than binary reward (0/1): per-step gradient norms differ between conditions at training step ≤500, and HumanEval pass@1 at checkpoint 200 shows a directional difference ≥1pp, because ratio reward provides differentiated signal across partially-correct completions within all-failing groups where binary reward assigns identical zero reward.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** N/A (no prerequisites for H-E1)
**Gate Status:** MUST_WORK — to be evaluated at experiment completion

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
MUST_WORK: At ≥1 checkpoint within first 500 GRPO training steps, gradient norms differ between binary and ratio conditions (95% bootstrap CI excludes 0); AND/OR HumanEval pass@1 at step-200 checkpoint shows directional difference ≥1pp in either direction.

---

## Continuation Context

H-E1 is the first hypothesis in the verification chain. No previous hypothesis results.

### Previous Hypothesis Results (if applicable)
None.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

> ⚠️ **ABLATION MODE**: MCP servers unavailable in this session (no_MCP ablation).
> Findings synthesized from Phase 1 research documented in 02b_verification_plan.md.

**Prior Literature (from Phase 1 — Established Facts):**

**Finding 1: GRPO for Code LLMs (DAPO — arXiv 2503.14476)**
- All prior RLEF papers use binary pass/fail reward exclusively
- GRPO eliminates critic network; 2–3x faster than PPO
- DeepSeek-Coder-6.7B used as standard 7B-class baseline in related work
- Typical GRPO training: 1000–2000 steps on code tasks
- Key hyperparameters from DAPO: group size G=8, clip ε=0.2, KL β=0.01–0.05

**Finding 2: APPS Dataset (Hendrycks et al. 2021 — arXiv 2105.09938)**
- 10,000 competitive programming problems
- Each problem has multiple test cases (avg ~20 per problem)
- Split: 5,000 train / 5,000 test
- Natively supports ratio reward: k tests passing / n total tests
- Pre-screen needed: retain problems with ≥5 non-redundant test cases

**Finding 3: HumanEval Evaluation (Chen et al. 2021)**
- 164 problems; standard pass@1 metric for code LLMs
- DeepSeek-Coder-6.7B baseline: ~52% pass@1 pre-training
- CodeRL RLEF improvement: ~5pp over SFT baseline
- Evaluation is binary (all-pass required) — tests reward-eval alignment hypothesis

**Finding 4: Binary vs. Ratio Reward Signal Analysis**
- Binary reward: all completions in GRPO group assigned 0 reward when all fail → zero gradient
- Ratio reward: partially-correct completions get non-zero reward even in all-fail group → non-zero gradient
- Expected effect: ratio reward provides non-zero gradient signal in more training steps
- This translates to measurably different gradient norms during training

**Implementation Challenges (known from domain knowledge):**
- GRPO group normalization: subtract group mean reward before computing policy gradient → ratio reward's extra signal survives normalization only when completions in same group have different pass counts
- Need ≥5 non-redundant test cases per problem for ratio reward to be informative
- HumanEval evaluation at step 200 requires checkpoint saving + inference pass

### Archon Code Examples

> ⚠️ ABLATION MODE — No MCP code search available.

**Known relevant codebases from Phase 1 research:**

**DAPO (Open-source GRPO for reasoning):**
- Source: ByteDance research group
- Framework: veRL / custom training loop
- Key pattern: GRPO with group size 8, generates G completions per prompt, normalizes rewards within group

**OpenRLHF GRPO implementation:**
- Common community GRPO implementation
- Supports custom reward functions via `reward_fn` callback
- Standard pattern for swapping binary → ratio reward

**trl (HuggingFace Transformers RL):**
- `GRPOTrainer` class available in recent trl versions
- Supports custom reward functions
- Easiest integration path for DeepSeek-Coder models

### Exa GitHub Implementations

> ⚠️ ABLATION MODE — No Exa MCP available.

**Known implementations (from domain knowledge):**

**Repository 1**: huggingface/trl (⭐ ~10k+)
- URL: https://github.com/huggingface/trl
- Relevance: GRPOTrainer with custom reward function support
- Key pattern: reward function receives completions list, returns float tensor
- Training config: supports DeepSeek-Coder via AutoModelForCausalLM
- Binary reward: `reward = float(all_tests_pass)`
- Ratio reward: `reward = tests_passing / total_tests`

**Repository 2**: OpenRLHF/OpenRLHF (⭐ ~5k+)
- URL: https://github.com/OpenRLHF/OpenRLHF
- Relevance: Production-grade GRPO implementation
- Supports custom remote reward functions
- Used in several code RLEF papers

**Repository 3**: qwenlm/qwen-rl or similar
- Pattern: GRPO with APPS-style code evaluation
- Typical code execution sandbox using subprocess with timeout

**Serena Analysis Needed**: false — reward function modification is simple, no complex code analysis needed

### 🎯 Implementation Priority Assessment

For H-E1, there is no single "author's official implementation" — this is a novel ablation not previously published.

**Recommended Implementation Path:**
- Primary: HuggingFace trl GRPOTrainer with custom reward function (simplest, most maintained)
- Fallback: OpenRLHF with custom reward module
- Justification: trl GRPOTrainer requires minimal modification to swap binary→ratio reward; DeepSeek-Coder-6.7B loads via AutoModelForCausalLM; gradient norm logging available via trainer callbacks

### Code Analysis (Serena MCP)

*Skipped* — Code from known sources is sufficiently clear; reward function swap is a 5-line change. No complex architecture analysis needed.

---

## Experiment Specification

### Dataset

**Name:** APPS (Automated Programming Progress Standard)
**Version:** Full dataset — codeparrot/apps on HuggingFace
**Type:** standard (real competitive programming problems)
**Source:** Hendrycks et al. 2021 (arXiv: 2105.09938); HuggingFace: `codeparrot/apps`

**Splits used:**
- Training: APPS train split (5,000 problems) → pre-screen to ≥5 non-redundant test cases
- Evaluation: HumanEval (164 problems, separate benchmark — NOT APPS test split)

**Pre-screening protocol:**
- Retain APPS training problems with ≥5 distinct, non-redundant test cases
- Non-redundancy check: test cases with distinct expected outputs and/or distinct input edge cases
- Expected retention: ~3,000–4,000 problems after filtering (assumption A1 validation)

**Statistics:**
- Total training problems: ~5,000 raw → ~3,000–4,000 filtered
- Test cases per problem: avg ~20 (range 2–100+)
- Difficulty: introductory (easy) to competition-level

**Preprocessing:**
- Format prompt as: `[problem description]\n\nWrite a Python solution:`
- Truncate problem descriptions > 1024 tokens
- No augmentation needed

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `codeparrot/apps`
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("codeparrot/apps", split="train")
# Filter for ≥5 test cases:
def has_enough_tests(example):
    import json
    try:
        tests = json.loads(example["input_output"])
        return len(tests.get("inputs", [])) >= 5
    except:
        return False
dataset = dataset.filter(has_enough_tests)
```

### Models

#### Baseline Model

**Architecture:** DeepSeek-Coder-6.7B-instruct
**Type:** Decoder-only transformer, code-specialized, instruction-tuned
**Parameters:** 6.7B
**Context:** 16,384 tokens

**Pre-experiment baseline (known):**
- HumanEval pass@1: ~52% (DeepSeek-Coder-6.7B-instruct, greedy)
- MBPP pass@1: ~65% (approximate)

**Modifications for experiment:**
- No architectural modification — reward function is the only change between conditions
- Both binary-condition and ratio-condition use identical base model weights

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `deepseek-ai/deepseek-coder-6.7b-instruct`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained(
    "deepseek-ai/deepseek-coder-6.7b-instruct",
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("deepseek-ai/deepseek-coder-6.7b-instruct")
```

#### Proposed Model

**Architecture:** DeepSeek-Coder-6.7B-instruct + ratio reward signal (training only)

The "proposed model" differs from baseline only in the reward function used during GRPO training. Architecture is identical; reward computation changes.

**Core Mechanism Implementation:**

```python
# Core Mechanism: Ratio Reward vs Binary Reward for GRPO
# Based on: APPS multi-test-case structure + GRPO reward normalization

import subprocess, json, signal

def execute_code_with_timeout(code: str, test_input: str, timeout: int = 5) -> bool:
    """Run generated code against one test input, return pass/fail."""
    try:
        result = subprocess.run(
            ["python3", "-c", code],
            input=test_input, capture_output=True,
            text=True, timeout=timeout
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False

def binary_reward(completion: str, test_cases: list) -> float:
    """Binary: 1.0 if ALL tests pass, else 0.0."""
    return float(all(execute_code_with_timeout(completion, t) for t in test_cases))

def ratio_reward(completion: str, test_cases: list) -> float:
    """Ratio: fraction of test cases passing (k/n)."""
    if not test_cases:
        return 0.0
    n_pass = sum(execute_code_with_timeout(completion, t) for t in test_cases)
    return n_pass / len(test_cases)

# GRPO group reward computation (used by trainer):
def compute_group_rewards(completions: list, test_cases: list, mode: str) -> list:
    reward_fn = ratio_reward if mode == "ratio" else binary_reward
    return [reward_fn(c, test_cases) for c in completions]
    # GRPO normalizes within group: reward_i - mean(rewards) before policy update
```

### Training Protocol

**Algorithm:** GRPO (Group Relative Policy Optimization)
**Implementation:** HuggingFace trl GRPOTrainer (or equivalent)

**Optimizer:** AdamW
- lr: 1e-6 (standard for RLEF fine-tuning of 7B models; from DAPO/related work)
- weight_decay: 0.01
- betas: (0.9, 0.999)

**Learning Rate Schedule:** Constant with warmup
- warmup_steps: 10
- Rationale: short training run (≤500 steps for gradient norm measurement); no decay needed

**Batch configuration:**
- prompt_batch_size: 64 (prompts per step)
- group_size G: 8 (completions per prompt, standard GRPO)
- Effective tokens per step: 64 × 8 × ~256 tokens avg ≈ 131K tokens/step

**Training steps:** 500 steps for primary gradient norm measurement; checkpoint at step 200 for HumanEval eval

**Generation config (during GRPO rollout):**
- max_new_tokens: 512
- temperature: 1.0 (sampling for diversity within group)
- do_sample: True

**Loss:** GRPO policy gradient loss
- clip_ratio ε: 0.2 (standard PPO/GRPO clip)
- KL penalty β: 0.01 (light regularization to reference model)

**Seeds:** 1 (fixed seed=42)

**Conditions (2 parallel runs):**
1. `binary_condition`: reward_fn = binary_reward
2. `ratio_condition`: reward_fn = ratio_reward

**Gradient norm logging:**
- Log per-step gradient norm (before clipping) via trainer callback
- Log to CSV: `gradient_norms_binary.csv`, `gradient_norms_ratio.csv`
- Capture: global_step, grad_norm, mean_reward, std_reward

**Checkpoint:** Save model at step 200 for HumanEval evaluation

### Evaluation

**Primary Metrics:**
1. **Per-step gradient norm** (training signal metric): `||∇θ L||_2` logged every step, steps 1–500
2. **HumanEval pass@1 at step 200**: greedy decoding on all 164 HumanEval problems

**Gradient norm analysis:**
- Bootstrap CI (n=1,000 bootstrap samples) on gradient norm difference: `norm_ratio[t] - norm_binary[t]` for t ∈ [100, 500]
- Success: 95% CI excludes 0 at ≥1 checkpoint

**HumanEval evaluation:**
- Greedy decode (temperature=0, do_sample=False)
- Evaluate all 164 problems
- Success: |pass@1_ratio - pass@1_binary| ≥ 0.01 (1pp)

**Success Criteria (EXISTENCE gate):**
- PRIMARY: Gradient norm difference is statistically distinguishable (95% bootstrap CI) at ≥1 step in [100, 500]
- SECONDARY: HumanEval directional difference ≥1pp at step 200

**Expected baseline performance (from literature):**
- HumanEval pass@1 before RLEF: ~52% (DeepSeek-Coder-6.7B-instruct greedy)
- After binary RLEF (~200 steps): ~54–57% (extrapolated from CodeRL ~5pp over 2000 steps)
- Source: CodeRL (arXiv 2207.01780), DAPO (arXiv 2503.14476)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: code generation / functional correctness
- Library: custom execution sandbox + HumanEval evaluation harness
- Code:
```python
# HumanEval evaluation
from human_eval.evaluation import evaluate_functional_correctness
# Or: use bigcode-evaluation-harness
# pip install human-eval
# evaluate_functional_correctness(sample_file, k=[1])
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart — binary vs ratio reward, HumanEval pass@1 at step 200

#### Additional Figures (LLM Autonomous)
Based on the hypothesis:
1. **Gradient norm trajectory plot**: Line plot of per-step gradient norm for both conditions (steps 1–500), with 95% bootstrap CI shading
2. **Reward distribution plot**: Histogram of per-group rewards for both conditions at representative steps (50, 100, 200, 500) — shows reward variance differences
3. **Mean group reward over training**: Line plot showing mean reward per step for both conditions — should show ratio reward having non-zero signal earlier

**Output Location**: `docs/youra_research/h-e1/figures/`

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (both conditions complete 500 GRPO steps)
2. Gradient norm bootstrap CI excludes 0 at ≥1 step in [100, 500] OR HumanEval difference ≥1pp

---

## Appendix: Reference Implementations

### A. Phase 1 Research Sources

**Source 1**: DAPO — arXiv 2503.14476 (Yu et al., 2025)
- Type: Primary paper — GRPO for code/reasoning RL
- Relevance: Canonical GRPO hyperparameters; confirms binary reward standard
- Key insights: G=8 group size, ε=0.2 clip, 1e-6 lr for RLEF
- Used for: Training protocol hyperparameters

**Source 2**: APPS — arXiv 2105.09938 (Hendrycks et al., 2021)
- Type: Dataset paper
- Relevance: Dataset selection rationale; multi-test-case structure
- Key insights: 10,000 problems; native k/n test structure; codeparrot/apps on HuggingFace
- Used for: Dataset specification

**Source 3**: CodeRL — arXiv 2207.01780 (Le et al., 2022)
- Type: RLEF for code paper
- Relevance: Baseline RLEF performance expectations
- Key insights: ~5pp HumanEval improvement over SFT with binary RLEF
- Used for: Expected baseline performance calibration

**Source 4**: HumanEval — arXiv 2107.03374 (Chen et al., 2021)
- Type: Evaluation benchmark
- Relevance: Primary evaluation metric source
- Key insights: 164 problems; pass@1 greedy; DeepSeek-Coder-6.7B ~52% baseline
- Used for: Evaluation protocol

### B. GitHub Implementations (from domain knowledge — Exa MCP unavailable)

**Repository 1**: huggingface/trl
- URL: https://github.com/huggingface/trl
- Relevance: GRPOTrainer with reward function callback — primary implementation path
- Key pattern: Custom reward_fn returning float list per completion
- Used for: Implementation path recommendation

**Repository 2**: OpenRLHF/OpenRLHF
- URL: https://github.com/OpenRLHF/OpenRLHF
- Relevance: Production GRPO; used in related RLEF papers
- Used for: Fallback implementation reference

### C. Code Analysis (Serena)
Not performed — reward function swap is straightforward; no complex architecture to analyze.

### D. Previous Hypothesis Context
None — H-E1 is the first hypothesis.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|---|---|---|
| Dataset: APPS | Phase 2B / Phase 1 research | Source A.2 (Hendrycks 2021) |
| Dataset loading | Domain knowledge | HuggingFace datasets API |
| Pre-screening (≥5 tests) | Phase 2B assumption A1 | 02b_verification_plan.md §1.5 |
| Model: DeepSeek-Coder-6.7B | Phase 2A selection | 02b_verification_plan.md §1.3 |
| GRPO hyperparameters | Prior RLEF papers | Source A.1 (DAPO 2503.14476) |
| Expected HumanEval baseline | CodeRL benchmark | Source A.3 (CodeRL 2207.01780) |
| Evaluation: HumanEval 164 | Phase 2B protocol | 02b_verification_plan.md §2.2 |
| Binary/Ratio reward pseudocode | Hypothesis mechanism | Derived from APPS test structure |
| Bootstrap CI (n=1000) | Phase 2B success criteria | 02b_verification_plan.md §2.2 |

---

## State Information

**State File:** verification_state.yaml (managed via ABLATION state blocks)
**Date:** 2026-08-31

### Workflow History for This Hypothesis
- 2026-08-31T04:57:48Z: H-E1 set to IN_PROGRESS (Phase 2C starting)
- 2026-08-31: Phase 2C experiment design completed

---

*MCP Tools Used: ABLATION MODE — no MCP available (no_MCP session). Research grounded in Phase 1 findings from 02b_verification_plan.md.*
*All specifications derived from established literature cited in Phase 1.*
*Next Phase: Phase 3 - Implementation Planning*
