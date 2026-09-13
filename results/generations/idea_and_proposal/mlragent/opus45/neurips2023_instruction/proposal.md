# Research Proposal: Self-Calibrating Instruction Following via Uncertainty-Aware Synthetic Data Generation

## 1. Introduction

### Background

The emergence of instruction-tuned large language models (LLMs) has revolutionized natural language processing, enabling models to comprehend and execute diverse open-ended language commands. Systems like GPT-4 and open-source alternatives have demonstrated remarkable capabilities in following user instructions across numerous domains. Central to these advances is instruction tuning—a process that aligns pre-trained language models with human intent through supervised fine-tuning on instruction-response pairs.

However, a critical limitation persists in current instruction-following systems: the tendency toward overconfidence when processing ambiguous, underspecified, or unclear instructions. When faced with instructions that lack sufficient context or contain inherent ambiguity, state-of-the-art LLMs typically generate confident-sounding but potentially incorrect responses rather than acknowledging uncertainty or seeking clarification. This behavior directly contributes to hallucinations—plausible-sounding but factually incorrect outputs—which represent one of the most significant barriers to deploying LLMs in high-stakes applications.

The proliferation of synthetic data generation for instruction tuning, while enabling unprecedented scale, has inadvertently exacerbated this problem. Current synthetic data pipelines (as reviewed in recent surveys on instruction tuning) focus primarily on generating diverse instruction-response pairs without incorporating quality signals about instruction clarity. Consequently, models trained on such data lack the fundamental ability to distinguish between instructions they can reliably follow and those requiring clarification.

### Research Objectives

This research proposes a novel framework called **Self-Calibrating Instruction Following (SCIF)** that jointly trains LLMs to follow instructions while calibrating their confidence based on instruction quality. Our specific objectives are:

1. Develop an automated pipeline for generating uncertainty-annotated synthetic instruction data that captures instruction ambiguity through multi-pass variance estimation.

2. Design a dual-head architecture that extends standard instruction tuning to simultaneously predict response content and instruction clarity scores.

3. Train models to exhibit appropriate clarification-seeking behavior when instruction uncertainty exceeds calibrated thresholds.

4. Empirically validate that SCIF reduces hallucinations on ambiguous queries by 20-30% while maintaining performance on clear instructions.

### Significance

This research addresses a fundamental gap between current instruction-following capabilities and the requirements for trustworthy AI deployment. By enabling models to "know when they don't know," we create systems that naturally route uncertain queries for human clarification rather than confidently producing errors. This has immediate practical implications for customer service automation, medical information systems, legal document processing, and other domains where incorrect confident outputs carry significant consequences. Furthermore, our uncertainty-annotated synthetic data generation methodology provides a scalable foundation for future research on calibrated instruction following.

## 2. Methodology

### 2.1 Overview

The SCIF framework comprises three interconnected components: (1) uncertainty-annotated synthetic data generation, (2) dual-head model architecture and training, and (3) clarification-seeking behavior integration. We detail each component below.

### 2.2 Uncertainty-Annotated Synthetic Data Generation

#### Multi-Pass Variance Estimation

We generate instruction-response pairs augmented with automatically computed ambiguity scores. For each instruction $x_i$, we sample $K$ responses from a teacher LLM (e.g., LLaMA-3-70B) using temperature sampling:

$$r_{i,k} \sim p_\theta(r | x_i), \quad k = 1, 2, \ldots, K$$

where $\theta$ represents the teacher model parameters and we use temperature $\tau = 0.7$ to encourage diversity.

#### Ambiguity Score Computation

We compute an ambiguity score $a_i$ for instruction $x_i$ based on the semantic variance among generated responses. Using a sentence embedding model $\phi$ (e.g., all-mpnet-base-v2), we compute:

$$a_i = 1 - \frac{1}{K(K-1)} \sum_{j \neq k} \cos(\phi(r_{i,j}), \phi(r_{i,k}))$$

This score ranges from 0 (all responses semantically identical, indicating clear instruction) to 1 (responses highly divergent, indicating ambiguous instruction).

#### Thresholded Labeling

Instructions are categorized using empirically determined thresholds:
- **Clear** ($a_i < 0.3$): High consensus among responses
- **Moderate** ($0.3 \leq a_i < 0.6$): Some response variation
- **Ambiguous** ($a_i \geq 0.6$): High response divergence

For ambiguous instructions, we additionally generate clarifying questions by prompting the teacher model: "Given this ambiguous instruction: [instruction], generate a clarifying question that would help resolve the ambiguity."

#### Dataset Construction

We construct a balanced dataset $\mathcal{D} = \{(x_i, r_i^*, a_i, q_i)\}_{i=1}^N$ where:
- $x_i$: instruction
- $r_i^*$: best response (selected via self-consistency or majority voting for clear instructions)
- $a_i$: ambiguity score
- $q_i$: clarifying question (for ambiguous instructions) or null

We aim for $N = 100,000$ examples with balanced representation across ambiguity categories.

### 2.3 Dual-Head Model Architecture

#### Architecture Design

We extend a base instruction-tuned LLM (e.g., LLaMA-3-8B) with an auxiliary calibration head. Let $h_L \in \mathbb{R}^d$ denote the final hidden state from the transformer backbone. The architecture includes:

**Response Generation Head**: Standard language modeling head
$$p(r_t | r_{<t}, x) = \text{softmax}(W_r h_L^{(t)})$$

**Calibration Head**: A lightweight MLP predicting instruction clarity
$$c = \sigma(W_2 \cdot \text{ReLU}(W_1 \cdot \text{Pool}(h_L)))$$

where $\text{Pool}(\cdot)$ applies mean pooling over sequence positions, $W_1 \in \mathbb{R}^{d \times d/4}$, $W_2 \in \mathbb{R}^{d/4 \times 1}$, and $\sigma$ is the sigmoid function. The confidence score $c \in [0, 1]$ represents predicted instruction clarity.

#### Training Objective

We optimize a joint loss function:

$$\mathcal{L} = \mathcal{L}_{\text{gen}} + \lambda_1 \mathcal{L}_{\text{cal}} + \lambda_2 \mathcal{L}_{\text{clarify}}$$

**Generation Loss**: Standard cross-entropy for response generation
$$\mathcal{L}_{\text{gen}} = -\sum_{t} \log p(r_t^* | r_{<t}^*, x)$$

**Calibration Loss**: Mean squared error for confidence prediction
$$\mathcal{L}_{\text{cal}} = \frac{1}{N} \sum_{i=1}^N (c_i - (1 - a_i))^2$$

where we train the model to predict clarity $(1 - a_i)$ rather than ambiguity.

**Clarification Loss**: For ambiguous instructions, we train the model to generate clarifying questions when confidence is low:
$$\mathcal{L}_{\text{clarify}} = -\mathbb{1}[a_i \geq 0.6] \sum_{t} \log p(q_t | q_{<t}, x, \text{[CLARIFY]})$$

We set $\lambda_1 = 0.5$ and $\lambda_2 = 0.3$ based on preliminary experiments.

### 2.4 Clarification-Seeking Inference

At inference time, the model first computes the confidence score $c$ for an input instruction. The behavior follows:

$$\text{Output} = \begin{cases} 
\text{Generate response } r & \text{if } c \geq \tau \\
\text{Generate clarifying question } q & \text{if } c < \tau
\end{cases}$$

We set the clarification threshold $\tau = 0.5$ by default, which can be adjusted based on application requirements (higher $\tau$ for risk-averse applications).

### 2.5 Experimental Design

#### Datasets and Baselines

**Training Data**: We generate 100K uncertainty-annotated examples using the methodology in Section 2.2, seeded from ShareGPT, FLAN, and self-generated instructions.

**Evaluation Benchmarks**:
- **AmbigQA**: Questions with inherent ambiguity requiring clarification
- **SituatedQA**: Context-dependent questions  
- **TruthfulQA**: Measuring hallucination tendencies
- **MMLU**: Standard capability benchmark for regression testing
- **Custom Ambiguous Instructions Test (CAIT)**: 500 manually crafted instructions with varying ambiguity levels

**Baselines**:
- Standard instruction-tuned LLaMA-3-8B
- Self-consistency decoding baseline
- Verbalized uncertainty prompting ("Express your confidence...")
- Contrastive instruction tuning (COIN)

#### Evaluation Metrics

1. **Calibration Error**: Expected Calibration Error (ECE) measuring alignment between confidence and accuracy:
$$\text{ECE} = \sum_{b=1}^B \frac{|B_b|}{N} |\text{acc}(B_b) - \text{conf}(B_b)|$$

2. **Hallucination Rate**: Percentage of factually incorrect responses on TruthfulQA and domain-specific evaluations

3. **Clarification Appropriateness**: F1 score for appropriately requesting clarification on ambiguous instructions vs. answering clear ones

4. **Task Performance**: Accuracy on MMLU and other standard benchmarks to ensure no capability regression

5. **Response Quality**: Human evaluation (n=200) of response helpfulness on a 5-point Likert scale

#### Implementation Details

- **Base Model**: LLaMA-3-8B-Instruct
- **Training**: LoRA fine-tuning (rank=64, $\alpha$=128) for efficiency
- **Optimization**: AdamW with learning rate $2 \times 10^{-5}$, batch size 32
- **Hardware**: 4× A100-80GB GPUs
- **Training Duration**: 3 epochs (~15 hours)

## 3. Expected Outcomes & Impact

### Expected Results

We anticipate the following outcomes from implementing the SCIF framework:

1. **Improved Calibration**: Models trained with SCIF will demonstrate 40-50% lower Expected Calibration Error compared to baseline instruction-tuned models, indicating better alignment between expressed confidence and actual accuracy.

2. **Reduced Hallucinations**: On ambiguous queries, we expect 20-30% reduction in hallucination rates as measured by TruthfulQA and human evaluation. The clarification-seeking mechanism will route genuinely ambiguous queries away from confident but incorrect responses.

3. **Appropriate Clarification Behavior**: SCIF models will achieve >80% F1 score on clarification appropriateness, correctly distinguishing when to answer versus when to seek clarification.

4. **Maintained Capability**: Performance on standard benchmarks (MMLU, HellaSwag) will remain within 2% of baseline, demonstrating that calibration training does not degrade general capabilities.

5. **Generalizable Uncertainty Annotation**: The multi-pass variance methodology will generalize across domains, providing a scalable approach for future uncertainty-aware dataset construction.

### Broader Impact

**Trustworthy AI Deployment**: By enabling models to acknowledge uncertainty, SCIF addresses a fundamental requirement for deploying LLMs in high-stakes applications including healthcare, legal services, and financial advisory systems.

**Human-AI Collaboration**: Clarification-seeking behavior naturally creates collaborative dialogue, shifting from a paradigm of AI providing answers to AI partnering with humans to ensure accurate understanding.

**Open Research Contribution**: We will release the uncertainty-annotated dataset, training code, and model checkpoints, enabling the research community to build upon this foundation for calibrated instruction following.

**Resource for Evaluation**: The Custom Ambiguous Instructions Test (CAIT) benchmark will provide a standardized evaluation resource for future research on instruction ambiguity handling.

### Limitations and Future Work

We acknowledge that our ambiguity detection relies on semantic variance, which may not capture all forms of instruction underspecification. Future work should explore syntactic and pragmatic ambiguity signals. Additionally, the clarification threshold $\tau$ requires application-specific tuning, suggesting opportunities for adaptive threshold learning based on user feedback.

In conclusion, the SCIF framework represents a significant step toward instruction-following systems that are not only capable but also appropriately humble—models that know when they don't know and act accordingly. This research bridges the gap between current LLM capabilities and the requirements for trustworthy, deployable AI systems.