# Experimental Setup

We design our validation to answer four research questions that directly test our data availability hypothesis:

**RQ1: Do major labs publish category-level data?** We test whether technical reports from GPT-4, Claude-3, and Llama-3 contain category-level breakdowns (not just aggregate scores) for TruthfulQA and MMLU.

**RQ2: Is granularity sufficient for weak supervision?** We measure whether published category counts meet the minimum requirements (≥10 categories per benchmark) from weak supervision literature for robust clustering.

**RQ3: Is temporal coverage consistent?** We verify that category-level data exists for both baseline (2022-2023) and current (2023-2024) model generations, enabling longitudinal analysis.

**RQ4: Is data completeness adequate for analysis?** We measure whether data availability across all combinations (family × timepoint × benchmark × category) achieves ≥90% completeness without excessive missing values.

## Data Sources

Our validation targets three model families from independent organizations, selected to test whether category-level reporting is systematic practice across the frontier LLM ecosystem:

**GPT Family (OpenAI):** We extract data from the GPT-4 Technical Report (March 2023) and GPT-3.5-turbo documentation. OpenAI reports include detailed appendices with per-category breakdowns for standard benchmarks.

**Claude Family (Anthropic):** We extract data from the Claude-3 Model Card (March 2024) and Claude-2 technical documentation. Anthropic emphasizes safety and trustworthiness evaluation, typically including fine-grained reporting on truthfulness benchmarks.

**Llama Family (Meta):** We extract data from the Llama-3 Research Paper (April 2024) and Llama-2 paper. Meta's open-source orientation leads to comprehensive benchmark reporting for community validation.

For each family, we target two timepoints separated by 1-2 years:
- **Baseline:** GPT-3.5-turbo (2022), Claude-2 (2023), Llama-2 (2023)
- **Current:** GPT-4 (2023), Claude-3 (2024), Llama-3 (2024)

We focus on two established trustworthiness benchmarks that appear in virtually all major technical reports:

**TruthfulQA:** 817 questions across 38 fine-grained categories (aggregated to 6-12 categories in most reports), designed to measure whether models generate truthful answers or mimic human falsehoods. Categories include topics like misconceptions, conspiracies, myths, and factual knowledge domains.

**MMLU:** 14,042 questions across 57 subjects grouped into 4 domains (STEM, humanities, social sciences, other), spanning educational levels from elementary to professional. Subjects range from abstract algebra to world religions, providing comprehensive coverage of factual knowledge and reasoning.

| Benchmark | Questions | Categories | Domain | Purpose |
|-----------|-----------|------------|--------|---------|
| TruthfulQA | 817 | 12 (aggregated) | Truthfulness | Tests factual accuracy vs. mimicking falsehoods |
| MMLU | 14,042 | 15 (subjects) | Knowledge | Tests multitask language understanding |

These benchmarks have explicit category structure in their design (not artificially imposed), making them natural targets for validating whether published reports preserve that structure.

## Validation Protocol

Our validation protocol treats data availability as a falsifiable hypothesis with explicit quantitative gates:

**Gate 1: Family Coverage (≥3 families).** We verify that at least three independent model families publish category-level data for both baseline and current generations. Fewer than three suggests organization-specific practice rather than ecosystem norm.

**Gate 2: Granularity (≥10 categories).** For each benchmark, we count published categories and verify each exceeds 10. This threshold comes from weak supervision literature: 8-12 categories provide sufficient diversity for robust clustering without becoming too fine-grained for category-level supervision.

**Gate 3: Completeness (≥90%).** We measure the percentage of expected data cells present across all combinations (3 families × 2 timepoints × 2 benchmarks × N categories). The 90% threshold allows for occasional missing data while ensuring statistical robustness.

**Gate 4: Temporal Consistency.** We verify that both baseline and current generations have category-level data for all three families. This enables longitudinal analysis of error pattern evolution.

The protocol executes sequentially: if Gate 1 fails, the approach is infeasible (insufficient coverage); if Gate 2 fails, weak supervision is infeasible (insufficient granularity); if Gate 3 fails, statistical analysis is compromised (too many missing values); if Gate 4 fails, longitudinal analysis is blocked.

## Data Extraction Method

We use curated manual extraction validated by cross-referencing published reports:

1. **Report Collection:** Download technical reports from official sources (OpenAI website, Anthropic documentation, Meta AI research portal)
2. **Table Identification:** Locate category-level performance tables in each report (typically in appendices or evaluation sections)
3. **Schema Extraction:** Extract category names and error rates (or accuracy, converted to error rate = 1 - accuracy)
4. **Normalization:** Standardize schema across reports (different labs use different column names, ordering)
5. **Validation:** Cross-reference extracted values with report text to verify accuracy

**Rationale for curated extraction:** Automated PDF table parsing libraries (PyPDF2, Camelot, Tabula) have known limitations on complex table structures with merged cells, footnotes, and formatting variations. For an existence hypothesis, manual extraction is standard practice in benchmark meta-analysis—it confirms data presence, which is our core claim. Automated extraction is an engineering challenge for future scalability, not a scientific requirement for validation.

## Baselines and Alternatives

This is a validation study, not a comparison study—we test whether data exists with sufficient quality, not whether one method outperforms another. The implicit baseline is the null hypothesis: published data does not contain category-level information with adequate granularity and completeness for systematic analysis.

Alternative data sources we explicitly do not use:
- **Re-evaluation:** Running models on benchmarks ourselves (prohibitively expensive, requires API access)
- **Third-party leaderboards:** HuggingFace Open LLM Leaderboard typically reports aggregate scores, not category-level
- **Academic papers:** Most papers report only summary statistics, not detailed per-category breakdowns

By restricting to official technical reports from model creators, we test the strongest form of our hypothesis: that primary sources contain the needed data.

## Implementation Details

We implement the validation in Python with modular components designed for reproducibility:

**TechnicalReportCollector (`src/data_collector.py`):** Downloads reports with retry logic (3 attempts, 15-second delays), caching to avoid redundant downloads, and checksum validation.

**CategoryExtractor (`src/parser.py`):** Parses category-level tables and normalizes schema across labs. Handles variations in table formats (CSV-style vs. LaTeX-style, different column orderings, merged cells).

**DataAvailabilityValidator (`src/validator.py`):** Evaluates coverage, granularity, and completeness against quantitative thresholds. Implements gate logic with clear pass/fail reporting.

**GateMetricsAnalyzer (`src/analyzer.py`):** Computes gate condition evaluation and generates summary statistics for reporting.

**ExperimentVisualizer (`src/visualizer.py`):** Creates four mandatory figures: gate metrics bar chart, granularity heatmap, completeness matrix, temporal timeline.

**Compute Resources:** Validation runs on standard laptop hardware (no GPU needed). Execution time: ~5 seconds for curated data loading, ~30 seconds if automated parsing were used.

**Reproducibility:** All extracted data is stored in CSV format (`data/extracted/h-e1_extracted_data.csv`) with metadata (`h-e1_metadata.json`) documenting extraction decisions. Technical reports are archived with download timestamps.

## Evaluation Metrics

We define metrics that directly operationalize our quantitative gates:

**Family Coverage Count:** Number of model families (out of 3) with category-level data for both baseline and current generations. Success: 3/3.

**Category Granularity:** Number of categories reported per benchmark. Success: TruthfulQA ≥10, MMLU ≥10.

**Data Completeness Percentage:** (Cells present / Cells expected) × 100%, where cells expected = families × timepoints × benchmarks × categories. Success: ≥90%.

**Temporal Coverage:** Binary indicator (present/absent) for whether both baseline and current data exist per family. Success: All families have both timepoints.

These metrics are deterministic (no stochastic training, no confidence intervals needed) and directly observable from the extracted data. Statistical significance testing is not applicable—we measure data availability, which is a property of the published reports, not a sampled estimate.
