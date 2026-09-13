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

All locality scores are identically 0.0000. The one-sided t-test yields p=1.0, providing no evidence that LS_A > LS_P. The H-E1 MUST_WORK gate fails.

**Key observation:** The null result is not a scientific finding about the oracle mechanism. It is a synthetic artifact.

Figure 1 shows the locality score comparison across conditions and datasets. The uniformly zero bars visually confirm the null result, but the interpretation requires the infrastructure diagnosis in Section 5.2.

*[Figure 1: locality_score_comparison.png — Bar chart of LS_A, LS_B, LS_P on miniF2F and Vericoding hard subsets. All 6 bars are 0.0.]*

Figure 2 shows the post-DPO probability mass distribution across tactic categories per condition. The uniform distribution across categories is consistent with a DPO model trained on synthetic (randomly generated) proof state triples rather than real Lean4 compiler outputs.

*[Figure 2: probability_mass_distribution.png — Stacked bar of tactic category mass shift (Δ = P_post - P_pre) per condition and dataset.]*

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

**What was validated (valid outputs):**
- DPO training loop implementation (β=10, lr schedule, concatenated forward pass, `average_log_prob=False`) matches the eric-mitchell/DPO reference implementation.
- State alignment protocol (100% state_id matching in pair builder) is correctly implemented for the synthetic data.
- Tactic taxonomy pre-specification (type_error, undefined_name, tactic_failure) was established before any training.
- Gate evaluation and validation report generation function correctly.

**What was not validated:**
- Real LeanDojo proof state extraction from actual Lean4 proofs.
- Real Lean4 compiler error messages as DPO negatives.
- Locality score computation on real probability distributions over tactic tokens.

Figure 3 shows locality scores broken down by LeanDojo error category. The uniform zero across all categories (type_error, undefined_name, tactic_failure) is consistent with synthetic data — real Lean4 runs would be expected to produce category-specific mass shifts.

*[Figure 3: error_category_breakdown.png — LS per error category per condition. All values 0.0.]*

Figure 4 shows locality score per proof state across hard subset instances. The uniformly zero scatter confirms that the null result is system-wide, not concentrated in specific proof states.

*[Figure 4: locality_score_per_state.png — Scatter: x=proof state index, y=LS. All points at 0.0.]*

## 5.3 Post-Hoc Mock Detection

An external LLM verification pass (applied after the Phase 4 run) identified the synthetic substitution by analyzing `leandojo_tracing.py`. The detection correctly localized the fallback at lines 50-51, 62-64, and 114-137, and confirmed that no real LeanDojo invocations occurred during the experiment. This demonstrates that automated post-run validity checking of experimental pipelines is feasible and informative.

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

The DPO training infrastructure is validated and ready for re-execution once LeanDojo is properly installed.

## 5.5 Convergent Evidence from Prior Systems

While H-E1 produces no direct evidence on the oracle hypothesis, three independent prior systems provide convergent evidence in the oracle direction:

| System | Result | Mechanism implied |
|--------|--------|------------------|
| BFS-Prover [Xin et al., 2025] | 72.95% miniF2F with Lean4 DPO | Step-local grounded → performance improvement |
| PropertyGPT [Liu et al., 2024] | 87% vs. 63% compilation success | Step-level structured feedback → inference improvement |
| Proof of Thought [Ganguly et al., 2024] | 14.6% → 0% compilation errors | Structured Z3 feedback → error elimination |

None of these systems isolates oracle from regularizer. The convergent direction is consistent with the oracle hypothesis but does not confirm it. A valid H-E1 run is required to provide the first direct mechanistic evidence.
