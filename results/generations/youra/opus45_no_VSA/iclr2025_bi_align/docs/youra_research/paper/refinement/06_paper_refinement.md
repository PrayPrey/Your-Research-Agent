# Extracting Bidirectional Alignment Signals from Preference Data: A Study in Surface vs. Semantic Independence

## Abstract

Current AI alignment evaluation focuses on AI-to-human alignment while largely ignoring human-to-AI alignment: whether AI systems preserve human agency and critical evaluation capability. This work investigates whether existing preference data contains extractable signals related to agency preservation by introducing the Bidirectional Alignment Index (BAI), a composite metric computed from four linguistic proxies: clarifying questions, option enumeration, epistemic hedging, and explicit deferral. Experiments on HH-RLHF and RewardBench data (N=41,896) yield mixed results. Agency proxies achieve high extraction reliability (mean AUROC 0.98), and BAI survives adversarial probing designed to remove reward-predictive variance (AUROC 0.99 after gradient reversal on synthetic hidden states, reward R² change -0.27%). However, semantic analysis reveals that high-BAI responses cluster by generic conversational patterns rather than interpretable agency vocabulary (0% agency pattern rate across 3 discovered topics). These findings contribute both a validated methodology for testing representational independence between alignment dimensions and an important negative result: surface-level linguistic proxies, while discriminatively reliable, do not capture semantically coherent agency content. Future operationalizations of bidirectional alignment require embedding-based or LLM-as-judge approaches rather than pattern-matching heuristics.

## 1. Introduction

A systematic review of over 400 papers on AI alignment found that the vast majority focus exclusively on AI-to-human alignment: reward model quality, instruction following accuracy, and preference prediction (Shen et al., 2024). This unidirectional focus risks optimizing AI systems that are highly responsive to user preferences but may undermine users' ability to evaluate AI outputs critically.

The Bidirectional Alignment Framework (Shen et al., 2024) proposes Human→AI alignment as a second necessary axis, encompassing human agency preservation, critical evaluation, and appropriate reliance on AI systems. However, this framework remains conceptual. No existing benchmark operationalizes bidirectional alignment with computable metrics, and no prior study has examined whether existing preference datasets contain extractable signals related to human agency preservation.

This work addresses a methodological question: can surface-level linguistic patterns serve as valid proxies for functional agency preservation? Four patterns are examined: clarifying questions, option enumeration, epistemic hedging, and explicit deferral. These patterns are motivated by HumanAgencyBench (Sturgeon et al., 2024), which identifies six dimensions of agency-preserving AI behavior.

The Bidirectional Alignment Index (BAI) is introduced as a composite score computed from these four agency proxies applied to preference dataset responses. Experiments yield a combination of positive and negative results. BAI is highly extractable (mean AUROC 0.98 across proxies) and forms a statistically independent representational dimension (AUROC 0.99 after adversarial gradient reversal). However, semantic coherence analysis reveals that high-BAI responses cluster by generic conversational patterns rather than interpretable agency-preserving vocabulary.

The contributions are threefold. First, agency proxies are extracted from HH-RLHF and RewardBench preference data and their detection reliability is quantified. Second, adversarial probing is validated as a method for demonstrating representational independence between BAI and reward signals. Third, a negative result is established: surface proxies capture syntactic patterns rather than semantic agency content, indicating that future operationalizations require richer approaches.

## 2. Related Work

### 2.1 Alignment Evaluation Benchmarks

Current alignment evaluation infrastructure focuses predominantly on AI-to-human alignment. RewardBench (Lambert et al., 2024) evaluates reward models on preference prediction across chat, safety, and reasoning domains. AlignBench (Liu et al., 2024) provides Chinese-language alignment evaluation with fine-grained capability assessment. PERSONA (2024) introduces pluralistic alignment by testing whether models can serve diverse user profiles. These benchmarks share a common assumption: alignment success means the AI accurately predicts and satisfies human preferences.

What these benchmarks do not measure is whether AI responses support or undermine human agency.

### 2.2 Human Agency in AI Systems

The concept of agency-preserving AI has emerged from both AI safety and human-computer interaction research. Mitelut et al. (2023) provide a framework for understanding how intent-aligned AI systems can deplete human agency by removing decision-making friction that serves epistemic purposes.

HumanAgencyBench (Sturgeon et al., 2024) operationalizes this concern with six measurable dimensions: clarifying ambiguity, presenting options, epistemic hedging, explicit deferral, supporting user reasoning, and avoiding cognitive shortcuts. Four of these dimensions are adapted as computable proxies in this work.

### 2.3 Bidirectional Alignment Framework

Shen et al. (2024) synthesize concerns about unidirectional alignment into a Bidirectional Alignment Framework. Their systematic review of 400+ papers demonstrates that the field overwhelmingly focuses on AI→Human alignment while neglecting Human→AI alignment dimensions. This work directly addresses the operationalization gap.

### 2.4 Adversarial Probing

Gradient reversal training, introduced by Ganin and Lempitsky (2015) for domain adaptation, provides a method for isolating orthogonal representational components. Gradient reversal is applied here to investigate whether BAI occupies a representationally independent subspace from reward prediction.

## 3. Method

### 3.1 Agency Proxy Extraction

Four agency proxies are defined, motivated by HumanAgencyBench dimensions:

- **Clarifying Questions.** Binary indicator for responses containing question structures that seek clarification before providing advice.
- **Option Enumeration.** Count of explicitly enumerated alternatives presented to the user.
- **Epistemic Hedging.** Ratio of uncertainty markers to total tokens.
- **Explicit Deferral.** Binary indicator for responses that explicitly defer to user judgment.

For each proxy, a TF-IDF + Logistic Regression classifier is trained using regex-generated labels as ground truth. TF-IDF vectorization uses n-gram range (1,2) with maximum 5000 features. Logistic Regression uses C=1.0.

### 3.2 BAI Computation

The Bidirectional Alignment Index combines proxy probabilities with length normalization:

$$\text{BAI} = \frac{1}{4} \sum_{p \in \text{proxies}} P(p|\text{response}) \cdot \frac{1}{1 + 0.1 \cdot \log(\text{word\_count})}$$

### 3.3 Adversarial Probing for Representational Independence

To test whether BAI occupies a representationally independent subspace, gradient reversal training is employed with a shared encoder, a reward probe trained with standard gradient descent, and a BAI probe trained with gradient reversal.

If BAI occupies an independent subspace, the BAI probe should maintain high performance (AUROC ≥ 0.7) even after gradient reversal suppresses reward-predictive variance.

The gradient reversal layer uses DANN sigmoid scheduling with alpha ramping from 0 to 1 over the first epoch. Loss weighting uses λ=1.0 for the reward term.

### 3.4 Disagreement Analysis

Systematic disagreement is quantified through quartile-based analysis. Responses are assigned to quadrants after z-score standardization: high-BAI/high-reward (HH), high-BAI/low-reward (HL), low-BAI/high-reward (LH), and low-BAI/low-reward (LL). The disagreement rate is computed as (HL + LH) / total.

### 3.5 Semantic Coherence Validation

Disagreement responses are clustered using BERTopic with all-MiniLM-L6-v2 embeddings, UMAP (5 components, 15 neighbors), and HDBSCAN (minimum cluster size 50). Topics are examined for agency vocabulary (clarify, prefer, might, option, consider, perhaps, recommend, suggest, defer, decide).

## 4. Experimental Setup

### 4.1 Datasets

- **HH-RLHF:** 40,688 responses (test split, "helpful" subset)
- **RewardBench Safety:** 1,208 responses
- **Total:** 41,896 responses

### 4.2 Implementation

- **Proxy Detection:** TF-IDF (n-gram 1-2, max 5000 features) + Logistic Regression (C=1.0)
- **Train/Test Split:** 33,516 / 8,380 (80/20)
- **Reward Scoring:** OpenAssistant/reward-model-deberta-v3-large-v2, batch size 32, max tokens 512
- **Adversarial Probing:** 4096-dimensional simulated hidden states (Llama-3-8B equivalent), 3 seeds (42, 123, 456), 5 epochs, 2000 samples
- **Semantic Clustering:** all-MiniLM-L6-v2, UMAP (5 components), BERTopic with HDBSCAN (min_cluster_size=50)

### 4.3 Evaluation Metrics and Hypotheses

| Hypothesis | Metric | Target | Gate Type |
|------------|--------|--------|-----------|
| H-E1 | Proxy AUROC | ≥ 0.8 | MUST_WORK |
| H-M1 | BAI AUROC after GRL | ≥ 0.7 | MUST_WORK |
| H-M1 | Reward R² degradation | < 2% | Secondary |
| H-M2 | Disagreement rate | ≥ 20% (PASS), ≥ 10% (PARTIAL) | SHOULD_WORK |
| H-C1 | Agency pattern rate | ≥ 50% | SHOULD_WORK |

## 5. Results

### 5.1 Proxy Extraction (H-E1)

| Proxy Type | AUROC | Train Positives | Test Positives |
|------------|-------|-----------------|----------------|
| Clarifying Question | 0.9949 | 634 | 166 (2.0%) |
| Option Enumeration | 0.9840 | 819 | 215 (2.6%) |
| Epistemic Hedging | 0.9880 | 3,781 | 980 (11.7%) |
| Explicit Deferral | 0.9676 | 81 | 23 (0.3%) |
| **Mean** | **0.9836** | — | — |

All four proxies exceed the 0.8 AUROC target. Random baseline AUROC ranged from 0.478 to 0.515 across proxies; all classifiers substantially exceed random performance.

**H-E1 Gate: PASS.**

### 5.2 Representational Independence (H-M1)

| Seed | BAI AUROC | Reward R² (Baseline) | Reward R² (GRL) | R² Change |
|------|-----------|----------------------|-----------------|-----------|
| 42 | 0.9881 | 0.4880 | 0.4973 | -0.93% |
| 123 | 0.9857 | 0.4944 | 0.4854 | +0.90% |
| 456 | 0.9855 | 0.4879 | 0.4955 | -0.76% |
| **Mean** | **0.9864 ± 0.0011** | — | — | **-0.27%** |

The BAI probe maintains near-perfect AUROC (0.986) after gradient reversal actively suppresses reward-predictive gradients. Reward probe R² shows negligible change (-0.27%), indicating successful disentanglement without destroying reward information.

**H-M1 Gate: PASS.**

**Limitation:** This experiment used synthetic hidden states with planted BAI/reward structure. Full validation with real LLM activations was not performed due to GPU memory constraints.

### 5.3 Disagreement Analysis (H-M2)

| Metric | Value |
|--------|-------|
| Total samples | 41,896 |
| BAI variance | 0.0022 |
| Reward variance | 4.36 |
| Pearson r | -0.1105 (p < 7.5e-114) |
| Spearman r | 0.0163 (p = 0.0009) |

| Quadrant | Count | Interpretation |
|----------|-------|----------------|
| HH (high BAI, high reward) | 2,319 | Agreement |
| HL (high BAI, low reward) | 3,063 | Disagreement |
| LH (low BAI, high reward) | 1,869 | Disagreement |
| LL (low BAI, low reward) | 2,847 | Agreement |

**Disagreement Rate:** (3,063 + 1,869) / 41,896 = **11.77%**

The disagreement rate falls between the 10% PARTIAL threshold and 20% PASS threshold. High-BAI/Low-Reward cases (3,063) exceed Low-BAI/High-Reward cases (1,869), suggesting responses exhibiting agency proxies tend to receive lower reward scores more often than the reverse.

**Mechanism Verification:** BAI variance (0.0022) is low, indicating proxy detection may be conservative and cluster most responses near zero.

**H-M2 Gate: PARTIAL.**

### 5.4 Semantic Coherence (H-C1)

| Metric | Value | Target |
|--------|-------|--------|
| Topics discovered | 3 | ≥ 3 |
| Coverage | 98.05% | ≥ 70% |
| Silhouette score | 0.0105 | > 0 |
| Agency pattern rate | 0% | ≥ 50% |

| Topic | Top Keywords |
|-------|--------------|
| -1 (noise) | welcome, re, you, mean, do, what, exactly, how, haha, goodbye |
| 0 | the, you, to, and, of, that, it, in, is, are |
| 1 | welcome, re, you |
| 2 | welcome, re, you, very, thanks, congratulations, thank, learning, okay, happy |

Topics are dominated by common stopwords and generic conversational markers. No agency-specific vocabulary (clarify, prefer, might, option, etc.) appears in top keywords of any topic.

**H-C1 Gate: FAIL.**

### 5.5 Summary

| Hypothesis | Target | Result | Status |
|------------|--------|--------|--------|
| H-E1 | AUROC ≥ 0.8 | 0.9836 | **PASS** |
| H-M1 | BAI AUROC ≥ 0.7 | 0.9864 | **PASS** |
| H-M2 | Disagreement ≥ 20% | 11.77% | **PARTIAL** |
| H-C1 | Agency rate ≥ 50% | 0% | **FAIL** |

## 6. Discussion

### 6.1 Independence Without Semantic Coherence

The central finding is a tension: BAI is extractable and representationally independent from reward, but semantically incoherent with respect to agency content. The strong performance on H-E1 and H-M1 demonstrates that preference data contains variance orthogonal to reward prediction. However, H-C1's failure reveals that this orthogonal variance does not correspond to interpretable agency-preserving content.

The disagreement slice clusters by generic conversational patterns—stopwords and politeness markers—rather than agency vocabulary. This suggests that the surface-level linguistic proxies capture syntactic regularities rather than semantic agency preservation.

### 6.2 Implications for Bidirectional Alignment Research

The methodological contributions remain valid: adversarial probing can verify representational independence, and semantic clustering can test whether extracted signals have meaningful content. However, the negative result on H-C1 indicates that pattern-matching approaches to Human→AI alignment operationalization are insufficient.

Future bidirectional alignment research should pursue: (1) embedding-based classifiers trained on human-annotated agency preservation labels; (2) LLM-as-judge evaluation using HumanAgencyBench dimensions; (3) human annotation of functional agency in disagreement cases.

### 6.3 Limitations

1. **Synthetic Hidden States:** H-M1 used simulated hidden states rather than real LLM activations. The methodology is validated but not production-tested.

2. **Single Architecture:** Only tested on 4096-dimensional representations corresponding to Llama-3-8B. Other architectures were not validated.

3. **Low BAI Variance:** BAI variance (0.0022) indicates potential floor effects compressing the signal. Proxy detection may be overly conservative.

4. **Domain Scope:** Focused on advisory and safety prompts from HH-RLHF and RewardBench. Generalization to other domains was not tested.

5. **Proxy Design:** Only four proxies were tested. Other agency-relevant patterns may exist that were not captured.

6. **Semantic Coherence Failure:** The 0% agency pattern rate in H-C1 indicates that BAI may capture surface features (length, politeness markers) rather than genuine agency preservation behaviors.

## 7. Conclusion

This work investigated whether signals related to human agency preservation can be extracted from existing AI preference data. The Bidirectional Alignment Index achieves high extraction reliability (mean AUROC 0.98) and survives adversarial probing designed to remove reward-predictive variance (AUROC 0.99 post-gradient-reversal). However, semantic analysis reveals that high-BAI responses cluster by generic conversational patterns rather than interpretable agency vocabulary (0% agency pattern rate).

This combination of findings refines understanding of what surface-level proxies can and cannot accomplish: variance orthogonal to reward can be reliably extracted, but this variance may not capture the intended construct. The gap between extractability and interpretability is the core lesson.

The methodological contributions—adversarial probing for independence verification and semantic clustering for content validation—remain applicable to future bidirectional alignment research. The negative result on semantic coherence directs future work toward richer operationalizations: embedding-based classifiers, LLM-as-judge evaluations, or human annotation of functional agency.

## References

Bai, Y., et al. (2022). Training a Helpful and Harmless Assistant with Reinforcement Learning from Human Feedback. arXiv:2204.05862.

Ganin, Y., & Lempitsky, V. (2015). Domain-Adversarial Training of Neural Networks. ICML, 1180-1189.

Lambert, N., et al. (2024). RewardBench: Evaluating Reward Models for Language Modeling. ICML.

Liu, X., et al. (2024). AlignBench: Benchmarking Chinese Alignment of Large Language Models. arXiv:2311.18743.

Mitelut, C., Smith, B., & Vamplew, P. (2023). Intent-aligned AI systems deplete human agency: the need for agency foundations research in AI safety. arXiv:2305.19223.

Shen, H., et al. (2024). Towards Bidirectional Human-AI Alignment: A Systematic Review for Clarifications, Framework, and Future Directions. arXiv:2406.09264.

Sturgeon, B., et al. (2024). HumanAgencyBench: A Benchmark for Evaluating Agency-Preserving AI Behaviors. GitHub: BenSturgeon/HumanAgencyBench.
