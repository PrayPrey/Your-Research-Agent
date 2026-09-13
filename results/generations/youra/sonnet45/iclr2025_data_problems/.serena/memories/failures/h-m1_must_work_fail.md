# Failure Record: H-M1 Phase 4 MUST_WORK Gate FAIL

## Metadata
- **Hypothesis ID:** h-m1
- **Phase:** Phase 4
- **Gate Type:** MUST_WORK
- **Gate Result:** FAIL
- **Timestamp:** 2026-05-10T12:21:30Z
- **Pipeline:** YouRA — Data Problems for Foundation Models (TEST_data_problems, sonnet46 run)

## Failure Summary
All 3 MUST_WORK criteria failed:
- `dolma_rank1_fraction = 0.0` (threshold: ≥0.70) — Dolma ranked 4th in ALL 5 resamples
- `non_adjacent_mass = 1.0` (threshold: <0.25) — 100% mass at non-adjacent rank positions
- `permutation_p_value = 1.0` (threshold: <0.05) — No significant difference from null

## Root Causes
1. **Hypothesis was factually inverted**: H-E1 showed Dolma had HIGHEST contamination rate (19.38% at dolma×hellaswag). H-M1 predicted Dolma would rank LOWEST (rank 1). The evidence from H-E1 directly contradicted the hypothesis direction.
2. **Corpus-construction decontamination claim not supported**: Dolma's documented n-gram decontamination at corpus construction time did NOT translate to lower benchmark contamination under n=8 LONGEST-MATCH scanning.
3. **Consistent across all 4 benchmarks**: Rank ordering (C4/RedPajama=1-2, Pile=3, Dolma=4) was stable across MMLU, HellaSwag, ARC-Challenge, WinoGrande.

## Bootstrap Results (All 5 Resamples)
- **pile:** ranks [3, 3, 3, 3, 3] — stable rank 3
- **c4:** ranks [2, 1, 1, 2, 1] — typically lowest contamination
- **dolma:** ranks [4, 4, 4, 4, 4] — stable rank 4, HIGHEST contamination
- **redpajama:** ranks [1, 2, 2, 1, 2] — typically lowest contamination

## Key Insight for Hypothesis Redesign
The ACTUAL finding is inverted: Dolma has HIGHEST contamination, C4 and RedPajama have LOWEST.
A redesigned hypothesis should predict C4 or RedPajama as rank 1 and explain why Dolma ranks last despite documented decontamination.

## Lessons Learned
1. Validate preliminary evidence direction before formulating directional hypotheses (H-E1 signaled this).
2. Bootstrap rank stability is highly informative — all 5 resamples agreed.
3. Documented corpus-level decontamination does not guarantee lower contamination under specific detection methodology.
4. C4 and RedPajama are the actual low-contamination corpora in this study.

## Cascade Effects
- h-m2: BLOCKED (prerequisite h-m1 failed)
- h-m3: BLOCKED (cascade via h-m2)

## Routing
→ Phase 0 for hypothesis redesign (mechanism fundamentally flawed, not implementation issue)
