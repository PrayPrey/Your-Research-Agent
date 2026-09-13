# Product Requirements Document: H-E1
# Difficulty-Stratified Curriculum GRPO — Existence Validation

**Hypothesis ID:** H-E1
**Type:** EXISTENCE (PoC)
**Gate:** MUST_WORK
**Generated:** 2026-05-02
**Phase:** 3 — Implementation Planning

---

## 1. Executive Summary

Implement and run a 4-condition comparison experiment to determine whether difficulty-stratified curriculum ordering (easy→hard) improves code generation performance under GRPO training with execution feedback. The experiment trains DeepSeek-Coder-7B-base on APPS+CodeContests under 4 conditions and evaluates pass@1 on HumanEval+ (164 problems) at the final checkpoint.

**Success criterion:** Curriculum condition pass@1 ≥ Uniform condition pass@1 + 2pp (McNemar's test, p<0.05, one-tailed).

---

## 2. Problem Statement

GRPO training with execution feedback suffers from "degenerate steps" when all G=8 completions fail (std=0, advantage=0, zero gradient). Easy problems early in training maintain higher reward density (non-zero std), potentially producing more effective policy gradient updates. This PoC tests whether a fixed easy→hard difficulty schedule improves final pass@1.

---

## 3. Functional Requirements

### FR-1: Dataset Loading and Preprocessing

- **FR-1.1**: Load APPS train split from `hendrycks/apps` via HuggingFace datasets
- **FR-1.2**: Load CodeContests train split from `google-deepmind/code_contests` via HuggingFace datasets
- **FR-1.3**: Filter APPS by difficulty tier:
  - Easy pool: tiers 0-2 (~3,000 problems)
  - Hard pool: tiers 3-4 (~2,000 problems)
- **FR-1.4**: Filter CodeContests by division:
  - Easy pool: Div 2 problems
  - Hard pool: Div 1 problems
- **FR-1.5**: Filter out problems with no unit tests (required for execution reward)
- **FR-1.6**: Tokenize prompts: problem description + function signature (max 512 tokens)
- **FR-1.7**: Construct 4 training datasets corresponding to 4 conditions

### FR-2: CurriculumDataset Module

- **FR-2.1**: Implement `CurriculumDataset(torch.utils.data.Dataset)` with:
  - `easy_data`: APPS tiers 0-2 + CC Div2
  - `hard_data`: APPS tiers 3-4 + CC Div1
  - `curriculum_step`: phase switch point (default=2500)
  - `set_step(step: int)`: switches active_data at curriculum_step
- **FR-2.2**: `UniformDataset`: full pool with uniform random sampling
- **FR-2.3**: `EasyOnlyDataset`: only easy pool throughout
- **FR-2.4**: `HardOnlyDataset`: only hard pool throughout

### FR-3: Training Loop

- **FR-3.1**: Use TRL GRPOTrainer with custom execution reward function
- **FR-3.2**: GRPO configuration:
  - `num_generations=8` (G=8)
  - `max_new_tokens=512`
  - `temperature=1.0` (training)
  - `learning_rate=1e-6`
  - `per_device_train_batch_size=1`
  - `gradient_accumulation_steps=8`
  - `max_steps=5000`
- **FR-3.3**: Binary execution reward: `r=1.0` if all unit tests pass, `r=0.0` otherwise
- **FR-3.4**: GRPO advantage: `A_i = (r_i - mean(r)) / (std(r) + 1e-8)`
- **FR-3.5**: Save checkpoint every 500 steps (10 checkpoints per condition)
- **FR-3.6**: Fixed seed=42 for reproducibility

### FR-4: CurriculumCallback

- **FR-4.1**: Implement `CurriculumCallback(TrainerCallback)` that calls `dataset.set_step(state.global_step)` at `on_step_begin`
- **FR-4.2**: Log phase switch event: `"Curriculum phase: switching to hard_data at step 2500"`

### FR-5: Reward Density Logging

- **FR-5.1**: Log reward density per step: `fraction of batches where std(rewards_in_group) > 0`
- **FR-5.2**: Save reward density log to `logs/reward_density_{condition}.csv`
- **FR-5.3**: Required for downstream H-M1 hypothesis validation

### FR-6: Evaluation

- **FR-6.1**: Evaluate each checkpoint with EvalPlus on HumanEval+ (164 problems)
  - Greedy decoding (temperature=0.0)
  - CLI: `python -m evalplus.evaluate --model <checkpoint> --dataset humaneval --greedy`
- **FR-6.2**: Evaluate final checkpoint on MBPP+ (378 problems)
- **FR-6.3**: Parse pass@1 from EvalPlus JSON output
- **FR-6.4**: Save results to `results/eval_results_{condition}.json`

### FR-7: Statistical Testing

- **FR-7.1**: Run McNemar's test comparing Curriculum vs Uniform on HumanEval+ final checkpoint
- **FR-7.2**: Report p-value (one-tailed), effect size (percentage point difference)
- **FR-7.3**: Gate check: `curriculum_pass@1 >= uniform_pass@1 + 0.02` AND `p < 0.05`

### FR-8: Visualization

- **FR-8.1**: Bar chart: Curriculum vs Uniform final pass@1 on HumanEval+ (mandatory gate metric)
- **FR-8.2**: Learning curves: pass@1 vs training step for all 4 conditions
- **FR-8.3**: Reward density over time: all 4 conditions, steps 0-5000
- **FR-8.4**: Condition comparison table: final pass@1 HumanEval+ and MBPP+
- **FR-8.5**: Save all figures to `h-e1/figures/`

---

## 4. Data Specification

### 4.1 Training Datasets (Manual Download Required)

| Dataset | Source | HuggingFace ID | Split | Size |
|---------|--------|----------------|-------|------|
| APPS | Hendrycks et al. 2021 | `hendrycks/apps` | train | ~5,000 problems |
| CodeContests | Google DeepMind 2022 | `google-deepmind/code_contests` | train | ~13,000 problems |

**Loading code:**
```python
from datasets import load_dataset
apps = load_dataset("hendrycks/apps", split="train")
code_contests = load_dataset("google-deepmind/code_contests", split="train")
easy_apps = apps.filter(lambda x: x["difficulty"] in [0, 1, 2])
hard_apps = apps.filter(lambda x: x["difficulty"] in [3, 4])
```

### 4.2 Evaluation Datasets (Auto-downloaded by EvalPlus)

| Dataset | Problems | Source |
|---------|----------|--------|
| HumanEval+ | 164 | EvalPlus (Liu et al. 2023) |
| MBPP+ | 378 | EvalPlus (Liu et al. 2023) |

### 4.3 Model Download

| Model | HuggingFace ID | Size |
|-------|----------------|------|
| DeepSeek-Coder-7B-base | `deepseek-ai/deepseek-coder-7b-base-v1.5` | 7B params |

---

## 5. Non-Functional Requirements

- **NFR-1**: Single GPU execution (CUDA_VISIBLE_DEVICES set to one empty GPU)
- **NFR-2**: Memory: DeepSeek-Coder-7B in bfloat16 fits on A100 80GB with batch_size=1
- **NFR-3**: Runtime: ~8-12 hours per condition on A100 80GB (total ~40 GPU-hours)
- **NFR-4**: Checkpoint storage: 10 checkpoints × 4 conditions × ~14GB = ~560GB
- **NFR-5**: Infrastructure tier: LIGHT (minimal — argparse config, print + CSV logging, smoke test)

---

## 6. Success Criteria

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| PoC Runs | All 4 conditions complete 5000 steps | No runtime errors |
| Mechanism Activated | Phase switch logged at step 2500 | Log check |
| Effect Direction | Curriculum pass@1 > Uniform pass@1 | Final checkpoint |
| Gate (MUST_WORK) | Curriculum pass@1 ≥ Uniform + 2pp, p<0.05 | McNemar's test |
| Reward Density Logged | 5000 entries per condition | CSV file check |

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.0.0
transformers>=4.40.0
trl>=0.8.0
datasets>=2.14.0
evalplus>=0.3.0
scipy>=1.10.0
matplotlib>=3.7.0
pandas>=2.0.0
numpy>=1.24.0
pytest>=7.0.0
```

### 7.2 External Repositories (Reference)

| Repo | URL | Purpose |
|------|-----|---------|
| huggingface/trl | https://github.com/huggingface/trl | GRPOTrainer framework |
| deepseek-ai/DeepSeek-R1 | https://github.com/deepseek-ai/DeepSeek-R1 | GRPO reference implementation |
| evalplus/evalplus | https://github.com/evalplus/evalplus | HumanEval+/MBPP+ evaluation |

---

## 8. Ablation Conditions

| Condition ID | Name | Steps 0-2500 | Steps 2501-5000 | Purpose |
|-------------|------|-------------|-----------------|---------|
| C1 | Curriculum (proposed) | Easy pool | Hard pool | Main hypothesis |
| C2 | Uniform (baseline) | Full pool random | Full pool random | Control |
| C3 | Easy-only (ablation) | Easy pool | Easy pool | Ablation |
| C4 | Hard-only (ablation) | Hard pool | Hard pool | Ablation |

---

## 9. File Structure

```
h-e1/
├── code/
│   ├── data/
│   │   ├── dataset.py          # CurriculumDataset, UniformDataset, EasyOnlyDataset, HardOnlyDataset
│   │   └── preprocessing.py    # Filter, tokenize APPS+CodeContests
│   ├── training/
│   │   ├── train.py            # Main training script (argparse)
│   │   ├── reward.py           # Execution reward function
│   │   └── callbacks.py        # CurriculumCallback, RewardDensityCallback
│   ├── evaluation/
│   │   ├── evaluate.py         # EvalPlus wrapper, McNemar's test
│   │   └── visualize.py        # Figures generation
│   └── config.py               # Hardcoded CONFIG dict
├── logs/
│   └── reward_density_{condition}.csv
├── results/
│   └── eval_results_{condition}.json
└── figures/
    ├── gate_metric_comparison.png
    ├── learning_curves.png
    ├── reward_density.png
    └── condition_comparison_table.png
```

---

*PRD generated inline (BMAD BMM not available in TEST_dl4c no-mcp environment)*
*Source: 02c_experiment_brief.md*
*Phase 3 — H-E1 EXISTENCE PoC*
