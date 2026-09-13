# Pivot Record: h-e1 → h-e1-v2

**Date:** 2026-03-17T10:45:00Z
**Hypothesis:** h-e1
**New Hypothesis:** h-e1-v2
**Modification Type:** SCOPE_REFINEMENT
**Gate Type:** MUST_WORK
**Gate Result:** PARTIAL

## What Happened
- n_analyzable=4488 (>>200 threshold — PASS)
- n_features_with_variance=2 (needed ≥3 — FAIL)
- Root cause: Alphabetical 0-A range retrieval yielded only 177/4497 model cards; model families in that range don't document advanced curation (perplexity filtering, decontamination)

## What Worked
- Full pipeline functional: leaderboard load → model card retrieval → feature extraction → registry build → OLS regression
- OLS runs: R²_baseline=0.426, R²_proposed=0.429
- 17/17 tasks completed, 40 tests passed
- Mechanism validated end-to-end

## What Failed
- perplexity_filter_documented: all-zero variance
- decontamination_documented: all-zero variance
- Caused by sampling only 0-A alphabetical models

## Lessons Learned
- Targeted family-based sampling (LLaMA, Mistral, Qwen, Falcon, Pythia, OLMo) is required to ensure variance across all 4 curation documentation features
- These major families publish comprehensive model cards with deduplication, perplexity filtering, domain composition, and decontamination documentation
- Use Open LLM Leaderboard v2 for h-e1-v2 (broader coverage)

## Modification Summary
h-e1-v2: Use targeted model family sampling instead of alphabetical retrieval; prioritize LLaMA/Mistral/Qwen families known to document curation practices
