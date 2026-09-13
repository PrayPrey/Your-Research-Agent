# Hypothesis Context: H-M-integrated

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-03-18
**Main Hypothesis:** H-AlignmentSignatures-v1
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
If alignment methods shape model output distributions through implicit optimization (3-step causal chain: feedback signal selection → repeated training exposure → observable signatures), then we will observe: (M1) execution-focused models dominate correctness dimension (top 15% pass@k rank), (M2) preference-focused models show balanced performance (top 30% across all dimensions), (M3) training dynamics create consistent within-method clustering (intracluster variance < intercluster distance), because feedback signals define what models optimize during alignment training.

### Type
Mechanism

### Rationale
This tests the mechanistic explanation for why clustering exists. Validates that feedback signal theory (models optimize what they're trained on) explains observed signatures through objective-specific dominance patterns.

---

## Verification Protocol

### Conceptual Test
1. Rank all models independently on each dimension (correctness, complexity, efficiency)
2. Compute percentile rankings per alignment method group
3. Test M1: execution models mean correctness rank ≤ 15th percentile
4. Test M2: preference models mean rank ≤ 30th percentile across ALL three dimensions
5. Test M3: within-method variance < between-method variance (Mann-Whitney U test, p < 0.05)

### Success Criteria
- Primary: M1 AND M2 hold (objective-specific dominance demonstrated)
- Secondary: M3 holds (clustering consistency validated)

### Variables
- **Independent Variable:** Feedback Signal Structure (binary pass/fail, comparative preference pairs, none)
- **Dependent Variable:** Correctness Dominance (percentile rank), Balanced Performance (mean rank), Intracluster Variance
- **Controlled Variables:** Same models as H-E1, Python-only, normalized metrics

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** HumanEval+
- **Type:** standard
- **Source:** EvalPlus (open-source benchmark suite)
- **Path:** https://github.com/evalplus/evalplus
- **Hypothesis Fit:** HumanEval+ provides 164 function-level Python programming tasks with test suites, enabling controlled pass@k measurement. Extended test suite (HumanEval+) reduces test case variance compared to original HumanEval. Task distribution suitable for clustering analysis with 60-80 samples per model.

### Selected Model
- **Name:** 6-8 Python code generation models
- **Type:** Open-source LLMs accessible via HuggingFace
- **Source:** HuggingFace Model Hub
- **Hypothesis Fit:** Model selection criteria: Execution-focused (2-3 models): SelfCodeAlign-7B, StepCoder, CodeLlama-Python-7B-Instruct; Preference-focused (2-3 models): Models trained with DPO/RLAIF (if publicly available); Baselines (1-2 models): CodeLlama-7B-Base, StarCoder-Base. All models share Python language, varying alignment methods. Llama-3-8B family preferred for base model consistency when available.

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
- SelfCodeAlign (Wei et al., 2024): 67.1% pass@1 on HumanEval+, 55 citations
- PrefGen (Peng et al., 2025): Balanced Pass@k + Gas@k + Secure@k for smart contracts, 3 citations
- NaturalCodeBench (Zhang et al., 2024): Shows 80% HumanEval → 20% real-world task mismatch, 22 citations

### Baseline Performance
SelfCodeAlign: 67.1% pass@1 on HumanEval+

### Gap Analysis
This hypothesis tests the mechanism behind alignment method signatures observed in H-E1. The baselines demonstrate different optimization objectives (execution-focused vs preference-based), which should produce distinguishable performance profiles.

---

## Dependencies and Gate Conditions

### Prerequisites
- H-E1 (Alignment Method Clustering Existence) - MUST PASS

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:**
- IF M1 fails (execution models don't dominate correctness): EXPLORE - check if baseline model differences explain clustering
- IF M2 fails (preference models imbalanced): PIVOT - revise feedback signal theory
- IF M3 fails (high intracluster variance): ABANDON - clustering is noise, not signal

**Phase Assignment:** Phase 2 (Mechanism Preconditions)

**Estimated Duration:** 4-6 hours GPU time

---

## Dependency Context

### Relationship to Other Hypotheses
H-M-integrated depends on H-E1 establishing that alignment method clustering exists. It tests the mechanistic explanation (feedback signal theory) for why the clustering pattern emerges. Success validates the causal chain; failure suggests alternative mechanisms should be explored.

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** READY (H-E1 prerequisite satisfied)
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
5. Output: {hypothesis_folder}/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes
- **H-M* (Mechanism)**: Baseline to understand improvement potential
- **H-C* (Condition)**: Baseline to identify scope boundaries
- **H-CP* (Comparison)**: **MANDATORY** - Direct comparison with baseline methods

---

*Generated by Phase 2C Workflow (JIT)*
*Optimized for single-hypothesis experiment design*
