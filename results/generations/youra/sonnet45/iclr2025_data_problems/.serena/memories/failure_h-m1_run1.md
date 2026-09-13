# Phase 4 Failure Record: h-m1 (Run 1)

**Date:** 2026-05-10T12:35:00Z
**Hypothesis:** h-m1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MUST_WORK_GATE_FAIL — directional hypothesis inversion

## Performance Gap

| Metric | Ours | Target | Gap |
|--------|------|--------|-----|
| dolma_rank1_fraction_mmlu | 0.0 | ≥ 0.70 | -0.70 (-100%) |
| non_adjacent_mass_mmlu | 1.0 | < 0.25 | +0.75 (+300%) |
| permutation_p_value | 1.0 | < 0.05 | +0.95 (indistinguishable from null) |

## Root Cause Analysis

- Hypothesis direction was inverted: Dolma has HIGHEST contamination (rank 4), not lowest (rank 1)
- Dolma consistently ranks 4th across all 4 benchmarks (MMLU, HellaSwag, ARC-Challenge, WinoGrande) and all 5 bootstrap resamples
- Rank ordering (lowest → highest contamination): C4/RedPajama (ranks 1-2) → Pile (rank 3) → Dolma (rank 4)
- This is consistent with H-E1 finding: dolma max_rate = 19.38% — highest among all corpora
- Construction-time n-gram decontamination of Dolma does NOT reduce P(contaminated document) under n=8 LONGEST-MATCH
- No partial success available; complete directional failure on all 3 MUST_WORK criteria

## Lessons Learned

1. H-E1 block_rates.json already showed Dolma had highest contamination rates — H-M1 hypothesis contradicted this prior finding
2. Bootstrap rank stability mechanism worked correctly (5 resamples executed, permutation test n=9999 ran) — the methodology itself is valid, hypothesis claim was wrong
3. Contamination measurement under n=8 LONGEST-MATCH may favor corpora with less aggressive decontamination (C4/RedPajama) over Dolma
4. Construction-time decontamination strategy ≠ lower contamination under post-hoc n-gram matching — these measure different things
5. Dolma rank=4 (highest contamination) is stable — not a threshold sensitivity issue

## Feedback for Next Phase

### Suggested Modifications
- Redesign hypothesis around actual empirical finding: Dolma ranks LAST in contamination-avoidance
- Investigate WHY Dolma has highest contamination despite construction-time decontamination
- Consider reformulating: does corpus-construction-time decontamination with different n-gram thresholds produce different outcomes?
- Explore whether the LONGEST-MATCH threshold n=8 is too permissive for Dolma's specific decontamination approach

### What NOT To Do
- Do NOT hypothesize Dolma will rank lowest in contamination under LONGEST-MATCH n=8
- Do NOT assume construction-time decontamination implies lower post-hoc contamination rates
- Do NOT use H-E1 block_rates.json as evidence for Dolma's superiority

### What Showed Promise
- Bootstrap rank stability methodology (valid, executed correctly)
- Permutation null test framework (valid scientific design)
- 4×4 contamination matrix analysis structure (useful for comparing corpora)
- The actual finding (Dolma highest contamination) is an interesting result worth pursuing from a different angle

## Cascade Effects

- h-m2: BLOCKED (prerequisite h-m1 failed)
- h-m3: BLOCKED (cascade via h-m2)

---
*For cross-phase reference*
*Written at: 2026-05-10T13:00:00Z*
