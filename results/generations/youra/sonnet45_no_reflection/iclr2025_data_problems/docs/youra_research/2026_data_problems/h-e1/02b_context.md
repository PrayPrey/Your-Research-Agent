# Hypothesis Context: h-e1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-05-11
**Main Hypothesis:** H-ContamGeometry-v1
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under finetuning conditions with 1-5% EAL-style paraphrased benchmark injection, if we apply the three-tier detection architecture (data-layer filters, TSG probes, geometric trajectory auditing), then we achieve ≥80% combined detection power at <5% false positive rate, because contamination-induced gains necessarily produce detectable multi-layer signatures across at least one tier.

### Type
EXISTENCE

### Rationale
This hypothesis validates that the proposed detection system achieves the target performance envelope. It tests the core claim that contamination cannot evade all three tiers simultaneously when producing meaningful benchmark gains. Success demonstrates practical viability; failure indicates fundamental architecture flaws.

---

## Verification Protocol

### Conceptual Test
1. Replicate EAL protocol: train N=20 runs each for clean baseline, 1% injection, 5% injection
2. Apply all three detection tiers independently to each run
3. Compute combined detection power (OR logic: detected by ANY tier) and FPR on clean runs
4. Statistical test: combined power ≥80% at α=0.05 significance level
5. Disaggregate results by tier to identify which tiers contribute most to detection

### Success Criteria
- **Primary:** Combined detection power ≥80% for 5% injection @ <5% FPR
- **Secondary:** At least 2 of 3 tiers show >0% detection power (complementary architecture validated)

### Variables
- **Independent Variables:** Contamination Rate (0%, 1%, 5%), Contamination Type (accidental vs adversarial)
- **Dependent Variables:** Combined Detection Power, False Positive Rate
- **Controlled Variables:** Base Model (Llama-2-7B/Mistral-7B), Hyperparameters (lr=2e-5, batch=64, epochs≤3)

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** GSM8K + Math Reasoning Datasets
- **Type:** standard
- **Source:** HuggingFace datasets, official benchmark repositories
- **Path:** Standard splits (GSM8K test set as contamination target, background math datasets for clean training)
- **Hypothesis Fit:** Target benchmark for contamination (GSM8K) + clean background training data (MATH, other math datasets) enables controlled EAL-protocol replication

### Selected Model
- **Name:** Llama-2-7B or Mistral-7B
- **Type:** Decoder-only transformer (7B parameters)
- **Source:** HuggingFace model hub (meta-llama/Llama-2-7b-hf or mistralai/Mistral-7B-v0.1)
- **Hypothesis Fit:** 7B scale enables controlled experiments with N=20 runs, gradient/Hessian computation feasible, matches EAL paper experimental setup

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods

| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|------------------|
| Membership Inference Attacks (MIA) | AUC≈50% pretraining, up to 99.4% finetuning | Pythia, OLMO-2 models | Fails under paraphrasing; detects memorization, not task learning |
| Semantic Similarity / Text Matching | TPR<2% @ 1%FPR against EAL | EAL-contaminated models | Evaded by GPT-4-level rephrasing while task knowledge preserved |
| LiveCodeBench (Continuous Fresh Benchmarks) | 100% contamination prevention | HumanEval-style code problems | Requires constant benchmark creation, fragments evaluation landscape |

### Baseline Performance
- MIA: AUC≈50% (random) in pretraining, TPR<2% against EAL paraphrasing
- Semantic Similarity: TPR<2% @ 1%FPR against EAL

### Gap Analysis
Instance-level detection methods (MIA, semantic matching) achieve near-random performance (AUC≈50%, TPR<2%) under EAL-style paraphrasing. The proposed multi-tier geometric detection approach aims to overcome this fundamental limitation by detecting learning-trajectory signatures rather than instance similarity.

---

## Dependencies and Gate Conditions

### Prerequisites
None (foundation hypothesis)

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** PIVOT to single-tier optimization or ABANDON multi-tier approach

**Phase Assignment:** Phase 1 - Foundation Establishment (Week 1-2)

**Estimated Duration:** 2 weeks

---

## Dependency Context

### Relationship to Other Hypotheses
Foundation hypothesis for the entire verification plan. Blocks all other hypotheses (H-M1, H-M2, H-M3, H-M4) until validated. If H-E1 fails, the entire hypothesis is invalid and should be abandoned.

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** IN_PROGRESS
**Workflow Status:** ACTIVE

---

## Phase 2C Usage Notes

**This context file provides:**
1. Complete hypothesis specification for experiment design
2. Gate conditions for prerequisite validation
3. Dependency information for controlled experiments
4. Success criteria for evaluation design
5. **Baseline comparison targets (CRITICAL for H-CP* hypotheses)**

**Phase 2C will:**
1. Load this file instead of full Phase 2B roadmap (91% smaller)
2. Search for implementation patterns (Archon, Exa MCP)
3. Use baseline metrics to set comparison targets
4. Design concrete experiment specification (Level 1.5)
5. Output: h-e1/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes
- **H-M* (Mechanism)**: Baseline to understand improvement potential
- **H-C* (Condition)**: Baseline to identify scope boundaries
- **H-CP* (Comparison)**: **MANDATORY** - Direct comparison with baseline methods

---

*Generated by Phase 2C Workflow (JIT)*
*Optimized for single-hypothesis experiment design*
