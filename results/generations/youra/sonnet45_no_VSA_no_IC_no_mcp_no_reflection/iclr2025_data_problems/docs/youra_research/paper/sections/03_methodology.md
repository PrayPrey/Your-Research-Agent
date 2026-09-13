# Methodology

Our methodology follows a controlled experimental design to isolate and measure the relationship between data quality metrics Q(D) and information density. The core idea is simple: if quality dimensions like deduplication, diversity, perplexity, and efficiency truly affect how much "information" each token carries, we should observe correlations when we systematically vary these dimensions and measure resulting information content.

## Data Quality Metric Q(D)

We define data quality as a composite of four components, each capturing a distinct aspect of information content:

**1. Deduplication Ratio** measures redundancy removal. Duplicate or near-duplicate documents carry zero marginal information—the second occurrence of identical text teaches the model nothing new. We compute the deduplication ratio as:

$$
\text{dedup\_ratio} = 1 - \frac{\text{tokens in duplicates}}{\text{total tokens}}
$$

where duplicates are identified via MinHash LSH (Broder, 1997) with Jaccard similarity threshold 0.9. A corpus with 40% duplicate content has dedup_ratio = 0.6. Higher values indicate less redundancy.

**Rationale:** GPT-3 and subsequent models use fuzzy deduplication heuristics, suggesting practitioners believe redundancy hurts efficiency. We test this empirically.

**2. Domain Diversity** measures concept coverage breadth. A corpus drawn from only one domain (e.g., medical journals) has narrower information content than one spanning multiple domains (news, Wikipedia, books, code). We compute diversity via Shannon entropy over domain distributions:

$$
\text{diversity} = -\sum_{i=1}^{N} p_i \log p_i
$$

where $p_i$ is the fraction of tokens from domain $i$. We use 8 C4 source domains (web crawl categories). Uniform distribution maximizes diversity.

**Rationale:** The Pile's emphasis on 22 curated sources reflects belief that domain diversity improves generalization. We quantify this intuition.

**3. Perplexity Score** measures signal-to-noise ratio. High-perplexity text is harder for a reference language model to predict, indicating either noise (garbled text, non-English) or unusual information. We score documents using GPT-2 small (125M parameters) and normalize:

$$
\text{perplexity\_score} = 1 - \frac{\log(\text{ppl}) - \log(\text{ppl}_{\min})}{\log(\text{ppl}_{\max}) - \log(\text{ppl}_{\min})}
$$

where lower perplexity (more predictable) scores higher. This inverts the intuition that "perplexity is bad"—we want predictable, well-formed text.

**Rationale:** LLaMA filters documents by perplexity. We validate whether perplexity correlates with information density.

**4. Token Efficiency** measures signal density within documents. Documents with excessive whitespace, short sentences, or boilerplate (e.g., cookie consent banners) carry less information per token. We compute:

$$
\text{efficiency} = \frac{\text{content tokens}}{\text{total tokens}}
$$

where content tokens exclude punctuation-only sequences, whitespace runs, and repetitive boilerplate patterns detected via regex.

**Rationale:** Information theory suggests compression removes redundancy. Efficient text packs more meaning per token.

**Composite Q(D):** We combine components via weighted average:

$$
Q(D) = w_1 \cdot \text{dedup\_ratio} + w_2 \cdot \text{diversity} + w_3 \cdot \text{perplexity\_score} + w_4 \cdot \text{efficiency}
$$

where weights $w_i$ are learned via linear regression against information density (Section 3.3). For interpretability, we also report individual component correlations.

## Information Density Measurement

Information density quantifies how much "learning content" each token provides, independent of downstream task performance. We measure it through three complementary proxies:

**1. Token Entropy** measures average information content per token via Shannon entropy over the unigram distribution. For a corpus with token counts $c(t)$ and total tokens $N$:

$$
H_{\text{token}} = -\sum_{t \in V} \frac{c(t)}{N} \log_2 \frac{c(t)}{N}
$$

Higher entropy indicates more uniform token distribution (less predictability), implying richer vocabulary usage. We normalize by log₂|V| to get density ∈ [0,1].

**2. N-gram Redundancy** measures repetitive structure via 3-gram and 5-gram overlap statistics. For each n-gram order, we compute:

$$
\text{redundancy}_n = \frac{\text{repeated n-grams}}{\text{total n-grams}}
$$

and invert to get diversity_n = 1 - redundancy_n. High redundancy indicates formulaic, repetitive text.

**3. Semantic Diversity** measures concept coverage via embedding-based analysis. We encode sentences using SentenceTransformer (Reimers & Gurevych, 2019), compute pairwise cosine similarities, and measure average distance:

$$
\text{semantic\_diversity} = 1 - \frac{1}{N(N-1)} \sum_{i \neq j} \text{sim}(e_i, e_j)
$$

where $e_i$ are sentence embeddings. Higher diversity indicates broader concept coverage.

**Combined Density:** We average the three proxies (after normalization to [0,1]) to get a single information density score ∈ [0,1]:

$$
\text{info\_density} = \frac{1}{3}(H_{\text{norm}} + \text{diversity}_{\text{ngram}} + \text{semantic\_diversity})
$$

This composite measure balances lexical (entropy), structural (n-gram), and semantic (embedding) perspectives on information content.

## Controlled Experimental Design

To isolate each quality dimension's effect, we create 12 C4 subsets (10GB each, 120GB total) with systematic quality variations:

- **3 deduplication levels:** None (baseline, ~40% duplicates), Medium (fuzzy dedup, ~20% duplicates), High (exact + fuzzy dedup, <5% duplicates)
- **3 diversity levels:** Low (single domain), Medium (4 domains balanced), High (8 domains balanced)
- **3 perplexity levels:** Low (bottom 33% GPT-2 perplexity), Medium (middle 33%), High (top 33%)
- **3 efficiency levels:** Low (<50th percentile token efficiency), Medium (50-75th), High (>75th)

We use a **fractional factorial design** (Box et al., 2005) to cover all dimensions without requiring $3^4 = 81$ subsets. Specifically, we sample 12 combinations that maximize orthogonality between factors, enabling independent effect estimation.

Each subset is created by:

1. **Sampling from C4:** Stream en-split C4 dataset (allenai/c4) and select 10GB of text matching the target quality profile
2. **Computing Q(D) metrics:** Apply MinHash LSH deduplication detection, domain classification, GPT-2 perplexity scoring, and efficiency analysis to each document
3. **Computing information density:** Calculate token entropy, n-gram redundancy, and semantic diversity on the full 10GB subset
4. **Correlation analysis:** Pearson and Spearman correlations between each Q(D) component and info_density, with p-value testing (H₀: r = 0) at α = 0.01 significance level

**Success criterion (h-e1 MUST_WORK gate):** All four Q(D) components achieve r > 0.5 and p < 0.01. This threshold was set a priori based on the expectation that quality should have large, easily detectable effects if it matters for scaling laws.

## Reproducibility Testing

To ensure Q(D) measurements are stable (not sample-dependent noise), we independently resample three additional C4 subsets at the "Medium" quality level (middle of each dimension) and compute coefficient of variation (CV = σ/μ) for each Q(D) component across the four instances (original Medium + 3 resamples).

**Success criterion:** CV < 10% for all components, indicating measurement variance is low enough for production use.

## Baseline Comparisons

We compare composite Q(D) against:

- **Random baseline:** Correlation between Q(D) and shuffled info_density values (should yield r ≈ 0)
- **Single-metric baselines:** Best individual Q(D) component (dedup_ratio alone)
- **Composite advantage:** Does weighted Q(D) outperform best single metric?

This tests whether combining four components provides value beyond the strongest single predictor.

## Implementation Details

All experiments use:

- **Dataset:** C4 (allenai/c4, en split)
- **Deduplication:** MinHash LSH with 128 hash functions, Jaccard threshold 0.9
- **Perplexity model:** GPT-2 small (125M params) from Hugging Face Transformers 4.30.2
- **Embedding model:** SentenceTransformer all-MiniLM-L6-v2 (22M params)
- **Computation:** V100 GPUs (32GB), 9.2 GPU-hours total for all subsets
- **Code:** Open-sourced at [URL] for reproducibility

Statistical tests use Python scipy.stats with Bonferroni correction for multiple comparisons (4 components × 2 correlation types = 8 tests, corrected α = 0.01/8 = 0.00125).

---

This methodology enables controlled, reproducible measurement of data quality's relationship to information content—the necessary first step before testing causal mechanisms (does curation *increase* density?) or compute tradeoffs (does higher Q(D) *reduce* required compute?). We focus narrowly on the existence proof: **do the metrics correlate?**
