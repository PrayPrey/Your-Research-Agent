# Research Proposal: Compression-Based Analysis of In-Context Learning: Information-Theoretic Bounds on Task Adaptation Without Gradient Updates

## 1. Introduction

### Background

In-context learning (ICL) represents one of the most remarkable emergent capabilities of large language models (LLMs) and other foundation models. Unlike traditional machine learning paradigms that require explicit gradient-based training or fine-tuning to adapt to new tasks, ICL enables models to perform novel tasks by simply conditioning on a few demonstration examples provided in the input prompt. This capability, first prominently demonstrated in GPT-3 (Brown et al., 2020), has fundamentally transformed our understanding of what neural networks can achieve and has profound implications for the deployment and application of foundation models.

Despite the empirical success and widespread adoption of ICL, our theoretical understanding of this phenomenon remains limited. While recent work has made progress in analyzing ICL from various perspectives—including approximation theory (Li et al., 2025), training dynamics (Yang et al., 2024), and scaling laws (Mehta & Gupta, 2025)—a fundamental gap persists between the observed capabilities of these models and our ability to predict, guarantee, or optimize their performance on in-context tasks. This gap is particularly concerning given the increasing reliance on foundation models in critical applications where predictability and reliability are paramount.

Information theory provides a natural and powerful lens through which to understand ICL. At its core, successful prediction requires compression: a model that can effectively compress data has necessarily captured its underlying structure and regularities. LLMs are fundamentally trained as compression engines through the language modeling objective, which minimizes the expected code length for text sequences. The connection between compression and learning, formalized through the Minimum Description Length (MDL) principle and algorithmic information theory, suggests that ICL can be rigorously analyzed as a conditional compression problem where the model must extract task structure from demonstration examples to compress (predict) query outputs.

### Research Objectives

This research proposal aims to establish a rigorous information-theoretic framework for understanding in-context learning in transformer-based foundation models. Specifically, we pursue the following objectives:

1. **Develop formal information-theoretic bounds** on ICL performance that relate the compressibility of task demonstrations, intrinsic task complexity, and achievable prediction accuracy.

2. **Characterize the fundamental limits** of what can be learned in-context by deriving sample complexity bounds for different task classes based on their information-theoretic properties.

3. **Analyze the relationship** between transformer architectural properties (attention mechanisms, depth, width, context length) and information extraction efficiency from in-context demonstrations.

4. **Derive principled strategies** for demonstration selection and prompt design that optimize information transmission from examples to the model.

5. **Provide actionable insights** for foundation model design that enhance ICL capabilities while maintaining efficiency and predictability.

### Significance

This research addresses critical needs identified in the workshop's three core themes:

**Efficiency**: By establishing information-theoretic bounds on ICL, we can determine the minimum number of demonstrations required for reliable task adaptation, directly improving data efficiency. Understanding compression limits will guide the design of more efficient architectures that maximize information extraction per computation.

**Responsibility**: Theoretical guarantees on ICL performance enable more reliable and predictable model behavior, essential for responsible deployment. Understanding when and why ICL fails provides safeguards against overreliance on unpredictable model capabilities.

**Principled Foundations**: Our information-theoretic framework provides fundamental insights into how transformers process and utilize contextual information, bridging the gap between empirical observations and theoretical understanding. This contributes to the broader goal of developing rigorous foundations for foundation models.

The proposed research has potential impact beyond ICL, as the compression-based analysis framework may generalize to other emergent capabilities of foundation models, providing a unified theoretical lens for understanding these systems.

## 2. Methodology

### 2.1 Theoretical Framework

#### 2.1.1 Problem Formulation

We formalize in-context learning as a conditional source coding problem. Let $\mathcal{T}$ denote a distribution over tasks, where each task $T \in \mathcal{T}$ defines a conditional distribution $P_T(y|x)$ over outputs $y \in \mathcal{Y}$ given inputs $x \in \mathcal{X}$. An in-context learning problem consists of:

- **Demonstration set**: $D_T = \{(x_1, y_1), \ldots, (x_k, y_k)\}$ drawn i.i.d. from $P_T(x,y)$
- **Query input**: $x_{k+1}$ drawn from $P_T(x)$
- **Prediction objective**: Predict $y_{k+1}$ with minimal loss

A foundation model $M$ parameterized by $\theta$ produces predictions via:
$$P_M(y|x, D_T; \theta) = \text{Transformer}_\theta(\text{concat}(D_T, (x, \cdot)))$$

#### 2.1.2 Information-Theoretic Characterization

We characterize ICL through the following information-theoretic quantities:

**Task Representation Information**: The mutual information between demonstrations and task identity:
$$I(T; D_T) = H(T) - H(T|D_T)$$

This quantifies how much information about the task structure is contained in $k$ demonstrations.

**Conditional Prediction Entropy**: The uncertainty in predictions given demonstrations:
$$H(Y_{k+1}|X_{k+1}, D_T, T) = \mathbb{E}_{x,D_T,T}[-\log P_T(y|x)]$$

**Model Compression Rate**: The expected code length achieved by the model:
$$L_M = \mathbb{E}_{x,y,D_T,T}[-\log P_M(y|x, D_T; \theta)]$$

The excess code length $L_M - H(Y_{k+1}|X_{k+1}, D_T, T)$ measures the model's sub-optimality in extracting task information from demonstrations.

### 2.2 Core Theoretical Contributions

#### 2.2.1 Information-Theoretic Lower Bounds

We will derive fundamental limits on ICL performance based on task complexity:

**Theorem 1 (Proposed - Lower Bound on Sample Complexity)**: For any model $M$ to achieve expected loss $\mathbb{E}[\ell(Y, \hat{Y})] \leq \epsilon$ on task distribution $\mathcal{T}$, the number of demonstrations $k$ must satisfy:
$$k \geq \frac{I(T; Y|X)}{\min_{i} I(T; Y_i|X_i)} \cdot \log\left(\frac{|\mathcal{T}|}{\delta}\right)$$

where $\delta$ is the failure probability and the denominator represents the information gained per demonstration.

**Proof Sketch**: Apply Fano's inequality to bound the task identification error, then relate task uncertainty to prediction error through the data processing inequality. Use rate-distortion theory to connect prediction error to required information.

#### 2.2.2 Upper Bounds via Compression Analysis

**Theorem 2 (Proposed - Transformer Compression Capacity)**: A transformer with $L$ layers, $d$ dimensions, and $h$ attention heads can achieve excess code length:
$$L_M - H(Y|X, D_T, T) \leq O\left(\sqrt{\frac{K(T) \cdot \log(khd)}{kd}}\right)$$

where $K(T)$ is the Kolmogorov complexity of the task's conditional distribution.

This bound connects architectural parameters to compression efficiency, showing how depth and width affect information extraction.

#### 2.2.3 Task Class Characterization

We will analyze specific task classes with varying information-theoretic properties:

**Linear Tasks**: $y = f_T(x) = w_T^\top x + \epsilon$ where $w_T \sim P_W$
- Derive tight bounds showing $k = O(d)$ demonstrations suffice
- Prove that attention mechanisms can implement optimal Bayesian inference

**Finite Concept Classes**: Tasks drawn from finite set $|\mathcal{T}| < \infty$
- Show $k = O(\log |\mathcal{T}|)$ suffices with high probability
- Characterize the role of task similarity via Rényi divergences

**Algorithmically Complex Tasks**: Tasks with high Kolmogorov complexity $K(T)$
- Establish impossibility results showing ICL fundamentally fails when $K(T) \gg k \log |\mathcal{X} \times \mathcal{Y}|$
- Derive compression-based characterization of learnable task classes

### 2.3 Architectural Analysis

#### 2.3.1 Attention as Information Routing

We model self-attention layers as information routing mechanisms:

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^\top}{\sqrt{d}}\right)V$$

**Analysis Goal**: Prove that attention mechanisms can implement near-optimal information extraction by showing:
$$I(Y_{k+1}; D_T | X_{k+1}, \text{Attn}) \geq (1-\epsilon) \cdot I(Y_{k+1}; D_T | X_{k+1})$$

under appropriate capacity conditions.

**Method**: Apply mutual information bounds for neural networks under gradient flow, adapted to the attention mechanism. Use techniques from information bottleneck theory to characterize what task-relevant information is preserved through attention layers.

#### 2.3.2 Depth and Iterative Refinement

**Proposition (Proposed)**: Each transformer layer can reduce prediction entropy by a multiplicative factor:
$$H(Y|X, D_T, h_\ell) \leq (1 - \gamma_\ell) \cdot H(Y|X, D_T, h_{\ell-1})$$

where $h_\ell$ represents the hidden state at layer $\ell$ and $\gamma_\ell$ depends on layer capacity.

This implies logarithmic depth suffices: $L = O(\log(1/\epsilon))$ layers achieve $\epsilon$ excess entropy.

### 2.4 Empirical Validation

#### 2.4.1 Synthetic Task Experiments

**Experimental Design**:

1. **Linear Regression Tasks**: Generate tasks $T_i$ with random weight vectors $w_i \sim \mathcal{N}(0, I_d)$
   - Vary dimension $d \in \{5, 10, 20, 50\}$
   - Vary number of demonstrations $k \in \{1, 2, 5, 10, 20, 50\}$
   - Measure: prediction MSE, estimated mutual information $\hat{I}(T; D_T)$

2. **Sparse Boolean Functions**: Tasks defined by $k$-sparse conjunctions
   - Control task complexity via sparsity level
   - Measure: classification accuracy, sample complexity curves

3. **Finite State Machines**: Tasks representing simple automata
   - Vary number of states (controls $K(T)$)
   - Measure: prediction accuracy, minimum demonstrations for learning

**Models**: Train transformers with varying architectures:
- Depth: $L \in \{2, 4, 8, 12\}$
- Width: $d \in \{64, 128, 256, 512\}$
- Attention heads: $h \in \{1, 2, 4, 8\}$

**Evaluation Metrics**:
- **Compression rate**: Empirical $-\log P_M(y|x, D_T)$ vs. theoretical entropy
- **Sample efficiency**: Critical $k^*$ where performance crosses threshold
- **Information utilization**: Estimated $I(Y; D_T | X)$ captured by model
- **Architectural scaling**: Validate predicted relationships between $L, d, h$ and performance

#### 2.4.2 Natural Language Tasks

**Experimental Design**:

1. **Semantic Classification**: Few-shot topic classification
   - Use subsets of AG News, DBpedia
   - Control number of classes (task complexity)
   
2. **Syntactic Tasks**: Part-of-speech tagging, grammatical error detection
   - Varying linguistic complexity

3. **Arithmetic Operations**: Addition, multiplication on varying number ranges
   - Controllable task complexity via number range

**Models**: Evaluate pre-trained LLMs:
- GPT-2 variants (117M, 345M, 774M parameters)
- LLaMA models (7B, 13B parameters)
- Fine-tuned variants with controlled pre-training data

**Evaluation Metrics**:
- **Task identification accuracy**: Can model distinguish tasks from demonstrations?
- **Information-theoretic measures**: Estimate $I(T; D_T)$ via neural estimation
- **Demonstration efficiency**: Performance vs. $k$ curves compared to theoretical bounds
- **Prompt sensitivity**: Robustness to demonstration ordering, formatting

#### 2.4.3 Information Estimation Procedures

To empirically validate theoretical predictions, we will estimate key information-theoretic quantities:

**Mutual Information Estimation**: Use MINE (Mutual Information Neural Estimation):
$$\hat{I}(T; D_T) = \sup_{\phi} \mathbb{E}_{P(T,D_T)}[\phi(T, D_T)] - \log \mathbb{E}_{P(T)P(D_T)}[e^{\phi(T, D_T)}]$$

**Entropy Estimation**: Use k-nearest neighbor estimators for conditional entropy:
$$\hat{H}(Y|X, D_T) = -\frac{1}{n}\sum_{i=1}^n \log \hat{P}(y_i|x_i, D_{T,i})$$

**Compression Rate**: Directly measure model log-likelihood on held-out queries

### 2.5 Demonstration Selection Strategies

Based on theoretical insights, we will develop and validate optimal demonstration selection algorithms:

**Maximum Information Gain**: Select demonstrations that maximize:
$$D^* = \arg\max_{D \subset \mathcal{D}} I(T; D)$$

**Diversity-Based Selection**: Choose demonstrations spanning the input space to maximize coverage

**Difficulty-Weighted Selection**: Prioritize examples with high conditional entropy

**Validation**: Compare against random selection and existing heuristics (e.g., semantic similarity) on both synthetic and natural tasks.

## 3. Expected Outcomes & Impact

### 3.1 Theoretical Contributions

**Rigorous Bounds on ICL**: We expect to establish the first comprehensive information-theoretic characterization of in-context learning, including:
- Sample complexity bounds for broad task classes
- Fundamental limits based on task Kolmogorov complexity
- Tight characterization for linear and finite concept classes

**Architectural Principles**: Our analysis will reveal:
- Optimal relationships between transformer depth, width, and ICL capacity
- Theoretical justification for attention mechanisms in information extraction
- Design principles for architectures optimized for specific task distributions

**Task Learnability Criteria**: Clear characterization of which tasks can/cannot be learned in-context based on their information-theoretic properties.

### 3.2 Practical Outcomes

**Efficient Demonstration Selection**: Principled algorithms for choosing optimal in-context examples that:
- Minimize required demonstrations (data efficiency)
- Maximize task learning signal
- Provide theoretical guarantees on performance

**Predictable Model Behavior**: Theoretical bounds enable:
- Reliability guarantees for deployment
- Prediction of ICL performance before inference
- Identification of failure modes

**Architecture Design Guidelines**: Concrete recommendations for:
- Optimal depth/width trade-offs for ICL
- Context length requirements for different task classes
- Efficient attention mechanisms for information extraction

### 3.3 Impact on Workshop Themes

**Efficiency**: 
- Theoretical minimum demonstrations required reduces inference costs
- Optimal architecture design minimizes computational overhead
- Principled demonstration selection improves data efficiency by 2-5× (estimated)

**Responsibility**:
- Performance guarantees enable safer deployment
- Failure prediction prevents overreliance on uncertain capabilities
- Transparent theoretical framework improves accountability

**Principled Foundations**:
- Bridges empirical ICL success with rigorous theory
- Provides unified compression-based lens for understanding FMs
- Establishes connections to classical learning theory and information theory

### 3.4 Broader Impact

**Beyond In-Context Learning**: The compression-based analysis framework may generalize to other emergent capabilities:
- Chain-of-thought reasoning as sequential compression
- Instruction following as task representation learning
- Few-shot alignment as preference compression

**Cross-Domain Applications**: Information-theoretic principles apply to:
- Vision foundation models (few-shot visual recognition)
- Multimodal models (cross-modal ICL)
- Scientific foundation models (molecular property prediction)

**Educational Value**: Clear theoretical framework will:
- Guide curriculum development for FM courses
- Provide intuition for practitioners
- Establish research directions for theory community

### 3.5 Timeline and Milestones

**Months 1-6**: 
- Develop core theoretical framework
- Prove fundamental bounds for simple task classes
- Implement synthetic experimental testbeds

**Months 7-12**:
- Extend theory to complex task classes
- Complete architectural analysis
- Validate on natural language tasks

**Months 13-18**:
- Develop and test demonstration selection algorithms
- Comprehensive empirical validation
- Refinement based on experimental insights

**Months 19-24**:
- Complete theoretical characterization
- Extensive experiments on large-scale models
- Prepare publications and open-source release

### 3.6 Expected Publications and Deliverables

**Publications**:
- Top-tier ML conference (NeurIPS, ICML, ICLR): Main theoretical results
- Theory journal (JMLR, IEEE TIT): Complete proofs and extended theory
- Workshop papers: Specific applications and empirical findings

**Open-Source Deliverables**:
- Theoretical bounds calculator for different task classes
- Demonstration selection toolkit
- Benchmark suite for ICL evaluation
- Information estimation tools for transformers

This research will establish a rigorous foundation for understanding one of the most important emergent capabilities of modern foundation models, with immediate practical applications and long-term theoretical impact. The compression-based perspective provides a unifying framework that connects classical information theory with modern deep learning, opening new avenues for principled AI system design.