# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-25
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Loop (UNATTENDED — independent-controller ablation)
- **Gap ID**: Gap-1
- **Gap Title**: No Unified Comparative Benchmark Across All Major Uncertainty Proxy Types on Standard Factual QA
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 6
- **Previous Failure Context**: h-e2-v2 SUPERSEDED (SE AUROC 0.75 gate failed at Llama-2-7B)

---

## Research Dialogue Context

**Participants**: Dr. Nova (Novelty), Prof. Vera (Falsifiability), Dr. Sage (Significance), Prof. Pax (Feasibility), Dr. Ally (Advocate), Prof. Rex (Critic)

**Total Exchanges**: 6

**Convergence Reason**: All six convergence criteria met at Exchange 6. Mechanism (NLI noise filtering), predictions (P1-P3 with falsification criteria), novelty (first 4-way SE-inclusive comparison at 7B), feasibility (h-e2-v2 reuse), and objections (N=98 gate, TruthfulQA secondary, Chat model) all addressed.

### Key Insights

1. h-e2-v2's AUROC failure at 0.75 is a positive scale-calibration finding, not just a failure — it establishes that SE AUROC at 7B is ~0.54-0.60, not 0.75+ (which is 65B-specific from Kuhn 2023).
2. Three of four methods (TE, SE, SelfCheckGPT) can be computed from existing h-e2-v2 samples at near-zero additional cost, making the four-way comparison immediately feasible.
3. The SelfCheckGPT equivalence prediction (P2) has major practical implications: if SCG ≈ SE AUROC, practitioners can use black-box-compatible SCG on any model without logit access.
4. The correct hypothesis question is not "does SE achieve 0.75 AUROC?" but "does SE's NLI overhead buy anything over cheaper alternatives (TE, SCG) at 7B scale?"

### Breakthrough Moments

- Dr. Sage (Exchange 3): Reframing h-e2-v2 failure as scale-calibration finding shifted the hypothesis from "prove SE works" to "characterize where SE beats alternatives."
- Prof. Pax (Exchange 4): Identifying SCG and TE as computable from existing h-e2-v2 samples made the experiment near-zero-cost.
- Prof. Rex (Exchange 6): Defining the pilot gate (extend if |gap| < 0.03) cleanly resolved the N=98 power concern.

---

## Final Hypothesis

### Title
Four-Way Uncertainty Proxy Comparison at 7B Scale: Does Semantic Entropy's NLI Overhead Buy Meaningful AUROC Gain?

**Hypothesis ID:** H-SE4Way-v1

### Core Claim (Under-If-Then-Because)

Under Llama-2-7B scale on TriviaQA dev (N≥98, extendable to N=500), if all four major uncertainty proxy methods (single-pass token entropy [TE], SelfCheckGPT consistency [SCG], semantic entropy [SE], and verbalized confidence [VC]) are applied under identical experimental conditions (same questions, same K=10 samples, same AUROC metric against binary EM correctness labels), then SE achieves a practically meaningful AUROC advantage over TE (SE-TE gap ≥ 0.05), SelfCheckGPT achieves comparable AUROC to SE (|SCG-SE| ≤ 0.03), and verbalized confidence underperforms both (VC < TE), because semantic-level clustering (SE) and consistency agreement (SelfCheckGPT) both filter paraphrase noise that degrades the discriminative power of token-level entropy, while verbalized confidence requires larger model scale (≥13B) to achieve reliable calibration.

### Mechanism

1. LLM generates K=10 stochastic samples per question. High-uncertainty questions produce semantically diverse outputs; low-uncertainty produce near-identical outputs.
2. Token entropy aggregates over vocabulary distribution at each token position — sensitive to paraphrase variation (same correct answer, different surface form → different token entropy).
3. SE (NLI clustering) and SCG (BERTScore consistency) both operate at semantic level, filtering paraphrase noise → higher discrimination.
4. Verbalized confidence at 7B lacks sufficient self-calibration → near-random AUROC.

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|------------------|---------------|
| **P1 (Primary)** | SE AUROC - TE AUROC ≥ 0.05 | Non-overlapping bootstrap 95% CIs | Gap < 0.03 after N=500 |
| P2 | \|SCG AUROC - SE AUROC\| ≤ 0.03 | Practical equivalence | Gap > 0.05 either direction |
| P3 | VC AUROC < TE AUROC < SE AUROC | VC worst at 7B | VC AUROC ≥ TE AUROC |

---

## Novelty

**Preserved Novelty:** First controlled four-way comparison including semantic entropy alongside TE, SelfCheckGPT, and verbalized confidence on TriviaQA at 7B scale.

**Key Innovation:** Reframes h-e2-v2's AUROC failure as a scale-calibration finding; establishes model-scale-calibrated comparison criterion (relative SE-TE gap ≥ 0.05) instead of absolute threshold (0.75).

**Differentiation:**
- Xiong 2023: omits semantic entropy
- Huang 2023: omits SE and SelfCheckGPT; no 7B/70B comparison
- Kuhn 2023: omits SCG and verbalized confidence; uses 65B model
- Manakul 2023 (SelfCheckGPT): WikiBio benchmark, not TriviaQA; no SE comparison

---

## Experimental Design

**Model:** Llama-2-7B (TE/SE/SCG) + Llama-2-7B-Chat (VC only)

**Dataset:** TriviaQA dev — N=98 pilot (existing h-e2-v2 samples), extension to N=500 if |SE-TE| < 0.03

**Secondary:** TruthfulQA (N=100) for cross-benchmark validation

**Compute plan:**
- TE from existing samples: ~free (log-prob extraction or 1 greedy-decode pass)
- SCG from existing K=10 samples: ~7 minutes CPU (BERTScore pairwise)
- SE from existing h-e2-v2 code: already done (AUROC = 0.5419 anchor)
- VC new inference: < 1 GPU hour on Llama-2-7B-Chat
- Extension to N=500: ~33 GPU hours (generate_shard.py) — gated on pilot result

---

## Limitations

- N=98 bootstrap CIs (~±0.05) are marginal for detecting gaps near 0.05 — pilot gate mandatory
- TriviaQA is trivia-domain only — TruthfulQA secondary required for generalization claim
- Verbalized confidence is Chat-model-specific; base model results not reported
- SE computation reuses h-e2-v2 NLI model — same model dependency applies
- Scale extension (13B, 70B) out of scope for this hypothesis — deferred to Phase 5

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Hypothesis ID** | H-SE4Way-v1 |
| **Convergence** | Exchange 6 — all criteria met |
| **Clarity Verified** | Yes |
| **Prior Failure Avoided** | Yes — no 0.75 gate; relative comparison used |
| **Key Remaining Action** | Enforce pilot gate at N=98; add TruthfulQA secondary |

---

*Phase 2A Complete — Ready for Phase 2B*
