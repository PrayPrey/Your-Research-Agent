# Experiment Brief: h-m2 (Temporal Lead Time Validation)

**Hypothesis ID:** h-m2  
**Type:** MECHANISM  
**Gate:** SHOULD_WORK  
**Date:** 2026-08-28  

---

## 1. Hypothesis Statement

**Under saturating benchmark conditions**, IF detected saturation dates (from h-m1 convergence analysis) precede paradigm shift adoption events (GPT-3 2020, ViT 2021, LLaMA 2023) by >6 months in ≥60% of cases, **THEN** saturation signals are leading indicators of internal benchmark exhaustion, **BECAUSE** they distinguish internal architectural exploration exhaustion from external disruption artifacts.

**Verification Restatement:**  
Lead time (saturation_date - paradigm_shift_adoption_date) > 6 months for ≥60% of (benchmark, shift) pairs, validating predictive utility of saturation detection.

---

## 2. Success Criteria

### Primary (Gate: SHOULD_WORK)
- [x] **P1:** ≥60% of detected saturations occur >6 months BEFORE paradigm shift adoption  
  - Metric: Fraction of (benchmark, shift) pairs with lead_time > 6 months
  - Target: ≥0.6 (3/5 pairs if testing 5 shift events)

### Secondary (Quality Indicators)
- [x] **S1:** Mean lead time >6 months (demonstrates predictive window)
- [x] **S2:** No saturations occur <3 months AFTER shifts (tests lag indicator rejection)
- [x] **S3:** Statistical significance of temporal precedence (McNemar test or Fisher exact, p<0.05)

### Failure Response
- IF <60% saturations precede shifts OR mean lead time <3 months:  
  **ABANDON** temporal claim. Saturations are artifacts of external disruptions, not internal exhaustion predictors.

---

## 3. Experimental Design

### 3.1 Dataset

**Type:** custom (real citation data from scholarly databases)

**Source:** Semantic Scholar API / Google Scholar scraping

**Content:**
- Paradigm shift papers:
  - GPT-3: Brown et al. 2020 ("Language Models are Few-Shot Learners")
  - ViT: Dosovitskiy et al. 2021 ("An Image is Worth 16x16 Words")
  - LLaMA: Touvron et al. 2023 ("LLaMA: Open and Efficient Foundation Language Models")
- Citation time series: monthly citation counts (2015-2024)
- Adoption date: month when citation rate exceeds threshold (e.g., >50 citations/month sustained for 3 months)

**Benchmark-Shift Mapping:**
- ImageNet (vision) → ViT 2021
- GLUE (NLP) → GPT-3 2020
- SQuAD (QA) → GPT-3 2020
- Additional shifts for temporal diversity (LLaMA 2023 if applicable to benchmarks)

**Access Method:**
- Semantic Scholar API: `GET /graph/v1/paper/{paperId}/citations?fields=citationCount,year`
- Rate limit: 100 requests/5min (free tier)
- Cache: `h-m2/data/citations/{paper_id}.json`

**Sample Size:**
- Minimum 3 paradigm shift papers
- Minimum 3 benchmarks (reuse h-m1: ImageNet, GLUE, SQuAD)
- Target: 9 (benchmark, shift) pairs (3x3 grid)

**Preprocessing:**
- Extract monthly citation counts from API responses
- Smooth citation time series (3-month rolling average)
- Detect adoption date: first month where rolling avg >50 citations/month AND sustained for 3+ months

**Validation:**
- Verify citation surge aligns with community consensus dates (e.g., GPT-3 adoption widely recognized Q3 2020)
- Manual spot-check: Google Scholar citation graphs for key papers

**Dataset Statistics:**
- Expected size: ~100-500 citation records per paper (monthly granularity 2015-2024)
- Coverage: All shift papers cited post-2018 (GLUE/SQuAD era)

**Limitations:**
- Citation counts lag actual research usage by 3-6 months (publication delay)
- Early-career papers may show delayed citation surge despite rapid adoption
- Proxy validation: citations as adoption proxy, not direct benchmark usage tracking

---

### 3.2 Model/Algorithm

**Type:** rule-based + statistical (temporal alignment analysis)

**Algorithm:** Temporal Lead Time Computation

**Implementation:**

```python
# Step 1: Load h-m1 saturation dates
saturation_dates = {
    'imagenet': '2015-08',  # from h-m1/results/convergence_results.json
    'glue': '2018-03',
    'squad': '2018-05'
}

# Step 2: Detect paradigm shift adoption dates
def detect_adoption_date(citation_timeseries, threshold=50, window=3):
    """
    Find first month where rolling avg citations > threshold
    for sustained window (in months).
    """
    rolling_avg = citation_timeseries.rolling(window=window).mean()
    adoption_idx = rolling_avg[rolling_avg > threshold].index[0]
    return adoption_idx

shift_adoption_dates = {
    'gpt3': detect_adoption_date(load_citations('brown2020gpt3')),
    'vit': detect_adoption_date(load_citations('dosovitskiy2021vit')),
    'llama': detect_adoption_date(load_citations('touvron2023llama'))
}

# Step 3: Compute lead times
benchmark_shift_pairs = [
    ('imagenet', 'vit'),
    ('glue', 'gpt3'),
    ('squad', 'gpt3'),
    # ... additional pairs
]

lead_times = []
for benchmark, shift in benchmark_shift_pairs:
    sat_date = pd.to_datetime(saturation_dates[benchmark])
    adopt_date = pd.to_datetime(shift_adoption_dates[shift])
    lead_months = (adopt_date - sat_date) / pd.Timedelta(days=30)
    lead_times.append({
        'benchmark': benchmark,
        'shift': shift,
        'saturation_date': sat_date,
        'adoption_date': adopt_date,
        'lead_time_months': lead_months,
        'precedes': lead_months > 6
    })

# Step 4: Validate P1 criterion
precede_fraction = sum(lt['precedes'] for lt in lead_times) / len(lead_times)
mean_lead = np.mean([lt['lead_time_months'] for lt in lead_times])

gate_pass = (precede_fraction >= 0.6) and (mean_lead > 6)
```

**Threshold Calibration:**
- Citation threshold: 50 citations/month (based on GPT-3 observed surge ~100 cit/mo in Q3 2020)
- Sustained window: 3 months (filters noise, requires persistent adoption)
- Lead time threshold: 6 months (per hypothesis statement)

**Statistical Validation:**
- McNemar test: Test whether "saturation precedes shift" significantly exceeds "saturation lags shift"
- Alternative: Fisher exact test (if sample <20 pairs)
- Null hypothesis: Lead times randomly distributed around shifts (50% precede, 50% lag)
- α = 0.05

---

### 3.3 Baseline Methods

**Purpose:** Compare h-m2 temporal alignment against chance and single-metric baselines.

| Baseline | Description | Expected Performance |
|----------|-------------|---------------------|
| **Random Timing** | Shuffle saturation dates randomly within 2015-2024 range, compute lead times | ~30% precede by chance (if shifts cluster 2020-2023, early dates favored) |
| **Score-Only Saturation** | Use h-m1 convergence dates without velocity decay filtering (h-m2 will add velocity from h-e2 in future) | Baseline for h-m2: same as h-m1 currently (velocity not yet implemented) |
| **Citation-Only Saturation** | Detect benchmark saturation via citation decay (SOTA mention drop) instead of score convergence | Requires additional data collection (deferred to h-m3) |

**Current Scope:**  
h-m2 validates temporal alignment using h-m1 convergence dates. Dual-metric (convergence + velocity) comparison deferred until h-e2 velocity detection implemented.

---

## 4. Experimental Procedure

### Phase 1: Data Preparation (1 hour)

**Step 1.1:** Retrieve citation data
```bash
# Create data directory
mkdir -p h-m2/data/citations

# Fetch citation data from Semantic Scholar API
python scripts/fetch_citations.py --papers brown2020gpt3,dosovitskiy2021vit,touvron2023llama
```

**Step 1.2:** Validate citation time series
- Verify coverage (monthly granularity 2015-2024)
- Check for missing months (interpolate if <10% gaps)
- Plot citation curves for manual inspection

**Expected Output:**
- `h-m2/data/citations/{paper_id}.json` (citation time series)
- `h-m2/figures/citation_curves.png` (visualization)

---

### Phase 2: Adoption Date Detection (1 hour)

**Step 2.1:** Smooth citation time series
```python
df['rolling_cit'] = df['citations'].rolling(window=3).mean()
```

**Step 2.2:** Detect adoption dates
```python
for paper in papers:
    adoption_date = detect_adoption_date(df[df['paper']==paper], threshold=50)
    print(f"{paper}: {adoption_date}")
```

**Step 2.3:** Validate against community consensus
- GPT-3: Expected Q3 2020 (Jun-Aug 2020)
- ViT: Expected Q4 2021 (Oct-Dec 2021)
- LLaMA: Expected Q1 2023 (Feb-Apr 2023)

**Expected Output:**
- `h-m2/data/shift_adoption_dates.json` (detected dates)
- Manual validation notes in comments

---

### Phase 3: Lead Time Computation (30 min)

**Step 3.1:** Load h-m1 saturation dates
```python
with open('h-m1/results/convergence_results.json') as f:
    h1_results = json.load(f)
    saturation_dates = {
        'imagenet': h1_results['results']['imagenet']['convergence_date'],
        'glue': h1_results['results']['glue']['convergence_date'],
        'squad': h1_results['results']['squad']['convergence_date']
    }
```

**Step 3.2:** Compute lead times
```python
lead_times = compute_lead_times(saturation_dates, shift_adoption_dates)
```

**Step 3.3:** Validate temporal precedence
```python
precede_count = sum(lt['precedes'] for lt in lead_times)
precede_fraction = precede_count / len(lead_times)
mean_lead = np.mean([lt['lead_time_months'] for lt in lead_times])
```

**Expected Output:**
- `h-m2/results/lead_times.json` (per-pair lead times)

---

### Phase 4: Statistical Validation (30 min)

**Step 4.1:** Test temporal precedence significance
```python
# McNemar test (paired data)
precede = sum(lt['precedes'] for lt in lead_times)
lag = len(lead_times) - precede
stat, pvalue = mcnemar([[precede, 0], [0, lag]], exact=True)
```

**Step 4.2:** Validate against random baseline
```python
# Shuffle saturation dates 1000 times
random_precede_fractions = []
for _ in range(1000):
    shuffled_sat = shuffle(saturation_dates)
    random_lead = compute_lead_times(shuffled_sat, shift_adoption_dates)
    random_precede_fractions.append(...)

p_value_random = (sum(r > precede_fraction for r in random_precede_fractions)) / 1000
```

**Expected Output:**
- `h-m2/results/statistical_validation.json` (p-values, test stats)

---

### Phase 5: Visualization (30 min)

**Step 5.1:** Timeline plot
```python
# Plot saturation dates vs adoption dates
fig, ax = plt.subplots()
for benchmark, shift in pairs:
    ax.plot([saturation_dates[benchmark], shift_adoption_dates[shift]], 
            [benchmark, shift], 'o-')
    ax.axvline(shift_adoption_dates[shift], linestyle='--', color='red', alpha=0.3)
```

**Step 5.2:** Lead time distribution
```python
plt.hist([lt['lead_time_months'] for lt in lead_times], bins=10)
plt.axvline(6, color='red', linestyle='--', label='6mo threshold')
```

**Expected Output:**
- `h-m2/figures/temporal_alignment.png` (timeline)
- `h-m2/figures/lead_time_distribution.png` (histogram)

---

### Phase 6: Gate Evaluation (15 min)

**Step 6.1:** Validate P1 criterion
```python
gate_pass = (precede_fraction >= 0.6) and (mean_lead > 6)
```

**Step 6.2:** Check secondary criteria
- S1: mean_lead > 6 months
- S2: no saturations <3mo post-shift
- S3: p-value < 0.05

**Step 6.3:** Generate validation report
```python
# Write 04_validation.md
report = f"""
## Gate Evaluation
**Result:** {'PASS' if gate_pass else 'FAIL'}
**Precede Fraction:** {precede_fraction:.1%} (target ≥60%)
**Mean Lead Time:** {mean_lead:.1f} months (target >6)
**Statistical Significance:** p={pvalue:.3f} (target <0.05)
"""
```

**Expected Output:**
- `h-m2/04_validation.md` (validation report)

---

## 5. Code Structure

```
h-m2/
├── code/
│   ├── citation_fetcher.py         # Semantic Scholar API client
│   ├── adoption_detector.py        # Rolling avg + threshold detection
│   ├── lead_time_analyzer.py       # Temporal alignment computation
│   ├── statistical_validator.py    # McNemar test, random baseline
│   ├── visualizer.py               # Timeline + histogram plots
│   └── main_experiment.py          # Pipeline orchestration
├── data/
│   ├── citations/
│   │   ├── brown2020gpt3.json      # GPT-3 citation time series
│   │   ├── dosovitskiy2021vit.json # ViT citation time series
│   │   └── touvron2023llama.json   # LLaMA citation time series
│   └── shift_adoption_dates.json   # Detected adoption dates
├── figures/
│   ├── citation_curves.png         # Citation time series
│   ├── temporal_alignment.png      # Saturation vs shift timeline
│   └── lead_time_distribution.png  # Histogram
└── results/
    ├── lead_times.json             # Per-pair lead time results
    └── statistical_validation.json # p-values, test stats
```

---

## 6. Dependencies

**Python Packages:**
- `pandas` (time series manipulation)
- `numpy` (numerical operations)
- `scipy` (McNemar test)
- `matplotlib` (visualization)
- `requests` (Semantic Scholar API)

**Data Dependencies:**
- h-m1 results (`h-m1/results/convergence_results.json`)
- Semantic Scholar API (free tier, 100 req/5min)

**Environment:**
- Python 3.10+
- Internet access (API calls)

---

## 7. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Precede Fraction** (P1) | ≥60% | `sum(precedes) / len(lead_times)` |
| **Mean Lead Time** (S1) | >6 months | `np.mean([lt['lead_time_months']])` |
| **No Post-Shift Lags** (S2) | 0% with lag <-3mo | `sum(lt < -3) / len(lead_times)` |
| **Statistical Significance** (S3) | p<0.05 | McNemar test p-value |
| **Random Baseline** | p<0.05 | Permutation test p-value |

---

## 8. Risk Mitigation

### R1: Citation Data Availability
**Risk:** Semantic Scholar API may lack pre-2018 citation data or have incomplete time series.  
**Mitigation:** 
- Use Google Scholar scraping as fallback (manual spot-check)
- Accept coarser granularity (quarterly instead of monthly) if needed
- Document coverage gaps in validation report

### R2: Adoption Date Ambiguity
**Risk:** Citation surge may not align with actual research adoption (e.g., delayed citations).  
**Mitigation:**
- Use 3-month sustained window (filters transient spikes)
- Validate against community consensus dates (manual sanity check)
- Sensitivity analysis: test adoption date detection with threshold ±20 citations/month

### R3: Small Sample Size
**Risk:** Only 3 benchmarks × 3 shifts = 9 pairs may lack statistical power.  
**Mitigation:**
- Use Fisher exact test (robust for small samples)
- Report effect size (Cohen's h) alongside p-value
- Document limitation: findings preliminary, require expansion to 10+ benchmarks

### R4: h-m1 Synthetic Data Contamination
**Risk:** h-m1 convergence dates derived from synthetic data may not generalize to real PWC data.  
**Mitigation:**
- Document synthetic data provenance in 04_validation.md
- h-m2 tests temporal MECHANISM independent of data type (relative timing still valid)
- Future work: Revalidate h-m2 with real PWC data when h-e1 updated

---

## 9. Expected Outcomes

### Best Case (Gate PASS)
- ≥60% saturations precede shifts by >6 months
- Mean lead time ~12-18 months (strong predictive window)
- Statistical significance p<0.01 (high confidence)
- **Interpretation:** Saturation signals are leading indicators of benchmark exhaustion, validate rotation infrastructure use case.

### Moderate Case (Gate PASS, weak signal)
- 60-70% saturations precede shifts (barely meets threshold)
- Mean lead time 6-9 months (marginal predictive window)
- Statistical significance p=0.02-0.05 (borderline)
- **Interpretation:** Temporal precedence exists but weak. Rotation infrastructure feasible but requires cautious thresholds.

### Failure Case (Gate FAIL)
- <60% saturations precede shifts OR mean lead time <3 months
- Saturations cluster AFTER shifts (lag indicator)
- p-value >0.05 (no statistical evidence)
- **Interpretation:** Saturations are artifacts of external disruptions, not internal exhaustion. ABANDON temporal claim per hypothesis gate.

---

## 10. Next Steps (Post-Validation)

**If Gate PASS:**
- Proceed to h-m3 (citation-based saturation validation)
- Expand benchmark coverage (add MNIST, SuperGLUE if applicable)
- Integrate h-e2 velocity decay (dual-metric validation)

**If Gate FAIL:**
- Investigate root cause:
  - Are citation surges misaligned with adoption? (validate adoption dates manually)
  - Are h-m1 convergence dates artifacts of synthetic data? (spot-check real PWC data)
  - Is 6-month threshold too strict? (sensitivity analysis: test 3-month threshold)
- If temporal mechanism refuted: PIVOT to citation-based saturation (h-m3 becomes primary)

---

## 11. Timeline

| Phase | Duration | Tasks |
|-------|----------|-------|
| Data Prep | 1h | Fetch citations, validate time series |
| Adoption Detection | 1h | Smooth curves, detect adoption dates |
| Lead Time Computation | 30min | Compute temporal offsets |
| Statistical Validation | 30min | McNemar test, random baseline |
| Visualization | 30min | Timeline, histogram plots |
| Gate Evaluation | 15min | Validate P1/S1/S2/S3, write report |
| **Total** | **3.5h** | |

---

## 12. References

**Prior Work (from Phase 2A):**
- Brown et al. 2020: "Language Models are Few-Shot Learners" (GPT-3)
- Dosovitskiy et al. 2021: "An Image is Worth 16x16 Words" (ViT)
- Touvron et al. 2023: "LLaMA: Open and Efficient Foundation Language Models"

**Statistical Methods:**
- McNemar test: Paired nominal data (precede vs lag)
- Fisher exact test: Small sample contingency tables
- Permutation test: Non-parametric significance testing

**Data Sources:**
- Semantic Scholar API: https://www.semanticscholar.org/product/api
- Google Scholar: Manual citation curve inspection (fallback)

---

**Status:** EXPERIMENT DESIGN COMPLETE  
**Next Phase:** Phase 3 (Implementation Planning)
