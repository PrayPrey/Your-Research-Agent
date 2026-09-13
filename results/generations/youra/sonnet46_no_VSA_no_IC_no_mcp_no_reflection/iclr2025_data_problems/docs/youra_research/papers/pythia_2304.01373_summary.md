# Paper Summary: Pythia (2304.01373)
**Title:** Pythia: A Suite for Analyzing Large Language Models Across Training and Scaling
**Authors:** Biderman et al., 2023
**arXiv:** 2304.01373

## Overview
Pythia provides 12 decoder-only transformer checkpoints trained on The Pile (825GB) across 5 scales (70M–12B parameters). All models trained on identical data in identical order, making it a controlled suite for studying training dynamics.

## Key Contributions
- 12 × 5 checkpoint matrix with intermediate checkpoints every 1000 steps
- All models trained on The Pile — documented, fixed data order
- Open weights + training code + data indices

## Methodology
Standard GPT-Neo architecture with Flash Attention. Training on 300B tokens from The Pile (deduplicated version available). Evaluations on ARC, HellaSwag, MMLU, WinoGrande, TruthfulQA via lm-evaluation-harness.

## Experiments & Results
Pythia-deduplicated vs Pythia baseline: deduplication shows mixed effects — no consistent improvement across benchmarks. Larger models improve uniformly. Training dynamics show capability emergence at specific token counts.

## Relevance to Gap 1
The deduplication ablation is the closest existing study to Gap 1 but uses only one curation dimension (deduplication) and reports aggregate rather than per-benchmark variance. The multi-checkpoint structure enables controlled curation stringency experiments without new training.

## Limitations
All models trained on The Pile only — no cross-corpus comparison. Deduplication is only one curation dimension; no filtering stringency, domain mixing, or quality filtering analysis.
