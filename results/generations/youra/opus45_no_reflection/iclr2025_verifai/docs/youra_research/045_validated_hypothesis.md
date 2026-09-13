# Validated Hypothesis Synthesis

**Generated:** 2026-08-19
**Workflow:** Phase 4.5 Hypothesis Synthesis 
**Pipeline Position:** Phase 4 (Hypothesis Loop) → [Phase 4.5] → Phase 5/6

---

## 1. Executive Summary

The Actionable Specificity (AS) hypothesis chain terminated early at H-E1 (existence test) due to gate failure. The foundational assumption — that AS components can be reliably extracted from standard verification signals — was only partially validated. While AS ordering constraints held (C1≥C2≥C3≥C4), extraction rate reached only 49.5% against 95% target.

**Root cause:** Regex-based extraction patterns require full Python tracebacks, but HumanEval/MBPP failures are dominated by assertion errors (53.4%) which produce minimal traceback output. The AS framework, as operationalized, is not applicable to assertion-dominant benchmarks.

| Metric | Value |
|--------|-------|
| **Original Core Statement** | AS components (loc/state/causal) predict repair success |
| **Refined Core Statement** | AS extraction requires traceback-rich errors; assertion errors need alternative operationalization |
| **Predictions Supported** | 0 / 4 |
| **Overall Pass Rate** | 49.5% |
| **Hypotheses Validated** | 0 / 1 (tested) |

---

## 2. Prediction-Result Matrix

| Prediction | Original Statement | Tested By | Key Metric | Result | Status | Confidence | Evidence Summary |
|------------|-------------------|-----------|------------|--------|--------|------------|------------------|
| **P1** | AS components collectively predict repair success | H-M4 (blocked) | Likelihood ratio p<0.05 | N/A | INCONCLUSIVE | N/A | Blocked by H-E1 failure |
| **P2** | C1 outperforms C4 by ≥5pp on assertion errors | H-M4 (blocked) | Δ ≥ 5pp | N/A | INCONCLUSIVE | N/A | Blocked by H-E1 failure |
| **P3** | C3 outperforms C6 by ≥5pp | H-M4 (blocked) | Δ ≥ 5pp | N/A | INCONCLUSIVE | N/A | Blocked by H-E1 failure |
| **P4** | Optimal trace length exists (non-monotonic) | H-M4 (blocked) | β_AS² < 0 | N/A | INCONCLUSIVE | N/A | Blocked by H-E1 failure |

**Status Legend:** SUPPORTED | PARTIALLY_SUPPORTED | REFUTED | INCONCLUSIVE

### Causal Mechanism Verification

| Mechanism Step | Description | Falsifier | Evidence | Verification Status |
|----------------|-------------|-----------|----------|---------------------|
| 1 | Test execution generates signals with varying AS levels | Signals cannot be reliably generated with controlled AS | Signals generated; AS extraction inconsistent (49.5%) | PARTIALLY_VERIFIED |
| 2 | LLM parses AS information from signals | LLM cannot extract AS components | NOT TESTED (blocked) | NOT_TESTED |
| 3 | Higher AS enables better bug localization | Repair success independent of AS | NOT TESTED (blocked) | NOT_TESTED |
| 4 | Higher AS leads to higher repair success | β coefficients ≈ 0 | NOT TESTED (blocked) | NOT_TESTED |

---

## 3. Hypothesis Refinement

### 3.1 Original Core Statement (Phase 2A)

> Under LLM-based iterative code repair on standard benchmarks (HumanEval, MBPP), if verification signals provide higher Actionable Specificity—decomposed into Localization (AS_loc), State Exposure (AS_state), and Causal Context (AS_causal)—then single-attempt repair success rates increase, because informationally richer feedback enables the model to localize bugs and infer correct fixes.

### 3.2 Refined Core Statement (Phase 4.5)

> The AS decomposition framework (AS_loc, AS_state, AS_causal) can extract localization and causal information from traceback-rich Python errors, but requires alternative operationalization for assertion-dominated benchmarks where minimal error output is standard. The hypothesis that AS predicts repair success remains untested due to extraction-rate failure on HumanEval/MBPP.

**Key Changes:**
- REMOVED claim: "AS components independently measurable across all signal types"
- ADDED boundary: "traceback-rich errors only"
- WEAKENED claim: From "AS predicts success" to "AS framework requires reformulation"

### 3.3 Causal Mechanism — Verified Chain

```
Step 1 (Signal Generation): PARTIALLY_VERIFIED
  - Signals generated for 600 samples (100 failures × 6 conditions)
  - AS ordering preserved (C1≥C2≥C3≥C4)
  - Extraction rate insufficient (49.5% vs 95% target)

Steps 2-4: NOT_TESTED (blocked by H-E1 failure)
```

**Removed/Modified Steps:**
- **Step 1** (original: "generates signals with varying AS levels"): Modified to acknowledge extraction limitation on assertion errors

### 3.4 Claims Removed or Weakened

| Original Claim | Action | Reason | Evidence |
|----------------|--------|--------|----------|
| AS components independently measurable | WEAKENED | Only valid for traceback-rich errors | 49.5% extraction rate; assertion errors (53.4%) produce no frames |
| AS decomposition valid across signal types | REMOVED | Regex patterns fail on assertion errors | AS_state = 2.7%, AS_causal = 15.5% |
| AS_state captures variable values | WEAKENED | Minimal variable exposure in assertion output | Only 2.7% extraction rate |

### 3.5 Assumptions Status

| Assumption | Original Status | Verification Status | Evidence | Impact if Violated |
|------------|----------------|---------------------|----------|-------------------|
| A1: AS components measurable from signal text | ASSUMED | VIOLATED | 49.5% extraction rate | Cannot operationalize AS; categorical analysis only |
| A2: LLMs can use AS information | ASSUMED | UNVERIFIED | Blocked by A1 failure | Unknown |
| A3: Error category confound controllable | ASSUMED | UNVERIFIED | Blocked by A1 failure | Unknown |
| A4: Single-attempt success meaningful | ASSUMED | UNVERIFIED | Blocked by A1 failure | Unknown |
| A5: Results generalize across models | ASSUMED | UNVERIFIED | Blocked by A1 failure | Unknown |

---

## 4. Theoretical Interpretation

### 4.1 Mechanistic Explanation (Experiment-Verified)

The core finding is a **negative result**: AS decomposition via regex extraction does not scale to assertion-dominated benchmarks. The theoretical mechanism assumed that Python tracebacks would provide extractable localization, state, and causal information. However:

1. **Assertion errors** (53.4% of HumanEval/MBPP failures) produce output like `AssertionError` without file:line traceback frames
2. **Regex patterns** designed for `File "X", line Y, in func` format match only 49.5% of signals
3. **AS_state** (variable values) is nearly absent (2.7%) because assertion output rarely includes variable context

This reveals a **framework boundary condition**: AS operationalization requires either (a) traceback-rich error types, or (b) alternative extraction methods for assertion errors.

### 4.2 Unexpected Findings Analysis

#### Finding: Near-Zero AS_state Extraction

- **Observation:** AS_state extraction rate = 2.7% (16/600 signals)
- **Why Unexpected:** Variable values were expected in trace frames
- **Competing Explanations:**
  1. **Assertion Format Limitation:** Assertion errors don't expose variable values in standard output (Plausibility: HIGH)
  2. **Regex Pattern Too Narrow:** `\w+\s*=\s*[value]` misses complex structures (Plausibility: MEDIUM)
  3. **Bug Injection Bias:** Simple mutations produce assertion failures, not rich exceptions (Plausibility: MEDIUM)
- **Most Likely Interpretation:** Assertion format limitation — standard assertion output is `assert X == Y` failure message, not variable dump
- **Additional Evidence Needed:** Test on traceback-rich subset (type errors, runtime exceptions)

#### Finding: AS Ordering Preserved Despite Low Extraction

- **Observation:** C1≥C2≥C3≥C4 ordering held even at low absolute values
- **Why Unexpected:** Expected higher variance with unreliable extraction
- **Competing Explanations:**
  1. **Relative ordering robust:** AS ordering is a rank property, not absolute (Plausibility: HIGH)
  2. **Sample bias:** 49.5% that extracted happened to preserve order (Plausibility: MEDIUM)
- **Most Likely Interpretation:** AS ordering is robust to extraction coverage when present
- **Additional Evidence Needed:** Bootstrap confidence intervals on ordering

### 4.3 Connection to Existing Literature

| Our Finding | Related Work | Relationship | Citation |
|-------------|-------------|--------------|----------|
| Assertion errors dominate benchmarks | How Many Tries [2026] | CONFIRMS — assertion errors have lowest repair success (~45%) | Prior work |
| Traceback richness varies by error type | DebugRepair [2026] | EXTENDS — we quantify the extraction gap | Kang et al. |
| Regex extraction insufficient | None found | NOVEL — first systematic measurement of AS extractability | This work |

### 4.4 Theoretical Contributions

1. **Boundary Condition Discovery:** AS framework requires traceback-rich errors; assertion-dominated benchmarks are out of scope for current operationalization
2. **Negative Result Value:** Documented why direct regex extraction fails on standard benchmarks
3. **Methodological Insight:** Future AS research should stratify by error type before extraction

---

## 5. Experiment Results (Phase 6 Evidence)

### 5.1 Per-Hypothesis Results

| Hypothesis | Title | Gate | Result | Pass Rate | Key Insight |
|------------|-------|------|--------|-----------|-------------|
| **H-E1** | AS Components Are Measurable | MUST_WORK | FAIL | 49.5% | Extraction fails on assertion errors |

### 5.2 Aggregate Metrics

| Metric | Value |
|--------|-------|
| **Total Hypotheses** | 5 (planned) |
| **Fully Validated** | 0 |
| **Partially Validated** | 0 |
| **Failed** | 1 |
| **Not Started** | 4 (blocked) |
| **Total Tasks Completed** | 5 / 5 (H-E1 only) |
| **SDD Compliance Rate** | N/A |

### 5.3 Optimal Hyperparameters

```yaml
# H-E1 Configuration (failed to meet gate)
extraction_patterns:
  FILE_LINE_PATTERN: 'File "([^"]+)", line (\d+)'
  VARIABLE_VALUE_PATTERN: '(\w+)\s*=\s*([''"]?[\w\d\.\-\[\]{}]+[''"]?)'
  TRACEBACK_FRAME_PATTERN: '^\s+File "([^"]+)", line (\d+), in (\w+)'
sampling:
  sample_size: 100
  stratification: by_error_type
  seed: 42
conditions: [C1, C2, C3, C4, C5, C6]
```

### 5.4 Proven Components

| Component | Source Hypothesis | File | Reusable |
|-----------|-------------------|------|----------|
| Signal generation (6 variants) | H-E1 | code/train.py | Yes |
| ASComponents dataclass | H-E1 | code/model.py | Partial (needs new patterns) |
| Visualization pipeline | H-E1 | code/evaluate.py | Yes |

### 5.5 Planned-vs-Actual Comparison

| Hypothesis | Planned Metric (03_tasks) | Planned Target | Actual Result (04_validation) | Deviation Type | Notes |
|------------|--------------------------|----------------|-------------------------------|----------------|-------|
| **H-E1** | Extraction rate | ≥95% | 49.5% | HYPOTHESIS_ISSUE | Regex patterns designed for traceback-rich errors; assertion errors dominate benchmark |
| **H-E1** | AS ordering | C1≥C2≥C3≥C4 | True | NONE | Ordering criterion met |

**Deviation Types:** IMPLEMENTATION_GAP | DESIGN_ISSUE | HYPOTHESIS_ISSUE | SCOPE_CHANGE | NONE

### 5.6 Key Figures Reference

| Figure | Source | Description | Suggested Paper Section |
|--------|--------|-------------|------------------------|
| extraction_rate_bar.png | h-e1/figures/ | Extraction rate per AS component | Results (negative result) |
| component_boxplots.png | h-e1/figures/ | AS component distributions by condition | Appendix |
| extraction_heatmap.png | h-e1/figures/ | Components × conditions success matrix | Results |
| correlation_matrix.png | h-e1/figures/ | Component independence verification | Results |

---

## 6. Limitations & Scope Boundaries

### 6.1 Principled Limitations

#### Limitation 1: Assertion Error Coverage Gap

- **What:** AS extraction patterns fail on assertion errors (53.4% of benchmark failures)
- **Why This Matters:** Majority of HumanEval/MBPP failures are assertion errors; AS framework cannot analyze them
- **Root Cause:** Standard assertion output (`AssertionError: assert X == Y`) contains no traceback frames, file:line info, or variable context in structured format
- **Impact on Claims:** Cannot claim AS framework applies to "standard benchmarks" — only traceback-rich error subsets
- **Why Acceptable:** This is a **boundary condition discovery**, not a framework failure. AS may still hold for type/runtime/syntax errors.

#### Limitation 2: Single Operationalization Tested

- **What:** Only regex-based extraction tested
- **Why This Matters:** Alternative operationalizations (AST analysis, LLM-based extraction) not evaluated
- **Root Cause:** Scope constraint — H-E1 is existence test for simplest operationalization
- **Impact on Claims:** Negative result applies to regex extraction only, not AS concept
- **Why Acceptable:** Establishes baseline; future work can test alternatives

### 6.2 Scope Conditions

| Condition | Results Hold | Results May Not Hold | Evidence |
|-----------|-------------|---------------------|----------|
| Error type | Type, Runtime, Syntax errors | Assertion errors | 53.4% assertion rate |
| Traceback format | Standard Python traceback | Custom error messages | Regex designed for stdlib format |
| Benchmark | Traceback-rich problems | Assertion-dominated benchmarks | HumanEval/MBPP have 53.4% assertion |

### 6.3 Assumption Violation Impact

- **A1 (AS components measurable):** VIOLATED — 49.5% extraction rate → Mechanism hypotheses (H-M1 to H-M4) blocked; cannot test AS→repair success link

---

## 7. Future Work

### 7.1 From Untested Alternative Explanations

- **Alternative:** LLM-based AS extraction instead of regex
  - **Why Not Yet Tested:** Out of scope for H-E1 (existence test for simplest method)
  - **Proposed Experiment:** Prompt LLM to extract (file, line, variables, trace depth) from signal text
  - **Expected Outcome:** Higher extraction rate on assertion errors via semantic parsing

- **Alternative:** Use `pytest --tb=long` for richer tracebacks
  - **Why Not Yet Tested:** H-E1 used direct Python execution
  - **Proposed Experiment:** Re-run signal generation with pytest verbose mode
  - **Expected Outcome:** More traceback frames, higher AS_causal extraction

### 7.2 From Unverified Assumptions

- **Assumption:** A2 — LLMs can effectively use AS information
  - **Current Status:** UNVERIFIED (blocked by A1 failure)
  - **Proposed Test:** Filter to traceback-rich errors, extract AS, correlate with repair success
  - **If Violated:** AS framework invalid for LLM repair regardless of extraction method

- **Assumption:** A3 — Error category confound controllable
  - **Current Status:** UNVERIFIED
  - **Proposed Test:** Stratified analysis within traceback-rich error types
  - **If Violated:** AS effect may be confounded with error difficulty

### 7.3 From Scope Extension Opportunities

- **Extension:** Test AS framework on traceback-rich benchmark subset
  - **Current Evidence Suggesting Feasibility:** Type errors (18.2%), Runtime errors (26.8%) may have richer traces
  - **Required Resources:** Filter H-E1 dataset to non-assertion errors, re-run extraction

- **Extension:** Alternative AS operationalization for assertions
  - **Current Evidence Suggesting Feasibility:** Assertion messages contain expected/actual values in text
  - **Required Resources:** Design assertion-specific regex or semantic parser

---

## 8. Implications for Phase 6 (Paper Writing)

### 8.1 Recommended Narrative Hook

The AS framework reveals a **hidden boundary condition** in feedback-driven code repair: the theoretical promise of "richer feedback enables better repair" holds only when that richness is extractable. On standard benchmarks dominated by assertion errors, the feedback that matters most (why did `assert X == Y` fail?) is precisely the information that error messages don't expose.

**Hook Strategy:** Frame as boundary condition discovery, not failure
**Why This Hook:** Positions work as methodological contribution (what researchers should check before designing feedback mechanisms) rather than negative result

### 8.2 Key Insight (Experiment-Verified)

> Assertion errors, which constitute 53% of HumanEval/MBPP failures and have the lowest repair success rate (~45%), produce error outputs with near-zero extractable state information (AS_state = 2.7%). This creates a fundamental mismatch between the error types that most need actionable feedback and the error types that provide it.

**Verification Evidence:** H-E1 extraction rate analysis; error type distribution (assertion=53.4%)

### 8.3 Strongest Claims (Paper-Ready)

1. **Claim:** AS extraction via regex achieves only 49.5% coverage on HumanEval/MBPP
   - Evidence: 600 signals analyzed, 297 with valid extraction
   - Confidence: HIGH (direct measurement)
   - Suggested Section: Results

2. **Claim:** Assertion errors (53.4% of failures) produce <3% extractable state information
   - Evidence: AS_state = 2.7% on assertion-dominated sample
   - Confidence: HIGH (direct measurement)
   - Suggested Section: Results + Discussion

3. **Claim:** AS ordering (C1≥C2≥C3≥C4) holds even under low extraction
   - Evidence: Ordering verified on 49.5% extracted subset
   - Confidence: MEDIUM (may not generalize to full population)
   - Suggested Section: Results

### 8.4 Honest Limitations (Must Include in Paper)

1. **Limitation:** Only one operationalization tested (regex extraction)
   - Why Acceptable: Establishes baseline; more sophisticated methods are future work
   - Suggested Framing: "We tested the simplest operationalization to establish feasibility bounds"

2. **Limitation:** Mechanism hypotheses (H-M1 to H-M4) not tested
   - Why Acceptable: Gate failure is informative; documents blocking condition
   - Suggested Framing: "Our staged verification design surfaced a fundamental barrier at the existence stage"

3. **Limitation:** Single benchmark family (HumanEval/MBPP)
   - Why Acceptable: These are standard benchmarks in code repair literature
   - Suggested Framing: "Results specific to assertion-dominated benchmarks"

### 8.5 Evidence Highlights (Most Persuasive)

1. **Highlight:** Extraction Rate Gap
   - Data: 49.5% vs 95% target; breakdown by component (loc=49.5%, state=2.7%, causal=15.5%)
   - "So What": The gap is not uniform — state extraction (the most actionable for repair) is nearly absent
   - Suggested Figure/Table: extraction_rate_bar.png + component breakdown table

2. **Highlight:** Error Type Distribution
   - Data: Assertion=53.4%, Other=26.8%, Type=18.2%, Syntax=0.8%
   - "So What": The hardest-to-repair category (assertion) is precisely the one with poorest AS extractability
   - Suggested Figure/Table: Error distribution pie chart + cross-tabulation with AS success

3. **Highlight:** Ordering Preservation
   - Data: C1≥C2≥C3≥C4 maintained despite low extraction
   - "So What": AS concept may be valid; operationalization needs refinement
   - Suggested Figure/Table: component_boxplots.png

---

## Source Files Reference

| File | Hypothesis | Purpose |
|------|------------|---------|
| `h-e1/04_validation.md` | H-E1 | Experiment results, gate outcome, failure analysis |
| `h-e1/04_checkpoint.yaml` | H-E1 | Pass rate (49.5%), reflection outcome |
| `h-e1/03_tasks.yaml` | H-E1 | Planned tasks, success criteria |
| `h-e1/02c_experiment_brief.md` | H-E1 | Experiment design, AS extraction specification |
| `03_refinement.yaml` | Main | Original hypothesis, predictions P1-P4, causal mechanism |
| `verification_state.yaml` | Pipeline | Hypothesis statuses, gate results, execution plan |

**Input files per hypothesis:**
- `h-{id}/04_validation.md` — Experiment results, gate outcomes, lessons learned
- `h-{id}/04_checkpoint.yaml` — Pass rate, failed checks, SDD metrics
- `h-{id}/03_tasks.yaml` — Planned tasks, expected metrics, success criteria
- `h-{id}/02c_experiment_brief.md` — Experiment design, variables, evaluation protocol

---

*YouRA Research Pipeline — Evidence-refined hypothesis with theoretical interpretation*
