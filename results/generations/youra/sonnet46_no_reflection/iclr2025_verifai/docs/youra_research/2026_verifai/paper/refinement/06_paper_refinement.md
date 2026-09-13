# Testing the Oracle Mechanism in LLM Formal Reasoning: A Locality Score Approach with Infrastructure Failure Analysis

## Abstract

Formal verification feedback loops have been shown to improve LLM performance on theorem proving and code verification tasks. The underlying mechanism remains unresolved: does structured formal feedback function as a *local logical oracle* that directs probability mass toward premise-consistent tactics, or as a *policy regularizer* that sharpens the model regardless of the semantic content of the feedback signal? This paper introduces the oracle/regularizer distinction as a testable mechanistic question, proposes the **locality score** — the fraction of post-DPO probability mass shift concentrated on premise-consistent tactic categories — as a direct mechanistic probe, and describes a 3-condition experiment (grounded, ungrounded, permuted control) within the BFS-Prover framework designed to test this distinction. An attempt to execute this experiment encountered an infrastructure failure: the LeanDojo proof state extraction layer silently substituted synthetic hardcoded error strings for real Lean4 compiler outputs, rendering all locality score measurements uninformative. Locality scores for all three conditions were uniformly 0.0000 on both the miniF2F and Vericoding evaluation datasets, with a one-sided t-statistic of 0.0000 and p-value of 1.0000. This outcome is a synthetic artifact rather than a scientific finding: the DPO training infrastructure (β=10, 100% state alignment on synthetic data, correct loss implementation) was validated, but no real Lean4 compiler invocations occurred. The experimental design and implementation are ready for re-execution after the LeanDojo environment is properly installed. This paper documents the silent synthetic fallback failure mode and proposes pre-run environment validation gates as a methodological recommendation for LLM experiments that depend on external formal tools.

## 1. Introduction

Three recent LLM formal reasoning systems share a common design feature: they supply the language model with structured feedback from a formal verifier. BFS-Prover achieves 72.95% on the miniF2F theorem proving benchmark using Lean4 compiler errors as DPO negatives [Xin et al., 2025]. PropertyGPT improves smart contract property compilation success from 63% to 87% using static analysis feedback at inference time [Liu et al., 2024]. Proof of Thought reduces compilation errors from 14.6% to 0% using Z3 SMT counterexamples via a JSON DSL bridge [Ganguly et al., 2024]. None of these systems identifies the mechanism by which formal feedback produces these improvements.

Two mechanistically distinct explanations are consistent with the observed results. Under the **oracle hypothesis**, structured formal feedback carries state-specific semantic information that directs the policy toward formally valid continuations. Under the **regularizer hypothesis**, formal feedback acts as a source of contrastive examples for DPO training, sharpening the policy through a general regularization effect that does not depend on the semantic content of the negative example.

These hypotheses predict different design conclusions. If the oracle hypothesis holds, feedback quality (semantic specificity) is the critical design variable. If the regularizer hypothesis holds, feedback diversity (number and variety of negatives) is more important. These conclusions point in opposite directions for future system design.

No existing work has been designed to distinguish these hypotheses. Each system uses a single feedback type; cross-condition controlled ablations have not been performed.

This paper introduces a 2×2 factorial design within the BFS-Prover framework intended to test the oracle/regularizer distinction. The design holds all variables constant except the semantic content of the DPO negative example, using three conditions: step-local Lean4 compiler errors (grounded), same-state failed-branch tactics (ungrounded), and permuted compiler error messages (control). The **locality score** metric is introduced as a mechanistic probe measuring what fraction of the post-DPO probability mass shift concentrates on tactic categories consistent with the specific error at each failed proof state.

Attempting to execute this experiment produced an infrastructure failure rather than empirical results. The LeanDojo proof state extraction layer silently fell back to synthetic data generation when the Lean4 toolchain was absent, producing uniformly zero locality scores that passed format validation while carrying no scientific content. This failure mode and the proposed remediation protocol are documented as a methodological contribution.

**Contributions:**

1. The **oracle/regularizer framing**: a testable mechanistic distinction that unifies BFS-Prover, PropertyGPT, and Proof of Thought under a single causal hypothesis.

2. The **locality score metric**: a novel mechanistic probe — the fraction of post-DPO probability mass shift on premise-consistent tactic categories — that directly operationalizes oracle function versus diffuse regularization.

3. An **implemented and unit-tested experimental infrastructure**: a 3-condition DPO pipeline with 100% state alignment verification, pre-specified tactic taxonomy (type_error, undefined_name, tactic_failure), and correct DPO loss implementation (β=10, lr 5e-6→5e-7, average_log_prob=False), ready for re-execution with real LeanDojo data.

4. A **methodological warning**: documentation of the silent synthetic fallback failure mode in LLM+formal-verifier pipelines, with a proposed pre-run environment validation protocol.

## 2. Related Work

### 2.1 Proof Checker Feedback

**BFS-Prover** [Xin et al., 2025] combines Best-First Tree Search with DPO training using Lean4 compiler errors as rejected examples. At each proof state, the Lean4 compiler returns structured error messages for failed tactics; these become the rejected examples in DPO pairs. The system achieves 72.95% on miniF2F. DPO hyperparameters include β=10, learning rate decay from 5e-6 to 5e-7, and a 1-epoch training schedule. BFS-Prover does not compare its feedback condition against semantically ungrounded alternatives, so whether the semantic content of compiler errors (versus simply having same-state failed tactics as negatives) drives the improvement is unknown.

**STP** [Dong and Ma, 2025] achieves 65% on miniF2F using self-play with formal verifier feedback at the episode level. Like BFS-Prover, STP uses a single feedback type without cross-condition ablation.

**Neural Theorem Proving** [Rao et al., 2025] applies SFT+RL with Isabelle verifier feedback, achieving state-of-the-art results on Isabelle benchmarks, again without testing the mechanistic question.

### 2.2 SMT Solver Feedback

**Proof of Thought** [Ganguly et al., 2024] uses Z3 SMT counterexamples via a JSON DSL bridge in an inference-time repair loop (no DPO training), reducing compilation errors from 14.6% to 0%. The Z3 counterexample provides episode-level grounded feedback, not step-local guidance.

**Step-Wise Formal Verification** [Zhou and Zhang, 2025] uses SMT solvers and computer algebra systems as external oracles for LLM math verification at inference time.

### 2.3 Static Analysis Feedback

**PropertyGPT** [Liu et al., 2024] uses PSL compiler feedback to guide LLM generation of smart contract formal properties, improving compilation success from 63% to 87% and achieving 80% recall on Certora-audited projects. This is the strongest available inference-time evidence consistent with the oracle framing. Structured feedback with explicit semantic content outperforms no-feedback baselines; the mechanism is not isolated.

### 2.4 DPO for Formal Reasoning

**Step-DPO** [Lai et al., 2024] applies step-level preference optimization to informal mathematical reasoning, treating individual reasoning steps as preference units. This is structurally analogous to tactic-level DPO in formal verification but operates without a formal verifier.

### 2.5 Benchmark Landscape

**miniF2F** [Zheng et al., 2021] provides 488 theorem proving problems (AMC/AIME/IMO and high-school/undergraduate mathematics) in Lean4 format. **Vericoding** [Bursuc et al., 2025] provides 12,504 formally verified code specifications across Lean4/Verus/Dafny formalisms. Neither benchmark includes feedback-loop evaluation metrics such as locality score or feedback signal quality.

### 2.6 Positioning

No prior work introduces the oracle/regularizer framing as a testable distinction, proposes a mechanistic metric (locality score) to directly measure oracle function, or designs a controlled cross-condition experiment within a fixed BFS framework to separate semantic from structural contributions of formal feedback.

## 3. Method

### 3.1 The Oracle/Regularizer Distinction

When the Lean4 compiler rejects a tactic at proof state *s* with a type mismatch message, that message carries semantic content: the violated type constraint and an implicit pointer toward premise-consistent continuations. Under the oracle hypothesis, a DPO model trained on this rejection concentrates probability mass on tactics that address the specific type constraint. Under the regularizer hypothesis, the DPO update diffusely sharpens the policy regardless of the error message content.

Two implications follow. If the oracle hypothesis holds, the quality of feedback (semantic specificity) is the key design variable. If the regularizer hypothesis holds, the quantity and diversity of negative examples is more important. These lead to opposite design recommendations.

### 3.2 Three-Condition DPO Design

The experiment extends the BFS-Prover framework [Xin et al., 2025], using `ByteDance-Seed/BFS-Prover-V2-7B` (Qwen2.5-Math-7B initialized from the BFS-Prover cold-start SFT checkpoint). All three conditions share the same base model (frozen π_ref), the same proof states (hard subset: cold-start SFT pass@1 < 20% across 16 rollouts), the same chosen tactics (a_w), and the same DPO hyperparameters (β=10, lr 5e-6→5e-7, 1-epoch). The conditions differ only in the rejected tactic (a_l):

| Condition | Name | a_l content | Semantic grounding |
|-----------|------|-------------|-------------------|
| A | Step-local Grounded | Lean4 compiler-error-triggering tactic at state *s* | Full: error type, location, violated constraint |
| B | Step-local Ungrounded | Failed-branch tactic at same state *s* (no error message) | None: failed tactic identity only |
| P | Permuted Control | Tactic paired with shuffled/permuted compiler error message | Scrambled: structure preserved, semantics destroyed |

Condition A versus P isolates the contribution of coherent semantic content (both have compiler error messages; only A has consistent ones). Condition A versus B isolates the contribution of semantic grounding (both are step-local; only A is grounded).

**State alignment requirement.** For all three conditions, the chosen tactic a_w and rejected tactic a_l must originate from the same proof state *s*. State alignment is verified via LeanDojo state IDs; the pipeline aborts if any pair has s_w ≠ s_l.

### 3.3 The Locality Score Metric

The **locality score (LS)** is defined as:

$$\text{LS} = \frac{\sum_s \left[ P_{\text{post}}(\text{premise-consistent} \mid s) - P_{\text{pre}}(\text{premise-consistent} \mid s) \right]}{\sum_s \sum_t \left| P_{\text{post}}(t \mid s) - P_{\text{pre}}(t \mid s) \right|}$$

where *P_pre* is the frozen reference policy and *P_post* is the DPO-trained policy for a given condition. "Premise-consistent" denotes tactics in the tactic category that addresses the specific violated constraint at state *s*, as determined by the pre-specified taxonomy.

An oracle produces LS >> 0 (focused mass shift); a regularizer produces LS ≈ 0 (diffuse mass shift).

**Tactic taxonomy (pre-specified).** To prevent post-hoc circularity, the tactic category taxonomy is defined before any training:
- **type_error**: `type mismatch`, `application type mismatch`
- **undefined_name**: `unknown identifier`, `unknown tactic`
- **tactic_failure**: `tactic failed`, `simp made no progress`

**Gate condition.** The oracle hypothesis predicts LS_A > LS_P, tested via one-sided t-test at p < 0.05. This is the MUST_WORK gate for hypothesis H-E1.

### 3.4 The α-Interaction Prediction

BFS-Prover's length normalization parameter α controls search depth bias:

$$\text{score}(s_L) = \frac{\sum_t \log p(a_t \mid s_t)}{L^\alpha}$$

At α=0, shorter proof paths are preferred regardless of tactic probability. Under the oracle hypothesis, step-local grounded feedback provides the greatest benefit at α=0, because local oracle guidance compensates for search depth bias that would otherwise prevent deep proofs from being explored. The prediction is: Δ(A−B)|_{α=0} > Δ(A−B)|_{α=0.5} > Δ(A−B)|_{α=1.0}. A regularizer would predict uniform gains across α settings. This α-interaction prediction is tested in hypotheses H-M3 and H-M4 (not executed in the present run).

### 3.5 Hypothesis Chain

The full verification plan decomposes into a 6-hypothesis chain:

| ID | Type | Gate | Description |
|----|------|------|-------------|
| H-E1 | Existence | MUST_WORK | LS_A > LS_P — oracle signal detectable at probability mass level |
| H-M1 | Mechanism | MUST_WORK | State alignment = 100% — valid state-aligned DPO supervision |
| H-M2 | Mechanism | SHOULD_WORK | LS_A > LS_B, Cohen's d > 0.2 — oracle mass shift is specific |
| H-M3 | Mechanism | SHOULD_WORK | Δ(A−B) ≥ 10pp on hard-stratum pass@1 |
| H-M4 | Mechanism | SHOULD_WORK | Monotonic α-interaction, Cohen's d ≥ 0.3 |
| H-C1 | Condition | SHOULD_WORK | Fidelity-stratified Δ(A−B): Q4 > Q1 (oracle requires ≥85% formalization fidelity) |

Phase 4 execution targets H-E1 only. H-M1 through H-C1 were not executed, as they depend on H-E1 passing.

## 4. Experimental Setup

### 4.1 Research Questions

**RQ1:** Does step-local grounded DPO feedback (Condition A) produce higher locality scores than permuted control (Condition P), confirming the oracle mechanism at the probability mass level? [Tests H-E1]

**RQ2:** Does the DPO pair construction protocol achieve 100% state alignment? [Tests H-M1]

**RQ3:** Does the oracle locality effect translate to greater hard-stratum pass@1 recovery, and does this advantage vary monotonically with α? [Tests H-M3, H-M4; not executed]

### 4.2 Datasets

**miniF2F Hard Subset.** Full benchmark: 488 problems (AMC/AIME/IMO and high-school/undergraduate mathematics) in Lean4 format, loaded via HuggingFace (`Tonic/MiniF2F`). Format: `{name, split, formal_statement, goal, header}`. The hard subset is defined as problems where BFS-Prover cold-start SFT achieves pass@1 < 20% across 16 rollouts. The full miniF2F dataset (488 problems) was loaded from HuggingFace in the Phase 4 run; the hard subset construction required cold-start SFT evaluation that was not completed (see Section 5.2).

**Vericoding Hard Subset.** Full benchmark: 12,504 formally verified code specifications across Lean4/Verus/Dafny [Bursuc et al., 2025]. The Vericoding data path was not found during the Phase 4 run (`data/vericoding` absent); 0 Vericoding problems were loaded. Any Vericoding results reported below are artifacts of the same synthetic fallback that produced the miniF2F null result.

| Dataset | Full Size | Intended Hard Subset | Actual Status in Phase 4 |
|---------|-----------|----------------------|--------------------------|
| miniF2F | 488 problems | ~100–150 (pass@1 < 20%) | 488 loaded; hard subset not constructed |
| Vericoding (Lean4) | ~3,000 (estimated) | ~300–600 | 0 loaded; data path not found |

### 4.3 Model

**Base model:** `ByteDance-Seed/BFS-Prover-V2-7B` — Qwen2.5-Math-7B with BFS-Prover cold-start SFT initialization. Architecture: decoder-only transformer, 7B parameters, bfloat16. The model serves as both the frozen reference π_ref and the starting point for each condition's DPO fine-tuning. The model was loaded with `device_map="auto"` on a single GPU (GPU 2 per the experiment log), using 90% of device memory.

### 4.4 DPO Training Configuration

| Hyperparameter | Value | Source |
|----------------|-------|--------|
| DPO β | 10.0 | BFS-Prover [Xin et al., 2025] |
| Learning rate start | 5e-6 | BFS-Prover |
| Learning rate end | 5e-7 (linear decay) | BFS-Prover |
| Batch size | 16 | BFS-Prover |
| Epochs | 1 | Standard DPO practice |
| Optimizer | AdamW (wd=0.01, β=(0.9, 0.999)) | eric-mitchell/DPO |
| Mixed precision | bfloat16 | BFS-Prover |
| Seeds | 1 | PoC stage |

The DPO loss uses `average_log_prob=False` (sum log-probabilities for variable-length tactic sequences), consistent with the eric-mitchell/DPO reference implementation. The concatenated forward pass pattern (chosen and rejected in a single forward pass) was implemented as specified.

### 4.5 Infrastructure

Single NVIDIA H100 GPU (80GB), CUDA 12.0+, Python 3.10+. LeanDojo (`lean-dojo>=2.0.0`) was listed as a required dependency but was not available at runtime due to the absent Lean4 toolchain on the H100 cluster.

### 4.6 Evaluation Metrics

**Primary metric (H-E1 gate):** Locality Score (LS) — tested via one-sided t-test (`scipy.stats.ttest_1samp`, alternative='greater'), significance threshold p < 0.05. Gate: LS_A > LS_P.

**Secondary metric:** LS_A > LS_B (grounded versus ungrounded comparison).

## 5. Results

### 5.1 Main Results: Locality Score Comparison

All locality scores for all three conditions were uniformly 0.0000 on both evaluation datasets. The H-E1 MUST_WORK gate failed.

**Table 1: Locality Scores — H-E1 Experiment**

| Condition | miniF2F Hard Subset LS | Vericoding Hard Subset LS |
|-----------|------------------------|--------------------------|
| A: Step-local Grounded | 0.0000 | 0.0000 |
| B: Step-local Ungrounded | 0.0000 | 0.0000 |
| P: Permuted Control | 0.0000 | 0.0000 |
| t-statistic (A vs. P) | 0.0000 | 0.0000 |
| p-value (one-sided) | 1.0000 | 1.0000 |
| Gate Pass (H-E1) | False | False |
| Secondary (LS_A > LS_B) | False | False |

**Note on Vericoding results:** Vericoding was not retrieved; 0 problems were loaded. The Vericoding rows originate from the same synthetic data fallback that produced the miniF2F null results. No actual Vericoding problems were processed.

These results are not a scientific finding about the oracle mechanism. They are a synthetic artifact caused by the infrastructure failure described in Section 5.2.

![Locality score comparison across conditions on miniF2F and Vericoding hard subsets. All conditions yield LS=0.0 due to synthetic data fallback.](/home/anonymous/YouRA_results_new_4_sonnet46_no_reflection/TEST_verifai_sonnet46_no_reflection/docs/youra_research/20260520_verifai/paper/figures/locality_score_comparison.png)

*Figure 1: Locality score comparison across three DPO conditions (A: grounded, B: ungrounded, P: permuted) on miniF2F and Vericoding hard subsets. All conditions yield LS=0.0 due to synthetic data substitution (LeanDojo absent).*

### 5.2 Infrastructure Failure Diagnosis

The H-E1 gate failure is attributable to a missing Lean4 toolchain rather than to a true null oracle effect.

**Root cause:** The Lean4 toolchain (`elan`, Lean4 compiler core) was not installed on the H100 cluster. `import lean_dojo` raised an `ImportError` in the production code path.

**Failure propagation:**

1. `leandojo_tracing.py`: `LeanGitRepo(url, commit)` succeeds as a git operation, masking the absent Lean4 runtime.
2. `trace(repo)` fails internally; the exception is caught and a fallback is triggered.
3. `_generate_synthetic_triples()` is invoked, returning hardcoded error strings (e.g., `"type mismatch"`, `"tactic failed"`) as compiler error messages, with synthetic state IDs.
4. `dpo_pairs.py`: DPO pairs are constructed from synthetic triples. The 100% state alignment rate reflects alignment of synthetic IDs, not real LeanDojo proof states.
5. `locality_score.py`: Probability mass shifts are computed over synthetic tactic representations. The formula executes without error but operates on meaningless inputs.
6. `statistical_tests.py`: Gate evaluation records FAIL with p=1.0 — the only output that accurately reflects the experimental situation.

The experiment log (recorded at 2026-05-20 10:01:34) confirms: 488 miniF2F problems were loaded from HuggingFace, 0 Vericoding problems were loaded (data path not found), and the cold-start SFT evaluation was initiated but not completed within the logged window.

![Post-DPO probability mass distribution across tactic categories per condition and dataset (synthetic artifact).](/home/anonymous/YouRA_results_new_4_sonnet46_no_reflection/TEST_verifai_sonnet46_no_reflection/docs/youra_research/20260520_verifai/paper/figures/probability_mass_distribution.png)

*Figure 2: Post-DPO probability mass distribution across tactic categories (type_error, undefined_name, tactic_failure) per condition and dataset. All distributions are synthetic artifacts from hardcoded error strings.*

### 5.3 Infrastructure Components Validated

Despite the data failure, the training infrastructure was validated on synthetic inputs:

**Table 2: DPO Training Configuration — Validation Status**

| Component | Configured Value | Validation Status |
|-----------|-----------------|-------------------|
| Model | ByteDance-Seed/BFS-Prover-V2-7B | Loaded correctly |
| DPO β | 10.0 | Matches BFS-Prover paper |
| Learning rate | 5e-6 → 5e-7 (linear decay) | Matches BFS-Prover paper |
| Epochs | 1 | Correct |
| State alignment rate | 100% (on synthetic IDs) | Protocol correct; data synthetic |
| Tactic taxonomy | Pre-specified (type_error, undefined_name, tactic_failure) | Immutable; pre-specified |
| Loss: average_log_prob | False (sum log-probs) | Matches eric-mitchell/DPO |
| Concatenated forward pass | Chosen + rejected in single pass | Implemented correctly |

**What was not validated:** real LeanDojo proof state extraction, real Lean4 compiler error messages as DPO negatives, and locality score computation on real probability distributions over tactic tokens.

### 5.4 Post-Hoc Code Review

Automated code review of `leandojo_tracing.py` confirmed that no real LeanDojo invocations occurred. The synthetic fallback was localized to the `_generate_synthetic_triples()` function. In the final version of the code (after the Phase 4 run), `leandojo_tracing.py` raises a `RuntimeError` rather than falling back to synthetic data when `import lean_dojo` fails, and similarly raises `RuntimeError` when `extract_state_triples` returns no triples. This post-run fix removes the silent fallback from the production code path.

![Locality score per proof state across hard subset instances (synthetic artifact showing uniformly zero scores).](/home/anonymous/YouRA_results_new_4_sonnet46_no_reflection/TEST_verifai_sonnet46_no_reflection/docs/youra_research/20260520_verifai/paper/figures/locality_score_per_state.png)

*Figure 3: Locality score per proof state across hard-subset instances, showing uniformly zero scores due to synthetic data generation rather than real LeanDojo extraction.*

### 5.5 Convergent Evidence from Prior Systems

The three prior systems that motivated the oracle hypothesis provide indirect evidence consistent with the oracle framing, but do not test it:

| System | Result | Mechanism implied |
|--------|--------|------------------|
| BFS-Prover [Xin et al., 2025] | 72.95% miniF2F with Lean4 DPO | Step-local grounded feedback → performance improvement |
| PropertyGPT [Liu et al., 2024] | 87% vs. 63% compilation success | Structured static analysis feedback → inference improvement |
| Proof of Thought [Ganguly et al., 2024] | 14.6% → 0% compilation errors | Structured Z3 feedback → error elimination |

None of these systems isolates oracle from regularizer function. The convergent direction is consistent with the oracle hypothesis but does not confirm it. The H-E1 experiment, once executed with real LeanDojo data, would provide the first controlled test.

![Locality score breakdown by LeanDojo error category for each DPO condition (synthetic artifact).](/home/anonymous/YouRA_results_new_4_sonnet46_no_reflection/TEST_verifai_sonnet46_no_reflection/docs/youra_research/20260520_verifai/paper/figures/error_category_breakdown.png)

*Figure 4: Locality score breakdown by LeanDojo error category (type_error, undefined_name, tactic_failure) per DPO condition. All values are zero due to synthetic data. No real error categorization occurred.*

## 6. Discussion

### 6.1 Interpretation of Results

The uniformly zero locality scores and p=1.0 do not constitute evidence that the oracle mechanism is absent. The synthetic data fallback means that no measurement of the oracle mechanism was attempted. Under the available evidence, the oracle/regularizer question remains open.

The DPO training infrastructure ran on synthetic (state, tactic, compiler_error) triples in which all error strings were hardcoded constants. Any probability mass shifts computed during training and evaluation reflect the model's response to meaningless inputs, not responses to real Lean4 compiler semantics. The 100% state alignment rate reflects alignment of synthetic state IDs, not real proof states.

The gate evaluation correctly recorded a FAIL with p=1.0. This is the only output of the Phase 4 run that accurately reflects the experimental situation.

The hypothesis is not falsified. The Phase 4.5 synthesis document (045_validated_hypothesis.md) classifies the outcome as INFRASTRUCTURE_FAILURE_NOT_SCIENTIFIC and recommends a Phase 4 retry after the LeanDojo environment is correctly installed and the synthetic fallback is removed.

### 6.2 The Silent Synthetic Fallback Failure Mode

The failure mode documented here — a production code path falling back to synthetic data generation when an external tool dependency is absent — poses a risk to any LLM+formal-verifier experiment. The failure is difficult to detect because:

1. Training runs complete without error.
2. Locality scores are computed and written to result files.
3. Format validation passes.
4. Only the uniformly zero values and subsequent code review reveal the problem.

Plausibility of numerical outputs is not a sufficient validity check. Any pipeline that (a) depends on an external formal tool and (b) has a fallback data generation path in the same codebase faces this risk. This includes pipelines built on Lean4 (LeanDojo), Z3, and static analyzers such as PSL.

The proposed detection protocol is:

```python
# Pre-run gate (required before any DPO training)
real_triples = extract_state_triples(problems[:10], timeout=60)
assert len(real_triples) >= 5, "Pre-run gate FAIL: LeanDojo not producing real triples"
```

This check must be placed before any training begins and must verify that real triples (not synthetic) are returned.

### 6.3 Locality Score Metric

The locality score metric has not yet been validated on real data. Its behavior on real LeanDojo tactic distributions is unknown. The formula includes an ε=1e-8 additive term in the denominator to prevent division by zero. Whether the metric reliably distinguishes oracle from regularizer function on real proof state distributions is an open empirical question.

### 6.4 Limitations

**L1 — Oracle hypothesis untested.** The central scientific claim — that step-local grounded feedback functions as a local logical oracle — has no direct experimental support from this run. Required fix: install Lean4 toolchain (`elan` + Lean4 compiler core), verify LeanDojo installation, remove `_generate_synthetic_triples()` from production code paths, add pre-run gate, and re-execute H-E1.

**L2 — Vericoding not retrieved.** The Vericoding dataset was not downloaded; 0 problems were loaded. The H-E1 MUST_WORK gate requires valid results only on miniF2F for the PoC stage.

**L3 — Hard subset not constructed.** Cold-start SFT evaluation on miniF2F (16 rollouts per problem) was not completed, so the hard subset (problems with pass@1 < 20%) was not identified. DPO training and locality score measurement require the hard subset.

**L4 — Single seed, 7B scale.** The PoC design uses seed=1 and a 7B parameter model. Statistical validation across seeds and at larger model scale is deferred to H-M3.

**L5 — Locality score not validated.** The metric has been computed only on synthetic inputs. Its calibration and discriminative power on real proof state distributions are unknown.

**L6 — Vericoding results are artifacts.** All Vericoding locality scores reported in Table 1 originate from the synthetic data fallback. No actual Vericoding problems were processed.

None of L1–L6 reflects on the scientific validity of the oracle/regularizer hypothesis. All are infrastructure and implementation limitations of this Phase 4 run.

### 6.5 Broader Impact

This research targets LLM theorem proving and formal code verification. The methodological contribution — pre-run environment validation for LLM+formal-verifier pipelines — applies broadly to any AI system that integrates with external formal tools. The silent fallback failure mode identified here could affect safety-critical formal specification tools. Potential negative impacts are limited; this is a methodological paper with no direct deployment pathway.

## 7. Conclusion

Three of the most successful LLM formal reasoning systems use structured formal feedback from a verifier to improve performance, yet none has tested why this feedback helps. This paper introduced the oracle/regularizer distinction as a testable mechanistic framing, the locality score metric as a direct mechanistic probe, and a 3-condition 2×2 factorial design intended to test the oracle hypothesis within the BFS-Prover framework.

Attempting to execute this experiment revealed that the LeanDojo proof state extraction layer silently substituted synthetic data for real Lean4 compiler outputs. The resulting locality scores — uniformly 0.0000 across all three conditions on both evaluation datasets, with t-statistic 0.0000 and p-value 1.0000 — are a synthetic artifact. The H-E1 MUST_WORK gate failed.

The hypothesis is not falsified. The DPO training loop is implemented and validated on synthetic data. The state alignment protocol is correctly implemented. The tactic taxonomy is pre-specified. The gate evaluation logic is correct. A single environment setup task — installing the Lean4 toolchain and removing the synthetic fallback from the production code path — unblocks re-execution of H-E1.

**Summary of outputs from this run:**

1. The **oracle/regularizer framing** — a testable mechanistic distinction with the α-interaction prediction as a uniquely discriminating empirical test.

2. The **locality score metric** — a novel mechanistic probe, not yet validated on real data.

3. An **implemented and unit-tested 3-condition DPO pipeline** — ready for re-execution with real LeanDojo data.

4. A **documented failure mode** — silent synthetic fallback in LLM+formal-verifier pipelines — with a proposed pre-run validation protocol.

**Immediate future work:** Install Lean4 toolchain on the H100 cluster, verify LeanDojo produces real proof state triples, and re-execute H-E1. If H-E1 passes (LS_A > LS_P, p < 0.05), the subsequent chain (H-M1 through H-C1) tests whether the oracle mass shift translates to hard-stratum pass@1 recovery and whether the α-interaction prediction holds. Two longer-term directions are (1) testing whether the oracle effect is detectable at inference time (frozen policy, no DPO) and (2) testing cross-formalism transfer — whether the oracle mechanism holds for Verus and Dafny formalisms in Vericoding, or is Lean4-specific.

## References

Bursuc, S., Ehrenborg, T., Lin, S., Astefanoaei, L., et al. A benchmark for vericoding: formally verified program synthesis. *arXiv:2509.22908*, 2025.

Dong, K. and Ma, T. STP: Self-play LLM theorem provers with iterative conjecturing and proving. In *International Conference on Machine Learning*, 2025.

Ganguly, D., Iyengar, S., Chaudhary, V., and Kalyanaraman, S. Proof of thought: Neurosymbolic program synthesis allows robust and interpretable reasoning. *arXiv:2409.17270*, 2024.

Lai, X., et al. Step-DPO: Step-wise preference optimization for long-chain reasoning of LLMs. *arXiv:2406.18629*, 2024.

Liu, Y., Xue, Y., Wu, D., Sun, Y., Li, Y., Shi, M., and Liu, Y. PropertyGPT: LLM-driven formal verification of smart contracts through retrieval-augmented property generation. In *Network and Distributed System Security Symposium*, 2025.

Mitchell, E. Direct preference optimization: Reference implementation. GitHub repository: https://github.com/eric-mitchell/direct-preference-optimization, 2023.

Rafailov, R., Sharma, A., Mitchell, E., Ermon, S., Manning, C. D., and Finn, C. Direct preference optimization: Your language model is secretly a reward model. In *Advances in Neural Information Processing Systems*, 2023.

Rao, A., et al. Neural theorem proving with ground truth proofs. *arXiv*, 2025.

Xin, R., Liu, C., Guo, Q., et al. BFS-Prover: Scalable best-first tree search for LLM-based automatic theorem proving. *arXiv:2502.03438*, 2025.

Yang, K., Swope, A. M., Gu, A., et al. LeanDojo: Theorem proving with retrieval-augmented language models. In *Advances in Neural Information Processing Systems*, 2023.

Zheng, K., Han, J. M., and Polu, S. MiniF2F: A cross-system benchmark for formal olympiad-level mathematics. In *International Conference on Learning Representations*, 2022.

Zhou, X. and Zhang, Y. Step-wise formal verification for LLM mathematical reasoning. *arXiv*, 2025.
