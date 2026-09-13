---
source_paper: "arxiv_2207_05221.md"
generated_at: "2026-03-18T02:46:15.391702"
model: "gpt-4o-mini"
summary_chars: 6317
---

# Language Models (Mostly) Know What They Know

## Key Metadata
- **Authors:** Saurav Kadavath et al.
- **Year:** 2022
- **Venue:** arXiv
- **Core Contribution:** This paper investigates language models' abilities to self-evaluate their outputs, specifically the calibration of their confidence levels in their knowledge and the probability of knowing answers to questions (P(IK)).

## Section Summaries

### Abstract
We study whether language models can evaluate the validity of their own claims and predict which questions they will be able to answer correctly. We first show that larger models are well-calibrated on diverse multiple choice and true/false questions when presented in the right format. Thus, we can approach self-evaluation on open-ended tasks by asking models to propose answers and then evaluate the probability "P(True)" that those answers are correct. Performance at self-evaluation improves when models consider many of their own samples before predicting validity. We also investigate whether models can predict "P(IK)", the probability that "I know" the answer to a question, without referring to a specific answer. Results show good performance and partial generalization across tasks, although models struggle with calibration on new tasks. The P(IK) probabilities increase in the presence of relevant materials and hints for problem-solving. These observations aim to lay groundwork for training more honest models and exploring honesty under different training objectives.

### Introduction & Motivation
This research aims to ascertain whether AI systems can accurately evaluate their confidence in knowledge, a crucial factor for developing truthful AI. The authors assess the calibration of language models (LMs) regarding their probabilistic outputs. Well-calibrated predictions suggest the potential for self-evaluation, where models determine the correctness of their generated answers. The work posits that larger models display improved calibration, allowing them to better distinguish between correct and incorrect outputs, and introduces methodologies to enhance their self-evaluation capabilities.

### Methodology
The study employs a varied suite of language models ranging from 800M to 52B parameters, utilizing a unified training approach. The models were pre-trained with large contexts (850 billion tokens). The calibration assessment focuses on three types of tasks: multiple choice questions, true/false questions, and the novel self-evaluation framework.

1. **Calibration Tasks:** The LM is assessed on its ability to accurately predict the correct answer among multiple choices, formatted with visible labels. The calibration is quantified using the Expected Calibration Error (ECE).
   
   - **Key equations:**
     - \( ECE = \frac{1}{n} \sum_{i=1}^n |p_i - o_i| \)
     - Where \( p_i \) is the predicted probability and \( o_i \) is the observed frequency.

2. **Self-Evaluation Method:** After generating answers to questions, the model assesses the validity of its outputs, generating the probability \( P(True) \) for its answer being correct. Enhanced performance is achieved by presenting multiple samples to the model, improving calibration.

3. **P(IK) Training:** The probability that the model knows the right answer to an input question, termed \( P(IK) \), is trained using a binary classification framework on samples at unit temperature. A value head is added to facilitate this.

4. **Experimental Setup:**
   - Training utilized a cross-entropy loss function.
   - Few-shot prompting methods involved using random examples or previous questions for context.
   - Evaluation metrics included AUROC for classification performance and accuracy scores.

### Experiments & Results
The evaluation employed diverse datasets such as BIG Bench, MMLU, TriviaQA, Lambada, Codex HumanEval, and GSM8k, achieving task-specific results. Each dataset's training/validation/test split varied, with a general trend showing larger models (particularly the 52B variant) achieving superior calibration across tasks.

1. **Calibration Performance:**
   - Models demonstrated significant accuracy improvements in multiple choice tasks, particularly when the calibration format was used.
   - Calibration scores improved from zero-shot to few-shot settings.

2. **Self-Evaluation Results:**
   - The 52B model’s self-evaluation accuracy yielded a conditional accuracy significantly higher than overall performance when \( P(True) > 0.5 \).
   - A histogram demonstrates clear distinctions between correct and incorrect samples, emphasizing the practical utility of self-evaluation in verifying model outputs.

3. **P(IK) Generalization:**
   - P(IK) was well-calibrated when trained on the TriviaQA dataset, with generalization observed when tested against various out-of-distribution datasets, though some calibration issues emerged.

**Main Results:**
| Task            | Accuracy (52B Model) | ECE    |
|------------------|----------------------|--------|
| TriviaQA         | 83.2%                | 0.06   |
| GS8K             | 75.1%                | 0.14   |
| Codex HumanEval  | 90.5%                | 0.05   |
| Lambada          | 78.4%                | 0.12   |

### Discussion & Conclusion
The findings affirm that larger language models not only self-evaluate effectively but also possess the potential for improved calibration and performance in self-knowledge assessments. Limitations include calibration difficulties out-of-distribution and the differences in task type performance. Future work may explore diverse training protocols and further methods to enhance calibration and honesty in language models.

## Key Contributions
- Demonstrated that large language models are well-calibrated on diverse multiple choice and true/false questions with appropriate formatting.
- Developed methods to allow self-evaluation in LMs, revealing the advantages of providing multiple answer samples.
- Achieved success in training models to predict their own knowledge levels, laying groundwork for improved AI honesty.

## Potential Relevance
This paper's insights into self-evaluation techniques and calibration metrics could inform methodologies for developing reliable models in various applications, particularly in domains where knowledge assessment is critical.