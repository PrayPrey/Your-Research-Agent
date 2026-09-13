# Hypothesis Completion Snapshot: h-e1

**Date:** 2026-03-17T11:00:00Z
**Hypothesis:** h-e1
**Statement:** Under the Open LLM Leaderboard v1 snapshot, if model cards are publicly accessible on HuggingFace for a sufficient fraction of evaluated models, then a dataset of ≥200 models with non-missing binary curation documentation features, ≥4/6 benchmark scores, and recoverable parameter count can be assembled.
**Final Status:** PARTIAL
**Gate Result:** PARTIAL (MUST_WORK)

## Results
- n_analyzable=4488 (PASS, ≥200)
- n_features_with_variance=2 (FAIL, needed ≥3)
- OLS R²_baseline=0.426, R²_proposed=0.429

## Reflection
- Outcome: SELF_MODIFY → h-e1-v2
- Root cause: alphabetical 0-A sampling retrieved only 177/4497 model cards from families that don't document perplexity filtering or decontamination
- Fix: targeted family-based sampling (LLaMA, Mistral, Qwen, Falcon, Pythia, OLMo)

---
*Per-hypothesis snapshot for Phase 2A reference*
