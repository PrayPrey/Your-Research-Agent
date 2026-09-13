---
source_paper: "arxiv_2404_18870.md"
generated_at: "2026-03-14T22:48:09.145290"
model: "gpt-4o-mini"
summary_chars: 7022
---

# More RLHF, More Trust? On The Impact of Preference Alignment On Trustworthiness

## Key Metadata
- **Authors:** Aaron J. Li et al.
- **Year:** 2024
- **Venue:** arXiv
- **Core Contribution:** This study rigorously examines how Reinforcement Learning from Human Feedback (RLHF) impacts the trustworthiness of language models across multiple dimensions, revealing that increased alignment with human preferences does not necessarily translate to enhanced trustworthiness.

## Section Summaries

### Abstract
The trustworthiness of Large Language Models (LLMs) refers to the extent to which their outputs are reliable, safe, and ethically aligned, and it has become a crucial consideration alongside their cognitive performance. In practice, Reinforcement Learning From Human Feedback (RLHF) has been widely used to align LLMs with labeled human preferences, but its assumed effect on model trustworthiness hasn’t been rigorously evaluated. To bridge this knowledge gap, this study investigates how models aligned with general-purpose preference data perform across five trustworthiness verticals: toxicity, stereotypical bias, machine ethics, truthfulness, and privacy. Our results demonstrate that RLHF on human preferences doesn’t automatically guarantee trustworthiness, and reverse effects are often observed. Furthermore, we propose to adapt efficient influence function based data attribution methods to the RLHF setting to better understand the influence of fine-tuning data on individual trustworthiness benchmarks, and show its feasibility by providing our estimated attribution scores. Together, our results underscore the need for more nuanced approaches for model alignment from both the data and framework perspectives, and we hope this research will guide the community towards developing language models that are increasingly capable without sacrificing trustworthiness. The code for our experiments is available at https://github.com/AI4LIFE-GROUP/RLHF_Trust.

### Introduction & Motivation
Large Language Models (LLMs) have recently made significant advancements, emphasizing the need for alignment with human preferences. This is crucial as trustworthiness—assessing AI reliability, safety, and ethical alignment—remains underexplored. The paper addresses the gap in understanding how RLHF techniques impact trustworthiness aspects, such as toxicity and bias, while highlighting the common use of general-purpose datasets that may not prioritize these dimensions.

### Methodology
The study involves a systematic evaluation of RLHF's impact on trustworthiness aspects using two RLHF variants: reward-based Proximal Policy Optimization (PPO) and reward-free Direct Policy Optimization (DPO). It investigates five specific trustworthiness metrics: toxicity, stereotypical bias, machine ethics, truthfulness, and privacy. The methodology includes the following steps:

1. **Model Architecture:** The experiments utilized Pythia models (1.4B, 2.8B, and 6.9B parameters) and Llama-7B to evaluate how model size affects trustworthiness.
2. **Data Preprocessing:** Human preference datasets were derived from the Anthropic Helpfulness and Harmlessness (HH) dataset, focusing on 100,000 response triples for supervised fine-tuning (SFT).
3. **Core Algorithms:**
   - **Supervised Fine-Tuning (SFT):**
     - Objective: \( L_{SFT}(\phi) = -E_{(x, yw) \sim D}[\log \pi_{SFT}\phi(yw | x)] \)
   - **Reward Model Training:**
     - Loss: \( L_{reward}(\theta) = -E_{(x, yw, yl) \sim D}[\log\left(\frac{e^{r_{\theta}(x, yw)}}{e^{r_{\theta}(x, yw)} + e^{r_{\theta}(x, yl)}}\right)] \)
   - **Proximal Policy Optimization (PPO):**
     - Objective: 
     \[
       L_{PPO}(\phi) = E_{(x, y) \sim D}\left[r_{\theta}(x, y) - \beta \log\left(\frac{\pi_{RL}(\phi)(y | x)}{\pi_{SFT}(y | x)}\right)\right] + \gamma E_{x \sim D_{pretrain}}\left[\log(\pi_{RL}(\phi)(x))\right]
     \]
   - **Direct Preference Optimization (DPO):**
     - Objective:
     \[
        L_{DPO}(\pi_{\theta}; \pi_{SFT}) = -E_{(x, yw, yl) \sim D}\left[\log \sigma\left(\beta \log\frac{\pi_{\theta}(yw|x)}{\pi_{SFT}(yw|x)} - \beta \log\frac{\pi_{\theta}(yl|x)}{\pi_{SFT}(yl|x)}\right)\right]
     \]
4. **Training Procedures:** Full parameter fine-tuning with hyperparameters such as batch size, learning rate, and optimizer details conforming to standard practices.
5. **Evaluation Metrics:** Each model's outputs are examined for toxicity, bias, and other metrics pre and post-RLHF phases.

### Experiments & Results
The study evaluates the models on the following aspects:

- **Datasets:** Utilize the Anthropic HH dataset, structured into train/validation/test splits.
- **Evaluation Metrics and Findings:**
  - **Toxicity:** Evaluated using Expected Maximum Toxicity (EMT); negligible fluctuations noted with a slight increase in toxicity.
  - **Stereotypical Bias:** Measured bias scores increased remarkably from below 0.4 to above 0.8 post-RLHF. 
  - **Machine Ethics:** Reduced false negative rates for morally wrong actions improved from 56.8% to approximately 38.3% post-RLHF.
  - **Truthfulness:** Average accuracy decreased by 25% after RLHF across models.
  - **Privacy:** Observed increased privacy leakage, mainly attributed to PPO/DPO.
  
Main results displayed in a compact format:
| Trustworthiness Aspect | SFT   | PPO   | DPO   |
|------------------------|-------|-------|-------|
| Toxicity               | \(\sim 0\) | \(\sim 0\) | \(\sim 0\) |
| Stereotypical Bias     | 0.4   | 0.8   | 0.8   |
| Machine Ethics         | 56.8% FNR | 38.3% FNR | 40.3% FNR |
| Truthfulness           | -25% decrease  | -25% decrease | -25% decrease |
| Privacy                | +12% leakage  | +12% leakage | +12% leakage |

Statistical significance was indicated, suggesting notable trends in model behavior in response to RLHF methods.

### Discussion & Conclusion
The study reveals that standard RLHF techniques do not robustly enhance trustworthiness across several dimensions, countering expectations. Notably, while machine ethics improved, other dimensions like toxicity and truthfulness experienced declines. The authors propose novel data attribution methods to trace the influences of fine-tuning data on trustworthiness metrics, highlighting a significant need for improved dataset curation practices aligned with safety and ethical considerations.

## Key Contributions
- First systematic evaluation of RLHF's impact on trustworthiness dimensions using open-source datasets.
- Uncovered conflicts between generic human preferences and specific trustworthiness criteria, indicating limitations in traditional RLHF procedures.
- Proposed a novel adaptation of influence function methods for RLHF, providing insights into harmful fine-tuning data.

## Potential Relevance
This paper's findings could inform hypothesis development by providing methods for assessing model trustworthiness in RLHF contexts, establishing baselines for ethical considerations, and highlighting the importance of dataset integrity in developing AI systems.