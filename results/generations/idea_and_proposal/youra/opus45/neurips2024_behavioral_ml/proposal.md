# Research Proposal: Soft Differentiable Cognitive Constraint Layers: Integrating ACT-R Memory Equations into Transformers for Human-Aligned Learning

## 1. Introduction

### 1.1 Background

Machine learning systems increasingly rely on human-generated data across diverse application domains, from natural language processing to decision-making systems. However, these systems typically treat human data as statistical patterns to be learned, without explicitly modeling the underlying cognitive processes that generate such data. This disconnect creates a fundamental gap: neural networks lack psychologically-grounded inductive biases, often leading to inefficient learning, non-human-like behavior patterns, and reduced interpretability.

The behavioral sciences, particularly cognitive psychology and cognitive science, have developed rich theoretical frameworks describing human cognition. Among the most influential is ACT-R (Adaptive Control of Thought-Rational), a cognitive architecture developed over four decades that provides validated mathematical models of human memory, attention, and decision-making. ACT-R's declarative memory module, for instance, uses precise equations to model how memory activation decays over time and how retrieval depends on contextual associations. These equations have been validated against extensive human behavioral data across hundreds of studies.

Despite this wealth of validated cognitive models, a significant technical barrier prevents their integration with modern deep learning: cognitive architectures like ACT-R are fundamentally symbolic systems, operating through discrete production rules and explicit memory retrievals. This symbolic nature makes them incompatible with gradient-based optimization, the cornerstone of contemporary neural network training. Consequently, the machine learning community has largely developed memory-augmented neural networks (such as Neural Turing Machines and Differentiable Neural Computers) using generic, psychologically-ungrounded memory mechanisms.

### 1.2 Research Objectives

This research proposes to bridge the gap between cognitive architectures and deep learning by developing **Soft Differentiable Cognitive Constraint Layers (S-DCCLs)**—PyTorch modules that implement soft, differentiable approximations of ACT-R's memory equations. Our primary objectives are:

1. **Technical Objective:** Design and implement differentiable approximations of ACT-R's declarative memory activation equation and capacity-limited working memory mechanisms as composable neural network modules.

2. **Empirical Objective:** Demonstrate that S-DCCL-augmented transformers achieve significant sample efficiency improvements (≥20% reduction in training samples to reach target accuracy) on working memory tasks compared to standard transformers with matched parameter counts.

3. **Behavioral Alignment Objective:** Validate that S-DCCL models produce error patterns that correlate positively (r > 0.5) with human behavioral data, indicating that the cognitive constraints induce human-like processing characteristics.

4. **Interpretability Objective:** Show that the internal states of S-DCCL modules (memory activations, slot contents) provide interpretable representations of cognitive processes.

### 1.3 Significance

This research addresses a critical need identified by the Workshop on Behavioral Machine Learning: converting qualitative insights from behavioral sciences into computational models suitable for integration with machine learning systems. The significance of this work spans multiple dimensions:

**Theoretical Significance:** This work establishes the first systematic framework for translating cognitive architecture equations into differentiable neural modules. By demonstrating that ACT-R's mathematical formulations can be approximated while preserving their qualitative properties, we open a pathway for incorporating decades of cognitive science research into modern AI systems.

**Practical Significance:** Improved sample efficiency directly translates to reduced computational costs and data requirements. For applications in intelligent tutoring systems, assistive AI, and cognitive assessment tools, models that exhibit human-like behavior patterns are more predictable, trustworthy, and effective in human-AI interaction scenarios.

**Methodological Significance:** The S-DCCL module library provides reusable components that can be integrated with various neural architectures, enabling researchers across AI, robotics, and HCI to incorporate cognitive constraints without requiring deep expertise in cognitive architectures.

## 2. Methodology

### 2.1 S-DCCL Module Design

We propose two core S-DCCL modules that implement soft approximations of ACT-R's memory mechanisms:

#### 2.1.1 DCCLMemory: Activation-Based Retrieval

The DCCLMemory module implements a differentiable approximation of ACT-R's base-level learning equation. In ACT-R, the activation $A_i$ of a memory chunk $i$ is computed as:

$$A_i = B_i + \sum_j W_j S_{ji}$$

where $B_i$ is the base-level activation reflecting recency and frequency of access, $W_j$ represents attentional weights, and $S_{ji}$ captures associative strengths.

We approximate the base-level activation dynamics using exponential trace decay:

$$A_i(t+1) = \lambda A_i(t) + (1-\lambda) \cdot \text{access}_i(t)$$

where $\lambda \in [0.9, 0.99]$ is the decay rate and $\text{access}_i(t) \in \{0, 1\}$ indicates whether item $i$ was accessed at time $t$. This exponential approximation, while simpler than ACT-R's power-law forgetting, preserves the critical qualitative property that recently and frequently accessed items maintain higher activation.

The retrieval probability is computed via softmax over activations:

$$P(\text{retrieve } i) = \frac{\exp(A_i / \tau)}{\sum_k \exp(A_k / \tau)}$$

where $\tau$ is a temperature parameter controlling retrieval noise, analogous to ACT-R's activation noise parameter.

**PyTorch Implementation:**
```python
class DCCLMemory(nn.Module):
    def __init__(self, memory_size, hidden_dim, decay_rate=0.95, temperature=1.0):
        super().__init__()
        self.memory_size = memory_size
        self.decay_rate = decay_rate
        self.temperature = temperature
        self.memory = nn.Parameter(torch.zeros(memory_size, hidden_dim))
        self.activations = None
    
    def forward(self, query, access_mask=None):
        # Update activations with decay
        if self.activations is None:
            self.activations = torch.zeros(self.memory_size)
        self.activations = self.decay_rate * self.activations
        if access_mask is not None:
            self.activations = self.activations + (1 - self.decay_rate) * access_mask
        
        # Compute retrieval weights
        similarities = torch.matmul(query, self.memory.T)
        retrieval_logits = similarities + self.activations
        retrieval_weights = F.softmax(retrieval_logits / self.temperature, dim=-1)
        
        return torch.matmul(retrieval_weights, self.memory)
```

#### 2.1.2 DCCLWorkingMemory: Capacity-Limited Storage

The DCCLWorkingMemory module implements a K-slot working memory buffer with competitive inhibition, reflecting Cowan's (2001) finding that human working memory capacity is limited to approximately 4±1 items.

The module maintains $K$ memory slots $\{s_1, ..., s_K\}$, each with an associated gating activation $g_k$. When new information $x$ arrives, slot selection uses competitive softmax:

$$\alpha_k = \frac{\exp(g_k / \tau)}{\sum_{j=1}^K \exp(g_j / \tau)}$$

The update rule combines new information with existing slot contents:

$$s_k \leftarrow \alpha_k \cdot x + (1 - \alpha_k) \cdot s_k$$

This soft selection mechanism ensures differentiability while approximating the discrete slot-based storage of human working memory. The competitive inhibition forces selective retention: storing new information necessarily reduces the fidelity of existing contents.

**PyTorch Implementation:**
```python
class DCCLWorkingMemory(nn.Module):
    def __init__(self, num_slots, slot_dim, temperature=1.0):
        super().__init__()
        self.num_slots = num_slots
        self.slots = nn.Parameter(torch.zeros(num_slots, slot_dim))
        self.gate_network = nn.Linear(slot_dim, num_slots)
        self.temperature = temperature
    
    def forward(self, input_item):
        # Compute slot selection probabilities
        gate_logits = self.gate_network(input_item)
        selection_probs = F.softmax(gate_logits / self.temperature, dim=-1)
        
        # Update slots with competitive writing
        update = torch.outer(selection_probs, input_item)
        retention = 1 - selection_probs.unsqueeze(-1)
        self.slots.data = retention * self.slots + update
        
        # Read from all slots weighted by activation
        return torch.matmul(selection_probs, self.slots)
```

### 2.2 Integration with Transformer Architecture

S-DCCL modules are integrated into a standard transformer encoder architecture as additional layers. Specifically:

1. **Input Embedding:** Standard token embedding + positional encoding
2. **Transformer Layers:** $L$ standard transformer encoder layers
3. **S-DCCL Integration Point:** After transformer layers, outputs are processed through:
   - DCCLWorkingMemory for capacity-limited storage
   - DCCLMemory for activation-based retrieval
4. **Output Head:** Task-specific classification layer

The complete forward pass for an N-back task:

$$h = \text{TransformerEncoder}(\text{Embed}(x))$$
$$m_{wm} = \text{DCCLWorkingMemory}(h)$$
$$m_{ret} = \text{DCCLMemory}(h, \text{access\_mask})$$
$$y = \text{Classifier}([h; m_{wm}; m_{ret}])$$

### 2.3 Experimental Design

#### 2.3.1 Task: N-back Working Memory

We use the N-back task, a canonical working memory paradigm extensively studied in cognitive psychology and validated with ACT-R models. Participants (or models) view a sequence of stimuli and must indicate whether the current stimulus matches the one presented N positions earlier.

**Task Parameters:**
- N-back levels: N ∈ {2, 3, 4}
- Sequence length: 20 items per trial
- Stimulus set: 8 distinct letters
- Target probability: 30% (standard in human studies)
- Lure trials: 20% (items matching N±1 positions, known to cause human errors)

**Dataset Generation:**
We generate synthetic N-back sequences following the protocols of Jaeggi et al. (2010), ensuring matched difficulty across conditions. Training sets contain 10,000 sequences; validation and test sets contain 1,000 sequences each.

#### 2.3.2 Model Configurations

| Model | Architecture | Parameters | S-DCCL Modules |
|-------|-------------|------------|----------------|
| Baseline Transformer | 4 layers, 256 dim, 4 heads | ~2.1M | None |
| S-DCCL Transformer | 3 layers, 256 dim, 4 heads | ~2.1M | DCCLMemory + DCCLWorkingMemory |
| Ablation: Memory Only | 3.5 layers, 256 dim | ~2.1M | DCCLMemory only |
| Ablation: WM Only | 3.5 layers, 256 dim | ~2.1M | DCCLWorkingMemory only |

Parameter counts are matched by adjusting the number of transformer layers, ensuring fair comparison.

#### 2.3.3 Training Protocol

- **Optimizer:** AdamW with weight decay 0.01
- **Learning Rate:** 1e-4 with cosine annealing
- **Batch Size:** 64
- **Maximum Epochs:** 100 (early stopping with patience 10)
- **Random Seeds:** 5 seeds per condition for statistical reliability
- **S-DCCL Hyperparameters:** 
  - Decay rate $\lambda$: initialized at 0.95, learnable
  - Working memory slots $K$: tested at {4, 7, 12}
  - Temperature $\tau$: annealed from 1.0 to 0.1 during training

### 2.4 Evaluation Metrics

#### 2.4.1 Primary Metrics

**Sample Efficiency Ratio:**
$$\text{SER} = \frac{\text{Samples}_{\text{baseline}}}{\text{Samples}_{\text{S-DCCL}}}$$

where samples are counted to reach 90% accuracy on the validation set. Hypothesis predicts SER ≥ 1.25.

**Behavioral Alignment Correlation:**
We compute Pearson correlation between model and human error patterns across:
- Serial position (primacy/recency effects)
- Lure confusion rates (N±1 false alarms)
- Target detection sensitivity (d')

Human behavioral data sourced from Kane et al. (2007) N-back study (N=236 participants).

#### 2.4.2 Secondary Metrics

**Capacity Scaling Analysis:**
Measure accuracy degradation from 2-back to 4-back:
$$\Delta_{\text{capacity}} = \text{Acc}_{2\text{-back}} - \text{Acc}_{4\text{-back}}$$

Compare model $\Delta_{\text{capacity}}$ to human data (expected: ~15-20% drop).

**Interpretability Score:**
For correct trials, compute the proportion where the target item (N positions back) has the highest activation among working memory slots:
$$\text{InterpScore} = \frac{1}{|T|}\sum_{t \in T} \mathbb{1}[\text{argmax}_k(A_k) = \text{target position}]$$

### 2.5 Statistical Analysis Plan

**Primary Analysis (P1 - Sample Efficiency):**
- Test: One-tailed paired t-test
- H₀: μ_SER ≤ 1.0; H₁: μ_SER > 1.25
- α = 0.0125 (Bonferroni corrected for 4 tests)
- Effect size: Cohen's d

**Secondary Analysis (P2 - Behavioral Alignment):**
- Test: Pearson correlation with Fisher z-transformation for confidence intervals
- H₀: ρ ≤ 0; H₁: ρ > 0.5
- α = 0.0125

**Interaction Analysis (P3 - Capacity Scaling):**
- Test: 2×3 mixed ANOVA (Model Type × N-back Level)
- Focus: Interaction effect indicating differential scaling
- α = 0.0125

**Interpretability Analysis (P4):**
- Test: One-sample t-test against chance (50%)
- H₀: μ_InterpScore = 0.5; H₁: μ_InterpScore > 0.8
- α = 0.0125

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

Based on our theoretical analysis and preliminary investigations, we anticipate the following outcomes:

**Primary Outcome (Sample Efficiency):** We expect S-DCCL-augmented transformers to achieve 90% accuracy on 2-back tasks using approximately 75-80% of the training samples required by baseline transformers, yielding a sample efficiency ratio of 1.25-1.33. This improvement stems from the restricted hypothesis space imposed by cognitive constraints—the model need not learn arbitrary memory strategies but is guided toward human-like recency-weighted, capacity-limited processing.

**Behavioral Alignment:** We predict error pattern correlations of r > 0.5 with human data, particularly for:
- Lure confusion rates (false alarms to N±1 items)
- Serial position effects (reduced accuracy for middle positions)
- Capacity-dependent accuracy degradation

**Capacity Scaling:** The S-DCCL model with K=4 slots should exhibit accuracy drops from 2-back to 4-back comparable to human participants (~15-20%), while baseline transformers with unconstrained memory may show flatter degradation curves (~5-10%).

**Interpretability:** We expect >80% of correct trials to show highest activation for the target position, providing transparent insight into the model's decision process.

### 3.2 Potential Challenges and Mitigations

| Challenge | Likelihood | Mitigation Strategy |
|-----------|------------|---------------------|
| Soft approximations lose critical ACT-R properties | Medium | Validate qualitative properties (recency effect, capacity limit) before full experiments |
| Gradient flow issues through S-DCCL modules | Low | Use straight-through estimators if needed; extensive gradient monitoring |
| Hyperparameter sensitivity (λ, K, τ) | Medium | Systematic hyperparameter search; sensitivity analysis |
| Human behavioral data variability | Low | Use multiple published datasets; report confidence intervals |

### 3.3 Broader Impact

**Scientific Impact:** This research establishes a new paradigm for integrating cognitive science with deep learning. By demonstrating that cognitive constraints can be implemented as differentiable modules, we enable the machine learning community to leverage decades of behavioral science research. The S-DCCL framework can be extended to other ACT-R modules (procedural memory, goal management) and potentially other cognitive architectures (SOAR, EPIC).

**Practical Applications:**

1. **Intelligent Tutoring Systems:** Models with human-like memory constraints can better predict student learning trajectories and optimize instructional sequencing.

2. **Assistive AI:** Systems exhibiting predictable, human-like error patterns are more trustworthy and easier for users to calibrate their expectations.

3. **Cognitive Assessment:** S-DCCL models could serve as computational baselines for clinical assessment of working memory deficits, with interpretable internal states aiding diagnosis.

4. **Human-Robot Interaction:** Robots with cognitively-grounded memory systems may exhibit more natural, predictable behavior in collaborative tasks.

**Alignment Implications:** By constraining AI systems to operate within human cognitive bounds, S-DCCLs represent a step toward AI systems that are inherently more aligned with human capabilities and limitations. This "cognitive alignment" complements value alignment efforts by ensuring AI behavior remains within human-comprehensible bounds.

### 3.4 Future Directions

This research opens several avenues for future investigation:

1. **Extended Cognitive Modules:** Implement S-DCCL versions of ACT-R's procedural memory (production rules as soft attention over action templates) and goal stack (hierarchical task management).

2. **Personalization:** Learn individual-specific parameters (decay rates, capacity limits) to model cognitive differences across users.

3. **Multi-Modal Extension:** Apply S-DCCL constraints to vision-language models for tasks requiring visual working memory.

4. **Theoretical Analysis:** Formally characterize the inductive bias imposed by S-DCCL constraints using PAC-learning or information-theoretic frameworks.

5. **Clinical Applications:** Validate S-DCCL models against patient populations with known working memory deficits (ADHD, schizophrenia) to assess clinical utility.

In conclusion, this research proposes a principled methodology for bridging cognitive architectures and deep learning, with concrete empirical validation on working memory tasks. By demonstrating that psychologically-grounded constraints improve both efficiency and behavioral alignment, we contribute to the broader goal of developing AI systems that are not only capable but also comprehensible and compatible with human cognition.