# Experiment Brief: h-e1 (Existence of Bandwidth Effect)

**Hypothesis ID:** h-e1
**Type:** EXISTENCE
**Gate:** MUST_WORK
**Date:** 2026-08-29

---

## 1. Hypothesis Statement

Under PPO training on MBPP, if reward provides higher bandwidth (categorical + continuous vs binary), then model convergence differs, because more information per update enables different learning dynamics.

## 2. Experimental Design

### 2.1 Independent Variable

**Reward Bandwidth Level** (3 conditions):

| Condition | Reward Function | Information Content |
|-----------|-----------------|---------------------|
| LOW | `reward = 1 if all_tests_pass else 0` | 1 bit |
| MEDIUM | `reward = num_passed / num_total` | ~log2(num_tests) bits |
| HIGH | `reward = 0.5 × pass_rate + 0.5 × error_score` | ~log2(num_tests × error_types) bits |

**Error Score Mapping (for HIGH condition):**
```python
ERROR_SCORES = {
    'syntax_error': 0.0,      # Parse fails
    'runtime_error': 0.25,    # Executes but crashes
    'assertion_error': 0.75,  # Runs but wrong output
    'pass': 1.0               # All tests pass
}
```

### 2.2 Dependent Variable

**Primary:** Samples-to-threshold (number of training samples to reach pass@1 > 0.3 on HumanEval)

**Secondary:**
- Learning curve trajectory (pass@1 at checkpoints)
- Final pass@1 at epoch end
- Training stability (reward variance across seeds)

### 2.3 Controlled Variables

| Variable | Value | Justification |
|----------|-------|---------------|
| Model | CodeLlama-7B-Instruct | Standard code LLM, proven PPO-trainable |
| Training Dataset | MBPP (full train split, 374 problems) | Standard code generation benchmark |
| Evaluation Dataset | HumanEval (164 problems) | Held-out test set with test suites |
| Algorithm | PPO via TRL | Stable implementation, used in PPOCoder |
| Epochs | 3 | Balance between training time and convergence |
| Seeds | 5 per condition | Power analysis: 80% power for d=0.8 |
| Batch Size | 4 | Memory constraints for 7B model |
| Learning Rate | 1e-5 | TRL default for PPO |
| KL Coefficient | 0.1 | Prevent reward hacking |

## 3. Dataset Specification

### 3.1 Training Data: MBPP

- **Source:** `datasets.load_dataset("mbpp")`
- **Type:** standard
- **Split:** train (374 problems)
- **Format:** Each problem has task_id, text (prompt), code (solution), test_list (test cases)
- **Cache Path:** `~/.cache/huggingface/datasets/mbpp`

### 3.2 Evaluation Data: HumanEval

- **Source:** `datasets.load_dataset("openai_humaneval")`
- **Type:** standard
- **Split:** test (164 problems)
- **Format:** Each problem has task_id, prompt, canonical_solution, test, entry_point
- **Cache Path:** `~/.cache/huggingface/datasets/openai_humaneval`

### 3.3 Data Verification Checklist

- [ ] MBPP loads without error
- [ ] HumanEval loads without error
- [ ] Test execution sandbox works (isolated Python environment)
- [ ] Execution timeout set (10s per test case)

## 4. Model Specification

### 4.1 Base Model

- **Name:** CodeLlama-7B-Instruct
- **Source:** `codellama/CodeLlama-7b-Instruct-hf`
- **Type:** decoder-only transformer
- **Parameters:** 7B
- **Context Length:** 16384 tokens
- **Cache Path:** `~/.cache/huggingface/hub/models--codellama--CodeLlama-7b-Instruct-hf`

### 4.2 Model Verification Checklist

- [ ] Model loads with transformers
- [ ] Tokenizer functions correctly
- [ ] Generation works with sampling
- [ ] Fits in GPU memory (A100 40GB recommended)

## 5. Training Protocol

### 5.1 PPO Configuration

```python
ppo_config = PPOConfig(
    model_name="codellama/CodeLlama-7b-Instruct-hf",
    learning_rate=1e-5,
    batch_size=4,
    mini_batch_size=1,
    gradient_accumulation_steps=4,
    ppo_epochs=4,
    init_kl_coef=0.1,
    target_kl=0.1,
    max_grad_norm=1.0,
    seed=SEED,  # varies per run
)
```

### 5.2 Training Loop

```
for epoch in [1, 2, 3]:
    for problem in MBPP_TRAIN:
        1. Generate code response
        2. Execute code against test cases
        3. Compute reward (per condition)
        4. PPO update
        
    # Checkpoint after each epoch
    evaluate_on_humaneval()
    log_metrics()
```

### 5.3 Evaluation Checkpoints

- Every 1000 training samples
- After each epoch
- Metrics: pass@1, pass@10 on HumanEval

## 6. Reward Function Implementation

### 6.1 LOW Condition (Binary)

```python
def compute_reward_low(code: str, tests: list[str]) -> float:
    results = execute_tests(code, tests)
    return 1.0 if all(results) else 0.0
```

### 6.2 MEDIUM Condition (Continuous)

```python
def compute_reward_medium(code: str, tests: list[str]) -> float:
    results = execute_tests(code, tests)
    return sum(results) / len(results)
```

### 6.3 HIGH Condition (Categorical + Continuous)

```python
ERROR_SCORES = {
    'syntax_error': 0.0,
    'runtime_error': 0.25,
    'assertion_error': 0.75,
    'pass': 1.0
}

def compute_reward_high(code: str, tests: list[str]) -> float:
    results = execute_tests_with_types(code, tests)
    pass_rate = sum(1 for r in results if r == 'pass') / len(results)
    error_score = sum(ERROR_SCORES[r] for r in results) / len(results)
    return 0.5 * pass_rate + 0.5 * error_score
```

## 7. Success Criteria

### 7.1 Primary (PoC - Direction-based)

**PASS:** HIGH condition reaches threshold in fewer samples than LOW condition
- Comparison: `samples_to_threshold(HIGH) < samples_to_threshold(LOW)`
- Across mean of 5 seeds

### 7.2 Secondary

- Learning curves visibly separate between conditions
- MEDIUM between HIGH and LOW (ordering preserved)

### 7.3 Statistical Analysis

- ANOVA across 3 conditions
- Post-hoc pairwise comparisons (Tukey HSD)
- Effect size: Cohen's d for HIGH vs LOW
- Significance threshold: p < 0.05

## 8. Failure Response

**IF h-e1 FAILS:**
- Gate type: MUST_WORK
- Action: STOP pipeline, reassess hypothesis foundation
- Analysis: Check if conditions converge at similar rates, examine gradient analysis

## 9. Compute Requirements

### 9.1 Per Run

- GPU: 1x A100 40GB (or 2x A10 24GB)
- Training time: ~8-12 hours per condition per seed
- Storage: ~30GB for model + checkpoints

### 9.2 Total Experiment

- Conditions: 3
- Seeds: 5 per condition
- Total runs: 15
- Total GPU hours: ~150-180 hours
- Recommended: Parallel execution on 3-5 GPUs

## 10. Deliverables

1. **Training logs** per condition per seed
2. **Checkpoints** at each epoch
3. **Evaluation results** (pass@1, samples-to-threshold)
4. **Learning curves** visualization
5. **Statistical analysis** report
6. **04_validation.md** with gate decision

## 11. Implementation References

### 11.1 Key Libraries

- `transformers`: Model loading and generation
- `trl`: PPO training (PPOTrainer)
- `datasets`: MBPP and HumanEval loading
- `RestrictedPython` or sandbox: Safe code execution

### 11.2 Prior Work

- PPOCoder (2023): PPO training for code LLMs
- CodeRL (2022): RL for code generation with execution feedback
- RLTF (2023): Multi-granularity feedback for code

---

## Appendix: Phase 2C Completion Checklist

- [x] Hypothesis statement defined
- [x] Independent/dependent variables specified
- [x] Dataset: MBPP + HumanEval (standard, real)
- [x] Model: CodeLlama-7B-Instruct
- [x] Training protocol specified
- [x] Reward functions for 3 conditions
- [x] Success criteria defined
- [x] Failure response documented
- [x] Compute requirements estimated
- [x] Deliverables listed

**Status:** COMPLETED
**Next Phase:** Phase 3 (Implementation Planning)
