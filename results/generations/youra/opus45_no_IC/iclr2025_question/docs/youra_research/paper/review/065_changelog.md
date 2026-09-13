# Phase 6.5 Changelog

## Version History

| Version | File | Changes |
|---------|------|---------|
| Original | `06_paper.md` | Initial paper from Phase 6 |
| R1 | `06_paper_r1.md` | Fixed 2 MAJOR issues |
| R2 | `06_paper_r2.md` | No changes (verified clean) |
| Final | `06_paper_final.md` | Publication-ready |

---

## Round 1 Changes

### Section 6.3 Limitations (MAJOR-001)

**Before:**
```markdown
### 6.3 Limitations

**Model scope:** Llama-2-7B-Chat only; larger models may differ.

**Task scope:** Short-form factual QA; summarization untested.

**Scale:** Proof-of-concept (100-1000 samples); full-scale validation planned.
```

**After:**
```markdown
### 6.3 Limitations

**Model scope:** Llama-2-7B-Chat only; larger models may exhibit different clustering structure and transfer behavior.

**Task scope:** Short-form factual QA; summarization and long-form generation untested.

**Scale:** Proof-of-concept (100-1000 samples per benchmark); full-scale validation planned.

**Cross-cluster transfer validation:** H-M4 cross-cluster degradation estimates are derived from JS-divergence correlation with observed within-cluster transfer, rather than exhaustive end-to-end threshold transfer experiments across all cross-cluster pairs. The 7× gap is theoretically grounded but requires additional validation with complete cross-cluster experiments.
```

**Reason:** Ground truth L3 specified H-M4 used simulated degradation. This was not disclosed in the original limitations section.

---

## Round 2 Changes

None. All numerical claims verified against source validation files.

---

## Issues NOT Fixed (Human Review)

See `065_human_review_notes.md` for 6 MINOR issues:
1. Table 5.2 rounding (d=1.33 vs 1.325)
2. Abstract silhouette rounding (0.82 vs 0.8245)
3. Terminology (6× vs 7× for different metrics)
4. Section 5.6 table redundancy
5. Within-cluster JS approximation (0.08 vs ~0.082)
6. Temperature inconsistency (T=0.7 vs T=1.0 in H-M3)
