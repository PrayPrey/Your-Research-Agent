# Product Requirements Document: h-m4
# Verbalized Confidence (VC) Calibration at 7B Scale

**Hypothesis:** h-m4
**Type:** MECHANISM
**Date:** 2026-08-25
**Status:** Phase 3 Implementation Planning

---

## 1. Executive Summary

This experiment tests whether Llama-2-7B-Chat's verbalized confidence (VC) underperforms token entropy (TE) and semantic entropy (SE) on TriviaQA hallucination detection, validating the mechanism claim that 7B-scale models lack sufficient meta-cognitive calibration for reliable self-reported uncertainty.

The experiment extends the h-m3 chain: TE AUROC (0.4381) and SE AUROC (0.286) are inherited ground-truth baselines. Only a single new inference pass with Llama-2-7B-Chat is required to compute VC AUROC.

**Gate:** SHOULD_WORK — VC AUROC < TE AUROC (0.4381) AND VC AUROC < SE AUROC (0.286)

---

## 2. Problem Statement

Verbalized confidence (VC) elicits uncertainty estimates by prompting a model to self-report a confidence score (0-100%). At 7B scale, Llama-2-7B-Chat may lack the meta-cognitive capacity to accurately self-assess, producing poorly calibrated or degenerate scores (always-high, always-50%).

The mechanism under test: **instruction-tuned 7B models systematically overestimate their own confidence**, causing VC AUROC to fall below both TE and SE baselines on TriviaQA.

---

## 3. Scope

### In Scope
- Verbalized Confidence (VC) inference with Llama-2-7B-Chat
- Loading h-m3 pre-computed TE/SE baselines (no re-inference)
- VC AUROC computation via bootstrap
- ECE, parse rate, confidence distribution diagnostics
- Figure generation: bar chart, histograms, ROC curves, calibration plot

### Out of Scope
- Re-computing TE or SE (inherited from h-m3)
- Fine-tuning or RLHF
- Multi-model comparison beyond Llama-2-7B-Chat
- Sampling-based VC (multi-pass); greedy only

---

## 4. Data Specification

### 4.1 Primary Dataset

| Field | Value |
|-------|-------|
| Name | TriviaQA dev (rc subset) |
| Source | HuggingFace: `mandarjoshi/trivia_qa`, config `rc`, split `validation` |
| N | 98 questions (same split as h-e1, h-m1, h-m2, h-m3) |
| Labels | Binary EM (exact match vs gold answer aliases) |
| Download | Auto (HuggingFace datasets) — no manual step |

**Loading code:**
```python
from datasets import load_dataset
dataset = load_dataset("mandarjoshi/trivia_qa", "rc", split="validation")
# Take first 98 questions (consistent with prior chain)
questions = [ex["question"] for ex in dataset.select(range(98))]
gold_answers = [ex["answer"]["aliases"] for ex in dataset.select(range(98))]
```

### 4.2 Preprocessing

- Questions: lowercase normalization
- Labels: binary EM — 1 if any gold alias matches model answer (case-insensitive), 0 otherwise
- Seed: 42 (fixed for reproducibility)

### 4.3 Inherited Baselines (No Re-computation Needed)

| Metric | Value | Source |
|--------|-------|--------|
| TE AUROC | 0.4381 | h-m3 gate result |
| SE AUROC | 0.286 | h-m3 gate result |
| N | 98 questions | h-m3 validated dataset |
| K | 10 samples | h-m3 methodology |

---

## 5. Functional Requirements

### FR-1: Data Loading and Label Preparation

**Priority:** P0

- Load 98 TriviaQA questions from HuggingFace (rc split, validation)
- Compute binary EM labels against gold answer aliases
- Load h-m3 baseline results (TE AUROC, SE AUROC) from `docs/youra_research/h-m3/`
- Validate consistency: same N=98, same questions

**Acceptance:** All 98 EM labels computed; h-m3 baselines loaded; assertion N=98 passes.

---

### FR-2: Verbalized Confidence (VC) Inference

**Priority:** P0

- Load Llama-2-7B-Chat (`meta-llama/Llama-2-7b-chat-hf`) in float16 with device_map="auto"
- Apply Llama-2-Chat prompt template `[INST] <<SYS>>...<</SYS>>\n\n{user_content} [/INST]`
- Generate responses with greedy decoding (do_sample=False, max_new_tokens=80, seed=42)
- Extract confidence score (0-100%) from response; fallback to 0.5 if unparseable
- Convert to uncertainty: `vc_uncertainty = 1.0 - confidence`
- Track fallback_count for parse rate computation

**Acceptance:** VC uncertainty scores computed for all 98 questions; parse_rate >= 0.80; std(vc_scores) > 0.05.

---

### FR-3: VC Mechanism Verification

**Priority:** P0

- Compute parse_rate = 1 - (fallback_count / N)
- Assert: parse_rate >= 0.80 (mechanism activation threshold)
- Assert: std(vc_scores) > 0.05 (not degenerate — not all-same)
- Log mechanism activation verdict: `verify_vc_mechanism_activated()`

**Acceptance:** Mechanism activation logged; degenerate output rate < 20%.

---

### FR-4: Bootstrap AUROC Computation

**Priority:** P0

- Compute VC AUROC via bootstrap (1000 iterations, seed=42)
- Report: mean VC AUROC ± 95% CI
- Compare: VC AUROC vs TE AUROC (0.4381) vs SE AUROC (0.286)
- Gate evaluation: VC AUROC < TE AUROC AND VC AUROC < SE AUROC

**Acceptance:** AUROC computed; gate verdict recorded (PASS/FAIL); delta_te = |VC - TE| reported.

---

### FR-5: Diagnostic Metrics

**Priority:** P1

- Expected Calibration Error (ECE): 10-bin reliability diagram computation
- Confidence distribution: histogram of raw confidence scores (0-100)
- Degenerate pattern detection: flag if >50% responses report same confidence

**Acceptance:** ECE value reported; confidence histogram data computed.

---

### FR-6: Figure Generation

**Priority:** P1 (mandatory per experiment brief)

All figures saved to `docs/youra_research/h-m4/figures/`:

| Figure | Type | Description |
|--------|------|-------------|
| `auroc_comparison.png` | Bar chart | VC vs TE vs SE AUROC with 95% CI error bars |
| `confidence_histogram.png` | Histogram | Raw confidence score distribution (0-100%) |
| `roc_curves.png` | Line plot | Overlay of VC, TE, SE ROC curves |
| `ece_calibration.png` | Reliability diagram | VC confidence vs actual accuracy |
| `failure_scatter.png` | Scatter | VC confidence vs EM correctness per question |

**Acceptance:** All 5 figures generated and saved.

---

### FR-7: Results Persistence

**Priority:** P0

Save to `docs/youra_research/h-m4/results.json`:
```json
{
  "hypothesis": "h-m4",
  "n_questions": 98,
  "auroc_vc": <float>,
  "auroc_vc_ci": [<lower>, <upper>],
  "auroc_te": 0.4381,
  "auroc_se": 0.286,
  "delta_te": <|VC - TE|>,
  "delta_se": <|VC - SE|>,
  "parse_rate": <float>,
  "fallback_count": <int>,
  "ece": <float>,
  "mechanism_activated": <bool>,
  "gate_passed": <bool>,
  "gate_condition": "VC AUROC < TE AND VC AUROC < SE",
  "seed": 42
}
```

**Acceptance:** results.json created; gate_passed field populated.

---

### FR-8: Ablation — Confidence Fallback Sensitivity

**Priority:** P2

- Re-compute VC AUROC with fallback_value = 0.0 (pessimistic) and fallback_value = 1.0 (optimistic)
- Report delta AUROC vs baseline fallback = 0.5
- Assess sensitivity of gate verdict to fallback choice

**Acceptance:** Three AUROC values reported (fallback 0.0, 0.5, 1.0).

---

## 6. Non-Functional Requirements

| NFR | Requirement |
|-----|-------------|
| Reproducibility | Seed=42 fixed; all random ops seeded |
| Performance | 98 inference calls; ~5-10 min on single A100 |
| Precision | float16 for model loading |
| Memory | ~14GB VRAM for Llama-2-7B-Chat in float16 |
| Compatibility | Python 3.10+, transformers>=4.31, datasets>=2.14, sklearn |

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.0.0
transformers>=4.31.0
datasets>=2.14.0
scikit-learn>=1.3.0
numpy>=1.24.0
matplotlib>=3.7.0
scipy>=1.11.0
tqdm>=4.65.0
```

### 7.2 External Model Access

- HuggingFace Hub access required for: `meta-llama/Llama-2-7b-chat-hf`
- Requires HuggingFace token with Llama-2 access granted
- Dataset: `mandarjoshi/trivia_qa` (public, no token needed)

### 7.3 Internal Dependencies

- h-m3 results: `docs/youra_research/h-m3/results.json` (TE/SE AUROC baselines)
- h-m3 EM labels: `docs/youra_research/h-m3/` (reuse dataset labels)

---

## 8. Success Criteria

| Criterion | Threshold | Status |
|-----------|-----------|--------|
| VC AUROC < TE AUROC (0.4381) | Required | Gate condition |
| VC AUROC < SE AUROC (0.286) | Required | Gate condition |
| parse_rate >= 0.80 | Required | Mechanism activation |
| std(vc_scores) > 0.05 | Required | Non-degenerate output |
| All 5 figures generated | Required | Visualization |
| results.json saved | Required | Persistence |

**Gate:** SHOULD_WORK — both conditions must hold for PASS.

---

## 9. Risk Assessment

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Low parse rate (<80%) | Medium | Robust regex with 3-pattern fallback; log degenerate outputs |
| Degenerate confidence (always 100%) | High | Detect via std check; report as mechanism failure if triggered |
| VC AUROC > TE AUROC (unexpected) | Medium | Document as contradiction; VC competitive at 7B → revise scale boundary |
| OOM on GPU | Low | float16 + device_map="auto" handles ≤16GB VRAM |
| h-m3 results file missing | Low | Fallback: hardcode TE=0.4381, SE=0.286 with warning |

---

*PRD generated for Phase 3 implementation planning. All specifications grounded in 02c_experiment_brief.md.*
