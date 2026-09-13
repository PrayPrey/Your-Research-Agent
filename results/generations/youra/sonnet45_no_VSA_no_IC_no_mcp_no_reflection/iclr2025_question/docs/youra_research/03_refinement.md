# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-28T09:30:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop (Independent Controller Ablation)
- **Gap ID**: Gap1
- **Gap Title**: Scalable Uncertainty Estimation Without Retraining
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 16

---

## Research Dialogue Context

**Participants**: Dr. Nova (Creative Novelty Explorer), Prof. Vera (Rigorous Validation Architect), Dr. Sage (Research Impact Evaluator), Prof. Pax (Feasibility & Reality Checker), Dr. Ally (Hypothesis Strengthening Champion), Prof. Rex (Hypothesis Stress-Test Master)

**Total Exchanges**: 16

**Convergence Reason**: All six personas reached consensus on hypothesis clarity, testability, feasibility, and scope. Mechanism is plausible with direct validation path (P3: top-5 entropy check). Predictions are falsifiable with existing benchmarks (TriviaQA, SQuAD, Natural Questions). Computational cost is minimal (6 GPU-hours).

### Key Insights

1. **Entropy captures multi-modal uncertainty** that max-probability (mode-only signal) misses
2. **Disagreement cases** (high max-prob, high entropy) are the critical test frontier where entropy's value is demonstrated
3. **Quadrant analysis framework** is a methodological contribution beyond just the entropy metric itself
4. **Single-pass, zero-shot uncertainty** is practical for deployment scenarios (no calibration data required)

### Breakthrough Moments

- **Exchange 4-5**: Paradigm shift from "entropy vs max-prob" competition to "disagreement quadrant analysis" framework
- **Exchange 7**: Reframing max-prob correlation as a feature, not a bug - correlation structure defines the test quadrants
- **Exchange 10**: Mechanism explanation crystallized via multi-modal distributions, with direct validation path (P3: top-5 flatness)

---

## Final Hypothesis

### Title
Single-Pass Distribution Entropy for Selective Prediction in Autoregressive Language Models

### Hypothesis ID
H-EntropySelectivePrediction-v1

### Core Claim

**Under-If-Then-Because Statement**:

Under factual question-answering tasks with single-answer targets, if we apply entropy-based rejection thresholds to frozen LLM predictions, then selective prediction accuracy will exceed max-probability-based rejection, because entropy captures multi-modal distribution uncertainty that max-probability (mode-only) misses.

### Mechanism

When large language models generate text, the output token distribution encodes uncertainty through its shape and spread across multiple plausible tokens:

1. **Distribution shape encodes uncertainty**: Peaked distributions indicate confidence; flat distributions indicate uncertainty
2. **Max-probability limitation**: Captures only the mode (highest peak), missing multi-modal cases where multiple answers have similar probabilities
3. **Entropy advantage**: Captures full distribution geometry, detecting cases with high max-prob but also high entropy (multiple competitive peaks)
4. **Selective prediction**: By rejecting high-entropy predictions, we identify uncertain outputs that max-prob thresholding misses

**Key Mechanism Insight**: The disagreement quadrant (Q3: high max-prob, high entropy) contains predictions where max-prob says "confident" but entropy says "uncertain." Hypothesis predicts these cases have lower accuracy, validating entropy's added value.

---

## Predictions

### P1 (Primary): Quadrant Gap Analysis

**Statement**: On TriviaQA, accuracy in the disagreement quadrant Q3 (high max-prob, high entropy) is more than 5 percentage points lower than the agreement quadrant Q1 (high max-prob, low entropy) with statistical significance (p < 0.017).

**Test Method**: 
- Median split on entropy and max-prob to create four quadrants
- Measure exact match accuracy in each quadrant
- Paired t-test comparing Q1 vs Q3

**Success Criterion**: 
- Q1 accuracy - Q3 accuracy > 5% (practical significance)
- p-value < 0.017 (Bonferroni-corrected for 3 predictions)

**Falsification**: If Q3 accuracy ≥ Q1 accuracy, OR p ≥ 0.017, OR gap ≤ 5%, entropy does not detect hidden uncertainty that max-prob misses.

---

### P2: Coverage-Accuracy AUC

**Statement**: Coverage-accuracy AUC for entropy-based rejection exceeds max-probability-based rejection on TriviaQA, SQuAD, and Natural Questions.

**Test Method**:
- Sweep rejection thresholds to vary coverage from 0% to 100%
- Plot accuracy vs coverage curves for each method
- Compute area under curve (AUC) for each method on each dataset

**Success Criterion**: AUC(entropy) > AUC(max-prob) on all three datasets

**Falsification**: If AUC(max-prob) ≥ AUC(entropy) on any dataset, max-prob is sufficient for that domain.

---

### P3: Mechanism Validation (Multi-Modal Distributions)

**Statement**: The disagreement quadrant Q3 exhibits significantly higher top-5 token distribution entropy than the agreement quadrant Q1 with p < 0.017.

**Test Method**:
- Extract top-5 token probabilities for each prediction
- Compute entropy over top-5 distribution
- Compare Q3 vs Q1 using t-test

**Success Criterion**: 
- Top-5 entropy(Q3) > Top-5 entropy(Q1)
- p-value < 0.017

**Falsification**: If top-5 entropy(Q3) ≤ top-5 entropy(Q1) OR p ≥ 0.017, the multi-modal mechanism explanation is incorrect.

---

## Novelty

### What's New

1. **Quadrant analysis framework** for entropy-maxprob disagreement in selective prediction
2. **First systematic study** of distribution entropy for LLM selective prediction (vs max-prob baselines)
3. **Zero-shot uncertainty** without calibration sets or held-out data
4. **Single-pass efficiency** (no ensembles, no multiple forward passes)

### Differentiation from Prior Work

**vs Max-probability baselines** (Hendrycks et al. OOD detection):
- Max-prob only captures mode; entropy captures full distribution shape including multi-modality

**vs Ensemble methods** (Lakshminarayanan et al.):
- Single forward pass vs multiple models; zero-shot vs training required

**vs Temperature scaling / calibration** (Guo et al.):
- No calibration set required; entropy from raw distribution vs post-hoc rescaling

**vs Conformal prediction**:
- No held-out calibration data; applicable to frozen API models with logprobs access

---

## Experimental Design

### Datasets
- **TriviaQA**: ~80k factual questions (primary evaluation)
- **SQuAD**: ~100k reading comprehension questions
- **Natural Questions**: ~300k open-domain QA

All are existing benchmarks with single-answer targets and exact match evaluation.

### Models
- **Llama-7B**: Small scale baseline
- **Llama-13B**: Medium scale (primary)
- **Llama-70B**: Large scale generalization test

All are open models with accessible logprobs, frozen (no retraining).

### Baselines
1. **Max-probability thresholding**: Reject predictions below threshold on max(P)
2. **Random rejection**: Uniform random rejection (sanity check)

### Evaluation Metrics
- **Primary**: Coverage-accuracy curves (accuracy vs % retained predictions)
- **Quadrant analysis**: Accuracy per quadrant (Q1, Q2, Q3, Q4)
- **AUC**: Area under coverage-accuracy curve (overall metric)
- **Top-5 entropy**: Mechanism validation

### Computational Cost
- **Per example**: Single forward pass + softmax + entropy computation (~0.1ms overhead)
- **Total**: ~6 GPU-hours for 3 datasets × 3 models
- **Hardware**: 1× A100 GPU (or equivalent with ~40GB VRAM)

---

## Scope & Limitations

### Applies To
- Factual question-answering tasks with single-answer targets
- Autoregressive language models with accessible logprobs
- Closed-set evaluation (exact match metrics)

### Does NOT Apply To
- Open-ended text generation (no ground truth for accuracy)
- Multi-answer questions or ambiguous queries
- Multi-hop reasoning tasks (not tested)
- Chain-of-thought or reasoning-heavy tasks (not tested)

### Known Limitations
- Scope restricted to three factual QA benchmarks (generalization to other domains unknown)
- Tested only on Llama family (architectural generalization unknown)
- Does not address calibration (only selective prediction / rejection)
- Threshold selection requires coverage target (not fully automatic)

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All six personas converged after 16 exchanges |
| **Clarity Verified** | Yes - mechanism, predictions, and scope clearly stated |
| **Remaining Objections** | None |
| **Falsifiability** | Strong - all predictions have clear nulls and statistical tests |
| **Feasibility** | Strong - 6 GPU-hours, existing benchmarks, standard libraries |
| **Novelty** | Strong - quadrant framework, first systematic entropy study for LLM selective prediction |
| **Significance** | Moderate - workshop/findings level, practical value, useful baseline |

---

## Phase 2B Readiness

**Status**: READY

**Sub-Hypotheses for Phase 2B**:
- **SH1 (Existence)**: Token probability distributions must be accessible (logprobs API or model internals)
- **SH2 (Mechanism)**: Entropy captures multi-modal uncertainty; max-prob captures mode only (validate via P3)
- **SH3 (Comparison)**: Entropy-based rejection vs max-prob-based rejection on coverage-accuracy performance (validate via P1, P2)

**Open Questions for Future Work**:
- Does entropy generalize to reasoning tasks beyond factual QA?
- Can we decompose entropy into top-k vs tail components for finer-grained signals?
- What is the optimal entropy variant (Shannon, top-k, normalized) across domains?

---

*End of Phase 2A Refinement Summary*
