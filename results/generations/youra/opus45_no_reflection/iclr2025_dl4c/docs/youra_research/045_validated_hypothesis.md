# Validated Hypothesis Synthesis

**Generated:** 2026-08-18
**Workflow:** Phase 4.5 Hypothesis Synthesis 
**Pipeline Position:** Phase 4 (Hypothesis Loop) → [Phase 4.5] → Phase 5/6

---

## 1. Executive Summary

The EVAF (Execution-Verified AI Feedback) hypothesis validation **failed** at the existence proof-of-concept stage. The experiment infrastructure crashed at 53% completion (87/164 HumanEval problems), preventing any measurement of the core accept rate metric. No predictions could be evaluated. The hypothesis remains **untested** rather than refuted — the failure was operational (infrastructure) not theoretical (mechanism disproven).

| Metric | Value |
|--------|-------|
| **Original Core Statement** | EVAF combines execution verification with AI feedback for code alignment |
| **Refined Core Statement** | EVAF mechanism implementable but requires infrastructure hardening |
| **Predictions Supported** | 0 / 3 |
| **Overall Pass Rate** | 0% |
| **Hypotheses Validated** | 0 / 4 |

---

## 2. Prediction-Result Matrix

| Prediction | Original Statement | Tested By | Key Metric | Result | Status | Confidence | Evidence Summary |
|------------|-------------------|-----------|------------|--------|--------|------------|------------------|
| **P1** | On semantic-error-prone problems, EVAF achieves higher pass@1 than Exec-Fine | h-m3 (dependent) | pass@1 OR ≥ 1.5 | N/A | **INCONCLUSIVE** | 0% | Blocked — h-e1 failed |
| **P2** | On semantic-error-prone problems, EVAF achieves higher pass@1 than AI-Only | h-m3 (dependent) | β(EVAF) > β(AI-Only) | N/A | **INCONCLUSIVE** | 0% | Blocked — h-e1 failed |
| **P3** | On syntactic-error-prone problems, Exec-Fine is non-inferior to EVAF | h-m3 (dependent) | Exec-Fine within 3pp | N/A | **INCONCLUSIVE** | 0% | Blocked — h-e1 failed |

**Status Legend:** SUPPORTED | PARTIALLY_SUPPORTED | REFUTED | INCONCLUSIVE

### Causal Mechanism Verification

| Mechanism Step | Description | Falsifier | Evidence | Verification Status |
|----------------|-------------|-----------|----------|---------------------|
| 1 | AI feedback generator produces semantically rich code critique | AI feedback contains no actionable suggestions | CodeLlama-7b-Instruct loaded, generated feedback for 87 problems before crash | PARTIAL (infrastructure issue, not mechanism) |
| 2 | Some AI suggestions are incorrect (~61% wrong fix rate) | AI feedback >90% accurate | Not measured — experiment incomplete | NOT_TESTED |
| 3 | Execution gating applies AI suggestion and runs unit tests | Unit tests too slow/unavailable | Gating code complete, ran for 87 problems | PARTIAL |
| 4 | Suggestions breaking tests rejected, passing accepted | False accept rate >50% | Not measured | NOT_TESTED |
| 5 | Filtered feedback retains semantic richness with high fidelity | Accept rate <10% or >90% | Not measured | NOT_TESTED |
| 6 | Model learns WHAT and HOW to fix | No improvement over pure execution | Training phase not reached | NOT_TESTED |

---

## 3. Hypothesis Refinement

### 3.1 Original Core Statement (Phase 2A)

> Under post-training alignment of code generation models using CodeT5-770M on HumanEval/MBPP benchmarks, if we apply Execution-Verified AI Feedback (EVAF)—where AI-generated code critiques are filtered through unit test execution before being used as training signals—then EVAF will achieve significantly higher pass@1 than pure execution feedback on problems where the baseline model primarily fails due to semantic errors, because EVAF combines ground-truth verification with rich semantic guidance.

### 3.2 Refined Core Statement (Phase 4.5)

> The EVAF mechanism is **implementable** using existing components (CodeT5-770M, CodeLlama-7b-Instruct, sandboxed test execution), but requires **infrastructure hardening** before experimental validation is possible. The core hypothesis remains untested. Key implementation exists but runtime stability failed at scale (87/164 problems). The theoretical basis remains plausible but **cannot be claimed as validated**.

**Key Changes:**
1. **REMOVED:** All performance claims (pass@1 improvement, OR ≥ 1.5)
2. **WEAKENED:** "Will achieve" → "May achieve if infrastructure stabilized"
3. **ADDED:** Infrastructure stability as prerequisite for any claims
4. **RETAINED:** Theoretical mechanism (fidelity × richness orthogonality) as motivating framework

### 3.3 Causal Mechanism — Verified Chain

```
[PARTIAL] Step 1: AI feedback generator produces critique
    ↓
[NOT_TESTED] Step 2: Some AI suggestions incorrect
    ↓
[PARTIAL] Step 3: Execution gating runs tests
    ↓
[NOT_TESTED] Step 4: Accept/reject based on results
    ↓
[NOT_TESTED] Step 5: Filtered feedback retains value
    ↓
[NOT_TESTED] Step 6: Model learns better
```

**Removed/Modified Steps:**
- **Step 6** (Model learns WHAT and HOW): DEFERRED — training phase never reached due to h-e1 failure

### 3.4 Claims Removed or Weakened

| Original Claim | Action | Reason | Evidence |
|----------------|--------|--------|----------|
| EVAF achieves significantly higher pass@1 than Exec-Fine | REMOVED | No experimental data | Experiment crashed before metrics |
| Accept rate 20-60% is achievable | WEAKENED to "plausible" | Not measured | 87/164 samples processed, no aggregate |
| EVAF combines fidelity and richness | RETAINED as theoretical | Mechanism not disproven | Implementation code exists |

### 3.5 Assumptions Status

| Assumption | Original Status | Verification Status | Evidence | Impact if Violated |
|------------|----------------|---------------------|----------|-------------------|
| A1: Error type distribution stable across training | ASSUMED | NOT_TESTED | Training not reached | Stratification invalid |
| A2: AI feedback errors detectable via test execution | ASSUMED | NOT_TESTED | Gating ran but no aggregate | Cannot filter bad suggestions |
| A3: Accept rate 20-60% sufficient for learning | ASSUMED | NOT_TESTED | No accept rate measured | EVAF degenerates to exec-only |
| A4: HumanEval tests sufficient to catch regressions | ASSUMED | PARTIALLY_VERIFIED | Tests ran for 87 problems | False accepts corrupt training |
| A5: CodeT5-770M has capacity for richer feedback | ASSUMED | NOT_TESTED | Training not reached | Model cannot utilize guidance |

---

## 4. Theoretical Interpretation

### 4.1 Mechanistic Explanation (Experiment-Verified)

**No verified mechanistic explanation available.** The experiment did not complete, so no causal claims can be made with empirical support.

**Theoretical framework remains:**
- Execution feedback provides high fidelity but low semantic richness
- AI feedback provides high richness but low fidelity (~61% wrong fix rate)
- EVAF proposes using execution as a filter for AI feedback (gating)
- This remains a plausible hypothesis awaiting proper experimental validation

### 4.2 Unexpected Findings Analysis

#### Finding: Infrastructure Crash at 53%

- **Observation:** Experiment process stalled at iteration 87/164 during EVAF gating phase
- **Why Unexpected:** Implementation code passed all unit tests; infrastructure failure at runtime
- **Competing Explanations:**
  1. **GPU OOM:** CodeLlama-7b-Instruct inference exhausted memory on complex problem (Plausibility: HIGH)
  2. **Timeout:** Subprocess test execution hung on infinite loop in generated code (Plausibility: MEDIUM)
  3. **System Kill:** External OOM killer or resource limit (Plausibility: MEDIUM)
- **Most Likely Interpretation:** GPU memory exhaustion during CodeLlama inference on longer problem
- **Additional Evidence Needed:** System logs, GPU memory profiling, per-iteration memory usage

### 4.3 Connection to Existing Literature

| Our Finding | Related Work | Relationship | Citation |
|-------------|-------------|--------------|----------|
| Infrastructure challenges at scale | RLTF runtime complexity | Confirms | Liu et al., 2023 |
| AI feedback generation overhead | Self-Refine compute cost | Extends | Madaan et al., 2023 |
| Test execution sandboxing needs | bigcode-evaluation-harness | Builds on | BigCode, 2023 |

### 4.4 Theoretical Contributions

1. **Fidelity × Richness Framework:** Proposed decomposition of feedback quality into orthogonal dimensions (retained as theoretical contribution despite experimental failure)
2. **Execution Gating Architecture:** Complete implementation pattern for filtering AI feedback through unit tests (code exists, validated at small scale)

---

## 5. Experiment Results (Phase 6 Evidence)

### 5.1 Per-Hypothesis Results

| Hypothesis | Title | Gate | Result | Pass Rate | Key Insight |
|------------|-------|------|--------|-----------|-------------|
| **h-e1** | EVAF Existence PoC | MUST_WORK | FAILED | 0% | Infrastructure crashed at 53%; mechanism not disproven but not validated |
| **h-m1** | AI Feedback Quality | MUST_WORK | BLOCKED | N/A | Depends on h-e1 |
| **h-m2** | Execution Gating Accuracy | SHOULD_WORK | BLOCKED | N/A | Depends on h-m1 |
| **h-m3** | Training Improvement | SHOULD_WORK | BLOCKED | N/A | Depends on h-m2 |

### 5.2 Aggregate Metrics

| Metric | Value |
|--------|-------|
| **Total Hypotheses** | 4 |
| **Fully Validated** | 0 |
| **Partially Validated** | 0 |
| **Failed** | 1 |
| **Total Tasks Completed** | 0 / 10 |
| **SDD Compliance Rate** | 0% |

### 5.3 Optimal Hyperparameters

```yaml
# Not applicable — experiment did not complete
# Partial configuration used:
baseline_model: Salesforce/codet5-large
feedback_model: codellama/CodeLlama-7b-Instruct-hf
test_timeout: 3.0  # seconds
ai_temperature: 0.2
ai_max_tokens: 512
```

### 5.4 Proven Components

| Component | Source Hypothesis | File | Reusable |
|-----------|-------------------|------|----------|
| Config module | h-e1 | code/config.py | Yes |
| Data loading | h-e1 | code/data.py | Yes |
| Baseline model wrapper | h-e1 | code/model.py | Yes |
| Feedback model wrapper | h-e1 | code/model.py | Needs memory optimization |
| Execution gating | h-e1 | code/gating.py | Needs checkpointing |
| Metrics computation | h-e1 | code/metrics.py | Yes |
| Visualization | h-e1 | code/visualize.py | Yes (untested) |
| Orchestration | h-e1 | code/train.py | Needs resume capability |

### 5.5 Planned-vs-Actual Comparison

| Hypothesis | Planned Metric (03_tasks) | Planned Target | Actual Result (04_validation) | Deviation Type | Notes |
|------------|--------------------------|----------------|-------------------------------|----------------|-------|
| **h-e1** | Accept rate | 20-60% | N/A (crashed at 53%) | IMPLEMENTATION_GAP | Infrastructure not production-ready |
| **h-e1** | Coverage | >80% | N/A | IMPLEMENTATION_GAP | Not measured |
| **h-e1** | Gate evaluation | PASS/FAIL | FAILED (incomplete) | IMPLEMENTATION_GAP | Crashed before completion |

**Deviation Types:** IMPLEMENTATION_GAP | DESIGN_ISSUE | HYPOTHESIS_ISSUE | SCOPE_CHANGE | NONE

### 5.6 Key Figures Reference

| Figure | Source | Description | Suggested Paper Section |
|--------|--------|-------------|------------------------|
| N/A | N/A | No figures generated — experiment crashed | N/A |

---

## 6. Limitations & Scope Boundaries

### 6.1 Principled Limitations

#### Infrastructure Stability

- **What:** Experiment crashed at 53% completion (87/164 problems)
- **Why This Matters:** No experimental conclusions possible without complete data
- **Root Cause:** Likely GPU memory exhaustion during CodeLlama-7b-Instruct inference
- **Impact on Claims:** ALL performance claims invalidated; hypothesis remains untested
- **Why Acceptable:** This is an engineering limitation, not a theoretical refutation

#### Single Hypothesis Tested

- **What:** Only h-e1 (existence) attempted; h-m1, h-m2, h-m3 blocked
- **Why This Matters:** Cannot validate causal mechanism or comparative claims
- **Root Cause:** Sequential dependency structure; h-e1 failure blocks all downstream
- **Impact on Claims:** No claims about EVAF effectiveness can be made
- **Why Acceptable:** Hypothesis chain design is scientifically sound; execution failed

### 6.2 Scope Conditions

| Condition | Results Hold | Results May Not Hold | Evidence |
|-----------|-------------|---------------------|----------|
| Complete experiment run | (Required) | Current state | Crashed at 53% |
| Production-grade infrastructure | (Required) | Development prototype | Single-run failure |
| Memory-optimized inference | (Required) | CodeLlama-7b full precision | OOM suspected |

### 6.3 Assumption Violation Impact

- **A3 (Accept rate 20-60%):** NOT MEASURABLE → Impact: Cannot determine if EVAF is viable
- **Infrastructure stability (implicit):** VIOLATED → Impact: All downstream analysis blocked

---

## 7. Future Work

### 7.1 From Untested Alternative Explanations

- **Alternative:** GPU OOM caused crash
  - **Why Not Yet Tested:** No memory profiling during failed run
  - **Proposed Experiment:** Add GPU memory logging, use smaller batch size or model quantization
  - **Expected Outcome:** Identify memory threshold for stable operation

- **Alternative:** Subprocess timeout on pathological code
  - **Why Not Yet Tested:** No per-iteration timeout analysis
  - **Proposed Experiment:** Log timeout events, add watchdog timer
  - **Expected Outcome:** Identify problematic patterns in generated code

### 7.2 From Unverified Assumptions

- **Assumption:** A3 — Accept rate 20-60% achievable
  - **Current Status:** UNVERIFIED
  - **Proposed Test:** Complete h-e1 experiment with infrastructure fixes
  - **If Violated:** EVAF degenerates to pure execution feedback (accept rate <10%) or gating unnecessary (>90%)

### 7.3 From Scope Extension Opportunities

- **Extension:** Add checkpointing to allow resume after crash
  - **Current Evidence Suggesting Feasibility:** Orchestration code (train.py) can be modified
  - **Required Resources:** 2-4 hours engineering effort

- **Extension:** Use quantized CodeLlama (4-bit) for memory efficiency
  - **Current Evidence Suggesting Feasibility:** BitsAndBytes integration standard in transformers
  - **Required Resources:** Model loading code change, validation of output quality

---

## 8. Implications for Phase 6 (Paper Writing)

### 8.1 Recommended Narrative Hook

**Cannot proceed to paper writing.** No validated experimental results exist.

**Hook Strategy:** N/A
**Why This Hook:** N/A

### 8.2 Key Insight (Experiment-Verified)

> No experiment-verified insight available. The EVAF hypothesis remains theoretically plausible but empirically untested.

**Verification Evidence:** None — experiment incomplete

### 8.3 Strongest Claims (Paper-Ready)

1. **None available** — All claims require experimental validation that did not complete

### 8.4 Honest Limitations (Must Include in Paper)

1. **Experiment did not complete**
   - Why Acceptable: Infrastructure failure, not theoretical refutation
   - Suggested Framing: "Implementation prototype; production validation pending"

2. **No quantitative results**
   - Why Acceptable: Crash at 53% prevents any metric computation
   - Suggested Framing: "Architecture validated at code level; runtime validation required"

### 8.5 Evidence Highlights (Most Persuasive)

1. **Implementation Code Complete**
   - Data: 7 modules implemented (config, data, model, gating, metrics, visualize, train)
   - "So What": EVAF architecture is implementable with existing tools
   - Suggested Figure/Table: Code structure diagram

---

## Source Files Reference

| File | Hypothesis | Purpose |
|------|------------|---------|
| `h-e1/04_validation.md` | h-e1 | Experiment results (FAILED) |
| `h-e1/04_checkpoint.yaml` | h-e1 | Gate status, error details |
| `h-e1/03_tasks.yaml` | h-e1 | Planned tasks and metrics |
| `h-e1/02c_experiment_brief.md` | h-e1 | Experiment design specification |
| `03_refinement.yaml` | all | Original hypothesis definition |
| `verification_state.yaml` | all | Pipeline state |

**Input files per hypothesis:**
- `h-{id}/04_validation.md` — Experiment results, gate outcomes, lessons learned
- `h-{id}/04_checkpoint.yaml` — Pass rate, failed checks, SDD metrics
- `h-{id}/03_tasks.yaml` — Planned tasks, expected metrics, success criteria
- `h-{id}/02c_experiment_brief.md` — Experiment design, variables, evaluation protocol

---

## Synthesis Verdict

**Pipeline Status:** BLOCKED
**Reason:** h-e1 (MUST_WORK gate) failed — experiment incomplete
**Recommended Action:** Return to Phase 0 or fix infrastructure and re-run Phase 4

**Phase 6 Readiness:** NOT READY — No validated results to write paper from

---

*Anonymous Research Pipeline — Phase 4.5 Hypothesis Synthesis*
*Result: FAILED — Infrastructure crash at 53% completion*
*Date: 2026-08-18*
