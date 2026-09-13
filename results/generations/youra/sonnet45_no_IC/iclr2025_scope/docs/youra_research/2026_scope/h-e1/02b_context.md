# Hypothesis Context: H-E1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-07-13
**Main Hypothesis:** Meta-Method Selector for Supervised Learning Benchmarks
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under supervised learning literature mining from target benchmark suites (OGB, FedML, LEAF, pFL-Bench, Champneys, Zhou), if we systematically extract method rankings from published papers, then at least 50 benchmarks with complete baseline comparisons will be collected, because these suites collectively provide diverse coverage across vision, time-series, tabular, and graph domains.

### Type
EXISTENCE

### Rationale
Validates Phase 2A Assumption A1 (≥50 benchmarks needed for robust meta-learning). Without sufficient training data, meta-classifier overfits and predictions fail to generalize.

---

## Verification Protocol

### Conceptual Test
1. Search each target suite systematically and extract dataset metadata, method rankings, and domain labels
2. Filter benchmarks: require ≥3 method comparisons and complete ranking data
3. Count total collected benchmarks and measure domain distribution
4. Statistical check: ≥50 total AND ≥10 per domain

### Success Criteria
- Primary: ≥50 benchmarks collected with complete rankings
- Secondary: Domain diversity ≥3 domains with ≥10 benchmarks each

### Variables
- **Independent Variable:** Target benchmark suites (OGB, FedML, LEAF, pFL-Bench, Champneys NLSI, Zhou medical FL)
- **Dependent Variable:** Count of successfully collected benchmarks with method rankings
- **Controlled Variables:** Minimum 3 methods compared per benchmark, domain diversity (≥3 domains)

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** Aggregated Benchmark Collection
- **Type:** standard
- **Source:** Literature mining: OGB (15 graph datasets), FedML (6), LEAF (5), pFL-Bench (8), Champneys NLSI (5), Zhou medical FL (9), Papers with Code leaderboards (10+)
- **Path:** To be collected from public repositories and published papers
- **Hypothesis Fit:** Collection spans vision/time-series/tabular domains with documented baseline comparisons, providing diverse training examples for meta-learning

### Selected Model
- **Name:** Random Forest Meta-Classifier
- **Type:** Ensemble tree-based classifier
- **Source:** scikit-learn RandomForestClassifier(n_estimators=100, max_depth=10)
- **Hypothesis Fit:** Interpretable (feature importance via SHAP), handles nonlinear feature relationships, robust to small sample sizes, proven for tabular data

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
| Method | Performance | Description |
|--------|-------------|-------------|
| Random Selection | 30% top-30% accuracy (expected) | Uniformly sample method family from {Linear, Polynomial, RNN, Augmentation} |
| Domain Folklore | 40-50% accuracy (expected) | Predict based on domain only (vision→CNN, time-series→RNN) |
| Majority Class | 30-40% accuracy (expected) | Always predict most frequent winner in training set (degeneracy check) |

### Baseline Performance
- Random baseline: 30% expected (4 method families)
- Domain folklore: 40-50% expected (simple heuristics)

### Gap Analysis
Target is ≥50% top-30% success rate, which represents a meaningful improvement over random selection (30%) and competitive with simple domain-based heuristics (40-50%).

---

## Dependencies and Gate Conditions

### Prerequisites
None (foundation hypothesis)

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** IF 40-49: EXPLORE additional sources; IF <40: ABANDON (A1 violated)

**Phase Assignment:** Phase 1 (Collection)

**Estimated Duration:** 1-2 weeks

---

## Dependency Context

### Relationship to Other Hypotheses
This is the foundation hypothesis. All subsequent mechanism hypotheses (H-M1-4) and the condition hypothesis (H-C1) depend on collecting sufficient benchmark data. If this fails, the entire meta-method selector approach is infeasible.

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** IN_PROGRESS
**Workflow Status:** ACTIVE

---

## Phase 2C Usage Notes

**This context file provides:**
1. Complete hypothesis specification for experiment design
2. Gate conditions for prerequisite validation
3. Dependency information for controlled experiments
4. Success criteria for evaluation design
5. **Baseline comparison targets (CRITICAL for H-CP* hypotheses)**

**Phase 2C will:**
1. Load this file instead of full Phase 2B roadmap (91% smaller)
2. Search for implementation patterns (Archon, Exa MCP)
3. Use baseline metrics to set comparison targets
4. Design concrete experiment specification (Level 1.5)
5. Output: /workspace/TEST_scope/docs/youra_research/h-e1/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes
- **H-M* (Mechanism)**: Baseline to understand improvement potential
- **H-C* (Condition)**: Baseline to identify scope boundaries
- **H-CP* (Comparison)**: **MANDATORY** - Direct comparison with baseline methods

---

*Optimized for single-hypothesis experiment design*
