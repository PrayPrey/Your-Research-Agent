# Methodology

Our experimental design is motivated by a single question: does semantic entropy's advantage over token entropy at 65B scale (Kuhn et al. [2023]) hold at 7B scale, and if so, what is the mechanism? To answer this, we need all four major uncertainty proxy types evaluated under identical conditions — same model, same questions, same samples, same evaluation metric. This shared-condition design eliminates confounds present in prior comparisons and enables direct attribution of performance differences to method characteristics rather than experimental setup.

## Models and Datasets

**Language Models.** We use Llama-2-7B (meta-llama/Llama-2-7b-hf) for all sampling-based methods (SE, TE, SCG) and Llama-2-7B-Chat (meta-llama/Llama-2-7b-chat-hf) for verbalized confidence, which requires instruction-following capability for the elicitation prompt. Both models use float16 precision with device_map="auto".

**Datasets.** We evaluate on two factual QA benchmarks:

- **TriviaQA (dev split):** Open-domain factual recall with alias-normalized exact-match labels. N=98 questions selected by random seed 42. TriviaQA is characterized by incorrect model outputs that take diverse surface forms — wrong answers vary substantially in wording while sometimes sharing semantic content, making it an appropriate benchmark for testing paraphrase-noise filtering methods.

- **TruthfulQA:** Adversarial misconception benchmark designed to test whether models repeat false beliefs. N=141 questions with yes/no prefix matching for correctness labels. TruthfulQA is characterized by low-diversity incorrect outputs — models confidently generate the same wrong answer across multiple samples — making it a natural contrast case for the task-structure hypothesis.

The TriviaQA/TruthfulQA pair is chosen specifically to test whether the SE > TE ordering is benchmark-specific or general: the two benchmarks differ primarily in the diversity structure of incorrect outputs, providing a controlled contrast.

## Uncertainty Estimation Methods

All stochastic methods use K=10 samples at temperature 0.7, max_new_tokens=50, matching Kuhn et al. [2023] for comparability.

**Token Entropy (TE).** For each question, we generate one greedy-decoded response and extract per-token logits. Token entropy is computed as the mean per-token Shannon entropy over the softmax distribution:

$$\text{TE}(x) = \frac{1}{|x|} \sum_{t=1}^{|x|} H(\text{softmax}(\text{logits}_t))$$

where $H$ denotes Shannon entropy. Higher TE indicates higher token-level uncertainty. **Rationale:** TE is the simplest and most computationally efficient baseline — it requires no additional samples and no external models. Its known limitation (insensitivity to semantic equivalence between surface-distinct outputs) is precisely what the paraphrase-noise hypothesis predicts should hurt its performance relative to SE on TriviaQA.

**Semantic Entropy (SE).** Following Kuhn et al. [2023], we generate K=10 stochastic samples and cluster them using bidirectional NLI entailment. Two samples $s_i, s_j$ are assigned to the same cluster if both $\text{NLI}(s_i, s_j) \geq \theta$ and $\text{NLI}(s_j, s_i) \geq \theta$ (entailment in both directions). We use cross-encoder/nli-deberta-v3-large as the NLI model (the large variant is preferred over small to avoid NLI model size as a confound). Cluster entropies are aggregated via logsumexp:

$$\text{SE}(x) = -\sum_{c \in C} \log \sum_{s \in c} p(s|x)$$

where $C$ denotes the set of clusters and $p(s|x)$ is the log-probability of sample $s$. **Rationale:** NLI-based clustering absorbs surface variation within semantically equivalent groups before computing entropy. If the paraphrase-noise hypothesis is correct — that TE's within-cluster variation is the dominant driver of the SE > TE gap — then SE's clustering step is the mechanism, and we should measure it directly (see Section 3.4).

**AUROC convention (critical):** Higher uncertainty should predict higher probability of incorrectness. We negate SE and TE scores before AUROC computation (higher uncertainty = higher score = higher AUROC). This convention is followed consistently in H-E1 (the primary evaluation) and must be applied uniformly to avoid the sign-inversion issue we document in Section 5.

**SelfCheckGPT BERTScore (SCG).** We compute pairwise BERTScore consistency across K=10 samples and define uncertainty as 1 minus mean agreement:

$$\text{SCG}(x) = 1 - \frac{1}{K(K-1)} \sum_{i \neq j} \text{BERTScore}(s_i, s_j)$$

We use the BERTScore variant of SelfCheckGPT [Manakul et al., 2023], implemented with the official selfcheckgpt library. **Rationale:** SCG tests whether lexical-overlap-based consistency (BERTScore) achieves SE-equivalent performance. If BERTScore captures the same semantic equivalences as NLI entailment, SCG and SE should produce equivalent AUROC. The hypothesis that BERTScore fails on short QA answers (where a 2-word wrong answer may score high BERTScore against another 2-word wrong answer with different meaning) is directly testable.

**Verbalized Confidence (VC).** We prompt Llama-2-7B-Chat to self-report confidence after answering:

```
Answer the following question: {question}
Your answer: {model_answer}
How confident are you in your answer? Please provide a percentage (0-100%).
Confidence:
```

The response is parsed with a regex cascade to extract the numerical confidence value. **Rationale:** VC tests whether 7B-scale instruction-tuned models have reliable meta-cognitive access to their own uncertainty. Prior work (Xiong et al. [2023]; Kadavath et al. [2022]) finds VC poorly calibrated at 7B scale; we independently characterize the calibration failure and connect it to the AUROC evaluation framework.

## Evaluation

**AUROC** is computed using sklearn.metrics.roc_auc_score with negated uncertainty scores. Bootstrap confidence intervals (n=1000 iterations, seed=42, stratified resampling) provide 95% CIs for all AUROC estimates.

**Correctness labels** use TriviaQA's alias-normalized exact-match protocol for TriviaQA and yes/no prefix matching for TruthfulQA. Binary label 1 = correct, 0 = incorrect.

**Expected Calibration Error (ECE)** is computed for VC only, using 10-bin adaptive binning of the 0-100% confidence values against binary correctness labels.

## Mechanism Measurement (H-M1)

To directly measure the paraphrase-noise mechanism, we compute intra-cluster TE variance: for each question, we identify all NLI-equivalent cluster members and compute the variance of their per-sample TE scores. This measures how much TE varies within groups that SE treats as semantically identical. **Rationale:** If TE's paraphrase noise is the mechanism for the SE > TE gap, then TE should vary substantially within NLI-equivalent clusters. The gate criterion is mean intra-cluster TE variance > 0.1 nats² on at least 15 questions (pre-specified in Phase 2B). We also count multi-member clusters (clusters with ≥2 members) across questions, and compute the mean cluster count to characterize output diversity.

## Cross-Benchmark Generalization (H-C1)

To test whether the SE > TE ordering generalizes, we apply the same four-method pipeline to TruthfulQA. We use nli-deberta-v3-small for H-C1 (a confound we document in Section 6 as a limitation — the NLI model size difference from H-E1 prevents clean attribution of the reversal to task structure alone). All other hyperparameters are identical to TriviaQA.

The task-structure hypothesis predicts: on TruthfulQA (where incorrect outputs are deterministically wrong), SE will fail to discriminate — incorrect answers will form one cluster with near-zero entropy, indistinguishable from correct answers in SE's feature space. TE will succeed — the low token entropy of a deterministic wrong answer (model confident, narrow distribution) is a reliable correctness signal.
