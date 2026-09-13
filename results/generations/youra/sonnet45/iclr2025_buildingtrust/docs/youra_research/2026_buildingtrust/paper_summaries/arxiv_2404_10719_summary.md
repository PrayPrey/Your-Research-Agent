---
source_paper: "arxiv_2404_10719.md"
generated_at: "2026-03-17T00:21:46.680916"
model: "gpt-4o-mini"
summary_chars: 6471
---

# Is DPO Superior to PPO for LLM Alignment? A Comprehensive Study

## Key Metadata
- **Authors:** Shusheng Xu et al.
- **Year:** 2024
- **Venue:** arXiv
- **Core Contribution:** This paper conducts a theoretical and empirical comparison between Direct Preference Optimization (DPO) and Proximal Policy Optimization (PPO) for aligning large language models (LLMs) with human preferences, concluding that PPO consistently outperforms DPO.

## Section Summaries

### Abstract
Reinforcement Learning from Human Feedback (RLHF) is currently the most widely used method to align large language models (LLMs) with human preferences. Existing RLHF methods can be roughly categorized as either reward-based or reward-free. Novel applications such as ChatGPT and Claude leverage reward-based methods that first learn a reward model and apply actor-critic algorithms like Proximal Policy Optimization (PPO). However, in academic benchmarks, the state-of-the-art results are often achieved via reward-free methods such as Direct Preference Optimization (DPO). Is DPO truly superior to PPO? Why does PPO perform poorly on these benchmarks? In this paper, we first conduct both theoretical and empirical studies on the algorithmic properties of DPO and show that DPO may have fundamental limitations. Moreover, we also comprehensively examine PPO and reveal the key factors for its best performance in fine-tuning LLMs. Finally, we benchmark DPO and PPO across a collection of RLHF testbeds, ranging from dialogue to code generation. Experiment results demonstrate that PPO surpasses other alignment methods in all cases, achieving state-of-the-art results in challenging code competitions.

### Introduction & Motivation
The alignment of large language models (LLMs) with human preferences is critical to their practical applications. Current fine-tuning methods include Supervised Fine-Tuning (SFT) and Reinforcement Learning from Human Feedback (RLHF). Within RLHF, reward-based methods (like PPO) learn a reward model from preference data, while reward-free methods (like DPO) optimize directly based on preferences without a reward function. This paper addresses the question of whether DPO is indeed superior to PPO, particularly given the observed discrepancies between their performances across various benchmarks. 

### Methodology
The study investigates two RLHF methods: **Proximal Policy Optimization (PPO)** and **Direct Preference Optimization (DPO)**. 

1. **PPO**:
    - **Model Setup**: PPO employs a reward model \( r_\phi \) trained on pairs of human responses \((x,y_w,y_l)\) where \(y_w\) is preferred over \(y_l\).
    - **Optimization Objective**: The objective is defined as:
    \[
    J_{r_\phi}(\pi_\theta) = \mathbb{E}_{x\sim p_{data},y\sim \pi_\theta}\left[r(x, y) - \beta \log\frac{\pi_\theta(y|x)}{\pi_{ref}(y|x)}\right]
    \]
    - **Training**: The reward model is optimized using the negative log-likelihood method:
    \[
    L_R(r_\phi) = -\mathbb{E}_{(x,y_w,y_l)\sim D}\left[\log \sigma(r_\phi(x,y_w) - r_\phi(x,y_l))\right]
    \]
    
2. **DPO**:
    - **Optimization Objective**: The DPO method aims to maximize the policy:
    \[
    \pi^*(y|x) = \frac{1}{Z(x)} \pi_{ref}(y|x) \exp\left(\frac{r(x,y)}{1/\beta}\right)
    \]
    where \(Z(x)\) is the partition function.
    - **Loss Function**:
    \[
    L_{DPO}(\pi_\theta) = -\mathbb{E}_{(x,y_w,y_l)\sim D}\left[\log \sigma\left(\frac{\beta}{1} \log\frac{\pi_\theta(y_w|x)}{\pi_{ref}(y_w|x)} - \log\frac{\pi_\theta(y_l|x)}{\pi_{ref}(y_l|x)}\right)\right]
    \]
    
Key hyperparameters include learning rates (for PPO), batch size (64 as baseline), optimizer (Adam), and epochs (varies by task). The models are fine-tuned with carefully designed datasets. Novel insights are gained by demonstrating how distribution shifts affect the performance of DPO compared to PPO, showing how PPO consistently outperforms DPO through systematic ablation studies focusing on batch size and normalization techniques.

### Experiments & Results
The experiments performed include extensive evaluations on multiple datasets: 

1. **Datasets**:
    - **HH-RLHF** (170k comparisons) - focuses on helpfulness and safety.
    - **SafeRLHF** (over 30k entries) - pairs of responses for alignment.
    - Code generation tasks include **APPS** and **CodeContest** datasets.
    
2. **Metrics**: 
    - Evaluation methods include pass rates (pass@k for code tasks), reward metrics (OpenAssistant Reward), and win rates against standard models.

3. **Results Summary**:
    - **PPO consistently outperformed DPO** in dialogue and code generation tasks, with notable results for the CodeContest:
        - PPO achieved a pass rate of 22.4% on CodeContest compared to AlphaCode-41B’s 16.4% (improvement noted from DPO iterations).
        - An ablation study indicated the most significant enhancements came from increasing batch size and employing advantage normalization.
        - DPO performed poorly in safety and helpfulness measurements, with only 55.4% safety in initial tests, significantly improved by re-training and reducing distribution shifts.

4. **Computational Costs**: The computational resources utilized include GPU hours calculated for training and inference speed details.

### Discussion & Conclusion
The results exemplify how PPO consistently outperforms DPO across diverse tasks, especially under challenging conditions like code generation, where DPO struggles significantly. The study outlines the potential for DPO through iterative improvement yet acknowledges that it remains sensitive to distribution shifts affecting overall performance. Future directions include investigating better reward modeling strategies that can enhance LLM alignment methods across domains.

## Key Contributions
- Comprehensive theoretical and empirical analysis of DPO and PPO, identifying critical factors that enhance PPO performance.
- Extensive benchmarking across various LLM alignment tasks, establishing PPO’s superiority.
- New insights into the limitations of DPO, particularly in relation to distribution shifts and preference data quality.

## Potential Relevance
This study may aid in formulating hypotheses regarding reinforcement learning methods for aligning LLMs, such as the efficacy of model architecture choices, the significance of data distribution during training, and the implications of employing reward models versus purely preference-based techniques in future research endeavors.