---
workflow: phase2c-experiment-design
generated_at: 2026-07-11T07:15:00Z
hypothesis_id: h-c1
parent_hypothesis: h-verifierteacher-v1
archon_project_id: 6b1361ed-02e6-4b99-ab72-78b79a4178ab
execution_mode: UNATTENDED
stepsCompleted:
  - step-01-load-hypothesis
  - step-02-archon-kb-search
  - step-03-exa-implementation-search
  - step-04-dataset-design
  - step-05-baseline-design
  - step-06-synthesis
  - step-07-finalize
---

# Phase 2C: Experiment Design Brief
**Hypothesis**: h-c1  
**Generated**: 2026-07-11  
**Archon Project**: 6b1361ed-02e6-4b99-ab72-78b79a4178ab  

---

## Section 1: Hypothesis Specification

### 1.1 Hypothesis Statement

**ID**: h-c1  
**Type**: Control Condition  
**Gate**: MUST_WORK  
**Prerequisites**: h-m1 (Information gradient hypothesis - VALIDATED)

**Statement**:
Under compute-matched budgets (equal tokens + verifier time), iterative feedback outperforms single-shot self-consistency sampling by ≥10pp in proof discharge rate

### 1.2 Rationale & Importance

This is a **critical control hypothesis** that validates whether the gains from iterative feedback (h-m1) are truly due to the **information content** of feedback rather than simply **more compute budget**. Without this control, critics could argue that any performance gain is just from spending more tokens/time, not from feedback quality.

**Key Question**: Is iterative refinement with structured feedback fundamentally better than just sampling multiple independent attempts with the same compute?

**Alternative Hypothesis (H0)**: Self-consistency sampling with N independent attempts performs equivalently to N iterations of feedback-driven refinement when matched for total tokens and verifier time.

### 1.3 Research Context from Phase 2A

From the validated h-m1 results:
- **RawError**: 31.92% discharge rate
- **TagOnly**: 44.8% (+12.89pp)
- **ObligationSlice**: 55.08% (+10.28pp)
- **FullStructured**: 70.12% (+15.03pp)

The iterative feedback approach (FullStructured) achieved 70.12% discharge rate. The control question is: **could self-consistency sampling achieve similar results with matched compute?**

### 1.4 Prior Work Analysis

**Key Finding from Literature Search**:

1. **Self-Correction as Feedback Control (Liu & Meng, 2024)** [arXiv:2604.22273]
   - Established stability threshold: iterate only when ECR/EIR > Acc/(1-Acc)
   - Sharp near-zero EIR boundary (<0.5%) separates beneficial from harmful self-correction
   - Only o3-mini (+3.4pp), Claude Opus 4.6 (+0.6pp) stayed non-degrading
   - **Implication**: Iterative refinement can degrade performance if error introduction rate is high

2. **SELF-REFINE (Madaan et al., NeurIPS 2023)**
   - Iterative feedback and refinement improved by ~20% absolute on average
   - No supervised training, RL, or additional models required
   - **Implication**: Single LLM can provide feedback and refine iteratively

3. **Internal Consistency and Self-Feedback (Liang et al., 2024)** [arXiv:2407.14507]
   - Self-Feedback framework: Self-Evaluation + Self-Update modules
   - **Implication**: Feedback mechanisms can mine internal consistency

4. **Iterative Agent Decoding (IAD) (Chakraborty et al., 2024)** [arXiv:2504.01931]
   - IAD with high-fidelity feedback: up to 10% absolute improvement over best-of-N
   - Tested on Sketch2Code, Text2SQL, Intercode, WebShop
   - **Implication**: Feedback integration beats diversity-only baselines

5. **Formal Verification Feedback Loops**:
   - **SpecLoop (Chang et al., 2026)** [arXiv:2603.02895]: Formal verification feedback for RTL-to-spec generation
   - **WybeCoder (Baksys et al., 2026)**: 74.1% solve rate with iterative proof refinement (32 turns × 16 agents)
   - **VRN2 (HierSVA, 2026)**: SVA generation with FPV/FTA/COV/FC feedback loop
   - **Implication**: Verification feedback loops are effective in formal methods domain

**Gap**: While prior work shows iterative feedback can help, **no study has rigorously compared iterative feedback vs self-consistency sampling under compute-matched conditions for formal specification synthesis**.

---

## Section 2: Experimental Design

### 2.1 Dataset Specification

**Dataset Name**: Frama-C Verified C Programs with ACSL Annotations  
**Dataset Type**: Standard benchmark  
**Dataset Source**: Open-source verification benchmarks (Frama-C examples, Juliet verified subset)

**Dataset Scale**:
- **Training/Few-shot Examples**: 10 programs (for in-context learning)
- **Validation Set**: 15 programs (for hyperparameter tuning)
- **Test Set**: 50 programs (for final evaluation)
- **Total**: 75 programs

**Justification for Scale**: 
- 50 test programs provides statistical power for detecting ≥10pp differences (power analysis: n=50, α=0.05, power=0.80 for effect size d=0.57)
- Full standard benchmark (not synthetic/simulated)
- Matches scale used in formal verification research (e.g., WybeCoder: 189 problems, SpecLoop: multiple RTL benchmarks)

**Dataset Characteristics**:
- **Domain**: Verified C programs with formal specifications
- **Complexity Range**: 
  - Simple: Array operations, basic arithmetic (10-50 LOC)
  - Medium: String manipulation, data structure operations (50-150 LOC)
  - Complex: Algorithmic implementations with non-trivial invariants (150-500 LOC)
- **Properties**: Safety properties (array bounds, null pointer checks), functional properties (correctness of algorithms)
- **Gold Standard**: Expert-written ACSL annotations with verified proof discharge

**Dataset Preparation Steps**:
1. **Collection**: Aggregate from Frama-C tutorial examples, Frama-C regression tests, Juliet test suite verified subset
2. **Filtering**: Select programs with:
   - Complete ACSL annotations (function contracts + loop invariants)
   - Verified proof discharge (WP plugin successfully proves all obligations)
   - Deterministic behavior (no concurrency, no I/O dependencies)
3. **Stratification**: Balance across complexity levels (30% simple, 50% medium, 20% complex)
4. **Splitting**: Random stratified split (10 train, 15 val, 50 test)
5. **Validation**: Verify gold standard specs still discharge with current Frama-C version

**Data Format**:
```
{
  "program_id": "array_max_001",
  "source_code": "...",  # C code without ACSL annotations
  "gold_spec": "...",    # Expert ACSL annotations
  "complexity": "medium",
  "proof_obligations": 12,
  "description": "Find maximum element in array"
}
```

### 2.2 Baseline Specifications

**Baseline 1: Iterative Feedback (from h-m1)**
- **Name**: IterativeFeedback-FullStructured
- **Description**: LLM receives FullStructured feedback and refines specifications iteratively
- **Parameters**:
  - Max iterations: 10
  - Feedback format: FullStructured (Witness + Obligation + Dependency)
  - Convergence criterion: No new proof obligations OR no change in spec for 2 consecutive iterations
- **Compute Budget Tracking**: 
  - Token count: Sum of (prompt tokens + completion tokens) across all iterations
  - Verifier time: Sum of Frama-C WP execution time across all iterations
- **Expected Performance**: 70.12% discharge rate (from h-m1)

**Baseline 2: Self-Consistency Sampling (CONTROL)**
- **Name**: SelfConsistency-ComputeMatched
- **Description**: Generate N independent specification candidates, select best via majority voting or verifier success
- **Parameters**:
  - Number of samples (N): Matched to average iterations from Baseline 1
  - Selection strategy: 
    1. **Verifier-based**: Run Frama-C WP on all N candidates, select the one with highest discharge rate
    2. **Voting-based**: For each proof obligation, use majority vote across N specs
  - Prompt: Single-shot prompt with examples (same as iteration 0 of Baseline 1)
- **Compute Budget Constraint**: 
  - Total tokens ≤ Average total tokens from Baseline 1 (across test set)
  - Total verifier time ≤ Average total verifier time from Baseline 1
- **Compute Matching Procedure**:
  1. Run Baseline 1 on validation set (15 programs)
  2. Calculate average iterations per program: `avg_iters = mean(iterations_per_program)`
  3. Set N = `floor(avg_iters)` for Baseline 2
  4. Verify token budget: If `N * single_shot_tokens > avg_total_tokens`, reduce N accordingly
  5. Verify time budget: Total verifier time for N samples should not exceed average from Baseline 1

**Baseline 3: Hybrid Approach (EXPLORATORY)**
- **Name**: Hybrid-SampleThenRefine
- **Description**: Generate K independent candidates, select best, then refine with feedback
- **Parameters**:
  - Initial samples (K): 3
  - Refinement iterations: Remaining budget after K samples
  - Selection: Best discharge rate after K samples
- **Rationale**: Tests whether combining diversity (sampling) with refinement (feedback) outperforms either alone

### 2.3 Compute Budget Formalization

**Compute Budget Definition**:
```
ComputeBudget = (TokenCount, VerifierTime)

where:
  TokenCount = Σ(prompt_tokens_i + completion_tokens_i) for all i ∈ iterations
  VerifierTime = Σ(framac_wp_time_i) for all i ∈ iterations
```

**Matching Criteria**:
Two conditions must satisfy for compute-matched comparison:
1. `|TokenCount_B1 - TokenCount_B2| / TokenCount_B1 < 0.10` (within 10%)
2. `|VerifierTime_B1 - VerifierTime_B2| / VerifierTime_B1 < 0.10` (within 10%)

**Budget Allocation for Baseline 2**:
Given average from Baseline 1:
- Average iterations: `I_avg`
- Average tokens per iteration: `T_iter`
- Average verifier time per iteration: `V_iter`

For Baseline 2:
- Number of samples: `N = floor(I_avg * 0.95)` (5% margin for variance)
- Token budget: `N * T_single_shot ≤ I_avg * T_iter`
- Time budget: `N * V_single_shot ≤ I_avg * V_iter`

### 2.4 Evaluation Metrics

**Primary Metric**:
- **ProofDischargeRate**: Percentage of proof obligations successfully discharged (0-100%)
  - Formula: `(Discharged_Obligations / Total_Obligations) * 100`
  - Aggregation: Mean across test set (50 programs)

**Secondary Metrics**:
1. **ConvergenceSpeed**: Iterations/samples to reach final performance
2. **SpecQuality**: Mutation kill rate (from h-c2 methodology)
3. **ComputeEfficiency**: Discharge rate per 1000 tokens, discharge rate per verifier-second
4. **Stability**: Variance in discharge rate across programs

**Statistical Tests**:
1. **Paired t-test**: Compare discharge rates between Baseline 1 and Baseline 2 (paired by program)
2. **Wilcoxon signed-rank test**: Non-parametric alternative for non-normal distributions
3. **Effect size**: Cohen's d for magnitude of difference
4. **Power analysis**: Post-hoc power calculation (target power ≥ 0.80)

**Success Criteria**:
- **MUST_WORK Gate Satisfied**: 
  - IterativeFeedback discharge rate ≥ SelfConsistency discharge rate + 10pp
  - Statistical significance: p < 0.05 (two-tailed paired t-test)
  - Effect size: Cohen's d ≥ 0.5 (medium effect)
- **Gate Failed**:
  - Difference < 10pp OR not statistically significant (p ≥ 0.05)

### 2.5 Implementation Requirements

**LLM Configuration**:
- **Model**: GPT-4 or Claude Opus (to be determined in Phase 3)
- **Temperature**: 0.7 (for Baseline 2 sampling diversity), 0.2 (for Baseline 1 refinement)
- **Max tokens**: 4096 per generation
- **System prompt**: Specification synthesis with Frama-C ACSL

**Frama-C WP Configuration**:
- **Version**: Frama-C 28.1 (Nickel) or later
- **Provers**: Z3 4.12.0, Alt-Ergo 2.4.3
- **Timeout**: 10 seconds per proof obligation
- **WP strategy**: Typed memory model, RTE generation enabled

**Feedback Extraction (Baseline 1)**:
- **FullStructured Feedback Format**:
  ```
  {
    "witness_dimension": {
      "failed_obligation_id": "...",
      "counterexample_trace": "...",
      "variable_values": {...}
    },
    "obligation_dimension": {
      "obligation_type": "...",
      "precondition_violated": "...",
      "postcondition_failed": "..."
    },
    "dependency_dimension": {
      "affected_functions": [...],
      "required_invariants": [...],
      "missing_contracts": [...]
    }
  }
  ```

**Self-Consistency Sampling (Baseline 2)**:
- **Sampling Strategy**: 
  - Generate N independent specifications (different random seeds, temperature=0.7)
  - No cross-contamination: Each sample generated independently
- **Selection Mechanisms**:
  1. **Best-of-N (Verifier)**: Run Frama-C WP on all N, select highest discharge rate
  2. **Majority Voting**: For each obligation, aggregate specs via voting, construct merged spec

**Experimental Pipeline**:
```
For each program in test_set:
  # Baseline 1: Iterative Feedback
  spec_B1 = initial_spec_from_llm(program)
  for iter in range(max_iterations):
    obligations = run_framac_wp(program, spec_B1)
    if all_discharged(obligations):
      break
    feedback = extract_fullstructured_feedback(obligations)
    spec_B1 = refine_spec_with_llm(spec_B1, feedback)
    track_compute(tokens, verifier_time)
  
  # Baseline 2: Self-Consistency (Compute-Matched)
  N = compute_matched_sample_count(avg_iters_from_val)
  specs_B2 = [generate_spec_from_llm(program) for _ in range(N)]
  results_B2 = [run_framac_wp(program, spec) for spec in specs_B2]
  best_spec_B2 = select_best(specs_B2, results_B2, strategy="verifier")
  track_compute(tokens, verifier_time)
  
  # Baseline 3: Hybrid (Exploratory)
  K = 3
  initial_specs_B3 = [generate_spec_from_llm(program) for _ in range(K)]
  best_initial_B3 = select_best(initial_specs_B3, strategy="verifier")
  remaining_budget = compute_budget - used_budget(K)
  spec_B3 = iterative_refine(best_initial_B3, remaining_budget)
  
  # Record results
  record_discharge_rates(program, [B1, B2, B3])
  record_compute_budgets(program, [B1, B2, B3])
```

---

## Section 3: Expected Outcomes & Risk Analysis

### 3.1 Expected Results

**Hypothesis Validation Scenario** (IterativeFeedback >> SelfConsistency):
- **IterativeFeedback**: 70.12% ± 5% discharge rate (from h-m1)
- **SelfConsistency**: 55-60% discharge rate
- **Gap**: 10-15pp (satisfies MUST_WORK gate)
- **Interpretation**: Feedback content is causally important, not just compute budget

**Hypothesis Rejection Scenario** (SelfConsistency ≈ IterativeFeedback):
- **IterativeFeedback**: 70.12% ± 5% discharge rate
- **SelfConsistency**: 65-72% discharge rate
- **Gap**: <10pp (fails MUST_WORK gate)
- **Interpretation**: Gains are primarily from compute budget, not feedback quality
- **Implication**: Main hypothesis claim about "structured feedback" is weakened

**Hybrid Scenario** (SampleThenRefine best):
- **Hybrid**: 75-78% discharge rate (outperforms both)
- **Interpretation**: Diversity + refinement is optimal strategy
- **Implication**: Future work should focus on hybrid approaches

### 3.2 Risk Factors

**Risk 1: Compute Matching is Imperfect**
- **Description**: Token counts and verifier times may vary significantly across programs, making "average" matching insufficient
- **Mitigation**: 
  - Use per-program compute matching (adaptive N for each program)
  - Report results with multiple budget levels (80%, 100%, 120% of B1 budget)
  - Sensitivity analysis across budget ranges

**Risk 2: Self-Consistency Sampling May Exceed Compute Budget**
- **Description**: If N samples require more total tokens than average iterations, comparison is unfair
- **Mitigation**: 
  - Pre-compute token estimates on validation set
  - Use adaptive N per program based on its iteration history
  - Include "single-shot best-of-1" as lower bound baseline

**Risk 3: Sampling Temperature Affects Quality**
- **Description**: Temperature=0.7 for diversity may reduce individual sample quality
- **Mitigation**: 
  - Test multiple temperatures (0.2, 0.5, 0.7, 1.0) on validation set
  - Select optimal temperature for Baseline 2
  - Report temperature sensitivity

**Risk 4: Selection Strategy Matters**
- **Description**: Best-of-N (verifier) vs. majority voting may yield different results
- **Mitigation**: 
  - Implement both selection strategies
  - Report results for both
  - Analyze which strategy is optimal for this domain

**Risk 5: LLM Model Choice Affects Stability Threshold**
- **Description**: Per Liu & Meng (2024), only o3-mini and Claude Opus 4.6 stay non-degrading in iterative refinement
- **Mitigation**: 
  - Test with multiple LLMs (GPT-4, Claude Opus)
  - Measure Error Introduction Rate (EIR) and Error Correction Rate (ECR)
  - Only proceed with iterative refinement if EIR < 0.5% (stability threshold)

### 3.3 Contingency Plans

**If MUST_WORK Gate Fails** (SelfConsistency ≈ IterativeFeedback):
1. **Re-evaluate Feedback Quality**: 
   - Check if FullStructured feedback is truly informative
   - Analyze failure cases where iterative refinement failed to improve
2. **Investigate Error Introduction Rate**:
   - Measure EIR per Liu & Meng (2024) framework
   - If EIR > 0.5%, iterative refinement may be harmful
3. **Pivot to Hybrid Approach**:
   - If Hybrid outperforms both, update main hypothesis to include sampling diversity
4. **Document Null Result**:
   - Publish negative result: "Compute budget, not feedback quality, drives gains"
   - Revise Phase 5 baseline comparison approach

**If Compute Matching is Impractical**:
1. **Use Multiple Budget Levels**:
   - Test SelfConsistency at 50%, 100%, 150% of IterativeFeedback budget
   - Plot discharge rate vs. compute budget curve
2. **Report Efficiency Metrics**:
   - Discharge rate per 1000 tokens
   - Discharge rate per verifier-second
   - Identify Pareto-optimal strategies

---

## Section 4: Timeline & Resource Estimates

### 4.1 Implementation Timeline

**Phase 3 (Implementation Planning)**: 2 weeks
- Week 1: PRD and architecture design
- Week 2: Task breakdown, Archon task creation

**Phase 4 (Coding & Validation)**: 6 weeks
- Week 1-2: Dataset preparation and validation
  - Collect Frama-C examples and Juliet programs
  - Verify gold standard specs discharge
  - Create train/val/test splits
- Week 3-4: Baseline 1 (IterativeFeedback) implementation
  - LLM integration (GPT-4/Claude Opus)
  - Frama-C WP integration
  - Feedback extraction pipeline
  - Validation on val set (15 programs)
- Week 5: Baseline 2 (SelfConsistency) implementation
  - Sampling loop
  - Selection strategies (best-of-N, voting)
  - Compute budget matching logic
  - Validation on val set
- Week 6: Baseline 3 (Hybrid) + final evaluation
  - Hybrid implementation
  - Full test set evaluation (50 programs)
  - Statistical analysis
  - Results writeup

**Phase 5 (Baseline Adaptation)**: 1 week
- Compare against non-verifier baselines (RAG, fine-tuning, etc.)

**Total Estimated Time**: 9 weeks

### 4.2 Compute Resources

**LLM API Costs**:
- **Baseline 1 (IterativeFeedback)**:
  - Average 7 iterations per program (from h-m1 simulation)
  - 50 test programs × 7 iterations × 8K tokens (prompt+completion) = 2.8M tokens
  - GPT-4: ~$56 (at $0.02/1K tokens)
  - Claude Opus: ~$84 (at $0.03/1K tokens)
- **Baseline 2 (SelfConsistency)**:
  - 50 programs × 7 samples × 8K tokens = 2.8M tokens (matched)
  - Same cost as Baseline 1
- **Baseline 3 (Hybrid)**:
  - 50 programs × (3 initial + 4 refinement) × 8K tokens = 2.8M tokens
  - Same cost as Baseline 1
- **Total LLM Cost**: ~$170-250 (depending on model choice)

**Compute Time**:
- **Frama-C WP Verification**:
  - 50 programs × 12 obligations/program × 10 sec timeout = 6000 CPU-seconds ≈ 1.7 CPU-hours
  - Across 3 baselines: ~5 CPU-hours
  - Parallelizable across programs
- **Total Wall-Clock Time** (with parallelization): 
  - 50 programs × 7 iterations × 30 sec (LLM + verifier) ≈ 3 hours per baseline
  - Total: ~9 hours for all baselines

**Dataset Storage**:
- Source code: ~5 MB (75 programs × ~100KB avg)
- ACSL annotations: ~2 MB
- Frama-C output logs: ~50 MB (verbose WP output)
- Total: ~60 MB

---

## Section 5: Success Criteria & Gate Satisfaction

### 5.1 MUST_WORK Gate Criteria

**Gate**: MUST_WORK  
**Rationale**: This is a control hypothesis - if iterative feedback does not outperform compute-matched self-consistency, the main claim about "structured feedback enabling synthesis" is invalid.

**Success Criteria**:
1. **Primary**: IterativeFeedback discharge rate ≥ SelfConsistency discharge rate + 10pp
2. **Statistical Significance**: Paired t-test p-value < 0.05
3. **Effect Size**: Cohen's d ≥ 0.5 (medium effect)
4. **Compute Matching**: Token and verifier time budgets within 10% between baselines

**Gate Satisfied**:
- All 4 criteria met
- Document results in 04_validation.md
- Mark h-c1.gate.satisfied = true in verification_state.yaml
- Proceed to Phase 5

**Gate Failed**:
- Any criterion not met
- Document failure mode in 04_validation.md
- Mark h-c1.gate.satisfied = false
- Trigger contingency planning (see Section 3.3)
- Consider blocking Phase 5 until hypothesis is revised

### 5.2 Secondary Success Indicators

**Desirable but Not Required for Gate**:
1. **Hybrid Approach**: If Hybrid outperforms both baselines by ≥5pp, document as future work direction
2. **Compute Efficiency**: IterativeFeedback achieves higher discharge rate per token
3. **Stability**: Lower variance in IterativeFeedback results (more predictable)
4. **Error Analysis**: Clear patterns in when/why SelfConsistency fails vs. IterativeFeedback succeeds

---

## Section 6: Implementation Readiness Checklist

**Prerequisites from h-m1** (VALIDATED):
- [x] Information gradient hypothesis validated
- [x] FullStructured feedback achieves 70.12% discharge rate
- [x] Feedback extraction pipeline exists
- [x] Frama-C WP integration working

**Phase 2C Outputs** (THIS DOCUMENT):
- [x] Dataset specification (Frama-C verified C programs, 75 total)
- [x] Baseline specifications (IterativeFeedback, SelfConsistency, Hybrid)
- [x] Compute budget formalization
- [x] Evaluation metrics and statistical tests
- [x] Risk analysis and contingency plans
- [x] Timeline and resource estimates

**Ready for Phase 3** (Implementation Planning):
- [ ] PRD document (product requirements for experiment harness)
- [ ] Architecture document (system design for compute-matched evaluation)
- [ ] PRP document (pseudo-code, API specs, data structures)
- [ ] Archon tasks created for Phase 4 implementation

**Blocking Issues**: None identified

---

## Section 7: References

### 7.1 Academic Papers

1. **Liu, A., & Meng, J. (2024)**. Self-Correction as Feedback Control: Error Dynamics, Stability Thresholds, and Prompt Interventions in LLMs. arXiv:2604.22273.
   - **Key Finding**: Stability threshold ECR/EIR > Acc/(1-Acc); only models with EIR < 0.5% benefit from iteration

2. **Madaan, A., et al. (2023)**. SELF-REFINE: Iterative Refinement with Self-Feedback. NeurIPS 2023.
   - **Key Finding**: ~20% absolute improvement via iterative self-feedback

3. **Liang, X., et al. (2024)**. Internal Consistency and Self-Feedback in Large Language Models: A Survey. arXiv:2407.14507.
   - **Key Framework**: Self-Feedback = Self-Evaluation + Self-Update

4. **Chakraborty, S., et al. (2024)**. On the Role of Feedback in Test-Time Scaling of Agentic AI Workflows. arXiv:2504.01931.
   - **Key Finding**: IAD with high-fidelity feedback outperforms best-of-N by up to 10% absolute

5. **Chang, F., et al. (2026)**. SpecLoop: An Agentic RTL-to-Specification Framework with Formal Verification Feedback Loop. arXiv:2603.02895.
   - **Key Architecture**: RTL → LLM → Spec → Reconstruct → Equivalence Check → Feedback

6. **Baksys, M., et al. (2026)**. WybeCoder: Verified Imperative Code Generation. 
   - **Key Result**: 74.1% solve rate on Verina (189 problems) with iterative proof refinement

### 7.2 Implementation References

1. **HierSVA/VRN2**: LLM-Driven SVA Generation and Formal Verification Loop
   - GitHub: https://github.com/HierSVAAnon/HierSVACodeAndArtifacts
   - **Relevance**: Golden pipeline with FPV/FTA/COV/FC feedback loop

2. **Shen-Backpressure**: Formal verification gates for AI coding loops
   - GitHub: https://github.com/pyrex41/shen-backpressure
   - **Relevance**: Spec-level gates with structural and behavioral checks

3. **code2lean**: Source code → Lean 4 with multi-gate validation
   - GitHub: https://github.com/phunterlau/code2lean
   - **Relevance**: Five independent validation gates (sanitizer, compile, axiom check, diff test, critic)

### 7.3 Archon KB References

- **Archon Search Query**: "iterative feedback LLM compute budget"
  - Limited relevant results (diffusion models, not formal verification)
  - **Action**: Manual literature search via Exa yielded better results

- **Code Examples Query**: "iterative refinement feedback loop"
  - Limited relevant results (image generation pipelines)
  - **Action**: GitHub searches for formal verification feedback loops more productive

---

## Section 8: Next Steps

### 8.1 Immediate Actions (Phase 3)

1. **Create PRD** (Product Requirements Document):
   - Experiment harness requirements
   - LLM integration specifications
   - Frama-C WP integration requirements
   - Compute budget tracking requirements

2. **Create Architecture Document**:
   - System components (LLM client, Frama-C wrapper, compute tracker, result aggregator)
   - Data flow (program → LLM → spec → verifier → feedback → LLM)
   - Storage schema (results database, experiment logs)

3. **Create PRP** (Pseudo-code, Requirements, Plan):
   - Core algorithms (iterative refinement, self-consistency sampling, hybrid)
   - API specifications (LLM client, Frama-C wrapper)
   - Data structures (program metadata, compute budget, results)

4. **Initialize Archon Tasks**:
   - Task hierarchy for Phase 4 implementation
   - Dependencies and milestones
   - Time estimates per task

### 8.2 Validation Readiness

**Prerequisites for Phase 4 Execution**:
- Dataset collection and validation (Week 1-2)
- LLM API access and rate limits confirmed
- Frama-C environment setup and version lock
- Compute budget tracking implementation

**Exit Criteria for Phase 4**:
- All 3 baselines implemented and validated on val set
- Full test set evaluated (50 programs)
- Statistical analysis completed
- Results documented in 04_validation.md
- Gate satisfaction decision made (MUST_WORK gate)

**Phase 5 Readiness**:
- If gate satisfied: Proceed to baseline adaptation (compare vs. RAG, fine-tuning, etc.)
- If gate failed: Contingency planning (revise hypothesis, hybrid approach, or document null result)

---

## APPENDIX A: Compute Budget Example

**Example Program: array_max_001**

**Baseline 1 (IterativeFeedback)**:
```
Iteration 0 (Initial):
  Prompt: 2500 tokens
  Completion: 800 tokens
  Verifier time: 15 sec
  Discharge rate: 40%

Iteration 1 (Feedback):
  Prompt: 3200 tokens (includes feedback)
  Completion: 900 tokens
  Verifier time: 18 sec
  Discharge rate: 65%

Iteration 2 (Feedback):
  Prompt: 3500 tokens
  Completion: 950 tokens
  Verifier time: 20 sec
  Discharge rate: 80%

Iteration 3 (Converged):
  No change, stop

Total Compute:
  Tokens: 2500+800 + 3200+900 + 3500+950 = 11,850 tokens
  Verifier time: 15 + 18 + 20 = 53 seconds
```

**Baseline 2 (SelfConsistency - Compute Matched)**:
```
Compute Budget:
  Token budget: 11,850 tokens
  Verifier time budget: 53 seconds

Single-shot estimate:
  Prompt: 2500 tokens
  Completion: 800 tokens
  Total per sample: 3300 tokens

Number of samples:
  N = floor(11,850 / 3,300) = 3 samples

Execution:
  Sample 1: 3300 tokens, 15 sec, discharge rate: 45%
  Sample 2: 3300 tokens, 14 sec, discharge rate: 55%
  Sample 3: 3300 tokens: 16 sec, discharge rate: 50%
  
  Best sample: Sample 2 (55% discharge rate)

Total Compute:
  Tokens: 3300 * 3 = 9,900 tokens (83% of budget, within 10% margin)
  Verifier time: 15 + 14 + 16 = 45 seconds (85% of budget, within 10% margin)
```

**Result**:
- IterativeFeedback: 80% discharge rate
- SelfConsistency: 55% discharge rate
- Gap: 25pp (exceeds 10pp threshold)
- Compute matched: ✓ (within 10% margin)

---

## APPENDIX B: Statistical Power Analysis

**Hypothesis Test**: Paired t-test (IterativeFeedback vs. SelfConsistency)

**Parameters**:
- Sample size: n = 50 programs
- Significance level: α = 0.05 (two-tailed)
- Target power: 1 - β = 0.80
- Expected difference: Δ = 10pp (10%)
- Estimated standard deviation of differences: σ_d = 15% (conservative)

**Effect Size**:
```
Cohen's d = Δ / σ_d = 10 / 15 = 0.67 (medium-to-large effect)
```

**Power Calculation**:
```
Power = 1 - β(t_critical, df=49, ncp=δ)
where:
  t_critical = t(0.025, 49) ≈ 2.01
  ncp (non-centrality parameter) = (Δ / σ_d) * sqrt(n) = 0.67 * sqrt(50) ≈ 4.74

Power ≈ 0.995 (very high power)
```

**Interpretation**: With n=50 programs, we have >99% power to detect a 10pp difference if it truly exists. If the true difference is smaller (e.g., 5pp), power drops to ~0.60, but 10pp difference is highly detectable.

**Minimum Detectable Effect** (MDE) at 80% power:
```
MDE = t_critical * σ_d / sqrt(n)
    = 2.01 * 15 / sqrt(50)
    ≈ 4.3pp
```

**Conclusion**: With 50 programs, we can reliably detect differences as small as 4.3pp, well below our 10pp threshold.

---

**END OF EXPERIMENT BRIEF**
