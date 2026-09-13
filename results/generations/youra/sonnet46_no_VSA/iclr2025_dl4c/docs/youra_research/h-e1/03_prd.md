# Product Requirements Document: H-E1
# Code Embedding Distribution Distinctiveness Analysis

**Status:** DRAFT
**Hypothesis:** H-E1 (EXISTENCE — PoC)
**Date:** 2026-08-02
**Phase:** 3 — Implementation Planning
**stepsCompleted:** [1, 2, 3, 4, 5, 6, 7]

---

## 1. Executive Summary

This experiment verifies that the four SFT training sources (HumanEval-train, MBPP-train, LeetCode, Equal-mix) produce measurably distinct code-embedding distributions. Success is confirmed by pairwise mean cosine similarity < 0.95 between each source and each test benchmark (HumanEval+, MBPP+) using two encoders: CodeBERT and all-MiniLM-L6-v2. This is a pure embedding analysis experiment — no model training is required.

**Gate Type:** MUST_WORK — failure blocks H-M2 (distributional alignment mechanism untestable without distinct distributions)

---

## 2. Problem Statement

Before testing whether SFT training source diversity improves code generation (H-M2), we must confirm the four training sources actually have distinct embedding distributions relative to the test benchmarks. If all sources produce nearly identical embeddings (cosine sim > 0.95), the P3 distributional alignment mechanism is untestable and H-M2 must be blocked.

---

## 3. Functional Requirements

### FR-1: Dataset Loading
- Load all 5 datasets from HuggingFace Hub:
  - `openai/openai_humaneval` split="test" → 164 problems (HumanEval-train)
  - `google-research-datasets/mbpp` name="sanitized" split="train" → ~374 problems (MBPP-train)
  - `newfacade/LeetCodeDataset` split="train" → ~2,500 Python problems (LeetCode)
  - `evalplus/humanevalplus` split="test" → 164 problems (HumanEval+)
  - `evalplus/mbppplus` split="test" → 378 problems (MBPP+)
- Construct Equal-mix corpus: 164 problems sampled uniformly from HumanEval-train (all), MBPP-train (seed=42), LeetCode (seed=42)
- Use full dataset splits (no subsampling of individual sources except Equal-mix construction)

### FR-2: Text Extraction
- HumanEval / HumanEval+: `prompt + canonical_solution` concatenated as raw text
- MBPP / MBPP+: `text + code` concatenated as raw text
- LeetCode: problem description + Python solution concatenated as raw text
- Strip whitespace; truncate at 512 tokens (CodeBERT) / 256 tokens (all-MiniLM-L6-v2 effective max)

### FR-3: Encoder 1 — CodeBERT
- Load `microsoft/codebert-base` via HuggingFace Transformers
- Encode each corpus with mean-pooling over last hidden states (attention-mask weighted)
- L2-normalize output embeddings → 768-dim unit vectors
- Batch size: 32 (reduce to 8 on OOM)
- Device: CUDA if available, else CPU

### FR-4: Encoder 2 — all-MiniLM-L6-v2
- Load `sentence-transformers/all-MiniLM-L6-v2` via sentence-transformers
- Encode each corpus with `normalize_embeddings=True`
- Output: 384-dim L2-normalized vectors
- Batch size: 32

### FR-5: Pairwise Similarity Matrix
- For each encoder, compute 4×2 mean pairwise cosine similarity matrix:
  - Rows: HumanEval-train, MBPP-train, LeetCode, Equal-mix
  - Columns: HumanEval+, MBPP+
- Cosine similarity: dot product of L2-normalized vectors → `source_embs @ target_embs.T` → mean
- Output: 16 similarity values (4 sources × 2 benchmarks × 2 encoders)

### FR-6: Gate Evaluation
- Check: any of the 16 values < 0.95 → gate SATISFIED
- Check: all 16 values > 0.95 → GATE FAIL → H-M2 blocked
- Report min, max, mean across all 16 values

### FR-7: Mechanism Verification
- Verify embedding shapes: CodeBERT → (N, 768), MiniLM → (N, 384) per corpus
- Verify std of 16 similarity values > 0.01 (non-degenerate)
- Log: "Encoded N problems for [source] with [encoder]" for each corpus

### FR-8: Visualization
- Required: 4×2 heatmap per encoder (2 heatmaps total) with 0.95 threshold annotated
- Optional: Distribution histograms of all pairwise similarities per source
- Optional: t-SNE/PCA 2D projection of all 6 corpus embeddings colored by source
- Save all figures to `h-e1/figures/`

---

## 4. Data Specification

| Role | Dataset ID | Split | Size | Load Method |
|------|-----------|-------|------|-------------|
| HumanEval-train | `openai/openai_humaneval` | test | 164 | HF datasets |
| MBPP-train | `google-research-datasets/mbpp` (sanitized) | train | ~374 | HF datasets |
| LeetCode | `newfacade/LeetCodeDataset` | train | ~2500 Python | HF datasets |
| Equal-mix | Constructed (seed=42) | — | ~492 or 164 | Sample from above |
| HumanEval+ | `evalplus/humanevalplus` | test | 164 | HF datasets |
| MBPP+ | `evalplus/mbppplus` | test | 378 | HF datasets |

All datasets auto-download via HuggingFace Hub — no manual download required.

---

## 5. Non-Functional Requirements

- **Runtime:** < 30 minutes total on single GPU (batch_size=32)
- **Memory:** < 8 GB VRAM (CodeBERT ~500MB, MiniLM ~80MB; batched encoding)
- **Reproducibility:** Seed=42 for all random sampling; deterministic encoding
- **No training:** No optimizer, no loss, no gradient computation

---

## 6. Success Criteria

| Criterion | Threshold | Type |
|-----------|-----------|------|
| Code runs without error | 0 runtime exceptions | Required |
| Embedding shapes correct | (N, 768) CodeBERT, (N, 384) MiniLM | Required |
| Gate satisfied | At least 1 of 16 similarities < 0.95 | MUST_WORK gate |
| Encoder concordance | Both encoders show same qualitative pattern | Desired |
| Visualization saved | 2 heatmaps in h-e1/figures/ | Required |

---

## 7. Dependencies

### 7.1 Python Packages
```
transformers>=4.43.0
sentence-transformers>=2.2.0
datasets>=2.14.0
torch>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
scikit-learn>=1.3.0  # for t-SNE
tqdm>=4.65.0
```

### 7.2 External Resources
- HuggingFace Hub access required (5 dataset + 2 model downloads, ~2–3 GB total)
- GPU optional (CPU fallback supported)

---

## 8. Constraints

- No custom model architectures — pretrained checkpoints only
- No fine-tuning — encoding only
- HumanEval split "test" used as training source (following literature convention; all 164 problems)
- Equal-mix size: document whether 492 or 164 final count in experiment log

---

## 9. Evaluation Metrics Summary

- **Primary:** 4×2×2 mean pairwise cosine similarity matrix (16 values)
- **Gate metric:** `min(sim_matrix_codebert.min(), sim_matrix_minilm.min()) < 0.95`
- **Diagnostic:** Std of 16 values (expect > 0.01), distribution histograms
