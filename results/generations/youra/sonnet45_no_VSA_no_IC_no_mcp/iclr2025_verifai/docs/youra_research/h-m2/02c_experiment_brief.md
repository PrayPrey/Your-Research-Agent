# Experiment Brief: Combined Scoring Function (h-m2)

**Date:** 2026-08-25  
**Hypothesis ID:** h-m2  
**Type:** MECHANISM  
**Gate:** SHOULD_WORK  
**Prerequisites:** h-m1 (VALIDATED)

---

## 1. Hypothesis Statement

**h-m2:** Combined scoring (α * log_likelihood + β * syntax_validity_score) correctly ranks beams by both fluency and validity, with AST parse checks fast enough (<50ms).

**Rationale:** Tests scoring mechanism. If scoring is broken (wrong formula, slow AST parsing) or invalid beams score higher than valid ones, pruning won't work.

---

## 2. Variables

### 2.1 Independent Variables
- **IV1:** Scoring weights (α, β) combinations
  - Values: (0.5, 0.5), (0.6, 0.4), (0.7, 0.3), (0.8, 0.2)
  - Default: α=0.7, β=0.3 (from verification plan)

### 2.2 Dependent Variables
- **DV1:** AST parse latency (milliseconds)
  - Measurement: Per beam candidate at each generation step
  - Target: <50ms (mean and p95)
  
- **DV2:** Beam ranking correctness
  - Measurement: Proportion of generation steps where valid beams (validity_score=1) rank higher than invalid beams (validity_score=0)
  - Target: ≥80% of steps

### 2.3 Control Variables
- **CV1:** Model = CodeLlama-7B (meta-llama/CodeLlama-7b-hf)
- **CV2:** Dataset = HumanEval-164 (standard benchmark)
- **CV3:** Beam width k = 5 (validated in h-m1)
- **CV4:** Generation strategy = Beam search with combined scoring

---

## 3. Dataset Preparation

### 3.1 Primary Dataset
**Name:** HumanEval-164  
**Type:** standard (real established dataset)  
**Source:** https://github.com/openai/human-eval  
**Size:** 164 hand-written Python programming problems  
**Split:** Full test set (no train/val split; code generation benchmark)

**Rationale:**
- Same dataset as h-m1 baseline (enables direct comparison)
- Real-world benchmark with established metrics
- Syntax error rate 64-68% well-documented from h-m1 analysis
- Sufficient sample size for statistical validity (>50 samples)

**Cache Path:** Will be set during data preparation phase  
**Verification:** SHA256 checksum against official HumanEval release

### 3.2 Ablation Subset
**Name:** HumanEval-Ablation-20  
**Type:** custom (sampled from HumanEval-164)  
**Size:** 20 problems (stratified sample by difficulty)  
**Purpose:** α/β grid search without full-scale compute cost

**Sampling Strategy:**
- Select 20 problems covering difficulty spectrum
- Include problems with varied syntax patterns (loops, comprehensions, recursion, control flow)
- Ensures representative coverage for weight tuning

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

**Cache Path:** Will be set during environment setup

---

## 5. Experiments

### 5.1 Experiment A: AST Parse Latency Measurement

**Objective:** Validate assumption A5 (AST parsing <50ms per check)

**Protocol:**
1. Implement scoring function with AST parse timing instrumentation
2. Run beam search on full HumanEval-164
3. For each beam candidate at each generation step:
   - Start timer
   - Execute `ast.parse(candidate_code)`
   - Record elapsed time
4. Aggregate latency statistics

**Metrics:**
- Mean AST parse latency (ms)
- Median AST parse latency (ms)
- p95 AST parse latency (ms)
- Max AST parse latency (ms)

**Success Criteria:**
- Mean latency <50ms
- p95 latency <100ms (allows occasional slow parses)

**Expected Compute:**
- ~164 problems × 5 beams × ~30 generation steps = ~24,600 AST parse calls
- Estimated time: ~5-10 minutes total runtime (from h-m1: 4.5min for beam generation + parse overhead)

---

### 5.2 Experiment B: Beam Ranking Verification

**Objective:** Verify valid beams rank higher than invalid beams when β=0.3

**Protocol:**
1. Implement scoring function: `final_score = α * log_likelihood + β * syntax_validity_score`
   - α = 0.7, β = 0.3 (default from verification plan)
   - syntax_validity_score = 1 if ast.parse() succeeds, else 0
2. Run beam search on full HumanEval-164
3. At each generation step, log:
   - beam_id
   - log_likelihood
   - syntax_validity_score (0 or 1)
   - final_score
   - rank (1 = highest score)
4. Analyze ranking correctness:
   - Count steps where valid beams (validity_score=1) have higher final_score than invalid beams (validity_score=0)
   - Compute proportion: correct_ranking_steps / total_steps

**Metrics:**
- Proportion of steps with correct ranking (valid > invalid)
- Distribution of valid beam ranks (how often valid beams rank in top-3, top-5)
- Mean final_score gap between valid and invalid beams

**Success Criteria:**
- Valid beams rank higher in ≥80% of generation steps
- At least 60% of top-ranked beams (rank=1) are valid

**Expected Compute:**
- Same as Experiment A (~5-10 minutes)
- Can run simultaneously with latency measurement

---

### 5.3 Experiment C: α/β Ablation Study

**Objective:** Validate assumption A3 (α=0.7, β=0.3 optimal) and explore alternative weights

**Protocol:**
1. Define weight combinations:
   - (α=0.5, β=0.5): Equal weight to fluency and validity
   - (α=0.6, β=0.4): Moderate validity emphasis
   - (α=0.7, β=0.3): Default from verification plan
   - (α=0.8, β=0.2): Strong fluency emphasis
2. Run beam search on HumanEval-Ablation-20 subset (20 problems)
3. For each α/β combination:
   - Measure beam ranking correctness (as in Experiment B)
   - Measure final output syntax validity rate
   - Measure final output quality (optional: check if code is semantically reasonable via manual inspection of 5 samples)
4. Compare across combinations

**Metrics:**
- Per combination:
  - Valid beam ranking proportion
  - Final output syntax error rate (invalid outputs / 20)
  - Beam diversity (proportion of unique outputs in k=5 beams)

**Success Criteria:**
- At least one combination achieves:
  - Valid beam ranking ≥80%
  - Final syntax error rate <50% (improvement over 64-68% greedy baseline)
- If α=0.7, β=0.3 is NOT optimal, identify better weights for subsequent hypotheses

**Expected Compute:**
- 4 combinations × 20 problems = 80 beam search runs
- Estimated time: ~15-20 minutes total

**Pivot Decision:**
- If all combinations fail ranking criterion: Increase β (test β=0.4, 0.5)
- If all combinations fail syntax criterion: α/β scoring insufficient → EXPLORE alternative scoring formulas

---

### 5.4 Baseline Comparison

**Baseline Methods:**
1. **Greedy Sampling (from h-m1):**
   - Syntax error rate: 64-68%
   - No beam exploration
   
2. **Pure Log-Likelihood Beam Search:**
   - α=1.0, β=0.0 (beam search without validity scoring)
   - Tests whether validity scoring adds value over pure fluency ranking

**Comparison Protocol:**
1. Run pure log-likelihood beam search (α=1.0, β=0.0) on same HumanEval-164
2. Measure:
   - Final output syntax error rate
   - Proportion of valid beams in top-k at final step
3. Compare against combined scoring (α=0.7, β=0.3)

**Expected Result:**
- Pure log-likelihood beam search: Similar syntax error rate to greedy (~60-70%)
- Combined scoring: Reduced syntax error rate (target: <40%)

---

## 6. Implementation Requirements

### 6.1 Code Components

**Required Modules:**
1. **Scoring Function:**
   ```python
   def combined_score(log_likelihood, syntax_validity_score, alpha=0.7, beta=0.3):
       return alpha * log_likelihood + beta * syntax_validity_score
   ```

2. **AST Validation:**
   ```python
   import ast
   import time
   
   def validate_syntax(code_snippet):
       start_time = time.perf_counter()
       try:
           ast.parse(code_snippet)
           valid = True
       except SyntaxError:
           valid = False
       elapsed_ms = (time.perf_counter() - start_time) * 1000
       return valid, elapsed_ms
   ```

3. **Beam Search with Custom Scoring:**
   - Extend HuggingFace `BeamSearchScorer` or implement custom beam selection
   - At each step:
     - Get log_likelihood from model
     - Validate each beam candidate with AST parse
     - Compute combined_score for each beam
     - Select top-k beams by combined_score (not just log_likelihood)

4. **Logging Infrastructure:**
   - Log beam states at each generation step
   - Store: step_id, beam_id, log_likelihood, syntax_validity_score, final_score, rank
   - Save to structured format (JSON or CSV)

### 6.2 Dependencies
- transformers (HuggingFace)
- torch (PyTorch backend)
- ast (Python standard library)
- datasets (for HumanEval loading)
- numpy, pandas (for analysis)

### 6.3 Hardware Requirements
- GPU: NVIDIA GPU with ≥16GB VRAM (for CodeLlama-7B)
- Estimated runtime: <30 minutes total (all experiments)

---

## 7. Success Criteria Summary

| Criterion | Metric | Target | Gate Action if Failed |
|-----------|--------|--------|----------------------|
| **Primary:** AST latency | Mean parse time | <50ms | PIVOT (cache AST parse or reduce beam width) |
| **Primary:** Beam ranking | Valid > invalid proportion | ≥80% | EXPLORE (adjust α/β or scoring formula) |
| **Secondary:** Final output quality | Syntax error rate | <greedy baseline | PIVOT (increase β weight) |
| **Secondary:** α/β optimality | Grid search validates weights | At least one combination passes | EXPLORE (alternative scoring) |

**Gate Type:** SHOULD_WORK
- **If Primary Criteria Fail:** PIVOT or EXPLORE (adjust weights, caching, or scoring formula)
- **If Secondary Criteria Fail:** Continue with caveats (may adjust weights for h-m3)

---

## 8. Data Analysis Plan

### 8.1 AST Latency Analysis
- Compute latency statistics (mean, median, p95, max)
- Plot histogram of parse times
- Identify outliers (>100ms cases)
- **Decision:** If p95 >100ms, investigate caching strategy

### 8.2 Beam Ranking Analysis
- Compute proportion of correct ranking steps
- Stratify by generation step position (early vs late)
- Analyze: Do rankings improve as generation progresses?
- **Decision:** If <80%, analyze failure cases (when do invalid beams rank higher?)

### 8.3 α/β Ablation Analysis
- Compare final syntax error rates across 4 combinations
- Identify optimal (α, β) pair
- Test statistical significance (if multiple combinations similar)
- **Decision:** Update default weights for h-m3 if better combination found

### 8.4 Baseline Comparison
- Compare final syntax error rate: greedy vs pure beam search vs combined scoring
- Compute relative improvement: (baseline - combined) / baseline × 100%
- **Decision:** If combined scoring not better than pure beam search, mechanism hypothesis fails

---

## 9. Risk Mitigation

### 9.1 Risk R5: AST Parsing Slow
**Mitigation:**
- Monitor latency in Experiment A
- If >50ms mean: Implement AST parse caching (cache parse results for identical code snippets)
- If still slow: Reduce beam width k (test k=3 as fallback)

### 9.2 Risk R3: α/β Suboptimal
**Mitigation:**
- Ablation study in Experiment C tests 4 combinations
- If all fail: Expand grid search to β=0.4, 0.5, 0.6
- If still suboptimal: Consider learned validity features (Variant B from verification plan)

### 9.3 Risk: Scoring Formula Broken
**Symptom:** Invalid beams consistently rank higher than valid beams
**Diagnosis:**
- Check log_likelihood values (are they much larger in magnitude than validity_score?)
- Normalize log_likelihood to [0, 1] range before combining
- Test alternative formula: `final_score = α * normalized_log_likelihood + β * syntax_validity_score`

---

## 10. Deliverables

### 10.1 Code Artifacts
1. `scoring_function.py` - Combined scoring implementation
2. `beam_search_custom.py` - Beam search with validity scoring
3. `ast_validator.py` - AST parse with timing
4. `run_experiment_a.py` - AST latency measurement
5. `run_experiment_b.py` - Beam ranking verification
6. `run_experiment_c.py` - α/β ablation study
7. `analysis_notebooks/` - Jupyter notebooks for data analysis

### 10.2 Data Artifacts
1. `results/ast_latency_stats.json` - Latency statistics
2. `results/beam_ranking_logs.csv` - Per-step beam rankings
3. `results/ablation_results.json` - α/β comparison
4. `results/baseline_comparison.json` - Greedy vs beam search vs combined scoring

### 10.3 Documentation
1. `04_validation.md` - Hypothesis validation report (generated in Phase 4)
2. `experiment_logs.txt` - Runtime logs and debug output

---

## 11. Timeline Estimate

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

## 12. Expected Outcomes

### 12.1 If Hypothesis Passes
- AST parse latency <50ms (validates A5)
- Valid beams rank higher ≥80% of time (validates scoring mechanism)
- α=0.7, β=0.3 confirmed optimal (or better weights identified)
- **Next Step:** Proceed to h-m3 (Invalid Beam Pruning)

### 12.2 If Hypothesis Fails (AST Slow)
- AST latency >50ms (violates A5)
- **Pivot:** Implement AST caching or reduce beam width to k=3
- **Re-run:** Experiment A with optimizations
- **Gate Decision:** If still slow, consider abandoning AST-based validation

### 12.3 If Hypothesis Fails (Ranking Incorrect)
- Valid beams rank higher <80% of time (scoring broken)
- **Explore:** Adjust α/β weights (increase β to 0.4, 0.5)
- **Explore:** Normalize log_likelihood before combining
- **Explore:** Alternative scoring formulas (learned validity features)
- **Gate Decision:** If all explorations fail, mechanism hypothesis invalid → ABANDON

### 12.4 If Hypothesis Fails (No Improvement over Baseline)
- Combined scoring syntax error rate ≈ greedy baseline (64-68%)
- **Analysis:** Beam search explores alternatives but validity scoring doesn't help pruning
- **Gate Decision:** ABANDON (mechanism doesn't reduce syntax errors)

---

## 13. Connection to Verification Plan

**From 02b_verification_plan.md:**
- **Section 2.2 (H-M2 Specification):** This experiment brief implements the verification protocol
- **Section 3.3 (Gate Summary):** SHOULD_WORK gate with PIVOT/EXPLORE on failure
- **Section 4.1 (Risk R5):** AST parsing speed validated in Experiment A
- **Section 4.1 (Risk R3):** α/β tuning validated in Experiment C

**Alignment:**
- All success criteria from verification plan preserved
- PoC direction-based approach (no statistical significance testing, focus on directional improvement)
- Gate-based progression: PIVOT on AST slow, EXPLORE on scoring broken, ABANDON if no improvement

---

## 14. Notes

**Experiment Design Level:** 1.5 (detailed specification ready for implementation planning)

**Synthetic Data:** NOT USED (HumanEval-164 is a real standard benchmark)

**Sample Size:** 164 problems (full test set, statistically meaningful)

**Compute Budget:** <30 minutes total runtime (well within feasibility)

**Dependencies on h-m1:** 
- Builds on validated beam search infrastructure (k=5 maintenance verified)
- Uses same dataset/model (enables direct comparison)
- Extends h-m1 by adding validity scoring to pure beam search

**Open Questions:**
- Should log_likelihood be normalized before combining? (Will test if ranking fails)
- Is β=0.3 sufficient or should we start with higher β? (Ablation study will answer)
- Can AST caching reduce latency if needed? (Implement as fallback)

---

**Generated:** 2026-08-25  
**Workflow:** Phase 2C Experiment Design (UNATTENDED mode)  
**Schema Version:** 3.5
