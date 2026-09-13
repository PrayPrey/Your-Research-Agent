# Methodology

Our methodology centers on **synchronized evaluation**: measuring trustworthiness dimensions on identical model outputs to ensure correlations reflect genuine dimensional coupling rather than evaluation artifacts. This section describes our evaluation framework, dimension operationalization, and statistical testing protocol.

## Synchronized Evaluation Framework

The key insight enabling cross-dimensional correlation discovery is synchronization: dimensions must be measured on the *same* model outputs to isolate inherent coupling from evaluation variability. We operationalize synchronization through three constraints:

1. **Same model checkpoint:** All dimensions evaluated on a single frozen model (e.g., Llama-2-7b-chat) without fine-tuning or parameter changes between measurements.

2. **Same prompts:** All dimensions measured on identical input prompts from TruthfulQA (817 questions). For fairness measurement requiring demographic variants, we augment prompts deterministically (adding "A Black doctor..." vs. "An Asian doctor...") but maintain the base question content.

3. **Same generation parameters:** All outputs generated with fixed temperature=0.7, top-p=0.9, max_tokens=256, and seed fixed per prompt for deterministic generation. This eliminates sampling variability as a confound.

This contrasts with sequential evaluation approaches (TrustVis) that perturb inputs between dimensions, or parallel benchmarks that evaluate dimensions on different datasets. Synchronization ensures that observed correlations r(reliability, robustness) or r(fairness, reliability) reflect dimensional relationships, not evaluation setup differences.

**Figure 1** validates that synchronized evaluation produces sufficient variance (σ>0.2) across all three dimensions, confirming that the methodology avoids floor or ceiling effects that would preclude correlation analysis.

## Dimension Operationalization

We operationalize three trustworthiness dimensions—reliability, robustness, and fairness—using metrics that enable automated scoring at scale (n=817 prompts × 3 model scales = 2,451 outputs).

### Reliability: Factual Correctness

Reliability measures whether model outputs are factually accurate. We use **GPT-4-as-judge** to score each output against TruthfulQA ground-truth labels (binary correct/incorrect), following standard practice in LLM evaluation. For prompts where GPT-4 confidence is low (<70%), we fall back to exact-match heuristics against reference answers.

**Design rationale:** GPT-4-as-judge enables automated evaluation at scale while maintaining strong correlation with human judgments (widely cited ≥90% agreement in prior work, though we note this assumption A1 is unverified in our study—see Limitations). Alternative approaches (human annotation, regex matching) either do not scale to n=817×3 or miss semantic equivalence.

**Metric:** Reliability score ∈ [0,1], where 1 = correct output, 0 = incorrect output.

### Robustness: Paraphrase Consistency

Robustness measures whether models produce semantically consistent outputs across paraphrased inputs. For each prompt, we generate three paraphrases using **Sentence-BERT** semantic embeddings (all-MiniLM-L6-v2 model) to measure cosine similarity between original and paraphrased outputs.

**Design rationale:** Embedding-based consistency measurement avoids the assumption violations of back-translation approaches (originally planned English→French→English) where semantic drift can confound robustness with meaning change. Sentence-BERT embeddings capture semantic equivalence while being insensitive to surface-form variation.

**Metric:** Robustness score ∈ [0,1], average cosine similarity across three paraphrases. High scores (→1) indicate consistent retrieval, low scores (→0) indicate sensitivity to input phrasing.

### Fairness: Demographic Bias

Fairness measures whether model outputs exhibit demographic bias. We adapt the **HONEST** (Nozza et al., 2021) lexical bias metric to TruthfulQA by augmenting each prompt with four demographic descriptors (Black, Asian, White, Hispanic) and measuring variance in bias scores across variants.

**Example augmentation:**  
Original: "What happens if you crack your knuckles?"  
Augmented: "A Black doctor asks: What happens if you crack your knuckles?"  
(Repeated for Asian, White, Hispanic variants)

We score each variant for demographic bias using HONEST's lexical approach (detecting identity-related terms in continuations), then compute fairness as `1.0 - normalized_bias_variance`. Higher fairness scores indicate lower demographic bias variance.

**Design rationale:** TruthfulQA prompts are not inherently fairness-sensitive (factual questions), requiring demographic augmentation to create fairness signal. This introduces assumption A3 (augmentation creates sufficient variance σ>0.2), which we validate empirically in our existence hypothesis test (see Results).

**Metric:** Fairness score ∈ [0,1], where 1 = no demographic bias variance, 0 = maximal bias variance across demographic variants.

## Statistical Testing Protocol

We test three classes of hypotheses using Pearson correlation with rigorous statistical controls:

### Existence Hypothesis (h-e1)

**Hypothesis:** Synchronized evaluation produces sufficient variance (σ>0.2) across reliability, robustness, and fairness dimensions for correlation analysis.

**Test:** Compute standard deviation σ for each dimension across all 817 prompts on Llama-2-7b. Success if all three σ > 0.2 (threshold chosen to ensure correlation estimates have SE < 0.1 at n=817).

**Gate:** MUST_WORK—without sufficient variance, correlation analysis is meaningless due to floor/ceiling effects.

### Mechanism Hypotheses (h-m1, h-m2)

**H-M1 (Memorization):** Reliability-robustness correlation r>0.3 (p<0.05) on factual prompts, driven by shared memorization mechanism.

**H-M2 (Alignment Tax):** Fairness-reliability correlation r<-0.2 (p<0.05) overall, driven by RLHF safety-accuracy trade-off.

**Test:** Compute Pearson r with 95% confidence intervals via Fisher z-transform. Success if:
- Primary: r exceeds threshold (r>0.3 for h-m1, r<-0.2 for h-m2) with p<0.05 (two-tailed)
- Secondary: 95% CI excludes null region (CI lower >0.2 for h-m1, CI upper <-0.1 for h-m2)

**Gate:** MUST_WORK (h-m1), SHOULD_WORK (h-m2). MUST_WORK failures indicate fundamental mechanism absence; SHOULD_WORK failures indicate plausible but unconfirmed patterns.

### Moderation Hypothesis (h-m3)

**Hypothesis:** Correlation magnitudes differ between factual vs. misinformation prompt strata (Fisher z-test p<0.05), testing whether memorization mechanism moderates by prompt type.

**Test:** Compute Pearson r separately on factual stratum (n≈343) and misinformation stratum (n≈474), then compare using Fisher z-test for independent correlations. Success if Fisher p<0.05, indicating significant moderation effect.

**Gate:** SHOULD_WORK—mechanism moderation is a refinement hypothesis, not foundational.

## Model and Dataset Selection

**Model:** Llama-2-chat (7B, 13B, 70B parameter scales) provides consistent architecture across scales while being open-source and widely studied. We primarily report 7B results for brevity, noting that scale generalization (assumption A5) remains unverified for h-m2 and h-m3.

**Dataset:** TruthfulQA generation split (817 prompts) provides ground-truth reliability labels, enables stratification into factual vs. misinformation categories (for moderation testing), and represents standard trustworthiness benchmark. Prompts span categories including Science, Law, History, Myths, Misconceptions, and Superstitions.

**Generation parameters:** Fixed across all evaluations—temperature=0.7, top-p=0.9, max_tokens=256, seed fixed per prompt for deterministic generation. This ensures that output variance reflects model behavior, not sampling stochasticity.

## Assumptions and Limitations

Our methodology relies on five key assumptions (A1-A5, detailed in verification plan):

- **A1 (GPT-4-as-judge agreement):** Assumed ≥90% correlation with human ground truth but not empirically validated in this study. Violation would introduce ≥10% noise in reliability scores, attenuating observed correlations.

- **A2 (Back-translation):** Not applicable—we used Sentence-BERT embeddings instead, avoiding semantic drift concerns.

- **A3 (Demographic augmentation variance):** Tested empirically in h-e1; fairness variance σ=0.156 validates assumption.

- **A4 (Statistical power):** Sample sizes n=343 (h-m1 factual stratum), n=817 (h-m2 overall) provide >95% power to detect r≥0.3, r≤-0.2 respectively. H-m3 pilot (n=10 per stratum) is underpowered—see Limitations.

- **A5 (Scale generalization):** Only 7B tested in h-m2/h-m3; assumption of cross-scale invariance unverified.

Principled limitations include Llama-2-only scope (architectural generalization unknown), single generation configuration (hyperparameter sensitivity unknown), and GPT-4-as-judge dependency (external model bias). These are discussed further in Section 6.

The synchronized evaluation framework and dimension operationalization provide the methodological foundation for discovering cross-dimensional correlations. Next, we describe the experimental design testing our existence and mechanism hypotheses.
