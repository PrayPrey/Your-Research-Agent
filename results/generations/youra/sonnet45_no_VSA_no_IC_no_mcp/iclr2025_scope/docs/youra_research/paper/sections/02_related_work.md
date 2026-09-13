# Related Work

Existing benchmark analysis approaches fall into three categories, none of which provide predictive coverage modeling.

## Benchmark Taxonomies

Papers with Code and similar platforms organize benchmarks descriptively by task type (classification, generation, translation) and domain (vision, language, multimodal). While valuable for browsing existing resources, these taxonomies lack predictive power for novel hypotheses—they tell researchers what benchmarks exist but not which will be suitable for future validation needs. Our work differs by using historical validation to predict future suitability from design features rather than retrospectively organizing existing benchmarks.

## Citation-Based Analysis

Semantic Scholar and Google Scholar enable benchmark popularity analysis through citation counts and co-citation networks. However, popularity does not equal coverage: ImageNet receives thousands of citations but is fundamentally unsuitable for sequence generation tasks due to metric incompatibility. These approaches measure usage frequency without extracting **why** benchmarks are suitable (design constraints). We extract design features (modality, metrics, task formulation) to predict benchmark-hypothesis compatibility independent of popularity.

## Benchmark Recommendation Systems

Collaborative filtering and user-behavior similarity approaches recommend benchmarks based on historical usage patterns. These methods require prior usage data for each hypothesis type, making them unsuitable for novel hypothesis categories with no historical record. Our design-feature-based approach enables prediction without prior usage by leveraging inherent benchmark characteristics (data modality, evaluation metrics) that persist across publication cycles.

## Technical Foundations

Our work builds on SciBERT for scientific text understanding and SentenceBERT for semantic similarity of benchmark descriptions. SciBERT's pre-training on scientific literature enables accurate citation context classification, while SentenceBERT embeddings capture semantic similarity enabling modality-driven patterns to emerge from text without requiring pre-defined categories. K-means clustering provides unsupervised discovery of coverage families, complemented by silhouette scoring for cluster quality validation.

## Positioning

Unlike descriptive taxonomies (organize but don't predict), citation analysis (popularity ≠ coverage), or recommendation systems (require prior usage), we provide the first systematic method to predict future benchmark suitability from design features using historical train/test validation, reducing manual selection from weeks to minutes.
