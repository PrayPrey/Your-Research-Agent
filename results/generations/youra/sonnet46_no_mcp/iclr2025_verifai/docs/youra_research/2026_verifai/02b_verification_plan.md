---
stepsCompleted: ["step-00-init-environment", "step-01-init-parsing", "step-02-input-hypothesis", "step-03-hypothesis-generation", "step-04-hypothesis-inventory", "step-05-risk-analysis", "step-06-dependency-graph", "step-07-timeline-planning", "step-08-dialectical-analysis", "step-09-summary", "step-10-finalize"]
status: complete
hypothesis_id: H-FormalComplement-v1
generated_at: "2026-05-09"
completedAt: "2026-05-09T00:00:00"
---

# Verification Plan: Conditional Mechanistic Complementarity of Formal Repair Strategies for LLM-Generated Python Code

**Date:** 2026-05-09
**Hypothesis ID:** H-FormalComplement-v1
**Confidence:** 0.72
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under evaluation of LLM-generated Python code on HumanEval/EvalPlus benchmarks using CodeLlama-7B with Python-native infrastructure (no Docker), if formal repair strategies (SynCode grammar-constrained decoding, Z3-guided post-hoc repair, mypy/ast static analysis feedback) are applied in a causally-ordered sequential pipeline and via feature-aware routing, then the ensemble achieves statistically significant pass@1 improvement over any single strategy (union gain > best-single-method upper 95% bootstrap CI), with failure-to-success transition sets exhibiting overlap below independence expectation (C_score > 0, p < 0.05) within eligibility-conditioned failure-type-stratified subsets, because each method operates on a distinct signal channel (decoding prior / structural conformance / symbolic constraint) that targets a different failure class in a causal hierarchy, and sequential staging expands downstream method eligibility by providing cleaner input distributions.

### 1.2 Alternative Hypothesis (H0)

**H0_complementarity:** Within eligibility-conditioned failure-type-stratified subsets, the pairwise Jaccard similarity of failure-to-success transition sets between any two repair methods is consistent with independence expectation (C_score ≤ 0, or J_obs ≥ E[J] at p < 0.05), meaning methods address the same failure subset and provide no complementary coverage.

**H0_cascade:** Sequential staging (SynCode → mypy → Z3) does not expand downstream Z3 eligibility: ΔP(Z3_success | after mypy) - P(Z3_success | baseline) ≤ 0, meaning causal ordering provides no benefit over independent parallel repair.

**H0_routing:** A Repair Strategy Selector trained on program features does not outperform the best single method on held-out MBPP benchmark: RSS_pass@1 ≤ best_single_method_pass@1 (p < 0.05).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | HumanEval + EvalPlus + MBPP (standard) | Python-native test runners with no Docker dependency; existing pass@k evaluation infrastructure; MBPP provides held-out test set for RSS evaluation. Standardized benchmarks enable direct SOTA comparison. |
| **Model** | CodeLlama-7B | Available via HuggingFace with device='auto' CPU fallback; reusable CodeGenerator from h-e1; 7B parameter scale is tractable without GPU; SynCode supports HuggingFace models via LogitsProcessor wrapper. |

**Dataset Details:**
- Source: evalplus/evalplus GitHub; openai/human-eval GitHub
- Path: Available via evalplus pip package

**Model Details:**
- Type: Decoder-only LLM (code-specialized)
- Source: HuggingFace: codellama/CodeLlama-7b-hf

### 1.4 Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| Unconstrained CodeLlama-7B | ~30–45% pass@1 [INFERRED] | HumanEval |
| SynCode only | ~3–8% pass@1 improvement [INFERRED] | HumanEval/Python |
| SELF-REFINE (LLM self-feedback) | ~4–8% pass@1 improvement [INFERRED] | Various code benchmarks |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | The three repair methods operate on sufficiently orthogonal information channels that their failure-to-success transition sets are not fully correlated by shared latent variables (e.g., overall problem difficulty). | Theoretically motivated by distinct signal channel analysis (prior / structural / symbolic). CodeT [Chen MSFT 2022] shows diverse strategies provide ensemble benefit. | Complementarity claim collapses; C_score ≤ 0; methods address same failure subset. Still publishable as null result. |
| A2 | Z3 constraint encoding is tractable for 30–40% of HumanEval/MBPP problems using only the z3-solver pip package. | Z3 API supports linear integer arithmetic, finite-domain constraints; HumanEval has arithmetic-heavy subset [INFERRED]. | If Z3 eligibility < 15%, cascade and complementarity claims for Z3 are underpowered; paper scope reduces to SynCode + mypy only. |
| A3 | Intra-method repair variance across seeds (Var_seed) is substantially lower than inter-problem variance (Var_problem), making routing signals learnable. | For SynCode: deterministic given same seed. For Z3: deterministic. Var_seed should be low for Z3/SynCode. | RSS routing is not learnable; routing policy contribution dropped from paper. |
| A4 | Sequential staging (SynCode → mypy → Z3) expands downstream eligibility — i.e., the post-mypy code distribution has higher Z3 encoding success rate than baseline-generated code. | Theoretical: type-consistent code is more likely to have encodable arithmetic invariants. Not yet measured empirically. | Cascade hypothesis drops; sequential staging provides no benefit; paper focuses on parallel independent repair complementarity only. |
| A5 | Failure types (syntax, type, constraint, logical) can be classified in parallel (independently) from Python-native signals without sequential dependency. | ast.parse() is independent of mypy; mypy can run on syntactically invalid files with partial output; Z3 encoding attempt is independent of mypy result. | FMD base-rate proportions are order-dependent artifacts; theoretical ceilings are invalid. |

### 1.6 Research Gap & Novelty

**Gap:** No existing study measures pairwise Jaccard similarity of failure sets fixed by SynCode, Z3-repair, and mypy/ast on the same Python-only benchmark.

**Novelty (PROVE NEW claims):**
1. **Complementarity measurement**: First cross-strategy failure-set complementarity analysis using independence null model (C_score metric) on standardized Python-only benchmark.
2. **Cascade eligibility expansion**: First measurement of ΔP(Z3_success | after mypy) as direct test of causal failure hierarchy via sequential staging.
3. **Routing policy (RSS)**: First feature-aware routing policy for formal repair method selection, validated on held-out MBPP benchmark.

**Scope Reduction (43%):** BUILD_ON claims (SynCode operational, benchmark infrastructure, tool availability) do not require re-verification. Focus on PROVE_NEW claims only.

**Differentiation from Prior Work:**
- SynCode [Ugare et al. ~2024]: evaluated in isolation; this work measures complementarity with post-hoc repair methods.
- SELF-REFINE [Madaan et al. 2023]: uses LLM feedback; this work uses formal method signals and measures mechanistic complementarity.
- CodeT [Chen et al. 2022]: ensemble benefit without formal methods or mechanism-specific analysis.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | SHOULD_WORK | H-M2 | NOT_STARTED |
| H-M4 | MECHANISM | SHOULD_WORK | H-M3 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Formal Repair Tool Operationality and Benchmark Accessibility**

**Statement**: Under the Python-native evaluation environment with HumanEval (164 problems) and MBPP (374 problems), if SynCode, z3-solver, and mypy/ast are pip-installed and CodeLlama-7B is loaded via HuggingFace with device='auto', then all three formal repair tools operate correctly on Python code generation tasks (SynCode reduces ast.parse failures, z3-solver encodes ≥15% of HumanEval problems as SMT constraints, mypy.api.run() returns structured type errors) because these tools are pip-installable with Python-native APIs confirmed operational in prior work.

**Rationale**: H-E1 establishes the existence precondition for all mechanism hypotheses. Without confirmed tool operationality and benchmark infrastructure, no complementarity measurement is possible. This is the foundational MUST_WORK gate — failure means the experiment cannot proceed at all.

**Variables**:
- Independent: Formal repair tool identity (SynCode / z3-solver / mypy/ast)
- Dependent: Tool operational status (ast.parse failure rate under SynCode, Z3 encoding eligibility rate, mypy structured error output)
- Controlled: CodeLlama-7B (fixed weights, device=auto), HumanEval + MBPP benchmark access via evalplus pip

**Verification Protocol**:
1. Install all tools (syncode, z3-solver, mypy, evalplus) via pip and verify import success.
2. Generate frozen baseline pool: CodeLlama-7B, N=20 samples per problem, T=0.8, fixed seeds, serialized to disk.
3. Measure SynCode operationality: compare ast.parse failure rate on SynCode-generated vs baseline-generated pool.
4. Measure Z3 eligibility: attempt SMT encoding on baseline pool; record per-problem encoding success/failure rate.
5. Verify mypy/ast feedback loop: run mypy.api.run() on 10 sample problems; confirm structured error output.

**Success Criteria**:
- Primary: SynCode-generated code shows lower ast.parse failure rate than baseline (directional, any reduction)
- Secondary: Z3 eligibility ≥ 15% of HumanEval problems (scope condition for cascade claim)
- Secondary: mypy.api.run() returns parseable structured errors on ≥ 90% of attempts

**Failure Response**:
- IF Z3 eligibility < 15%: SCOPE REDUCTION — drop cascade/Z3 claims; focus on SynCode + mypy complementarity
- IF SynCode has no effect: PIVOT — reassess SynCode integration with current CodeLlama-7B version
- IF mypy API fails: EXPLORE — alternative static analysis (pyflakes, ast-only) as fallback

**Dependencies**: None (H-E1 is the foundation)

**Source**: Phase 2A Section 5 (sh1_existence), Phase 2B Established Facts (BUILD_ON verification)

---

---
**H-M1: Distinct Failure Channel — SynCode Eliminates Syntactic Invalidity**

**Statement**: Under evaluation of CodeLlama-7B-generated Python code using SynCode grammar-constrained decoding vs. unconstrained baseline on HumanEval (N=20 frozen pool per problem), if SynCode is applied at generation time via LogitsProcessor CFG masking, then the SynCode-generated pool shows statistically significant reduction in ast.parse failure rate compared to baseline pool (directional improvement, bootstrap 95% CI), because SynCode masks tokens that violate Python CFG pushdown automaton during generation, eliminating syntactic invalidity by construction.

**Rationale**: H-M1 validates the first causal mechanism: that SynCode's distinct signal channel (generation prior / CFG) produces a qualitatively different failure distribution from unconstrained generation. This establishes that Step 1 of the causal chain operates correctly and cleanses the code pool for subsequent methods.

**Variables**:
- Independent: Generation method (SynCode constrained vs. unconstrained baseline)
- Dependent: ast.parse failure rate per problem (primary); failure mass in "syntax" stratum of FMD (secondary)
- Controlled: CodeLlama-7B (fixed weights), HumanEval frozen pool (N=20, fixed seeds), temperature T=0.8

**Verification Protocol**:
1. Apply Step 0 FMD: parallel failure classification of baseline pool (ast.parse, mypy.api.run, Z3 encoding, EvalPlus) for all 164×20 samples.
2. Generate SynCode pool: same 164 problems with grammar-constrained decoding (separate pool, same seeds as baseline).
3. Compute per-problem ast.parse failure rate for both pools; perform bootstrap CI comparison.
4. Classify SynCode pool with FMD; compare syntax stratum proportion vs. baseline FMD.
5. Record failure-to-success transition set F_SynCode→✓ for complementarity analysis in H-M2/H-M3.

**Success Criteria**:
- Primary: ast.parse failure rate (SynCode) < ast.parse failure rate (baseline), bootstrap 95% CI excludes 0
- Secondary: Syntax failure mass in FMD decreases meaningfully under SynCode

**Failure Response**:
- IF fails: EXPLORE — check SynCode LogitsProcessor integration with CodeLlama-7B tokenizer; verify CFG matches Python 3.x grammar

**Dependencies**: H-E1 (tool operationality confirmed, frozen baseline pool created)

**Source**: Phase 2A Causal Step 1, Prediction P1 (complementarity precondition)

---

---
**H-M2: Distinct Failure Channel — mypy/ast Feedback Addresses Type/Structural Failures and Expands Z3 Eligibility**

**Statement**: Under evaluation of CodeLlama-7B-generated Python code using mypy/ast iterative feedback (max 3 rounds) on HumanEval baseline pool within eligibility-conditioned, failure-type-stratified subsets, if mypy-feedback is applied post-generation, then (a) the mypy-feedback failure-to-success transition set F_mypy→✓ exhibits Jaccard overlap below independence expectation with F_SynCode→✓ (C_score > 0, p < 0.05) within the type/structural failure stratum, AND (b) Z3 encoding success rate on post-mypy code is higher than on baseline code (ΔP > 0.05), because mypy/ast operates on a structural/type conformance signal channel orthogonal to SynCode's generation prior.

**Rationale**: H-M2 tests two aspects of the second causal step: (a) complementarity between SynCode and mypy, and (b) cascade eligibility expansion — that type-consistent post-mypy code has higher Z3 encodability. This is the core mechanistic test for the independence of signal channels.

**Variables**:
- Independent: Repair method identity (mypy-feedback vs. SynCode, within eligibility-conditioned strata)
- Dependent: C_score (pairwise Jaccard complement within stratified subset); ΔP(Z3_success | post-mypy vs. baseline)
- Controlled: CodeLlama-7B baseline pool (frozen), eligibility conditioning (mypy-eligible problems only), difficulty quintile stratification

**Verification Protocol**:
1. Apply mypy-feedback loop (max 3 rounds) on baseline pool; log all repair attempts and success/failure per problem.
2. Compute F_mypy→✓ (set of problems where mypy-feedback caused failure-to-success transition).
3. Compute Jaccard(F_SynCode→✓, F_mypy→✓), E[Jaccard] = (r1×r2)/(r1+r2-r1×r2), C_score = (E[J]-J_obs)/E[J] within eligibility ∩ type/structural failure stratum.
4. Perform bootstrap CI at problem level; apply Bonferroni correction for multiple pair comparisons.
5. Attempt Z3 SMT encoding on baseline pool and post-mypy pool; compare encoding success rates with bootstrap CI.

**Success Criteria**:
- Primary: C_score(SynCode, mypy) > 0 AND J_obs < E[J] at p < 0.05 within eligibility-conditioned type/structural failure stratum
- Secondary: ΔP(Z3_eligible | post-mypy) - P(Z3_eligible | baseline) > 0.05, 95% CI lower bound > 0

**Failure Response**:
- IF C_score ≤ 0: Document as null result (equally publishable per Dr. Sage's assessment); refocus on Z3 cascade claim
- IF ΔP ≤ 0: CASCADE HYPOTHESIS DROPS — sequential staging provides no eligibility benefit; paper focuses on parallel complementarity only

**Dependencies**: H-M1 (SynCode pool and FMD classification complete, baseline pool frozen)

**Source**: Phase 2A Causal Step 2, Predictions P1 and P2

---

---
**H-M3: Distinct Failure Channel — Z3-Repair Addresses Arithmetic Constraint Failures**

**Statement**: Under evaluation of CodeLlama-7B-generated Python code using Z3-guided SMT repair on the Z3-eligible subset of HumanEval baseline problems (arithmetic constraint failures only), if Z3-repair is applied post-generation on problems with tractable SMT encodings, then the Z3 failure-to-success transition set F_Z3→✓ exhibits Jaccard overlap below independence expectation with both F_SynCode→✓ and F_mypy→✓ (C_score > 0, p < 0.05) within the constraint/logical failure stratum, because Z3 operates via symbolic constraint satisfaction — a fundamentally different signal channel from syntactic (SynCode) and type-structural (mypy) repair.

**Rationale**: H-M3 tests the third causal channel: symbolic constraint satisfaction addresses constraint-type failures that neither SynCode nor mypy can address. Confirming all three pairwise C_scores > 0 (or ≥2 of 3) validates the core claim that the three methods partition the failure space by mechanism.

**Variables**:
- Independent: Repair method identity (Z3-repair vs. SynCode and mypy, within Z3-eligible constraint failure stratum)
- Dependent: C_score(SynCode, Z3) and C_score(mypy, Z3) within Z3-eligible, constraint/logical failure stratum
- Controlled: Z3-eligible subset only (tractable SMT encoding confirmed), 60s timeout per problem, z3-solver Python API

**Verification Protocol**:
1. Apply Z3-repair on Z3-eligible baseline problems: extract arithmetic invariants from failing test assertions; search for constraint-satisfying repairs.
2. Compute F_Z3→✓ (problems where Z3-repair succeeded).
3. Compute Jaccard and C_score for pairs (SynCode, Z3) and (mypy, Z3) within Z3-eligible ∩ constraint/logical failure stratum.
4. Run synthetic perturbation validation: inject 10 constraint-violation examples into HumanEval reference solutions; verify Z3 (not SynCode/mypy) repairs them.
5. Run three-block logistic regression per method with difficulty control to assess mechanistic attribution.

**Success Criteria**:
- Primary: C_score > 0 AND J_obs < E[J] at p < 0.05 for ≥2 of 3 method pairs within eligibility-conditioned failure-type-stratified subset
- Secondary: Synthetic perturbation shows Z3 repairs constraint violations while SynCode/mypy do not

**Failure Response**:
- IF all C_scores ≤ 0: SCOPE — report null result (methods address same failures); publishable per pre-registration
- IF Z3 eligibility too low for statistical power: SCOPE REDUCTION — focus on SynCode + mypy complementarity pair only

**Dependencies**: H-M2 (cascade eligibility test complete, mypy pool generated)

**Source**: Phase 2A Causal Step 3, Prediction P1 (primary success criterion)

---

---
**H-M4: Feature-Aware Routing Policy (RSS) Approaches Oracle Performance**

**Statement**: Under evaluation of a logistic regression Repair Strategy Selector (RSS) trained on program features (arithmetic density, type annotation richness, AST depth, cyclomatic complexity, baseline syntax invalidity rate) from HumanEval complementarity results, if RSS is applied to route each MBPP problem to the predicted best single repair strategy, then RSS achieves pass@1 on held-out MBPP (374 problems) that exceeds the best single method's pass@1 (p < 0.05) at ≤1.3× computational cost, because the variance decomposition shows Var_problem >> Var_seed (routing is learnable) and program features reliably predict which repair channel is most effective for a given problem.

**Rationale**: H-M4 tests the practical deployability of the complementarity finding: if methods target different failure classes, then measurable program features should predict which method to apply, enabling a cost-effective routing policy that outperforms any single method. This converts the mechanistic finding into a deployable artifact.

**Variables**:
- Independent: Routing strategy (RSS-routed vs. best-single-method, oracle ensemble)
- Dependent: pass@1 on MBPP (374 problems); cost ratio C_total_RSS / C_total_best_single
- Controlled: HumanEval as training data (no MBPP leakage), logistic regression classifier, fixed feature extraction pipeline

**Verification Protocol**:
1. Perform variance decomposition on HumanEval repair results: mixed-effects model separating Var_problem vs. Var_seed; confirm Var_problem >> Var_seed before proceeding.
2. Extract program features per HumanEval problem: AST depth, arithmetic density, annotation richness, cyclomatic complexity, baseline syntax invalidity rate.
3. Train logistic regression RSS on HumanEval feature-repair-success pairs; evaluate feature coefficient stability.
4. Apply RSS routing decisions to MBPP (374 problems); report Δpass@1 vs. best single method with bootstrap CI.
5. Compute full cost accounting C_total = C_gen + C_feature + C_eligibility + C_repair + C_verify; report cost ratio.

**Success Criteria**:
- Primary: RSS_pass@1 > best_single_pass@1 at p < 0.05 (bootstrap), AND C_total_RSS / C_total_best_single ≤ 1.3
- Secondary: Variance decomposition confirms Var_problem >> Var_seed (routing signal is learnable)

**Failure Response**:
- IF Var_seed >> Var_problem: ABANDON routing claim — report as null; remove RSS contribution from paper
- IF RSS does not outperform best single: DOCUMENT — report as failure; publishable as "routing not learnable at this scale"

**Dependencies**: H-M3 (all pairwise complementarity scores computed, HumanEval per-problem repair results available)

**Source**: Phase 2A Causal Step 4, Prediction P3

---

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | All tools operational, Z3 eligibility ≥15% | STOP — reassess entire approach |
| H-M1 | MUST_WORK | SynCode reduces ast.parse failures (directional, CI > 0) | EXPLORE integration issues |
| H-M2 | SHOULD_WORK | C_score(SynCode,mypy) > 0 AND/OR ΔP(Z3) > 0.05 | Document null; focus on other claims |
| H-M3 | SHOULD_WORK | ≥2 of 3 C_scores > 0 at p < 0.05 | Report null; publishable as pre-registered failure |
| H-M4 | SHOULD_WORK | RSS_pass@1 > best_single at p < 0.05, cost ≤ 1.3× | Drop routing claim; report null |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Core Mechanisms | H-M1, H-M2, H-M3, H-M4 | 5 weeks (2+1+1+1) |

**Total Duration:** 7 weeks

---

## 4. Risk Analysis

### 4.1 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: Methods share latent failure predictors | A1 | H-M2, H-M3 | High |
| R2: Z3 eligibility too low (<15%) | A2 | H-E1, H-M2, H-M3 | High |
| R3: Routing not learnable (Var_seed ≥ Var_problem) | A3 | H-M4 | Medium |
| R4: No cascade eligibility expansion | A4 | H-M2 | Medium |
| R5: FMD order-dependent artifacts | A5 | H-M1, H-M2, H-M3 | Medium |

### 4.2 Mitigation Strategies

**Risk R1: Methods share latent failure predictors (A1 violated)**
- **Severity:** High
- **Affected:** H-M2, H-M3
- **Prevention:** Apply eligibility conditioning AND difficulty quintile stratification before Jaccard analysis to remove confounds.
- **Detection:** Check C_score across raw / eligibility-conditioned / difficulty-stratified subsets; if C_score disappears after conditioning, R1 is materializing.
- **Response:**
  - SCOPE: Report null result per pre-registration (publishable per Dr. Sage's assessment)
  - PIVOT: Focus analysis on synthetic perturbation validation (inject known failure types; measure which method repairs which)
  - Paper narrative pivots to "formal method repair sets are correlated by problem difficulty, not by mechanism"

**Risk R2: Z3 eligibility too low (<15%) (A2 violated)**
- **Severity:** High
- **Affected:** H-E1 (scope condition), H-M2 (ΔP claim), H-M3 (Z3 pair complementarity)
- **Prevention:** Measure Z3 eligibility as part of H-E1 FMD Step 0 before committing to Z3 claims.
- **Detection:** Z3 encoding attempt success rate < 15% on HumanEval FMD classification.
- **Response:**
  - SCOPE REDUCTION: Drop Z3 cascade and complementarity claims; refocus paper on SynCode + mypy complementarity pair
  - The C_score(SynCode, mypy) pair remains testable regardless of Z3 eligibility
  - Paper scope narrows but remains publishable

**Risk R3: Routing not learnable (Var_seed ≥ Var_problem) (A3 violated)**
- **Severity:** Medium
- **Affected:** H-M4 only
- **Prevention:** Run variance decomposition as first step of H-M4 before training RSS.
- **Detection:** Mixed-effects model shows Var_seed / Var_problem ratio > 0.5.
- **Response:**
  - ABANDON H-M4: Drop routing policy from paper; document as null finding
  - Paper retains H-E1, H-M1, H-M2, H-M3 contributions

**Risk R4: No cascade eligibility expansion (A4 violated)**
- **Severity:** Medium
- **Affected:** H-M2 (ΔP component only)
- **Prevention:** Pre-register cascade claim as secondary hypothesis; main complementarity claim (C_score) is independent.
- **Detection:** ΔP ≤ 0 with CI lower bound ≤ 0.
- **Response:**
  - SCOPE: Drop cascade claim; paper focuses on parallel independent repair complementarity
  - Complementarity (C_score) claim unaffected by cascade failure

**Risk R5: FMD order-dependent artifacts (A5 violated)**
- **Severity:** Medium
- **Affected:** H-M1, H-M2, H-M3 (FMD-based stratification)
- **Prevention:** Run FMD in parallel (not sequential): ast.parse, mypy.api.run, Z3 encoding attempt all run independently on same samples.
- **Detection:** Compare sequential vs. parallel FMD classification outputs on 10-sample validation subset.
- **Response:**
  - EXPLORE: Determine which classification is order-dependent; use only order-independent classifiers (ast.parse is fully independent)
  - FALLBACK: Use binary FMD (syntax/non-syntax only) if parallel classification is infeasible

### 4.3 Risk Summary Table

| ID | Risk | Source | Severity | Affected | Mitigation |
|----|------|--------|----------|----------|------------|
| R1 | Shared latent failure predictors | A1 | High | H-M2, H-M3 | Eligibility + difficulty stratification; null publishable |
| R2 | Z3 eligibility < 15% | A2 | High | H-E1, H-M2, H-M3 | Measure first in H-E1; drop Z3 claims if below threshold |
| R3 | Routing not learnable | A3 | Medium | H-M4 | Variance decomposition before RSS training; drop if fails |
| R4 | No cascade expansion | A4 | Medium | H-M2 | Pre-registered secondary; main C_score claim independent |
| R5 | FMD order-dependent | A5 | Medium | H-M1-3 | Parallel FMD; validate with sequential comparison |

Critical Risks: 0
High Risks: 2 (R1, R2)
Medium Risks: 3 (R3, R4, R5)
Low Risks: 0

---

## 5. Dependency Graph & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1 (EXISTENCE - Formal Tool Operationality)
    [GATE 1: MUST_WORK → failure = STOP]
         │
         ▼
[Level 1 - Mechanism Step 1]
    H-M1 ← H-E1 (SynCode Distinct Channel)
    [GATE 2: MUST_WORK → failure = EXPLORE then STOP if unresolvable]
         │
         ▼
[Level 2 - Mechanism Step 2]
    H-M2 ← H-M1 (mypy Complementarity + Cascade)
    [GATE 3: SHOULD_WORK → failure = document null, continue]
         │
         ▼
[Level 3 - Mechanism Step 3]
    H-M3 ← H-M2 (Z3 Complementarity + Synthetic Validation)
    [GATE 4: SHOULD_WORK → failure = document null, continue]
         │
         ▼
[Level 4 - Mechanism Step 4]
    H-M4 ← H-M3 (RSS Routing Policy)
    [GATE 5: SHOULD_WORK → failure = drop routing claim]

═══════════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
No parallel branches (all sequential chain)
═══════════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy Table

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-M1 | SHOULD_WORK |
| 3 | H-M3 | H-M2 | SHOULD_WORK |
| 4 | H-M4 | H-M3 | SHOULD_WORK |

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis │ W1-2    │ W3-4    │ W5      │ W6      │ W7
─────────────────┼─────────┼─────────┼─────────┼─────────┼────────
PHASE 1: Foundation
  H-E1           │ ████████│         │         │         │
  [Gate 1]       │        ◆│         │         │         │
─────────────────┼─────────┼─────────┼─────────┼─────────┼────────
PHASE 2: Core Mechanisms
  H-M1           │         │ ████████│         │         │
  [Gate 2]       │         │        ◆│         │         │
  H-M2           │         │         │ ████    │         │
  [Gate 3]       │         │         │     ◆   │         │
  H-M3           │         │         │         │ ████    │
  [Gate 4]       │         │         │         │     ◆   │
  H-M4           │         │         │         │         │ ████
  [Gate 5]       │         │         │         │         │     ◆
─────────────────┼─────────┼─────────┼─────────┼─────────┼────────
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 7 weeks
Formula: 2 (H-E1) + 2 (H-M1) + 1 (H-M2) + 1 (H-M3) + 1 (H-M4) = 7 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4

Total Duration: 7 weeks
  Formula: 2 (H-E1) + 2 (H-M1) + 1 (H-M2) + 1 (H-M3) + 1 (H-M4)

Slack Available: 0 weeks (all sequential chain)

Parallelization Opportunities: None in Phase 2 PoC
  Note: H-M3 synthetic perturbation could overlap with H-M2 cascade test
  (same baseline pool), but kept sequential for clarity.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.5 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Hypotheses: 5
- Existence: 1 (H-E1)
- Mechanism: 4 (H-M1 to H-M4)
- Condition: 0 (none needed)

Verification Phases: 2
1. Foundation (H-E1): Tool operationality + FMD setup
2. Mechanisms (H-M1-4): Complementarity + cascade + routing

Total Duration: 7 weeks
Critical Path Length: 7 weeks
Execution Mode: Sequential chain (MUST_WORK → SHOULD_WORK chain)

Compute Requirements:
- CodeLlama-7B: CPU fallback (device=auto); no GPU required
- Generation: 164 × 20 = 3280 samples baseline; same for SynCode pool
- MBPP: 374 problems × 20 samples for RSS evaluation
- Z3: 60s timeout per eligible problem (~50-65 problems on HumanEval)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Execution Order

```
Step 1: Execute H-E1 (Foundation) — Week 1-2
  - Install tools, generate frozen baseline pool, run FMD Step 0
  - Measure SynCode operationality, Z3 eligibility, mypy API
Step 2: Evaluate Gate 1 (MUST_WORK) — End of Week 2
  - PASS (Z3 ≥ 15%) → proceed to Phase 2 full scope
  - PARTIAL (Z3 < 15%) → proceed with scope reduction (drop Z3 claims)
  - FAIL (tools broken) → STOP
Step 3: Execute H-M1 (SynCode channel) — Week 3-4
  - Generate SynCode pool, compute F_SynCode→✓, bootstrap CI
Step 4: Evaluate Gate 2 (MUST_WORK) — End of Week 4
  - PASS → proceed to H-M2
  - FAIL → EXPLORE integration fix; if unresolvable → STOP
Step 5: Execute H-M2 (mypy complementarity + cascade) — Week 5
  - Apply mypy-feedback, compute F_mypy→✓, C_score(SynCode,mypy), ΔP(Z3)
Step 6: Evaluate Gate 3 (SHOULD_WORK) — End of Week 5
  - Any result → document and proceed (null results publishable)
Step 7: Execute H-M3 (Z3 complementarity + synthetic validation) — Week 6
  - Apply Z3-repair, compute F_Z3→✓, pairwise C_scores, synthetic perturbation
Step 8: Evaluate Gate 4 (SHOULD_WORK) — End of Week 6
  - Any result → document and proceed
Step 9: Execute H-M4 (RSS routing) — Week 7
  - Variance decomposition, train RSS, evaluate on MBPP, cost accounting
Step 10: Final Gate 5 (SHOULD_WORK) → Verification complete
```

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** Formal repair methods (SynCode, Z3-repair, mypy/ast) exhibit conditional mechanistic complementarity on LLM-generated Python code: within eligibility-conditioned, failure-type-stratified subsets of HumanEval/EvalPlus, their failure-to-success transition sets overlap less than predicted by independence expectation (C_score > 0). Moreover, sequential staging expands downstream Z3 eligibility, and a feature-aware routing policy approaches oracle ensemble performance at sublinear cost on held-out MBPP.

**Supporting Evidence:**
1. Three information channels are theoretically orthogonal: generation prior (SynCode/CFG), type system (mypy/ast), constraint algebra (Z3/SMT) — confirmed by Phase 2A Round Table consensus.
2. CodeT [Chen MSFT 2022] demonstrates ensemble benefit from diverse repair strategies; formal methods provide stronger channel separation than heuristic diversity.
3. Cascade eligibility expansion is theoretically motivated: type-consistent code (post-mypy) has higher SMT encodability because type consistency is a prerequisite for extracting arithmetic invariants.

**Strengths:**
- First cross-strategy failure-set complementarity analysis on standardized benchmark
- Three publishable outcomes (strong/partial/null) — all advance field understanding
- Pre-registered falsification criteria prevent HARKing (Hypothesizing After Results Known)
- FMD establishes theoretical repair ceilings before complementarity claims

**Expected Outcomes:**
- P1: C_score > 0, J_obs < E[J] at p < 0.05 for ≥2 method pairs within eligibility-conditioned strata
- P2: ΔP(Z3_eligible | post-mypy) > 0.05, 95% CI lower bound > 0
- P3: RSS_pass@1 > best_single at p < 0.05, cost ratio ≤ 1.3×

### 6.2 Antithesis

**Null Hypothesis (H0):** Within eligibility-conditioned failure-type-stratified strata, all method pairs exhibit C_score ≤ 0 (overlap consistent with or exceeding independence expectation). Sequential staging provides no eligibility benefit (ΔP ≤ 0). RSS does not outperform best single method (RSS_pass@1 ≤ best_single at p < 0.05).

**Counter-Arguments:**
1. **Shared difficulty confound (Prof. Rex, Round Table):** Overall problem difficulty may drive failure rates for all three methods simultaneously — harder problems fail under all methods, easier problems succeed under all — producing positive Jaccard overlap that masquerades as correlation. Eligibility conditioning addresses this but may not fully resolve difficulty-based correlation.
2. **Z3 non-applicability (A2 risk):** Z3 eligibility may be too low (<15%) to achieve statistical power for Z3-specific claims. If most HumanEval problems are not arithmetically constrained, Z3 repairs a negligible subset with high variance.
3. **Routing signal noise (A3 risk):** If LLM stochasticity introduces per-seed variance comparable to per-problem variance, program features cannot reliably predict repair success — the routing signal is dominated by noise.

**Potential Failure Points:**
- R1 materializes: High-difficulty problems fail under all methods regardless of failure type → C_score ≤ 0 for all pairs
- R2 materializes: Z3 eligibility < 15% → Z3 claims underpowered, cascade measurement impossible
- R5 materializes: FMD classification is order-dependent → failure type stratification is an artifact

**Conditions Under Which H0 Would Be Supported:**
- All three C_score values ≤ 0 within eligibility-conditioned strata
- ΔP(Z3 | post-mypy) ≤ 0 with CI lower bound ≤ 0
- Synthetic perturbation shows cross-method repair (Z3 repairs type errors, SynCode repairs constraint failures)

### 6.3 Synthesis

**Balanced Assessment:**

The hypothesis H-FormalComplement-v1 presents a testable claim backed by theoretical motivation from three orthogonal signal channels. However, the null hypothesis raises valid concerns regarding shared difficulty confounds and Z3 eligibility limitations.

**Resolution Path:** The verification plan addresses this dialectic through:
1. **Foundation verification (H-E1):** Establishes tool operationality and measures Z3 eligibility before committing to Z3 claims — null result at H-E1 scopes the paper, not terminates it.
2. **Eligibility conditioning + difficulty stratification:** Three-tier analysis (raw → eligibility-conditioned → failure-type-stratified) addresses Prof. Rex's eligibility masquerade concern directly.
3. **Independence null model (C_score):** Replaces arbitrary Jaccard thresholds with principled statistical operationalization — eliminates subjective threshold choice.
4. **Pre-registered null results as publishable:** All three failure scenarios (strong/partial/null complementarity) are publishable and advance field understanding.

**Conditions for Thesis Support:**
- H-E1 MUST_WORK gate passes (tools operational, Z3 ≥ 15%)
- H-M1 MUST_WORK gate passes (SynCode reduces syntax failures)
- ≥2 of 3 C_scores > 0 within eligibility-conditioned strata

**Conditions for Antithesis Support:**
- H-E1 scope condition fails (Z3 < 15%) → cascade/Z3 claims dropped
- H-M1 fails → SynCode not operating as expected on CodeLlama-7B
- All C_scores ≤ 0 within conditioned strata → null complementarity result

**Nuanced Outcome Possibilities:**
1. **Full Support:** All C_scores > 0, ΔP > 0.05, RSS outperforms → Complete thesis validated; strongest paper version.
2. **Partial Support (most likely):** SynCode + mypy complementarity confirmed (C_score > 0), Z3 claims dropped (low eligibility or low power), RSS not learnable → Refined thesis; still publishable contribution.
3. **No Complementarity:** All C_scores ≤ 0 → Antithesis supported; null result publishable as "formal method repair sets are correlated by problem difficulty, not mechanism." Pre-registered so not buried.

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Tool Operationality | Tools pip-installable and operational | Z3 eligibility may be too low | H-E1 measures eligibility; scope reduction triggered if needed |
| Mechanism Distinctness | Three orthogonal signal channels | Difficulty confound correlates all methods | Eligibility conditioning + difficulty stratification + three-block logistic regression |
| Cascade Benefit | Type-consistent code expands Z3 eligibility | No empirical evidence for eligibility expansion | H-M2 directly measures ΔP; pre-registered as secondary hypothesis |
| Routing Performance | Program features predict repair success | Var_seed too high for learnable signal | Variance decomposition in H-M4; drop routing claim if fails |
| Scope | Python-native, HumanEval/MBPP, CodeLlama-7B | Single model, single language, inferred evidence | Explicit limitation; pre-registered scope conditions |

**Overall Robustness:** Medium-High
- Strong: Theoretical motivation, pre-registered criteria, three publishable outcomes, independence null model
- Weak: All Phase 1 evidence is INFERRED; Z3 eligibility estimate (30-40%) not empirically confirmed

**Confidence in Verification Plan:** 0.72 (from Phase 2A)

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** H-FormalComplement-v1 — Conditional Mechanistic Complementarity of Formal Repair Strategies
- ID: H-FormalComplement-v1, Confidence: 0.72, Mode: Incremental

**Verification Structure:**
- Sub-Hypotheses: 5 total (H-E1, H-M1, H-M2, H-M3, H-M4)
  - H-E: 1 (existence/operationality), H-M: 4 (causal chain)
- Phases: 2 phases over 7 weeks
- Critical Gates: 5 decision points (1 MUST_WORK × 2, 3 SHOULD_WORK)
- Scope Reduction: 43% (BUILD_ON claims skip re-verification)

**Risk Assessment:** Medium
- Primary concerns: Z3 eligibility too low (R2, High), shared difficulty confounds (R1, High)
- All failure scenarios pre-registered and publishable

**Immediate Action:** Begin Phase 1 with H-E1 (tool operationality + FMD baseline measurement)

### 7.2 Conclusions

**Key Achievements:**
- 5 hypotheses across 2 phases, addressing 3 PROVE_NEW claims from Phase 2A
- H0 fully operationalized: C_score ≤ 0 / ΔP ≤ 0 / RSS_pass@1 ≤ best_single (all pre-registered)
- 43% scope reduction from BUILD_ON claims (tool operationality, benchmark infrastructure)

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: Install tools, generate baseline pool (N=20/problem), run FMD, measure SynCode operationality, Z3 eligibility, mypy API
- Gate 1 (MUST_WORK): If Z3 < 15% → scope reduction; if tools broken → STOP

**Phase 2: Core Mechanisms** (5 weeks)
- H-M1: Generate SynCode pool; compute F_SynCode→✓; bootstrap CI on ast.parse failure rate
- H-M2: Apply mypy-feedback; compute F_mypy→✓; C_score(SynCode,mypy); ΔP(Z3 eligibility)
- H-M3: Apply Z3-repair; compute F_Z3→✓; pairwise C_scores; synthetic perturbation; three-block logistic regression
- H-M4: Variance decomposition; train RSS on HumanEval; evaluate on MBPP (374 problems); cost accounting
- Gates 2-5: H-M1 MUST_WORK; H-M2-4 SHOULD_WORK (failure = document null, continue)

**Critical Decision Points:**

1. **Gate 1 (Foundation, End Week 2):** H-E1 MUST_WORK
   - Z3 < 15% → SCOPE: drop Z3 claims, continue with SynCode + mypy scope
   - Tools broken → STOP: reassess experimental approach
   - PASS → Full scope proceeds

2. **Gate 2 (SynCode Channel, End Week 4):** H-M1 MUST_WORK
   - FAIL → EXPLORE integration fix; if unresolvable → STOP
   - PASS → SynCode channel confirmed; proceed to complementarity measurement

3. **Gates 3-5 (Mechanism Claims, Weeks 5-7):** SHOULD_WORK
   - Any result → Document (null results pre-registered and publishable); continue to next

**Open Questions (from Phase 2A):**
- Actual Z3 eligibility rate on HumanEval/MBPP: is 30–40% estimate accurate?
- Variance decomposition (Var_problem vs. Var_seed) — is routing signal learnable?
- Does cascade staging provide measurable ΔP(Z3_success) improvement?
- Are failure types truly classifiable in parallel without order dependence?
- Does synthetic perturbation validation confirm mechanism specificity?

**Recommendations:**
1. **Immediate:** Run H-E1 FMD Step 0 (parallel failure classification) as first action — determines full scope of experiment.
2. **Resource:** Allocate 7 weeks on CPU-only machine (device=auto); all tools pip-installable, no Docker.
3. **Failure Management:** Pre-register all null results; execute scope reduction rather than hypothesis abandonment when possible.
4. **Reporting:** Prepare three-version paper skeleton (full support / partial support / null) before starting experiments.

### 7.3 Appendices

**A. Phase 2A Reference:**
- Source: 03_refinement.yaml (ID: H-FormalComplement-v1, generated 2026-05-09)
- Discussion: 16 exchanges, 6 agents (Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex)
- Convergence: All 6 criteria at exchange 16

**B. MCP Tool Usage Summary:**
- Total MCP calls: 0 (no-mcp environment; workflow executed inline using Phase 2A data directly)
- Compensation: MCP scientific method synthesis performed manually from Phase 2A causal chain (4 steps → H-M1-4)

---

*Generated by YouRA Phase 2B (v7.7.0) | 2026-05-09*
