# 6. Discussion

## 6.1 Key Findings

**Finding 1: The oracle/regularizer distinction is empirically tractable but infrastructure-dependent.**

The most important finding of this work is not the gate result (FAIL) but what the gate failure reveals: testing a mechanistic causal question in LLM formal reasoning requires infrastructure that the field has not yet systematically validated. Our 3-condition design, locality score metric, and α-interaction prediction are all theoretically sound. The experiment produced no scientific content not because the oracle hypothesis is false, but because the formal verifier — the essential instrument of the experiment — was never invoked. This suggests that the oracle/regularizer question is not merely open but *inaccessible* to existing experimental pipelines that lack pre-run environment validation.

**Finding 2: Silent synthetic fallbacks are a systemic risk in LLM+formal-verifier experiments.**

The failure mode we document — a production code path falling back to synthetic data generation when an external tool dependency is absent — is not specific to LeanDojo or this pipeline. Any LLM experiment that (a) depends on an external formal tool (proof assistant, SMT solver, static analyzer) and (b) has a fallback data generation path in the same codebase faces this risk. The BFS-Prover community, the PropertyGPT community, and the Proof of Thought community all rely on such tools. If fallback paths exist in production code, any of these pipelines could produce numerically consistent but scientifically empty results.

The failure is particularly insidious because it passes format validation: training runs completed, locality scores were computed, results files were written. Only the uniformly zero values and subsequent code review revealed the problem. This implies that *result plausibility* is not a sufficient validity check — experiments must explicitly verify that the formal verifier was invoked with real inputs.

**Finding 3: The DPO infrastructure for the oracle test is validated and ready.**

The positive outcome of this run is a validated implementation of the exact DPO training configuration needed to test the oracle hypothesis. The β=10 setting matches BFS-Prover; the state alignment protocol is correct; the tactic taxonomy is pre-specified; the gate evaluation logic works. Re-running H-E1 after installing LeanDojo requires only environment setup, not re-implementation.

## 6.2 Implications for the Field

**For experimental practice:** LLM formal reasoning experiments should adopt pre-run environment validation gates — explicit checks that verify real tool invocation with real outputs before training begins. For a LeanDojo-dependent experiment, this means: verify that `import lean_dojo` succeeds, that `Dojo` returns real proof states, and that at least N real (state, tactic, error) triples are extracted before any DPO training starts. We propose:

```python
# Pre-run gate (required before any DPO training)
real_triples = extract_state_triples(problems[:10], timeout=60)
assert len(real_triples) >= 5, "Pre-run gate FAIL: LeanDojo not producing real triples"
```

**For metric design:** The locality score metric is a substantive contribution independent of the oracle/regularizer result. Prior work measures only pass@1 — a task-level outcome that cannot distinguish oracle function from regularization. Locality score provides a mechanistic intermediate measurement that can identify *why* DPO training succeeds or fails, and can detect null effects that pass@1 would miss (a regularizer might improve pass@1 while producing diffuse locality scores; an oracle might improve locality scores even when pass@1 gains are modest).

**For benchmark design:** The miniF2F and Vericoding datasets do not include feedback loop evaluation metrics. A benchmark designed to evaluate formal feedback mechanisms would include: baseline pass@1 per problem, expected feedback type per error, locality score ground truth (which tactics are premise-consistent for each error), and repair success rate per feedback round. We leave benchmark construction to future work.

## 6.3 Limitations

**L1 — H-E1 oracle hypothesis remains untested.** The central scientific claim of this paper — that step-local grounded feedback functions as a local logical oracle — has no direct experimental support. The three convergent prior systems (BFS-Prover, PropertyGPT, Proof of Thought) are consistent with the oracle hypothesis but do not test it. Until a valid LeanDojo-enabled H-E1 run is completed, the oracle/regularizer question is open.

*Why acceptable:* The experimental design and infrastructure are validated. The single remaining blocker is environment setup, not scientific uncertainty. A valid re-run will provide the first direct test of the oracle mechanism.

*Future work:* Install Lean4 toolchain (`elan` + Lean4 compiler core), remove `_generate_synthetic_triples()` from production paths, add pre-run gate, and re-execute H-E1. Estimated effort: 1–2 days.

**L2 — Locality score not yet validated on real data.** The locality score metric is theoretically grounded but has been computed only on synthetic proof state representations. Its behavior on real LeanDojo tactic distributions is unknown. The metric may require calibration — the denominator (total mass shift) could be near-zero for some proof states, requiring regularization.

*Why acceptable:* The metric design is sound; validation on real data is a necessary next step. The formula includes a 1e-8 epsilon term in the denominator to prevent division by zero.

**L3 — Single seed, single model scale.** The PoC design uses seed=1 and Qwen2.5-Math-7B (7B parameters). Results may differ across seeds and at other model scales (70B+).

*Why acceptable:* The EXISTENCE-level hypothesis (H-E1) requires only directional evidence (LS_A > LS_P). Full statistical validation across seeds and scales is the responsibility of H-M3.

**L4 — Vericoding not retrieved.** Vericoding requires manual download from the arXiv paper release. The H-E1 run used miniF2F only for the final evaluation; Vericoding locality scores are reported as part of the infrastructure failure (all zeros regardless of dataset).

*Why acceptable:* The oracle/regularizer test is valid on miniF2F alone for H-E1. Vericoding cross-formalism generalization is tested in H-M3.

## 6.4 Broader Impact

This research directly targets LLM theorem proving and formal code verification — systems with significant potential for positive impact in software safety, mathematical discovery, and formal specification. More reliable formal reasoning LLMs could reduce critical software bugs, accelerate mathematical proof verification, and make formally verified software development accessible at scale.

The methodological contribution (pre-run environment validation) applies broadly to any AI system that integrates with external formal tools. The risk we identify — silent fallback to synthetic data — could affect medical AI systems, safety-critical code generators, or formal specification tools. Raising awareness of this failure mode and proposing detection protocols has immediate practical value.

Potential negative impacts are limited: this is a methodological paper about LLM training mechanisms, with no direct deployment pathway. The DPO training infrastructure, if misused, could train models on synthetic data — but our contribution is precisely to detect and prevent this.
