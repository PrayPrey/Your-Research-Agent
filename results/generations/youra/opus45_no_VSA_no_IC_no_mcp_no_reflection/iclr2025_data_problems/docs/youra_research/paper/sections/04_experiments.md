# Experimental Setup

We design experiments to validate the EDMP scoring pipeline before testing its predictive power for downstream performance.

## Research Questions

Our experiments address the following questions:

**RQ1:** Can EDMP scores be reliably computed for all domains in a multi-domain corpus?
*Maps to contribution 1: Pipeline validation*

**RQ2:** Do EDMP scores show sufficient cross-domain variance to discriminate between domains?
*Maps to contribution 2: Testing whether the scoring mechanism produces meaningful signal*

**RQ3:** Are EDMP scores reproducible across random seeds?
*Maps to contribution 1: Reliability validation*

## Datasets

### Domain Corpus

We evaluate on a subset of The Pile [Gao et al., 2020], selecting 8 representative domains:

| Domain | Description | Characteristics |
|--------|-------------|-----------------|
| Pile-CC | Common Crawl web text | Broad web content |
| Wikipedia | Encyclopedia articles | Structured factual text |
| GitHub | Source code repositories | Programming and documentation |
| ArXiv | Scientific preprints | Technical academic writing |
| StackExchange | Q&A forum content | Technical discussion |
| PubMed | Biomedical abstracts | Medical/scientific text |
| Books3 | Book excerpts | Long-form narrative |
| OpenWebText2 | Curated web text | High-quality web content |

**Sampling:** 1,000 samples per domain (8,000 total), truncated to 512 tokens.

**Note:** Due to data access constraints (zstd library dependency for Pile streaming), we use synthetic domain-distinguishable text for this validation experiment. Synthetic samples are generated with ~30% domain-specific vocabulary and ~70% shared vocabulary to simulate domain structure.

### Task Exemplars

We use the MMLU validation set [Hendrycks et al., 2021] as task exemplars:
- 1,531 questions across 57 subjects
- Format: Question + four answer choices concatenated as text
- Coverage: STEM, humanities, social sciences, professional domains

**Rationale:** MMLU provides broad coverage of downstream task types, representing the diversity of capabilities we want the model to acquire through pretraining.

## Baselines

For this pipeline validation experiment, we compare against:

**Random Embeddings:** Domain samples embedded with random unit vectors instead of E5-large.
- **Purpose:** Establish that E5 embeddings carry semantic content (not noise)
- **Expected result:** Near-zero similarity scores, no domain discrimination

**Uniform Distribution:** Equal score assigned to all domains.
- **Purpose:** Baseline for variance comparison
- **Expected result:** Zero variance (by construction)

## Implementation Details

**Embedding Model:**
- Model: E5-large-v2 (intfloat/e5-large-v2)
- Embedding dimension: 1024
- Framework: sentence-transformers

**Prefixes:**
- Domain samples: "passage: {text}"
- Task exemplars: "query: {text}"

**Aggregation:**
- Similarity: Cosine similarity between normalized embeddings
- Per-domain score: Mean similarity across all samples × all exemplars

**Hardware:**
- GPU: Single NVIDIA A100
- Compute time: <30 minutes for full pipeline

**Reproducibility:**
- Seeds tested: [42, 43, 44]
- All computations deterministic (no dropout, no sampling)

## Evaluation Metrics

We evaluate the EDMP pipeline using the following metrics:

**Score Computability:**
- Criterion: All 8 domains produce valid (finite, non-NaN) similarity scores
- Success: 8/8 domains computed

**Non-Trivial Variance:**
- Metric: Standard deviation of domain scores
- Threshold: std > 0.05
- Rationale: Scores must differentiate domains to enable ranking

**Statistical Significance:**
- Test: One-way ANOVA across domain scores
- Threshold: p < 0.05
- Interpretation: Domain scores are statistically distinguishable

**Reproducibility:**
- Metric: Variance across seeds
- Threshold: Variance < 0.05
- Rationale: Scores must be stable for practical use

These metrics validate the existence of a functioning scoring mechanism—a prerequisite for testing predictive power in future work.
