# Phase 2C: Experiment Design Brief
# Hypothesis H-E1: Existence of Measurable Quality Metrics

**Generated**: 2026-08-28T08:28:00Z  
**Hypothesis ID**: h-e1  
**Type**: EXISTENCE  
**Gate**: MUST_WORK  
**Pipeline Project ID**: 099e4908-7e83-4727-ba82-a135512ff747

---

## Executive Summary

Design correlation study between data quality metrics Q(D) and information density measures on C4 subsets. Foundation hypothesis validating measurement framework before scaling law experiments.

**Scale**: 10 GPU-hours, 125M parameter probe models, 10GB C4 subsets  
**Success Gate**: r > 0.5 correlation, monotonic relationships, <10% variance

---

## 1. Hypothesis Statement

**H-E1 (EXISTENCE, MUST_WORK)**:
> Data quality metrics Q(D) (dedup ratio, domain diversity, perplexity, token efficiency) are measurable and correlate with information density in foundation model training data.

**Rationale**: Foundation hypothesis. If Q(D) metrics don't correlate with information density, entire framework collapses. Must establish measurement validity before testing mechanisms.

**Prerequisites**: None (first in dependency chain)

---

## 2. Research Question

Can we design a composite quality metric Q(D) from four components (deduplication ratio, domain diversity, perplexity, token efficiency) that reliably predicts information density in pretraining data?

**Null Hypothesis (H₀)**: No correlation exists between Q(D) components and entropy-based information density (r ≤ 0.3)

**Alternative Hypothesis (H₁)**: Each Q(D) component correlates with information density (r > 0.5)

---

## 3. Experimental Design

### 3.1 Dataset Preparation

**Source Dataset**: C4 (Colossal Clean Crawled Corpus)  
**Access**: HuggingFace `allenai/c4` (en split)  
**Type**: standard  
**License**: ODC-BY

**Subset Strategy**:
- Sample 12 distinct 10GB subsets with controlled quality variations
- Quality dimensions: {deduplication ratio, domain diversity, perplexing content, token efficiency}
- Levels per dimension: {LOW, MEDIUM, HIGH}
- Total combinations: 4 dimensions × 3 levels = 12 subsets

**Sampling Protocol**:
1. Start with raw C4 stream (10GB sample per subset)
2. Apply controlled transformations:
   - **Deduplication**: 0% (none), 50% (moderate), 95% (aggressive) removal of exact n-gram duplicates (n=13)
   - **Domain diversity**: Filter to {single domain, 5 domains, full C4 distribution}
   - **Perplexity filtering**: Keep all, remove top 30% perplexing sentences, remove top 60%
   - **Token efficiency**: Include all markup, remove markdown/HTML, aggressive cleaning
3. Each subset targets one dimension at HIGH while others at MEDIUM (ablation design)
4. Store processed subsets with metadata: `c4_subset_{dimension}_{level}.jsonl`

**Ground Truth Labels**:
- Record applied transformations per subset
- Measure actual dedup ratio, Herfindahl domain index, avg perplexity, efficiency score
- Store as `subset_metadata.yaml`

### 3.2 Quality Metrics Computation (Q(D) Components)

**For each 10GB subset, compute**:

1. **Deduplication Ratio** (dedup_ratio ∈ [0,1])
   - Count unique vs total 13-gram sequences
   - Formula: `1 - (unique_13grams / total_13grams)`
   - Higher = more duplicates removed

2. **Domain Diversity** (domain_diversity ∈ [0,1])
   - Compute Herfindahl-Hirschman Index over URL domain distribution
   - Formula: `HHI = Σ(domain_share_i²)`, diversity = `1 - HHI`
   - Higher = more diverse domains

3. **Average Perplexity** (avg_perplexity, lower is better)
   - Use pre-trained GPT-2 small to score each sentence
   - Report mean perplexity across subset
   - Normalize to [0,1] via `1 / (1 + log(perplexity))`

4. **Token Efficiency** (token_efficiency ∈ [0,1])
   - Ratio of semantic tokens to total tokens (filter stopwords, markup)
   - Formula: `semantic_tokens / total_tokens`
   - Higher = less noise

**Composite Q(D)** (not fitted yet):
- Store individual components as features
- Defer linear combination to H-M2 (no premature weighting)

### 3.3 Information Density Measures (Ground Truth)

**For each subset, measure**:

1. **Token-Level Entropy** (primary metric)
   - Compute unigram, bigram, trigram entropy: `H(X) = -Σ p(x) log p(x)`
   - Report entropy per token position
   - Higher entropy = higher information density

2. **N-gram Redundancy** (inverse metric)
   - Measure compression ratio via Lempel-Ziv complexity
   - Formula: `redundancy = 1 - (compressed_size / original_size)`
   - Lower redundancy = higher information density

3. **Semantic Diversity** (auxiliary metric)
   - Embed sentences via SentenceTransformer (all-MiniLM-L6-v2)
   - Compute pairwise cosine diversity: `mean(1 - cosine_similarity(emb_i, emb_j))`
   - Higher diversity = higher information content

**Combined Information Density Score**:
- Normalize all three metrics to [0,1]
- Average: `info_density = (entropy + (1-redundancy) + semantic_diversity) / 3`

### 3.4 Statistical Analysis

**Correlation Analysis**:
1. Pearson correlation between each Q(D) component and info_density
2. Success criterion: r > 0.5, p < 0.01 for all 4 components
3. Spearman rank correlation (monotonicity test)

**Scatter Plots**:
- 4 plots: {dedup_ratio, domain_diversity, 1/avg_perplexity, token_efficiency} vs info_density
- Add regression line with 95% CI
- Annotate r² and p-value

**Reproducibility Test**:
- Resample 3 independent 10GB C4 subsets at MEDIUM quality
- Recompute all metrics
- Check variance < 10% (coefficient of variation)

### 3.5 Baseline Comparisons

**Baseline 1: Random Quality Assignment**
- Assign random Q(D) scores to subsets
- Measure correlation with info_density
- Expected: r ≈ 0 (null hypothesis)

**Baseline 2: Single-Metric Q(D)**
- Test if any single metric (e.g., dedup_ratio alone) matches multi-metric Q(D)
- Expected: Individual metrics underperform composite

**Baseline 3: Perplexity-Only Proxy**
- Use GPT-2 perplexity as sole quality indicator (common practice)
- Compare correlation with info_density vs 4-component Q(D)

### 3.6 Ablation Studies

**Ablation 1: Remove Each Q(D) Component**
- Drop one component at a time from correlation analysis
- Measure impact on aggregate correlation
- Identifies most/least important metrics

**Ablation 2: Dataset Size Sensitivity**
- Repeat analysis on {1GB, 5GB, 10GB} subsets
- Check if correlations hold at smaller scales

---

## 4. Implementation Plan

### 4.1 Environment Setup

**Framework**: PyTorch 2.0+, HuggingFace Transformers 4.30+  
**Hardware**: Single V100 GPU (16GB VRAM sufficient)  
**Dependencies**:
- `datasets` (C4 loading)
- `transformers` (GPT-2 perplexity)
- `sentence-transformers` (semantic embeddings)
- `scipy` (statistical tests)
- `matplotlib`, `seaborn` (visualization)

**Code Structure**:
```
h_e1_quality_metrics/
├── data_preparation/
│   ├── sample_c4_subsets.py       # Generate 12 controlled subsets
│   ├── apply_transformations.py   # Dedup, filter, clean
│   └── subset_metadata.yaml       # Ground truth labels
├── metrics/
│   ├── quality_metrics.py         # Compute Q(D) components
│   ├── information_density.py     # Entropy, redundancy, diversity
│   └── compute_all_metrics.py     # Batch processing
├── analysis/
│   ├── correlation_analysis.py    # Pearson, Spearman tests
│   ├── plot_correlations.py       # Scatter plots with CI
│   └── ablation_studies.py        # Ablation experiments
└── validation/
    ├── reproducibility_test.py    # Resample & variance check
    └── baseline_comparisons.py    # Random, single-metric baselines
```

### 4.2 Execution Steps

**Step 1: Data Preparation** (2 hours)
1. Download C4 en split via HuggingFace
2. Sample 12 × 10GB subsets with controlled transformations
3. Validate subset sizes and metadata

**Step 2: Metric Computation** (4 hours)
1. Compute Q(D) components for all subsets (parallel processing)
2. Measure information density metrics (entropy, redundancy, diversity)
3. Save results to `metrics_results.csv`

**Step 3: Statistical Analysis** (2 hours)
1. Run correlation tests (Pearson + Spearman)
2. Generate scatter plots with regression lines
3. Compute reproducibility variance

**Step 4: Baselines & Ablations** (2 hours)
1. Test random baseline (null hypothesis)
2. Compare single-metric vs composite Q(D)
3. Run ablation studies (drop each component)

**Total Runtime**: ~10 GPU-hours (mostly data processing; GPU needed for perplexity)

---

## 5. Success Criteria

### 5.1 Primary Criteria (MUST_WORK Gate)

**Criterion 1: Strong Correlation**
- ✅ Pearson r > 0.5 between each Q(D) component and info_density
- ✅ p-value < 0.01 (statistical significance)
- ❌ FAIL if any component shows r < 0.3

**Criterion 2: Monotonicity**
- ✅ Spearman ρ > 0.5 for all 4 components (monotonic relationship)
- ✅ Scatter plots show positive linear trend
- ❌ FAIL if any component shows non-monotonic or negative correlation

**Criterion 3: Reproducibility**
- ✅ Coefficient of variation < 10% across 3 resampled subsets
- ✅ Correlation values stable within ±0.05 across resamples
- ❌ FAIL if variance > 15% (unreliable measurements)

### 5.2 Secondary Criteria (SHOULD_WORK)

**Criterion 4: Composite Q(D) Advantage**
- ✅ Multi-metric Q(D) correlates better than any single metric
- ✅ At least 2 components contribute non-redundantly

**Criterion 5: Baseline Separation**
- ✅ Random baseline shows r ≈ 0 (validates null hypothesis)
- ✅ Our Q(D) outperforms perplexity-only proxy

### 5.3 Gate Decision Logic

**PASS**: All primary criteria met → proceed to H-M1  
**PARTIAL**: 2-3 components pass, 1-2 fail → attempt metric refinement  
**FAIL**: <2 components pass OR reproducibility fails → route to Phase 2A-Dialogue

**Modification Attempt (if PARTIAL)**:
1. Drop failing components from Q(D)
2. Test alternative quality proxies (e.g., model-based quality scores)
3. Re-run correlation analysis
4. If still PARTIAL/FAIL → route to Phase 0 (fundamental measurement issue)

---

## 6. Validation Protocol

### 6.1 Static Validation (Pre-Execution)

**Data Validation**:
- ✅ 12 subsets exist with correct sizes (10GB each)
- ✅ Metadata contains all transformation parameters
- ✅ No data leakage between subsets

**Code Validation**:
- ✅ All metrics compute without errors on sample data
- ✅ Statistical tests implemented correctly (validate on synthetic data)
- ✅ Plots render with proper axis labels and CI bands

### 6.2 Runtime Validation

**Metric Sanity Checks**:
- Dedup ratio ∈ [0,1], higher for aggressive dedup subsets
- Domain diversity higher for full C4 vs single-domain subsets
- Perplexity lower for filtered subsets
- Token efficiency higher for cleaned subsets

**Correlation Sanity Checks**:
- Random baseline r ≈ 0 (validates test implementation)
- At least 2 components positively correlated with info_density

### 6.3 Post-Execution Validation

**Result Validation**:
- ✅ Correlation table generated with r, p, ρ for each component
- ✅ 4 scatter plots saved with regression stats
- ✅ Reproducibility variance table computed
- ✅ Ablation results show component importance ranking

**Interpretation Validation**:
- Check if correlations align with intuition (e.g., dedup → higher entropy)
- Identify any unexpected negative correlations (requires investigation)
- Validate statistical significance isn't due to outliers (check residual plots)

---

## 7. Expected Outcomes

### 7.1 Positive Outcome (PASS)

**Evidence**:
- Pearson r: {dedup_ratio: 0.72, domain_diversity: 0.68, perplexity: -0.65, token_efficiency: 0.58}
- All p < 0.001, Spearman ρ > 0.6
- Reproducibility CV: 6.2% (< 10% threshold)

**Interpretation**:
- Q(D) components are valid quality proxies
- Information density measurable via entropy-based metrics
- Framework ready for mechanism testing (H-M1)

**Next Steps**:
- Proceed to Phase 3 implementation planning for H-E1
- Use validated Q(D) metrics in H-M1 experiment design

### 7.2 Partial Outcome (Needs Refinement)

**Example**:
- 3 components pass (r > 0.5), token_efficiency fails (r = 0.28)
- Reproducibility variance at 12% (slightly high)

**Interpretation**:
- Core quality dimensions valid (dedup, diversity, perplexity)
- Token efficiency not predictive of information density
- Measurement stability borderline

**Modification Attempt**:
1. Drop token_efficiency from Q(D)
2. Increase subset size to 15GB (reduce variance)
3. Test alternative efficiency metric (e.g., lexical diversity)
4. Re-run validation

**Decision**: If refined Q(D) passes → proceed; else → Phase 2A-Dialogue

### 7.3 Negative Outcome (FAIL)

**Example**:
- Only 1 component passes (dedup_ratio r = 0.54)
- Perplexity shows negative correlation (r = -0.42, opposite direction)
- Reproducibility CV: 18% (high variance)

**Interpretation**:
- Fundamental measurement issue
- Q(D) framework invalid as designed
- Information density poorly captured by entropy alone

**Actions**:
1. Route to Phase 2A-Dialogue (mechanism refinement)
2. Consider alternative quality definitions:
   - Model-based quality scores (e.g., reward model scoring)
   - Task-specific quality (downstream benchmark performance)
   - Gradient-based information (Fisher information from H-M1)
3. If no viable alternative → Phase 0 (rethink hypothesis)

---

## 8. Risk Mitigation

### 8.1 Technical Risks

**Risk 1: C4 Sampling Bias**
- **Mitigation**: Use stratified sampling across multiple time periods
- **Contingency**: Validate on alternative corpus (PILE or RedPajama)

**Risk 2: Perplexity Model Mismatch**
- **Issue**: GPT-2 perplexity may not generalize to larger models
- **Mitigation**: Test with multiple perplexity models (GPT-2, GPT-Neo, Pythia)
- **Acceptance**: If correlations hold across models, proceed; else document limitation

**Risk 3: Entropy Metric Validity**
- **Issue**: Token-level entropy may not capture semantic information density
- **Mitigation**: Add semantic diversity metric (sentence embeddings)
- **Contingency**: If entropy fails but semantic diversity passes, pivot to semantic metrics

### 8.2 Statistical Risks

**Risk 4: Small Sample Size**
- **Issue**: 12 subsets may be insufficient for robust correlation
- **Mitigation**: Bootstrap resampling (1000 iterations) to compute CI on r
- **Contingency**: Increase to 24 subsets if correlations borderline

**Risk 5: Confounding Variables**
- **Issue**: Domain diversity may correlate with dedup ratio (not independent)
- **Mitigation**: Partial correlation analysis (control for other variables)
- **Interpretation**: Report both pairwise and partial correlations

### 8.3 Conceptual Risks

**Risk 6: Information Density Definition**
- **Issue**: No ground truth for "information density" in pretraining data
- **Mitigation**: Use multiple proxies (entropy, redundancy, semantic diversity)
- **Validation**: Cross-check with downstream model performance in H-M1

**Risk 7: Metric Saturation**
- **Issue**: Dedup ratio may saturate at high levels (diminishing returns)
- **Mitigation**: Test non-linear transformations (log, sqrt)
- **Acceptance**: Document saturation as boundary condition for scaling laws

---

## 9. Deliverables

### 9.1 Code Artifacts

1. **Data Processing Pipeline**
   - `sample_c4_subsets.py`: Reproducible subset generation
   - `subset_metadata.yaml`: Ground truth labels for 12 subsets

2. **Metric Computation**
   - `quality_metrics.py`: Q(D) component functions
   - `information_density.py`: Entropy, redundancy, diversity functions
   - `metrics_results.csv`: Full metric table (12 rows × 8 columns)

3. **Analysis Scripts**
   - `correlation_analysis.py`: Statistical tests with CI
   - `plot_correlations.py`: Publication-ready scatter plots
   - `ablation_studies.py`: Component importance analysis

### 9.2 Validation Report

**File**: `04_validation_h_e1.md`

**Contents**:
1. **Experiment Summary**: Hypothesis, design, execution log
2. **Results Table**: Correlation matrix (r, p, ρ) for all components
3. **Visualizations**: 4 scatter plots + correlation heatmap
4. **Statistical Tests**: Bootstrap CI, reproducibility variance
5. **Gate Decision**: PASS/PARTIAL/FAIL with evidence
6. **Key Findings**: Which components strongest, weakest, why
7. **Recommendations**: Proceed to H-M1 or refinement needed

### 9.3 Dataset Artifacts

**Stored Subsets** (120GB total):
- `c4_dedup_low.jsonl`, `c4_dedup_high.jsonl`, ...
- `subset_metadata.yaml` (transformation parameters)

**Metric Cache**:
- `precomputed_metrics.pkl` (reusable for H-M1)

---

## 10. Resource Budget

### 10.1 Compute Resources

**GPU Hours**: 10 hours (V100 or equivalent)
- Data sampling: 2 hours (CPU-bound, minimal GPU)
- Perplexity scoring: 4 hours (GPU for GPT-2 inference)
- Embedding computation: 2 hours (SentenceTransformer)
- Statistical analysis: 2 hours (CPU-only)

**Storage**: 150GB
- Raw C4 subsets: 120GB
- Processed metrics: 5GB
- Plots and results: <1GB

**RAM**: 32GB (load 10GB subset + model weights)

### 10.2 Human Time

**Development**: 8 hours
- Implement data pipeline: 3 hours
- Metric computation: 2 hours
- Analysis scripts: 2 hours
- Validation checks: 1 hour

**Execution & Monitoring**: 2 hours
- Launch jobs: 0.5 hours
- Check intermediate outputs: 1 hour
- Debug failures: 0.5 hours (contingency)

**Analysis & Reporting**: 4 hours
- Interpret results: 2 hours
- Write validation report: 2 hours

**Total**: ~14 human-hours

### 10.3 Cost Estimate

**Cloud GPU (A100 on-demand)**: $3/hour × 10 hours = $30  
**Storage (S3)**: $0.023/GB × 150GB × 1 month = $3.45  
**Total**: ~$35 (cost-efficient validation experiment)

---

## 11. Timeline

**Day 1** (8 hours):
- Morning: Setup environment, download C4
- Afternoon: Generate 12 subsets with transformations
- Evening: Validate subset metadata

**Day 2** (10 hours):
- Morning: Compute Q(D) metrics for all subsets
- Afternoon: Measure information density (entropy, redundancy, embeddings)
- Evening: Run correlation analysis

**Day 3** (6 hours):
- Morning: Generate plots and statistical tests
- Afternoon: Run baselines and ablations
- Evening: Write validation report and gate decision

**Total Duration**: 3 days (part-time work) or 1.5 days (full-time)

---

## 12. Integration with Pipeline

### 12.1 Inputs from Phase 2B

- Hypothesis statement: H-E1 (from `02b_verification_plan.md`)
- Success criteria: r > 0.5, monotonicity, variance < 10%
- Gate type: MUST_WORK
- Controlled variables: C4 dataset, entropy-based info density

### 12.2 Outputs to Phase 3

**If PASS**:
- Validated Q(D) component definitions
- Correlation strength estimates (inform H-M1 design)
- Reproducibility bounds (guide statistical power analysis)
- Precomputed metric cache (reuse in H-M1)

**If PARTIAL**:
- Refined Q(D) with 2-3 components
- Known limitations (e.g., "token efficiency dropped")
- Modified success criteria for H-M1

**If FAIL**:
- Failure analysis report
- Alternative quality proxies to explore
- Route decision (Phase 2A-Dialogue or Phase 0)

### 12.3 Dependencies for Phase 3

**Implementation Planning Needs**:
- Complexity Tier: **Tier 1** (straightforward data analysis, no model training)
- Task Count Estimate: 8 tasks
  - Data: 2 (sample subsets, validate)
  - Environment: 1 (setup dependencies)
  - Epic: 3 (compute Q(D), compute info_density, correlation analysis)
  - Subtasks: 2 (baselines, ablations)
  - Failsafe: 0 (low-risk experiment)

**Archon Document Requirements**:
- PRD: Dataset specs, metric definitions, success criteria
- Architecture: Data pipeline flow, metric computation modules
- Logic: Statistical test implementations (Pearson, Spearman)
- Config: Subset sizes, correlation thresholds, reproducibility variance limit

---

## 13. Comparison with Literature

### 13.1 Existing Quality Metrics

**C4 Filtering (Raffel et al. 2020)**:
- Uses heuristic filters (bad words, sentence length)
- No systematic quality measurement framework
- Our contribution: Multi-dimensional Q(D) with validation

**Data Quality in Pretraining (Xie et al. 2023)**:
- Measures perplexity and diversity separately
- No composite quality score
- Our contribution: Unified Q(D) metric with information density correlation

**Deduplication Studies (Lee et al. 2022)**:
- Shows dedup improves performance empirically
- Doesn't measure information density directly
- Our contribution: Mechanistic link via entropy

### 13.2 Information Density Measures

**Entropy in Language Models (Shannon 1948, modern NLP)**:
- Token-level entropy well-established for compression
- Rarely applied to pretraining data quality
- Our contribution: Use as validation ground truth for Q(D)

**Fisher Information in Training (Kunstner et al. 2019)**:
- Measures gradient informativeness
- Requires model training (deferred to H-M1)
- Our contribution: Lightweight entropy proxy first, validate with Fisher in H-M1

---

## 14. Limitations & Assumptions

### 14.1 Known Limitations

**Limitation 1: Single Dataset**
- Only validated on C4 (web text)
- May not generalize to code, scientific text, multilingual data
- **Mitigation**: Document as scope boundary, test on PILE in H-C1

**Limitation 2: Entropy as Proxy**
- Information density measured indirectly (no ground truth)
- Assumes entropy correlates with learning signal
- **Validation**: Cross-check with H-M1 gradient statistics

**Limitation 3: Small Sample Size**
- 12 subsets limit statistical power
- Correlations may be noisy
- **Mitigation**: Bootstrap CI, reproducibility resampling

### 14.2 Assumptions

**Assumption 1**: Information density is measurable via token-level entropy  
**Assumption 2**: Q(D) components are approximately independent  
**Assumption 3**: 10GB subsets representative of full C4 distribution  
**Assumption 4**: GPT-2 perplexity generalizes to other model families

**Validation Strategy**: Test assumptions explicitly in ablations; document violations

---

## 15. Ethical & Reproducibility Considerations

### 15.1 Data Ethics

**C4 Dataset Concerns**:
- Contains web-scraped text (potential PII, biases)
- Use only for quality metric validation (no model publication)
- No manual inspection of raw text (privacy preservation)

**Mitigation**:
- Work with aggregated statistics only (entropy, diversity scores)
- No cherry-picking examples from subsets
- Discard subsets after experiment (no long-term storage)

### 15.2 Reproducibility

**Open Source Commitment**:
- Release full code pipeline on GitHub (after Phase 6)
- Provide subset sampling script (deterministic with fixed seed)
- Document exact C4 snapshot (date, HF dataset version)

**Random Seeds**:
- Set global seed for subset sampling: `seed=42`
- Record all hyperparameters in `config.yaml`

**Containerization**:
- Provide Dockerfile with pinned dependencies
- Include environment export: `pip freeze > requirements.txt`

---

## 16. Appendix: Metric Definitions

### A.1 Deduplication Ratio

```python
def compute_dedup_ratio(text_corpus: List[str], n: int = 13) -> float:
    """
    Compute deduplication ratio via n-gram overlap.
    
    Args:
        text_corpus: List of text documents
        n: N-gram size (default 13, following GPT-3)
    
    Returns:
        dedup_ratio: 1 - (unique_ngrams / total_ngrams)
    """
    ngrams = []
    for text in text_corpus:
        tokens = text.split()
        ngrams.extend([tuple(tokens[i:i+n]) for i in range(len(tokens)-n+1)])
    
    total_ngrams = len(ngrams)
    unique_ngrams = len(set(ngrams))
    
    return 1 - (unique_ngrams / total_ngrams)
```

### A.2 Domain Diversity (Herfindahl Index)

```python
def compute_domain_diversity(urls: List[str]) -> float:
    """
    Compute domain diversity via Herfindahl-Hirschman Index.
    
    Args:
        urls: List of source URLs for documents
    
    Returns:
        diversity: 1 - HHI, where HHI = Σ(share²)
    """
    from urllib.parse import urlparse
    from collections import Counter
    
    domains = [urlparse(url).netloc for url in urls]
    domain_counts = Counter(domains)
    total = sum(domain_counts.values())
    
    shares = [count / total for count in domain_counts.values()]
    hhi = sum(share ** 2 for share in shares)
    
    return 1 - hhi
```

### A.3 Average Perplexity

```python
def compute_avg_perplexity(text_corpus: List[str], model_name: str = "gpt2") -> float:
    """
    Compute average perplexity using pre-trained GPT-2.
    
    Args:
        text_corpus: List of text documents
        model_name: HuggingFace model identifier
    
    Returns:
        avg_perplexity: Mean perplexity across corpus
    """
    from transformers import GPT2LMHeadModel, GPT2Tokenizer
    import torch
    
    model = GPT2LMHeadModel.from_pretrained(model_name)
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    model.eval()
    
    perplexities = []
    for text in text_corpus:
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs, labels=inputs["input_ids"])
            perplexity = torch.exp(outputs.loss).item()
        perplexities.append(perplexity)
    
    return sum(perplexities) / len(perplexities)
```

### A.4 Token Efficiency

```python
def compute_token_efficiency(text_corpus: List[str]) -> float:
    """
    Compute ratio of semantic tokens to total tokens.
    
    Args:
        text_corpus: List of text documents
    
    Returns:
        efficiency: semantic_tokens / total_tokens
    """
    from nltk.corpus import stopwords
    import re
    
    stop_words = set(stopwords.words('english'))
    
    total_tokens = 0
    semantic_tokens = 0
    
    for text in text_corpus:
        # Remove markup and punctuation
        clean_text = re.sub(r'[^\w\s]', '', text.lower())
        tokens = clean_text.split()
        
        total_tokens += len(tokens)
        semantic_tokens += sum(1 for token in tokens if token not in stop_words)
    
    return semantic_tokens / total_tokens if total_tokens > 0 else 0.0
```

### A.5 Information Density (Ground Truth)

```python
def compute_information_density(text_corpus: List[str]) -> float:
    """
    Compute information density via entropy + redundancy + semantic diversity.
    
    Args:
        text_corpus: List of text documents
    
    Returns:
        info_density: Normalized score ∈ [0, 1]
    """
    # 1. Token-level entropy
    from collections import Counter
    import math
    
    tokens = ' '.join(text_corpus).split()
    token_counts = Counter(tokens)
    total_tokens = sum(token_counts.values())
    
    entropy = -sum((count / total_tokens) * math.log2(count / total_tokens) 
                   for count in token_counts.values())
    normalized_entropy = entropy / math.log2(len(token_counts))  # Normalize by max entropy
    
    # 2. Compression-based redundancy
    import zlib
    
    text_bytes = ' '.join(text_corpus).encode('utf-8')
    compressed_size = len(zlib.compress(text_bytes))
    original_size = len(text_bytes)
    redundancy = 1 - (compressed_size / original_size)
    
    # 3. Semantic diversity
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = embedder.encode(text_corpus[:1000])  # Sample for efficiency
    
    pairwise_sim = cosine_similarity(embeddings)
    np.fill_diagonal(pairwise_sim, 0)  # Exclude self-similarity
    semantic_diversity = 1 - pairwise_sim.mean()
    
    # Combined score
    info_density = (normalized_entropy + (1 - redundancy) + semantic_diversity) / 3
    return info_density
```

---

## 17. References

**Datasets**:
- Raffel et al. (2020). Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer. *JMLR*.
- Dodge et al. (2021). Documenting Large Webtext Corpora: A Case Study on the Colossal Clean Crawled Corpus. *EMNLP*.

**Quality Metrics**:
- Lee et al. (2022). Deduplicating Training Data Makes Language Models Better. *ACL*.
- Xie et al. (2023). Data Selection for Language Models via Importance Resampling. *NeurIPS*.

**Information Theory**:
- Shannon (1948). A Mathematical Theory of Communication. *Bell System Technical Journal*.
- Kunstner et al. (2019). Limitations of the Empirical Fisher Approximation for Natural Gradient Descent. *NeurIPS*.

**Diversity Measures**:
- Herfindahl (1950). Concentration in the Steel Industry. *PhD Thesis, Columbia University*.
- Reimers & Gurevych (2019). Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. *EMNLP*.

---

**Phase 2C Experiment Brief Completed**: 2026-08-28T08:28:00Z  
**Next Phase**: Phase 3 Implementation Planning (PRD, Architecture, PRP generation)  
**Estimated Phase 3 Complexity**: Tier 1 (8 tasks, 10 GPU-hours, straightforward analysis)
