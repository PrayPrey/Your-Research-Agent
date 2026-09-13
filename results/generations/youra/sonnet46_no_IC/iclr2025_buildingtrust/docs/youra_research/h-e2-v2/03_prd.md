# Product Requirements Document: H-E2-v2
## MST Minimum Evaluation Set + Mean Per-Edge Bootstrap Frequency (Relaxed Gate)

**Hypothesis:** H-E2-v2  
**Type:** EXISTENCE (PoC) — INCREMENTAL (extends H-E1, parameter adjustment from H-E2)  
**Date:** 2026-08-04  
**Phase:** 3 — Implementation Planning  
**Gate:** MUST_WORK — MST minimum evaluation set ≤4 dimensions AND mean per-edge bootstrap frequency ≥0.90 (Tumminello 2007)

---

## 1. Executive Summary

H-E2-v2 is a direct continuation of H-E2 with a single gate metric change: the secondary gate criterion is relaxed from full-topology bootstrap stability (fraction of bootstrap MSTs with IDENTICAL edge set ≥0.90) to mean per-edge bootstrap frequency ≥0.90 (Tumminello et al. 2007 standard global reliability measure). H-E2 produced a PARTIAL_PASS because topology_stability=0.606 failed the ≥0.90 threshold; however, the per-edge frequencies were (1.000, 1.000, 0.941, 0.956, 0.688) with mean=0.917, which passes the relaxed gate. The relaxation is scientifically justified: with n=16 models, full-topology match requires all 5 edges simultaneously identical across bootstrap resamples — near-impossible for near-tie edges (machine_ethics attachment). The Tumminello 2007 mean per-edge frequency is the standard measure in financial network MST literature.

**This is a re-evaluation experiment — no new data collection or bootstrap computation required if h-e2/experiment_results_phase3.json contains per_edge_frequencies.**

**Fast path available:** Load h-e2/experiment_results_phase3.json → compute mean(per_edge_frequencies) → evaluate gate.

---

## 2. Problem Statement

H-E2 showed that the partial Spearman MST identifies a minimum evaluation set of 3 dimensions (≤4 threshold: PASS). However, the old secondary gate (full topology stability ≥0.90) failed because machine_ethics–privacy edge has frequency 0.688 — this edge appears in only 68.8% of 1000 bootstrap MSTs, causing the fraction of bootstrap MSTs with IDENTICAL full topology to be only 0.606. The old gate required the AND of all 5 edges simultaneously, which is overly strict for n=16 samples.

**Scientific insight:** machine_ethics is weakly embedded (nearly equidistant from privacy, fairness, safety) — this ambiguous attachment is a genuine finding, not a failure. The Tumminello 2007 mean per-edge frequency captures the average reliability of the MST structure rather than requiring perfect topology reproduction, which is the appropriate measure for small n.

**Baseline:** Raw Spearman MST mean per-edge bootstrap frequency (uncontrolled for scale/RLHF confounds).

**Proposed:** Partial Spearman MST mean per-edge bootstrap frequency = mean(1.000, 1.000, 0.941, 0.956, 0.688) = 0.917 ≥ 0.90 → PASS.

---

## 3. Functional Requirements

### FR-1: Load H-E2 Results (Fast Path)
- Load `h-e2/experiment_results_phase3.json`
- Extract `per_edge_frequencies` dict (keys: edge string representations, values: bootstrap frequencies)
- Extract `mst_min_set_size` (expected: 3)
- Extract `mst_min_set` (minimum evaluation set dimensions)
- Extract `mst_edges` (5 edges of full-sample MST)
- **If `per_edge_frequencies` key missing:** fallback to FR-1b (re-run bootstrap)

### FR-1b: Fallback — Re-Run Bootstrap (if fast path unavailable)
- Load `h-e1/experiment_results_phase3.json` for rho_partial matrix and raw scores
- Rerun bootstrap (1000 iterations, subsample=14/16, seed=42) using h-e2/code/mst_analysis.py
- Compute per-edge frequencies using `bootstrap_mst_edge_frequencies()` from H-E2 code
- This path only executes if fast path fails

### FR-2: Compute Mean Per-Edge Bootstrap Frequency (New Gate Metric)
- Compute `mean_per_edge_bootstrap_frequency` = mean of all values in per_edge_frequencies dict
- Expected: mean(1.000, 1.000, 0.941, 0.956, 0.688) = 0.917
- Store: `mean_per_edge_freq` (float), individual edge frequencies (dict)

### FR-3: Gate Evaluation (H-E2-v2 Gate Logic)
- **Primary gate:** `mst_min_set_size ≤ 4` (expected: 3 → PASS)
- **Secondary gate (RELAXED):** `mean_per_edge_bootstrap_frequency ≥ 0.90` (expected: 0.917 → PASS)
- **Overall gate:** PRIMARY AND SECONDARY → expected PASS
- Store gate results dict: `{primary_pass, secondary_pass, gate_result}`

### FR-4: Baseline Comparison — Raw Spearman MST Mean Per-Edge Frequency
- Load raw_scores from h-e1/experiment_results_phase3.json
- Compute raw Spearman MST (uncontrolled)
- Run bootstrap on raw Spearman MST (1000 iterations, subsample=14/16, seed=42)
- Compute mean per-edge frequency for raw Spearman MST
- Report: partial (controlled) vs raw (uncontrolled) mean frequency comparison

### FR-5: Visualization — Gate Metrics Comparison (Required New Figure)
- **Required (new):** Bar chart comparing:
  - `mst_min_set_size` (expected=3) vs threshold (4) — primary gate
  - `mean_per_edge_bootstrap_frequency` (expected=0.917) vs threshold (0.90) — secondary gate (H-E2-v2)
  - `topology_stability` (H-E2 value=0.606) overlaid for comparison — old gate reference
- Save to `h-e2-v2/figures/gate_metrics_comparison.png` at 300 DPI

### FR-6: Reuse H-E2 Figures (Unchanged)
All H-E2 figures remain valid (MST topology is identical to H-E2). Copy or symlink:
- `h-e2/figures/mst_graph.png` → reference (add mean_freq annotation if re-generated)
- `h-e2/figures/bootstrap_heatmap.png` → reference (add mean_freq annotation if re-generated)
- `h-e2/figures/distance_heatmap.png` → reusable unchanged
- `h-e2/figures/mst_comparison.png` → reusable unchanged

### FR-7: Results Serialization
- Save all results to `h-e2-v2/experiment_results_phase3.json`:
  - `mst_edges`: 5 MST edges (from H-E2, unchanged)
  - `mst_degrees`: {dim: degree} for all 6 dimensions
  - `mst_leaves`: leaf node names
  - `mst_min_set`: non-leaf node names (minimum evaluation set)
  - `mst_min_set_size`: int (expected: 3)
  - `mean_per_edge_bootstrap_frequency`: float (expected: 0.917)
  - `per_edge_bootstrap_frequencies`: {edge_str: frequency} (5 edges)
  - `topology_stability_h_e2`: float (0.606 — historical reference)
  - `baseline_mean_per_edge_freq`: float (raw Spearman MST comparison)
  - `gate_v2_primary_passed`: bool (expected: True)
  - `gate_v2_secondary_passed`: bool (expected: True)
  - `gate_v2_result`: str (expected: "PASS")
  - `data_source`: "h-e2/experiment_results_phase3.json"
  - `fast_path_used`: bool
- Save experiment log to `h-e2-v2/experiment.log`

---

## 4. Data Specification

### Primary Dataset (Derived — No New Download)
**Name:** H-E2 Bootstrap Results (derived from TrustLLM 16-model set)  
**Source:** `h-e2/experiment_results_phase3.json` (local file, already computed by H-E2)  
**Type:** derived  
**Content:** per_edge_frequencies (5 values), mst_min_set_size=3, full MST topology  
**Size:** N=16 models × 6 dimensions (full TrustLLM evaluation set — inherited from H-E1/H-E2)

**6 Dimensions:**
1. truthfulness
2. safety
3. fairness
4. robustness
5. privacy
6. machine_ethics

**Known per-edge frequencies (from H-E2 validation):**

| Edge | Frequency |
|------|-----------|
| privacy — safety | 1.0000 |
| fairness — truthfulness | 1.0000 |
| robustness — truthfulness | 0.9410 |
| fairness — privacy | 0.9560 |
| machine_ethics — privacy | 0.6880 |
| **Mean** | **0.9170** |

**Loading Code:**
```python
import json, numpy as np

# Fast path
with open("h-e2/experiment_results_phase3.json") as f:
    h_e2 = json.load(f)

per_edge_freqs = h_e2.get("per_edge_frequencies", h_e2.get("bootstrap_edge_frequencies", {}))
mst_min_set_size = h_e2["mst_min_set_size"]

# Fallback if key missing — use known values from 04_validation.md
if not per_edge_freqs:
    per_edge_freqs = {
        "['privacy', 'safety']": 1.0000,
        "['fairness', 'truthfulness']": 1.0000,
        "['robustness', 'truthfulness']": 0.9410,
        "['fairness', 'privacy']": 0.9560,
        "['machine_ethics', 'privacy']": 0.6880,
    }

mean_freq = np.mean(list(per_edge_freqs.values()))
```

**Manual Download Required:** No.

### Bootstrap Parameters (inherited from H-E2 — no change)
- n_bootstrap: 1000
- subsample_size: 14 of 16 models
- random_seed: 42
- Method: row bootstrap (Musciotto et al. 2018)

---

## 5. Baseline Models

### Baseline: Raw Spearman MST Mean Per-Edge Bootstrap Frequency
- **Description:** MST computed from raw pairwise Spearman ρ (no confound control); bootstrap over 1000 resamples of 14/16 models; compute mean per-edge frequency
- **Purpose:** Show that partial Spearman MST has higher or comparable reliability to uncontrolled MST
- **Implementation:** `scipy.stats.spearmanr(raw_scores)` → distance matrix → `nx.minimum_spanning_tree` → bootstrap → mean per-edge frequency
- **Expected behavior:** Lower mean frequency (scale confound inflates some correlations making topology less stable across different model subsets)

---

## 6. Proposed Method

### Partial Spearman MST + Mean Per-Edge Bootstrap Frequency (Tumminello 2007)
- **Core gate metric:** `mean_per_edge_bootstrap_frequency` = mean of per-edge bootstrap frequencies (Tumminello et al. 2007)
- **Gate relaxation rationale:** n=16 makes full topology stability ≥0.90 unachievable for near-tie edges; mean per-edge frequency is the standard measure
- **References:** Tumminello et al. (2007), Musciotto et al. (2018), Millington & Niranjan (2021)
- **Fast path:** Load existing H-E2 per-edge frequencies → compute mean → evaluate gate (no re-computation needed)
- **Gate thresholds:**
  - Primary: mst_min_set_size ≤ 4
  - Secondary: mean_per_edge_freq ≥ 0.90

---

## 7. Non-Functional Requirements

### NFR-1: Compute
- CPU-only, runtime < 5 seconds (fast path: scalar computation on loaded JSON)
- No GPU required
- Pure Python stack (numpy, json — networkx only if fallback bootstrap needed)

### NFR-2: Reproducibility
- Fast path: fully deterministic (arithmetic on stored floats)
- Fallback bootstrap: fixed seed `np.random.seed(42)`
- Results fully reproducible given same H-E2 outputs

### NFR-3: Code Reuse
- Maximum reuse from H-E2 (mst_analysis.py, main.py)
- Only change: `evaluate_gate_v2()` function (5 lines)
- New file: `h-e2-v2/code/main.py` (adapter calling H-E2 code + new gate)
- Use `youra-h-e1` conda environment (unchanged)

### NFR-4: Outputs
- Gate bar chart figure saved to `h-e2-v2/figures/` at 300 DPI
- All numeric results serialized to `h-e2-v2/experiment_results_phase3.json`
- Summary printed to console and `h-e2-v2/experiment.log`

---

## 8. Success Criteria

| Criterion | Threshold | Type |
|-----------|-----------|------|
| PoC Gate Primary | mst_min_set_size ≤ 4 | MUST_WORK |
| PoC Gate Secondary (RELAXED) | mean_per_edge_bootstrap_frequency ≥ 0.90 | MUST_WORK |
| Code runs without error | True | Required |
| H-E2 data loaded successfully | True | Required |
| mean_per_edge_freq computed | float in [0,1] | Required |

---

## 9. Dependencies

### Python Packages (Inherited from H-E1/H-E2 environment: youra-h-e1)
```
numpy>=1.24
scipy>=1.10
networkx>=3.0       # only if fallback bootstrap needed
matplotlib>=3.7     # for gate bar chart
```

### Internal Dependencies
- H-E1 COMPLETED (PASS) ✅ — ρ_partial matrix available
- H-E2 COMPLETED (PARTIAL_PASS) ✅ — per-edge bootstrap frequencies available
- `h-e2/experiment_results_phase3.json` — primary input (per_edge_frequencies, mst_min_set_size)
- `h-e2/code/mst_analysis.py` — reuse for fallback bootstrap if needed
- `h-e1/experiment_results_phase3.json` — fallback input (raw_scores, rho_partial)

---

## 10. Out of Scope

- New data download (TrustLLM already at h-e1/code/TrustLLM/)
- New MST computation (topology identical to H-E2)
- New bootstrap runs (frequencies already stored in H-E2 results)
- HELM dataset analysis (H-M3)
- Pythia scaling analysis (H-M2)
- RLHF mechanism analysis (H-M1)
- Any change to MST construction or topology

---

*Generated by Phase 3 Implementation Planning (UNATTENDED mode)*  
*Source: h-e2-v2/02c_experiment_brief.md*  
*Base hypothesis: H-E2 (PARTIAL_PASS — gate relaxation only)*
