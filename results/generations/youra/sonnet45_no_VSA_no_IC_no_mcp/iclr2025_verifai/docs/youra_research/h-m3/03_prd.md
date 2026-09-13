# Product Requirements Document: Invalid Beam Pruning (h-m3)

**Version:** 1.0  
**Date:** 2026-08-25  
**Hypothesis ID:** h-m3  
**Type:** MECHANISM  
**Status:** Implementation Planning

---

## Executive Summary

Implement beam validity tracking mechanism to verify that invalid beams (syntax_validity_score=0) receive lower final scores and are pruned over time in favor of valid beams (validity_score=1) during beam search code generation. This validates the pruning mechanism introduced by h-m2's combined scoring approach.

**Success Metric:** ≥50% reduction in invalid beam proportion from start to end of generation, with ≥60% of final beams being syntactically valid.

---

## Problem Statement

### Background
h-m2 validated that combined scoring (α * log_likelihood + β * syntax_validity_score) correctly ranks beams by fluency and validity. However, ranking alone doesn't prove pruning effectiveness - invalid beams could persist despite lower scores if beam search selection doesn't converge correctly.

### Research Question
Does the combined scoring mechanism (α=0.7, β=0.3) actually prune invalid beams over time, or do they persist throughout generation?

### Dependencies
- **h-m2 (VALIDATED):** Combined scoring mechanism proven effective
  - AST parsing <0.05ms (well under 50ms target)
  - 73.33% valid beam outputs (target ≥60%)
  - 38% syntax error reduction vs baseline
  - Optimal weights: α=0.7, β=0.3

---

## Functional Requirements

### FR1: Beam Validity Tracker
**Priority:** P0 (Critical)

Implement `BeamValidityTracker` class to monitor beam validity status at each generation step.

**Acceptance Criteria:**
- Track validity status (valid=1, invalid=0) for all k beams at each step
- Compute invalid_proportion = count(validity=0) / k
- Store temporal log: step_id → invalid_proportion
- Compute reduction rate: (initial - final) / initial

**Interface:**
```python
class BeamValidityTracker:
    def track_step(self, step_id: int, beams: List[str]) -> None
    def compute_reduction(self) -> float
    def get_temporal_log(self) -> List[Dict[str, float]]
```

---

### FR2: Experiment A - Invalid Beam Proportion Tracking
**Priority:** P0 (Critical)

Run beam search on full HumanEval-164 dataset with per-step validity tracking.

**Acceptance Criteria:**
- Execute beam search with k=5, α=0.7, β=0.3
- Track invalid proportion at each generation step (t=0 to T)
- Measure reduction rate for all 164 problems
- Report: mean reduction ≥50%, median reduction ≥50%
- Generate `results/reduction_rates.json`

---

### FR3: Experiment B - Final Beam Validity Distribution
**Priority:** P0 (Critical)

Measure final k=5 beam validity distribution after generation completes.

**Acceptance Criteria:**
- Parse all final beams with ast.parse()
- Count valid beams per problem
- Compute valid_proportion = count(valid) / k
- Report: mean valid proportion ≥60%
- At least 70% of problems have ≥3 valid beams
- Generate `results/final_validity.json`

---

### FR4: Experiment C - Temporal Pruning Dynamics
**Priority:** P1 (High)

Analyze pruning pattern across generation timeline (early/middle/late phases).

**Acceptance Criteria:**
- Divide generation into 3 phases: early (0-33%), middle (33-66%), late (66-100%)
- Compute mean invalid proportion per phase
- Track beam turnover rate per phase
- Verify monotonic decrease (late < early)
- Generate `results/temporal_dynamics.json`

---

### FR5: Baseline Comparison - Pure Log-Likelihood Beam Search
**Priority:** P1 (High)

Run control experiment with no validity scoring (α=1.0, β=0.0).

**Acceptance Criteria:**
- Execute beam search with α=1.0, β=0.0 on same HumanEval-164
- Track invalid proportion over time (same protocol as FR2)
- Compare temporal patterns: pure vs combined scoring
- Expected: pure beam search shows no systematic pruning
- Generate `results/baseline_comparison.json`

---

### FR6: AST Validation Module (Reuse from h-m2)
**Priority:** P0 (Critical)

Reuse AST-based syntax validation from h-m2 codebase.

**Acceptance Criteria:**
- Reuse existing `validate_syntax(code_snippet)` function
- Return: (is_valid: bool, validity_score: int)
- Latency requirement: <50ms (h-m2 achieved <0.05ms)
- Handle partial code snippets gracefully

**Interface:**
```python
def validate_syntax(code_snippet: str) -> Tuple[bool, int]:
    # Returns (True, 1) if valid, (False, 0) if invalid
```

---

### FR7: Beam Search with Tracking (Extension of h-m2)
**Priority:** P0 (Critical)

Extend h-m2 beam search implementation to include validity tracking.

**Acceptance Criteria:**
- Integrate BeamValidityTracker at each generation step
- Log beam states before and after pruning
- Preserve h-m2's combined scoring: α=0.7, β=0.3
- Return: generated code + validity logs
- No performance degradation vs h-m2 baseline

---

### FR8: Logging Infrastructure
**Priority:** P1 (High)

Structured logging for per-step beam validity states.

**Acceptance Criteria:**
- Log format: CSV or JSON
- Fields: problem_id, step_id, beam_id, validity_score, invalid_proportion
- Save to: `results/beam_validity_logs.csv`
- Support incremental writing (stream-friendly)

---

### FR9: Data Analysis Pipeline
**Priority:** P1 (High)

Generate statistical summaries and visualizations.

**Acceptance Criteria:**
- Compute reduction statistics: mean, median, p25, p75
- Plot reduction histogram across 164 problems
- Plot temporal pruning curve (invalid proportion over time)
- Plot final validity distribution (0-5 valid beams)
- Baseline comparison plot (pure vs combined scoring)
- Save figures to: `figures/*.png`

---

## Non-Functional Requirements

### NFR1: Compute Budget
- **Constraint:** <30 minutes total runtime for all experiments
- **Justification:** Full HumanEval-164 generation estimated at ~15 min, baseline comparison adds ~15 min
- **Hardware:** GPU with ≥16GB VRAM for CodeLlama-7B

### NFR2: Reproducibility
- **Requirement:** Fixed random seed for beam search
- **Justification:** Enable exact reproduction of results
- **Implementation:** Set torch.manual_seed(42) before generation

### NFR3: Code Reuse
- **Requirement:** Maximize reuse from h-m2 codebase
- **Justification:** Reduce implementation time, ensure consistency
- **Components to reuse:** AST validation, combined scoring, beam search core

### NFR4: Data Integrity
- **Requirement:** HumanEval-164 SHA256 checksum verification
- **Justification:** Ensure dataset not corrupted
- **Implementation:** Verify checksum against official release

### NFR5: Failure Handling
- **Requirement:** Graceful handling of AST parse errors
- **Justification:** Invalid code may cause parse crashes
- **Implementation:** Wrap ast.parse() in try-except, return validity_score=0 on failure

---

## Success Criteria

### Primary Criteria (Gate: SHOULD_WORK)
1. **Invalid beam reduction ≥50%** (mean across 164 problems)
2. **Final valid proportion ≥60%** (mean across 164 problems)

**Pass Action:** Proceed to h-m4 (Final Valid Output Selection)  
**Fail Action:** PIVOT - increase β weight to 0.4 or 0.5

### Secondary Criteria
3. **Monotonic pruning** (invalid proportion decreases over time)
4. **Baseline difference** (combined scoring shows pruning, pure beam search doesn't)

**Pass Action:** Validates mechanism design  
**Fail Action:** EXPLORE - analyze why pruning delayed or irregular

---

## Dependencies and Integration

### Upstream Dependencies
- **h-m2 codebase:**
  - `validate_syntax()` function
  - Combined scoring implementation
  - Beam search core logic
  - HumanEval-164 dataset loader

### Downstream Dependencies
- **h-m4:** Uses same beam search infrastructure
- **Phase 4.5:** Synthesis report will reference pruning effectiveness
- **Phase 6:** Paper will discuss pruning mechanism validation

### External Dependencies
- **transformers:** HuggingFace library for CodeLlama-7B
- **torch:** PyTorch backend
- **datasets:** HumanEval dataset loading
- **ast:** Python standard library (no install needed)
- **numpy, pandas:** Data analysis
- **matplotlib, seaborn:** Visualization

---

## Data Requirements

### Input Data
- **HumanEval-164 dataset**
  - Source: https://github.com/openai/human-eval
  - Size: 164 problems
  - Format: JSON with prompt + canonical_solution + test
  - Verification: SHA256 checksum

### Output Data
- `results/beam_validity_logs.csv` (~4,920 rows: 164 problems × 30 steps)
- `results/reduction_rates.json` (164 entries)
- `results/final_validity.json` (164 entries)
- `results/temporal_dynamics.json` (3 phases × statistics)
- `results/baseline_comparison.json` (2 conditions × temporal data)

### Visualizations
- `figures/reduction_histogram.png`
- `figures/temporal_pruning.png`
- `figures/final_validity_dist.png`
- `figures/baseline_comparison.png`

---

## Model Configuration

**Model:** CodeLlama-7B  
**Pretrained ID:** meta-llama/CodeLlama-7b-hf  
**Framework:** HuggingFace Transformers  

**Generation Config:**
- max_new_tokens: 512
- temperature: 0.8
- num_beams: 5
- num_return_sequences: 5

**Scoring Config:**
- α (log-likelihood weight): 0.7
- β (validity weight): 0.3
- scoring_function: `α * log_likelihood + β * syntax_validity_score`

---

## Risk Mitigation

### Risk 1: Invalid Beams Persist (Reduction <50%)
**Diagnosis:** β=0.3 too low, validity signal drowned by log-likelihood  
**Mitigation:** Increase β to 0.4 or 0.5 in ablation run

### Risk 2: No Pruning Observed
**Diagnosis:** Beam search implementation broken  
**Mitigation:** Add detailed score logging, verify selection logic against h-m2

### Risk 3: Pruning Delayed (Only Late-Phase)
**Diagnosis:** Beam diversity low early, validity matters only at completion  
**Mitigation:** Analyze beam diversity, consider dynamic β schedule

---

## Deliverables

### Code Artifacts
1. `beam_validity_tracker.py` - BeamValidityTracker class
2. `beam_search_with_tracking.py` - Extended beam search
3. `run_experiment_a.py` - Invalid proportion tracking
4. `run_experiment_b.py` - Final validity measurement
5. `run_experiment_c.py` - Temporal dynamics analysis
6. `run_baseline_comparison.py` - Pure beam search control
7. `analysis_notebooks/` - Jupyter notebooks

### Data Artifacts
1. `results/beam_validity_logs.csv`
2. `results/reduction_rates.json`
3. `results/final_validity.json`
4. `results/temporal_dynamics.json`
5. `results/baseline_comparison.json`

### Visualizations
1. `figures/reduction_histogram.png`
2. `figures/temporal_pruning.png`
3. `figures/final_validity_dist.png`
4. `figures/baseline_comparison.png`

### Documentation
1. `04_validation.md` - Hypothesis validation report (Phase 4)
2. `experiment_logs.txt` - Runtime logs

---

## Timeline Estimate

| Phase | Duration | Notes |
|-------|----------|-------|
| Data Preparation | 10 min | Reuse h-m2 cache |
| Environment Setup | 10 min | Reuse h-m2 environment |
| Implementation | 3-4 hours | Extend h-m2 beam search |
| Experiment A | 15 min | Run with tracking |
| Experiment B | 0 min | Same run as A |
| Experiment C | 0 min | Analysis only |
| Baseline Comparison | 15 min | Pure beam search |
| Analysis | 2-3 hours | Plots, statistics, report |

**Total:** 6-8 hours

---

## Appendix A: Experiment Brief Reference

**Source:** `h-m3/02c_experiment_brief.md`  
**Generated:** 2026-08-25  
**Schema Version:** 3.5

Key sections referenced:
- Section 5: Experiments (FR2, FR3, FR4, FR5)
- Section 6: Implementation Requirements (FR1, FR6, FR7, FR8)
- Section 7: Success Criteria (Primary/Secondary)
- Section 9: Risk Mitigation (Risk 1-3)

---

## Appendix B: Baseline Reference (h-m2)

**h-m2 Validation Results:**
- AST parsing latency: <0.05ms (target <50ms) ✓
- Valid beam proportion: 73.33% (target ≥60%) ✓
- Syntax error reduction: 38% vs pure log-likelihood ✓
- Optimal weights: α=0.7, β=0.3 ✓

**Reusable Components:**
- `validate_syntax()` function
- Combined scoring implementation
- Beam search core logic
- HumanEval-164 dataset loader

---

**Document Status:** Ready for Architecture Design (Step 3)
