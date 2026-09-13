# Product Requirements Document (PRD)
# H-M2: Difficulty Tier Stratification — Cross-Model Jaccard Analysis

**Status:** Draft
**Version:** 1.0
**Date:** 2026-03-18
**Hypothesis:** H-M2 (MECHANISM, SHOULD_WORK gate)
**Phase:** 3 - Implementation Planning
**Tier:** FULL (MECHANISM → max 30 tasks)

---

## Frontmatter

```yaml
stepsCompleted:
  - executive_summary
  - problem_statement
  - functional_requirements
  - non_functional_requirements
  - success_criteria
hypothesis_id: h-m2
hypothesis_type: MECHANISM
gate_type: SHOULD_WORK
phase2c_source: h-m2/02c_experiment_brief.md
base_hypothesis: h-m1
```

---

## 1. Executive Summary

H-M2 is the second mechanism verification step in the LLM Calibration pipeline (H-E1 → H-M1 → **H-M2** → H-M3 → H-M4). It validates that **difficulty tier assignments are meaningful** by computing Jaccard similarity between model-specific hard-tier problem sets across 3 LLMs.

**Key characteristic:** H-M2 is a **pure statistical analysis** experiment — no model inference required. It consumes `h-m1/results/pass_at_1_hm1_verified.json` and computes cross-model overlap of problem difficulty tiers.

**Gate Condition (SHOULD_WORK):**
- At least 1 of 3 model pairs has Jaccard(hard_set_A, hard_set_B) > 0.3
- Gate failure does NOT block h-m3 (SHOULD_WORK semantics — pipeline continues regardless)

**Expected outcome:** PASS. Based on h-e1/h-m1 results, hard tier sizes are substantial (68–199 problems per model per benchmark), making Jaccard > 0.3 plausible for structurally similar problems. Runtime: < 30 seconds on CPU.

---

## 2. Problem Statement

### 2.1 Background

H-M3 and H-M4 depend on the assumption that difficulty tier assignments (hard/easy) are not arbitrary model-specific quirks, but reflect genuine problem difficulty structure shared across architectures. H-M2 tests this assumption by measuring cross-model agreement in hard-tier classifications.

If Jaccard similarity > 0.3 for at least one model pair, this supports the interpretation that:
1. Hard problems are structurally difficult (not just model-specific weaknesses)
2. The difficulty stratification captures a real signal for ECE analysis in H-M4

### 2.2 Research Gap

While individual model pass@1 distributions are verified (h-m1), the cross-model consistency of difficulty tiers has not been established. Without this check, tier-stratified calibration analysis (H-M4) could be confounded by idiosyncratic model behavior rather than genuine difficulty structure.

### 2.3 Hypothesis Statement (H-M2)

Under model-specific pass@1 stratification from H-M1, if problems are assigned to hard (pass@1=0.0) and easy (pass@1≥0.6) tiers per model, then tier assignments reflect genuine competence differences (Jaccard similarity of hard-tier problem sets across models > 0.3), because problems that are structurally hard tend to be hard across different architectures.

---

## 3. Functional Requirements

### FR-1: Input Data Loading

**FR-1.1: Load H-M1 Verified Pass@1 Data**
- Primary: Load `h-m1/results/pass_at_1_hm1_verified.json`
- Format (FR-5.1 from H-M1): `{model_id: {task_id: {pass_at_1: float, ...}}}`
- Models:
  - `NousResearch/Meta-Llama-3-8B`
  - `codellama/CodeLlama-7b-hf`
  - `deepseek-ai/deepseek-coder-6.7b-base`
- Expected: 542 problems per model (164 HumanEval+ + 378 MBPP+)

**FR-1.2: Benchmark-level Splitting**
- HumanEval+ task_ids: prefix `HumanEval/` (164 problems)
- MBPP+ task_ids: prefix `Mbpp/` (378 problems)
- Split for per-benchmark tier size reporting and primary/secondary analysis designation

**FR-1.3: Input Validation**
- Verify file exists; raise FileNotFoundError with clear message if missing
- Verify 3 model keys present
- Verify per-model problem count ≥ 500 (sanity check for truncation)

### FR-2: Difficulty Tier Stratification

**FR-2.1: Tier Assignment Per Model**
```python
def compute_difficulty_tiers(pass_at_1_data: dict,
                              hard_threshold: float = 0.0,
                              easy_threshold: float = 0.6) -> dict:
    """
    Returns: {model_id: {"hard": set(task_ids), "easy": set(task_ids)}}
    """
```
- Hard tier: `pass@1 == 0.0` (0/5 correct)
- Easy tier: `pass@1 >= 0.6` (≥3/5 correct)
- Medium tier: `pass@1 ∈ {0.2, 0.4}` — excluded from analysis

**FR-2.2: Per-Benchmark Tier Sizes**
- Compute n_hard, n_easy separately for HumanEval+ and MBPP+ per model
- Verify n_hard ≥ 20 and n_easy ≥ 20 per model (minimum for reliable analysis)
- Special case: CodeLlama HumanEval n_easy=0 → use MBPP+ as primary benchmark (consistent with h-e1)

**FR-2.3: Tier Assignment on Combined Set**
- Compute tier assignments on full 542-problem combined set (HE+ + MBPP+ combined)
- Used for Jaccard computation (primary analysis uses combined set)

### FR-3: Cross-Model Jaccard Similarity

**FR-3.1: Pairwise Jaccard Computation**
```python
def jaccard_similarity(set_a: set, set_b: set) -> float:
    """Jaccard: |A ∩ B| / |A ∪ B|"""
    union = set_a | set_b
    return len(set_a & set_b) / len(union) if union else 0.0

def compute_cross_model_jaccard(tiers: dict) -> dict:
    """
    Compute Jaccard for all model pairs on hard tier.
    Returns: {(model_a, model_b): float}  # 3 pairs
    """
```
- Compute for all 3 pairs: (Llama3, CodeLlama), (Llama3, DeepSeek), (CodeLlama, DeepSeek)
- Compute on combined set (542 problems)
- Also compute per-benchmark (HE+ separately, MBPP+ separately)

**FR-3.2: Pairwise Overlap Matrix**
- For each pair: n_intersection, n_union, jaccard_score
- Report full 3×3 symmetric matrix (diagonal = 1.0)

**FR-3.3: Consensus Hard Set**
- `consensus_hard = hard_llama3 ∩ hard_codellama ∩ hard_deepseek`
- Report n_consensus and percentage of total problems
- Compute for combined set and per-benchmark

### FR-4: Gate Evaluation

**FR-4.1: SHOULD_WORK Gate Check**
```python
def evaluate_gate(jaccard_results: dict) -> tuple[bool, dict]:
    gate_pass = any(j > 0.3 for j in jaccard_results.values())
    return gate_pass, {
        "gate_type": "SHOULD_WORK",
        "threshold": 0.3,
        "results": {str(pair): score for pair, score in jaccard_results.items()},
        "passing_pairs": [str(p) for p, j in jaccard_results.items() if j > 0.3],
        "gate_satisfied": gate_pass
    }
```

**FR-4.2: Mechanism Activation Verification**
```python
def verify_mechanism_activated(tiers: dict, jaccard_results: dict) -> tuple[bool, dict]:
    indicators = {
        "tiers_populated": all(
            len(tiers[m]["hard"]) > 0 and len(tiers[m]["easy"]) > 0
            for m in tiers
        ),
        "jaccard_computed": len(jaccard_results) == 3,
        "jaccard_non_trivial": len(set(jaccard_results.values())) > 1,
        "tier_sizes_valid": all(
            len(tiers[m]["hard"]) >= 20 for m in tiers
        )
    }
    return all(indicators.values()), indicators
```

### FR-5: 6-Point Pass@1 Histogram Analysis

**FR-5.1: Histogram Per Model Per Benchmark**
- Bins: {0.0, 0.2, 0.4, 0.6, 0.8, 1.0} (6-point discrete from k=5)
- Report count and percentage per bin
- Report distribution shape (bimodal, skewed, uniform)

**FR-5.2: Distribution Statistics**
- mean, std, min, max per model per benchmark
- Report hard/easy/medium tier percentage breakdown

### FR-6: Output Files

**FR-6.1: Stratification Results JSON**
- Output: `h-m2/results/stratification_results.json`
- Format:
```json
{
  "metadata": {"source": "h-m1", "timestamp": "..."},
  "tier_sizes": {
    "NousResearch/Meta-Llama-3-8B": {
      "combined": {"hard": 228, "easy": 167, "medium": 147},
      "humaneval": {"hard": 78, "easy": 39, "medium": 47},
      "mbpp": {"hard": 150, "easy": 128, "medium": 100}
    },
    ...
  },
  "jaccard_results": {
    "(llama3, codellama)": 0.42,
    "(llama3, deepseek)": 0.38,
    "(codellama, deepseek)": 0.31
  },
  "consensus_hard": {"n": 45, "percentage": 0.083},
  "gate": {"satisfied": true, "passing_pairs": [...]}
}
```

**FR-6.2: Tier Assignment CSV**
- Output: `h-m2/results/tier_assignments.csv`
- Columns: task_id, benchmark, llama3_tier, codellama_tier, deepseek_tier, n_models_hard, n_models_easy

### FR-7: Visualization

**FR-7.1: Jaccard Bar Chart (MANDATORY — Gate Metrics)**
- Bar chart: 3 model pairs × Jaccard score
- Dashed red line at 0.3 threshold
- Save: `h-m2/figures/jaccard_similarity_bars.png`

**FR-7.2: 6-Point Pass@1 Histograms**
- 3 models × 2 benchmarks = 6 subplots
- 6-point bins {0.0, 0.2, 0.4, 0.6, 0.8, 1.0}
- Color-coded by tier (hard=red, medium=gray, easy=green)
- Save: `h-m2/figures/pass_at_1_histograms.png`

**FR-7.3: Tier Size Summary (Stacked Bar)**
- Per model per benchmark: stacked hard/medium/easy counts
- Save: `h-m2/figures/tier_size_summary.png`

**FR-7.4: Pairwise Overlap Heatmap**
- 3×3 Jaccard similarity matrix (hard tier)
- Color: 0.0 (white) → 1.0 (dark blue)
- Save: `h-m2/figures/jaccard_heatmap.png`

**FR-7.5: Consensus Hard Problems Pie**
- Hard for 1/3 models, 2/3 models, 3/3 models — pie chart
- Save: `h-m2/figures/consensus_hard_pie.png`

---

## 4. Non-Functional Requirements

### NFR-1: Reproducibility
- Deterministic (no random sampling) — pure set operations
- All results saved as JSON/CSV for reproducibility audit
- requirements.txt with pinned versions (extend h-m1 requirements)

### NFR-2: Infrastructure (FULL Tier — MECHANISM PoC)
- Configuration: argparse + hardcoded constants (extend h-m1 patterns)
- Logging: print statements with structured JSON output
- Testing: unit tests for core functions (jaccard_similarity, compute_difficulty_tiers, evaluate_gate)

### NFR-3: Compute
- **CPU only** — no GPU required (pure Python + numpy)
- Expected runtime: < 30 seconds
- Memory: < 100 MB (JSON dict ~542 × 3 entries)

### NFR-4: Code Structure — Extend from H-M1
- New modules in `h-m2/code/src/h_m2/`:
  - `stratify.py`: `compute_difficulty_tiers()`, `split_by_benchmark()`
  - `jaccard.py`: `jaccard_similarity()`, `compute_cross_model_jaccard()`, `compute_consensus_set()`
  - `analyze.py`: `compute_histograms()`, `compute_distribution_stats()`
  - `evaluate.py`: `evaluate_gate()`, `verify_mechanism_activated()`
  - `visualize_hm2.py`: 5 figure generators
  - `run_hm2_stratification.py`: orchestrator entry point
- Reused from h-m1: JSON loading pattern, file path conventions, result output structure

### NFR-5: H-M3 Interface Contract
- `stratification_results.json` MUST exist before h-m3 starts
- Tier assignments available for h-m3 P(True) analysis
- Primary benchmark: MBPP+ (consistent with h-e1/h-m1 findings about CodeLlama)

---

## 5. Technical Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| Python | ≥3.9 | Runtime |
| numpy | ≥1.24 | Histograms, distribution stats |
| matplotlib | ≥3.7 | 5 visualization figures |
| pandas | ≥2.0 | tier_assignments.csv output |
| json | stdlib | File I/O for pass@1 data |
| pathlib | stdlib | Path handling |
| itertools | stdlib | Model pair combinations |

**Environment:** Reuse `youra-h-e1` or `youra-h-m1` conda environment (all deps already installed)
**No GPU required** — pure analysis on h-m1 output

---

## 6. Data Specifications

### 6.1 Input Data (from H-M1)

| File | Location | Format | Content |
|------|----------|--------|---------|
| `pass_at_1_hm1_verified.json` | `h-m1/results/` | JSON `{model_id: {task_id: {pass_at_1: float, ...}}}` | Verified pass@1 for 3 models × 542 problems |

### 6.2 Output Data

| File | Location | Format | Content |
|------|----------|--------|---------|
| `stratification_results.json` | `h-m2/results/` | JSON | Tier sizes, Jaccard scores, gate result |
| `tier_assignments.csv` | `h-m2/results/` | CSV | Per-problem tier per model |
| `jaccard_similarity_bars.png` | `h-m2/figures/` | PNG | Gate metric bar chart |
| `pass_at_1_histograms.png` | `h-m2/figures/` | PNG | 6-point histograms (6 subplots) |
| `tier_size_summary.png` | `h-m2/figures/` | PNG | Stacked bar chart |
| `jaccard_heatmap.png` | `h-m2/figures/` | PNG | 3×3 Jaccard matrix |
| `consensus_hard_pie.png` | `h-m2/figures/` | PNG | Consensus overlap pie |

### 6.3 Total Problems

| Benchmark | Problems | Task ID Prefix |
|-----------|----------|----------------|
| HumanEval+ | 164 | `HumanEval/` |
| MBPP+ | 378 | `Mbpp/` |
| **Total** | **542** | — |

### 6.4 Tier Thresholds

| Tier | Criterion | Pass@1 Values |
|------|-----------|---------------|
| Hard | pass@1 == 0.0 | 0/5 correct |
| Medium | 0.0 < pass@1 < 0.6 | 1/5 or 2/5 correct |
| Easy | pass@1 ≥ 0.6 | ≥3/5 correct |

---

## 7. Success Criteria

### 7.1 Gate Condition (SHOULD_WORK)

| Criterion | Threshold | Required For |
|-----------|-----------|--------------|
| Jaccard(hard_A, hard_B) | > 0.3 | Gate PASS |
| Model pairs passing | ≥ 1 of 3 | Gate PASS |
| Tier sizes | n_hard ≥ 20 per model | Mechanism valid |

**PASS:** ≥1 pair Jaccard > 0.3 → tier assignments reflect genuine competence differences → h-m3 proceeds with original difficulty-conditioned framing
**FAIL (SHOULD_WORK):** All pairs Jaccard ≤ 0.3 → reframe contribution as "competence-boundary calibration" → h-m3 still proceeds with model-specific framing; NOT blocked

### 7.2 Execution Success Criteria

| Check | Condition |
|-------|-----------|
| Input loaded | 3 models × 542 problems loaded successfully |
| Tiers computed | n_hard ≥ 20, n_easy ≥ 20 per model (MBPP+ primary) |
| Jaccard computed | 3 pair scores computed, all ∈ [0, 1] |
| Gate evaluated | Binary PASS/FAIL with pair-level breakdown |
| Figures generated | 5 required figures saved |
| Results written | stratification_results.json + tier_assignments.csv |

### 7.3 Expected Performance

| Metric | Expected | Source |
|--------|----------|--------|
| Max Jaccard | 0.3–0.5 (at least 1 pair) | Hard tier overlap ~30% prevalence |
| n_hard (combined, per model) | 228 / 341 / 173 | h-e1 gate details (HE+MBPP) |
| n_easy (combined, per model) | 167 / 37 / 200 | h-e1 gate details (HE+MBPP) |
| Runtime | < 30 seconds | Pure Python + numpy, no GPU |

---

## 8. Out of Scope

- P(True) logprob elicitation — this is H-M3
- ECE computation — this is H-M4
- Model inference or solution generation
- Re-running EvalPlus evaluation
- New model training or fine-tuning
- Jaccard analysis for easy tier (hard tier is primary for gate)

---

## 9. Risks and Mitigations

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| R1: H-M1 pass@1 file missing | Very Low | Raise FileNotFoundError with clear message; check h-m1 completion |
| R2: All Jaccard ≤ 0.3 (gate fail) | Low | SHOULD_WORK gate — pipeline continues; reframe contribution |
| R3: Degenerate hard tier (n<20) | Very Low | h-e1 confirmed n_hard ≥ 68 per model per benchmark |
| R4: CodeLlama n_easy=0 on HumanEval | Known | Use MBPP+ as primary (consistent with h-e1) |
| R5: Identical Jaccard for all pairs | Very Low | Log warning; check data loading; all-same value indicates error |

---

## 10. Dependencies and Integration

### 10.1 Upstream (inputs from h-m1)

| Component | Used By | Location |
|-----------|---------|----------|
| `pass_at_1_hm1_verified.json` | FR-1.1 | `h-m1/results/` |
| `youra-h-e1` conda env | run_hm2_stratification.py | `conda activate youra-h-e1` |

### 10.2 Downstream (outputs consumed by h-m3)

| Output | Consumer | Location |
|--------|----------|----------|
| `stratification_results.json` | h-m3 tier context | `h-m2/results/` |
| `tier_assignments.csv` | h-m3 per-problem tier lookup | `h-m2/results/` |
| Gate result (SHOULD_WORK) | h-m3 framing decision | `verification_state.yaml` |

---

*Generated by Phase 3 PRD Generation (inline from Phase 2C experiment brief)*
*Source: h-m2/02c_experiment_brief.md, h-m1/03_prd.md (base reference)*
*BMAD PRD workflow: executed inline (bmm not installed in project)*
*Date: 2026-03-18*
