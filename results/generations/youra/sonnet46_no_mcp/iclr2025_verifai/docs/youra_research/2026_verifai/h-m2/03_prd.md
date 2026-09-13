# Product Requirements Document: h-m2

**Project:** Conditional Mechanistic Complementarity of Formal Repair Strategies for LLM-Generated Python Code
**Hypothesis:** h-m2 (MECHANISM / INCREMENTAL — prerequisites: h-e1, h-m1)
**Date:** 2026-05-10
**Author:** Anonymous
**Phase:** 3 — Implementation Planning
**Status:** Phase 2C Complete → Phase 3 PRD Generation

---

## 1. Executive Summary

This PRD defines implementation requirements for **h-m2**: a MECHANISM hypothesis that verifies mypy/ast iterative feedback repair operates via a distinct structural/type failure channel orthogonal to SynCode's syntactic channel. The experiment measures complementarity (C_score) between repair transition sets F_mypy→✓ and F_SynCode→✓, and measures whether mypy repair expands Z3 encoding eligibility (ΔP).

**Hypothesis Statement:** Under evaluation of CodeLlama-7B-generated Python code using mypy/ast iterative feedback (max 3 rounds) on HumanEval baseline pool within eligibility-conditioned, failure-type-stratified subsets, if mypy-feedback is applied post-generation, then (a) F_mypy→✓ exhibits Jaccard overlap below independence expectation with F_SynCode→✓ (C_score > 0, p < 0.05) within the type/structural failure stratum, AND (b) Z3 encoding success rate on post-mypy code is higher than on baseline code (ΔP > 0.05), because mypy/ast operates on a structural/type conformance signal channel orthogonal to SynCode's generation prior.

**Gate:** SHOULD_WORK — failure (null C_score) is publishable; proceed to h-m3 regardless.

**Success Criteria:**
1. **Primary:** C_score(SynCode, mypy) > 0, bootstrap p < 0.0167 (Bonferroni α=0.05/3) within eligibility-conditioned type/structural failure stratum
2. **Secondary:** ΔP(Z3_eligible | post-mypy vs. baseline) > 0.05, 95% CI lower bound > 0

**Incremental Context:** Builds on h-m1 (PARTIAL: delta_ast=0.075, F_SynCode→✓ extracted at N=20). Expands to full HumanEval N=164 for statistical power. Reuses CodeLlama-7B cached weights, evalplus baseline pool protocol, fixed seed scheme.

---

## 2. Problem Statement

H-M1 established that SynCode operates via a syntactic channel (delta_ast=0.075, directional PASS at N=20; bootstrap CI underpowered). H-M2 must verify:

1. mypy/ast iterative feedback addresses a **different** failure channel (type/structural) than SynCode (syntactic)
2. The repair transition sets are **complementary** — F_mypy→✓ and F_SynCode→✓ have lower Jaccard overlap than expected under independence
3. mypy repair **expands Z3 eligibility** — post-mypy code has higher SMT encoding success rate due to type consistency

This is an **inference-only statistical experiment** — no model training, no novel architecture. The goal is mechanistic verification of the orthogonality of mypy's signal channel relative to SynCode's.

Key challenge: h-m1 used N=20 (underpowered). This experiment uses full N=164 HumanEval problems, regenerating the baseline pool and recomputing F_SynCode→✓ at full scale for valid statistical comparison.

---

## 3. Functional Requirements

### FR-1: Full-Scale Baseline Pool (164 Problems)

**Description:** Generate or extend the baseline (unconstrained CodeLlama-7B) frozen pool from h-m1's 20-problem subset to the full 164 HumanEval problems.

**Acceptance Criteria:**
- Baseline pool covers all 164 HumanEval+ problems (from evalplus)
- N=20 samples per problem with fixed seeds: `seed = problem_idx * 100 + sample_idx`
- First 20 problems attempt to reuse h-e1 baseline pool at `h-e1/data/baseline_pool.jsonl`; remaining 144 generated fresh with identical parameters
- Generation parameters: temperature=0.8, max_new_tokens=512, do_sample=True, top_p=0.95
- Pool serialized to `h-m2/data/baseline_pool.jsonl` (format: `{task_id, problem_idx, sample_idx, seed, completion, ast_valid}`)
- Total: 164 × 20 = 3,280 samples

**Dependencies:** `pip install evalplus>=0.3.0 transformers>=4.35.0 torch accelerate`

---

### FR-2: Failure Mode Distribution (FMD) Classification

**Description:** Classify every baseline pool sample into one of four FMD strata: syntax, type/structural, constraint/logical, functional-only (passes ast+mypy but fails EvalPlus test).

**Acceptance Criteria:**
- For each baseline sample, apply in parallel (order-independent):
  1. `ast.parse(code)` → syntax_valid (bool)
  2. `mypy.api.run(['--ignore-missing-imports', '--no-error-summary', '-c', code])` → mypy_exit_code, mypy_error_count
  3. Z3 encoding attempt (heuristic: integer arithmetic density + explicit return type annotation check) → z3_eligible (bool)
  4. EvalPlus functional evaluation → pass_at_1 (bool, per problem)
- FMD stratum assignment per sample:
  - `syntax`: not ast_valid
  - `type_structural`: ast_valid AND mypy_exit_code ≠ 0
  - `constraint_logical`: ast_valid AND mypy_exit_code == 0 AND z3_eligible AND not pass_at_1
  - `functional_only`: ast_valid AND mypy_exit_code == 0 AND not z3_eligible AND not pass_at_1
  - `pass`: pass_at_1
- FMD results serialized to `h-m2/data/fmd_classification.jsonl`
- type/structural stratum must contain ≥10 eligible problems (pre-condition check)
- Cross-validation: sequential FMD on 10 random samples must agree with parallel FMD (validate order-independence assumption A5 from 02b)

**Dependencies:** `pip install mypy z3-solver evalplus`

---

### FR-3: mypy/ast Iterative Feedback Repair

**Description:** Apply mypy/ast iterative feedback repair loop (max 3 rounds) to all 164 baseline pool problems using CodeLlama-7B for re-generation.

**Acceptance Criteria:**
- For each problem, apply repair to each baseline sample:
  - Round loop: ast.parse → mypy.api.run → if errors exist: build structured feedback prompt → regenerate with T=0.2
  - Structured feedback format: list of `(line_num, error_type, message)` tuples
  - Stop early if ast_valid AND mypy_exit_code == 0
  - Max 3 rounds per sample
- mypy flags: `--ignore-missing-imports --no-error-summary`
- Repair generation: temperature=0.2, max_new_tokens=512, same model (CodeLlama-7B)
- Repair log per sample: `{task_id, problem_idx, sample_idx, rounds_used, final_code, success, feedback_history}`
- Results serialized to `h-m2/data/mypy_repair_pool.jsonl`
- Mechanism verification log: print `"mypy_feedback_applied: round={r}, errors_before={n}, errors_after={m}"` per round
- mechanism_activated rate (fraction of samples where rounds_used > 0) must be > 0.10

**Dependencies:** `pip install mypy transformers`

---

### FR-4: F_SynCode→✓ Recomputation at Full N=164

**Description:** Recompute F_SynCode→✓ (SynCode failure-to-success transition set) on the full 164-problem HumanEval pool. H-M1 extracted this from N=20 (2 transitions); h-m2 requires full-scale extraction for valid C_score comparison.

**Acceptance Criteria:**
- Generate SynCode pool for remaining 144 problems (problems 20–163) not covered by h-m1
- OR: Reuse h-m1 SynCode pool and extend to all 164 problems
- F_SynCode→✓ defined as: problem IDs where at least one sample transitions from baseline pass@1=0 to syncode pass@1>0
- F_SynCode→✓ serialized to `h-m2/data/f_syncode_transitions.json`
- Total SynCode pool serialized to `h-m2/data/syncode_pool.jsonl`

**Dependencies:** `pip install syncode` (fallback: git install from uiuc-focal-lab/syncode)

---

### FR-5: F_mypy→✓ Transition Set Extraction

**Description:** Extract F_mypy→✓ = set of problem IDs where any sample transitions from baseline fail to mypy-repair success.

**Acceptance Criteria:**
- F_mypy→✓ defined as: problem IDs where baseline pass@1=0 AND post-mypy pass@1>0 (at least one sample)
- Restricted to mypy-eligible problems: those with ≥1 baseline sample where mypy_exit_code ≠ 0
- F_mypy→✓ serialized to `h-m2/data/f_mypy_transitions.json`
- Repair success rate = |F_mypy→✓| / |mypy-eligible problems| logged
- F_mypy→✓ must be non-empty (≥1 transition) as PoC pre-condition

**Dependencies:** FR-3 (mypy_repair_pool.jsonl required)

---

### FR-6: C_score Computation within Eligibility-Conditioned Stratum

**Description:** Compute Jaccard overlap and C_score between F_SynCode→✓ and F_mypy→✓ within the eligibility-conditioned type/structural failure stratum, with bootstrap CI and Bonferroni correction.

**Acceptance Criteria:**
- Stratum definition: Problems where ≥1 baseline sample has FMD = type_structural AND is mypy-eligible
- Within stratum only: compute |F_SynCode ∩ F_mypy| and |F_SynCode ∪ F_mypy|
- J_obs = |F_SynCode ∩ F_mypy| / |F_SynCode ∪ F_mypy| (0.0 if union is empty)
- r1 = |F_SynCode ∩ stratum| / |stratum|; r2 = |F_mypy ∩ stratum| / |stratum|
- E[J] = (r1 × r2) / (r1 + r2 - r1 × r2)
- C_score = (E[J] - J_obs) / E[J]
- Bootstrap CI: 10,000 iterations, problem-level resampling (not sample-level); α=0.0167 (Bonferroni)
- Bootstrap p-value = fraction of bootstrap iterations where C_score ≤ 0
- Also compute raw (non-conditioned) C_score for comparison
- Difficulty quintile stratification: compute C_score per quintile (baseline pass@1 rate as difficulty proxy)
- All results serialized to `h-m2/results/c_score_results.json`

**Dependencies:** FR-4 (f_syncode_transitions.json), FR-5 (f_mypy_transitions.json), FR-2 (fmd_classification.jsonl)

---

### FR-7: Z3 Eligibility Expansion Measurement (ΔP)

**Description:** Measure whether mypy repair increases Z3 SMT encoding eligibility, computing ΔP = P(Z3_eligible | post-mypy) - P(Z3_eligible | baseline).

**Acceptance Criteria:**
- For each problem, attempt Z3 encoding on: (a) best-of-20 baseline sample, (b) best-of-20 post-mypy sample
- Z3 eligibility heuristic: integer arithmetic density in code AST > threshold AND return type annotated
- OR: Attempt actual Z3 encoding via existing z3_eligible_check from h-e1 codebase
- ΔP = mean(z3_eligible_post_mypy) - mean(z3_eligible_baseline) across all 164 problems
- Bootstrap CI: 10,000 iterations, problem-level resampling; CI lower bound > 0 required for secondary claim
- Results serialized to `h-m2/results/z3_eligibility_delta.json`

**Dependencies:** FR-3 (mypy_repair_pool.jsonl), FR-1 (baseline_pool.jsonl)

---

### FR-8: Visualization and Reporting

**Description:** Generate all required figures for paper and result reporting.

**Acceptance Criteria:**
- Figure 1 (Mandatory): Bar chart — C_score(SynCode, mypy) vs. 0 baseline with 95% CI error bars; ΔP(Z3_eligible) with CI. Save to `h-m2/figures/gate_metrics.png`
- Figure 2: Jaccard Matrix Heatmap — F_SynCode vs. F_mypy overlap: (a) raw, (b) eligibility-conditioned, (c) difficulty-stratified. Save to `h-m2/figures/jaccard_heatmap.png`
- Figure 3: FMD Failure Distribution Pie Chart — proportion of baseline pool in each stratum. Save to `h-m2/figures/fmd_distribution.png`
- Figure 4: Z3 Eligibility Before/After — P(Z3_eligible | baseline) vs. P(Z3_eligible | post-mypy) with 95% CI. Save to `h-m2/figures/z3_eligibility_comparison.png`
- Figure 5: Repair Round Convergence — fraction of eligible problems fixed at round 1, 2, 3. Save to `h-m2/figures/repair_convergence.png`
- Figure 6: Difficulty Quintile C_score — C_score per quintile with CI. Save to `h-m2/figures/quintile_c_score.png`
- All figures use matplotlib; saved as PNG at 150 DPI minimum

**Dependencies:** FR-2 through FR-7

---

### FR-9: Metrics Serialization and Gate Evaluation

**Description:** Serialize all gate-relevant metrics to a standardized JSON file for Phase 4 validator consumption.

**Acceptance Criteria:**
- Metrics file at `h-m2/results/metrics.json` with schema:
  ```json
  {
    "hypothesis_id": "h-m2",
    "gate_type": "SHOULD_WORK",
    "primary_metric": {
      "c_score": float,
      "j_obs": float,
      "e_j": float,
      "bootstrap_p_value": float,
      "ci_lower": float,
      "ci_upper": float,
      "stratum_size": int,
      "f_syncode_in_stratum": int,
      "f_mypy_in_stratum": int
    },
    "secondary_metric": {
      "delta_p_z3": float,
      "ci_lower": float,
      "ci_upper": float
    },
    "fmd_stats": {
      "n_problems": int,
      "n_syntax": int,
      "n_type_structural": int,
      "n_constraint_logical": int,
      "n_functional_only": int,
      "n_pass": int
    },
    "repair_stats": {
      "n_mypy_eligible": int,
      "f_mypy_size": int,
      "repair_success_rate": float,
      "mechanism_activated_rate": float
    },
    "gate_result": "PASS|PARTIAL|FAIL",
    "n_problems": 164
  }
  ```
- Gate evaluation logic:
  - PASS: C_score > 0 AND p < 0.0167 AND ΔP > 0.05 AND CI_lower > 0
  - PARTIAL: C_score > 0 AND (p >= 0.0167 OR ΔP ≤ 0.05) — directional but not significant
  - FAIL: C_score ≤ 0 — null result (publishable, proceed to h-m3)

**Dependencies:** FR-6, FR-7

---

## 4. Non-Functional Requirements

### NFR-1: Reproducibility
- All random seeds fixed (seed = problem_idx * 100 + sample_idx for pool generation)
- Bootstrap seeds fixed: `np.random.seed(42)` before bootstrap loop
- All pool files include seed metadata in JSONL records

### NFR-2: Performance
- Baseline pool generation: ≤4 hours on single GPU (A100 or equivalent)
- mypy feedback repair: ≤6 hours on single GPU (164 problems × 20 samples × 3 rounds max)
- Z3 eligibility check: 60s timeout per problem (from h-e1 established protocol)
- Bootstrap CI: ≤10 minutes on CPU (10,000 iterations, 164 problems)

### NFR-3: Fault Tolerance
- Checkpoint after every 10 problems in pool generation loops
- Resume from checkpoint on restart: check existing JSONL records, skip completed problems
- mypy API errors (import errors, timeout): catch and log, do not crash experiment

### NFR-4: Code Reuse
- Reuse h-e1 Z3 eligibility check function from `h-e1/code/`
- Reuse h-m1 SynCode pool for first 20 problems where available
- Share utility functions (FMD classification, bootstrap CI) via `h-m2/code/utils.py`

### NFR-5: Logging
- Experiment log to `h-m2/code/experiment.log` (append mode)
- Log format: `[TIMESTAMP] [LEVEL] [MODULE] message`
- Mechanism verification prints: `"mypy_feedback_applied: round={r}, errors_before={n}, errors_after={m}"`

---

## 5. Success Criteria

### Gate Metrics (SHOULD_WORK)

| Metric | Threshold | Type |
|--------|-----------|------|
| C_score(SynCode, mypy) | > 0, p < 0.0167 | Primary (SHOULD_WORK) |
| ΔP(Z3_eligible) | > 0.05, CI lower > 0 | Secondary |
| F_mypy→✓ | ≥ 1 transition | Pre-condition |
| type/structural stratum | ≥ 10 problems | Pre-condition |
| mechanism_activated | > 0.10 | Pre-condition |

### Pre-conditions (PoC Validity)
1. mypy-feedback repair loop runs without error on all 164 baseline pool problems
2. F_mypy→✓ is non-empty (≥1 failure-to-success transition)
3. FMD type/structural stratum has ≥10 eligible problems
4. Z3 eligibility test on post-mypy code completes without error

### Null Result Protocol
- C_score ≤ 0: Report "methods address same failure subset within conditioned stratum"; publishable null; proceed to h-m3
- ΔP ≤ 0: "Sequential staging provides no eligibility benefit"; paper focuses on parallel complementarity only

---

## 6. Dependencies

### External Libraries
```
evalplus>=0.3.0        # HumanEval+ dataset and functional evaluation
transformers>=4.35.0   # CodeLlama-7B generation
torch>=2.0.0           # GPU inference
accelerate>=0.24.0     # device_map="auto"
mypy>=1.0.0            # Type checking feedback
z3-solver>=4.12.0      # SMT eligibility check
numpy>=1.24.0          # Bootstrap CI
matplotlib>=3.7.0      # Visualization
syncode                # SynCode CFG generation (F_SynCode recomputation)
```

### Internal Dependencies
| Dependency | Source | Usage |
|------------|--------|-------|
| h-e1 baseline pool | `h-e1/data/baseline_pool.jsonl` | Reuse first 20 problems |
| h-m1 SynCode pool | `h-m1/data/syncode_pool.jsonl` | Reuse partial SynCode pool |
| h-e1 Z3 eligibility | `h-e1/code/` | Reuse z3_eligible_check function |
| CodeLlama-7B weights | `~/.cache/huggingface/hub/models--codellama--CodeLlama-7b-hf` | Already cached |

---

## 7. Out of Scope

- Model fine-tuning or gradient updates
- Datasets other than HumanEval+ (164 problems)
- C_score computation for h-m3 pairs (Z3 vs. SynCode, Z3 vs. mypy) — deferred to h-m3
- RSS (repair strategy selector) — deferred to h-m4
- Comparison against external baselines (Phase 5 comparison not required, skip_baseline_comparison=true)

---

## 8. Appendix: Phase 2C Completeness Check

| Phase 2C Item | Found in PRD | Section |
|--------------|-------------|---------|
| Dataset: HumanEval full 164 problems | ✅ | FR-1 |
| 20 samples/problem, fixed seeds | ✅ | FR-1 |
| mypy iterative feedback (max 3 rounds) | ✅ | FR-3 |
| T=0.8 baseline, T=0.2 repair | ✅ | FR-3 |
| FMD classification (4 strata) | ✅ | FR-2 |
| F_SynCode→✓ recomputation at N=164 | ✅ | FR-4 |
| F_mypy→✓ extraction | ✅ | FR-5 |
| C_score formula (independence null model) | ✅ | FR-6 |
| Bootstrap CI (10,000 iterations) | ✅ | FR-6 |
| Bonferroni correction α=0.0167 | ✅ | FR-6 |
| ΔP(Z3_eligible) measurement | ✅ | FR-7 |
| Difficulty quintile stratification | ✅ | FR-6 |
| Z3 timeout 60s | ✅ | NFR-2 |
| Figures (6 total) | ✅ | FR-8 |
| Metrics JSON with gate evaluation | ✅ | FR-9 |
| Null result protocol | ✅ | §5 |

*Generated by Phase 3 Workflow (no-MCP environment — inline PRD generation consistent with h-e1, h-m1 pipeline history)*
*Next: Step 3 — Architecture Agent*
