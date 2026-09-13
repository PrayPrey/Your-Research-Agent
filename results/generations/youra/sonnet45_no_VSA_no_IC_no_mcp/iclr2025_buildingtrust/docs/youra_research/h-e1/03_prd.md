# Product Requirements Document: h-e1

**Date:** 2026-08-24  
**Hypothesis ID:** h-e1  
**Hypothesis Statement:** Entity-substitution errors exhibit significantly lower attention entropy over NER-identified entity spans compared to non-entity errors (p < 0.05, entity-error mean < non-entity-error mean)  
**Phase:** 3 (Implementation Planning)  
**Experiment Type:** EXISTENCE (PoC pattern detection)

---

## Executive Summary

**Goal:** Validate that entity-substitution errors show measurably different attention patterns (lower entropy over entity spans) compared to non-entity errors in pre-trained LLMs.

**Success Criteria:** p < 0.05 AND mean_entity_entropy < mean_non_entity_entropy (MUST_WORK gate)

**No Training Required:** Inference-only experiment on Llama-2-7B

**Output:** Statistical validation report (04_validation.md) with pass/fail determination

---

## Functional Requirements

### FR1: Attention Extraction
- **FR1.1:** Load Llama-2-7B model with `output_attentions=True`
- **FR1.2:** Run inference on TruthfulQA questions to extract last-layer attention weights
- **FR1.3:** Average attention across all heads → `[seq_len, seq_len]` matrix per sample
- **FR1.4:** Handle model loading (float16 precision, device mapping)

### FR2: Entity Span Detection
- **FR2.1:** Load spaCy `en_core_web_lg` NER model (validated in h-c1, F1=0.96)
- **FR2.2:** Identify entity spans at character level
- **FR2.3:** Map character spans to token indices using tokenizer.char_to_token()
- **FR2.4:** Validate span alignment on 10 samples before full run

### FR3: Entropy Calculation
- **FR3.1:** Compute entropy `H(A) = -Σ(p_i * log(p_i))` for attention weights TO entity tokens
- **FR3.2:** Average entropy across all tokens in entity span
- **FR3.3:** Handle edge cases: zero attention (add 1e-10 smoothing), empty spans (skip sample)
- **FR3.4:** Return single float entropy score per sample

### FR4: Statistical Comparison
- **FR4.1:** Collect entropy scores for entity-error samples (N=50)
- **FR4.2:** Collect entropy scores for non-entity-error samples (N=50)
- **FR4.3:** Run independent samples t-test (one-tailed: entity < non-entity)
- **FR4.4:** Calculate Cohen's d effect size
- **FR4.5:** Determine pass/fail: `(p < 0.05) AND (mean_entity < mean_non_entity)`

### FR5: Visualization
- **FR5.1:** Generate violin plot comparing entropy distributions (entity vs non-entity)
- **FR5.2:** Generate overlapping histograms of entropy scores
- **FR5.3:** Save figures to `h-e1/figures/` directory
- **FR5.4:** Annotate plots with p-value and means

### FR6: Validation Report
- **FR6.1:** Generate 04_validation.md with:
  - Gate metrics: p-value, mean_entity_entropy, mean_non_entity_entropy, Cohen's d
  - Pass/fail determination
  - Figure references
  - Sample diagnostics (outliers, failed spans)
- **FR6.2:** Save entropy scores to CSV: [sample_id, error_type, entropy]
- **FR6.3:** Save statistical results to JSON

---

## Data Requirements

### DR1: Dataset
- **Source:** TruthfulQA generation split (HuggingFace Datasets)
- **Preprocessing:** Reuse h-c1 entity-annotated subset (N=100, 50 entity-error + 50 non-entity-error)
- **Format:** JSON with fields: `{question, error_type, entity_span_chars}`
- **Path:** `./data/truthfulqa_entity_subset/`

### DR2: Model
- **Model:** Llama-2-7B (`meta-llama/Llama-2-7b-hf`)
- **Configuration:** `output_attentions=True, torch_dtype=torch.float16, device_map="auto"`
- **Cache:** HuggingFace default cache (`~/.cache/huggingface/`)
- **Fallback:** GPT-2 if Llama-2 unavailable (update documentation)

### DR3: NER Tool
- **Model:** spaCy `en_core_web_lg` (validated F1=0.96 in h-c1)
- **Usage:** `nlp = spacy.load("en_core_web_lg")`
- **Output:** Entity spans (character-level start/end)

---

## Non-Functional Requirements

### NFR1: Performance
- **Execution Time:** < 10 minutes for N=100 samples (single GPU, A100/V100)
- **Memory:** < 16GB GPU memory (float16 Llama-2-7B)
- **Throughput:** ≥ 10 samples/minute (batching optional but not required)

### NFR2: Robustness
- **Error Handling:** Skip samples with failed NER or span misalignment (log count)
- **Reproducibility:** Set seed=42 for deterministic sampling (if dataset > 100)
- **Validation:** Pre-flight checks for model/dataset availability before full run

### NFR3: Interpretability
- **Logging:** Print progress every 10 samples (e.g., "Processed 10/100 samples")
- **Diagnostics:** Log outlier entropy values (>2 std dev from group mean)
- **Visualization:** Clear labels, legends, p-value annotation on plots

---

## Technical Constraints

### TC1: Model Access
- **Llama-2:** Requires HuggingFace access token (if gated)
- **Compute:** Minimum 1x GPU with 16GB VRAM (T4/V100/A100)
- **Storage:** ~15GB for model weights + datasets

### TC2: Dependencies
- **Core:** `transformers>=4.30`, `torch>=2.0`, `spacy>=3.5`, `scipy>=1.10`
- **NER Model:** spaCy `en_core_web_lg` (300MB download)
- **Visualization:** `matplotlib>=3.5` or `seaborn>=0.12`

### TC3: Implementation Tier
- **Tier 1:** Low complexity (no training, standard library usage)
- **Budget:** 34 token budget for implementation (from state)
- **Task Count:** 8 tasks (data prep, env setup, 5 Epic tasks, 1 failsafe)

---

## Acceptance Criteria

### AC1: Gate Metrics (MUST_WORK)
- [ ] p_value < 0.05 (statistical significance)
- [ ] mean_entity_entropy < mean_non_entity_entropy (directional hypothesis)
- [ ] Both conditions satisfied → PASS, else FAIL

### AC2: Code Quality
- [ ] All 100 samples processed without crash
- [ ] Entropy values in valid range [0.0, log(seq_len)]
- [ ] No NaN/inf in results
- [ ] Character-to-token alignment validated on ≥10 samples

### AC3: Documentation
- [ ] 04_validation.md generated with gate determination
- [ ] Figures saved to h-e1/figures/ (violin plot, histograms)
- [ ] CSV entropy scores saved
- [ ] JSON statistical results saved

### AC4: Reproducibility
- [ ] Seed fixed (if sampling applied)
- [ ] Model/dataset versions documented
- [ ] Execution command documented in validation report

---

## Out of Scope

- **Training or fine-tuning:** Inference-only experiment
- **Multi-model comparison:** Llama-2-7B only (GPT-3.5 excluded due to API limits)
- **Error type annotation:** Reuse h-c1 annotations (no new labeling)
- **Sample size expansion:** Fixed N=100 (no adaptive sampling)
- **Multi-layer analysis:** Last layer only (layers 0-31 not analyzed)
- **Per-head entropy:** Average across heads (no per-head breakdown)

---

## Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Llama-2 unavailable | Low | Medium | Fallback to GPT-2 (document in validation) |
| Entity span misalignment | Low | Medium | Validate on 10 samples pre-flight, skip bad spans |
| Insufficient effect size | Medium | High | N=100 powered for d=0.5; collect N=200 if p borderline |
| GPU OOM | Low | Medium | Use float16, reduce batch size to 1 if needed |

---

## Dependencies

### Upstream (Prerequisites)
- **h-c1:** NER tool validation (spaCy F1=0.96, Wikipedia coverage 100%)
  - **Status:** COMPLETED
  - **Artifacts:** `h-c1/04_validation.md`, entity-annotated dataset

### Downstream (Blocked Until This Passes)
- **h-m1:** Entropy threshold mechanism (uses entropy as classification feature)
- **h-m2:** Retrieval routing mechanism (combines entropy + Wikipedia search)

---

## Success Metrics Summary

| Metric | Threshold | Source |
|--------|-----------|--------|
| p_value | < 0.05 | Hypothesis statement |
| mean_entity_entropy | < mean_non_entity_entropy | Hypothesis statement |
| Cohen's d | > 0.5 (desirable, not required) | Effect size interpretation |
| Processed samples | 100/100 (skip failures, log count) | Data completeness |
| Execution time | < 10 minutes | Performance target |

---

## Appendix: Sample Data Flow

```
Input: TruthfulQA question + error_type label
  ↓
[1] NER (spaCy) → entity_span_chars (start, end)
  ↓
[2] Tokenize (Llama-2 tokenizer) → entity_span_tokens
  ↓
[3] Model inference (output_attentions=True) → attention_weights [seq_len, seq_len]
  ↓
[4] Extract attention TO entity span → entity_attn [seq_len, entity_len]
  ↓
[5] Calculate entropy → H(A) = -Σ(p * log(p)) → single float
  ↓
[6] Aggregate by error_type → two distributions (entity-error, non-entity-error)
  ↓
[7] Statistical test (t-test) → p_value, means, Cohen's d
  ↓
Output: Pass/fail determination + 04_validation.md
```

---

**Document Version:** 1.0  
**Next Phase:** Architecture Design (03_architecture.md)
