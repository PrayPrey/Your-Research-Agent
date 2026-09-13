# Product Requirements Document (PRD)
# Hypothesis H-E1: Data Quality Metrics Correlation Study

**Document Version**: 1.0  
**Created**: 2026-08-28  
**Hypothesis ID**: h-e1  
**Type**: EXISTENCE  
**Gate**: MUST_WORK

---

## 1. Executive Summary

Build correlation analysis system measuring relationships between data quality metrics Q(D) and information density on C4 dataset subsets. Foundation experiment validating measurement framework for 125M parameter probe models across 12 controlled 10GB data subsets.

**Scope**: Data preparation pipeline, 4-component quality metric computation, 3-metric information density measurement, statistical correlation analysis, baseline comparisons, ablation studies.

**Success Metric**: Pearson r > 0.5 correlation between each Q(D) component and information density, p < 0.01, reproducibility CV < 10%.

---

## 2. Problem Statement

**Core Problem**: Need empirical validation that data quality metrics (deduplication ratio, domain diversity, perplexity, token efficiency) correlate with information density in foundation model pretraining data.

**Why This Matters**: Foundation hypothesis for data quality framework. If Q(D) metrics don't predict information density, entire scaling law investigation collapses.

**Current Gap**: Existing research uses individual quality proxies (perplexity alone) without validating multi-metric correlations or reproducibility.

---

## 3. Functional Requirements

### FR-1: C4 Dataset Sampling and Subset Generation

**Description**: Sample 12 distinct 10GB C4 subsets with controlled quality variations across 4 dimensions.

**Acceptance Criteria**:
- 12 subsets stored as `c4_subset_{dimension}_{level}.jsonl` files
- Each subset exactly 10GB
- Quality dimensions: deduplication ratio, domain diversity, perplexity filtering, token efficiency
- Levels per dimension: LOW, MEDIUM, HIGH
- Ablation design: each subset targets one dimension at HIGH while others at MEDIUM
- Metadata file `subset_metadata.yaml` records ground truth transformations

**Input**: HuggingFace `allenai/c4` (en split)
**Output**: 12 × 10GB JSONL files + metadata YAML

**Dependencies**: None

---

### FR-2: Deduplication Ratio Computation

**Description**: Measure duplicate content removal rate via 13-gram matching.

**Acceptance Criteria**:
- Count unique vs total 13-gram sequences per subset
- Formula: `dedup_ratio = 1 - (unique_13grams / total_13grams)`
- Output range: [0, 1], higher = more duplicates removed
- Result stored in `metrics_results.csv`

**Input**: Processed C4 subset JSONL
**Output**: dedup_ratio float per subset

**Dependencies**: FR-1

---

### FR-3: Domain Diversity Computation

**Description**: Measure URL domain distribution diversity via Herfindahl-Hirschman Index.

**Acceptance Criteria**:
- Extract URL domains from C4 metadata
- Compute HHI: `Σ(domain_share_i²)` 
- Calculate diversity: `1 - HHI`
- Output range: [0, 1], higher = more diverse
- Result stored in `metrics_results.csv`

**Input**: C4 subset with URL metadata
**Output**: domain_diversity float per subset

**Dependencies**: FR-1

---

### FR-4: Average Perplexity Computation

**Description**: Score linguistic complexity via GPT-2 small perplexity.

**Acceptance Criteria**:
- Load pretrained GPT-2 small model
- Compute perplexity per sentence
- Calculate mean perplexity across subset
- Normalize to [0,1] via `1 / (1 + log(perplexity))`
- Result stored in `metrics_results.csv`

**Input**: C4 subset text
**Output**: avg_perplexity_normalized float per subset

**Dependencies**: FR-1

---

### FR-5: Token Efficiency Computation

**Description**: Measure semantic token ratio filtering stopwords and markup.

**Acceptance Criteria**:
- Tokenize text via GPT-2 tokenizer
- Filter stopwords, HTML/markdown, punctuation
- Formula: `token_efficiency = semantic_tokens / total_tokens`
- Output range: [0, 1], higher = less noise
- Result stored in `metrics_results.csv`

**Input**: C4 subset text
**Output**: token_efficiency float per subset

**Dependencies**: FR-1

---

### FR-6: Token-Level Entropy Measurement

**Description**: Compute unigram/bigram/trigram entropy as primary information density metric.

**Acceptance Criteria**:
- Calculate token probability distributions (1-gram, 2-gram, 3-gram)
- Compute Shannon entropy: `H(X) = -Σ p(x) log p(x)`
- Average entropy per token position
- Higher entropy = higher information density
- Result stored in `metrics_results.csv`

**Input**: Tokenized C4 subset
**Output**: token_entropy float per subset

**Dependencies**: FR-1

---

### FR-7: N-gram Redundancy Measurement

**Description**: Measure compression ratio via Lempel-Ziv complexity as inverse information density metric.

**Acceptance Criteria**:
- Apply LZ77 compression to tokenized text
- Calculate redundancy: `1 - (compressed_size / original_size)`
- Lower redundancy = higher information density
- Result stored in `metrics_results.csv`

**Input**: Tokenized C4 subset
**Output**: ngram_redundancy float per subset

**Dependencies**: FR-1

---

### FR-8: Semantic Diversity Measurement

**Description**: Measure sentence embedding diversity via SentenceTransformer.

**Acceptance Criteria**:
- Embed sentences using `all-MiniLM-L6-v2` model
- Compute pairwise cosine distances
- Calculate mean diversity: `mean(1 - cosine_similarity(emb_i, emb_j))`
- Higher diversity = higher information content
- Result stored in `metrics_results.csv`

**Input**: C4 subset sentences
**Output**: semantic_diversity float per subset

**Dependencies**: FR-1

---

### FR-9: Combined Information Density Score

**Description**: Aggregate three information density metrics into normalized composite score.

**Acceptance Criteria**:
- Normalize token_entropy, (1 - ngram_redundancy), semantic_diversity to [0,1]
- Average: `info_density = (entropy_norm + (1-redundancy_norm) + diversity_norm) / 3`
- Result stored as ground truth label
- Range: [0, 1]

**Input**: FR-6, FR-7, FR-8 outputs
**Output**: info_density float per subset

**Dependencies**: FR-6, FR-7, FR-8

---

### FR-10: Pearson Correlation Analysis

**Description**: Compute linear correlation between each Q(D) component and information density.

**Acceptance Criteria**:
- Calculate Pearson r for 4 pairs: {dedup_ratio, domain_diversity, 1/avg_perplexity, token_efficiency} × info_density
- Compute p-values via scipy.stats
- Success threshold: r > 0.5, p < 0.01 for all 4 components
- Results saved to `correlation_results.csv`

**Input**: FR-2, FR-3, FR-4, FR-5, FR-9 outputs (12 data points each)
**Output**: correlation table with r, p per component

**Dependencies**: FR-2, FR-3, FR-4, FR-5, FR-9

---

### FR-11: Spearman Rank Correlation Analysis

**Description**: Test monotonicity of relationships via non-parametric correlation.

**Acceptance Criteria**:
- Calculate Spearman ρ for same 4 pairs as FR-10
- Success threshold: ρ > 0.5 for all components
- Validates monotonic increasing relationships
- Results saved to `correlation_results.csv`

**Input**: Same as FR-10
**Output**: Spearman ρ per component

**Dependencies**: FR-2, FR-3, FR-4, FR-5, FR-9

---

### FR-12: Correlation Scatter Plots

**Description**: Visualize relationships with regression lines and confidence intervals.

**Acceptance Criteria**:
- Generate 4 scatter plots (one per Q(D) component vs info_density)
- Add OLS regression line with 95% CI shading
- Annotate with r², p-value, equation
- Save as PNG: `scatter_{component}_vs_infodensity.png`

**Input**: FR-2, FR-3, FR-4, FR-5, FR-9 outputs
**Output**: 4 PNG visualization files

**Dependencies**: FR-10

---

### FR-13: Reproducibility Test

**Description**: Validate measurement stability across independent C4 resamples.

**Acceptance Criteria**:
- Sample 3 additional 10GB C4 subsets at MEDIUM quality (control condition)
- Recompute all metrics (FR-2 through FR-9)
- Calculate coefficient of variation: `CV = std(metric) / mean(metric)`
- Success threshold: CV < 10% for all metrics
- Results saved to `reproducibility_results.csv`

**Input**: Fresh C4 samples
**Output**: CV per metric, PASS/FAIL status

**Dependencies**: FR-2, FR-3, FR-4, FR-5, FR-9

---

### FR-14: Baseline 1 - Random Quality Assignment

**Description**: Validate null hypothesis by testing random Q(D) scores.

**Acceptance Criteria**:
- Generate random values for dedup_ratio, domain_diversity, perplexity, token_efficiency (uniform [0,1])
- Compute correlation with actual info_density
- Expected: r ≈ 0, p > 0.05
- Confirms test validity
- Results saved to `baseline_results.csv`

**Input**: FR-9 outputs (info_density ground truth)
**Output**: Correlation r, p for random baseline

**Dependencies**: FR-9

---

### FR-15: Baseline 2 - Single-Metric Q(D)

**Description**: Test if any individual metric matches multi-metric Q(D) performance.

**Acceptance Criteria**:
- Correlate each single metric (dedup_ratio alone, domain_diversity alone, etc.) with info_density
- Compare r values to best multi-metric composite
- Success: multi-metric outperforms all single metrics
- Results saved to `baseline_results.csv`

**Input**: FR-2, FR-3, FR-4, FR-5, FR-9
**Output**: Comparison table of single vs composite metrics

**Dependencies**: FR-10

---

### FR-16: Baseline 3 - Perplexity-Only Proxy

**Description**: Compare 4-component Q(D) against common perplexity-only quality proxy.

**Acceptance Criteria**:
- Correlate avg_perplexity (inverse) with info_density
- Compare to composite Q(D) correlation
- Expected: 4-component Q(D) shows higher r
- Results saved to `baseline_results.csv`

**Input**: FR-4, FR-9
**Output**: Perplexity-only r vs composite Q(D) r

**Dependencies**: FR-10

---

### FR-17: Ablation - Remove Each Q(D) Component

**Description**: Identify component contributions by dropout analysis.

**Acceptance Criteria**:
- Create 4 ablated Q(D) versions (drop one component each)
- Recompute correlation with info_density for each version
- Measure delta r compared to full 4-component Q(D)
- Identify most/least important components
- Results saved to `ablation_results.csv`

**Input**: FR-2, FR-3, FR-4, FR-5, FR-9
**Output**: Component importance ranking

**Dependencies**: FR-10

---

### FR-18: Ablation - Dataset Size Sensitivity

**Description**: Test correlation stability at smaller data scales.

**Acceptance Criteria**:
- Repeat full pipeline on {1GB, 5GB, 10GB} C4 subsets (3 size conditions)
- Recompute all metrics and correlations
- Check if r > 0.5 threshold holds at 1GB and 5GB
- Results saved to `ablation_results.csv`

**Input**: Multi-scale C4 samples
**Output**: Correlation r vs dataset size table

**Dependencies**: FR-2 through FR-11

---

## 4. Non-Functional Requirements

### NFR-1: Performance
- Metric computation completes within 4 GPU-hours for all 12 subsets
- Statistical analysis completes within 2 CPU-hours
- Total pipeline runtime ≤ 10 GPU-hours

### NFR-2: Resource Constraints
- Single V100 GPU (16GB VRAM)
- Max disk usage: 120GB (12 subsets + models)
- RAM: 32GB

### NFR-3: Reproducibility
- All random seeds fixed (C4 sampling, shuffling)
- Environment pinned: PyTorch 2.0+, Transformers 4.30+
- Deterministic GPU operations enabled

### NFR-4: Code Quality
- All metrics implemented as reusable functions
- Unit tests on synthetic data (validate statistical tests)
- Type hints and docstrings

### NFR-5: Data Integrity
- No data leakage between subsets
- Metadata checksums for subset verification
- Exact 10GB size validation per subset

---

## 5. Success Criteria

### 5.1 Primary Success (MUST_WORK Gate)

**Criterion 1: Strong Correlation**
- ✅ Pearson r > 0.5 for ALL 4 Q(D) components vs info_density
- ✅ p < 0.01 (statistical significance)
- ❌ FAIL if any component r < 0.3

**Criterion 2: Monotonicity**
- ✅ Spearman ρ > 0.5 for all 4 components
- ✅ Positive linear trends in scatter plots
- ❌ FAIL if any non-monotonic or negative correlation

**Criterion 3: Reproducibility**
- ✅ CV < 10% across 3 resampled MEDIUM quality subsets
- ✅ Correlation values stable within ±0.05
- ❌ FAIL if variance > 15%

### 5.2 Secondary Success (SHOULD_WORK)

**Criterion 4: Composite Q(D) Advantage**
- ✅ Multi-metric Q(D) outperforms all single-metric baselines
- ✅ At least 2 components contribute non-redundantly

**Criterion 5: Baseline Separation**
- ✅ Random baseline r ≈ 0 (validates test)
- ✅ 4-component Q(D) beats perplexity-only proxy

### 5.3 Gate Decision Logic

| Outcome | Condition | Next Step |
|---------|-----------|-----------|
| **PASS** | All 3 primary criteria met | Proceed to H-M1 |
| **PARTIAL** | 2-3 components pass, 1-2 fail | Attempt metric refinement |
| **FAIL** | <2 components pass OR reproducibility fails | Route to Phase 2A-Dialogue |

**Modification Path (if PARTIAL)**:
1. Drop failing components from Q(D)
2. Test alternative quality proxies
3. Re-run correlation analysis
4. If still PARTIAL/FAIL → route to Phase 0 (fundamental issue)

---

## 6. Dependencies

### External Dependencies
- `allenai/c4` dataset (HuggingFace, ODC-BY license)
- Pretrained GPT-2 small (perplexity computation)
- `all-MiniLM-L6-v2` SentenceTransformer (semantic embeddings)

### Python Libraries
- `torch>=2.0`
- `transformers>=4.30`
- `datasets`
- `sentence-transformers`
- `scipy`
- `numpy`
- `pandas`
- `matplotlib`
- `seaborn`

### No Prerequisites
- Foundation hypothesis (first in dependency chain)
- No dependent hypotheses blocking start

---

## 7. Out of Scope

- Training full-scale foundation models (probe models only)
- Multi-dataset validation beyond C4
- Causal mechanism investigation (reserved for H-M1, H-M2)
- Data selection algorithms (H-C1, H-C2)
- Production deployment or API endpoints

---

## 8. Open Questions

1. Should we use GPT-2 small or medium for perplexity? (Trade-off: speed vs accuracy)
2. What n-gram size for deduplication? (13-grams standard, but 7-grams faster)
3. Sentence vs document-level semantic embeddings for diversity metric?

**Resolutions**:
- Q1: Use small (faster, sufficient for relative comparisons)
- Q2: 13-grams (matches existing research baselines)
- Q3: Sentence-level (captures local redundancy better)

---

## 9. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| C4 download failures | High | Cache subsets locally, retry logic |
| GPU memory overflow (perplexity) | Medium | Batch processing, 128 sentences/batch |
| Low correlation (r < 0.3) | High | Already mitigated by controlled subset design |
| Reproducibility variance > 10% | Medium | Increase resample count to 5, report CI |

---

## 10. Validation Protocol

### Static Validation (Pre-Execution)
- ✅ 12 subsets exist, each 10GB
- ✅ Metadata contains transformation parameters
- ✅ No duplicate data across subsets

### Runtime Validation
- Dedup ratio ∈ [0,1], higher for aggressive dedup subsets
- Domain diversity higher for multi-domain vs single-domain
- Perplexity lower for filtered subsets
- Token efficiency higher for cleaned subsets
- Random baseline r ≈ 0

### Post-Execution Validation
- ✅ Correlation table generated with r, p, ρ
- ✅ 4 scatter plot PNGs exist
- ✅ Reproducibility CV table complete
- ✅ Ablation results table complete

---

## 11. Deliverables

### Code Artifacts
1. `sample_c4_subsets.py` - C4 sampling with transformations
2. `quality_metrics.py` - Q(D) component computation
3. `information_density.py` - Entropy, redundancy, diversity
4. `correlation_analysis.py` - Statistical tests
5. `plot_correlations.py` - Visualization generation
6. `ablation_studies.py` - Ablation experiments
7. `baseline_comparisons.py` - Null hypothesis tests
8. `reproducibility_test.py` - Variance validation

### Data Artifacts
1. 12 × C4 subset JSONL files (10GB each)
2. `subset_metadata.yaml` - Ground truth labels
3. `metrics_results.csv` - All computed metrics
4. `correlation_results.csv` - Pearson/Spearman results
5. `reproducibility_results.csv` - CV validation
6. `baseline_results.csv` - Null hypothesis tests
7. `ablation_results.csv` - Component analysis

### Visualization Artifacts
1. `scatter_dedup_vs_infodensity.png`
2. `scatter_diversity_vs_infodensity.png`
3. `scatter_perplexity_vs_infodensity.png`
4. `scatter_efficiency_vs_infodensity.png`

### Documentation
1. `04_validation.md` - Results report (generated in Phase 4)
2. README with setup instructions
3. Requirements.txt with pinned versions

---

## 12. Timeline and Effort

| Phase | Duration | Effort |
|-------|----------|--------|
| Data preparation | 2 hours | 1 GPU-hour |
| Metric computation | 4 hours | 4 GPU-hours |
| Statistical analysis | 2 hours | CPU-only |
| Baselines & ablations | 2 hours | 1 GPU-hour |
| **Total** | **10 hours** | **6 GPU-hours** |

**Total Task Budget**: ≤15 tasks (LIGHT tier for EXISTENCE hypothesis)

---

**END OF PRD**
