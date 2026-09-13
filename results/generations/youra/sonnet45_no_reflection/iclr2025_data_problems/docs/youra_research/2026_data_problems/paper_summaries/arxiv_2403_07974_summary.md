---
source_paper: "arxiv_2403_07974.md"
generated_at: "2026-05-11T01:13:49.821665"
model: "gpt-4o-mini"
summary_chars: 6965
---

# LiveCodeBench: Holistic and Contamination Free Evaluation of Large Language Models for Code

## Key Metadata
- **Authors:** Naman Jain et al.
- **Year:** 2024
- **Venue:** arXiv
- **Core Contribution:** Introduction of LiveCodeBench, a continuously updated benchmark for evaluating large language models (LLMs) in code-related tasks with a focus on contamination-free assessments.

## Section Summaries

### Abstract
Large Language Models (LLMs) applied to code-related applications have emerged as a prominent field, attracting significant interest from both academia and industry. However, as new and improved LLMs are developed, existing evaluation benchmarks (e.g., HumanEval, MBPP) are no longer sufficient for assessing their capabilities. In this work, we propose LiveCodeBench, a comprehensive and contamination-free evaluation of LLMs for code, which collects new problems over time from contests across three competition platforms, namely LeetCode, AtCoder, and CodeForces. Notably, our benchmark also focuses on a broader range of code-related capabilities, such as self-repair, code execution, and test output prediction, beyond just code generation. Currently, LiveCodeBench hosts over five hundred coding problems that were published between May 2023 and May 2024. We have evaluated 18 base LLMs and 34 instruction-tuned LLMs on LiveCodeBench. We present empirical findings on contamination, holistic performance comparisons, potential overfitting in existing benchmarks as well as individual model comparisons. We will release all prompts and model completions for further community analysis, along with a general toolkit for adding new scenarios and models.

### Introduction & Motivation
Code has increasingly become a vital application area for LLMs. Despite the rapid developments in code-specific models, existing evaluation methods, primarily focused on natural language-to-code tasks, have remained stagnant, failing to capture the multifaceted nature of programming. This limitation can lead to misleading evaluations and potential overfitting. To address these gaps, the authors introduce LiveCodeBench as a holistic, contamination-free benchmark that collects continuously updated problems from credible coding platforms, providing a more accurate evaluation of LLM capabilities across a variety of code-related tasks.

### Methodology
LiveCodeBench incorporates a robust methodology divided into several components.

**1. Problem Collection:** Problems are sourced from AtCoder, LeetCode, and CodeForces, emphasizing quality by utilizing user-vetted problems. A total of 511 problems were collected over the period from May 2023 to May 2024.

**2. Evaluation Scenarios:** The benchmark evaluates LLMs on four tasks:
   - **Code Generation:** Standard task of generating code from natural language. Evaluated using Pass@1, the percentage of problems for which models generate correct solutions.
   - **Self-Repair:** Models repair faulty code using provided error feedback. Evaluated similarly to code generation, considering both original and repaired codes.
   - **Code Execution:** Models predict the output of given code snippets provided with test inputs, evaluated for correctness based on executed assertions.
   - **Test Output Prediction:** Models generate expected outputs based on problem statements and given input cases.

**3. Training Procedures and Metrics:**
   - Models are evaluated using the Pass@1 metric, which captures performance across multiple outputs generated per problem (10 candidates).
   - Different prompts are used to cater to scenario requirements: e.g., zero-shot for code generation and self-repair, few-shot with COT for code execution.

**4. Statistical Controls:** To avoid contamination, evaluations are performed strictly on problems released after each model’s training cutoff date. This method prevented assessment bias from pre-trained models encountering the test problems.

**5. Hyperparameters:** Evaluation settings include specific temperature control for sampling (temperature = 0.2, top-p = 0.95) ensuring diversity without sacrificing correctness.

### Experiments & Results
In evaluating 52 models (18 base, 34 instruction-tuned), significant findings were recorded:

**1. Datasets and Metrics:** Model performances were assessed across scenarios and categorized by ease:
   - **Total Problems:** 511 with 206 labeled as easy, 182 as medium, and 123 as hard (Table 1).

**2. Performance Overview:** 
   - Various model performances scored by scenarios shown in Figure 4 indicate higher accuracy in code generation and self-repair for models like GPT-4 and Claude-3-Opus.

| Model Name              | Code Generation (Pass@1) | Self-Repair (Pass@1) | Code Execution (Pass@1) | Test Output Prediction (Pass@1) |
|------------------------|--------------------------|----------------------|--------------------------|----------------------------------|
| GPT-4-Turbo            | 83.2                     | 78.5                 | 60.0                     | 75.5                             |
| Claude-3-Opus         | 81.5                     | 80.0                 | 65.0                     | 76.0                             |
| L3-Ins-70B            | 78.1                     | 72.3                 | 54.0                     | 70.1                             |

**3. Statistical Variance:** High correlations across performance metrics for related tasks (e.g., 0.98 for code generation and self-repair) indicated model performance stability within related contexts.

**4. Contamination Highlights:** Models like DeepSeek and GPT-4 showed marked declines in scores on newer problems, indicating potential contamination effects especially noticeable post their release periods.

### Discussion & Conclusion
LiveCodeBench presents a critical advancement in evaluating coding capabilities of LLMs, addressing limitations found in existing benchmarks like HumanEval. Key takeaways include identification of contamination risks and the importance of holistic evaluations encompassing more than mere code generation. Future work will focus on expanding the dataset, improving the evaluation frameworks, and potentially incorporating support for additional languages to encompass broader coding capabilities.

## Key Contributions
- Introduction of a robust, contamination-free benchmark to evaluate code-related tasks in LLMs.
- Emphasis on diverse evaluation scenarios to assess broader coding abilities beyond code generation.
- Analysis revealing performance discrepancies indicating potential overfitting in existing benchmarks.

## Potential Relevance
LiveCodeBench provides a comprehensive framework that can enhance discussions around model evaluation in coding tasks. Its focus on ongoing assessments, contamination-free methodologies, and the incorporation of complex coding tasks may inform hypotheses about future model developments and benchmarking standards in programming AI.