# Product Requirements Document: H-E2
## MST Minimum Evaluation Set + Bootstrap Topology Stability

**Hypothesis:** H-E2  
**Type:** EXISTENCE (PoC) — INCREMENTAL (extends H-E1)  
**Date:** 2026-08-04  
**Phase:** 3 — Implementation Planning  
**Gate:** MUST_WORK — MST minimum evaluation set ≤4 dimensions AND bootstrap topology stability ≥0.90

---

## 1. Executive Summary

H-E2 extends H-E1's partial Spearman correlation matrix to identify the minimum sufficient evaluation set of LLM trustworthiness dimensions using Minimum Spanning Tree (MST) analysis. Given the strong correlation structure found in H-E1 (8/15 significant pairs, silhouette=0.614), we construct an MST from the 6×6 distance matrix (d = 1 − |ρ_partial|) and perform 1000-resample bootstrap stability analysis (14/16 model subsamples). The experiment passes if the MST identifies ≤4 dimensions as the minimum sufficient evaluation set AND bootstrap topology stability is ≥0.90.

**This is a statistical analysis experiment — no model training required.**  
**All data is derived from H-E1 outputs — no new data download required.**

---

## 2. Problem Statement

H-E1 demonstrated that LLM trustworthiness dimensions are significantly correlated after controlling for scale and RLHF confounds. If the correlation structure is strong and stable, some dimensions are redundant for evaluation purposes. An MST identifies the backbone structure: leaf nodes (degree=1) are the most redundant dimensions, while the minimum covering set (non-leaf nodes) forms the smallest evaluation set that captures all structural connections.

**Baseline approach:** Raw Spearman MST (uncontrolled) — inflated by scale confound, may overestimate dimension interdependencies.

**Proposed approach:** Partial Spearman MST with bootstrap stability — uses H-E1 ρ_partial matrix to build a confound-controlled MST with validated topological stability across 1000 bootstrap resamples.

---

## 3. Functional Requirements

### FR-1: Load H-E1 Outputs
- Load `h-e1/experiment_results_phase3.json` containing:
  - `rho_partial_matrix` (6×6 ndarray)
  - `raw_scores` (16×6 ndarray)
  - `model_metadata` (log10_params, is_RLHF per model)
- Validate matrix symmetry and diagonal = 1.0
- Dimension names: [truthfulness, safety, fairness, robustness, privacy, machine_ethics]

### FR-2: Baseline MST (Raw Spearman)
- Compute all 15 pairwise Spearman ρ_raw values on 16×6 raw score matrix
- Construct 6×6 distance matrix: D_raw[i,j] = 1 − |ρ_raw[i,j]|, diagonal = 0
- Build NetworkX undirected graph from D_raw
- Compute MST via `nx.minimum_spanning_tree(G, algorithm='kruskal')`
- Record: MST edges, node degrees, leaf nodes, min_set_size_raw

### FR-3: Partial Spearman MST (Primary Analysis)
- Use ρ_partial matrix from H-E1 (loaded in FR-1)
- Construct 6×6 distance matrix: D_partial[i,j] = 1 − |ρ_partial[i,j]|, diagonal excluded from graph
- Build NetworkX undirected graph from D_partial
- Compute MST via `nx.minimum_spanning_tree(G, algorithm='kruskal')`
- Compute node degrees; identify leaf nodes (degree=1)
- Compute `mst_min_set_size` = N_nodes − N_leaves (non-leaf count)
- Verify MST has exactly n−1 = 5 edges (assert for n=6 nodes)
- **Gate condition (primary):** `mst_min_set_size ≤ 4`

### FR-4: Bootstrap Topology Stability
- Fix random seed: `np.random.seed(42)`
- Run 1000 bootstrap iterations:
  - Sample 14 rows (model indices) from 16, without replacement
  - Recompute ρ_partial on subsampled 14×6 scores via OLS residualization (identical method to H-E1)
  - Construct distance matrix and MST on bootstrap subsample
  - Compare bootstrap MST edge set to full-sample MST edge set (frozenset comparison)
  - Count matching iterations
- Compute `bootstrap_topology_stability` = matches / 1000
- **Gate condition (secondary):** `bootstrap_topology_stability ≥ 0.90`
- Store per-edge bootstrap frequency (fraction of 1000 MSTs containing each edge)

### FR-5: Per-Edge Bootstrap Frequency
- For each of 5 MST edges, compute fraction of 1000 bootstrap MSTs containing that edge
- Store as dict: {(dim_i, dim_j): frequency}
- Report: mean edge frequency, min edge frequency, max edge frequency

### FR-6: Visualization
- **Required:** Bar chart comparing mst_min_set_size vs threshold (4) and bootstrap_stability vs threshold (0.90) — Gate Metrics Comparison
- **Additional:** MST graph visualization via NetworkX drawing — 6 nodes, 5 edges, edge labels = d_ij, nodes colored by H-E1 cluster membership (RLHF-sensitive vs insensitive), leaf nodes highlighted
- **Additional:** Bootstrap edge stability heatmap — 6×6 heatmap showing per-edge bootstrap frequency; MST edges overlaid
- **Additional:** Distance matrix heatmap — 6×6 d_ij = 1−|ρ_partial| with MST edges marked bold
- **Additional:** Side-by-side comparison: partial Spearman MST vs raw Spearman MST
- Output location: `h-e2/figures/`

### FR-7: Results Serialization
- Save all numeric results to `h-e2/experiment_results_phase3.json`:
  - `mst_edges`: list of (dim_i, dim_j, weight) tuples
  - `mst_degrees`: {dim: degree} for all 6 dimensions
  - `mst_leaves`: list of leaf node names
  - `mst_min_set`: list of non-leaf node names
  - `mst_min_set_size`: int
  - `bootstrap_topology_stability`: float
  - `bootstrap_edge_frequencies`: {edge_str: frequency}
  - `raw_mst_edges`: baseline MST edges
  - `raw_mst_min_set_size`: int
  - `gate_passed`: bool
  - `gate_primary_passed`: bool (mst_min_set_size ≤ 4)
  - `gate_secondary_passed`: bool (bootstrap_stability ≥ 0.90)
- Save experiment log to `h-e2/experiment.log`

---

## 4. Data Specification

### Primary Dataset (Derived — No New Download Required)
**Name:** TrustLLM Published Score Tables — Derived from H-E1  
**Source:** `h-e1/experiment_results_phase3.json` (local file, already computed)  
**Type:** derived (from H-E1 standard/real data)  
**Size:** N=16 models × 6 dimensions (full TrustLLM evaluation set)  
**Content:** ρ_partial 6×6 matrix, raw 16×6 scores, model metadata

**6 Dimensions:**
1. truthfulness
2. safety
3. fairness
4. robustness
5. privacy
6. machine_ethics

**Loading Code:**
```python
import json
import numpy as np

with open("h-e1/experiment_results_phase3.json") as f:
    h_e1_results = json.load(f)

rho_partial = np.array(h_e1_results["rho_partial_matrix"])   # 6×6
raw_scores  = np.array(h_e1_results["raw_scores"])            # 16×6
model_metadata = h_e1_results["model_metadata"]               # log10_params, is_RLHF per model
```

**Manual Download Required:** No — data loaded from H-E1 outputs.

### Bootstrap Parameters
- n_bootstrap: 1000 (standard per Musciotto et al. 2018)
- subsample_size: 14 (of 16 models)
- random_seed: 42

### No Training/Validation Split
Full 16-model set for primary MST; 14/16 subsamples for bootstrap only.

---

## 5. Baseline Models

### Baseline: Raw Spearman MST
- **Description:** MST computed from raw pairwise Spearman ρ on 16×6 score matrix (no confound control)
- **Purpose:** Show effect of confound removal — does partial Spearman MST differ in min_set_size?
- **Implementation:** `scipy.stats.spearmanr(raw_scores)` → distance matrix → `nx.minimum_spanning_tree`
- **Expected behavior:** May produce different topology due to scale confound inflating correlations

---

## 6. Proposed Method

### Partial Spearman MST + Bootstrap Stability
- **Core Algorithm:** Build MST from H-E1 ρ_partial distance matrix; compute leaf/non-leaf structure for minimum evaluation set
- **Bootstrap:** Row bootstrap (14/16 subsamples, 1000 iterations); topology stability = fraction with identical edge set
- **Distance Metric:** d_ij = 1 − |ρ_partial_ij| (Mantegna-style, consistent with Millington & Niranjan 2021)
- **MST Algorithm:** Kruskal (via NetworkX) — deterministic for connected graphs
- **Gate Threshold:** mst_min_set_size ≤ 4 AND bootstrap_stability ≥ 0.90

---

## 7. Non-Functional Requirements

### NFR-1: Compute
- CPU-only, runtime < 60 seconds for 1000 bootstrap iterations
- No GPU required
- Pure Python stack (numpy, scipy, networkx, sklearn, matplotlib)

### NFR-2: Reproducibility
- Fixed seed `np.random.seed(42)` before all bootstrap operations
- Deterministic given same H-E1 outputs and seed

### NFR-3: Code Reuse
- Maximum code reuse from H-E1 (data_loader.py, analysis.py)
- Only new module needed: mst_analysis.py (MST construction + bootstrap)
- Use h-e1 conda environment (youra-h-e1): Python 3.10 + numpy + scipy + networkx + sklearn + matplotlib

### NFR-4: Outputs
- All figures saved to PNG at 300 DPI in `h-e2/figures/`
- All numeric results serialized to `h-e2/experiment_results_phase3.json`
- Summary printed to console and `h-e2/experiment.log`

---

## 8. Success Criteria

| Criterion | Threshold | Type |
|-----------|-----------|------|
| PoC Gate Primary | mst_min_set_size ≤ 4 | MUST_WORK |
| PoC Gate Secondary | bootstrap_topology_stability ≥ 0.90 | MUST_WORK |
| Code runs without error | True | Required |
| MST has 5 edges | assert len(edges) == 5 | Required |
| H-E1 data loaded successfully | True | Required |

---

## 9. Dependencies

### Python Packages (Inherited from H-E1 environment: youra-h-e1)
```
numpy>=1.24
pandas>=1.5
scipy>=1.10
scikit-learn>=1.2
networkx>=3.0
matplotlib>=3.7
seaborn>=0.12
```

### No New Package Installation Required
All dependencies already installed in `youra-h-e1` conda environment.

### Internal Dependencies
- H-E1 COMPLETED (PASS) ✅ — required for ρ_partial matrix
- `h-e1/experiment_results_phase3.json` — primary input (rho_partial, raw_scores, model_metadata)
- `h-e1/code/` — reference for reusable modules (data_loader.py, analysis.py)

---

## 10. Out of Scope

- Model training or fine-tuning
- HELM dataset analysis (H-M3)
- Pythia scaling series analysis (H-M2)
- RLHF mechanism analysis (H-M1, H-M2)
- Hierarchical clustering analysis (covered in H-E1 FR-4, H-M3)
- Datasets other than TrustLLM 16-model set
- Any sample size smaller than the full 16-model TrustLLM set for the primary analysis

---

*Generated by Phase 3 Implementation Planning (UNATTENDED mode)*  
*Source: h-e2/02c_experiment_brief.md*  
*Base hypothesis: H-E1 (COMPLETED PASS)*
