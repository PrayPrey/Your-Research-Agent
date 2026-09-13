# Experiment Brief: H-E1 Retrospective Corpus Collection

## Metadata
- **Hypothesis ID:** h-e1
- **Type:** EXISTENCE
- **Gate:** MUST_WORK
- **Brief Version:** 1.0
- **Created:** 2026-08-25

---

## 1. Hypothesis Recap

**Statement:** Under retrospective validation using published ML research, if we search Papers with Code leaderboards and conference papers (NeurIPS, ICML, ICLR) for hypotheses with micro-pilot data, then we will find ≥30 hypotheses with BOTH 10-sample and full-scale overhead measurements, because ML papers often report ablation studies with small-sample timing data.

**Success Criteria:**
- Primary: ≥30 hypotheses with micro-pilot (≤50 samples) + full-scale overhead data
- Secondary: Balanced stratification (10 low <20%, 10 mid 20-80%, 10 high >80% overhead)

**Gate:** MUST_WORK
- FAIL (<20 hypotheses): PIVOT to prospective validation
- PASS (≥30 hypotheses): Proceed to H-M1

---

## 2. Dataset Specification

### 2.1 Dataset Selection

**Dataset Name:** Retrospective ML Overhead Corpus v1.0  
**Type:** custom (curated from published research)  
**Size:** Target 30-50 papers with timing data

**Source Strategy:**
1. **Papers with Code Leaderboards** (pwc.dev/api)
   - Filter: Papers with ablation studies
   - Extract: Timing tables, sample size breakdowns
   - Target: 15-20 papers

2. **Conference Papers** (NeurIPS/ICML/ICLR 2020-2024)
   - Search: "ablation study" + "overhead" + "sample size"
   - Extract: Supplementary materials, timing appendices
   - Target: 15-20 papers

3. **GitHub ML Benchmarks**
   - Repos: facebookresearch/*, google-research/*
   - Extract: README timing tables, benchmark scripts
   - Target: 5-10 repos with multi-scale timing

**Data Fields Per Hypothesis:**
```python
{
  "paper_id": str,
  "title": str,
  "venue": str,  # NeurIPS/ICML/ICLR/arXiv
  "year": int,
  "hypothesis_type": str,  # attention/gradient/regularization/etc
  "overhead_measurements": {
    "micro_pilot": {
      "sample_size": int,  # ≤50 samples
      "time_seconds": float,
      "baseline_time": float,
      "overhead_percent": float
    },
    "full_scale": {
      "sample_size": int,  # Full dataset (e.g., 10k-50k)
      "time_seconds": float,
      "baseline_time": float,
      "overhead_percent": float
    }
  },
  "hardware": str,  # GPU/CPU info if reported
  "framework": str  # PyTorch/TensorFlow
}
```

**Cache Path:** `data/retrospective_corpus/papers_metadata.json`

**Verification:**
- Each entry must have BOTH micro_pilot AND full_scale measurements
- Sample sizes must differ by ≥10x (e.g., 10 vs 1000)
- Overhead percent must be calculable from baseline

### 2.2 Data Preparation Steps

**Phase 1: Collection (Week 1)**
1. Query Papers with Code API for papers with "ablation" tag
2. Scrape NeurIPS/ICML/ICLR proceedings (2020-2024) for timing keywords
3. Clone GitHub benchmark repos with multi-scale timing data

**Phase 2: Extraction (Week 1)**
1. Parse papers (PDF → text via PyMuPDF)
2. Extract timing tables using regex patterns:
   - "Table X: Overhead vs sample size"
   - "Ablation: 10 samples: X sec, full dataset: Y sec"
3. Manual verification: Spot-check 20% of entries

**Phase 3: Stratification (Week 2)**
1. Compute overhead_percent for each hypothesis
2. Stratify into bins: low (<20%), mid (20-80%), high (>80%)
3. Balance corpus: 10 per bin (target 30 total)

**Baseline Preparation:** N/A (meta-analysis, no model training)

**Quality Checks:**
- Completeness: All fields populated
- Validity: Overhead percent matches (time - baseline) / baseline
- Diversity: ≥3 hypothesis types (attention, gradient, etc.)

---

## 3. Baseline Experiment Design

### 3.1 Baseline Configuration

**No ML Model Required**

This is a retrospective corpus collection task, not a model training/evaluation task.

**Metrics:**
- Primary: Count of valid hypotheses (target ≥30)
- Secondary: Stratification balance (coefficient of variation <0.3 across bins)

### 3.2 Evaluation Protocol

**Evaluation Dataset:** The collected corpus itself

**Metrics Computation:**
```python
# Primary metric
valid_count = len([h for h in corpus if h["overhead_measurements"]["micro_pilot"] and h["overhead_measurements"]["full_scale"]])

# Secondary metric
bins = {"low": 0, "mid": 0, "high": 0}
for h in corpus:
    overhead = h["overhead_measurements"]["full_scale"]["overhead_percent"]
    if overhead < 20:
        bins["low"] += 1
    elif overhead < 80:
        bins["mid"] += 1
    else:
        bins["high"] += 1

cv = std(bins.values()) / mean(bins.values())  # Coefficient of variation
```

**Success Thresholds:**
- PASS: valid_count ≥30 AND cv <0.5
- PARTIAL: 20 ≤ valid_count <30 (explore combining retrospective + prospective)
- FAIL: valid_count <20 (PIVOT to prospective validation)

**Logging:**
- Log each paper extraction: `{paper_id, extraction_status, fields_found}`
- Log stratification distribution: `{low: X, mid: Y, high: Z}`

---

## 4. Implementation Notes

### 4.1 Environment

**Hardware:** CPU only (no GPU needed for corpus collection)

**Software:**
- Python 3.9+
- Libraries: requests, PyMuPDF, beautifulsoup4, pandas, numpy

**Estimated Runtime:** 2 weeks (10 days collection + extraction + verification)

### 4.2 Code Structure

```
experiments/h-e1_corpus_collection/
├── collect_papers.py          # Query APIs, scrape papers
├── extract_timing_data.py     # Parse PDFs, extract tables
├── verify_corpus.py           # Validate completeness, compute metrics
├── config.yaml                # API keys, search queries
└── data/
    └── retrospective_corpus/
        ├── papers_metadata.json   # Main corpus
        └── raw_papers/            # Downloaded PDFs
```

### 4.3 Key Functions

**collect_papers.py:**
```python
def query_papers_with_code(tag="ablation"):
    """Query PWC API for papers with timing data."""
    # GET https://paperswithcode.com/api/v1/papers/?tag=ablation
    pass

def scrape_conference_proceedings(venue, year):
    """Scrape NeurIPS/ICML/ICLR for timing keywords."""
    # Search titles/abstracts for "overhead" + "ablation"
    pass
```

**extract_timing_data.py:**
```python
def extract_timing_table(pdf_path):
    """Parse PDF, extract timing measurements."""
    # PyMuPDF → text → regex for "X samples: Y sec"
    pass

def parse_overhead(text):
    """Extract micro-pilot and full-scale overhead from text."""
    # Pattern: r"(\d+)\s*samples?:\s*(\d+\.?\d*)\s*sec"
    pass
```

**verify_corpus.py:**
```python
def validate_hypothesis(hypothesis_dict):
    """Check completeness of overhead measurements."""
    required = ["micro_pilot", "full_scale"]
    return all(k in hypothesis_dict["overhead_measurements"] for k in required)

def compute_stratification_metrics(corpus):
    """Compute bin counts and CV."""
    pass
```

---

## 5. Expected Challenges

### 5.1 Data Availability

**Challenge:** ML papers may not report micro-pilot timing (only full-scale)

**Mitigation:**
1. Expand search to arXiv preprints (often have more ablation detail)
2. Search GitHub repos with `benchmark.py` scripts (timing logs)
3. Contact authors for supplementary timing data (if <25 papers found)

**Fallback:** If <20 hypotheses found, PIVOT to prospective validation (run new micro-pilots on 30 selected ML tasks)

### 5.2 Measurement Heterogeneity

**Challenge:** Different papers use different sample sizes (10 vs 50 vs 100 for "micro-pilot")

**Mitigation:**
1. Accept any sample size ≤50 as "micro-pilot"
2. Normalize overhead measurements to per-sample overhead
3. Group by sample size ranges (e.g., 1-20, 21-50) for analysis

### 5.3 Overhead Definition Variability

**Challenge:** Papers may report different overhead types (time, memory, FLOPs)

**Mitigation:**
1. Focus exclusively on wall-clock time overhead
2. Exclude papers that only report memory/FLOPs
3. Document overhead type in metadata for future filtering

---

## 6. Success Indicators

**Minimum Viable Corpus:**
- 30 hypotheses with micro-pilot + full-scale timing
- ≥3 hypothesis types (attention, gradient, regularization)
- Overhead range: 1% to 200% (diversity check)

**Quality Indicators:**
- 90%+ of entries have complete metadata
- Stratification CV <0.5 (balanced across overhead bins)
- ≥2 different venues represented (NeurIPS + ICML or ICLR)

**Gate Decision:**
- PASS (≥30): Proceed to H-M1 (correlation analysis)
- FAIL (<20): PIVOT to prospective validation (Phase 2B alternative route)

---

## 7. Deliverables

1. **Corpus Data:** `data/retrospective_corpus/papers_metadata.json`
2. **Validation Report:** `experiments/h-e1_corpus_collection/validation_report.md`
   - Total papers collected
   - Valid hypotheses count
   - Stratification breakdown
   - Quality metrics (completeness %, CV)
3. **Code:** Collection + extraction + verification scripts

**Timeline:** 2 weeks (Weeks 1-2 of 5-week verification plan)

---

## 8. Integration with Phase 4

**Prerequisites for H-M1 (Next Hypothesis):**
- H-E1 must PASS (≥30 hypotheses found)
- Corpus must include overhead_percent fields for correlation analysis

**Data Handoff:**
- `papers_metadata.json` → Input for H-M1 correlation script
- Extract `O_10` (micro-pilot overhead) and `O_full` (full-scale overhead) arrays
- Compute Pearson correlation `r = corr(O_10, O_full)`

**Failure Contingency:**
- If H-E1 FAILS, H-M1-3 cannot proceed with retrospective validation
- PIVOT: Design prospective validation with 30 new micro-pilots (5-week extension)

---

## Appendix: Example Paper Entry

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

**Note:** This example shows ideal case where overhead is constant across scales (70% at both 10 and 10k samples). H-M1 will test if this holds across the corpus.
