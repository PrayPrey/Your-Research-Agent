# Validation Report: h-m3

**Date:** 2026-08-25
**Hypothesis ID:** h-m3
**Type:** MECHANISM
**Gate Type:** MUST_WORK

---

## Hypothesis Statement

If we model benchmark usage as a bipartite graph (benchmarks ↔ methods) and apply community detection, then methods using the same benchmarks will cluster into research communities with ≥70% shared citation patterns, because benchmark constraints create methodological similarities.

---

## Experiment Results

### Primary Metrics

**Citation Overlap (Proposed):** 0.7807
- **Target:** ≥0.70
- **Status:** PASS ✓

**Modularity:** 0.5452
- **Target:** >0.40
- **Status:** PASS ✓

### Baseline Comparison

**Citation Overlap (Random Baseline):** 0.1961
**Proposed > Baseline:** YES ✓

### Community Statistics

**Number of communities:** 4
**Mean community size:** 25.0 methods
**Size range:** 25 - 25 methods

---

## Gate Decision

**Result:** PASS

**Rationale:**

- Citation overlap (0.7807) meets threshold (≥0.70)
- Modularity (0.5452) exceeds threshold (>0.40)
- Proposed significantly outperforms random baseline
- Mechanism hypothesis VALIDATED


---

## Key Findings

1. Citation overlap 0.7807 exceeds threshold by +0.081
2. Modularity 0.5452 indicates well-separated communities
3. Proposed outperforms baseline by +0.585
4. 4 communities identified via Louvain


---

## Figures

See `docs/youra_research/h-m3/figures/`:
- `gate_metrics.png` - Target vs actual metrics
- `community_sizes.png` - Community size distribution
- `citation_heatmap.png` - Pairwise citation overlap
- `network_graph.png` - Network visualization

---

**Validation completed:** 2026-08-25 14:14:10
