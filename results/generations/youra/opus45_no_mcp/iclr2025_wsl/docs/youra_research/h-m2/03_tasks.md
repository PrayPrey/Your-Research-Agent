# Tasks: H-M2 (Alignment Preprocessing Benefit)

**Hypothesis**: H-M2 - Git Re-Basin alignment + Layer-wise encoding
**Tier**: FULL (max 30 tasks)
**Total Tasks**: 10
**Total Complexity**: 67

---

## Epic Breakdown

| ID | Task | Description | Complexity | Status |
|----|------|-------------|------------|--------|
| B-1 | detect_permutable_layers + reorder helpers | Identify conv/fc perm layers, get_next_layer, reorder_input_dim | 6 | TODO |
| B-2 | align_to_reference (greedy weight matching) | Correlation-based permutation + input-dim propagation | 9 | TODO |
| B-3 | compute_alignment_batch + verify_alignment | Zoo-wide alignment loop, convergence tracking (target >95%) | 8 | TODO |
| B-4 | Alignment caching layer | Cache aligned weights to disk, load-if-exists to avoid recompute | 5 | TODO |
| B-5 | AlignmentConfig + reference selection strategies | Extend Config, select_reference (first/random/median/highest) | 5 | TODO |
| B-6 | build_aligned_dataset pipeline | Wire alignment into H-M1 data pipeline for train/val/test | 6 | TODO |
| B-7 | run_seed dual-method orchestration | Train baseline (unaligned) vs proposed (aligned) per seed | 7 | TODO |
| B-8 | Multi-seed + gate decision | 5 seeds x 2 methods, compare_methods, paired t-test, gate logic | 8 | TODO |
| B-9 | Visualization: alignment diagnostic | plot_alignment_diagnostic, wire H-M1 plots | 5 | TODO |
| B-10 | Ablation studies | reference selection, greedy vs Hungarian, conv-only vs all-layer | 8 | TODO |

---

## Complexity Distribution

- **VeryHigh (18-20)**: None
- **High (14-17)**: None
- **Medium (9-13)**: B-2, B-3, B-8, B-10
- **Low (4-8)**: B-1, B-4, B-5, B-6, B-7, B-9

---

## Dependencies

```
B-1 → B-2 → B-3 → B-6 → B-7 → B-8
         ↓
       B-4 (parallel with B-3)
       B-5 (parallel with B-1)
       B-9 (after B-8)
       B-10 (after B-8, optional ablations)
```

---

## Critical Path

B-1 → B-2 → B-3 → B-6 → B-7 → B-8

---

## Gate Criteria (from PRD)

- **Primary**: Δr > 0.05 (Layer-wise+GRB vs Layer-wise alone)
- **Secondary**: p < 0.05 (paired t-test, 5 seeds)
- **Convergence**: >95% aligned pairs meet similarity threshold
