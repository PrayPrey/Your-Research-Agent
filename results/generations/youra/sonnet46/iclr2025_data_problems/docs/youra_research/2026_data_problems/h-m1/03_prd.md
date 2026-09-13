# Product Requirements Document: H-M1
# Conditional Log-Odds Demographic-Occupation Analysis Pipeline

**Hypothesis ID:** H-M1
**Hypothesis Type:** MECHANISM (Causal Chain Step 1: Corpus → Log-Odds)
**Generated:** 2026-03-14
**Phase:** 3 - Implementation Planning
**Source:** 02c_experiment_brief.md
**Base Hypothesis:** H-E1 (COMPLETED, PASS)

---

## Frontmatter

```yaml
stepsCompleted:
  - Executive Summary
  - Problem Statement
  - Functional Requirements
  - Non-Functional Requirements
  - Data Specification
  - Dependencies
  - Success Criteria
```

---

## 1. Executive Summary

H-M1 is a **corpus statistical analysis experiment** testing whether different data curation paths applied to DCLM-POOL produce systematically varying conditional log-odds of demographic-occupation co-occurrences. H-M1 extends H-E1 (aggregate entropy) to finer-grained per-pair log-odds analysis. No model training is required.

**Core Question:** Do the conditional log-odds P(occupation|demographic) / P(occupation|~demographic) vary monotonically with fastText filtering intensity (Spearman ρ ≠ 0, p < 0.05), establishing the corpus-level mechanism driving differential fairness outcomes?

**Gate:** MUST_WORK — if log-odds do not vary significantly with filtering intensity, the H-M2 → H-M3 chain is blocked.

**Key Design:** H-M1 reuses corpus subsets C1–C6 computed in H-E1. No re-filtering. Only a new log-odds computation layer on top of existing co-occurrence infrastructure.

---

## 2. Problem Statement

### 2.1 Background

H-E1 established that fastText quality filtering creates monotonic shifts in aggregate H(occupation|demographic): Spearman ρ = -1.0, -22.41% relative change (C1→C5). H-M1 investigates the finer-grained mechanism: do individual demographic-occupation conditional log-odds also vary systematically? This is Causal Chain Step 1 in the PCFH: corpus curation → differential log-odds → differential logit structures → fairness benchmark divergence.

### 2.2 Hypothesis Statement

Under controlled corpus conditions, if different curation paths (fastText filtering at 10%-90% percentile cutoffs, DoReMi domain reweighting) are applied to Dolma/DCLM-POOL, then the conditional log-odds of demographic-occupation co-occurrences will vary systematically across configurations in a manner correlated with filtering intensity (Spearman ρ ≠ 0 across configurations), because fastText assigns differential quality scores correlated with demographic register, and DoReMi shifts domain proportions with known demographic distribution differences.

### 2.3 Why This Experiment

H-E1 proved the existence of differential H(occupation|demographic). H-M1 characterizes the functional mechanism — the direction, magnitude, and pair-level specificity of log-odds variation — providing the statistical fingerprint needed to predict H-M2 logit structure effects.

---

## 3. Functional Requirements

### FR-1: Corpus Data Access (H-E1 Reuse)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1.1 | Load H-E1 corpus subsets C1–C6 from `h-e1/code/` or `h-e1/data/` | Must Have |
| FR-1.2 | If H-E1 subsets unavailable, regenerate from DCLM-POOL using H-E1 corpus_filter.py | Must Have |
| FR-1.3 | Verify each subset contains at least 500K tokens for statistical power | Must Have |
| FR-1.4 | Apply identical demographic + occupation lexicons from H-E1 (no new lexicon) | Must Have |

**Configuration C1–C6 (reused from H-E1):**

| Config | Type | Filter Level |
|--------|------|--------------|
| C1 | fastText ≥ 10th percentile | Lowest filtering |
| C2 | fastText ≥ 30th percentile | Low filtering |
| C3 | fastText ≥ 50th percentile | Medium filtering |
| C4 | fastText ≥ 70th percentile | High filtering |
| C5 | fastText ≥ 90th percentile | Highest filtering |
| C6 | DoReMi domain reweighting | External comparison |

### FR-2: Log-Odds Computation

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-2.1 | For each corpus subset C1–C6, compute co-occurrence counts in sliding window (window=5) | Must Have |
| FR-2.2 | For each (demographic, occupation) pair, compute 2×2 contingency table: (demo∩occ, demo∩¬occ, ¬demo∩occ, ¬demo∩¬occ) | Must Have |
| FR-2.3 | Apply Laplace smoothing α=0.5 to all cells (prevents log(0) on sparse pairs) | Must Have |
| FR-2.4 | Compute log-odds ratio: log(P(occ|demo)/P(occ|¬demo)) using statsmodels.stats.contingency_tables.Table2x2 | Must Have |
| FR-2.5 | Compute 95% CI for each log-odds pair via Table2x2.log_oddsratio_confint() | Should Have |
| FR-2.6 | Aggregate log-odds into matrix shape: (N_demo × N_occ) per configuration | Must Have |
| FR-2.7 | Compute mean log-odds per configuration as aggregate signal | Must Have |

### FR-3: Statistical Analysis

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-3.1 | Compute Spearman ρ: mean_log_odds ~ filtering_intensity [10, 30, 50, 70, 90] using scipy.stats.spearmanr | Must Have |
| FR-3.2 | Bootstrap 95% CI for Spearman ρ using scipy.stats.bootstrap (n=1000, paired=True, seed=42) | Must Have |
| FR-3.3 | OLS regression: log-odds ~ percentile cutoff using statsmodels.OLS (R², coefficient β) | Must Have |
| FR-3.4 | Mann-Whitney U test: log-odds distributions C5 vs C6 (fastText extreme vs DoReMi) | Should Have |
| FR-3.5 | Kolmogorov-Smirnov test: C1 vs C5 log-odds distributions | Should Have |
| FR-3.6 | Per-(demographic, occupation) pair Spearman ρ heatmap to identify which pairs drive the effect | Should Have |

### FR-4: Gate Evaluation

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-4.1 | Primary gate: |ρ| > 0 AND p < 0.05 | Must Have |
| FR-4.2 | Record: rho, pvalue, bootstrap_ci_low, bootstrap_ci_high | Must Have |
| FR-4.3 | Record gate result in results.json and 04_validation.md | Must Have |
| FR-4.4 | Mechanism activation verification: log-odds computed for all 6 configs | Must Have |

### FR-5: Visualization

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-5.1 | Gate Metrics: Spearman ρ bar/violin chart with 95% CI | Must Have |
| FR-5.2 | Log-Odds vs Filtering Intensity: scatter + OLS regression line (C1–C5), DoReMi highlighted | Should Have |
| FR-5.3 | Log-Odds Heatmap: (demographic × occupation) per configuration | Should Have |
| FR-5.4 | FastText vs DoReMi: violin plots of log-odds distributions C5 vs C6 | Should Have |
| FR-5.5 | All figures saved to h-m1/figures/ as PNG | Must Have |

### FR-6: Reporting

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-6.1 | Write results.json with all metrics and gate result | Must Have |
| FR-6.2 | Write 04_validation.md with gate evaluation and key findings | Must Have |
| FR-6.3 | Log-odds matrix saved as h-m1/data/log_odds_matrix.csv for downstream use (H-M2) | Should Have |

---

## 4. Non-Functional Requirements

| ID | Requirement | Detail |
|----|-------------|--------|
| NFR-1 | Reproducibility | seed=42 throughout; all random operations seeded |
| NFR-2 | Reuse H-E1 | Import/call h-e1/code/ modules directly; no duplication |
| NFR-3 | Statistical correctness | Laplace smoothing α=0.5; avoid log(0) |
| NFR-4 | FULL tier infrastructure | YAML + dataclass config, structured logging, unit tests |
| NFR-5 | Runtime | Complete in <2 hours on a single GPU-free node (CPU-only corpus analysis) |
| NFR-6 | Code organization | h-m1/code/ separate from h-e1/code/; import h-e1 via relative path |

---

## 5. Data Specification

### 5.1 Primary Dataset

**Dataset:** mlfoundations/dclm-baseline-1.0 (DCLM-POOL)
- **Source:** HuggingFace Datasets
- **Size:** ~3.8B documents (~3.4TB)
- **Access:** Streaming via HuggingFace
- **Download Required:** NO — reuse H-E1 filtered subsets (already computed)
- **Load Code:**
```python
# Reuse from h-e1/code/ — call h-e1 modules directly
import sys
sys.path.insert(0, 'h-e1/code')
from corpus_filter import CorpusFilter
# Load H-E1 corpus subsets (C1-C6)
cf = CorpusFilter(fasttext_model_path=config["fasttext_model_path"])
for config_id in ['C1', 'C2', 'C3', 'C4', 'C5', 'C6']:
    docs = cf.load_corpus(config_id, data_dir='h-e1/data')
```

### 5.2 Lexicons (from H-E1)

**Demographic Lexicon (N=26 tokens):** Same as H-E1 config — gendered pronouns + demographic NEs
**Occupation Lexicon (N=60 tokens):** Same 60 WinoBias occupations as H-E1

### 5.3 Statistical Methods (no download required)

```python
# All standard scientific Python stack
import scipy.stats          # spearmanr, bootstrap, mannwhitneyu, ks_2samp
import statsmodels.api as sm # OLS, Table2x2
import numpy as np
import pandas as pd
```

---

## 6. Success Criteria

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Gate PASS | Spearman ρ ≠ 0 AND p < 0.05 | spearmanr(filtering_intensity, mean_log_odds) |
| Mechanism Activated | 6/6 configs computed | Shape check: log_odds_matrix.shape[1] == 6 |
| Effect Detectable | Δmean_log_odds(C5-C1) ≠ 0 | Numerical comparison |
| Full Audit Trail | results.json + 04_validation.md | File existence check |

**Gate FAIL condition:** |ρ| < 0.3 OR p ≥ 0.05 → blocks H-M2, H-M3

---

## 7. Dependencies

### 7.1 Python Packages

| Package | Version | Purpose |
|---------|---------|---------|
| scipy | >=1.11.0 | spearmanr, bootstrap, mannwhitneyu, ks_2samp |
| statsmodels | >=0.14.0 | OLS regression, Table2x2 log-odds |
| numpy | >=1.24.0 | Array operations, Laplace smoothing |
| pandas | >=2.0.0 | DataFrame for log-odds matrix, CSV I/O |
| matplotlib | >=3.7.0 | Figure generation |
| seaborn | >=0.12.0 | Heatmap, violin plots |
| tqdm | >=4.65.0 | Progress bars |
| pyyaml | >=6.0 | Config loading |
| jsonlines | >=3.1.0 | Corpus JSONL I/O (via H-E1 module) |

### 7.2 Internal Dependencies

| Module | Source | Usage |
|--------|--------|-------|
| h-e1/code/corpus_filter.py | H-E1 | Load C1–C6 corpus subsets via load_corpus() |
| h-e1/code/config.py | H-E1 | CONFIGURATIONS dict, OCCUPATION_LEXICON, DEMOGRAPHIC_LEXICON |
| h-e1/data/corpora/ | H-E1 | C1.jsonl – C6.jsonl corpus subsets |

### 7.3 External Reference Repositories

| Repo | URL | Usage |
|------|-----|-------|
| statsmodels | docs | Table2x2 log-odds API |
| scipy | docs | spearmanr, bootstrap API |
| tolga-b/debiaswe | GitHub | Occupation word list reference |

---

## 8. Implementation Boundaries

**In Scope:**
- Log-odds computation layer on H-E1 corpus subsets
- Spearman ρ gate evaluation
- H-M1-specific visualization
- results.json + 04_validation.md generation

**Out of Scope:**
- Any model training (H-M2 domain)
- Re-filtering DCLM-POOL (H-E1 already done)
- New lexicon design (reuse H-E1)
- New corpus sampling (reuse H-E1)
