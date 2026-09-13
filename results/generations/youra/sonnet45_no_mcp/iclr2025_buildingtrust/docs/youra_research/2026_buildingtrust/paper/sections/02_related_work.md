# Related Work

Our work intersects three research areas: LLM error analysis methods, benchmark meta-analysis, and weak supervision approaches. We position our contribution by identifying limitations in existing work that our public-data approach addresses.

## LLM Error Analysis and Trustworthiness

Understanding where and why language models fail has become critical as these systems move from research prototypes to production deployments. The ICLR 2025 Workshop on Building Trust in Language Models and Applications identifies explainability and interpretability of model responses as a core research priority, reflecting broad community interest in systematic failure analysis.

Existing error analysis methods typically require model re-evaluation or API access to collect item-level responses. Approaches based on embedding analysis, attention visualization, or activation patterns necessitate either full model access or expensive inference calls to generate the data needed for analysis. While these methods can be sophisticated and informative, they create cost barriers ($22-45 per experiment in our experience) and dependency on proprietary access. When API credentials are unavailable, researchers face the choice between abandoning the analysis or resorting to mock data—a failure mode we experienced firsthand when our initial clustering approach defaulted to synthetic data generation.

Our approach differs fundamentally: we use only published results, eliminating API costs entirely and removing access dependencies. This makes the analysis fully reproducible from public data available to any researcher with internet access.

## Benchmark Design and Meta-Analysis

**TruthfulQA** (Lin et al., 2021) introduced a benchmark specifically designed to measure whether models generate truthful answers, with 817 questions spanning 38 fine-grained categories that aggregate into 6-10 broader categories in practice. The benchmark explicitly targets failure modes where models might mimic human falsehoods—common misconceptions, myths, and false beliefs propagated online.

**MMLU** (Hendrycks et al., 2020) provides massive multitask language understanding evaluation across 57 subjects grouped into four domains (STEM, humanities, social sciences, other), creating a comprehensive assessment of factual knowledge and reasoning across educational levels from elementary to professional.

Both benchmarks have become standard evaluation tools, appearing in virtually every major model release's technical report. However, prior meta-analyses aggregate across benchmarks at the model level (comparing average scores) without exploiting category-level structure within benchmarks. For example, analyses might compare "GPT-4 scores 86% on MMLU" across multiple models, but rarely ask "which MMLU subjects show systematic failures across model families?"

We systematically validate category-level granularity within benchmarks, establishing that the structure exists not just in the benchmark design but in the published reporting practices. This enables item-level pattern analysis through weak supervision: category-level rates serve as noisy labels that propagate to items via shared metadata features.

## Weak Supervision and Coarse-Grained Labels

The weak supervision paradigm (Ratner et al., 2019) demonstrates that machine learning models can be trained effectively with noisy, programmatically generated labels rather than expensive hand-labeled ground truth. Labeling functions provide coarse-grained supervision that, when combined with unlabeled data and feature extraction, enables learning at finer granularity than the supervision signal itself.

Item Response Theory from educational testing provides theoretical grounding for our approach: item characteristics (difficulty, discrimination, topic) predict performance across test-takers, suggesting that question metadata should correlate with model error rates. If metadata features capture intrinsic difficulty independent of the specific test-taker (or model), then category-level error rates combined with item-level features enable inferring item-level patterns.

Existing weak supervision approaches typically assume item-level labels are available (even if noisy) or require expensive annotation to bootstrap the system. Few validate whether coarse-grained supervision at the category level suffices for item-level clustering. We explicitly test this assumption as our h-m1 through h-m3 hypotheses (planned future work), but first validate the prerequisite: that category-level rates exist in published data.

Our validation establishes the foundation: category-level rates are available with sufficient granularity (12-15 categories) and completeness (100%) to support weak supervision approaches. This bridges benchmark design (which provides category structure) with weak supervision theory (which enables learning from coarse labels) using published data (which eliminates re-evaluation costs).

## Positioning Our Contribution

Where existing error analysis methods require expensive re-evaluation or API access, we demonstrate that published data suffices for systematic analysis. Where meta-analyses treat benchmarks as monolithic scores, we validate that category-level structure is consistently reported across major labs. Where weak supervision assumes labeled data, we confirm that category-level rates in technical reports provide the coarse-grained signal needed.

Our contribution is foundational: we validate data availability as an empirical hypothesis with explicit quantitative gates (≥3 model families, ≥10 categories, ≥90% completeness, both timepoints). This systematic validation establishes that public-data-only approaches are viable, not merely theoretical possibilities. While we do not yet demonstrate the full taxonomy generation pipeline (feature correlation, clustering, expert validation remain future work), we prove that the critical prerequisite—accessible, high-quality category-level data—exists in published technical reports.
