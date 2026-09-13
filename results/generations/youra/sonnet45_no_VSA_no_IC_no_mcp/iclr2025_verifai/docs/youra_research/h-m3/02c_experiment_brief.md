# Experiment Brief: Invalid Beam Pruning (h-m3)

**Date:** 2026-08-25  
**Hypothesis ID:** h-m3  
**Type:** MECHANISM  
**Gate:** SHOULD_WORK  
**Prerequisites:** h-m2 (VALIDATED)

---

## 1. Hypothesis Statement

**h-m3:** Invalid beams (validity_score=0) receive lower final scores and are pruned over time in favor of valid beams (validity_score=1).

**Rationale:** Tests pruning mechanism. If invalid beams persist despite lower scores, beam search won't converge to valid outputs.

---

## 2. Variables

### 2.1 Independent Variables
- **IV1:** Beam pruning strategy (keep top-k by score)
  - Implementation: Standard beam search top-k selection at each step
  - k=5 (validated in h-m1)

### 2.2 Dependent Variables
- **DV1:** Proportion of invalid beams in top-k over time
  - Measurement: Track valid/invalid status of beams at each generation step
  - Target: ≥50% reduction from start to end of generation
  
- **DV2:** Final beam validity
  - Measurement: Proportion of valid beams in final k=5 beams
  - Target: ≥60% (at least 3 out of 5 beams valid)

### 2.3 Control Variables
- **CV1:** Model = CodeLlama-7B (meta-llama/CodeLlama-7b-hf)
- **CV2:** Dataset = HumanEval-164 (standard benchmark)
- **CV3:** Beam width k = 5 (validated in h-m1)
- **CV4:** Scoring weights = α=0.7, β=0.3 (validated in h-m2)
- **CV5:** Generation strategy = Beam search with combined scoring

---

## 3. Dataset Preparation

### 3.1 Primary Dataset
**Name:** HumanEval-164  
**Type:** standard (real established dataset)  
**Source:** https://github.com/openai/human-eval  
**Size:** 164 hand-written Python programming problems  
**Split:** Full test set (no train/val split; code generation benchmark)

**Rationale:**
- Same dataset as h-m1 and h-m2 (enables direct comparison)
- Real-world benchmark with established metrics
- Syntax error rate 64-68% well-documented from h-m1 analysis
- Sufficient sample size for statistical validity (>50 samples)

**Cache Path:** Will be set during data preparation phase  
**Verification:** SHA256 checksum against official HumanEval release

---

## 4. Model Configuration

**Model:** CodeLlama-7B  
**Pretrained ID:** meta-llama/CodeLlama-7b-hf  
**Framework:** HuggingFace Transformers  
**Hardware:** GPU (CUDA)

**Generation Config:**
- max_new_tokens: 512 (sufficient for HumanEval solutions)
- temperature: 0.8 (standard for code generation)
- num_beams: 5 (validated in h-m1)
- num_return_sequences: 5 (return all k beams for analysis)

**Scoring Config:**
- α (log-likelihood weight): 0.7 (from h-m2)
- β (validity weight): 0.3 (from h-m2)
- scoring_function: `α * log_likelihood + β * syntax_validity_score`

**Cache Path:** Will be set during environment setup

---

## 5. Experiments

### 5.1 Experiment A: Invalid Beam Proportion Tracking

**Objective:** Measure proportion of invalid beams in top-k over time to validate pruning mechanism

**Protocol:**
1. Implement beam validity tracker:
   - At each generation step (t=0 to T):
     - For each beam in top-k:
       - Validate syntax with `ast.parse(beam_code)`
       - Record validity_score (1 if valid, 0 if invalid)
     - Compute invalid_proportion = count(validity_score=0) / k
     - Log: step_id, invalid_proportion
2. Run beam search on full HumanEval-164
3. For each problem:
   - Track invalid_proportion at initial step (t=0)
   - Track invalid_proportion at final step (t=T)
   - Compute reduction: (initial - final) / initial × 100%
4. Aggregate statistics across all 164 problems

**Metrics:**
- Initial invalid proportion (mean, median across problems)
- Final invalid proportion (mean, median across problems)
- Reduction rate: (initial - final) / initial × 100%
- Proportion of problems where invalid beams reduced by ≥50%

**Success Criteria:**
- Mean reduction rate ≥50%
- Median reduction rate ≥50%
- At least 60% of problems show ≥50% reduction

**Expected Compute:**
- ~164 problems × ~30 generation steps = ~4,920 tracking measurements
- Estimated time: ~10-15 minutes total runtime (same generation as h-m2, only adds tracking)

---

### 5.2 Experiment B: Final Beam Validity Distribution

**Objective:** Verify final k=5 beams have high valid proportion (≥60%)

**Protocol:**
1. After beam search completes for each problem:
   - Parse final k=5 beams with `ast.parse()`
   - Count valid beams (validity_score=1)
   - Compute valid_proportion = count(valid) / k
   - Record per problem
2. Aggregate across all 164 problems

**Metrics:**
- Mean final valid proportion
- Median final valid proportion
- Distribution: proportion of problems with 0, 1, 2, 3, 4, 5 valid beams
- Proportion of problems with ≥60% valid beams (≥3 out of 5)

**Success Criteria:**
- Mean final valid proportion ≥60%
- At least 70% of problems have ≥3 valid beams in final output

**Expected Compute:**
- Same run as Experiment A (no additional computation)
- Analysis time: ~5 minutes

---

### 5.3 Experiment C: Temporal Pruning Dynamics

**Objective:** Analyze how invalid beams are pruned over time (early vs late generation)

**Protocol:**
1. Divide generation timeline into 3 phases:
   - Early: steps 0-33% of total
   - Middle: steps 33%-66% of total
   - Late: steps 66%-100% of total
2. For each phase:
   - Compute mean invalid proportion
   - Track beam turnover (how many beams replaced at each step)
3. Analyze pruning pattern:
   - Does invalid proportion decrease monotonically?
   - When does most pruning happen (early/middle/late)?

**Metrics:**
- Invalid proportion per phase (early, middle, late)
- Beam turnover rate per phase
- Monotonicity score: proportion of problems where invalid proportion decreases monotonically

**Success Criteria:**
- Invalid proportion decreases from early to late (late < early)
- Mean pruning concentrated in early-middle phases (confirms mechanism working)

**Expected Compute:**
- Same run as Experiment A (analysis only)
- Analysis time: ~10 minutes

---

### 5.4 Baseline Comparison

**Baseline Methods:**
1. **Pure Log-Likelihood Beam Search (from h-m2):**
   - α=1.0, β=0.0 (no validity scoring)
   - Expected: Invalid beams NOT pruned (no validity signal)
   
2. **Greedy Sampling (from h-m1):**
   - No beam exploration, single output
   - Syntax error rate: 64-68%

**Comparison Protocol:**
1. Run pure log-likelihood beam search (α=1.0, β=0.0) on same HumanEval-164
2. Track invalid proportion over time (same as Experiment A)
3. Compare:
   - Pure beam search: invalid proportion likely stays high or random
   - Combined scoring: invalid proportion should decrease (h-m3 prediction)

**Expected Result:**
- Pure beam search: No systematic pruning (invalid proportion fluctuates randomly)
- Combined scoring: Systematic pruning (invalid proportion decreases over time)

---

## 6. Implementation Requirements

### 6.1 Code Components

**Required Modules:**
1. **Beam Validity Tracker:**
   ```python
   class BeamValidityTracker:
       def __init__(self):
           self.step_logs = []
       
       def track_step(self, step_id, beams):
           validities = [validate_syntax(beam)[0] for beam in beams]
           invalid_count = sum(1 for v in validities if not v)
           invalid_proportion = invalid_count / len(beams)
           self.step_logs.append({
               'step_id': step_id,
               'invalid_proportion': invalid_proportion,
               'validities': validities
           })
       
       def compute_reduction(self):
           if not self.step_logs:
               return None
           initial = self.step_logs[0]['invalid_proportion']
           final = self.step_logs[-1]['invalid_proportion']
           reduction = (initial - final) / initial if initial > 0 else 0
           return reduction
   ```

2. **Beam Search with Tracking:**
   - Extend h-m2 beam search implementation
   - Add BeamValidityTracker at each step
   - Log beam states before and after pruning

3. **AST Validation (reuse from h-m2):**
   ```python
   import ast
   
   def validate_syntax(code_snippet):
       try:
           ast.parse(code_snippet)
           return True, 1  # valid, validity_score=1
       except SyntaxError:
           return False, 0  # invalid, validity_score=0
   ```

4. **Logging Infrastructure:**
   - Log per-step beam validity states
   - Store: step_id, beam_id, validity_score, invalid_proportion
   - Save to structured format (JSON or CSV)

### 6.2 Dependencies
- transformers (HuggingFace)
- torch (PyTorch backend)
- ast (Python standard library)
- datasets (for HumanEval loading)
- numpy, pandas (for analysis)
- matplotlib, seaborn (for visualization)

### 6.3 Hardware Requirements
- GPU: NVIDIA GPU with ≥16GB VRAM (for CodeLlama-7B)
- Estimated runtime: <20 minutes total (all experiments)

---

## 7. Success Criteria Summary

| Criterion | Metric | Target | Gate Action if Failed |
|-----------|--------|--------|----------------------|
| **Primary:** Invalid beam reduction | Mean reduction rate | ≥50% | PIVOT (increase β weight or adjust pruning threshold) |
| **Primary:** Final beam validity | Valid proportion | ≥60% (≥3/5 beams) | PIVOT (increase β to 0.4 or 0.5) |
| **Secondary:** Temporal dynamics | Pruning pattern | Invalid proportion decreases monotonically | EXPLORE (analyze why pruning delayed) |
| **Secondary:** Baseline comparison | vs pure beam search | Combined scoring shows pruning | PIVOT (scoring mechanism broken) |

**Gate Type:** SHOULD_WORK
- **If Primary Criteria Fail:** PIVOT (increase β weight from 0.3 to 0.4 or 0.5)
- **If Secondary Criteria Fail:** Continue with caveats (pruning works but pattern unexpected)

---

## 8. Data Analysis Plan

### 8.1 Reduction Rate Analysis
- Compute reduction statistics (mean, median, p25, p75)
- Plot histogram of reduction rates across 164 problems
- Identify problems with no reduction or negative reduction
- **Decision:** If mean <50%, analyze failure cases (when do invalid beams persist?)

### 8.2 Final Validity Analysis
- Compute valid proportion statistics
- Plot distribution of valid beam counts (0-5)
- Stratify by problem difficulty (if metadata available)
- **Decision:** If valid proportion <60%, test higher β weights

### 8.3 Temporal Dynamics Analysis
- Plot mean invalid proportion over generation steps (averaged across problems)
- Compute phase-wise statistics (early/middle/late)
- Identify monotonicity violations
- **Decision:** If non-monotonic, investigate scoring formula or beam diversity issues

### 8.4 Baseline Comparison
- Plot invalid proportion over time: pure beam search vs combined scoring
- Statistical test: Are temporal patterns different? (qualitative visual inspection sufficient for PoC)
- **Decision:** If no difference, combined scoring doesn't enable pruning → mechanism fails

---

## 9. Risk Mitigation

### 9.1 Risk: Invalid Beams Persist
**Symptom:** Reduction rate <50% or final validity <60%
**Diagnosis:**
- Check if β=0.3 is too low (validity signal drowned by log-likelihood)
- Verify scoring function implementation (are invalid beams actually getting lower scores?)
**Mitigation:**
- Increase β weight (test β=0.4, 0.5 in ablation)
- Verify beam selection logic (ensure pruning by score, not random)

### 9.2 Risk: No Pruning Observed
**Symptom:** Invalid proportion stays constant or increases
**Diagnosis:**
- Beam search may be broken (not selecting by score)
- Scoring formula may be incorrect (all beams get same score)
**Mitigation:**
- Add detailed logging of beam scores and selection process
- Verify implementation against h-m2 validated scoring function
- Test on small subset (5 problems) with verbose debugging

### 9.3 Risk: Pruning Delayed (Late-Phase Only)
**Symptom:** Invalid proportion stays high until final steps, then drops suddenly
**Diagnosis:**
- Beam diversity may be low early on (all beams similar)
- Validity signal may only matter once generation completes
**Mitigation:**
- Analyze beam diversity at each step
- Consider early-phase validity boost (higher β in early steps, lower in late)
- Document as limitation if cannot fix

---

## 10. Deliverables

### 10.1 Code Artifacts
1. `beam_validity_tracker.py` - BeamValidityTracker class
2. `beam_search_with_tracking.py` - Extended beam search with validity tracking
3. `run_experiment_a.py` - Invalid beam proportion tracking
4. `run_experiment_b.py` - Final beam validity measurement
5. `run_experiment_c.py` - Temporal dynamics analysis
6. `run_baseline_comparison.py` - Pure beam search vs combined scoring
7. `analysis_notebooks/` - Jupyter notebooks for data analysis

### 10.2 Data Artifacts
1. `results/beam_validity_logs.csv` - Per-step beam validity states
2. `results/reduction_rates.json` - Per-problem reduction statistics
3. `results/final_validity.json` - Final beam validity distribution
4. `results/temporal_dynamics.json` - Phase-wise invalid proportions
5. `results/baseline_comparison.json` - Pure vs combined scoring

### 10.3 Visualizations
1. `figures/reduction_histogram.png` - Distribution of reduction rates
2. `figures/temporal_pruning.png` - Invalid proportion over time (mean across problems)
3. `figures/final_validity_dist.png` - Distribution of valid beam counts
4. `figures/baseline_comparison.png` - Pure beam search vs combined scoring over time

### 10.4 Documentation
1. `04_validation.md` - Hypothesis validation report (generated in Phase 4)
2. `experiment_logs.txt` - Runtime logs and debug output

---

## 11. Timeline Estimate

| Phase | Duration | Notes |
|-------|----------|-------|
| **Data Preparation** | 10 minutes | Reuse h-m2 dataset cache |
| **Environment Setup** | 10 minutes | Reuse h-m2 environment |
| **Implementation** | 3-4 hours | Extend h-m2 beam search with tracking |
| **Experiment A (Tracking)** | 15 minutes | Run full HumanEval-164 with tracking |
| **Experiment B (Final Validity)** | 0 minutes | Same run as A |
| **Experiment C (Temporal)** | 0 minutes | Analysis only |
| **Baseline Comparison** | 15 minutes | Pure log-likelihood beam search |
| **Analysis** | 2-3 hours | Generate plots, compute statistics, write validation report |

**Total Estimated Time:** 6-8 hours

---

## 12. Expected Outcomes

### 12.1 If Hypothesis Passes
- Invalid beam proportion reduces by ≥50% on average
- Final beams have ≥60% valid proportion
- Pruning pattern shows monotonic decrease (validates mechanism)
- **Next Step:** Proceed to h-m4 (Final Valid Output Selection)

### 12.2 If Hypothesis Fails (No Pruning)
- Invalid proportion stays high or fluctuates randomly
- **Pivot:** Increase β weight to 0.4 or 0.5
- **Re-run:** Experiment A with higher β
- **Gate Decision:** If still no pruning, scoring mechanism insufficient → ABANDON

### 12.3 If Hypothesis Fails (Insufficient Validity)
- Pruning happens but final validity <60%
- **Pivot:** Increase β weight or adjust beam width (test k=3 for higher validity concentration)
- **Explore:** Early-phase validity boosting (dynamic β schedule)
- **Gate Decision:** If all pivots fail, mechanism doesn't converge to valid outputs → ABANDON

### 12.4 If Hypothesis Fails (Same as Pure Beam Search)
- No difference between combined scoring and pure log-likelihood
- **Analysis:** Validity scoring component β=0.3 too weak to influence pruning
- **Gate Decision:** Increase β significantly (0.5+) or ABANDON if validity signal irrelevant

---

## 13. Connection to Verification Plan

**From 02b_verification_plan.md:**
- **Section 2.2 (H-M3 Specification):** This experiment brief implements the verification protocol
- **Section 3.3 (Gate Summary):** SHOULD_WORK gate with PIVOT on failure
- **Section 4.1 (Risk Mapping):** Addresses R3 (α/β suboptimal) and R6 (beam diversity)

**Alignment:**
- All success criteria from verification plan preserved
- PoC direction-based approach (no statistical significance testing)
- Gate-based progression: PIVOT on pruning failure, ABANDON if mechanism broken

---

## 14. Notes

**Experiment Design Level:** 1.5 (detailed specification ready for implementation planning)

**Synthetic Data:** NOT USED (HumanEval-164 is a real standard benchmark)

**Sample Size:** 164 problems (full test set, statistically meaningful)

**Compute Budget:** <30 minutes total runtime (well within feasibility)

**Dependencies on h-m2:** 
- Builds on validated combined scoring (α=0.7, β=0.3)
- Reuses beam search infrastructure with AST validation
- Extends h-m2 by tracking beam validity over time

**Dependencies on h-m1:**
- Uses validated beam width k=5
- Same dataset and model for direct comparison

**Open Questions:**
- Is β=0.3 strong enough for effective pruning? (Will test in Experiment A)
- Does pruning happen early or late in generation? (Experiment C will answer)
- Can we detect pruning failure early (5 problems) or need full 164? (Run full set for robustness)

**Key Difference from h-m2:**
- h-m2 validated scoring MECHANISM (valid beams score higher)
- h-m3 validates pruning OUTCOME (invalid beams actually removed over time)
- h-m2 is STATIC (score at single step), h-m3 is DYNAMIC (tracking over time)

---

**Generated:** 2026-08-25  
**Workflow:** Phase 2C Experiment Design (Ablation Mode - No MCP)  
**Schema Version:** 3.5
