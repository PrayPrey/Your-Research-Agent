# Phase 2C: Experiment Design Brief
# H-M2: Proof Depth Filtering

**Generated**: 2026-08-20  
**Hypothesis ID**: h-m2  
**Experiment Type**: Post-hoc Analysis (MECHANISM)  
**Gate**: SHOULD_WORK  
**Complexity**: Level 1 (Post-processing Analysis)

---

## 1. Hypothesis Statement

**H-M2**: Proof depth filtering (≤3 tactics) drops LLM success by 10-20 percentage points (tests 30% contribution claim)

**Predicted Effect**:
- Full proofs (all depths): 65%
- Shallow only (≤3 tactics): 50%
- Delta: 15 percentage points

**Falsification Criteria**: 
- IF Δ < 5%: Reject (depth contributes <8% of gap)
- IF Δ > 30%: Reject (depth explains >60% of gap, contradicts NL dominance)

---

## 2. Research Foundation

### 2.1 Archon KB Evidence

No direct proof depth filtering experiments found. Related automated proving work focuses on depth limits for search (dmax=8 common in miniF2F baselines), not post-hoc filtering by proof complexity.

### 2.2 Implementation Evidence (Exa)

**Key Finding**: miniF2F proof length distribution bounded:
- Median: 9 tactic invocations
- 96th percentile: 22 tactics
- Maximum: 40 tactics
- Source: Analysis of 1,840 machine-found Lean proofs

**Relevant Infrastructure**:
- Lean 4 proof term tactic extraction (proof terms → tactic count)
- miniF2F benchmark (244 Lean 4 theorems)
- DeepSeek-Prover-V1.5 (k=16, 1024 tokens, 60s timeout)
- Standard evaluation: pass@k metric on full miniF2F-test

**Depth Stratification Strategy**:
- ≤3 tactics: Shallow (single-step or 2-3 step proofs)
- 4-10 tactics: Medium
- >10 tactics: Deep

---

## 3. Experiment Specification

### 3.1 Dataset

**Primary Dataset**: miniF2F Lean 4 (google-deepmind/miniF2F fork)
- **Type**: standard
- **Size**: 244 theorems (full test split)
- **Source**: https://github.com/google-deepmind/miniF2F
- **Justification**: Standard benchmark, AlphaProof evaluation set, corrected formalizations

**Data Splits**:
- N/A (post-hoc analysis on completed proof runs, not train/val/test)

**Preprocessing**:
1. Run LLM prover (LeanCopilot or equivalent) on full miniF2F-test
2. Extract tactic count from successful proof terms
3. Classify proofs by depth: shallow (≤3), medium (4-10), deep (>10)
4. Compute success rates stratified by allowed depth categories

---

### 3.2 Baseline Comparison

**Primary Comparison**:
- **Full proofs** (all depths allowed): Baseline LLM success rate
- **Shallow-only** (≤3 tactics): Filtered success rate
- **Delta**: Measures depth contribution to LLM advantage

**Control Analysis**:
- Compare depth distribution: LLM proofs vs lean-auto proofs (from H-E1)
- If lean-auto also skews shallow, depth filtering affects both equally (confound)

---

### 3.3 Evaluation Protocol

**Proof Collection Phase**:
1. Run LLM prover on miniF2F-test (244 theorems)
   - Config: pass@16, 1024 tokens, 60s timeout per attempt
   - Log: successful proofs with full proof terms
2. Extract tactic count from each successful proof term
   - Method: Parse Lean 4 proof term, count tactic invocations
   - Fallback: Count proof script lines (if term parsing unavailable)

**Filtering Phase**:
1. Classify each problem by minimum proof depth found:
   - If ANY solution ≤3 tactics exists → "shallow-solvable"
   - Else → "deep-only"
2. Compute filtered success rate:
   - Success_shallow = (problems with ≤3 tactic solution) / 244
   - Success_full = (all solved problems) / 244
   - Delta = Success_full - Success_shallow

**Metrics**:
- **Primary**: Δ success rate (percentage points)
- **Secondary**: 
  - Depth distribution histogram (solved problems)
  - Correlation: problem difficulty × proof depth
  - Proportion of problems requiring >3 tactics

**Statistical Validation**:
- McNemar's test (paired comparison: full vs shallow)
- Bootstrap 95% CI for Δ estimate
- Minimum N=30 solved problems for reliable statistics

---

### 3.4 Implementation Requirements

**Infrastructure** (Level 1 - Simple):
1. **Proof Runner**:
   - LLM prover integration (LeanCopilot API or DeepSeek-Prover-V1.5)
   - miniF2F-test benchmark loader
   - Proof logging (store successful proof terms)

2. **Tactic Extractor**:
   - Lean 4 metaprogramming: proof term → tactic list
   - Fallback: regex-based proof script line counting
   - Output: CSV mapping (theorem_name, tactic_count)

3. **Stratification Analyzer**:
   - Python script: read tactic counts → compute stratified success rates
   - Statistical tests: McNemar, bootstrap CI
   - Visualization: depth distribution histograms

**Dependencies**:
- Lean 4.14+ (Mathlib compatible)
- LeanCopilot or DeepSeek-Prover-V1.5 API access
- Python 3.10+ (pandas, scipy, matplotlib)

**Estimated Runtime**:
- Proof collection: 4-6 hours (244 theorems × 16 attempts × 60s timeout)
- Tactic extraction: <10 minutes (post-processing)
- Analysis: <5 minutes

---

## 4. Risk Analysis

### 4.1 Technical Risks

**R1: Proof Term Tactic Extraction Failure** (LOW)
- **Scenario**: Lean 4 proof terms too complex for reliable tactic counting
- **Probability**: 20%
- **Mitigation**: Fallback to proof script line counting (proxy metric)
- **Impact**: Medium (reduces precision, but direction still valid)

**R2: Insufficient Solved Problems** (MEDIUM)
- **Scenario**: LLM solves <30 problems → underpowered statistics
- **Probability**: 30% (depends on LLM baseline performance)
- **Mitigation**: Use MUST_WORK hypothesis H-E1 or H-M1 proof logs (≥50 expected)
- **Impact**: High (blocks statistical validation)

**R3: Depth Distribution Too Homogeneous** (LOW)
- **Scenario**: >95% proofs are shallow OR >95% are deep
- **Probability**: 15% (empirical data shows median=9, suggesting spread)
- **Mitigation**: Report as null result (depth not discriminative)
- **Impact**: Medium (hypothesis rejected, but informative)

### 4.2 Validity Threats

**Confound 1: Difficulty Correlation**
- **Threat**: Shallow-solvable problems are inherently easier
- **Test**: Compare lean-auto success on shallow vs deep categories
- **Mitigation**: If lean-auto also shows gap, stratify by baseline difficulty

**Confound 2: Proof Search Bias**
- **Threat**: LLM search prefers shallow proofs (not capability difference)
- **Test**: Check if multiple proof depths exist for same problem
- **Mitigation**: Report as limitation (post-hoc filtering ≠ controlled ablation)

---

## 5. Success Criteria

### 5.1 Gate Satisfaction (SHOULD_WORK)

**Pass**: 5% < Δ < 30%
- Confirms depth contributes 8-60% of LLM advantage
- Supports 30% mechanistic claim (within uncertainty)

**Fail**: Δ < 5% OR Δ > 30%
- Reject 30% contribution claim
- Route to reflection: revise mechanistic attribution

### 5.2 Deliverables

1. **Tactic depth dataset**: CSV with (theorem, tactic_count, success)
2. **Stratified success table**: Full vs shallow success rates
3. **Statistical report**: McNemar p-value, bootstrap CI, effect size
4. **Depth distribution plots**: Histogram of tactic counts (solved problems)

---

## 6. Timeline & Resources

**Phase Duration**: 2 days

| Task | Duration | Dependencies |
|------|----------|--------------|
| Infrastructure setup | 4 hours | LeanCopilot API, miniF2F repo |
| Proof collection run | 6 hours | LLM API access, compute |
| Tactic extraction | 2 hours | Lean 4 metaprogramming |
| Statistical analysis | 3 hours | Python scripts |
| Report generation | 1 hour | Results interpretation |

**Compute Requirements**:
- 1 GPU (LLM inference, if local)
- 8 GB RAM (Lean verification)
- API credits (if using DeepSeek-Prover cloud)

**Blocking Dependencies**: None (post-hoc analysis, independent)

---

## 7. Pilot Study (Optional)

**Scope**: N=20 miniF2F problems
**Goal**: Validate tactic extraction pipeline
**Success**: ≥80% accurate tactic counts (manual verification)
**Duration**: 2 hours

**Decision Point**:
- If extraction works → proceed to full experiment
- If extraction fails → pivot to proof script line counting

---

## 8. Fallback Plan

**If LLM proof collection fails** (e.g., API unavailable):
- Use public proof logs from prior work:
  - DeepSeek-Prover-V1.5 paper results
  - miniF2F leaderboard submissions
- Limitation: Unknown tactic counts → BLOCK experiment

**If tactic extraction fails**:
- Use proof script length (lines) as proxy
- Report correlation: script length ≈ tactic depth (empirical validation)

---

## 9. Expected Outcomes

### 9.1 Hypothesis Confirmation (Δ = 15%)

**Interpretation**: 
- Depth filtering removes ~30% of LLM advantage (50 → 65% gap)
- Supports long-range proof search mechanism
- Complements NL ablation (H-M1) and corpus control (H-M3)

**Next Steps**:
- Combine with H-M1, H-M3 results for additive attribution
- Report in Phase 6 paper as mechanistic evidence

### 9.2 Hypothesis Rejection (Δ < 5%)

**Interpretation**:
- Depth does NOT explain LLM advantage
- Revise mechanistic model (NL + corpus only)
- Depth may be consequence, not cause (easier problems = shorter proofs)

**Next Steps**:
- Reflection task: update attribution percentages
- Rerun Phase 2B with revised mechanisms

### 9.3 Unexpected High Effect (Δ > 30%)

**Interpretation**:
- Depth explains >60% of gap (contradicts NL=60% claim)
- Mechanistic model invalid (mechanisms not independent)
- Possible interaction: NL helps find SHALLOW proofs specifically

**Next Steps**:
- Reframe as interaction hypothesis
- Cross-tabulate: NL presence × proof depth

---

## 10. Alignment with Main Hypothesis

**Main Hypothesis Attribution**:
- NL understanding: 60% (tested by H-M1)
- Proof depth: 30% (tested by H-M2)
- Corpus patterns: 10% (tested by H-M3)

**H-M2 Validation Strategy**:
- Measures Δ for depth-filtered LLM vs full LLM
- Expected Δ ≈ 15 percentage points (30% of 50-point gap)
- Falsification bounds: [5%, 30%] (prevents overclaiming)

**Integration**:
- H-M2 runs independently (no H-E1 dependency)
- Results combine with H-M1, H-M3 for triangulated attribution
- Phase 5 validates additive model: NL + depth + corpus ≈ total gap

---

## 11. Open Questions

1. **Multiple proof depths**: Can same problem be solved with both shallow and deep proofs?
   - If yes: LLM preference for shallow is search strategy, not capability
   - If no: Depth is problem property, not prover property

2. **Lean-auto depth distribution**: Do hammer proofs also skew shallow?
   - If yes: Depth filtering affects both → not LLM-specific
   - If no: LLM exploits shallow proof paths uniquely

3. **Difficulty confound**: Are shallow-solvable problems easier?
   - Test: Compare lean-auto success on shallow vs deep strata
   - Control: Stratify by baseline difficulty before depth filtering

---

## 12. References

**Empirical Evidence**:
- miniF2F proof length distribution (median=9, max=40)
- https://www.sed-contra.com/claim/1db2c924-bc2a-478c-a687-966aa41366c0/

**Benchmark**:
- miniF2F Lean 4 (google-deepmind/miniF2F)
- https://github.com/google-deepmind/miniF2F

**Prover Baselines**:
- DeepSeek-Prover-V1.5 (pass@16, structured hints paper)
- LeanCopilot (LLM-guided proving)

**Statistical Methods**:
- McNemar's test (paired proportions)
- Bootstrap confidence intervals (effect size)

---

**Phase 2C Complete for H-M2**  
**Next Phase**: Phase 3 Implementation Planning (PRD/Architecture generation)
