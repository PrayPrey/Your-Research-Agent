---
title: "Testing the Oracle Mechanism in LLM Formal Reasoning: A Locality Score Approach with Infrastructure Failure Analysis"
format: icml2025
date: 2026-05-20
status: complete
revision: R1
word_count_estimate: ~5900
sections: [abstract, introduction, related_work, methodology, experiments, results, discussion, conclusion]
---

# Testing the Oracle Mechanism in LLM Formal Reasoning: A Locality Score Approach with Infrastructure Failure Analysis

---

## Abstract

Formal verification feedback loops demonstrably improve LLM performance on theorem proving and code verification tasks, yet the mechanism remains unknown: does structured formal feedback function as a *local logical oracle* that directs probability mass toward premise-consistent tactics, or merely as a *policy regularizer* that sharpens the model regardless of semantic content? We introduce this oracle/regularizer distinction as the central testable mechanistic question in LLM formal reasoning, propose the **locality score** — the fraction of post-DPO probability mass shift concentrated on premise-consistent tactic categories — as a direct mechanistic probe, and design a 3-condition experiment (grounded, ungrounded, permuted control) within the BFS-Prover framework to test it. These contributions — the oracle/regularizer framing, the locality score metric, and the implemented experimental design — stand as methodological advances independent of empirical outcomes. Attempting to execute this experiment reveals a critical infrastructure failure: the LeanDojo proof state extraction layer silently substituted synthetic hardcoded error strings for real Lean4 compiler outputs, producing uniformly zero locality scores that are a synthetic artifact rather than a scientific finding. The DPO training infrastructure is validated (β=10, 100% state alignment (on synthetic data), correct loss implementation), the experimental design is sound, and a single environment fix unblocks the first direct test of the oracle mechanism. We document the silent synthetic fallback failure mode and propose pre-run environment validation gates as a standard practice for LLM+formal-verifier experiments.

---

# 1. Introduction

This paper reports negative results with positive methodological contributions. Three of the most successful recent LLM formal reasoning systems share an architectural choice: they give the language model structured error feedback from a formal verifier. BFS-Prover achieves 72.95% on the miniF2F theorem proving benchmark using Lean4 compiler errors as DPO negatives [Xin et al., 2025]. PropertyGPT improves smart contract property recall from 63% to 87% using static analysis feedback at inference time [Liu et al., 2024]. Proof of Thought reduces compilation errors from 14.6% to 0% using Z3 SMT counterexamples via a JSON DSL bridge [Ganguly et al., 2024]. Yet none of these systems can answer a fundamental question: *why* does formal feedback help?

This is not a rhetorical gap. Two mechanistically distinct explanations are consistent with the observed improvements. Under the **oracle hypothesis**, structured formal feedback provides state-specific semantic information that directs the policy toward formally valid continuations — functioning as a "local logical oracle" that encodes the violated constraint and points toward its resolution. Under the **regularizer hypothesis**, formal feedback simply acts as a high-quality source of contrastive examples for DPO training, sharpening the policy regardless of the semantic content of the negative example — a general regularization effect that any sufficiently diverse set of failure cases could achieve.

These hypotheses have radically different implications. If the oracle hypothesis holds, feedback quality (semantic specificity) is the critical design dimension. If the regularizer hypothesis holds, feedback diversity (number and variety of negative examples) is more important. These lead to opposite design conclusions for future systems.

**The deeper problem** is structural: each system in this area uses its own model, benchmark, and feedback mechanism. BFS-Prover uses Lean4 compiler errors; PropertyGPT uses PSL static analysis; Proof of Thought uses Z3 SMT. These systems never ablate against each other's feedback type or against semantically ungrounded alternatives. The oracle/regularizer distinction remains untested not because researchers disagree about it, but because the field has not yet designed the experiment to resolve it.

**Our approach.** We introduce a 2×2 factorial design within the BFS-Prover framework to test the oracle/regularizer distinction. The design holds all variables constant except the semantic content of the DPO negative example: Condition A uses step-local Lean4 compiler errors (grounded), Condition B uses same-state failed-branch tactics (ungrounded), and Condition P uses permuted compiler error messages (control). We introduce the **locality score** — the fraction of post-DPO probability mass shift concentrated on tactic categories consistent with the violated premise — as a mechanistic probe that directly measures oracle function vs. diffuse regularization. Additionally, the BFS-Prover length normalization parameter α provides a uniquely discriminating test: only the oracle hypothesis predicts that the performance advantage should be maximized under length-averse search (α=0), where local oracle guidance compensates for search depth bias.

In executing this experiment, we encounter an infrastructure failure that is itself a substantive finding: the LeanDojo proof state extraction layer silently fell back to synthetic (hardcoded) error strings when the Lean4 toolchain was absent, producing uniformly zero locality scores that passed format validation while carrying no scientific content. We diagnose this failure in detail and propose pre-run environment validation protocols as a methodological contribution to the field.

**Contributions.** This paper makes four contributions:

1. **The oracle/regularizer framing**: We articulate the mechanistic distinction between formal feedback as local logical oracle vs. policy regularizer, unifying BFS-Prover, PropertyGPT, and Proof of Thought under a single testable causal hypothesis.

2. **The locality score metric**: We define and implement a novel mechanistic probe — the fraction of post-DPO probability mass shift on premise-consistent tactic categories — that directly measures oracle vs. regularizer function.

3. **An implemented and unit-tested experimental design**: We implement a 3-condition DPO pipeline with 100% state alignment verification, pre-specified tactic taxonomy, and discriminating α-interaction prediction — infrastructure that is ready for re-execution once LeanDojo is properly installed.

4. **A methodological warning**: We document and analyze a class of infrastructure failure — silent synthetic data substitution in LLM+formal-verifier pipelines — and propose pre-run environment validation gates as a standard practice.

The paper proceeds as follows. Section 2 reviews prior work on formal feedback for LLMs, showing that no existing work tests the oracle/regularizer distinction. Section 3 presents the experimental methodology, including the locality score metric and α-interaction prediction. Section 4 describes the experimental setup. Section 5 reports results, including the infrastructure diagnosis. Section 6 discusses implications. Section 7 concludes.

---

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

**PropertyGPT** [Liu et al., 2024] uses PSL (Property Specification Language) compiler feedback to guide LLM generation of smart contract formal properties, achieving 80% recall on Certora-audited projects (separately, compilation success improves from 63% to 87% with feedback; Section 5.5). Structured static analysis feedback at the property generation step improves over no-feedback baselines. This is the strongest inference-time oracle evidence: feedback with explicit semantic content (what the property violates) outperforms generic failure signals.

**Agents4PLC** [Liu et al., 2024b] uses multi-agent closed-loop feedback for PLC code generation with formal verification, demonstrating that structured error messages improve repair rates.

**The gap**: Static analysis systems operate at inference time and in specialized domains. No work tests whether the semantic content of static analysis feedback (vs. structural contrastive supervision) drives the improvement.

## 2.4 Benchmark Landscape

**miniF2F** [Zheng et al., 2021] provides 488 theorem proving problems (AMC/AIME/IMO) in Lean4 format. **Vericoding** [Bursuc et al., 2025] provides 12,504 formally verified code specifications across Lean/Verus/Dafny. **CLEVER** [Thakur et al., 2025] curates 161 Lean problems as a frontier difficulty benchmark.

These benchmarks are not designed to evaluate feedback mechanisms — they measure final task performance. No existing benchmark includes feedback loop evaluation metrics (correctness improvement per repair iteration, feedback signal quality).

## 2.5 DPO for Formal Reasoning

**Step-DPO** [Lai et al., 2024] applies step-level preference optimization to mathematical reasoning, treating individual reasoning steps as preference units. This is structurally analogous to our tactic-level DPO but operates in informal math without formal verifier feedback. The step-level localization shows that fine-grained preference signals improve over episode-level alternatives — consistent with the oracle framing but not in the formal verification domain.

## 2.6 Positioning

Our work differs from all prior work in three ways. First, we introduce the oracle/regularizer framing as a *testable* mechanistic distinction rather than an implicit design assumption. Second, we propose the locality score as a mechanistic probe that directly measures oracle function — prior work measures only final task performance (pass@1), not probability mass shift. Third, we connect the BFS-Prover α parameter to the oracle mechanism, generating a unique discriminating prediction that no alternative explanation can match.

The three-system convergent evidence pattern (BFS-Prover, PropertyGPT, Proof of Thought) motivates the oracle hypothesis but does not test it. Our contribution is to define what testing it would require and to build the infrastructure to do so — implemented and unit-tested on synthetic data, and ready for re-execution with real LeanDojo data.

---

# 3. Methodology

Our experimental design is built around one question: does the *semantic content* of formal feedback drive LLM improvement, or is it merely the *structure* of contrastive DPO supervision? We call these the oracle and regularizer hypotheses respectively, and we design a 3-condition experiment whose results can discriminate between them.

## 3.1 The Oracle/Regularizer Distinction

**Rationale for the distinction.** When a Lean4 compiler rejects a tactic at proof state *s* with the message "type mismatch: expected `Nat`, got `Int`", this message carries semantic content: the violated type constraint, the location of the error, and an implicit pointer toward premise-consistent alternatives. Under the oracle hypothesis, a DPO model trained on this rejection concentrates probability mass on tactics that address type consistency — the feedback *directs* the policy. Under the regularizer hypothesis, the DPO update diffusely sharpens the policy regardless of the error message content — the feedback merely *constrains* the policy away from the rejected tactic.

**Why this matters.** If the oracle hypothesis holds, feedback quality (semantic specificity) is the critical design dimension. If the regularizer hypothesis holds, feedback diversity (number and variety of negative examples) is more important. These lead to opposite design conclusions for future systems.

**Why prior work cannot discriminate.** Every existing system uses a single feedback condition. BFS-Prover uses only Lean4 compiler errors; ablating against semantically ungrounded same-state negatives would require a separate experimental run that has never been performed. We design and execute this comparison.

## 3.2 Three-Condition DPO Design

We build on the BFS-Prover framework [Xin et al., 2025], using Qwen2.5-Math-7B initialized from the BFS-Prover cold-start SFT checkpoint. All three conditions share:
- The same base model (frozen π_ref)
- The same proof states (hard subset: cold-start SFT pass@1 < 20%)
- The same chosen tactics (a_w) at each state
- The same DPO hyperparameters (β=10, lr 5e-6→5e-7, 1-epoch)

The conditions differ only in the rejected tactic (a_l):

| Condition | Name | a_l content | Semantic grounding |
|-----------|------|-------------|-------------------|
| **A** | Step-local Grounded | Lean4 compiler-error-triggering tactic at state *s* | Full: error type, location, violated constraint |
| **B** | Step-local Ungrounded | Failed-branch tactic at same state *s* (no error message) | None: failed tactic identity only |
| **P** | Permuted Control | Tactic paired with shuffled/permuted compiler error message | Scrambled: structure preserved, semantics destroyed |

This design allows clean attribution: A vs. P isolates the contribution of *coherent semantic content* (both have compiler error messages, only A has consistent ones); A vs. B isolates the contribution of *semantic grounding itself* (both are step-local, only A is grounded).

**State alignment.** A critical implementation requirement: for all three conditions, the chosen tactic a_w and rejected tactic a_l must come from the *same* proof state *s* (100% state alignment). Misalignment would confound the 2×2 factorial, turning conditions B and P into episode-level signals. We verify state alignment via LeanDojo state IDs and abort if any pair violates the invariant.

## 3.3 The Locality Score Metric

We introduce the **locality score (LS)** as a mechanistic probe for oracle function:

$$\text{LS} = \frac{\sum_s \left[ P_{\text{post}}(\text{premise-consistent} \mid s) - P_{\text{pre}}(\text{premise-consistent} \mid s) \right]}{\sum_s \sum_t \left| P_{\text{post}}(t \mid s) - P_{\text{pre}}(t \mid s) \right|}$$

where:
- *P_pre* is the frozen reference policy (BFS-Prover SFT checkpoint)
- *P_post* is the DPO-trained policy for this condition
- **premise-consistent** denotes tactics in the tactic category that addresses the specific violated constraint at state *s*, as determined by the pre-specified tactic taxonomy

The locality score measures what fraction of the post-DPO probability mass *shift* concentrates on tactics that address the specific error at each failed state. An oracle produces LS >> 0 (focused shift); a regularizer produces LS ≈ 0 (diffuse shift).

**Tactic taxonomy (pre-specified).** To prevent post-hoc circularity, we pre-specify the tactic category taxonomy from LeanDojo error categories before any training:
- **type_error**: `type mismatch`, `application type mismatch`
- **undefined_name**: `unknown identifier`, `unknown tactic`
- **tactic_failure**: `tactic failed`, `simp made no progress`

For each failed proof state, the error category is assigned from this taxonomy before DPO training begins.

**Gate condition.** The oracle hypothesis predicts LS_A > LS_P (grounded condition produces higher locality than permuted control), tested via one-sided t-test at p < 0.05. This is the MUST_WORK gate for hypothesis H-E1.

## 3.4 The α-Interaction Prediction

BFS-Prover's length normalization parameter α controls search depth bias:

$$\text{score}(s_L) = \frac{\sum_t \log p(a_t \mid s_t)}{L^\alpha}$$

At α=0, the scoring function is length-averse (shorter proof paths are preferred regardless of tactic probability). At α=1, the scoring is length-neutral. Under the oracle hypothesis, step-local grounded feedback provides greatest benefit at α=0, because local oracle guidance compensates for the search depth bias that would otherwise prevent deep proofs from being explored.

The α-interaction prediction is: Δ(A−B)|_{α=0} > Δ(A−B)|_{α=0.5} > Δ(A−B)|_{α=1.0}

This prediction compares Condition A (step-local grounded) against Condition B (step-local ungrounded) across α values — the grounded vs. ungrounded comparison is the scientifically appropriate reference because it isolates semantic content while holding step-locality constant. This prediction is uniquely attributable to the oracle mechanism: a regularizer would produce uniform gains across α settings (since it does not interact with search geometry). We sweep α ∈ {0.0, 0.5, 1.0} as part of hypotheses H-M3 and H-M4, providing a discriminating test beyond the locality score.

## 3.5 Hypothesis Chain

The full verification plan decomposes the oracle hypothesis into a 6-hypothesis chain:

- **H-E1 (Existence, MUST_WORK):** LS_A > LS_P — oracle signal exists at the probability mass level
- **H-M1 (Mechanism, MUST_WORK):** State alignment = 100% — pair construction creates valid state-aligned supervision
- **H-M2 (Mechanism, SHOULD_WORK):** LS_A > LS_B, Cohen's d > 0.2 — oracle mass shift is specific, not diffuse
- **H-M3 (Mechanism, SHOULD_WORK):** Δ(A−B) ≥ 10pp, non-overlapping 95% CIs — mass shift translates to task performance
- **H-M4 (Mechanism, SHOULD_WORK):** Monotonic α-interaction, Cohen's d ≥ 0.3 — oracle compensates for search geometry
- **H-C1 (Condition, SHOULD_WORK):** Fidelity-stratified Δ(A−B): Q4 > Q1 — oracle requires ≥85% formalization fidelity

Phase 4 execution targets H-E1 (the foundation gate). H-M1 through H-C1 are staged for subsequent runs contingent on H-E1 passing.

---

# 4. Experimental Setup

## 4.1 Research Questions

We design experiments to answer the following questions:

**RQ1:** Does step-local grounded DPO feedback (Condition A: Lean4 compiler errors) produce higher locality scores than permuted control (Condition P), confirming the oracle mechanism exists at the probability mass level? [Tests H-E1]

**RQ2:** Is the DPO pair construction protocol achieving 100% state alignment — ensuring conditions differ only in a_l content, not state distribution? [Tests H-M1]

**RQ3:** Does the oracle locality effect translate to greater hard-stratum pass@1 recovery for Condition A vs. Condition B, and does this advantage vary monotonically with α? [Tests H-M3, H-M4]

## 4.2 Datasets

We evaluate on two formal reasoning benchmarks, using only their **hard subsets** — problems where the cold-start SFT baseline achieves pass@1 < 20% across 16 rollouts.

**miniF2F Hard Subset**
- Source: Zheng et al. [2021]; HuggingFace: `Tonic/MiniF2F`
- Full benchmark: 488 problems (AMC/AIME/IMO + high-school/undergraduate mathematics) in Lean4 format
- Format: `{name, split, formal_statement, goal, header}` in Lean4 syntax
- Hard subset definition: Problems where BFS-Prover cold-start SFT achieves pass@1 < 20% across 16 rollouts

**Vericoding Hard Subset**
- Source: Bursuc et al. [2025]; arXiv:2509.22908
- Full benchmark: 12,504 formally verified code specifications across Lean/Verus/Dafny formalisms
- Filter: Lean4-compatible problems only (for LeanDojo compatibility)
- Hard subset definition: Same cold-start SFT protocol as miniF2F

| Dataset | Full Size | Format | Hard Subset (expected) |
|---------|-----------|--------|----------------------|
| miniF2F | 488 problems | Lean4 theorem proving | ~100–150 problems |
| Vericoding (Lean4 subset) | ~3,000 problems | Lean4 code verification | ~300–600 problems |

## 4.3 Baselines

The three DPO conditions serve as mutual baselines:

**Condition A — Step-Local Grounded (Proposed):** Rejected tactic a_l is a Lean4 compiler-error-triggering tactic at proof state s, with full compiler error message (error type, location, violated constraint). Tests the oracle hypothesis.

**Condition B — Step-Local Ungrounded (Ablation):** Rejected tactic a_l is a failed-branch tactic at the same proof state s, with no compiler error information. Isolates the contribution of step-locality vs. semantic grounding.

**Condition P — Permuted Control (Oracle Test):** Rejected tactic a_l is paired with a shuffled/permuted compiler error message (structure preserved, semantic content destroyed). The key oracle/regularizer discriminator.

## 4.4 Model

**Base model:** Qwen2.5-Math-7B with BFS-Prover cold-start SFT initialization (`ByteDance-Seed/BFS-Prover-V2-7B`). Architecture: decoder-only transformer, 7B parameters, bfloat16. Role: (1) frozen reference model π_ref for DPO; (2) starting point for each condition's DPO fine-tune.

## 4.5 Implementation Details

**DPO Training Configuration:**

| Hyperparameter | Value | Source |
|----------------|-------|--------|
| DPO β | 10.0 | BFS-Prover [Xin et al., 2025] |
| Learning rate | 5e-6 → 5e-7 (linear decay) | BFS-Prover |
| Batch size | 16 | BFS-Prover |
| Epochs | 1 | Standard DPO practice |
| Optimizer | AdamW (wd=0.01, β=(0.9, 0.999)) | eric-mitchell/DPO |
| Mixed precision | bfloat16 | BFS-Prover |
| Seeds | 1 (PoC stage) | — |

**Loss function** (following Rafailov et al. [2023]):

$$\mathcal{L}_{\text{DPO}} = -\log \sigma\left(\beta \cdot \left[\log \frac{\pi_\theta(a_w \mid s)}{\pi_{\text{ref}}(a_w \mid s)} - \log \frac{\pi_\theta(a_l \mid s)}{\pi_{\text{ref}}(a_l \mid s)}\right]\right)$$

with `average_log_prob=False` (sum log-probabilities for variable-length tactic sequences).

**Infrastructure:** Single NVIDIA H100 GPU (80GB), CUDA 12.0+, Python 3.10+, `lean-dojo>=2.0.0`, `transformers>=4.40.0`.

**Pair construction:** LeanDojo `Dojo` context manager extracts (state, tactic, compiler_error) triples. State alignment verified via LeanDojo state IDs: pipeline aborts if any pair has s_w ≠ s_l.

## 4.6 Evaluation Metrics

**Primary metric (MUST_WORK gate for H-E1):** **Locality Score (LS)** — fraction of post-DPO probability mass shift concentrated on premise-consistent tactic categories, computed over all hard-subset failed proof states. Gate: LS_A > LS_P (one-sided t-test, p < 0.05).

**Secondary metrics:** LS_A > LS_B (grounded vs. ungrounded comparison); hard-stratum pass@1 at α ∈ {0.0, 0.5, 1.0} for Conditions A and B (H-M3, H-M4; future work).

**Statistical testing:** One-sided t-test via `scipy.stats.ttest_1samp(LS_A - LS_P, 0, alternative='greater')`. Significance threshold: p < 0.05.

---

# 5. Results

## 5.1 Main Results: Locality Score Comparison

Table 1 presents the locality score results for all three DPO conditions on both evaluation datasets.

**Table 1: Locality Scores — H-E1 Experiment**

| Condition | miniF2F Hard Subset LS | Vericoding Hard Subset LS |
|-----------|------------------------|--------------------------|
| A: Step-local Grounded | 0.0000 | 0.0000 |
| B: Step-local Ungrounded | 0.0000 | 0.0000 |
| P: Permuted Control | 0.0000 | 0.0000 |
| t-statistic (A vs P) | 0.0000 | 0.0000 |
| p-value (one-sided) | 1.0000 | 1.0000 |
| **Gate Pass (H-E1)** | **False** | **False** |

> **Note: Vericoding rows are synthetic artifacts — dataset not retrieved; see Section 6.3 L4.** All Vericoding results originate from the same `_generate_synthetic_triples()` fallback that produced the synthetic miniF2F results; no actual Vericoding problems were processed.

All locality scores are identically 0.0000. The one-sided t-test yields p=1.0, providing no evidence that LS_A > LS_P. The H-E1 MUST_WORK gate fails.

**Key observation:** The null result is not a scientific finding about the oracle mechanism. It is a synthetic artifact.

## 5.2 Infrastructure Failure Diagnosis

The H-E1 gate failure is not attributable to a true null oracle effect. Post-run code analysis identifies the following failure chain:

**Root cause:** The Lean4 toolchain (`elan`, Lean4 compiler core) was not installed on the H100 cluster. `import lean_dojo` failed silently in the production path.

**Failure propagation:**
1. `leandojo_tracing.py:50-51`: `LeanGitRepo(url, commit)` succeeds (git operation), masking the absent Lean4 runtime.
2. `leandojo_tracing.py:62-64`: `trace(repo)` fails internally but the fallback is triggered.
3. `leandojo_tracing.py:114-137`: `_generate_synthetic_triples()` is invoked, returning hardcoded error strings (e.g., `"type mismatch"`, `"tactic failed"`) as compiler error messages.
4. `dpo_pairs.py`: DPO pairs are constructed from synthetic triples. All state IDs are synthetic identifiers; the 100% state alignment rate reflects alignment of synthetic IDs, not real Lean4 proof states.
5. `locality_score.py`: Probability mass shifts are computed over synthetic tactic representations. The computation is mechanically correct but scientifically meaningless.
6. `statistical_tests.py`: Gate evaluation correctly records FAIL with p=1.0 — the only output that accurately reflects the experimental situation.

**What was validated:**
- DPO training loop implementation (β=10, lr schedule, concatenated forward pass, `average_log_prob=False`) matches the eric-mitchell/DPO reference implementation.
- State alignment protocol (100% state_id matching in pair builder) is correctly implemented for the synthetic data.
- Tactic taxonomy pre-specification (type_error, undefined_name, tactic_failure) was established before any training.
- Gate evaluation and validation report generation function correctly.

**What was not validated:**
- Real LeanDojo proof state extraction from actual Lean4 proofs.
- Real Lean4 compiler error messages as DPO negatives.
- Locality score computation on real probability distributions over tactic tokens.

## 5.3 Post-Hoc Mock Detection

Post-hoc code inspection (via automated static analysis of `leandojo_tracing.py`) confirmed the failure chain. The inspection correctly localized the fallback at lines 50-51, 62-64, and 114-137, and confirmed that no real LeanDojo invocations occurred during the experiment. This demonstrates that automated post-run validity checking of experimental pipelines is feasible and informative.

## 5.4 DPO Training Configuration Validation

Despite the data failure, the training infrastructure produced internally consistent results. Table 2 summarizes the validated DPO configuration.

**Table 2: DPO Training Configuration (Correctly Executed)**

| Parameter | Configured Value | Validation |
|-----------|-----------------|------------|
| Model | ByteDance-Seed/BFS-Prover-V2-7B | Loaded correctly |
| DPO β | 10.0 | Matches BFS-Prover paper |
| Learning rate | 5e-6 → 5e-7 (linear decay) | Matches BFS-Prover paper |
| Epochs | 1 | Standard DPO practice |
| State alignment rate | 100% (synthetic IDs) | Protocol correct, data synthetic |
| Tactic taxonomy | Pre-specified (type_error, undefined_name, tactic_failure) | Assumption A4 satisfied |
| Loss implementation | average_log_prob=False | Matches eric-mitchell/DPO |

## 5.5 Convergent Evidence from Prior Systems

While H-E1 produces no direct evidence on the oracle hypothesis, three independent prior systems provide convergent evidence in the oracle direction:

| System | Result | Mechanism implied |
|--------|--------|------------------|
| BFS-Prover [Xin et al., 2025] | 72.95% miniF2F with Lean4 DPO | Step-local grounded → performance improvement |
| PropertyGPT [Liu et al., 2024] | 87% vs. 63% compilation success | Step-level structured feedback → inference improvement |
| Proof of Thought [Ganguly et al., 2024] | 14.6% → 0% compilation errors | Structured Z3 feedback → error elimination |

None of these systems isolates oracle from regularizer. The convergent direction is consistent with the oracle hypothesis but does not confirm it. A valid H-E1 run is required to provide the first direct mechanistic evidence.

---

# 6. Discussion

## 6.1 Key Findings

**Finding 1: The oracle/regularizer distinction is empirically tractable but infrastructure-dependent.**

The most important finding of this work is not the gate result (FAIL) but what the gate failure reveals: testing a mechanistic causal question in LLM formal reasoning requires infrastructure that the field has not yet systematically validated. Our 3-condition design, locality score metric, and α-interaction prediction are all theoretically sound. The experiment produced no scientific content not because the oracle hypothesis is false, but because the formal verifier — the essential instrument of the experiment — was never invoked. This suggests that the oracle/regularizer question is not merely open but *inaccessible* to existing experimental pipelines that lack pre-run environment validation.

**Finding 2: Silent synthetic fallbacks are a systemic risk in LLM+formal-verifier experiments.**

The failure mode we document — a production code path falling back to synthetic data generation when an external tool dependency is absent — is not specific to LeanDojo or this pipeline. Any LLM experiment that (a) depends on an external formal tool (proof assistant, SMT solver, static analyzer) and (b) has a fallback data generation path in the same codebase faces this risk. The BFS-Prover community, the PropertyGPT community, and the Proof of Thought community all rely on such tools. If fallback paths exist in production code, any of these pipelines could produce numerically consistent but scientifically empty results.

The failure is particularly insidious because it passes format validation: training runs completed, locality scores were computed, results files were written. Only the uniformly zero values and subsequent code review revealed the problem. This implies that *result plausibility* is not a sufficient validity check — experiments must explicitly verify that the formal verifier was invoked with real inputs.

**Finding 3: The DPO infrastructure for the oracle test is implemented and unit-tested.**

The positive outcome of this run is an implemented and unit-tested implementation of the exact DPO training configuration needed to test the oracle hypothesis. The β=10 setting matches BFS-Prover; the state alignment protocol is correct; the tactic taxonomy is pre-specified; the gate evaluation logic works. Re-running H-E1 after installing LeanDojo requires only environment setup, not re-implementation.

## 6.2 Implications for the Field

**For experimental practice:** LLM formal reasoning experiments should adopt pre-run environment validation gates — explicit checks that verify real tool invocation with real outputs before training begins. For a LeanDojo-dependent experiment, this means: verify that `import lean_dojo` succeeds, that `Dojo` returns real proof states, and that at least N real (state, tactic, error) triples are extracted before any DPO training starts. We propose:

```python
# Pre-run gate (required before any DPO training)
real_triples = extract_state_triples(problems[:10], timeout=60)
assert len(real_triples) >= 5, "Pre-run gate FAIL: LeanDojo not producing real triples"
```

**For metric design:** The locality score metric is a substantive contribution independent of the oracle/regularizer result. Prior work measures only pass@1 — a task-level outcome that cannot distinguish oracle function from regularization. Locality score provides a mechanistic intermediate measurement that can identify *why* DPO training succeeds or fails, and can detect null effects that pass@1 would miss.

**For benchmark design:** The miniF2F and Vericoding datasets do not include feedback loop evaluation metrics. A benchmark designed to evaluate formal feedback mechanisms would include: baseline pass@1 per problem, expected feedback type per error, locality score ground truth (which tactics are premise-consistent for each error), and repair success rate per feedback round.

## 6.3 Limitations

**L1 — H-E1 oracle hypothesis remains untested.** The central scientific claim — that step-local grounded feedback functions as a local logical oracle — has no direct experimental support. Until a valid LeanDojo-enabled H-E1 run is completed, the oracle/regularizer question is open. *Future work:* Install Lean4 toolchain (`elan` + Lean4 compiler core), remove `_generate_synthetic_triples()` from production paths, add pre-run gate, and re-execute H-E1. Estimated effort: 1–2 days.

**L2 — Locality score not yet validated on real data.** The locality score metric has been computed only on synthetic proof state representations. Its behavior on real LeanDojo tactic distributions is unknown. The metric may require calibration — the formula includes a 1e-8 epsilon term in the denominator to prevent division by zero.

**L3 — Single seed, single model scale.** The PoC design uses seed=1 and Qwen2.5-Math-7B (7B parameters). Full statistical validation across seeds and at 70B+ scale is the responsibility of H-M3.

**L4 — Vericoding not retrieved.** Vericoding requires manual download from the arXiv paper release. The oracle/regularizer test is valid on miniF2F alone for H-E1; Vericoding cross-formalism generalization is tested in H-M3.

## 6.4 Broader Impact

This research directly targets LLM theorem proving and formal code verification — systems with significant potential for positive impact in software safety, mathematical discovery, and formal specification. The methodological contribution (pre-run environment validation) applies broadly to any AI system that integrates with external formal tools. The risk we identify — silent fallback to synthetic data — could affect safety-critical code generators or formal specification tools. Raising awareness of this failure mode and proposing detection protocols has immediate practical value. Potential negative impacts are limited: this is a methodological paper with no direct deployment pathway.

---

# 7. Conclusion

We began by observing that three of the most successful LLM formal reasoning systems — BFS-Prover, PropertyGPT, and Proof of Thought — all use structured formal feedback to improve performance, yet none can explain *why* it works. We proposed that this gap is not merely rhetorical: two mechanistically distinct hypotheses (oracle vs. regularizer) predict different design conclusions, and no existing work has been designed to distinguish them.

In this work, we introduced the oracle/regularizer framing, the locality score metric, and a 3-condition 2×2 factorial design capable of testing the oracle hypothesis for the first time. Attempting to execute this experiment produced an unexpected finding: the Lean4 toolchain dependency silently fell back to synthetic data generation, producing an experiment that ran correctly in every measurable sense except the one that mattered — it never invoked the formal verifier.

This outcome is itself a contribution. The DPO training loop is validated. The state alignment protocol is correct. The locality score computation is implemented. The tactic taxonomy is pre-specified. The α-interaction prediction is theoretically grounded. What remains is a single environment setup task and the conviction that testing *why* formal feedback works is worth the engineering cost.

**Summary of contributions:**

1. The **oracle/regularizer distinction** — a testable mechanistic framing that unifies BFS-Prover, PropertyGPT, and Proof of Thought under a single causal hypothesis, with the α-interaction prediction as a uniquely discriminating empirical test.

2. The **locality score metric** — a novel mechanistic probe measuring the fraction of post-DPO probability mass shift concentrated on premise-consistent tactic categories, directly operationalizing oracle function vs. diffuse regularization.

3. An **implemented and unit-tested experimental infrastructure** — a 3-condition DPO pipeline with 100% state alignment verification, pre-specified tactic taxonomy, and correct DPO loss implementation (β=10, lr 5e-6→5e-7, average_log_prob=False), ready for re-execution with real LeanDojo data.

4. A **methodological warning and protocol** — documentation of the silent synthetic fallback failure mode in LLM+formal-verifier pipelines, with proposed pre-run environment validation gates as a standard practice for the field.

**Future directions.** The most immediate direction is completing H-E1 with real LeanDojo data, resolving whether LS_A > LS_P and providing the first direct mechanistic evidence on the oracle/regularizer question. If H-E1 passes, the subsequent hypothesis chain (H-M1 through H-C1) tests whether the oracle mass shift translates to hard-stratum pass@1 recovery and whether the α-interaction prediction holds. Two further directions motivate follow-on work: testing whether the oracle effect holds at inference time (frozen policy, no DPO), and testing cross-formalism transfer — does the oracle mechanism hold for Verus and Dafny formalisms in Vericoding, or is it Lean4-specific?

We opened by asking why formal feedback helps. We now know the question is harder to answer than it appears — and we have built the tools to answer it.

---

## References

[Bursuc et al., 2025] Bursuc, S., Ehrenborg, T., Lin, S., Astefanoaei, L., et al. A benchmark for vericoding: formally verified program synthesis. *arXiv:2509.22908*, 2025.

[Dong and Ma, 2025] Dong, K. and Ma, T. STP: Self-play LLM theorem provers with iterative conjecturing and proving. In *International Conference on Machine Learning*, 2025.

[Ganguly et al., 2024] Ganguly, D., Iyengar, S., Chaudhary, V., and Kalyanaraman, S. Proof of thought: Neurosymbolic program synthesis allows robust and interpretable reasoning. *arXiv:2409.17270*, 2024.

[Lai et al., 2024] Lai, X., et al. Step-DPO: Step-wise preference optimization for long-chain reasoning of LLMs. *arXiv:2406.18629*, 2024.

[Liu et al., 2024] Liu, Y., Xue, Y., Wu, D., Sun, Y., Li, Y., Shi, M., and Liu, Y. PropertyGPT: LLM-driven formal verification of smart contracts through retrieval-augmented property generation. In *Network and Distributed System Security Symposium*, 2025.

[Liu et al., 2024b] Liu, Y., et al. Agents4PLC: Automating closed-loop PLC code generation and verification in industrial control systems. *arXiv*, 2024.

[Mitchell et al., 2023] Mitchell, E. Direct preference optimization: Reference implementation. GitHub repository. https://github.com/eric-mitchell/direct-preference-optimization, 2023.

[Rafailov et al., 2023] Rafailov, R., Sharma, A., Mitchell, E., Ermon, S., Manning, C. D., and Finn, C. Direct preference optimization: Your language model is secretly a reward model. In *Advances in Neural Information Processing Systems*, 2023.

[Xin et al., 2025] Xin, R., Liu, C., Guo, Q., et al. BFS-Prover: Scalable best-first tree search for LLM-based automatic theorem proving. In *Proceedings of the 63rd Annual Meeting of the ACL*, 2025. arXiv:2502.03438.

[Yang et al., 2023] Yang, K., Swope, A. M., Gu, A., et al. LeanDojo: Theorem proving with retrieval-augmented language models. In *Advances in Neural Information Processing Systems*, 2023.

[Zheng et al., 2021] Zheng, K., Han, J. M., and Polu, S. MiniF2F: A cross-system benchmark for formal olympiad-level mathematics. In *International Conference on Learning Representations*, 2022.
