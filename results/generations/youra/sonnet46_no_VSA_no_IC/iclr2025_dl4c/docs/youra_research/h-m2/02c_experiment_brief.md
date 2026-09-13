# Experiment Design: H-M2

**Date:** 2026-08-21
**Author:** Anonymous
**Hypothesis Statement:** GRPO training on variance-50 produces lower mean TRL frac_reward_zero_std than random-50 at training checkpoints (steps 10, 20, 50), confirming that variance profiling successfully identifies MBPP problems with nonzero GRPO gradient signal.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (PoC) Template** - Test "does variance selection reduce zero-gradient groups?"

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-M1 VALIDATED (MUST_WORK gate PASSED)
**Gate Status:** SHOULD_WORK — failure triggers PIVOT to online selection

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (VALIDATED)

### Gate Condition
SHOULD_WORK: mean_frac_zero_std(variance-50) < mean_frac_zero_std(random-50) at ALL three checkpoints (steps 10, 20, 50). Secondary: gap ≥ 5pp at checkpoint 10.

---

## Continuation Context

H-M1 VALIDATED: Top-50 variance-selected MBPP problems have meaningfully higher mean variance than random-50. The variance profiling signal is confirmed real and ranking is stable at k=8. Top-50 selected problem IDs and their variance_i values are available from H-M1 output.

**Applied from H-M1:**
- MBPP training split (374 problems) profiled at k=8 with DeepSeek-Coder-7B-Instruct
- Top-50 selected problem IDs confirmed stable
- mean(variance_i(variance-50)) > mean(variance_i(random-50)) confirmed
- Frozen model checkpoint path established

### Previous Hypothesis Results (if applicable)
H-M1 (VALIDATED): Variance profiling produces stable ranking. Top-50 selection is meaningful. Proceed to mechanism test: does training on this selection actually reduce zero-gradient groups?

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: GRPO training frac_reward_zero_std gradient signal**
- Archon KB does not contain direct hits for TRL/GRPO frac_reward_zero_std (KB is diffusion-model focused). No relevant results.

**Query 2: Variance guided data selection RLEF subset GRPO**
- No relevant Archon KB results for this specific topic (KB covers image generation training, not RLEF code generation).

**Key Insight:** Archon KB is not a relevant source for this hypothesis. All implementation evidence sourced from Exa (official TRL docs + GitHub).

### Archon Code Examples

**Query: TRL GRPO trainer frac_reward_zero_std logging**
- No relevant code examples found in Archon KB (diffusion-model focused).

### Exa GitHub Implementations

**Source 1: Official TRL GRPOTrainer Documentation**
- **URL:** https://huggingface.co/docs/trl/en/grpo_trainer
- **Relevance:** Authoritative definition of `frac_reward_zero_std` metric
- **Key Finding:** `frac_reward_zero_std` = "The fraction of samples in the generation batch with a reward std of zero, implying there is little diversity for that prompt (all answers are correct or incorrect)." This is logged automatically by TRL GRPOTrainer — no custom instrumentation needed.
- **Architecture:** GRPOTrainer with `use_vllm=False`, `num_generations=4`, `generation_batch_size=4`
- **Key insight:** `frac_reward_zero_std` is computed per-step over the generation batch. For binary execution rewards (0/1), a group of G=4 completions has zero std iff all 4 pass or all 4 fail — i.e., exactly when σ=0 by the identity σ=√(k(G-k))/G.

**Source 2: TRL GRPOTrainer source (grpo_trainer.py)**
- **URL:** https://github.com/huggingface/trl/blob/main/trl/trainer/grpo_trainer.py
- **Key Finding:** `frac_reward_zero_std` is part of `self._metrics` logged per training step. Available via `logging_steps=1`. Trainer internally computes `std_grouped_rewards` and derives the fraction of groups with zero std.
- **Logging code:**
  ```python
  self._metrics[mode]["reward_std"].append(std_grouped_rewards.mean().item())
  # frac_reward_zero_std derived from grouped reward std per generation batch
  ```

**Source 3: TRL Bug Report #5588 (Zero-std reward groups)**
- **URL:** https://github.com/huggingface/trl/issues/5588
- **Key Finding:** Confirms mechanistic interpretation: "When all completions in a group receive the same reward, advantages are zero: `advantages = rewards - mean_grouped_rewards = 0`". Zero-std groups produce no policy gradient. This is the exact mechanism H-M2 tests.
- **Critical note for experiment:** Use `beta=0.0` (no KL penalty) or `beta` very small to avoid spurious KL gradients on zero-std groups (TRL issue #5588).

**Source 4: RRPO-ARR/Code (GRPO on MBPP)**
- **URL:** https://github.com/RRPO-ARR/Code
- **Key Finding:** Working GRPO training on MBPP with DeepSpeed. `grpo_mbpp.py` script confirms MBPP binary execution reward training pattern.
- **Config reference:** `--model_path Qwen/Qwen3-8B --dataset_path /path/to/mbpp`

**Source 5: nancui0000/adaptive-mogrpo**
- **URL:** https://github.com/nancui0000/adaptive-mogrpo
- **Key Finding:** Confirms that binary pass/fail reward causes zero-gradient problem. "GRPO requires within-group variance to compute meaningful advantages." Uses G=16 completions, but same principle applies at G=4.
- **Baseline pass@1 on MBPP:** Qwen2.5-7B gets +18% relative improvement in 2000 steps, but starts from 8.2% pass@1. Different model; confirms MBPP is tractable for GRPO.

**Source 6: Mroueh 2025 (GRPO with Verifiable Rewards)**
- **URL:** https://arxiv.org/html/2503.06639v2
- **Key Finding:** GRPO with binary rewards is an adaptive weighted contrastive loss. Groups where k=0 or k=G contribute zero gradient — mathematically exact. Confirms theoretical basis of H-M2.

### 🎯 Implementation Priority Assessment

**CRITICAL: H-M2 uses TRL GRPOTrainer directly (no paper reproduction). Priority:**

1. **TRL GRPOTrainer** (HIGHEST) — official, `frac_reward_zero_std` logged automatically, confirmed functional in H-E1
2. **Custom data subset selection wrapper** — load variance-50 vs random-50 subsets as separate datasets, pass to GRPOTrainer

**Recommended Implementation Path:**
- Primary: TRL GRPOTrainer with `use_vllm=False`, `num_generations=4`, `generation_batch_size=4`, `logging_steps=1`, `beta=0.0`
- Fallback: verl framework (more complex, unnecessary for this experiment)
- Justification: TRL already confirmed functional in H-E1; `frac_reward_zero_std` logged automatically; minimal new code required.

### Code Analysis (Serena MCP)

*Skipped* — Code from TRL docs and GitHub search is sufficiently clear. TRL GRPOTrainer is a well-documented library; semantic analysis not required. The `frac_reward_zero_std` metric is built-in.

---

## Experiment Specification

### Dataset

**Training Data:**
- **Name:** MBPP (Mostly Basic Python Problems)
- **Source:** google-research-datasets/mbpp (HuggingFace Datasets)
- **Split used:** Training split (374 problems)
- **Subsets:**
  - **variance-50:** Top-50 problems by variance_i = p_i*(1-p_i) from H-M1 profiling output
  - **random-50:** 50 randomly sampled problems from the 374 (fixed seed=42)
- **Type:** standard (real benchmark)
- **Format:** Each problem has: task_id, text (prompt), code (reference solution), test_list (unit tests)
- **Preprocessing:** Binary execution reward — generate 4 completions per problem, execute against test_list, reward = 1.0 if all tests pass, 0.0 otherwise

**Statistics:**
- Training pool: 374 problems (MBPP train split)
- Variance-50: 50 problems (top-50 by variance_i from H-M1)
- Random-50: 50 problems (random sample, seed=42, drawn ONCE and fixed)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Datasets
- Identifier: `"google-research-datasets/mbpp"`
- Code:
  ```python
  from datasets import load_dataset
  mbpp = load_dataset("google-research-datasets/mbpp", "sanitized")
  train_split = mbpp["train"]  # 374 problems
  ```

### Models

#### Baseline Model

**Architecture:** DeepSeek-Coder-7B-Instruct (v1.5)
- 7B parameters, instruction-tuned, code-specialized
- Confirmed functional in H-E1 environment

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: `"deepseek-ai/deepseek-coder-7b-instruct-v1.5"`
- Code:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  model = AutoModelForCausalLM.from_pretrained(
      "deepseek-ai/deepseek-coder-7b-instruct-v1.5",
      torch_dtype=torch.bfloat16,
      device_map="auto"
  )
  tokenizer = AutoTokenizer.from_pretrained(
      "deepseek-ai/deepseek-coder-7b-instruct-v1.5"
  )
  ```

#### Proposed Model

**Architecture:** Same model trained on variance-50 subset vs. random-50 subset (controlled comparison, not architecture change)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Variance-Guided Subset Selection for GRPO Training
# Based on: H-M1 profiling output + TRL GRPOTrainer (huggingface/trl)

def load_variance_selected_dataset(mbpp_train, top50_problem_ids):
    """
    Filter MBPP training split to variance-50 or random-50 subset.
    Args:
        mbpp_train: HuggingFace Dataset (374 problems)
        top50_problem_ids: list[int] — from H-M1 profiling output
    Returns:
        HuggingFace Dataset (50 problems)
    """
    return mbpp_train.filter(
        lambda x: x["task_id"] in set(top50_problem_ids)
    )

def make_binary_execution_reward(problem):
    """Reward function: 1.0 if code passes all unit tests, else 0.0."""
    def reward_fn(completions, **kwargs):
        rewards = []
        for code in completions:
            passed = execute_against_tests(code, problem["test_list"])
            rewards.append(1.0 if passed else 0.0)
        return rewards
    return reward_fn

# Training config (same for both conditions)
config = GRPOConfig(
    num_generations=4,           # G=4 groups
    generation_batch_size=4,     # one problem per forward pass
    max_steps=50,                # short RLEF budget
    learning_rate=5e-7,
    beta=0.0,                    # no KL penalty (avoid zero-std spurious grads)
    logging_steps=1,             # log frac_reward_zero_std every step
    use_vllm=False,
    save_steps=[10, 20, 50],     # checkpoints at key evaluation points
)
```

### Training Protocol

**Two conditions, identical config except dataset:**

| Parameter | Value | Source |
|-----------|-------|--------|
| Model | deepseek-ai/deepseek-coder-7b-instruct-v1.5 | H-E1 confirmed |
| Optimizer | AdamW | TRL default |
| Learning rate | 5e-7 | Phase 2B spec (same as h-e1) |
| num_generations (G) | 4 | Phase 2B spec |
| generation_batch_size | 4 | H-E1 environment constraint |
| use_vllm | False | H-E1 environment constraint |
| max_steps | 50 | Phase 2B spec |
| beta (KL coef) | 0.0 | TRL issue #5588: avoid spurious KL grads on zero-std groups |
| logging_steps | 1 | Required for per-step frac_reward_zero_std |
| save_steps | [10, 20, 50] | Checkpoint for evaluation |
| Seed | 42 | Fixed |

**Condition A:** Train on variance-50 (top-50 by variance_i from H-M1)
**Condition B:** Train on random-50 (50 randomly sampled, seed=42)

**Reward function:** Binary execution reward — 1.0 if all unit tests pass, 0.0 otherwise. No partial credit.

**Seeds:** 1 (single run per condition; mechanistic metric `frac_reward_zero_std` less noise-sensitive than pass@1)

### Evaluation

**Primary Metric:** `frac_reward_zero_std` (logged automatically by TRL GRPOTrainer per step)

**Measurement protocol:**
1. Read `frac_reward_zero_std` from TRL training logs at steps 1-50
2. Compute mean_frac_zero_std for each condition at checkpoints 10, 20, 50:
   - `mean_frac_10 = mean(frac_reward_zero_std[steps 1-10])`
   - `mean_frac_20 = mean(frac_reward_zero_std[steps 1-20])`
   - `mean_frac_50 = mean(frac_reward_zero_std[steps 1-50])`
3. Compare: variance-50 vs random-50 at each checkpoint

**Success Criteria:**
- Primary (P2): mean_frac_zero_std(variance-50) < mean_frac_zero_std(random-50) at ALL three checkpoints
- Secondary: Gap ≥ 5pp at checkpoint 10 (early signal of selection quality)

**Expected baseline performance (random-50):**
- At G=4 binary reward: ~69.25% zero-gradient groups expected (Gradient Starvation arXiv:2605.07689)
- Random-50 includes ~31% intermediate-p_i problems → expect ~69% frac_zero_std
- Variance-50 includes top-50 by p_i*(1-p_i) → expect lower frac_zero_std (all selected problems have nonzero expected reward variance)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: RLEF mechanism verification
- Library: TRL built-in (`frac_reward_zero_std` auto-logged)
- Code:
  ```python
  # frac_reward_zero_std logged automatically to trainer.log_history
  # Also available via wandb/tensorboard if report_to configured
  # Read from log file:
  frac_zero_std_per_step = [
      log["frac_reward_zero_std"]
      for log in trainer.state.log_history
      if "frac_reward_zero_std" in log
  ]
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart comparing mean_frac_zero_std(variance-50) vs mean_frac_zero_std(random-50) at checkpoints 10, 20, 50

#### Additional Figures (LLM Autonomous)
- Learning curves: frac_reward_zero_std per step (1-50) for both conditions (line plot)
- Gap trajectory: frac_zero_std(random-50) - frac_zero_std(variance-50) over steps 1-50
- Reward distribution: histogram of group reward std at step 0, 10, 20, 50 per condition

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-m2/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (both training conditions complete 50 steps)
2. mean_frac_zero_std(variance-50) < mean_frac_zero_std(random-50) at steps 10, 20, AND 50

**Mechanism Verification Pre-conditions:**
- `mechanism_exists`: YES — `frac_reward_zero_std` is a built-in TRL metric, logged automatically
- `mechanism_isolatable`: YES — only the dataset subset changes between conditions; model, config, seed identical
- `baseline_measurable`: YES — random-50 condition provides direct baseline; theoretical expectation ~69% frac_zero_std

**Architecture Compatibility:**
- TRL GRPOTrainer confirmed functional in H-E1 environment
- `frac_reward_zero_std` available in TRL >= 0.15.x (verified in Exa search)
- Binary execution reward compatible with `frac_reward_zero_std` computation (reward std = std of 0/1 values in group of 4)

**Mechanism Activation Indicators:**
- Log message: `frac_reward_zero_std` value decreasing in variance-50 condition vs random-50
- Expected tensor behavior: rewards tensor shape `(batch, G=4)` → std per group → fraction with std=0
- Metric delta expected: gap of ≥5pp in frac_zero_std at step 10

**Failure Detection:**
- If frac_zero_std(variance-50) ≥ frac_zero_std(random-50) at step 10: mechanism not working; check variance_i values of selected problems
- If both conditions show frac_zero_std < 30%: model may have drifted even in first 10 steps (check training logs)
- If frac_reward_zero_std not in logs: TRL version may not support metric — verify TRL version ≥ 0.15

**Mechanism Verification Code:**
```python
# After training, verify mechanism worked:
assert len(frac_zero_std_variance50) == 50, "Missing steps"
mean_at_10_var = np.mean(frac_zero_std_variance50[:10])
mean_at_10_rnd = np.mean(frac_zero_std_random50[:10])
gap_at_10 = mean_at_10_rnd - mean_at_10_var
print(f"Gap at step 10: {gap_at_10:.3f} (target: ≥0.05)")
assert gap_at_10 > 0, "FAIL: variance-50 not showing lower frac_zero_std"
```

**Hypothesis Support Threshold:** mean_frac_zero_std(variance-50) < mean_frac_zero_std(random-50) at ALL of steps 10, 20, 50
**Hypothesis Support Metric:** frac_reward_zero_std (TRL built-in, per-step)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Result:** No relevant Archon KB sources for this hypothesis. Archon KB contains diffusion model training examples (LoRA, DreamBooth, HunyuanDiT) — not relevant to GRPO/RLEF code generation. All implementation evidence sourced from Exa.

### B. GitHub / Web Implementations (Exa)

**Source B.1: TRL GRPOTrainer Official Docs**
- **URL:** https://huggingface.co/docs/trl/en/grpo_trainer
- **Query:** "TRL GRPO training frac_reward_zero_std metric logging PyTorch"
- **Relevance:** Authoritative definition of `frac_reward_zero_std`; confirms it is auto-logged
- **Used for:** Dataset specification (understanding metric), Training protocol (logging_steps=1), Evaluation metrics
- **Key excerpt:** "frac_reward_zero_std: The fraction of samples in the generation batch with a reward std of zero, implying there is little diversity for that prompt (all answers are correct or incorrect)."

**Source B.2: TRL grpo_trainer.py (GitHub)**
- **URL:** https://github.com/huggingface/trl/blob/main/trl/trainer/grpo_trainer.py
- **Query:** "TRL GRPO training frac_reward_zero_std metric logging PyTorch"
- **Relevance:** Source code confirming `frac_reward_zero_std` stored in `self._metrics` and logged each step
- **Used for:** Training protocol, understanding logging mechanism, pseudo-code design

**Source B.3: TRL Issue #5588 (Zero-std spurious KL gradients)**
- **URL:** https://github.com/huggingface/trl/issues/5588
- **Query:** "TRL GRPOTrainer frac_reward_zero_std zero gradient group reward variance"
- **Relevance:** Confirms mechanistic interpretation of zero-std groups; motivates `beta=0.0` choice
- **Used for:** Training protocol (beta=0.0 decision), failure detection, mechanism verification

**Source B.4: RRPO-ARR/Code (GRPO on MBPP)**
- **URL:** https://github.com/RRPO-ARR/Code
- **Query:** "GRPO binary execution reward code generation MBPP DeepSeek training script"
- **Relevance:** Working GRPO training scripts for MBPP (`grpo_mbpp.py`); confirms feasibility
- **Used for:** Dataset loading confirmation, training script structure

**Source B.5: nancui0000/adaptive-mogrpo**
- **URL:** https://github.com/nancui0000/adaptive-mogrpo
- **Query:** "GRPO binary execution reward code generation MBPP DeepSeek training script"
- **Relevance:** Confirms binary pass/fail causes zero-gradient problem; confirms MBPP GRPO setup
- **Used for:** Expected baseline frac_zero_std estimation; training protocol hyperparameters

**Source B.6: Mroueh 2025 (GRPO with Verifiable Rewards)**
- **URL:** https://arxiv.org/html/2503.06639v2
- **Query:** "DeepSeek-Coder GRPO MBPP binary execution reward frac_reward_zero_std subset selection"
- **Relevance:** Mathematical proof that binary reward groups with k=0 or k=G produce zero gradient
- **Used for:** Theoretical justification; expected baseline frac_zero_std

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — TRL GRPOTrainer is well-documented library code. `frac_reward_zero_std` is a built-in metric; no semantic analysis of custom code required.

### D. Previous Hypothesis Context

**Source:** H-M1 validation output
- **Reused components:**
  - Top-50 selected MBPP problem IDs (variance-selected) — used as variance-50 dataset
  - Frozen DeepSeek-Coder-7B-Instruct checkpoint — same model for GRPO training start
  - k=8 profiling run output (variance_i per problem) — used for dataset construction
- **Why reused:** Only the training dataset subset differs between conditions; all other parameters identical for controlled comparison

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (MBPP) | Phase 2B + H-E1 | 02b_verification_plan.md Section 1.3 |
| Variance-50 problem IDs | H-M1 output | H-M1 validation |
| frac_reward_zero_std metric | Exa (TRL docs) | B.1, B.2 |
| beta=0.0 choice | Exa (TRL issue) | B.3 |
| Binary execution reward | Phase 2B + H-E1 | Confirmed operational |
| G=4, use_vllm=False | Phase 2B | Section 1.3 |
| lr=5e-7 | Phase 2B | Section 1.3 |
| Expected ~69% frac_zero_std | Phase 2B + Exa | B.5, B.6; Gradient Starvation arXiv:2605.07689 |
| Pseudo-code | Exa (TRL source) | B.1, B.2 |
| Save at steps 10,20,50 | Phase 2B | H-M2 verification protocol |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — state restated in ```state block)
**Date:** 2026-08-21

### Workflow History for This Hypothesis
- 2026-08-21: H-M2 set to IN_PROGRESS (hypothesis loop)
- 2026-08-21: Phase 2C experiment design COMPLETED

---

*MCP Tools Used: Archon (no relevant results), Exa (TRL docs + GitHub), Serena (skipped — clear code)*
*All specifications grounded in TRL GRPOTrainer official documentation and GitHub implementations*
*Next Phase: Phase 3 - Implementation Planning*
