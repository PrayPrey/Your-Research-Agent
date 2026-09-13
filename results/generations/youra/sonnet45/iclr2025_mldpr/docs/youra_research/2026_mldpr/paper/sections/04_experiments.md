# Experimental Setup

Our experimental design tests three questions that decompose the lifecycle separability hypothesis: (Q1) Do lifecycle categories exhibit operational stability across repositories? (Q2) Are lifecycle signals linearly detectable in semantic embeddings? (Q3) Can unsupervised clustering recover lifecycle structure? Each question maps to specific experimental protocols with quantitative success criteria.

## Research Questions and Success Criteria

| Question | Hypothesis | Metric | Success Threshold | Purpose |
|----------|------------|--------|-------------------|---------|
| **Q1** | Lifecycle categories are reliable measurement constructs | Inter-annotator agreement (κ) | κ ≥ 0.60 | Validate operational stability—if annotators can't agree, automated methods have no ground truth |
| **Q2** | Embeddings encode lifecycle signals linearly | Linear probe accuracy | ≥ 0.75 on held-out data | Prove distributional signatures exist and are geometrically accessible—rules out "signal absent" |
| **Q3** | Unsupervised clustering recovers structure | K-means NMI & baseline gap | NMI > 0.60 AND gap ≥ 0.15 | Test unsupervised discovery—can lifecycle structure be found without labels? |

This decomposition isolates failure modes: if Q1/Q2 pass but Q3 fails, lifecycle separability manifests as a supervised signal (clustering algorithm mismatch), not signal absence.

## Datasets and Sampling

We collected 300 metadata fields stratified across three repositories:

- **HuggingFace Hub (150 fields)**: 75 scaffolded (Open Datasheets structured markup) + 75 unscaffolded (legacy datasets). Sample drawn from top-1000 most-downloaded datasets (Feb 2026 snapshot). Scaffolded/unscaffolded split tests interface amplification hypothesis.

- **OpenML (100 fields)**: Sampled from datasets with ≥50 downloads and complete metadata (quality filter). Intermediate schema structure—predefined categories (data properties, task descriptions) with free-text.

- **UCI Machine Learning Repository (50 fields)**: Sampled from datasets added post-2020 (modern documentation). Minimal schema—plain text READMEs with variable formatting. Critical for testing unstructured case.

**Stratification rationale**: Oversampled UCI (50 fields from ~500 total datasets vs. 150 fields from HF's 100,000+) to ensure generalization beyond structured repositories despite UCI's smaller ecosystem size. Scaffolded/unscaffolded HF split controls for interface effects on intrinsic signals.

**Exclusion criteria**: Datasets without English metadata (4 excluded), metadata fields with <5 words (uninformative, 12 excluded), duplicate datasets across repositories (2 excluded). Final N=300.

## Baselines

We compare semantic clustering (K-means on sentence-transformer embeddings) against three baselines:

### Permutation Baseline (Chance Performance)

Random 2-way label permutation repeated 1000 times, report mean NMI. Establishes chance performance for 11:1 class imbalance (not uniform 50-50).

### Topic Model Baseline (LDA)

Latent Dirichlet Allocation with 2 topics on TF-IDF bag-of-words representations (stop-words removed via NLTK). Tests whether topic clustering recovers lifecycle structure without semantic embeddings. Hyperparameters: α=0.5 (document-topic prior), β=0.01 (topic-word prior), 1000 Gibbs sampling iterations.

**Rationale**: LDA is standard for unsupervised document clustering. If LDA performs comparably to sentence-transformers, embeddings provide no value over simpler methods.

### Lexical Heuristic Baseline

Keyword matching for lifecycle categories:
- **RAI keywords**: {`license`, `privacy`, `ethical`, `ethics`, `fairness`, `bias`, `prohibited`, `restriction`, `consent`, `anonymization`}
- **General Info keywords**: {`name`, `source`, `description`, `format`, `size`, `url`, `download`, `version`, `date`, `author`}

Fields matching ≥1 RAI keyword → RAI; otherwise → General Info. Tests whether simple lexical patterns suffice without embeddings.

**Rationale**: If lexical heuristics achieve NMI ~0.50, lifecycle categories manifest as surface keyword patterns—semantic embeddings unnecessary. If lexical heuristics fail, distributional context matters (justifies embeddings).

## Experimental Protocols

### Q1: Inter-Annotator Agreement (Operational Stability)

**Protocol**: Three annotators (A1, A2, A3) independently labeled all 300 fields blind to repository source using Roman et al.'s [2023] 2-tier taxonomy (General Information vs. Responsible AI). Annotators received Datasheets for Datasets [Gebru et al., 2018] documentation as reference. No discussion allowed pre-annotation to ensure independence.

**Metrics**: Cohen's κ for all pairs (A1-A2, A1-A3, A2-A3), report mean ± std. Compute κ_within for each repository (HF, OpenML, UCI) to identify context-dependence.

**Success criterion**: κ ≥ 0.60 (substantial agreement by Landis & Koch [1977]). If κ_across < 0.60 but κ_within ≥ 0.70 for structured repos, conclude lifecycle is repository-scoped.

### Q2: Linear Probe (Signal Detectability)

**Protocol**: Embed all 300 fields using `sentence-transformers/all-MiniLM-L6-v2` (frozen, 384-d). Train logistic regression probe on scaffolded HF data (75 samples, 60/15 train/validation split via stratified sampling to preserve 8.3% class balance). L2 regularization with C=1.0 (default scikit-learn). Test on remaining 225 fields (unscaffolded HF + OpenML + UCI).

**Rationale**: Train on scaffolded data (highest expected signal due to structured interface) and test on unscaffolded + cross-repository samples. If probe generalizes, distributional signatures transcend interface effects.

**Metrics**: Accuracy, precision/recall per class (General vs. RAI), confusion matrix.

**Success criterion**: Accuracy ≥ 0.75 on held-out test set. High precision/recall for both classes (not just majority class).

### Q3a: K-means Clustering (Unsupervised Recovery)

**Protocol**: K-means clustering (k=2) on 384-d embeddings. K-means++ initialization [Arthur & Vassilvitskii, 2007], 10 independent trials with different random seeds. Compute NMI between discovered clusters and ground-truth lifecycle labels.

**Metrics**: NMI (mean ± std over 10 trials), Adjusted Rand Index (ARI) for cluster stability.

**Success criterion**: NMI > 0.60 AND variance < 0.05 (stable across seeds).

### Q3b: Baseline Comparisons (Semantic Value)

**Protocol**: Compute NMI for all baselines (permutation, LDA, lexical) on same 300-field dataset. Compare K-means NMI against max(baseline NMI).

**Metrics**: Baseline gap = NMI(K-means) - max(NMI(baselines)).

**Success criterion**: Baseline gap ≥ 0.15. If gap < 0.05, embeddings provide minimal value—simpler methods suffice.

### Q3c: Repository Stratification (Generalization)

**Protocol**: Compute K-means NMI separately for HF, OpenML, UCI. Train repository-specific linear probes (HF-only 75 train, test on same repo's held-out). Measure probe accuracy variance and NMI variance across repositories.

**Metrics**: Probe accuracy std, NMI std across repositories.

**Interpretation**: High variance (>0.15 std) indicates lifecycle separability is repository-specific rather than universal.

### Q3d: Scaffolding Effect (Interface Amplification)

**Protocol**: Compare K-means NMI for scaffolded (75 HF fields) vs. unscaffolded (75 HF fields) subsets.

**Metrics**: NMI(scaffolded) - NMI(unscaffolded) gap.

**Interpretation**: Gap ∈ [0.1, 0.2] validates signal amplification (scaffolding enhances intrinsic structure). Gap > 0.2 suggests interface-induced artifacts. Gap < 0.05 suggests scaffolding adds no value.

## Hyperparameters and Implementation Details

| Component | Implementation | Hyperparameters |
|-----------|---------------|-----------------|
| Sentence embeddings | `sentence-transformers/all-MiniLM-L6-v2` | 384-d, frozen, cosine similarity |
| Linear probe | Logistic regression (scikit-learn 1.2.2) | L2 regularization C=1.0, max_iter=1000 |
| K-means | scikit-learn 1.2.2 | k=2, init='k-means++', n_init=10, random_state=42 |
| LDA | scikit-learn 1.2.2 | n_topics=2, α=0.5, β=0.01, 1000 iterations |
| TF-IDF | scikit-learn 1.2.2 | max_features=1000, min_df=2, stop_words='english' |

**Compute environment**: Single NVIDIA A100 GPU (40GB), PyTorch 2.0, Python 3.10. Embedding inference: ~0.5 seconds for 300 fields. K-means 10 trials: ~2 seconds total. Linear probe training: ~0.1 seconds.

## Evaluation Metrics Justification

- **NMI (Normalized Mutual Information)**: Measures cluster-label agreement, normalized for cluster size imbalance. Range [0,1], 1=perfect agreement. Preferred over Rand Index because NMI handles imbalanced clusters (our 11:1 ratio) without penalty.

- **Cohen's κ**: Standard inter-annotator reliability metric, accounts for chance agreement. κ>0.60 = substantial agreement [Landis & Koch, 1977]. More robust than raw percent agreement for imbalanced classes.

- **Probe accuracy**: Direct measure of linear separability. High accuracy proves distributional signals are geometrically accessible to linear classifiers. Per-class precision/recall ensures we're not just predicting majority class.

## Reproducibility

All data collection scripts, annotation guidelines, sampled field lists, and experimental code will be released under MIT license upon publication. Repository snapshots (HF: Feb 2026, OpenML: Jan 2026, UCI: Dec 2025) archived for reproducibility. Sentence-transformer model cached from Hugging Face Hub (sha256 checksum verified). Random seeds fixed (42 for data splits, 0-9 for K-means trials) for deterministic reproduction.
