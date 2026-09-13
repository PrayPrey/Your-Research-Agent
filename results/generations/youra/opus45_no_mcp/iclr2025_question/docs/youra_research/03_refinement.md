# Phase 2A: Refinement Summary

## Metadata

- **Generated at**: 2026-08-19
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop
- **Gap ID**: Gap-1
- **Gap Title**: Optimal Combination of Token Entropy and Semantic Consistency
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 10

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 10

**Convergence Reason**: All six convergence criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS)

### Key Insights

- Token entropy and semantic consistency probe different LLM failure modes: entropy captures internal model uncertainty (doesn't "know" the answer), while consistency captures output stability (can't reliably generate the answer)
- Both methods already require multi-sampling, so combination adds no computational overhead
- Quadrant-based analysis (2x2 split on entropy/consistency) provides interpretable structure for understanding when each signal matters

### Breakthrough Moments

- Dr. Nova's reframing: signals are redundant on easy questions but complementary on hard questions where the real value lies
- Prof. Vera's operationalization: quadrant classification as a cleaner alternative to regression with interaction terms

---

## Final Hypothesis

### Title

Complementary Entropy-Consistency Hallucination Detection

### Hypothesis ID

H-EntropyConsistency-v1

### Core Claim

Under QA task conditions with pretrained instruction-tuned LLMs, if we combine token-level entropy and semantic consistency into a single hallucination prediction score, then prediction accuracy (AUROC) improves by ≥2 percentage points over the best single metric, because entropy and consistency capture complementary failure modes (internal confusion vs. output instability).

### Mechanism

1. **Token Entropy**: Compute entropy from token logit distributions — high entropy means flat probability distribution, indicating the model is "uncertain"
2. **Semantic Consistency**: Generate N samples, compute pairwise semantic similarity — low consistency means the model produces different answers, indicating "instability"
3. **Combination**: Linear fusion (α·inverse_entropy + β·consistency) or quadrant classification
4. **Evaluation**: Compare combined score's ability to predict correctness against single metrics

---

## Predictions

| ID | Primary | Statement | Success Criterion |
|----|---------|-----------|-------------------|
| P1 | Yes | Combined metric achieves ≥2pp AUROC improvement on TriviaQA | Δ AUROC ≥ 0.02 or ceiling (>0.97) |
| P2 | No | ECE improves by ≥0.02 | Δ ECE ≥ 0.02 (lower is better) |
| P3 | No | Results hold on NQ and TruthfulQA | Consistent improvement on 3 datasets |
| P4 | No | Quadrant analysis shows distinct patterns | Q1 (low entropy + high consistency) highest accuracy |

---

## Novelty

**Key Innovation**: First systematic combination of token entropy and semantic consistency on standard QA benchmarks.

**Differentiation**:
- vs. Kuhn et al. (Semantic Entropy): They use clustering + entropy; we add consistency
- vs. Manakul et al. (SelfCheckGPT): They use consistency only; we add entropy
- vs. Xiong et al. (Verbalized Confidence): They use self-report; we use token-level signals

**Novel Framing**: "Complementary failure modes" — entropy captures internal confusion, consistency captures output instability.

---

## Experimental Design

**Primary Dataset**: TriviaQA (~95K QA pairs with ground-truth answers)

**Robustness Datasets**: Natural Questions (~300K), TruthfulQA (designed to elicit failures)

**Model**: Llama-2-7B-chat (instruction-tuned, HuggingFace, logit access)

**Baselines**:
- Token entropy alone
- Semantic consistency alone (SelfCheckGPT)
- Verbalized confidence

**Protocol**:
1. Generate 10 samples per question at temperature 0.7
2. Compute entropy from logits, consistency from embedding similarity
3. Compare: single metrics vs. linear fusion vs. quadrant classification
4. Evaluate AUROC, ECE, quadrant accuracies

---

## Limitations

- **Model Scope**: Tested on Llama-2-7B-chat only; may not generalize to larger models or API-only models (no logit access)
- **Task Scope**: QA with ground-truth; does not apply to open-ended generation
- **Computational**: Requires 10 samples per question (already required by both baseline methods)

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 personas agreed after 10 exchanges |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None (ceiling effects and model scope addressed) |

---

## Phase 2B Readiness

| Sub-Hypothesis | Description |
|----------------|-------------|
| **SH1 (Existence)** | Entropy and consistency can be computed for any question |
| **SH2 (Mechanism)** | Combined score is more predictive than single scores |
| **SH3 (Comparison)** | Deferred to Phase 5 (vs. ensemble methods) |

---

*Phase 2A Complete | Ready for Phase 2B Hypothesis Verification Planning*
