# Experiment Design: h-m1

**Date:** 2026-03-18
**Author:** Anonymous
**Hypothesis Statement:** Under EvalPlus augmented test execution, if k=5 solutions are generated per problem per model using temperature sampling and evaluated via EvalPlus check_correctness, then pass@1 values are reliably computed with ≥95% problem coverage (≤5% generation failures), because the Run 3 infrastructure is validated and reusable with minimal modifications.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (PoC) Template** — Infrastructure re-validation: confirms pass@1 computation pipeline is stable and reusable for h-m2 through h-m4.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-E1 → MUST_WORK PASS (2026-03-18T08:21) ✅
**Gate Status:** MUST_WORK (to be evaluated after Phase 4 execution)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m1
- **Type:** MECHANISM (Step 1 of 4 in causal chain H-M1 → H-M2 → H-M3 → H-M4)
- **Prerequisites:** h-e1 (MUST_WORK → PASS)

### Gate Condition

**MUST_WORK gate — both conditions required:**
1. **Coverage ≥ 95%**: At most 27 of 542 problems may have generation failures (across all 3 models)
2. **Non-trivial distribution**: pass@1 values are not all 0.0 or all 1.0 per model (std > 0)

**If FAIL:** Debug EvalPlus API compatibility; fallback to vanilla HumanEval/MBPP oracle with note

---

## Continuation Context

### Reuse from h-e1 (Validated Infrastructure)

h-m1 is a **continuation experiment** that directly reuses h-e1 validated infrastructure.

| Component | Reuse Decision | Rationale |
|-----------|---------------|-----------|
| Dataset (EvalPlus HumanEval+ + MBPP+) | ✅ REUSE — already cached at `~/.cache/evalplus/` | Same 542 problems; EvalPlus augmented oracle already verified |
| Models (3 LLMs) | ✅ REUSE — already downloaded at `~/.cache/huggingface/` | Same 3 model checkpoints from Run 3 and h-e1 |
| `generate_solutions.py` | ✅ REUSE with minor extension | h-e1 validated generation for all 542 × 3 models; coverage check adds minimal overhead |
| `evaluate_solutions.py` | ✅ REUSE | EvalPlus API fix known: read `_eval_results.json` when `evaluate()` returns None |
| `analyze_tiers.py` | ✅ EXTEND — add coverage stats | Tier analysis works; extend to compute pass@1 distribution statistics |
| Conda env `youra-h-e1` | ✅ REUSE | All deps installed; use same env or create `youra-h-m1` from same requirements |

**H-M1 delta over h-e1 (new code needed):**
- Coverage rate computation module (`compute_coverage_rate`)
- pass@1 distribution statistics per model (`mean`, `std`, `min`, `max`, `6-point histogram`)
- Verification of 6-point pass@1 distribution ({0.0, 0.2, 0.4, 0.6, 0.8, 1.0}) completeness
- Output: `results/pass_at_1_hm1_verified.json` (canonical file consumed by h-m2)

### Previous Hypothesis Results (h-e1)

| Finding | Value | Implication for h-m1 |
|---------|-------|----------------------|
| Coverage rate | 1.0 (all 542 × 3 models) | Expect near-100% coverage; 95% threshold is conservative |
| Pass@1 files | `h-e1/results/pass_at_1_*.json` (3 files) | Primary input; h-m1 loads + validates + re-exports |
| Correctness files | `h-e1/results/correctness_*.json` (3 files) | Raw correctness data available for recomputation |
| Primary benchmark | MBPP+ (378 problems) — more reliable tier separation | Verify coverage on MBPP first |
| EvalPlus fix | `evaluate()` returns None when cache exists → read `_eval_results.json` directly | Apply same fix |
| CodeLlama note | n_easy=0 on HumanEval (all problems "hard") | Expected; still passes MBPP gate |

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Assessment:** Archon KB contains primarily image generation / diffusers content. No domain-relevant results for EvalPlus or LLM code evaluation were found (similarity scores 0.28–0.47, all from HuggingFace diffusers/image generation repos). The knowledge base does not index code evaluation literature.

**Query 1:** "EvalPlus pass@k solution generation coverage" → Results: diffusers/HuggingFace image gen repos (not relevant)
**Query 2:** "LLM code evaluation pass@1 implementation challenges" → Results: diffusers community examples (not relevant)
**Query 3:** "code benchmark evaluation temperature sampling HuggingFace" → Best result: hf.co/papers/2306.00637 (similarity 0.47 — borderline; about temperature/sampling but not pass@k)

**Code Examples Query:** "generate solutions temperature sampling pass@k" → Results: DPM-Solver diffusion sampling (not relevant)

**Conclusion:** Archon KB provides no directly applicable insights for this domain. Exa GitHub search (Step 3) provides all necessary implementation grounding.

### Archon Code Examples

**Assessment:** No relevant code examples found. All code examples returned are from diffusers/image generation domain (DPM-Solver, DEIS, AYS scheduling). Not applicable to LLM code evaluation.

### Exa GitHub Implementations

**Query 1: EvalPlus official repository (HIGHEST PRIORITY)**

**Repository 1:** `evalplus/evalplus` ⭐ (NeurIPS'23 — official EvalPlus framework)
- **URL:** https://github.com/evalplus/evalplus
- **Relevance:** ⭐⭐⭐ HIGHEST — this IS the evaluation framework for h-m1. Official ground truth.
- **Version in use:** v0.2.x (MBPP+ 378 tasks, HumanEval+ 164 tasks — matches our 542 total)
- **Key API:**
  ```python
  from evalplus.data import get_human_eval_plus, get_mbpp_plus, write_jsonl

  # Load problems
  problems = get_human_eval_plus()   # 164 problems
  problems = get_mbpp_plus()         # 378 problems

  # Generate solutions → write to samples.jsonl
  samples = [
      dict(task_id=task_id, solution=GEN_SOLUTION(problem["prompt"]))
      for task_id, problem in problems.items()
      for _ in range(k)  # k=5 solutions per problem
  ]
  write_jsonl("samples.jsonl", samples)

  # Evaluate
  evalplus.evaluate --dataset [humaneval|mbpp] --samples samples.jsonl
  # OR: python evalplus/evaluate.py --dataset humaneval --samples samples.jsonl
  ```
- **Results format:** `samples_eval_results.json` (or `_eval_results.json` in cache)
- **Known issue:** `evaluate()` returns None with cached results → read JSON directly (fixed in h-e1)
- **Pass@k formula:** Standard Chen et al. 2021 unbiased estimator

**Repository 2:** `openai/human-eval` ⭐ (Original HumanEval reference)
- **URL:** https://github.com/openai/human-eval
- **Relevance:** ⭐⭐ Reference for pass@k estimation formula
- **Key insight:** Standard evaluation: generate n=200 solutions, compute pass@1/10/100
- **Formula:** `evaluate_functional_correctness samples.jsonl` → `{'pass@1': ..., 'pass@10': ..., 'pass@100': ...}`

**Repository 3:** `bigcode-project/bigcode-evaluation-harness` ⭐ (Comprehensive benchmark harness)
- **URL:** https://github.com/bigcode-project/bigcode-evaluation-harness
- **Relevance:** ⭐⭐ Standard harness showing HumanEval+ / MBPP+ evaluation conventions
- **Key insight:** For pass@k estimation, `n=200 > k` solutions generated per problem (Chen et al. approach)
- **For MBPP:** `n=15 > k=1` solutions per problem at temperature=0.1; `n_samples=15`
- **Augmented tests:** `--tasks mbppplus --n_samples 200 --temperature 0.2`

**Query 2: Pass@k estimation and coverage computation**

**Key finding from bigcode harness docs:**
> "We follow Chen et al. approach for pass@k estimation, where n=200 > k solutions are generated per problem. Low temperatures generally work better for small k in pass@k."

**For our k=5 setup:** n=5 solutions per problem (h-e1 established this as sufficient for difficulty stratification). Coverage = fraction of problems where ALL k solutions are successfully generated and evaluated.

**Serena Analysis Needed:** false (code patterns from Exa are clear)

### 🎯 Implementation Priority Assessment

**For h-m1 (infrastructure re-validation), implementation priority:**

| Priority | Approach | Rationale |
|----------|----------|-----------|
| ⭐⭐⭐ HIGHEST | Load h-e1 pass@1 + correctness files directly | Already computed; zero additional GPU time needed |
| ⭐⭐ MEDIUM | Re-run evaluation on h-e1 solutions if files incomplete | EvalPlus evaluation is fast (<10min); generation not needed |
| ⭐ LOW | Full regeneration from scratch | Only if h-e1 solutions corrupted; takes ~3-4h |

**Recommended Implementation Path:**
- **Primary:** Load `h-e1/results/pass_at_1_*.json` + `h-e1/results/correctness_*.json` → compute coverage + distribution stats → write verified output
- **Fallback:** If pass@1 files missing, re-run `evaluate_solutions.py` on existing solutions (no generation needed)
- **Justification:** h-e1 already achieved coverage=1.0. H-M1 is a verification step, not a new computation. Minimizing GPU usage is appropriate for this infrastructure validation hypothesis.

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. EvalPlus API documented comprehensively in official docs and PyPI pages. h-e1 code (`generate_solutions.py`, `evaluate_solutions.py`) already validated and understood.

---

## Experiment Specification

### Dataset

**Name:** EvalPlus — HumanEval+ (164 problems) + MBPP+ (378 problems)
**Type:** standard (real, established academic benchmark — NOT synthetic)
**Source:** Liu et al. 2023, NeurIPS'23 — https://github.com/evalplus/evalplus
**Version:** HumanEval+ v0.1.10, MBPP+ v0.2.0 (378 tasks after quality filter from 399)
**Total Problems:** 542 (164 + 378)
**Augmented Tests:** ~760 tests/problem (80x HumanEval, 35x MBPP)
**Cache Path:** `~/.cache/evalplus/` (already populated by h-e1)
**HuggingFace Datasets:**
- HumanEval+: `evalplus/humanevalplus`
- MBPP+: `evalplus/mbppplus` (378 rows)

**Dataset Fit Confirmation:**
- ✅ IV (k=5 solution generation) operates on these 542 problems
- ✅ DV (coverage rate, pass@1 distribution) is directly measured on this dataset
- ✅ Same dataset as h-e1 → controlled experiment (only coverage computation added)

**Loading Information** (for Phase 4 download):
- Method: `evalplus` Python package (programmatic-api)
- Identifier: `get_human_eval_plus()`, `get_mbpp_plus()`
- Code: `from evalplus.data import get_human_eval_plus, get_mbpp_plus`

### Models

#### Baseline Model

**Architectures (3 models, all decoder-only LLMs):**

| Model | HuggingFace ID | Type | Size | Status |
|-------|---------------|------|------|--------|
| Llama3-8B | `NousResearch/Meta-Llama-3-8B` | General-purpose | 8B | Downloaded in h-e1 |
| CodeLlama-7B | `codellama/CodeLlama-7b-hf` | Code-specialized (fine-tuned from Llama) | 7B | Downloaded in h-e1 |
| DeepSeek-Coder-6.7B | `deepseek-ai/deepseek-coder-6.7b-base` | Code-specialized (trained from scratch) | 6.7B | Downloaded in h-e1 |

**Configuration:**
- All models: decoder-only autoregressive generation
- Tokenizer: model-specific (from HuggingFace)
- Inference: single GPU (CUDA_VISIBLE_DEVICES set to empty GPU)
- Precision: fp16 or bf16 (as validated in h-e1)

**Model Fit Confirmation:**
- ✅ Same 3 models as h-e1 → reuse downloaded weights
- ✅ Generation parameters validated in h-e1 (temperature=0.8, k=5)
- ✅ These models span general-purpose → code-adapted → code-specialized (needed for H-M4 architecture analysis)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace `transformers`
- Identifier: `NousResearch/Meta-Llama-3-8B`, `codellama/CodeLlama-7b-hf`, `deepseek-ai/deepseek-coder-6.7b-base`
- Code:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float16, device_map="auto")
  tokenizer = AutoTokenizer.from_pretrained(model_id)
  ```

#### Proposed Model

**Architecture:** Same models + coverage verification wrapper (no model modification)

**Core Mechanism Implementation:**

```python
# Core Mechanism: pass@1 Coverage Verification for h-m1
# Based on: h-e1/code/src/h_e1/ validated infrastructure
# Purpose: Verify >=95% problem coverage and non-trivial pass@1 distribution

import json
import numpy as np
from pathlib import Path

def load_or_recompute_pass_at_1(h_e1_results_dir: Path, model_name: str) -> dict:
    """Load h-e1 pass@1 results; recompute from correctness if needed."""
    pass_at_1_file = h_e1_results_dir / f"pass_at_1_{model_name}.json"
    correctness_file = h_e1_results_dir / f"correctness_{model_name}.json"

    if pass_at_1_file.exists():
        with open(pass_at_1_file) as f:
            return json.load(f)  # {task_id: pass@1_value}

    # Recompute from correctness data
    with open(correctness_file) as f:
        correctness = json.load(f)  # {task_id: [bool, bool, bool, bool, bool]}
    return {tid: sum(results) / len(results) for tid, results in correctness.items()}

def compute_coverage_rate(pass_at_1: dict, total_problems: int) -> float:
    """Coverage = fraction of problems with valid evaluations."""
    return len(pass_at_1) / total_problems  # Target: >= 0.95

def compute_distribution_stats(pass_at_1: dict) -> dict:
    """Compute non-triviality statistics for pass@1 distribution."""
    values = list(pass_at_1.values())
    histogram = {v: values.count(v) for v in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]}
    return {
        "mean": np.mean(values), "std": np.std(values),
        "min": np.min(values),   "max": np.max(values),
        "histogram_6pt": histogram,
        "non_trivial": np.std(values) > 0  # Gate check
    }

def verify_gate(coverage: float, stats: dict) -> tuple[bool, list]:
    """Check MUST_WORK gate conditions."""
    checks = []
    gate_pass = coverage >= 0.95 and stats["non_trivial"]
    checks.append(f"coverage={coverage:.4f} >= 0.95: {'PASS' if coverage >= 0.95 else 'FAIL'}")
    checks.append(f"non_trivial (std={stats['std']:.4f} > 0): {'PASS' if stats['non_trivial'] else 'FAIL'}")
    return gate_pass, checks
```

### Training Protocol

**Note:** h-m1 is an infrastructure validation experiment — NO model training required.

**Execution Protocol (replacing training):**

| Step | Action | Details |
|------|--------|---------|
| 1 | Load h-e1 results | Read `pass_at_1_*.json` from `h-e1/results/` for all 3 models |
| 2 | Compute coverage rates | `len(pass_at_1) / 542` per model (HumanEval: /164, MBPP: /378) |
| 3 | Compute distribution stats | mean, std, min, max, 6-point histogram per model |
| 4 | Verify non-triviality | Check std > 0 per model per benchmark |
| 5 | Evaluate gate | Coverage ≥ 0.95 AND non-trivial per model |
| 6 | Export verified file | Write `results/pass_at_1_hm1_verified.json` for h-m2 consumption |

**Fixed Parameters (from h-e1 validation):**

| Parameter | Value | Source |
|-----------|-------|--------|
| k (solutions per problem) | 5 | Phase 2A design; h-e1 validated |
| Temperature (if regen needed) | 0.8 | h-e1 validated parameter |
| Top-p (if regen needed) | 0.95 | Standard BigCode harness convention |
| Random seed | Fixed (same as h-e1) | h-e1 established |
| Models | 3 (Llama3-8B, CodeLlama-7B, DeepSeek-6.7B) | h-e1 downloaded + validated |
| Benchmarks | HumanEval+ (164) + MBPP+ (378) | h-e1 established |

**Seeds:** 1 (fixed; same seed as h-e1 for reproducibility)

**Computational Cost Estimate:**
- **Expected runtime:** < 5 minutes (loading JSON + computing statistics)
- **GPU required:** None for coverage verification (CPU only)
- **GPU required if regen:** ~3-4 hours (h-e1 precedent)

### Evaluation

**Primary Metrics:**

| Metric | Definition | Target (MUST_WORK) |
|--------|-----------|-------------------|
| Coverage Rate | `n_evaluated / n_total` per model per benchmark | ≥ 0.95 (≥95%) |
| Distribution Non-triviality | `std(pass@1) > 0` per model | TRUE for all 3 models |

**Secondary Metrics:**

| Metric | Definition | Target |
|--------|-----------|--------|
| 6-point histogram | Count per pass@1 ∈ {0.0, 0.2, 0.4, 0.6, 0.8, 1.0} | Non-zero in ≥3 buckets |
| Mean pass@1 per model | Average pass@1 across problems | Report (no threshold) |
| Hard-tier size | n with pass@1=0.0 per model | ≥20 (already validated by h-e1) |
| Easy-tier size | n with pass@1≥0.6 per model | ≥20 on ≥1 benchmark (validated by h-e1) |

**Success Criteria:**
- **Primary PASS:** coverage ≥ 0.95 AND std(pass@1) > 0 for all 3 models
- **Partial:** coverage ≥ 0.95 for ≥2/3 models → investigate failing model
- **FAIL → Debug:** coverage < 0.95 → check EvalPlus API; verify solution file integrity

**Expected Performance (from h-e1):**
- Coverage: 1.0 (perfect) — h-e1 demonstrated 100% coverage for all 3 models
- std(pass@1): Non-trivial (h-e1 showed diverse pass@1 distributions across tiers)
- Source: h-e1/04_validation.md — all models produced valid k=5 solutions

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: `coverage_verification` (not standard ML classification/regression)
- Library: `numpy` (for std/mean computation), `json` (for file I/O), `pathlib`
- Code:
  ```python
  import numpy as np
  coverage = len(pass_at_1_dict) / total_problems
  std_pass_at_1 = np.std(list(pass_at_1_dict.values()))
  gate_pass = (coverage >= 0.95) and (std_pass_at_1 > 0)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison:** Coverage rate per model (bar chart) vs 0.95 threshold (red dashed line)

#### Additional Figures (LLM Autonomous)

Suggested additional figures for h-m1:
1. **Pass@1 Distribution Histograms (3 subplots):** 6-point histogram {0.0, 0.2, 0.4, 0.6, 0.8, 1.0} per model for HumanEval+ and MBPP+ — shows non-triviality visually
2. **Problem Coverage Heatmap:** 3 models × 2 benchmarks grid showing coverage rate (% of problems evaluated)
3. **Pass@1 Cumulative Distribution:** CDF per model showing distribution shape (bimodal = distinct hard/easy tiers)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | h-e1 pass@1 files exist at `h-e1/results/pass_at_1_*.json` | Verified: h-e1 completed with coverage=1.0 |
| Mechanism Isolatable | Coverage computation is independent of tier assignment | TRUE: coverage = count(valid) / total, no tier dependency |
| Baseline Measurable | h-e1 pass@1 values load without error | TRUE: JSON files readable; h-e1 validation confirmed |

### Architecture Compatibility Check

**This hypothesis has no model architecture compatibility issue** — h-m1 tests the evaluation pipeline (EvalPlus oracle + pass@1 computation), not a model modification.

**Required Components:**
- `evalplus` Python package (≥0.2.0) — already installed in `youra-h-e1` env
- `h-e1/results/pass_at_1_*.json` — 3 files, one per model (already generated)
- `h-e1/results/correctness_*.json` — fallback if pass@1 files corrupted

**Incompatible Scenarios:**
- If `h-e1/results/` directory missing → regenerate from scratch (3-4h GPU time)
- If EvalPlus package not importable → `pip install evalplus --upgrade`

> ⚠️ If h-e1 results files are missing, Phase 4 MUST detect this early and fallback to solution regeneration!

### Mechanism Activation Indicators

**How to detect if mechanism (coverage verification) is actually working:**

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | `"Loaded pass@1 for {model}: {n} problems"` | `verify_coverage.py:load_pass_at_1()` |
| Data Shape | `len(pass_at_1_dict) == 164` (HumanEval) or `== 378` (MBPP) | `verify_coverage.py:compute_coverage_rate()` |
| Metric Delta | `coverage_rate == 1.0` (expected from h-e1) | `results/coverage_report.json` |

**Activation Verification Code:**
```python
def verify_mechanism_activated(pass_at_1_dicts: dict, results: dict) -> tuple[bool, dict]:
    """Verify coverage verification mechanism is active and producing valid outputs."""
    indicators = {
        "files_loaded": all(len(d) > 0 for d in pass_at_1_dicts.values()),
        "coverage_computed": all(r["coverage"] > 0 for r in results.values()),
        "distribution_computed": all("std" in r for r in results.values()),
        "gate_evaluated": "gate_pass" in results
    }
    return all(indicators.values()), indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| pass@1 files missing | `FileNotFoundError` on load | FALLBACK: rerun evaluate_solutions.py from h-e1 solutions |
| Coverage < 0.95 | `coverage_rate < 0.95` check | DEBUG: inspect which task_ids are missing; check EvalPlus version |
| All pass@1 == 0.0 | `std(pass@1) == 0.0` | FAIL: degenerate; check model generation; try temperature=0.6 |
| All pass@1 == 1.0 | `std(pass@1) == 0.0` | FAIL: degenerate (trivially easy); check problem loading |
| EvalPlus import error | `ImportError` | FIX: `pip install evalplus --upgrade` in conda env |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Files Loaded | len > 0 for all 3 models × 2 benchmarks | JSON load check |
| Coverage Sufficient | ≥ 0.95 per model | `len(pass_at_1) / total_problems` |
| Hypothesis Supported | std(pass@1) > 0 for all 3 models | `np.std(list(pass_at_1.values()))` |

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (file I/O, JSON parsing, numpy computation)
2. `coverage_rate ≥ 0.95` for all 3 models on at least 1 benchmark
3. `std(pass@1) > 0` for all 3 models (non-degenerate distribution)

**Note:** Based on h-e1 results (coverage=1.0, diverse pass@1 distributions), this gate is very likely to PASS with minimal new computation.

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Assessment:** Archon KB did not contain domain-relevant content for EvalPlus / LLM code evaluation. All queries returned image generation / diffusers content with low similarity scores (0.28–0.47). No Archon sources were used in the experiment specification.

### B. GitHub Implementations (Exa)

**Repository 1:** `evalplus/evalplus` — Official EvalPlus Framework
- **URL:** https://github.com/evalplus/evalplus
- **Query Used:** "evalplus check_correctness pass@k solution generation HumanEval MBPP coverage rate GitHub"
- **Relevance:** HIGHEST — this IS the framework being tested in h-m1
- **Key API Used For:**
  - Dataset loading: `from evalplus.data import get_human_eval_plus, get_mbpp_plus`
  - Evaluation: `evalplus.evaluate --dataset [humaneval|mbpp] --samples samples.jsonl`
  - Results: `_eval_results.json` cache file structure
- **Known Issue Documented:** `evaluate()` returns None when cache exists → read JSON directly (applied in h-e1)
- **Used For:** Dataset loading code, evaluation API, results file format

**Repository 2:** `openai/human-eval` — Original HumanEval Reference
- **URL:** https://github.com/openai/human-eval
- **Query Used:** "evalplus check_correctness pass@k solution generation HumanEval MBPP coverage rate GitHub"
- **Relevance:** HIGH — defines pass@k estimation formula (Chen et al. 2021)
- **Key Insight:** Standard evaluation generates n=200 solutions per problem; coverage = all problems evaluated
- **Used For:** pass@k formula understanding; coverage rate definition

**Repository 3:** `bigcode-project/bigcode-evaluation-harness`
- **URL:** https://github.com/bigcode-project/bigcode-evaluation-harness
- **Query Used:** Same as above (appeared in results)
- **Relevance:** MEDIUM — shows HumanEval+/MBPP+ evaluation conventions
- **Key Insight:** Temperature 0.1-0.2 for small-k pass@k; n=200 solutions for unbiased estimation
- **Training config extracted:**
  - HumanEval+: `--temperature 0.2 --n_samples 200` (for k=1,10,100)
  - MBPP+: `--temperature 0.1 --n_samples 15` (for k=1)
  - Our k=5: temperature=0.8 (higher for diversity; already validated in h-e1)
- **Used For:** Training protocol temperature and n_samples conventions

**Repository 4:** `codeeval-pro/codeeval-pro` — HumanEval Pro & MBPP Pro
- **URL:** https://github.com/codeeval-pro/codeeval-pro
- **Relevance:** LOW — extended harder benchmarks; confirms evalplus as standard evaluation backend
- **Used For:** Confirmation that evalplus is the standard evaluation backend for code benchmarks

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from Exa search results and h-e1 validated infrastructure was sufficiently clear. The EvalPlus API and pass@1 computation patterns are well-documented.

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Report — h-e1 (`h-e1/04_validation.md`)

**Reused Components:**
- Dataset: EvalPlus HumanEval+ (164) + MBPP+ (378) — proven stable, cache populated
- Pass@1 files: `h-e1/results/pass_at_1_llama3_8b.json`, `pass_at_1_codellama_7b.json`, `pass_at_1_deepseek_6.7b.json`
- Correctness files: `h-e1/results/correctness_llama3_8b.json`, etc.
- Code: `h-e1/code/src/h_e1/generate_solutions.py` (210 lines), `evaluate_solutions.py` (212 lines), `analyze_tiers.py` (298 lines)
- Conda env: `youra-h-e1` with all EvalPlus + transformers + torch dependencies
- EvalPlus API fix: evaluate() → None → read `_eval_results.json` directly

**Why Reused:** Enables controlled experiment — h-m1 isolates coverage verification from generation, enabling direct comparison. h-e1 already proved coverage=1.0, so h-m1 is primarily a structured re-validation that also produces the canonical `pass_at_1_hm1_verified.json` file needed by h-m2.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (EvalPlus HumanEval+ + MBPP+) | Previous hypothesis | h-e1 validation report + 02b_verification_plan.md §1.3 |
| k=5 solutions per problem | Phase 2A design | 02b_verification_plan.md §2.2 (H-M1 variables) |
| Coverage ≥ 95% threshold | Phase 2B verification protocol | 02b_verification_plan.md §2.2 (H-M1 success criteria) |
| Non-triviality check (std > 0) | Phase 2B success criteria | 02b_verification_plan.md §2.2 (H-M1 secondary) |
| Temperature 0.8 for generation | Previous hypothesis | h-e1/04_validation.md (task-003 validated) |
| EvalPlus API usage | GitHub | evalplus/evalplus official repo (Exa B.1) |
| Pass@k formula | GitHub | openai/human-eval (Exa B.2) |
| MBPP as primary benchmark | Previous hypothesis | h-e1/04_validation.md (key finding #3) |
| Evaluation metrics (coverage, std) | Phase 2B | 02b_verification_plan.md §2.2 (H-M1 DV definition) |
| Core mechanism pseudo-code | Previous hypothesis + Exa | h-e1 code + evalplus/evalplus API (B.1) |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-18

### Workflow History for This Hypothesis
- Phase 2B completed: 2026-03-18T03:10:00
- h-e1 prerequisite completed: 2026-03-18T08:21:00 (MUST_WORK PASS)
- h-m1 set to IN_PROGRESS: 2026-03-18T08:39:17
- Phase 2C IN_PROGRESS started: 2026-03-18

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code — no relevant results), Exa (GitHub — EvalPlus official docs), Serena (skipped — code clear)*
*All specifications grounded in h-e1 validated infrastructure and EvalPlus official documentation*
*Next Phase: Phase 3 - Implementation Planning*
