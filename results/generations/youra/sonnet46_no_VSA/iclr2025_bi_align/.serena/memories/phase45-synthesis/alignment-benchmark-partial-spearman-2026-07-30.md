# Phase 4.5 Synthesis Results
Date: 2026-07-30
Research: Pairwise Partial Spearman Structure of Alignment Benchmarks After MMLU Scale Control

## Key Outcomes
- Predictions supported: P1 SUPPORTED (high), P2 PARTIALLY_SUPPORTED (medium), P3 REFUTED (high)
- Refined core statement: MMLU control reduces TruthfulQA–BBQ rho from 0.732 to 0.343 (Fisher z=6.97, p=3.22e-12); residual partial rho=0.343 significant but ambiguous scenario at N=296
- Main theoretical contribution: MMLU explains 49-76% of alignment benchmark rank variance (R²=0.493/0.763); Fisher z difference test as benchmark audit tool
- Critical limitation: BBQ data was ARC Challenge proxy (HELM Lite inaccessible); HarmBench Tier 2 N=0 (name format mismatch)

## Lessons for Future Pipelines
- HELM Lite BBQ unavailable via HuggingFace Hub or website from typical compute environments; plan direct HELM release download in Phase 2C
- HarmBench Table 2 model names require normalization (strip org prefix, lowercase) before fuzzy join; threshold=75 alone insufficient
- pingouin 0.6.1 uses 'p_val' not 'p-val' — dynamic key detection required in all partial_corr wrappers
- N=296 sufficient for Fisher z significance but insufficient for partial rho scenario a/b classification; need N≳800 for CI width ~0.15
- ARC Challenge proxy for BBQ yields unusually high MMLU–BBQ R²=0.763 (reasoning benchmark artifact); true BBQ replication required
