# Experiment Brief: Final Valid Output Selection (h-m4)

**Date:** 2026-08-25  
**Hypothesis ID:** h-m4  
**Type:** MECHANISM  
**Gate:** SHOULD_WORK  
**Prerequisites:** h-m3 (VALIDATED)

---

## 1. Hypothesis Statement

**h-m4:** Final selected code is from top-scoring beam which has been incrementally validated for syntax correctness throughout generation process.

**Rationale:** Tests final output quality. If top beam is still invalid after pruning process, mechanism failed.

---

## 2. Variables

### 2.1 Independent Variables
- **IV1:** Final beam selection strategy (argmax score)
  - Implementation: Select beam with highest final_score from k=5 candidates
  - Uses combined scoring from h-m2/h-m3: `final_score = α * log_likelihood + β * validity_score`

### 2.2 Dependent Variables
- **DV1:** Syntax validity of selected output
  - Measurement: AST parse success of final selected beam
  - Target: ≥60% syntax validity rate (at least 3 out of 5 problems valid)
  
- **DV2:** Syntax error rate vs greedy baseline
  - Measurement: Comparison of syntax error rate between beam search and greedy sampling
  - Target: Syntax error rate < greedy baseline (directional improvement)

### 2.3 Control Variables
- **CV1:** Model = CodeLlama-7B (meta-llama/CodeLlama-7b-hf)
- **CV2:** Dataset = HumanEval-164 (standard benchmark)
- **CV3:** Beam width k = 5 (validated in h-m1/h-m2/h-m3)
- **CV4:** Scoring weights = α=0.7, β=0.3 (validated in h-m2/h-m3)
- **CV5:** Generation strategy = Beam search with combined scoring + pruning

---

## 3. Dataset Preparation

### 3.1 Primary Dataset
**Name:** HumanEval-164  
**Type:** standard (real established dataset)  
**Source:** https://github.com/openai/human-eval  
**Size:** 164 hand-written Python programming problems  
**Split:** Full test set (no train/val split; code generation benchmark)

**Rationale:**
- Same dataset as h-m1/h-m2/h-m3 (enables end-to-end pipeline validation)
- Real-world benchmark with established metrics
- Greedy baseline syntax error rate 64-68% documented from h-m1 analysis
- Full test set provides statistically meaningful sample size

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
- num_return_sequences: 5 (return all k beams for comparison)

**Scoring Config:**
- α (log-likelihood weight): 0.7 (from h-m2)
- β (validity weight): 0.3 (from h-m2)
- scoring_function: `α * log_likelihood + β * syntax_validity_score`
- selection: argmax(final_score) over k=5 beams

**Cache Path:** Will be set during environment setup

---

## 5. Experiments

### 5.1 Experiment A: Final Output Validity

**Objective:** Measure syntax validity of final selected outputs from validity-scored beam search

**Protocol:**
1. Run beam search (k=5, α=0.7, β=0.3) on HumanEval-164
2. For each problem:
   - Generate k=5 beams with combined scoring
   - Compute final_score for each beam
   - Select final output: beam with highest final_score
   - Validate syntax: `ast.parse(selected_output)`
   - Record: problem_id, selected_beam_id, validity (True/False)
3. Aggregate across all 164 problems

**Metrics:**
- Syntax validity rate: (valid outputs / total outputs) × 100%
- Syntax error rate: (invalid outputs / total outputs) × 100%
- Distribution: count of valid vs invalid final outputs

**Success Criteria:**
- Syntax validity rate ≥60% (at least 98 out of 164 problems)
- Syntax error rate ≤40% (target from main hypothesis)

**Expected Compute:**
- ~10-15 minutes for full HumanEval-164 generation + selection

---

### 5.2 Experiment B: Baseline Comparison (Greedy Sampling)

**Objective:** Compare final output syntax error rate between validity-scored beam search and greedy sampling baseline

**Protocol:**
1. Run greedy sampling on same HumanEval-164
   - temperature: 0.8
   - num_beams: 1 (greedy decoding)
   - max_new_tokens: 512
2. For each problem:
   - Generate single greedy output
   - Validate syntax: `ast.parse(greedy_output)`
   - Record: problem_id, validity (True/False)
3. Compare with Experiment A results:
   - Greedy syntax error rate
   - Beam search syntax error rate
   - Absolute reduction: greedy_error_rate - beam_error_rate
   - Relative reduction: (greedy_error_rate - beam_error_rate) / greedy_error_rate × 100%

**Metrics:**
- Greedy baseline syntax error rate (expected: 64-68% from h-m1)
- Beam search syntax error rate (target: ≤40%)
- Error rate reduction (absolute and relative)

**Success Criteria:**
- Beam search syntax error rate < greedy baseline (directional improvement)
- Relative reduction ≥40% (target from main hypothesis: 64-68% → ≤40%)

**Expected Compute:**
- ~5-10 minutes for greedy sampling (faster than beam search)

---

### 5.3 Experiment C: Selection Quality Analysis

**Objective:** Verify that argmax selection actually picks valid beams when available

**Protocol:**
1. For each problem where k=5 beams available:
   - Count total valid beams in final k=5
   - Check if selected beam (argmax score) is valid
   - Compute selection accuracy: proportion of problems where valid beam selected
2. Stratify by availability:
   - Problems with ≥3 valid beams (from h-m3: 80% of problems)
   - Problems with 1-2 valid beams
   - Problems with 0 valid beams

**Metrics:**
- Selection accuracy when ≥1 valid beam available
- Selection accuracy when ≥3 valid beams available
- Miss rate: proportion of problems where valid beam exists but invalid selected

**Success Criteria:**
- When ≥3 valid beams available, selection accuracy ≥90%
- When ≥1 valid beam available, selection accuracy ≥70%

**Expected Result:**
- If h-m3 pruning worked (73% final validity), and scoring ranks valid beams higher, argmax should select valid outputs most of the time
- If selection accuracy low despite high beam validity, scoring mechanism may be broken

**Expected Compute:**
- Same run as Experiment A (analysis only)
- Analysis time: ~5 minutes

---

### 5.4 Ablation: Selection Strategy Comparison

**Objective:** Test whether argmax is optimal selection strategy or if alternatives perform better

**Protocol:**
1. From same k=5 beams generated in Experiment A, test alternative selection strategies:
   - **Strategy 1 (Current):** argmax(final_score) - pick highest combined score
   - **Strategy 2:** argmax(validity_score) then argmax(log_likelihood) - prefer any valid beam, tie-break by likelihood
   - **Strategy 3:** Random valid beam - if ≥1 valid exists, pick randomly from valid set
2. For each strategy:
   - Compute syntax validity rate
   - Compare against Strategy 1 baseline

**Metrics:**
- Syntax validity rate per strategy
- Best performing strategy

**Success Criteria:**
- argmax(final_score) should perform best (validates combined scoring design)
- If Strategy 2 better, indicates β=0.3 may be too low

**Expected Compute:**
- Same run as Experiment A (analysis only)
- Analysis time: ~10 minutes

---

## 6. Implementation Requirements

### 6.1 Code Components

**Required Modules:**
1. **Final Output Selector:**
   ```python
   class FinalOutputSelector:
       def __init__(self, alpha=0.7, beta=0.3):
           self.alpha = alpha
           self.beta = beta
       
       def select_final_output(self, beams, log_likelihoods):
           """Select best beam using combined scoring."""
           final_scores = []
           for beam, log_likelihood in zip(beams, log_likelihoods):
               validity_score = validate_syntax(beam)[1]  # 1 if valid, 0 if invalid
               final_score = self.alpha * log_likelihood + self.beta * validity_score
               final_scores.append(final_score)
           
           best_idx = np.argmax(final_scores)
           return beams[best_idx], best_idx, final_scores
   ```

2. **Baseline Greedy Sampler:**
   ```python
   def run_greedy_baseline(model, tokenizer, prompts):
       """Run greedy sampling baseline."""
       outputs = []
       for prompt in prompts:
           inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
           generated = model.generate(
               **inputs,
               max_new_tokens=512,
               temperature=0.8,
               num_beams=1,
               do_sample=False
           )
           output = tokenizer.decode(generated[0], skip_special_tokens=True)
           outputs.append(output)
       return outputs
   ```

3. **AST Validation (reuse from h-m2/h-m3):**
   ```python
   import ast
   
   def validate_syntax(code_snippet):
       try:
           ast.parse(code_snippet)
           return True, 1  # valid, validity_score=1
       except SyntaxError:
           return False, 0  # invalid, validity_score=0
   ```

4. **Comparison Analysis:**
   ```python
   def compute_error_reduction(greedy_results, beam_results):
       """Compare greedy vs beam search syntax error rates."""
       greedy_errors = sum(1 for valid, _ in greedy_results if not valid)
       beam_errors = sum(1 for valid, _ in beam_results if not valid)
       
       greedy_error_rate = greedy_errors / len(greedy_results)
       beam_error_rate = beam_errors / len(beam_results)
       
       absolute_reduction = greedy_error_rate - beam_error_rate
       relative_reduction = (absolute_reduction / greedy_error_rate) * 100 if greedy_error_rate > 0 else 0
       
       return {
           'greedy_error_rate': greedy_error_rate,
           'beam_error_rate': beam_error_rate,
           'absolute_reduction': absolute_reduction,
           'relative_reduction': relative_reduction
       }
   ```

### 6.2 Dependencies
- transformers (HuggingFace)
- torch (PyTorch backend)
- ast (Python standard library)
- datasets (for HumanEval loading)
- numpy, pandas (for analysis)
- matplotlib, seaborn (for visualization)

### 6.3 Hardware Requirements
- GPU: NVIDIA GPU with ≥16GB VRAM (for CodeLlama-7B)
- Estimated runtime: <30 minutes total (all experiments)

---

## 7. Success Criteria Summary

| Criterion | Metric | Target | Gate Action if Failed |
|-----------|--------|--------|----------------------|
| **Primary:** Final output validity | Syntax validity rate | ≥60% | ABANDON (mechanism doesn't improve final output) |
| **Primary:** Baseline comparison | Syntax error reduction | < greedy baseline (directional) | ABANDON (beam search no better than greedy) |
| **Secondary:** Selection quality | Selection accuracy (≥3 valid beams) | ≥90% | EXPLORE (scoring may be broken) |
| **Secondary:** Strategy comparison | argmax performance | Best among alternatives | PIVOT (adjust α/β weights) |

**Gate Type:** SHOULD_WORK
- **If Primary Criteria Fail:** ABANDON (entire beam search mechanism doesn't reduce syntax errors)
- **If Secondary Criteria Fail:** Continue with caveats (mechanism works but selection suboptimal)

---

## 8. Data Analysis Plan

### 8.1 Final Output Validity Analysis
- Compute syntax validity rate and error rate
- Plot distribution: valid vs invalid final outputs
- Stratify by problem difficulty (if metadata available)
- **Decision:** If validity <60%, mechanism fails → ABANDON

### 8.2 Baseline Comparison Analysis
- Compute greedy baseline error rate (expect 64-68% from h-m1)
- Compute beam search error rate
- Calculate absolute and relative reduction
- Plot comparison: greedy vs beam search error rates
- **Decision:** If beam ≥ greedy, mechanism provides no benefit → ABANDON

### 8.3 Selection Quality Analysis
- Compute selection accuracy when valid beams available
- Identify miss cases (valid beam available but invalid selected)
- Analyze scoring patterns: do valid beams score higher?
- **Decision:** If selection accuracy low, investigate scoring formula

### 8.4 Strategy Comparison Analysis
- Compare argmax vs validity-first vs random-valid selection
- Plot validity rates per strategy
- **Decision:** If argmax not best, β weight may need adjustment

---

## 9. Risk Mitigation

### 9.1 Risk: Final Outputs Still Invalid
**Symptom:** Syntax validity <60% or error rate ≥ greedy baseline
**Diagnosis:**
- Pruning (h-m3) didn't improve final beams enough
- Selection mechanism picks invalid beams despite valid options
- β=0.3 insufficient to overcome log-likelihood bias
**Mitigation:**
- Analyze h-m3 results: did pruning actually work? (73% final validity expected)
- Check selection quality: are valid beams available but not selected?
- Test higher β weights (0.4, 0.5) if selection quality good but final validity low
- **Gate Decision:** If all mitigations fail → ABANDON (mechanism doesn't work)

### 9.2 Risk: No Improvement Over Greedy
**Symptom:** Beam search error rate ≥ greedy baseline (64-68%)
**Diagnosis:**
- Entire pipeline (h-m2 → h-m3 → h-m4) fails to reduce syntax errors
- Beam search overhead not justified by quality improvement
**Mitigation:**
- Verify greedy baseline actually matches h-m1 result (64-68%)
- Check if beam search implementation correct (using validated α/β from h-m2/h-m3)
- Analyze where pipeline fails: scoring (h-m2), pruning (h-m3), or selection (h-m4)
- **Gate Decision:** If verified correct, mechanism fundamentally flawed → ABANDON

### 9.3 Risk: Valid Beams Available but Not Selected
**Symptom:** Selection accuracy <70% when valid beams exist
**Diagnosis:**
- Scoring formula broken (valid beams score lower than invalid)
- Log-likelihood dominates validity signal (α=0.7 too high)
**Mitigation:**
- Verify scoring implementation matches h-m2 validated formula
- Test alternative α/β ratios (0.5/0.5, 0.6/0.4)
- Implement validity-first selection as fallback
- **Gate Decision:** If scoring broken, PIVOT to higher β or validity-first selection

---

## 10. Deliverables

### 10.1 Code Artifacts
1. `final_output_selector.py` - FinalOutputSelector class
2. `greedy_baseline.py` - Greedy sampling baseline
3. `run_experiment_a.py` - Final output validity measurement
4. `run_experiment_b.py` - Baseline comparison
5. `run_experiment_c.py` - Selection quality analysis
6. `run_experiment_d.py` - Strategy comparison ablation
7. `analysis_notebooks/` - Jupyter notebooks for data analysis

### 10.2 Data Artifacts
1. `results/final_outputs.json` - Selected outputs with validity labels
2. `results/greedy_baseline.json` - Greedy sampling results
3. `results/error_rate_comparison.json` - Greedy vs beam search comparison
4. `results/selection_quality.json` - Selection accuracy statistics
5. `results/strategy_comparison.json` - Ablation results

### 10.3 Visualizations
1. `figures/validity_distribution.png` - Valid vs invalid final outputs
2. `figures/baseline_comparison.png` - Greedy vs beam search error rates
3. `figures/selection_accuracy.png` - Selection quality by beam availability
4. `figures/strategy_comparison.png` - Validity rates per selection strategy
5. `figures/gate_metrics.png` - Target vs actual metrics bar chart (MANDATORY)

### 10.4 Documentation
1. `04_validation.md` - Hypothesis validation report (generated in Phase 4)
2. `experiment_logs.txt` - Runtime logs and debug output

---

## 11. Timeline Estimate

| Phase | Duration | Notes |
|-------|----------|-------|
| **Data Preparation** | 5 minutes | Reuse h-m3 dataset cache |
| **Environment Setup** | 5 minutes | Reuse h-m3 environment |
| **Implementation** | 2-3 hours | Extend h-m3 with final selection + greedy baseline |
| **Experiment A (Final Validity)** | 15 minutes | Run beam search on HumanEval-164 |
| **Experiment B (Baseline)** | 10 minutes | Run greedy sampling |
| **Experiment C (Selection Quality)** | 0 minutes | Analysis only |
| **Experiment D (Strategy Ablation)** | 0 minutes | Analysis only |
| **Analysis** | 2-3 hours | Generate plots, compute statistics, write validation report |

**Total Estimated Time:** 5-7 hours

---

## 12. Expected Outcomes

### 12.1 If Hypothesis Passes
- Final output syntax validity ≥60% (beam search selects valid outputs)
- Syntax error rate < greedy baseline (64-68% → ≤40% target met)
- Selection accuracy high when valid beams available (≥90%)
- **Next Step:** Phase 4.5 Synthesis (aggregate results across h-e1 → h-m4)

### 12.2 If Hypothesis Fails (Final Outputs Invalid)
- Syntax validity <60% or error rate ≥ greedy baseline
- **Analysis:** Where did pipeline fail? (scoring, pruning, or selection)
- **Pivot:** Test higher β weights or validity-first selection
- **Gate Decision:** If all pivots fail → ABANDON (mechanism doesn't reduce syntax errors)

### 12.3 If Hypothesis Fails (No Improvement Over Greedy)
- Beam search error rate ≥ greedy baseline
- **Analysis:** Entire pipeline (h-m2 → h-m3 → h-m4) ineffective
- **Gate Decision:** ABANDON (beam search overhead not justified by quality improvement)

### 12.4 If Hypothesis Fails (Selection Broken)
- Valid beams available but invalid selected (selection accuracy <70%)
- **Pivot:** Increase β weight to 0.4-0.5 or implement validity-first selection
- **Re-run:** Experiment A with adjusted selection strategy
- **Gate Decision:** If selection accuracy improves, continue; else ABANDON

---

## 13. Connection to Verification Plan

**From 02b_verification_plan.md:**
- **Section 2.2 (H-M4 Specification):** This experiment brief implements the verification protocol
- **Section 3.3 (Gate Summary):** SHOULD_WORK gate with ABANDON on failure
- **Section 4.1 (Risk Mapping):** Addresses R1 (syntax validity meaningful), R3 (α/β tuning), R4 (compensatory errors)

**Alignment:**
- All success criteria from verification plan preserved
- PoC direction-based approach (directional improvement, no statistical tests)
- Gate-based progression: ABANDON if mechanism doesn't reduce syntax errors
- End-to-end pipeline validation (h-e1 → h-m1 → h-m2 → h-m3 → h-m4)

---

## 14. Notes

**Experiment Design Level:** 1.5 (detailed specification ready for implementation planning)

**Synthetic Data:** NOT USED (HumanEval-164 is a real standard benchmark)

**Sample Size:** 164 problems (full test set, statistically meaningful)

**Compute Budget:** <30 minutes total runtime (well within feasibility)

**Dependencies on h-m3:** 
- Builds on validated beam pruning (62% invalid reduction, 73% final validity)
- Expects ≥3 valid beams in 80% of problems (from h-m3 results)
- Tests whether pruning translates to improved final outputs

**Dependencies on h-m2:**
- Uses validated combined scoring (α=0.7, β=0.3)
- Reuses scoring formula for final beam selection

**Dependencies on h-m1:**
- Uses validated beam width k=5
- Same dataset and model for end-to-end comparison
- Greedy baseline established: 64-68% syntax error rate

**Open Questions:**
- Does h-m3 pruning actually improve final output quality? (Experiment A/B will answer)
- Is argmax selection optimal or do we need validity-first? (Experiment D ablation)
- Can we achieve target ≥40% error reduction (64-68% → ≤40%)? (Experiment B comparison)

**Key Difference from h-m3:**
- h-m3 validated pruning PROCESS (invalid beams removed over time)
- h-m4 validates pruning OUTCOME (final selected output quality)
- h-m3 is INTERNAL (beam-level tracking), h-m4 is EXTERNAL (user-facing output quality)

**Critical Test:**
- This is the FINAL validation of entire syntax-aware beam search pipeline
- If h-m4 fails, entire approach (h-e1 → h-m4) doesn't reduce syntax errors → ABANDON
- If h-m4 passes, pipeline validated → proceed to Phase 4.5 Synthesis

---

**Generated:** 2026-08-25  
**Workflow:** Phase 2C Experiment Design (Ablation Mode - No MCP)  
**Schema Version:** 3.5
