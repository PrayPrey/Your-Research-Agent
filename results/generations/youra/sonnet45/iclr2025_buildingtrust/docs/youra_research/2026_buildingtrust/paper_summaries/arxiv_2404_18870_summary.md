---
source_paper: "arxiv_2404_18870.md"
generated_at: "2026-03-17T00:22:10.744642"
model: "gpt-4o-mini"
summary_chars: 6647
---

# More RLHF, More Trust? On The Impact of Preference Alignment On Trustworthiness

## Key Metadata
- **Authors:** Aaron J. Li et al.
- **Year:** 2024
- **Venue:** arXiv
- **Core Contribution:** This study investigates the relationship between Reinforcement Learning from Human Feedback (RLHF) and the trustworthiness of Large Language Models (LLMs), revealing significant misalignments in performance across critical safety aspects.

## Section Summaries

### Abstract
The trustworthiness of Large Language Models (LLMs) refers to the extent to which their outputs are reliable, safe, and ethically aligned, and it has become a crucial consideration alongside their cognitive performance. In practice, Reinforcement Learning From Human Feedback (RLHF) has been widely used to align LLMs with labeled human preferences, but its assumed effect on model trustworthiness hasn’t been rigorously evaluated. To bridge this knowledge gap, this study investigates how models aligned with general-purpose preference data perform across five trustworthiness verticals: toxicity, stereotypical bias, machine ethics, truthfulness, and privacy. Our results demonstrate that RLHF on human preferences doesn’t automatically guarantee trustworthiness, and reverse effects are often observed. Furthermore, we propose to adapt efficient influence function-based data attribution methods to the RLHF setting to better understand the influence of fine-tuning data on individual trustworthiness benchmarks and show its feasibility by providing our estimated attribution scores. Together, our results underscore the need for more nuanced approaches for model alignment from both the data and framework perspectives, and we hope this research will guide the community towards developing language models that are increasingly capable without sacrificing trustworthiness. The code for our experiments is available at https://github.com/AI4LIFE-GROUP/RLHF_Trust.

### Introduction & Motivation
As LLMs improve, ensuring their alignment with human preferences becomes critical to their deployment. Despite utilizing RLHF methods (like Proximal Policy Optimization and Direct Preference Optimization) to enhance model alignment, their impact on model trustworthiness has not been systematically evaluated. The existing preference datasets used for RLHF do not focus on key trustworthiness metrics, potentially leading to a misalignment wherein RLHF enhances performance on aligned tasks but exacerbates issues like toxicity and bias.

### Methodology
The study systematically evaluates the effects of two RLHF methods: Proximal Policy Optimization (PPO)—which operates with rewards derived from human feedback—and Direct Preference Optimization (DPO)—which simplifies the RL process. The model architecture includes multiple LLMs sized from 1.4B to 7B parameters. The hyperparameters follow recommended settings, utilizing a learning rate of 1e-5, a batch size of 32, and 3 epochs. Training consists of the following stages:

1. **Supervised Fine-Tuning (SFT)**: The model is fine-tuned on a human-generated dataset consisting of prompts and chosen responses, with the objective given by:
   \[
   L_{SFT}(\phi) = -E_{(x,y_w) \sim D} \left[ \log \pi^{SFT}_{\phi}(y_w | x) \right]
   \]
   
2. **Reward Modeling**: A reward model \( r_\theta \) predicts human preferences, trained using the Bradley-Terry loss:
   \[
   L_{reward}(\theta) = -E_{(x,y_w,y_l) \sim D} \left[ \log \left( \frac{e^{r_\theta(x, y_w)}}{e^{r_\theta(x, y_w)} + e^{r_\theta(x, y_l)}} \right) \right]
   \]
   
3. **Reinforcement Learning**: PPO uses the reward model as an objective:
   \[
   L_{PPO}(\phi) = E_{(x,y) \sim D} \left[ r_\theta(x, y) - \beta \log \left( \frac{\pi_{RL}(\phi)(y | x)}{\pi_{SFT}(y | x)} \right) \right] + \gamma E_{x \sim D_{pretrain}} \left[ \log(\pi_{RL}(\phi)(x)) \right]
   \]

DPO modifies preference optimization directly into policy optimization, focusing on minimizing:
\[
L_{DPO}(\pi_\theta; \pi_{SFT}) = -E_{(x,y_w,y_l) \sim D} \left[ \log \sigma\left( \beta \log\frac{\pi_\theta(y_w|x)}{\pi_{SFT}(y_w|x)} - \beta \log\frac{\pi_\theta(y_l|x)}{\pi_{SFT}(y_l|x)} \right)\right]
\]

The study focused on five trustworthiness benchmarks: toxicity, stereotypical bias, machine ethics, truthfulness, and privacy using diverse datasets for each aspect while ensuring that the models were assessed before SFT, after SFT, and post-RLHF.

### Experiments & Results
The models evaluated include three Pythia models (1.4B, 2.8B, 6.9B) and Llama-7B, using the Anthropic HH dataset comprising around 100,000 human-generated response triples. Key findings are summarized:

| Trustworthiness Aspect | SFT Change | PPO Change | DPO Change |
|-----------------------|------------|------------|------------|
| Toxicity              | Negligible | -           | -          |
| Stereotypical Bias    | +150%      | -           | -          |
| Machine Ethics        | +31%       | Use of PPO/DPO only improves marginally | Not evaluated |
| Truthfulness          | -25%       | -           | -          |
| Privacy               | +12%       | +           | -          |

Statistical significance was noted, especially for toxicity and bias measurements across multiple runs. Furthermore, the experiments concluded that while machine ethics improved, the RLHF processes often led to negative outcomes in other trustworthiness metrics.

### Discussion & Conclusion
The research reveals an inherent misalignment between RLHF objectives and specific trustworthiness dimensions. While RLHF enhancement methods can improve certain ethical considerations, they may inadvertently lead to increases in bias and risks to privacy. The proposed data attribution method offers potential to identify and rectify detrimental fine-tuning samples. This insight calls for more tailored approaches to RLHF that account for trustworthiness complexities in the continuous development of LLMs.

## Key Contributions
- Systematic evaluation of RLHF's impact on major trustworthiness aspects.
- Identification of misalignment between general human preferences and specific trustworthiness measures.
- Introduction of a novel data attribution analysis framework for better understanding and mitigation of detrimental impacts from training datasets.

## Potential Relevance
The methodologies and findings in this paper may inform strategies for more effective RLHF implementation in future models, especially for research surrounding safety and ethical guidelines. Understanding the tension between model alignment goals and real-world trustworthiness will be critical for the next generation of LLM development.