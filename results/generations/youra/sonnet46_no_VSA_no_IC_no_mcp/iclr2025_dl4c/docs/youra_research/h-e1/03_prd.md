---
title: "PRD: H-E1 — RLEF-Fraction Difficulty-Scaling Existence Proof"
hypothesis_id: H-E1
hypothesis_type: EXISTENCE
tier: LIGHT
stepsCompleted:
  - prd-executive-summary
  - prd-problem-statement
  - prd-functional-requirements
  - prd-non-functional-requirements
  - prd-data-specification
  - prd-evaluation-metrics
  - prd-dependencies
  - prd-success-criteria
date: "2026-08-26"
author: yoon303@ust.ac.kr
source: 02c_experiment_brief.md
---

# PRD: H-E1 — RLEF-Fraction Difficulty-Scaling Existence Proof

## 1. Executive Summary

This PRD defines the implementation requirements for **H-E1**, a proof-of-concept (PoC) experiment verifying that RLEF with a fraction-of-tests-passing reward (RLEF-Fraction) yields disproportionately larger improvements on harder coding benchmarks compared to easy benchmarks, relative to a matched SFT baseline.

**Core claim (gate condition):**
> Δ(RLEF-Fraction, SFT) at LiveCodeBench-Medium/Hard ≥ 1.5× Δ(RLEF-Fraction, SFT) at HumanEval, with bootstrap 95% CI lower bound > 1.0 (p < 0.05 equivalent).

**Approach:** Train DeepSeek-Coder-7B-base with (a) SFT on APPS solutions and (b) GRPO with fraction-of-tests reward on APPS. Evaluate both on 5 benchmarks (HumanEval, MBPP, LCB-Easy, LCB-Medium, LCB-Hard). Compute Δ ratio and bootstrap CI.

---

## 2. Problem Statement

### 2.1 Research Gap

The hypothesis of "difficulty-scaling" — that online RLEF provides disproportionate benefit on harder problems — is supported by RLEF-2024 (Gehring et al., Meta 2024) but with non-public code. No open-source reproducible study confirms this phenomenon using a standard GRPO-based fraction reward on a public LLM and public benchmarks.

### 2.2 What This PoC Answers

**Question:** Does the difficulty-scaling phenomenon exist under controlled, reproducible open-source conditions?

**Not answered here:** Why the phenomenon occurs (H-M1), whether fraction reward is responsible (H-M3), or how it scales (H-M4). This is existence-only.

### 2.3 Controlled Conditions

| Factor | Fixed Value |
|--------|-------------|
| Base model | DeepSeek-Coder-7B-base |
| Training data | APPS train split (5,000 problems) |
| Evaluation harness | bigcode-evaluation-harness (correctness-only) |
| Gradient steps | Matched between SFT and RLEF-Fraction |
| Random seed | 42 (single seed, PoC) |

---

## 3. Functional Requirements

### FR-1: Data Pipeline

**FR-1.1: APPS Dataset Loading**
- Load `codeparrot/apps` via HuggingFace datasets
- Split: use `train` split (5,000 problems)
- Filter: retain only problems with ≥ 1 test case (ensures non-zero reward signal)
- Format for SFT: `(prompt=problem_description, target=canonical_solution)`
- Format for RLEF: `(prompt=problem_description, test_cases=list_of_(input, expected_output))`
- Tokenization: DeepSeek-Coder tokenizer, max_length=1024

**FR-1.2: Evaluation Benchmarks (no download task — harness handles)**
- HumanEval: 164 problems (OpenAI 2021)
- MBPP: 374 problems (Google 2021)
- LiveCodeBench-Easy: ~400 problems (2024 Q4 snapshot)
- LiveCodeBench-Medium: ~400 problems (2024 Q4 snapshot)
- LiveCodeBench-Hard: ~200 problems (2024 Q4 snapshot)

### FR-2: Baseline (SFT) Training

**FR-2.1: Pre-experiment Ceiling Check**
- Evaluate zero-shot DeepSeek-Coder-7B-base on HumanEval before training
- If pass@1 ≥ 90%: switch to DeepSeek-Coder-1.3B-base
- Expected: ~30–40% (well below ceiling)

**FR-2.2: SFT Training**
- Model: `deepseek-ai/deepseek-coder-7b-base` in bfloat16
- Loss: cross-entropy on canonical solutions
- Data: APPS train (5,000 problems)
- Hyperparameters: AdamW lr=1e-5, effective batch=32 (4 × 8 grad_accum), 3 epochs, cosine schedule with 100-step warmup, gradient clipping max_norm=1.0, seed=42
- Output: `checkpoints/sft_baseline/`

### FR-3: Proposed Method (RLEF-Fraction) Training

**FR-3.1: Fraction-of-Tests Reward Function**
- For each model completion, execute against APPS test cases (timeout=3.0s per test)
- Reward = (number of tests passed) / (total tests)
- Returns float in [0.0, 1.0]; 0.0 if no test cases or all exceptions
- Execution: isolated subprocess with `python` interpreter, stdin injection

**FR-3.2: GRPO Training**
- Base model: `deepseek-ai/deepseek-coder-7b-base` in bfloat16
- Framework: TRL GRPOTrainer
- Config: lr=1e-5, effective batch=32 (4 × 8 grad_accum), 3 epochs, G=8 rollouts per prompt, β=0.04 KL penalty, max_grad_norm=1.0, max_new_tokens=512, temperature=0.8 (rollout), seed=42
- Matched gradient steps to SFT baseline
- Output: `checkpoints/rlef_fraction/`

**FR-3.3: Reward Monitoring Callback (required for H-M2 data)**
- TRL callback logging per-batch: mean reward stratified by APPS difficulty bucket (intro/interview/competition)
- Saved to: `logs/reward_monitoring.jsonl`
- Format: `{"step": int, "intro_reward": float, "interview_reward": float, "competition_reward": float}`

### FR-4: Evaluation

**FR-4.1: Evaluation of Both Models**
- Evaluate both `sft_baseline` and `rlef_fraction` checkpoints on all 5 benchmarks
- Tool: bigcode-evaluation-harness (correctness-only mode)
- Metric: pass@1 with n_samples=1, temperature=0.2 (greedy)
- Invocation per benchmark:
```bash
accelerate launch main.py \
  --model {checkpoint_path} \
  --tasks {task_name} \
  --n_samples 1 \
  --temperature 0.2 \
  --allow_code_execution \
  --metric_output_path results/h-e1/{model}_{task}.json
```
- Task names: `humaneval`, `mbpp`, `livecodebench` (with difficulty filter)
- Pin bigcode-harness commit for reproducibility (store in requirements)

**FR-4.2: Δ Computation**
```python
delta_humaneval = rlef_humaneval_pass1 - sft_humaneval_pass1
delta_lcb_medium_hard = (
    (rlef_lcb_medium_pass1 + rlef_lcb_hard_pass1) / 2 -
    (sft_lcb_medium_pass1 + sft_lcb_hard_pass1) / 2
)
delta_ratio = delta_lcb_medium_hard / delta_humaneval
```

**FR-4.3: Bootstrap CI**
- Bootstrap 1,000 resamples on per-problem pass/fail vectors
- Report: 95% CI on Δ_ratio; p-value equivalent (fraction of bootstrap samples with ratio ≥ 1.5)
- Gate: CI lower bound > 1.0 and Δ_ratio ≥ 1.5

### FR-5: Visualization

**FR-5.1: Gate Metrics Comparison (mandatory)**
- Bar chart: Δ pass@1 (RLEF-Fraction − SFT) for each benchmark
- Error bars: 95% CI from bootstrap
- Threshold line: Δ ratio = 1.5
- Save: `docs/youra_research/h-e1/figures/gate_metrics.png`

**FR-5.2: Difficulty-Scaling Plot (autonomous)**
- Line graph: pass@1 (y) vs difficulty level (x: HumanEval, MBPP, LCB-Easy, LCB-Med, LCB-Hard) for both SFT and RLEF-Fraction
- Save: `docs/youra_research/h-e1/figures/difficulty_scaling.png`

**FR-5.3: Training Reward Curve (autonomous)**
- Line graph: per-epoch mean fraction reward stratified by APPS difficulty bucket
- Source: `logs/reward_monitoring.jsonl`
- Save: `docs/youra_research/h-e1/figures/reward_curve.png`

**FR-5.4: Bootstrap Distribution (autonomous)**
- Histogram: bootstrap distribution of Δ_LCB/Δ_HumanEval with 1.5× threshold marked
- Save: `docs/youra_research/h-e1/figures/bootstrap_ratio.png`

---

## 4. Data Specification

### 4.1 Training Dataset

| Field | Value |
|-------|-------|
| Name | APPS (Automated Programming Progress Standard) |
| HuggingFace ID | `codeparrot/apps` |
| Split used | `train` (5,000 problems) |
| Manual download? | **NO** — HuggingFace auto-download |
| Filter | ≥ 1 test case |
| Languages | Python only |
| Difficulty buckets | intro / interview / competition |

### 4.2 Evaluation Datasets

All evaluation datasets are handled by bigcode-evaluation-harness (auto-managed). No manual download required.

| Dataset | HF/Source | Auto-managed |
|---------|-----------|-------------|
| HumanEval | openai_humaneval | ✓ |
| MBPP | google-research-datasets/mbpp | ✓ |
| LiveCodeBench 2024-Q4 | livecodebench/code_generation_lite | ✓ |

---

## 5. Evaluation Metrics

### 5.1 Primary Gate Metric

| Metric | Computation | Gate |
|--------|-------------|------|
| Δ_ratio | (Δ_LCB_Med_Hard) / (Δ_HumanEval) | ≥ 1.5 |
| Bootstrap 95% CI lower | percentile(bootstrap_ratios, 2.5) | > 1.0 |

### 5.2 Secondary Metrics

| Metric | Requirement |
|--------|-------------|
| Δ_HumanEval | > 0 (RLEF improves over SFT) |
| Δ_LCB_Med_Hard | > 0 (positive improvement) |
| Individual benchmark pass@1 | Reported for all 5 benchmarks |

### 5.3 Diagnostic Metrics

- Per-difficulty APPS reward curve (from FR-3.3 callback)
- Training loss curves (SFT and RLEF)

---

## 6. Non-Functional Requirements

### NFR-1: Reproducibility
- All random seeds fixed at 42
- bigcode-harness commit pinned in `requirements.txt`
- All hyperparameters logged to `logs/config_dump.json` at training start
- APPS filter criteria documented and deterministic

### NFR-2: Computational Budget
- Target: runnable on single A100 80GB GPU (or 2× A100 40GB with FSDP)
- bfloat16 precision for all training
- Gradient checkpointing if needed for 7B model
- APPS execution timeout hard-coded at 3.0s to prevent runaway processes

### NFR-3: Safety
- Code execution sandboxed in subprocess (no `exec()` in-process)
- `ulimit` or resource limits on subprocess execution
- Timeout enforced via `subprocess.run(..., timeout=3.0)`

### NFR-4: Data Organization
```
docs/youra_research/h-e1/
├── 02c_experiment_brief.md
├── 03_prd.md
├── 03_architecture.md
├── 03_logic.md
├── 03_config.md
├── figures/
│   ├── gate_metrics.png
│   ├── difficulty_scaling.png
│   ├── reward_curve.png
│   └── bootstrap_ratio.png
└── code/
    ├── data_utils.py
    ├── reward.py
    ├── train_sft.py
    ├── train_rlef.py
    ├── evaluate.py
    ├── analyze.py
    └── requirements.txt

checkpoints/
├── sft_baseline/
└── rlef_fraction/

results/h-e1/
└── {model}_{task}.json

logs/
├── reward_monitoring.jsonl
└── config_dump.json
```

---

## 7. Dependencies

### 7.1 Python Packages

```txt
# Core training
torch>=2.1.0
transformers>=4.40.0
trl>=0.8.6
peft>=0.10.0
accelerate>=0.27.0
datasets>=2.18.0
bitsandbytes>=0.43.0

# Evaluation
# bigcode-evaluation-harness (pinned commit — see 7.2)

# Analysis & visualization
scipy>=1.11.0
numpy>=1.26.0
matplotlib>=3.8.0
seaborn>=0.13.0
pandas>=2.0.0
pyyaml>=6.0
tqdm>=4.66.0
```

### 7.2 External Repositories

| Repo | Purpose | Pin strategy |
|------|---------|-------------|
| `huggingface/trl` | GRPOTrainer (pip install trl) | version pin |
| `bigcode-project/bigcode-evaluation-harness` | Evaluation | git clone + commit pin |

**bigcode-harness setup:**
```bash
git clone https://github.com/bigcode-project/bigcode-evaluation-harness.git
cd bigcode-evaluation-harness
git checkout {PINNED_COMMIT}  # record commit in requirements
pip install -e ".[vllm]"
```

### 7.3 Hardware

| Resource | Minimum | Recommended |
|---------|---------|-------------|
| GPU | 1× A100 40GB | 1× A100 80GB |
| RAM | 64GB | 128GB |
| Storage | 100GB | 200GB |
| Python | 3.10+ | 3.11 |

---

## 8. Success Criteria

### PoC Pass Conditions (ALL required)

1. **Code correctness:** All scripts run without error (SFT training, RLEF-Fraction training, all 5 benchmark evaluations, analysis)
2. **Gate condition:** Δ_LCB_Med_Hard / Δ_HumanEval ≥ 1.5
3. **Statistical validity:** Bootstrap 95% CI lower bound > 1.0 (p < 0.05 equivalent)

### Fail Action

If gate not met: STOP — difficulty-scaling phenomenon not demonstrated; reassess entire hypothesis chain before proceeding to H-M1/H-M2/etc.

### Phase 2C Completeness Check

| Item | Covered in FRs |
|------|---------------|
| SFT baseline model | FR-2.2 ✓ |
| RLEF-Fraction model | FR-3.2 ✓ |
| APPS training dataset | FR-1.1 ✓ |
| HumanEval evaluation | FR-4.1 ✓ |
| MBPP evaluation | FR-4.1 ✓ |
| LiveCodeBench-Easy | FR-4.1 ✓ |
| LiveCodeBench-Medium | FR-4.1 ✓ |
| LiveCodeBench-Hard | FR-4.1 ✓ |
| Fraction reward function | FR-3.1 ✓ |
| Δ computation | FR-4.2 ✓ |
| Bootstrap CI | FR-4.3 ✓ |
| Reward monitoring callback | FR-3.3 ✓ |
| Visualization (4 figures) | FR-5.1–5.4 ✓ |
| Ceiling check | FR-2.1 ✓ |
