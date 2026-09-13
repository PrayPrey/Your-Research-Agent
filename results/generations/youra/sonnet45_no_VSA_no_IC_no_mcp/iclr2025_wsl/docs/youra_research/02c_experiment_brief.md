# Experiment Design Brief: H-E1 Knowledge Base Constructability

**Hypothesis ID:** h-e1  
**Date:** 2026-08-25  
**Status:** DESIGNED

---

## 1. Hypothesis Overview

**Statement:** Under constraint-driven DL research contexts (existing datasets/benchmarks only), if Papers With Code catalog (Jan 2026) is scraped and structured, then a (Dataset, Benchmark, Metric) triple knowledge base covering >80% of well-known DL datasets/benchmarks can be constructed, because the catalog provides comprehensive metadata on dataset-benchmark-metric relationships.

**Type:** EXISTENCE  
**Gate:** MUST_WORK  
**Prerequisites:** None

**Success Criteria:**
- Primary: Coverage >80% (40/50 well-known datasets present in KB)
- Secondary: Metadata completeness (each entry has D, B, M fields populated)

---

## 2. Experiment Design

### 2.1 Dataset Preparation

**Dataset Type:** standard  
**Dataset Name:** Papers With Code Catalog Snapshot  
**Source:** https://paperswithcode.com/  

**Preparation Steps:**

1. **Catalog Acquisition:**
   - Use Papers With Code public API: `https://paperswithcode.com/api/v1/`
   - Endpoints to scrape:
     - `/datasets/` - List all datasets with metadata
     - `/benchmarks/` - Benchmark task information
     - `/evaluation-tables/` - Dataset-benchmark-metric associations
   - Target: January 2026 snapshot (current date)
   - Format: JSON responses, save as structured YAML/JSON KB

2. **Ground Truth Construction:**
   - Curate list of 50 well-known DL datasets across domains:
     - **Vision:** CIFAR-10, CIFAR-100, ImageNet, COCO, Pascal VOC, MNIST, Fashion-MNIST, CelebA, Places365, ADE20K
     - **NLP:** GLUE, SuperGLUE, SQuAD, WMT14/WMT19, Penn Treebank, WikiText, IMDB, AG News, SST-2, CoNLL-2003
     - **Speech:** LibriSpeech, Common Voice, TIMIT, VoxCeleb, AudioSet
     - **Multimodal:** VQA, Conceptual Captions, Flickr30k, MS-COCO Captions, CLEVR
     - **Graph/RL:** Cora, Citeseer, PubMed, Atari Benchmarks, MuJoCo, OpenAI Gym
     - **Other:** Kinetics-400, UCF-101, KITTI, ModelNet, ShapeNet
   - Each entry must have:
     - Dataset name
     - At least one standard benchmark task
     - At least one standard evaluation metric

3. **KB Construction:**
   - Parse API responses into (Dataset, Benchmark, Metric) triples
   - Schema: `{dataset: str, benchmark: str, metrics: List[str], domain: str, url: str}`
   - Store in structured format (YAML/JSON)
   - Index by dataset name for fast lookup

**Cache Strategy:**
- API responses cached to `/data/pwc_cache/`
- Ground truth list stored as `/data/ground_truth_datasets.yaml`
- Final KB stored as `/data/knowledge_base.yaml`

**Verification:**
- Successful API access to all three endpoints
- Ground truth list contains exactly 50 entries with complete metadata
- KB structure validates against schema

---

### 2.2 Baseline Experiment

**Experiment Type:** Coverage Analysis (no model training required)

**Implementation:**

1. **KB Extraction:**
   - Implement scraper: `scripts/scrape_pwc.py`
   - Parse JSON responses from PWC API
   - Extract (D, B, M) triples from evaluation tables
   - Build knowledge base structure

2. **Coverage Measurement:**
   - Load ground truth list (50 datasets)
   - For each dataset in ground truth:
     - Check if dataset name exists in KB (exact match or fuzzy match)
     - Verify metadata completeness (benchmark + metric fields populated)
   - Calculate coverage: `(# found) / 50 * 100%`

3. **Metadata Quality Check:**
   - For each KB entry:
     - Verify D field (dataset name) is non-empty
     - Verify B field (benchmark/task) is non-empty
     - Verify M field (metrics list) has ≥1 metric
   - Calculate completeness: `(# complete entries) / (# total entries) * 100%`

**No Training Required:** This is a data construction and validation experiment, not a model training experiment.

**Computational Requirements:**
- API scraping: ~1-2 hours (rate-limited requests)
- Coverage analysis: <5 minutes (simple lookup)
- Total: ~2 hours

---

### 2.3 Evaluation Protocol

**Primary Metric:** Coverage Percentage
- Formula: `(# ground truth datasets found in KB) / 50 * 100%`
- Success threshold: >80% (≥40 datasets found)

**Secondary Metric:** Metadata Completeness
- Formula: `(# entries with D, B, M populated) / (# total KB entries) * 100%`
- Success threshold: >90%

**Evaluation Steps:**

1. **Exact Match Search:**
   - For each ground truth dataset, search KB by exact name
   - Record: found/not_found

2. **Fuzzy Match Search (for misses):**
   - Apply fuzzy string matching (Levenshtein distance <3)
   - Handle variations: "ImageNet" vs "ImageNet-1K", "CIFAR-10" vs "CIFAR10"
   - Record: fuzzy_found/not_found

3. **Metadata Validation:**
   - For each found entry, check field population
   - Record: complete/incomplete

4. **Analysis:**
   - Generate coverage report by domain (vision/NLP/speech/etc.)
   - Identify systematic gaps (e.g., missing all RL datasets)
   - Document reasons for misses (not in PWC, API parsing error, etc.)

**Output Format:**
```yaml
coverage:
  total_ground_truth: 50
  exact_matches: X
  fuzzy_matches: Y
  total_found: X+Y
  coverage_percentage: (X+Y)/50 * 100
  
completeness:
  total_kb_entries: N
  complete_entries: M
  completeness_percentage: M/N * 100

by_domain:
  vision:
    total: 10
    found: X
    coverage: X/10 * 100
  nlp:
    total: 10
    found: Y
    coverage: Y/10 * 100
  # ... other domains

missing_datasets:
  - name: "DatasetX"
    reason: "Not in PWC catalog"
  - name: "DatasetY"
    reason: "API parsing error"
```

---

### 2.4 Success/Failure Criteria

**SUCCESS (Gate: MUST_WORK):**
- Primary metric ≥80% (≥40/50 datasets found)
- Secondary metric ≥90% (metadata complete)
- → Proceed to H-M1 (KB Extraction Coverage)

**FAILURE:**
- Primary metric <80%
- → EXPLORE alternatives:
  - HuggingFace Datasets Hub API
  - Google Dataset Search structured data
  - Manual curation from survey papers
- → Document limitation and reassess approach

**PARTIAL SUCCESS:**
- Primary metric 70-79%
- → Analyze gaps by domain
- → If gaps are systematic (e.g., missing all RL datasets), adjust scope
- → If gaps are random (API errors), improve scraper robustness

---

## 3. Implementation Checklist

### Phase 3 (Implementation Planning):
- [ ] Design API scraper architecture
- [ ] Define KB schema (YAML/JSON structure)
- [ ] Plan error handling for rate limits, API changes
- [ ] Design ground truth construction process

### Phase 4 (Coding):
- [ ] Implement `scripts/scrape_pwc.py`
- [ ] Implement `scripts/construct_kb.py`
- [ ] Implement `scripts/evaluate_coverage.py`
- [ ] Implement fuzzy matching logic
- [ ] Create ground truth list (50 datasets)

### Phase 4.5 (Validation):
- [ ] Run scraper on PWC API
- [ ] Build KB from scraped data
- [ ] Evaluate coverage against ground truth
- [ ] Generate coverage report
- [ ] Validate metadata completeness

---

## 4. Known Risks & Mitigations

**Risk 1:** PWC API rate limiting
- Mitigation: Implement exponential backoff, cache responses

**Risk 2:** API structure changes between now and implementation
- Mitigation: Version-pinned API endpoints, fallback to web scraping

**Risk 3:** Dataset name variations (ImageNet vs ImageNet-1K)
- Mitigation: Fuzzy matching, maintain alias dictionary

**Risk 4:** Incomplete API responses (missing benchmark/metric data)
- Mitigation: Multi-source validation (check dataset detail pages), flag incomplete entries

**Risk 5:** Ground truth bias (only well-known datasets)
- Mitigation: Sample across domains, include recent datasets (2023-2025)

---

## 5. Expected Outputs

**Artifacts:**
- `/data/pwc_cache/` - Cached API responses
- `/data/ground_truth_datasets.yaml` - 50 well-known datasets
- `/data/knowledge_base.yaml` - Extracted (D,B,M) KB
- `/results/h-e1_coverage_report.yaml` - Coverage analysis

**Deliverables:**
- Coverage percentage (primary metric)
- Metadata completeness percentage (secondary metric)
- Domain-wise coverage breakdown
- List of missing datasets with reasons
- Validated KB ready for H-M1 testing

---

## 6. Resource Requirements

**Compute:**
- CPU-only (no GPU required)
- 4GB RAM (API responses + KB in memory)
- 500MB disk (cached responses + KB)

**Time:**
- API scraping: 1-2 hours
- KB construction: 10 minutes
- Coverage evaluation: 5 minutes
- Total: ~2-3 hours

**Dependencies:**
- Python 3.8+
- Libraries: `requests`, `pyyaml`, `fuzzywuzzy`, `python-Levenshtein`

---

## 7. Post-Experiment Analysis

**If SUCCESS:**
- Document which domains have highest coverage
- Identify KB entry quality patterns (complete vs incomplete metadata)
- Use validated KB as input to H-M1 (extraction logic verification)

**If FAILURE:**
- Root cause analysis: API coverage gaps vs scraper bugs
- Decision: Fix scraper, switch to alternative source, or manual curation
- Re-evaluate hypothesis if fundamental coverage limitation found

---

## 8. Integration with Downstream Hypotheses

**H-M1 Dependencies:**
- Requires: Validated KB from H-E1
- Uses: KB as ground truth for extraction logic testing

**H-M2 Dependencies:**
- Requires: KB with ≥80% coverage
- Uses: KB for formal verification (∃ (D,B,M) checks)

**Critical Path:**
- H-E1 must achieve ≥80% to unblock entire verification pipeline
- KB quality directly impacts downstream precision/recall metrics

---

**Experiment Design Completed:** 2026-08-25  
**Ready for Phase 3 (Implementation Planning)**
