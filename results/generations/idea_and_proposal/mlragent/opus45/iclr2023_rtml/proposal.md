# Research Proposal: Selective Unlearning via Influence-Guided Low-Rank Adaptation for Detoxifying Large Language Models

## 1. Introduction

### Background

Large language models (LLMs) have revolutionized natural language processing, demonstrating remarkable capabilities across diverse applications including text generation, question answering, and code synthesis. However, these models are trained on massive web-scale corpora that inevitably contain toxic, biased, and privacy-sensitive content. As a consequence, LLMs can generate harmful outputs that perpetuate stereotypes, produce offensive language, or leak sensitive personal information. Studies have shown that models like GPT-3 and LLaMA exhibit measurable toxicity in open-ended generation tasks and demonstrate biases against marginalized communities, raising serious concerns for deployment in mission-critical domains such as healthcare, education, and legal services.

Current approaches to mitigating these issues face significant limitations. Reinforcement Learning from Human Feedback (RLHF) requires extensive human annotation and computational resources, often costing millions of dollars for large-scale models. Full fine-tuning approaches risk catastrophic forgetting, where models lose valuable general capabilities while attempting to remove specific harmful behaviors. Moreover, these methods lack surgical precision—they operate as blunt instruments that cannot distinguish between truly harmful knowledge and benign content that may superficially resemble toxic patterns.

Machine unlearning has emerged as a promising paradigm for addressing these challenges. Unlike traditional fine-tuning, unlearning aims to selectively remove specific learned associations while preserving overall model utility. Recent surveys (Geng et al., 2025; Ren et al., 2025) have systematically categorized unlearning approaches for LLMs, identifying key challenges including precision in targeting harmful content, computational efficiency, and prevention of catastrophic forgetting. The Multi-Objective Large Language Model Unlearning (MOLLM) framework (Pan et al., 2024) has shown that formulating unlearning as a multi-objective optimization problem can help balance forgetting targets with utility preservation, while hierarchical federated approaches (Zhong et al., 2025) demonstrate the potential for scalable, privacy-preserving unlearning.

### Research Objectives

This research proposes **Influence-Guided Low-Rank Unlearning (IGLU)**, a novel parameter-efficient framework for targeted removal of toxic and biased content from LLMs. Our primary objectives are:

1. **Develop a precise influence mapping technique** that identifies specific parameters, attention heads, and layer combinations most responsible for generating harmful outputs, enabling surgical intervention rather than broad model modification.

2. **Design a parameter-efficient unlearning mechanism** using targeted Low-Rank Adaptation (LoRA) modules that selectively modify only the identified problematic components, achieving significant computational savings compared to full fine-tuning.

3. **Establish a utility preservation framework** that maintains model performance on benign tasks through knowledge distillation regularization while ensuring effective removal of harmful behaviors.

4. **Validate the approach comprehensively** across multiple toxicity benchmarks, bias metrics, and general capability evaluations to demonstrate both effectiveness and safety.

### Significance

This research addresses critical gaps in trustworthy AI development. By enabling precise, efficient, and utility-preserving unlearning, IGLU offers practical solutions for organizations deploying LLMs in sensitive applications. The framework's parameter efficiency makes it accessible to researchers and practitioners without access to massive computational resources, democratizing the ability to create safer AI systems. Furthermore, the influence mapping component provides interpretability into model behavior, contributing to the broader goal of explainable AI.

## 2. Methodology

### 2.1 Overview of the IGLU Framework

IGLU consists of three interconnected stages: (1) Influence Mapping for identifying harmful parameter regions, (2) Low-Rank Intervention for targeted unlearning, and (3) Utility Preservation for maintaining general capabilities. Figure 1 (conceptual) illustrates the overall pipeline.

### 2.2 Stage 1: Influence Mapping

The goal of influence mapping is to identify which model components are most responsible for generating specific harmful outputs. We adapt influence functions from classical machine learning to the LLM setting, focusing on computational tractability.

**Gradient-Based Influence Computation**: Given a pre-trained LLM with parameters $\theta \in \mathbb{R}^d$, a harmful input-output pair $(x_h, y_h)$ from a curated toxicity dataset $\mathcal{D}_h$, and a loss function $\mathcal{L}$, we compute the influence of each parameter group on the harmful output:

$$I(\theta_i; x_h, y_h) = \nabla_{\theta_i} \mathcal{L}(x_h, y_h; \theta)^\top H_{\theta_i}^{-1} \nabla_{\theta_i} \mathcal{L}(x_h, y_h; \theta)$$

where $H_{\theta_i}$ is the Hessian matrix restricted to parameter group $i$. Direct computation of the Hessian inverse is intractable for LLMs; we employ the Kronecker-factored approximate curvature (K-FAC) method:

$$H_{\theta_i}^{-1} \approx (A_i^{-1} \otimes G_i^{-1})$$

where $A_i$ and $G_i$ are the input activation and gradient covariance matrices for layer $i$, respectively.

**Attention Head Attribution**: For transformer architectures, we additionally compute attention head-level influence scores:

$$S_h^{(l)} = \frac{1}{|\mathcal{D}_h|} \sum_{(x,y) \in \mathcal{D}_h} \left\| \frac{\partial \mathcal{L}(x, y; \theta)}{\partial W_h^{(l)}} \right\|_F$$

where $W_h^{(l)}$ represents the parameters of attention head $h$ in layer $l$, and $\|\cdot\|_F$ denotes the Frobenius norm.

**Selection Criterion**: We select the top-$k$ parameter groups and attention heads based on aggregated influence scores:

$$\mathcal{S} = \text{Top-}k\left(\{(i, I_{\text{agg}}(\theta_i))\}_{i=1}^{N}\right)$$

where $I_{\text{agg}}(\theta_i) = \frac{1}{|\mathcal{D}_h|} \sum_{(x,y) \in \mathcal{D}_h} I(\theta_i; x, y)$.

### 2.3 Stage 2: Low-Rank Intervention

Rather than modifying all model parameters, we apply LoRA adapters specifically to the identified problematic components in $\mathcal{S}$.

**LoRA Parameterization**: For each selected weight matrix $W_i \in \mathcal{S}$, we introduce low-rank decomposition:

$$W_i' = W_i + \Delta W_i = W_i + B_i A_i$$

where $B_i \in \mathbb{R}^{d_{out} \times r}$, $A_i \in \mathbb{R}^{r \times d_{in}}$, and $r \ll \min(d_{in}, d_{out})$ is the rank hyperparameter.

**Contrastive Unlearning Objective**: We train the LoRA adapters using a contrastive objective that pushes the model away from harmful outputs while anchoring to benign responses. Given harmful dataset $\mathcal{D}_h$ and a corresponding set of benign reformulations $\mathcal{D}_b$ (created by replacing toxic responses with safe alternatives):

$$\mathcal{L}_{\text{unlearn}} = \mathbb{E}_{(x_h, y_h) \sim \mathcal{D}_h} \left[ -\log \sigma\left( -\log p_\theta(y_h | x_h) \right) \right]$$

$$\mathcal{L}_{\text{anchor}} = \mathbb{E}_{(x_b, y_b) \sim \mathcal{D}_b} \left[ -\log p_\theta(y_b | x_b) \right]$$

The combined intervention loss is:

$$\mathcal{L}_{\text{intervention}} = \mathcal{L}_{\text{unlearn}} + \lambda_1 \mathcal{L}_{\text{anchor}}$$

where $\lambda_1$ balances the two objectives.

**Gradient Ascent with Stability**: To prevent gradient explosion (a known issue identified in Pan et al., 2024), we employ gradient clipping and a cosine annealing learning rate schedule:

$$\eta_t = \eta_{\min} + \frac{1}{2}(\eta_{\max} - \eta_{\min})\left(1 + \cos\left(\frac{t\pi}{T}\right)\right)$$

### 2.4 Stage 3: Utility Preservation

To prevent catastrophic forgetting of benign capabilities, we introduce a knowledge distillation regularizer using the original model as a teacher.

**Distillation Loss**: For a held-out dataset $\mathcal{D}_{\text{retain}}$ of general language tasks:

$$\mathcal{L}_{\text{KD}} = \mathbb{E}_{x \sim \mathcal{D}_{\text{retain}}} \left[ \text{KL}\left( p_{\theta_{\text{orig}}}(\cdot | x) \| p_{\theta'}(\cdot | x) \right) \right]$$

where $\theta_{\text{orig}}$ denotes the original frozen parameters and $\theta' = \theta + \Delta\theta$ represents the model with LoRA modifications.

**Final Objective**: The complete IGLU training objective combines all components:

$$\mathcal{L}_{\text{IGLU}} = \mathcal{L}_{\text{unlearn}} + \lambda_1 \mathcal{L}_{\text{anchor}} + \lambda_2 \mathcal{L}_{\text{KD}}$$

We optimize only the LoRA parameters $\{A_i, B_i\}_{i \in \mathcal{S}}$ while keeping all other parameters frozen.

### 2.5 Experimental Design

**Models**: We evaluate IGLU on three model scales: LLaMA-2-7B, LLaMA-2-13B, and Mistral-7B-Instruct.

**Datasets**:
- *Harmful content identification*: RealToxicityPrompts (10K prompts), ToxiGen (13K statements), and a curated bias probing dataset targeting gender, race, and religion.
- *Utility preservation*: MMLU, HellaSwag, ARC-Challenge, and TruthfulQA.
- *Benign anchoring*: Alpaca-cleaned dataset for safe response generation.

**Baselines**:
1. Full fine-tuning with negative examples
2. Standard LoRA fine-tuning (non-targeted)
3. Gradient Ascent unlearning (GA)
4. MOLLM (Multi-Objective LLM Unlearning)
5. Offset Unlearning

**Evaluation Metrics**:
- *Toxicity*: Expected Maximum Toxicity (Perspective API), Toxicity Probability, and ToxiGen accuracy
- *Bias*: Stereotype Score, Demographic Parity, and Equal Opportunity metrics
- *Utility*: Accuracy on MMLU, HellaSwag, ARC-Challenge; perplexity on WikiText-103
- *Efficiency*: Training time, GPU memory usage, number of trainable parameters

**Hyperparameters**: LoRA rank $r \in \{8, 16, 32\}$, $\lambda_1 \in \{0.5, 1.0, 2.0\}$, $\lambda_2 \in \{0.1, 0.5, 1.0\}$, top-$k$ selection $\in \{5\%, 10\%, 20\%\}$ of total layers.

**Ablation Studies**:
1. Impact of influence mapping precision (random selection vs. gradient-based vs. full influence function)
2. Effect of LoRA rank on unlearning effectiveness
3. Contribution of each loss component
4. Generalization to unseen toxic patterns

## 3. Expected Outcomes & Impact

### Expected Outcomes

**Quantitative Results**: We anticipate IGLU will achieve:
- 40-60% reduction in Expected Maximum Toxicity on RealToxicityPrompts compared to the original model
- Less than 2% degradation in MMLU accuracy (vs. 5-10% for full fine-tuning baselines)
- 10x reduction in computational cost compared to full fine-tuning (measured in GPU-hours)
- 90% reduction in trainable parameters compared to standard LoRA (due to targeted application)

**Qualitative Insights**: The influence mapping component will reveal interpretable patterns about where toxicity is encoded in LLMs, potentially showing:
- Concentration of harmful associations in specific attention heads
- Layer-wise distribution of different types of toxic content (explicit vs. implicit bias)
- Correlation between influence scores and semantic categories of harm

### Broader Impact

**Practical Deployment**: IGLU enables organizations to perform on-demand detoxification of deployed LLMs without requiring massive computational infrastructure or complete model retraining. This is particularly valuable for:
- Healthcare applications requiring removal of medical misinformation
- Educational tools needing age-appropriate content filtering
- Customer service bots requiring professional communication standards

**Research Contributions**: This work advances the field of trustworthy AI by:
1. Providing a theoretically grounded framework connecting influence functions to unlearning
2. Demonstrating the viability of parameter-efficient approaches for model correction
3. Establishing new benchmarks for evaluating surgical unlearning precision

**Societal Benefits**: By making detoxification accessible and efficient, IGLU contributes to reducing harmful AI outputs that disproportionately affect marginalized communities. The interpretability provided by influence mapping also supports accountability and auditing requirements increasingly demanded by AI governance frameworks.

**Limitations and Future Work**: We acknowledge that IGLU addresses post-hoc correction rather than preventing harmful content absorption during pre-training. Future research should explore integration with safe pre-training curricula and extension to multi-modal models where visual toxicity presents additional challenges.

### Conclusion

IGLU represents a significant advancement in trustworthy LLM development, offering a principled, efficient, and precise approach to removing harmful content while preserving model utility. By bridging influence functions, parameter-efficient fine-tuning, and machine unlearning, this research provides both theoretical contributions and practical tools for building safer AI systems.