# Related Work

Our work bridges two research streams: individual truthfulness benchmarks and meta-evaluation methodology. We position our contribution as the first systematic cross-benchmark correlation study for truthfulness evaluation.

## Truthfulness Benchmarks

**TruthfulQA** (Lin et al., 2022) introduced 817 questions across 38 categories designed to elicit "imitative falsehoods"—plausible-sounding misconceptions that models reproduce from training data. The benchmark offers multiple evaluation modes (MC1, MC2, generation) and specifically targets misconceptions that humans commonly believe, making it orthogonal to factual knowledge tests.

**HaluEval** (Li et al., 2023) provides 35,000 samples across QA, dialogue, and summarization tasks, targeting hallucinated details during text generation. Using a sampling-then-filtering framework with ChatGPT, the benchmark found approximately 19.5% hallucination rates in ChatGPT responses. Unlike TruthfulQA's focus on misconceptions, HaluEval tests generation coherence and consistency maintenance.

**FactScore** (Min et al., 2023) introduced atomic fact decomposition for evaluating long-form generation. By breaking responses into individual claims and verifying each against retrieval sources (typically Wikipedia), FactScore provides fine-grained factuality measurement. This methodology differs fundamentally from both multiple-choice evaluation (TruthfulQA) and binary detection (HaluEval).

These benchmarks developed independently, each establishing its evaluation paradigm without cross-benchmark validation. Open LLM Leaderboard reports scores for multiple benchmarks but does not compute correlations.

## Benchmark Meta-Evaluation

**BenchBench** (Perlitz et al., 2024) proposed a meta-benchmark methodology for evaluating benchmark agreement. Their key finding—that benchmark agreement varies with methodological choices—motivates our investigation of truthfulness-specific correlation structure. However, BenchBench examines general benchmark methodology rather than computing domain-specific correlations.

**Ailem et al. (2024)** demonstrated non-random correlations in model performance across test prompts within benchmarks, showing that accounting for prompt-level correlations can change model rankings. This work operates at the prompt level within benchmarks; we extend to model-level correlations across benchmarks.

**"The Moving Target"** (Fan et al., 2026) audited benchmark score drift across LLM release lines (Yi, Qwen, Mistral, Gemma), finding that trust scores should be treated as checkpoint-bound rather than version-stable. While relevant for longitudinal analysis, this work does not address cross-benchmark correlation structure.

**"Benchmarks Are Not Monolithic"** (Siedler & Sassoon, 2026) revealed pronounced internal heterogeneity within MMLU, ARC, WinoGrande, HellaSwag, and TruthfulQA at the sample level. This finding supports our hypothesis that benchmark scores aggregate over heterogeneous capabilities, but the study does not compute cross-benchmark correlations.

## Hallucination Taxonomies

Several works have proposed hallucination taxonomies. **HalluLens** (Bang et al., 2025) distinguishes extrinsic and intrinsic hallucinations. **AMBER** (Wang et al., 2023) categorizes existence, attribute, and relation hallucinations in multimodal settings. However, no unified taxonomy spans TruthfulQA, HaluEval, and FactScore to enable cross-benchmark failure pattern analysis.

## Our Position

We differ from prior work in three ways:

1. **Domain-specific correlation study.** Unlike BenchBench's general methodology, we compute empirical correlations specifically for truthfulness benchmarks on the same model population.

2. **Model-level cross-benchmark analysis.** Unlike Ailem et al.'s prompt-level within-benchmark correlations, we analyze model-level correlations across benchmarks.

3. **Multi-dimensional structure testing.** We explicitly test whether truthfulness benchmarks measure a single factor or multiple dimensions using factor analysis, going beyond correlation matrices to characterize the latent structure.

Our methodology builds on lm-evaluation-harness (EleutherAI), the de facto standard framework enabling unified evaluation across 70+ benchmarks, which makes cross-benchmark correlation analysis tractable on the same model population.
