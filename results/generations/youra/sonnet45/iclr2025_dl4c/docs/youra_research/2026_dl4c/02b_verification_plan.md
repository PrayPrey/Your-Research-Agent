# Verification Plan: Alignment Method Objective Function Signatures

**Date:** 2026-03-18
**Hypothesis ID:** H-AlignmentSignatures-v1
**Confidence:** 0.80
**Total Hypotheses:** 2

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under code generation evaluation conditions (Python function-level tasks, HumanEval+/MBPP+/BigCodeBench benchmarks,
post-alignment models), if we measure model outputs across correctness, complexity, and efficiency dimensions,
then models aligned with different feedback signal types (execution-based vs preference-based) will exhibit
statistically distinguishable performance profiles ("objective function signatures") with intercluster distance > 1.5σ,
because feedback signals during alignment act as implicit objective functions that shape output distributions
toward optimizing whatever the feedback measures.

### 1.2 Alternative Hypothesis (H0)
There is no significant difference in multi-dimensional performance profiles (correctness, complexity, efficiency)
between models aligned with execution-based methods, preference-based methods, and unaligned baselines.
All models produce statistically indistinguishable output distributions (intercluster distance < 1.5σ).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | HumanEval+ (standard) | HumanEval+ provides 164 function-level Python programming tasks with test suites, enabling controlled pass@k measurement. Extended test suite (HumanEval+) reduces test case variance compared to original HumanEval. Task distribution suitable for clustering analysis with 60-80 samples per model. |
| **Model** | 6-8 Python code generation models | Model selection criteria: Execution-focused (2-3 models): SelfCodeAlign-7B, StepCoder, CodeLlama-Python-7B-Instruct; Preference-focused (2-3 models): Models trained with DPO/RLAIF (if publicly available); Baselines (1-2 models): CodeLlama-7B-Base, StarCoder-Base. All models share Python language, varying alignment methods. Llama-3-8B family preferred for base model consistency when available. |

**Dataset Details:**
- Source: EvalPlus (open-source benchmark suite)
- Path: https://github.com/evalplus/evalplus

**Model Details:**
- Type: Open-source LLMs accessible via HuggingFace
- Source: HuggingFace Model Hub

### 1.4 Baseline Methods (for comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| SelfCodeAlign (Wei et al., 2024) | 67.1% pass@1 on HumanEval+, 55 citations | HumanEval+, MBPP+ |
| PrefGen (Peng et al., 2025) | Balanced Pass@k + Gas@k + Secure@k for smart contracts, 3 citations | Smart contract benchmarks (Solidity) |
| NaturalCodeBench (Zhang et al., 2024) | Shows 80% HumanEval → 20% real-world task mismatch, 22 citations | Real-world Python tasks |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Proxy validity: Code complexity metrics (cyclomatic complexity, AST depth) and efficiency metrics (runtime, memory) correlate sufficiently with 'code quality' to serve as objective dimensions | Complexity metrics established in software engineering for human code (Halstead, McCabe). Efficiency metrics directly measurable. Exchange 5 - Dr. Ally proposes objective proxies instead of subjective rubrics | Quality dimension collapses to noise, clustering may only reflect correctness vs efficiency (2D not 3D). Mitigation: Validate proxies on small human-annotated sample (50-100 samples) |
| A2 | Feedback signal theory: Models learn to optimize whatever their training feedback measures, creating persistent biases in output distributions | Implicit bias theory in ML optimization (SGD, Adam have inductive biases). Exchange 9 - Dr. Sage mechanistic link: feedback signals define objectives. SelfCodeAlign/PrefGen demonstrate feedback-dependent outcomes | Clustering could be due to base model differences or data confounds rather than alignment method. Causal claims weakened to correlational. Mitigation: Between-method variance >> within-model variance comparison |
| A3 | Public benchmark data provides sufficient signal: Leaderboard scores + targeted model inference (60-80 samples per model) capture alignment method signatures without access to full training data | Phase 1 estimates 64-85 GPU hours feasible. Exchange 10 - Prof. Pax validates resource requirements. Literature shows pass@k differences detectable with N=50-100 samples (HumanEval+ papers) | Insufficient statistical power, clustering not detectable. Mitigation: Phase 1 (leaderboard analysis) verifies benchmark overlap before GPU commitment |
| A4 | Within-language controls eliminate confounds: Restricting to Python-only models removes language-specific complexity patterns that could dominate alignment method effects | Exchange 12 - Prof. Rex requires within-language comparison. PrefGen (Solidity) vs StepCoder (Python) language difference could confound clustering | Language patterns dominate alignment signals, clusters reflect Python vs Solidity not execution vs preference. Mitigation: Require 3+ Python models per alignment method group |
| A5 | Benchmark sensitivity differences exist: HumanEval/MBPP emphasize similar objectives (function-level correctness), BigCodeBench emphasizes different objectives (repository-level complexity) | NaturalCodeBench paper shows 80% HumanEval → 20% real-world mismatch. Exchange 15 - benchmarks vary in what they measure. Task characteristics differ (function vs repo-level) | All benchmarks measure identical objectives (uniform high correlation r > 0.85), no differential sensitivity exists. Hypothesis H3 fails but H1-H2 can still succeed |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** Reverse-engineering implicit objectives from model outputs - first systematic characterization of alignment method 'objective function signatures' via post-hoc analysis

**Key Innovation:**
1. Objective inference direction: Prior work demonstrates multi-objective TRAINING (forward: objective → model). We demonstrate objective INFERENCE (reverse: model outputs → inferred objective).
2. Evaluation ontology framework: Systematic three-way mapping between alignment methods, objective dimensions, and benchmark sensitivities - positions work as foundational infrastructure.
3. Benchmark diagnostic methodology: Validation framework for which benchmarks measure which objectives, addressing evaluation crisis identified by NaturalCodeBench and LiveCodeBench.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | READY |
| H-M-integrated | Mechanism | MUST_WORK | H-E1 | READY |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Alignment Method Clustering Existence**

**Statement**: Under code generation evaluation conditions (Python function-level tasks, HumanEval+/MBPP+/BigCodeBench benchmarks), if we measure 6-8 post-alignment models across correctness, complexity, and efficiency dimensions, then models will cluster in 3D performance space according to alignment method type (execution-based, preference-based, unaligned baseline) with statistically significant intercluster distance > 1.5σ (Cohen's d), because feedback signals during alignment shape output distributions toward implicit optimization objectives.

**Rationale**: This tests the foundational claim that alignment methods produce detectable "objective function signatures". If clustering exists, it validates that feedback signals create systematic biases in output distributions. This is the existence proof needed before testing mechanism.

**Variables** (from Phase 2A):
- Independent: Alignment Method Type (execution-based, preference-based, baseline)
- Dependent: Intercluster Distance (Cohen's d in 3D space)
- Controlled: Programming Language (Python only), Task Distribution (HumanEval+ 164 tasks)

**Verification Protocol**:
1. Select 6-8 models (2-3 execution-focused, 2-3 preference-focused, 1-2 baselines) from HuggingFace
2. Generate 60-80 code samples per model on HumanEval+ tasks (temperature 0.8)
3. Measure three dimensions: correctness (pass@k via test execution), complexity (cyclomatic via radon, AST depth via lizard), efficiency (runtime via cProfile, memory via memory_profiler)
4. Apply PCA on signature vectors, run k-means clustering (k=3)
5. Compute Cohen's d effect size (intercluster distance / intracluster SD)

**Success Criteria** (PoC: Direction-based):
- Primary: Cohen's d > 1.5σ (moderate success) or > 2.5σ (strong success)
- Secondary: Alignment method clustering stronger than language confounds

**Failure Response**:
- IF Cohen's d < 1.5σ: ABANDON - no detectable signatures exist
- IF language confounds dominate: PIVOT - add cross-language controls

**Dependencies**: None (foundation hypothesis)

**Source**: Phase 2A Prediction 1 (P1)

---
**H-M-integrated: Objective Function Mechanism (3-step causal chain)**

**Statement**: If alignment methods shape model output distributions through implicit optimization (3-step causal chain: feedback signal selection → repeated training exposure → observable signatures), then we will observe: (M1) execution-focused models dominate correctness dimension (top 15% pass@k rank), (M2) preference-focused models show balanced performance (top 30% across all dimensions), (M3) training dynamics create consistent within-method clustering (intracluster variance < intercluster distance), because feedback signals define what models optimize during alignment training.

**Rationale**: This tests the mechanistic explanation for why clustering exists. Validates that feedback signal theory (models optimize what they're trained on) explains observed signatures through objective-specific dominance patterns.

**Variables** (from Phase 2A):
- Independent: Feedback Signal Structure (binary pass/fail, comparative preference pairs, none)
- Dependent: Correctness Dominance (percentile rank), Balanced Performance (mean rank), Intracluster Variance
- Controlled: Same models as H-E1, Python-only, normalized metrics

**Verification Protocol**:
1. Rank all models independently on each dimension (correctness, complexity, efficiency)
2. Compute percentile rankings per alignment method group
3. Test M1: execution models mean correctness rank ≤ 15th percentile
4. Test M2: preference models mean rank ≤ 30th percentile across ALL three dimensions
5. Test M3: within-method variance < between-method variance (Mann-Whitney U test, p < 0.05)

**Success Criteria** (PoC: Direction-based):
- Primary: M1 AND M2 hold (objective-specific dominance demonstrated)
- Secondary: M3 holds (clustering consistency validated)

**Failure Response**:
- IF M1 fails (execution models don't dominate correctness): EXPLORE - check if baseline model differences explain clustering
- IF M2 fails (preference models imbalanced): PIVOT - revise feedback signal theory
- IF M3 fails (high intracluster variance): ABANDON - clustering is noise, not signal

**Dependencies**: H-E1 (requires clustering to exist before testing mechanism)

**Source**: Phase 2A Causal Mechanism Steps 1-3, Prediction 2 (P2)

---

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M-integrated
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Cohen's d > 1.5σ | ABANDON entire hypothesis |
| H-M-integrated | MUST_WORK | M1 AND M2 hold | EXPLORE alternative mechanisms |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 2C | Experiment Design | 15-20 min |
| Phase 3 | Implementation Planning | 20-30 min |
| Phase 4 | H-E1 Implementation | 8-12 hours |
| Phase 4 | H-M-integrated Implementation | 4-6 hours |

**Total Duration:** ~12-18 hours GPU time + ~1-2 hours planning

---

*Generated by YouRA Phase 2B | 2026-03-18*
