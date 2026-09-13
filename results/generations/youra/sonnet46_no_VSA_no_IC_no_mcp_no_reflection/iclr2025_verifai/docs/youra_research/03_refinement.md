# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-31T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop (Independent-Controller Ablation)
- **Gap ID**: gap-2
- **Gap Title**: No Overhead-Normalized Cross-Category Comparison of Formal Feedback Methods
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 8

---

## Research Dialogue Context

**Participants**: Dr. Nova (Creative Novelty Explorer), Prof. Vera (Rigorous Validation Architect), Dr. Sage (Research Impact Evaluator), Prof. Pax (Feasibility & Reality Checker), Dr. Ally (Hypothesis Strengthening Champion), Prof. Rex (Hypothesis Stress-Test Master)

**Total Exchanges**: 8

**Convergence Reason**: All 6 personas participated; all convergence criteria met (SPECIFIC, MECHANISM, PREDICTIONS with quantitative criteria, NOVELTY confirmed, FEASIBILITY confirmed, OBJECTIONS addressed with mitigations)

### Key Insights
1. The "apples-to-oranges" problem (different categories catch different bug types) was reframed as the core contribution — bug-type coverage taxonomy is the novel contribution, not just an efficiency ranking
2. Execution oracle circularity (using evaluation test suite as repair oracle) is a real threat; resolved by using CodeT-style generated tests as oracle, keeping evaluation suite blind
3. SMT's ~40% problem coverage gap is addressed by dual reporting: full-set results (all 4 categories on 538 problems) + matched-subset results (SMT-feasible subset only)
4. Feedback format is a confound (Pyright JSON vs. Z3 natural language counterexample); controlled by standardizing prompt injection template across all categories

### Breakthrough Moments
- **Exchange 7** (Dr. Nova): Reframing from efficiency ranking to bug-type coverage profile taxonomy elevated novelty significantly — the asymmetry in what each category catches becomes the finding, not a limitation
- **Exchange 6** (Prof. Rex): Identifying the SMT coverage problem and proposing dual reporting as the experimental design solution
- **Exchange 4** (Prof. Pax): Confirming all 4 categories are implementable within a $50-100 API budget and <48h compute window

---

## Final Hypothesis

### Title
Formal Feedback Category Efficiency and Bug-Type Coverage in LLM Code Generation

### Hypothesis ID
H-FormalFeedbackComparison-v1

### Core Claim
Under LLM code generation on HumanEval and MBPP benchmarks with a fixed backbone (GPT-4o-mini) and fixed repair budget (3 iterations), if the post-generation verifier type is varied across four formal feedback categories (execution monitoring, static analysis, type checking, SMT solving), then correctness-per-overhead efficiency and bug-type coverage profiles will differ systematically across categories, because feedback signal specificity trades off with computational overhead and matches the dominant error types in these benchmarks.

### Mechanism
Feedback signal specificity trades off with computational overhead across four categories:
1. **Execution monitoring**: cheap (O(ms)), broad signal (pass/fail + error trace), catches any test-failing behavior
2. **Static analysis** (Pyright): cheap (O(100ms)), precise structured errors for type violations (JSON output)
3. **Type checking** (mypy): similar to static analysis, slightly different error coverage
4. **SMT solving** (Z3): expensive (O(1-10s)), exact counterexamples for logic violations, requires property annotations

The dominant error distribution in HumanEval/MBPP (mostly type errors and runtime errors, fewer deep logic violations) predicts execution monitoring and static analysis will dominate efficiency metrics. SMT will show highest per-error specificity on its feasible subset at higher overhead cost.

---

## Predictions

### P1 (Primary): Efficiency Ordering
Execution monitoring achieves the highest Δpass@1 / mean-wall-clock-seconds ratio on HumanEval + MBPP.

**Success criterion**: Execution monitoring ratio ≥ 1.5× next-best category (bootstrap CI, p < 0.05)

**Falsification**: Any other category within 1.5× of execution monitoring ratio

### P2 (Secondary): Bug-Type Coverage
Static analysis improves type-error problems most; execution monitoring improves runtime-error problems most; SMT improves logic-error problems most (on annotatable subset).

**Success criterion**: Chi-squared test significant (p < 0.05) for bug-type × category interaction; each category highest in predicted stratum

**Falsification**: Non-significant interaction or categories show uniform coverage across strata

### P3 (Tertiary): Difficulty Stratification
Harder problems (baseline pass@1 < 30%) show larger absolute pass@1 gains from formal feedback than easier problems, but the efficiency ordering (P1) is preserved within difficulty strata.

**Success criterion**: ANOVA p < 0.05 for difficulty effect on absolute gains; ordering preserved in all three strata

---

## Novelty

**Key innovation**: First controlled cross-category formal feedback comparison with overhead normalization and bug-type coverage profiling enabling diagnostic routing recommendation.

**Differentiation from prior work**:
- Self-Repair (Olausson 2023): single category, no overhead, no cross-comparison
- Reflexion (Shinn 2023): verbal feedback, not formal methods, single category
- CodeT (Bei Chen 2022): selection-based, not repair, execution only
- Grammar-Constrained Decoding (Geng 2023): generation-time constraint, not post-generation repair

---

## Experimental Design

**LLM Backbone**: GPT-4o-mini (temperature 0.2 generation, 0.0 repair)

**Benchmarks**: HumanEval (164 problems) + MBPP (374 problems) = 538 total

**Conditions (4)**:
1. No feedback baseline (vanilla generation)
2. Execution monitoring — CodeT-style generated-test oracle (avoids circularity)
3. Static analysis — Pyright JSON error injection
4. Type checking — mypy error injection
5. SMT solving — Z3 auto-extracted constraints from docstrings (feasible subset ~40%)

**Repair budget**: 3 iterations max; terminate on first pass

**Overhead metric**: Wall-clock seconds per problem

**Pilot**: 20-problem SMT soundness validation before full run

**Cost estimate**: ~$50-100 API budget; <48h compute

---

## Limitations

- SMT comparison restricted to ~40% of HumanEval problems (auto-extractable properties only)
- Bug-type classification is automated heuristic (not ground-truth annotated)
- Results specific to GPT-4o-mini — may not generalize to all LLM families
- Findings may not generalize to repository-level tasks (SWE-bench) or non-Python code
- Wall-clock overhead includes API latency variability — must standardize infrastructure

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | 8 exchanges, all 6 personas, all criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | SMT pilot required; bug-type classifier reliability check |

---

*Phase 2A complete. Ready for Phase 2B planning.*
