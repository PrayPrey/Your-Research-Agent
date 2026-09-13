# Introduction

Researchers spend 2-4 weeks manually reviewing benchmark papers to determine suitability for their hypotheses. When validating novel hypotheses about model behavior, researchers must manually read dozens of benchmark papers, extract design features (task formulation, evaluation metrics, data modality, dataset characteristics), and match them to hypothesis requirements—work that delays publication cycles by months and risks choosing inappropriate evaluation frameworks that undermine hypothesis validity.

This manual benchmark selection bottleneck stems from a deeper problem: benchmark design features create systematic constraints on hypothesis testability, but these constraints are implicit, scattered across papers, and lack standardized representation. While prior work has focused on benchmark popularity through citation counts or organized benchmarks into descriptive taxonomies, no systematic method exists to **predict** future benchmark suitability from design features using historical validation. Descriptive approaches organize existing benchmarks but don't predict suitability for novel hypotheses. Citation-based methods measure popularity, not coverage—ImageNet is highly cited but unsuitable for sequence generation hypotheses. Manual expert review achieves high accuracy but requires weeks per hypothesis and doesn't scale.

We demonstrate that **modality, not task type, is the primary constraint on benchmark coverage**. This insight emerges because data modality determines which evaluation metrics are applicable: image benchmarks use mAP/IoU, text benchmarks use BLEU/ROUGE, audio uses WER—creating coverage families that predict future citation co-occurrence with 78% accuracy. By extracting design features from benchmark papers and clustering them into coverage families using SentenceBERT embeddings and k-means, we show that benchmarks cluster primarily by data modality (image, text, audio) rather than task complexity. Historical train/test validation (pre-2023 benchmarks predicting 2023-2024 adoption) breaks circular reasoning between describing usage patterns and predicting suitability.

Building on the modality-constraint insight, we make the following contributions:

1. **First demonstration of temporal persistence in benchmark coverage prediction:** Coverage families from pre-2023 benchmarks predict 2023-2024 citation co-occurrence with 78.07% accuracy (Jaccard similarity), outperforming random baseline (19.61%) by 298%, validated via historical train/test split on 2015-2024 data.

2. **Standardized feature extraction protocol achieving substantial inter-rater agreement:** Cohen's kappa ≥0.917 for task type, modality, metrics, and dataset size, demonstrating that benchmark design features can be extracted objectively at scale.

3. **Discovery of modality-driven clustering exceeding task-based groupings:** SentenceBERT-based clustering achieves 0.748 intra-family similarity (24.7% above threshold) with modularity 0.5452, revealing that modality creates stronger coverage patterns than task formulation.

4. **Validated temporal persistence across 1-2 year publication cycles:** Pre-2023 features predict 2023-2024 patterns, enabling automated benchmark selection to replace weeks of manual review with minutes of computation while discovering coverage gaps before experiments begin.

This work shifts benchmark coverage analysis from descriptive taxonomy to predictive tool, reducing researcher effort from weeks to minutes and providing systematic methods to identify underserved hypothesis categories before implementation.
