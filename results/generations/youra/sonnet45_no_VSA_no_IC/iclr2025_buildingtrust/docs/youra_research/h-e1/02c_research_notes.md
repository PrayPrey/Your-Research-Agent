# Phase 2C Research Notes: H-E1

**Date:** 2026-08-19
**Hypothesis:** At least one model exhibits statistically significant coupling (phi ≥ 0.3, p < 0.01) for at least one dimension pair
**Research Mode:** Web Research (Archon/Exa MCP unavailable)

---

## Research Query Log

### Query 1: LLM Trustworthiness Evaluation Frameworks (2025-2026)

**Search Terms:** "phi coefficient correlation trustworthiness dimensions LLM evaluation 2025 2026"

**Findings:**

1. **MultiTrust Benchmark** (arxiv:2406.07057)
   - Comprehensive MLLM trustworthiness evaluation
   - 5 dimensions: truthfulness, safety, robustness, fairness, privacy
   - Multi-modal evaluation framework
   - HuggingFace dataset: `thu-ml/MultiTrust`

2. **TrustLLM Framework** (ICML 2024)
   - 8-dimension assessment standard
   - Dimensions: truthfulness, safety, fairness, robustness, privacy, machine ethics, transparency, accountability
   - GitHub: HowieHwong/TrustLLM (⭐ 500+)
   - Supports OpenAI, Anthropic, Azure APIs
   - Standard sample sizes: 500-1000 instances

3. **PT-LLM-8 Scale**
   - Validated measurement tool
   - 8 perceived trustworthiness dimensions
   - High internal consistency: Cronbach's α = 0.90

**Key Insight:** Standard frameworks evaluate dimensions independently; no prior work explicitly tests cross-dimension coupling using phi coefficient.

**Sources:**
- [A Survey on Evaluating Quality and Trustworthiness in LLM-Generated Data](https://arxiv.org/html/2601.17717v3)
- [MultiTrust Benchmark](https://arxiv.org/pdf/2406.07057)
- [TrustLLM](https://trustllmbenchmark.github.io/TrustLLM-Website/)

---

### Query 2: Statistical Methods for Dimension Correlation

**Search Terms:** "phi coefficient PyTorch implementation sklearn scipy contingency table"

**Findings:**

1. **Phi Coefficient Basics**
   - Measures association in 2×2 contingency tables
   - Range: 0 (no association) to 1 (perfect association)
   - Equivalent to Matthews Correlation Coefficient for binary data

2. **Implementation Libraries:**
   - **sklearn.metrics.matthews_corrcoef**: Direct phi calculation
   - **scipy.stats.chi2_contingency**: Chi-square test + phi derivation
   - **KaveIO/PhiK** (⭐ 75+): Production-grade library with significance testing

3. **Statistical Requirements:**
   - Minimum 5 observations per cell for chi-square validity
   - P-value < 0.01 for statistical significance
   - Sample sizes 500-1000 standard in recent LLM evaluations

4. **Correlation Ranges in Literature:**
   - Recent LLM studies report Pearson correlation: 0.20-0.49
   - Medium effect size threshold: phi ≥ 0.3

**Implementation Code:**

```python
# Method 1: sklearn (direct)
from sklearn.metrics import matthews_corrcoef
phi = matthews_corrcoef(labels_d1, labels_d2)

# Method 2: scipy (with significance)
from scipy.stats import chi2_contingency
import numpy as np

table = np.array([[n11, n10], [n01, n00]])
chi2, p_value, dof, expected = chi2_contingency(table)
phi = np.sqrt(chi2 / table.sum())
```

**Sources:**
- [sklearn.metrics documentation](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.matthews_corrcoef.html)
- [scipy.stats chi2_contingency](https://docs.scipy.org/doc/scipy/tutorial/stats/hypothesis_chi2_contingency.html)
- [KaveIO/PhiK GitHub](https://github.com/KaveIO/PhiK)

---

### Query 3: Evaluation Dataset Characteristics

**Search Terms:** "LLM trustworthiness MultiTrust TrustLLM dataset sample size API evaluation"

**Findings:**

1. **Sample Size Standards:**
   - Typical range: 500-1000 instances per model
   - TrustLLM framework uses 500+ instances across dimensions
   - MultiTrust provides sufficient coverage for statistical analysis

2. **API-Only Evaluation:**
   - Standard practice in 2025-2026 research
   - No internal states required
   - Evaluation based on outputs + optional logprobs

3. **Multi-Dimensional Coverage:**
   - MultiTrust: 5 dimensions (truthfulness, robustness, fairness, safety, privacy)
   - TrustLLM: 8 dimensions (adds machine ethics, transparency, accountability)
   - Binary pass/fail labels standard format

4. **Model Selection:**
   - Representative families: GPT (OpenAI), Claude (Anthropic), Llama (Meta)
   - API access: OpenAI API, Anthropic API, Together AI/Replicate

**Dataset Access:**

```python
from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="thu-ml/MultiTrust",
    local_dir="./data/multitrust",
    repo_type="dataset",
    allow_patterns=['*']
)
```

**Sources:**
- MultiTrust HuggingFace dataset
- TrustLLM GitHub repository
- OpenAI/Anthropic/Together AI API documentation

---

## GitHub Implementation Survey

### Repository 1: KaveIO/PhiK

**URL:** https://github.com/KaveIO/PhiK
**Stars:** 75+
**Relevance:** Production-grade phi coefficient library

**Key Features:**
- Works with categorical, ordinal, interval variables
- Captures non-linear dependency
- Statistical significance evaluation built-in
- Python ≥3.8

**Installation:**
```bash
pip install phik
```

**Usage:**
```python
import phik
phi_k_matrix = data.phik_matrix()
significance = data.significance_matrix()
```

**Decision:** Use as fallback if scipy implementation shows instability.

---

### Repository 2: HowieHwong/TrustLLM

**URL:** https://github.com/HowieHwong/TrustLLM
**Stars:** 500+ (ICML 2024)
**Relevance:** Reference framework for multi-dimensional evaluation

**Key Features:**
- 8-dimension evaluation pipeline
- Supports multiple API providers
- Standardized benchmarks
- pip installable: `pip install trustllm==0.2.1`

**Usage Patterns:**
- API integration examples
- Sample size guidance (500-1000 typical)
- Evaluation protocol design

**Decision:** Reference for evaluation pipeline structure, not directly used (custom phi coupling analyzer).

---

### Repository 3: SciPy Official

**URL:** https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chi2_contingency.html
**Relevance:** Standard library implementation

**Implementation:**
```python
from scipy.stats import chi2_contingency
import numpy as np

table = np.array([[n11, n10], [n01, n00]])
chi2, p_value, dof, expected = chi2_contingency(table)
phi = np.sqrt(chi2 / table.sum())
```

**Assumptions:**
- ≥5 observations per cell required
- Returns: chi2 statistic, p-value, degrees of freedom, expected frequencies

**Decision:** Primary implementation method.

---

## Implementation Strategy

### Selected Approach

**Primary Implementation:** Custom coupling analyzer using scipy + sklearn
- scipy.stats.chi2_contingency for chi-square test + p-value
- sklearn.metrics.matthews_corrcoef for phi coefficient verification
- Justification: Standard statistical libraries sufficient for contingency table analysis

**Fallback:** KaveIO/PhiK library if numerical instability detected

**Rationale:**
- No complex mechanism requiring paper reproduction
- Standard libraries well-validated
- Direct control over implementation for verification

### Dataset Selection

**Chosen:** MultiTrust (thu-ml/MultiTrust on HuggingFace)

**Justification:**
- Real, established benchmark (not synthetic)
- 5 trustworthiness dimensions (10 pairwise combinations)
- Sufficient sample size for statistical validity
- Publicly available
- Multi-modal LLM coverage

### Model Selection

**Chosen:** GPT-4, Claude 3, Llama 3 (API-based)

**Justification:**
- Representative of major model families
- API access available (no internal state needed)
- Black-box evaluation aligns with hypothesis (behavioral coupling)
- Standard evaluation protocol

### Configuration

**API Settings:**
- Temperature: 0.0 (deterministic)
- Max Tokens: 512
- Seed: 42 (reproducibility)
- Batch Size: 10 (rate limit consideration)

**Sample Size:** 500 instances per model (per Phase 2B specification)

---

## Mechanism Verification Planning

### Pre-conditions Verified

| Check | Status | Evidence |
|-------|--------|----------|
| Mechanism Exists | ✅ TRUE | Statistical analysis code (phi coefficient, chi-square) |
| Mechanism Isolatable | ✅ TRUE | Can compare coupling vs no-coupling baseline |
| Baseline Measurable | ✅ TRUE | Independent dimension evaluation (no coupling analysis) |

### Activation Indicators

| Type | Expected Signal | Location |
|------|----------------|----------|
| Log Message | "Computing phi coefficient for {dim1} × {dim2}" | coupling_analyzer.py:compute_coupling() |
| Data Structure | 2×2 contingency table constructed | coupling_analyzer.py:compute_coupling() |
| Metric Output | phi ∈ [0, 1], p_value ∈ [0, 1] returned | coupling_analyzer.py:analyze_model() |

### Failure Modes

| Mode | Detection | Action |
|------|-----------|--------|
| No coupling log | Log missing "Computing phi" | FAIL: Analysis not run |
| Invalid phi | phi < 0 or phi > 1 | FAIL: Computation error |
| All p-values NaN | Missing significance tests | FAIL: Statistical test not executed |
| Zero valid pairs | No contingency tables | FAIL: Data preparation failed |

---

## Traceability Matrix

| Specification | Source Type | Reference |
|--------------|-------------|-----------|
| Dataset selection | Web Research | MultiTrust (thu-ml/MultiTrust) |
| Sample size (500) | Web Research | TrustLLM standard practices |
| Model APIs | Web Research | OpenAI/Anthropic/Together docs |
| Phi coefficient | GitHub/Docs | scipy.stats, sklearn.metrics |
| Chi-square test | GitHub/Docs | scipy.stats.chi2_contingency |
| Contingency table | Web Research | Statistical methodology |
| Evaluation protocol | Web Research | TrustLLM framework |
| Success criteria | Phase 2B | 02b_verification_plan.md |
| Mechanism verification | Template | mechanism_verification_protocol.md |

**All Sources Publicly Accessible:** ✅

---

## Research Completion Summary

**Date Completed:** 2026-08-19

**Research Mode:** Web Research (Archon/Exa MCP unavailable)

**Key Decisions:**
1. Dataset: MultiTrust (real benchmark, not synthetic)
2. Implementation: scipy + sklearn (standard libraries)
3. Models: GPT-4, Claude 3, Llama 3 (API-based)
4. Sample Size: 500 instances per model
5. Success Criteria: phi ≥ 0.3, p < 0.01 for ≥1 dimension pair

**Next Phase:** Phase 3 - Implementation Planning

---

*Research conducted using web search alternative to Archon/Exa MCP*
*All specifications grounded in peer-reviewed literature and production implementations*
