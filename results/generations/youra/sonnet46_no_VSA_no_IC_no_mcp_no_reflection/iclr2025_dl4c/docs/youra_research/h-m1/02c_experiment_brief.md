# Experiment Design: H-M1

**Date:** 2026-08-31
**Author:** yoon303@ust.ac.kr
**Hypothesis Statement:** Under GRPO post-training on APPS with ratio reward for DeepSeek-Coder-6.7B, reward signal format shifts the optimal policy target from all-pass maximization (binary) to expected-coverage maximization (ratio): ratio-trained models achieve ≥3pp higher HumanEval pass@1 than binary-trained models, but show lower or equal APPS validation all-pass rates, because ratio reward incentivizes models to reliably pass high fractions of tests without consistently achieving all-pass on hard problems.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis Template** — Tests whether reward format shifts the policy optimization target.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 VALIDATED (ratio reward advantage variance = 0.0475 vs binary = 0.0 for partially-correct groups; 98.7% of early-training groups have ratio≠binary signal; smoke test confirmed)
**Gate Status:** MUST_WORK — if pass@1(ratio) - pass@1(binary) < 3pp on HumanEval, null finding for H-M1; proceed to H-M2 independently

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (SATISFIED)

### Gate Condition
**MUST_WORK:** pass@1(ratio) - pass@1(binary) ≥ 0.03 on HumanEval (95% bootstrap CI excluding 0) AND APPS validation all-pass rate: ratio-trained ≤ binary-trained (policy target shift signature).

**If Fail:** Null finding for H-M1; study still valid; proceed to H-M2 to check alignment effect independently.

---

## Continuation Context

H-M1 directly extends H-E1 by training to convergence (1000 steps vs. H-E1's 200-step checkpoint evaluation). H-E1 confirmed the mechanistic precondition: ratio reward generates differentiated gradient signal from partially-correct completions. H-M1 tests whether this signal difference produces measurable policy-level behavioral differences at task completion.

**Reuse from H-E1:**
- Same GRPO infrastructure (confirmed working; smoke test exit=0)
- Same APPS dataset preprocessing (≥5 non-redundant test cases filter)
- Same binary and ratio reward implementations (validated correct)
- Background run (PID=2605366) may provide intermediate checkpoints

**Key difference:** H-M1 trains to 1000 steps (vs. H-E1 step-200 checkpoint), evaluates HumanEval (164 problems), MBPP (374 problems), and APPS validation all-pass rate (≥500 problems).

### Previous Hypothesis Results (H-E1)
- Ratio reward advantage variance: 0.0475 vs binary 0.0 for partially-correct groups
- 98.7% of early-training GRPO groups receive different signals under ratio vs binary
- Smoke test (3 GRPO steps) confirmed infrastructure works
- Mechanistic proof: ratio reward is informationally superior in partially-correct completion groups

---

## Implementation Research Summary

### Archon Knowledge Base Findings

> ⚠️ **ABLATION NOTE:** Archon MCP not available in this execution environment. Findings synthesized from Phase 1 literature review embedded in 02b_verification_plan.md and established RLEF/GRPO literature.

**Relevant prior work extracted from Phase 2B Section 0 (BUILD_ON facts):**

**Finding 1: GRPO for Code LLMs**
- Source: DAPO (Yu et al., 2025 — arXiv 2503.14476)
- Dataset: Code and math reasoning benchmarks
- Key insight: GRPO eliminates critic network vs PPO; 2-3x faster; stable training signal
- Hyperparameters common in GRPO code training: group size G=8-16, clip ratio ε=0.2, KL penalty β=0.01-0.04
- Baselines: SFT → GRPO pipeline with binary execution reward

**Finding 2: RLEF for Code (Binary Reward)**
- Source: CodeRL (Le et al., 2022 — arXiv 2207.01780)
- Dataset: APPS (training), HumanEval (evaluation)
- Key insight: Binary pass/fail reward with PPO on APPS improves HumanEval ~5pp over SFT; binary reward is universal standard
- Expected baseline: HumanEval pass@1 ≈ 13-18% for 7B models with RLEF

**Finding 3: APPS Dataset Structure**
- Source: Hendrycks et al. (2021 — arXiv 2105.09938)
- Multi-test-case structure: 10,000 problems with ≥10 test cases each
- Training split: 5,000 problems; validation split: 500; test split: 5,000
- Partial-credit computation: k/n test cases pass → ratio = k/n ∈ [0,1]
- Key insight for H-M1: Problems where ratio=0.5 (5/10 tests pass) get meaningful gradient signal under ratio reward but zero under binary

**Finding 4: Policy Target Shift Mechanism (Theoretical)**
- Source: Reward shaping / RLHF literature (Ziegler et al. 2019; Stiennon et al. 2020)
- Key insight: Reward function shape determines the policy's optimization manifold; partial-credit rewards shift policy toward coverage maximization vs all-or-nothing maximization
- Analogous finding: In NLP, ROUGE-optimized models sacrifice precision for recall — ratio reward may cause analogous tradeoff in code (partial test coverage vs full test pass)

### Archon Code Examples

> ⚠️ **ABLATION NOTE:** Archon code MCP not available. Code patterns synthesized from DAPO/GRPO public implementations.

**Pattern 1: GRPO Training Loop (from DAPO/trl library)**
```python
# Standard GRPO training setup for code LLMs
from trl import GRPOTrainer, GRPOConfig

config = GRPOConfig(
    num_generations=8,       # group size G
    max_prompt_length=512,
    max_completion_length=512,
    learning_rate=1e-6,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=8,
    num_train_epochs=1,
    beta=0.04,               # KL penalty
)
```

**Pattern 2: Reward Function Variants**
```python
# Binary reward
def binary_reward(completions, test_cases):
    return [1.0 if all_tests_pass(c, test_cases) else 0.0 
            for c in completions]

# Ratio reward  
def ratio_reward(completions, test_cases):
    return [sum(run_test(c, t) for t in test_cases) / len(test_cases)
            for c in completions]
```

### Exa GitHub Implementations

> ⚠️ **ABLATION NOTE:** Exa MCP not available. GitHub references from Phase 2B literature.

**Repository 1: DAPO (Official)**
- URL: https://github.com/BytedanceSeed/DAPO (from Phase 2B citation)
- Relevance: Official GRPO code LLM implementation with binary reward baseline
- Architecture: GRPO + DeepSeek-series model + execution reward
- Training config: G=8, ε=0.2, β=0.04, lr=1e-6, 1000 steps
- Dataset: Code/math benchmarks

**Repository 2: TRL (HuggingFace)**
- URL: https://github.com/huggingface/trl
- Relevance: GRPOTrainer implementation; supports custom reward functions
- Key code: `GRPOTrainer.compute_rewards()` — overrideable for custom reward

**Repository 3: CodeRL (Official)**
- URL: https://github.com/salesforce/CodeRL
- Relevance: Binary reward RLEF baseline; APPS training setup
- Training config: PPO, APPS training split, HumanEval evaluation

**Serena Analysis Needed:** false — code patterns sufficiently clear from above references.

### 🎯 Implementation Priority Assessment

**Priority:** Extend existing H-E1 implementation (already validated)

**Recommended Implementation Path:**
- Primary: Existing codebase from H-E1 (confirmed working, exit=0)
- Fallback: trl GRPOTrainer with custom reward function
- Justification: H-E1 smoke test confirms infrastructure; extending to 1000 steps and adding MBPP/APPS-val evaluation is incremental

### Code Analysis (Serena MCP)

*Skipped* — Code from H-E1 implementation is sufficiently clear; no new complex code patterns required. H-M1 extends H-E1 training duration and evaluation scope.

---

## Experiment Specification

### Dataset

**Primary Training Dataset: APPS (Automated Programming Progress Standard)**
- Source: Hendrycks et al. 2021 (arXiv 2105.09938)
- HuggingFace: `codeparrot/apps`
- Type: standard (real competitive programming problems)
- Total problems: 10,000
- Training split: 5,000 problems
- Validation split for APPS all-pass rate evaluation: 500 held-out problems (difficulty-stratified)
- Test split: 5,000 (not used in training)
- Preprocessing: Filter to problems with ≥5 non-redundant test cases (inherited from H-E1)
- Expected problems after filter: ~3,500-4,000 training problems

**Evaluation Dataset 1: HumanEval**
- Source: Chen et al. 2021 (OpenAI)
- HuggingFace: `openai_humaneval`
- Problems: 164 (full standard set — do NOT reduce)
- Metric: pass@1
- Type: standard

**Evaluation Dataset 2: MBPP (Mostly Basic Programming Problems)**
- Source: Austin et al. 2021 (Google)
- HuggingFace: `google-research-datasets/mbpp`
- Problems: 374 (full standard test split — do NOT reduce)
- Metric: pass@1
- Type: standard

**Loading Information (for Phase 4 download):**
- Method: HuggingFace datasets
- Training: `load_dataset("codeparrot/apps", split="train")`
- HumanEval: `load_dataset("openai_humaneval", split="test")`
- MBPP: `load_dataset("google-research-datasets/mbpp", split="test")`
- Code:
  ```python
  from datasets import load_dataset
  apps_train = load_dataset("codeparrot/apps", split="train")
  humaneval = load_dataset("openai_humaneval", split="test")
  mbpp = load_dataset("google-research-datasets/mbpp", split="test")
  ```

### Models

#### Baseline Model

**Architecture:** DeepSeek-Coder-6.7B-instruct
- Type: Decoder-only transformer, code-specialized
- Parameters: 6.7B
- Source: deepseek-ai/DeepSeek-Coder-V2-Instruct (HuggingFace)
- Configuration: 32 layers, 32 heads, hidden dim 4096
- Input: Code prompt (function signature + docstring)
- Output: Code completion

**Loading Information (for Phase 4 download):**
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
  tokenizer = AutoTokenizer.from_pretrained(
      "deepseek-ai/deepseek-coder-6.7b-instruct"
  )
  ```

**Why this model:** Strongest open-weight 7B code LLM; representative of RLEF-capable models; H-E1 infrastructure already tested on it.

#### Proposed Model

**Architecture:** DeepSeek-Coder-6.7B-instruct + GRPO post-training with ratio reward (k/n test cases)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Ratio Reward for GRPO
# Based on: Phase 2B design + H-E1 validated implementation

def compute_ratio_reward(
    completions: list[str],
    test_cases: list[dict],
    timeout: float = 3.0
) -> list[float]:
    """
    Args:
        completions: list of G generated completions per prompt
        test_cases: list of {input, output} dicts
        timeout: per-test execution timeout in seconds
    Returns:
        rewards: list[float] in [0, 1], one per completion
                 = k/n where k = tests passed, n = total tests
    """
    rewards = []
    for completion in completions:
        passed = 0
        total = len(test_cases)
        for test in test_cases:
            try:
                result = execute_with_timeout(
                    completion, test["input"], timeout
                )
                if result == test["output"]:
                    passed += 1
            except Exception:
                pass  # timeout or runtime error = 0
        rewards.append(passed / total if total > 0 else 0.0)
    return rewards

# Integration: replaces binary_reward in GRPO trainer
# GRPO advantage computation uses ratio rewards directly:
# A_i = (r_i - mean(r)) / (std(r) + eps)
# Key: when all completions fail, binary gives A_i=0 for all,
#      ratio gives non-zero A_i for partially-correct completions
```

**Comparison Condition (Binary Reward):**
```python
def compute_binary_reward(completions, test_cases, timeout=3.0):
    """Returns 1.0 if all tests pass, 0.0 otherwise."""
    rewards = []
    for completion in completions:
        all_pass = all(
            execute_with_timeout(completion, t["input"], timeout) 
            == t["output"]
            for t in test_cases
        )
        rewards.append(1.0 if all_pass else 0.0)
    return rewards
```

### Training Protocol

**Reused from H-E1 (optimal; confirmed working):**

| Parameter | Value | Source |
|-----------|-------|--------|
| Optimizer | AdamW | DAPO/GRPO standard |
| Learning Rate | 1e-6 | DAPO paper; GRPO code baseline |
| LR Schedule | Constant with warmup (100 steps) | DAPO standard |
| Batch Size | 1 prompt × 8 completions per group (G=8) | DAPO G=8 |
| Gradient Accumulation | 8 steps → effective batch = 8 prompts | GPU memory constraint |
| Training Steps | 1000 (primary criterion for H-M1) | Phase 2B §2.2 |
| KL Penalty β | 0.04 | DAPO paper |
| Clip Ratio ε | 0.2 | GRPO standard (PPO-clip) |
| Max Prompt Length | 512 tokens | Standard for APPS |
| Max Completion Length | 512 tokens | Standard for code |
| Seeds | 1 (fixed seed=42) | Compute efficiency |
| Checkpointing | Every 200 steps (steps 0,200,400,600,800,1000) | Phase 2B §2.2 |

**Two Training Conditions (controlled comparison):**
1. **Binary condition:** Same as above but with `compute_binary_reward`
2. **Ratio condition:** Same as above but with `compute_ratio_reward`

All hyperparameters identical across conditions except reward function.

**APPS Test Case Pre-screening (inherited from H-E1):**
- Retain only APPS problems with ≥5 non-redundant test cases
- Non-redundancy: test cases where input hashes are distinct
- Expected: ~3,500-4,000 training problems

### Evaluation

**Primary Metric: HumanEval pass@1**
- Evaluation at: steps 200, 400, 600, 800, 1000
- Full set: 164 problems
- Sampling: greedy decoding (temperature=0 for pass@1)
- Library: `evaluate` (HuggingFace) with `code_eval` metric
- Success criterion: pass@1(ratio, step=1000) - pass@1(binary, step=1000) ≥ 0.03

**Secondary Metric 1: MBPP pass@1**
- Evaluation at: step 1000 only (compute constraint)
- Full set: 374 problems
- Sampling: greedy decoding
- Directional check only (no threshold)

**Secondary Metric 2: APPS validation all-pass rate**
- Evaluation at: step 1000
- 500 held-out APPS problems (stratified by difficulty)
- Metric: fraction of problems where ALL test cases pass (10/10 equivalent)
- Prediction: ratio-trained ≤ binary-trained (policy target shift signature)
- This is the KEY distinguishing metric for H-M1 mechanism claim

**Success Criteria:**
- P1 (primary): pass@1(ratio) - pass@1(binary) ≥ 0.03 on HumanEval at step 1000, 95% bootstrap CI (n=1000) excluding 0
- P2 (mechanism): APPS all-pass rate: ratio-trained ≤ binary-trained at step 1000 (this confirms policy target shift, not just performance improvement)
- Both P1 AND P2 required for GATE SATISFIED

**Expected Baseline Performance (from Phase 2B §1.4):**
- DeepSeek-Coder-6.7B-instruct SFT baseline: ~45-50% HumanEval pass@1
- Binary GRPO expected gain: ~3-8pp (based on CodeRL 5pp gain from smaller models; GRPO should be ≥ PPO)
- Ratio GRPO expected gain: ~5-11pp (hypothesis prediction)

**Metrics Loading Information (for Phase 4 implementation):**
- Task Type: code generation / functional correctness
- Library: `evaluate` (HuggingFace) + custom execution sandbox
- Code:
  ```python
  from evaluate import load
  code_eval = load("code_eval")
  # pass@1 evaluation
  pass_at_k, results = code_eval.compute(
      references=test_cases,
      predictions=completions,
      k=[1],
      num_workers=4
  )
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing HumanEval pass@1 (binary vs ratio at step 1000) and APPS all-pass rate (binary vs ratio at step 1000). Two side-by-side bars per metric.

#### Additional Figures (LLM Autonomous)

Based on H-M1's focus on policy target shift and training dynamics:

1. **Learning Curves:** HumanEval pass@1 vs. training step (0-1000) for binary and ratio conditions. X-axis: steps [0,200,400,600,800,1000]. Both conditions on same plot.

2. **APPS All-Pass Distribution:** Histogram of per-problem test-pass rates (k/n) at step 1000 for binary vs ratio models. Shows whether binary model concentrates mass at 0 and 1 (bimodal) while ratio shows smoother distribution.

3. **Reward Signal Distribution (from H-E1 inherited):** Box plot of reward values per GRPO group at step 200, 600, 1000 — shows whether reward variance changes over training.

4. **Policy Target Shift Scatter:** For each APPS validation problem: scatter of (binary_pass_rate, ratio_pass_rate) showing which regime each condition optimizes toward.

Output Location: `docs/youra_research/h-m1/figures/`

---

## 🔬 Mechanism Verification Protocol

**Purpose:** Define how Phase 4 verifies that the policy target shift mechanism actually operates, not just that code runs.

### Pre-conditions (verify before training)

| Pre-condition | Check | Expected |
|--------------|-------|----------|
| `mechanism_exists` | Ratio reward computation returns values in (0,1) for partially-correct completions | True — confirmed by H-E1 (advantage variance = 0.0475 > 0) |
| `mechanism_isolatable` | Binary and ratio conditions differ ONLY in reward function; all other hyperparameters identical | True — controlled experiment design |
| `baseline_measurable` | HumanEval and APPS validation evaluation pipelines produce stable pass@1 | True — greedy decoding is deterministic |

**Architecture Compatibility:**
- DeepSeek-Coder-6.7B-instruct accepts GRPO gradient updates ✅ (confirmed H-E1)
- Ratio reward integrates at reward computation stage, before GRPO advantage normalization ✅
- No architectural modification required — reward is external to model ✅

### Activation Indicators

**During Training (log every 50 steps):**
```python
# Mechanism log message — confirms ratio reward is active
logger.info(f"Step {step}: ratio_reward_mean={reward_mean:.4f}, "
            f"ratio_reward_std={reward_std:.4f}, "
            f"fraction_partial={fraction_strictly_between_0_and_1:.4f}")
# Expected: fraction_partial > 0.05 throughout training
# If fraction_partial → 0: model learned to always pass all or fail all → degenerate
```

**Tensor shape change:** None — ratio reward is a scalar per completion, same shape as binary reward. No architectural tensor changes.

**Metric delta expected:**
- Step 200: Expect ratio advantage variance > binary advantage variance (already confirmed by H-E1)
- Step 1000: Expect HumanEval pass@1 gap ≥ 3pp (primary criterion)
- Step 1000: Expect APPS all-pass rate gap ≤ 0 (ratio ≤ binary — mechanism signature)

### Failure Detection

```python
# Failure mode 1: Ratio reward degenerates to binary
# (APPS test cases are fully redundant — A1 assumption violated)
def check_ratio_degeneracy(rewards_per_group):
    """Returns True if ratio reward has degenerated."""
    return all(r in [0.0, 1.0] for r in rewards_per_group)

# Failure mode 2: No policy target shift (APPS all-pass rates converge)
def check_policy_shift(binary_allpass_rate, ratio_allpass_rate, threshold=0.02):
    """H-M1 mechanism requires ratio ≤ binary on APPS all-pass."""
    return ratio_allpass_rate <= binary_allpass_rate + threshold

# Failure mode 3: Training instability (gradient explosion)
def check_gradient_health(grad_norm, threshold=10.0):
    return grad_norm < threshold
```

### Mechanism Verification Code (Phase 4 integration)

```python
# After training completes — verify mechanism operated
def verify_h_m1_mechanism(
    ratio_humaneval_pass1: float,
    binary_humaneval_pass1: float, 
    ratio_apps_allpass: float,
    binary_apps_allpass: float,
    bootstrap_ci_lower: float  # 95% CI lower bound for HumanEval gap
) -> dict:
    """
    Returns mechanism verification result for H-M1.
    """
    p1_satisfied = (ratio_humaneval_pass1 - binary_humaneval_pass1 >= 0.03 
                    and bootstrap_ci_lower > 0)
    p2_satisfied = (ratio_apps_allpass <= binary_apps_allpass)
    
    return {
        "gate_satisfied": p1_satisfied and p2_satisfied,
        "p1_humaneval_gap": ratio_humaneval_pass1 - binary_humaneval_pass1,
        "p2_policy_shift": ratio_apps_allpass <= binary_apps_allpass,
        "mechanism_confirmed": p1_satisfied and p2_satisfied,
        "result": "GATE_SATISFIED" if (p1_satisfied and p2_satisfied) 
                  else "GATE_FAILED"
    }
```

**Success Threshold:** `hypothesis_support_threshold` = 0.03 HumanEval gap + directional APPS all-pass reversal
**Success Metric:** `hypothesis_support_metric` = HumanEval pass@1 delta + APPS all-pass rate comparison

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

> ⚠️ ABLATION: Archon MCP unavailable. Sources from Phase 2B literature registry.

**Source A.1: DAPO Paper (Yu et al., 2025)**
- Type: Literature review finding (Phase 1)
- Query equivalent: "GRPO code LLM training hyperparameters"
- Relevance: Official GRPO hyperparameters for code post-training
- Key insights: G=8, β=0.04, ε=0.2, lr=1e-6
- Used for: Training protocol (Step 4 of training protocol section)

**Source A.2: CodeRL (Le et al., 2022)**
- Type: Literature review finding (Phase 1)
- Query equivalent: "RLEF binary reward APPS HumanEval baseline"
- Relevance: Binary reward baseline; ~5pp HumanEval gain benchmark
- Key insights: Binary RLEF improves HumanEval 5pp; APPS is standard training set
- Used for: Expected baseline performance; binary reward design

**Source A.3: APPS Dataset (Hendrycks et al., 2021)**
- Type: Literature review finding (Phase 1)
- Query equivalent: "APPS dataset structure multi-test competitive programming"
- Relevance: Ratio reward requires multi-test-case problems; APPS has 10+ per problem
- Key insights: 10,000 problems, 5/10/5k train/val/test split, multi-test-case structure
- Used for: Dataset selection justification; ratio reward feasibility

### B. GitHub Implementations (Exa)

> ⚠️ ABLATION: Exa MCP unavailable. References from Phase 2B/Phase 1 citations.

**Repository B.1: DAPO Official**
- URL: https://github.com/BytedanceSeed/DAPO
- Query equivalent: "DAPO GRPO code LLM official implementation"
- Relevance: Official GRPO training loop for code LLMs
- Configuration extracted: G=8, ε=0.2, β=0.04, AdamW lr=1e-6
- Used for: Training protocol; GRPO implementation reference

**Repository B.2: TRL GRPOTrainer**
- URL: https://github.com/huggingface/trl
- Query equivalent: "GRPO trainer HuggingFace custom reward function"
- Relevance: Standard GRPO trainer with overrideable reward function
- Key code: `GRPOTrainer` with `reward_funcs` parameter
- Used for: Implementation path for ratio vs binary reward swap

**Repository B.3: CodeRL Official**
- URL: https://github.com/salesforce/CodeRL
- Query equivalent: "CodeRL APPS binary reward RLEF"
- Relevance: Binary reward RLEF baseline for APPS → HumanEval evaluation
- Configuration extracted: PPO (not GRPO), binary reward, APPS training
- Used for: Binary condition baseline design; evaluation pipeline reference

### C. Code Analysis (Serena)

Serena analysis not performed — H-M1 extends H-E1 implementation which is already validated. Code patterns from B.1-B.3 are sufficiently clear. No novel architecture to analyze.

### D. Previous Hypothesis Context

**Source: H-E1 Validation (completed 2026-08-31)**
- Validation result: GATE SATISFIED
- Key finding: Ratio reward advantage variance = 0.0475 vs binary = 0.0 for partially-correct groups
- Key finding: 98.7% of early-training groups receive different signals under ratio vs binary
- Reused components:
  - GRPO training infrastructure (confirmed working)
  - APPS dataset preprocessing (≥5 test case filter)
  - Binary and ratio reward implementations (validated)
  - DeepSeek-Coder-6.7B model loading (confirmed)
- Why reused: Enables controlled experiment — only extension is training duration (200 → 1000 steps) and evaluation scope (add MBPP, APPS-val)

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|-----------------|
| APPS training dataset | Literature (Phase 1) | Source A.3 (Hendrycks 2021) |
| HumanEval evaluation | Literature (Phase 1) | Source A.2 (Chen 2021 via CodeRL) |
| MBPP evaluation | Phase 2B §2.2 | Verification Protocol for H-M1 |
| APPS val all-pass rate | Phase 2B §2.2 | Verification Protocol for H-M1 |
| DeepSeek-Coder-6.7B | Phase 2B §1.3 | Experimental setup selection |
| GRPO hyperparameters | Literature (Phase 1) | Source A.1 (DAPO); B.1 |
| Binary reward function | H-E1 implementation | D.1 (validated) |
| Ratio reward function | H-E1 implementation | D.1 (validated) |
| Training protocol | Phase 1 + H-E1 | A.1, D.1 |
| Success criteria | Phase 2B §2.2 | H-M1 Verification Protocol |
| Bootstrap CI method | Phase 2B §2.2 | n=1000 bootstrap samples |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — not written to disk)
**Date:** 2026-08-31

### Workflow History for This Hypothesis

- 2026-08-31T05:53:53: H-M1 set IN_PROGRESS (external loop started Phase 2C → 3 → 4)
- 2026-08-31: Phase 2C experiment design completed
- Prerequisite H-E1 validated: GATE SATISFIED

---

*MCP Tools Used: ABLATION MODE — Archon/Exa unavailable; research synthesized from Phase 2B literature registry and H-E1 validation results*
*All specifications grounded in Phase 2B verification protocol and Phase 1 established facts*
*Next Phase: Phase 3 - Implementation Planning*
