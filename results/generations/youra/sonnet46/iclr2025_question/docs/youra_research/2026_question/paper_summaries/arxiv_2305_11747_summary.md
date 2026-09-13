---
source_paper: "arxiv_2305_11747.md"
generated_at: "2026-03-16T14:06:16.572079"
model: "gpt-4o-mini"
summary_chars: 6009
---

# HaluEval: A Large-Scale Hallucination Evaluation Benchmark for Large Language Models

## Key Metadata
- **Authors:** Junyi Li et al.
- **Year:** 2023
- **Venue:** arXiv
- **Core Contribution:** Introduction of the HaluEval benchmark for evaluating hallucination in large language models, encompassing a large dataset of generated and human-annotated hallucinated samples.

## Section Summaries

### Abstract
User Query Retrieve the oldest photo of a cat

Large language models (LLMs), such as ChatGPT, are prone to generate hallucinations, i.e., content that conflicts with the source or cannot be verified by the factual knowledge. To understand what types of content and to which extent LLMs are apt to hallucinate, we introduce the Hallucination Evaluation benchmark for Large Language Models (HaluEval), a large collection of generated and human-annotated hallucinated samples for evaluating the performance of LLMs in recognizing hallucination. To generate these samples automatically, we propose a two-stage framework, i.e., sampling-then-filtering. Besides, we hire some human labelers to annotate the hallucinations in ChatGPT responses. The empirical results suggest that ChatGPT is likely to generate hallucinated content related to specific topics by fabricating unverifiable information (i.e., about 19.5% responses). Moreover, existing LLMs face great challenges in recognizing the hallucinations in texts. However, our experiments also prove that providing external knowledge or adding reasoning steps can help LLMs recognize hallucinations. Our benchmark can be accessed at https://github.com/RUCAIBox/HaluEval.

### Introduction & Motivation
The introduction highlights the critical issue of hallucination in LLMs, which generates content that can be factually incorrect, presenting a significant risk in real-world applications. The paper notes that previous efforts have primarily focused on understanding the causes of hallucination in smaller language models but fails to analyze the extent and types applicable to larger models like ChatGPT. The authors aim to fill this gap by creating the HaluEval benchmark, comprising 35,000 user queries with LLM responses, to assess hallucination occurrences and contribute to safer LLM deployment.

### Methodology
HaluEval employs a **two-stage sampling-then-filtering process** to create hallucinated samples effectively:

1. **Diverse Hallucination Sampling**: 
   - Uses ChatGPT for generating responses based on user queries from the Alpaca dataset. Two distinct sampling instructions are utilized:
     - **One-pass Instruction**: Direct prompts result in hallucinated answers.
     - **Conversational Instruction**: Gradual learning from sequential parts of the instruction structure enhances understanding and generates varied outputs.

2. **High-Quality Hallucination Filtering**:
   - Selected responses are filtered to retain only those that resemble factual answers yet diverge significantly. Human annotators evaluate whether ChatGPT's response contains hallucinations by marking spans of unverifiable information (e.g., “the oldest photo of a cat” details).

Each sample is categorized as either hallucinated or factual, and spans are annotated using agreement from multiple human labelers, achieving a Fleiss's Kappa score of 0.811, indicating strong reliability.

Key hyperparameters during generation include:
- **Temperature**: 1.0 for sampling, 0 for evaluation.
- **Maximum tokens**: Capped at 256.
- Various hallucination patterns are defined across task domains (QA, dialogue, summarization).

The benchmark enables researchers to evaluate LLMs effectively and understand the hallucination types they commonly generate.

### Experiments & Results
The evaluation employed multiple LLMs, including ChatGPT, GPT-3, Claude 1 and 2, alongside open-source models like Alpaca, to test hallucination identification:

- **Datasets**: HaluEval comprises 35,000 samples across three tasks (QA, dialogue, summarization).
- **Metrics**: Accuracy in recognizing hallucinations was assessed, revealing substantial shortcomings:
  - ChatGPT achieved only **62.59%** accuracy in QA and **58.53%** in summarization.
  - The accuracy varied significantly across models, indicating a systemic issue with underlying LLM architectures.

Results are summarized as follows (accuracy %):

| Model | QA  | Dialogue | Summarization |
|-------|-----|----------|---------------|
| ChatGPT | 62.59 | 72.40   | 58.53         |
| Claude 1 | 69.78 | 80.42   | 70.73         |
| Dyn. GPT-3 | 60.05 | 49.65 | 49.21         |

An ablation study evaluated methods to enhance recognition, including knowledge retrieval, which notably improved QA performance from **62.59%** to **76.83%** but showed minimal effects in the dialogue context.

### Discussion & Conclusion
The authors concluded that the HaluEval benchmark illuminates the frequency and nature of hallucinations in LLM outputs. The findings underline the importance of integrating external knowledge and reasoning pathways to improve hallucination recognition. However, challenges persist due to the proximity of hallucinated outputs to factual content, emphasizing the need for ongoing research into reducing these occurrences.

## Key Contributions
- A comprehensive, annotated dataset consisting of 35,000 samples for studying hallucinations in LLMs.
- A novel two-stage approach using sampling and filtering techniques to create challenging hallucinated outputs.
- Empirical evaluation revealing the limitations of existing LLMs in identifying hallucinations, furthering ongoing discussions about reliability in AI systems.

## Potential Relevance
This work can inform the development of hypotheses surrounding the effectiveness of hallucination detection methods in LLMs, integrating findings such as the efficacy of external knowledge retrieval and reasoning techniques. The benchmark can serve as a basis for exploring mitigation strategies to enhance factual accuracy in AI-generated content.