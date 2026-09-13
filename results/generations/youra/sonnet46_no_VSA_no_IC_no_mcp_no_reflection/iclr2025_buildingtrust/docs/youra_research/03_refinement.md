# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-31T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop (Independent-Controller Ablation)
- **Gap ID**: gap-1
- **Gap Title**: No Systematic Cross-Alignment Trustworthiness Comparison on Unified Benchmark Suite
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 11

---

## Research Dialogue Context

**Participants**: Dr. Nova (Creative Novelty Explorer), Prof. Vera (Rigorous Validation Architect), Dr. Sage (Research Impact Evaluator), Prof. Pax (Feasibility & Reality Checker), Dr. Ally (Hypothesis Strengthening Champion), Prof. Rex (Hypothesis Stress-Test Master)

**Total Exchanges**: 11

**Convergence Reason**: All 6 convergence criteria satisfied (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS) after full persona round-trip with self-play

### Key Insights
1. **Detection over explanation**: Framing alignment fingerprinting as a classification problem (can you identify alignment strategy from benchmark scores?) is cleaner than mechanistic explanation — directly falsifiable and practically useful.
2. **Small-n is the core challenge**: With ~6-10 model pairs, standard t-tests are underpowered. Permutation test + binomial sign test are the appropriate statistical framework.
3. **Alignment-handbook is the gold standard**: The DPO/SFT pairs from `HuggingFaceH4/zephyr-7b-*` give the cleanest available controlled comparison. 3-way RLHF comparison is too confounded to include as a primary condition.
4. **Both results are informative**: A null result (fingerprint absent) is as publishable as a positive result — it means standard benchmarks cannot detect alignment strategy, which is itself important knowledge.

### Breakthrough Moments
- **Exchange 4 (Prof. Pax)**: Identifying the controlled-pair scarcity problem — pivoting from 3-way to 2-way comparison is the critical feasibility fix.
- **Exchange 7 (Dr. Nova)**: Detection problem reframe — classification accuracy as the primary outcome resolves the mechanism-verification problem.
- **Exchange 8 (Prof. Vera)**: Specifying permutation test + sign test — gives the study real statistical validity with small n.

---

## Final Hypothesis

### Title
Alignment Fingerprinting: DPO vs SFT Produces Detectable Trustworthiness Profile Shift in Standard Benchmark Space

### Hypothesis ID
H-AlignFingerprint-v1

### Core Claim (Under-If-Then-Because)
Under inference-only evaluation of 7B-parameter language models fine-tuned on the same base model with matched data using DPO vs SFT alignment strategies, if we evaluate models on a 4-benchmark trustworthiness suite (TruthfulQA MC2, BBQ, WinoGrande, WinoGender), then DPO-aligned models will exhibit a systematically different trustworthiness profile from SFT-aligned models — specifically higher fairness scores (BBQ, WinoGender) and neutral-to-lower truthfulness scores (TruthfulQA MC2) — and this profile difference will be detectable by a k-NN classifier with leave-one-out cross-validation (≥67% accuracy, permutation p≤0.05 across ≥6 matched model pairs), because DPO preference optimization rewards annotator-preferred responses that avoid bias-triggering patterns without explicitly rewarding factual accuracy.

### Mechanism (Candidate Explanation)
1. DPO learns from human preference pairs where annotators favor bias-avoidance responses → elevated BBQ/WinoGender scores
2. DPO does not explicitly reward factual accuracy (unlike RLHF with explicit truthfulness signal) → neutral-to-lower TruthfulQA scores
3. The combined profile shape constitutes a detectable fingerprint in 4D benchmark space

**Note:** The mechanism is a *candidate explanation*, not a verified causal claim. The primary experimental test is empirical detection (is the fingerprint present?), not mechanistic verification.

---

## Predictions

| ID | Statement | Test Method | Success Criterion | Falsification |
|----|-----------|-------------|-------------------|---------------|
| **P1** *(primary)* | k-NN LOO accuracy ≥67% over ≥6 matched pairs, permutation p≤0.05 | sklearn k-NN (k=1) LOO CV + permutation_test_score (1000 permutations) | Accuracy ≥0.67 AND p≤0.05 | Accuracy <0.50 = fingerprint absent |
| **P2** | TruthfulQA MC2 is most discriminative dimension | Fisher's criterion per benchmark, rank comparison | TruthfulQA ranks 1st | Another benchmark ranks 1st |
| **P3** | BBQ DPO ≥ SFT in ≥4/6 pairs | Directional count + one-sided binomial sign test (n=6) | ≥4/6 pairs DPO>SFT, p≤0.125 | ≤3/6 pairs DPO>SFT |

---

## Novelty

**What's new:** First study using alignment strategy as IV + unified trustworthiness benchmark suite as DV + classification/fingerprinting framing. Methodologically agnostic (detection without explanation). Enables model auditing without training data access.

**Prior work differentiation:**
- DecodingTrust: evaluates trust dimensions but no alignment strategy IV
- InstructGPT: RLHF vs SFT on TruthfulQA only — no DPO, no unified suite, no fingerprinting
- DPO paper: capability benchmarks only, no trustworthiness evaluation
- HELM: multi-benchmark correlation analysis for capability, not alignment detection

---

## Experimental Design

**Primary model pair:** `HuggingFaceH4/zephyr-7b-sft-full` vs `HuggingFaceH4/zephyr-7b-dpo-full` (alignment-handbook, gold standard controlled comparison)

**Additional pairs:** Community 7B DPO/SFT pairs with documented alignment methods (target: ≥6 total)

**Benchmarks:**
- TruthfulQA MC2: `lm_eval --tasks truthfulqa_mc2`
- BBQ: `lm_eval --tasks bbq`
- WinoGrande: `lm_eval --tasks winogrande` (robustness proxy)
- WinoGender: manual setup or `winograd_wsc` proxy

**Compute:** ~32 GPU hours on A100 (8 models × 4 hours per model for all tasks)

**Baselines:** 50% random classifier; majority-class classifier; single-benchmark k-NN (TruthfulQA only)

---

## Limitations

- Small model count (n≈6-10 pairs) — pilot/confirmatory scale, not population-level definitive
- Mechanism cannot be verified without training data access
- WinoGender small size and binary gender framing — treated as exploratory secondary dimension
- Community DPO models have partially uncontrolled data differences — disclosed in limitations
- 3-way RLHF comparison excluded due to controlled-pair scarcity (future work)

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria satisfied after 11 exchanges |
| **Clarity Verified** | Yes |
| **Feasibility Constraints Satisfied** | Yes — no new benchmarks, no synthetic data, no human eval |
| **Remaining Objections** | Minor (model curation, WinoGender size, community confounds) — mitigated |

---

*Phase 2A complete. Ready for Phase 2B planning.*
