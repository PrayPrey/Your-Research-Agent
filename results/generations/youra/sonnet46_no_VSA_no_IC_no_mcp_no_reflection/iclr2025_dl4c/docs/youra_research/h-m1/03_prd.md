# Product Requirements Document: H-M1
## Ratio vs Binary Reward Policy Target Shift in GRPO Training for DeepSeek-Coder-6.7B

**Hypothesis:** H-M1  
**Type:** MECHANISM (INCREMENTAL — extends H-E1)  
**Date:** 2026-08-31  
**Author:** yoon303@ust.ac.kr  
**Source:** 02c_experiment_brief.md  
**Base Hypothesis:** H-E1 (VALIDATED)

---

## Executive Summary

This PRD specifies requirements for a full-scale controlled experiment comparing binary reward (0/1) versus ratio reward (k/n test cases) as training signal in GRPO post-training of DeepSeek-Coder-6.7B-instruct on APPS, trained to 1000 steps. H-E1 confirmed the mechanistic precondition: ratio reward generates differentiated gradient signal (advantage variance 0.0475 vs 0.0). H-M1 tests whether this signal difference produces measurable policy-level behavioral divergence at task completion: ≥3pp HumanEval pass@1 improvement for ratio-trained models, accompanied by lower or equal APPS validation all-pass rate (policy target shift signature). Both conditions must hold for GATE SATISFIED.

---

## Problem Statement

GRPO-based RLEF for code LLMs universally uses binary pass/fail reward. H-E1 proved ratio reward generates non-zero gradient signal where binary produces zero (partially-correct completion groups). H-M1 tests the downstream consequence: does this richer signal shift the optimal policy target from all-pass maximization (binary) to expected-coverage maximization (ratio)? The distinguishing prediction is that ratio-trained models will generalize better (higher HumanEval pass@1) but sacrifice strict all-pass performance on hard multi-test problems (lower APPS all-pass rate). This is a policy-level behavioral hypothesis requiring full training convergence.

---

## Section 1: Functional Requirements

### FR-1: Data Pipeline — APPS Dataset Loading and Filtering
- Load APPS train split from HuggingFace (`codeparrot/apps`)
- Filter to retain problems with ≥5 distinct, non-redundant test cases (inherited from H-E1)
- Non-redundancy: distinct input hashes
- Expected post-filter size: ~3,500–4,000 problems
- Format prompt: `{problem_description}\n\nWrite a Python solution:`
- Truncate descriptions >512 tokens (max_prompt_length=512 per training protocol)

### FR-2: Model Loading — DeepSeek-Coder-6.7B-instruct
- Load `deepseek-ai/deepseek-coder-6.7b-instruct` via HuggingFace transformers
- dtype: bfloat16
- device_map: auto
- Load corresponding tokenizer
- Both experimental conditions use identical base weights (same seed=42)

### FR-3: Reward Function Implementation (Inherited from H-E1)
- **Binary reward**: `float(all_tests_pass)` — 1.0 if all test cases pass, else 0.0
- **Ratio reward**: `sum(test_i_passes) / len(test_cases)` — fraction of test cases passing
- Code execution sandbox: subprocess with 3-second timeout (per H-E1 validated implementation)
- Graceful handling of syntax errors, runtime errors, timeout (count as 0 for that test)

### FR-4: GRPO Training — Binary Condition (1000 steps)
- Use HuggingFace trl GRPOTrainer with binary reward function
- Group size G=8 completions per prompt
- Gradient accumulation: 8 steps (effective batch = 8 prompts)
- per_device_train_batch_size: 1
- max_prompt_length: 512, max_completion_length: 512
- Learning rate: 1e-6, AdamW
- Warmup: 100 steps (constant schedule)
- Clip ratio ε=0.2, KL β=0.04
- Train for 1000 steps
- Save checkpoints at steps 200, 400, 600, 800, 1000
- Seed: 42

### FR-5: GRPO Training — Ratio Condition (1000 steps)
- Identical to FR-4 except reward function = ratio reward (k/n)
- Same seed (42), same base model weights
- Save checkpoints at steps 200, 400, 600, 800, 1000

### FR-6: HumanEval Evaluation (Primary Gate Metric)
- Evaluate at checkpoints: steps 200, 400, 600, 800, 1000
- Full HumanEval set: 164 problems (do NOT reduce)
- Greedy decoding: temperature=0, do_sample=False
- Report pass@1 for each condition at each checkpoint
- Primary gate criterion: pass@1(ratio, step=1000) - pass@1(binary, step=1000) ≥ 0.03
- 95% bootstrap CI (n=1000 samples) must exclude 0

### FR-7: MBPP Evaluation (Secondary)
- Evaluate at step 1000 only (compute efficiency)
- Full MBPP test set: 374 problems (do NOT reduce)
- Greedy decoding: temperature=0
- Directional check only (no threshold requirement)
- Dataset: `google-research-datasets/mbpp`, split="test"

### FR-8: APPS Validation All-Pass Rate (Mechanism Signature)
- Evaluate at step 1000
- 500 held-out APPS problems (difficulty-stratified from APPS validation split)
- Metric: fraction of problems where ALL test cases pass
- Gate criterion (P2): ratio_allpass_rate ≤ binary_allpass_rate (policy target shift)
- Dataset: `codeparrot/apps`, split="validation" (first 500 stratified by difficulty)

### FR-9: Training Metrics Logging
- Log every 50 steps: step, reward_mean, reward_std, fraction_partial_correct, grad_norm, kl_divergence
- `fraction_partial_correct`: fraction of completions with reward in (0,1) exclusive — monitors ratio degeneracy
- Alert if fraction_partial → 0 (ratio degeneracy failure mode)
- Output: `training_log_{condition}.csv`

### FR-10: Statistical Analysis
- Bootstrap CI (n=1000) on HumanEval pass@1 gap: `pass@1_ratio - pass@1_binary` at step 1000
- Report: mean gap, 95% CI lower bound, whether CI excludes 0
- APPS all-pass comparison: directional test (ratio ≤ binary)
- Learning curve comparison: HumanEval pass@1 vs step for both conditions

### FR-11: Mechanism Verification Checks
- Pre-training: verify ratio reward returns values in (0,1) for test problems
- During training: check fraction_partial > 0.05 at step 200 (ratio reward active)
- Post-training: compute `verify_h_m1_mechanism(ratio_humaneval, binary_humaneval, ratio_apps_allpass, binary_apps_allpass, ci_lower)`
- Failure mode checks: ratio degeneracy, gradient explosion (grad_norm > 10.0), policy non-divergence

### FR-12: Visualization (Mandatory)
- **Figure 1 (Gate)**: Side-by-side bar chart — HumanEval pass@1 (binary vs ratio at step 1000) AND APPS all-pass rate (binary vs ratio at step 1000) with 95% CI error bars on HumanEval
- **Figure 2 (Dynamics)**: HumanEval pass@1 vs. training step (0-1000) for both conditions, same plot
- **Figure 3 (Distribution)**: Histogram of per-problem test-pass rates (k/n) at step 1000 — binary vs ratio models
- **Figure 4 (Scatter)**: APPS validation per-problem scatter: (binary_pass_rate, ratio_pass_rate) — visualizes policy target divergence
- Output: `docs/youra_research/h-m1/figures/`

---

## Section 2: Non-Functional Requirements

### NFR-1: Compute Budget
- Two full 1000-step training runs (binary + ratio conditions)
- HumanEval evaluations: 5 per condition × 2 conditions = 10 evaluations × 164 problems = 1640 greedy decodes
- MBPP evaluation: 1 per condition × 374 problems = 748 greedy decodes
- APPS val evaluation: 1 per condition × 500 problems (execution-based)
- Total compute: ~40-60 GPU-hours on A100 (estimated)

### NFR-2: Reproducibility
- Fixed seed=42 for all runs
- Identical base model weights for both conditions
- All hyperparameters identical except reward function
- Checkpoint saving enables restart from any 200-step interval

### NFR-3: Code Reuse
- Reuse H-E1 GRPO infrastructure (exit=0 confirmed)
- Reuse binary and ratio reward implementations (validated)
- Reuse APPS preprocessing pipeline (≥5 test case filter)
- Reuse DeepSeek-Coder-6.7B loading code

### NFR-4: Evaluation Correctness
- HumanEval: use `evaluate` (HuggingFace) `code_eval` metric with execution
- Greedy decoding must be deterministic (temperature=0)
- Test execution with 3-second timeout to prevent hanging

---

## Section 3: Data Specification

### Primary Training Dataset
- **APPS**: `codeparrot/apps`, split="train"
- Post-filter size: ~3,500–4,000 problems
- Auto-download via HuggingFace datasets (**no manual download needed**)

### Evaluation Datasets
- **HumanEval**: `openai_humaneval`, split="test" — 164 problems — auto-download
- **MBPP**: `google-research-datasets/mbpp`, split="test" — 374 problems — auto-download
- **APPS validation**: `codeparrot/apps`, split="validation" — first 500 stratified — auto-download

**All datasets auto-download** — no manual download tasks needed.

```python
from datasets import load_dataset
apps_train = load_dataset("codeparrot/apps", split="train")
humaneval = load_dataset("openai_humaneval", split="test")
mbpp = load_dataset("google-research-datasets/mbpp", split="test")
apps_val = load_dataset("codeparrot/apps", split="validation")
```

---

## Section 4: Success Criteria

### Gate Conditions (BOTH required for GATE SATISFIED)

| Gate | Metric | Threshold | Condition |
|------|--------|-----------|-----------|
| P1 (primary) | HumanEval pass@1 gap (ratio - binary) | ≥ 0.03 | AND 95% bootstrap CI lower bound > 0 |
| P2 (mechanism) | APPS all-pass rate comparison | ratio ≤ binary | directional test at step 1000 |

**If P1 fails:** Null finding for H-M1; proceed to H-M2 independently.  
**If P1 passes, P2 fails:** Report anomaly — performance improvement without policy target shift; warrants further investigation.  
**Both pass:** GATE SATISFIED — mechanism confirmed.

### Secondary Success Metrics
- MBPP pass@1 directional advantage for ratio condition (expected but not gated)
- Learning curves show ratio condition monotonically improving or matching binary

---

## Section 5: Failure Detection

| Failure Mode | Detection | Action |
|--------------|-----------|--------|
| Ratio reward degeneracy | fraction_partial → 0 at any checkpoint | Report; continue; note in results |
| Gradient explosion | grad_norm > 10.0 | Stop run; investigate KL β adjustment |
| No policy target shift | ratio_allpass ≈ binary_allpass | P2 fails; report null mechanism |
| HumanEval regression | ratio pass@1 < baseline SFT | Report unexpected regression |

---

## Section 6: Experiment Conditions Summary

| Parameter | Binary Condition | Ratio Condition |
|-----------|-----------------|-----------------|
| Reward function | `float(all_pass)` | `sum(pass_i)/n` |
| Training steps | 1000 | 1000 |
| Group size G | 8 | 8 |
| Learning rate | 1e-6 | 1e-6 |
| KL β | 0.04 | 0.04 |
| Seed | 42 | 42 |
| Model | DeepSeek-Coder-6.7B-instruct | DeepSeek-Coder-6.7B-instruct |

All parameters identical except reward function.

---

## Section 7: Dependencies

### 7.1 Python Packages
```
torch>=2.0
transformers>=4.40
trl>=0.8
datasets>=2.18
evaluate
accelerate
numpy
scipy
matplotlib
pandas
```

### 7.2 External Repositories (Reference Only)
- DAPO: https://github.com/BytedanceSeed/DAPO (training protocol reference)
- TRL: https://github.com/huggingface/trl (GRPOTrainer)
- CodeRL: https://github.com/salesforce/CodeRL (binary reward baseline reference)

### 7.3 H-E1 Code Reuse
- Base path: `docs/youra_research/h-e1/code/`
- Components to reuse: GRPO training loop, reward functions, APPS preprocessing, model loading

---

## Section 8: Incremental Context (from H-E1)

**H-E1 confirmed:**
- Ratio reward generates differentiated gradient signal (advantage variance 0.0475 vs 0.0 for partially-correct groups)
- 98.7% of early-training GRPO groups receive different signals under ratio vs binary
- GRPO infrastructure works (smoke test exit=0)
- Binary and ratio reward implementations are correct

**H-M1 extends by:**
- Full training: 1000 steps (vs H-E1 200-step checkpoint)
- Full evaluation: HumanEval (164), MBPP (374), APPS-val all-pass (500)
- Policy-level behavioral measurement (not just gradient signal)
