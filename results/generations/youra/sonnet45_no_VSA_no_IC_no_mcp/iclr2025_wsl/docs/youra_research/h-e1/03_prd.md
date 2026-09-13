# Product Requirements Document: H-E1 Knowledge Base Extractor

**Date:** 2026-08-25  
**Hypothesis ID:** h-e1  
**Hypothesis Type:** EXISTENCE  
**Gate Type:** MUST_WORK  

---

## Executive Summary

Build a deterministic knowledge base (KB) extraction system that proves Papers With Code (PWC) catalog contains sufficient metadata to construct a (Dataset, Benchmark, Metric) triple KB covering >80% of well-known DL datasets. This is the foundation hypothesis — all downstream hypotheses depend on this KB existing.

**Success Criteria:**
- Coverage: >80% of 50 well-known datasets found in extracted KB
- Metadata Completeness: >95% of triples have all (D,B,M) fields populated
- Execution Time: <15 minutes (full extraction + evaluation)

**Gate Consequence:** MUST_WORK — failure stops entire workflow, requires exploring alternative catalogs.

---

## Functional Requirements

### FR1: Papers With Code API Client
- Install and configure `paperswithcode-client` Python library
- Handle pagination for datasets (4,000+ total entries)
- Implement exponential backoff for rate limit compliance
- Cache all API responses locally to `/data/pwc_cache/responses/`

### FR2: Triple Extraction Engine
- For each dataset: query associated benchmarks via API
- For each benchmark: extract evaluation metrics
- Store as structured triple: `{dataset: str, benchmark: str, metric: str}`
- Handle missing fields (skip incomplete triples, log warnings)

### FR3: Knowledge Base Storage
- Output format: YAML (human-readable for Phase 4 inspection)
- File: `/data/pwc_cache/kb.yaml`
- Schema: List of (D,B,M) dictionaries
- Include metadata header: extraction timestamp, API version, triple count

### FR4: Ground Truth Comparison
- Hardcoded list of 50 well-known datasets (vision/NLP/audio/graph/video)
- Exact string matching (case-sensitive) for dataset names
- Report: found datasets, missing datasets, coverage percentage

### FR5: Coverage Metrics
- Primary: `coverage = (# found) / 50`
- Secondary: `completeness = (# complete triples) / (# total triples)`
- Output: JSON summary file with both metrics

### FR6: Baseline Comparison
- Random baseline: 50% coverage (select 25/50 datasets randomly, seed=42)
- Compare: extracted coverage vs random baseline
- Assertion: extracted > baseline (else fail)

### FR7: Visualization Generation
- Bar chart: coverage comparison (random vs extracted)
- Pie chart: domain distribution (vision/NLP/audio/graph/video)
- Table: missing datasets (if any)
- Save figures to `h-e1/figures/`

---

## Non-Functional Requirements

### NFR1: Performance
- Full extraction: <10 minutes (API queries + processing)
- Retry limit: 3 attempts per failed API call
- Timeout: 30s per API request

### NFR2: Reliability
- API failures: log errors, continue with partial results
- Cache hit: skip re-downloading if response exists (<24h old)
- Graceful degradation: report coverage even if <100% API queries succeed

### NFR3: Reproducibility
- Fixed random seed: 42 (for baseline comparison)
- API snapshot: Jan 2026 (note: live API, not versioned snapshot)
- Deterministic output order (sort triples by dataset name)

### NFR4: Code Quality
- Single Python script: `extract_kb.py` (no multi-file structure for PoC)
- No external config files (all parameters hardcoded)
- Minimal dependencies: `paperswithcode-client`, `pyyaml`, `matplotlib`, `pandas`

---

## Data Requirements

### Input Data
- **Source:** Papers With Code API (https://paperswithcode.com/api/v1/)
- **Access Method:** Official Python client (`paperswithcode-client`)
- **Expected Volume:** 4,000+ datasets, 3,000+ benchmarks
- **Rate Limit:** Unknown (use exponential backoff)

### Output Data
- **KB File:** `/data/pwc_cache/kb.yaml` (~500KB estimated)
- **Metrics Summary:** `/data/pwc_cache/metrics.json` (~1KB)
- **Figures:** `h-e1/figures/*.png` (3 figures)

### Ground Truth Dataset List (50 entries)
```yaml
vision: [CIFAR-10, CIFAR-100, ImageNet, COCO, ADE20K, Pascal VOC, MS COCO, CelebA, Places365, STL-10, SVHN, Fashion-MNIST, MNIST, Caltech-101, Caltech-256]
nlp: [GLUE, SuperGLUE, SQuAD, WMT, WikiText-103, IMDB, SST-2, CoNLL-2003, MultiNLI, SNLI, QQP, MRPC, RTE, WNLI, CoLA]
audio: [LibriSpeech, Common Voice, TIMIT, VoxCeleb, AudioSet]
graph: [Cora, CiteSeer, PubMed, Reddit, ogbn-arxiv]
video: [Kinetics, UCF-101, Something-Something, ActivityNet, HMDB51]
other: [Omniglot, miniImageNet, tieredImageNet, CUB-200, Stanford Cars]
```

---

## Success Validation

### Acceptance Tests
1. **AT1:** Extract KB without crashes (script runs to completion)
2. **AT2:** Coverage >80% (40/50 datasets found)
3. **AT3:** Completeness >95% (all triples have D,B,M fields)
4. **AT4:** Extracted coverage > random baseline (by >10 percentage points)
5. **AT5:** All 3 figures generated and saved to `h-e1/figures/`

### Failure Modes
- **FM1:** Coverage <80% → STOP workflow, explore alternative catalogs
- **FM2:** API unreachable → Retry 3x, then fail with error log
- **FM3:** Completeness <95% → Warn (does not fail gate), proceed with partial KB

---

## Technical Constraints

### Dependencies
- Python 3.9+
- `paperswithcode-client==0.3.0` (or latest stable)
- `pyyaml>=5.4`
- `matplotlib>=3.5`
- `pandas>=1.3`

### Environment
- Cache directory: `/data/pwc_cache/` (must exist before run)
- Network: Outbound HTTPS to `paperswithcode.com` (port 443)
- Disk: ~1GB free space (for API cache + KB)

### No Training Required
This is a deterministic extraction task — no model training, no GPU, no hyperparameter tuning.

---

## Deliverables

1. **KB File:** `/data/pwc_cache/kb.yaml` (structured (D,B,M) triples)
2. **Metrics Summary:** `/data/pwc_cache/metrics.json` (coverage, completeness)
3. **Figures:** `h-e1/figures/coverage_comparison.png`, `domain_distribution.png`, `missing_datasets.txt`
4. **Validation Report:** Console output + saved to `h-e1/04_validation.md`

---

## Out of Scope

- Multi-version KB tracking (only single Jan 2026 snapshot)
- API authentication (public read-only API)
- Web scraping fallback (API-only approach)
- Dataset aliasing / fuzzy matching (exact string match only)
- Benchmark result extraction (focus on D,B,M structure, not performance numbers)

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| API rate limit exceeded | Medium | High | Exponential backoff, local caching |
| Coverage <80% | Low | Critical | Validate ground-truth list beforehand, check API stats |
| API schema change | Low | Medium | Pin client version, document API version |
| Incomplete metadata | Medium | Low | Log warnings, continue with partial data |

---

## Phase 4 Handoff Notes

**For Coder:**
- This is a **deterministic PoC** — no training loops, no model checkpoints
- Single script: `extract_kb.py` (run once, output KB + metrics)
- All parameters hardcoded (no config files)
- Use `if __name__ == '__main__':` block for standalone execution
- Print progress to console (dataset X/Y processed)

**For Validator:**
- Verify: KB file exists, non-empty, valid YAML
- Check: metrics.json has `coverage` and `completeness` keys
- Assert: `coverage > 0.80` (MUST_WORK gate)
- Figures: all 3 PNG files exist in `h-e1/figures/`

---

*This PRD defines the minimum viable KB extraction system to validate H-E1. No over-engineering.*
