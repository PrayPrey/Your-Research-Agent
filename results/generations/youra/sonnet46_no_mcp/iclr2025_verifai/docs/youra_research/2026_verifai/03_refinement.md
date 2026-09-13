# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-05-09T15:30:00
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: gap3
- **Gap Title**: No Complementary Failure Coverage Analysis Comparing SynCode, Z3-Repair, and Static Analysis Feedback on the Same Python-Only Benchmark
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 16
- **Convergence**: Exchange 16 — all 6 criteria met

---

## Research Dialogue Context

**Participants**: Dr. Nova (🔭), Prof. Vera (🔬), Dr. Sage (🎯), Prof. Pax (⚙️), Dr. Ally (🛡️), Prof. Rex (🔍)

**Total Exchanges**: 16 (External LLM: 8 exchanges; Claude: 8 exchanges)

**Convergence Reason**: All 6 convergence criteria met — SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS

### Key Insights
1. The hypothesis evolved from "methods fix different problems" to "conditional mechanistic complementarity measured against an independence null model" — a rigorous operationalization replacing arbitrary Jaccard thresholds.
2. Failure Mass Decomposition (FMD) is an essential pre-experiment step that establishes theoretical repair ceilings and prevents post-hoc rationalization of complementarity claims.
3. The cascade reframing (Dr. Nova, Exchange 14) — viewing sequential staging (SynCode → mypy → Z3) as a test of causal failure hierarchy — is the most novel conceptual contribution.
4. An independence null model (C_score = (E[Jaccard] - J_observed) / E[Jaccard]) provides a principled metric replacing arbitrary thresholds.
5. Synthetic perturbation validation using HumanEval reference solutions provides clean mechanism isolation at minimal cost.

### Breakthrough Moments
- **Exchange 3** (Prof. Rex): Identifying that eligibility restriction masquerades as complementarity → prompted the conditioning framework
- **Exchange 10** (Dr. Sage): Formalizing C_score metric; recognizing null results are equally publishable
- **Exchange 11** (Dr. Ally): Three-block logistic model with difficulty control for mechanistic regression
- **Exchange 14** (Dr. Nova): Cascade reframing — failure types as causally ordered, sequential staging as eligibility expansion test
- **Exchange 16** (Dr. Sage): Synthetic perturbation as a feasible, low-cost mechanism validation step

---

## Final Hypothesis

### Title
**Conditional Mechanistic Complementarity of Formal Repair Strategies for LLM-Generated Python Code**

### Hypothesis ID
`H-FormalComplement-v1`

### Core Claim (Under-If-Then-Because)
Under evaluation of LLM-generated Python code on HumanEval/EvalPlus using CodeLlama-7B with Python-native infrastructure (no Docker), **if** formal repair strategies (SynCode grammar-constrained decoding, Z3-guided post-hoc repair, mypy/ast static analysis feedback) are applied in a causally-ordered sequential pipeline and via feature-aware routing, **then** the ensemble achieves statistically significant pass@1 improvement over any single strategy with failure-to-success transition sets overlapping less than independence expectation (C_score > 0) within eligibility-conditioned, failure-type-stratified subsets, **because** each method operates on a distinct signal channel (decoding prior / structural conformance / symbolic constraint) targeting a different failure class in a causal hierarchy, and sequential staging expands downstream method eligibility by providing cleaner input distributions.

### Null Hypothesis
H0: Within eligibility-conditioned, failure-type-stratified strata, all method pairs exhibit C_score ≤ 0 (overlap consistent with independence expectation); sequential staging provides no eligibility expansion (ΔP ≤ 0); RSS does not outperform best single method (p ≥ 0.05).

### Mechanism (4-step causal chain)
1. **SynCode** eliminates syntactic invalidity at generation time via CFG token masking → produces syntactically valid code pool for subsequent methods
2. **mypy/ast feedback** identifies type violations in syntactically valid code → cleans input distribution for Z3 by resolving type inconsistencies that block SMT encoding
3. **Z3-repair** addresses arithmetic constraint violations in type-consistent code → eligibility expands after Steps 1-2 because code is structurally cleaner
4. **RSS routing** identifies the cost-effective strategy per problem from program features → achieves near-oracle performance at ≤1.3× single-method cost on held-out MBPP

---

## Predictions (Pre-Registered)

### P1 (Primary) — Complementarity
- **Statement**: At least 2 of 3 method pairs exhibit C_score > 0 and J_obs < E[Jaccard] at p < 0.05 within eligibility-conditioned, failure-type-stratified subset
- **Test**: Pairwise Jaccard + independence null model + bootstrap CI at problem level
- **Success criterion**: C_score > 0, J_obs < E[J] at p < 0.05 for ≥2 pairs
- **Falsification**: All pairs show C_score ≤ 0 or J_obs ≥ E[J]

### P2 (Secondary) — Cascade Eligibility
- **Statement**: ΔP(Z3_success | post-mypy) - P(Z3_success | baseline) > 5 percentage points, 95% CI lower bound > 0
- **Test**: Z3 encoding success rate on baseline vs. post-mypy code pools
- **Success criterion**: ΔP > 0.05, bootstrap 95% CI lower bound > 0
- **Falsification**: ΔP ≤ 0 or CI lower bound ≤ 0

### P3 (Secondary) — RSS Routing
- **Statement**: RSS achieves pass@1 > best single method on held-out MBPP at p < 0.05, with cost ratio ≤ 1.3×
- **Test**: Train RSS on HumanEval features; evaluate on MBPP; full cost accounting C_total
- **Success criterion**: RSS_pass@1 > best_single at p < 0.05, cost ratio ≤ 1.3
- **Falsification**: RSS not statistically better than single method, or cost ratio > 1.3

---

## Novelty

**What's New**: First cross-strategy failure-set complementarity analysis for formal methods in LLM Python code generation. Prior work evaluates each method in isolation. This work: (1) applies independence null model to normalize complementarity claims, (2) measures cascade eligibility expansion in sequential staging, (3) validates mechanism via synthetic perturbation, (4) trains feature-aware routing policy across benchmarks.

**Key Differentiators**:
- vs. SynCode [Ugare et al. ~2024]: Evaluated in isolation; no complementarity measurement
- vs. SELF-REFINE [Madaan et al. 2023]: LLM feedback, not formal method signals; no failure-type stratification
- vs. CodeT [Chen MSFT 2022]: Execution ensemble, not formal method complementarity with eligibility conditioning
- vs. LLM repair surveys [Xia et al. 2023]: Per-method analysis only; no cross-strategy measurement protocol

---

## Experimental Design

### Dataset
- **Primary**: HumanEval (164 problems) + EvalPlus HumanEval+ (964 problems)
- **Held-out**: MBPP (374 problems) — RSS routing evaluation
- **Type**: Standard benchmarks; Python-native subprocess evaluation; no Docker

### Model
- **Primary**: CodeLlama-7B (`codellama/CodeLlama-7b-hf`)
- **CPU fallback**: device="auto" — no GPU required
- **Generation pool**: N=20 samples/problem, T=0.8, fixed seeds, frozen

### Baselines
1. Unconstrained CodeLlama-7B (no repair)
2. SynCode-only (grammar-constrained generation)
3. mypy-feedback-only (max 3 rounds)
4. Z3-repair-only (eligible tasks only)
5. Oracle ensemble (oracle-selected best)
6. Parallel full ensemble (all methods applied)

### Experimental Protocol
- **Step 0 (FMD)**: Parallel failure classification — ast.parse, mypy, Z3 encoding, EvalPlus
- **Step 1 (Repair)**: Independent repair per method on baseline pool
- **Step 2 (Complementarity)**: Stratified Jaccard + C_score + independence null model
- **Step 3 (Cascade)**: ΔP(Z3_success | post-mypy) vs. baseline
- **Step 4 (Regression)**: Three-block logistic model with difficulty control
- **Step 5 (Synthetic)**: Perturbation validation on HumanEval reference solutions
- **Step 6 (RSS)**: Train on HumanEval, evaluate on MBPP with cost accounting
- **Step 7 (Pipeline)**: Sequential SynCode → mypy → Z3 vs. parallel baselines

---

## Limitations

- All Phase 1 evidence [INFERRED] — no live MCP verification; requires empirical validation
- Z3 eligibility estimated at ~30–40% of HumanEval problems — may be lower
- Single base model (CodeLlama-7B); complementarity pattern may differ for GPT-4 or larger models
- Synthetic perturbation validation limited to 30 examples (10 per failure type) — sufficient for mechanism confirmation, insufficient for statistical power analysis
- Workshop scope: full ordering ablation (6 permutations) deferred to extended version
- MBPP as held-out set assumes similar feature-repair-success relationships to HumanEval

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | Exchange 16 — all 6 criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | Two minor implementation concerns, both addressed in protocol |
| **Phase 2B Readiness** | READY |

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
*Hypothesis: H-FormalComplement-v1*
*Gap: gap3 — No Complementary Failure Coverage Analysis*
