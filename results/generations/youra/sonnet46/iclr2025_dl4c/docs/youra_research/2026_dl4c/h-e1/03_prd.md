# Product Requirements Document (PRD)
# Hypothesis h-e1: EXISTENCE Prescreening Validation

**Status:** Draft
**Generated:** 2026-03-15
**Phase:** Phase 3 - Implementation Planning
**Hypothesis Type:** EXISTENCE (MUST_WORK gate)
**Source:** Phase 2C Experiment Brief (`02c_experiment_brief.md`)

---

## 1. Executive Summary

This PRD specifies the implementation requirements for **h-e1**, a prescreening validation experiment that determines whether the APPS introductory problem set (difficulty=0), filtered to S_term ∈ [0.3, 0.55], exhibits:

1. Sufficient solvability: fraction(k_pass ≥ 1) ≥ 10% (problems that at least 1 out of 8 rollouts can partially solve)
2. Sufficient variance advantage: E[Var(r_ratio)] / E[Var(r_binary)] ≥ 1.5× across ≥80% of problem groups

**Why it matters:** This is the **foundational gate** for the entire research pipeline. If h-e1 fails, GRPO training on R_ratio vs R_binary becomes meaningless (all-zero or all-one rewards). If h-e1 passes, the full hypothesis chain (h-m1 through h-m4) can proceed.

**What we build:** A prescreening inference harness that runs Qwen2.5-Coder-7B-Instruct + SFT checkpoint in pass@8 mode over APPS introductory problems and computes both gate metrics.

---

## 2. Problem Statement

### 2.1 Research Question
Does the prescreened APPS introductory subset (S_term ∈ [0.3, 0.55]) provide a regime where:
- (a) At least 10% of problem groups have at least one partial solution (solvability check)
- (b) R_ratio has at least 1.5× higher within-group variance than R_binary (variance advantage check)

### 2.2 Hypothesis Statement
Under APPS introductory problems (difficulty=0) with Qwen2.5-Coder-7B-Instruct + SFT checkpoint (pass@8, temperature=0.8, max_new_tokens=1024), if prescreening inference is run on problems with S_term ∈ [0.3, 0.55], then:
- (a) fraction(k_pass ≥ 1) ≥ 10%
- (b) E[Var(r_ratio within group)] / E[Var(r_binary within group)] ≥ 1.5× across ≥80% of problem groups

### 2.3 Scope Boundaries
- **In scope:** APPS introductory split only; prescreening inference; R_ratio and R_binary computation; gate metric evaluation
- **Out of scope:** GRPO training; fine-tuning; test set evaluation beyond prescreening; comparison with other reward functions

---

## 3. Functional Requirements

### FR-1: Dataset Loading and Filtering
- **FR-1.1:** Load APPS dataset from `codeparrot/apps` via HuggingFace `datasets` library
- **FR-1.2:** Filter to introductory split: `difficulty == "introductory"` (≈2,342 train problems)
- **FR-1.3:** Apply T≥3 filter: retain only problems with ≥3 test cases (mitigates degenerate R_ratio=R_binary edge case)
- **FR-1.4:** Parse test cases from APPS JSON format into structured `{input: str, output: str}` list

### FR-2: Prescreening Inference
- **FR-2.1:** Generate k=8 rollouts per problem using the SFT checkpoint model
- **FR-2.2:** Use temperature=0.8, max_new_tokens=1024, do_sample=True
- **FR-2.3:** Handle SFT checkpoint fallback: if `h-e1/code/sft_checkpoint/` does not exist, load base `Qwen/Qwen2.5-Coder-7B-Instruct`
- **FR-2.4:** Batch inference for efficiency (batch size determined by GPU memory; suggested 4-8 problems per batch on H100 NVL)
- **FR-2.5:** Set seed=42 for reproducibility

### FR-3: Code Execution Harness
- **FR-3.1:** Execute each generated code solution against all T test cases using subprocess sandbox
- **FR-3.2:** Apply per-test-case timeout of 5 seconds
- **FR-3.3:** Capture stdout and compare to expected output (exact string match after strip)
- **FR-3.4:** Return `tests_passed` count per rollout (integer 0..T)
- **FR-3.5:** Handle execution errors gracefully (SyntaxError, RuntimeError, TimeoutError → tests_passed=0)

### FR-4: Reward Function Computation
- **FR-4.1 R_ratio:** `r_i = tests_passed_i / T` — continuous score in [0, 1]
- **FR-4.2 R_binary:** `r_i = float(tests_passed_i == T)` — binary {0.0, 1.0}
- **FR-4.3:** Compute per-group (per-problem) reward vectors of length k=8 for both R_ratio and R_binary

### FR-5: S_term Computation and Prescreening Filter
- **FR-5.1:** Compute S_term = fraction of k=8 rollouts with R_binary=1.0 (i.e., at least 1 test case passed — using R_binary gate)
  - Note: S_term is defined as fraction(k_pass≥1), not fraction(all_pass), per Phase 2B spec
  - Correction: S_term = fraction of rollouts where `tests_passed >= 1` (not full pass)
- **FR-5.2:** Retain problems where S_term ∈ [0.3, 0.55]
- **FR-5.3:** Record pre- and post-filter dataset sizes for diagnostic output

### FR-6: Gate Metric Computation
- **FR-6.1:** For each problem group in prescreened subset, compute:
  - `var_ratio_group = np.var([r_ratio_i for i in 1..k])`
  - `var_binary_group = np.var([r_binary_i for i in 1..k])`
  - `variance_ratio = var_ratio_group / var_binary_group` (only when var_binary_group > 1e-8)
- **FR-6.2:** Compute `fraction_k_pass_ge1` = mean over all groups of [any(r_binary > 0)]
- **FR-6.3:** Compute `pct_groups_above_1_5x` = fraction of variance ratios ≥ 1.5
- **FR-6.4:** Determine gate result: PASS if fraction_k_pass_ge1 ≥ 0.10 AND pct_groups_above_1_5x ≥ 0.80

### FR-7: Results Persistence
- **FR-7.1:** Save gate metrics to `h-e1/results/gate_metrics.json`
- **FR-7.2:** Save per-problem results (S_term, var_ratio, var_binary, variance_ratio) to `h-e1/results/per_problem_results.csv`
- **FR-7.3:** Save all generated rollouts (optional, large) to `h-e1/results/rollouts.json` if disk space available
- **FR-7.4:** Save figures to `h-e1/figures/`

### FR-8: Visualization
- **FR-8.1 (Mandatory):** Gate metrics bar chart — fraction_k_pass_ge1 and pct_groups_above_1.5x vs thresholds (0.10, 0.80)
- **FR-8.2:** S_term distribution histogram (pre- and post-prescreening)
- **FR-8.3:** Variance ratio scatter plot (Var(r_ratio) vs Var(r_binary) per problem)
- **FR-8.4:** T distribution histogram (test case counts in prescreened subset)
- **FR-8.5:** Empirical vs theoretical Binomial(T,q) variance ratio scatter

---

## 4. Data Specification

### 4.1 Primary Dataset

| Field | Value |
|-------|-------|
| Name | APPS — Automated Programming Progress Standard |
| Source | `codeparrot/apps` (HuggingFace Hub) |
| Split | `train` (introductory difficulty=0 subset) |
| Size (full) | 5,000 train problems |
| Size (intro) | ~2,342 introductory problems |
| Expected prescreened size | ~200–600 problems (S_term ∈ [0.3, 0.55]) |
| Download method | `datasets.load_dataset("codeparrot/apps", split="train")` |
| Cache path | `~/.cache/huggingface/datasets/codeparrot___apps` |
| Download size | ~1.2 GB |
| Requires manual download | **NO** — HuggingFace auto-download |

**No data preparation task needed** — dataset downloads automatically via HuggingFace.

### 4.2 Model

| Field | Value |
|-------|-------|
| Primary | `h-e1/code/sft_checkpoint/` (local SFT checkpoint) |
| Fallback | `Qwen/Qwen2.5-Coder-7B-Instruct` (HuggingFace Hub) |
| Architecture | Qwen2.5 transformer, 7B parameters |
| dtype | bfloat16 |
| VRAM requirement | ~15 GB (7B bfloat16) |
| Download size | ~14 GB (if fallback needed) |
| Requires manual download | **NO** if SFT exists; auto-download if fallback |

---

## 5. Non-Functional Requirements

### NFR-1: Performance
- **NFR-1.1:** Complete prescreening inference within 4 hours on a single H100 NVL GPU
- **NFR-1.2:** Target ≥10 problems/minute throughput at batch_size=4
- **NFR-1.3:** Per-rollout execution timeout: 5 seconds (prevent infinite loops)

### NFR-2: Reproducibility
- **NFR-2.1:** Set torch.manual_seed(42) and transformers sampling seed=42 before inference
- **NFR-2.2:** Results must be reproducible within ±1% across identical hardware runs
- **NFR-2.3:** All intermediate results saved to disk for analysis

### NFR-3: Robustness
- **NFR-3.1:** Handle execution sandbox failures gracefully (log error, continue)
- **NFR-3.2:** Resume capability: if run interrupted, skip already-processed problems
- **NFR-3.3:** If SFT checkpoint missing, auto-fallback to base model with warning
- **NFR-3.4:** Minimum viable sample: if T≥3 filter produces <50 problems, FAIL EARLY with clear message

### NFR-4: Diagnostics
- **NFR-4.1:** Log per-group statistics every 100 problems
- **NFR-4.2:** Progress bar (tqdm) during inference
- **NFR-4.3:** Print intermediate gate metric estimates every 500 problems

---

## 6. Success Criteria

| Criterion | Gate Type | Threshold | Measurement |
|-----------|-----------|-----------|-------------|
| fraction_k_pass_ge1 | MUST_WORK (a) | ≥ 0.10 | Over all prescreened groups |
| pct_groups_above_1.5x | MUST_WORK (b) | ≥ 0.80 | Fraction of groups with var_ratio ≥ 1.5 |
| Code runs without fatal error | Technical | 100% | No unhandled exceptions |
| Prescreened subset size | Practical | ≥ 50 problems | After T≥3 + S_term filters |

**Gate PASS:** Both (a) AND (b) met → proceed to h-m1
**Gate FAIL:** Either (a) OR (b) not met → STOP pipeline, return to Phase 0 for regime redesign

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.1.0
transformers>=4.45.0
datasets>=2.20.0
trl==0.29.0
numpy>=1.24.0
pandas>=2.0.0
matplotlib>=3.7.0
seaborn>=0.12.0
tqdm>=4.65.0
scipy>=1.11.0
```

### 7.2 Environment
- Python 3.10+
- CUDA 12.1+ (for H100 NVL)
- Single GPU: H100 NVL (~40GB VRAM)
- Disk: ≥50 GB free (APPS cache + model weights + results)

### 7.3 External Repositories (Reference Only)
- TRL GRPOTrainer documentation: https://huggingface.co/docs/trl/grpo_trainer
- APPS dataset paper: Hendrycks et al. 2021 (for dataset format reference)
- Afterburner (ArXiv 2505.23387): GRPO+APPS execution feedback patterns
- PKPO (ArXiv 2505.15201): pass@k reward theory and variance analysis

---

## 8. File Structure

```
h-e1/
├── code/
│   ├── prescreening.py          # Main prescreening script (entry point)
│   ├── reward_fn.py             # R_ratio and R_binary computation
│   ├── execution_sandbox.py     # Code execution harness
│   ├── data_loader.py           # APPS dataset loading and filtering
│   ├── evaluate.py              # Gate metric computation
│   ├── visualization.py         # Figure generation
│   └── sft_checkpoint/          # SFT checkpoint (if exists)
├── results/
│   ├── gate_metrics.json        # Final gate metric values
│   ├── per_problem_results.csv  # Per-problem statistics
│   └── rollouts.json            # (Optional) generated code rollouts
└── figures/
    ├── gate_metrics.png         # Required: gate metrics vs thresholds
    ├── s_term_distribution.png  # S_term histogram
    ├── variance_ratio_scatter.png
    ├── t_distribution.png
    └── empirical_vs_theoretical.png
```

---

## 9. Constraints and Risks

| Risk | Mitigation |
|------|------------|
| SFT checkpoint missing | Auto-fallback to base Qwen2.5-Coder-7B-Instruct |
| T≥3 filter produces <50 problems | FAIL EARLY with diagnostic output |
| Execution sandbox timeout rate >50% | Diagnostic warning; verify problem parsing |
| All S_term outside [0.3, 0.55] | FAIL: prescreening regime assumption violated |
| GPU OOM | Reduce batch size; use gradient checkpointing if needed (inference only: unlikely) |

---

## 10. Phase 4 Guidance

**Entry point:** `h-e1/code/prescreening.py`

Phase 4 should implement in this order:
1. `data_loader.py` — APPS loading + filtering
2. `execution_sandbox.py` — subprocess execution harness
3. `reward_fn.py` — R_ratio and R_binary computation
4. `evaluate.py` — gate metric computation
5. `prescreening.py` — main orchestration script
6. `visualization.py` — figure generation

Run with: `python h-e1/code/prescreening.py --seed 42 --batch_size 4`

---

*PRD generated by Phase 3 Implementation Planning (inline execution)*
*Source: h-e1/02c_experiment_brief.md*
*BMAD PRD workflow bmm module absent — inline generation*
