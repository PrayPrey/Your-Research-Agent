# Product Requirements Document: H-E1
# Frozen-Model Variance Profiling for MBPP Training Split

**Hypothesis ID:** h-e1
**Hypothesis Type:** EXISTENCE (PoC)
**Gate Type:** MUST_WORK
**Generated:** 2026-08-21
**Phase:** 3 — Implementation Planning

---

## 1. Executive Summary

H-E1 is a measurement/profiling experiment that determines whether the MBPP training split (374 problems) exhibits a non-degenerate variance distribution under frozen DeepSeek-Coder-7B-Instruct with k=8 i.i.d. completions per problem. The gate condition is: ≥50 MBPP training problems must have p_i*(1-p_i) > 0.1. This is a pure profiling script — no gradient training occurs.

**Deliverable:** A Python profiling script (`profile_mbpp.py`) that:
1. Loads MBPP training split (374 problems)
2. Generates k=8 completions per problem from frozen DeepSeek-Coder-7B-Instruct
3. Executes completions against test cases (binary pass/fail)
4. Computes p_i = pass_count/k and variance_i = p_i*(1-p_i) per problem
5. Checks MUST_WORK gate: count(variance_i > 0.1) ≥ 50
6. Saves results JSON + 4 figures

---

## 2. Problem Statement

### 2.1 Research Question

Does the MBPP training split contain a sufficient number of problems with intermediate pass rates (0 < p_i < 1) under frozen DeepSeek-Coder-7B-Instruct to yield meaningful GRPO gradient signal for ≥50 problems?

### 2.2 Theoretical Basis

For binary reward r(o) ∈ {0,1}, GRPO advantage weight is proportional to p_i*(1-p_i) — the Bernoulli variance of problem pass rate (Source: ymroueh.me/GRPO.pdf). Problems where the model always succeeds (p_i=1) or always fails (p_i=0) contribute zero gradient. Only problems with 0 < p_i < 1 carry learning signal.

### 2.3 Success Threshold

Gate: **count(p_i*(1-p_i) > 0.1) ≥ 50** across 374 MBPP training problems.

Literature expectation: ~15% variable samples (from agentpatterns.ai FinQA case study) → ~56 of 374 problems expected above threshold. DeepSeek-Coder-7B's MBPP base performance (~54%) supports a substantial intermediate zone.

---

## 3. Scope

### 3.1 In Scope
- Load MBPP training split (374 problems) via HuggingFace Datasets
- Load frozen DeepSeek-Coder-7B-Instruct-v1.5 (no fine-tuning, eval() mode)
- Generate k=8 i.i.d. completions per problem (temperature=1.0, top_p=0.95, max_new_tokens=512)
- Execute completions with subprocess sandbox (binary pass/fail per problem)
- Compute p_i and variance_i for all 374 problems
- Select top-50 by variance
- Generate 4 visualizations (gate metrics bar, p_i histogram, variance histogram, top-50 scatter)
- Save results to JSON for downstream use by H-M1

### 3.2 Out of Scope
- GRPO training (no gradient updates in H-E1)
- HumanEval+ evaluation (downstream, H-M1+)
- vLLM backend (transformers primary; vLLM fallback only if too slow)
- Any model fine-tuning

---

## 4. Data Specification

### 4.1 Primary Dataset: MBPP Training Split

| Field | Value |
|-------|-------|
| Name | MBPP (Mostly Basic Python Problems) |
| HuggingFace ID | `google-research-datasets/mbpp` |
| Config | `"full"` |
| Split | `"train"` |
| Size | 374 problems |
| Download Method | Auto via HuggingFace Datasets API |
| Manual Download Required | **No** — auto-download |
| Preprocessing | None — raw `text` field used as prompt; `test_list` used for execution |

**Loading Code:**
```python
from datasets import load_dataset
mbpp = load_dataset("google-research-datasets/mbpp", "full")
train_problems = mbpp["train"]  # 374 problems
```

**Problem Schema:**
```
task_id: int
text: str        # Problem description → prompt
code: str        # Reference solution (NOT used for generation)
test_list: list  # Test cases for binary execution reward
```

### 4.2 Evaluation Dataset

HumanEval+ (EvalPlus): **NOT used in H-E1**. Downstream metric for H-M1+.

---

## 5. Functional Requirements

### FR-1: Environment Setup
**ID:** FR-1
**Priority:** Critical
**Description:** Install all required Python packages.
**Packages:**
- `datasets` (HuggingFace Datasets)
- `transformers` (HuggingFace Transformers)
- `torch` (PyTorch, CUDA-enabled)
- `numpy`
- `matplotlib`
- Existing: `evalplus` (already operational)

### FR-2: MBPP Data Loading
**ID:** FR-2
**Priority:** Critical
**Description:** Load MBPP training split using HuggingFace Datasets. No preprocessing — raw text field used as DeepSeek chat template prompt.

**Prompt Format:**
```python
def format_mbpp_prompt(problem: dict) -> str:
    """Format MBPP problem as DeepSeek instruction prompt."""
    return f"""You are an expert Python programmer. Write a Python function to solve the following problem.

Problem: {problem['text']}

Write only the function implementation:"""
```

### FR-3: Frozen Model Loading
**ID:** FR-3
**Priority:** Critical
**Description:** Load DeepSeek-Coder-7B-Instruct-v1.5 in frozen inference mode.
- `model.eval()` — no gradient tracking
- `torch.no_grad()` context
- `torch_dtype=torch.bfloat16`
- `device_map="auto"` (CUDA)

### FR-4: k=8 i.i.d. Completion Generation
**ID:** FR-4
**Priority:** Critical
**Description:** For each of 374 MBPP problems, generate k=8 independent completions.
- Temperature: 1.0 (random sampling for i.i.d. draws)
- top_p: 0.95
- max_new_tokens: 512
- do_sample: True
- Seed: 42 (fixed for reproducibility — reset per-problem, vary per completion index)

### FR-5: Binary Execution Testing
**ID:** FR-5
**Priority:** Critical
**Description:** Execute each completion against MBPP test_list with subprocess sandbox.
- Timeout: 10 seconds per execution
- Sandbox: `subprocess.run(["python", tmpfile], timeout=10, capture_output=True)`
- Binary result: returncode == 0 → pass (1), else → fail (0)
- Count passes across k=8 runs → pass_count

### FR-6: Variance Computation
**ID:** FR-6
**Priority:** Critical
**Description:** Compute Bernoulli statistics per problem.
```python
p_i = pass_count / k
variance_i = p_i * (1 - p_i)
```

### FR-7: MUST_WORK Gate Check
**ID:** FR-7
**Priority:** Critical
**Description:** Check gate condition and report result.
```python
gate_passed = sum(1 for v in variances if v > 0.1) >= 50
```
- Log `count_nonzero_variance` vs threshold 50
- Log `mean_p_top50` (mean pass rate of top-50 by variance)
- EXIT_CODE: 0 if gate passed, 1 if gate failed

### FR-8: Top-50 Selection
**ID:** FR-8
**Priority:** Critical
**Description:** Select top-50 problems by variance_i (descending).
```python
top50_ids = sorted(results, key=lambda t: results[t]["variance_i"], reverse=True)[:50]
```

### FR-9: Results Persistence
**ID:** FR-9
**Priority:** Critical
**Description:** Save results JSON for H-M1+ downstream use.
- Path: `docs/youra_research/h-e1/results/mbpp_variance_profile.json`
- Schema: `{task_id: {p_i, variance_i, pass_count, k, rank_by_variance}}`
- Include: top50_ids list, gate_result, metrics summary

### FR-10: Visualization Generation
**ID:** FR-10
**Priority:** High
**Description:** Generate 4 mandatory figures.

| Figure | Type | Description |
|--------|------|-------------|
| fig1_gate_metrics.png | Bar chart | count_nonzero_variance vs threshold 50; mean_p_top50 vs [0.25, 0.75] |
| fig2_pass_rate_histogram.png | Histogram | p_i distribution across 374 problems; shade [0.25, 0.75] zone |
| fig3_variance_histogram.png | Histogram | variance_i distribution; vertical line at 0.1 threshold |
| fig4_top50_scatter.png | Scatter | All 374 problems (x=rank, y=p_i); top-50 red, rest gray |

- Save path: `docs/youra_research/h-e1/figures/`

---

## 6. Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed seed (42) for all random operations
- Seed reset per-problem: `torch.manual_seed(42 + problem_idx + completion_idx)`
- Full results JSON saved for exact reproduction

### NFR-2: Performance
- Target: ≤4 hours for 374×8=2,992 forward passes on single A100/V100
- Progress bar (tqdm) showing problem count and estimated remaining time
- Checkpoint saving: save intermediate results every 50 problems

### NFR-3: Safety
- Subprocess sandbox with 10s timeout prevents infinite loops in generated code
- `os.unlink(tmpfile)` in finally block for cleanup
- No network access in sandbox

### NFR-4: Logging
- Log level: INFO
- Log: per-problem completion count, pass_count, p_i, variance_i
- Log: running count of problems above threshold (FR-7)
- Log: gate result at end

---

## 7. Dependencies

### 7.1 Python Packages
```
datasets>=2.14.0
transformers>=4.40.0
torch>=2.1.0          # CUDA-enabled build
numpy>=1.24.0
matplotlib>=3.7.0
tqdm>=4.65.0
```

### 7.2 External Repositories (Reference Only)
- TRL GRPOTrainer: https://huggingface.co/docs/trl/en/grpo_trainer (BUILD_ON reference)
- EvalPlus: Already operational (confirmed in h-e1 environment)

### 7.3 Hardware Requirements
- GPU: CUDA-capable, ≥24GB VRAM (for 7B bfloat16 model)
- Storage: ~15GB for model weights + ~50MB results

---

## 8. Success Criteria

### 8.1 Primary Gate (MUST_WORK)
```
count(p_i*(1-p_i) > 0.1) ≥ 50
```
- **PASS:** ≥50 problems above threshold → H-E1 gate satisfied → proceed to H-M1
- **FAIL:** <50 problems → variance distribution degenerate → ABANDON hypothesis chain

### 8.2 Secondary Criteria
- Top-50 selected problems have `mean_p_top50` ∈ [0.25, 0.75]
- All 4 figures generated without error
- Results JSON written successfully

### 8.3 Code Quality Gate
- Script runs end-to-end without exception
- Exit code 0 on gate pass, 1 on gate fail

---

## 9. Implementation Notes

### 9.1 Execution Order
1. Environment setup (FR-1)
2. MBPP load + validate 374 problems (FR-2)
3. Model load + move to CUDA (FR-3)
4. Profiling loop: for each problem, generate k=8, execute, compute p_i, variance_i (FR-4, FR-5, FR-6)
5. Gate check + report (FR-7)
6. Top-50 selection (FR-8)
7. Save results JSON (FR-9)
8. Generate figures (FR-10)

### 9.2 Memory Management
- Use `torch.no_grad()` throughout generation
- Clear GPU cache every 50 problems: `torch.cuda.empty_cache()`
- Generate completions one-at-a-time (batch_size=1) for memory safety

### 9.3 Intermediate Checkpointing
Save every 50 problems to `results/checkpoint_{n}.json` to enable resume on failure.
