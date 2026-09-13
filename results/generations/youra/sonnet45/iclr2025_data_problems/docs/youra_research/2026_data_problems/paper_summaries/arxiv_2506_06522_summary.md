---
source_paper: "arxiv_2506_06522.md"
generated_at: "2026-03-17T07:42:14.952598"
model: "gpt-4o-mini"
summary_chars: 6929
---

# Fixing It in Post: LLM Post-Training Data Quality

## Key Metadata
- **Authors:** Aladin Djuhera et al.
- **Year:** 2025
- **Venue:** 39th Conference on Neural Information Processing Systems (NeurIPS 2025) Track on Datasets and Benchmarks
- **Core Contribution:** This paper introduces TuluTalk, a curated dataset that improves upon two prior post-training datasets, Tulu and SmolTalk, by leveraging detailed quality annotations.

## Section Summaries

### Abstract
Recent work on large language models (LLMs) has increasingly focused on post-training and alignment with datasets curated to enhance instruction following, world knowledge, and specialized skills. However, most post-training datasets used in leading open- and closed-source LLMs remain inaccessible to the public, with limited information about their construction process. This lack of transparency has motivated the recent development of open-source post-training corpora. While training on these open alternatives can yield performance comparable to that of leading models, systematic comparisons remain challenging due to the significant computational cost of conducting them rigorously at scale, and are therefore largely absent. As a result, it remains unclear how specific samples, task types, or curation strategies influence downstream performance when assessing data quality. In this work, we conduct the first comprehensive side-by-side analysis of two prominent open post-training datasets: Tulu-3-SFT-Mix and SmolTalk. Using the Magpie framework, we annotate each sample with detailed quality metrics, including turn structure (single-turn vs. multi-turn), task category, input quality, and response quality, and we derive statistics that reveal structural and qualitative similarities and differences between the two datasets. Based on these insights, we design a principled curation recipe that produces a new data mixture, TuluTalk, which contains 14% fewer samples than either source dataset while matching or exceeding their performance on key benchmarks. Our findings offer actionable insights for constructing more effective post-training datasets that improve model performance within practical resource limits. To support future research, we publicly release both the annotated source datasets and our curated TuluTalk mixture.

### Introduction & Motivation
The introduction highlights the increasing complexity of large language models necessitating larger datasets for effective training. While pre-training on vast, general-purpose corpora is established, the focus is shifting toward post-training methods like supervised fine-tuning (SFT) and reinforcement learning (RL). The paper identifies significant challenges due to proprietary post-training datasets that limit public scrutiny and insights into their curation processes. By systematically comparing open-source SFT mixtures—Tulu and SmolTalk—the authors aim to illuminate how specific dataset features affect LLM performance, ultimately establishing a foundation for constructing effective post-training datasets.

### Methodology
The paper compares two open-source post-training datasets—Tulu-3-SFT-Mix and SmolTalk—using the Magpie framework for quality annotation. Each dataset is analyzed regarding structural and qualitative aspects, with a focus on the following core techniques and processes:

1. **Annotation Pipeline:** The Magpie framework annotates data samples for multiple dimensions, including turn structure (single-turn vs. multi-turn), task category, input quality (rated from "very poor" to "excellent"), response quality (instruct reward), and safety assessments. A total of 12 task categories are identified.

2. **Data Mixtures:** The study begins by curating high-quality samples from Tulu and SmolTalk, resulting in the creation of TuluTalk. This mixture is 14% smaller than Tulu and 23% smaller than SmolTalk but enhances performance on key benchmarks.

3. **Training Parameters:** Fine-tuning was conducted with Llama-3.1-8B and SmolLM2-1.7B models on Tulu, SmolTalk, and TuluTalk datasets, using the same experimental setup to ensure comparability.

4. **Quality- and Task-Aware Curation:** The final dataset (TuluTalk) selects multi-turn samples with excellent input quality (score of 5) and single-turn samples with higher-than-median scores, resulting in a curated mixture focused on quality and task diversity.

5. **Key Equations:** There are no explicit mathematical equations; instead, the research focuses on qualitative metrics and performance scores across various benchmarks.

### Experiments & Results
The experiments involve a comprehensive evaluation of the Tulu and SmolTalk datasets as follows:

- **Datasets:** Tulu features approximately 0.94 million pairs across seven domains, while SmolTalk offers about 1.04 million samples focused on conversational depth.
  
- **Benchmarks:** Performance is assessed using 14 benchmarks from popular Open LLM Leaderboards, including knowledge, reasoning, and specialized tasks.

- **Evaluation Metrics:** Key comparisons include accuracy, instruction following, and coding performance across datasets, reported in Table 1. For example, on GSM8K, TuluTalk achieves a score of 69.45%.

- **Ablation Studies:** Significant differences between datasets in task coverage are highlighted. Tulu is STEM-focused, while SmolTalk emphasizes conversational interactions. 

- **Main Results:**
  | Benchmark           | Tulu      | SmolTalk  | TuluTalk     |
  |---------------------|-----------|-----------|--------------|
  | GSM8K               | 66.64%    | 61.97%    | 69.45%       |
  | MMLU                | 63.27%    | 62.90%    | 64.38%       |
  | HumanEval (pass@1) | 44.33%    | 48.67%    | 56.49%       |

- **Computational Costs:** Not detailed explicitly, but the work emphasizes efficiency in terms of achievable performance despite reduced dataset sizes.

### Discussion & Conclusion
The main takeaway is that a smaller, carefully curated dataset can outperform larger counterparts, emphasizing that high-quality samples are key to driving performance gains. Limitations involve the novelty of the datasets and potential biases in the selected samples. Future research could expand on these datasets and explore their effects on various model architectures.

## Key Contributions
- Introduced TuluTalk, an optimized mixture of Tulu and SmolTalk datasets that balances quality and efficiency.
- Provided a detailed qualitative analysis of the datasets through Magpie annotations.
- Developed curation recipes based on task awareness to improve model outputs significantly.

## Potential Relevance
This paper's meticulous methodology and insights into dataset curation can inform future dataset generation efforts. Understanding the impact of sample quality and task diversity on model performance is crucial for researchers aiming to enhance LLM capabilities while optimizing resource use.