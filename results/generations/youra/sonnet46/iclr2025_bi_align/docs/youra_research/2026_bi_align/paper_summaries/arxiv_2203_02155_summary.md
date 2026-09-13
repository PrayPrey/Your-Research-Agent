---
source_paper: "arxiv_2203_02155.md"
generated_at: "2026-03-14T20:46:04.934797"
model: "gpt-4o-mini"
summary_chars: 6566
---

# Training language models to follow instructions with human feedback (InstructGPT)

## Key Metadata
- **Authors:** Long Ouyang et al.
- **Year:** 2022
- **Venue:** arXiv
- **Core Contribution:** This paper presents InstructGPT, a language model fine-tuned with human feedback to better align outputs with user intentions across a wide range of tasks.

## Section Summaries

### Abstract
Making language models bigger does not inherently make them better at following a user’s intent. For example, large language models can generate outputs that are untruthful, toxic, or simply not helpful to the user. In other words, these models are not aligned with their users. In this paper, we show an avenue for aligning language models with user intent on a wide range of tasks by fine-tuning with human feedback. Starting with a set of labeler-written prompts and prompts submitted through the OpenAI API, we collect a dataset of labeler demonstrations of the desired model behavior, which we use to fine-tune GPT-3 using supervised learning. We then collect a dataset of rankings of model outputs, which we use to further fine-tune this supervised model using reinforcement learning from human feedback. We call the resulting models InstructGPT. In human evaluations on our prompt distribution, outputs from the 1.3B parameter InstructGPT model are preferred to outputs from the 175B GPT-3, despite having 100x fewer parameters. Moreover, InstructGPT models show improvements in truthfulness and reductions in toxic output generation while having minimal performance regressions on public NLP datasets. Even though InstructGPT still makes simple mistakes, our results show that fine-tuning with human feedback is a promising direction for aligning language models with human intent.

### Introduction & Motivation
Large language models (LMs) can perform a variety of natural language processing (NLP) tasks via prompting; however, they often generate biased or untruthful outputs that fail to meet user instructions due to a misalignment of the underlying language modeling objective. The primary objective of this research is to align language models with user intentions, encompassing both explicit (following instructions) and implicit (truthfulness, non-bias) expectations. The method proposed utilizes reinforcement learning from human feedback (RLHF), enhancing model outputs across a diverse range of tasks to make them more helpful, honest, and harmless.

### Methodology
The proposed methodology consists of three main steps (see Figure 2):

1. **Supervised Fine-Tuning (SFT):** A dataset comprising demonstrations from labelers is created by collecting prompts from the OpenAI API and having labelers perform labeled tasks. GPT-3 is fine-tuned using supervised learning on 13,000 training prompts from this dataset for 16 epochs with a cosine learning rate decay and a dropout rate of 0.2.

2. **Reward Model (RM) Training:** A dataset of outputs, where model completions are ranked by labelers, is compiled (33,000 comparisons). A reward model is trained to predict which output a labeler would prefer, using cross-entropy loss based on preferences indicated during ranking (expressed mathematically as: 
   \[
   \text{loss}(\theta) = -\frac{1}{\binom{K}{2}} \mathbb{E}_{(x,y_w,y_l) \sim D} [\log(\sigma(r_\theta(x, y_w) - r_\theta(x, y_l)))]
   \] 
   where \(r_\theta(x, y)\) denotes the output of the RM).

3. **Reinforcement Learning with Proximal Policy Optimization (PPO):** The SFT model is optimized against the RM using PPO (Schulman et al., 2017), incorporating a penalty term to maintain some characteristics from the pre-trained model, referred to as PPO-ptx. The objective function for this step is:
   \[
   \text{objective}(\phi) = \mathbb{E}_{(x,y) \sim D^{\pi}_{RL}} \left[r_\theta(x, y) - \beta \log(\pi_{RL}[\log(\pi_{RL}^{\phi}(x)))] + \gamma \mathbb{E}_{x \sim D_{pretrain}}[\frac{\pi^{pretrain}(y|x)}{\pi^{SFT}(y|x)}]\right]
   \]
   where \(\beta\) and \(\gamma\) control penalty strengths.

The use of reinforcement learning leverages human preferences as a reward signal, iteratively refining the model to align its outputs closely with desired behaviors detailed by human labelers.

### Experiments & Results
The models were evaluated on a diverse set of prompts derived from the OpenAI API. Evaluation metrics included Labeler Preference Ratings, TruthfulQA scores, and toxicity measurements from the RealToxicityPrompts dataset. The study used multiple datasets (SQuAD, DROP, HellaSwag, WMT 2015) to assess performance regressions due to the alignment tax:
- InstructGPT (1.3B, 175B) outperformed GPT-3 outputs 85 ± 3% to 71 ± 4%.
- TruthfulQA benchmark results showed InstructGPT is approximately twice as truthful.
- On the RealToxicityPrompts dataset, InstructGPT generated 25% less toxic responses when prompted respectfully. Performance comparisons to models fine-tuned on public datasets (e.g., FLAN, T0) showed a 73.4% win rate against other methods, indicating superior generalization in instruction-following scenarios.
- Performance on public NLP datasets remained lower initially but could be mitigated by training methods that combined RL updates with pretraining data.

### Discussion & Conclusion
InstructGPT showcases significant advances in aligning language models to user intentions, achieving improved output quality and reduced unwanted behaviors (toxicity, hallucinations). However, models continue to exhibit limitations, particularly around instruction fidelity and handling sensitive prompts. Future work will aim to broaden alignment beyond the training dataset, question model generalizability, and explore methods to prevent alignment-induced performance regressions.

## Key Contributions
- Development of InstructGPT, a model fine-tuned with human feedback using a three-step approach (SFT, RM training, PPO).
- Demonstrated improvements in truthfulness and reduced harmful outputs compared to existing models despite less computational complexity (1.3B vs. 175B parameters).
- Insights into handling multi-task alignment and effective evaluation of model behavior against user requests.

## Potential Relevance
This paper provides a structured framework for incorporating human feedback in model training that may be useful in hypothesis discussions related to model alignment. The methods of evaluation and performance enhancement can inform future research directions for developing reliable language models that adhere to user intents, especially important in high-stakes or sensitive applications.