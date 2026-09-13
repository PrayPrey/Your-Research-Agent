# Research Proposal: Uncertainty-Aware Neural Scene Graphs for Interpretable End-to-End Driving

## 1. Introduction

### Background

Autonomous driving represents one of the most challenging applications of machine learning, requiring systems to perceive complex environments, predict the behavior of multiple agents, and plan safe trajectories—all in real-time under safety-critical constraints. Recent years have witnessed remarkable progress in end-to-end driving approaches that learn direct mappings from sensory inputs to control actions. However, these models often operate as "black boxes," making it difficult to understand their decision-making processes, diagnose failure modes, and ensure safety in deployment scenarios.

Traditional modular autonomous driving stacks decompose the problem into perception, prediction, and planning components with well-defined interfaces. While interpretable, these systems suffer from error propagation and suboptimal information transfer between modules. The emerging paradigm of end-to-end learning promises to overcome these limitations by jointly optimizing all components, yet sacrifices the interpretability that is crucial for debugging, validation, and regulatory approval.

Scene graphs have emerged as a promising intermediate representation that captures the relational structure of driving environments. Recent work such as GraphAD demonstrates that Interaction Scene Graphs (ISG) can effectively model relationships among ego-vehicles, road agents, and map elements, improving performance across perception, prediction, and planning tasks. However, existing scene graph approaches lack principled uncertainty quantification—a critical capability for safety-critical autonomous systems.

Concurrently, research on uncertainty-aware planning, exemplified by SUPER-AD, has shown that incorporating aleatoric uncertainty estimates into planning modules significantly improves robustness and safety. Yet these approaches typically operate on dense feature maps rather than structured representations, limiting interpretability.

### Research Objectives

This research proposes **Probabilistic Neural Scene Graphs (PNSG)**, a novel intermediate representation that synergistically combines the interpretability of structured scene graphs with rigorous uncertainty quantification. Our specific objectives are:

1. **Develop a perception module** that extracts scene graph nodes with calibrated uncertainty estimates using evidential deep learning
2. **Design a probabilistic graph construction mechanism** that represents relationships with uncertainty-aware edge weights
3. **Formulate uncertainty propagation methods** through graph neural network layers using tractable approximations
4. **Integrate uncertainty-conditioned planning** that enables graceful degradation under high uncertainty
5. **Validate the framework** on established benchmarks, demonstrating improved interpretability, out-of-distribution detection, and safety metrics

### Significance

This research addresses a critical gap at the intersection of interpretability and uncertainty quantification in autonomous driving. By providing auditable decision-making with principled uncertainty estimates, PNSG directly addresses key barriers to regulatory approval and real-world deployment. The framework enables developers to understand *why* the system made particular decisions and *how confident* it is in those decisions—capabilities essential for building trust and ensuring safety.

## 2. Methodology

### 2.1 System Overview

The PNSG framework consists of four interconnected modules: (1) Uncertainty-Aware Perception, (2) Probabilistic Graph Construction, (3) Uncertainty-Propagating Graph Neural Network, and (4) Uncertainty-Conditioned Planning. The entire pipeline is end-to-end differentiable, enabling joint optimization.

### 2.2 Uncertainty-Aware Perception Module

We employ evidential deep learning to extract node features with calibrated aleatoric and epistemic uncertainty estimates. For each detected object $i$ (vehicles, pedestrians, cyclists) and map element $j$ (lanes, crosswalks, traffic signs), we predict:

**Object Nodes:** Given sensor inputs $\mathbf{X}$ (camera images and/or LiDAR point clouds), the perception backbone outputs parameters of a Normal-Inverse-Gamma (NIG) distribution for continuous attributes:

$$p(y_i | \mathbf{X}) = \text{Student-t}(y_i; \mu_i, \frac{\beta_i(1+\nu_i)}{\nu_i \alpha_i}, 2\alpha_i)$$

where $(\mu_i, \nu_i, \alpha_i, \beta_i)$ are predicted by the neural network. The aleatoric uncertainty is estimated as $\sigma_{aleatoric}^2 = \beta_i / (\alpha_i - 1)$, and epistemic uncertainty as $\sigma_{epistemic}^2 = \beta_i / (\nu_i(\alpha_i - 1))$.

**Node Feature Representation:** Each node $v_i$ is represented as:
$$\mathbf{h}_i^{(0)} = [\mathbf{f}_i; \mathbf{u}_i^{ale}; \mathbf{u}_i^{epi}; \mathbf{c}_i]$$

where $\mathbf{f}_i$ denotes spatial-temporal features (position, velocity, heading), $\mathbf{u}_i^{ale}$ and $\mathbf{u}_i^{epi}$ are uncertainty vectors, and $\mathbf{c}_i$ is a class embedding.

**Classification Uncertainty:** For categorical attributes (object class, traffic light state), we use Dirichlet-based evidential classification:
$$p(\mathbf{c}_i | \mathbf{X}) = \text{Dir}(\boldsymbol{\alpha}_i)$$

The predictive entropy $H[\mathbf{c}_i]$ quantifies classification uncertainty.

### 2.3 Probabilistic Graph Construction

We construct a dynamic scene graph $\mathcal{G} = (\mathcal{V}, \mathcal{E}, \mathcal{R})$ where edges encode probabilistic relationships.

**Edge Types and Relations:** We define relation types $\mathcal{R} = \{$spatial proximity, lane following, potential collision, yielding priority$\}$. For each potential edge $(i, j, r)$, we predict:

$$p(e_{ij}^r = 1 | \mathbf{h}_i, \mathbf{h}_j) = \sigma(\text{MLP}_r([\mathbf{h}_i; \mathbf{h}_j; \mathbf{h}_i - \mathbf{h}_j]))$$

**Uncertainty-Weighted Edges:** Edge weights incorporate both interaction strength and uncertainty:
$$w_{ij}^r = p(e_{ij}^r = 1) \cdot \exp(-\lambda(\|\mathbf{u}_i\|_2 + \|\mathbf{u}_j\|_2))$$

This formulation naturally downweights edges involving highly uncertain nodes, preventing unreliable information from dominating message passing.

**Temporal Edge Construction:** We maintain a sliding window of $T$ frames, creating temporal edges between the same entity across frames:
$$e_{i,t \to i,t+1}^{temporal} = \text{TrackAssociation}(v_i^t, v_i^{t+1})$$

### 2.4 Uncertainty-Propagating Graph Neural Network

Standard GNN message passing does not preserve uncertainty information. We develop a moment-matching approximation for uncertainty propagation.

**Message Passing with Uncertainty:** At layer $l$, we compute messages as:
$$\mathbf{m}_{ij}^{(l)} = \phi^{(l)}(\mathbf{h}_i^{(l)}, \mathbf{h}_j^{(l)}, \mathbf{e}_{ij})$$

For uncertainty propagation, assuming Gaussian-distributed node features $\mathbf{h}_i \sim \mathcal{N}(\boldsymbol{\mu}_i, \boldsymbol{\Sigma}_i)$, we approximate the output distribution using first-order Taylor expansion:

$$\boldsymbol{\mu}_{out} = \phi(\boldsymbol{\mu}_i, \boldsymbol{\mu}_j, \mathbf{e}_{ij})$$
$$\boldsymbol{\Sigma}_{out} \approx \mathbf{J}_i \boldsymbol{\Sigma}_i \mathbf{J}_i^\top + \mathbf{J}_j \boldsymbol{\Sigma}_j \mathbf{J}_j^\top$$

where $\mathbf{J}_i = \frac{\partial \phi}{\partial \mathbf{h}_i}|_{\boldsymbol{\mu}_i, \boldsymbol{\mu}_j}$ is the Jacobian.

**Aggregation:** Node features are updated by aggregating messages weighted by edge confidence:
$$\mathbf{h}_i^{(l+1)} = \gamma^{(l)}\left(\mathbf{h}_i^{(l)}, \sum_{j \in \mathcal{N}(i)} w_{ij} \cdot \mathbf{m}_{ij}^{(l)}\right)$$

The corresponding covariance update follows the uncertainty propagation rules above.

### 2.5 Uncertainty-Conditioned Planning

The planning module generates trajectory proposals conditioned on both graph structure and aggregated uncertainty.

**Trajectory Prediction:** We predict a distribution over future trajectories:
$$p(\boldsymbol{\tau}_{ego} | \mathcal{G}) = \sum_{k=1}^{K} \pi_k \mathcal{N}(\boldsymbol{\tau}_{ego}; \boldsymbol{\mu}_k, \boldsymbol{\Sigma}_k)$$

where $K$ trajectory modes capture multimodal future possibilities.

**Uncertainty-Aware Cost Function:** The trajectory selection incorporates uncertainty:
$$\mathcal{L}_{plan} = \mathcal{L}_{goal} + \lambda_1 \mathcal{L}_{collision} + \lambda_2 \mathcal{L}_{comfort} + \lambda_3 \mathcal{L}_{uncertainty}$$

The uncertainty regularization term encourages conservative behavior:
$$\mathcal{L}_{uncertainty} = \sum_{t=1}^{T_h} \sum_{j \in \mathcal{N}_{risk}} \frac{\text{CollisionRisk}(\boldsymbol{\tau}_{ego}^t, v_j^t)}{d(\boldsymbol{\tau}_{ego}^t, v_j^t)} \cdot \|\mathbf{u}_j\|_2$$

This formulation increases the cost of trajectories passing close to highly uncertain objects.

### 2.6 Training Strategy

**Multi-Task Loss:** The complete training objective is:
$$\mathcal{L}_{total} = \mathcal{L}_{perception} + \lambda_g \mathcal{L}_{graph} + \lambda_p \mathcal{L}_{plan} + \lambda_c \mathcal{L}_{calibration}$$

where $\mathcal{L}_{calibration}$ ensures uncertainty estimates are well-calibrated using negative log-likelihood on held-out data.

**Curriculum Learning:** We employ a three-stage curriculum: (1) perception pre-training, (2) graph construction training, (3) end-to-end fine-tuning with planning.

### 2.7 Experimental Design

**Datasets:** We evaluate on:
- **nuScenes**: 1000 driving scenes with 3D annotations
- **NAVSIM**: Closed-loop evaluation benchmark
- **Bench2Drive**: Diverse scenario benchmark for closed-loop testing

**Baselines:** We compare against:
- GraphAD (scene graph without uncertainty)
- SUPER-AD (uncertainty without structured representation)
- UniAD (state-of-the-art end-to-end system)
- GEMINUS (mixture-of-experts approach)

**Evaluation Metrics:**
1. *Planning Performance*: L2 error, collision rate, progress along route
2. *Uncertainty Quality*: Expected Calibration Error (ECE), Area Under Sparsification Error curve (AUSE)
3. *Interpretability*: Human evaluation of decision explanations, attention alignment with ground truth relations
4. *OOD Detection*: AUROC for detecting novel scenarios using uncertainty thresholds
5. *Safety Metrics*: Time-to-collision, minimum distance to obstacles, intervention rate

**Ablation Studies:** We systematically evaluate: (a) evidential vs. ensemble uncertainty, (b) uncertainty propagation methods, (c) graph structure variations, (d) uncertainty weighting in planning.

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Improved Interpretability**: PNSG will provide human-understandable explanations by highlighting which objects and relationships most influenced planning decisions, with associated confidence levels.

2. **Superior Uncertainty Calibration**: We expect ECE improvements of 15-25% over non-evidential baselines, with uncertainty estimates that reliably indicate prediction quality.

3. **Enhanced OOD Detection**: The framework should achieve >85% AUROC in detecting out-of-distribution scenarios, enabling appropriate fallback behaviors.

4. **Competitive Planning Performance**: Despite the interpretability focus, we target performance within 5% of state-of-the-art black-box methods on standard metrics, with significantly improved safety metrics.

5. **Graceful Degradation**: In challenging scenarios, the system should demonstrate measurably more conservative behavior, reducing collision rates by 20-30% compared to uncertainty-unaware approaches.

### Broader Impact

**Regulatory Pathway**: By providing auditable decision-making with quantified uncertainty, PNSG addresses key requirements for regulatory approval of autonomous vehicles, potentially accelerating safe deployment.

**Safety Improvement**: Principled uncertainty quantification enables the system to recognize its limitations and request human intervention appropriately, reducing the risk of catastrophic failures.

**Research Foundation**: The probabilistic scene graph framework establishes a foundation for future research combining structured representations with uncertainty quantification, applicable beyond autonomous driving to robotics and other safety-critical domains.

**Industry Adoption**: The interpretable nature of PNSG facilitates debugging and validation workflows essential for industrial deployment, bridging the gap between research advances and real-world applications.

In conclusion, PNSG represents a significant step toward autonomous driving systems that are not only performant but also interpretable, uncertainty-aware, and suitable for safety-critical deployment—addressing fundamental challenges that currently limit the real-world impact of machine learning in autonomous vehicles.