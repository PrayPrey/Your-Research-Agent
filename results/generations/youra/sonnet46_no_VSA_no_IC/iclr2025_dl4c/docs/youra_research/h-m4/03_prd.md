---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7]
hypothesis_id: h-m4
type: MECHANISM
generated_at: 2026-08-21
author: yoon303@etri.re.kr
base_hypothesis: h-m2
---

# PRD: H-M4 — Variance Selection Translates to HumanEval+ pass@1 Improvement

## 1. Executive Summary

H-M4 tests whether GRPO training on variance-50 MBPP problems (confirmed to reduce zero-gradient groups in H-M2) translates into measurable HumanEval+ pass@1 improvement: ≥2pp over the frozen baseline AND ≥1pp over random-50 at step 50.

**Gate:** SHOULD_WORK — failure = partial result (P2 mechanistic evidence from H-M2 remains), not stop.

**Prerequisite:** H-M3 (SHOULD_WORK, FAILED — gradient concentration advantage did not sustain to step 50; limitation recorded, H-M4 proceeds with elevated risk on P1).

**Continuation:** H-M4 is evaluation-only. No new GRPO training runs. It adds EvalPlus evaluation at H-M2 checkpoints (step 0 baseline, step 10, 20, 50) for all three conditions (variance-50, random-50, full-374).

---

## 2. Problem Statement

H-M2 confirmed variance-50 reduces `frac_reward_zero_std` (gradient concentration advantage). H-M3 showed this advantage may not sustain throughout all 50 steps. H-M4 directly tests the downstream question: does the gradient concentration advantage during training (even if transient, per H-M3) produce a measurable improvement in code generation quality as measured by HumanEval+ pass@1?

**Success demonstrates:** Variance profiling (YOURA core mechanism) produces capability improvement — the ultimate goal of the selection strategy — under short RLEF (50 steps).

---

## 3. Functional Requirements

### FR-1: Verify H-M2 Checkpoints Exist
- Check paths: `docs/youra_research/h-m2/results/variance50/checkpoint-10`, `checkpoint-20`, `checkpoint-50`
- Check paths: `docs/youra_research/h-m2/results/random50/checkpoint-10`, `checkpoint-20`, `checkpoint-50`
- Check paths: `docs/youra_research/h-m2/results/full374/checkpoint-10`, `checkpoint-20`, `checkpoint-50` (if full-374 run exists)
- **If checkpoints MISSING:** Re-run H-M2 training with `save_steps=10` (use H-M2 code at `docs/youra_research/h-m2/code/train.py`)
- **If checkpoints PRESENT:** Skip training, go directly to evaluation

### FR-2: Install EvalPlus
```bash
pip install "evalplus[vllm]" --upgrade
```
Verify: `python -c "import evalplus; print(evalplus.__version__)"`

### FR-3: Define Checkpoint Map
```python
CHECKPOINT_MAP = {
    "variance50": {
        "step_0":  "deepseek-ai/deepseek-coder-7b-instruct-v1.5",  # frozen baseline (shared)
        "step_10": "docs/youra_research/h-m2/results/variance50/checkpoint-10",
        "step_20": "docs/youra_research/h-m2/results/variance50/checkpoint-20",
        "step_50": "docs/youra_research/h-m2/results/variance50/checkpoint-50",
    },
    "random50": {
        "step_0":  "deepseek-ai/deepseek-coder-7b-instruct-v1.5",  # same frozen baseline
        "step_10": "docs/youra_research/h-m2/results/random50/checkpoint-10",
        "step_20": "docs/youra_research/h-m2/results/random50/checkpoint-20",
        "step_50": "docs/youra_research/h-m2/results/random50/checkpoint-50",
    },
    "full374": {
        "step_0":  "deepseek-ai/deepseek-coder-7b-instruct-v1.5",  # same frozen baseline
        "step_10": "docs/youra_research/h-m2/results/full374/checkpoint-10",
        "step_20": "docs/youra_research/h-m2/results/full374/checkpoint-20",
        "step_50": "docs/youra_research/h-m2/results/full374/checkpoint-50",
    },
}
# Note: step_0 is the same frozen model for all conditions.
# Evaluate frozen baseline ONCE, reuse for all conditions.
```

### FR-4: EvalPlus Code Generation (k=8 samples per problem)
For each (condition, step) checkpoint:
```python
def generate_samples(checkpoint_path: str, condition: str, step: str, output_root: str):
    """Generate k=8 samples per HumanEval+ problem using EvalPlus CLI."""
    output_dir = f"{output_root}/{condition}/step_{step}"
    cmd = [
        "python", "-m", "evalplus.codegen",
        "--model", checkpoint_path,
        "--dataset", "humaneval",
        "--backend", "hf",
        "--n_samples", "8",
        "--temperature", "0.8",
        "--root", output_dir,
    ]
    subprocess.run(cmd, check=True)
    return output_dir
```
- 164 HumanEval+ problems × 8 samples = 1,312 generations per checkpoint
- Total: ~12 (condition × step) evaluations; frozen baseline (step_0) evaluated ONCE

### FR-5: EvalPlus Evaluation (pass@1 computation)
```python
def evaluate_samples(output_dir: str, condition: str, step: str) -> float:
    """Evaluate generated samples and return pass@1."""
    samples_path = f"{output_dir}/samples.jsonl"
    cmd = [
        "python", "-m", "evalplus.evaluate",
        "--dataset", "humaneval",
        "--samples", samples_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    # Parse: "humaneval_plus pass@1: 0.7317"
    pass_at_1 = parse_pass_at_1_from_evalplus_output(result.stdout)
    return pass_at_1
```

### FR-6: Compute Improvement Metrics
```python
baseline_pass_at_1 = pass_at_1_results["variance50"]["step_0"]  # frozen (same for all)

# Primary gate metrics
improvement_variance50 = pass_at_1_results["variance50"]["step_50"] - baseline_pass_at_1
improvement_random50   = pass_at_1_results["random50"]["step_50"] - baseline_pass_at_1
improvement_full374    = pass_at_1_results["full374"]["step_50"] - baseline_pass_at_1  # if available

gap_vs_random50 = improvement_variance50 - improvement_random50

# P1 gate
p1_pass = (improvement_variance50 >= 0.02) and (gap_vs_random50 >= 0.01)

# P3 secondary (conditional)
p3_pass = None
if improvement_variance50 >= 0.02 and improvement_full374 >= 0.02:
    efficiency_ratio = improvement_variance50 / improvement_full374
    p3_pass = efficiency_ratio >= 0.80
```

### FR-7: Trajectory Analysis (pass@1 across steps 10, 20, 50)
```python
for condition in ["variance50", "random50", "full374"]:
    for step in ["step_10", "step_20", "step_50"]:
        improvement_trajectory[condition][step] = (
            pass_at_1_results[condition][step] - baseline_pass_at_1
        )
```

### FR-8: Condition Asserts
```python
# Verify evaluation ran on all checkpoints
for condition in required_conditions:
    for step in ["step_0", "step_10", "step_20", "step_50"]:
        assert pass_at_1_results[condition][step] is not None, f"Missing eval: {condition}/{step}"
        assert 0.0 <= pass_at_1_results[condition][step] <= 1.0, f"Invalid pass@1: {condition}/{step}"

print(f"[H-M4] baseline pass@1 = {baseline_pass_at_1:.4f}")
print(f"[H-M4] improvement_variance50 at step50 = {improvement_variance50*100:.2f}pp")
print(f"[H-M4] gap_vs_random50 at step50 = {gap_vs_random50*100:.2f}pp")
print(f"[H-M4] P1 gate: {p1_pass}")
```

### FR-9: Results JSON
Save `docs/youra_research/h-m4/results/gate_results.json`:
```json
{
  "gate_passed": bool,
  "p1_pass": bool,
  "p3_pass": bool_or_null,
  "baseline_pass_at_1": float,
  "pass_at_1": {
    "variance50": {"step_0": float, "step_10": float, "step_20": float, "step_50": float},
    "random50":   {"step_0": float, "step_10": float, "step_20": float, "step_50": float},
    "full374":    {"step_0": float, "step_10": float, "step_20": float, "step_50": float}
  },
  "improvement": {
    "variance50": {"step_10": float, "step_20": float, "step_50": float},
    "random50":   {"step_10": float, "step_20": float, "step_50": float},
    "full374":    {"step_10": float, "step_20": float, "step_50": float}
  },
  "gap_vs_random50_at_50": float,
  "efficiency_ratio": float_or_null,
  "thresholds": {"p1_improvement_pp": 2.0, "p1_gap_pp": 1.0, "p3_efficiency": 0.80},
  "n_samples_per_problem": 8,
  "n_problems": 164,
  "dataset": "humaneval_plus"
}
```

### FR-10: Visualization — 4 Figures
- **Fig 1 (mandatory — gate metric):** Bar chart comparing improvement (pp) for all 3 conditions at step 50. Horizontal threshold lines at 2pp and 1pp gap. Shows pass/fail clearly.
- **Fig 2:** Line plot: pass@1 improvement trajectory across steps 10, 20, 50 for all 3 conditions.
- **Fig 3:** Heatmap: pass@1 at each (condition × step) checkpoint, 3×4 grid.
- **Fig 4:** Scatter: frac_reward_zero_std from H-M2 logs vs pass@1 improvement per condition — mechanistic-capability correlation test.

Output: `docs/youra_research/h-m4/figures/`

### FR-11: Conditional Training (Fallback)
If H-M2 checkpoints do not exist, re-train using H-M2 code with `save_steps=10`:
```python
# Use train.py from h-m2/code/ with save_steps=10 added to GRPOConfig
# See H-M2 training protocol for full config
```
This is a fallback — the primary path assumes H-M2 checkpoints are present.

---

## 4. Data Specification

### 4.1 Evaluation Dataset: HumanEval+ (EvalPlus)
- **Source:** `evalplus` pip package; `get_human_eval_plus()` function
- **Auto-download via EvalPlus:** Yes (internal to evalplus package)
- **Size:** 164 problems with augmented test cases (80× more than original HumanEval)
- **Loading code:**
  ```python
  # Handled internally by EvalPlus CLI
  # evalplus.codegen downloads and caches HumanEval+ automatically
  ```

### 4.2 Training Dataset: MBPP (for conditional fallback training only)
- **Source:** HuggingFace `google-research-datasets/mbpp`, config=`"full"`, split=`"train"`
- **Auto-download:** Yes (HuggingFace Datasets API)
- **Size:** 374 problems (primary use for H-M2; inherited by H-M4 fallback)
- **Subset IDs:** variance-50 from `docs/youra_research/h-e1/results/mbpp_variance_profile.json`

### 4.3 H-M2 Checkpoints (pre-existing artifacts)
- **Source:** H-M2 training output at `docs/youra_research/h-m2/results/`
- **Type:** HuggingFace model checkpoint format (directory with `config.json`, `model.safetensors`, etc.)
- **No download needed:** Local artifacts from prior training

### 4.4 H-M2 Training Logs (for Fig 4 scatter plot)
- **Source:** `docs/youra_research/h-m2/results/gate_results.json`
- **Field used:** `frac_reward_zero_std_per_step.variance50` and `frac_reward_zero_std_per_step.random50`

---

## 5. Evaluation Configuration

| Parameter | Value | Source |
|-----------|-------|--------|
| Dataset | HumanEval+ (164 problems) | Phase 2B §H-M4 |
| k (samples per problem) | 8 | Phase 2B §H-M4 protocol |
| Temperature | 0.8 | Phase 2B (non-zero for k>1 sampling) |
| Backend | `hf` (HuggingFace local) | EvalPlus docs |
| Metric | pass@1 (correctness, augmented tests) | Phase 2B |
| Improvement threshold P1 | ≥ 2pp over baseline | Phase 2B §2.2 |
| Gap threshold P1 | ≥ 1pp over random-50 | Phase 2B §2.2 |
| Efficiency ratio threshold P3 | ≥ 0.80 (conditional) | Phase 2B §2.2 |

---

## 6. Evaluation Metrics

| Metric | Type | Gate | Threshold |
|--------|------|------|-----------|
| improvement_variance50 at step 50 | Primary | SHOULD_WORK | ≥ 2pp |
| gap_vs_random50 at step 50 | Primary | SHOULD_WORK | ≥ 1pp |
| efficiency_ratio = var50_improvement / full374_improvement | Secondary | P3 (conditional) | ≥ 0.80 |
| pass@1 trajectory at steps 10, 20 | Diagnostic | None | N/A |
| Scatter: frac_reward_zero_std vs improvement | Diagnostic | None | N/A |

**PoC Pass Condition:**
1. EvalPlus evaluation completes without error for all checkpoints
2. `improvement_variance50 ≥ 2pp` AND `gap_vs_random50 ≥ 1pp` at step 50

**Failure Modes:**
- P1 fails but H-M2 P2 (frac_reward_zero_std) passes → PARTIAL: mechanism confirmed, capability transfer needs more steps
- All conditions < 2pp improvement → R4: "P1 untestable" (50-step budget insufficient); P2 evidence from H-M2 is primary
- Checkpoints missing → run fallback training (FR-11)

---

## 7. Dependencies

### 7.1 Python Packages
```
torch>=2.0
transformers>=4.35
trl>=0.15.0
datasets>=2.0
numpy>=1.20
matplotlib>=3.5
accelerate>=0.20
evalplus>=0.3.0      # NEW for H-M4: EvalPlus evaluation framework
```

### 7.2 Local Artifacts (H-M2 outputs)
- `docs/youra_research/h-m2/results/variance50/checkpoint-10` — H-M2 variance-50 checkpoint
- `docs/youra_research/h-m2/results/variance50/checkpoint-20` — H-M2 variance-50 checkpoint
- `docs/youra_research/h-m2/results/variance50/checkpoint-50` — H-M2 variance-50 checkpoint
- `docs/youra_research/h-m2/results/random50/checkpoint-10` — H-M2 random-50 checkpoint
- `docs/youra_research/h-m2/results/random50/checkpoint-20` — H-M2 random-50 checkpoint
- `docs/youra_research/h-m2/results/random50/checkpoint-50` — H-M2 random-50 checkpoint
- `docs/youra_research/h-m2/results/gate_results.json` — frac_reward_zero_std logs for Fig 4
- `docs/youra_research/h-e1/results/mbpp_variance_profile.json` — variance-50 IDs (fallback training)

### 7.3 External Repositories (reference only)
- evalplus/evalplus: official EvalPlus evaluation framework
- axolotl-ai-cloud/grpo_code: GRPO + EvalPlus integration pattern reference
- huggingface/trl: GRPOTrainer reference (for fallback training)

---

## 8. Non-Functional Requirements

- **Reproducibility:** k=8 sampling with temperature=0.8; deterministic via EvalPlus seed if supported
- **Compute:** 12 checkpoint evaluations × 164 problems × 8 samples; expected: 4–12h GPU time
- **Isolation:** All evaluation output in `docs/youra_research/h-m4/results/`; no modification of H-M2 artifacts
- **Output:** All artifacts in `docs/youra_research/h-m4/`; figures in `docs/youra_research/h-m4/figures/`
- **Checkpoint reuse:** H-M4 must not overwrite H-M2 checkpoints

---

## 9. Success Criteria

**PASS (P1):** improvement_variance50 ≥ 2pp AND gap_vs_random50 ≥ 1pp at step 50
**PARTIAL:** P1 fails but H-M2 P2 (frac_reward_zero_std) evidence confirmed → mechanism holds, capability transfer needs more steps
**P3 (conditional):** If both variance50 and full374 achieve ≥2pp, then efficiency_ratio ≥ 0.80
**UNTESTABLE (R4):** If no condition achieves 2pp → 50-step budget insufficient; declare P1 untestable, P2 as primary evidence
