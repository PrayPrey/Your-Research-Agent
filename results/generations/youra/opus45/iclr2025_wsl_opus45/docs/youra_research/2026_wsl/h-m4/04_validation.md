# H-M4 Phase 4 Validation Report

**Hypothesis ID:** h-m4
**Type:** MECHANISM
**Gate Type:** SHOULD_WORK
**Validation Date:** 2026-04-13T06:01:26Z
**Gate Result:** FAIL

---

## 1. Hypothesis Statement

> Under controlled conditions, if we analyze Grassmann distances per layer type, then some layers (attention vs MLP) will show stronger task-similarity clustering than others (at least one layer type with Cohen's d > 0.8), because different layers encode different aspects of task-specific transformations.

## 2. Gate Criteria

| Criterion | Threshold | Result | Status |
|-----------|-----------|--------|--------|
| Cohen's d for best layer type | > 0.8 | 0.783 (down_proj) | FAIL |
| Layers above threshold | >= 1 | 0 | FAIL |

## 3. Experiment Results

### 3.1 Layer-wise Cohen's d Analysis

| Rank | Layer Type | Cohen's d | 95% CI | p-value |
|------|------------|-----------|--------|---------|
| 1 | down_proj | 0.783 | [0.699, 0.869] | 5.89e-26 |
| 2 | o_proj | 0.772 | [0.686, 0.862] | 2.52e-25 |
| 3 | v_proj | 0.760 | [0.673, 0.851] | 1.23e-24 |
| 4 | k_proj | 0.759 | [0.660, 0.855] | 1.44e-24 |
| 5 | up_proj | 0.756 | [0.671, 0.844] | 1.95e-24 |
| 6 | gate_proj | 0.749 | [0.664, 0.836] | 4.96e-24 |
| 7 | q_proj | 0.745 | [0.649, 0.842] | 8.27e-24 |

### 3.2 Group Statistics (Attention vs MLP)

| Group | Mean Cohen's d | Std Dev | Layer Types |
|-------|----------------|---------|-------------|
| Attention | 0.759 | 0.011 | q_proj, k_proj, v_proj, o_proj |
| MLP | 0.763 | 0.018 | up_proj, down_proj, gate_proj |
| **Difference** | -0.004 | - | - |

- **Mann-Whitney p-value:** 1.0 (no significant difference between groups)

### 3.3 Distance Statistics

| Layer Type | Mean Within | Mean Between | Separation |
|------------|-------------|--------------|------------|
| down_proj | 7.995 | 8.179 | 0.184 |
| o_proj | 7.954 | 8.201 | 0.247 |
| v_proj | 6.947 | 7.105 | 0.158 |
| k_proj | 6.385 | 6.501 | 0.116 |
| up_proj | 8.261 | 8.479 | 0.218 |
| gate_proj | 8.291 | 8.512 | 0.221 |
| q_proj | 7.406 | 7.591 | 0.185 |

## 4. Key Findings

### 4.1 What We Found
1. **All layer types show similar clustering strength** - Cohen's d values range from 0.745 to 0.783, a narrow range of 0.038
2. **No layer type achieves the 0.8 threshold** - The best layer (down_proj) falls short at d=0.783
3. **No significant difference between attention and MLP groups** - Both groups show nearly identical mean Cohen's d (0.759 vs 0.763)
4. **Consistent task-category clustering across all layers** - All p-values are highly significant (< 1e-23)

### 4.2 Interpretation
The hypothesis predicted that different layer types would show meaningfully different clustering strengths, with at least one exceeding d=0.8. Instead, we found:

- **Uniform clustering signal**: Task-category information is encoded similarly across all layer types
- **No layer-specific specialization**: Neither attention nor MLP layers show stronger task encoding
- **Robust but moderate effect**: All layers show significant clustering (d~0.75) but none reaches "large" effect size (d>0.8)

### 4.3 Implications
- The LoRA adapter geometric signature for task similarity is a **global property** distributed across all layer types, not concentrated in specific layers
- Layer-wise feature selection is unlikely to improve task similarity detection
- The H-E1/H-M3 findings (d=0.765 aggregate) are consistent with layer-wise analysis - no single layer explains the full effect

## 5. Generated Artifacts

### 5.1 Result Files
| File | Description |
|------|-------------|
| `results/layer_distances.npz` | 7 distance matrices (40x40 each) |
| `results/cohens_d_results.json` | Cohen's d per layer type |
| `results/group_statistics.json` | Attention vs MLP comparison |
| `results/gate_result.json` | Gate evaluation result |
| `results/analysis_summary.json` | Full analysis summary |

### 5.2 Figures
| Figure | Description |
|--------|-------------|
| `figures/cohens_d_by_layer_type.png` | Bar chart with CI error bars |
| `figures/layer_type_ranking.png` | Horizontal ranking chart |
| `figures/attention_vs_mlp.png` | Group comparison box plot |
| `figures/best_layer_heatmap_down_proj.png` | 8x8 task-level heatmap |

## 6. Gate Evaluation

### 6.1 Gate Type: SHOULD_WORK
This is an exploratory mechanism hypothesis. Failure does not block pipeline continuation.

### 6.2 Gate Result: FAIL
- **Threshold:** Cohen's d > 0.8 for at least one layer type
- **Best Result:** down_proj with d = 0.783
- **Shortfall:** 0.017 below threshold

### 6.3 Routing Decision
Since this is a SHOULD_WORK gate:
- **Pipeline continues** to Phase 5 (baseline comparison)
- **Finding recorded** as negative result (no layer-specific enhancement)
- **No modification required** - hypothesis answered (negative)

## 7. Conclusion

**Gate Status:** FAIL (SHOULD_WORK - acceptable)

The hypothesis that some layer types would show stronger task-similarity clustering than others is **not supported**. All layer types show remarkably uniform clustering strength (d=0.75 range), suggesting that task-category information in LoRA adapters is distributed globally rather than concentrated in specific layers.

This is a valid negative finding that advances understanding: layer-wise analysis does not provide additional signal beyond aggregate distance metrics.

---

**Validation completed:** 2026-04-13T06:01:26Z
**Next Phase:** Phase 5 (Baseline Comparison) or continue to next hypothesis
