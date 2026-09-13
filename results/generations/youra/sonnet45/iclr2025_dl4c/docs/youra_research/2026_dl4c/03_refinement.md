# Phase 2A Hypothesis Refinement Summary

**Generated:** 2026-03-18T17:20:00Z
**Workflow:** Phase 2A-Dialogue v10.0.0 (Self-Contained Tikitaka Loop)
**Research Gap:** Gap 1 - Empirical Measurement of Multi-Objective Trade-offs in Existing Code Generation Benchmarks
**Discussion Exchanges:** 17

---

## Hypothesis Statement

**Hypothesis ID:** H-AlignmentSignatures-v1
**Confidence Level:** 0.80 (STRONG across all four perspectives)

**Core Claim:**

Alignment methods for code generation LLMs exhibit empirically detectable "objective function signatures" - characteristic performance profiles across correctness, complexity, and efficiency dimensions that reflect their implicit optimization objectives as determined by feedback signal types (execution-based vs preference-based).

**Under-If-Then-Because Format:**

Under code generation evaluation conditions (Python function-level tasks, HumanEval+/MBPP+/BigCodeBench benchmarks, post-alignment models), if we measure model outputs across correctness, complexity, and efficiency dimensions, then models aligned with different feedback signal types (execution-based vs preference-based) will exhibit statistically distinguishable performance profiles with intercluster distance > 1.5σ, because feedback signals during alignment act as implicit objective functions that shape output distributions toward optimizing whatever the feedback measures.

---

## Three Testable Predictions

### P1: Alignment Method Clustering (PRIMARY)
- **Statement:** Models cluster in [correctness, complexity, efficiency] 3D space by alignment method type
- **Success Criterion:** Cohen's d > 2.5σ (strong) or 1.5-2.5σ (moderate)
- **Falsification:** If d < 1.5σ, alignment methods do not produce detectable signatures

### P2: Objective-Specific Dominance
- **Statement:** Execution-focused models rank top 15% for correctness, preference-focused models show balanced top 30%
- **Success Criterion:** Rank patterns match predicted specializations
- **Falsification:** If execution models don't dominate correctness, feedback theory fails

### P3: Differential Benchmark Sensitivity
- **Statement:** HumanEval-MBPP correlation significantly higher than HumanEval-BigCodeBench correlation
- **Success Criterion:** r_HM - r_HB > 0.20
- **Falsification:** If all correlations > 0.85, benchmarks measure identically

---

## Key Novelty

**Three-Fold Innovation:**

1. **Objective Inference Direction:** Prior work demonstrates multi-objective TRAINING (PrefGen, SIPO). We demonstrate objective INFERENCE (reverse: model outputs → inferred objectives).

2. **Evaluation Ontology Framework:** Three-way mapping between alignment methods × objective dimensions × benchmark sensitivities positions work as foundational infrastructure.

3. **Benchmark Diagnostic Methodology:** Systematic characterization of what benchmarks measure, addressing evaluation crisis (NaturalCodeBench ranking mismatch, LiveCodeBench contamination).

**Differentiation from Prior Work:**
- PrefGen/SIPO: Multi-objective training → We: Multi-dimensional evaluation
- NaturalCodeBench/LiveCodeBench: Identify problems → We: Provide diagnostic framework
- RL Survey: Catalog methods → We: Characterize implicit objectives

---

## Experimental Design

**Three-Phase Approach:**

**Phase 1: Leaderboard Analysis** (0 GPU hours)
- Collect rankings from HumanEval+, MBPP+, BigCodeBench for 15-20 models
- Compute Spearman rank correlations
- Test P3 (benchmark sensitivity): r_HM - r_HB > 0.20

**Phase 2: Targeted Model Inference** (64-85 GPU hours)
- Select 6-8 Python models (execution-focused, preference-focused, baselines)
- Generate 60-80 samples per model on HumanEval+ tasks
- Measure: pass@k (correctness), cyclomatic complexity (radon/lizard), runtime/memory (profiling)

**Phase 3: Statistical Analysis** (0 GPU hours)
- PCA clustering with k-means (k=3 groups)
- Compute Cohen's d effect size for intercluster distance
- Ranking analysis per dimension
- Test P1 (clustering) and P2 (dominance)

---

## Feasibility Assessment

✅ **GPU Budget:** 64-85 hours (within 50-120 hour Phase 1 constraint)
✅ **Models Available:** SelfCodeAlign, CodeLlama, StarCoder families on HuggingFace
✅ **Measurement Tools:** radon, lizard (static analysis), memory_profiler, cProfile (profiling) - all mature
✅ **Statistical Power:** N=480-640 samples, power=0.80 for Cohen's d=0.5
✅ **ROUTE_TO_0 Constraints:** No cloud APIs, public benchmarks only, no gradient measurements

**Risk Mitigation:** Phased design - Phase 1 (leaderboard analysis) verifies benchmark overlap before committing GPU resources in Phase 2.

---

## Scope & Boundaries

**Applies To:**
- Python code generation (function-level tasks)
- Post-alignment evaluation (not training dynamics)
- Public models via HuggingFace
- Three dimensions: correctness, complexity, efficiency

**Does Not Apply To:**
- Non-Python languages (language confounds)
- Training-time analysis (requires gradient access)
- Subjective quality (requires human annotation)
- Repository-level tasks (focus on function-level)

---

## Key Assumptions

**A1:** Proxy validity - Complexity/efficiency metrics correlate with code quality for LLM outputs
**A2:** Feedback signal theory - Models learn to optimize whatever training feedback measures
**A3:** Public data sufficiency - Leaderboards + 60-80 samples provide adequate signal
**A4:** Within-language controls - Python-only eliminates language confounds
**A5:** Benchmark sensitivity differences - HumanEval/MBPP vs BigCodeBench measure different objectives

---

## Success Criteria

**Strong Success:** Cohen's d > 2.5σ + dominance patterns + correlation difference > 0.20 → **Top-tier venue** (ICML/NeurIPS/ICLR)

**Moderate Success:** Cohen's d 1.5-2.5σ + partial dominance + P3 holds → **Second-tier venue** with caveats

**Failure:** d < 1.5σ OR no dominance OR uniform r > 0.85 → **Hypothesis rejected**

---

## Phase 2B Readiness

**Status:** ✅ READY

**Sub-Hypothesis Structure:**
- **H-E1 (EXISTENCE):** Clustering exists with distance > 1.5σ - MUST_WORK gate
- **H-M1 (MECHANISM):** Execution-focused models dominate correctness - SHOULD_WORK gate
- **H-M2 (MECHANISM):** Preference-focused models show balance - SHOULD_WORK gate
- **H-M3 (BOUNDARY):** BigCodeBench measures different dimensions - SHOULD_WORK gate (independent)

**Open Questions for Future Work:**
- Do signatures generalize across model scales (7B → 70B)?
- What additional objective dimensions exist beyond correctness/complexity/efficiency?
- Can signatures transfer across base architectures (Llama → StarCoder → CodeGen)?

---

## Persona Verdicts

🔭 **Dr. Nova (Novelty):** STRONG - Paradigm shift to objective inference, evaluation ontology framework
🔬 **Prof. Vera (Falsifiability):** STRONG - Three quantitative predictions with clear falsification criteria
🎯 **Dr. Sage (Significance):** STRONG - Addresses evaluation crisis, actionable practitioner guidance
⚙️ **Prof. Pax (Feasibility):** STRONG - Resource-validated, mature tools, phased risk mitigation
🛡️ **Dr. Ally (Synthesis):** VALIDATED - All refinements incorporated, ROUTE_TO_0 constraints satisfied
🔍 **Prof. Rex (Critique):** THREE CONCERNS - Moderate clustering ambiguity, proxy validity, benchmark overlap (all mitigated)

---

**Files Generated:**
- ✅ `03_refinement.yaml` - Primary hypothesis definition (Phase 2B input)
- ✅ `02_synthesis.yaml` - Synthesis details (Phase 2B supplementary)
- ✅ `01_round_table/final_opinions.yaml` - Per-agent assessments (Phase 2B reference)
- ✅ `discussion_log.md` - Full 17-exchange discussion transcript (920 lines)

**Next Phase:** Phase 2B - Verification Planning (hypothesis decomposition into sub-hypotheses with gate policies)
