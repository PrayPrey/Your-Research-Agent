# Research Proposal: Contrastive Molecular Goal-Conditioned RL: Bridging Representation Learning and Sample-Efficient Molecular Design via HER-Style Property Relabeling

## 1. Introduction

### 1.1 Background

Goal-conditioned reinforcement learning (GCRL) represents a paradigm shift in how agents learn to achieve desired outcomes. Rather than optimizing hand-crafted reward functions, GCRL enables specification of goals through observations or target states, making it particularly attractive for domains where reward engineering is challenging. Recent theoretical advances have established profound connections between GCRL and contrastive representation learning, with Eysenbach et al. (2022) proving that optimal goal-conditioned value functions can be expressed as inner products of learned representations: $V(s, g) = \phi(s)^\top \psi(g)$. This equivalence has opened new avenues for leveraging self-supervised learning techniques within reinforcement learning frameworks.

Molecular design presents a compelling application domain for GCRL. Drug discovery requires generating molecules with specific properties—binding affinity, solubility, toxicity profiles—that are naturally expressed as goals rather than reward functions. However, current molecular generation methods face severe sample inefficiency challenges. The discrete, combinatorial nature of molecular graphs creates sparse reward landscapes where random exploration rarely discovers molecules satisfying target properties. Standard RL approaches may require millions of molecular evaluations, each potentially involving expensive computational simulations or experimental assays.

Hindsight Experience Replay (HER), introduced by Andrychowicz et al. (2017), revolutionized sample efficiency in robotics by relabeling failed trajectories with achieved states as new goals. This creates an implicit curriculum where every experience provides learning signal, achieving 10-100x efficiency improvements in manipulation tasks. However, HER's application to molecular design remains unexplored, primarily because the contrastive-GCRL equivalence has only been established for continuous state spaces, while molecules exist as discrete graph structures.

Recent advances in molecular representation learning provide a potential bridge. UniCorn (2024) demonstrated that multi-view contrastive learning on molecular graphs achieves state-of-the-art performance across quantum mechanical, physicochemical, and biological property prediction tasks. This suggests that graph neural networks (GNNs) can learn representations capturing property-relevant molecular features, potentially enabling the continuous embedding space required for the contrastive-GCRL equivalence.

### 1.2 Research Objectives

This research proposes CM-GCRL (Contrastive Molecular Goal-Conditioned RL), a novel framework that:

1. **Extends the contrastive-GCRL equivalence to discrete molecular graphs** by training GNN molecular encoders $\phi(\text{mol})$ and property encoders $\psi(\text{prop})$ such that their inner product approximates goal-conditioned value functions.

2. **Enables HER-style property relabeling for molecular generation** by leveraging the learned value function to relabel failed molecular generations with their achieved properties as new goals.

3. **Introduces confidence-weighted relabeling** to prevent noise corruption from uncertain property predictions, ensuring robust learning despite predictor limitations.

### 1.3 Research Significance

This work addresses a critical gap at the intersection of representation learning, goal-conditioned RL, and molecular design. The theoretical contribution establishes whether the contrastive-GCRL equivalence—proven for continuous spaces—extends to graph-structured data through appropriate neural network architectures. The practical contribution enables sample-efficient multi-property molecular optimization, potentially accelerating drug discovery pipelines by reducing the number of expensive property evaluations required.

The research directly addresses key workshop themes: connections between GCRL and representation learning, algorithmic improvements enabling broader applications, and novel applications of goal-conditioned decision making in molecular discovery where GCRL is not yet mainstream.

## 2. Methodology

### 2.1 Problem Formulation

We formulate molecular property optimization as a goal-conditioned Markov Decision Process (MDP). Let $\mathcal{M}$ denote the space of valid molecules represented as graphs $G = (V, E, X)$ where $V$ is the atom set, $E$ is the bond set, and $X$ contains atom/bond features. Let $\mathcal{P} \subset \mathbb{R}^d$ denote the property space (e.g., binding affinity, LogP, solubility).

The goal-conditioned MDP is defined as:
- **States**: Partial or complete molecular graphs $s \in \mathcal{M}$
- **Actions**: Graph modifications (atom addition, bond formation, fragment attachment)
- **Goals**: Target property vectors $g \in \mathcal{P}$
- **Reward**: $r(s, g) = \mathbb{1}[\|p(s) - g\| < \epsilon]$ where $p(s)$ returns the properties of molecule $s$

The objective is to learn a goal-conditioned policy $\pi(a|s, g)$ that generates molecules achieving target properties with minimal samples.

### 2.2 CM-GCRL Architecture

#### 2.2.1 Graph Neural Network Molecular Encoder

We employ an equivariant GNN encoder $\phi: \mathcal{M} \rightarrow \mathbb{R}^{d_\phi}$ based on SchNet or DimeNet architecture. For a molecular graph $G$, the encoder computes:

$$h_i^{(l+1)} = h_i^{(l)} + \sum_{j \in \mathcal{N}(i)} W^{(l)} \cdot \text{filter}(r_{ij}) \odot h_j^{(l)}$$

where $h_i^{(l)}$ is the hidden representation of atom $i$ at layer $l$, $\mathcal{N}(i)$ denotes neighbors, $r_{ij}$ is the interatomic distance, and $\text{filter}(\cdot)$ is a continuous filter convolution. Graph-level representation is obtained via attention-weighted pooling:

$$\phi(G) = \sum_{i \in V} \alpha_i h_i^{(L)}, \quad \alpha_i = \frac{\exp(w^\top h_i^{(L)})}{\sum_j \exp(w^\top h_j^{(L)})}$$

#### 2.2.2 Property Encoder

The property encoder $\psi: \mathcal{P} \rightarrow \mathbb{R}^{d_\psi}$ maps target property vectors to the same embedding space:

$$\psi(g) = \text{MLP}(g) = W_2 \cdot \text{ReLU}(W_1 g + b_1) + b_2$$

For multi-property goals, we use property-specific encoders with shared final layers to capture property interactions.

#### 2.2.3 Contrastive Learning Objective

We train encoders via InfoNCE loss to establish the contrastive-GCRL equivalence. For a batch of $N$ molecule-property pairs $\{(m_i, p_i)\}_{i=1}^N$:

$$\mathcal{L}_{\text{InfoNCE}} = -\frac{1}{N} \sum_{i=1}^N \log \frac{\exp(\phi(m_i)^\top \psi(p_i) / \tau)}{\sum_{j=1}^N \exp(\phi(m_i)^\top \psi(p_j) / \tau)}$$

where $\tau$ is the temperature parameter. This objective encourages $\phi(m)^\top \psi(p) \approx V(m, p)$, where high values indicate the molecule $m$ achieves property goal $p$.

### 2.3 HER-Style Property Relabeling

#### 2.3.1 Standard HER Adaptation

For each molecular generation trajectory $\{s_0, a_0, s_1, ..., s_T\}$ targeting goal $g$, we store transitions $(s_t, a_t, s_{t+1}, g)$ in replay buffer $\mathcal{B}$. With probability $k$ (relabeling ratio), we additionally store relabeled transitions:

$$(s_t, a_t, s_{t+1}, g') \quad \text{where} \quad g' = p(s_T)$$

Here $p(s_T)$ is the achieved property of the final molecule, creating positive reward signal even for "failed" generations.

#### 2.3.2 Confidence-Weighted Relabeling

Property predictions carry uncertainty. Let $\hat{p}(s)$ denote the predicted properties with confidence $c(s) \in [0, 1]$ (obtained via ensemble disagreement or MC dropout). We only relabel when confidence exceeds threshold $\tau$:

$$\text{Relabel}(s_T) = \begin{cases} \hat{p}(s_T) & \text{if } c(s_T) \geq \tau \\ \text{skip} & \text{otherwise} \end{cases}$$

The effective relabeling probability becomes $k \cdot \mathbb{P}[c(s_T) \geq \tau]$.

### 2.4 Training Algorithm

**Algorithm 1: CM-GCRL Training**

```
Input: QM9 dataset D, relabeling ratio k, confidence threshold τ
Initialize: GNN encoder φ, property encoder ψ, policy π, replay buffer B

# Phase 1: Contrastive Pre-training
For epoch = 1 to E_pretrain:
    Sample batch {(m_i, p_i)} from D
    Compute L_InfoNCE and update φ, ψ

# Phase 2: Goal-Conditioned RL with HER
For episode = 1 to E_train:
    Sample goal g ~ P(g)
    Generate trajectory τ = {s_0, a_0, ..., s_T} using π(·|s, g)
    
    # Standard transitions
    For t = 0 to T-1:
        Store (s_t, a_t, s_{t+1}, g, r_t) in B
    
    # HER relabeling with confidence
    If random() < k and c(s_T) ≥ τ:
        g' = p̂(s_T)
        For t = 0 to T-1:
            Store (s_t, a_t, s_{t+1}, g', r'_t) in B
    
    # Policy update
    Sample minibatch from B
    Update π using SAC with V(s,g) = φ(s)ᵀψ(g)
    
    # Contrastive fine-tuning
    Update φ, ψ with L_InfoNCE on generated molecules

Output: Trained policy π, encoders φ, ψ
```

### 2.5 Experimental Design

#### 2.5.1 Datasets and Benchmarks

- **Pre-training**: QM9 dataset (134,000 molecules with quantum mechanical properties)
- **Evaluation**: GuacaMol benchmark suite (goal-directed generation tasks)
- **Properties**: LogP, QED, binding affinity (DRD2), solubility, synthetic accessibility

#### 2.5.2 Baselines

1. **Standard RL**: SAC without HER relabeling
2. **Mol-AIR (2024)**: State-of-the-art molecular RL with intrinsic rewards
3. **GFlowNets (2023)**: Flow-based generative model for multi-objective optimization
4. **Random Search**: Uniform sampling from molecular space

#### 2.5.3 Ablation Studies

| Ablation | Configuration | Tests |
|----------|--------------|-------|
| A1: No contrastive | Remove $\mathcal{L}_{\text{InfoNCE}}$, use MLP value function | Contrastive equivalence necessity |
| A2: No HER | Set $k = 0$ | HER contribution |
| A3: No confidence | Set $\tau = 0$ | Confidence thresholding effect |
| A4: Relabeling ratio | $k \in \{0.25, 0.5, 0.8\}$ | Optimal relabeling rate |

#### 2.5.4 Evaluation Metrics

**Primary Metrics:**
- **Sample Efficiency**: Number of molecules generated to achieve 80% goal success rate
- **Goal Achievement Rate**: Fraction of generated molecules within $\epsilon$ of target properties
- **Molecular Validity**: Percentage of chemically valid molecules

**Secondary Metrics:**
- **Diversity**: Tanimoto diversity among successful molecules
- **Novelty**: Fraction not in training set
- **Pareto Hypervolume**: Coverage of multi-property Pareto front

#### 2.5.5 Statistical Analysis

- **Runs**: 20 independent runs per configuration with different random seeds
- **Tests**: Paired t-test with Bonferroni correction ($\alpha = 0.017$)
- **Effect Size**: Cohen's d with 95% confidence intervals
- **Power Analysis**: Minimum detectable effect size 0.8 with power 0.8

### 2.6 Verification of Core Hypothesis

**SH1 (Existence Test)**: Compute Pearson correlation between $\phi(m)^\top \psi(p)$ and actual goal achievement across 10,000 molecule-property pairs. Success criterion: $r > 0.5$ with $p < 0.001$.

**SH2 (Mechanism Test)**: Sequential ablations testing each causal step:
- H-M1: Compare learned vs. random GNN representations
- H-M2: Verify $\phi(m)^\top \psi(p)$ predicts goal achievement better than MLP
- H-M3: Compare HER vs. no-HER sample efficiency
- H-M4: Compare $\tau > 0$ vs. $\tau = 0$ on noisy property predictions

**SH3 (Comparison Test)**: Head-to-head evaluation against baselines on GuacaMol tasks.

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

Based on our hypothesis and supporting evidence, we predict:

1. **Sample Efficiency (P1)**: CM-GCRL will achieve 80% goal success using $\geq 30\%$ fewer molecular generations than standard RL. This prediction is grounded in HER's demonstrated 10-100x improvements in robotics, moderated by the additional challenges of discrete molecular spaces.

2. **Molecular Validity (P2)**: Generated molecules will maintain $> 85\%$ chemical validity, as the GNN architecture inherently respects molecular graph constraints.

3. **Multi-Property Optimization (P3)**: CM-GCRL will achieve superior Pareto front coverage compared to single-objective baselines, as HER naturally creates diverse goal distributions during training.

4. **Contrastive Equivalence Validation**: We expect correlation $r > 0.5$ between $\phi(m)^\top \psi(p)$ and goal achievement, validating extension of the theoretical equivalence to molecular graphs.

### 3.2 Theoretical Impact

This research establishes whether the contrastive-GCRL equivalence—a fundamental result connecting representation learning and reinforcement learning—extends beyond continuous state spaces to discrete graph-structured data. A positive result would:

- Provide theoretical foundations for GCRL in combinatorial domains
- Enable transfer of advances in graph representation learning to goal-conditioned decision making
- Open new research directions connecting GNN architectures with value function approximation

### 3.3 Practical Impact

**Drug Discovery**: Sample-efficient multi-property optimization could accelerate lead optimization by reducing expensive computational or experimental evaluations. The ability to specify goals as property vectors rather than reward functions makes the approach accessible to medicinal chemists without RL expertise.

**Broader Applications**: The methodology generalizes to other graph-structured goal-conditioned problems: materials design, chemical reaction optimization, and molecular synthesis planning.

### 3.4 Limitations and Future Work

**Limitations**:
- Reliance on property predictor accuracy and calibration
- Computational overhead of GNN + contrastive + RL pipeline
- Limited to chemical space covered by training distribution

**Future Directions**:
- Extension to protein-ligand binding with 3D structural goals
- Integration with active learning for experimental validation
- Application to synthesis-aware molecular generation

### 3.5 Conclusion

CM-GCRL represents a principled approach to bridging representation learning and goal-conditioned reinforcement learning for molecular design. By establishing the contrastive-GCRL equivalence for graph-structured molecules and enabling HER-style relabeling, we address the critical sample efficiency bottleneck in computational drug discovery. The proposed methodology, grounded in theoretical foundations and validated through rigorous experimental design, promises both scientific insights into GCRL's applicability to discrete domains and practical advances in multi-property molecular optimization.