# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-05-20T07:30:00
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: gap_1
- **Gap Title**: No Systematic Comparative Study of Formal Feedback Signal Effectiveness
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: All 6 criteria met — SPECIFIC (oracle/regularizer core claim), MECHANISM (state-local semantic grounding via DPO), PREDICTIONS (P1 hard-stratum, P2 α-interaction, P3 locality), NOVELTY (oracle/regularizer dichotomy unifying 3 prior systems), FEASIBILITY (BFS-Prover open-source scaffold), OBJECTIONS (pair construction, fidelity audit, tactic taxonomy addressed)

### Key Insights
1. Formal feedback signals differ qualitatively in "repair information density" — specificity, localizability, and semantic content at the proof-state level
2. BFS-Prover's DPO framework provides a ready-made scaffold for a controlled variation study — swap the rejection source, hold everything else fixed
3. PropertyGPT (87% vs 63%) and Proof of Thought (0% vs 14.6% compilation errors) provide natural inference-time frozen-policy controls already in the literature
4. The α-interaction prediction (oracle advantage largest at α=0, shrinking as α→1) is a novel discriminating test that distinguishes oracle from regularizer mechanisms
5. The 2×2 design (granularity × semantic groundedness) within BFS-Prover's DPO framework cleanly isolates the causal dimension

### Breakthrough Moments
- **Exchange 9**: Identifying the 2×2 granularity × semantic groundedness design within BFS-Prover's existing DPO framework
- **Exchange 11**: Recognizing PropertyGPT as a natural frozen-policy control, resolving the training vs. inference disentanglement concern
- **Exchange 15**: Articulating the oracle/regularizer dichotomy as the unifying mechanistic claim discriminated by α-interaction + locality predictions

---

## Final Hypothesis

### Title
Formal Feedback as Local Logical Oracle: Mechanistic Study of Step-Local vs. Episode-Level Signals in LLM Formal Reasoning

### Hypothesis ID
H-FormalFeedbackOracle-v1

### Core Claim
Under fixed search geometry (BFS with length normalization α, fixed expansion width and tactic budget) and high formalization fidelity (≥85% audit threshold), if LLM policy training uses semantically grounded step-local formal feedback signals (Lean4 compiler errors or Z3 SMT counterexamples via DSL bridge) as DPO negative examples, then correctness recovery on hard benchmark instances (cold-start SFT baseline pass rate <20%) will be significantly greater (≥10pp, non-overlapping 95% CIs) compared to episode-level or semantically ungrounded feedback, **because step-local grounded signals function as "local logical oracles" — providing state-specific semantic information that directs the policy toward formally valid continuations — rather than as "policy regularizers" that sharpen any policy regardless of semantic content.**

### Null Hypothesis (H0)
There is no significant difference in hard-stratum pass@1 between semantically grounded step-local feedback and episode-level or ungrounded feedback conditions under fixed search geometry and DPO training (Δ < 2pp, 95% CIs overlapping).

### Mechanism
1. Formal verifier produces step-local semantically grounded rejection at proof state s (Lean4 compiler error with location + violated constraint, or Z3 counterexample via DSL)
2. Step-local grounded rejection is encoded as DPO negative at the same proof state (s, a_w, a_l), creating state-aligned contrastive supervision
3. DPO training with state-aligned grounded negatives shifts policy mass toward premise-consistent tactics (oracle function), not diffuse sharpening (regularizer)
4. Under length-averse BFS (α=0), oracle guidance compensates for search depth bias, producing the largest hard-stratum recovery gains; advantage shrinks as α→1

---

## Predictions

| ID | Primary | Statement | Success Criterion |
|----|---------|-----------|-------------------|
| P1 | ✅ | Step-local grounded (A) produces ≥10pp greater hard-stratum pass@1 than episode-level ungrounded (D) under DPO, fixed search geometry | Δ ≥ 10pp, non-overlapping 95% CIs, 3 seeds |
| P2 | ❌ | α-interaction: Δ(A−D) maximized at α=0.0, decreases monotonically to α=1.0 | Cohen's d ≥ 0.3 for interaction effect |
| P3 | ❌ | Locality: post-DPO mass shift concentrates on premise-consistent tactics vs. permutation control | Locality score A > permutation control, p<0.05 |

**Pre-registered failure thresholds**: P1 Δ<2pp → reject; P2 Cohen's d<0.3 → oracle-search-bias claim rejected; P3 locality ≈ permutation → regularizer, not oracle

---

## Novelty

**Key Innovation**: First controlled study of oracle vs. regularizer mechanism for formal feedback in LLM policy training. Unifies PropertyGPT, Proof of Thought, and BFS-Prover under a single testable mechanistic claim — no prior paper has explicitly tested this causal question.

**Differentiation**:
- **vs. BFS-Prover**: BFS-Prover used compiler feedback but never tested whether it is causal; this provides the controlled ablation
- **vs. PropertyGPT**: PropertyGPT used static analysis at inference time but never compared to alternatives; this generalizes to cross-signal comparison
- **vs. Proof of Thought**: PoT showed Z3 feedback works but didn't test granularity or mechanism; this provides the missing comparison

---

## Experimental Design

**Base Model**: Qwen2.5-Math-7B (cold-start SFT from BFS-Prover)

**Benchmarks**: miniF2F hard subset + Vericoding hard subset (Lean/Verus/Dafny); cold-start SFT baseline <20%

**Feedback Conditions (2×2)**:
| | Step-Local | Episode-Level |
|---|---|---|
| **Semantically Grounded** | A: Lean4 compiler errors (LeanDojo) | C: Z3 SMT failure, state-aligned pairs |
| **Semantically Ungrounded** | B: Same-state failed-branch tactics | D: Binary pass/fail |

**Factorial Design**: Conditions A/B/C/D × DPO on/off × α ∈ {0.0, 0.5, 1.0}

**Two Experiments**:
- **Experiment A** (frozen policy): inference-time repair loop with 4 feedback conditions — tests oracle function without training
- **Experiment B** (DPO): construct DPO pairs for each condition, train 1 epoch — tests oracle function in preference learning

---

## Limitations

- Results on miniF2F may not transfer to Vericoding without cross-formalism validation
- Qwen2.5-Math-7B as base model; larger models (70B+) may show different scaling behavior
- LeanDojo-specific tactic interface; generalization to Isabelle/Coq requires separate validation
- Formalization fidelity boundary (85%) is empirically chosen — exact threshold affects scope claims
- MATH-VF-style SimpleMath coverage (>90%) required; Coq formalization (<10%) falls outside scope

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Hypothesis ID** | H-FormalFeedbackOracle-v1 |
| **Discussion Convergence** | All 6 criteria met at exchange 15 |
| **Clarity Verified** | Yes |
| **Feasibility Constraints** | ✅ Existing benchmarks only (miniF2F, Vericoding) |
| **No new benchmark creation** | ✅ |
| **No synthetic data** | ✅ |
| **No human evaluation** | ✅ |
| **Remaining Pre-Registration Tasks** | (1) Episode-level pair construction protocol, (2) LeanDojo tactic taxonomy, (3) Two-annotator fidelity audit κ≥0.7 |

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
