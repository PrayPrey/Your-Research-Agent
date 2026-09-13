# Product Requirements Document: KB Extraction Logic (h-m1)

**Date:** 2026-08-25
**Author:** Anonymous
**Hypothesis:** h-m1 (MECHANISM)
**Version:** 1.0

---

## Executive Summary

### Purpose
Implement automated KB extraction logic to validate the hypothesis: Under automated scraping conditions, if KB extraction logic is applied to Papers With Code catalog, then >80% of well-known datasets/benchmarks are captured in the KB, because the catalog's structured format enables reliable automated extraction.

### Success Criteria
- **Primary**: Coverage >80% (40/50 well-known datasets found)
- **Secondary**: Metadata completeness >95% (all triples have D,B,M fields)
- **Baseline Comparison**: Outperform random baseline (~50%) and manual curation (~60-70%)

### Gate
MUST_WORK gate: If coverage <80%, EXPLORE alternative extraction methods or catalog sources.

---

## Problem Statement

h-e1 demonstrated that KB construction from HuggingFace Datasets Hub API achieves 84% coverage (42/50 datasets). h-m1 tests whether automated extraction logic reliably achieves the >80% threshold, validating that the mechanism (automated scraping) is the causal factor for high coverage, not manual intervention.

**Key Challenge**: Prove automated extraction achieves >80% coverage without manual curation steps.

---

## Functional Requirements

### FR-1: Data Acquisition
- **FR-1.1**: Query HuggingFace Datasets Hub API via `list_datasets()` function
- **FR-1.2**: Extract dataset metadata (dataset cards) for each dataset
- **FR-1.3**: Cache API responses locally to avoid rate limits (`h-m1/data/pwc_cache/`)
- **FR-1.4**: Implement exponential backoff for failed API calls
- **FR-1.5**: Handle API deprecation gracefully (fallback mechanisms)

### FR-2: KB Triple Extraction
- **FR-2.1**: For each dataset, infer (Dataset, Benchmark, Metric) triple from metadata
- **FR-2.2**: Default inference rules:
  - Benchmark: `dataset_name + "-benchmark"` if not in metadata
  - Metric: `"accuracy"` if not in metadata
- **FR-2.3**: Store triples in structured format (YAML)
- **FR-2.4**: Validate completeness: all triples must have D,B,M fields populated

### FR-3: Coverage Evaluation
- **FR-3.1**: Load ground-truth list of 50 well-known datasets (5 domains):
  - Vision (15): CIFAR-10, CIFAR-100, ImageNet, COCO, ADE20K, Pascal VOC, MS COCO, CelebA, Places365, STL-10, SVHN, Fashion-MNIST, MNIST, Caltech-101, Caltech-256
  - NLP (15): GLUE, SuperGLUE, SQuAD, WMT, WikiText-103, IMDB, SST-2, CoNLL-2003, MultiNLI, SNLI, QQP, MRPC, RTE, WNLI, CoLA
  - Audio (5): LibriSpeech, Common Voice, TIMIT, VoxCeleb, AudioSet
  - Graph (5): Cora, CiteSeer, PubMed, Reddit, ogbn-arxiv
  - Video (5): Kinetics, UCF-101, Something-Something, ActivityNet, HMDB51
  - Other (5): Omniglot, miniImageNet, tieredImageNet, CUB-200, Stanford Cars
- **FR-3.2**: Compute coverage: `(# datasets found) / 50`
- **FR-3.3**: Identify missing datasets (not found in KB)
- **FR-3.4**: Compute metadata completeness: `(# complete triples) / (# total triples)`

### FR-4: Baseline Comparison
- **FR-4.1**: Implement random baseline (50% coverage, seed=42)
- **FR-4.2**: Compare against manual curation baseline (~60-70% from literature)
- **FR-4.3**: Compare against h-e1 result (84% coverage)

### FR-5: Visualization
- **FR-5.1**: Coverage bar chart (random, manual, h-e1, h-m1)
- **FR-5.2**: Domain distribution pie chart (coverage by domain)
- **FR-5.3**: Missing datasets table (if coverage <100%)
- **FR-5.4**: Metadata completeness histogram
- **FR-5.5**: Gate metrics comparison (target 80% vs actual)

---

## Non-Functional Requirements

### NFR-1: Performance
- Execution time: <10 minutes for full KB extraction
- API call rate: Respect HuggingFace rate limits

### NFR-2: Reliability
- Handle API failures gracefully (retry logic)
- Cache responses to avoid repeated calls
- Validate data integrity (completeness checks)

### NFR-3: Maintainability
- Code structure: Modular (`KBExtractionLogic` class)
- Documentation: Inline comments for inference rules
- Reproducibility: Fixed random seed (42)

### NFR-4: Compatibility
- Python 3.8+
- Dependencies: `datasets` library, `pyyaml`, `sklearn`

---

## Data Specifications

### Input Data
- **Source**: HuggingFace Datasets Hub API
- **Access Method**: `datasets.list_datasets()` + `load_dataset_builder()`
- **Expected Volume**: 40,000+ datasets cataloged
- **Sample Rate**: Full catalog (no sampling)

### Output Data
- **KB Format**: YAML file with list of (D,B,M) triples
- **Triple Schema**:
  ```yaml
  - dataset: "CIFAR-10"
    benchmark: "cifar10-benchmark"
    metric: "accuracy"
  ```
- **Output Path**: `h-m1/data/pwc_cache/kb.yaml`

### Ground Truth Data
- **Format**: Python list (50 dataset names)
- **Source**: Standard benchmarks from DL literature (h-e1 validated)
- **Storage**: Hardcoded in evaluation module

---

## Technical Constraints

### Dependencies
- **Required Libraries**:
  - `datasets` (HuggingFace)
  - `pyyaml`
  - `sklearn.metrics` (for evaluation)
- **Installation**: `pip install datasets pyyaml scikit-learn`

### System Requirements
- Internet connectivity (API access)
- Disk space: ~500MB for cache
- Python 3.8+

### Known Limitations
- 8/50 datasets missing in h-e1 (Pascal VOC, MS COCO, STL-10, SST-2, Common Voice, tieredImageNet, CUB-200, Stanford Cars)
- API deprecation risk (HuggingFace may change API)
- Metadata quality varies across datasets

---

## Success Metrics

### Primary Metrics
1. **Coverage**: `(# found) / 50 > 0.80` (MUST_WORK gate)
2. **Metadata Completeness**: `(# complete triples) / (# total triples) > 0.95`

### Secondary Metrics
1. Baseline comparison: h-m1 > random baseline (+30pp minimum)
2. Baseline comparison: h-m1 > manual curation (+10pp minimum)
3. h-e1 comparison: h-m1 ≈ h-e1 (±5pp tolerance)

### Gate Condition
- **PASS**: Coverage ≥80% AND Completeness ≥95%
- **FAIL**: Coverage <80% → EXPLORE alternative extraction methods

---

## Dependencies

### Prerequisite Hypotheses
- **h-e1 (VALIDATED)**: Provides ground-truth list, coverage baseline (84%), validated HuggingFace API approach

### External Dependencies
- HuggingFace Datasets Hub API availability
- Internet connectivity
- Python environment

### Data Dependencies
- Ground-truth list from h-e1
- HuggingFace API endpoint

---

## Out of Scope

- Manual curation of missing datasets
- Alternative API sources (Papers With Code API is deprecated)
- HTML scraping (fragile, high maintenance)
- Semantic similarity matching for dataset names
- Benchmark-level analysis (focus is dataset-level coverage)

---

## Appendix

### Reference Implementations
- **h-e1 validation**: 84% coverage using HuggingFace API
- **HuggingFace datasets library**: Official client (19k+ GitHub stars)
- **Code pattern**: `list_datasets()` → `load_dataset_builder()` → extract metadata

### Risk Mitigation
- **API deprecation**: Cache responses locally, maintain fallback sources
- **Missing datasets**: Document coverage gaps, identify patterns
- **Low coverage**: Fallback to manual hybrid approach

### Related Documents
- Phase 2C Experiment Brief: `h-m1/02c_experiment_brief.md`
- h-e1 Validation Report: `h-e1/04_validation.md`
- h-e1 Architecture: `h-e1/03_architecture.md`
