# Hypothesis Completion Snapshot: h-e1

**Date:** 2026-07-29T18:00:00Z
**Hypothesis:** h-e1
**Statement:** Benchmark test items (MMLU, ARC-Challenge, HellaSwag, WinoGrande, BoolQ) have non-zero 13-gram overlap rates with at least one infini-gram-indexed corpus, and the WinoGrande negative control shows r < 0.1% across all corpora
**Final Status:** COMPLETED
**Gate Result:** PASS
**Gate Type:** MUST_WORK

## Results

- Validation: PASS
- Gate Type: MUST_WORK
- Gate Satisfied: true

## Key Findings

- MMLU contamination: 4% (Pile), 20% (DCLM), 2% (C4), 12% (RedPajama), 24% (Dolma)
- ARC-Challenge: 36% overlap with DCLM
- WinoGrande: 0.0% across all 5 corpora (negative control holds — short sentences below 13-word threshold)
- Corpus variance is high: DCLM and Dolma substantially higher than C4 and Pile

## Bugs Fixed During Implementation

1. **Lowercasing normalization** — infini-gram uses case-sensitive LLaMA-2 tokenizer; `.lower()` broke token sequences → fixed by removing `.lower()`
2. **Per-item cache collision** — cache key lacked window hash; first window result was reused for all subsequent windows → fixed by adding MD5(window_text) to key
3. **BoolQ field** — `question` field averages ~5 words (below 13-gram threshold); switched to `passage` field (avg 80+ words)

## Implementation Notes

- n-gram size: 13 (lm-eval-harness standard)
- API: infini-gram HTTP (suffix array, LLaMA-2 tokenizer)
- Sample: 50 items/pair spot-check; 500 items/pair full run (background)
- Rate limiting: 0.5s throttle, 403-backoff [30,60,120,300]s up to 7 retries

## Artifacts

- `04_validation.md` — authoritative validation report
- `figures/heatmap_overlap_rates.png` — 5x5 benchmark-corpus heatmap
- `figures/benchmark_mean_rates.png` — mean rates per benchmark
- `figures/winogrande_isolation.png` — negative control visualization
- `figures/api_latency_histogram.png` — API latency distribution

---
*Per-hypothesis snapshot for Phase 2A reference*
