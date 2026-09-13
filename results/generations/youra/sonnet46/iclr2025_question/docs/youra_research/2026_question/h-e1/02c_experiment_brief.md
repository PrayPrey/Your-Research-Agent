# Experiment Design: H-E1

**Date:** 2026-03-16
**Author:** Anonymous
**Hypothesis Statement:** DeBERTa-v3-large-mnli contradiction/entailment scores systematically differ between hallucinated and non-hallucinated (context, response) pairs on HaluEval across Dialogue, QA, and Summarization tasks, producing AUROC > 0.55 on at least 2/3 tasks (DeLong p < 0.05).
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** N/A (no prerequisites — H-E1 is the foundation hypothesis)
**Gate Status:** MUST_WORK — AUROC > 0.55 on at least 2/3 of {Dialogue, QA, Summarization}; DeLong p < 0.05

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (Foundation hypothesis)

### Gate Condition
**MUST_WORK:** AUROC > 0.55 on at least 2/3 of {HaluEval-Dialogue, HaluEval-QA, HaluEval-Summarization} using DeBERTa-v3-large-mnli zero-shot; DeLong test p < 0.05 vs. AUROC=0.5 uniform baseline.

Failure action: STOP pipeline; write Serena memory; pivot to Phase 0 brainstorm (generative approaches).

---

## Continuation Context

N/A — H-E1 is the first hypothesis in the verification chain. No previous hypothesis results to carry forward.

### Previous Hypothesis Results (if applicable)
*None — H-E1 is the foundation hypothesis.*

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Archon KB Query Execution:**
- Query 1: "NLI hallucination detection experiment design dataset" → 3 results returned, similarity 0.44-0.48
- Query 2: "DeBERTa NLI cross-encoder hallucination detection implementation" → 5 results returned, similarity 0.40-0.42
- Query 3: "AUROC factual consistency NLI benchmark evaluation" → 3 results returned, similarity 0.40-0.44
- Queries 4-5: Code example searches → returned DALLE2/diffusion model examples

**Assessment:** Archon KB is populated with image generation / diffusion model content (DALLE2, ControlNet, HuggingFace Diffusers). No relevant NLI hallucination detection cases found. All similarity scores are low (0.39-0.51) confirming domain mismatch. This is expected for a fresh KB that has not been populated with NLI research content.

**Key Insight from Archon (indirect):** The HuggingFace `load_dataset` pattern confirmed from Archon code examples:
```python
from datasets import load_dataset
dataset = load_dataset("imagefolder", data_dir="/path/to/folder", split="train")
```
This confirms the standard `load_dataset(identifier, split=...)` API pattern used for HaluEval loading.

### Archon Code Examples

*No domain-relevant code examples found in Archon KB (KB populated with image generation content, not NLI research).*

**Fallback:** Implementation grounded in Phase 2B verification protocol (Section 2.2 H-E1) and established HuggingFace cross-encoder usage patterns documented in sentence-transformers documentation.

### Exa GitHub Implementations

**Exa API Status:** UNAVAILABLE — HTTP 402 (quota/payment required) on all 4 queries attempted:
- `cross-encoder nli-deberta-v3-large hallucination detection HaluEval official implementation GitHub`
- `DeBERTa NLI hallucination detection HaluEval AUROC PyTorch implementation`
- `pminervini HaluEval huggingface datasets load_dataset python`
- `cross-encoder nli-deberta-v3-large sentence-transformers inference AUROC hallucination`

**Documented Limitation:** GitHub code search unavailable. Proceeding with Phase 2B context as primary source (which already contains fully-specified verification protocol from prior h-e1 runs — confirmed by BUILD_ON note: "DeBERTa-v3-large-mnli is publicly available and cached; confirmed from h-e1 runs").

**Known Reference Implementations (from Phase 2B literature):**
- SummaC (Laban et al., 2022): SUMMACConv — NLI cross-encoder for summarization factual consistency
- TRUE (Honovich et al., 2022): Fine-tuned NLI for factuality across 11 datasets
- ORION (Gerner et al., 2025): Cross-encoder NLI achieves F1=0.83 on RAGTruth without task training
- SelfCheckGPT-NLI (Manakul et al., 2023): NLI-based self-consistency (orthogonal signal type)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This experiment does NOT reproduce a specific prior paper — it applies a known model (DeBERTa-v3-large-mnli) to a known dataset (HaluEval) in a novel post-hoc evaluation paradigm (ExtrospectiveNLI). No "paper author's official implementation" exists for this exact combination.

**Recommended Implementation Path:**
- Primary: Direct HuggingFace `sentence-transformers` CrossEncoder API (`cross-encoder/nli-deberta-v3-large`) — standard, well-documented, batch inference supported
- Fallback: HuggingFace `transformers` AutoModelForSequenceClassification with manual softmax — more control over batch size and truncation
- Justification: CrossEncoder API provides clean 3-class probability output via `predict(sentences, apply_softmax=True)`. The model is confirmed cached from prior h-e1 runs (Phase 2B BUILD_ON registry). Batch processing with `torch.inference_mode()` is standard.

### Code Analysis (Serena MCP)

*Skipped* — No complex code requiring Serena analysis. `cross-encoder/nli-deberta-v3-large` is a standard HuggingFace model loaded via `from_pretrained()` or `CrossEncoder()`. The implementation pattern is well-known from sentence-transformers documentation and requires no semantic code analysis.

---

## Experiment Specification

### Dataset

**Dataset:** HaluEval
**Type:** standard (real benchmark dataset — NOT synthetic ✅)
**Source:** Li et al. (2023), "HaluEval: A Large-Scale Hallucination Evaluation Benchmark for Large Language Models"
**HuggingFace Identifier:** `pminervini/HaluEval`

**Subsets and Sizes:**
| Subset | HF Config Name | Size | Split Used |
|--------|---------------|------|------------|
| Dialogue | `dialogue_data` | ~12,988 examples | full test set |
| QA | `qa_data` | 10,000 examples | full test set |
| Summarization | `summarization_data` | 10,000 examples | full test set |

**Total:** ~32,988 examples across 3 tasks

**Label Distribution:**
- Binary: `hallucinated` (label=1) vs. `non-hallucinated` (label=0)
- HaluEval construction: GPT-3.5 generated hallucinated responses + human filtering
- Label quality: Inter-annotator kappa=0.811 (Li et al., 2023)

**Input Fields (task-dependent):**
- Dialogue: `knowledge` (premise) + `response` (hypothesis) + `hallucination` (label)
- QA: `question`+`answer`+`context` → premise=context, hypothesis=response
- Summarization: `document` (premise) + `summary` (hypothesis) + `hallucination` (label)

**Preprocessing:**
- No tokenization or special preprocessing (raw text passed to cross-encoder tokenizer)
- Truncation: max_length=512 tokens (DeBERTa tokenizer auto-truncation)
- Batch size: 32 (for GPU inference)
- No augmentation (inference-only experiment)

**Path Specification:**
- Type: `standard` (HuggingFace dataset)
- Path: `auto` — downloaded via `load_dataset('pminervini/HaluEval', config_name)` to `~/.cache/huggingface/datasets/`
- Note: Prior h-e1 runs confirm dataset is already cached

**Loading Information** (for Phase 4 download):
- Method: HuggingFace `datasets`
- Identifier: `pminervini/HaluEval`
- Code: `load_dataset('pminervini/HaluEval', 'qa_data')` (repeat for `dialogue_data`, `summarization_data`)

### Models

#### Baseline Model

**Architecture:** cross-encoder/nli-deberta-v3-large (DeBERTa-v3-large fine-tuned on MNLI)
**Type:** Cross-encoder NLI discriminative model
**Source:** HuggingFace Hub — `cross-encoder/nli-deberta-v3-large`
**Pretrained:** Yes (MNLI-fine-tuned, 3-class: contradiction / entailment / neutral)
**Parameters:** ~435M (DeBERTa-v3-large)
**Frozen:** Yes (inference-only — no gradient computation)

**Configuration:**
- Input format: `[CLS] premise [SEP] hypothesis [SEP]`
- Output: 3-class softmax → P(contradiction), P(entailment), P(neutral)
- Inference: `torch.inference_mode()` (no grad, faster)
- Batch size: 32
- Max sequence length: 512 tokens (DeBERTa tokenizer)
- Truncation: True (auto-truncate to 512)
- Device: Single GPU (CUDA_VISIBLE_DEVICES set to lowest-memory GPU)

**Baseline Score (h-e1 PoC):**
- P(contradiction) used as hallucination score → compared against uniform random baseline (AUROC=0.5)
- Reference lower bound: SelfCheckGPT-NLI AUROC 0.48 (Dialogue), 0.53 (QA) on same dataset

**Loading Information** (for Phase 4 download):
- Method: HuggingFace `sentence-transformers` CrossEncoder
- Identifier: `cross-encoder/nli-deberta-v3-large`
- Code: `from sentence_transformers import CrossEncoder; model = CrossEncoder('cross-encoder/nli-deberta-v3-large')`

#### Proposed Model

**Architecture:** Same as Baseline (cross-encoder/nli-deberta-v3-large) applied to ExtrospectiveNLI framing

**Core Mechanism:** Post-hoc ExtrospectiveNLI scoring — applying NLI to existing (context, response) pairs to detect hallucination without any LLM generation at experiment time.

**Integration Point:** The "proposed" model is the scoring methodology applied on top of frozen DeBERTa:
- For H-E1 (EXISTENCE PoC): Raw `P(contradiction)` as hallucination score
- Compared against: AUROC=0.5 (random baseline)

**Core Mechanism Implementation:**

```python
# Core Mechanism: ExtrospectiveNLI Hallucination Detection
# Based on: cross-encoder/nli-deberta-v3-large (HuggingFace)
# H-E1 PoC: Raw P(contradiction) as hallucination score

from sentence_transformers import CrossEncoder
import torch
import numpy as np
from sklearn.metrics import roc_auc_score
from datasets import load_dataset

def run_nli_inference_batch(premises, hypotheses, model, batch_size=32):
    """
    Args:
        premises: list of str (context / grounding text)
        hypotheses: list of str (response / generated text)
        model: CrossEncoder with 3-class NLI output
    Returns:
        scores: np.array (N, 3) — [P(contradiction), P(entailment), P(neutral)]
    """
    pairs = list(zip(premises, hypotheses))
    # CrossEncoder.predict returns (N, 3) with apply_softmax=True
    scores = model.predict(pairs, batch_size=batch_size,
                           apply_softmax=True, show_progress_bar=True)
    return scores  # shape: (N, 3)

def compute_auroc_per_task(scores, labels):
    """
    Args:
        scores: np.array (N, 3) — NLI class probabilities
        labels: np.array (N,) — binary hallucination labels (1=hallucinated)
    Returns:
        results: dict with AUROC per framing
    """
    p_contradiction = scores[:, 0]   # class index depends on model's label map
    p_entailment    = scores[:, 1]
    auroc = roc_auc_score(labels, p_contradiction)
    return {"auroc_contradiction": auroc}

# Integration: DeBERTa frozen → inference-only, no gradient computation
# Label map: cross-encoder/nli-deberta-v3-large → {0: contradiction, 1: entailment, 2: neutral}
# Note: verify label order with model.config.id2label before using
```

### Training Protocol

**No training — inference-only experiment (H-E1 PoC)**

H-E1 uses a frozen pre-trained model. There is no optimization loop.

| Parameter | Value | Source |
|-----------|-------|--------|
| Optimizer | N/A (inference-only) | Phase 2B H-E1 spec |
| Learning Rate | N/A | Phase 2B H-E1 spec |
| Batch Size (inference) | 32 | Phase 2B Section 1.3 controlled variables |
| Max Sequence Length | 512 | Phase 2B Section 1.3 controlled variables |
| Truncation | True | Phase 2B Section 1.3 |
| Inference Mode | `torch.inference_mode()` | Phase 2B Section 1.3 |
| Seeds | 1 (fixed) | EXISTENCE PoC — single run |
| Device | Single GPU | CUDA_VISIBLE_DEVICES set to lowest-memory GPU |
| Model Weights | Frozen (no fine-tuning) | Phase 2B hypothesis definition |

**Inference Procedure:**
1. Load HaluEval subsets (Dialogue, QA, Summarization) via `load_dataset`
2. Map each subset to (premise, hypothesis, label) triples
3. Run DeBERTa CrossEncoder inference in batches (batch_size=32)
4. Collect per-example NLI scores: P(contradiction), P(entailment), P(neutral)
5. Compute AUROC per task using `sklearn.metrics.roc_auc_score`
6. Run DeLong test vs. AUROC=0.5 per task
7. Compute Cohen's d for score distribution separation
8. Execute label audit: stratified sample 200 hallucinated examples per task

### Evaluation

**Primary Metric:** AUROC (Area Under ROC Curve)
- Implementation: `sklearn.metrics.roc_auc_score(y_true, y_score)`
- Score used: P(contradiction) as hallucination score
- Computed per task: Dialogue, QA, Summarization

**Statistical Test:** DeLong test for AUROC vs. 0.5 (uniform baseline)
- Implementation: `scipy.stats` or `fastDeLong` (numpy implementation)
- Significance threshold: p < 0.05

**Secondary Metric:** Cohen's d (score distribution separation)
- `cohen_d = (mean_hall - mean_nonhall) / pooled_std`
- Threshold: d > 0.2

**Diagnostic:** Structural ceiling AUROC_max = p_contradictory + 0.5*(1 - p_contradictory)
- Requires label audit: stratified sample 200 hallucinated examples/task
- Categorize as: (A) contradiction, (B) unsupported-non-contradicted, (C) ambiguous
- p_contradictory = proportion of category (A)

**Success Criteria (PoC direction-based):**
- **PASS:** AUROC > 0.55 on at least 2/3 tasks AND DeLong p < 0.05 on at least 2/3 tasks
- **FAIL:** AUROC ≤ 0.55 on ALL THREE tasks → STOP pipeline

**Expected Baseline Performance (from Phase 2B literature):**
| Source | Metric | Dataset | Value |
|--------|--------|---------|-------|
| SelfCheckGPT-NLI | AUROC | HaluEval-Dialogue | 0.48 (lower bound) |
| SelfCheckGPT-NLI | AUROC | HaluEval-QA | 0.53 (lower bound) |
| Random baseline | AUROC | All | 0.50 |
| Target (H-E1) | AUROC | ≥2/3 tasks | >0.55 |

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Binary classification (hallucination detection)
- Library: `sklearn.metrics`
- Code: `from sklearn.metrics import roc_auc_score; auroc = roc_auc_score(y_true, y_score)`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual AUROC bar chart (3 tasks × target line at 0.55)

#### Additional Figures (LLM Autonomous)

The Phase 4 Coder should autonomously decide appropriate figures. Recommended based on hypothesis type and evaluation metrics:

1. **ROC Curves per Task** — 3 subplots (Dialogue, QA, Summarization), showing actual ROC curves with AUC annotation
2. **NLI Score Distributions** — violin/box plots of P(contradiction) for hallucinated vs. non-hallucinated groups per task (supports H-M1 visual)
3. **Structural Ceiling Bar Chart** — actual AUROC vs. theoretical ceiling AUROC_max = p + 0.5*(1-p) per task
4. **Label Audit Pie Charts** — per-task breakdown of hallucination types (A=contradiction, B=unsupported, C=ambiguous)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | DeBERTa 3-way NLI softmax output is accessible (P(contradiction), P(entailment), P(neutral)) | TRUE — standard CrossEncoder API returns 3-class probs |
| Mechanism Isolatable | P(contradiction) can be extracted and compared against P(entailment) independently | TRUE — index into scores array |
| Baseline Measurable | Random baseline (AUROC=0.5) is computable and comparable | TRUE — sklearn.metrics.roc_auc_score against uniform labels |

### Architecture Compatibility Check

**DeBERTa-v3-large-mnli Architecture:**
- Input: Token sequence with [CLS] + premise + [SEP] + hypothesis + [SEP]
- Output: 3-class logits → softmax → P(contradiction), P(entailment), P(neutral)
- Mechanism: Cross-attention over full premise+hypothesis sequence

**Required Features for H-E1:**
- 3-class NLI output with explicit contradiction/entailment separation ✅
- Batch inference capability (batch_size=32) ✅
- Handles long texts up to 512 tokens ✅

**Incompatible Architectures:**
- Bi-encoder models (encode premise/hypothesis separately — cannot capture cross-attention)
- 2-class NLI models (no separation between entailment and neutral)
- Generative models (not discriminative classifiers)

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | "Running NLI inference: N examples, batch_size=32" | `run_inference()` start |
| Score Shape | `scores.shape == (N, 3)` for each task | After `model.predict()` call |
| Score Non-Uniformity | `scores.std(axis=0) > 0.05` — scores not all ~0.33 | After batch inference |
| AUROC Above Random | `auroc > 0.50` on at least 1 task | After `roc_auc_score()` call |
| DeLong p-value | `p_value < 0.05` on at least 1 task | After DeLong test |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(scores, labels, task_name):
    """Verify NLI mechanism is producing meaningful signals."""
    indicators = {
        "shape_correct": scores.shape[1] == 3,
        "non_uniform": scores.std(axis=0).mean() > 0.05,
        "above_random": roc_auc_score(labels, scores[:, 0]) > 0.50,
        "label_verified": labels.mean() > 0.0 and labels.mean() < 1.0
    }
    all_pass = all(indicators.values())
    if not all_pass:
        failed = [k for k, v in indicators.items() if not v]
        print(f"[{task_name}] MECHANISM CHECK FAILED: {failed}")
    return all_pass, indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| Near-uniform NLI scores | `scores.std(axis=0) < 0.05` (all ~0.33) | FAIL: Distribution shift — DeBERTa not generalizing |
| AUROC < 0.50 on all tasks | `all(auroc < 0.50 for auroc in aurocs)` | FAIL: Score direction inverted — try 1-score |
| Inverted but correctable | `all(1-auroc > 0.55 for ...)` | WARN: Inversion detected; report flipped |
| Shape error | `scores.shape != (N, 3)` | FAIL: Model output format unexpected |
| Label map error | Contradiction not at index 0 | FAIL: Verify `model.config.id2label` mapping |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | TRUE (non-uniform scores, shape=3) | Batch output shape + std check |
| Effect Measurable | AUROC > 0.50 on ≥1 task | `roc_auc_score()` |
| Hypothesis Supported | AUROC > 0.55, DeLong p < 0.05 on ≥2/3 tasks | `roc_auc_score()` + DeLong test |

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. AUROC > 0.55 on at least 2/3 tasks (DeLong p < 0.05)

**PoC Fail Condition:**
- AUROC ≤ 0.55 on ALL three tasks → MUST_WORK gate FAILED → STOP pipeline

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Status:** No domain-relevant results found.

**Queries Executed (5 total):**
| Query | Results | Relevance |
|-------|---------|-----------|
| "NLI hallucination detection experiment design dataset" | 3 results | 0 relevant (diffusion model content) |
| "DeBERTa NLI cross-encoder hallucination detection implementation" | 5 results | 0 relevant (diffusion model content) |
| "AUROC factual consistency NLI benchmark evaluation" | 3 results | 0 relevant (image generation content) |
| "cross-encoder NLI PyTorch inference batch" | 5 results | 0 relevant (DALLE2 code) |
| "HaluEval HuggingFace datasets load_dataset PyTorch" | 5 results | 0 relevant (image dataset loading) |

**Assessment:** Archon KB populated with image generation / diffusion model content (DALLE2-pytorch, ControlNet, HuggingFace Diffusers). No NLI or hallucination detection content indexed. Domain mismatch confirmed by low similarity scores (avg 0.42) and irrelevant page URLs.

**Indirect Utility:** Confirmed standard `load_dataset(identifier, split=...)` HuggingFace API pattern from Archon code examples (chunk 874).

### B. GitHub Implementations (Exa)

**Status:** UNAVAILABLE — HTTP 402 (quota/payment required)

**Queries Attempted (4 total):**
- `cross-encoder nli-deberta-v3-large hallucination detection HaluEval official implementation GitHub`
- `DeBERTa NLI hallucination detection HaluEval AUROC PyTorch implementation`
- `pminervini HaluEval huggingface datasets load_dataset python`
- `cross-encoder nli-deberta-v3-large sentence-transformers inference AUROC hallucination`

**Documented Limitation:** GitHub code search unavailable due to API quota. Implementation grounded in:
1. Phase 2B verification protocol (Section 2.2, H-E1) — contains complete step-by-step procedure
2. Phase 2B BUILD_ON registry confirms: "DeBERTa-v3-large-mnli is publicly available and cached; confirmed from h-e1 runs"
3. Standard sentence-transformers CrossEncoder API (widely documented)

### C. Code Analysis (Serena)

**Status:** Skipped — `serena_needed = false`

No complex custom code requiring analysis. `cross-encoder/nli-deberta-v3-large` is a standard HuggingFace model with well-documented inference API. Code pattern is straightforward CrossEncoder inference.

### D. Previous Hypothesis Context

**Previous Context:** None — H-E1 is the foundation hypothesis (no prerequisites).

### E. Literature Sources (from Phase 2B)

**Source 1:** HaluEval — Li et al. (2023)
- Description: Benchmark for hallucination evaluation across Dialogue, QA, Summarization
- HuggingFace: `pminervini/HaluEval`
- Used For: Primary dataset selection, label quality (kappa=0.811)

**Source 2:** SummaC — Laban et al. (2022)
- Description: NLI-based factual consistency scoring; SUMMACConv achieves 74.4% balanced accuracy on summarization
- Used For: Evidence that NLI-based detection is viable (BUILD_ON); motivates H-E1

**Source 3:** TRUE — Honovich et al. (2022)
- Description: Fine-tuned NLI achieves ROC AUC ~81.5 across 11 factuality datasets
- Used For: Upper bound evidence for NLI-based detection capability

**Source 4:** ORION — Gerner et al. (2025)
- Description: Cross-encoder NLI F1=0.83 on RAGTruth without task training
- Used For: Confirms zero-shot cross-encoder NLI generalizes to factual inconsistency detection

**Source 5:** SelfCheckGPT — Manakul et al. (2023)
- Description: NLI-based self-consistency; AUROC 0.48 (Dialogue), 0.53 (QA) on HaluEval
- Used For: Available lower bound; note orthogonality (self-consistency vs. extrospective NLI)

**Source 6:** FActScore — Min et al. (2023)
- Description: 40% atomic facts unsupported at sentence granularity
- Used For: Motivates sentence-level max aggregation (H-M4); supports existence of detectable signal

### F. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset: HaluEval | Phase 2B Section 1.3 | HuggingFace `pminervini/HaluEval` |
| Dataset type: standard | Phase 2B H-E1 spec | Li et al. (2023) |
| Dataset subsets + sizes | Phase 2B Section 5.5 | Resource summary (~32,988 examples) |
| Model: cross-encoder/nli-deberta-v3-large | Phase 2B Section 1.3 | HuggingFace cross-encoder |
| Batch size: 32 | Phase 2B Section 1.3 (controlled variables) | Phase 2B hypothesis definition |
| Max length: 512 | Phase 2B Section 1.3 (controlled variables) | Phase 2B hypothesis definition |
| Inference mode: torch.inference_mode() | Phase 2B Section 1.3 | Phase 2B hypothesis definition |
| Metric: AUROC | Phase 2B H-E1 success criteria | sklearn.metrics.roc_auc_score |
| Statistical test: DeLong p < 0.05 | Phase 2B H-E1 success criteria | Phase 2B Section 2.2 |
| Success threshold: >0.55 on ≥2/3 tasks | Phase 2B H-E1 success criteria | Phase 2B Section 2.2 |
| Label audit (200/task) | Phase 2B H-E1 verification protocol step 4 | Phase 2B Section 2.2 |
| Structural ceiling formula | Phase 2B Section 6.3 synthesis | AUROC_max = p + 0.5*(1-p) |
| SelfCheckGPT lower bound | Phase 2B Section 1.4 | Manakul et al. (2023) |
| Core mechanism pseudocode | Phase 2B + sentence-transformers API | CrossEncoder.predict() pattern |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-16T15:00:00Z

### Workflow History for This Hypothesis
- 2026-03-16: H-E1 set to IN_PROGRESS (Phase 2C started)
- 2026-03-16: Phase 2C execution initiated (UNATTENDED mode)

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code) — 5 queries executed, 0 domain-relevant hits (KB domain mismatch); Exa (GitHub) — UNAVAILABLE (402); Serena (Code Analysis) — Skipped (no complex code needed)*
*Implementation grounded in Phase 2B verification protocol + established HuggingFace cross-encoder patterns*
*Next Phase: Phase 3 - Implementation Planning*
