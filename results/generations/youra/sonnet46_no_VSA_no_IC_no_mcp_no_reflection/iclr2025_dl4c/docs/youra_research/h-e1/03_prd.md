# Product Requirements Document: H-E1
## Binary vs Ratio Reward Signal in GRPO Training for DeepSeek-Coder-6.7B

**Hypothesis:** H-E1  
**Type:** EXISTENCE (PoC)  
**Date:** 2026-08-31  
**Author:** Anonymous  
**Source:** 02c_experiment_brief.md  

---

## Executive Summary

This PRD specifies requirements for a controlled PoC experiment comparing binary reward (0/1 pass/fail) versus ratio reward (k/n test cases passing) as training signal in GRPO post-training of DeepSeek-Coder-6.7B-instruct on the APPS dataset. The experiment measures whether ratio reward produces detectably different gradient norms and HumanEval pass@1 compared to binary reward within ≤500 training steps. This is an EXISTENCE hypothesis — the goal is detection of signal difference, not performance optimization.

---

## Problem Statement

GRPO-based RLEF for code LLMs universally uses binary pass/fail reward. When all completions in a GRPO group fail all tests, binary reward assigns identical zero reward to all completions → zero gradient → no learning signal for that group. Ratio reward (k/n) assigns non-zero reward to partially-correct completions even within all-failing groups, potentially providing a non-zero gradient in more training steps. The question is whether this translates to a measurable training signal difference within 500 steps.

---

## Section 1: Functional Requirements

### FR-1: Data Pipeline — APPS Dataset Loading and Filtering
- Load APPS train split from HuggingFace (`codeparrot/apps`)
- Filter to retain problems with ≥5 distinct, non-redundant test cases
- Expected post-filter size: ~3,000–4,000 problems
- Format prompt: `{problem_description}\n\nWrite a Python solution:`
- Truncate descriptions >1024 tokens

### FR-2: Model Loading — DeepSeek-Coder-6.7B-instruct
- Load `deepseek-ai/deepseek-coder-6.7b-instruct` via HuggingFace transformers
- dtype: bfloat16
- device_map: auto
- Load corresponding tokenizer
- Both experimental conditions use identical base weights

### FR-3: Reward Function Implementation
- **Binary reward**: `float(all_tests_pass)` — 1.0 if all test cases pass, else 0.0
- **Ratio reward**: `sum(test_i_passes) / len(test_cases)` — fraction of test cases passing
- Code execution sandbox: subprocess with 5-second timeout
- Graceful handling of syntax errors, runtime errors, timeout

### FR-4: GRPO Training — Binary Condition
- Use HuggingFace trl GRPOTrainer with binary reward function
- Group size G=8 completions per prompt
- Prompt batch size: 64
- max_new_tokens: 512, temperature: 1.0 during rollout
- Learning rate: 1e-6, AdamW, weight_decay=0.01
- Warmup: 10 steps
- Clip ratio ε=0.2, KL β=0.01
- Train for 500 steps
- Log per-step gradient norm to `gradient_norms_binary.csv`
- Save checkpoint at step 200

### FR-5: GRPO Training — Ratio Condition
- Identical to FR-4 except reward function = ratio reward
- Same seed (42), same base model weights
- Log to `gradient_norms_ratio.csv`
- Save checkpoint at step 200

### FR-6: Gradient Norm Logging
- Log every training step (steps 1–500): `{global_step, grad_norm, mean_reward, std_reward}`
- Output CSV format: `gradient_norms_{condition}.csv`
- Capture gradient norm BEFORE clipping via trainer callback

### FR-7: HumanEval Evaluation at Step 200
- Load step-200 checkpoint for each condition
- Greedy decode (temperature=0, do_sample=False) on all 164 HumanEval problems
- Report pass@1 for each condition
- Use `human-eval` package or `bigcode-evaluation-harness`

### FR-8: Statistical Analysis
- Bootstrap CI (n=1,000 samples) on gradient norm difference: `norm_ratio[t] - norm_binary[t]` for t ∈ [100, 500]
- Report: mean difference, 95% CI bounds, whether CI excludes 0
- HumanEval difference: `|pass@1_ratio - pass@1_binary|` ≥ 0.01 (1pp)

### FR-9: Visualization
- **Required**: Bar chart — binary vs ratio HumanEval pass@1 at step 200
- **Additional**: Gradient norm trajectory (steps 1–500) with 95% bootstrap CI shading
- **Additional**: Reward distribution histograms at steps 50, 100, 200, 500
- **Additional**: Mean group reward over training steps
- Output location: `docs/youra_research/h-e1/figures/`

### FR-10: Results Reporting
- Summary table: metric, binary value, ratio value, difference, CI
- Gate evaluation: PRIMARY (gradient norm CI) + SECONDARY (HumanEval 1pp)
- Output: `docs/youra_research/h-e1/04_validation.md`

---

## Section 2: Ablation Variants

| Variant ID | Description | Purpose |
|------------|-------------|---------|
| AV-1 | Binary reward (binary_condition) | Baseline — standard GRPO |
| AV-2 | Ratio reward (ratio_condition) | Treatment — proposed signal |

These are the two conditions; no additional ablations for EXISTENCE hypothesis.

---

## Section 3: Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed seed=42 for both conditions
- Deterministic data filtering (same filtered dataset used for both conditions)
- Log all hyperparameters to `experiment_config.yaml`

### NFR-2: Compute Efficiency
- Both conditions must complete 500 training steps within reasonable wall time
- Code execution sandbox: 5-second timeout per test case
- Expected training: ~6–12 hours per condition on single A100

### NFR-3: Error Handling
- Sandbox must catch: syntax errors, runtime exceptions, TLE, OOM in generated code
- Training must be resumable from checkpoints
- Log failures in reward computation with fallback reward=0.0

### NFR-4: Isolation
- Both conditions run from identical initial model state
- No shared mutable state between conditions

---

## Section 4: Data Specification

### Primary Dataset: APPS
- Source: HuggingFace `codeparrot/apps`
- Split: train (5,000 problems raw, ~3,000–4,000 after filter)
- Filter criterion: ≥5 distinct, non-redundant test cases
- Non-redundancy: distinct expected outputs or distinct input edge cases
- Load method: `datasets.load_dataset("codeparrot/apps", split="train")`
- **Manual download required**: No — HuggingFace auto-download
- Preprocessing: prompt formatting, description truncation at 1024 tokens

### Evaluation Dataset: HumanEval
- Source: `openai/human-eval` package or HuggingFace
- Problems: 164
- Load method: `human_eval` package or `datasets.load_dataset("openai_humaneval")`
- **Manual download required**: No — auto-download via package

### Static Baseline
- DeepSeek-Coder-6.7B-instruct pre-training HumanEval pass@1: ~52% (from literature)
- Used as reference point; not re-evaluated (known value)

---

## Section 5: Success Criteria

### Gate: MUST_WORK

**PRIMARY (sufficient alone):**
- Gradient norm bootstrap CI (95%) excludes 0 at ≥1 step in t ∈ [100, 500]

**SECONDARY (sufficient alone):**
- |HumanEval pass@1_ratio − pass@1_binary| ≥ 0.01 at step 200

**Minimum PoC Pass:**
- Both conditions complete 500 training steps without error
- At least one gate criterion satisfied

---

## Section 6: Out of Scope

- Optimization for best HumanEval performance (this is detection, not optimization)
- Evaluation on MBPP, MBPP+, or other benchmarks
- Multi-seed runs (single seed=42 for EXISTENCE PoC)
- Fine-tuning hyperparameter search
- Evaluation beyond step 200 checkpoint

---

## Section 7: Dependencies

### 7.1 Python Packages
```
torch>=2.0
transformers>=4.40
trl>=0.8  # GRPOTrainer
datasets>=2.18
human-eval  # or bigcode-evaluation-harness
numpy
scipy
matplotlib
pandas
accelerate
```

### 7.2 External Repositories (Reference)
- HuggingFace trl: https://github.com/huggingface/trl (GRPOTrainer)
- OpenRLHF: https://github.com/OpenRLHF/OpenRLHF (fallback)
- human-eval: https://github.com/openai/human-eval

### 7.3 Infrastructure
- GPU: ≥1× A100 80GB (or equivalent) for 6.7B model training
- Storage: ~50GB for model weights, checkpoints, dataset

---

## Section 8: Assumptions

- A1: APPS filtering retains ≥2,000 problems with ≥5 test cases (sufficient training data)
- A2: trl GRPOTrainer supports custom reward function returning float list
- A3: DeepSeek-Coder-6.7B-instruct loads in bfloat16 on available GPU
- A4: Gradient norm difference is detectable within 500 steps (from hypothesis mechanism analysis)

---

*stepsCompleted: [Step1-ExecutiveSummary, Step2-ProblemStatement, Step3-FunctionalRequirements, Step4-DataSpec, Step5-SuccessCriteria, Step6-OutOfScope, Step7-Dependencies]*
