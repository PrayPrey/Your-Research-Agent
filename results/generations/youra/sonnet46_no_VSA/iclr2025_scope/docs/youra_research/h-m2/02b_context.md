# H-M2 Per-Hypothesis Context (JIT Generated)

**Source:** 02b_verification_plan.md
**Generated:** 2026-08-03

---

## Hypothesis Info

**ID:** H-M2
**Type:** MECHANISM
**Gate:** SHOULD_WORK (if fails: EXPLORE — narrow Conv1D mechanism claim; H-E1 may still hold)
**Prerequisites:** H-M1 (VALIDATED), H-E1 (VALIDATED — provides evaluation data)

**Statement:**
MOHAWK-SSM converted LLaMA-3-8B exhibits a significantly steeper needle-depth accuracy degradation slope than LAWCAT-converted LLaMA-3-8B on LongBench v2 multi-doc QA and synthetic tasks, quantified as |β_depth^SSM| ≥ 2× |β_depth^LAWCAT| in logistic regression of P(correct) ~ DepthPercentile + (1|Task), because SSM bounded-state exponential forgetting (h_t = A·h_{t-1} + B·x_t) loses exact positional identity of early tokens while LAWCAT's causal Conv1D preserves local token-to-token attention within a sliding window.

**Rationale:**
Step 2 of the causal chain — the mechanistic heart of H-Conv1D-v1. The depth-slope differential (P2 in Phase 2A) is the sharpest falsifier of the Conv1D mechanism claim. A positive result confirms degradation is not uniformly distributed across needle positions but concentrated at greater depths, exactly as predicted by SSM forgetting dynamics.

---

## Variables

- **Independent:** Conversion Strategy (MOHAWK-SSM vs LAWCAT)
- **Dependent:** β_depth (logistic regression coefficient of accuracy on needle depth percentile), per-model
- **Controlled:** Evaluation subset (LongBench v2 multi-doc QA + synthetic, ~166 questions); base model (LLaMA-3-8B fixed)

---

## Experimental Setup (from Phase 2A via Phase 2B)

### Dataset

| Field | Value |
|-------|-------|
| Name | LongBench v2 |
| Type | standard |
| Source | THUDM/LongBench on HuggingFace |
| Subset | Multi-doc QA + synthetic task categories (~166 of 503 questions) |
| Context | 8k–2M tokens per example |
| Task categories | single-doc QA, multi-doc QA, summarization, few-shot, synthetic, code |
| Hypothesis fit | Provides per-example needle depth metadata needed for logistic regression; multi-doc QA and synthetic tasks have highest retrieval demand |

### Model

| Field | Value |
|-------|-------|
| Name | LLaMA-3-8B (Meta) |
| Type | Decoder-only transformer, 8B parameters |
| Source | meta-llama/Llama-3-8B on HuggingFace |
| Conversion 1 | MOHAWK Stage 1+2 (SSD structured mixer, ≤1B tokens C4) |
| Conversion 2 | LAWCAT (causal Conv1D linear attention, ≤1B tokens C4) |
| Hypothesis fit | Fixed base model eliminates capability confound; both MOHAWK and LAWCAT have demonstrated pipelines at 7-8B scale |

---

## Verification Protocol

1. From H-E1 evaluation run, extract per-example needle depth percentile for multi-doc QA and synthetic tasks (built into LongBench v2 per-example metadata).
2. Fit per-model logistic regression: P(correct) ~ DepthPercentile + (1|Task), separately for MOHAWK-SSM and LAWCAT.
3. Compute β_depth coefficients and 95% CIs for both models.
4. Test: |β_depth^SSM| ≥ 2× |β_depth^LAWCAT| with non-overlapping 95% CIs; at least one β_depth significantly < 0 (p<0.01, Holm).
5. Report coefficient ratio with CI; assess Conv1D mechanism support.

---

## Success Criteria

- **Primary:** |β_depth^SSM| ≥ 2× |β_depth^LAWCAT| with non-overlapping 95% CIs
- **Secondary:** β_depth^SSM significantly < 0 (p<0.01); β_depth^LAWCAT closer to 0

---

## Dependencies

- H-M1: VALIDATED — Frobenius gate passed (slope β=-0.368 ≤ 0.5; 90th pct error ≤ 0.3). Interpretation of depth-slope as architectural (not approximation-driven) is confirmed.
- H-E1: VALIDATED — per-example evaluation data (accuracy + depth percentile) available for 503 LongBench v2 questions. H-M2 performs statistical analysis on this data — no new GPU compute needed.

---

## Key Mechanistic Background

**SSM bounded-state forgetting:**
h_t = A·h_{t-1} + B·x_t (exponential forgetting of early-token positions)

**LAWCAT Conv1D mechanism:**
Causal Conv1D sliding window preserves local token-to-token attention — demonstrated via >90% passkey retrieval at 22K tokens from Mistral-7B.

**Prediction:** At greater needle depth percentiles (needle placed earlier in document = higher depth), SSM accuracy should drop significantly while LAWCAT should remain relatively stable — reflected as a steeper negative β_depth coefficient for MOHAWK-SSM.
