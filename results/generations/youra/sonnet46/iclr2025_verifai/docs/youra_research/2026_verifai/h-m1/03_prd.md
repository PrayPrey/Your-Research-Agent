# Product Requirements Document (PRD)
# H-M1: Pass@1 Coverage Verification — Infrastructure Re-Validation

**Status:** Draft
**Version:** 1.0
**Date:** 2026-03-18
**Hypothesis:** H-M1 (MECHANISM, MUST_WORK gate)
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
hypothesis_id: h-m1
hypothesis_type: MECHANISM
gate_type: MUST_WORK
phase2c_source: h-m1/02c_experiment_brief.md
base_hypothesis: h-e1
```

---

## 1. Executive Summary

H-M1 is the first mechanism verification step in the LLM Calibration pipeline (H-M1 → H-M2 → H-M3 → H-M4). It validates the **pass@1 computation pipeline infrastructure** by confirming that h-e1's validated results are correctly reusable: coverage ≥ 95% of the 542 problems, and the pass@1 distribution is non-trivial (std > 0 per model).

**Key distinction from h-e1:** H-M1 does NOT regenerate solutions or re-run EvalPlus evaluation. It loads already-computed `h-e1/results/pass_at_1_*.json` files, computes verification statistics, and exports a canonical `pass_at_1_hm1_verified.json` consumed by h-m2.

**Gate Condition (MUST_WORK):**
1. **Coverage ≥ 95%**: `len(pass_at_1) / total_problems ≥ 0.95` for all 3 models
2. **Non-trivial distribution**: `std(pass@1) > 0` for all 3 models

**Expected outcome:** PASS (h-e1 achieved coverage=1.0 with diverse pass@1 distributions). Runtime: < 5 minutes on CPU.

---

## 2. Problem Statement

### 2.1 Background

H-M2 through H-M4 depend on reliable pass@1 values for all 3 models across all 542 problems. Before proceeding to tier assignment (H-M2), the pipeline must confirm that:
1. The h-e1 pass@1 files are complete and non-degenerate
2. The EvalPlus evaluation infrastructure produced valid results

H-M1 provides this infrastructure confidence checkpoint. It isolates **coverage verification** as a distinct mechanism from tier-level analysis.

### 2.2 Research Gap

While h-e1 demonstrated coverage=1.0 empirically, the pipeline requires a structured verification that:
- Loads and validates pass@1 files programmatically
- Computes formal coverage rates per model per benchmark
- Confirms distribution non-triviality (no degenerate all-0 or all-1 distributions)
- Exports a canonical verified file as the official h-m2 input

### 2.3 Hypothesis Statement (H-M1)

Under EvalPlus augmented test execution, if k=5 solutions are generated per problem per model using temperature sampling and evaluated via EvalPlus `check_correctness`, then pass@1 values are reliably computed with ≥95% problem coverage, because the Run 3 infrastructure is validated and reusable with minimal modifications.

---

## 3. Functional Requirements

### FR-1: Input File Loading

**FR-1.1: Load H-E1 Pass@1 Results**
- Primary: Load `h-e1/results/pass_at_1_{model_name}.json` for each of 3 models
- Format: `{task_id: float}` where float ∈ {0.0, 0.2, 0.4, 0.6, 0.8, 1.0}
- Files:
  - `h-e1/results/pass_at_1_llama3_8b.json` (164 + 378 = 542 entries expected)
  - `h-e1/results/pass_at_1_codellama_7b.json`
  - `h-e1/results/pass_at_1_deepseek_6.7b.json`

**FR-1.2: Fallback to Correctness Files**
- If `pass_at_1_{model}.json` missing or incomplete:
  - Load `h-e1/results/correctness_{model}.json` (format: `{task_id: [bool × 5]}`)
  - Recompute: `pass_at_1[task_id] = sum(results) / len(results)`
- Files: `correctness_llama3_8b.json`, `correctness_codellama_7b.json`, `correctness_deepseek_6.7b.json`

**FR-1.3: Benchmark-level Splitting**
- HumanEval+ task_ids: prefix `HumanEval/` (164 problems)
- MBPP+ task_ids: prefix `Mbpp/` (378 problems)
- Split loaded dict by prefix to enable per-benchmark coverage computation

### FR-2: Coverage Rate Computation

**FR-2.1: Per-Model Coverage Rate**
- `coverage_he[model] = len(he_pass_at_1) / 164`
- `coverage_mbpp[model] = len(mbpp_pass_at_1) / 378`
- `coverage_combined[model] = (len(he_pass_at_1) + len(mbpp_pass_at_1)) / 542`

**FR-2.2: Coverage Gate Check**
- Gate: `coverage_combined[model] >= 0.95` for ALL 3 models
- Partial: `coverage_combined[model] >= 0.95` for ≥2/3 → WARN + investigate 3rd model

### FR-3: Distribution Non-Triviality Check

**FR-3.1: Per-Model Distribution Statistics**
- For each model × benchmark:
  - `mean = np.mean(values)`
  - `std = np.std(values)`
  - `min_val = np.min(values)`, `max_val = np.max(values)`
  - `histogram_6pt = {v: count for v in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]}`

**FR-3.2: Non-Triviality Gate Check**
- Gate: `std > 0` for all 3 models (non-degenerate distribution)
- Secondary: ≥3 non-zero buckets in 6-point histogram

### FR-4: Gate Evaluation

**FR-4.1: MUST_WORK Gate**
```python
def verify_gate(coverage_combined: float, std: float) -> tuple[bool, list]:
    gate_pass = (coverage_combined >= 0.95) and (std > 0)
    checks = [
        f"coverage={coverage_combined:.4f} >= 0.95: {'PASS' if coverage_combined >= 0.95 else 'FAIL'}",
        f"non_trivial (std={std:.4f} > 0): {'PASS' if std > 0 else 'FAIL'}"
    ]
    return gate_pass, checks
```

**FR-4.2: Mechanism Activation Verification**
```python
def verify_mechanism_activated(pass_at_1_dicts: dict, results: dict) -> tuple[bool, dict]:
    indicators = {
        "files_loaded": all(len(d) > 0 for d in pass_at_1_dicts.values()),
        "coverage_computed": all(r["coverage"] > 0 for r in results.values()),
        "distribution_computed": all("std" in r for r in results.values()),
        "gate_evaluated": "gate_pass" in results
    }
    return all(indicators.values()), indicators
```

### FR-5: Canonical Output File Export

**FR-5.1: Write Verified Pass@1 File for H-M2**
- Output: `h-m1/results/pass_at_1_hm1_verified.json`
- Format:
```json
{
  "metadata": {
    "source": "h-e1",
    "verification_status": "PASS",
    "coverage_combined": {"llama3": 1.0, "codellama": 1.0, "deepseek": 1.0},
    "timestamp": "2026-03-18T..."
  },
  "models": {
    "NousResearch/Meta-Llama-3-8B": {"HumanEval/0": 0.4, ...},
    "codellama/CodeLlama-7b-hf": {...},
    "deepseek-ai/deepseek-coder-6.7b-base": {...}
  }
}
```

**FR-5.2: Coverage Report**
- Output: `h-m1/results/coverage_report.json`
- Format: per-model per-benchmark coverage rates + distribution stats + gate results

### FR-6: Visualization

**FR-6.1: Coverage Rate Bar Chart (MANDATORY)**
- Bar chart: coverage per model (HumanEval+, MBPP+, Combined) vs 0.95 threshold (red dashed line)
- Save: `h-m1/figures/coverage_rates.png`

**FR-6.2: Pass@1 Distribution Histograms (3 subplots)**
- 6-point histogram {0.0, 0.2, 0.4, 0.6, 0.8, 1.0} per model for HumanEval+ and MBPP+
- Dual benchmark per subplot (side-by-side bars)
- Save: `h-m1/figures/pass_at_1_histograms.png`

**FR-6.3: Problem Coverage Heatmap**
- 3 models × 2 benchmarks grid — coverage fraction (color-coded)
- Save: `h-m1/figures/coverage_heatmap.png`

**FR-6.4: Pass@1 CDF (3 models)**
- Cumulative distribution per model showing bimodal hard/easy tier structure
- Save: `h-m1/figures/pass_at_1_cdf.png`

### FR-7: Fallback: Re-run EvalPlus Evaluation

**FR-7.1: Detect Missing Files**
- If both `pass_at_1_*.json` AND `correctness_*.json` missing for any model:
  - Log: "FALLBACK: h-e1 result files missing for {model} — regeneration required"
  - Load existing solutions from `h-e1/results/solutions_{model}.jsonl`
  - Re-run `evaluate_solutions.py` (no generation needed, use existing solutions)

**FR-7.2: Scope Boundary**
- H-M1 does NOT regenerate solutions (k=5 generation from scratch)
- Only recomputes evaluation if solution files exist but evaluation files are missing
- Full regeneration (3-4h GPU) requires explicit `--force_regenerate` flag

---

## 4. Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed seed: 42 (consistent with h-e1)
- All intermediate results saved (coverage_report.json, pass_at_1_hm1_verified.json)
- requirements.txt with pinned versions (reuse h-e1 requirements + additions)

### NFR-2: Infrastructure (FULL Tier — MECHANISM PoC)
- Configuration: argparse + hardcoded constants (extend h-e1 patterns)
- Logging: print statements with structured JSON output
- Testing: smoke test mode (`--smoke_test`: process first 10 problems per benchmark)

### NFR-3: Compute
- **Primary path (load+verify):** CPU only, < 5 minutes
- **Fallback path (re-evaluate):** single GPU (set `CUDA_VISIBLE_DEVICES=<empty_gpu>`)
- HuggingFace models: float16, device_map="auto" (only if fallback needed)

### NFR-4: Code Structure — Reuse from H-E1
- New module: `verify_coverage.py` (primary new code for h-m1)
- Extended: `analyze_tiers.py` → add distribution stats functions
- Reused unchanged: `generate_solutions.py`, `evaluate_solutions.py`
- New visualization: `visualize_hm1.py` (h-m1-specific figures)
- Orchestrator: `run_hm1_verification.py` (lightweight entry point)

### NFR-5: H-M2 Interface Contract
- `pass_at_1_hm1_verified.json` MUST be present before h-m2 starts
- Schema documented in FR-5.1
- H-M2 reads from `h-m1/results/pass_at_1_hm1_verified.json`

---

## 5. Technical Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| Python | ≥3.9 | Runtime |
| numpy | ≥1.24 | Statistics computation (mean, std, histogram) |
| matplotlib | ≥3.7 | 4 visualization figures |
| pandas | ≥2.0 | Coverage report table (CSV format) |
| json | stdlib | File I/O for pass@1 and correctness files |
| pathlib | stdlib | Path handling and file existence checks |
| PyTorch | ≥2.0 | Only if fallback evaluation needed |
| transformers | ≥4.35 | Only if fallback evaluation needed |
| evalplus | ≥0.3.0 | Only if fallback evaluation needed |

**Environment:** Reuse `youra-h-e1` conda environment (all deps already installed)
**Alternative:** Create `youra-h-m1` from same requirements.txt

---

## 6. Data Specifications

### 6.1 Input Data (Reused from H-E1)

| File | Location | Format | Content |
|------|----------|--------|---------|
| `pass_at_1_llama3_8b.json` | `h-e1/results/` | JSON `{task_id: float}` | pass@1 per problem (Llama3-8B) |
| `pass_at_1_codellama_7b.json` | `h-e1/results/` | JSON `{task_id: float}` | pass@1 per problem (CodeLlama-7B) |
| `pass_at_1_deepseek_6.7b.json` | `h-e1/results/` | JSON `{task_id: float}` | pass@1 per problem (DeepSeek-6.7B) |
| `correctness_llama3_8b.json` | `h-e1/results/` | JSON `{task_id: [bool×5]}` | Fallback: raw correctness data |
| `correctness_codellama_7b.json` | `h-e1/results/` | JSON `{task_id: [bool×5]}` | Fallback: raw correctness data |
| `correctness_deepseek_6.7b.json` | `h-e1/results/` | JSON `{task_id: [bool×5]}` | Fallback: raw correctness data |

### 6.2 Output Data

| File | Location | Format | Content |
|------|----------|--------|---------|
| `pass_at_1_hm1_verified.json` | `h-m1/results/` | JSON (nested) | Canonical verified pass@1 for h-m2 |
| `coverage_report.json` | `h-m1/results/` | JSON | Per-model coverage + stats + gate |
| `coverage_report.csv` | `h-m1/results/` | CSV | Tabular coverage summary |
| `coverage_rates.png` | `h-m1/figures/` | PNG | Bar chart vs 0.95 threshold |
| `pass_at_1_histograms.png` | `h-m1/figures/` | PNG | 6-point histogram per model |
| `coverage_heatmap.png` | `h-m1/figures/` | PNG | 3×2 coverage grid |
| `pass_at_1_cdf.png` | `h-m1/figures/` | PNG | CDF per model |

### 6.3 Total Problems

| Benchmark | Problems | Task ID Prefix |
|-----------|----------|----------------|
| HumanEval+ | 164 | `HumanEval/` |
| MBPP+ | 378 | `Mbpp/` |
| **Total** | **542** | — |

---

## 7. Success Criteria

### 7.1 Gate Condition (MUST_WORK)

| Criterion | Threshold | Required For |
|-----------|-----------|--------------|
| Coverage (combined) per model | ≥ 0.95 (≥515/542) | Gate PASS |
| std(pass@1) per model | > 0 | Gate PASS |
| Models satisfying both | All 3 models | Gate PASS |
| 6-point histogram | ≥3 non-zero buckets | Secondary check |

**PASS:** Both conditions met for all 3 → export `pass_at_1_hm1_verified.json` → H-M2 unblocked
**PARTIAL:** 2/3 models pass → investigate failing model; WARN
**FAIL:** Coverage < 0.95 on any model → debug EvalPlus API; check solution integrity; fallback

### 7.2 Execution Success Criteria

| Check | Condition |
|-------|-----------|
| Input files loaded | pass_at_1 dict len > 0 for all 3 models |
| Coverage computed | Per model, per benchmark (6 coverage values) |
| Distribution computed | mean, std, min, max, histogram per model |
| Gate evaluated | Binary PASS/FAIL with supporting checks |
| Verified output written | `pass_at_1_hm1_verified.json` exists |
| Figures generated | 4 required figures saved |

### 7.3 Expected Performance (based on h-e1)

| Metric | Expected | Source |
|--------|----------|--------|
| Coverage (combined) | 1.0 (all 542 problems) | h-e1/04_validation.md |
| std(pass@1) | Non-trivial (> 0.05) | h-e1 diverse distributions |
| Runtime | < 5 minutes | JSON load + numpy stats (no GPU) |

---

## 8. Out of Scope

- Tier assignment (hard/easy classification) — this is H-M2
- P(True) logprob elicitation — this is H-M3
- ECE computation — this is H-M4
- New model training or fine-tuning
- EvalPlus re-evaluation of solutions (fallback only, not primary)
- Solution regeneration from scratch (only if h-e1 results entirely missing)

---

## 9. Risks and Mitigations

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| R1: H-E1 pass@1 files missing | Very Low | Fallback: recompute from correctness files; then re-evaluate |
| R2: Degenerate distribution (std=0) | Very Low | h-e1 validated non-trivial distributions; recheck model loading |
| R3: Coverage < 0.95 | Very Low | h-e1 coverage=1.0; investigate which task_ids missing |
| R4: Task_id prefix split failure | Low | Add explicit prefix detection logic; validate count sum = 542 |
| R5: JSON parse error | Very Low | Validate JSON structure before processing; log schema errors |

---

## 10. Dependencies and Integration

### 10.1 Upstream (inputs from h-e1)

| Component | Used By | Location |
|-----------|---------|----------|
| pass@1 files | verify_coverage.py FR-1.1 | `h-e1/results/pass_at_1_*.json` |
| correctness files | verify_coverage.py FR-1.2 | `h-e1/results/correctness_*.json` |
| youra-h-e1 conda env | run_hm1_verification.py | `conda activate youra-h-e1` |

### 10.2 Downstream (outputs consumed by h-m2)

| Output | Consumer | Location |
|--------|----------|----------|
| `pass_at_1_hm1_verified.json` | h-m2 tier assignment | `h-m1/results/` |
| `coverage_report.json` | 04_validation.md | `h-m1/results/` |

---

*Generated by Phase 3 PRD Generation (inline from Phase 2C experiment brief)*
*Source: h-m1/02c_experiment_brief.md, h-e1/03_prd.md (base reference)*
*BMAD PRD workflow: executed inline (bmm not installed in project)*
*Date: 2026-03-18*
