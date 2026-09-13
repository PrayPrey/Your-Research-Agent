# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md (Round 1 - FEASIBLE)
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-ESRC-001
**Confidence Level:** 0.78

**Main Hypothesis:**
Under standard Long CoT reasoning conditions, if delta-entropy (rate of entropy change in answer token distribution) falls below a calibrated threshold for N consecutive steps, then reasoning has reached saturation and halting with self-consistency verification will maintain ≥97% relative accuracy while reducing compute by 30-50%, because entropy stabilization indicates diminishing information gain per reasoning step according to optimal stopping theory.

**Alternative Hypothesis (H0):**
Entropy dynamics during Long CoT reasoning do not provide a reliable signal for reasoning saturation; halting based on delta-entropy stabilization will either (a) cause significant accuracy degradation (>5%), (b) fail to achieve meaningful compute reduction (<15%), or (c) not generalize across task domains.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Delta-entropy threshold (τ) | Independent | Compute H(t) = -Σ p(x)log p(x) of answer token distribution at step t; calculate \|H(t) - H(t-1)\|; calibrate τ on validation set | τ ∈ [0.01, 0.10] nats |
| Consecutive stabilization steps (N) | Independent | Count of consecutive steps where \|delta-entropy\| < τ | N ∈ {2, 3, 4} |
| Task accuracy | Dependent | Exact match accuracy on reasoning benchmarks (GSM8K, MATH, HotpotQA) | 85-95% absolute, ≥97% relative to full CoT |
| Compute cost reduction | Dependent | (Full CoT tokens - ESRC tokens) / Full CoT tokens × 100% | Target: 30-50% reduction |
| Base LLM architecture | Controlled | Fixed reasoning model (DeepSeek-R1, Qwen-QwQ, o1-mini) | No architecture modifications |
| Reasoning format | Controlled | Standard Chain-of-Thought prompting with <think> tags | Consistent across conditions |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
[Reasoning Progress] → [Entropy Dynamics] → [Stabilization Signal] → [Efficient Halt with Accuracy]
     Step 1                  Step 2                Step 3                  Outcome
```

**Step 1: Reasoning Progress → Entropy Dynamics**
As the model reasons through a problem, entropy of answer tokens changes reflecting evolving certainty.

**Step 2: Entropy Dynamics → Stabilization Signal**
When delta-entropy approaches zero for consecutive steps, additional reasoning provides diminishing information gain (optimal stopping).

**Step 3: Stabilization Signal → Efficient Halt with Accuracy**
Halting at stabilization with 2-sample self-consistency check maintains accuracy while reducing tokens.

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | DiffAdapt (2025) | 22-25% entropy reduction from easy to medium difficulty | Strong |
| Step 1 → Step 2 | Think Just Enough (2025) | Entropy-based confidence emergent in reasoning models | Strong |
| Step 2 → Step 3 | Optimal Stopping Theory | Stop when expected information gain < cost | Strong |
| Step 3 → Outcome | Self-Consistency (2022) | +17.9% improvement on GSM8K via sampling verification | Strong |

**Key Tension:**
- **Tension:** DiffAdapt shows U-shaped entropy (high-low-high), Think Just Enough assumes monotonic
- **Resolution:** ESRC uses STABILIZATION (rate approaching zero) which works regardless of U-shape

### 1.4 Key Assumptions

| Assumption | Evidence | Consequence if Violated |
|------------|----------|------------------------|
| A1: Entropy reflects reasoning progress | DiffAdapt, Think Just Enough | Method fails; need alternative signal |
| A2: Stabilization = saturation | Optimal stopping theory | Wrong halt points; accuracy loss or no efficiency |
| A3: Self-consistency catches errors | +17.9% on GSM8K | Accuracy degradation |
| A4: Single threshold transfers | Think Just Enough: 5-10 samples | Per-task calibration needed |

### 1.5 Scope & Boundaries

**Applies to:** Long CoT reasoning (math, QA, code); post-trained models with logprobs; inference-time
**Does NOT apply to:** Single-turn generation; tool-calling tasks; models without logprobs
**Limitations:** Requires calibration (5-10 samples); ~2x overhead at halt points; may need domain tuning

### 1.6 Testable Predictions

**Primary Prediction:**
**P1:** ESRC achieves token reduction ≥30% while maintaining ≥97% relative accuracy on GSM8K/MATH.
- Measurement: Paired t-test, n ≥ 500 problems, p < 0.05
- Falsification: Token reduction <15% OR Accuracy <92%

**Secondary Predictions:**
**P2:** Entropy stabilization occurs in ≥80% of reasoning traces before natural stopping
**P3:** Threshold calibrated on GSM8K transfers to MATH/HotpotQA with <5% accuracy drop

**Falsification Criteria:**
1. Primary: Token reduction <15% OR Accuracy retention <92%
2. Mechanism: Stabilization absent in >50% of traces
3. Comparative: Pareto-dominated by DiffAdapt AND TALE

### 1.7 SOTA Baseline

| Method | Token Reduction | Accuracy Impact | Approach |
|--------|----------------|-----------------|----------|
| DiffAdapt | 22.4% | Comparable | Difficulty classification |
| TALE | 67% | <3% decrease | Budget prompting |
| Think Just Enough | 25-50% | Maintained | Absolute entropy |

**ESRC Target:** 30-40% reduction with theoretical grounding + interpretability

### 1.8 Statistical Verification Design

- Sample: n ≥ 500 per benchmark
- Test: Paired t-test (same problems, same seeds), α = 0.05
- Report: Mean ± Std Dev, 95% CI, Cohen's d, Pareto frontier

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does entropy stabilization consistently occur during Long CoT reasoning across task types and model families?"
- Dependency: None (run first)
- Critical: MUST PASS

**SH2 (Mechanism):**
"Is the 3-step causal mechanism the actual cause of efficiency-accuracy trade-off?"
- H-M1: Reasoning → entropy dynamics
- H-M2: Stabilization → saturation signal
- H-M3: Halt + self-consistency → accuracy preservation
- Dependency: SH1

**SH3 (Comparison):**
"Does ESRC match/outperform DiffAdapt and TALE on Pareto frontier?"
- Dependency: SH1, SH2

**Total:** 5 sub-hypotheses (1 + 3 + 1)

### Readiness Checklist

- [x] Hypothesis in scientific format with H0
- [x] Hypothesis ID: H-ESRC-001, Confidence: 0.78
- [x] 6 variables operationalized
- [x] N=3 causal steps with evidence
- [x] 4 assumptions with consequences
- [x] 3 predictions (P1 primary)
- [x] Falsification criteria quantified
- [x] Baselines: Full CoT, DiffAdapt, TALE
- [x] SOTA benchmarks collected

### Open Questions

1. **Model Access:** Which models expose logprobs? (DeepSeek-R1, Qwen-QwQ, o1?)
2. **Calibration:** Minimal validation set size? (5-10 samples per prior work)
3. **Resources:** GPU/API budget for GSM8K/MATH/HotpotQA experiments?
4. **Priority:** SH1 first, or parallel validation?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work (9 sources with citations)

---

*Generated using YouRA Research Phase 2A Extended Workflow (YOLO Mode)*
*2026-02-12*
