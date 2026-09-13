# Verification Plan: Error Localization Granularity for LLM Code Repair

**Date:** 2026-03-30
**Hypothesis ID:** H-GranularityOptimal-v1
**Confidence:** 0.75
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under conditions where LLM-generated code fails with a localizable runtime error, if we provide error feedback at varying granularity levels G0-G4, then repair success rate will show a non-monotonic relationship with peak at G3 ± 1, because G3 provides minimal sufficient localization that focuses LLM attention without cognitive overload from irrelevant trace details.

### 1.2 Alternative Hypothesis (H0)
There is no significant difference in repair success rate across granularity levels G0-G4. Granularity of error feedback has no effect on LLM code repair performance.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | MBPP (standard) | Standard benchmark for code generation; provides diverse error types; used in Self-Debug |
| **Model** | CodeLlama-7B-Instruct | Representative of instruction-tuned code LLMs; widely used in self-repair literature |

**Dataset Details:**
- Source: https://github.com/google-research/google-research/tree/master/mbpp
- Path: mbpp/mbpp.jsonl (test split: 500 problems)

**Model Details:**
- Type: instruction-tuned code LLM
- Source: meta-llama/CodeLlama-7b-Instruct-hf

### 1.4 Baseline Methods (for H-CP* comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| G0 (Pass/Fail Only) | Baseline | MBPP |
| Self-Debug (Chen et al.) | +12% on MBPP | MBPP, Spider |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Runtime errors with localizable stack traces are prevalent (≥30%) in LLM code failures | SBEST found 98.3% of crash bugs have relevant stack traces | Granularity study has limited scope |
| A2 | CodeLlama-7B-Instruct is representative of instruction-tuned code LLMs | Widely used in self-repair literature | Results may not generalize to larger/smaller models |
| A3 | MBPP test set provides sufficient error type diversity | 500 problems across various coding tasks | Results may not generalize to other benchmarks |
| A4 | Single repair attempt is sufficient to measure effect | Self-Debug uses 1-3 repair iterations | Multi-turn repair may show different granularity effects |
| A5 | The Self-Debug prompt template doesn't interact with granularity | Template is standard in literature | Different templates may show different optimal granularity |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** First systematic granularity comparison for LLM code repair with controlled ablation

**Key Innovation:** The Attention Window Hypothesis: LLMs have limited effective attention for repair tasks. Intermediate granularity (G3) provides optimal "pointer" signal without context overload. This challenges the implicit "more information is better" assumption in prior work.

**Differentiation:**
- Self-Debug (Chen et al., 2023): Uses G2-level feedback only; no granularity comparison
- TraceFixer (Bouzenia et al., 2023): Uses full traces (G4) only; no ablation study
- DynaFix (Huang et al., 2025): Uses variable states (G4+); no comparison to simpler levels
- Haque et al. (2025): Found traces help less than expected but didn't test granularity systematically

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | READY |
| H-M1 | Mechanism | MUST_WORK | H-E1 | BLOCKED |
| H-M2 | Mechanism | SHOULD_WORK | H-M1 | BLOCKED |
| H-M3 | Mechanism | SHOULD_WORK | H-M1 | BLOCKED |

---

### 2.2 Hypothesis Specifications

---
#### H-E1: Runtime Error Prevalence (Foundation Gate)

**Statement**: Under conditions where CodeLlama-7B-Instruct generates code for MBPP problems, if we execute the generated code against test cases, then at least 30% of failures will be runtime errors with localizable stack traces, because modern LLMs produce syntactically valid code but make semantic errors that manifest at runtime.

**Rationale**: This hypothesis validates the foundation assumption (A1) that runtime errors are prevalent enough to make granularity comparison meaningful. Without sufficient runtime error prevalence, the entire granularity study has limited scope.

**Variables**:
- Independent: Code generation task (MBPP problems)
- Dependent: Runtime error prevalence (% of failures with stack traces)
- Controlled: Model (CodeLlama-7B), temperature (0), execution timeout (10s)

**Verification Protocol**:
1. Generate code for all 500 MBPP test problems using CodeLlama-7B-Instruct
2. Execute each solution against provided test cases with 10s timeout
3. Categorize failures: RUNTIME_ERROR, WRONG_OUTPUT, TIMEOUT, SYNTAX_ERROR
4. Calculate prevalence = RUNTIME_ERROR / total_failures
5. Apply Wilson confidence interval for proportion estimate

**Success Criteria** (PoC):
- Primary: runtime_error_prevalence ≥ 30% (lower bound of 95% CI)
- Secondary: Minimum 150 runtime error cases for adequate statistical power

**Failure Response**:
- IF fails (<30%): PIVOT to studying wrong-output errors or ABANDON granularity hypothesis

**Dependencies**: None (foundation hypothesis)

**Source**: Phase 2A SH1 + Assumption A1

---
#### H-M1: Granularity Effect on Repair Success (Primary Mechanism)

**Statement**: Under conditions where LLM-generated code fails with runtime errors, if we vary error feedback granularity from G0 (pass/fail) to G4 (full trace), then repair success rates will differ significantly across levels, because error information content affects LLM's ability to localize and fix bugs.

**Rationale**: This is the primary mechanism test validating that granularity matters at all. Without a significant ANOVA result, the specific G3 optimality claim cannot be supported.

**Variables**:
- Independent: Error feedback granularity (G0, G1, G2, G3, G4)
- Dependent: Repair success rate (binary per case, aggregated to %)
- Controlled: Model, temperature, prompt template, timeout, random seed

**Verification Protocol**:
1. Select runtime error cases from H-E1 (minimum 150, target 200+)
2. Generate 5 feedback versions per case (G0-G4)
3. Attempt repair with Self-Debug template for each version
4. Record binary success (all tests pass) per condition
5. Run one-way ANOVA across 5 granularity levels

**Success Criteria** (PoC):
- Primary: ANOVA p < 0.05 (significant effect of granularity)
- Secondary: Effect size η² > 0.02 (small but meaningful effect)

**Failure Response**:
- IF fails (p ≥ 0.05): ABANDON - supports H0 that granularity doesn't matter

**Dependencies**: H-E1 (requires runtime error cases)

**Source**: Phase 2A Causal Step 1 + Prediction P1

---
#### H-M2: G3 Superiority Over Minimal Feedback

**Statement**: Under conditions where repair is attempted with varying feedback, if we compare G3 (error+line) to G0 (pass/fail only), then G3 will achieve at least 10 percentage points higher repair success, because line-level localization provides actionable information that pass/fail alone lacks.

**Rationale**: Demonstrates that adding localization information provides substantial practical benefit over naive retry approaches. The 10pp threshold represents meaningful improvement.

**Variables**:
- Independent: Feedback level (G3 vs G0)
- Dependent: Repair success rate difference
- Controlled: Same as H-M1

**Verification Protocol**:
1. Extract G3 and G0 results from H-M1 experiment
2. Calculate repair_rate_G3 - repair_rate_G0
3. Run planned contrast (paired t-test or McNemar's test)
4. Compute 95% confidence interval for difference

**Success Criteria** (PoC):
- Primary: (G3 - G0) ≥ 10 percentage points, p < 0.05
- Secondary: Lower bound of 95% CI for difference > 5pp

**Failure Response**:
- IF fails: EXPLORE - G3 may still be best even if not 10pp better than G0

**Dependencies**: H-M1 (uses same experimental data)

**Source**: Phase 2A Prediction P2

---
#### H-M3: Non-Monotonicity (G3 ≥ G4)

**Statement**: Under conditions where repair is attempted with G3 vs G4 feedback, if we compare their repair success rates, then G4 will not significantly outperform G3 (G4 ≤ G3 + 2%), because full stack traces add cognitive load without proportional benefit for single-function repairs.

**Rationale**: This is the key novel prediction - that more information is NOT always better. Confirming non-monotonicity validates the Attention Window Hypothesis and differentiates this work from prior "more is better" approaches.

**Variables**:
- Independent: Feedback level (G4 vs G3)
- Dependent: Repair success rate difference
- Controlled: Same as H-M1

**Verification Protocol**:
1. Extract G4 and G3 results from H-M1 experiment
2. Calculate repair_rate_G4 - repair_rate_G3
3. Test for practical equivalence (TOST procedure) or G3 superiority
4. Verify G3 is at or near peak of the granularity curve

**Success Criteria** (PoC):
- Primary: G4 ≤ G3 + 2% (practical equivalence or G3 wins)
- Secondary: G3 or G2 is the peak performer (non-monotonic pattern)

**Failure Response**:
- IF fails (G4 >> G3): PIVOT - "more is better" may be correct for this model/task

**Dependencies**: H-M1 (uses same experimental data)

**Source**: Phase 2A Prediction P3 + Attention Window Hypothesis

---

## 3. Risk Analysis

### 3.1 Risk Identification

| ID | Risk | Source | Severity | Likelihood | Description |
|----|------|--------|----------|------------|-------------|
| R1 | Foundation Failure | A1 | **CRITICAL** | Medium | Runtime error prevalence <30% - study loses scope |
| R2 | Model Non-Representativeness | A2 | Medium | Low | Results may not generalize to other model sizes |
| R3 | Dataset Bias | A3 | Medium | Medium | MBPP may not cover all error types |
| R4 | Single-Turn Limitation | A4 | Medium | Low | Multi-turn repair may show different patterns |
| R5 | Template Confound | A5 | **HIGH** | Medium | Prompt template may interact with granularity |

**Previous Failure Context**: The static analysis prevalence hypothesis failed dramatically (4.92% vs 15% expected), demonstrating that foundation assumptions require rigorous validation.

### 3.2 Risk-Hypothesis Mapping

| Risk | Affected Hypotheses | Impact Type |
|------|---------------------|-------------|
| R1 (Foundation) | H-E1 (direct), H-M1-M3 (cascade) | **Blocking** - if H-E1 fails, mechanism tests have limited scope |
| R2 (Model) | H-M1, H-M2, H-M3 | Generalizability - results valid for 7B scale only |
| R3 (Dataset) | H-M1, H-M2, H-M3 | Generalizability - results valid for MBPP-style problems |
| R4 (Single-Turn) | H-M2, H-M3 | Scope - optimal granularity may differ in multi-turn |
| R5 (Template) | H-M1, H-M2, H-M3 | Validity - confounding if template favors certain levels |

### 3.3 Mitigation Strategies

**R1: Foundation Failure (CRITICAL)**
- **Prevention**: Two-phase design validates foundation before mechanism tests
- **Detection**: H-E1 explicitly tests prevalence with 95% CI
- **Response**:
  - If 20-30%: Proceed with caution, note limited scope
  - If 10-20%: PIVOT to studying wrong-output errors
  - If <10%: ABANDON granularity hypothesis for this model/benchmark
- **Early Warning**: Generate and categorize 100 problems first as pilot

**R2: Model Non-Representativeness (MEDIUM)**
- **Prevention**: Cannot fully prevent - single model is scope limitation
- **Detection**: Compare to published results for CodeLlama-7B
- **Response**: Document as limitation, suggest multi-model study as future work
- **Mitigation**: Note that 7B scale is common in self-repair literature

**R3: Dataset Bias (MEDIUM)**
- **Prevention**: Use full MBPP test split (500 problems) for diversity
- **Detection**: Stratify results by error type (IndexError, TypeError, etc.)
- **Response**: Report per-error-type results; if one type dominates, note limitation
- **Mitigation**: Stratified analysis reveals which error types benefit most

**R4: Single-Turn Limitation (MEDIUM)**
- **Prevention**: Cannot prevent - multi-turn is out of scope
- **Detection**: N/A - single-turn is design choice
- **Response**: Document as scope limitation; note for future work
- **Mitigation**: Single-turn captures primary signal per Self-Debug methodology

**R5: Template Confound (HIGH)**
- **Prevention**: Use standardized Self-Debug template from literature
- **Detection**: If G2 (error+message) outperforms others, template may favor it
- **Response**: Run sensitivity analysis with 1-2 alternative templates
- **Early Warning**: G2-specific advantage would indicate template bias
- **Mitigation**: Vary only error feedback section, keep other sections constant

### 3.4 Risk Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    RISK SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Priority | Risk | Mitigation Status |
|----------|------|-------------------|
| 1 | R1: Foundation Failure | Two-phase design + H-E1 gate |
| 2 | R5: Template Confound | Sensitivity analysis planned |
| 3 | R3: Dataset Bias | Stratified analysis by error type |
| 4 | R2: Model Generalization | Documented as scope limitation |
| 5 | R4: Single-Turn | Documented as scope limitation |

Risk Counts:
- Critical: 1 (R1)
- High: 1 (R5)
- Medium: 3 (R2, R3, R4)
- Low: 0

Overall Risk Assessment: MANAGEABLE
- Critical risk (R1) addressed by foundation gate design
- High risk (R5) requires sensitivity analysis
- Medium risks documented as scope limitations
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 4. Dependency Structure

### 4.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════════════════
              DEPENDENCY GRAPH (DAG) - 4 Hypotheses
═══════════════════════════════════════════════════════════════════════

[Phase 1 - Foundation]
                    ┌─────────────────────────────┐
                    │  H-E1: Runtime Prevalence   │
                    │  Gate: MUST_WORK            │
                    │  Prerequisites: None        │
                    └─────────────┬───────────────┘
                                  │
                    ══════════════╪══════════════
                         GATE 1: ≥30% prevalence
                    ══════════════╪══════════════
                                  │
                                  ▼
[Phase 2 - Mechanism Tests]
                    ┌─────────────────────────────┐
                    │  H-M1: Granularity Effect   │
                    │  Gate: MUST_WORK            │
                    │  Prerequisites: H-E1        │
                    └─────────────┬───────────────┘
                                  │
                    ══════════════╪══════════════
                         GATE 2: ANOVA p < 0.05
                    ══════════════╪══════════════
                                  │
                    ┌─────────────┴───────────────┐
                    │                             │
                    ▼                             ▼
        ┌───────────────────┐         ┌───────────────────┐
        │  H-M2: G3 > G0    │         │  H-M3: G3 ≥ G4    │
        │  Gate: SHOULD_WORK│         │  Gate: SHOULD_WORK│
        │  Prereq: H-M1     │         │  Prereq: H-M1     │
        └─────────┬─────────┘         └─────────┬─────────┘
                  │                             │
                  └──────────────┬──────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────────┐
                    │        COMPLETION           │
                    │   All hypotheses verified   │
                    └─────────────────────────────┘

═══════════════════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → {H-M2 || H-M3}
Path Length: 3 levels (H-M2 and H-M3 can run in parallel after H-M1)
═══════════════════════════════════════════════════════════════════════
```

**Dependency Map:**
```
H-E1 → []                    (Foundation - no dependencies)
H-M1 → [H-E1]               (Requires runtime error samples)
H-M2 → [H-M1]               (Uses G3 vs G0 data from H-M1)
H-M3 → [H-M1]               (Uses G4 vs G3 data from H-M1)
```

### 4.2 Dependency Hierarchy

| Level | Phase | Hypothesis | Prerequisites | Gate Type | If Fail |
|-------|-------|------------|---------------|-----------|---------|
| 0 | Foundation | H-E1 | None | MUST_WORK | STOP - reassess hypothesis |
| 1 | Mechanism | H-M1 | H-E1 | MUST_WORK | STOP - supports H0 |
| 2 | Mechanism | H-M2 | H-M1 | SHOULD_WORK | Document - G3 may still be best |
| 2 | Mechanism | H-M3 | H-M1 | SHOULD_WORK | Document - non-monotonicity unconfirmed |

**Verification Phases:**

**Phase 1 - Foundation (H-E1)**
- Test: Runtime error prevalence ≥30%
- Gate: MUST_WORK
- Action on Pass: Proceed to Phase 2
- Action on Fail: PIVOT or ABANDON

**Phase 2 - Core Mechanism (H-M1)**
- Test: ANOVA p < 0.05 across G0-G4
- Gate: MUST_WORK
- Action on Pass: Proceed to detailed comparisons (H-M2, H-M3)
- Action on Fail: ABANDON - supports null hypothesis

**Phase 2b - Detailed Comparisons (H-M2, H-M3)**
- H-M2: G3 vs G0 comparison (≥10pp difference)
- H-M3: G3 vs G4 comparison (non-monotonicity)
- Gate: SHOULD_WORK
- Note: H-M2 and H-M3 use same data from H-M1, can analyze in parallel
- Action on Fail: Document as limitation, main mechanism still valid if H-M1 passed

---

## 5. Execution

### 5.1 Dependency Chain
```
H-E1 → H-M1 → {H-M2 ∥ H-M3} → COMPLETE
```

### 5.2 Gate Summary

| Gate | Hypothesis | Pass Condition | Fail Action |
|------|------------|----------------|-------------|
| Gate 1 | H-E1 | Runtime error prevalence ≥30% | PIVOT or ABANDON |
| Gate 2 | H-M1 | ANOVA p < 0.05 | ABANDON - supports H0 |
| Gate 2b | H-M2 | G3 - G0 ≥ 10pp | Document limitation |
| Gate 2b | H-M3 | G4 ≤ G3 + 2% | Document limitation |

### 5.3 Timeline

```
═══════════════════════════════════════════════════════════════════════════════
                    VERIFICATION TIMELINE - 4 Hypotheses
═══════════════════════════════════════════════════════════════════════════════
Phase/Hypothesis    │ Week 1  │ Week 2  │ Week 3  │ Week 4  │ Week 5  │
────────────────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 1: Foundation │         │         │         │         │         │
  H-E1 Prevalence   │ ████████│█████████│         │         │         │
  [Gate 1]          │         │        ◆│         │         │         │
────────────────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 2: Mechanism  │         │         │         │         │         │
  H-M1 ANOVA        │         │         │ ████████│█████████│         │
  [Gate 2]          │         │         │         │        ◆│         │
────────────────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 2b: Analysis  │         │         │         │         │         │
  H-M2 (G3 vs G0)   │         │         │         │         │ ████████│
  H-M3 (G3 vs G4)   │         │         │         │         │ ████████│
  [Gate 2b]         │         │         │         │         │        ◆│
═══════════════════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 5 weeks
═══════════════════════════════════════════════════════════════════════════════
```

| Phase | Hypotheses | Duration | Cumulative |
|-------|------------|----------|------------|
| Phase 1: Foundation | H-E1 | 2 weeks | Week 1-2 |
| Phase 2: Mechanism | H-M1 | 2 weeks | Week 3-4 |
| Phase 2b: Analysis | H-M2, H-M3 | 1 week (parallel) | Week 5 |

**Total Duration:** 5 weeks

### 5.4 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: H-E1 → H-M1 → {H-M2 ∥ H-M3}

Path Breakdown:
┌──────────┬──────────────────────────────┬──────────┐
│ Phase    │ Work                         │ Duration │
├──────────┼──────────────────────────────┼──────────┤
│ Phase 1  │ Generate 500 solutions       │ 1 week   │
│          │ Execute & categorize errors  │ 0.5 week │
│          │ Validate prevalence ≥30%     │ 0.5 week │
├──────────┼──────────────────────────────┼──────────┤
│ Phase 2  │ Create G0-G4 feedback        │ 0.5 week │
│          │ Generate repairs (5 × N)     │ 1 week   │
│          │ Execute & record results     │ 0.5 week │
├──────────┼──────────────────────────────┼──────────┤
│ Phase 2b │ ANOVA + planned contrasts    │ 0.5 week │
│          │ G3 vs G0, G4 vs G3 analysis  │ 0.5 week │
└──────────┴──────────────────────────────┴──────────┘

Total Critical Path: 5 weeks
Slack Available: 0 weeks (fully sequential until Phase 2b)
Parallelization: H-M2 and H-M3 use same data, analyze in parallel

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.5 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Hypotheses: 4 total
  • Existence: 1 (H-E1)
  • Mechanism: 3 (H-M1, H-M2, H-M3)
  • Condition: 0

Computational Resources:
  • GPU: Single GPU (CodeLlama-7B inference)
  • LLM Calls: ~1,250 total
    - Phase 1: 500 (code generation)
    - Phase 2: ~750 (5 repairs × ~150 runtime errors)
  • Estimated GPU Time: <2 hours total

Data Requirements:
  • MBPP test set: 500 problems
  • Test cases per problem: 3 (average)
  • Expected runtime errors: 150-200 cases

Statistical Resources:
  • scipy.stats for ANOVA
  • statsmodels for planned contrasts
  • Wilson CI for prevalence estimation

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Execution Order

**Step 1: Foundation (H-E1)** - Week 1-2
1. Load MBPP test split (500 problems)
2. Generate code with CodeLlama-7B-Instruct (temp=0)
3. Execute each solution against test cases
4. Categorize failures by type
5. Calculate runtime error prevalence
6. **Gate 1 Decision**: If ≥30% → PROCEED; else → PIVOT/ABANDON

**Step 2: Primary Mechanism (H-M1)** - Week 3-4
1. Select runtime error cases (minimum 150)
2. Create 5 feedback versions per case (G0-G4)
3. Generate repair attempts for each version
4. Execute and record pass/fail
5. Run one-way ANOVA across G0-G4
6. **Gate 2 Decision**: If p < 0.05 → PROCEED; else → ABANDON (H0 supported)

**Step 3: Detailed Analysis (H-M2, H-M3)** - Week 5
1. Extract G3 vs G0 results → Run planned contrast (H-M2)
2. Extract G4 vs G3 results → Run planned contrast (H-M3)
3. Calculate confidence intervals for differences
4. **Gate 2b Decision**: Document findings, proceed to conclusions

**Step 4: Completion**
1. Compile all results
2. Generate visualizations (repair rate by granularity)
3. Document scope limitations
4. Prepare for Phase 5 (Baseline Comparison)

---

## 6. Dialectical Analysis

### 6.1 Thesis Statement

**Core Claim:** Intermediate error feedback granularity (G3: error type + line number) achieves optimal LLM code repair performance, outperforming both minimal (G0-G2) and maximal (G4) feedback levels.

**Supporting Premises:**
1. LLMs have limited effective attention for repair tasks (Attention Window Hypothesis)
2. Line-level localization provides sufficient pointer signal for single-function repairs
3. Full stack traces add cognitive load without proportional benefit
4. Self-Debug demonstrates execution feedback improves repair over blind retry
5. Haque et al. (2025) found full traces help less than expected

**Strengths:**
- Novel theoretical framework (Attention Window Hypothesis)
- Clear falsifiable predictions (ANOVA, G3 vs G0, G4 vs G3)
- Builds on established Self-Debug methodology
- Challenges implicit "more is better" assumption in prior work

**Expected Outcomes:**
- P1: ANOVA across G0-G4 shows significant effect (p < 0.05)
- P2: G3 outperforms G0 by ≥10 percentage points
- P3: G4 does not outperform G3 (non-monotonic pattern)

### 6.2 Antithesis Development

**Null Hypothesis (H0):** There is no significant difference in repair success rate across granularity levels G0-G4. Granularity of error feedback has no meaningful effect on LLM code repair performance.

**Counter-Arguments:**
1. LLMs may have sufficient world knowledge to repair code without localization hints
2. The repair task difficulty (problem complexity) may dominate over feedback effects
3. Modern LLMs are trained on diverse code and may be robust to input format variations
4. Previous static analysis hypothesis failed dramatically (4.92% vs 15%), showing assumptions can be wrong
5. Template and prompt format may confound any granularity effects

**Potential Failure Points:**
- R1: Runtime error prevalence <30% (foundation fails)
- R5: Template confounds granularity effects
- General: Problem difficulty dominates over feedback effects

**Conditions Under Which H0 Would Be Supported:**
- ANOVA p ≥ 0.05 (no significant difference across G0-G4)
- H-E1 fails (insufficient runtime error scope)
- All granularity levels perform similarly (±2%)

### 6.3 Synthesis

**Balanced Assessment:**

The hypothesis H-GranularityOptimal-v1 presents a testable claim that intermediate granularity (G3) optimizes LLM repair through the Attention Window mechanism. However, the null hypothesis raises valid concerns regarding potential confounds, model robustness, and the risk of repeating prior assumption failures.

**Resolution Path:**

The verification plan addresses this dialectic through:
1. **Foundation verification (H-E1):** Establishes sufficient scope before mechanism tests
2. **Sequential mechanism testing (H-M1):** Directly tests thesis vs antithesis with ANOVA
3. **Gate conditions:** Allow early detection of H0 support without wasted effort
4. **Documented limitations:** Acknowledge scope constraints regardless of outcome

**Conditions for Thesis Support:**
- H-E1 passes: runtime error prevalence ≥30%
- H-M1 passes: ANOVA p < 0.05 (granularity matters)
- H-M2 passes: G3 - G0 ≥ 10pp (localization helps)
- H-M3 passes: G4 ≤ G3 + 2% (non-monotonicity confirmed)

**Conditions for Antithesis Support:**
- H-E1 fails: runtime error prevalence <30% → limited scope
- H-M1 fails: ANOVA p ≥ 0.05 → no granularity effect
- G4 >> G3: "more is better" is correct, not Attention Window

**Nuanced Outcome Possibilities:**
1. **Full Support:** All hypotheses pass → Thesis validated, G3 is optimal
2. **Partial Support:** H-M1 passes but H-M2/H-M3 fail → Granularity matters but G3 not optimal
3. **Weak Support:** H-E1 passes marginally → Results valid but scope limited
4. **No Support:** H-M1 fails → Antithesis supported, granularity doesn't matter

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Runtime errors are prevalent (≥30%) | May be lower than expected | H-E1 gate with 95% CI |
| Mechanism | Attention Window explains effect | Alternative explanations possible | H-M1 ANOVA test |
| Optimal Level | G3 is optimal (non-monotonic) | G4 might be better | H-M3 comparison |
| Practical Impact | ≥10pp improvement | Marginal improvement | H-M2 threshold |
| Generalization | Results apply to code LLMs | Single model limitation | Document scope |

**Robustness Indicators:**

| Metric | Assessment |
|--------|------------|
| Falsifiability | **High** - Clear rejection criteria for each hypothesis |
| Internal Validity | **High** - Within-subject design, controlled variables |
| External Validity | **Medium** - Single model/dataset limits generalization |
| Statistical Power | **High** - 150+ samples, standard tests (ANOVA, contrasts) |
| Confound Control | **Medium** - Template confound requires sensitivity analysis |

**Overall Robustness Score:** **MEDIUM-HIGH**

**Confidence in Verification Plan:** 0.75

The plan is robust to both thesis and antithesis outcomes. Either result advances scientific understanding: thesis support provides actionable design guidance, antithesis support eliminates granularity as a design consideration.

---

## 7. Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** Error feedback granularity (G0-G4) affects LLM code repair with peak at G3
- ID: H-GranularityOptimal-v1, Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (Phase 2A data available)
- Sub-Hypotheses: 4 total (H-E: 1, H-M: 3)
- Phases: 3 phases over 5 weeks
- Critical Gates: 3 decision points (Gate 1, Gate 2, Gate 2b)

**Risk Assessment:** Medium
- Critical: Foundation failure (R1) - mitigated by two-phase design
- High: Template confound (R5) - requires sensitivity analysis

**Immediate Action:** Begin Phase 1 with H-E1 (runtime error prevalence test)

### 7.2 Final Summary

**Key Achievements:**
- 4 hypotheses defined with clear verification protocols
- Sequential dependency structure with gate conditions
- Risk analysis with mitigation strategies for all 5 assumptions
- Dialectical evaluation confirming robustness to both thesis/antithesis outcomes

**Scope Reduction:** 60% (3 BUILD_ON claims from established literature)

**Novel Contribution:** First systematic granularity comparison for LLM code repair testing the Attention Window Hypothesis

### 7.3 Conclusions

**Verification Execution Order:**

| Phase | Hypotheses | Duration | Gate |
|-------|------------|----------|------|
| 1. Foundation | H-E1: Runtime error prevalence ≥30% | 2 weeks | MUST_WORK |
| 2. Mechanism | H-M1: ANOVA across G0-G4 | 2 weeks | MUST_WORK |
| 2b. Analysis | H-M2: G3 vs G0, H-M3: G3 vs G4 | 1 week | SHOULD_WORK |

**Critical Decision Points:**

1. **Gate 1 (H-E1):** Runtime error prevalence
   - PASS (≥30%): Proceed to mechanism tests
   - FAIL (<30%): PIVOT to wrong-output errors or ABANDON

2. **Gate 2 (H-M1):** Granularity effect test
   - PASS (p < 0.05): Granularity matters, proceed to detailed analysis
   - FAIL (p ≥ 0.05): ABANDON - supports null hypothesis

3. **Gate 2b (H-M2, H-M3):** Specific predictions
   - PASS: Full thesis support
   - FAIL: Partial support - document limitations

**Open Questions:**
- What is the exact runtime error prevalence on MBPP?
- Does optimal granularity vary by error type?
- How does model size affect optimal granularity?

**Recommendations:**

1. **Immediate Actions:**
   - Set up MBPP dataset and CodeLlama-7B environment
   - Implement error categorization pipeline
   - Begin H-E1 prevalence test

2. **Resource Allocation:**
   - GPU: Single GPU sufficient (~2 hours compute)
   - Timeline: 5 weeks for critical path
   - Buffer: 1 week for unexpected issues

3. **Failure Management:**
   - Document all outcomes (pass/fail/partial)
   - Execute PIVOT strategies if foundation fails
   - Prepare scope limitation documentation

### 7.4 Appendices

**A. Phase 2A Reference**
- Source: `03_refinement.yaml` (H-GranularityOptimal-v1)
- Schema: v10.0.0 Free-Parse
- Consensus: 6 personas, 12 exchanges

**B. MCP Tool Usage Summary**
- Total MCP calls: 6
- ClearThought scientificmethod: 4 (hypothesis + experiment stages)
- ClearThought collaborativereasoning: 1 (risk analysis)
- ClearThought structuredargumentation: 3 (dialectical analysis)

**C. Key Metrics**
- LLM calls required: ~1,250 (500 generation + 750 repair)
- Statistical tests: ANOVA, planned contrasts, Wilson CI
- Minimum sample: 150 runtime errors for adequate power

---

*Generated by YouRA Phase 2B (v6.0) | 2026-03-30*
