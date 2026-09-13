# Experimental Setup

We design experiments to answer four research questions mapping to our assumptions:

**RQ1:** Can design features be extracted objectively at scale? (Tests A2: feature extraction protocol)

**RQ2:** Do coverage families capture meaningful groupings? (Tests A4: family similarity)

**RQ3:** Do families predict future adoption? (Tests main claim + A3: temporal persistence)

**RQ4:** Can NLP classify citation contexts reliably? (Tests A1: citation evidence quality)

## Datasets

**Benchmark Paper Corpus:** 20 diverse benchmarks stratified across modalities:
- **Vision (5):** ImageNet, COCO, PASCAL VOC, CelebA, CIFAR-10
- **Language-Translation (3):** WMT14, WMT16, IWSLT
- **Language-QA (4):** SQuAD, Natural Questions, TriviaQA, HotpotQA
- **Audio/Multimodal (8):** LibriSpeech, Common Voice, VGGSound, VoxCeleb, MS-COCO (multimodal), Conceptual Captions, Visual Genome, MSCOCO Captions

**Rationale:** Pilot sample (20 vs 100+ targeted corpus) enables proof-of-concept while covering major modalities. Stratified sampling ensures diversity for cluster discovery. Benchmarks selected with ≥50 citations to ensure sufficient usage data.

**Citation Data:** Extracted via Semantic Scholar API for 2015-2024 papers citing selected benchmarks. Historical split: pre-2023 for training, 2023-2024 for test (temporal validation).

**Synthetic Citation Contexts (H-E1):** 100 template-generated validation claims vs baseline mentions for SciBERT classifier training. Real-world validation deferred to future work.

## Baselines

**Random Baseline:** Random assignment of benchmarks to coverage families. Expected citation overlap ≤50% (null hypothesis H0).

**Citation-Count Baseline:** Rank by popularity (total citations). Tests whether popularity alone predicts coverage.

**Manual Expert Review:** Gold standard for accuracy but requires weeks per hypothesis (not scalable). Comparison deferred to Phase 5.

## Evaluation Metrics

**H-M1 (Feature Extraction):** Cohen's kappa for categorical features (task, modality, metrics), ICC for continuous (dataset size). Target: kappa >0.80.

**H-M2 (Clustering Quality):** Intra-family cosine similarity, silhouette score, modularity on citation network. Target: similarity ≥0.60.

**H-M3 (Prediction Accuracy):** Jaccard similarity of citation sets within families. Target: >70% with p<0.05 vs random.

**H-E1 (Classification):** Precision/recall on held-out synthetic test set. Target: precision >85%.

## Implementation Details

- **Embeddings:** SentenceBERT (all-MiniLM-L6-v2) for benchmark descriptions
- **Clustering:** K-means with k∈{2,4,6,8}, selected via silhouette score
- **Citation Classifier:** SciBERT fine-tuned on synthetic data (80/20 train/test split)
- **Statistical Testing:** Permutation test (1000 iterations) for citation overlap significance
