# Product Requirements Document: Combined Scoring Function (h-m2)

**Date:** 2026-08-25  
**Hypothesis ID:** h-m2  
**Type:** MECHANISM  
**Gate:** SHOULD_WORK  
**Prerequisites:** h-m1 (VALIDATED)

---

## Executive Summary

Implement and validate a combined scoring mechanism (α * log_likelihood + β * syntax_validity_score) for beam search code generation. This mechanism ranks beam candidates by both fluency (log-likelihood) and syntactic validity (AST parsing), enabling proper beam pruning in subsequent hypotheses. Success requires: (1) AST parsing latency <50ms per check, (2) valid beams ranking higher than invalid beams in ≥80% of generation steps, (3) improved syntax error rate over greedy baseline.

---

## Problem Statement

**Problem:** Beam search (h-m1) maintains k=5 candidate sequences, but without validity-aware scoring, invalid syntactic candidates may rank higher than valid ones, preventing effective pruning.

**Impact:** If scoring is broken (wrong formula, slow AST parsing) or invalid beams consistently score higher, subsequent pruning mechanisms (h-m3) cannot reduce syntax errors.

**Constraints:**
- AST parse latency budget: <50ms mean (to avoid generation slowdown)
- Computational budget: <30 minutes total runtime for all experiments
- Hardware: Single GPU (≥16GB VRAM for CodeLlama-7B)

---

## Functional Requirements

### FR-1: Combined Scoring Function
**Priority:** P0 (Critical)  
**Description:** Implement scoring formula that combines log-likelihood and syntax validity.

**Specifications:**
- Formula: `final_score = α * log_likelihood + β * syntax_validity_score`
- Default weights: α=0.7, β=0.3 (from verification plan)
- Inputs:
  - `log_likelihood`: float (from model output)
  - `syntax_validity_score`: binary (1 if AST parse succeeds, 0 otherwise)
- Output: `final_score`: float

**Acceptance Criteria:**
- Scoring function callable at each beam search step
- Weights configurable via parameters
- Returns numerical score for each beam candidate

---

### FR-2: AST Syntax Validation
**Priority:** P0 (Critical)  
**Description:** Validate Python code snippets using AST parsing with latency instrumentation.

**Specifications:**
- Module: Python standard library `ast.parse()`
- Inputs: Code string (beam candidate)
- Outputs:
  - `valid`: boolean (True if parse succeeds, False on SyntaxError)
  - `elapsed_ms`: float (parse latency in milliseconds)
- Error handling: Catch `SyntaxError`, return valid=False

**Acceptance Criteria:**
- AST parse mean latency <50ms
- AST parse p95 latency <100ms
- Validation callable for each beam candidate

---

### FR-3: Beam Search with Custom Scoring
**Priority:** P0 (Critical)  
**Description:** Extend HuggingFace beam search to use combined scoring instead of pure log-likelihood.

**Specifications:**
- Base: HuggingFace Transformers `BeamSearchScorer`
- Customization: Override beam selection to use `final_score` from FR-1
- At each generation step:
  1. Get log_likelihood from model
  2. Validate each beam candidate with AST parse (FR-2)
  3. Compute final_score for each beam (FR-1)
  4. Select top-k beams by final_score (not log_likelihood)
- Beam width: k=5 (validated in h-m1)

**Acceptance Criteria:**
- Beam selection uses combined scoring
- All k=5 beams tracked with scores at each step
- Log-likelihood and validity scores logged separately

---

### FR-4: Experiment A - AST Latency Measurement
**Priority:** P0 (Critical)  
**Description:** Measure AST parse latency across full HumanEval-164 dataset.

**Specifications:**
- Dataset: HumanEval-164 (164 problems, standard benchmark)
- Model: CodeLlama-7B (meta-llama/CodeLlama-7b-hf)
- Beam width: k=5
- For each beam candidate at each generation step:
  - Measure AST parse time (FR-2)
  - Log: problem_id, step_id, beam_id, elapsed_ms
- Aggregate statistics: mean, median, p95, max latency

**Acceptance Criteria:**
- All 164 problems processed
- ~24,600 AST parse calls logged (164 × 5 beams × ~30 steps)
- Statistics computed and saved to JSON

---

### FR-5: Experiment B - Beam Ranking Verification
**Priority:** P0 (Critical)  
**Description:** Verify valid beams rank higher than invalid beams when using default weights (α=0.7, β=0.3).

**Specifications:**
- Dataset: HumanEval-164 (same as FR-4)
- Model: CodeLlama-7B
- Beam width: k=5
- At each generation step, log:
  - beam_id, log_likelihood, syntax_validity_score, final_score, rank
- Analysis:
  - Count steps where valid beams (validity=1) have higher final_score than invalid beams (validity=0)
  - Compute proportion: correct_ranking_steps / total_steps

**Acceptance Criteria:**
- All 164 problems processed
- Beam rankings logged at each step
- Proportion of correct rankings computed

---

### FR-6: Experiment C - α/β Ablation Study
**Priority:** P1 (High)  
**Description:** Test 4 weight combinations to validate α=0.7, β=0.3 optimality.

**Specifications:**
- Dataset: HumanEval-Ablation-20 (20 problems, stratified sample)
- Weight combinations:
  1. (α=0.5, β=0.5) - Equal weight
  2. (α=0.6, β=0.4) - Moderate validity emphasis
  3. (α=0.7, β=0.3) - Default
  4. (α=0.8, β=0.2) - Strong fluency emphasis
- For each combination:
  - Run beam search on 20 problems
  - Measure: ranking correctness, final syntax error rate, beam diversity
- Compare across combinations

**Acceptance Criteria:**
- 80 beam search runs completed (4 combinations × 20 problems)
- Metrics computed per combination
- Optimal weights identified

---

### FR-7: Baseline Comparison
**Priority:** P1 (High)  
**Description:** Compare combined scoring against greedy sampling and pure log-likelihood beam search.

**Specifications:**
- Baselines:
  1. **Greedy Sampling** (from h-m1): Syntax error rate 64-68%
  2. **Pure Log-Likelihood Beam Search**: α=1.0, β=0.0 (beam search without validity scoring)
- Dataset: HumanEval-164
- Run pure log-likelihood beam search
- Measure: final syntax error rate, proportion of valid beams in top-k
- Compare against combined scoring results

**Acceptance Criteria:**
- Pure log-likelihood baseline completed
- Syntax error rates compared
- Relative improvement computed

---

### FR-8: Logging Infrastructure
**Priority:** P0 (Critical)  
**Description:** Log beam states at each generation step for analysis.

**Specifications:**
- Log fields:
  - problem_id, step_id, beam_id
  - log_likelihood, syntax_validity_score, final_score, rank
  - elapsed_ms (AST parse time)
- Output format: CSV or JSON (structured)
- Storage: Save to `results/beam_ranking_logs.csv` or `.json`

**Acceptance Criteria:**
- All beam states logged during generation
- Logs readable and parsable for analysis
- No data loss or missing fields

---

## Non-Functional Requirements

### NFR-1: Performance
- **AST Latency:** Mean <50ms, p95 <100ms (per FR-2)
- **Total Runtime:** <30 minutes for all experiments (FR-4 + FR-5 + FR-6 + FR-7)
- **Compute:** Single GPU run (no distributed setup)

### NFR-2: Reproducibility
- Fixed random seed for beam search sampling
- HuggingFace model cache path documented
- Dataset checksum verification (SHA256 for HumanEval-164)

### NFR-3: Code Quality
- Modular design: separate modules for scoring (FR-1), validation (FR-2), beam search (FR-3)
- Type hints for function signatures
- Error handling for SyntaxError in AST parsing

### NFR-4: Data Integrity
- No silent failures in AST parsing
- All 164 problems processed (no early termination)
- Log completeness verification

---

## Data Specifications

### Dataset 1: HumanEval-164
- **Type:** Standard benchmark
- **Source:** https://github.com/openai/human-eval
- **Size:** 164 hand-written Python programming problems
- **Split:** Full test set (no train/val split)
- **Verification:** SHA256 checksum against official release
- **Cache Path:** TBD during data preparation
- **Used In:** FR-4, FR-5, FR-7

### Dataset 2: HumanEval-Ablation-20
- **Type:** Custom subset (stratified sample)
- **Source:** Sampled from HumanEval-164
- **Size:** 20 problems
- **Sampling Strategy:** Stratified by difficulty, covering varied syntax patterns (loops, comprehensions, recursion)
- **Used In:** FR-6

### Model: CodeLlama-7B
- **Pretrained ID:** meta-llama/CodeLlama-7b-hf
- **Framework:** HuggingFace Transformers
- **Hardware:** GPU (CUDA)
- **Generation Config:**
  - max_new_tokens: 512
  - temperature: 0.8
  - num_beams: 5
  - num_return_sequences: 5
- **Cache Path:** TBD during environment setup

---

## Evaluation Metrics

### Primary Metrics (Success Criteria)

| Metric | Target | Gate Action if Failed |
|--------|--------|----------------------|
| **AST Parse Latency (Mean)** | <50ms | PIVOT (implement caching or reduce k) |
| **AST Parse Latency (p95)** | <100ms | PIVOT |
| **Beam Ranking Correctness** | ≥80% of steps (valid > invalid) | EXPLORE (adjust α/β or scoring formula) |

### Secondary Metrics

| Metric | Target | Gate Action if Failed |
|--------|--------|----------------------|
| **Final Syntax Error Rate** | < greedy baseline (64-68%) | PIVOT (increase β weight) |
| **Top-Ranked Valid Proportion** | ≥60% of rank-1 beams valid | EXPLORE (adjust weights) |
| **α/β Optimality** | At least one combination passes ranking criterion | EXPLORE (alternative scoring) |

### Diagnostic Metrics
- Mean final_score gap between valid and invalid beams
- Beam diversity (proportion of unique outputs in k=5 beams)
- Distribution of valid beam ranks (top-3, top-5 frequency)

---

## Success Criteria

### Gate: SHOULD_WORK

**Primary Success (All Required):**
1. AST parse mean latency <50ms
2. Valid beams rank higher in ≥80% of generation steps (α=0.7, β=0.3)
3. At least one α/β combination achieves ranking ≥80%

**Secondary Success (At Least One):**
1. Final syntax error rate < greedy baseline (64-68%)
2. Combined scoring outperforms pure log-likelihood beam search

**Gate Actions on Failure:**
- **AST Slow (latency >50ms):** PIVOT → Implement AST caching or reduce k to 3
- **Ranking Incorrect (<80%):** EXPLORE → Adjust α/β (test β=0.4, 0.5) or normalize log_likelihood
- **No Improvement over Baseline:** ABANDON → Mechanism hypothesis invalid

---

## Dependencies

### Prerequisite Hypotheses
- **h-m1 (VALIDATED):** Beam search infrastructure with k=5 maintenance verified
  - Reuse beam search setup
  - Same dataset/model (enables direct comparison)
  - Extends h-m1 by adding validity scoring

### External Dependencies
- **HuggingFace Transformers:** Beam search API
- **Python Standard Library:** `ast` module for parsing
- **datasets:** HumanEval loading
- **numpy, pandas:** Statistical analysis

### Hardware Dependencies
- NVIDIA GPU with ≥16GB VRAM
- CUDA support

---

## Implementation Deliverables

### Code Modules
1. `scoring_function.py` - Combined scoring implementation (FR-1)
2. `ast_validator.py` - AST validation with timing (FR-2)
3. `beam_search_custom.py` - Beam search with custom scoring (FR-3)
4. `run_experiment_a.py` - AST latency measurement (FR-4)
5. `run_experiment_b.py` - Beam ranking verification (FR-5)
6. `run_experiment_c.py` - α/β ablation study (FR-6)
7. `run_baseline_comparison.py` - Baseline experiments (FR-7)

### Data Artifacts
1. `results/ast_latency_stats.json` - Latency statistics (FR-4)
2. `results/beam_ranking_logs.csv` - Per-step beam rankings (FR-5, FR-8)
3. `results/ablation_results.json` - α/β comparison (FR-6)
4. `results/baseline_comparison.json` - Baseline vs combined scoring (FR-7)

### Documentation
1. `04_validation.md` - Hypothesis validation report (Phase 4 output)
2. `experiment_logs.txt` - Runtime logs and debug output

---

## Timeline Estimate

| Phase | Duration | Notes |
|-------|----------|-------|
| **Data Preparation** | 30 minutes | Download HumanEval, verify checksums, create ablation subset |
| **Environment Setup** | 30 minutes | Install dependencies, configure GPU, test model loading |
| **Implementation** | 4-6 hours | Code scoring function, beam search, logging infrastructure |
| **Experiment A (AST Latency)** | 10 minutes | Run full HumanEval-164 with timing |
| **Experiment B (Beam Ranking)** | 10 minutes | Same run as A, analyze logs |
| **Experiment C (Ablation)** | 20 minutes | 4 combinations × 20 problems |
| **Baseline Comparison** | 10 minutes | Pure log-likelihood beam search |
| **Analysis** | 2-3 hours | Generate plots, compute statistics, write validation report |

**Total Estimated Time:** 8-12 hours

---

## Risk Mitigation

### Risk R5: AST Parsing Slow
**Mitigation:**
- Monitor latency in Experiment A (FR-4)
- If >50ms mean: Implement AST parse caching (cache results for identical code snippets)
- If still slow: Reduce beam width k (test k=3 as fallback)

### Risk R3: α/β Suboptimal
**Mitigation:**
- Ablation study (FR-6) tests 4 combinations
- If all fail: Expand grid search to β=0.4, 0.5, 0.6
- If still suboptimal: Consider learned validity features (Variant B from verification plan)

### Risk: Scoring Formula Broken
**Symptom:** Invalid beams consistently rank higher than valid beams  
**Diagnosis:**
- Check log_likelihood magnitude (much larger than validity_score?)
- Normalize log_likelihood to [0, 1] range before combining
- Test alternative formula: `final_score = α * normalized_log_likelihood + β * syntax_validity_score`

---

## Out of Scope

- Semantic correctness validation (only syntax checked)
- Multi-language support (Python only)
- Distributed/multi-GPU training
- Online learning or model fine-tuning
- Execution-based validation (no code execution, only AST parsing)

---

## Appendix: Phase 2C Alignment

This PRD fully covers the Phase 2C experiment brief (02c_experiment_brief.md):

| Phase 2C Element | PRD Coverage |
|------------------|--------------|
| **Experiments A-C** | FR-4 (Latency), FR-5 (Ranking), FR-6 (Ablation) |
| **Baseline Comparison** | FR-7 (Greedy + Pure Log-Likelihood) |
| **Dataset HumanEval-164** | FR-4, FR-5, FR-7 (full test set) |
| **Dataset Ablation-20** | FR-6 (stratified subset) |
| **Model CodeLlama-7B** | Data Specifications section |
| **Success Criteria** | Success Criteria section (AST <50ms, Ranking ≥80%, Error rate < baseline) |
| **α/β Combinations** | FR-6 (4 weight pairs tested) |
| **Logging Infrastructure** | FR-8 (per-step beam state logs) |

---

**Generated:** 2026-08-25  
**Workflow:** Phase 3 Implementation Planning (BATCH mode)  
**Schema Version:** 3.5
