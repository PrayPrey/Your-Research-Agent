# Product Requirements Document: H-E1 Retrospective Corpus Collection

## Executive Summary

**Hypothesis:** H-E1 (EXISTENCE, MUST_WORK gate)  
**Goal:** Validate that published ML research contains sufficient micro-pilot overhead data by collecting ≥30 hypotheses with BOTH 10-sample and full-scale overhead measurements from Papers with Code, conference papers (NeurIPS/ICML/ICLR), and GitHub benchmarks.

**Success Criteria:**
- Primary: ≥30 valid hypotheses with micro-pilot (≤50 samples) + full-scale overhead data
- Secondary: Balanced stratification (CV <0.5 across low/mid/high overhead bins)

**Gate Decision:**
- PASS (≥30): Proceed to H-M1 (correlation analysis)
- FAIL (<20): PIVOT to prospective validation

---

## Problem Statement

ML research often includes ablation studies with timing data, but it's unclear whether these studies systematically report BOTH small-sample (micro-pilot) and full-scale overhead measurements needed for YouRA validation. This hypothesis tests the feasibility of retrospective validation by searching existing publications for overhead data pairs.

---

## Functional Requirements

### FR-1: Data Collection Pipeline

**FR-1.1: Papers with Code API Integration**
- Query PWC API for papers tagged with "ablation"
- Extract timing tables from paper metadata
- Target: 15-20 papers with timing data
- Filter: Papers must contain numerical timing measurements

**FR-1.2: Conference Paper Scraping**
- Search NeurIPS/ICML/ICLR proceedings (2020-2024)
- Keywords: "ablation study" + "overhead" + "sample size"
- Extract supplementary materials and timing appendices
- Target: 15-20 papers

**FR-1.3: GitHub Benchmark Extraction**
- Clone repos: facebookresearch/*, google-research/*
- Parse README timing tables and benchmark scripts
- Target: 5-10 repos with multi-scale timing data

### FR-2: Timing Data Extraction

**FR-2.1: PDF Parsing**
- Tool: PyMuPDF for PDF → text conversion
- Extract timing tables using regex patterns:
  - Pattern 1: "Table X: Overhead vs sample size"
  - Pattern 2: "Ablation: N samples: X sec, full dataset: Y sec"
- Store: paper_id, title, venue, year, hypothesis_type

**FR-2.2: Overhead Measurement Parsing**
- Extract micro-pilot measurements (sample_size ≤50)
- Extract full-scale measurements (sample_size ≥1000)
- Compute overhead_percent = (time - baseline) / baseline × 100
- Validate: Sample sizes differ by ≥10x

**FR-2.3: Metadata Collection**
- Hardware: GPU/CPU type if reported
- Framework: PyTorch/TensorFlow
- Hypothesis type: attention/gradient/regularization/etc.

### FR-3: Corpus Validation

**FR-3.1: Completeness Checks**
- Required fields: All fields in schema populated
- Validity: overhead_percent matches computed value from time/baseline
- Diversity: ≥3 hypothesis types represented

**FR-3.2: Stratification**
- Bin corpus by overhead: low (<20%), mid (20-80%), high (>80%)
- Target: 10 per bin (30 total)
- Metric: Coefficient of variation CV <0.5

**FR-3.3: Manual Verification**
- Spot-check 20% of entries (6 papers minimum)
- Verify extracted data matches source tables
- Document extraction errors for pattern refinement

### FR-4: Output Generation

**FR-4.1: Corpus File**
- Format: JSON
- Path: `data/retrospective_corpus/papers_metadata.json`
- Schema:
```json
{
  "paper_id": "string",
  "title": "string",
  "venue": "string",
  "year": "integer",
  "hypothesis_type": "string",
  "overhead_measurements": {
    "micro_pilot": {
      "sample_size": "integer (≤50)",
      "time_seconds": "float",
      "baseline_time": "float",
      "overhead_percent": "float"
    },
    "full_scale": {
      "sample_size": "integer (≥1000)",
      "time_seconds": "float",
      "baseline_time": "float",
      "overhead_percent": "float"
    }
  },
  "hardware": "string",
  "framework": "string"
}
```

**FR-4.2: Validation Report**
- Path: `experiments/h-e1_corpus_collection/validation_report.md`
- Contents:
  - Total papers collected
  - Valid hypotheses count (pass/fail threshold)
  - Stratification breakdown (low/mid/high bins)
  - Quality metrics: completeness %, CV
  - Gate decision: PASS/FAIL with reasoning

---

## Non-Functional Requirements

### NFR-1: Performance
- Total runtime: ≤2 weeks (10 days collection + extraction + verification)
- API rate limits: Respect PWC API limits (max 100 requests/hour)

### NFR-2: Reliability
- Error handling: Retry failed PDF downloads (max 3 retries)
- Logging: Log extraction status per paper
- Checkpointing: Save intermediate results after each source

### NFR-3: Maintainability
- Code structure: Separate scripts for collect/extract/verify
- Configuration: API keys and search queries in config.yaml
- Documentation: README with setup instructions

### NFR-4: Reproducibility
- Version control: Track all extraction patterns in repo
- Data provenance: Store source URLs for each paper
- Seed data: Save raw PDFs in `data/raw_papers/` directory

---

## Data Specifications

### Input Data
- **Papers with Code API:** https://paperswithcode.com/api/v1/papers
- **Conference proceedings:** Public URLs (OpenReview, proceedings.mlr.press)
- **GitHub repos:** Public repositories only

### Output Data
- **Corpus file:** `data/retrospective_corpus/papers_metadata.json` (JSON)
- **Raw papers:** `data/retrospective_corpus/raw_papers/*.pdf` (PDF archive)

### Data Quality
- Completeness: 90%+ entries with all required fields
- Accuracy: Spot-check validation passes for 80%+ entries
- Diversity: ≥3 hypothesis types, ≥2 venues

---

## Dependencies

### External Services
- Papers with Code API (public, no authentication)
- Conference proceedings websites (public access)
- GitHub (public repos, no authentication required)

### Software Libraries
- Python 3.9+
- requests (HTTP client)
- PyMuPDF (PDF parsing)
- beautifulsoup4 (HTML scraping)
- pandas (data processing)
- numpy (statistics)

### Hardware
- CPU only (no GPU needed)
- Storage: ~500MB for PDFs + metadata

---

## Success Criteria

### Primary Success (Gate PASS)
- Valid hypothesis count ≥30
- Each entry has micro-pilot + full-scale measurements
- Sample size ratio ≥10x between micro/full

### Secondary Success
- Stratification CV <0.5 (balanced across overhead bins)
- ≥3 hypothesis types represented
- ≥2 venues (NeurIPS + ICML or ICLR)

### Gate Decision Logic
```python
if valid_count >= 30:
    decision = "PASS"
    next_step = "Proceed to H-M1"
elif 20 <= valid_count < 30:
    decision = "PARTIAL"
    next_step = "Explore combining retrospective + prospective"
else:
    decision = "FAIL"
    next_step = "PIVOT to prospective validation (new micro-pilots)"
```

---

## Timeline

**Total: 2 weeks**

- Week 1: Collection + Extraction
  - Days 1-3: Query APIs, scrape papers
  - Days 4-7: Parse PDFs, extract timing tables

- Week 2: Verification + Stratification
  - Days 8-9: Validate completeness, compute stratification
  - Day 10: Generate validation report, gate decision

---

## Risks and Mitigations

### Risk 1: Insufficient micro-pilot data in papers
**Likelihood:** Medium  
**Impact:** High (blocks retrospective validation)  
**Mitigation:**
- Expand search to arXiv preprints (more detailed ablations)
- Search GitHub benchmark logs (often have multi-scale timing)
- Contact authors if <25 papers found (request supplementary data)

### Risk 2: Heterogeneous measurement formats
**Likelihood:** High  
**Impact:** Medium (extraction complexity)  
**Mitigation:**
- Accept any sample size ≤50 as "micro-pilot"
- Normalize to per-sample overhead if needed
- Manual verification of 20% sample to catch edge cases

### Risk 3: Overhead definition variability
**Likelihood:** Medium  
**Impact:** Low (filtering reduces corpus)  
**Mitigation:**
- Focus exclusively on wall-clock time overhead
- Exclude papers reporting only memory/FLOPs
- Document overhead type in metadata field

---

## Appendix: Example Data Entry

```json
{
  "paper_id": "smith2023efficient",
  "title": "Efficient Attention Mechanisms for Large-Scale NLP",
  "venue": "NeurIPS",
  "year": 2023,
  "hypothesis_type": "attention",
  "overhead_measurements": {
    "micro_pilot": {
      "sample_size": 10,
      "time_seconds": 0.85,
      "baseline_time": 0.50,
      "overhead_percent": 70.0
    },
    "full_scale": {
      "sample_size": 10000,
      "time_seconds": 850.0,
      "baseline_time": 500.0,
      "overhead_percent": 70.0
    }
  },
  "hardware": "NVIDIA V100",
  "framework": "PyTorch"
}
```

---

**Document Version:** 1.0  
**Created:** 2026-08-25  
**Hypothesis:** H-E1 (EXISTENCE, MUST_WORK)
