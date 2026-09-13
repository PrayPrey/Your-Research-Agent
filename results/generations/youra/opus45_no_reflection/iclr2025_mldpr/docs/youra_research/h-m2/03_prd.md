# Product Requirements Document: H-M2

**Hypothesis:** MMLU, BIG-Bench, HumanEval and similar emergent-capability benchmarks created post-foundation-model emergence (>80% post-2020)

**Date:** 2026-08-18
**Author:** Anonymous
**Type:** MECHANISM
**Gate:** SHOULD_WORK

---

## 1. Executive Summary

This experiment validates that emergent-capability benchmarks (MMLU, BIG-Bench, HumanEval, TruthfulQA, GSM8K) were primarily created after foundation model emergence (post-2020). Success criterion: >80% of classified emergent-capability benchmarks have creation dates >= 2020.

---

## 2. Problem Statement

Foundation models (GPT-3, ViT, BERT successors) emerged 2019-2021, creating new evaluation needs. H-M2 tests whether this paradigm shift drove creation of specialized benchmarks for emergent capabilities that didn't exist before.

---

## 3. Functional Requirements

### FR-1: Data Acquisition
- **FR-1.1**: Download PWC datasets.json from HuggingFace `pwc-archive/datasets`
- **FR-1.2**: Extract benchmark metadata: name, description, tasks, introducing_paper
- **FR-1.3**: Fallback: Semantic Scholar API lookup for missing paper dates

### FR-2: Benchmark Classification
- **FR-2.1**: Classify benchmarks as "emergent-capability" or "traditional"
- **FR-2.2**: Use keyword matching (reasoning, emergent, capability, understanding, etc.)
- **FR-2.3**: Use direct name matching (MMLU, BIG-Bench, HumanEval, etc.)
- **FR-2.4**: Use task-type classification (QA, code-generation, math-word-problems)

### FR-3: Date Extraction
- **FR-3.1**: Parse paper dates from PWC metadata
- **FR-3.2**: Lookup missing dates via Semantic Scholar API
- **FR-3.3**: Extract year from paper publication date

### FR-4: Temporal Analysis
- **FR-4.1**: Compute post-2020 ratio for emergent-capability benchmarks
- **FR-4.2**: Compare to 0.80 threshold
- **FR-4.3**: Compute creation rate acceleration (post-2020 vs pre-2020)

### FR-5: Visualization
- **FR-5.1**: Generate gate metrics bar chart (ratio vs threshold)
- **FR-5.2**: Generate benchmark creation timeline histogram
- **FR-5.3**: Generate cumulative creation curve with GPT-3 marker

---

## 4. Data Specification

### Primary Dataset
- **Name**: Papers With Code Benchmark Metadata
- **Source**: HuggingFace `pwc-archive/datasets`
- **Format**: JSON with benchmark metadata
- **Size**: ~4,500+ datasets, ~2,000+ with identifiable dates
- **Auto-download**: Yes (via datasets library)

```python
from datasets import load_dataset
pwc_datasets = load_dataset("pwc-archive/datasets", split="train")
```

### Fallback Data Source
- **Name**: Semantic Scholar API
- **URL**: https://api.semanticscholar.org/
- **Purpose**: Date lookup for benchmarks without PWC paper links

---

## 5. Success Criteria

### Primary Gate (SHOULD_WORK)
- **Metric**: post_2020_ratio > 0.80
- **Meaning**: >80% of emergent-capability benchmarks created 2020 or later

### Secondary Metrics
- Creation rate acceleration ratio
- Semantic similarity to foundation model capabilities

---

## 6. Non-Functional Requirements

### NFR-1: Performance
- Total pipeline runtime: <20 minutes
- API rate limiting: 100 requests/min for Semantic Scholar

### NFR-2: Reliability
- Handle missing paper links gracefully
- Fallback to manual verification set for key benchmarks

### NFR-3: Reproducibility
- All classification rules documented
- Threshold 2020 hardcoded (not tunable post-hoc)

---

## 7. Dependencies

### 7.1 Python Packages
```
datasets>=2.14.0
requests>=2.28.0
pandas>=1.5.0
matplotlib>=3.6.0
pyyaml>=6.0
```

### 7.2 External APIs
- Semantic Scholar API (backup date lookup)

### 7.3 Reference Implementations
- Papers With Code data: https://github.com/paperswithcode/paperswithcode-data

---

## 8. Out of Scope

- Manual curation of all benchmarks (use rule-based classification)
- Training ML classifier for benchmark categorization
- Scraping original papers for exact publication dates

---

## 9. Acceptance Criteria

1. Code runs without error on full PWC dataset
2. At least 50 benchmarks classified as emergent-capability
3. Post-2020 ratio computed with statistical confidence
4. Visualizations generated and saved to figures/
5. Gate result (PASS/FAIL) determined per threshold

---

*Generated from Phase 2C Experiment Brief*
*Next: Architecture Design*
