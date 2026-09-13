# Experiment Design: H-E1

**Date:** 2026-08-04
**Author:** Anonymous
**Hypothesis Statement:** Under the TrustLLM 16-model × 6-dimension evaluation setting, if we compute partial Spearman rank correlations for all 15 dimension pairs controlling for log(param_count) and RLHF status, then at least one correlation will be statistically significant (|ρ_partial| > 0.5, p < 0.0033 Bonferroni-corrected), because LLM trustworthiness dimensions are not statistically independent — RLHF optimization systematically co-moves related dimensions.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** Yes (no prerequisites — foundation hypothesis)
**Gate Status:** MUST_WORK — at least 1 of 15 |ρ_partial| > 0.5, p < 0.0033

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition

MUST_WORK: At least one of 15 partial Spearman correlations must be statistically significant (|ρ_partial| > 0.5, p < 0.0033 after Bonferroni correction for 15 tests). If this gate fails, the pipeline STOPS and pivots to lm-eval-harness data collection.

---

## Continuation Context

No previous hypothesis — H-E1 is the foundation of the verification chain. Previous context: null.

### Previous Hypothesis Results (if applicable)
None — first hypothesis in the dependency chain.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Note:** Archon KB is currently populated with diffusion model content (HuggingFace diffusers, Stable Diffusion) and does not contain directly relevant entries for LLM trustworthiness correlation analysis. The following summarizes what was found and the alternative sources used.

**Query 1: "partial Spearman correlation experiment design LLM evaluation"**
- Results matched diffusion model papers (similarity ~0.36) — no relevant entries
- Key insight: Archon KB does not cover this statistical analysis domain; Exa searches are primary source

**Query 2: "Bonferroni correction multiple hypothesis testing"**
- Results matched diffusion model repos — no relevant entries
- Key insight: Standard scipy/statsmodels implementations used instead

**Query 3: "hierarchical clustering Ward linkage silhouette score sklearn" (code examples)**
- Results returned diffusion scheduler examples — no relevant entries
- Key insight: sklearn.cluster.AgglomerativeClustering documentation used directly via Exa

### Archon Code Examples

No relevant code examples found in Archon KB (domain mismatch: KB contains diffusion model code). All implementation patterns sourced from Exa GitHub and scipy/sklearn documentation below.

### Exa GitHub Implementations

**Query 1: TrustLLM HowieHwong results JSON score extraction partial correlation Python**

**Repository: HowieHwong/TrustLLM** (⭐ 628)
- **URL:** https://github.com/HowieHwong/TrustLLM
- **Relevance:** Primary data source — TrustLLM toolkit provides 6-dimension evaluation pipeline for 16 LLMs
- **Key Finding:** TrustLLM provides `run_truthfulness`, `run_safety`, `run_fairness`, `run_robustness`, `run_privacy`, `run_ethics` pipeline functions. Results stored as JSON per dimension. The `results/` folder contains per-model per-dimension numeric scores (not just rankings) — confirmed by evaluation toolkit returning dictionaries of float metrics.
- **Data Format:** Per-model JSON files with float scores for each task within each dimension; dimension scores are averaged or aggregated from subtask metrics.
- **Loading Code:**
  ```python
  import json, glob
  import numpy as np
  
  # Load all result JSONs from TrustLLM results/ directory
  results = {}
  for path in glob.glob("TrustLLM/results/*.json"):
      with open(path) as f:
          results[path] = json.load(f)
  ```
- **Dimensions confirmed:** truthfulness, safety, fairness, robustness, privacy, machine_ethics (6 total)

**Repository: StackOverflow partial Spearman via OLS residualization**
- **URL:** https://stackoverflow.com/questions/73633787/get-partial-correlations-matrix-from-pandas-dataframe-using-spearman
- **Relevance:** Direct implementation pattern for the core analysis
- **Key Code:**
  ```python
  from itertools import combinations
  from sklearn import linear_model
  from scipy.stats import spearmanr
  import pandas as pd
  
  def part_corr(df, var1, var2, rest):
      var1_reg = linear_model.LinearRegression().fit(df[rest], df[var1])
      var2_reg = linear_model.LinearRegression().fit(df[rest], df[var2])
      var1_res = df[var1] - var1_reg.predict(df[rest])
      var2_res = df[var2] - var2_reg.predict(df[rest])
      rho, pval = spearmanr(var1_res, var2_res)
      return rho, pval
  ```
- **Pattern:** OLS-residualize both variables on covariates [log_params, is_RLHF], then compute Spearman on residuals

**Query 2: Ward hierarchical clustering silhouette score scipy sklearn minimum spanning tree networkx**

**sklearn AgglomerativeClustering (Ward)**
- **URL:** https://sklearn.org/stable/modules/generated/sklearn.cluster.AgglomerativeClustering.html
- **Key Code:**
  ```python
  from sklearn.cluster import AgglomerativeClustering
  from sklearn.metrics import silhouette_score
  
  clustering = AgglomerativeClustering(n_clusters=2, linkage='ward').fit(distance_matrix)
  labels = clustering.labels_
  score = silhouette_score(distance_matrix, labels, metric='precomputed')
  ```
- **Note:** Ward linkage with precomputed distance matrix requires `metric='euclidean'` on feature matrix, not distance matrix directly. Use correlation matrix as feature input.

**networkx minimum_spanning_tree**
- **URL:** https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.tree.mst.minimum_spanning_tree.html
- **Key Code:**
  ```python
  import networkx as nx
  import numpy as np
  
  # Build complete graph from distance matrix (1 - |rho_partial|)
  G = nx.Graph()
  dims = ['truthfulness', 'safety', 'fairness', 'robustness', 'privacy', 'ethics']
  for i, d1 in enumerate(dims):
      for j, d2 in enumerate(dims):
          if i < j:
              weight = 1 - abs(rho_partial[i, j])
              G.add_edge(d1, d2, weight=weight)
  T = nx.minimum_spanning_tree(G, algorithm='kruskal')
  ```

**scipy.stats.spearmanr**
- **URL:** https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html
- **Key Finding:** For n=16 (small sample), p-value from asymptotic approximation is unreliable (accurate only for n>500). Use t-distribution: t = rho * sqrt((n-2)/(1-rho^2)), df = n-2-k where k=number of controls.

### 🎯 Implementation Priority Assessment

**CRITICAL: This is a statistical analysis experiment on pre-existing published data — not a paper reproduction.**

No official author implementation to target (this is novel analysis on TrustLLM data). Implementation uses standard scipy/sklearn/networkx stack.

**Recommended Implementation Path:**
- Primary: Direct implementation using scipy (spearmanr), sklearn (LinearRegression, AgglomerativeClustering), networkx (minimum_spanning_tree), pingouin (alternative for partial correlation validation)
- Fallback: pingouin.partial_corr(method='spearman') for cross-validation of OLS residualization approach
- Justification: OLS residualization is the standard approach for partial Spearman on small samples; pingouin provides independent validation

### Code Analysis (Serena MCP)

*Skipped* — Code from search results (StackOverflow, scipy/sklearn docs) was sufficiently clear and self-contained. No complex multi-file repository requiring semantic analysis. Serena analysis not required.

---

## Experiment Specification

### Dataset

**Name:** TrustLLM Published Score Tables
**Type:** standard (programmatic-api)
**Source:** HowieHwong/TrustLLM GitHub repository, results/ folder
**Version:** v0.3.0 (ICML 2024, [Sun et al., 2024])

**Description:**
- 16-model × 6-dimension evaluation scores
- 6 dimensions: Truthfulness, Safety, Fairness, Robustness, Privacy, Machine Ethics
- Each model has a scalar score per dimension (aggregated from multiple subtasks within each dimension)
- Models include: LLaMA-2-7b-base, LLaMA-2-7b-chat, LLaMA-2-13b-base, LLaMA-2-13b-chat, LLaMA-2-70b-base, LLaMA-2-70b-chat, Mistral-7b, Falcon-7b, Vicuna-7b, Vicuna-13b, Vicuna-33b, GPT-3.5-turbo, GPT-4, Claude-2, and others (~16 total as reported in TrustLLM paper)

**Sample Size:** N=16 models (full evaluation set; no subsampling)

**Model Annotations Required (to be assembled):**
| Model | log10(params) | is_RLHF |
|-------|---------------|---------|
| LLaMA-2-7b-base | 9.845 (7B) | 0 |
| LLaMA-2-7b-chat | 9.845 | 1 |
| LLaMA-2-13b-base | 10.114 (13B) | 0 |
| LLaMA-2-13b-chat | 10.114 | 1 |
| LLaMA-2-70b-base | 10.845 (70B) | 0 |
| LLaMA-2-70b-chat | 10.845 | 1 |
| Mistral-7b | 9.845 | 0 |
| Falcon-7b | 9.845 | 0 |
| Vicuna-7b | 9.845 | 1 (SFT/RLHF) |
| Vicuna-13b | 10.114 | 1 |
| GPT-3.5-turbo | 11.176 (~175B est.) | 1 |
| GPT-4 | 11.903 (~1T est.) | 1 |
| Claude-2 | 11.699 (~500B est.) | 1 |
| [remaining ~3 models per TrustLLM paper appendix] | | |

**Preprocessing:**
- Step 1: Clone HowieHwong/TrustLLM, navigate to results/ folder
- Step 2: For each model, extract per-dimension aggregate scores (float [0,1]) from JSON files
- Step 3: Build 16×6 pandas DataFrame (rows=models, cols=dimensions)
- Step 4: Add log10_params and is_RLHF columns per annotation table above
- Step 5: Check for floor/ceiling effects (any dimension with >20% models at 0 or 1 → report both Spearman and Pearson)

**Loading Information** (for Phase 4 download):
- Method: GitHub clone + JSON parsing (no HuggingFace dataset loader needed)
- Identifier: `https://github.com/HowieHwong/TrustLLM` → `results/` subfolder
- Code:
  ```python
  # Clone and load TrustLLM results
  # git clone https://github.com/HowieHwong/TrustLLM.git
  import json, os
  import pandas as pd
  
  results_dir = "TrustLLM/results"
  # Results are organized per dimension per model
  # Load and aggregate to per-model per-dimension scalar scores
  ```

### Models

#### Baseline Model

**Name:** Raw (uncontrolled) Spearman correlation matrix
**Description:** Standard pairwise Spearman ρ computed directly on 16×6 score matrix without controlling for confounds. Expected to show mostly positive correlations due to scale confound (larger/more capable models tend to score higher on all dimensions).
**Purpose:** Demonstrates that naive correlation analysis conflates RLHF and scale effects; motivates partial correlation approach.

**Configuration:**
```python
from scipy.stats import spearmanr
import numpy as np

# Baseline: raw Spearman on all 15 pairs
baseline_rho = np.zeros((6, 6))
baseline_pval = np.zeros((6, 6))
for i in range(6):
    for j in range(i+1, 6):
        rho, p = spearmanr(scores[:, i], scores[:, j])
        baseline_rho[i, j] = baseline_rho[j, i] = rho
        baseline_pval[i, j] = baseline_pval[j, i] = p
```

**Loading Information** (for Phase 4):
- Method: Computed directly from the 16×6 score matrix
- No external download required

#### Proposed Model

**Architecture:** Partial Spearman correlation matrix (baseline + OLS residualization controlling for [log_params, is_RLHF])

**Core Mechanism Implementation:**

```python
# Core Mechanism: Partial Spearman Correlation via OLS Residualization
# Based on: StackOverflow Q73633787, scipy spearmanr, sklearn LinearRegression
# Source: https://stackoverflow.com/questions/73633787/

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from scipy.stats import spearmanr
from scipy.stats import t as t_dist
from itertools import combinations

def compute_partial_spearman_matrix(scores_df, covariates_df, alpha_bonferroni=0.0033):
    """
    Compute 6x6 partial Spearman correlation matrix.
    Args:
        scores_df: DataFrame (16, 6) — trustworthiness dimension scores
        covariates_df: DataFrame (16, 2) — [log10_params, is_RLHF]
    Returns:
        rho_partial: (6, 6) ndarray — partial Spearman matrix
        pvals: (6, 6) ndarray — p-values (t-dist, df=n-2-k=13)
        significant_pairs: list of (dim_i, dim_j, rho, p) where p < alpha_bonferroni
    """
    dims = scores_df.columns.tolist()
    n = len(scores_df)
    k = covariates_df.shape[1]  # number of controls = 2
    df_resid = n - 2 - k  # = 12... wait: df = n - 2 for Spearman t-test
    # Standard partial Spearman t-test: df = n - 2 - k = 16 - 2 - 2 = 12
    
    rho_matrix = np.zeros((6, 6))
    pval_matrix = np.ones((6, 6))
    significant_pairs = []
    
    for i, dim_i in enumerate(dims):
        for j, dim_j in enumerate(dims):
            if i >= j:
                continue
            # OLS-residualize dim_i on covariates
            reg_i = LinearRegression().fit(covariates_df, scores_df[dim_i])
            res_i = scores_df[dim_i] - reg_i.predict(covariates_df)
            # OLS-residualize dim_j on covariates
            reg_j = LinearRegression().fit(covariates_df, scores_df[dim_j])
            res_j = scores_df[dim_j] - reg_j.predict(covariates_df)
            # Spearman on residuals
            rho, _ = spearmanr(res_i, res_j)
            # t-test with df = n - 2 - k = 12
            t_stat = rho * np.sqrt(df_resid / (1 - rho**2 + 1e-10))
            pval = 2 * t_dist.sf(abs(t_stat), df=df_resid)
            
            rho_matrix[i, j] = rho_matrix[j, i] = rho
            pval_matrix[i, j] = pval_matrix[j, i] = pval
            
            if abs(rho) > 0.5 and pval < alpha_bonferroni:
                significant_pairs.append((dim_i, dim_j, rho, pval))
    
    np.fill_diagonal(rho_matrix, 1.0)
    return rho_matrix, pval_matrix, significant_pairs
```

### Training Protocol

**No model training required.** This experiment is a statistical analysis on pre-existing published data.

**Analysis Protocol:**

**Step 1: Data Loading and Validation**
- Load TrustLLM results/*.json
- Build 16×6 score matrix
- Validate: check no missing values, check score ranges [0,1]
- Check VIF for [log_params, is_RLHF] covariates (if VIF > 5, flag multicollinearity risk)
- Check for floor/ceiling effects (>20% at 0 or 1 per dimension)

**Step 2: Partial Spearman Computation (H-E1 Primary)**
- Apply OLS residualization: for each dimension pair (15 pairs), regress both dimensions on [log10_params, is_RLHF], compute Spearman ρ on residuals
- Significance test: t-distribution with df = n - 2 - k = 12 (n=16, k=2 covariates)
- Bonferroni correction: α = 0.05 / 15 = 0.0033
- Output: 6×6 ρ_partial matrix, p-value matrix, list of significant pairs

**Step 3: Hierarchical Clustering (H-E1 Secondary)**
- Apply Ward hierarchical clustering on 6×6 ρ_partial matrix (use 1 - ρ_partial as distance after symmetrizing with abs)
- k=2 solution: compute silhouette score
- Compare cluster membership to predicted {safety, ethics} vs {robustness, calibration/privacy}

**Step 4: Sensitivity Check**
- Compare Spearman vs Pearson partial correlations (if signs diverge, flag)
- Report both raw and partial correlation matrices

**Seeds:** Not applicable (deterministic statistical analysis)

**Compute Requirements:** CPU-only, <1 minute runtime. No GPU required.

**Libraries:**
- numpy, pandas (data handling)
- scipy.stats (spearmanr)
- sklearn.linear_model (LinearRegression for OLS residualization)
- sklearn.cluster (AgglomerativeClustering)
- sklearn.metrics (silhouette_score)
- networkx (minimum_spanning_tree — used in H-E2, constructed here as secondary output)
- statsmodels (VIF check: variance_inflation_factor)
- pingouin (optional cross-validation of partial correlation)

### Evaluation

**Metric 1: Existence of Significant Partial Correlation (Primary Gate)**
- Definition: Count of pairs with |ρ_partial| > 0.5 AND p < 0.0033 (Bonferroni-corrected)
- Gate: count ≥ 1 → PASS; count = 0 → FAIL (MUST_WORK)
- Expected: ≥1 significant pair (pre-specified prediction from Phase 2A)

**Metric 2: Maximum |ρ_partial| (Informative)**
- Definition: max over all 15 pairs of |ρ_partial|
- Baseline (uncontrolled): Expected high (scale confound inflates raw Spearman)
- Proposed (partial): Expected to detect structure after removing scale/RLHF confounds

**Metric 3: Silhouette Score for k=2 Ward Clustering (Secondary)**
- Definition: sklearn.metrics.silhouette_score on 6×6 distance matrix (1 - |ρ_partial|)
- Success criterion: silhouette > 0.3
- Note: EXISTENCE PoC — direction check only (silhouette > 0 is already informative)

**Success Criteria:**
- **PoC Pass:** ≥1 pair with |ρ_partial| > 0.5 AND p < 0.0033
- **Secondary:** silhouette > 0.3 for k=2 Ward clustering
- **Relationship to baseline:** partial rho matrix should show cleaner cluster structure than raw uncontrolled rho matrix

**Expected Baseline Performance (from research):**
- Raw Spearman: Most pairs expected to be positive (scale confound), median ~0.4-0.6
- Source: Epoch AI general capability benchmark median ρ=0.73 (BUILD_ON fact from Phase 2A)
- Partial Spearman: After controlling for scale+RLHF, safety-ethics expected > 0.5; safety-robustness expected < -0.4

**Metrics Loading Information:**
- Task Type: statistical correlation analysis (no standard ML task)
- Library: scipy.stats (spearmanr), sklearn.metrics (silhouette_score)
- Code:
  ```python
  from scipy.stats import spearmanr
  from sklearn.metrics import silhouette_score
  from sklearn.cluster import AgglomerativeClustering
  
  # Silhouette on partial correlation distance matrix
  dist_matrix = 1 - np.abs(rho_partial)
  np.fill_diagonal(dist_matrix, 0)
  clustering = AgglomerativeClustering(n_clusters=2, metric='precomputed', linkage='average')
  # Note: Ward requires euclidean; use average linkage with precomputed distance for 6x6 matrix
  labels = clustering.fit_predict(dist_matrix)
  sil = silhouette_score(dist_matrix, labels, metric='precomputed')
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing |ρ_partial| for all 15 dimension pairs, with Bonferroni threshold line at 0.5, color-coded by significance

#### Additional Figures (LLM Autonomous)

Based on the hypothesis type and analysis, the following additional visualizations are recommended:

1. **Heatmap: Raw vs Partial Correlation Matrix** — Side-by-side 6×6 heatmaps showing how controlling for scale+RLHF changes the correlation structure (diverging colormap centered at 0)
2. **Dendrogram: Ward Hierarchical Clustering** — scipy.cluster.hierarchy.dendrogram on ρ_partial matrix, showing 2-cluster solution
3. **Scatter: Confound Demonstration** — For the most significant pair (e.g., safety vs ethics): raw scores scatter + residuals scatter (before/after residualization), colored by RLHF status

**Output Location:** `h-e1/figures/`

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (data loads, analysis completes)
2. At least 1 of 15 |ρ_partial| > 0.5 AND p < 0.0033 (Bonferroni-corrected)

**Note for Phase 4 Coder:** The MUST_WORK gate is purely statistical — no "proposed > baseline" comparison in the deep-learning sense. The "mechanism" here is OLS residualization + Spearman, and the gate is whether significant structure is detected after controlling for confounds.

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Archon KB Assessment:** KB contains diffusion model content (HuggingFace diffusers). No relevant entries for statistical correlation analysis of LLM trustworthiness. Archon KB is not a useful source for this experiment.

- Queries run: 2 KB queries + 1 code example query
- Match quality: Low (similarity ~0.27-0.36, all matched diffusion model content)
- Decision: Use Exa findings as sole MCP source for this experiment

### B. GitHub Implementations (Exa)

**Source B.1: HowieHwong/TrustLLM (⭐ 628)**
- **URL:** https://github.com/HowieHwong/TrustLLM
- **Query:** "TrustLLM HowieHwong results JSON score extraction partial correlation Python"
- **Relevance:** Primary data source — confirms 6-dimension evaluation structure, JSON format, per-model float scores
- **Configuration extracted:** 6 dimensions confirmed: truthfulness, safety, fairness, robustness, privacy, machine_ethics
- **Used for:** Dataset specification, loading code

**Source B.2: TrustLLM Evaluation Docs**
- **URL:** https://howiehwong.github.io/TrustLLM/guides/evaluation.html
- **Query:** Same as B.1
- **Relevance:** Confirms evaluation pipeline returns float metric dictionaries per dimension
- **Key insight:** `run_safety()`, `run_ethics()`, etc. return per-model numeric scores that can be extracted into scalar summaries
- **Used for:** Dataset loading verification

**Source B.3: StackOverflow — Partial Spearman via OLS Residualization**
- **URL:** https://stackoverflow.com/questions/73633787/get-partial-correlations-matrix-from-pandas-dataframe-using-spearman
- **Query:** "partial Spearman rank correlation OLS residualization scipy Python implementation"
- **Relevance:** Direct implementation pattern for the core mechanism
- **Key Code (annotated):**
  ```python
  # OLS residualization approach for partial Spearman:
  # 1. Regress variable X on covariates Z → get residuals res_X
  # 2. Regress variable Y on covariates Z → get residuals res_Y
  # 3. Compute Spearman(res_X, res_Y)
  # This is mathematically equivalent to partial Pearson on ranks
  
  def part_corr(df, var1, var2, rest):
      var1_reg = LinearRegression().fit(df[rest], df[var1])
      var2_reg = LinearRegression().fit(df[rest], df[var2])
      var1_res = df[var1] - var1_reg.predict(df[rest])
      var2_res = df[var2] - var2_reg.predict(df[rest])
      return spearmanr(var1_res, var2_res)
  ```
- **Used for:** Core mechanism pseudo-code

**Source B.4: scipy.stats.spearmanr documentation**
- **URL:** https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html
- **Key insight:** For n=16, asymptotic p-value unreliable (accurate only n>500). Use t-distribution: t = ρ√((n-2-k)/(1-ρ²)), df = n-2-k = 12
- **Used for:** Significance testing protocol

**Source B.5: sklearn AgglomerativeClustering Ward**
- **URL:** https://sklearn.org/stable/modules/generated/sklearn.cluster.AgglomerativeClustering.html
- **Key insight:** Ward linkage requires euclidean distance, not precomputed. For 6×6 correlation matrix, use the matrix directly as feature space, or use average linkage with precomputed distance.
- **Used for:** Hierarchical clustering step

**Source B.6: networkx minimum_spanning_tree**
- **URL:** https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.tree.mst.minimum_spanning_tree.html
- **Key insight:** `nx.minimum_spanning_tree(G, algorithm='kruskal')` takes weighted graph with edge weight = 1 - |ρ_partial|
- **Used for:** MST construction (H-E2 prerequisite output, constructed here)

### C. Code Analysis (Serena)

*Skipped* — Code from StackOverflow and scipy/sklearn documentation was sufficiently clear and self-contained. All patterns fit in <30 lines. Serena analysis not required.

### D. Previous Hypothesis Context

**Previous Context:** None — H-E1 is the foundation hypothesis with no prerequisites.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (TrustLLM, 16×6 matrix) | Exa/GitHub | B.1 (HowieHwong/TrustLLM) |
| Dataset format (float scores per dimension) | Exa/Web | B.2 (TrustLLM evaluation docs) |
| Partial Spearman via OLS residualization | Exa/StackOverflow | B.3 (SO Q73633787) |
| Significance testing (t-dist, df=n-2-k) | Exa/scipy docs | B.4 (scipy spearmanr) |
| Bonferroni α = 0.0033 | Phase 2B plan | 02b_verification_plan.md H-E1 spec |
| Ward clustering, k=2 | Exa/sklearn docs | B.5 (AgglomerativeClustering) |
| MST (for H-E2 prerequisite) | Exa/networkx docs | B.6 (nx.minimum_spanning_tree) |
| Silhouette > 0.3 threshold | Phase 2B plan | 02b_verification_plan.md H-E1 spec |
| n=16 model annotation (log_params, is_RLHF) | Phase 2B plan | 02b_verification_plan.md Section 1.3 |
| Core mechanism pseudo-code | Exa/StackOverflow | B.3, B.4 |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-04

### Workflow History for This Hypothesis

- Phase 2B completed: 2026-08-04 — verification plan established H-E1 as foundation hypothesis
- Phase 2C started: 2026-08-04 — experiment design initiated (UNATTENDED mode)
- Phase 2C completed: 2026-08-04 — experiment brief generated

---

*MCP Tools Used: Archon (KB + Code, low relevance), Exa (GitHub + Web, primary source), Serena (skipped — code sufficiently clear)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
