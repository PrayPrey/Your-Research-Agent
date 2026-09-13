# Phase 2A Hypothesis Refinement Summary

**Generated:** 2026-07-11T05:05:00Z  
**Workflow:** phase2a-dialogue  
**Architecture:** Self-Contained Tikitaka Loop  
**Gap:** GAP-001 - Weak Specification Synthesis for Formal Verification  
**Exchanges:** 15  
**Convergence:** Achieved ✓

---

## Executive Summary

**Hypothesis ID:** H-VerifierTeacher-v1  
**Confidence:** 80%  
**Verdict:** PROCEED to Phase 2B

**Core Claim:** Verifier-driven iterative refinement with structured feedback decomposed into three informational dimensions (Witness Instantiation, Logical Structure, Dependency Preservation) achieves ≥80% proof discharge rate within ≤10 iterations and demonstrates cross-verifier portability via semantic normalization.

**Novelty:** First demonstration of verifier-as-teacher for specification synthesis (vs. code generation), semantic normalization for cross-tool transfer, and information-theoretic decomposition of feedback primitives.

**Impact:** Enables formal verification for low-resource languages, legacy code, and rapid prototyping by eliminating the expert specification bottleneck.

---

## Hypothesis Statement

Under formal specification synthesis for programs with verifiable properties, **if** LLMs receive structured verifier feedback decomposed into three informational dimensions (Witness Instantiation, Logical Structure, Dependency Preservation) and iterate through staged refinement (types → preconditions → postconditions → invariants), **then** the synthesized specifications will achieve ≥80% proof discharge rate within ≤10 iterations and demonstrate cross-verifier portability via semantic normalization, **because** structured feedback encodes semantic constraints that guide specification refinement more effectively than unstructured iteration or single-shot synthesis.

---

## Key Predictions

1. **P1 - Effectiveness:** Iterative refinement with full structured feedback achieves ≥80% proof discharge rate within ≤10 iterations on held-out verified programs. *Falsification:* <70% or >15 iterations.

2. **P2 - Information Gradient:** Performance scales with feedback richness (Condition C > B > A by ≥25%). *Falsification:* Condition A within 10% of C or non-monotonic ordering.

3. **P3 - Cross-Verifier Portability:** Semantic normalization enables ≥80% performance retention when transferring from Frama-C to Dafny/Why3. *Falsification:* >40% degradation.

4. **P4 - Non-Vacuity:** Synthesized specs kill ≥70% of mutants that expert specs kill. *Falsification:* <50% of baseline.

5. **P5 - Compute-Matched:** Under equal budget, iterative outperforms single-shot by ≥10pp. *Falsification:* Single-shot matches or exceeds iterative.

---

## Causal Mechanism

Structured verifier feedback provides semantic supervision by exposing the gap between current specification and verifiable correctness. The three informational dimensions encode complementary repair signals:

- **Witness Instantiation:** Concrete counterexamples show WHERE specs fail
- **Logical Structure:** Proof obligations show WHAT needs to be proven
- **Dependency Preservation:** Failure localization shows WHY proofs fail

The semantic normalization layer abstracts tool-specific feedback into universal repair primitives (category + obligation slice + witness), enabling transfer across verifiers. Specifications progress through staged refinement (types → pre → post → inv) with automated validation at each stage.

---

## Experimental Design

**Dataset:** Verified C programs with gold ACSL annotations (≥100 programs, 70/30 split)

**Conditions:**
- C_Full: Tag + Obligation + Witness
- B_Obligation: Tag + Obligation Slice
- A_Tag: Category label only
- Raw: Unstructured verifier errors
- SingleShot: Compute-matched baseline

**Metrics:**
- Primary: Proof Discharge Rate (%)
- Secondary: Mutation Kill Rate, Iterations to Convergence, Cross-Verifier Performance

**Baselines:** Zero-shot LLM, non-expert human specs, compute-matched single-shot sampling

---

## Novelty vs. Prior Work

| Prior Work | Limitation | Our Advance |
|------------|------------|-------------|
| PropertyGPT (119 cites) | RAG for domain-specific contracts | No knowledge base; learns from verifier feedback directly |
| Astrogator (12 cites) | Requires expert-written queries | Eliminates expert bottleneck via co-evolutionary refinement |
| AutoSpec | LLM+Frama-C integration shown | Adds semantic normalization + information-theoretic analysis |
| Verification-in-loop (70%) | Assumes specs exist | Applies to specification synthesis itself |

---

## Persona Verdicts

- 🔭 **Dr. Nova** (Novelty): **STRONG** - Paradigm shift from retrieval/template to co-evolutionary
- 🔬 **Prof. Vera** (Falsifiability): **STRONG** - Pre-registered metrics, explicit failure boundaries
- 🎯 **Dr. Sage** (Significance): **STRONG** - Field-advancing, addresses scalability bottleneck
- ⚙️ **Prof. Pax** (Feasibility): **MODERATE** - Technically sound, 3-6 month timeline, cross-domain assumptions strong

---

## Remaining Concerns (Prof. Rex)

1. **Information gradient ordering** must be empirically validated, not assumed. *Mitigation:* Pre-register regression analysis.

2. **Cross-domain transfer** (systems → mathematics → contracts) may require >40% degradation tolerance. *Mitigation:* Distinguish from cross-verifier claim; pre-specify thresholds.

3. **Semantic normalization causal structure preservation** must be demonstrated via ablation. *Mitigation:* Validate minimal viable abstraction (Conditions A/B/C).

---

## Phase 2B Readiness

✅ **All convergence criteria met:** SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS  
✅ **Phase 2B-compatible outputs generated:** 03_refinement.yaml, 02_synthesis.yaml, final_opinions.yaml  
✅ **Consensus verdict:** PROCEED with HIGH confidence  
✅ **Implementation feasible:** Existing tools (Frama-C, Z3, Dafny, Why3), 3-6 month timeline

**Next Phase:** Phase 2B - Research Planning & Roadmap Creation

---

*Phase 2A Complete*
