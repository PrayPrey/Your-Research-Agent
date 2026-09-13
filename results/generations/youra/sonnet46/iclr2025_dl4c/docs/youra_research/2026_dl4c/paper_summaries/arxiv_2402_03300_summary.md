---
source_paper: "arxiv_2402_03300.md"
generated_at: "2026-03-15T15:14:57.091629"
model: "gpt-4o-mini"
summary_chars: 6276
---

# DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models

## Key Metadata
- **Authors:** Zhihong Shao et al.
- **Year:** 2024
- **Venue:** arXiv
- **Core Contribution:** Development of DeepSeekMath 7B, a mathematically advanced language model achieving state-of-the-art performance on mathematical reasoning benchmarks using innovative reinforcement learning and data optimization methodologies.

## Section Summaries

### Abstract
Mathematical reasoning poses a significant challenge for language models due to its complex and structured nature. In this paper, we introduce DeepSeekMath 7B, which continues pre-training DeepSeek-Coder-Base-v1.5 7B with 120B math-related tokens sourced from Common Crawl, together with natural language and code data. DeepSeekMath 7B has achieved an impressive score of 51.7% on the competition-level MATH benchmark without relying on external toolkits and voting techniques, approaching the performance level of Gemini-Ultra and GPT-4. Self-consistency over 64 samples from DeepSeekMath 7B achieves 60.9% on MATH. The mathematical reasoning capability of DeepSeekMath is attributed to two key factors: First, we harness the significant potential of publicly available web data through a meticulously engineered data selection pipeline. Second, we introduce Group Relative Policy Optimization (GRPO), a variant of Proximal Policy Optimization (PPO), that enhances mathematical reasoning abilities while concurrently optimizing the memory usage of PPO.

### Introduction & Motivation
Large language models have made significant strides in mathematical reasoning, evidenced by improvements in benchmarks related to quantitative and geometric problem-solving. However, leading models like GPT-4 remain proprietary, leaving a gap in effective open-source alternatives. This work addresses this gap by presenting DeepSeekMath, designed specifically to enhance mathematical reasoning significantly beyond existing open-source models and nearing the capabilities of proprietary alternatives like GPT-4. The authors establish a large-scale, high-quality pre-training dataset and analyze the impact of newly designed reinforcement learning techniques on model performance.

### Methodology
DeepSeekMath introduces several innovations:
- **Core Algorithm:** The Group Relative Policy Optimization (GRPO) algorithm refines the mathematical reasoning abilities of the model by estimating the baseline from group scores, negating the need for a traditional critic model, yielding significant reductions in computational resources.
- **Model Architecture:** Initiated from the DeepSeek-Coder-Base-v1.5 7B architecture, DeepSeekMath is a transformer model that incorporates both textual and programming language capabilities. It processes a mix of data types to optimize performance across various contexts.
- **Key Hyperparameters:** Training involved 500 billion tokens with the AdamW optimizer (both $\beta_1$ and $\beta_2$ set as 0.9 and 0.95 respectively, weight decay of 0.1), with a maximum learning rate of 5.3e-4. 
- **Training Procedure:** The model underwent pre-training on the DeepSeekMath Corpus and was further refined using mathematical instruction tuning, including procedures simulating chain-of-thought and program-of-thought reasoning.
- **Input/Output Format:** The model is fed with a concatenation of problem statements and solutions in natural and mathematical languages, alongside programming prompts, with outputs being the solutions generated through reasoning and code execution.
- **Data Selection Pipeline:** A fastText-based classifier was developed and trained on positive examples from curated datasets such as OpenWebMath to filter and refine mathematical data from a vast pool of Common Crawl data.

### Experiments & Results
The evaluation utilized several datasets:
- **Datasets Used:** English benchmarks such as GSM8K, MATH, and SAT; Chinese benchmarks like CMATH and the Gaokao tests. The training splits were carefully curated to exclude any data overlapping with evaluation sets.
- **Evaluation Metrics:** Accuracy on mathematical reasoning tasks was measured, primarily focusing on MATH accuracy. DeepSeekMath 7B achieved significant results: 51.7% on MATH and 64.2% on GSM8K. The model's performance demonstrated a marked increase over baseline models such as Minerva.
- **Comparative Results:** Results were compiled in a table showing that DeepSeekMath outperformed state-of-the-art models, consistently outperforming Minerva 540B across English and Chinese datasets.
- **Ablation Studies:** The GRPO variant showed superior improvements in both domain-specific and out-of-domain tasks, indicating framework robustness.
- **Computational Cost:** The model’s architecture allows for reduced memory requirements due to GRPO’s elimination of the critic model, making it both resource-efficient and effective in training.

### Discussion & Conclusion
DeepSeekMath has set a new benchmark for open-source mathematical reasoning, approaching the capabilities of closed models like GPT-4. However, the authors acknowledge limitations in handling geometry-related tasks, reflecting potential biases in dataset selection. Future work aims to refine the data selection process and enhance model adaptability, especially focusing on expanding its instructional capabilities and performance in theorem proving.

## Key Contributions
- Developed DeepSeekMath 7B, achieving competitive MATH benchmark performance using an innovative pre-training data selection and reinforcement learning algorithm.
- Introduced GRPO, optimizing reinforcement learning for mathematical reasoning in language models.
- Created the DeepSeekMath Corpus, a large-scale dataset specifically designed to enhance mathematical instruction and reasoning capabilities in language models.

## Potential Relevance
This paper provides a valuable framework for understanding how to leverage extensive web data for mathematical reasoning in models, offering methodologies that can enhance future research and applications in this domain. The innovative GRPO technique and detailed dataset construction strategies can inform various hypothesis developments concerning LLM performance enhancements and training efficiency measures.