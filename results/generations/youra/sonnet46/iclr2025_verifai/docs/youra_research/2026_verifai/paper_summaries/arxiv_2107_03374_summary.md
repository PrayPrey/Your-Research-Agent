---
source_paper: "arxiv_2107_03374.md"
generated_at: "2026-03-18T02:44:38.977405"
model: "gpt-4o-mini"
summary_chars: 5767
---

# Evaluating Large Language Models Trained on Code

## Key Metadata
- **Authors:** Mark Chen et al.
- **Year:** 2021
- **Venue:** arXiv
- **Core Contribution:** This paper introduces Codex, a GPT model fine-tuned on GitHub code, assessing its code-writing capabilities and functional correctness through the HumanEval benchmark.

## Section Summaries

### Abstract
We introduce Codex, a GPT language model fine-tuned on publicly available code from GitHub and study its Python code-writing capabilities. A distinct production version of Codex powers GitHub Copilot. On HumanEval, a new evaluation set we release to measure functional correctness for synthesizing programs from docstrings, our model solves 28.8% of the problems, while GPT-3 solves 0% and GPT-J solves 11.4%. Furthermore, we find that repeated sampling from the model is a surprisingly effective strategy for producing working solutions to difficult prompts. Using this method, we solve 70.2% of our problems with 100 samples per problem. Careful investigation of our model reveals its limitations, including difficulty with docstrings describing long chains of operations and with binding operations to variables. Finally, we discuss the potential broader impacts of deploying powerful code generation technologies, covering safety, security, and economics.

### Introduction & Motivation
This paper addresses the challenge of program synthesis using large language models, motivated by their demonstrated capabilities in various domains. Prior work shows that existing general-purpose models, like GPT-3, can generate basic code but struggle with more complex tasks. Codex, a specialized model trained on a substantial dataset of code from GitHub, is expected to perform significantly better. This paper investigates Codex's performance against a new benchmark, HumanEval, specifically designed for evaluating functional correctness in code generation tasks.

### Methodology
Codex is built upon a fine-tuning of the GPT architecture, specifically tailored for code. The training data consists of approximately 179 GB of unique Python files collected from 54 million public GitHub repositories. The data undergoes rigorous filtering to ensure quality, ensuring that only files likely to contain useful code remain. Codex employs the same learning rate schedule as GPT but uses an Adam optimizer with \(β_1 = 0.9\), \(β_2 = 0.95\), \(ε = 10^{-8}\), and a weight decay of 0.1. 

To evaluate the model, we generate samples for tasks and check their correctness using unit tests within our evaluation framework. The primary metric for assessment is \(pass@k\), where a problem is deemed solved if any of the \(k\) generated samples pass the tests. The evaluation procedure involves generating \(200\) samples for each task, counting the correct outputs, and calculating the unbiased estimator using:

\[
pass@k := E\left[1 - \prod_{j=0}^{k-1}\left(1-\frac{c-j}{n-j}\right)\right],
\]
where \(c\) is the number of correct samples among \(n\) total samples.

To increase performance, Codex utilizes nucleus sampling with \(top\_p = 0.95\) and various sampling temperatures optimized for different \(k\) values. For example, temperatures of \(0.2\) for \(pass@1\) and \(0.8\) for \(pass@100\) yield the highest performance. The model architecture scales optimally with size, following a power law relation in model parameters.

### Experiments & Results
We introduce HumanEval, a dataset of 164 hand-written programming problems designed to benchmark Codex’s capabilities. The average unit tests per problem is \(7.7\), ensuring adequate coverage for evaluating functional correctness. Codex-12B solves \(28.8\%\) of the problems at pass@1, with repeated sampling pushing this to \(77.5\%\) at pass@100. 

The performance is compared against baseline models, including GPT-3, which achieves near \(0\%\), and GPT-J (11.4%). In terms of sample efficiency, Codex benefits significantly from multiple generation approaches, surpassing the capabilities of smaller models like Tabnine. Evaluating model sizes, performance improves with the number of parameters, demonstrating that upscaling directly correlates with better performance metrics.

An ablation study highlights that the improved performance of Codex-S—models fine-tuned on correct implementations—results in consistent gains across model sizes. When generating \(100\) samples per problem, the average performance across model variants in terms of \(pass@1\) and \(pass@100\) is displayed in a comparative table.

### Discussion & Conclusion
The findings indicate that while Codex excels at generating functional code bodies, it exhibits significant limitations in handling long operation chains and variable bindings. Moreover, the model must be treated carefully concerning its broader societal implications, including risks of over-reliance and possible biases in generated outputs. The paper emphasizes the necessity of user oversight in practical applications of such code-generating technologies and acknowledges the potential for bias and misuse.

## Key Contributions
- Introduction of Codex, fine-tuned GPT on GitHub code, achieving high performance in code generation.
- Creation of the HumanEval benchmark for evaluating coding capabilities of language models.
- Comprehensive analysis of model limitations and implications for real-world usage and deployment.

## Potential Relevance
This paper is relevant for developing hypotheses around automated code synthesis, providing actionable insights into performance metrics, empirical data on model limits, and real-world implications of AI-generated code. The methodology and experimental design could inform future research efforts in the domain of AI-assisted programming and education.