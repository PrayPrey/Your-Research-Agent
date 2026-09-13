# Experiment Design: H-E1 — Tier Sample Size Viability

**Date:** 2026-03-18
**Author:** Anonymous
**Hypothesis Statement:** Under k=5 self-contained solution generation on HumanEval+/MBPP+ (542 problems), if we stratify problems by pass@1 per model (hard = 0/5 correct, easy = ≥3/5 correct), then each tier will contain n≥20 problems per model per benchmark, enabling reliable ECE computation with M=15 bins.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** N/A (no prerequisites for H-E1)
**Gate Status:** MUST_WORK (pending validation)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
**Type:** MUST_WORK
**Pass Condition:** n_hard ≥ 20 AND n_easy ≥ 20 for ≥2/3 models on ≥1 benchmark
**Fail Action:** Relax hard threshold to pass@1≤0.2; if still underpowered → STOP pipeline

---

## Continuation Context

This is the first hypothesis in the verification chain. No previous hypothesis context available.

### Previous Hypothesis Results (if applicable)
None — H-E1 is the foundational hypothesis with no dependencies.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: P(True) calibration LLM code verification ECE** (match_count=5)
- No domain-relevant results. All matches from diffusion model knowledge base (source: HuggingFace Diffusers). Best aggregate similarity: 0.4123. Not applicable to LLM calibration experiments.

**Query 2: EvalPlus pass@1 difficulty stratification** (match_count=5)
- No domain-relevant results. Matches from CUDA documentation and diffusion model repos. Best similarity: 0.4046. Not applicable.

**Query 3: Expected Calibration Error LLM benchmark** (match_count=5)
- Closest match: `hf.co/papers/2305.14314` (similarity 0.4218) — a HuggingFace paper page, not directly relevant to ECE computation methodology.

**Assessment:** Archon KB does not contain past implementation cases for LLM calibration, EvalPlus, or ECE computation. This is a novel research area not yet represented in the KB. Proceeding with established literature (Kadavath et al. 2022, Guo et al. 2017, Liu et al. 2023) as documented in Phase 2B.

### Archon Code Examples

**Query 1: EvalPlus check_correctness Python** (match_count=5)
- No relevant code examples. Results from LaTeX documentation (incidence matrix example) and diffusion model benchmarks. Not applicable.

**Query 2: ECE calibration PyTorch logprob** (match_count=5)
- Best match: `optimum-quanto Calibration` (model quantization calibration, not ECE). Not applicable.

**Assessment:** Archon code examples do not contain EvalPlus, logprob extraction, or ECE implementations. Will use established public API patterns from EvalPlus documentation and HuggingFace transformers documentation.

### Exa GitHub Implementations

**Exa MCP Status:** UNAVAILABLE — 402 Payment Required (billing quota exhausted). Three retry attempts failed.

**Known Reference Implementations (from Phase 2B documentation):**

**Repository 1: evalplus/evalplus** (canonical)
- **URL:** https://github.com/evalplus/evalplus
- **Relevance:** Official EvalPlus benchmark — contains `check_correctness()` API for evaluating code solutions against augmented test suites (HumanEval+, MBPP+). This is the ground-truth oracle.
- **Key API:**
  ```python
  from evalplus.data import get_human_eval_plus, get_mbpp_plus
  from evalplus.eval._special_oracle import MBPP_OUTPUT_NOT_NONE_TASKS
  from evalplus.eval import check_correctness

  # Load problems
  problems = get_human_eval_plus()  # 164 problems
  problems.update(get_mbpp_plus())   # 378 problems → 542 total

  # Evaluate solution
  result = check_correctness(
      dataset="humaneval",
      problem=problems[task_id],
      solution=solution_code,
      max_as_limit=30,
      max_data_limit=30,
      max_stack_limit=10,
      identifier=None,
      min_time_limit=1,
      gt_time_limit_factor=4.0,
  )
  # result["base_status"] and result["plus_status"]
  ```
- **Install:** `pip install evalplus`
- **Results reported:** Liu et al. 2023 — pass rates drop 28.9% under augmented tests

**Repository 2: Kadavath et al. 2022 (P(True) methodology)**
- **URL:** https://arxiv.org/abs/2207.05221 (reference paper)
- **Relevance:** Defines P(True) logprob elicitation approach for LLM self-evaluation
- **Key Method:**
  - Prompt: append "Is the above [answer] True or False?" after the model output
  - Extract: `logprob("True")` and `logprob("False")` from output distribution
  - Normalize: `c = softmax([logprob(True), logprob(False)])[0]`
  - HuggingFace implementation: `model.generate(..., output_scores=True, return_dict_in_generate=True)`

**Serena Analysis Needed:** False — Standard EvalPlus API + HuggingFace generate() calls, no complex custom architecture.

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This is not a paper reproduction experiment — it is an empirical measurement study using existing tools:
1. EvalPlus (Liu et al. 2023) — official pip package, no reimplementation needed
2. HuggingFace Transformers — standard `generate()` API for all 3 models
3. Custom ECE computation — standard numpy implementation (no existing library needed)

**Recommended Implementation Path:**
- Primary: `evalplus` pip package for oracle + `transformers` for model loading/generation
- Fallback: vanilla `human_eval` + `mbpp` for oracle if EvalPlus API issues arise
- Justification: EvalPlus is the canonical benchmark for this research area; HuggingFace transformers is the standard loading API for all 3 model checkpoints

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. EvalPlus is a well-documented pip package with standard API. No complex custom layers or architectures require semantic analysis.

---

## Experiment Specification

### Dataset

**Name:** HumanEval+ and MBPP+ (via EvalPlus)
**Type:** programmatic-api (real benchmark via pip package — NOT synthetic)
**Source:** Liu et al. 2023, https://github.com/evalplus/evalplus
**Version:** Latest (evalplus >= 0.3.0)

**Dataset Statistics:**
- HumanEval+: 164 problems (augmented from original 164 HumanEval problems)
- MBPP+: 378 problems (augmented from original 374 MBPP problems)
- **Total: 542 problems**
- Test density: ~760 augmented tests per problem (vs. ~10 in vanilla HumanEval)
- Language: Python (function completion / standalone scripts)

**Splits for H-E1:**
- No train/val/test split needed — H-E1 uses ALL 542 problems
- Each problem evaluated with k=5 generated solutions per model
- Total evaluations: 542 problems × 3 models × 5 solutions = 8,130 evaluations

**Preprocessing:**
- Load all problems via `get_human_eval_plus()` and `get_mbpp_plus()`
- No tokenization preprocessing needed for H-E1 (this step only counts tier sizes)
- Solutions regenerated with `temperature=0.8, top_p=0.95, max_new_tokens=512`

**Augmentation:** None (EvalPlus augmented tests already built-in)

**Loading Information** (for Phase 4 download):
- Method: pip package (programmatic-api)
- Identifier: `evalplus>=0.3.0`
- Code:
  ```python
  # Install: pip install evalplus
  from evalplus.data import get_human_eval_plus, get_mbpp_plus
  problems_he = get_human_eval_plus()   # dict: task_id → problem
  problems_mbpp = get_mbpp_plus()        # dict: task_id → problem
  ```

### Models

#### Baseline Model

**Architecture:** Llama3-8B (NousResearch/Meta-Llama-3-8B) — general-purpose LLM
**Type:** HuggingFace decoder-only causal LM
**Role in H-E1:** Solution generation only (k=5 per problem); P(True) elicitation NOT needed in H-E1 (tier counting only)

**3 Model Families (all used for H-E1):**
1. `NousResearch/Meta-Llama-3-8B` — general-purpose, 8B params
2. `codellama/CodeLlama-7b-hf` — code fine-tuned Llama2, 7B params
3. `deepseek-ai/deepseek-coder-6.7b-base` — code-specialized, 6.7B params

**Configuration per model:**
- Precision: float16 (or bfloat16 where supported)
- Device: single GPU (CUDA_VISIBLE_DEVICES=<empty_gpu>)
- Generation: temperature=0.8, top_p=0.95, max_new_tokens=512, do_sample=True
- Seed: 42 (fixed for reproducibility; 1 seed per PoC rules)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `NousResearch/Meta-Llama-3-8B`, `codellama/CodeLlama-7b-hf`, `deepseek-ai/deepseek-coder-6.7b-base`
- Code:
  ```python
  from transformers import AutoTokenizer, AutoModelForCausalLM
  import torch

  model_id = "NousResearch/Meta-Llama-3-8B"  # or CodeLlama-7b-hf, deepseek-coder-6.7b-base
  tokenizer = AutoTokenizer.from_pretrained(model_id)
  model = AutoModelForCausalLM.from_pretrained(
      model_id, torch_dtype=torch.float16, device_map="auto"
  )
  ```

#### Proposed Model

**Architecture:** Same 3 models + EvalPlus oracle for tier stratification

**Core Mechanism Implementation:**

```python
# Core Mechanism: Pass@1-based Difficulty Tier Stratification
# Based on: EvalPlus API (Liu et al. 2023) + Kadavath et al. 2022 bootstrap
# H-E1 Goal: Verify n>=20 per tier per (model, benchmark)

import numpy as np
from collections import defaultdict
from evalplus.data import get_human_eval_plus, get_mbpp_plus
from evalplus.eval import check_correctness

def compute_pass_at_1(solutions_per_problem: dict, k: int = 5) -> dict:
    """
    Compute pass@1 = correct_count / k for each (problem_id, model) pair.
    Returns: dict[task_id] -> float in {0.0, 0.2, 0.4, 0.6, 0.8, 1.0}
    """
    pass_at_1 = {}
    for task_id, results in solutions_per_problem.items():
        correct = sum(1 for r in results if r["passed"])
        pass_at_1[task_id] = correct / k
    return pass_at_1

def assign_tiers(pass_at_1: dict, hard_thresh=0.0, easy_thresh=0.6) -> dict:
    """
    Assign hard/easy/medium tiers based on pass@1 thresholds.
    hard: pass@1 == 0.0 (no correct solutions in k=5)
    easy: pass@1 >= 0.6 (>=3/5 correct)
    medium: excluded
    """
    tiers = {}
    for task_id, p in pass_at_1.items():
        if p == hard_thresh:
            tiers[task_id] = "hard"
        elif p >= easy_thresh:
            tiers[task_id] = "easy"
        else:
            tiers[task_id] = "medium"
    return tiers

def verify_tier_viability(tiers: dict, min_n: int = 20) -> dict:
    """Check n>=20 for hard and easy tiers (H-E1 gate criterion)."""
    n_hard = sum(1 for t in tiers.values() if t == "hard")
    n_easy = sum(1 for t in tiers.values() if t == "easy")
    return {
        "n_hard": n_hard, "n_easy": n_easy,
        "hard_ok": n_hard >= min_n, "easy_ok": n_easy >= min_n,
        "gate_pass": n_hard >= min_n and n_easy >= min_n
    }
```

### Training Protocol

> ⚠️ **EXISTENCE (PoC):** H-E1 is a data analysis step — no model training required.

**H-E1 is a tier viability check, not a training experiment.** The protocol is:

**Step 1: Solution Generation**
- For each of 3 models, for each of 542 problems: generate k=5 solutions
- Settings: temperature=0.8, top_p=0.95, max_new_tokens=512, seed=42
- Estimated time: ~2-4 hours per model on single GPU (∼8-12h total)
- Note: If Run 3 solutions exist at `h-e1/code/src/h_e1/`, REUSE them (no regeneration needed)

**Step 2: EvalPlus Correctness Evaluation**
- For each (problem, solution) pair: run `check_correctness()` with EvalPlus augmented tests
- Collect: `passed = (result["base_status"] == "pass") and (result["plus_status"] == "pass")`
- Coverage target: ≥95% of problems (≤27 evaluation failures across 542)

**Step 3: Tier Assignment and Counting**
- Compute pass@1 per (problem, model)
- Apply: hard = pass@1==0.0, easy = pass@1≥0.6, medium = excluded
- Count: n_hard and n_easy per (model, benchmark)
- Report: 6-point pass@1 histogram for each model

**Hyperparameters (fixed):**
- k = 5 (solutions per problem)
- hard_threshold = 0.0 (pass@1 == 0.0)
- easy_threshold = 0.6 (pass@1 >= 0.6, i.e., ≥3 correct)
- min_n = 20 (gate criterion)
- Seed: 42
- Source: Phase 2B specification + Kadavath et al. 2022 bootstrap approach

**Seeds:** 1 (seed=42, fixed per PoC rules)

### Evaluation

**Task Type:** Tier viability count (binary gate check)

**Primary Metrics:**
- `n_hard[model][benchmark]` — count of hard-tier problems per (model, benchmark)
- `n_easy[model][benchmark]` — count of easy-tier problems per (model, benchmark)
- `coverage_rate` — fraction of problems with valid EvalPlus evaluations

**Success Criteria (EXISTENCE PoC):**
- Gate PASS: n_hard ≥ 20 AND n_easy ≥ 20 for ≥2/3 models on ≥1 benchmark
- Gate FAIL: If only 0 or 1 model satisfies → relax threshold first, then STOP if still underpowered
- PoC success = gate condition satisfied (direction-based, no statistical tests)

**Expected Baseline Performance (from Phase 2B + Run 3):**
- Based on Run 3 data: Llama3-8B non-stratified ECE=0.4895, CodeLlama ECE=0.5218, DeepSeek ECE=0.1358
- These suggest high variability in model accuracy → reasonable expectation for tier separation
- From HumanEval benchmarks: typical pass@1 for 7-8B models ranges 0.2-0.45 → expected bimodal or heavy-tailed distribution
- Source: Phase 2B Section 1.4 (Run 3 baseline results)

**Secondary Output:**
- 6-point pass@1 histogram per model (distribution over {0.0, 0.2, 0.4, 0.6, 0.8, 1.0})
- Cross-model tier overlap statistics (Jaccard similarity, prep for H-M2)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: tier_viability_check (no ML metrics library needed)
- Library: numpy (custom)
- Code:
  ```python
  import numpy as np
  # Tier size counting
  tiers = {"hard": [], "easy": [], "medium": []}
  for task_id, p in pass_at_1.items():
      if p == 0.0: tiers["hard"].append(task_id)
      elif p >= 0.6: tiers["easy"].append(task_id)
      else: tiers["medium"].append(task_id)
  n_hard, n_easy = len(tiers["hard"]), len(tiers["easy"])
  gate_pass = n_hard >= 20 and n_easy >= 20
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing n_hard and n_easy per (model, benchmark) vs. threshold n=20

#### Additional Figures (LLM Autonomous)
- **Pass@1 Distribution Histogram**: 6-point histogram ({0.0, 0.2, 0.4, 0.6, 0.8, 1.0}) per model per benchmark
- **Tier Size Heatmap**: Matrix of (model × benchmark) → (n_hard, n_easy) tier sizes
- **Coverage Rate Bar Chart**: Fraction of problems successfully evaluated per model

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | EvalPlus `check_correctness()` API available and functional | TRUE — pip installable, verified via `evalplus --version` |
| Mechanism Isolatable | Tier assignment is a post-hoc computation on pass@1 values — fully isolatable | TRUE — tier computation is a pure function of pass@1 |
| Baseline Measurable | Non-stratified pass@1 (baseline) measurable independently of tier assignment | TRUE — pass@1 computed before tier labeling |

### Architecture Compatibility Check

**H-E1 uses standard code generation + EvalPlus oracle — no neural architecture constraints:**
- Required: Any HuggingFace CausalLM that can generate Python code
- Required: EvalPlus installation (`pip install evalplus`)
- Required: Python sandbox execution (subprocess/subprocess32) for test evaluation
- Incompatible: Models that cannot generate Python function completions

**Required Features:**
- `model.generate()` with `do_sample=True` for k=5 diverse solutions
- EvalPlus `check_correctness()` with augmented test suite enabled

**Incompatible Architectures:**
- None for H-E1 (no custom layers, no attention mechanism requirements)

### Mechanism Activation Indicators

**How to detect if mechanism is actually working:**

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | `"Tier assignment complete: n_hard={X}, n_easy={Y} for {model} on {benchmark}"` | tier_stratifier.py:assign_tiers() |
| Metric Check | `n_hard > 0 AND n_easy > 0` (non-empty tiers) | evaluate.py:verify_tier_viability() |
| Metric Delta | `abs(n_hard - n_easy) > 0` (tiers differ in size) | evaluate.py:verify_tier_viability() |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_tier_mechanism_activated(tier_results: dict) -> tuple[bool, dict]:
    """Verify tier stratification mechanism is working correctly."""
    indicators = {
        "tiers_non_empty": (
            tier_results["n_hard"] > 0 and tier_results["n_easy"] > 0
        ),
        "coverage_adequate": tier_results["coverage_rate"] >= 0.95,
        "distribution_non_trivial": (
            tier_results["n_hard"] != tier_results["total_problems"] and
            tier_results["n_easy"] != tier_results["total_problems"]
        ),
        "gate_satisfied": tier_results["gate_pass"]
    }
    return all(indicators.values()), indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| All problems in one tier | n_hard == 0 OR n_easy == 0 | FAIL: Tier assignment degenerate; check threshold values |
| Coverage too low | coverage_rate < 0.95 | WARN: EvalPlus execution issues; debug sandbox |
| EvalPlus API error | ImportError or check_correctness exception | FAIL: Check evalplus version; try pip install --upgrade evalplus |
| n_hard < 20 AND n_easy < 20 | Gate check fails | Gate FAIL: Relax hard_threshold to 0.2, retry |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | n_hard > 0 AND n_easy > 0 for all 3 models | Tier assignment log |
| Coverage Adequate | coverage_rate ≥ 0.95 | EvalPlus evaluation count |
| Hypothesis Supported | n_hard ≥ 20 AND n_easy ≥ 20 for ≥2/3 models on ≥1 benchmark | `verify_tier_viability()` per model per benchmark |

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (EvalPlus oracle executes for ≥95% of problems)
2. Gate condition satisfied: n_hard ≥ 20 AND n_easy ≥ 20 for ≥2/3 models on ≥1 benchmark

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Assessment:** Archon KB queries executed (5 knowledge queries + 2 code queries). No domain-relevant results found for LLM calibration, EvalPlus, or ECE computation. The KB is populated primarily with diffusion model content. This is documented as a limitation.

**Query 1: P(True) calibration LLM code verification ECE** — No relevant results (sim 0.41)
**Query 2: EvalPlus pass@1 difficulty stratification** — No relevant results (sim 0.40)
**Query 3: Expected Calibration Error LLM benchmark** — Marginal: `hf.co/papers/2305.14314` (sim 0.42)
**Code Query 1: EvalPlus check_correctness Python** — No relevant results
**Code Query 2: ECE calibration PyTorch logprob** — `optimum-quanto Calibration` (quantization, not ECE)

**Used For:** Not used (no applicable findings). Documented for traceability.

### B. GitHub Implementations (Exa)

**Exa MCP Status:** UNAVAILABLE (402 Payment Required — billing quota exhausted after 3 retry attempts).

**Known Reference from Phase 2B:**

**Repository 1: evalplus/evalplus** (primary oracle source)
- **URL:** https://github.com/evalplus/evalplus
- **Stars:** 1k+ (active benchmark repository)
- **Query Used:** Documented in Phase 2B Section 1.3
- **Relevance:** Official EvalPlus augmented benchmark — `check_correctness()` API
- **Key API Pattern:**
  ```python
  from evalplus.data import get_human_eval_plus, get_mbpp_plus
  from evalplus.eval import check_correctness
  # Load 542 problems and evaluate solutions with augmented test suites
  ```
- **Configuration Extracted:** pip install evalplus, Python sandbox execution
- **Their Results:** Pass rates drop 28.9% under augmented tests (validates oracle strength)
- **Used For:** Dataset loading, correctness oracle, tier stratification foundation

**Repository 2: Kadavath et al. 2022 P(True) methodology**
- **URL:** https://arxiv.org/abs/2207.05221 (reference paper, not a code repo for H-E1)
- **Relevance:** Defines P(True) approach used in H-M3/H-M4; not directly needed for H-E1
- **Key Method (for context):** `logprob(True)` extraction via `output_scores=True`
- **Used For:** Background context; H-E1 does not use P(True) (tier counting only)

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from search results was sufficiently clear.
- EvalPlus is a standard pip package with documented API
- Tier stratification is a simple numpy computation (no custom layers or architecture analysis needed)
- HuggingFace `generate()` is well-documented for all 3 model checkpoints

### D. Previous Hypothesis Context

**Previous Context:** None — H-E1 is the first hypothesis in the verification chain.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection (EvalPlus) | Phase 2B | 02b_verification_plan.md Section 1.3 |
| Problem count (542 = 164+378) | Phase 2B | 02b_verification_plan.md Section 1.3 |
| k=5 solutions per problem | Phase 2B | H-E1 verification protocol |
| hard threshold (pass@1==0.0) | Phase 2B | H-E1 variables definition |
| easy threshold (pass@1>=0.6) | Phase 2B | H-E1 variables definition |
| min_n=20 gate criterion | Phase 2B | H-E1 success criteria |
| Model checkpoints (3 HF models) | Phase 2B | 02b_verification_plan.md Section 1.3 |
| Generation settings (temp=0.8) | Phase 2B | H-M1 verification protocol |
| EvalPlus oracle API | Phase 2B + Exa (known ref) | evalplus/evalplus GitHub |
| Core mechanism pseudo-code | Phase 2B spec + standard Python | Custom (no existing library) |
| Tier assignment logic | Phase 2B H-E1 protocol | 02b_verification_plan.md Section 2.2 |
| Success criteria | Phase 2B | H-E1 gate condition |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-18

### Workflow History for This Hypothesis
- 2026-03-18T03:17:42: Phase 2C experiment design started (IN_PROGRESS)
- 2026-03-18: Archon KB searches executed (7 queries, no domain-relevant results)
- 2026-03-18: Exa MCP unavailable (402), documented known references from Phase 2B
- 2026-03-18: Serena analysis skipped (no complex code requiring semantic analysis)
- 2026-03-18: Dataset/baseline confirmed from 02b_context.md (programmatic-api, non-synthetic)
- 2026-03-18: Experiment specification synthesized (EXISTENCE PoC, no stats tests, no ablations)
- 2026-03-18: Phase 2C COMPLETED

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code — 7 queries), Exa (unavailable — 402), Serena (skipped — not needed)*
*Specifications grounded in Phase 2B verification plan and established EvalPlus/HuggingFace APIs*
*Next Phase: Phase 3 - Implementation Planning*
