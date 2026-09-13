# Product Requirements Document: H-M1

**Hypothesis:** The Pile training corpus contains measurable 13-gram overlap (>1% of benchmark content) with standard benchmarks (MMLU, ARC, HellaSwag, WinoGrande).

**Date:** 2026-08-10
**Author:** Anonymous
**Version:** 1.0

---

## 1. Executive Summary

This PRD defines requirements for implementing n-gram overlap detection between The Pile training corpus and standard NLP benchmarks. The experiment validates whether measurable contamination exists at the 13-gram level.

**Success Criteria:** At least one benchmark shows >1% 13-gram overlap with The Pile.

---

## 2. Problem Statement

Language model benchmarks may be contaminated by training data overlap. This hypothesis tests whether The Pile contains verbatim 13-gram sequences from MMLU, ARC, HellaSwag, and WinoGrande test sets.

**Key Question:** Does The Pile contain >1% 13-gram overlap with any standard benchmark?

---

## 3. Functional Requirements

### FR-1: N-gram Extraction Module
- Extract 13-grams from text using whitespace tokenization
- Lowercase normalization for matching
- Support for both training corpus and benchmark text

### FR-2: Pile Indexing Pipeline
- Index all 13-grams from The Pile corpus
- Efficient storage using hash-based indexing
- Support for subset processing (due to corpus size)

### FR-3: Benchmark Processing
- Load benchmark test sets from HuggingFace:
  - MMLU: `cais/mmlu` (~14,042 samples)
  - ARC: `allenai/ai2_arc` ARC-Challenge (~3,548 samples)
  - HellaSwag: `Rowan/hellaswag` (~10,042 samples)
  - WinoGrande: `allenai/winogrande` (~1,267 samples)
- Extract 13-grams from each benchmark item
- Total: ~28,899 evaluation samples (full test splits)

### FR-4: Overlap Computation
- Match benchmark n-grams against Pile index
- Compute per-item overlap percentage
- Aggregate to per-benchmark statistics

### FR-5: Visualization
- Bar chart: overlap % per benchmark
- Distribution histogram per benchmark
- Comparison table with prior work

---

## 4. Data Specification

### 4.1 Training Corpus
| Dataset | Source | Size | Format |
|---------|--------|------|--------|
| The Pile | EleutherAI | 825 GiB | JSONL (zst) |

**Loading:** Direct download from pile.eleuther.ai or HuggingFace `EleutherAI/pile`

### 4.2 Benchmark Test Sets
| Benchmark | Source | Samples | Split |
|-----------|--------|---------|-------|
| MMLU | cais/mmlu | ~14,042 | test |
| ARC-Challenge | allenai/ai2_arc | ~3,548 | test |
| HellaSwag | Rowan/hellaswag | ~10,042 | validation |
| WinoGrande | allenai/winogrande | ~1,267 | validation |

**Loading Code:**
```python
from datasets import load_dataset

mmlu = load_dataset("cais/mmlu", "all", split="test")
arc = load_dataset("allenai/ai2_arc", "ARC-Challenge", split="test")
hellaswag = load_dataset("Rowan/hellaswag", split="validation")
winogrande = load_dataset("allenai/winogrande", "winogrande_xl", split="validation")
```

---

## 5. Non-Functional Requirements

### NFR-1: Scalability
- Handle 825GB corpus processing (parallelizable)
- ~100GB n-gram index storage

### NFR-2: Reproducibility
- Deterministic n-gram extraction
- Documented preprocessing steps

### NFR-3: Compute Resources
- Pile indexing: ~48 GPU-hours (parallelizable)
- Benchmark processing: ~1 hour

---

## 6. Success Criteria

### Primary Gate (SHOULD_WORK)
- At least one benchmark shows >1% 13-gram overlap

### Secondary Criteria
- Overlap varies across benchmarks (not uniform ~0%)
- Results comparable to prior work (Yang et al. found 8-18% in RedPajama)

### Failure Response
- If all benchmarks show <1% overlap: PIVOT to semantic contamination measures

---

## 7. Dependencies

### 7.1 Python Packages
- datasets (HuggingFace)
- zstandard (Pile decompression)
- tqdm (progress tracking)
- matplotlib (visualization)
- pandas (data analysis)

### 7.2 Reference Implementations
- EleutherAI/lm-evaluation-harness: `lm_eval/decontamination/`
- stanford-crfm/data-overlap: HELM-compatible
- nlx-group/overlapy: GPT-3 methodology

---

## 8. Out of Scope

- Model training or fine-tuning
- Semantic similarity measures (future work if n-gram fails)
- Real-time contamination detection
- Full Pile indexing (may use representative subset)

---

## 9. Verification Protocol

### Mechanism Check
```python
def verify_mechanism():
    detector = NgramOverlapDetector(ngram_size=13)
    training = "the quick brown fox jumps over the lazy dog repeatedly"
    test = "the quick brown fox jumps over the lazy dog"
    
    detector.training_ngrams = detector.extract_ngrams(detector.tokenize(training))
    result = detector.compute_overlap(test)
    
    assert result["overlap"] > 0, "Mechanism failed"
    return True
```

### PoC Pass Condition
1. Code runs without error
2. At least one benchmark shows >1% overlap

---

*Generated from Phase 2C Experiment Brief*
*Next: Architecture Design*
