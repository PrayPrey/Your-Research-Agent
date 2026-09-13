# Experiment Design: H-E2

**Date:** 2026-08-04
**Author:** Anonymous
**Hypothesis Statement:** Under the TrustLLM 16-model evaluation setting, if we construct the minimum spanning tree (MST) of the partial Spearman distance matrix (1-|ρ_partial|), then the MST will identify a minimum sufficient evaluation set of ≤4 dimensions with ≥90% bootstrap topology stability (1000 resamples of 14/16 models), because the correlation structure is strong enough to make some dimensions redundant for evaluation purposes.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-E1 COMPLETED (PASS) ✅ — 8/15 significant pairs, silhouette=0.614
**Gate Status:** MUST_WORK (primary: MST set ≤4 dims; secondary: bootstrap stability ≥0.90)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E2
- **Type:** EXISTENCE
- **Prerequisites:** H-E1 (COMPLETED — PASS)

### Gate Condition
MUST_WORK: MST minimum evaluation set ≤4 dimensions AND bootstrap topology stability ≥0.90.
Failure action: EXPLORE — report full correlation structure as null result; consider Pythia expansion to increase n.

---

## Continuation Context

H-E2 is a continuation of H-E1. The ρ_partial matrix and all preprocessing decisions are **inherited** from H-E1. The experiment directly builds on H-E1's output (h-e1/experiment_results_phase3.json).

### Previous Hypothesis Results (H-E1)
- **Gate:** PASSED (MUST_WORK) ✅
- **Key output:** 6×6 partial Spearman correlation matrix (rho_partial) with covariates [log10_params, is_RLHF]
- **Significant pairs (8/15):** safety-privacy (ρ=0.9706), truthfulness-fairness (ρ=0.9353), fairness-privacy (ρ=0.8941), safety-fairness (ρ=0.8588), privacy-machine_ethics (ρ=0.8588), safety-machine_ethics (ρ=0.8412), fairness-machine_ethics (ρ=0.7824), truthfulness-privacy (ρ=0.7324)
- **Robustness:** No significant pairs — behaves as isolated node, expected to be a leaf/outlier in MST
- **MST note:** 5-edge MST already constructed in H-E1 code as prerequisite output
- **Runtime:** <2s CPU (no training required)
- **Code location:** h-e1/code/ (data_loader.py, analysis.py, clustering.py, visualization.py, main.py)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "minimum spanning tree correlation matrix bootstrap stability"**
- Results returned: 5 pages (diffusers/stable-diffusion KB — LOW RELEVANCE)
- Relevance: 0.34 similarity max — Archon KB contains diffusion model content, not MST/statistics
- Useful insight: None directly applicable

**Query 2: "networkx MST Kruskal distance matrix implementation"**
- Results returned: 3 pages (overleaf/nvidia/diffusion — LOW RELEVANCE)
- Useful insight: None directly applicable

**Summary:** Archon KB is a diffusion-model knowledge base and does not contain MST/correlation analysis content. All substantive research came from Exa.

### Archon Code Examples

**Query: "minimum spanning tree networkx scipy bootstrap"**
- Results returned: 5 examples (all stable diffusion inference code — LOW RELEVANCE)
- No applicable code patterns found in Archon KB

### Exa GitHub Implementations

**Query 1: "networkx minimum_spanning_tree Spearman correlation distance matrix bootstrap topology stability Python"**

**Source 1**: NetworkX 3.6.1 Official Documentation
- **URL:** https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.tree.mst.minimum_spanning_tree.html
- **Relevance:** Core API for MST construction
- **Key API:**
  ```python
  import networkx as nx
  T = nx.minimum_spanning_tree(G, weight='weight', algorithm='kruskal')
  ```
- **Notes:** Default is Kruskal's algorithm. Input must be undirected weighted graph. Returns MST as NetworkX Graph.

**Source 2**: Millington & Niranjan (2021) — "Construction of MSTs from Financial Returns using Rank Correlation"
- **URL:** https://ar5iv.labs.arxiv.org/html/2005.03963
- **Relevance:** ⭐⭐⭐ HIGHEST — directly uses Spearman MST with bootstrap stability analysis
- **Key findings:**
  - Spearman-based MSTs are MORE STABLE than Pearson MSTs under bootstrap
  - Distance metric: d_ij = sqrt(2(1-ρ_ij)) [Mantegna 1999] OR d_ij = 1-|ρ_ij| (our approach)
  - Bootstrap: 1000 pseudo-datasets, compare edge sets between bootstrap MSTs and original
  - Code: https://github.com/shazzzm/rank_correlation_msts (uses TopCorr + NetworkX)
  - Metric for stability: "fraction of difference in edge presence across MSTs"
  - Result: Rank-based MSTs show strong agreement across bootstrap samples at all times

**Source 3**: Musciotto et al. (2018) — "Bootstrap validation of links of a minimum spanning tree"
- **URL:** https://ar5iv.labs.arxiv.org/html/1802.03395
- **Relevance:** ⭐⭐⭐ HIGHEST — defines the bootstrap link reliability methodology
- **Key methodology:**
  - r=1000 bootstrap replicas (standard in phylogenetic analysis)
  - "Row bootstrap": resample rows of data matrix with replacement
  - Bootstrap value = fraction of bootstrap MSTs containing each link
  - Global reliability = mean bootstrap value across all links
  - Recommends both "row bootstrap" and "pair bootstrap" for complementary information

**Source 4**: Tumminello et al. (2007) — "Spanning Trees and bootstrap reliability estimation"
- **URL:** https://ar5iv.labs.arxiv.org/html/physics/0605116
- **Relevance:** ⭐⭐ HIGH — original bootstrap MST stability framework
- **Key insight:** Average bootstrap value across all MST links = global reliability measure
- **Our adaptation:** topology stability = proportion of bootstrap samples with identical edge set to original MST (stricter than average link reliability)

**Source 5**: Shayan-Akhavan/pybootnet (GitHub)
- **URL:** https://github.com/Shayan-Akhavan/pybootnet
- **Relevance:** ⭐ LOW — network bootstrapping utility, limited to correlation threshold graphs (not MST)
- **Note:** Uses `bootstrap_replicates()` + `correlation_matrix()` + `build_network_graph()` pattern

**Query 2: "TrustLLM evaluation scores JSON loading partial Spearman correlation Python scipy"**

**Source 6**: HowieHwong/TrustLLM Official Repository
- **URL:** https://github.com/HowieHwong/TrustLLM
- **Relevance:** ⭐⭐⭐ HIGHEST — exact data source
- **Key findings:**
  - 6 dimensions: truthfulness, safety, fairness, robustness, privacy, machine_ethics
  - JSON files in results/ folder with per-model per-dimension scores
  - Already downloaded and used in H-E1; scores in h-e1/experiment_results_phase3.json

**Source 7**: scipy.stats.spearmanr documentation
- **URL:** https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html
- **Relevance:** ⭐⭐ HIGH — core statistical API
- **Key note:** For n=16, asymptotic p-values may be unreliable; consider permutation test — but H-E1 already validated using t-distribution with df=12, so same approach applies here

**Serena Analysis Needed**: false — code is based on pure numpy/scipy/networkx, sufficiently clear from documentation

### 🎯 Implementation Priority Assessment

**This is NOT a paper reproduction experiment** — it is an original analysis using TrustLLM published scores. No "author's official implementation" exists for this specific MST analysis. Implementation path:

**Primary:** Custom Python implementation using:
- networkx.minimum_spanning_tree (Kruskal) on 6×6 distance matrix derived from H-E1 ρ_partial matrix
- Bootstrap: numpy random sampling (resample 14/16 models 1000 times), recompute ρ_partial via OLS residualization, compare edge sets

**Fallback:** scipy.sparse.csgraph.minimum_spanning_tree if networkx shows issues

**Recommended Implementation Path:**
- Primary: networkx + scipy.stats + numpy (all standard, already used in H-E1)
- Fallback: scipy.sparse.csgraph.minimum_spanning_tree
- Justification: H-E1 already uses this stack; maximum code reuse, minimal new dependencies

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. The MST algorithm is a standard networkx call; the bootstrap is pure numpy. No complex custom layers requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Name:** TrustLLM Published Score Tables (16×6 matrix) — DERIVED from H-E1
**Type:** standard (real, established dataset — NOT synthetic)
**Source:** HowieHwong/TrustLLM (GitHub) — results/*.json
**Derived input:** h-e1/experiment_results_phase3.json (ρ_partial 6×6 matrix + raw 16×6 score matrix)

**Statistics:**
- N_models: 16 (full TrustLLM evaluation set — LLaMA-2 7B/13B/70B base+chat, Mistral-7B, Falcon-7B, GPT-3.5/4, Claude-2, Vicuna, etc.)
- N_dimensions: 6 (truthfulness, safety, fairness, robustness, privacy, machine_ethics)
- N_pairs: 15 (C(6,2))
- Bootstrap: 1000 resamples of 14/16 models (subsample size matches H-E1 spec)

**Loading Information** (for Phase 4 download):
- Method: File read from H-E1 output (no new download required)
- Identifier: `h-e1/experiment_results_phase3.json` (contains rho_partial matrix and raw scores)
- Code:
  ```python
  import json
  with open("h-e1/experiment_results_phase3.json") as f:
      h_e1_results = json.load(f)
  rho_partial = np.array(h_e1_results["rho_partial_matrix"])   # 6×6
  raw_scores = np.array(h_e1_results["raw_scores"])            # 16×6
  model_metadata = h_e1_results["model_metadata"]              # log10_params, is_RLHF per model
  ```

**Synthetic data check:** PASSED — TrustLLM published scores are real data from a peer-reviewed benchmark (Sun et al., ICML 2024). Type: standard.

### Models

#### Baseline Model

**Architecture:** Identity (no model — this is a statistical analysis, not a neural network experiment)
**Baseline method:** Raw Spearman correlation MST (uncontrolled, no OLS residualization)
- Construct distance matrix from raw Spearman ρ_raw (not partial)
- Apply MST
- Compare: does partial Spearman MST differ from raw Spearman MST in minimum set size?

**Loading Information** (for Phase 4 download):
- Method: Computed inline from raw_scores (no download)
- Identifier: N/A
- Code: `scipy.stats.spearmanr(raw_scores)` → raw ρ matrix

#### Proposed Model

**Architecture:** Partial Spearman MST + Bootstrap Stability Analysis

**Core Mechanism Implementation:**

```python
# Core Mechanism: MST Minimum Evaluation Set + Bootstrap Stability
# Based on: networkx docs, Millington & Niranjan (2021), Musciotto et al. (2018)

import numpy as np
import networkx as nx
from scipy import stats
from sklearn.linear_model import LinearRegression

def compute_rho_partial(scores_16x6, covariates_16x2):
    """
    Args:
        scores_16x6: ndarray (16, 6) — raw dimension scores
        covariates_16x2: ndarray (16, 2) — [log10_params, is_RLHF]
    Returns:
        rho_partial: ndarray (6, 6) — partial Spearman matrix
    """
    n_dims = scores_16x6.shape[1]
    rho_partial = np.zeros((n_dims, n_dims))
    for i in range(n_dims):
        for j in range(i+1, n_dims):
            # OLS residualization (same as H-E1)
            res_i = scores_16x6[:, i] - LinearRegression().fit(
                covariates_16x2, scores_16x6[:, i]).predict(covariates_16x2)
            res_j = scores_16x6[:, j] - LinearRegression().fit(
                covariates_16x2, scores_16x6[:, j]).predict(covariates_16x2)
            rho, _ = stats.spearmanr(res_i, res_j)
            rho_partial[i, j] = rho_partial[j, i] = rho
    np.fill_diagonal(rho_partial, 1.0)
    return rho_partial

def build_mst(rho_partial, dim_names):
    """Build MST from distance matrix d_ij = 1 - |rho_partial_ij|"""
    G = nx.Graph()
    n = len(dim_names)
    for i in range(n):
        for j in range(i+1, n):
            dist = 1.0 - abs(rho_partial[i, j])
            G.add_edge(dim_names[i], dim_names[j], weight=dist)
    return nx.minimum_spanning_tree(G, algorithm='kruskal')

def bootstrap_mst_stability(raw_scores, covariates, dim_names, n_boot=1000, subsample=14):
    """
    Returns: topology_stability (float) — fraction of bootstrap MSTs with
             identical edge set as full-sample MST
    """
    full_mst = build_mst(compute_rho_partial(raw_scores, covariates), dim_names)
    full_edges = frozenset(frozenset(e) for e in full_mst.edges())
    matches = 0
    for _ in range(n_boot):
        idx = np.random.choice(len(raw_scores), size=subsample, replace=False)
        rho_boot = compute_rho_partial(raw_scores[idx], covariates[idx])
        boot_mst = build_mst(rho_boot, dim_names)
        boot_edges = frozenset(frozenset(e) for e in boot_mst.edges())
        if boot_edges == full_edges:
            matches += 1
    return matches / n_boot
```

### Training Protocol

**This is a statistical analysis experiment (no training).**

**Computation protocol (inherited from H-E1, adapted for MST):**
- **Optimizer:** N/A
- **Learning Rate:** N/A
- **Batch Size:** N/A
- **Epochs:** N/A
- **Random Seed:** 42 (for bootstrap reproducibility — `np.random.seed(42)`)
- **Bootstrap iterations:** 1000 (standard per Musciotto et al. 2018; Tumminello et al. 2007)
- **Bootstrap subsample size:** 14 (of 16 models) — per H-E2 specification
- **Loss Function:** N/A
- **Seeds:** 1 (fixed seed=42)

**Software stack (reused from H-E1):**
- Python 3.10 (youra-h-e1 conda env)
- numpy, scipy.stats, sklearn.linear_model (OLS residualization)
- networkx (MST construction)
- matplotlib (visualization)

> ⚠️ **EXISTENCE (PoC):** Single run with fixed seed. No multiple seeds.

### Evaluation

**Primary Metric:**
- `mst_min_set_size`: number of non-leaf dimensions (or dimensions in minimum covering set). Success = ≤4.
- Operationalization: In a 6-node MST with 5 edges, the minimum covering set = nodes whose removal disconnects the tree. Simpler operationalization: count nodes with degree=1 (leaves); minimum sufficient set = non-leaf nodes. For a path graph of 6 nodes, 2 are leaves → minimum set = 4. For star graph, 1 hub → minimum set = 1.

**Secondary Metric:**
- `bootstrap_topology_stability`: proportion of 1000 bootstrap MSTs with identical edge set to full-sample MST. Success = ≥0.90.

**Success Criteria:**
- PoC Pass: `mst_min_set_size ≤ 4` AND code runs without error
- PoC Secondary: `bootstrap_topology_stability ≥ 0.90`

**Expected Baseline Performance (from H-E1 ρ_partial results):**
- Given 8/15 pairs are significant with high ρ (0.73–0.97), the MST will be dominated by high-ρ edges
- Robustness (no significant pairs) will be a leaf → minimum set likely 5 nodes or fewer
- Truthfulness (high ρ with fairness, privacy) may be a leaf in a dense cluster → minimum set likely 4 or fewer
- Bootstrap stability expected HIGH given the very strong ρ values (>0.85 for top 5 pairs)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: graph_analysis / statistical_analysis
- Library: networkx + numpy (no torchmetrics needed)
- Code:
  ```python
  mst_edges = list(mst.edges(data=True))
  degrees = dict(mst.degree())
  leaves = [n for n, d in degrees.items() if d == 1]
  min_set_size = len(dim_names) - len(leaves)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart comparing mst_min_set_size vs threshold (4) and bootstrap_stability vs threshold (0.90)

#### Additional Figures (LLM Autonomous)
Based on the MST structure and bootstrap analysis, the following figures are recommended:

1. **MST Graph Visualization**: NetworkX graph drawing of the 6-node MST with edge weights (1-|ρ|) as labels. Nodes colored by cluster membership (from H-E1 clustering). Leaf nodes highlighted.
2. **Bootstrap Edge Stability Heatmap**: 6×6 heatmap showing per-edge bootstrap frequency (what fraction of 1000 bootstrap MSTs contain each edge). Reveals which edges are robust vs. unstable.
3. **Distance Matrix Heatmap**: 6×6 heatmap of d_ij = 1-|ρ_partial| with MST edges overlaid as bold borders.
4. **MST vs Raw Spearman MST Comparison**: Side-by-side comparison of MST from partial vs raw Spearman correlations.

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e2/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `mst_min_set_size ≤ 4` (proposed mechanism identifies redundant dimensions)

**Secondary Check (not required for gate):**
3. `bootstrap_topology_stability ≥ 0.90`

**Mechanism Verification:**

| Verification Element | Value |
|---------------------|-------|
| `mechanism_exists` | True — MST algorithm is deterministic given input matrix |
| `mechanism_isolatable` | True — MST is computed independently from H-E1 ρ_partial |
| `baseline_measurable` | True — raw Spearman MST provides uncontrolled comparison |
| `architecture_compatibility` | True — pure numpy/scipy/networkx, no NN required |
| `mechanism_log_message` | "MST constructed: {n_edges} edges. Leaves: {leaf_nodes}. Min set size: {min_set_size}" |
| `tensor_shape_change` | 6×6 distance matrix → 5-edge MST → scalar min_set_size |
| `metric_delta_expected` | mst_min_set_size < 6 (any reduction = mechanism works) |
| `mechanism_verification_code` | `assert len(list(mst.edges())) == 5, "MST must have n-1=5 edges for n=6 nodes"` |
| `hypothesis_support_threshold` | mst_min_set_size ≤ 4 AND bootstrap_stability ≥ 0.90 |
| `hypothesis_support_metric` | mst_min_set_size (primary), bootstrap_topology_stability (secondary) |

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Summary:** Archon KB returned diffusion model content (similarity ~0.34 max). No relevant MST/correlation/bootstrap content found. This is expected given the KB was indexed on stable-diffusion-related repositories.

**Used For:** Nothing — Exa was the primary research source for this hypothesis.

### B. GitHub Implementations (Exa)

**Repository 1**: NetworkX 3.6.1 Official Documentation
- **URL:** https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.tree.mst.minimum_spanning_tree.html
- **Query Used:** "networkx minimum_spanning_tree Spearman correlation distance matrix bootstrap topology stability Python"
- **Relevance:** Core MST API
- **Key Code** (annotated):
  ```python
  # Standard Kruskal MST construction
  T = nx.minimum_spanning_tree(G, weight='weight', algorithm='kruskal')
  # Used as basis for: build_mst() function in pseudo-code
  ```
- **Used For:** Core MST construction step

**Repository 2**: shazzzm/rank_correlation_msts (Millington & Niranjan 2021)
- **URL:** https://github.com/shazzzm/rank_correlation_msts (referenced in paper ar5iv.labs.arxiv.org/html/2005.03963)
- **Query Used:** "networkx minimum_spanning_tree Spearman correlation distance matrix bootstrap topology stability Python"
- **Relevance:** ⭐⭐⭐ Most directly relevant — Spearman rank correlation MST with bootstrap stability
- **Key insight extracted:**
  ```
  # Millington & Niranjan (2021) approach:
  # 1. Compute Spearman correlation matrix
  # 2. Distance: d_ij = 1 - |rho_ij| (or sqrt(2(1-rho)))
  # 3. Build MST with Kruskal's via TopCorr/NetworkX
  # 4. Bootstrap: 1000 pseudo-datasets, compare edge sets
  # Finding: Spearman MSTs are MORE stable under bootstrap than Pearson MSTs
  ```
- **Configuration Extracted:** 1000 bootstrap replicas (standard); edge set comparison for stability
- **Used For:** Bootstrap stability methodology; confirmation that Spearman-based MSTs are stable

**Repository 3**: MST Bootstrap Validation (Musciotto et al. 2018)
- **URL:** https://ideas.repec.org/a/eee/phsmap/v512y2018icp1032-1043.html (physics/0605116 = ar5iv)
- **Query Used:** "MST minimum spanning tree Spearman distance matrix bootstrap stability LLM evaluation Python scipy networkx"
- **Relevance:** ⭐⭐⭐ HIGHEST — defines standard bootstrap MST validation framework
- **Key methodology extracted:**
  ```
  # Musciotto et al. (2018) row bootstrap:
  # 1. Original data matrix X (n_elements × T_samples)
  # 2. Create r=1000 bootstrap replicas X*_i by resampling rows (with replacement)
  # 3. For each replica: compute correlation matrix → extract MST
  # 4. Bootstrap value for link = fraction of bootstrap MSTs containing that link
  # 5. Global reliability = mean bootstrap value across all MST links
  # Our adaptation: topology stability = fraction with IDENTICAL edge set (stricter)
  ```
- **Used For:** Bootstrap methodology; r=1000 standard; row bootstrap approach

**Repository 4**: pybootnet (Shayan-Akhavan)
- **URL:** https://github.com/Shayan-Akhavan/pybootnet
- **Query Used:** "MST minimum spanning tree Spearman distance matrix bootstrap stability"
- **Relevance:** ⭐ LOW — uses threshold correlation graphs, not MST
- **Used For:** Confirmed bootstrap_replicates() + correlation_matrix() pattern (not used directly)

**Repository 5**: HowieHwong/TrustLLM
- **URL:** https://github.com/HowieHwong/TrustLLM
- **Query Used:** "TrustLLM evaluation scores JSON loading partial Spearman correlation Python scipy"
- **Relevance:** ⭐⭐⭐ HIGHEST — primary data source
- **Key insight:** 6 dimensions confirmed (truthfulness, safety, fairness, robustness, privacy, machine_ethics). Scores in results/*.json. Already loaded by H-E1.
- **Used For:** Dataset confirmation; data access path

**Repository 6**: scipy.stats.spearmanr documentation
- **URL:** https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html
- **Used For:** Confirming spearmanr API (same as H-E1 — no change needed)

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed — code from search results was sufficiently clear. The MST computation is a standard 3-line networkx call; the bootstrap is straightforward numpy sampling. No complex architecture patterns requiring semantic analysis.

### D. Previous Hypothesis Context

**Source**: Phase 4 Validation Report — H-E1
- **File:** `h-e1/04_validation.md`
- **Reused Components:**
  - Dataset: TrustLLM 16-model scores — already downloaded, no new download required
  - ρ_partial matrix: directly reused (h-e1/experiment_results_phase3.json)
  - OLS residualization code: identical (data_loader.py + analysis.py from h-e1/code/)
  - Conda environment: youra-h-e1 (Python 3.10 + numpy + scipy + networkx + sklearn + matplotlib)
  - Covariate design: [log10_params, is_RLHF] — same as H-E1
- **Why Reused:** H-E2 is a direct extension of H-E1. Only the MST construction and bootstrap steps are new.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|-----------------|
| Dataset (TrustLLM scores) | GitHub (Exa) | Repo B.5 — HowieHwong/TrustLLM |
| Derived input (ρ_partial) | Previous hypothesis | D — H-E1 experiment_results_phase3.json |
| Distance metric (1-\|ρ\|) | Academic paper (Exa) | B.2 — Millington & Niranjan 2021 |
| MST algorithm (Kruskal) | Documentation (Exa) | B.1 — NetworkX docs |
| Bootstrap r=1000 | Academic paper (Exa) | B.3 — Musciotto et al. 2018 |
| Bootstrap subsample=14/16 | Phase 2B spec | 02b_verification_plan.md H-E2 |
| Topology stability metric | Academic paper (Exa) | B.3 — Musciotto et al. 2018 (adapted) |
| OLS residualization code | Previous hypothesis | D — H-E1 code/analysis.py |
| Success criteria (≤4, ≥0.90) | Phase 2B spec | 02b_verification_plan.md H-E2 |
| Evaluation metrics (degree/leaves) | NetworkX docs (Exa) | B.1 |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-04

### Workflow History for This Hypothesis
- 2026-08-04T00:00:00Z: Phase 2B completed — H-E2 defined as EXISTENCE hypothesis requiring H-E1
- 2026-08-04T05:58:42Z: H-E2 set to IN_PROGRESS (external loop starting Phase 2C → 3 → 4)
- 2026-08-04: Phase 2C experiment design initiated (UNATTENDED mode)

---

*MCP Tools Used: Archon (Knowledge + Code — low relevance, diffusion KB), Exa (GitHub — primary: NetworkX docs, Millington & Niranjan 2021, Musciotto et al. 2018, HowieHwong/TrustLLM, scipy docs), Serena (skipped — code sufficiently clear)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
