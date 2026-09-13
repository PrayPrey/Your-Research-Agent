# Research Proposal: Confidence-Calibrated Regret: A Zone of Proximal Development Curriculum for LLM Self-Training

## 1. Introduction

### 1.1 Background

The pursuit of open-ended learning (OEL) systems represents one of the most ambitious frontiers in artificial intelligence research. Unlike traditional machine learning paradigms where training concludes once a model masters a fixed task distribution, OEL systems aspire to generate an endless stream of increasingly challenging problems that continuously push agent capabilities. This paradigm mirrors the evolutionary pressures that shaped human intelligence—a process of perpetual adaptation to novel environmental challenges.

Recent advances in large language models (LLMs) have created unprecedented opportunities for self-improving systems. Models like GPT-4, Llama, and Mistral demonstrate remarkable capabilities in mathematical reasoning, code generation, and logical inference. More importantly, these models can generate their own training data, verify solutions in domains with executable ground truth, and iteratively refine their capabilities. This self-training paradigm has shown promise in works such as STaR (Self-Taught Reasoner), ReST (Reinforced Self-Training), and various self-improvement frameworks.

However, a critical limitation persists: current self-training methods typically select training examples through random sampling or simple heuristics (e.g., filtering by correctness). This approach ignores a fundamental insight from developmental psychology—Vygotsky's Zone of Proximal Development (ZPD). The ZPD posits that learning is maximized when learners engage with tasks just beyond their current competence, neither too easy (providing no learning signal) nor too difficult (causing frustration and failure). This principle has been successfully operationalized in reinforcement learning through regret-based curricula such as PAIRED (Protagonist Antagonist Induced Regret Environment Design) and ACCEL (Adaptive Curriculum for Emergent Complexity in RL), which identify the learning frontier by measuring the gap between current and optimal performance.

Unfortunately, these regret-based methods require expensive rollouts across multiple policies—a computational burden incompatible with LLM training where each forward pass is costly. This gap between the theoretical promise of ZPD-based curricula and practical LLM self-training motivates our research.

### 1.2 Research Objectives

This research proposes **Confidence-Calibrated Regret (CCR)**, a novel single-pass metric that identifies ZPD-boundary examples for efficient LLM self-training. Our primary objectives are:

1. **Develop the CCR metric** that combines calibrated model confidence with verification outcomes to identify examples at the competence frontier—where the model is "confidently wrong" or "surprisingly correct."

2. **Establish a complete CCR-based curriculum pipeline** including confidence calibration, CCR computation, example selection, and iterative refinement.

3. **Empirically validate** that CCR-based curriculum selection achieves equivalent performance with 30-50% fewer training examples compared to random sampling in verifiable domains.

4. **Analyze the causal mechanism** through systematic ablations to understand how each component contributes to learning efficiency.

### 1.3 Significance

This research addresses a fundamental challenge in open-ended learning: how to efficiently identify and exploit the learning frontier without expensive multi-policy rollouts. The significance is threefold:

**Theoretical Contribution:** CCR bridges developmental psychology (ZPD), reinforcement learning (regret-based curricula), and LLM self-training, providing a unified framework for understanding optimal curriculum design.

**Practical Impact:** A 30-50% reduction in required training examples translates directly to reduced computational costs, faster iteration cycles, and more accessible self-improvement for resource-constrained practitioners.

**Open-Ended Learning Advancement:** By enabling more efficient self-improvement in verifiable domains, CCR contributes to the broader goal of creating agents that continuously expand their capabilities—a core aspiration of the ALOE workshop community.

## 2. Methodology

### 2.1 Problem Formulation

Consider an LLM $M_\theta$ with parameters $\theta$, operating in a verifiable domain (mathematics or code generation). Given a problem $x$, the model generates a solution $y = M_\theta(x)$ with associated confidence $c(x) \in [0,1]$. A verification oracle $V$ provides ground truth: $V(x,y) \in \{0,1\}$ indicating correctness.

**Goal:** Select a subset $S \subset D$ from a candidate pool $D$ of self-generated examples such that training on $S$ maximizes learning efficiency:

$$\text{Efficiency} = \frac{\Delta \text{Accuracy}_{\text{test}}}{|S|}$$

### 2.2 Confidence-Calibrated Regret (CCR) Metric

#### 2.2.1 Confidence Estimation

We combine two complementary confidence signals:

**Token-level confidence:** The geometric mean of token probabilities in the solution:
$$c_{\text{token}}(x) = \left(\prod_{t=1}^{T} p(y_t | y_{<t}, x)\right)^{1/T}$$

**Verbalized confidence:** Prompting the model to explicitly state its confidence:
$$c_{\text{verbal}}(x) = M_\theta(\text{"Rate your confidence in this solution from 0 to 1"} | x, y)$$

**Combined confidence:**
$$c_{\text{raw}}(x) = \gamma \cdot c_{\text{token}}(x) + (1-\gamma) \cdot c_{\text{verbal}}(x)$$

where $\gamma = 0.5$ by default.

#### 2.2.2 Confidence Calibration

Raw LLM confidence is typically poorly calibrated. We apply temperature scaling calibration:

$$c(x) = \sigma\left(\frac{\text{logit}(c_{\text{raw}}(x))}{T}\right)$$

where $T$ is learned on a held-out calibration set to minimize Expected Calibration Error (ECE):

$$\text{ECE} = \sum_{b=1}^{B} \frac{|B_b|}{N} \left| \text{acc}(B_b) - \text{conf}(B_b) \right|$$

We require ECE < 0.15 before proceeding to CCR computation.

#### 2.2.3 CCR Computation

The CCR score identifies examples at the ZPD boundary through two components:

**Confidently Wrong (CW):** High confidence but incorrect—indicates systematic misconceptions:
$$\text{CW}(x) = c(x) \cdot (1 - V(x, y))$$

**Surprisingly Correct (SC):** Low confidence but correct—indicates emerging competence:
$$\text{SC}(x) = (1 - c(x)) \cdot V(x, y)$$

**Combined CCR:**
$$\text{CCR}(x) = \alpha \cdot \text{CW}(x) + \beta \cdot \text{SC}(x)$$

where $\alpha, \beta > 0$ are hyperparameters controlling the balance. Default: $\alpha = \beta = 1.0$.

**Intuition:** High CCR examples represent the competence frontier—tasks where the model's internal representation conflicts with reality, providing maximal gradient information for learning.

### 2.3 Complete Algorithm

**Algorithm 1: CCR-Based Self-Training**

```
Input: Base model M_θ, task generator G, verification oracle V, 
       iterations K, examples per iteration N, selection ratio r
Output: Improved model M_θ*

1. Initialize: θ* ← θ

2. For k = 1 to K:
   
   # Phase 1: Task Generation
   3. D_k ← {} 
   4. For i = 1 to N:
   5.    x_i ← G(M_θ*)           # Generate task
   6.    y_i ← M_θ*(x_i)         # Generate solution
   7.    c_raw_i ← Confidence(M_θ*, x_i, y_i)
   8.    v_i ← V(x_i, y_i)       # Verify correctness
   9.    D_k ← D_k ∪ {(x_i, y_i, c_raw_i, v_i)}
   
   # Phase 2: Calibration
   10. D_cal, D_train ← Split(D_k, ratio=0.1)
   11. T ← LearnTemperature(D_cal)  # Minimize ECE
   12. Assert ECE(D_cal, T) < 0.15
   
   # Phase 3: CCR Computation & Selection
   13. For each (x, y, c_raw, v) in D_train:
   14.    c ← σ(logit(c_raw) / T)   # Calibrate
   15.    CCR(x) ← α·c·(1-v) + β·(1-c)·v
   16. S_k ← TopK(D_train, by=CCR, k=r·|D_train|)
   
   # Phase 4: Training
   17. θ* ← FineTune(θ*, S_k)      # Standard SFT on correct examples
                                    # or preference learning on pairs

3. Return M_θ*
```

### 2.4 Training Objective

For selected high-CCR examples, we employ two training strategies:

**Strategy A (SFT on Correct):** For surprisingly correct examples, standard supervised fine-tuning:
$$\mathcal{L}_{\text{SFT}} = -\sum_{(x,y) \in S_k: V(x,y)=1} \log p_\theta(y|x)$$

**Strategy B (DPO on Pairs):** For confidently wrong examples, we generate a corrected solution $y^+$ and apply Direct Preference Optimization:
$$\mathcal{L}_{\text{DPO}} = -\log \sigma\left(\beta \log \frac{p_\theta(y^+|x)}{p_{\text{ref}}(y^+|x)} - \beta \log \frac{p_\theta(y^-|x)}{p_{\text{ref}}(y^-|x)}\right)$$

### 2.5 Experimental Design

#### 2.5.1 Datasets and Domains

**Mathematical Reasoning:**
- GSM8K: 8,500 grade school math problems (train/test split)
- MATH: 12,500 competition mathematics problems across 7 categories

**Code Generation:**
- HumanEval: 164 Python programming problems
- MBPP: 974 Python programming problems

#### 2.5.2 Models

- **Primary:** Llama-3-8B-Instruct, Mistral-7B-Instruct
- **Ablation:** Llama-3-8B-Base (to test instruction-tuning effects)

#### 2.5.3 Baselines

1. **Random Sampling:** Uniform random selection from candidate pool
2. **Loss-Based Selection:** Select examples with highest training loss
3. **Uncertainty Sampling:** Select examples with highest entropy
4. **Correctness Filtering:** Train only on correct self-generated examples
5. **Difficulty Heuristics:** Select by problem length or complexity metrics

#### 2.5.4 Experimental Conditions

| Condition | Selection Method | Training Data |
|-----------|------------------|---------------|
| CCR-Full | CCR top-r% | High-CCR examples |
| CCR-CW | CW component only | Confidently wrong |
| CCR-SC | SC component only | Surprisingly correct |
| Random | Uniform random | Random subset |
| Loss | Highest loss | High-loss examples |
| Uncertainty | Highest entropy | High-uncertainty examples |

#### 2.5.5 Evaluation Metrics

**Primary Metrics:**
- **Learning Efficiency:** $\eta = \frac{\text{Accuracy}_{\text{final}} - \text{Accuracy}_{\text{initial}}}{N_{\text{training examples}}}$
- **Sample Efficiency Ratio:** Examples needed by baseline / Examples needed by CCR to reach target accuracy

**Secondary Metrics:**
- Expected Calibration Error (ECE) before and after training
- Pass@1 accuracy on held-out test sets
- Convergence speed (iterations to plateau)

**Statistical Analysis:**
- Paired t-tests across 5 random seeds per condition
- Significance threshold: $p < 0.05$ (one-tailed)
- Effect size: Cohen's d with 95% confidence intervals
- Sample size: $n \geq 15$ runs per condition for adequate power

#### 2.5.6 Ablation Studies

**A1: Calibration Necessity**
- Compare CCR with calibrated vs. raw confidence
- Hypothesis: Calibration is necessary for CCR effectiveness

**A2: Component Contribution**
- Compare CCR-Full vs. CCR-CW vs. CCR-SC
- Hypothesis: Both components contribute; full CCR outperforms either alone

**A3: Hyperparameter Sensitivity**
- Vary $\alpha/\beta$ ratio: {0.5, 1.0, 2.0}
- Vary selection ratio $r$: {0.1, 0.2, 0.3, 0.5}

**A4: Iterative Refinement**
- Compare single-round vs. multi-round CCR training
- Hypothesis: Iterative refinement enables continued improvement

### 2.6 Implementation Details

- **Framework:** PyTorch + HuggingFace Transformers
- **Fine-tuning:** LoRA (rank=16, alpha=32) for efficiency
- **Batch size:** 8 with gradient accumulation to effective batch 32
- **Learning rate:** 2e-5 with cosine decay
- **Training epochs:** 3 per iteration
- **Hardware:** 4× A100 80GB GPUs

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

**Primary Outcome (P1):** We expect CCR-based curriculum selection to achieve equivalent held-out accuracy with **30-50% fewer training examples** compared to random sampling. Specifically:
- On GSM8K: Reaching 70% accuracy with ~3,500 examples (CCR) vs. ~5,000 examples (random)
- On MATH: Reaching 35% accuracy with ~7,000 examples (CCR) vs. ~10,000 examples (random)

**Secondary Outcomes:**
- **P2 (Calibration Improvement):** Training on high-CCR examples will reduce ECE by ≥20%, as the model learns to better distinguish its competence boundaries
- **P3 (Sustained Improvement):** Iterative CCR refinement will enable continued improvement beyond single-round training plateaus, demonstrating open-ended learning dynamics

### 3.2 Theoretical Contributions

1. **Unified Framework:** CCR bridges ZPD theory, regret-based RL curricula, and LLM self-training into a coherent theoretical framework
2. **Single-Pass Regret Proxy:** Demonstrates that confidence-correctness relationships can approximate multi-policy regret without expensive rollouts
3. **Calibration-Curriculum Connection:** Establishes that confidence calibration is not merely a reliability concern but a prerequisite for effective curriculum design

### 3.3 Practical Impact

1. **Computational Efficiency:** 30-50% reduction in training examples directly reduces GPU hours, carbon footprint, and financial costs
2. **Accessibility:** More efficient self-training democratizes LLM improvement for resource-constrained researchers
3. **Deployment Pipeline:** CCR can be integrated into production self-improvement pipelines for continuously deployed models

### 3.4 Broader Impact on Open-Ended Learning

This research advances the ALOE workshop's core mission by:

1. **Practical OEL Metrics:** CCR provides a measurable, actionable metric for identifying the learning frontier—addressing the workshop's call for "practical measures of open-endedness aligned with capability emergence"

2. **Efficient Curriculum Learning:** By exploiting substructure in the problem space (the ZPD boundary), CCR enables more efficient training of generally-capable agents

3. **Self-Improving Systems:** The iterative CCR refinement loop demonstrates a concrete mechanism for sustained self-improvement, contributing to understanding of "self-fulfilling learning dynamics" in deployed models

### 3.5 Limitations and Future Work

**Limitations:**
- Restricted to verifiable domains with ground-truth oracles
- Calibration overhead adds ~10% computational cost
- Hyperparameters ($\alpha$, $\beta$) may require domain-specific tuning

**Future Directions:**
1. Extending CCR to open-ended generation via learned reward models
2. Multi-agent CCR for population-based training
3. Theoretical analysis connecting CCR to information-theoretic learning bounds
4. Application to real-world deployed systems with human feedback

### 3.6 Conclusion

Confidence-Calibrated Regret offers a principled, efficient approach to curriculum design for LLM self-training. By operationalizing the Zone of Proximal Development through calibrated confidence and verification outcomes, CCR identifies the learning frontier without expensive multi-policy rollouts. Our comprehensive experimental design will validate the hypothesis that ZPD-boundary training maximizes learning efficiency, contributing both theoretical insights and practical tools to the open-ended learning community.