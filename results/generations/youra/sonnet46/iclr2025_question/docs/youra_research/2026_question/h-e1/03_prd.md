# Product Requirements Document: H-E1

**Hypothesis:** H-E1 (EXISTENCE PoC)
**Type:** EXISTENCE
**Gate:** MUST_WORK
**Generated:** 2026-03-16
**Phase:** 3 — Implementation Planning

---

## Executive Summary

This PRD specifies the implementation requirements for H-E1, an existence proof-of-concept (PoC) that tests whether applying a frozen DeBERTa-v3-large NLI cross-encoder to existing (context, response, label) triples from HaluEval produces AUROC > 0.55 on at least 2/3 tasks (Dialogue, QA, Summarization). This is a purely inference-based experiment — no training, no fine-tuning, no data generation. The implementation must be minimal (PoC scope), statistically rigorous, and executable on a single GPU.

**Hypothesis Statement:**
> DeBERTa-v3-large-mnli contradiction/entailment scores systematically differ between hallucinated and non-hallucinated (context, response) pairs on HaluEval across Dialogue, QA, and Summarization tasks, producing AUROC > 0.55 on at least 2/3 tasks (DeLong p < 0.05).

---

## 1. Problem Statement

### 1.1 Research Question

Can a frozen NLI cross-encoder (cross-encoder/nli-deberta-v3-large) detect hallucination in LLM-generated text by treating it as a post-hoc textual entailment problem? Specifically, does P(contradiction) computed between grounding context and response serve as a discriminative hallucination signal without any task-specific training?

### 1.2 Motivation

- LLM hallucination detection typically requires expensive generative sampling or LLM-call pipelines at inference time
- Post-hoc ExtrospectiveNLI applies discriminative NLI scoring to existing (context, response) pairs — no LLM generation needed at experiment time
- DeBERTa-v3-large fine-tuned on MNLI encodes graded entailment/contradiction sensitivity
- Prior work (SummaC, TRUE, ORION) establishes NLI-based detection viability — this experiment validates the specific zero-shot transfer to HaluEval

### 1.3 Scope

- **In scope:** Frozen model inference, AUROC evaluation across 3 HaluEval subsets, statistical testing
- **Out of scope:** Fine-tuning, ablations (deferred to H-M series), multi-model comparison, LLM generation

---

## 2. Functional Requirements

### FR-1: Data Loading and Preparation

**FR-1.1 HaluEval Dialogue Loading**
- Load `pminervini/HaluEval` config `dialogue_data` via `load_dataset('pminervini/HaluEval', 'dialogue_data')`
- Extract fields: `knowledge` (premise), `response` (hypothesis), `hallucination` (label: "yes"/"no" → 1/0)
- Full test set: ~12,988 examples
- No preprocessing beyond tokenizer auto-truncation at max_length=512

**FR-1.2 HaluEval QA Loading**
- Load `pminervini/HaluEval` config `qa_data`
- Extract fields: `context` (premise), `answer` (hypothesis), `hallucination` (label)
- Full test set: 10,000 examples

**FR-1.3 HaluEval Summarization Loading**
- Load `pminervini/HaluEval` config `summarization_data`
- Extract fields: `document` (premise), `summary` (hypothesis), `hallucination` (label)
- Full test set: 10,000 examples

**FR-1.4 Label Encoding**
- Encode `hallucination` field: "yes" → 1 (hallucinated), "no" → 0 (non-hallucinated)
- Verify label distribution: expected ~50/50 split per subset

### FR-2: Model Loading

**FR-2.1 CrossEncoder Loading**
- Load `cross-encoder/nli-deberta-v3-large` via `sentence_transformers.CrossEncoder`
- Model frozen — no gradient computation
- Fallback: `transformers.AutoModelForSequenceClassification.from_pretrained('cross-encoder/nli-deberta-v3-large')`

**FR-2.2 Label Map Verification**
- Verify `model.config.id2label` to confirm class index → label mapping
- Expected: `{0: 'contradiction', 1: 'entailment', 2: 'neutral'}` (verify before using)
- Log actual mapping to ensure correct P(contradiction) extraction

**FR-2.3 Device Configuration**
- Automatically detect available CUDA device (lowest memory usage)
- Set `CUDA_VISIBLE_DEVICES` to selected GPU before model loading
- Use `torch.inference_mode()` for all forward passes

### FR-3: NLI Inference

**FR-3.1 Batch Inference**
- Run CrossEncoder.predict() on (premise, hypothesis) pairs
- Batch size: 32 (configurable)
- Max sequence length: 512 tokens (DeBERTa tokenizer auto-truncation)
- Apply softmax: `apply_softmax=True` (returns probabilities, not logits)
- Output shape: `(N, 3)` — [P(contradiction), P(entailment), P(neutral)]

**FR-3.2 Progress Monitoring**
- Log progress every 1000 examples
- Log: "Running NLI inference: {N} examples, batch_size=32"
- Log output shape after first batch: `scores.shape == (N_batch, 3)`

**FR-3.3 Score Extraction**
- Extract P(contradiction) from scores array at verified class index
- Store full (N, 3) score matrix for downstream analysis (H-M series reuse)

### FR-4: Evaluation and Statistical Testing

**FR-4.1 AUROC Computation**
- Compute per-task AUROC: `sklearn.metrics.roc_auc_score(y_true, y_score)`
- `y_score` = P(contradiction) column from scores
- `y_true` = binary hallucination labels (1=hallucinated)
- Compute for all 3 tasks: Dialogue, QA, Summarization

**FR-4.2 DeLong Test**
- Compute DeLong test for each task: AUROC vs. 0.5 (uniform baseline)
- Implementation: fastDeLong (numpy-based) or `scipy.stats`
- Report p-value per task
- Significance threshold: p < 0.05

**FR-4.3 Cohen's d**
- Compute effect size: `d = (mean_hallucinated - mean_non_hallucinated) / pooled_std`
- Applied to P(contradiction) scores per task
- Threshold: d > 0.2 (small-to-medium effect)

**FR-4.4 Mechanism Activation Verification**
- Verify NLI mechanism produces meaningful signals:
  - `scores.shape[1] == 3` (3-class output)
  - `scores.std(axis=0).mean() > 0.05` (non-uniform scores)
  - `auroc > 0.50` on at least 1 task (above random)
  - Labels contain both classes (not all same)
- Log FAILED checks if any indicator fails

**FR-4.5 Score Inversion Check**
- If all AUROCs < 0.50, try inverted score: 1 - P(contradiction)
- If inverted scores > 0.55, report as WARN (inversion detected) and use inverted

### FR-5: Label Audit

**FR-5.1 Structural Ceiling Audit**
- Stratified sample 200 hallucinated examples per task (random seed=42)
- Manually categorize (or auto-classify) into:
  - Category A: True contradiction (detectable by NLI)
  - Category B: Unsupported/non-contradicted (NLI cannot detect)
  - Category C: Ambiguous
- Compute `p_contradictory` = proportion of category A
- Compute `AUROC_max = p_contradictory + 0.5 * (1 - p_contradictory)`
- Report structural ceiling vs. actual AUROC

### FR-6: Visualization

**FR-6.1 Mandatory Figure — Gate Metrics Comparison**
- Bar chart: Actual AUROC per task (Dialogue, QA, Summarization)
- Horizontal reference line at AUROC = 0.55 (pass threshold)
- Save to: `h-e1/figures/gate_metrics_comparison.png`

**FR-6.2 ROC Curves (Autonomous)**
- 3-subplot figure: ROC curves for Dialogue, QA, Summarization
- Each subplot: AUC annotation
- Save to: `h-e1/figures/roc_curves.png`

**FR-6.3 NLI Score Distributions (Autonomous)**
- Violin or box plots: P(contradiction) distributions for hallucinated vs. non-hallucinated
- Per task
- Save to: `h-e1/figures/score_distributions.png`

**FR-6.4 Structural Ceiling Chart (Autonomous)**
- Bar chart: actual AUROC vs. AUROC_max per task
- Save to: `h-e1/figures/structural_ceiling.png`

---

## 3. Non-Functional Requirements

### NFR-1: Performance
- Full inference over ~32,988 examples must complete within reasonable time on single GPU
- Target: < 30 minutes on V100/A100 with batch_size=32

### NFR-2: Reproducibility
- Fixed random seed: 42 for label audit sampling
- Single run (EXISTENCE PoC — no ensemble, no repeated runs)
- All scores saved to disk for reuse by H-M series

### NFR-3: GPU Usage
- Single GPU only (`CUDA_VISIBLE_DEVICES` set to lowest-memory GPU)
- No distributed training/inference

### NFR-4: Output Format
- Results saved to `h-e1/results/h-e1_results.json` with full per-example scores
- Summary results saved to `h-e1/results/h-e1_summary.json`
- Figures saved to `h-e1/figures/`

### NFR-5: Code Quality
- Single-file inference script preferred (PoC scope)
- Exception: separate `evaluate.py` if evaluation logic is complex
- No over-engineering — minimal structure for PoC

---

## 4. Data Specification

### 4.1 Primary Dataset

**Dataset:** HaluEval
**HuggingFace ID:** `pminervini/HaluEval`
**Type:** Standard benchmark (auto-download via HuggingFace datasets)
**No manual download required.**

| Subset | Config Name | Size | Split | Fields |
|--------|-------------|------|-------|--------|
| Dialogue | `dialogue_data` | ~12,988 | full | knowledge, response, hallucination |
| QA | `qa_data` | 10,000 | full | context, answer, hallucination |
| Summarization | `summarization_data` | 10,000 | full | document, summary, hallucination |

**Label Quality:** Inter-annotator kappa = 0.811 (Li et al., 2023)

### 4.2 Label Construction

- Hallucination labels: "yes" (hallucinated=1), "no" (non-hallucinated=0)
- HaluEval construction: GPT-3.5 generated hallucinated responses + human filtering

### 4.3 Premise/Hypothesis Mapping

| Subset | Premise | Hypothesis |
|--------|---------|------------|
| Dialogue | `knowledge` field | `response` field |
| QA | `context` field | `answer` field |
| Summarization | `document` field | `summary` field |

---

## 5. Model Specification

### 5.1 Model

| Property | Value |
|----------|-------|
| Name | cross-encoder/nli-deberta-v3-large |
| Source | HuggingFace Hub |
| Architecture | DeBERTa-v3-large fine-tuned on MNLI |
| Parameters | ~435M |
| Output | 3-class softmax (contradiction, entailment, neutral) |
| Mode | Inference-only (frozen) |

### 5.2 Inference Configuration

| Parameter | Value |
|-----------|-------|
| Batch Size | 32 |
| Max Sequence Length | 512 |
| Truncation | True |
| Inference Mode | torch.inference_mode() |
| Device | Single GPU (CUDA_VISIBLE_DEVICES=lowest_memory) |
| Softmax | apply_softmax=True |

---

## 6. Success Criteria

### 6.1 Gate Condition (MUST_WORK)

**PASS:** AUROC > 0.55 on at least 2 of 3 tasks AND DeLong p < 0.05 on at least 2 of 3 tasks

**FAIL:** AUROC ≤ 0.55 on ALL THREE tasks → STOP pipeline, write Serena failure memory

### 6.2 Expected Reference Values

| Source | Task | AUROC |
|--------|------|-------|
| Random baseline | All | 0.50 |
| SelfCheckGPT-NLI | Dialogue | 0.48 (lower bound) |
| SelfCheckGPT-NLI | QA | 0.53 (lower bound) |
| Target (H-E1) | ≥2/3 tasks | >0.55 |

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.0.0
sentence-transformers>=2.2.0
transformers>=4.30.0
datasets>=2.14.0
scikit-learn>=1.3.0
scipy>=1.11.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
tqdm>=4.65.0
pyyaml>=6.0
```

### 7.2 External References

- HaluEval paper: Li et al. (2023) — `pminervini/HaluEval`
- SummaC: Laban et al. (2022) — NLI cross-encoder for summarization factuality
- TRUE: Honovich et al. (2022) — Fine-tuned NLI for factuality
- ORION: Gerner et al. (2025) — Cross-encoder NLI zero-shot generalization

---

## 8. Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Label map mismatch (contradiction not at index 0) | Verify `model.config.id2label` before extracting scores |
| Near-uniform NLI scores | Mechanism activation check: std > 0.05 |
| AUROC < 0.50 (inverted signal) | Inversion check: try 1 - P(contradiction) |
| GPU OOM with batch_size=32 | Reduce to batch_size=16 as fallback |
| Dataset not cached | `load_dataset` auto-downloads; ensure HF cache dir accessible |

---

## Traceability

| Specification | Source |
|--------------|--------|
| Dataset: HaluEval | Phase 2B Section 1.3, Li et al. (2023) |
| Dataset subsets + sizes | Phase 2C experiment brief |
| Model: cross-encoder/nli-deberta-v3-large | Phase 2B Section 1.3 |
| Batch size 32, max_length 512 | Phase 2B controlled variables |
| AUROC metric | Phase 2B H-E1 success criteria |
| DeLong p < 0.05 | Phase 2B Section 2.2 |
| Success threshold >0.55 on ≥2/3 | Phase 2B Section 2.2 |
| Label audit 200/task | Phase 2B H-E1 verification protocol step 4 |
| Structural ceiling formula | Phase 2B Section 6.3 |

---

*PRD generated inline by Phase 3 workflow (BMAD PRD workflow files not found — generated directly)*
*Hypothesis: H-E1 | Type: EXISTENCE | Tier: LIGHT | Budget: 15 tasks*
