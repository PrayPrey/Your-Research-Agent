# 2. Related Work

We organize prior work by feedback signal type, showing that each line of research operates in isolation and that none tests the oracle/regularizer distinction.

## 2.1 Proof Checker Feedback (Lean4, Isabelle)

**BFS-Prover** [Xin et al., 2025] achieves 72.95% on miniF2F by combining Best-First Tree Search with DPO training using Lean4 compiler errors as negative examples. At each proof state, the Lean4 compiler returns structured error messages (type mismatches, undefined names, tactic failures) for failed tactics; these become the rejected examples in DPO pairs. This is the closest prior work to our oracle framing — and the system our experiment extends. However, BFS-Prover never ablates against semantically ungrounded alternatives. Its DPO negatives are always compiler-error-tagged; whether the semantic content of those errors (vs. simply having same-state failed tactics as negatives) drives improvement is untested.

**STP** [Dong and Ma, 2025] achieves 65% on miniF2F using self-play with formal verifier feedback. The self-play training signal also uses proof checker success/failure, but at the episode level rather than per proof state. STP demonstrates that training-time formal feedback improves theorem proving, but — like BFS-Prover — uses only one feedback type and does not test the mechanism.

**Neural Theorem Proving** [Rao et al., 2025] trains on Isabelle verifier feedback using SFT+RL, achieving state-of-the-art results on Isabelle benchmarks. Again, a single feedback type with no cross-signal comparison.

**The gap**: None of these systems compares step-local grounded feedback against ungrounded alternatives or tests whether semantic content drives the improvement.

## 2.2 SMT Solver Feedback (Z3, CVC5)

**Proof of Thought** [Ganguly et al., 2024] uses Z3 SMT counterexamples via a JSON DSL bridge, reducing compilation errors from 14.6% to 0% on StrategyQA and achieving 81.55% win rate on Reddit-OSHA. This is an inference-time repair loop: no DPO training is involved. The Z3 counterexample provides episode-level grounded feedback (the final proof obligation fails, here is a counterexample), not step-local guidance.

**Step-Wise Formal Verification** [Zhou and Zhang, 2025] uses SMT solvers and computer algebra systems as external oracles for LLM math verification. The focus is inference-time step-level checking, not training signal design.

**Holey** [Namin, 2024] applies Z3/CVC5 CEGIS loops to Python hole-filling, demonstrating that counterexample feedback drives LLM repair. Again, inference-time only.

**The gap**: SMT-based systems operate at inference time or provide episode-level signals. No work compares Z3 SMT feedback against Lean4 step-local feedback, or tests whether the SMT counterexample's semantic content (vs. its role as a contrastive example) drives improvement.

## 2.3 Static Analysis Feedback

**PropertyGPT** [Liu et al., 2024] uses PSL (Property Specification Language) compiler feedback to guide LLM generation of smart contract formal properties, achieving 80% recall on Certora-audited projects. Structured static analysis feedback at the property generation step improves over no-feedback baselines (87% vs. 63% compilation success). This is the strongest inference-time oracle evidence: feedback with explicit semantic content (what the property violates) outperforms generic failure signals.

**Agents4PLC** [Liu et al., 2024b] uses multi-agent closed-loop feedback for PLC code generation with formal verification, demonstrating that structured error messages improve repair rates.

**The gap**: Static analysis systems operate at inference time and in specialized domains. No work tests whether the semantic content of static analysis feedback (vs. structural contrastive supervision) drives the improvement.

## 2.4 Benchmark Landscape

**miniF2F** [Zheng et al., 2021] provides 488 theorem proving problems (AMC/AIME/IMO) in Lean4 format. **Vericoding** [Bursuc et al., 2025] provides 12,504 formally verified code specifications across Lean/Verus/Dafny. **CLEVER** [Thakur et al., 2025] curates 161 Lean problems as a frontier difficulty benchmark.

These benchmarks are not designed to evaluate feedback mechanisms — they measure final task performance. No existing benchmark includes feedback loop evaluation metrics (correctness improvement per repair iteration, feedback signal quality).

## 2.5 DPO for Formal Reasoning

**Step-DPO** [Lai et al., 2024] applies step-level preference optimization to mathematical reasoning, treating individual reasoning steps as preference units. This is structurally analogous to our tactic-level DPO but operates in informal math without formal verifier feedback. The step-level localization shows that fine-grained preference signals improve over episode-level alternatives — consistent with the oracle framing but not in the formal verification domain.

## 2.6 Positioning

Our work differs from all prior work in three ways. First, we introduce the oracle/regularizer framing as a *testable* mechanistic distinction rather than an implicit design assumption. Second, we propose the locality score as a mechanistic probe that directly measures oracle function — prior work measures only final task performance (pass@1), not probability mass shift. Third, we connect the BFS-Prover α parameter to the oracle mechanism, generating a unique discriminating prediction that no alternative explanation can match.

The three-system convergent evidence pattern (BFS-Prover, PropertyGPT, Proof of Thought) motivates the oracle hypothesis but does not test it. Our contribution is to define what testing it would require and to build the infrastructure to do so.
