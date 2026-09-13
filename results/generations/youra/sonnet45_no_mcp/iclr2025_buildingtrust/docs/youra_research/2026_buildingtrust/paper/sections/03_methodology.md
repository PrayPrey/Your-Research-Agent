# Methodology

Building on our observation that published technical reports may contain category-level benchmark data, we design a systematic validation approach to empirically test data availability. Our methodology treats data availability not as an assumption but as a falsifiable hypothesis with explicit quantitative success criteria.

## Overview

If major LLM labs publish category-level error rates with sufficient granularity and completeness, then systematic error analysis becomes feasible without expensive re-evaluation. To test this hypothesis, we need to validate across multiple dimensions: (1) coverage across model families from independent organizations, (2) granularity meeting weak supervision requirements, (3) completeness sufficient for statistical analysis, and (4) temporal coverage enabling longitudinal analysis.

Our validation protocol follows a census-like approach: we systematically query the "distributed database" of published technical reports to measure coverage, granularity, and completeness across the population of interest (frontier LLM families, standard trustworthiness benchmarks, recent model generations).

## Model Family Selection

**Rationale:** Testing whether category-level reporting is systematic practice requires validation across independent organizations with different incentives, engineering cultures, and reporting standards. Focusing on a single lab (e.g., OpenAI only) risks discovering organization-specific practices rather than ecosystem-wide patterns.

We select three model families from independent organizations:
- **GPT** (OpenAI): GPT-3.5-turbo (baseline, released 2022) and GPT-4 (current, released 2023)
- **Claude** (Anthropic): Claude-2 (baseline, released 2023) and Claude-3 (current, released 2024)
- **Llama** (Meta): Llama-2 (baseline, released 2023) and Llama-3 (current, released 2024)

These three organizations represent diverse institutional backgrounds (for-profit with closed models, public benefit corporation with safety focus, and open-source-oriented research lab) and use different architectures and training methodologies. If category-level reporting appears consistently across all three despite these differences, it indicates systematic practice rather than single-organization artifact.

**Alternative considered:** Expanding to 5-8 families (Gemini, Cohere, Mistral, xAI) would strengthen coverage claims but risks diminishing returns—validation across three independent families sufficiently tests ecosystem consistency. Additional families become valuable for tracking how reporting practices evolve, not for establishing the existence of the pattern.

## Temporal Coverage Design

**Rationale:** Including both baseline and current model generations enables longitudinal analysis of error pattern evolution, addressing whether failure modes remain stable as models improve. This tests assumption A4 (patterns reflect general LLM limitations, not transient artifacts).

For each family, we extract data for two timepoints:
- **Baseline generation** (2022-2023): Earlier models representing previous generation's capabilities
- **Current generation** (2023-2024): Latest publicly released models

The ~1-2 year separation provides meaningful temporal distance for measuring improvement patterns while remaining recent enough that technical reports are accessible and reporting standards comparable.

**Alternative considered:** Focusing solely on current models would simplify extraction but miss the opportunity to validate temporal consistency. If error patterns shift dramatically between generations, it suggests they reflect training distribution artifacts rather than fundamental task difficulty.

## Benchmark Selection

**Rationale:** TruthfulQA and MMLU represent standard trustworthiness and knowledge evaluation, appear in virtually all major technical reports, and have explicit category structure in their design. Validating on established benchmarks with known structure confirms that category-level reporting extends beyond aggregate scores.

- **TruthfulQA**: 817 questions across 38 fine-grained categories (aggregated to 6-12 categories in most reports), targeting truthfulness and factual accuracy
- **MMLU**: 14,042 questions across 57 subjects (grouped into 4 domains), spanning educational levels from elementary to professional

Both benchmarks provide the category structure needed for weak supervision: questions naturally group by topic/type, and category membership is explicit in the benchmark data files.

**Alternative considered:** Extending to newer benchmarks (HELM with 42 scenarios, BIG-Bench with 200+ tasks) would demonstrate broader applicability but risks discovering that category-level reporting is specific to established benchmarks. Starting with TruthfulQA and MMLU tests whether reporting practices have matured on widely-used benchmarks before testing on emerging ones.

## Data Extraction Approach

**Rationale:** We prioritize extraction accuracy over automation, using curated manual extraction validated by cross-referencing published reports. While automated PDF parsing is attractive for scalability, known limitations of PDF table parsing libraries (PyPDF2, Camelot, Tabula) on complex table structures risk false negatives—failing to extract data that actually exists.

Our extraction process:
1. Download technical reports from official sources (OpenAI technical reports, Anthropic model cards, Meta research papers)
2. Identify category-level tables for TruthfulQA and MMLU in each report
3. Extract category names and error rates (or accuracy, which we convert to error rate)
4. Normalize schema across reports (different labs use different table formats)
5. Validate completeness: verify all expected cells (family × timepoint × benchmark × category) are present

**Why curated extraction is acceptable:** For an existence hypothesis, manual extraction is standard and sufficient. Benchmark aggregation papers routinely use manual data collection. The hypothesis asks "does the data exist?" not "can it be easily parsed?" Manual extraction confirms presence; automated extraction would be an engineering challenge for future work (we estimate 85-95% success rate based on pilot parsing attempts).

**Alternative considered:** Requiring 100% automated parsing would be more scalable but introduces false negatives from library limitations. Given that our core claim is about data availability (not extraction automation), pragmatic manual extraction is methodologically sound.

## Quantitative Success Criteria

**Rationale:** Explicit thresholds enable clear pass/fail validation and set minimum requirements from weak supervision literature.

We define quantitative gates:
- **Family coverage:** ≥3 model families with category-level data for both timepoints
  - *Justification:* Three independent organizations test ecosystem consistency; fewer risks single-lab artifact
- **Granularity:** ≥10 categories per benchmark
  - *Justification:* Weak supervision literature suggests minimum 8-12 categories for robust clustering; 10 provides comfortable margin
- **Completeness:** ≥90% of expected data cells present
  - *Justification:* Statistical analysis tolerates some missing data; 90% ensures robustness while acknowledging occasional reporting gaps
- **Temporal coverage:** Both baseline and current generations have data
  - *Justification:* Enables longitudinal analysis; confirms pattern persists across model improvements

These thresholds distinguish between "barely sufficient" and "comfortably sufficient" data quality. We aim for the latter: not just confirming data exists, but establishing it meets downstream analysis requirements.

## Validation Protocol

Our validation executes as a MUST_WORK gate: if any threshold fails, the entire public-data approach becomes infeasible for weak supervision-based taxonomy generation.

1. **Data extraction:** Extract category-level rates from technical reports for all combinations (3 families × 2 timepoints × 2 benchmarks)
2. **Family coverage check:** Count model families with data for both timepoints; verify ≥3
3. **Granularity measurement:** Count categories per benchmark; verify each has ≥10 categories
4. **Completeness calculation:** Measure % of expected data cells present; verify ≥90%
5. **Temporal validation:** Confirm both baseline and current data exist for all families

If all checks pass, we conclude that published data is sufficient for weak supervision approaches. If any check fails, we document the gap and assess whether the approach remains viable with reduced scope.

## Technical Implementation

We implement the validation in Python with modular components:
- `TechnicalReportCollector`: Downloads reports with retry logic and caching
- `CategoryExtractor`: Parses category-level tables and normalizes schema across labs
- `DataAvailabilityValidator`: Evaluates family coverage, granularity, and completeness against thresholds
- `GateMetricsAnalyzer`: Computes gate pass/fail and generates visualizations
- `ExperimentVisualizer`: Creates 4 mandatory figures showing coverage, granularity, completeness, temporal timeline

The implementation is instrumented to record all extraction decisions (e.g., which report page contained the table, how schema normalization was performed) for reproducibility.
