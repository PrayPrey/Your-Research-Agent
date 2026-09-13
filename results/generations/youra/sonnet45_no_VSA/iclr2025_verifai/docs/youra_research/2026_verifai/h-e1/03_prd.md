# Product Requirements Document: H-E1 Verifier-Feedback-Driven Specification Synthesis

**Date:** 2026-07-11  
**Hypothesis:** H-E1 - LLMs can utilize structured verifier feedback (witness + obligation + dependency dimensions) to iteratively refine formal specifications, achieving measurable improvement in proof discharge rate  
**Phase:** Phase 3 Implementation Planning  
**Experiment Brief:** 02c_experiment_brief.md  

---

## Executive Summary

**Goal:** Build a minimal proof-of-concept system demonstrating that large language models can iteratively improve formal specifications using structured verifier feedback from Frama-C/WP.

**Core Innovation:** Verifier-as-Teacher - the verifier provides pedagogical feedback (witness values, failed obligations, dependency violations) that guides the LLM to refine ACSL specifications without human intervention.

**Success Criteria (PoC):**
1. Iterative improvement: iteration N+1 proof discharge > iteration N
2. Final proof discharge ≥50% on minimal benchmark (5-10 programs)
3. Evidence that feedback dimensions are utilized in LLM responses

**Implementation Scope:** 3-stage simplified pipeline adapted from AutoSpec+ (ACL 2026):
- Stage 1: Neural Generation (LLM produces initial ACSL spec)
- Stage 2: Formal Verification (Frama-C/WP validates spec)
- Stage 3: Iterative Repair (LLM refines spec using structured feedback)

---

## Problem Statement

### Research Motivation

**Current State:** Formal verification requires expert-written specifications (ACSL, Dafny, etc.). Existing LLM approaches either:
1. Generate specifications without verification feedback (low quality)
2. Use verification as binary pass/fail (PropertyGPT, Astrogator)
3. Require expert knowledge bases (PropertyGPT)

**Gap:** No existing work demonstrates that **verifier feedback alone** (witness + obligation + dependency dimensions) can guide iterative LLM refinement to working specifications.

**Hypothesis H-E1 Tests:** Whether LLMs can parse and utilize three dimensions of verifier feedback:
1. **Witness Instantiation**: Concrete counterexample values
2. **Logical Structure**: Which proof obligation failed (precondition/postcondition/invariant)
3. **Dependency Preservation**: Inter-specification dependencies causing failures

### Downstream Impact

**If H-E1 succeeds:** Enables Wave 2 hypotheses testing mechanism optimizations (H-M1 information gradient, H-M2 staged synthesis)

**If H-E1 fails:** Core verifier-as-teacher thesis is invalidated; pivot to expert-guided synthesis

**GATE:** MUST_WORK - Failure blocks entire research program

---

## Functional Requirements

### FR1: Dataset Management

**FR1.1:** Download and preprocess FM-Bench-Verified dataset (280 programs)
- Load from HuggingFace: `fm-universe/FM-bench-verified`
- Extract C code and gold ACSL annotations separately
- Create 80/10/10 train/val/test splits (but only use 5-10 test programs for PoC)
- **No data augmentation** (formal verification requires exact code)

**FR1.2:** Select minimal benchmark subset (5-10 programs)
- Criteria: Diverse safety properties (bounds checks, null pointer checks, arithmetic overflow)
- Complexity: Range from simple (binary search) to moderate (linked list operations)
- Pre-verified: All must have gold ACSL that Frama-C/WP can prove
- Output: `benchmark_programs/` directory with `.c` files (unannotated)

**FR1.3:** Maintain gold ACSL ground truth
- Store in `ground_truth/` directory
- Use for post-hoc evaluation (not during synthesis)
- Format: Same as dataset (ACSL comments in C code)

### FR2: LLM Integration (Claude Opus 4.5)

**FR2.1:** Initial specification generation
- Input: Unannotated C program
- Prompt: Include ACSL grammar, few-shot examples (3-5), verification goal
- Model: `claude-opus-4-5`
- Temperature: 0.7 (initial generation)
- Max tokens: 4096
- Output: ACSL-annotated C code

**FR2.2:** Iterative refinement using feedback
- Input: Current ACSL spec + structured feedback (3 dimensions)
- Prompt: Include feedback interpretation guide, refinement strategies
- Model: `claude-opus-4-5`
- Temperature: 0.5 (refinement - lower for consistency)
- Max tokens: 4096
- Output: Refined ACSL-annotated C code

**FR2.3:** API configuration
- Authentication: Via `ANTHROPIC_API_KEY` environment variable
- Rate limiting: 1 req/second (Anthropic tier limits)
- Error handling: Retry on 429/500 errors (3 retries, exponential backoff)
- Cost tracking: Log token usage per program

### FR3: Frama-C/WP Verifier Integration

**FR3.1:** Verification execution
- Command: `frama-c -wp -wp-timeout 10 -wp-prover alt-ergo,z3 <annotated_c_file>`
- Solvers: Alt-Ergo 2.6.2, Z3 4.15.2 via Why3 1.8.2
- Timeout: 10 seconds per proof obligation
- Memory model: Typed (default WP model)
- Output: WP report with proof obligation status

**FR3.2:** Result parsing
- Extract total proof obligations (VCs)
- Extract proved obligations (Valid/Qed status)
- Calculate proof discharge rate: `(proved / total) × 100`
- Output: Structured result object

### FR4: Feedback Structure Extraction

**FR4.1:** Parse Frama-C/WP output for three dimensions
1. **Witness Instantiation** (Dimension 1):
   - Parse counterexample values from failed proofs
   - Format: Variable assignments that violate specification
   - Example: `x=5, y=-1` (invalid input causing assertion failure)

2. **Logical Structure** (Dimension 2):
   - Identify which proof obligation failed
   - Types: precondition, postcondition, loop invariant, assertion
   - Location: File + line number + function name
   - Example: `Postcondition at line 42 in function binary_search failed`

3. **Dependency Preservation** (Dimension 3):
   - Extract inter-specification dependencies
   - Example: Loop invariant depends on precondition assumption
   - Parse from WP dependency graph (if available)
   - Fallback: Heuristic dependency extraction (pre/post/inv relationships)

**FR4.2:** Feedback formatting for LLM
- Convert parsed dimensions to natural language
- Template: "Verification failed at [location]. Failed obligation: [type]. Counterexample: [witness]. Dependency violation: [clause]."
- Include guidance on how to fix (e.g., "Strengthen loop invariant to preserve postcondition")

### FR5: Iterative Refinement Loop

**FR5.1:** Convergence detection
- Success: All proof obligations proved (100% discharge rate)
- Failure: Max iterations reached (10 iterations)
- Early stopping: No improvement for 3 consecutive iterations

**FR5.2:** Iteration tracking
- Log proof discharge rate at each iteration
- Store all intermediate ACSL specs (for analysis)
- Track which feedback dimensions triggered refinements
- Output: `iteration_log.json` per program

**FR5.3:** Refinement orchestration
```python
for iteration in range(max_iterations=10):
    if all_proved:
        return spec, True
    feedback = extract_feedback(verification_result)
    spec = llm.refine(spec, feedback, iteration)
    verification_result = verifier.verify(spec)
return spec, False
```

### FR6: Evaluation Metrics

**FR6.1:** Primary metrics
1. **Proof Discharge Rate**: `(proved_VCs / total_VCs) × 100`
   - Measure at each iteration
   - Final value determines success (≥50% for PoC)

2. **Iterative Improvement**: `rate[N+1] > rate[N]`
   - Binary: Did at least 1 iteration show improvement?
   - Tracks mechanism validity

**FR6.2:** Secondary metrics
1. **Iterations to Convergence**: If converged, how many iterations?
2. **Feedback Dimension Utilization**: Which dimensions appeared in refinement prompts?
3. **Specification Coverage**: Count of preconditions/postconditions/invariants generated

**FR6.3:** Qualitative analysis
- Manual inspection of LLM responses
- Evidence that feedback was understood (not just random changes)
- Document specific examples where feedback led to correct refinement

### FR7: Visualization

**FR7.1:** Required gate metrics plot
- Bar chart: Target (50%) vs Actual proof discharge rate
- X-axis: Programs
- Y-axis: Proof discharge rate (%)
- Save: `h-e1/figures/gate_metrics_comparison.png`

**FR7.2:** Iteration progress plot
- Line chart: Proof discharge rate vs iteration
- Multiple lines (one per program)
- X-axis: Iteration number (0-10)
- Y-axis: Proof discharge rate (%)
- Save: `h-e1/figures/iteration_progress.png`

**FR7.3:** Feedback utilization heatmap
- Rows: Programs
- Columns: Witness | Obligation | Dependency
- Cell color: Frequency of dimension in refinement
- Save: `h-e1/figures/feedback_utilization.png`

**FR7.4:** Convergence histogram
- X-axis: Iterations to convergence
- Y-axis: Program count
- Save: `h-e1/figures/convergence_histogram.png`

### FR8: Experiment Execution

**FR8.1:** Batch processing
- Sequential execution (1 program at a time)
- Save all intermediate states (checkpointing)
- Graceful failure handling (log errors, continue to next program)

**FR8.2:** Result aggregation
- Combine metrics across all programs
- Calculate mean/median/std for proof discharge rate
- Generate summary statistics table
- Save: `h-e1/04_results.json`

**FR8.3:** Reproducibility
- Seed LLM temperature for variation (not deterministic but traceable)
- Log all API calls (prompts + responses)
- Save Frama-C/WP versions and solver versions
- Output: `h-e1/04_experiment_log.md`

---

## Non-Functional Requirements

### NFR1: Performance
- **LLM latency**: ≤30 seconds per API call (Claude Opus typical)
- **Verifier latency**: ≤10 seconds per proof obligation (configurable timeout)
- **Total runtime**: ≤2 hours for 5-10 programs (assuming 10 iterations × 10 programs)

### NFR2: Cost
- **LLM cost**: $0.002-$0.036 per program (from AutoSpec+ benchmarks)
- **Total budget**: ≤$0.50 for PoC (10 programs × $0.05 max)
- **Verifier cost**: Free (open-source Frama-C/WP)

### NFR3: Reliability
- **API error handling**: Retry on transient failures (3 attempts)
- **Verifier crash handling**: Log error, mark program as failed, continue
- **Data integrity**: Validate ACSL syntax before verification (avoid malformed input)

### NFR4: Maintainability
- **Code structure**: Modular (separate classes for LLM, Verifier, Feedback, Loop)
- **Logging**: Detailed logs for debugging (level: INFO for progress, DEBUG for internals)
- **Configuration**: YAML config file for all hyperparameters (not hardcoded)

### NFR5: Extensibility
- **Feedback dimensions**: Easy to add new dimensions (plugin architecture)
- **LLM backend**: Swappable (support GPT-4, Gemini via API abstraction)
- **Verifier backend**: Support future verifiers (Dafny, Boogie) via common interface

---

## Out of Scope (Phase 3)

### Explicitly NOT Implemented
1. **Proof-aware decomposition** (AutoSpec+ Stage 1): Simplified PoC omits call graph analysis
2. **Termination analysis** (AutoSpec+ Stage 5): Only functional correctness, not termination
3. **Multi-program dependencies**: Each program processed independently (no inter-program reasoning)
4. **Baseline comparisons**: Phase 4 only (no PropertyGPT/Astrogator implementation)
5. **Large-scale evaluation**: Full dataset (280 programs) reserved for post-PoC (if H-E1 succeeds)

### Future Extensions (if H-E1 succeeds)
1. **H-M1 (Information Gradient)**: Test which feedback dimensions are most effective
2. **H-M2 (Staged Synthesis)**: Bottom-up specification generation using call graphs
3. **Scale-up**: Expand to full FM-Bench (280 programs), ACSL by Example (126 programs)

---

## Dependencies

### External Dependencies
1. **Frama-C 29.0 (Copper)**: Formal verification framework
   - Installation: `opam install frama-c`
   - Version: ≥29.0 (compatibility with Why3 1.8.2)

2. **Why3 1.8.2**: Proof obligation manager
   - Installation: `opam install why3`
   - Solvers: Alt-Ergo 2.6.2, Z3 4.15.2

3. **Anthropic Python SDK**: LLM API client
   - Installation: `pip install anthropic`
   - Version: ≥0.18.0

4. **HuggingFace Datasets**: Dataset loader
   - Installation: `pip install datasets`
   - Version: ≥2.14.0

### Python Dependencies
```python
# requirements.txt
anthropic>=0.18.0
datasets>=2.14.0
matplotlib>=3.7.0
seaborn>=0.12.0
pyyaml>=6.0
```

### System Requirements
- **OS**: Linux (Ubuntu 22.04+) or macOS (Frama-C compatibility)
- **Python**: 3.10+
- **OCaml**: 4.14+ (for Frama-C/Why3)
- **Disk**: 5GB (dataset + intermediate results)
- **Memory**: 8GB RAM (verifier + LLM API calls)

---

## Acceptance Criteria

### PoC Success Conditions
1. **Code executes without errors** on all 5-10 benchmark programs
2. **Iterative improvement demonstrated**: At least 1 program shows `rate[N+1] > rate[N]`
3. **Minimum proof discharge**: Mean proof discharge rate ≥50% across benchmark
4. **Feedback utilization evidence**: Manual inspection confirms LLM uses feedback (not random changes)

### Deliverables Checklist
- [ ] `h-e1/03_prd.md` (this document)
- [ ] `h-e1/03_architecture.md` (system design)
- [ ] `h-e1/03_logic.md` (core algorithm pseudo-code)
- [ ] `h-e1/03_config.md` (hyperparameters + infrastructure)
- [ ] `h-e1/03_tasks.yaml` (implementation task list)
- [ ] Phase 4 validated code (after PoC execution)
- [ ] `h-e1/04_validation.md` (PoC results + gate decision)

### Gate Decision Criteria
- **PASS**: Mean proof discharge ≥50% AND iterative improvement demonstrated
- **FAIL**: Mean proof discharge <50% OR no iterative improvement
- **Consequence if FAIL**: Research program stops (MUST_WORK gate)

---

## Risk Assessment

### Technical Risks

**Risk 1: LLM cannot parse Frama-C/WP feedback**
- Probability: LOW (Frama-C output is semi-structured)
- Impact: HIGH (core hypothesis fails)
- Mitigation: Preprocess feedback into clear natural language templates
- Fallback: Simplify feedback to single dimension (failed obligation only)

**Risk 2: Proof discharge rate too low (baseline <50%)**
- Probability: MEDIUM (novel task for LLMs)
- Impact: HIGH (PoC fails)
- Mitigation: Select easier benchmark programs (simple algorithms)
- Fallback: Lower success threshold to 30% (document as limitation)

**Risk 3: LLM refinements are random (no feedback utilization)**
- Probability: MEDIUM (LLM may hallucinate)
- Impact: HIGH (mechanism hypothesis invalidated)
- Mitigation: Manual inspection + few-shot examples demonstrating feedback usage
- Fallback: Use prompted reasoning (chain-of-thought) to force feedback interpretation

### Operational Risks

**Risk 4: API rate limits / cost overrun**
- Probability: LOW (small benchmark)
- Impact: MEDIUM (delays, but not fatal)
- Mitigation: Implement rate limiting, checkpoint progress
- Fallback: Use cached results, reduce benchmark size

**Risk 5: Frama-C/WP crashes on malformed ACSL**
- Probability: MEDIUM (LLM may generate invalid syntax)
- Impact: LOW (can retry)
- Mitigation: ACSL syntax validation before verification
- Fallback: Log error, skip program, continue

---

## Timeline Estimate

**Total Duration:** 4 weeks (aligned with Phase 2B estimate)

**Week 1-2:** Implementation (Phase 4 Coder)
- LLM integration + prompt engineering (3 days)
- Frama-C/WP integration + feedback parser (4 days)
- Iterative refinement loop + logging (3 days)

**Week 3:** Validation (Phase 4 Validator)
- Static analysis (syntax checks, dependency validation) (2 days)
- Runtime execution on benchmark (3 days)
- Debugging and fixes (2 days)

**Week 4:** Analysis + Gate Decision
- Metric computation + visualization (2 days)
- Manual inspection of LLM responses (2 days)
- Write 04_validation.md report (1 day)
- Gate decision meeting (1 day)

---

## Appendix: Reference Implementations

### AutoSpec+ (Primary Reference)
- **Repository**: https://github.com/Xidian-ICTT-GZ/AutoSpec
- **Paper**: AutoSpec+: LLM-Driven Neuro-Symbolic Program Specification Synthesis (ACL 2026)
- **Relevant Components**:
  - `auto_run.py`: Batch verification orchestrator
  - `configs/func_config.json`: Specification generation config
  - `configs/loop_config.yaml`: Loop invariant config
  - Feedback parsing logic (implicit in refinement prompts)

### Frama-C/WP Documentation
- **API**: https://www.frama-c.com/api/frama-c-wp/Wp/index.html
- **Manual**: https://www.frama-c.com/download/wp-manual-29.0-Copper.pdf
- **Key Modules**: `Wp.VC` (proof obligations), `Wp.VCS` (results)

### FM-Bench-Verified Dataset
- **HuggingFace**: https://huggingface.co/datasets/fm-universe/FM-bench-verified
- **Content**: 280 verified C programs with gold ACSL
- **Loading**: `from datasets import load_dataset; dataset = load_dataset("fm-universe/FM-bench-verified")`

---

**PRD Version:** 1.0  
**Approved for Phase 3 Architecture Design:** Pending  
**Next Step:** Generate 03_architecture.md, 03_logic.md, 03_config.md via specialized agents
