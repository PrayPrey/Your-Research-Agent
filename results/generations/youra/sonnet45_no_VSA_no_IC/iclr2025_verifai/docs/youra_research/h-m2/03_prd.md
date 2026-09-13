# Product Requirements Document (PRD)
# H-M2: Proof Depth Filtering Analysis

**Version**: 1.0  
**Date**: 2026-08-20  
**Hypothesis ID**: h-m2  
**Gate**: SHOULD_WORK  
**Complexity**: Level 1 (Post-processing Analysis)

---

## 1. Executive Summary

**Goal**: Measure how much proof depth contributes to LLM advantage in theorem proving by comparing success rates when restricted to shallow proofs (≤3 tactics) vs full proof search.

**Hypothesis**: Filtering to shallow proofs drops LLM success by 10-20 percentage points, testing the claim that proof depth explains 30% of the LLM advantage.

**Success Criteria**: 
- Pass: 5% < Δ < 30% (confirms depth contributes 8-60% of advantage)
- Fail: Δ outside bounds (rejects 30% attribution claim)

**Implementation Approach**: Post-hoc analysis pipeline — run LLM prover on miniF2F-test, extract tactic counts from successful proofs, compute stratified success rates.

---

## 2. User Stories

**US1**: As a researcher, I want to run an LLM prover on miniF2F-test and collect all successful proof terms, so I can analyze proof complexity patterns.

**US2**: As a researcher, I want to extract tactic counts from Lean 4 proof terms, so I can classify proofs by depth (shallow/medium/deep).

**US3**: As a researcher, I want to compute success rates stratified by allowed proof depth, so I can measure depth contribution to LLM advantage.

**US4**: As a researcher, I want statistical validation (McNemar test, bootstrap CI), so I can report effect size with confidence intervals.

**US5**: As a researcher, I want depth distribution visualizations (histograms), so I can communicate proof complexity patterns.

---

## 3. Functional Requirements

### 3.1 Proof Collection (FR1)

**FR1.1**: Run LLM prover (LeanCopilot or DeepSeek-Prover-V1.5) on miniF2F Lean 4 test set (244 theorems).

**FR1.2**: Configuration:
- Pass@k: k=16 attempts per problem
- Timeout: 60 seconds per attempt
- Max tokens: 1024 per generation
- Temperature: Standard LLM prover defaults

**FR1.3**: Log all successful proofs with:
- Problem name
- Full proof term (Lean 4 syntax)
- Success timestamp
- Attempt number (which of k=16)

**FR1.4**: Store proofs in structured format (JSON/CSV) for downstream analysis.

### 3.2 Tactic Extraction (FR2)

**FR2.1**: Parse Lean 4 proof terms to count tactic invocations.

**FR2.2**: Lean 4 Metaprogramming Approach:
- Use Lean 4 metaprogramming API to traverse proof term AST
- Count tactic nodes (e.g., `tacticSeq`, `tacticBlock`)
- Handle nested tactics correctly

**FR2.3**: Fallback: Proof script line counting (if AST parsing unavailable)
- Count non-empty, non-comment lines in proof script
- Normalize: remove `by`, `begin`, `end` markers
- Report as proxy metric with validation note

**FR2.4**: Output: CSV mapping (theorem_name, tactic_count, success)

**FR2.5**: Validation: Manual spot-check 10% of tactic counts for accuracy.

### 3.3 Stratification Analysis (FR3)

**FR3.1**: Classify each solved problem by minimum proof depth found:
- Shallow-solvable: ANY solution exists with ≤3 tactics
- Deep-only: ALL solutions require >3 tactics

**FR3.2**: Compute success rates:
- `Success_full` = (total solved problems) / 244
- `Success_shallow` = (shallow-solvable problems) / 244
- `Δ = Success_full - Success_shallow`

**FR3.3**: Depth distribution histogram:
- X-axis: tactic count (bins: 1-3, 4-10, 11-20, >20)
- Y-axis: problem count
- Annotation: median, 75th, 95th percentiles

**FR3.4**: Correlation analysis: problem difficulty (lean-auto baseline) × proof depth

### 3.4 Statistical Validation (FR4)

**FR4.1**: McNemar's test for paired comparison:
- Null: no difference between full vs shallow success
- Alternative: depth filtering affects success
- Report: χ² statistic, p-value, interpretation

**FR4.2**: Bootstrap confidence intervals:
- Resample (theorem, depth) pairs 10,000 times
- Compute Δ for each resample
- Report: 95% CI for effect size

**FR4.3**: Power analysis:
- Minimum N=30 solved problems required
- If <30 solved, report insufficient power, BLOCK hypothesis

**FR4.4**: Control test: Compare lean-auto depth distribution (from H-E1 data)
- If lean-auto also skews shallow, depth is difficulty confound
- Stratify by baseline success before depth filtering

---

## 4. Non-Functional Requirements

### 4.1 Performance

**NFR1**: Proof collection runtime ≤8 hours (244 theorems × 16 attempts × 60s + overhead).

**NFR2**: Tactic extraction runtime ≤15 minutes (post-processing all collected proofs).

**NFR3**: Statistical analysis runtime ≤5 minutes (Python scripts on single machine).

### 4.2 Reliability

**NFR4**: Proof collection fault tolerance:
- Resume from last checkpoint if interrupted
- Skip problems that timeout (log failures)
- Graceful API error handling (retry 3× with backoff)

**NFR5**: Tactic extraction validation:
- Spot-check 10% manual verification ≥80% accuracy
- If <80%, fallback to proof script line counting

### 4.3 Reproducibility

**NFR6**: Seed all randomness (LLM sampling, bootstrap resampling).

**NFR7**: Log exact versions:
- Lean 4 version
- Mathlib commit hash
- LLM prover version/API endpoint
- miniF2F commit hash

**NFR8**: Configuration file (YAML) for all hyperparameters.

### 4.4 Usability

**NFR9**: Single command execution: `python run_h_m2.py --config config.yaml`

**NFR10**: Progress logging: Print theorem N/244, current success rate every 10 problems.

**NFR11**: Output artifacts:
- `proofs.json`: All collected proofs
- `tactic_counts.csv`: Extracted depth data
- `results.json`: Success rates, Δ, statistics
- `depth_histogram.png`: Visualization
- `report.md`: Human-readable summary

---

## 5. Technical Constraints

**TC1**: Lean 4.14+ required (Mathlib v4 compatibility).

**TC2**: LLM API access:
- LeanCopilot API credentials OR
- DeepSeek-Prover-V1.5 API key OR
- Local Lean LLM prover setup (≥8GB VRAM GPU)

**TC3**: miniF2F Lean 4 dataset:
- Clone: `https://github.com/google-deepmind/miniF2F`
- Checkout: Lean 4 compatible branch
- Requires: Mathlib v4 dependencies

**TC4**: Python environment:
- Python 3.10+
- Dependencies: `pandas`, `scipy`, `matplotlib`, `lean4-interaction` (if available)

---

## 6. Out of Scope

**OS1**: Training new LLM models (use existing provers).

**OS2**: Proof search algorithm modifications (post-hoc analysis only).

**OS3**: Extending beyond miniF2F (no additional datasets).

**OS4**: Interactive proof refinement (automated pipeline only).

**OS5**: Comparing multiple LLM architectures (single prover baseline).

---

## 7. Dependencies

### 7.1 Data Dependencies

**D1**: miniF2F Lean 4 benchmark (244 theorems)
- Source: `https://github.com/google-deepmind/miniF2F`
- License: Apache 2.0
- Size: ~5 MB

### 7.2 Infrastructure Dependencies

**D2**: LLM Prover API (one of):
- LeanCopilot (preferred if available)
- DeepSeek-Prover-V1.5 API
- Alternative: Lean-gymnasium with LLM backend

**D3**: Lean 4 compiler + Mathlib
- Install: `elan install leanprover/lean4:v4.14.0`
- Mathlib: Compatible version from miniF2F repo

### 7.3 Code Dependencies

**D4**: Lean 4 metaprogramming (for tactic extraction)
- Use `Lean.Meta.MetaM` to traverse proof terms
- Fallback: Regex-based script parsing

**D5**: Statistical libraries
- `scipy.stats` (McNemar test)
- `numpy` (bootstrap resampling)
- `matplotlib` / `seaborn` (visualization)

### 7.4 Hypothesis Dependencies

**D6**: No blocking dependencies (h-m2 runs independently).

**D7**: Optional synergy: Reuse lean-auto depth data from h-e1 for confound control.

---

## 8. Success Metrics

### 8.1 Primary Metric

**M1**: Δ success rate (percentage points)
- **Target range**: 5% < Δ < 30%
- **Measurement**: `Success_full - Success_shallow`
- **Interpretation**: 
  - Δ ≈ 15% → confirms 30% depth contribution
  - Δ < 5% → rejects depth mechanism
  - Δ > 30% → contradicts NL dominance claim

### 8.2 Secondary Metrics

**M2**: Statistical significance (p < 0.05, McNemar test)

**M3**: Effect size precision (95% CI width <10 percentage points)

**M4**: Depth distribution shape:
- Median tactic count
- % problems solvable with ≤3 tactics
- % problems requiring >10 tactics

**M5**: Correlation: baseline difficulty × proof depth (Spearman ρ)

---

## 9. Risk Mitigation

### 9.1 Technical Risks

**R1: Insufficient solved problems (<30)**
- **Mitigation**: If LLM baseline low, reuse H-E1 or H-M1 proof logs
- **Fallback**: Report hypothesis as BLOCKED, insufficient statistical power

**R2: Tactic extraction failure**
- **Mitigation**: Fallback to proof script line counting (proxy metric)
- **Validation**: Manually verify 10% of counts

**R3: API rate limits / timeouts**
- **Mitigation**: Retry logic with exponential backoff
- **Fallback**: Local LLM prover deployment (requires GPU)

### 9.2 Validity Threats

**R4: Difficulty confound** (shallow problems inherently easier)
- **Test**: Compare lean-auto success on shallow vs deep strata
- **Control**: Stratify by baseline difficulty before depth filtering

**R5: Search bias** (LLM prefers shallow proofs)
- **Test**: Check if multiple proof depths exist for same problem
- **Limitation**: Post-hoc filtering ≠ controlled ablation (report in limitations)

---

## 10. Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Infrastructure setup | 4 hours | LeanCopilot API working, miniF2F cloned |
| Proof collection | 6-8 hours | `proofs.json` (all successful proofs) |
| Tactic extraction | 2 hours | `tactic_counts.csv` |
| Statistical analysis | 3 hours | `results.json`, `report.md` |
| Visualization | 1 hour | `depth_histogram.png` |
| **Total** | **16-18 hours** | Complete H-M2 validation package |

---

## 11. Deliverables

**Deliverable 1**: Proof dataset (`proofs.json`)
- All successful proofs from miniF2F-test
- Fields: problem name, proof term, tactic count, attempt number

**Deliverable 2**: Stratified success table (`results.json`)
- Success_full, Success_shallow, Δ
- McNemar p-value, bootstrap 95% CI
- Depth distribution statistics

**Deliverable 3**: Depth histogram (`depth_histogram.png`)
- Tactic count distribution (solved problems only)
- Annotations: median, quartiles, shallow threshold

**Deliverable 4**: Validation report (`04_validation.md`)
- Hypothesis outcome (CONFIRMED / REJECTED)
- Statistical evidence (effect size, CI, significance)
- Limitations (confounds, validity threats)
- Next steps (integration with H-M1, H-M3)

---

## 12. Acceptance Criteria

**AC1**: Proof collection completes for all 244 miniF2F theorems (or documents failures).

**AC2**: Tactic extraction validated: ≥80% accuracy on 10% manual spot-check.

**AC3**: Statistical tests executed: McNemar χ², bootstrap CI reported.

**AC4**: Δ success rate computed with clear pass/fail determination vs gate criteria.

**AC5**: All deliverables generated (proofs.json, results.json, histogram, report).

**AC6**: Reproducibility: Config file + random seeds allow exact rerun.

**AC7**: Report includes limitation discussion (difficulty confound, search bias).

---

## 13. Open Questions

**Q1**: Which LLM prover to use (LeanCopilot vs DeepSeek-Prover-V1.5)?
- **Decision**: Prefer LeanCopilot if API available (used in baseline)
- **Fallback**: DeepSeek-Prover-V1.5 (well-documented, miniF2F results published)

**Q2**: Tactic extraction method (AST parsing vs script counting)?
- **Decision**: Attempt Lean 4 metaprogramming first
- **Fallback**: Proof script line counting with validation

**Q3**: Should we analyze depth distribution of lean-auto proofs (confound control)?
- **Decision**: Yes, if H-E1 data available
- **Action**: Check verification_state for H-E1 proof logs

**Q4**: What if Δ is near boundary (e.g., Δ = 4.8%)?
- **Decision**: Report as borderline, widen CI via more bootstrap samples
- **Reflection**: Discuss uncertainty in Phase 4.5 synthesis

---

**PRD Approved**: Ready for architecture design (Step 03)
