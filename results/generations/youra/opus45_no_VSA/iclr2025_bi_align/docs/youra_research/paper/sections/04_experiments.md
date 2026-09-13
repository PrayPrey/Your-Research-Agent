# Experimental Setup

## Research Questions

Our experiments address three interconnected questions. First, can agency-preserving behaviors be reliably detected in existing preference data using simple linguistic proxies? This tests whether the construct is extractable at all. Second, does the extracted BAI signal occupy a representationally independent subspace from reward prediction? This tests whether BAI captures genuinely orthogonal variance rather than a stylistic subcomponent of helpfulness. Third, do high-BAI responses exhibit semantically coherent agency patterns? This tests whether representational independence translates to meaningful content.

## Datasets

We draw responses from two complementary preference datasets.

**HH-RLHF** \citep{HHRLHF2022} provides 170,000+ preference pairs from Anthropic's human feedback collection. We use the test split (40,688 responses) focusing on the "helpful" subset, which contains advisory and moral reasoning prompts where agency preservation is most relevant.

**RewardBench Safety** \citep{Lambert2024} provides 1,208 responses from the safety-focused evaluation subset. These responses often involve hedging, deferral, and clarification — behaviors our proxies target — making them valuable despite smaller scale.

Combined, we analyze 41,896 responses. For proxy classifier training, we use an 80/20 train/test split (33,516 / 8,380).

## Implementation

**Proxy Detection.** We generate ground-truth labels via regex pattern matching for each proxy type. Clarifying questions match interrogative structures (question marks following advisory content). Option enumeration matches numbered or bulleted lists. Epistemic hedging counts modal and uncertainty markers. Explicit deferral matches phrases indicating AI limitations or deference to user judgment.

Using these labels, we train TF-IDF + Logistic Regression classifiers (n-gram range 1-2, max 5000 features, C=1.0). This simple architecture provides interpretable probability scores for aggregation.

**Reward Scoring.** We score responses using OpenAssistant/reward-model-deberta-v3-large-v2, a publicly available reward model trained on preference data. Batch size 32, max tokens 512, GPU inference.

**Adversarial Probing.** We simulate 4096-dimensional hidden states with planted BAI and reward structure to validate the gradient reversal methodology. Real LLM activation extraction is deferred to future work due to computational constraints. The adversarial probing architecture uses DANN sigmoid scheduling (α: 0→1 over epoch 1), loss weighting λ=1.0, and 5 training epochs across 3 random seeds (42, 123, 456).

**Semantic Clustering.** We embed responses using sentence-transformers/all-MiniLM-L6-v2, reduce to 5 dimensions via UMAP (n_neighbors=15), and cluster with BERTopic (HDBSCAN, min_cluster_size=50). Topic keywords are extracted via c-TF-IDF.

## Evaluation Metrics

**Proxy Extraction (H-E1).** AUROC of each proxy classifier against held-out test set. Success: mean AUROC ≥ 0.8, all proxies > baseline (0.5).

**Representational Independence (H-M1).** BAI probe AUROC after gradient reversal (target: ≥ 0.7) and reward probe R² degradation (target: < 2%). Evaluated across 3 seeds for consistency.

**Disagreement Rate (H-M2).** Percentage of responses in HL ∪ LH quadrants after z-score standardization. PASS: ≥ 20%. PARTIAL: ≥ 10%.

**Semantic Coherence (H-C1).** Agency pattern rate: proportion of discovered topics with ≥ 2 agency keywords in top-10 c-TF-IDF terms. Target: ≥ 50%.

## Baselines

We compare against two baselines to isolate BAI's contribution:

**Reward Only.** Standard reward model scores without BAI computation. Tests whether disagreement analysis requires a second axis.

**Verbosity-Normalized BAI.** BAI without residualization against politeness markers. Tests whether length normalization alone explains results.
