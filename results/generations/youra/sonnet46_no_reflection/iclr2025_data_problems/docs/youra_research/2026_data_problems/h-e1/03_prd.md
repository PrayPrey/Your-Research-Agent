# Product Requirements Document: h-e1
## Contamination Geometry Decomposition Exists

**Hypothesis ID:** h-e1
**Type:** EXISTENCE (PoC)
**Date:** 2026-05-13
**Phase:** 3 - Implementation Planning
**Source:** 02c_experiment_brief.md

---

## 1. Executive Summary

This PRD defines the implementation requirements for hypothesis h-e1: "Contamination Geometry Decomposition Exists." The experiment verifies that corpus-side geometric signals (max 13-gram overlap count, SBERT cosine similarity) can stratify benchmark items into geometry zones (lexical / semantic / indeterminate), and that detector families exhibit distinct recall patterns per stratum. Specifically, n-gram detectors should achieve recall ≥ 0.80 in the lexical stratum and ≤ 0.40 in the semantic stratum, while Min-K%++ F1 variance across three corpora (The Pile, C4, RedPajama) should be ≥ 0.15.

**PoC Pass Condition:** Geometry-stratified recall separation confirmed (N-gram recall_lexical > recall_semantic) AND Min-K%++ F1 variance > 0.

---

## 2. Problem Statement

Foundation model evaluation benchmarks (MMLU, HellaSwag, GSM8K) may be contaminated in pretraining corpora (The Pile, C4, RedPajama). Current contamination detection methods (n-gram overlap, MIA-based, embedding similarity) are applied uniformly without accounting for the nature of contamination. This experiment tests whether corpus-side geometry signals determine which detector family performs best—a prerequisite for the broader routing hypothesis (H-GeomRoute-v1).

**Root Cause:** Detector families operate on orthogonal signal types (exact lexical matching vs. memorization likelihood vs. semantic proximity), which are differentially effective depending on the type of corpus overlap present.

---

## 3. Objectives and Success Criteria

### Primary Success Criteria (MUST_WORK gate)
- **SC-1:** N-gram recall ≥ 0.80 in lexical stratum (high 13-gram overlap items)
- **SC-2:** N-gram recall ≤ 0.40 in semantic stratum (high SBERT cosine, low 13-gram items)
- **SC-3:** Min-K%++ F1 variance ≥ 0.15 across The Pile / C4 / RedPajama for MMLU or HellaSwag

### Secondary Success Criteria
- **SC-4:** Indeterminacy rate in [10%, 50%] (blind spot confirmed, routing remains useful)

### PoC Pass Condition (minimal bar)
1. Code runs without error
2. N-gram recall_lexical > recall_semantic (directional separation confirmed)
3. Min-K%++ F1 variance > 0 (any variance detected)

### Fail Condition (stop chain)
N-gram recall ≥ 0.60 in semantic stratum OR Min-K%++ variance < 0.10

---

## 4. Data Specification

### 4.1 Benchmark Datasets (Evaluation Items)

| Dataset | HuggingFace ID | Split | Items | Domain |
|---------|---------------|-------|-------|--------|
| MMLU | `cais/mmlu`, config=`all` | `test` | ~14K | Knowledge/factual |
| HellaSwag | `Rowan/hellaswag` | `validation` | ~10K | Commonsense completion |
| GSM8K | `openai/gsm8k`, config=`main` | `test` | ~1.3K | Math reasoning |

**Total:** ~25K items across 3 benchmarks

### 4.2 Pretraining Corpora (Geometry Index Sources)

| Corpus | HuggingFace ID | Notes |
|--------|---------------|-------|
| The Pile | `EleutherAI/pile` | 825GB; streaming; pre-computed 13-gram indices available |
| C4 | `allenai/c4`, config=`en` | ~13TB; use streaming + subset |
| RedPajama | `togethercomputer/RedPajama-Data-1T` | Streaming |

**Loading:** HuggingFace `datasets` library with `streaming=True` for corpora.

### 4.3 Data Loading Code

```python
from datasets import load_dataset

# Benchmarks (standard download)
mmlu = load_dataset("cais/mmlu", "all", split="test")
hellaswag = load_dataset("Rowan/hellaswag", split="validation")
gsm8k = load_dataset("openai/gsm8k", "main", split="test")

# Corpora (streaming)
pile = load_dataset("EleutherAI/pile", split="train", streaming=True)
c4 = load_dataset("allenai/c4", "en", split="train", streaming=True)
redpajama = load_dataset("togethercomputer/RedPajama-Data-1T", split="train", streaming=True)
```

### 4.4 Contamination Rate
Equal-prevalence subsampling at 10% contamination rate per benchmark-corpus pair.

---

## 5. Functional Requirements

### FR-1: Corpus Index Construction
- **FR-1a:** Build 13-gram inverted index for each of 3 corpora using EleutherAI/lm-evaluation-harness pipeline (`generate_13_grams.py` → `sort_13_gram_buckets.py` → `compress_and_package.py`)
- **FR-1b:** Build SBERT FAISS index (IndexFlatIP) using `all-MiniLM-L6-v2` embeddings (normalized) for each corpus
- **FR-1c:** Support streaming corpus ingestion to handle large corpora (C4 ~13TB, RedPajama)

### FR-2: Geometry Feature Extraction
- **FR-2a:** Compute max 13-gram overlap count per benchmark item × corpus
- **FR-2b:** Compute max SBERT cosine similarity per benchmark item × corpus (nearest neighbor in FAISS index)
- **FR-2c:** Output geometry feature matrix: shape `(N_items, 2)` — (ngram_count, cosine) per item-corpus pair

### FR-3: Stratum Assignment
- **FR-3a:** Compute top-quartile thresholds (75th percentile) of each geometry feature across all benchmark items × corpora
- **FR-3b:** Assign items to strata: `lexical` (ngram_count ≥ lexical_thresh), `semantic` (cosine ≥ semantic_thresh), `indeterminate` (neither)
- **FR-3c:** Handle overlap (item in both lexical and semantic): assign to `lexical` (higher precision, lower recall requirement)

### FR-4: Detector Evaluation — N-gram (Detector Family 1)
- **FR-4a:** Apply EleutherAI 13-gram inverted index pipeline to each benchmark item
- **FR-4b:** Output binary contamination label (contaminated=1/clean=0) + max n-gram match count per item
- **FR-4c:** Compute per-stratum recall for n-gram detector across all benchmark-corpus pairs

### FR-5: Detector Evaluation — Min-K%++ (Detector Family 3)
- **FR-5a:** Apply zjysteven/mink-plus-plus `run.py` with k=20% default on Llama-2-7B, Mistral-7B, Pythia-7B
- **FR-5b:** Compute F1 per corpus (The Pile, C4, RedPajama) for MMLU and HellaSwag
- **FR-5c:** Compute F1 variance across 3 corpora per benchmark

### FR-6: Detector Evaluation — Embedding Similarity (Detector Family 2)
- **FR-6a:** Apply ntunlp/LLMSanitize embedding similarity method for each benchmark item × corpus
- **FR-6b:** Output binary contamination label per item

### FR-7: Detector Evaluation — DC-PDD (Detector Family 4)
- **FR-7a:** Apply DC-PDD with fixed reference model (Pythia-2.8B as neutral-corpus reference)
- **FR-7b:** Per Zhang et al. 2024 implementation

### FR-8: Detector Evaluation — ConStat (Detector Family 5)
- **FR-8a:** Apply ConStat (longest contaminated substring) per Singh et al. 2024
- **FR-8b:** Via ntunlp/LLMSanitize library

### FR-9: Ground Truth Generation (Approach A + B)
- **FR-9a (Approach A):** Known inclusion audit — Pythia-7B test items known to appear in The Pile (as positive labels)
- **FR-9b (Approach B):** Simulated leakage — 3 injection regimes via lm-sys/llm-decontaminator:
  - Uniform contamination
  - Clustered contamination
  - Paraphrased injection

### FR-10: Metric Computation
- **FR-10a:** Per-stratum recall for n-gram detector (primary metric SC-1, SC-2)
- **FR-10b:** Min-K%++ F1 variance across corpora (primary metric SC-3)
- **FR-10c:** Indeterminacy rate (fraction of items where no detector has F1 margin ≥ 0.05 above second-best)
- **FR-10d:** Bootstrap CI (N=10,000 iterations) for 95% CI on all recall/F1 estimates

### FR-11: Visualization
- **FR-11a (Required):** Gate metrics comparison bar chart — N-gram recall (lexical/semantic strata) vs. targets + Min-K%++ F1 variance vs. target
- **FR-11b:** 2D contamination phase diagram — scatter of ~25K items in (max_13gram × max_cosine) space, colored by dominant detector family; indeterminate zone in grey
- **FR-11c:** Per-stratum F1 heatmap — 5 detectors × 3 strata × 3 corpora
- **FR-11d:** Min-K%++ F1 variance bar chart per benchmark
- **FR-11e:** Indeterminacy rate pie chart per benchmark
- **Output:** All figures saved to `h-e1/figures/`

---

## 6. Non-Functional Requirements

### NFR-1: Performance
- Single GPU (A100) execution
- Total compute budget: 24-48 GPU-hours
- SBERT encoding batch size: 256
- Must handle streaming corpora without OOM

### NFR-2: Reproducibility
- Fixed seed: 42
- Single run (no multiple seeds for EXISTENCE PoC)
- Bootstrap CI for statistical uncertainty

### NFR-3: Infrastructure
- Python environment with CUDA support
- Set `CUDA_VISIBLE_DEVICES` before execution (lowest memory GPU)
- No distributed training required

### NFR-4: Code Quality
- Modular design (geometry_features.py, detectors/, evaluation/, visualization/)
- All figures auto-saved to `h-e1/figures/`

---

## 7. Dependencies

### 7.1 Python Packages
```
torch>=2.0.0
transformers>=4.35.0
datasets>=2.14.0
sentence-transformers>=2.2.0
faiss-gpu>=1.7.4  # or faiss-cpu
scikit-learn>=1.3.0
scipy>=1.11.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
pyyaml>=6.0
tqdm>=4.65.0
llmsanitize  # pip install llmsanitize
```

### 7.2 External Repositories (Clone/Install)
| Repository | Purpose | Priority |
|-----------|---------|----------|
| zjysteven/mink-plus-plus | Min-K%++ official implementation | ⭐⭐⭐ Critical |
| EleutherAI/lm-evaluation-harness | N-gram 13-gram pipeline | ⭐⭐⭐ Critical |
| lm-sys/llm-decontaminator | Paraphrased injection (Approach B) | ⭐⭐ Important |

### 7.3 Models (HuggingFace)
| Model | HF ID | Purpose |
|-------|-------|---------|
| Llama-2-7B | `meta-llama/Llama-2-7b-hf` | Min-K%++ evaluation |
| Mistral-7B | `mistralai/Mistral-7B-v0.1` | Min-K%++ evaluation |
| Pythia-7B | `EleutherAI/pythia-6.9b` | Min-K%++ + ground truth (Pile-trained) |
| Pythia-2.8B | `EleutherAI/pythia-2.8b` | DC-PDD reference model |
| all-MiniLM-L6-v2 | `sentence-transformers/all-MiniLM-L6-v2` | SBERT geometry feature |

---

## 8. Out of Scope

- Training any ML model (EXISTENCE PoC — no gradient-based training)
- Routing classifier training (Phase H-M3)
- Cross-corpus importance weighting (Phase H-M4)
- Hypotheses H-M1 through H-M4

---

## 9. Implementation Notes

### 9.1 Key Implementation Reference
- GeometryStratifier class defined in 02c_experiment_brief.md Section "Core Mechanism Implementation"
- EleutherAI n-gram pipeline: `generate_13_grams.py` → `sort_13_gram_buckets.py` → `compress_and_package.py`
- Min-K%++ entry point: `zjysteven/mink-plus-plus/run.py` with `--method minkpp`

### 9.2 Stratum Assignment Logic
```python
strata = "indeterminate"
if ngram_count >= lexical_thresh:  strata = "lexical"
elif cosine >= semantic_thresh:    strata = "semantic"
```

### 9.3 Metric Implementation
```python
from sklearn.metrics import recall_score, f1_score
import numpy as np

recall_lexical = recall_score(y_true[lexical_mask], y_pred_ngram[lexical_mask])
recall_semantic = recall_score(y_true[semantic_mask], y_pred_ngram[semantic_mask])
f1_per_corpus = [f1_score(y_true_c, y_pred_minkpp_c) for c in corpora]
variance = np.var(f1_per_corpus)
indeterminate_rate = np.mean((top1_f1 - top2_f1) < 0.05)
```

---

## Appendix: Traceability

| FR | Phase 2C Source |
|----|----------------|
| FR-1 (Corpus Index) | Section: Training Protocol |
| FR-2 (Geometry Features) | Section: Proposed Model — GeometryStratifier |
| FR-3 (Stratum Assignment) | Section: Proposed Model — assign_strata |
| FR-4 (N-gram Detector) | Section: Baseline Model; Repo B.2 |
| FR-5 (Min-K%++) | Section: Training Protocol; Repo B.1 |
| FR-6 (Embedding Similarity) | Section: Training Protocol; Repo B.3 |
| FR-7 (DC-PDD) | Section: Training Protocol |
| FR-8 (ConStat) | Section: Training Protocol; Repo B.3 |
| FR-9 (Ground Truth) | Section: Training Protocol (Approach A/B) |
| FR-10 (Metrics) | Section: Evaluation |
| FR-11 (Visualization) | Section: Visualization Requirements |

---

*Generated by Phase 3 Implementation Planning — UNATTENDED mode*
*Source: h-e1/02c_experiment_brief.md*
