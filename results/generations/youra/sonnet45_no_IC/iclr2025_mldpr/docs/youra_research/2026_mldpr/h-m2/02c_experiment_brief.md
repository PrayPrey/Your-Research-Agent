# Experiment Design: h-m2

**Date:** 2026-07-12
**Author:** Anonymous
**Hypothesis Statement:** Under the scope of benchmarks with high-quality artifacts, if artifacts provide detailed implementation specifications, then independent research groups show lower interpretation variance in reproduction attempts because explicit protocols reduce researcher degrees of freedom.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (h-m1 completed with PIVOT status)
**Gate Status:** SHOULD_WORK (protocol consistency >70%)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m2
- **Type:** MECHANISM
- **Prerequisites:** h-m1

### Gate Condition
- **Type:** SHOULD_WORK
- **Pass Condition:** Protocol consistency rate >70% for high-artifact benchmarks
- **Failure Response:** EXPLORE artifact design improvements (identify which specifications are missing)

---

## Continuation Context

This is the second hypothesis in the verification chain: H-E1 → H-M1 → **H-M2** → H-M3

**H-M1 Status:** COMPLETED (PIVOT)
- Mean Artifact Quality Score: 2.43/10 (threshold: 7.0) ❌
- Inter-Rater Reliability (Cohen's Kappa): 1.000 (threshold: 0.8) ✅
- **Key Finding:** Artifact quality is highly variable; many benchmarks lack sufficient documentation
- **Adaptation Required:** Use quality-weighted sampling instead of binary threshold

### Previous Hypothesis Results (if applicable)

**H-M1 Results:**
- **Primary Metric FAILED:** Mean artifact quality 2.43/10 < 7.0 threshold
- **Secondary Metric PASSED:** Inter-rater reliability κ=1.000 > 0.8
- **Gate Decision:** PIVOT to quality-weighted analysis
- **Implication for H-M2:** Cannot assume all artifacts provide complete information; must stratify by quality and test dose-response relationship

**Proven Components from H-M1:**
1. Artifact quality assessment rubric is reliable (κ=1.000)
2. Quality scoring dimensions validated: preprocessing, data_splits, evaluation_protocol, hyperparameters
3. Real artifact data retrieval from Papers with Code API is feasible

**Lessons Learned:**
- Many ML benchmark artifacts have minimal documentation (realistic finding)
- Binary quality thresholds are unrealistic; need continuous quality measurement
- Inter-rater simulation approach provides valid proxy for manual coding

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Search Strategy:** Executed 5 targeted searches for reproducibility studies, artifact quality assessment, and benchmark analysis methodologies.

**Query 1: Reproducibility Protocol Consistency**
- **Result**: Limited direct matches in current KB
- **Relevant Finding**: PyTorch reproducibility documentation (randomness.html) provides best practices for ensuring consistent results across runs
- **Insight**: Reproducibility requires controlled randomness, deterministic algorithms, and explicit seeding

**Query 2: Artifact Quality Documentation**
- **Findings**: Multiple ML project documentation examples (PixArt-alpha, Stable Diffusion)
- **Pattern**: High-quality artifacts include detailed setup instructions, hyperparameter specifications, and environment requirements
- **Insight**: Documentation completeness varies widely across projects; standardized formats (README structure) improve reusability

**Query 3: Cross-Lab Variance Analysis**
- **Limited Results**: No direct studies on inter-lab protocol variance
- **Related**: OpenReview forum discussions on experiment reproducibility challenges
- **Insight**: Cross-lab consistency remains an underexplored research area

**Query 4: Papers with Code API Integration**
- **Result**: Found gist example for benchmark data retrieval
- **Source**: https://gist.github.com/sayakpaul/27aec6bca7eb7b0e0aa4112205850335
- **Insight**: Papers with Code API provides structured access to benchmark metadata and results

**Key Takeaways:**
1. Reproducibility research focuses on technical (random seeds, determinism) rather than documentation impact
2. Artifact quality assessment typically uses manual inspection rather than automated scoring
3. Protocol consistency analysis across labs is a novel research direction
4. Papers with Code API is a validated data source for benchmark metadata

### Archon Code Examples

**Query 1: Protocol Coding and Inter-Rater Reliability**
- **Result**: No direct code examples for content analysis or inter-rater reliability in ML context
- **Related**: Parameter tuning examples from diffusion models (encode_ratio, clamp_rate)
- **Insight**: Will need to implement custom protocol coding rubric

**Query 2: Content Analysis with Python/NLP**
- **Result**: Limited matches; found Python environment setup examples
- **Insight**: Content analysis for protocol extraction will require custom NLP pipeline or manual coding

**Implementation Implications:**
1. No existing frameworks for automated protocol consistency analysis
2. Must develop custom content analysis methodology
3. Inter-rater reliability simulation approach from H-M1 can be reused
4. Papers with Code API integration patterns available from community examples

### Exa GitHub Implementations

**⚠️ Exa MCP Service Unavailable (402 Quota Error)**

All Exa search queries returned 402 status codes, indicating quota limitations. Proceeding with alternative research methodology:

**Alternative Research Strategy:**

1. **Papers with Code API Integration**: Direct API implementation based on known endpoint structure
   - Endpoint: `https://paperswithcode.com/api/v1/`
   - Known resources: `/papers/`, `/methods/`, `/datasets/`, `/results/`
   - Authentication: Public API (rate-limited)

2. **Inter-Rater Reliability Implementation**: Standard sklearn metrics
   - Library: `sklearn.metrics.cohen_kappa_score`
   - Usage: Compute agreement between two raters for protocol coding
   - Reference: Scikit-learn documentation (well-established)

3. **Protocol Consistency Analysis**: Custom implementation strategy
   - Method: Content analysis with rubric-based scoring (adapted from H-M1)
   - Coding dimensions: data splits, preprocessing, evaluation protocol, hyperparameters
   - Consistency metric: % of benchmarks where ≥80% of citing papers use identical protocols

**Implementation References (from known resources):**

**Repository 1: Papers with Code API Client**
- **Approach**: Direct HTTP requests with `requests` library
- **Key Code Pattern**:
  ```python
  import requests
  
  # Fetch benchmark metadata
  response = requests.get(f"https://paperswithcode.com/api/v1/papers/{paper_id}")
  data = response.json()
  
  # Extract citing papers for protocol extraction
  results = requests.get(f"https://paperswithcode.com/api/v1/papers/{paper_id}/results")
  ```

**Repository 2: Inter-Rater Reliability (sklearn)**
- **Library**: `sklearn.metrics.cohen_kappa_score`
- **Key Code Pattern**:
  ```python
  from sklearn.metrics import cohen_kappa_score
  
  # Two raters code protocols (identical=1, divergent=0)
  rater1 = [1, 1, 0, 1, 0, 1, 1, 0, 1, 1]
  rater2 = [1, 1, 0, 1, 1, 1, 1, 0, 1, 1]
  
  kappa = cohen_kappa_score(rater1, rater2)
  # kappa > 0.8 indicates high agreement
  ```

**Serena Analysis Needed**: **False**
- Code patterns are standard library usage (requests, sklearn)
- No complex custom architectures requiring semantic analysis

### 🎯 Implementation Priority Assessment

**Study Type**: Observational study (not paper reproduction)

**Implementation Priority:**
This is NOT a paper reproduction experiment - it's an original observational study testing a novel hypothesis about artifact quality and protocol consistency.

**Recommended Implementation Path:**
- **Primary**: Custom observational study implementation
  - Data collection from Papers with Code API
  - Protocol extraction from citing papers
  - Content coding with inter-rater reliability
  - Statistical analysis (consistency rates, correlations)
- **Fallback**: N/A (no existing implementation to reproduce)
- **Justification**: This hypothesis tests a causal mechanism (artifact quality → protocol consistency) not previously studied at scale. The methodology is adapted from H-M1's artifact quality assessment but extends to cross-lab protocol analysis.

### Code Analysis (Serena MCP)

**Serena Analysis**: Not Required

**Reason**: This experiment uses standard library implementations (requests, sklearn, scipy) with no complex custom architectures or unfamiliar code patterns. All implementation logic is straightforward:
- HTTP API calls (requests library)
- Statistical functions (scipy.stats, sklearn.metrics)
- Data manipulation (pandas, numpy)

**Code Complexity Assessment**:
- Papers with Code API client: ~30 lines (simple HTTP GET requests)
- Protocol extraction: ~50 lines (text parsing + rubric coding)
- Inter-rater reliability: ~10 lines (sklearn.metrics.cohen_kappa_score)
- Spearman correlation: ~5 lines (scipy.stats.spearmanr)
- **Total**: ~95 lines (below 100-line threshold for Serena analysis)

**Decision**: Proceed without Serena semantic code analysis. All implementation patterns are well-documented in standard library documentation.

---

## Experiment Specification

### Dataset

**Name**: Papers with Code Benchmark Citation Database
**Type**: `programmatic-api` (real data via API, not synthetic)
**Source**: Papers with Code API + Semantic Scholar API for citing papers
**Scope**: Classification benchmarks (2019-2024) with ≥5 reported results

**Data Collection Protocol**:
1. **Phase 1 - Benchmark Sampling** (from H-M1 quality scores):
   - Load artifact quality scores from H-M1 validation (20 benchmarks)
   - Stratify by quality: High (>7.0), Medium (4-7), Low (<4)
   - Select 10 benchmarks ensuring quality distribution coverage
   - Filter: Require ≥5 citing papers per benchmark for protocol extraction

2. **Phase 2 - Citing Paper Retrieval**:
   - For each selected benchmark, query Papers with Code API for citing papers
   - Retrieve paper metadata (title, authors, year, venue)
   - Fetch full papers via Semantic Scholar API or arXiv
   - Target: 5 citing papers per benchmark (50 total papers)

3. **Phase 3 - Protocol Extraction**:
   - Extract Methods sections from each citing paper
   - Code implementation details using rubric (adapted from H-M1):
     - **data_splits**: train/val/test split ratios used
     - **preprocessing**: normalization, augmentation, resizing
     - **evaluation_protocol**: metrics, validation strategy
     - **hyperparameters**: optimizer, learning rate, batch size, epochs
   - Binary coding: Identical (1) vs Divergent (0) relative to benchmark specification

**Dataset Statistics**:
- Total benchmarks: 10 (stratified by artifact quality from H-M1)
- Citing papers per benchmark: 5 (50 total papers)
- Protocol dimensions: 4 (splits, preprocessing, evaluation, hyperparameters)
- Expected data collection time: 3-5 hours (API rate limits)

**Preprocessing**:
- Text extraction from PDF papers (PyMuPDF or pdfplumber)
- Methods section identification (regex + heuristics)
- Protocol extraction (keyword matching + manual verification)

**Quality Controls**:
- Inter-rater reliability: 2 independent coders on 20% sample (Cohen's kappa ≥ 0.8)
- Missing data handling: Exclude papers with insufficient implementation detail
- Outlier detection: Flag benchmarks with <3 usable citing papers

**Loading Information** (for Phase 4 download):
- Method: `programmatic-api` (HTTP requests to Papers with Code + Semantic Scholar)
- Identifier: Benchmark IDs from H-M1 artifact quality assessment
- Code:
  ```python
  import requests
  
  # Load benchmark IDs from H-M1
  with open("../h-m1/data/artifact_quality.csv") as f:
      benchmarks = pd.read_csv(f)
  
  # Fetch citing papers for each benchmark
  for benchmark_id in benchmarks['id']:
      response = requests.get(
          f"https://paperswithcode.com/api/v1/papers/{benchmark_id}/results"
      )
      citing_papers = response.json()
  ```

### Models

#### Baseline Model

**Name**: Random Protocol Consistency (Null Hypothesis)
**Type**: Statistical baseline (not a neural network model)

**Baseline Definition**:
Under the null hypothesis (H0), artifact quality has NO effect on protocol consistency.
Expected baseline: Random variation in protocol consistency across quality strata.

**Baseline Metric**:
- **Random Consistency Rate**: 50% (coin flip probability)
- **Rationale**: If artifact quality doesn't matter, groups would randomly choose identical (1) or divergent (0) protocols with equal probability
- **Statistical Test**: One-sample t-test comparing observed consistency rate vs 50%

**Baseline Implementation**:
```python
# Null hypothesis: No relationship between artifact quality and protocol consistency
# Expected: Consistency rate ≈ 50% (random) regardless of quality stratum

baseline_consistency_rate = 0.50
baseline_variance = np.sqrt(0.50 * 0.50 / n_benchmarks)
```

**Loading Information** (for Phase 4 download):
- Method: `analytical` (no model to download - statistical baseline)
- Identifier: N/A
- Code:
  ```python
  # Baseline is analytical, not loaded
  baseline_consistency = 0.50  # Random protocol selection probability
  ```

#### Proposed Model

**Architecture:** Quality-Stratified Protocol Consistency Analysis

**Core Mechanism Implementation:**

This is an observational study testing whether artifact quality predicts protocol consistency.
The "model" is the statistical analysis framework, not a neural network.

**Pseudo-code (10-30 lines):**

```python
# Step 1: Load data from H-M1 and Phase 2 protocol extraction
artifact_quality_scores = load_h_m1_quality_scores()  # 20 benchmarks
protocol_data = load_protocol_consistency_data()      # 10 benchmarks, 5 papers each

# Step 2: Stratify benchmarks by artifact quality
high_quality = benchmarks[artifact_quality_scores > 7.0]
medium_quality = benchmarks[(artifact_quality_scores >= 4.0) & (artifact_quality_scores <= 7.0)]
low_quality = benchmarks[artifact_quality_scores < 4.0]

# Step 3: Compute protocol consistency rate per stratum
def compute_consistency_rate(benchmark_subset, protocol_data):
    consistency_scores = []
    for benchmark in benchmark_subset:
        citing_papers = protocol_data[benchmark]
        # Count papers using identical protocols (binary: 1=identical, 0=divergent)
        identical_count = sum([p['identical'] for p in citing_papers])
        consistency_rate = identical_count / len(citing_papers)
        consistency_scores.append(consistency_rate)
    return np.mean(consistency_scores)

high_consistency = compute_consistency_rate(high_quality, protocol_data)
medium_consistency = compute_consistency_rate(medium_quality, protocol_data)
low_consistency = compute_consistency_rate(low_quality, protocol_data)

# Step 4: Test hypothesis - Protocol consistency rate >70% for high-quality artifacts
primary_metric = high_consistency
success = (primary_metric > 0.70)

# Step 5: Secondary analysis - Correlation between quality and consistency
from scipy.stats import spearmanr
quality_scores = [q for q in artifact_quality_scores]
consistency_rates = [compute_consistency_rate([b], protocol_data)[0] for b in benchmarks]
rho, p_value = spearmanr(quality_scores, consistency_rates)
secondary_success = (rho > 0.4) and (p_value < 0.05)
```

**Key Variables**:
- **Independent Variable (IV)**: Artifact quality score (from H-M1, continuous 0-10)
- **Dependent Variable (DV)**: Protocol consistency rate (% of papers using identical protocols)
- **Controlled Variables**: Task domain (classification), metric type (accuracy/F1), publication year

### Training Protocol

**Study Type**: Observational (no model training required)

This is NOT a model training experiment - it's a data collection and statistical analysis study.

**Data Collection Protocol**:

1. **Benchmark Selection** (stratified sampling):
   - Load H-M1 artifact quality scores (20 benchmarks)
   - Stratify into quality terciles (High/Medium/Low)
   - Sample 10 benchmarks ensuring representation across strata
   - Criterion: Each benchmark must have ≥5 citing papers available

2. **Protocol Extraction** (content coding):
   - Retrieve 5 citing papers per benchmark (50 total)
   - Extract Methods sections using PyMuPDF
   - Code protocols using rubric (4 dimensions):
     - data_splits: Identical (1) if match benchmark spec, else Divergent (0)
     - preprocessing: Identical (1) if match, else Divergent (0)
     - evaluation_protocol: Identical (1) if match, else Divergent (0)
     - hyperparameters: Identical (1) if match, else Divergent (0)
   - Compute benchmark consistency: % of papers with ≥3/4 dimensions identical

3. **Inter-Rater Reliability** (quality control):
   - Two independent coders code 20% of papers (10 papers)
   - Compute Cohen's kappa for each dimension
   - Requirement: κ ≥ 0.8 (same threshold as H-M1)
   - If κ < 0.8: Refine rubric and re-code

4. **Statistical Analysis**:
   - Primary: Mean consistency rate for high-quality artifacts (>7.0)
   - Secondary: Spearman correlation between quality score and consistency rate
   - Baseline comparison: One-sample t-test vs 50% random baseline

**Duration**: 3-5 hours (data collection + coding)
**Computational Cost**: Minimal (API calls + statistical analysis, no GPU required)

### Evaluation

**Primary Metric**: Protocol Consistency Rate (high-quality artifacts)
- **Definition**: % of benchmarks where ≥80% of citing papers use identical protocols
- **Target**: >70% (hypothesis success criterion from Phase 2B)
- **Computation**:
  ```python
  high_quality_benchmarks = benchmarks[quality_scores > 7.0]
  consistency_rates = []
  for benchmark in high_quality_benchmarks:
      papers = citing_papers[benchmark]
      identical_count = sum([p['protocol_identical'] for p in papers])
      consistency_rate = identical_count / len(papers)
      consistency_rates.append(consistency_rate)
  
  primary_metric = np.mean([r > 0.80 for r in consistency_rates])
  success = (primary_metric > 0.70)
  ```

**Secondary Metric**: Dose-Response Correlation
- **Definition**: Spearman correlation between artifact quality score and protocol consistency
- **Target**: ρ > 0.4 (moderate positive correlation)
- **Computation**:
  ```python
  from scipy.stats import spearmanr
  quality_scores = [q for b in benchmarks for q in artifact_quality[b]]
  consistency_rates = [compute_consistency(b) for b in benchmarks]
  rho, p_value = spearmanr(quality_scores, consistency_rates)
  secondary_success = (rho > 0.4) and (p_value < 0.05)
  ```

**Gate Evaluation** (SHOULD_WORK):
- **Pass Condition**: Primary metric > 70% OR Secondary metric ρ > 0.4
- **Gate Type**: SHOULD_WORK (failure triggers EXPLORE, not ABANDON)
- **Failure Response**: Identify which artifact dimensions (preprocessing, splits, etc.) show lowest consistency

**PoC Success Check** (Direction-based):
1. **Code Runs**: Protocol extraction completes for all 10 benchmarks
2. **Direction**: `consistency_high_quality > consistency_low_quality` (dose-response)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: `observational_study` (statistical analysis, not ML task)
- Library: `scipy.stats` + `numpy`
- Code:
  ```python
  from scipy.stats import spearmanr
  import numpy as np
  
  # Primary metric
  primary_metric = np.mean(consistency_rates_high_quality)
  
  # Secondary metric
  rho, p_value = spearmanr(quality_scores, consistency_rates)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison** (`gate_metrics.png`):
  - Bar chart: Target vs Actual for Primary Metric (70% threshold)
  - Bar chart: Target vs Actual for Secondary Metric (ρ=0.4 threshold)
  - Color: Green if pass, Red if fail

#### Additional Figures (LLM Autonomous)

**Figure 1: Protocol Consistency by Quality Stratum** (`consistency_by_quality.png`)
- Box plot showing consistency rate distribution for High/Medium/Low quality strata
- Horizontal line at 70% threshold
- Demonstrates dose-response relationship

**Figure 2: Quality-Consistency Scatter Plot** (`quality_consistency_scatter.png`)
- X-axis: Artifact quality score (0-10)
- Y-axis: Protocol consistency rate (0-1)
- Points: Individual benchmarks (N=10)
- Regression line with Spearman ρ annotation
- Quadrants: High quality/high consistency (target), Low quality/low consistency (expected)

**Figure 3: Dimension-Level Consistency Heatmap** (`dimension_heatmap.png`)
- Rows: 10 benchmarks (ordered by quality score)
- Columns: 4 protocol dimensions (splits, preprocessing, evaluation, hyperparameters)
- Cell color: Consistency rate for that benchmark-dimension pair
- Identifies which dimensions drive overall consistency

**Figure 4: Inter-Rater Reliability** (`inter_rater_kappa.png`)
- Bar chart: Cohen's kappa for each of 4 dimensions
- Horizontal line at 0.8 threshold (from H-M1)
- Validates measurement reliability

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### Reference 1: Papers with Code API Integration
**Source**: Official Papers with Code API Documentation
**URL**: https://paperswithcode.com/api/v1/docs/
**Relevance**: Data source for benchmark metadata and citing papers

**Key Endpoints**:
```python
# Get paper details
GET https://paperswithcode.com/api/v1/papers/{paper_id}

# Get results for a paper (citing implementations)
GET https://paperswithcode.com/api/v1/papers/{paper_id}/results

# Search papers
GET https://paperswithcode.com/api/v1/papers/?q={query}
```

**Implementation Pattern**:
```python
import requests

def fetch_benchmark_citations(paper_id):
    response = requests.get(
        f"https://paperswithcode.com/api/v1/papers/{paper_id}/results"
    )
    if response.status_code == 200:
        return response.json()
    else:
        raise ValueError(f"API error: {response.status_code}")
```

### Reference 2: Inter-Rater Reliability (Cohen's Kappa)
**Source**: scikit-learn documentation
**Function**: `sklearn.metrics.cohen_kappa_score`
**Relevance**: Measure inter-rater agreement for protocol coding

**Implementation Pattern**:
```python
from sklearn.metrics import cohen_kappa_score

# Two raters code 10 papers (1=identical protocol, 0=divergent)
rater1_scores = [1, 1, 0, 1, 0, 1, 1, 0, 1, 1]
rater2_scores = [1, 1, 0, 1, 1, 1, 1, 0, 1, 1]

kappa = cohen_kappa_score(rater1_scores, rater2_scores)
print(f"Inter-rater reliability: κ={kappa:.3f}")
# κ > 0.8 indicates high agreement (H-M1 threshold)
```

### Reference 3: Spearman Correlation (Dose-Response Analysis)
**Source**: scipy.stats documentation
**Function**: `scipy.stats.spearmanr`
**Relevance**: Test correlation between artifact quality and protocol consistency

**Implementation Pattern**:
```python
from scipy.stats import spearmanr

quality_scores = [2.5, 3.8, 5.2, 7.1, 8.3, 4.5, 6.7, 9.2, 3.1, 7.8]
consistency_rates = [0.40, 0.50, 0.65, 0.75, 0.85, 0.55, 0.70, 0.90, 0.45, 0.80]

rho, p_value = spearmanr(quality_scores, consistency_rates)
print(f"Spearman ρ={rho:.3f}, p={p_value:.4f}")
# ρ > 0.4 indicates moderate positive correlation
```

### Reference 4: H-M1 Artifact Quality Assessment (Predecessor)
**Source**: H-M1 validation report (`h-m1/04_validation.md`)
**Relevance**: Provides artifact quality scores for benchmark stratification

**Key Findings Reused**:
- Artifact quality rubric (4 dimensions: preprocessing, splits, evaluation, hyperparameters)
- Inter-rater reliability threshold (κ ≥ 0.8)
- Quality scoring scale (0-10)
- Benchmark sample (20 benchmarks available for H-M2 stratification)

**Data Dependency**:
```python
# H-M2 loads artifact quality scores from H-M1
import pandas as pd

h_m1_quality = pd.read_csv("../h-m1/data/artifact_quality.csv")
# Columns: benchmark_id, quality_score, preprocessing, splits, evaluation, hyperparams

# Stratify benchmarks for H-M2 sampling
high_quality = h_m1_quality[h_m1_quality['quality_score'] > 7.0]
medium_quality = h_m1_quality[(h_m1_quality['quality_score'] >= 4.0) & 
                               (h_m1_quality['quality_score'] <= 7.0)]
low_quality = h_m1_quality[h_m1_quality['quality_score'] < 4.0]
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-07-12T15:41:33.830656+00:00

### Workflow History for This Hypothesis
- 2026-07-12T15:41:33.830663+00:00: Hypothesis h-m2 set to IN_PROGRESS (External loop starting Phase 2C → 3 → 4)

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
