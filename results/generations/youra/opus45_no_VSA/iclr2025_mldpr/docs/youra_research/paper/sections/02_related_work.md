# Related Work

We position our work at the intersection of reproducibility assessment, benchmark methodology, and dataset documentation standards. While substantial prior work identifies reproducibility failures and provides evaluation tools, no existing approach predicts reproducibility from dataset characteristics before experiments run.

## Reproducibility Crisis and Assessment

The machine learning reproducibility crisis has received systematic attention. Kapoor and Narayanan (2022) developed a taxonomy of eight data leakage types, documenting their prevalence across 329 papers in 17 scientific fields. This work established that reproducibility failures often trace to methodological issues rather than implementation bugs, with preprocessing leakage and data contamination as leading causes. Hullman et al. (2022) drew parallels between psychology's replication crisis and machine learning, highlighting shared patterns of p-hacking, selective reporting, and specification gaming.

Assessment tools emerged in response. rliable (Agarwal et al., 2021) provides statistical methods for reliable evaluation on reinforcement learning benchmarks, particularly when limited seeds are available. Reproscreener (Bhaskar & Stodden, 2024) leverages language models to automatically assess computational reproducibility of ML pipelines, producing a ReproScore metric. paper-replay enables end-to-end verification through an init-setup-verify-attest workflow with GPG signing.

These tools share a limitation: they operate post-hoc. A researcher must run experiments before learning whether their pipeline meets reproducibility standards. We extend this line of work by predicting reproducibility from dataset metadata *before* experimental execution.

## Benchmark Methodology and Standards

The ML benchmarking community has developed infrastructure for standardized evaluation. OpenML (Vanschoren et al., 2014) provides a platform with extensive metadata including 38 auto-computed meta-features per dataset, enabling large-scale reproducibility analysis. MLCommons (previously MLPerf) established industry benchmarks with specified configurations. HPOBench (Eggensperger et al., 2021) uses containerization to ensure environmental reproducibility.

OpenML's benchmark suites offer curated collections with machine-readable metadata, providing the infrastructure our study requires. The AutoML Benchmark (Gijsbers et al., 2019) enables reproducible AutoML system evaluation across standardized datasets. These efforts focus on infrastructure reproducibility—ensuring the same code produces the same results—rather than predicting which datasets will exhibit low variance across independent implementations.

## Documentation and Metadata Quality

Dataset documentation has received increasing attention. Datasheets for Datasets (Gebru et al., 2021) proposed structured documentation covering motivation, composition, collection process, and intended uses. Model cards (Mitchell et al., 2019) provide analogous documentation for ML models. HuggingFace dataset cards operationalize these principles for their model hub.

However, existing work treats documentation as a qualitative good practice rather than quantifying its impact on downstream reproducibility. We bridge this gap by demonstrating that metadata completeness—operationalized as a 5-field checklist—predicts measurable reductions in reproducibility variance. Our preprocessing entropy mediation analysis provides a mechanistic explanation: documentation constrains the degrees of freedom available to implementers, reducing pipeline heterogeneity.

## Variance Decomposition in ML

Bouthillier et al. (2021) decomposed variance in deep learning experiments, identifying sources including random initialization, data shuffling, and hardware non-determinism. Picard (2021) quantified variation due to random seed selection. These studies characterize *sources* of variance but do not predict which experimental configurations will exhibit high variance.

Our work complements variance decomposition by identifying an *upstream predictor*—metadata completeness—that forecasts variance magnitude before experiments run. While variance decomposition answers "why did variance occur?", we answer "which datasets will exhibit high variance?"

## Our Positioning

Unlike prior work that identifies reproducibility failures post-hoc or provides assessment tools for completed experiments, we offer predictive guidance. Our approach differs from:

- **Leakage taxonomies** (Kapoor & Narayanan): We predict variance from metadata rather than categorizing leakage types after detection.
- **Assessment tools** (Reproscreener, rliable): We operate before experiments rather than evaluating completed pipelines.
- **Documentation standards** (Datasheets, model cards): We quantify documentation impact rather than prescribing qualitative practices.
- **Variance decomposition** (Bouthillier et al.): We predict variance from upstream factors rather than decomposing observed variance into sources.

This predictive framing enables proactive dataset selection—researchers can identify datasets optimized for reproducibility before investing computational resources.
