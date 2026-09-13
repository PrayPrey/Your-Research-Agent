# Implementation Task List: H-E1 Verifier-Feedback-Driven Specification Synthesis

**Date:** 2026-07-11  
**Hypothesis:** H-E1 - LLMs can utilize structured verifier feedback to iteratively refine formal specifications  
**Phase:** Phase 3 → Phase 4 Handoff  
**Total Complexity:** 80 points (from 03_architecture.md)  
**Estimated Duration:** 4 weeks  

---

## Task Allocation Strategy

Based on 03_architecture.md Epic breakdown (7 major components):

| Component | Complexity | Priority | Dependencies |
|-----------|-----------|----------|--------------|
| T-1: Dataset Setup | 8 | P0 (Critical Path) | None |
| T-2: LLM Client | 13 | P0 (Critical Path) | T-1 |
| T-3: Verifier Integration | 16 | P0 (Critical Path) | T-1 |
| T-4: Feedback Parser | 14 | P0 (Critical Path) | T-3 |
| T-5: Refinement Loop | 12 | P0 (Critical Path) | T-2, T-4 |
| T-6: Metrics & Visualization | 9 | P1 (Post-MVP) | T-5 |
| T-7: Experiment Runner | 8 | P1 (Integration) | All |

**Total:** 80 complexity points across 7 tasks

---

## Critical Path Tasks (P0)

### T-1: Dataset Setup and Preprocessing
**Complexity:** 8 points  
**Duration:** 2 days  
**Owner:** Phase 4 Coder  
**Prerequisites:** None  

**Subtasks:**
1. Install HuggingFace `datasets` library
2. Download FM-Bench-Verified dataset (`fm-universe/FM-bench-verified`)
3. Extract C code and ACSL annotations separately
4. Select minimal benchmark subset (5-10 programs):
   - Criteria: Diverse safety properties (bounds, null checks, overflow)
   - Complexity: Simple (binary search) to moderate (linked lists)
   - Pre-verified: Gold ACSL that Frama-C/WP can prove
5. Create directory structure:
   ```
   data/
     benchmark_programs/  # Unannotated C files
     ground_truth/        # Gold ACSL specs (for evaluation only)
     raw/                 # Original FM-Bench data
   ```
6. Validate files: Ensure all benchmark programs compile and gold specs verify
7. Document dataset statistics (LOC, function count, VC count per program)

**Deliverables:**
- `data/benchmark_programs/*.c` (5-10 unannotated C programs)
- `data/ground_truth/*.c` (corresponding gold ACSL specs)
- `data/dataset_stats.json` (statistics)

**Validation Criteria:**
- All unannotated programs compile with `gcc -c`
- All gold specs verify with `frama-c -wp` (100% proof discharge)
- Benchmark size: 5-10 programs (not less, not more)

---

### T-2: LLM Client Implementation
**Complexity:** 13 points  
**Duration:** 3 days  
**Owner:** Phase 4 Coder  
**Prerequisites:** T-1 (for testing with real C programs)  

**Subtasks:**
1. Install Anthropic Python SDK (`anthropic>=0.18.0`)
2. Implement `LLMClient` class (from 03_architecture.md):
   - `__init__(api_key, model="claude-opus-4-5")`
   - `generate_specification(c_code, temperature=0.7)` → ACSL spec
   - `refine_specification(c_code, current_spec, feedback, iteration, temperature=0.5)` → refined ACSL spec
3. Build ACSL generation prompt (from 03_logic.md A-1):
   - Include ACSL grammar summary
   - Add 2-3 few-shot examples (from FM-Bench gold specs)
   - Specify verification goal (functional correctness)
4. Build refinement prompt (from 03_logic.md A-4):
   - Include current spec + structured feedback (3 dimensions)
   - Add iteration number for context
   - Provide refinement strategies (strengthen invariant, weaken precondition, etc.)
5. Implement response parsing:
   - Extract ACSL-annotated code from markdown blocks
   - Parse individual ACSL clauses (requires, ensures, loop invariant)
6. Implement error handling:
   - API failures → retry with exponential backoff (3 attempts)
   - Rate limiting → respect 1 req/sec limit
   - Malformed responses → log warning, request regeneration
7. Add token usage tracking (for cost analysis)
8. Write unit tests:
   - Mock Anthropic API responses
   - Test prompt construction
   - Test response parsing (valid + edge cases)

**Deliverables:**
- `src/llm_client.py` (LLMClient class)
- `src/prompts/generation_template.txt` (ACSL generation prompt)
- `src/prompts/refinement_template.txt` (ACSL refinement prompt)
- `tests/test_llm_client.py` (unit tests)

**Validation Criteria:**
- Unit tests pass (100% coverage for critical paths)
- End-to-end test: Generate spec for 1 benchmark program
- Token usage logged correctly
- API errors handled gracefully (no crashes)

---

### T-3: Frama-C/WP Verifier Integration
**Complexity:** 16 points (HIGHEST)  
**Duration:** 4 days  
**Owner:** Phase 4 Coder  
**Prerequisites:** T-1 (for testing with real programs)  

**Subtasks:**
1. Validate environment setup:
   - Frama-C 29.0 (Copper) installed via `opam`
   - Why3 1.8.2 installed
   - Alt-Ergo 2.6.2 and Z3 4.15.2 configured
2. Implement `FramaCVerifier` class (from 03_architecture.md):
   - `__init__(timeout=10, solvers=["alt-ergo", "z3"])`
   - `verify(annotated_c_file)` → VerificationResult
3. Build Frama-C command (from 03_config.md):
   ```bash
   frama-c -wp -wp-timeout 10 -wp-prover alt-ergo,z3 -wp-out <output_dir> <c_file>
   ```
4. Execute via subprocess:
   - Timeout handling (10s per VC, 300s global)
   - Stderr/stdout capture
   - Exit code checking
5. Implement VerificationResult parser (from 03_logic.md A-2):
   - Parse JSON report (if available): `frama-c -wp -wp-report-json`
   - Fallback: Parse text output for "goal", "Valid", "Qed" keywords
   - Extract total VCs, proved VCs, failed VCs (with IDs)
6. Calculate proof discharge rate: `(proved / total) × 100`
7. Implement error handling:
   - Frama-C crashes → log error, return empty result
   - Timeout → mark as "timeout", continue
   - Malformed ACSL → parse error, return diagnostic
8. Write integration tests:
   - Test with gold ACSL specs (should achieve 100% discharge)
   - Test with empty spec (should achieve 0% discharge)
   - Test with partially correct spec (should achieve 50-80% discharge)

**Deliverables:**
- `src/verifier.py` (FramaCVerifier + VerificationResult classes)
- `tests/test_verifier.py` (integration tests with real Frama-C)

**Validation Criteria:**
- Gold ACSL specs achieve 100% proof discharge (sanity check)
- Empty specs achieve 0% proof discharge
- Parser correctly extracts VC counts from Frama-C output
- No subprocess hangs (timeout enforced)

---

### T-4: Feedback Parser (3 Dimensions)
**Complexity:** 14 points (CRITICAL - Core hypothesis mechanism)  
**Duration:** 4 days  
**Owner:** Phase 4 Coder  
**Prerequisites:** T-3 (requires VerificationResult)  

**Subtasks:**
1. Implement `FeedbackParser` class (from 03_architecture.md):
   - `extract_feedback(verification_result)` → StructuredFeedback
   - `format_for_llm(structured_feedback)` → natural language string
2. **Dimension 1: Witness Instantiation** (from 03_logic.md A-3):
   - Parse counterexample values from failed VC output
   - Regex patterns for variable assignments (e.g., `x=5, y=-1`)
   - Handle missing counterexamples (some solvers don't provide them)
   - Format: `{"x": "5", "y": "-1"}` (dict of variable → value)
3. **Dimension 2: Logical Structure** (from 03_logic.md A-3):
   - Identify failed obligation type: precondition, postcondition, loop invariant, assertion
   - Extract location: file, line number, function name
   - Parse from VC goal description (e.g., "ensures clause at line 42")
   - Format: `{"type": "postcondition", "location": "file.c:42", "function": "binary_search"}`
4. **Dimension 3: Dependency Preservation** (from 03_logic.md A-3):
   - Extract inter-specification dependencies (heuristic-based for PoC)
   - Patterns:
     - Loop invariant depends on precondition (if inv uses pre variables)
     - Postcondition depends on loop invariant (if post uses inv variables)
   - Fallback: Parse WP dependency graph (if available in output)
   - Format: `{"depends_on": ["precondition at line 10"], "violates": "postcondition at line 42"}`
5. Implement natural language formatting (for LLM consumption):
   - Template: "Verification failed at {location}. Failed obligation: {type}. Counterexample: {witness}. Dependency violation: {dependency}."
   - Include refinement guidance: "Strengthen loop invariant to preserve postcondition"
6. Handle edge cases:
   - No counterexample provided → use generic guidance
   - Multiple failed VCs → prioritize first failure (or aggregate feedback)
   - Ambiguous obligation type → default to "assertion"
7. Write unit tests:
   - Mock VerificationResult with known failures
   - Test each dimension extraction independently
   - Test natural language formatting

**Deliverables:**
- `src/feedback_parser.py` (FeedbackParser + StructuredFeedback classes)
- `tests/test_feedback_parser.py` (unit tests)
- `docs/feedback_dimension_examples.md` (documented examples for each dimension)

**Validation Criteria:**
- All 3 dimensions extracted for at least 1 failed VC
- Natural language feedback is LLM-readable (manual inspection)
- Edge cases handled (missing counterexamples, ambiguous types)
- Unit tests pass

---

### T-5: Iterative Refinement Loop
**Complexity:** 12 points  
**Duration:** 3 days  
**Owner:** Phase 4 Coder  
**Prerequisites:** T-2 (LLM Client), T-4 (Feedback Parser)  

**Subtasks:**
1. Implement `RefinementLoop` class (from 03_architecture.md):
   - `__init__(llm_client, verifier, feedback_parser, max_iterations=10)`
   - `run(c_program, program_id)` → (final_spec, metrics)
2. Algorithm implementation (from 03_logic.md A-4):
   ```python
   for iteration in range(max_iterations):
       if all_proved: return spec, True
       feedback = feedback_parser.extract_feedback(verification_result)
       spec = llm_client.refine(spec, feedback, iteration)
       verification_result = verifier.verify(spec)
   return spec, False
   ```
3. Convergence detection (3 conditions):
   - **Success**: `verification_result.all_proved == True` (100% discharge)
   - **Max iterations**: `iteration >= max_iterations` (default 10)
   - **Early stopping**: No improvement for 3 consecutive iterations
4. Iteration tracking:
   - Log proof discharge rate at each iteration
   - Store intermediate ACSL specs (for analysis)
   - Track which feedback dimensions triggered refinements
5. Checkpointing (every iteration):
   - Save current spec to `results/{program_id}/iteration_{n}.c`
   - Save metrics to `results/{program_id}/iteration_log.json`
   - Allow resume from checkpoint (if experiment crashes)
6. Implement metrics collection:
   - Per-iteration: discharge rate, iteration number, timestamp
   - Per-dimension: witness_used, obligation_used, dependency_used (boolean flags)
   - Aggregate: total iterations, converged (boolean), final discharge rate
7. Error handling:
   - LLM API failure mid-loop → retry current iteration (3 attempts)
   - Verifier crash → mark iteration as failed, continue
   - Malformed ACSL from LLM → log warning, request regeneration
8. Write integration tests:
   - Test with mock LLM (returns improving specs)
   - Test convergence detection (all 3 conditions)
   - Test checkpointing (save + resume)

**Deliverables:**
- `src/refinement_loop.py` (RefinementLoop class)
- `tests/test_refinement_loop.py` (integration tests)

**Validation Criteria:**
- End-to-end test: Run on 1 benchmark program, achieves >0% improvement
- Convergence detection works (unit tests confirm)
- Checkpointing saves all required data
- Metrics logged correctly at each iteration

---

## Post-MVP Tasks (P1)

### T-6: Metrics Tracking and Visualization
**Complexity:** 9 points  
**Duration:** 2 days  
**Owner:** Phase 4 Coder  
**Prerequisites:** T-5 (requires completed experiment data)  

**Subtasks:**
1. Implement `MetricsTracker` class (from 03_architecture.md):
   - `aggregate_results(program_results)` → aggregate metrics
   - `calculate_statistics(discharge_rates)` → mean/median/std
2. Compute primary metrics (from 03_prd.md FR6):
   - **Proof Discharge Rate**: Mean across all programs
   - **Iterative Improvement**: Binary flag (did any program improve?)
3. Compute secondary metrics:
   - Iterations to convergence (mean)
   - Feedback dimension utilization (count per dimension)
   - Specification coverage (preconditions, postconditions, invariants)
4. Implement `Visualizer` class (from 03_architecture.md):
   - `plot_gate_metrics(target, actual)` → bar chart
   - `plot_iteration_progress(program_results)` → line chart
   - `plot_feedback_heatmap(dimension_usage)` → heatmap
   - `plot_convergence_histogram(iterations_list)` → histogram
5. Save all figures to `h-e1/figures/*.png` (from 03_prd.md FR7)
6. Generate summary statistics table:
   - Program ID | Final Discharge Rate | Iterations | Converged
   - Save to `h-e1/04_results.json`
7. Write unit tests:
   - Test metric calculations with mock data
   - Test plot generation (ensure files created)

**Deliverables:**
- `src/metrics_tracker.py` (MetricsTracker class)
- `src/visualizer.py` (Visualizer class)
- `h-e1/figures/gate_metrics_comparison.png` (required)
- `h-e1/figures/iteration_progress.png`
- `h-e1/figures/feedback_utilization.png`
- `h-e1/figures/convergence_histogram.png`
- `h-e1/04_results.json`

**Validation Criteria:**
- All 4 plots generated and saved
- Summary statistics match manual calculations
- Gate metrics comparison shows target (50%) vs actual

---

### T-7: Experiment Runner (End-to-End Orchestration)
**Complexity:** 8 points  
**Duration:** 2 days  
**Owner:** Phase 4 Coder  
**Prerequisites:** All tasks (T-1 through T-6)  

**Subtasks:**
1. Implement `ExperimentRunner` class (from 03_architecture.md):
   - `run_experiment(config)` → experiment results
2. Load configuration from `config.yaml` (from 03_config.md):
   - Use `ExperimentConfig.from_yaml("config.yaml")`
3. Sequential batch processing:
   - For each program in benchmark:
     1. Load unannotated C code
     2. Run refinement loop
     3. Save results (checkpointed)
     4. Log progress
4. Graceful error handling:
   - Program failure → log error, continue to next program
   - Keyboard interrupt → save partial results, exit
5. Aggregate results across all programs:
   - Combine per-program metrics
   - Calculate aggregate statistics
   - Generate visualizations
6. Generate experiment log (from 03_prd.md FR8.3):
   - Frama-C/WP versions
   - Solver versions
   - LLM model and temperature settings
   - Total API calls and token usage
   - Total cost
   - Save to `h-e1/04_experiment_log.md`
7. Write end-to-end test:
   - Run on 2 programs (not full benchmark)
   - Verify all outputs generated
   - Check cost is within budget

**Deliverables:**
- `src/experiment_runner.py` (ExperimentRunner class)
- `main.py` (CLI entry point)
- `h-e1/04_experiment_log.md` (reproducibility log)
- `tests/test_experiment_runner.py` (end-to-end test)

**Validation Criteria:**
- End-to-end test passes (2 programs complete successfully)
- All outputs generated (results, figures, logs)
- Graceful error handling (test with invalid program)
- Cost tracking accurate (compare with Anthropic API logs)

---

## Implementation Budget Allocation

**Total Budget:** 80 complexity points over 4 weeks

| Week | Tasks | Focus | Points |
|------|-------|-------|--------|
| Week 1 | T-1, T-2, T-3 | Dataset + Core Components | 37 points |
| Week 2 | T-4, T-5 | Feedback Parser + Refinement Loop | 26 points |
| Week 3 | T-6, T-7 | Metrics + Integration | 17 points |
| Week 4 | Validation + Debugging | Phase 4 Validator | - |

**Critical Path:** T-1 → T-2 → T-5 → T-6 → T-7 (Dataset → LLM → Loop → Metrics → Runner)  
**Parallel Track:** T-3 → T-4 → T-5 (Verifier → Feedback → Loop)

**Bottleneck:** T-3 (Verifier Integration) - 16 points, most complex, requires Frama-C expertise

---

## Acceptance Criteria (Handoff to Phase 4 Validator)

### Code Completeness
- [ ] All 7 tasks implemented (T-1 through T-7)
- [ ] Unit tests pass for all components
- [ ] Integration tests pass (end-to-end with 2 programs)
- [ ] No TODOs or placeholder code

### Functional Requirements
- [ ] LLM generates ACSL specs (T-2)
- [ ] Frama-C/WP verifies specs (T-3)
- [ ] Feedback parser extracts 3 dimensions (T-4)
- [ ] Refinement loop iterates and converges (T-5)
- [ ] Metrics calculated and visualized (T-6)
- [ ] Full experiment runs on 5-10 programs (T-7)

### PoC Success Criteria (from 03_prd.md)
- [ ] Code executes without errors on all benchmark programs
- [ ] At least 1 program shows iterative improvement (`rate[N+1] > rate[N]`)
- [ ] Mean proof discharge rate ≥50% across benchmark
- [ ] Evidence of feedback utilization (manual inspection confirms)

### Deliverables Checklist
- [ ] `h-e1/03_prd.md` ✅ (already completed)
- [ ] `h-e1/03_architecture.md` ✅ (already completed)
- [ ] `h-e1/03_logic.md` ✅ (already completed)
- [ ] `h-e1/03_config.md` ✅ (already completed)
- [ ] `h-e1/03_implementation_tasks.md` ✅ (this document)
- [ ] Working code (Phase 4 Coder deliverable)
- [ ] `h-e1/04_validation.md` (Phase 4 Validator deliverable)

---

## Risk Mitigation

### Technical Risks

**Risk 1: Frama-C/WP output parsing is brittle**
- Mitigation: Implement dual parser (JSON + text fallback)
- Contingency: Manual inspection of failed parses, update regex patterns
- Owner: T-3 (Verifier Integration)

**Risk 2: LLM generates syntactically invalid ACSL**
- Mitigation: ACSL syntax validation before verification (regex pre-check)
- Contingency: Regenerate spec with stronger prompt constraints
- Owner: T-2 (LLM Client)

**Risk 3: Feedback dimensions are not extractable from WP output**
- Mitigation: Heuristic fallback for missing dimensions
- Contingency: Simplify to 1 dimension (failed obligation only)
- Owner: T-4 (Feedback Parser)

### Operational Risks

**Risk 4: API rate limits during benchmark run**
- Mitigation: 1 req/sec rate limiting built into LLMClient
- Contingency: Checkpointing allows resume after rate limit reset
- Owner: T-2, T-7 (LLM Client + Runner)

**Risk 5: Experiment runtime exceeds 2 hours**
- Mitigation: Reduce benchmark size to 5 programs (not 10)
- Contingency: Run overnight, use checkpointing
- Owner: T-7 (Experiment Runner)

---

## Handoff Notes for Phase 4

### For Phase 4 Coder
1. **Start with T-1 (Dataset Setup)** - No dependencies, quick win
2. **Prioritize T-3 (Verifier Integration)** - Highest complexity, longest pole
3. **Use 03_logic.md pseudo-code directly** - Copy-paste API signatures
4. **Reference AutoSpec+ repo for inspiration** - https://github.com/Xidian-ICTT-GZ/AutoSpec
5. **Test incrementally** - Don't wait until all tasks are done to run end-to-end

### For Phase 4 Validator
1. **Static Analysis Focus:**
   - Verify all API signatures match 03_logic.md
   - Check error handling coverage (LLM failures, verifier crashes)
   - Validate ACSL syntax checking before verification
2. **Runtime Execution Focus:**
   - Run end-to-end test on 2 benchmark programs
   - Verify proof discharge calculation is correct (compare with manual `frama-c` run)
   - Check all 4 plots are generated
3. **Gate Decision:**
   - If mean discharge ≥50% AND iterative improvement shown → PASS
   - If mean discharge <50% OR no improvement → FAIL (document in 04_validation.md)

---

**Task List Complete**  
**Ready for Phase 4 Implementation**  
**Next Step:** Execute tasks T-1 through T-7 in sequence, then validate with Phase 4 Validator
