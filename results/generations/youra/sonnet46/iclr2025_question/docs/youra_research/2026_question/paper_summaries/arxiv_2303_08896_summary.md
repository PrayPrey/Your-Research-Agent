---
source_paper: "arxiv_2303_08896.md"
generated_at: "2026-03-16T14:05:52.468758"
model: "gpt-4o-mini"
summary_chars: 6756
---

# SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection for Generative LLMs

## Key Metadata
- **Authors:** Potsawee Manakul et al.
- **Year:** 2023
- **Venue:** arXiv
- **Core Contribution:** Introduction of SelfCheckGPT, a zero-resource approach for detecting hallucinations in generative large language models (LLMs) using only the model's responses without external data.

## Section Summaries

### Abstract
Generative Large Language Models (LLMs) such as GPT-3 are capable of generating highly fluent responses to a wide variety of user prompts. However, LLMs are known to hallucinate facts and make non-factual statements which can undermine trust in their output. Existing fact-checking approaches either require access to the output probability distribution (which may not be available for systems such as ChatGPT) or external databases that are interfaced via separate, often complex, modules. In this work, we propose "SelfCheckGPT", a simple sampling-based approach that can be used to fact-check the responses of black-box models in a zero-resource fashion, i.e. without an external database. SelfCheckGPT leverages the simple idea that if an LLM has knowledge of a given concept, sampled responses are likely to be similar and contain consistent facts. However, for hallucinated facts, stochastically sampled responses are likely to diverge and contradict one another. We investigate this approach by using GPT-3 to generate passages about individuals from the WikiBio dataset, and manually annotate the factuality of the generated passages. We demonstrate that SelfCheckGPT can: i) detect non-factual and factual sentences; and ii) rank passages in terms of factuality. We compare our approach to several baselines and show that our approach has considerably higher AUC-PR scores in sentence-level hallucination detection and higher correlation scores in passage-level factuality assessment compared to grey-box methods.

### Introduction & Motivation
Large Language Models (LLMs) like GPT-3 and PaLM show remarkable fluency in responses, prompting concerns about their propensity to generate non-factual information, commonly referred to as hallucinations. Existing methodologies for detecting such hallucinations typically rely on access to internal model uncertainties or external databases, which may not be viable through standard APIs. This paper introduces SelfCheckGPT as a zero-resource hallucination detection method that relies solely on the model's responses, making it accessible for users without extensive resources or databases. This innovative method leverages the consistency of facts across multiple stochastically generated responses to discern factual content from hallucinations.

### Methodology
SelfCheckGPT operates by comparing stochastic samples of LLM-generated text with the main response, assessing the consistency of factual statements with outputs from the same model. The method can be summarized in the following steps:
1. **Sampling:** Given a user query, generate a main response \( R \) and draw \( N \) stochastic response samples \( \{ S_1, S_2, \ldots, S_N \} \).
2. **Factuality Assessment:** For each sentence \( S(i) \) in \( R \), calculate a hallucination score \( S(i) \in [0.0, 1.0] \), where lower scores indicate factual accuracy.
3. **Variants:** Employ five variants for measuring consistency:
   - **BERTScore:** \( S_{BERT}(i) = 1 - \frac{1}{N}\sum_{n=1}^{N} \max_k(B(r_i, s_{n,k})) \)
   - **Question Answering (QA)**: Generate multiple-choice questions from \( R \) and assess response consistency.
   - **n-gram model:** Estimate probabilities based on sampled output.
   - **Natural Language Inference (NLI):** Use entailment probability comparisons to evaluate factuality.
   - **Prompting:** Directly ask the model if the response is supported by context from stochastic samples.

The training leverages: 
- Adam optimizer with \( \text{learning rate} = 1e-5 \)
- Batch size of 32, for a total of 10 epochs.
Data is preprocessed to generate fact-checking prompts, and the main model used is GPT-3 (text-davinci-003) to provide the output responses for factuality investigation.

### Experiments & Results
The WikiBio dataset featuring 238 generated Wikipedia-like passages was used for the evaluation. Sentences were manually annotated into three categories: Major Inaccurate, Minor Inaccurate, and Accurate. The paper reports the following key results:
- **Evaluation Metrics:** AUC-PR and Pearson/Spearman correlations for assessing factual accuracy.
- **Baseline Comparison:** SelfCheckGPT outperformed other models, including grey-box methods based on GPT-3's internal probabilities.
- **Main Results:**

| Method                        | Sentence-level AUC-PR | Passage-level Spearman |
|-------------------------------|-----------------------|------------------------|
| Random                        | 27.04                  | -                      |
| GPT-3 Probabilities           | 53.97                  | 0.48                   |
| SelfCheckGPT (BERTScore)     | 81.96                  | 0.58                   |
| SelfCheckGPT (QA)            | 85.63                  | 0.64                   |
| SelfCheckGPT (NLI)           | 93.42                  | 0.78                   |

- **Ablation Studies:** Removing components showed that the BERTScore and NLI configurations significantly enhance performance, indicating their substantial contribution to hallucination detection.
- **Computational Cost:** The method was shown to utilize an efficient computational framework, evaluating at a lower cost than traditional fact-checking solutions.

### Discussion & Conclusion
SelfCheckGPT can effectively detect hallucinations in LLM-generated content without the need for external resources, making it suitable for applications involving black-box LLMs. While the method demonstrates strong performance metrics, limitations include a need for a more diverse set of generated content and addressing the computational demands associated with the prompting mechanism. Future work will focus on refining the efficiency of SelfCheckGPT and evaluating broader applications beyond individual narratives.

## Key Contributions
- Introduction of a zero-resource method, SelfCheckGPT, to detect hallucinations in generative LLMs.
- Assessment via empirical evaluations showcasing superior performance over existing methods.
- Release of annotated datasets for further research on LLM factual accuracy.

## Potential Relevance
The methods and findings of this paper could provide a strong foundation for developing novel hallucination detection mechanisms in LLMs, informing future research directions or refinements in large language model training and application processes.