# Product Requirements Document (PRD)
# H-E1: Difficulty-Tier Sample Size Viability Check

**Status:** Draft
**Version:** 1.0
**Date:** 2026-03-18
**Hypothesis:** H-E1 (EXISTENCE, MUST_WORK gate)
**Phase:** 3 - Implementation Planning
**Tier:** LIGHT (EXISTENCE → max 15 tasks)

---

## Frontmatter

```yaml
stepsCompleted:
  - executive_summary
  - problem_statement
  - functional_requirements
  - non_functional_requirements
  - success_criteria
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
gate_type: MUST_WORK
phase2c_source: h-e1/02c_experiment_brief.md
```

---

## 1. Executive Summary

H-E1 is the foundational existence check for the LLM Calibration as Self-Contained Code Verifier pipeline. It answers a single question: **Are there enough hard and easy problems in HumanEval+/MBPP+ to reliably compute ECE with M=15 bins per difficulty tier?**

The experiment generates k=5 code solutions per problem per model using three LLM families (Llama3-8B, CodeLlama-7B, DeepSeek-Coder-6.7B), evaluates correctness via EvalPlus, computes per-problem pass@1, assigns hard/easy/medium tiers, and counts tier sizes.

**Gate Condition (MUST_WORK):** n_hard ≥ 20 AND n_easy ≥ 20 for ≥2/3 models on ≥1 benchmark (HumanEval+ or MBPP+).

**Fail consequence:** If gate fails → relax hard_threshold from 0.0 to 0.2 and retry; if still underpowered → STOP pipeline.

---

## 2. Problem Statement

### 2.1 Background

The main hypothesis (H-CalibDiff-v1) requires stratifying 542 programming problems into hard/easy difficulty tiers based on LLM pass@1 performance, then computing ECE per tier with M=15 bins. Reliable ECE computation requires at minimum n=20 problems per bin system to populate bins meaningfully.

Without verifying tier viability first, the downstream ECE analysis (H-M3/H-M4) could fail silently due to degenerate bin counts.

### 2.2 Research Gap

It is unknown whether the specific threshold definitions (hard = pass@1==0.0, easy = pass@1≥0.6) produce sufficient tier sizes on HumanEval+ (164 problems) and MBPP+ (378 problems) for the 3 target model families.

### 2.3 Hypothesis Statement (H-E1)

Under k=5 self-contained solution generation on HumanEval+/MBPP+ (542 problems), if we stratify problems by pass@1 per model (hard = 0/5 correct, easy = ≥3/5 correct), then each tier will contain n≥20 problems per model per benchmark, enabling reliable ECE computation with M=15 bins.

---

## 3. Functional Requirements

### FR-1: Dataset Loading

**FR-1.1: Load HumanEval+ and MBPP+ via EvalPlus**
- Load via `evalplus` Python package (evalplus >= 0.3.0)
- `problems_he = get_human_eval_plus()` → 164 problems
- `problems_mbpp = get_mbpp_plus()` → 378 problems
- Total: 542 problems across both benchmarks
- No filtering required (use all problems)

### FR-2: Solution Generation

**FR-2.1: Generate k=5 Solutions Per Problem Per Model**
- Models: 3 HuggingFace CausalLM checkpoints:
  1. `NousResearch/Meta-Llama-3-8B` (general-purpose, 8B)
  2. `codellama/CodeLlama-7b-hf` (code-specialized, 7B)
  3. `deepseek-ai/deepseek-coder-6.7b-base` (code-specialized, 6.7B)
- Load via: `AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float16, device_map="auto")`
- Generation params: `temperature=0.8, top_p=0.95, max_new_tokens=512, do_sample=True`
- Fixed seed: 42 (all models)
- Total: 542 × 3 × 5 = 8,130 generated solutions

**FR-2.2: Save Solutions**
- Format: JSONL per model — `{task_id, solutions: [str × 5]}`
- Path: `h-e1/results/solutions_{model_name}.jsonl`
- Note: If Run 3 solutions already exist at `h-e1/code/src/h_e1/`, REUSE without regeneration

### FR-3: EvalPlus Correctness Evaluation

**FR-3.1: Execute Each Solution Against EvalPlus Augmented Tests**
- API: `check_correctness(dataset, problem, solution, max_as_limit=30, max_data_limit=30, max_stack_limit=10, min_time_limit=1, gt_time_limit_factor=4.0)`
- Label: `passed = (result["base_status"] == "pass") and (result["plus_status"] == "pass")`
- Save: `{task_id: [bool × 5]}` per model
- Coverage target: ≥95% of problems successfully evaluated

**FR-3.2: Compute Pass@1 Per (Problem, Model)**
- `pass_at_1[task_id] = correct_count / k` → value in {0.0, 0.2, 0.4, 0.6, 0.8, 1.0}

### FR-4: Tier Assignment and Viability Check

**FR-4.1: Assign Difficulty Tiers**
- Hard: `pass@1 == 0.0` (0 correct out of 5)
- Easy: `pass@1 >= 0.6` (≥3 correct out of 5)
- Medium: all other values (excluded from ECE analysis)
- Thresholds: `hard_threshold=0.0`, `easy_threshold=0.6`

**FR-4.2: Count Tier Sizes Per (Model, Benchmark)**
- Compute `n_hard` and `n_easy` separately for:
  - HumanEval+ (164 problems)
  - MBPP+ (378 problems)
- Report per (model, benchmark) pair: 6 counts total for n_hard, 6 for n_easy

**FR-4.3: Gate Evaluation**
- Gate PASS: `n_hard ≥ 20 AND n_easy ≥ 20` for ≥2/3 models on ≥1 benchmark
- If gate fails: relax `hard_threshold` to 0.2, recompute
- If still fails: STOP pipeline

**FR-4.4: Mechanism Activation Verification**
- Run `verify_tier_mechanism_activated()` after tier assignment
- Assert: `n_hard > 0 AND n_easy > 0` for all 3 models
- Assert: `coverage_rate ≥ 0.95`

### FR-5: Visualization

**FR-5.1: Gate Metrics Bar Chart (MANDATORY)**
- Bar chart: n_hard and n_easy per (model, benchmark) vs. threshold n=20
- Save: `h-e1/figures/tier_sizes_bar.png`

**FR-5.2: Pass@1 Distribution Histogram**
- 6-point histogram ({0.0, 0.2, 0.4, 0.6, 0.8, 1.0}) per model per benchmark
- Save: `h-e1/figures/pass_at_1_distribution.png`

**FR-5.3: Tier Size Heatmap**
- Matrix of (model × benchmark) → (n_hard, n_easy)
- Save: `h-e1/figures/tier_size_heatmap.png`

**FR-5.4: Coverage Rate Bar Chart**
- Fraction of problems successfully evaluated per model
- Save: `h-e1/figures/coverage_rate.png`

### FR-6: Results Reporting

**FR-6.1: Save Tier Statistics**
- CSV: `{model, benchmark, n_hard, n_easy, n_medium, n_total, coverage_rate, gate_pass}`
- Path: `h-e1/results/tier_statistics.csv`

**FR-6.2: Pass@1 Data Persistence**
- Save all pass@1 values for downstream use by H-M1/H-M2
- Format: `{task_id: float}` per model in `h-e1/results/pass_at_1_{model}.json`

**FR-6.3: Cross-Model Tier Overlap (Secondary)**
- Jaccard similarity of hard-tier problem sets across model pairs
- Preparatory output for H-M2 analysis

---

## 4. Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed seed=42 for ALL random operations (generation, sampling)
- All intermediate results saved (solutions, correctness labels, pass@1 values)
- Requirements.txt with pinned versions

### NFR-2: Infrastructure (LIGHT Tier — EXISTENCE PoC)
- Configuration: argparse + hardcoded constants (no YAML config files)
- Logging: print statements + CSV/JSON output (no WandB)
- Testing: smoke test on 5 problems per model before full run

### NFR-3: Compute
- Single GPU per CLAUDE.md (set `CUDA_VISIBLE_DEVICES=<empty_gpu>`)
- HuggingFace models: float16 precision, device_map="auto"
- Estimated: 2-4 hours per model on single GPU (8-12h total for all 3 models)

### NFR-4: Code Structure
- Modular: `generate_solutions.py`, `evaluate_solutions.py`, `analyze_tiers.py`, `visualize.py`
- No training code (measurement study)
- All output paths configurable via argparse

---

## 5. Technical Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| Python | ≥3.9 | Runtime |
| PyTorch | ≥2.0 | LLM inference |
| transformers | ≥4.35 | HuggingFace model loading |
| evalplus | ≥0.3.0 | Dataset loading + correctness oracle |
| numpy | ≥1.24 | Pass@1 computation, tier counting |
| matplotlib | ≥3.7 | Visualization |
| pandas | ≥2.0 | Results tables |

---

## 6. Data Specifications

### 6.1 Input Data

| Dataset | Size | Source | Access |
|---------|------|--------|--------|
| HumanEval+ | 164 problems | EvalPlus (Liu et al. 2023) | `evalplus` pip package |
| MBPP+ | 378 problems | EvalPlus (Liu et al. 2023) | `evalplus` pip package |

### 6.2 Intermediate Data

| File | Format | Content |
|------|--------|---------|
| `results/solutions_{model}.jsonl` | JSONL | k=5 generated solutions per problem |
| `results/correctness_{model}.json` | JSON | Pass/fail per (problem, solution) |
| `results/pass_at_1_{model}.json` | JSON | pass@1 value per (problem, model) |

### 6.3 Output Data

| File | Format | Content |
|------|--------|---------|
| `results/tier_statistics.csv` | CSV | n_hard, n_easy, coverage per (model, benchmark) |
| `figures/tier_sizes_bar.png` | PNG | Gate check visualization |
| `figures/pass_at_1_distribution.png` | PNG | 6-point histogram per model |

---

## 7. Success Criteria

### 7.1 Gate Condition (MUST_WORK)

| Criterion | Threshold | Required For |
|-----------|-----------|--------------|
| n_hard per (model, benchmark) | ≥ 20 | Gate pass |
| n_easy per (model, benchmark) | ≥ 20 | Gate pass |
| Models satisfying both | ≥ 2/3 models | Gate pass |
| Benchmark satisfying | ≥ 1 of 2 benchmarks | Gate pass |
| coverage_rate | ≥ 0.95 | Mechanism verified |

**PASS:** Gate conditions met → H-M1 unblocked
**FAIL (threshold relaxation):** Relax hard_threshold to 0.2, retry once
**FAIL (pipeline stop):** Still underpowered after relaxation → STOP

### 7.2 Execution Success Criteria

| Check | Condition |
|-------|-----------|
| Solutions generated | 8,130 (or reused from prior run) |
| EvalPlus evaluations | coverage ≥ 95% (≥515 of 542 problems) |
| Tier assignment runs | All 3 models, both benchmarks |
| Gate evaluated | Binary PASS/FAIL with supporting counts |
| Figures generated | All 4 required figures saved |

---

## 8. Out of Scope

- P(True) logprob elicitation (this is H-M3)
- ECE computation (this is H-M4)
- Temperature scaling or calibration correction (downstream hypotheses)
- Statistical testing across models (this is H-E1 scope: tier counting only)
- New model architectures or fine-tuning

---

## 9. Risks and Mitigations

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| R1: Insufficient hard-tier problems (n_hard < 20) | Low | Relax hard_threshold 0.0 → 0.2 as fallback |
| R2: EvalPlus API errors | Low | Retry logic; fallback to cached solutions from Run 3 |
| R3: CUDA OOM on model loading | Low | float16 + device_map="auto"; try single smaller model first |
| R4: All problems in one tier (degenerate) | Very Low | Assert n_hard > 0 and n_easy > 0 at mechanism activation |
| R5: Low EvalPlus coverage (<95%) | Low | Use subprocess sandbox with timeout; log failures |

---

*Generated by Phase 3 PRD Generation (inline from Phase 2C experiment brief)*
*Source: h-e1/02c_experiment_brief.md*
*BMAD PRD workflow: executed inline (bmm not installed in project)*
*Date: 2026-03-18*
