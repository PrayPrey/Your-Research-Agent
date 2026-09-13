# Product Requirements Document: H-E2
# SFT Training Source Ablation Study

**Hypothesis ID:** H-E2
**Type:** EXISTENCE (MUST_WORK gate)
**Date:** 2026-08-02
**Author:** Anonymous
**Phase:** 3 — Implementation Planning

---

## 1. Executive Summary

This experiment tests whether SFT training source identity (HumanEval-only vs MBPP-only vs LeetCode-only vs Equal-mix) produces a statistically significant main effect on pass@1 at 1.3B scale. We train 12 models (4 source conditions × 3 seeds) using TRL SFTTrainer on DeepSeek-Coder-1.3B-Base, evaluate on HumanEval+ (164 tasks) and MBPP+ (378 tasks) via EvalPlus greedy decoding, and test significance via a linear mixed-effects model. Minimum detectable effect: ≥2.0 absolute percentage points.

---

## 2. Problem Statement

Does the identity of SFT training data source significantly affect code generation benchmark performance at 1.3B scale? If yes (gate PASS), downstream mechanism and comparison hypotheses proceed. If all pairwise contrasts fall within ±1.5 pp across both benchmarks and all seeds, the pipeline routes back to Phase 0.

---

## 3. Functional Requirements

### FR-01: Data Pipeline — Training Source Construction

**4 Mutually Exclusive Training Conditions:**

| Condition ID | Source Dataset | HuggingFace ID | Expected Size |
|---|---|---|---|
| `humaneval_only` | HumanEval problems (train split) | `openai/openai_humaneval` | ~164 problems pre-dedup |
| `mbpp_only` | MBPP sanitized (train split) | `google-research-datasets/mbpp` (sanitized) | ~374 train problems |
| `leetcode_only` | LeetCodeDataset Python subset | `newfacade/LeetCodeDataset` | ~2,869 Python problems |
| `equal_mix` | 1/4 from each above source | combined | balanced mixture |

**Data Preparation Pipeline (per condition):**
1. Load raw source from HuggingFace
2. Deduplicate against HumanEval+ + MBPP+ test sets (cosine similarity > 0.95 using all-MiniLM-L6-v2 → remove)
3. Downsample to equal problem count across conditions (≤164 post-dedup, limited by HumanEval-only)
4. Apply uniform prompt template: `"# Complete the following Python function:\n{docstring}\n{function_signature}"`
5. Repeat to equalize total training tokens across conditions

**Token budget equalization target epochs (approximate):**
- HumanEval-only: ~5–8 epochs
- MBPP-only: ~3 epochs
- LeetCode-only: ~1 epoch
- Equal-mix: ~2–3 epochs

### FR-02: SFT Training Module

**Model:** `deepseek-ai/deepseek-coder-1.3b-base`

**Training Framework:** TRL SFTTrainer + Accelerate + DeepSpeed ZeRO-3

**Fixed Hyperparameters (same across all 12 runs):**

| Hyperparameter | Value | Source |
|---|---|---|
| `learning_rate` | 2e-5 | DeepSeek-Coder finetune + ESONG1999 ref |
| `lr_scheduler_type` | cosine | Standard |
| `warmup_ratio` | 0.05 | Standard |
| `per_device_train_batch_size` | 4 | Multi-GPU scaled |
| `gradient_accumulation_steps` | 4 | Effective BS=16 per GPU |
| `bf16` | True | DeepSeek-Coder official |
| `completion_only_loss` | True | TRL SFTTrainer docs |
| `max_length` | 2048 | Standard code SFT |
| `weight_decay` | 0.01 | DeepSeek-Coder official |
| `adam_beta1` | 0.9 | Standard |
| `adam_beta2` | 0.95 | DeepSeek-Coder official |

**Variable per condition:** `num_train_epochs` (to equalize token budget)

**Variable per run:** `seed` ∈ {42, 123, 777}

**Total runs:** 4 conditions × 3 seeds = **12 SFT checkpoints**

**Output:** checkpoint saved to `./checkpoints/condition_{condition}_seed_{seed}/`

### FR-03: Evaluation Module

**Evaluation on 2 benchmarks per checkpoint:**

| Benchmark | Source | Tasks | Evaluation Tool |
|---|---|---|---|
| HumanEval+ | EvalPlus | 164 | `evalplus.evaluate --dataset humaneval --greedy` |
| MBPP+ | EvalPlus | 378 | `evalplus.evaluate --dataset mbpp --greedy` |

**Total evaluations:** 12 checkpoints × 2 benchmarks = **24 evaluation runs**

**Evaluation command:**
```bash
python -m evalplus.evaluate \
    --model ./checkpoints/condition_{condition}_seed_{seed} \
    --dataset [humaneval|mbpp] \
    --backend hf \
    --greedy
```

**Results collection:** Parse EvalPlus JSON output for `pass@1` per problem → aggregate to CSV.

### FR-04: Statistical Analysis Module

**Mixed-Effects Model:**
```
pass@1 ~ C(source_condition) + solution_length + (1|problem_id)
```

Fitted via `statsmodels.formula.api.mixedlm`.

**Multiple comparisons:** Holm-Bonferroni correction across C(4,2)=6 pairwise contrasts.

**Gate evaluation:**
- PASS: Fixed effect `source_condition` p < 0.05 (corrected) on ≥1 benchmark, AND ≥1 pairwise contrast ≥2.0 pp, AND direction consistent ≥2/3 seeds
- FAIL: All pairwise contrasts within ±1.5 pp on both benchmarks across all seeds

### FR-05: Mechanism Verification

After each SFT run (before evaluating all 12), verify training worked:
```python
BASE_HUMANEVAL = 0.15  # DeepSeek-Coder-1.3B base baseline
BASE_MBPP = 0.45
# Require pass@1 > base + 0.03 on at least one benchmark
```

Abort early if a condition produces 0 improvement — debug LR or dedup issue before proceeding.

### FR-06: Visualization

**Mandatory:**
- Bar chart: pass@1 per source condition on HumanEval+ and MBPP+ (with error bars across 3 seeds)

**Additional (LLM Autonomous):**
- 2×4 transfer matrix heatmap (training source × eval benchmark, cell = mean pass@1)
- Strip plots: per-seed pass@1 per condition per benchmark
- Forest plot: pairwise contrasts with 95% CI and Holm-Bonferroni p-values
- Bar chart: equalized training tokens per condition (verification)

All figures saved to `docs/youra_research/h-e2/figures/`.

---

## 4. Data Specification

### 4.1 Training Data Sources

| Dataset | HuggingFace ID | Manual Download? | Notes |
|---|---|---|---|
| HumanEval | `openai/openai_humaneval` | No (auto) | Use train split problems |
| MBPP sanitized | `google-research-datasets/mbpp` (sanitized) | No (auto) | Use train split |
| LeetCodeDataset | `newfacade/LeetCodeDataset` | No (auto) | Python subset only |
| Sentence encoder | `all-MiniLM-L6-v2` | No (auto via sentence-transformers) | For dedup |

### 4.2 Evaluation Benchmarks

| Benchmark | Access | Manual Download? |
|---|---|---|
| HumanEval+ | `from evalplus.data import get_human_eval_plus` | No |
| MBPP+ | `from evalplus.data import get_mbpp_plus` | No |

**No manual downloads required** — all datasets load via HuggingFace or evalplus Python API.

### 4.3 Intermediate Artifacts

| Artifact | Path | Format |
|---|---|---|
| Processed SFT datasets | `./data/sft_sources/{condition}/` | HuggingFace Dataset (arrow) |
| Model checkpoints | `./checkpoints/condition_{cond}_seed_{seed}/` | HuggingFace model dir |
| EvalPlus results | `./results/{condition}_{seed}_{benchmark}.json` | JSON |
| Aggregated CSV | `./results/all_results.csv` | CSV |
| Statistical report | `./results/statistical_report.txt` | Text |
| Figures | `docs/youra_research/h-e2/figures/` | PNG |

---

## 5. Non-Functional Requirements

### NFR-01: Reproducibility
- Fixed seeds {42, 123, 777} for all RNG sources (PyTorch, NumPy, Python random, HuggingFace datasets)
- DeepSpeed ZeRO-3 config saved alongside checkpoint

### NFR-02: Compute Efficiency
- 5× H100 GPUs via Accelerate + DeepSpeed ZeRO-3
- bfloat16 precision throughout
- Estimated: ~24 compute-hours total

### NFR-03: Robustness
- OOM fallback: reduce `per_device_train_batch_size` to 2, increase `gradient_accumulation_steps` to 8
- Early abort if SFT checkpoint underperforms base model after first eval

### NFR-04: Infrastructure (LIGHT tier)
- Config via argparse (no YAML config system)
- Logging via print statements + CSV results file
- Smoke test per script (runs 1 step without error)

---

## 6. Success Criteria

| Criterion | Threshold | Type |
|---|---|---|
| Code runs without error | 12/12 SFT runs + 24/24 evals complete | Required |
| Gate PASS — main effect p < 0.05 | Holm-Bonferroni corrected, ≥1 benchmark | MUST_WORK |
| Gate PASS — minimum contrast | ≥2.0 pp for ≥1 source-benchmark pair | MUST_WORK |
| Gate PASS — seed consistency | Direction consistent ≥2/3 seeds | MUST_WORK |

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.0
transformers>=4.40
trl>=0.9
accelerate>=0.30
deepspeed>=0.14
datasets>=2.18
sentence-transformers>=2.7
evalplus>=0.3
statsmodels>=0.14
scipy>=1.12
pandas>=2.1
matplotlib>=3.8
seaborn>=0.13
numpy>=1.26
```

### 7.2 External References

| Reference | URL | Purpose |
|---|---|---|
| DeepSeek-Coder official finetune | https://github.com/deepseek-ai/DeepSeek-Coder | bf16 + ZeRO-3 config |
| ESONG1999 SFT reference | https://github.com/ESONG1999/Code_Agent_RL_Github | Hyperparameter baseline |
| EvalPlus | https://github.com/evalplus/evalplus | Evaluation framework |

---

## 8. Out of Scope

- LoRA/PEFT (full SFT for clean ablation)
- Models other than DeepSeek-Coder-1.3B-Base
- Benchmarks other than HumanEval+ and MBPP+
- Training token counts beyond equalized budget
- Any architectural modification to the model

---

*stepsCompleted: PRD*
*Source: Phase 2C experiment brief (02c_experiment_brief.md)*
