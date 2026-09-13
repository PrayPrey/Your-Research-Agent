# Experiment Design: h-m2

**Date:** 2026-03-18
**Author:** Anonymous
**Hypothesis Statement:** Under model-specific pass@1 stratification from H-M1, if problems are assigned to hard (pass@1=0.0) and easy (pass@1>=0.6) tiers per model, then tier assignments reflect genuine competence differences (Jaccard similarity of hard-tier problem sets across models > 0.3), because problems that are structurally hard tend to be hard across different architectures.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** h-m1 (MUST_WORK PASS ✅)
**Gate Status:** SHOULD_WORK (not yet evaluated)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m2
- **Type:** MECHANISM (Step 2 of 4 in H-M chain)
- **Prerequisites:** h-m1 (COMPLETED ✅, MUST_WORK PASS)

### Gate Condition
**SHOULD_WORK:** At least 1 of 3 model pairs has Jaccard similarity of hard-tier problem sets > 0.3.

**If Gate FAILS:** Proceed with model-specific framing only; reframe contribution as "competence-boundary calibration" rather than "difficulty-conditioned calibration". h-m3 still proceeds (gate type allows continuation).

---

## Continuation Context

**Previous Hypothesis:** h-m1 — pass@1 Coverage Verification via EvalPlus (COMPLETED, PASS)

**h-m1 Key Results (continuation context):**
- All 3 models: coverage = 1.0000 (542/542 problems)
- pass_at_1_hm1_verified.json generated (FR-5.1 compliant) at `h-m1/results/pass_at_1_hm1_verified.json`
- Non-trivial distributions: llama3_8b std=0.331, codellama_7b std=0.195, deepseek_6.7b std=0.345
- Infrastructure: `h-m1/code/src/h_m1/` reusable

### Previous Hypothesis Results (if applicable)
**h-m1 Pass@1 Data Available for h-m2:**
| Model | Hard tier (pass@1=0.0) | Easy tier (pass@1≥0.6) |
|-------|------------------------|------------------------|
| NousResearch/Meta-Llama-3-8B | HE:78, MBPP:150 | HE:39, MBPP:128 |
| codellama/CodeLlama-7b-hf | HE:142, MBPP:199 | HE:0, MBPP:37 |
| deepseek-ai/deepseek-coder-6.7b-base | HE:68, MBPP:105 | HE:24, MBPP:176 |

**Note:** CodeLlama has n_easy=0 on HumanEval (degenerate) → use MBPP as primary benchmark per h-e1 findings.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "Jaccard similarity difficulty stratification benchmark"**
- Results: Low relevance (diffusion model repos, general ML content)
- Key insight: No specific past cases for pass@1-based Jaccard tier analysis in Archon KB
- Assessment: Archon KB does not contain domain-specific cases for this hypothesis

**Query 2: "LLM difficulty tier pass@1 stratification implementation"**
- Results: Low relevance (LoRA, diffusion models)
- Key insight: No prior YouRA pipeline cases for this mechanism

**Query 3: "code benchmark difficulty cross-model agreement"**
- Results: Low relevance (vision/generation model repos)
- Assessment: Domain gap between Archon KB content and h-m2 subject matter

**Summary:** Archon KB does not contain relevant past cases for this specific mechanism (cross-model Jaccard analysis of difficulty tiers on code benchmarks). Implementation will rely on first-principles design + Exa GitHub findings.

### Archon Code Examples

**Query: "Jaccard similarity set intersection Python"**
- Results: Unrelated code (distributed tensors, incidence matrices)
- Assessment: No useful code examples in Archon KB for this hypothesis
- **Fallback:** Jaccard implementation is trivially derivable from standard Python set operations; no Archon code basis needed.

### Exa GitHub Implementations

**Source 1: evalplus/evalplus** (⭐ 1698)
- **URL:** https://github.com/evalplus/evalplus
- **Relevance:** Official EvalPlus repo — provides HumanEval+ (164) + MBPP+ (378) benchmark. This is the exact dataset used.
- **Key API:**
  ```python
  from evalplus.data import get_humaneval_plus, get_mbpp_plus
  # Returns dict: task_id -> {prompt, canonical_solution, test, ...}
  problems_he = get_humaneval_plus()  # 164 problems
  problems_mbpp = get_mbpp_plus()     # 378 problems
  ```
- **Dataset Info:** Apache-2.0 license, pip-installable (`pip install evalplus`), data cached at `~/.cache/evalplus/`
- **Used For:** Confirming dataset is standard, pip-loadable

**Source 2: LiveCodeBench/LiveCodeBench** (GitHub, Python)
- **URL:** https://github.com/LiveCodeBench/LiveCodeBench
- **Relevance:** Reference implementation of difficulty-stratified pass@1 computation
- **Key Pattern:**
  ```python
  # compute_scores.py — per-difficulty pass@1
  python -m lcb_runner.evaluation.compute_scores --eval_all_file {file} --start_date {date}
  # Outputs: pass@1 for easy/medium/hard separately
  ```
- **Design Pattern:** Uses `problem.difficulty` field to stratify, then computes pass@1 per stratum separately
- **Used For:** Reference architecture for difficulty-stratified evaluation loop

**Source 3: TowardsDataScience — Jaccard Similarity Python**
- **URL:** https://towardsdatascience.com/jaccard-similarity-and-jaccard-distance-in-python...
- **Relevance:** Standard Jaccard computation pattern
- **Key Code:**
  ```python
  def jaccard_similarity(set1, set2):
      intersection = len(set1.intersection(set2))
      union = len(set1.union(set2))
      return intersection / union if union > 0 else 0.0
  ```
- **Used For:** Core mechanism pseudo-code basis

**Source 4: Easy2Hard-Bench (AAAI)**
- **URL:** https://www.proceedings.com/content/079/079017-1407open.pdf
- **Relevance:** Systematic difficulty stratification for code benchmarks using IRT/Glicko-2
- **Key Insight:** Cross-model difficulty consistency is a research question; their approach uses human statistics (IRT) while h-m2 uses model-specific pass@1 — both valid approaches
- **Used For:** Validates research direction; confirms Jaccard > 0.3 is reasonable threshold

**Serena Analysis Needed:** false — mechanism is straightforward Python set operations

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This is NOT a paper reproduction experiment. h-m2 is an ORIGINAL analysis computing Jaccard similarity between model-specific difficulty tier assignments using pass@1 data from h-m1.

**Recommended Implementation Path:**
- Primary: Original implementation using h-m1 output (`pass_at_1_hm1_verified.json`) + pure Python set operations
- Fallback: scipy.spatial.distance.jaccard for numerical validation
- Justification: No prior paper to reproduce; mechanism is straightforward set intersection/union on problem ID sets

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. Jaccard similarity uses native Python set operations: `len(A & B) / len(A | B)`. No complex architecture patterns requiring Serena analysis.

---

## Experiment Specification

### Dataset

**Name:** EvalPlus (HumanEval+ 164 + MBPP+ 378 = 542 problems total)
**Type:** standard (real benchmark, NOT synthetic)
**Source:** Liu et al. 2023 (NeurIPS); https://github.com/evalplus/evalplus
**Version:** HumanEval+ v0.1.10, MBPP+ v0.2.0

**Input Data (PRIMARY — from h-m1):**
- File: `h-m1/results/pass_at_1_hm1_verified.json`
- Schema (FR-5.1): `{model_id: {task_id: {pass_at_1: float, correct_count: int, total: int}}}`
- Content: pass@1 per (problem, model) for all 542 × 3 = 1,626 pairs

**Secondary Reference:**
- EvalPlus benchmarks: used to map task_ids to benchmark (HumanEval+ vs MBPP+)
- No new EvalPlus API calls needed — data already in h-m1 output

**Problem Coverage:** 164 HumanEval+ + 378 MBPP+ = 542 problems
**Pass@1 Values:** 6-point discrete {0.0, 0.2, 0.4, 0.6, 0.8, 1.0} (from k=5 solutions)

**Tier Definitions:**
- Hard tier: pass@1 = 0.0 (0/5 correct)
- Medium tier: pass@1 ∈ {0.2, 0.4} (excluded from analysis)
- Easy tier: pass@1 ≥ 0.6 (≥3/5 correct)

**Loading Information** (for Phase 4 download):
- Method: JSON file load (no download needed — already generated)
- Identifier: `h-m1/results/pass_at_1_hm1_verified.json`
- Code:
  ```python
  import json
  with open("../h-m1/results/pass_at_1_hm1_verified.json") as f:
      pass_at_1_data = json.load(f)
  # Schema: {model_id: {task_id: {pass_at_1: float, ...}}}
  ```

### Models

#### Baseline Model

**Architecture:** No ML model needed for h-m2 — this is a STATISTICAL ANALYSIS experiment
**Type:** Analysis-only (no model inference)
**Input:** pass_at_1_hm1_verified.json from h-m1
**Models Analyzed (3):**
1. NousResearch/Meta-Llama-3-8B — general-purpose LLM
2. codellama/CodeLlama-7b-hf — code-adapted LLM
3. deepseek-ai/deepseek-coder-6.7b-base — code-specialized LLM

**Loading Information** (for Phase 4 download):
- Method: No model loading required (analysis of h-m1 output only)
- Identifier: `h-m1/results/pass_at_1_hm1_verified.json`
- Code: See Dataset loading above

#### Proposed Model

**Architecture:** Baseline (h-m1 pass@1 data) + Tier Stratification + Jaccard Analysis

**Core Mechanism Implementation:**

```python
# Core Mechanism: Difficulty Tier Stratification + Cross-Model Jaccard Analysis
# Based on: TowardsDataScience Jaccard tutorial + LiveCodeBench difficulty stratification pattern
# Input: pass_at_1_data dict from h-m1/results/pass_at_1_hm1_verified.json

def compute_difficulty_tiers(pass_at_1_data: dict,
                              hard_threshold: float = 0.0,
                              easy_threshold: float = 0.6) -> dict:
    """
    Compute hard/easy tier problem sets per model.
    Returns: {model_id: {"hard": set(task_ids), "easy": set(task_ids)}}
    """
    tiers = {}
    for model_id, problems in pass_at_1_data.items():
        hard_set = set(t for t, v in problems.items() if v["pass_at_1"] == hard_threshold)
        easy_set = set(t for t, v in problems.items() if v["pass_at_1"] >= easy_threshold)
        tiers[model_id] = {"hard": hard_set, "easy": easy_set}
    return tiers

def jaccard_similarity(set_a: set, set_b: set) -> float:
    """Jaccard similarity: |A ∩ B| / |A ∪ B|"""
    union = set_a | set_b
    if len(union) == 0:
        return 0.0
    return len(set_a & set_b) / len(union)

def compute_cross_model_jaccard(tiers: dict) -> dict:
    """
    Compute Jaccard similarity for all model pairs on hard tier.
    Returns: {(model_a, model_b): jaccard_score}
    """
    model_ids = list(tiers.keys())
    results = {}
    for i in range(len(model_ids)):
        for j in range(i + 1, len(model_ids)):
            m_a, m_b = model_ids[i], model_ids[j]
            jaccard = jaccard_similarity(tiers[m_a]["hard"], tiers[m_b]["hard"])
            results[(m_a, m_b)] = jaccard
    return results  # 3 pairs: (llama3, codellama), (llama3, deepseek), (codellama, deepseek)

# Gate check: at least 1 pair with Jaccard > 0.3
gate_pass = any(j > 0.3 for j in cross_model_jaccard.values())
```

### Training Protocol

**No Training Required** — h-m2 is a STATISTICAL ANALYSIS experiment, not a model training experiment.

**Execution Protocol:**

| Step | Action | Tool |
|------|--------|------|
| 1 | Load pass_at_1_hm1_verified.json | json.load() |
| 2 | Compute tier assignments per model | compute_difficulty_tiers() |
| 3 | Compute cross-model Jaccard (3 pairs) | compute_cross_model_jaccard() |
| 4 | Compute 6-point pass@1 histograms | np.histogram() |
| 5 | Report per-benchmark tier sizes (n_hard, n_easy) | dict lookup |
| 6 | Gate check: Jaccard > 0.3 in ≥1 pair | any() |
| 7 | Generate visualizations | matplotlib |

**Computational Parameters:**
- No GPU required (pure Python + numpy)
- No optimizer, no learning rate, no batch size
- Single run (no random seeds needed — deterministic)
- Expected runtime: < 30 seconds

**Benchmark Splits:**
- Primary: MBPP+ (378 problems) — used as primary because CodeLlama has n_easy=0 on HumanEval
- Secondary: HumanEval+ (164 problems) — reported separately; CodeLlama degenerate edge noted
- Combined: 542 problems (both benchmarks together)

### Evaluation

**Primary Metrics:**
1. **Jaccard similarity** (3 model pairs × hard tier):
   - Jaccard(Llama3_hard, CodeLlama_hard)
   - Jaccard(Llama3_hard, DeepSeek_hard)
   - Jaccard(CodeLlama_hard, DeepSeek_hard)
   - Target: at least 1 pair > 0.3

2. **Tier size summary** (per model, per benchmark):
   - n_hard, n_easy per (model, benchmark) — verify n ≥ 20 consistent with h-e1

3. **6-point pass@1 histogram** (per model, per benchmark):
   - Bins: {0.0, 0.2, 0.4, 0.6, 0.8, 1.0}
   - Report shape (bimodal? skewed? uniform?)

**Secondary Metrics:**
4. **Consensus hard set** (problems hard for ALL 3 models):
   - n_consensus = |hard_llama3 ∩ hard_codellama ∩ hard_deepseek|
   - Percentage of total problems

5. **Pairwise overlap matrix** (n_intersection, n_union per pair)

**Success Criteria:**
- **Primary (gate):** At least 1 of 3 model pairs has Jaccard > 0.3 for hard tier
- **Secondary:** Bimodal or skewed (non-uniform) pass@1 distribution in ≥2 models
- **SHOULD_WORK fail action:** Gate fails → continue with model-specific framing (not blocked)

**Expected Values** (from h-e1/h-m1 data):
- Hard tier sizes are substantial (68–199 per model per benchmark)
- Random Jaccard expected: ~(n_hard/N)² × N / (2×n_hard - n_hard²/N) ≈ 0.1–0.2 for 30% tier prevalence
- Threshold 0.3 is conservative (slightly above random expectation)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical analysis (not classification/regression)
- Library: pure Python + numpy (no torchmetrics/sklearn needed)
- Code:
  ```python
  import numpy as np
  # Jaccard: pure Python set operations
  jaccard = len(A & B) / len(A | B)
  # Histogram: numpy
  hist, _ = np.histogram([v["pass_at_1"] for v in model_data.values()],
                          bins=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.01])
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Jaccard similarity per model pair (bar chart, dashed line at 0.3 threshold)

#### Additional Figures (LLM Autonomous)
Based on the mechanism (cross-model difficulty tier overlap analysis), the following are recommended:

1. **Jaccard similarity heatmap** (3×3 model matrix for hard tier)
2. **6-point pass@1 histograms** (3 models × 2 benchmarks = 6 subplots)
3. **Tier size summary** (stacked bar: hard/medium/easy per model per benchmark)
4. **Venn diagram** (2D: Llama3_hard ∩ DeepSeek_hard, as highest expected overlap)
5. **Consensus hard problems** pie chart (problem overlap levels: 1/3, 2/3, 3/3 models)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m2/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. At least 1 of 3 model pairs has Jaccard(hard_set_A, hard_set_B) > 0.3

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | pass_at_1_hm1_verified.json exists and contains data for 3 models × 542 problems | **TRUE** (h-m1 completed, PASS) |
| Mechanism Isolatable | Tier assignment and Jaccard computation are independent, can be tested separately | **TRUE** (pure functions, no side effects) |
| Baseline Measurable | Random Jaccard expectation computable analytically (baseline: tier prevalence²/(2p-p²)) | **TRUE** |

### Architecture Compatibility Check

**Mechanism Type:** Statistical analysis (no neural network architecture involved)

**Required Features:**
- pass_at_1_hm1_verified.json with FR-5.1 schema compliance (verified in h-m1)
- Python set operations (native, no special requirements)
- numpy for histogram computation

**Incompatible Architectures:**
- None — this is a pure data analysis step with no model inference

> ⚠️ If pass_at_1_hm1_verified.json is missing or malformed, Phase 4 MUST fail early with explicit error.

### Mechanism Activation Indicators

**How to detect if mechanism is actually working:**

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | "Tier assignment complete: hard={n}, easy={n}" per model | stratify.py:compute_difficulty_tiers() |
| Data Shape | 3 tier dicts × 2 benchmarks = 6 sets populated | analyze.py:line ~50 |
| Metric Delta | Jaccard values vary per pair (not all identical) | jaccard.py:compute_cross_model_jaccard() |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(tiers: dict, jaccard_results: dict) -> tuple[bool, dict]:
    indicators = {
        "tiers_populated": all(
            len(tiers[m]["hard"]) > 0 and len(tiers[m]["easy"]) > 0
            for m in tiers
        ),
        "jaccard_computed": len(jaccard_results) == 3,  # All 3 pairs
        "jaccard_non_trivial": len(set(jaccard_results.values())) > 1,  # Not all identical
        "tier_sizes_valid": all(
            len(tiers[m]["hard"]) >= 20 and len(tiers[m]["easy"]) >= 20
            for m in tiers
        )
    }
    return all(indicators.values()), indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| Missing pass@1 file | FileNotFoundError on json.load | FAIL: "h-m1 output missing — run h-m1 first" |
| Degenerate tiers (n<20) | len(hard_set) < 20 | WARN: Use MBPP only (consistent with h-e1) |
| All Jaccard = 0 | All pairs have zero intersection | FAIL: "Tier overlap mechanism not working" |
| Jaccard all identical | All 3 pairs have same value | WARN: Potential data loading error |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | All 3 tiers populated, n≥20 | verify_mechanism_activated() |
| Effect Measurable | Jaccard values in [0, 1], varying per pair | jaccard_results values |
| Hypothesis Supported | At least 1 Jaccard > 0.3 | any(j > 0.3 for j in jaccard_results.values()) |

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Overall Assessment:** Archon KB (source: 8b1c7f40739544a6) does not contain relevant cases for this specific mechanism.
- Query 1 ("Jaccard similarity difficulty stratification benchmark"): Low relevance results (OpenReview diffusion, LAION datasets)
- Query 2 ("LLM difficulty tier pass@1 stratification"): Low relevance (HuggingFace papers about text/image models)
- Query 3 ("code benchmark difficulty cross-model agreement"): Low relevance (vision generation repos)
- Code Query ("Jaccard similarity set intersection Python"): No relevant code examples

**Used For:** Confirmed no prior YouRA cases for this mechanism; implementation relies on first-principles design.

### B. GitHub Implementations (Exa)

**Repository 1: evalplus/evalplus** (⭐ 1698)
- **URL:** https://github.com/evalplus/evalplus
- **Query Used:** "EvalPlus HumanEval MBPP difficulty tier stratification Python implementation"
- **Relevance:** Official dataset source; confirmed 164+378=542 problems, Apache-2.0 license
- **Key API:**
  ```python
  from evalplus.data import get_humaneval_plus, get_mbpp_plus
  problems = get_humaneval_plus()  # {task_id: {prompt, test, ...}}
  ```
- **Configuration Extracted:** MBPP+ v0.2.0 (378 tasks), HumanEval+ v0.1.10 (164 tasks)
- **Used For:** Dataset loading confirmation, benchmark ID mapping

**Repository 2: LiveCodeBench/LiveCodeBench** (GitHub)
- **URL:** https://github.com/LiveCodeBench/LiveCodeBench
- **Query Used:** "LiveCodeBench difficulty stratification pass@1 per difficulty level Python"
- **Relevance:** Reference implementation for difficulty-stratified pass@1 evaluation
- **Key Code Pattern:**
  ```python
  # compute_scores.py: group problems by difficulty, compute pass@1 per group
  easy_scores = [score for p, score in results if p.difficulty == "easy"]
  pass_at_1_easy = np.mean(easy_scores)
  ```
- **Used For:** Architectural reference for difficulty stratification loop

**Repository 3: Jaccard Similarity Python (TowardsDataScience)**
- **URL:** https://towardsdatascience.com/jaccard-similarity-and-jaccard-distance-in-python-statistics-f6aa214a9816/
- **Query Used:** "Jaccard similarity set comparison Python benchmark problem difficulty cross-model"
- **Key Code:**
  ```python
  def jaccard_similarity(set1, set2):
      intersection = len(set1.intersection(set2))
      union = len(set1.union(set2))
      return intersection / union  # returns float [0, 1]
  ```
- **Used For:** Direct basis for core mechanism pseudo-code (Section 3 above)

**Paper: Easy2Hard-Bench (AAAI)**
- **URL:** https://www.proceedings.com/content/079/079017-1407open.pdf
- **Query Used:** "pass@1 difficulty stratification Jaccard similarity code benchmark LLM evaluation"
- **Key Insight:** Cross-model difficulty consistency studied using IRT/Glicko-2; confirms research direction. Their benchmark uses external human statistics; h-m2 uses self-contained model pass@1.
- **Used For:** Validates research direction; confirms Jaccard > 0.3 is reasonable threshold for non-trivial overlap

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from search results was sufficiently clear. Jaccard similarity and difficulty tier assignment are trivially implementable with Python set operations. No complex architecture patterns required.

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Report — h-m1
- **File:** `h-m1/04_validation.md`
- **Reused Components:**
  - Data: `h-m1/results/pass_at_1_hm1_verified.json` — primary input for h-m2
  - Infrastructure: PYTHONPATH chain from h-e1/h-m1 source directories
  - Benchmark setup: MBPP as primary (CodeLlama degenerate on HumanEval easy tier)
- **Why Reused:** h-m2 analyzes h-m1 output directly; no new model inference needed

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (EvalPlus) | Exa GitHub | Repository B.1 (evalplus/evalplus) |
| Dataset loading code | Exa GitHub | Repository B.1 |
| Jaccard core mechanism | Exa Web | Source B.3 (TowardsDataScience) |
| Tier stratification pattern | Exa GitHub | Repository B.2 (LiveCodeBench) |
| Research direction validation | Exa Web | Paper B.4 (Easy2Hard-Bench) |
| pass@1 input data | Previous hypothesis | h-m1 04_validation.md (D.1) |
| Hard/easy thresholds | Phase 2B | 02b_verification_plan.md §2.2 H-M2 |
| Gate threshold (Jaccard > 0.3) | Phase 2B | 02b_verification_plan.md §2.2 H-M2 success criteria |
| Tier sizes (n_hard, n_easy) | Previous hypothesis | h-e1 04_validation.md gate details |
| Primary benchmark (MBPP) | Previous hypothesis | h-m1 key findings: CodeLlama n_easy=0 HE |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-18

### Workflow History for This Hypothesis
- h-m2 set to IN_PROGRESS (2026-03-18T09:22:12)
- Phase 2C Step 1: context loaded, output file initialized
- Phase 2C Step 2: Archon KB searches executed (3 KB + 1 code query)
- Phase 2C Step 3: Exa GitHub searches executed (4 queries)
- Phase 2C Step 4: Serena analysis skipped (simple mechanism)
- Phase 2C Step 5: Dataset/baseline confirmed (reusing h-m1 output)
- Phase 2C Step 6: Experiment specification synthesized
- Phase 2C Step 7: References documented with traceability matrix
- Phase 2C Step 8: Quality validation in progress

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub + Web), Serena (skipped — simple mechanism)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
