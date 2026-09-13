# Hypothesis Completion Snapshot: h-e1-v2

**Date:** 2026-03-17T17:30:00Z
**Hypothesis:** h-e1-v2
**Statement:** Under the Open LLM Leaderboard v2 snapshot (open-llm-leaderboard/contents), if model cards from well-documented model families (LLaMA, Mistral, Qwen, Falcon, Pythia, OLMo) are retrieved in targeted fashion, then a dataset of ≥200 models with non-missing binary curation documentation features in ≥3/4 dimensions can be assembled.
**Final Status:** COMPLETED
**Gate Result:** PASS (MUST_WORK)

## Results
- Validation: PASS
- Gate Type: MUST_WORK
- n_analyzable: 4,493 (target: ≥200) ✅
- n_features_with_variance: 3 (target: ≥3) ✅
- perplexity_filter_documented: 0% coverage (zero variance — persistent issue)
- dedup/domain_composition/decontamination: non-zero variance ✅
- OLS: R²_baseline=0.4247, R²_proposed=0.4289, beta_docs=-3.45 (p=1.1e-8)

## Key Mechanism
- sort_model_ids_by_family() places targeted families first → ensures well-documented cards fetched within API budget
- 3,749 cards retrieved; 114 targeted family models prioritized
- INCREMENTAL hypothesis (SCOPE_REFINEMENT of h-e1)

## Important Lessons
- perplexity_filter_documented is persistently zero-variance even with targeted sampling — the concept is rarely expressed in HuggingFace model cards
- beta_docs is negative (counter-intuitive): confound with model size and documentation completeness trends
- Relative output paths in config.py cause nesting issues when CWD ≠ project root
- Reuse h-e1-v2/data/registry.csv (4,493 rows) for dependent hypotheses — don't re-fetch

## Impact on Pipeline
- h-m1 is now UNBLOCKED (was blocked by h-e1-v2)
- Registry at h-e1-v2/data/registry.csv is the canonical dataset for h-m1, h-m2, h-m3

---
*Per-hypothesis snapshot for Phase 2A reference*
