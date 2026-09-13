# Methodology

Our approach is designed to answer three mechanistic questions: Does semantic clustering add value beyond multiple sampling? Do uncertainty methods capture orthogonal dimensions? Do error types exhibit distinct uncertainty signatures? To answer these questions, we need controlled comparisons that isolate specific mechanisms while holding other factors constant.

## Experimental Design Principles

The key challenge in comparing uncertainty methods is disentangling mechanism from computational budget. A naive comparison of semantic entropy (which requires K=10 samples for clustering) to token probability variance (which requires K=1 sample) confounds the clustering mechanism with the sampling cost. We cannot determine whether any performance difference comes from clustering or from simply using more samples.

Our solution is to design ablation studies with matched computational budgets. For the semantic entropy ablation, both the test method (semantic entropy with clustering) and the baseline (ensemble voting without clustering) use exactly K=10 samples. The only difference is the semantic clustering step. This isolates the clustering contribution.

Similarly, for the method independence analysis, we apply all methods to identical samples from the same model runs. This ensures that observed correlations reflect genuine mechanistic differences rather than sample variance.

## Uncertainty Estimation Methods

We implement four uncertainty methods representing distinct computational approaches:

**Semantic Entropy** follows Kuhn et al. (2023). For each question, we sample K=10 answers at temperature T=0.7 using Mistral-7B. We embed each answer using sentence-transformers (all-MiniLM-L6-v2) and perform agglomerative clustering with cosine distance threshold 0.5. This groups semantically equivalent answers like "Paris", "The capital is Paris", and "Paris, France" into the same cluster. We then compute entropy over the cluster distribution:

H_semantic = -∑_c p(c) log p(c)

where p(c) is the proportion of samples in cluster c. Higher entropy indicates higher uncertainty.

**Ensemble Baseline** provides the ablation control. We sample K=10 answers at temperature T=0.7 (identical sampling to semantic entropy) but skip the semantic clustering step. Instead, we use exact string matching to identify the most common answer and compute disagreement rate:

U_ensemble = 1 - (count of most common answer / K)

This measures sampling agreement without semantic grouping. By comparing semantic entropy to this baseline with matched K=10, we isolate the clustering contribution.

**Self-Consistency** follows Wang et al. (2022). We sample K=10 answers and compute the agreement fraction for the most common answer. This differs from the ensemble baseline in that we report agreement rather than disagreement and use this for method independence analysis rather than ablation.

**Verbalized Confidence** prompts the model to self-report confidence following Kadavath et al. (2022). We append to each question: "Provide your answer and your confidence level from 0% (not confident) to 100% (fully confident)." We extract the percentage using regex pattern matching, with fallback to 50% if no percentage is found. This requires K=2 forward passes (answer + confidence).

**Token Variance** computes variance over token probability distributions as a traditional baseline. For each generated answer, we calculate the variance of token probabilities across the sequence. Due to an implementation issue discovered during validation, this method collapsed with self-consistency (correlation 1.0) and requires reimplementation for future work.

## Datasets and Error Types

We use two standard benchmarks representing different error characteristics:

**NaturalQuestions** (Kwiatkowski et al., 2019) provides factual questions drawn from Google search queries with Wikipedia-based answers. We use the unanswerable subset (100 questions) where no answer exists in the provided context. These represent knowledge gaps where the model lacks information to answer correctly. Ground truth labels allow us to measure whether uncertainty methods can detect these knowledge limitations.

**TruthfulQA** (Lin et al., 2021) tests whether models generate truthful answers to questions designed to elicit common misconceptions. We sample 100 questions covering domains like health, law, and politics. These represent scenarios where models might confidently produce false information based on training data patterns. Ground truth labels indicate whether generated answers are truthful.

The hypothesis that these datasets cleanly separate error types (knowledge gaps vs. confident misconceptions) is testable. We measure semantic diversity and sampling agreement on both datasets to determine whether error types exhibit distinct signatures.

## Model and Generation Parameters

All experiments use Mistral-7B-v0.1, an open-source 7-billion parameter decoder-only transformer model. This choice balances accessibility (publicly available weights) with capability (achieves >50% accuracy on NaturalQuestions, avoiding the failure mode where GPT-2 achieved only 0.9% on TruthfulQA in prior work).

Generation parameters are fixed across all experiments:
- Temperature: 0.7 (enables diversity while maintaining quality)
- Maximum tokens: 50
- Number of samples K: 10 for semantic entropy, ensemble baseline, and self-consistency; 1 for token variance; 2 for verbalized confidence
- Random seed: 42 for reproducibility

## Evaluation Metrics

We evaluate uncertainty methods using standard discrimination and calibration metrics:

**Area Under ROC Curve (AUROC)** measures how well the uncertainty estimate discriminates between correct and incorrect answers. AUROC ranges from 0 to 1, with 0.5 indicating random performance and 1.0 indicating perfect discrimination. We use AUROC as the primary metric because it is threshold-independent and robust to class imbalance.

**Pearson correlation** quantifies the linear relationship between uncertainty method scores. For the method independence analysis, we compute pairwise correlations across all method pairs. Low correlation (|r| < 0.3) indicates orthogonal signals, while high correlation (|r| > 0.7) suggests redundancy.

**Statistical significance** is assessed using t-tests for mean differences (error-type diversity comparison) with significance threshold α = 0.05. For the ablation study, we set the minimum detectable effect size at 0.07 AUROC points based on pilot data.

## Experimental Protocol

Each hypothesis follows a three-stage protocol:

**Stage 1: Data Collection.** Generate K samples per question using Mistral-7B with fixed seed. Store all generations with ground truth labels for consistent evaluation across methods.

**Stage 2: Method Application.** Apply all uncertainty methods to the same generated samples. This ensures that observed differences reflect method mechanisms rather than sampling variance.

**Stage 3: Analysis.** Compute evaluation metrics (AUROC, correlation, statistical tests) and compare against pre-registered thresholds from the verification plan (Phase 2B). Gate conditions determine validation status: MUST_WORK gates require passing for core contributions, SHOULD_WORK gates indicate supporting evidence.

This protocol ensures that experimental design matches the mechanistic questions we aim to answer, with controls in place to isolate specific contributions.
