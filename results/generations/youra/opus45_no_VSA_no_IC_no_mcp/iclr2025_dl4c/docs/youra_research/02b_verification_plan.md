# Verification Plan: Execution vs AI Feedback for Code Generation

**Date:** 2026-08-28
**Hypothesis ID:** H-ExecVsAI-v1
**Confidence:** 0.75
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under iterative code generation refinement on standard benchmarks (HumanEval, MBPP),
if feedback is provided by execution (compiler + tests) versus AI critique (instruction-tuned LLM),
then execution feedback will yield higher pass@1 rates,
because execution provides ground-truth counterfactual error localization that AI critique must approximate.

### 1.2 Alternative Hypothesis (H0)
There is no significant difference in pass@1 between execution feedback and AI feedback conditions
when controlling for base model, dataset, and number of refinement iterations.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | HumanEval + MBPP (standard) | Standard code generation benchmarks with automated test suites enable execution feedback |
| **Model** | CodeLlama-7B-Instruct, StarCoder-7B | Open-source models enable controlled experimentation; two families test generalization |

**Dataset Details:**
- Source: https://github.com/openai/human-eval, https://github.com/google-research/mbpp
- Path: datasets/

**Model Details:**
- Type: instruction-tuned code LLM
- Source: HuggingFace

### 1.4 Baseline Methods (for H-CP* comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Self-Debug (Chen et al., 2023) | ~10% improvement over zero-shot | HumanEval |
| Self-Refine (Madaan et al., 2023) | ~5-8% improvement | Multiple |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Off-the-shelf LLM critics have not been fine-tuned on execution feedback | Using GPT-4/Claude trained on diverse data without explicit execution labels | AI feedback would contain indirect execution signal, confounding comparison |
| A2 | Execution sandbox faithfully represents target environment | Using standardized sandboxes (E2B, Docker) with documented configurations | Execution feedback may not generalize to real deployment |
| A3 | Natural language normalization preserves feedback information content | Template conversion maintains error type, location, expected/actual values | Format differences would confound feedback type comparison |
| A4 | Base model can utilize feedback for refinement | Both CodeLlama and StarCoder support instruction-following for code editing | Results would reflect model capability, not feedback effectiveness |

### 1.6 Research Gap & Novelty

**Gap:** No prior controlled comparison exists between execution feedback and AI feedback under identical experimental conditions. Prior work (CodeRL, Self-Debug, Self-Refine, Reflexion) compares methods, not feedback signals.

**Novelty:** First controlled comparison of feedback types (execution vs AI) with granularity ablation, isolating the feedback signal from method confounds.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | READY |
| H-M2 | MECHANISM | MUST_WORK | H-M1 | READY |
| H-M3 | MECHANISM | MUST_WORK | H-M2 | READY |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Execution Feedback Provides Unique Ground-Truth Signal**

**Statement**: Under iterative code generation refinement, if execution feedback (compiler + tests) is provided, then the model receives ground-truth counterfactual error localization not replicable by AI critique, because execution output contains exact error traces with line numbers, variable values, and expected vs actual outputs.

**Rationale**: This hypothesis validates the core claim that execution feedback provides fundamentally different information than AI critique. If AI critique can fully replicate the information content of execution feedback, the entire research premise falls. This is the foundation for all mechanism hypotheses.

**Variables**:
- Independent: Feedback source (execution vs AI)
- Dependent: Information content (error localization accuracy)
- Controlled: Base model, benchmark, iterations, temperature

**Verification Protocol**:
1. Generate code with deliberate bugs and collect execution error traces
2. Query AI critic for error diagnosis on same code
3. Compare localization accuracy (line number, error type, value identification)
4. Measure information overlap via semantic similarity metrics
5. Calculate unique information content per feedback type

**Success Criteria** (PoC: Direction-based):
- Primary: Execution feedback contains localization info absent from AI critique
- Secondary: Error trace uniquely identifies bug location in >80% cases

**Failure Response**:
- IF fails: PIVOT to investigating what unique signal execution provides

**Dependencies**: None

**Source**: Phase 2A SH1, Prediction P1

---
**H-M1: Error Traces Contain Counterfactual Information**

**Statement**: Under execution on buggy code, if compiler/test output is generated, then error traces contain counterfactual information ("if X were different, Y would not have failed"), because traces include line numbers, variable values, and expected vs actual outputs.

**Rationale**: This mechanism step establishes that execution feedback inherently encodes counterfactual information. This is the entry point to the causal chain — without counterfactual content, subsequent mechanism steps cannot operate.

**Variables**:
- Independent: Execution feedback presence
- Dependent: Counterfactual information content
- Controlled: Bug type, code complexity, test coverage

**Verification Protocol**:
1. Generate buggy code across bug categories (syntax, logic, type)
2. Execute and collect error traces
3. Annotate traces for counterfactual structure (if-then relationships)
4. Quantify counterfactual density per trace
5. Validate against human annotations

**Success Criteria** (PoC: Direction-based):
- Primary: >70% of error traces contain extractable counterfactual information
- Secondary: Counterfactual information correctly identifies bug root cause

**Failure Response**:
- IF fails: EXPLORE alternative signal types in execution feedback

**Dependencies**: H-E1

**Source**: Phase 2A Causal Step 1

---
**H-M2: Counterfactual Information Enables Targeted Edits**

**Statement**: Under code refinement with counterfactual feedback, if the model receives localized error information, then it produces targeted code edits rather than global rewrites, because specific location information constrains the edit space.

**Rationale**: This mechanism step links counterfactual information to edit behavior. Self-Debug shows execution errors guide specific line edits. The question is whether this targeting is causal or correlational.

**Variables**:
- Independent: Counterfactual information availability
- Dependent: Edit scope (targeted vs global)
- Controlled: Base model, prompt format, bug severity

**Verification Protocol**:
1. Provide model with localized vs non-localized feedback
2. Collect generated code edits
3. Measure edit scope via diff metrics (lines changed, AST distance)
4. Compare edit targeting between feedback conditions
5. Analyze edit precision (changes at bug location vs elsewhere)

**Success Criteria** (PoC: Direction-based):
- Primary: Localized feedback produces smaller diffs than non-localized
- Secondary: Edits concentrate at actual bug location with localized feedback

**Failure Response**:
- IF fails: EXPLORE if models ignore localization information

**Dependencies**: H-M1

**Source**: Phase 2A Causal Step 2

---
**H-M3: Targeted Edits Have Higher Fix Probability**

**Statement**: Under iterative refinement, if edits are targeted (small scope), then they have higher probability of fixing bugs than global rewrites, because smaller diffs preserve working code and reduce regression risk.

**Rationale**: This is the final mechanism step linking targeted edits to actual bug fixing success. If global rewrites work equally well, the entire mechanism chain provides no advantage.

**Variables**:
- Independent: Edit scope (targeted vs global)
- Dependent: Bug fix success rate
- Controlled: Bug type, baseline correctness, model capability

**Verification Protocol**:
1. Classify generated edits by scope (targeted vs global)
2. Execute refined code on test suites
3. Measure fix success rate per edit category
4. Control for initial bug severity
5. Analyze regression rates (new bugs introduced)

**Success Criteria** (PoC: Direction-based):
- Primary: Targeted edits achieve higher fix rate than global rewrites
- Secondary: Targeted edits introduce fewer regressions

**Failure Response**:
- IF fails: ABANDON mechanism hypothesis, explore alternative explanations

**Dependencies**: H-M2

**Source**: Phase 2A Causal Step 3

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Execution contains unique localization | STOP: Premise invalid |
| H-M1 | MUST_WORK | >70% traces have counterfactual info | PIVOT: Alternative signal |
| H-M2 | MUST_WORK | Localized feedback produces smaller diffs | EXPLORE: Why no targeting |
| H-M3 | MUST_WORK | Targeted edits have higher fix rate | ABANDON: Mechanism fails |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanisms | H-M1, H-M2, H-M3 | 3 weeks |

**Total Duration:** 5 weeks

---

## 4. Risk Analysis

### 4.1 Risk Identification

**R1: AI Critic Contains Implicit Execution Signal**
- Source: A1 (Off-the-shelf LLM critics not fine-tuned on execution feedback)
- Description: LLMs trained on code may have learned execution patterns from training data
- Severity: High
- Likelihood: Medium

**R2: Sandbox Environment Divergence**
- Source: A2 (Execution sandbox faithfully represents target environment)
- Description: Test results may not transfer to real deployment environments
- Severity: Medium
- Likelihood: Low

**R3: Format Confounding**
- Source: A3 (Natural language normalization preserves information content)
- Description: Differences in feedback presentation may affect model behavior
- Severity: High
- Likelihood: Medium

**R4: Model Capability Ceiling**
- Source: A4 (Base model can utilize feedback for refinement)
- Description: Results may reflect model limitations rather than feedback effectiveness
- Severity: Medium
- Likelihood: Low

### 4.2 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1 | A1 | H-E1 (invalidates premise) | High |
| R2 | A2 | H-M3 (generalization) | Medium |
| R3 | A3 | H-M1, H-M2 (mechanism validity) | High |
| R4 | A4 | All (experimental validity) | Medium |

### 4.3 Mitigation Strategies

**R1 Mitigation (AI Critic Implicit Execution Signal):**
1. Prevention: Use random baseline to establish true no-signal condition
2. Detection: Compare AI critic to random baseline; if similar, implicit signal minimal
3. Response: If AI matches execution, PIVOT to studying what signal AI has learned

**R2 Mitigation (Sandbox Divergence):**
1. Prevention: Use standardized Docker environments with documented configs
2. Detection: Validate subset of results on alternative sandbox
3. Response: Document environment assumptions in scope limitations

**R3 Mitigation (Format Confounding):**
1. Prevention: Template conversion that preserves error type, location, expected/actual
2. Detection: Human annotation of information content in both formats
3. Response: If confounded, add format control condition

**R4 Mitigation (Model Capability):**
1. Prevention: Use two model families (CodeLlama, StarCoder) to test generalization
2. Detection: If both models fail to use feedback, capability issue identified
3. Response: Report as scope limitation; test on larger models if available

### 4.4 Risk Summary

| ID | Risk | Source | Severity | Affected | Mitigation |
|----|------|--------|----------|----------|------------|
| R1 | Implicit execution signal in AI | A1 | High | H-E1 | Random baseline control |
| R2 | Sandbox divergence | A2 | Medium | H-M3 | Documented environment |
| R3 | Format confounding | A3 | High | H-M1, H-M2 | Template validation |
| R4 | Model capability ceiling | A4 | Medium | All | Two model families |

**Risk Distribution:** Critical: 0, High: 2, Medium: 2, Low: 0

---

## 5. Dependency Graph

### 5.1 DAG Visualization

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 4 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Foundation]
    ┌─────────────────────────────────────┐
    │  H-E1: Existence                    │
    │  Gate: MUST_WORK                    │
    └─────────────────────────────────────┘
                    │
                    ▼
[Level 1 - Mechanism Chain]
    ┌─────────────────────────────────────┐
    │  H-M1: Counterfactual Information   │
    │  Gate: MUST_WORK                    │
    └─────────────────────────────────────┘
                    │
                    ▼
    ┌─────────────────────────────────────┐
    │  H-M2: Targeted Edit Behavior       │
    │  Gate: MUST_WORK                    │
    └─────────────────────────────────────┘
                    │
                    ▼
    ┌─────────────────────────────────────┐
    │  H-M3: Fix Probability              │
    │  Gate: MUST_WORK                    │
    └─────────────────────────────────────┘

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
All gates MUST_WORK for PoC validation
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type | If Fail |
|-------|------------|---------------|-----------|---------|
| 0 | H-E1 | None | MUST_WORK | STOP: Premise invalid |
| 1 | H-M1 | H-E1 | MUST_WORK | PIVOT: Alternative signal |
| 2 | H-M2 | H-M1 | MUST_WORK | EXPLORE: Why no targeting |
| 3 | H-M3 | H-M2 | MUST_WORK | ABANDON: Mechanism fails |

**Verification Phases:**

**Phase 1 - Foundation (H-E1)**
- Gate: Execution feedback provides unique signal
- Pass: Proceed to mechanism validation
- Fail: Research premise invalid, reassess hypothesis

**Phase 2 - Mechanisms (H-M1 → H-M2 → H-M3)**
- Gate: Each mechanism step must validate
- Pass: Causal chain confirmed
- Fail: Document limitation at failing step

---

## 6. Timeline Planning

### 6.1 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 4 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis  │ W1-2     │ W3-4     │ W5       │ W6       │
──────────────────┼──────────┼──────────┼──────────┼──────────┤
PHASE 1: Foundation
  H-E1            │ ████████ │          │          │          │
  [Gate 1]        │          │ ◆        │          │          │
──────────────────┼──────────┼──────────┼──────────┼──────────┤
PHASE 2: Mechanisms
  H-M1            │          │ ████████ │          │          │
  H-M2            │          │          │ ████     │          │
  H-M3            │          │          │          │ ████     │
  [Gate 2]        │          │          │          │     ◆    │
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 5 weeks
═══════════════════════════════════════════════════════════════════
```

### 6.2 Critical Path Analysis

**Critical Path:** H-E1 → H-M1 → H-M2 → H-M3

**Duration Breakdown:**
- H-E1: 2 weeks (existence validation + instrumentation)
- H-M1: 2 weeks (counterfactual extraction + analysis)
- H-M2: 1 week (edit scope measurement)
- H-M3: 1 week (fix success correlation)

**Total Duration:** 5 weeks (sequential, no parallelization)
**Slack Available:** 0 weeks (all on critical path)

### 6.3 Resource Summary

| Resource | Allocation |
|----------|------------|
| Compute | 2x 7B models (CodeLlama, StarCoder) |
| Datasets | HumanEval-164, MBPP-500 |
| Sandbox | E2B or Docker containers |
| AI Critics | GPT-4 API (for AI feedback condition) |

**Estimated Compute:**
- ~10K inference calls per model per benchmark
- ~2K execution sandbox invocations
- Total GPU time: ~48 hours (A100 equivalent)

### 6.4 Execution Order

1. **Week 1-2 (H-E1):** Establish existence of unique execution signal
   - Generate buggy code samples
   - Collect execution traces and AI critiques
   - Compare information content
   - **Gate 1:** Proceed if execution contains unique localization info

2. **Week 3-4 (H-M1):** Validate counterfactual information in traces
   - Annotate error traces for counterfactual structure
   - Quantify counterfactual density
   - **Check:** >70% traces contain counterfactual info

3. **Week 5 (H-M2):** Test targeted edit behavior
   - Compare edit scope with localized vs non-localized feedback
   - Measure diff sizes and edit locations

4. **Week 6 (H-M3):** Correlate edit targeting with fix success
   - Classify edits by scope
   - Measure fix rates per category
   - **Gate 2:** Full mechanism chain validated or failure documented

---

## 7. Dialectical Analysis

### 7.1 Thesis Statement

**Core Claim:** Execution feedback yields higher pass@1 than AI feedback because it provides ground-truth counterfactual error localization that AI must approximate.

**Supporting Evidence:**
1. Error traces contain line numbers, variable values, expected vs actual outputs (direct localization)
2. Self-Debug shows execution-guided refinement achieves ~10% improvement
3. AI critics trained on diverse data lack explicit execution labels (per A1)

**Strengths:**
- Clear falsifiable mechanism: counterfactual info → targeted edits → higher fix rate
- Established precedent: execution-based methods (CodeRL, Self-Debug) show improvements
- Controlled comparison isolates signal from method confounds

**Expected Outcomes:**
- Primary: Execution-detailed > AI-critic > Execution-binary on pass@1
- Secondary: Execution advantage larger on complex tasks (MBPP vs HumanEval)
- Tertiary: Self-critique approaches execution performance if signal learned

### 7.2 Antithesis Development

**Null Hypothesis (H0):** No significant difference in pass@1 between execution and AI feedback when controlling for base model, dataset, and iterations.

**Counter-Arguments:**
1. AI critics may have learned implicit execution patterns from code training data
2. Format differences between execution traces and AI critique may confound comparison
3. Model capability may be the limiting factor, not feedback quality

**Potential Failure Points:**
- R1: If AI feedback contains indirect execution signal, comparison is confounded
- R3: If format normalization loses information, mechanism is obscured
- R4: If models cannot utilize feedback, results reflect capability not signal

**Conditions Under Which H0 Would Be Supported:**
- AI-critic matches or exceeds execution-detailed performance
- Random baseline performs similarly to AI-critic (no signal in AI feedback)
- Both feedback types show similar edit patterns

### 7.3 Synthesis

**Balanced Assessment:**

The hypothesis H-ExecVsAI-v1 presents a testable claim that execution feedback provides superior refinement signal due to ground-truth localization. However, H0 raises valid concerns: AI critics may have implicitly learned execution patterns, or format differences may confound the comparison rather than feedback content.

**Resolution Path:**

The verification plan addresses this dialectic through:
1. **H-E1 (Foundation):** Directly measures information content difference — if AI critique contains equivalent localization info, thesis falls
2. **Random baseline control:** Establishes true no-signal condition, isolating AI critic contribution
3. **Format validation:** Template conversion preserves error type, location, expected/actual to control R3
4. **Two model families:** Tests generalization across CodeLlama and StarCoder

**Conditions for Thesis Support:**
- H-E1 shows execution contains unique localization info
- Execution-detailed > AI-critic with p<0.05, d>0.3
- Edit targeting correlates with feedback type

**Conditions for Antithesis Support:**
- AI-critic matches execution-detailed (implicit signal learned)
- H-E1 fails (no unique information in execution)
- Edit patterns independent of feedback type

**Nuanced Outcome Possibilities:**
1. **Full Support:** All hypotheses pass, clear ordering effect
2. **Partial Support:** H-E1 passes but effect smaller than expected — mechanism exists but less dominant
3. **No Support:** H-E1 fails or AI matches execution — premise invalid

### 7.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Execution signal is unique | May be learned by AI | H-E1 direct comparison |
| Mechanism | Counterfactual → targeting → fix | Alternative pathways | H-M1-3 sequential test |
| Scope | Works on standard benchmarks | May not transfer | Scope documented |
| Performance | Clear ordering effect | Marginal difference | Phase 5 baseline |

**Overall Robustness Score:** Medium-High

**Confidence in Verification Plan:** 0.75

The plan is robust against key failure modes through controls (random baseline, format validation) and sequential gate testing. Remaining uncertainty centers on whether AI critics have implicitly learned execution patterns — H-E1 directly addresses this.

---

## 8. Executive Summary & Conclusions

### 8.1 Executive Summary

**Main Hypothesis:** Execution feedback yields higher pass@1 than AI feedback due to ground-truth error localization
- ID: H-ExecVsAI-v1, Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (Phase 2A available)
- Sub-Hypotheses: 4 total (H-E: 1, H-M: 3)
- Phases: 2 phases over 5 weeks
- Critical Gates: 2 decision points

**Risk Assessment:** Medium
- Primary concerns: AI may contain implicit execution signal (R1), format confounding (R3)

**Immediate Action:** Begin Phase 1 with H-E1 (existence validation)

### 8.2 Final Summary

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: Execution provides unique ground-truth signal
- Gate 1: MUST PASS (if fail, premise invalid)

**Phase 2: Mechanisms** (3 weeks)
- H-M1: Error traces contain counterfactual information
- H-M2: Counterfactual info enables targeted edits
- H-M3: Targeted edits have higher fix probability
- Gate 2: H-M1 must pass; later failures documented as limitations

### 8.3 Conclusions

**Key Achievements:**
- 4 hypotheses across 2 phases (5 weeks total)
- H0 addressed: No difference between feedback types under controlled conditions
- 40% scope reduction from Phase 2A established facts

**Critical Decision Points:**

1. **Gate 1 (Week 2):** H-E1 existence test
   - FAIL: STOP, hypothesis premise invalid
   - PASS: Proceed to mechanism testing

2. **Gate 2 (Week 6):** Mechanism chain validation
   - H-M1 FAIL: PIVOT to alternative signal investigation
   - H-M2-3 FAIL: Document limitation, partial mechanism support

**Open Questions:**
- Does effect hold for larger models (13B+)?
- How does critic model capability affect AI feedback quality?
- What is compute cost tradeoff between feedback types?

**Recommendations:**

1. **Immediate:** Set up execution sandbox (E2B/Docker) and API access (GPT-4 for AI critic)
2. **Resource:** Allocate 5 weeks for critical path, 1 week buffer
3. **Failure Management:** Document all gate failures; execute PIVOT strategies per hypothesis

---

## Appendices

### A. Phase 2A Reference
- **Source:** 03_refinement.yaml (ID: H-ExecVsAI-v1)
- **Schema Version:** 10.0.0
- **Discussion Exchanges:** 7 (all 6 personas converged)

### B. MCP Tool Usage
- **Planned calls:** 4-6 (incremental mode)
- **Tools:** scientificmethod (2x), structuredargumentation (1x)

### C. Established Facts (BUILD_ON)
1. Execution feedback can improve code generation (Self-Debug, CodeRL)
2. AI feedback can improve code generation (Self-Refine, Reflexion)
3. Execution feedback provides ground-truth error localization

---

## State Generation

**Verification State:** Generated (4 sub-hypotheses)
**Pipeline Tasks:** Phase 2B → done, Phase 2C → doing
**Hypothesis Tasks:** Created for H-E1, H-M1, H-M2, H-M3
