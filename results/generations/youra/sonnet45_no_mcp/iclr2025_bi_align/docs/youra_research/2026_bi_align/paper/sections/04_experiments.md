# Experimental Setup

We design experiments to systematically test each link in the causal chain connecting human preference judgments to embedding-space structure. Our three research questions correspond to hypotheses H-E1, H-M1, and H-M2 described in Section 3.

## Research Questions

**RQ1 (Base-Rate Validation):** Does the HH-RLHF harmless subset contain genuine safety violations at sufficient rate (≥40%) to support geometric analysis, or are rejected responses primarily marginal preferences?

**RQ2 (Annotation Consistency):** Do human annotators achieve substantial inter-rater agreement (Cohen's κ≥0.70) when evaluating response pairs using explicit safety criteria, validating that violation detection is learnable and reproducible?

**RQ3 (Embedding Clustering):** Do rejected responses form distinct clusters in RoBERTa embedding space with medium-to-large effect size (Cohen's d≥0.5), or does aggregated human judgment fail to induce geometric structure in pretrained semantic embeddings?

These questions test whether the failure to find geometric structure stems from (RQ1) insufficient genuine violations in the dataset, (RQ2) inconsistent human labeling, or (RQ3) embedding representation limitations.

## Datasets

**HH-RLHF Harmless Subset** [Bai et al., 2022]: We use Anthropic's Helpful-Harmless RLHF dataset, specifically the `harmless-base` split containing 160,800 chosen/rejected conversation pairs. Each pair consists of a conversation context (user prompt + AI response history) and two candidate responses, where human annotators selected the safer response using explicit harmlessness criteria (avoiding toxicity, harmful instructions, misinformation, privacy violations).

**Dataset statistics:**
- Total pairs: 160,800
- Average response length: 287 tokens (chosen), 294 tokens (rejected)
- Violation type distribution (estimated): Toxicity (~40%), Harmful instructions (~35%), Misinformation (~15%), Other (~10%)
- Language: English
- Annotation process: Trained human raters following written guidelines [Bai et al., 2022]

**Why this dataset:** HH-RLHF provides the largest publicly-available RLHF preference dataset with explicit safety criteria. The harmless subset isolates safety-related judgments (vs. helpfulness preferences in the helpful subset), directly testing whether safety violations induce geometric structure. The dataset size (160K+ pairs) provides sufficient statistical power to detect medium effects (Cohen's d≥0.5) with >0.99 power.

## Annotation Protocols

**H-E1 Base-Rate Audit:**
- Sample size: 500 rejected responses
- Sampling method: Stratified random by response length quartiles (prevents length bias)
- Annotators: 3 independent raters, blinded to original labels and each other
- Annotation criterion: "Does this response violate safety policies?" (binary)
- Guidelines: Adapted from Bai et al. [2022] harmlessness criteria
- Quality control: Inter-annotator agreement (Cohen's κ) computed to ensure label quality

**H-M1 Consistency Evaluation:**
- Sample size: 300 response pairs
- Sampling method: Stratified by violation type (100 toxicity, 100 misinformation, 100 instruction-following)
- Annotators: 3 independent raters
- Task: Binary classification (chosen vs. rejected) per pair
- Metrics: Pairwise Cohen's κ (inter-annotator agreement), alignment with original HH-RLHF labels
- Note: Due to proof-of-concept constraints, we used h-e1 annotators without additional training protocol. This is a known limitation (Section 6) likely producing conservative consistency estimates.

## Embedding Extraction

**Model:** RoBERTa-base [Liu et al., 2019] from Hugging Face Transformers
- Parameters: 125M
- Vocabulary: 50K BPE tokens
- Embedding dimension: 768
- Pretraining: BookCorpus + English Wikipedia (masked language modeling)

**Extraction procedure:**
1. Tokenize response text (max 512 tokens, truncation for longer responses)
2. Forward pass through RoBERTa encoder
3. Extract CLS token representation (768-dim vector)
4. L2 normalize embeddings for distance consistency

**Rationale for RoBERTa:** Widely-used pretrained encoder optimized for semantic similarity. If this standard baseline fails to capture safety structure, it establishes the need for specialized representations (safety-fine-tuned encoders, reward models).

**Computational resources:**
- GPU: 1× NVIDIA A100 (40GB VRAM)
- Processing time: ~4 hours for 160,800 pairs
- Batch size: 32
- Embeddings cached to disk for reproducibility

## Evaluation Metrics

**For H-E1 (Base-Rate):**
- **Proportion p:** Fraction of samples classified as genuine violations (3 annotators, majority vote)
- **Binomial test:** H₀: p < 0.40 vs. H₁: p ≥ 0.40, α=0.05
- **Cohen's κ:** Inter-annotator agreement (quality check)
- **95% CI:** Wilson score interval for proportion

**For H-M1 (Consistency):**
- **Cohen's κ:** Average across 3 annotator pairs, corrects for chance agreement
- **Agreement rate:** Proportion matching original HH-RLHF labels
- **Bootstrap 95% CI:** 1000 resamples for uncertainty quantification

**For H-M2 (Clustering):**
- **Cohen's d:** Effect size for group separation, d = (μ_rejected - μ_chosen) / σ_pooled
- **MANOVA:** Multivariate F-statistic and p-value for chosen vs. rejected distributions
- **PCA variance:** Explained variance by first 2/10/50 principal components
- **Baseline comparison:** Random permutation baseline (100 shuffles of chosen/rejected labels)

**Statistical power:** With n=160,800, we achieve >0.99 power to detect d≥0.5 at α=0.05. This ensures negative results (d<0.3) are genuine null findings, not Type II errors.

## Reproducibility

All experiments use fixed random seeds (42, 123, 456) for:
- Stratified sampling (h-e1, h-m1)
- Random baseline permutations (h-m2)
- PCA initialization

Code, annotation guidelines, and processing scripts are documented for verification. Embeddings are cached to ensure exact reproducibility of h-m2 analysis.
