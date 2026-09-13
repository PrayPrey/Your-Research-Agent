# Paper Summary: RefinedWeb (2306.01116)
**Title:** The RefinedWeb Dataset for Falcon LLM: Outperforming Curated Corpora with Web Data Only
**Authors:** Penedo et al., 2023
**arXiv:** 2306.01116

## Overview
RefinedWeb demonstrates that aggressively filtered web data alone can match or outperform carefully curated mixtures (The Pile, C4) on standard NLP benchmarks. Uses MacroData Refinement (MDR) pipeline with URL filtering, deduplication, quality filtering.

## Key Contributions
- Filtering pipeline with quantified stringency: 5T raw tokens → 600B filtered (88% rejection rate)
- Shows web-only filtered data matches curated-mixture models at 1B, 7B scale
- Ablation: each filtering stage has documented contribution to final performance

## Methodology
Falcon-1B and Falcon-7B trained on RefinedWeb vs. curated baselines. Evaluations on HellaSwag, LAMBADA, Winogrande, PIQA, ARC. Ablations: no filter, URL-only, dedup-only, full pipeline.

## Experiments & Results
Full MDR pipeline: +8-12% on HellaSwag vs. unfiltered; matches The Pile on ARC and WinoGrande. Deduplication alone: +3-5%. URL filtering alone: +1-2%. Quality filtering (perplexity-based): +4-6% additional.

## Relevance to Gap 1
Provides the strongest evidence that filtering stringency causally affects benchmark performance — but on Falcon architecture only. Gap 1 is to replicate this finding on Pythia/OLMo suites where we have multiple sizes and documented data recipes, enabling within-suite controlled comparison.

## Limitations
Single architecture (Falcon); no per-benchmark variance analysis; no mechanistic explanation of which training subsets drive which benchmark improvements.
