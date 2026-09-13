# Paper Summary: OLMo + Dolma (2402.00838 + 2402.00159)
**Title:** OLMo: Accelerating the Science of Language Models
**Authors:** Groeneveld et al., 2024
**arXiv:** 2402.00838

## Overview
OLMo is a fully open LM (weights, training code, data, evals) trained on Dolma — a 3T token corpus with documented curation decisions across 7 data sources (Common Crawl, C4, Reddit, Semantic Scholar, Wikipedia, Project Gutenberg, books).

## Key Contributions
- Complete reproducibility: weights + optimizer states + training logs released
- Dolma provides domain-level curation metadata (filtering decisions per source)
- Ablation experiments on data mixing ratios for 1B scale models
- Benchmarked on MMLU, HellaSwag, ARC-Easy/Challenge, WinoGrande, TruthfulQA

## Methodology
7B parameter LLaMA-style architecture. Training on 2T tokens from Dolma. Multiple 1B ablation runs testing data mixture variations. Evaluation via lm-evaluation-harness.

## Experiments & Results
Domain proportion ablations: higher C4/web ratio improves HellaSwag; higher academic paper ratio improves MMLU. No single mixing ratio dominates all benchmarks. Quality filtering (heuristic-based) shows modest gains on average but high variance across tasks.

## Relevance to Gap 1
Dolma's 7-source domain breakdown with documented filtering decisions is the ideal operationalization of "curation stringency." Comparing OLMo checkpoints against Pythia checkpoints creates a natural curated vs. less-curated contrast testable with existing benchmarks.

## Limitations
Only 1B and 7B scale ablations; no systematic filtering stringency gradient; different architecture from Pythia makes direct comparison confounded.
