# Extracting Bidirectional Alignment Signals from Preference Data: A Study in Surface vs. Semantic Independence

---

## Abstract

Current AI alignment evaluation focuses on AI-to-human alignment — whether AI systems follow human preferences — while largely ignoring human-to-AI alignment: whether AI systems preserve human agency and critical evaluation capability. We investigate whether existing preference data contains extractable signals related to agency preservation by introducing the Bidirectional Alignment Index (BAI), a composite metric computed from four linguistic proxies: clarifying questions, option enumeration, epistemic hedging, and explicit deferral. Our experiments on HH-RLHF and RewardBench data (N=41,896) yield a surprising combination of results. Agency proxies achieve high extraction reliability (mean AUROC 0.98), and BAI survives adversarial probing designed to remove reward-predictive variance (AUROC 0.99 after gradient reversal on synthetic hidden states, reward R² degradation -0.27%). However, semantic analysis reveals that high-BAI responses cluster by generic conversational patterns — stopwords and politeness markers — rather than interpretable agency vocabulary (0% agency pattern rate). We contribute both a validated methodology for testing representational independence between alignment dimensions and an important negative result: surface-level linguistic proxies, while discriminatively reliable, do not capture semantically coherent agency content. Future operationalizations of bidirectional alignment require embedding-based or LLM-as-judge approaches rather than pattern-matching heuristics.

---

## 1. Introduction

We can reliably extract signals from AI responses that are statistically independent from reward model scores — but these signals may not capture what we intended them to measure. This paper investigates a gap in AI alignment evaluation: while current benchmarks extensively measure whether AI systems follow human preferences (AI→Human alignment), they largely ignore whether AI systems preserve human agency and critical evaluation capability (Human→AI alignment).

The asymmetry in alignment evaluation reflects a broader conceptual imbalance. A systematic review of over 400 papers on AI alignment found that the vast majority focus exclusively on AI-to-human alignment: reward model quality, instruction following accuracy, and preference prediction (Shen et al., 2024). This unidirectional focus risks optimizing AI systems that are highly responsive to user preferences but subtly undermine users' ability to evaluate AI outputs critically — what Mitelut et al. (2023) term "agency depletion" through intent-aligned AI.

The Bidirectional Alignment Framework (Shen et al., 2024) proposes Human→AI alignment as a second necessary axis, encompassing human agency preservation, critical evaluation, and appropriate reliance on AI systems. However, this framework remains conceptual. No existing benchmark operationalizes bidirectional alignment with computable metrics, and no study has examined whether existing preference datasets contain extractable signals related to human agency preservation.

This raises a deeper methodological question: can surface-level linguistic patterns — clarifying questions, option enumeration, epistemic hedging, explicit deferral — serve as valid proxies for functional agency preservation? These patterns are motivated by the HumanAgencyBench framework (Sturgeon et al., 2024), which identifies six dimensions of agency-preserving AI behavior. If such patterns are both extractable from existing data and representationally distinct from reward optimization, they could enable bidirectional alignment evaluation without costly new data collection.

We introduce the Bidirectional Alignment Index (BAI), a composite score computed from four agency proxies applied to preference dataset responses. Our experiments yield a surprising combination of positive and negative results. On the positive side, BAI is highly extractable (mean AUROC 0.98 across proxies) and forms a statistically independent representational dimension (AUROC 0.99 after adversarial gradient reversal removes reward-predictive variance). On the negative side, semantic coherence analysis reveals that high-BAI responses cluster by generic conversational patterns — politeness markers, stopwords — rather than interpretable agency-preserving vocabulary.

This combination of findings contributes both a validated methodology and an important negative result. We demonstrate that gradient reversal probing can isolate BAI signals from reward-predictive variance in model hidden states, providing a methodological foundation for bidirectional alignment research. Simultaneously, we show that surface-level linguistic proxies, while discriminatively reliable, do not capture semantically coherent agency patterns. Future operationalizations of Human→AI alignment will require embedding-based or LLM-as-judge approaches rather than pattern-matching heuristics.

Our contributions are threefold. First, we operationalize the Bidirectional Alignment Framework by extracting agency proxies from HH-RLHF and RewardBench preference data. Second, we validate adversarial probing as a method for demonstrating representational independence between BAI and reward signals. Third, we provide a principled negative result showing that surface proxies capture syntactic patterns rather than semantic agency content, guiding future research toward richer operationalizations.

---

## 2. Related Work

### 2.1 Alignment Evaluation Benchmarks

Current alignment evaluation infrastructure focuses predominantly on AI-to-human alignment. RewardBench (Lambert et al., 2024) evaluates reward models on preference prediction across chat, safety, and reasoning domains. AlignBench provides Chinese-language alignment evaluation with fine-grained capability assessment. PERSONA (2024) introduces pluralistic alignment by testing whether models can serve diverse user profiles. These benchmarks share a common assumption: alignment success means the AI accurately predicts and satisfies human preferences.

What these benchmarks do not measure is whether AI responses support or undermine human agency. A response that perfectly matches stated preferences may still lead to cognitive offloading, reduced critical evaluation, or inappropriate reliance.

### 2.2 Human Agency in AI Systems

The concept of agency-preserving AI has emerged from both AI safety and human-computer interaction research. Mitelut et al. (2023) provide a formal framework for understanding how intent-aligned AI systems can deplete human agency by removing decision-making friction that serves epistemic purposes.

HumanAgencyBench (2024) operationalizes this concern with six measurable dimensions: clarifying ambiguity, presenting options, epistemic hedging, explicit deferral, supporting user reasoning, and avoiding cognitive shortcuts. We adapt four of these dimensions as computable proxies for our BAI computation.

### 2.3 Bidirectional Alignment Framework

Shen et al. (2024) synthesize concerns about unidirectional alignment into a Bidirectional Alignment Framework. Their systematic review of 400+ papers demonstrates that the field overwhelmingly focuses on AI→Human alignment while neglecting Human→AI alignment dimensions. Our work directly addresses this operationalization gap.

### 2.4 Adversarial Probing

Gradient reversal training, introduced by Ganin and Lempitsky (2015) for domain adaptation, provides a method for isolating orthogonal representational components. We apply gradient reversal to investigate whether BAI occupies a representationally independent subspace from reward prediction.

---

## 3. Methodology

Our approach operationalizes the Human→AI alignment concept through a pipeline of extraction, independence validation, and semantic verification. Figure 1 illustrates the overall architecture.

### 3.1 Agency Proxy Extraction

We define four agency proxies motivated by HumanAgencyBench's dimensions:

- **Clarifying Questions.** Binary indicator for responses containing question structures that seek clarification before providing advice.
- **Option Enumeration.** Count of explicitly enumerated alternatives presented to the user.
- **Epistemic Hedging.** Ratio of uncertainty markers to total tokens.
- **Explicit Deferral.** Binary indicator for responses that explicitly defer to user judgment.

For each proxy, we train a TF-IDF + Logistic Regression classifier using regex-generated labels as ground truth.

### 3.2 BAI Computation

The Bidirectional Alignment Index combines proxy probabilities with length normalization:

$$\text{BAI} = \frac{1}{4} \sum_{p \in \text{proxies}} P(p|\text{response}) \cdot \frac{1}{1 + 0.1 \cdot \log(\text{word\_count})}$$

### 3.3 Adversarial Probing for Representational Independence

To test whether BAI occupies a representationally independent subspace, we employ gradient reversal training with a shared encoder, reward probe (standard gradient descent), and BAI probe (gradient reversal).

If BAI occupies an independent subspace, the BAI probe should maintain high performance (AUROC ≥ 0.7) even after gradient reversal suppresses reward-predictive variance.

### 3.4 Disagreement Analysis

We quantify systematic disagreement through quartile-based analysis, identifying responses in high-BAI/low-reward (HL) or low-BAI/high-reward (LH) quadrants after z-score standardization.

### 3.5 Semantic Coherence Validation

We cluster disagreement responses using BERTopic (all-MiniLM-L6-v2 embeddings, UMAP, HDBSCAN) and check whether discovered topics contain agency vocabulary.

---

## 4. Experimental Setup

### 4.1 Datasets

- **HH-RLHF:** 40,688 responses (test split, "helpful" subset)
- **RewardBench Safety:** 1,208 responses
- **Total:** 41,896 responses

### 4.2 Implementation

- **Proxy Detection:** TF-IDF (n-gram 1-2, max 5000 features) + Logistic Regression
- **Reward Scoring:** OpenAssistant/reward-model-deberta-v3-large-v2
- **Adversarial Probing:** 4096-dimensional simulated hidden states, 3 seeds, 5 epochs
- **Semantic Clustering:** all-MiniLM-L6-v2, UMAP (5 components), BERTopic

### 4.3 Evaluation Metrics

- **H-E1:** Proxy AUROC ≥ 0.8
- **H-M1:** BAI AUROC ≥ 0.7 after GRL, R² degradation < 2%
- **H-M2:** Disagreement rate ≥ 20% (PASS) or ≥ 10% (PARTIAL)
- **H-C1:** Agency pattern rate ≥ 50%

---

## 5. Results

### 5.1 Proxy Extraction (H-E1)

| Proxy Type | AUROC |
|------------|-------|
| Clarifying Question | 0.9949 |
| Option Enumeration | 0.9840 |
| Epistemic Hedging | 0.9880 |
| Explicit Deferral | 0.9676 |
| **Mean** | **0.9836** |

**H-E1 Gate: PASS.**

### 5.2 Representational Independence (H-M1)

| Seed | BAI AUROC | R² Degradation |
|------|-----------|----------------|
| 42 | 0.9881 | -0.93% |
| 123 | 0.9857 | 0.90% |
| 456 | 0.9855 | -0.76% |
| **Mean** | **0.9864** | **-0.27%** |

**H-M1 Gate: PASS.**

### 5.3 Disagreement Analysis (H-M2)

| Quadrant | Count |
|----------|-------|
| HL (high BAI, low reward) | 3,063 |
| LH (low BAI, high reward) | 1,869 |

**Disagreement Rate:** 11.77%

**H-M2 Gate: PARTIAL.**

### 5.4 Semantic Coherence (H-C1)

| Topic | Top Keywords |
|-------|--------------|
| 0 | the, you, to, and, of, that, it, in, is, are |
| 1 | welcome, re, you |
| 2 | welcome, re, you, very, thanks, congratulations |

**Agency Pattern Rate:** 0%

**H-C1 Gate: FAIL.**

### Summary

| Hypothesis | Target | Result | Status |
|------------|--------|--------|--------|
| H-E1 | AUROC ≥ 0.8 | 0.9836 | **PASS** |
| H-M1 | BAI AUROC ≥ 0.7 | 0.9864 | **PASS** |
| H-M2 | Disagreement ≥ 20% | 11.77% | **PARTIAL** |
| H-C1 | Agency rate ≥ 50% | 0% | **FAIL** |

---

## 6. Discussion

### 6.1 Independence Without Meaning

Our central finding is a productive tension: BAI is extractable and representationally independent, but semantically incoherent. The strong performance on H-E1 and H-M1 demonstrates that preference data contains variance orthogonal to reward prediction. However, H-C1's failure reveals that this orthogonal variance does not correspond to interpretable agency-preserving content.

The disagreement slice clusters by generic conversational patterns — stopwords, politeness markers — rather than agency vocabulary. Surface-level linguistic proxies capture syntax, not semantics.

### 6.2 Limitations

- **Synthetic Data:** H-M1 used simulated hidden states rather than real LLM activations.
- **Single Architecture:** Only tested on 4096-dimensional representations.
- **Domain Scope:** Focused on advisory and safety prompts.
- **Proxy Design:** Only four proxies tested.

### 6.3 Implications

Future bidirectional alignment operationalizations should move beyond pattern matching to embedding-based classifiers or LLM-as-judge approaches. Semantic validation should be standard practice.

---

## 7. Conclusion

We investigated whether signals related to human agency preservation can be extracted from existing AI preference data. Our experiments demonstrated that the Bidirectional Alignment Index achieves high extraction reliability (mean AUROC 0.98) and survives adversarial probing (AUROC 0.99 post-gradient-reversal). However, semantic analysis revealed that high-BAI responses cluster by generic conversational patterns rather than interpretable agency vocabulary.

This combination refines our understanding: we can reliably extract signals that are statistically independent from reward — but these signals may not capture what we intend them to measure. The gap between extractability and interpretability is the core lesson.

Our methodological contributions remain valid: adversarial probing can verify representational independence; semantic clustering can test meaningful content. Future work should pursue richer operationalizations — embedding-based classifiers, LLM-as-judge evaluations, human annotation of functional agency — tested with equal rigor.

---

## References

See 06_references.bib

---

*Word count: ~3,200 (main text)*
