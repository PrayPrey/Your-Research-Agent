# Product Requirements Document: Final Valid Output Selection (h-m4)

**Date:** 2026-08-25  
**Hypothesis ID:** h-m4  
**Type:** MECHANISM  
**Gate:** SHOULD_WORK  
**Prerequisites:** h-m3 (VALIDATED)  
**Document Version:** 1.0

---

## 1. Executive Summary

### 1.1 Purpose
Validate that validity-scored beam search produces syntactically correct final outputs by testing final beam selection quality and comparing syntax error rate against greedy baseline.

### 1.2 Core Hypothesis
Final selected code from argmax beam (after validity-scored pruning) is syntactically valid throughout generation process.

### 1.3 Success Criteria
- **Primary:** Syntax validity rate ≥60% (98/164 problems)
- **Primary:** Beam search syntax error rate < greedy baseline (directional improvement)
- **Secondary:** Selection accuracy ≥90% when ≥3 valid beams available
- **Secondary:** argmax outperforms alternative selection strategies

### 1.4 Scope
- Final output selection from k=5 beams using combined scoring (α=0.7, β=0.3)
- Greedy sampling baseline on HumanEval-164
- Selection quality analysis (argmax vs alternatives)
- End-to-end validation of beam search pipeline (h-m2 → h-m3 → h-m4)

---

## 2. Background

### 2.1 Problem Statement
Beam search with validity scoring (h-m2) and pruning (h-m3) should produce syntactically valid final outputs. Need to validate final selection quality and measure syntax error reduction vs greedy baseline.

### 2.2 Research Context
- **h-m1:** Greedy baseline syntax error rate 64-68% on HumanEval-164
- **h-m2:** Combined scoring (α=0.7, β=0.3) achieves 73% valid beams
- **h-m3:** Pruning reduces invalid beams by 62%, 80% problems have ≥3 valid final beams
- **h-m4:** Tests whether pruning translates to improved final output quality

### 2.3 Key Assumptions
- Top-scoring beam after pruning is likely syntactically valid (73% final validity in h-m3)
- argmax selection on combined score captures best beam
- Syntax validity correlates with semantic correctness
- No compensatory error mode shifts (type errors, semantic bugs)

---

## 3. User Requirements

### 3.1 Functional Requirements

**FR1: Final Beam Selection**
- Select beam with highest final_score from k=5 candidates
- Use combined scoring: `final_score = α * log_likelihood + β * validity_score`
- Return selected beam text, beam index, and all scores

**FR2: Greedy Baseline Generation**
- Run greedy sampling (num_beams=1, temperature=0.8) on same HumanEval-164
- Generate single output per problem
- Return greedy outputs with timing data

**FR3: Syntax Validation**
- Validate final beam selection using `ast.parse()`
- Validate greedy baseline using `ast.parse()`
- Return validity labels (True/False) and error messages

**FR4: Selection Quality Analysis**
- Count valid beams in final k=5 per problem
- Check if selected beam is valid when valid options exist
- Stratify by beam availability (0, 1-2, ≥3 valid beams)

**FR5: Strategy Comparison**
- Implement alternative selection strategies:
  - argmax(final_score) - current
  - argmax(validity_score) then argmax(log_likelihood) - validity-first
  - Random from valid beams - random valid
- Compare syntax validity rates across strategies

### 3.2 Non-Functional Requirements

**NFR1: Performance**
- Full HumanEval-164 generation ≤30 minutes total
- Greedy baseline ≤10 minutes
- Analysis scripts ≤5 minutes

**NFR2: Reproducibility**
- Fixed random seed for beam search and greedy sampling
- Deterministic beam selection (argmax tie-breaking)
- Cache model and dataset to avoid re-downloads

**NFR3: Logging**
- Log selected beam index and scores per problem
- Log selection misses (valid beam available but invalid selected)
- Save intermediate beam scores and validity labels

**NFR4: Hardware**
- GPU execution (CUDA) for CodeLlama-7B
- Fallback to CPU with reduced batch size if GPU unavailable
- ≥16GB VRAM recommended

---

## 4. Technical Requirements

### 4.1 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Final Output Selection System (h-m4)                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Experiment A: Final Output Validity                   │ │
│  │  - Load HumanEval-164                                 │ │
│  │  - Run beam search (k=5, α=0.7, β=0.3)               │ │
│  │  - Select argmax(final_score) per problem             │ │
│  │  - Validate with ast.parse()                          │ │
│  │  - Output: validity rate, error rate                  │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Experiment B: Greedy Baseline                         │ │
│  │  - Run greedy sampling (num_beams=1)                  │ │
│  │  - Validate outputs with ast.parse()                  │ │
│  │  - Compute error rate reduction                       │ │
│  │  - Output: absolute/relative reduction                │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Experiment C: Selection Quality                       │ │
│  │  - Count valid beams in final k=5                     │ │
│  │  - Check if selected beam is valid                    │ │
│  │  - Stratify by availability (0, 1-2, ≥3 valid)        │ │
│  │  - Output: selection accuracy, miss rate              │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Experiment D: Strategy Comparison                     │ │
│  │  - Test argmax, validity-first, random-valid          │ │
│  │  - Compare validity rates                             │ │
│  │  - Output: best strategy, performance gap             │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Core Components

**Component 1: FinalOutputSelector**
- Input: k beams, log-likelihoods, α, β
- Logic: Compute final_score per beam, select argmax
- Output: selected beam, beam index, all scores

**Component 2: GreedySampler**
- Input: model, tokenizer, HumanEval prompts
- Logic: Generate single output per problem (num_beams=1)
- Output: greedy outputs, generation times

**Component 3: SyntaxValidator**
- Input: code snippet
- Logic: `ast.parse()` with exception handling
- Output: validity (True/False), error message

**Component 4: SelectionAnalyzer**
- Input: final beams, selected indices, validity labels
- Logic: Compute selection accuracy per beam availability stratum
- Output: accuracy metrics, miss cases

**Component 5: StrategyComparator**
- Input: k beams, beam scores, validity labels
- Logic: Apply alternative selection strategies, compare validity rates
- Output: strategy-wise validity rates, best performer

### 4.3 Data Flow

```
HumanEval-164 (164 problems)
    ↓
Beam Search (k=5, α=0.7, β=0.3)
    ↓
FinalOutputSelector → Select argmax(final_score)
    ↓
SyntaxValidator → ast.parse()
    ↓
Results: validity_rate, error_rate
    ↓
Compare with GreedySampler baseline
    ↓
SelectionAnalyzer → accuracy, miss_rate
    ↓
StrategyComparator → best_strategy
    ↓
04_validation.md report
```

### 4.4 Algorithms

**Algorithm 1: Final Beam Selection**
```python
def select_final_output(beams, log_likelihoods, alpha=0.7, beta=0.3):
    final_scores = []
    for beam, log_likelihood in zip(beams, log_likelihoods):
        validity_score = 1 if validate_syntax(beam) else 0
        final_score = alpha * log_likelihood + beta * validity_score
        final_scores.append(final_score)
    
    best_idx = np.argmax(final_scores)
    return beams[best_idx], best_idx, final_scores
```

**Algorithm 2: Error Rate Comparison**
```python
def compute_error_reduction(greedy_results, beam_results):
    greedy_errors = sum(1 for valid in greedy_results if not valid)
    beam_errors = sum(1 for valid in beam_results if not valid)
    
    greedy_error_rate = greedy_errors / len(greedy_results)
    beam_error_rate = beam_errors / len(beam_results)
    
    absolute_reduction = greedy_error_rate - beam_error_rate
    relative_reduction = (absolute_reduction / greedy_error_rate) * 100
    
    return absolute_reduction, relative_reduction
```

**Algorithm 3: Selection Accuracy**
```python
def compute_selection_accuracy(beams_validity, selected_indices):
    correct = 0
    total = 0
    
    for problem_beams, selected_idx in zip(beams_validity, selected_indices):
        if any(problem_beams):  # at least 1 valid beam exists
            total += 1
            if problem_beams[selected_idx]:  # selected beam is valid
                correct += 1
    
    return correct / total if total > 0 else 0
```

---

## 5. Experiments

### 5.1 Experiment A: Final Output Validity

**Objective:** Measure syntax validity of final selected outputs from validity-scored beam search

**Protocol:**
1. Load HumanEval-164, CodeLlama-7B
2. Run beam search (k=5, α=0.7, β=0.3) on all 164 problems
3. Select argmax(final_score) per problem
4. Validate with `ast.parse()`
5. Compute validity rate, error rate

**Metrics:**
- Syntax validity rate: (valid outputs / 164) × 100%
- Syntax error rate: (invalid outputs / 164) × 100%

**Success:** Validity ≥60%, Error ≤40%

### 5.2 Experiment B: Baseline Comparison

**Objective:** Compare beam search syntax error rate vs greedy sampling baseline

**Protocol:**
1. Run greedy sampling (num_beams=1, temperature=0.8) on HumanEval-164
2. Validate greedy outputs with `ast.parse()`
3. Compare error rates: greedy vs beam search
4. Compute absolute and relative reduction

**Metrics:**
- Greedy error rate (expected: 64-68%)
- Beam error rate (target: ≤40%)
- Absolute reduction: greedy - beam
- Relative reduction: (greedy - beam) / greedy × 100%

**Success:** Beam error rate < greedy (directional improvement)

### 5.3 Experiment C: Selection Quality

**Objective:** Verify argmax selects valid beams when available

**Protocol:**
1. From Experiment A beams, count valid beams per problem
2. Check if selected beam is valid
3. Stratify by availability: 0, 1-2, ≥3 valid beams
4. Compute selection accuracy per stratum

**Metrics:**
- Selection accuracy (≥1 valid beam)
- Selection accuracy (≥3 valid beams)
- Miss rate: valid available but invalid selected

**Success:** Accuracy ≥90% when ≥3 valid beams, ≥70% when ≥1

### 5.4 Experiment D: Strategy Comparison

**Objective:** Test whether argmax is optimal selection strategy

**Protocol:**
1. From Experiment A beams, apply alternative selection strategies:
   - argmax(final_score) - current
   - argmax(validity_score) then argmax(log_likelihood) - validity-first
   - Random from valid beams
2. Compute validity rate per strategy
3. Identify best performer

**Metrics:**
- Validity rate per strategy
- Performance gap: best - argmax

**Success:** argmax performs best (validates α=0.7, β=0.3 design)

---

## 6. Implementation Tasks

### 6.1 Data Preparation (1 task)
1. Load HumanEval-164 and CodeLlama-7B (reuse h-m3 cache)

### 6.2 Core Implementation (4 tasks)
2. Implement FinalOutputSelector class
3. Implement GreedySampler class
4. Implement SyntaxValidator (reuse h-m3)
5. Implement SelectionAnalyzer

### 6.3 Experiment Scripts (4 tasks)
6. Write run_experiment_a.py (final validity)
7. Write run_experiment_b.py (baseline comparison)
8. Write run_experiment_c.py (selection quality)
9. Write run_experiment_d.py (strategy comparison)

### 6.4 Analysis (1 task)
10. Write analysis script (aggregate results, generate 04_validation.md)

---

## 7. Success Metrics

| Metric | Target | Critical? | Action if Failed |
|--------|--------|-----------|------------------|
| Syntax validity rate | ≥60% (98/164) | YES | ABANDON |
| Error rate vs greedy | < baseline (directional) | YES | ABANDON |
| Selection accuracy (≥3 valid) | ≥90% | NO | Investigate scoring |
| argmax vs alternatives | Best performer | NO | Adjust α/β |

---

## 8. Risk Mitigation

**Risk 1: Final outputs still invalid (validity <60%)**
- Check h-m3 pruning results: did 73% final validity hold?
- Analyze selection quality: valid beams available but not selected?
- Test higher β weights (0.4, 0.5)
- **Gate:** ABANDON if all mitigations fail

**Risk 2: No improvement over greedy (beam error ≥ greedy)**
- Verify greedy baseline matches h-m1 (64-68%)
- Check beam search implementation (α/β correct)
- Analyze where pipeline fails: scoring, pruning, or selection
- **Gate:** ABANDON if pipeline fundamentally flawed

**Risk 3: Valid beams available but not selected (accuracy <70%)**
- Verify scoring formula matches h-m2
- Test alternative α/β ratios
- Implement validity-first selection as fallback
- **Gate:** PIVOT to higher β or validity-first if scoring broken

---

## 9. Deliverables

### 9.1 Code
1. `final_output_selector.py` - FinalOutputSelector class
2. `greedy_baseline.py` - GreedySampler class
3. `syntax_validator.py` - AST validation (reused from h-m3)
4. `selection_analyzer.py` - Selection quality analysis
5. `run_experiment_a.py` - Final validity experiment
6. `run_experiment_b.py` - Baseline comparison
7. `run_experiment_c.py` - Selection quality
8. `run_experiment_d.py` - Strategy comparison
9. `analyze_results.py` - Aggregate and generate report

### 9.2 Data
1. `results/final_outputs.json` - Selected outputs with validity
2. `results/greedy_baseline.json` - Greedy outputs
3. `results/error_comparison.json` - Greedy vs beam error rates
4. `results/selection_quality.json` - Selection accuracy
5. `results/strategy_comparison.json` - Strategy ablation

### 9.3 Visualizations
1. `figures/validity_distribution.png` - Valid vs invalid bar chart
2. `figures/baseline_comparison.png` - Error rate comparison
3. `figures/selection_accuracy.png` - Accuracy by beam availability
4. `figures/strategy_comparison.png` - Validity per strategy
5. `figures/gate_metrics.png` - Target vs actual metrics (MANDATORY)

### 9.4 Documentation
1. `04_validation.md` - Hypothesis validation report (generated in Phase 4)

---

## 10. Timeline

| Task | Duration | Notes |
|------|----------|-------|
| Data preparation | 5 min | Reuse h-m3 cache |
| Core implementation | 2-3 hours | Extend h-m3 with final selection + baseline |
| Experiment A (validity) | 15 min | Full HumanEval-164 generation |
| Experiment B (baseline) | 10 min | Greedy sampling |
| Experiment C (quality) | 0 min | Analysis only |
| Experiment D (strategy) | 0 min | Analysis only |
| Analysis | 2-3 hours | Plots, statistics, report |

**Total:** 5-7 hours

---

## 11. Acceptance Criteria

**Primary (must pass):**
- [ ] Syntax validity rate ≥60% (98/164 problems)
- [ ] Beam search error rate < greedy baseline (directional)

**Secondary (nice to have):**
- [ ] Selection accuracy ≥90% when ≥3 valid beams
- [ ] argmax outperforms alternative strategies

**Deliverables:**
- [ ] All 9 code artifacts implemented
- [ ] All 5 data/result files generated
- [ ] All 5 figures generated (including gate_metrics.png)
- [ ] 04_validation.md report written

---

## 12. Appendix

### 12.1 Dependencies
- transformers (HuggingFace)
- torch (PyTorch)
- datasets (HumanEval loading)
- ast (Python stdlib)
- numpy, pandas (analysis)
- matplotlib, seaborn (visualization)

### 12.2 Hardware
- GPU: NVIDIA ≥16GB VRAM (for CodeLlama-7B)
- CPU fallback: supported but slower

### 12.3 Configuration
- Beam width: k=5
- Scoring weights: α=0.7, β=0.3
- Temperature: 0.8
- Max tokens: 512

### 12.4 Connection to Verification Plan
- Implements Section 2.2 (H-M4 Specification) from 02b_verification_plan.md
- SHOULD_WORK gate with ABANDON on failure
- Addresses risks R1 (syntax validity), R3 (α/β tuning), R4 (compensatory errors)

---

**Document Status:** READY FOR IMPLEMENTATION PLANNING (Phase 3)  
**Next Step:** Launch architecture-agent, logic-agent, configuration-agent for detailed design  
**Schema Version:** 3.5
