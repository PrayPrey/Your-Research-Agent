# Product Requirements Document (PRD)
# Hypothesis h-m1: NL Hint Ablation Experiment

**Generated**: 2026-08-20  
**Hypothesis ID**: h-m1  
**Type**: MECHANISM  
**Gate**: MUST_WORK  
**Archon Task**: 100fc27f-e71c-43b4-abd4-fd896677e021

---

## Executive Summary

Build evaluation harness testing h-m1: "NL hint removal drops LLM theorem prover success by 25-35 percentage points (tests 60% contribution claim)". Uses miniF2F-v2c (244 olympiad problems), comparing LeanCopilot on original vs NL-stripped Lean files. Primary metric: success rate delta (Δ). MUST_WORK gate requires Δ ≥ 25% with p < 0.05 to validate mechanistic attribution.

**Key Risk**: NL removal may break type-checking. **Mitigation**: 20-problem pilot validation before full run.

---

## Objectives

### Primary Goal
Measure performance drop when natural language hints (docstrings/comments) removed from formal Lean 4 theorems.

### Success Criteria
- **Technical**: Both datasets compile, 244 problems evaluated per condition
- **Scientific**: 25% ≤ Δ ≤ 35%, p < 0.05 (McNemar's test)
- **Gate**: PASS if Δ ≥ 25%; FAIL if Δ < 10%

### Non-Goals
- Optimizing LeanCopilot performance
- Testing alternative theorem provers
- Modifying miniF2F dataset beyond NL ablation

---

## Functional Requirements

### FR-1: Dataset Loading
**Priority**: P0  
**Description**: Download miniF2F-v2c from HuggingFace, extract 244 test problems.

**Acceptance**:
- [x] Load dataset: `roozbeh-yz/miniF2F_v2`, config `v2c`, split `test`
- [x] Verify 244 rows, schema includes `formal_statement` field
- [x] Export to structured format (list of dicts)

### FR-2: NL Ablation Preprocessing
**Priority**: P0  
**Description**: Strip docstrings (`/--! ... -/`) and inline comments (`-- ...`) from Lean code.

**Acceptance**:
- [x] Regex-based removal preserves theorem structure
- [x] Type signatures intact
- [x] No syntax errors introduced

### FR-3: Pilot Validation
**Priority**: P0  
**Description**: 20-problem pilot validates ablation feasibility.

**Acceptance**:
- [x] Random sample 20 problems (seed 42)
- [x] Generate ablated Lean file
- [x] Verify compilation: ≤3 type-check failures
- [x] Measure Δ on pilot: ≥5% measurable effect
- [x] Go/No-Go decision: escalate if >3 failures OR Δ < 5%

### FR-4: LeanCopilot Evaluation
**Priority**: P0  
**Description**: Run theorem prover on both conditions (baseline, ablated).

**Acceptance**:
- [x] LeanCopilot with `search_proof` tactic
- [x] Config: @32 sampling, 300s timeout per problem
- [x] Parallel execution: 8 workers
- [x] Log per-problem: `success` (bool), `tactics_used` (int), `wall_time` (float), `error_type` (str)
- [x] Output: `baseline_results.jsonl`, `ablated_results.jsonl` (244 rows each)

### FR-5: Statistical Analysis
**Priority**: P0  
**Description**: Compare success rates, compute Δ, test significance.

**Acceptance**:
- [x] McNemar's test (paired proportions)
- [x] Bootstrap 95% CI (10,000 resamples)
- [x] Stratified analysis if metadata available (AMC/AIME/IMO)
- [x] Output: `comparison_stats.json` (Δ, p-value, CI, verdict)

### FR-6: Visualization
**Priority**: P1  
**Description**: Generate plots for 04_validation.md report.

**Acceptance**:
- [x] Bar chart: success rate by condition
- [x] Scatter: per-problem success (baseline vs ablated)
- [x] Histogram: Δ bootstrap distribution

---

## Non-Functional Requirements

### NFR-1: Performance
- Pilot: complete in <3 hours (20 problems × 2 conditions)
- Full run: complete in <48 hours (244 problems × 2 conditions, 8 workers)
- Analysis: complete in <1 hour

### NFR-2: Reproducibility
- Fixed random seeds (dataset sampling: 42, bootstrap: 42)
- Pinned versions: Lean 4.17.0, LeanCopilot main branch
- Logged configuration (sampling budget, timeout) in output files

### NFR-3: Robustness
- Timeout handling: kill stuck processes after 360s (300s + 60s buffer)
- Error logging: type-check failures, tactic failures, timeouts
- Partial results: IF worker crashes, continue with remaining problems

### NFR-4: Usability
- CLI interface for evaluation harness
- JSON output (machine-readable)
- Markdown report (human-readable, embeds plots)

---

## User Stories

### US-1: Research Scientist Validates NL Hypothesis
**As a** research scientist,  
**I want to** compare LeanCopilot performance on original vs NL-stripped theorems,  
**So that** I can quantify NL hint contribution to LLM prover advantage.

**Acceptance**:
- Run pilot, get Go/No-Go decision
- IF pilot passes, run full evaluation
- Receive 04_validation.md with Δ, p-value, gate verdict

### US-2: Experimenter Debugs Type-Check Failures
**As an** experimenter,  
**I want to** inspect failed ablations in pilot,  
**So that** I can diagnose if NL removal broke semantic type info.

**Acceptance**:
- Pilot outputs list of failed problems
- Manual inspection of 5 examples
- Decision: refine regex OR escalate fallback

### US-3: Reviewer Inspects Statistical Tests
**As a** reviewer,  
**I want to** verify McNemar's test and bootstrap CI,  
**So that** I can trust gate decision (PASS/FAIL).

**Acceptance**:
- comparison_stats.json includes test statistic, p-value, CI bounds
- 04_validation.md cites statistical assumptions
- Bootstrap distribution plot shows no outliers

---

## Technical Specifications

### TS-1: Dataset Schema
```python
{
  "problem_id": str,          # e.g., "test_001"
  "formal_statement": str,    # Lean 4 theorem declaration
  "informal_statement": str,  # NL problem description (not used)
  "source": str               # AMC/AIME/IMO (optional)
}
```

### TS-2: Evaluation Results Schema
```json
{
  "problem_id": "test_001",
  "condition": "baseline",  // "baseline" | "ablated"
  "success": true,
  "tactics_used": 8,
  "wall_time": 12.3,
  "error_type": null        // null | "timeout" | "type_check" | "tactic_failed"
}
```

### TS-3: Statistical Output Schema
```json
{
  "baseline_success_rate": 0.65,
  "ablated_success_rate": 0.35,
  "delta": 0.30,
  "mcnemar_statistic": 45.2,
  "p_value": 0.0001,
  "ci_95_low": 0.25,
  "ci_95_high": 0.35,
  "verdict": "PASS"  // "PASS" | "FAIL" | "INCONCLUSIVE"
}
```

---

## Dependencies

### External Systems
- **HuggingFace Datasets**: `roozbeh-yz/miniF2F_v2` (public)
- **LeanCopilot**: https://github.com/lean-dojo/LeanCopilot (main branch)
- **Lean 4**: v4.17.0 (elan-managed)

### Libraries
- Python 3.9+
- `datasets` (HuggingFace)
- `numpy`, `scipy` (statistical tests)
- `matplotlib` (plots)

### Infrastructure
- 1× GPU (NVIDIA A5000, 24GB VRAM)
- 32 CPU cores
- 128GB RAM
- 50GB storage

---

## Risks and Mitigations

### RISK-001: Type-Check Failures After NL Removal
**Probability**: 30%  
**Impact**: HIGH (blocks experiment)  
**Mitigation**: 20-problem pilot before full run  
**Fallback**: Pivot to external Mathlib docs removal (not inline comments)

### RISK-002: No Measurable Effect (Δ < 10%)
**Probability**: 20%  
**Impact**: HIGH (falsifies hypothesis)  
**Mitigation**: Accept negative result, report in 04_validation.md  
**Implication**: Revise main hypothesis (NL contributes <30%, not 60%)

### RISK-003: Confound (NL Removal Also Removes Type Info)
**Probability**: 40%  
**Impact**: MEDIUM (conflates mechanisms)  
**Mitigation**: Manual inspection of 20 ablated examples  
**Diagnostic**: IF type signatures preserved AND success drops → NL effect is real

### RISK-004: GPU Availability
**Probability**: 30%  
**Impact**: LOW (delays timeline)  
**Mitigation**: Queue overnight, request dedicated allocation

---

## Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Setup | 1 day | Lean 4.17 + LeanCopilot installed |
| Pilot | 0.5 day | 20-problem validation, Go/No-Go |
| Full Run | 2 days | 244 problems × 2 conditions evaluated |
| Analysis | 0.5 day | Statistical tests, plots, 04_validation.md |
| **Total** | **4 days** | **Complete h-m1 validation** |

---

## Deliverables

### Code
- `dataset_loader.py`: Download miniF2F-v2c
- `preprocess.py`: NL ablation script
- `evaluate_leancopilot.py`: Parallel evaluation harness
- `analyze.py`: Statistical tests + plots

### Data
- `MiniF2F_v2c_Test.lean` (baseline)
- `MiniF2F_v2c_Test_NoNL.lean` (ablated)
- `baseline_results.jsonl` (244 rows)
- `ablated_results.jsonl` (244 rows)
- `comparison_stats.json`

### Reports
- `04_validation.md`: Gate decision, statistical tests, plots

### Visualizations
- `success_rate_comparison.png`
- `per_problem_scatter.png`
- `delta_bootstrap_distribution.png`

---

## Acceptance Criteria

### Technical
- [ ] Pilot: ≤3 type-check failures, Δ ≥ 5%
- [ ] Full run: 0 compilation errors for both datasets
- [ ] Full run: 244 problems evaluated per condition
- [ ] All results logged to JSONL (no missing rows)

### Scientific
- [ ] **Primary**: 25% ≤ Δ ≤ 35% (confirms 60% NL contribution)
- [ ] **Falsification**: IF Δ < 10%, reject NL hypothesis
- [ ] **Statistical**: p < 0.05 (McNemar's test)
- [ ] **Robustness**: 95% CI excludes 0

### Gate Decision
- [ ] PASS: Δ ≥ 25% AND p < 0.05 → proceed to next hypothesis
- [ ] FAIL: Δ < 10% OR p ≥ 0.05 → terminate h-m1, revise main hypothesis
- [ ] INCONCLUSIVE: 10% ≤ Δ < 25% → re-evaluate attribution percentages

---

## References

**miniF2F-v2c**: https://huggingface.co/datasets/roozbeh-yz/miniF2F_v2  
**LeanCopilot**: https://github.com/lean-dojo/LeanCopilot  
**miniF2F-v2 Paper**: https://arxiv.org/abs/2511.03108  
**LeanCopilot Paper**: https://arxiv.org/abs/2404.12534
