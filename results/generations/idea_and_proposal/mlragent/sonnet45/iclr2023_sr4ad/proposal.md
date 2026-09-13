# Research Proposal: Hierarchical Uncertainty-Aware Scene Graphs for Joint Perception-Prediction with Safety Guarantees in Autonomous Driving

## 1. Introduction

### Background

Autonomous driving systems have traditionally employed modular architectures where perception, prediction, and planning operate as separate components. While this modularity offers interpretability and ease of debugging, it suffers from critical limitations: errors cascade through the pipeline, intermediate representations discard valuable uncertainty information, and components optimized independently may be suboptimal when integrated. Recent end-to-end learning approaches address some of these issues but sacrifice interpretability and struggle to provide safety guarantees required for real-world deployment.

A fundamental challenge lies at the perception-prediction interface, where misdetected objects or miscalculated uncertainties propagate downstream, leading to potentially catastrophic planning failures. Current systems often exhibit overconfidence in erroneous predictions, providing no mechanism for the planning module to distinguish between high-confidence accurate predictions and high-confidence incorrect predictions. This overconfidence problem is particularly acute in safety-critical edge cases—precisely the scenarios where robust uncertainty quantification is most needed.

Recent advances in conformal prediction and evidential deep learning offer promising pathways to quantify uncertainty with theoretical guarantees. Meanwhile, graph-based scene representations have demonstrated effectiveness in capturing complex relationships between traffic agents. However, existing approaches typically operate at a single level of abstraction and lack principled uncertainty propagation mechanisms through hierarchical structures.

### Research Objectives

This research aims to develop a novel **Hierarchical Uncertainty-Aware Scene Graph (HUASG)** framework that addresses the perception-prediction interface problem through the following specific objectives:

1. **Design a hierarchical probabilistic scene graph** that represents driving scenes at multiple abstraction levels, from raw sensory detections to high-level scene semantics, with explicit uncertainty quantification at each level.

2. **Develop joint training methodologies** that enable end-to-end optimization of perception and prediction modules while maintaining the interpretable graph structure.

3. **Integrate conformal prediction techniques** to provide finite-sample statistical guarantees on prediction validity, enabling principled safety assessment and fallback triggering.

4. **Validate the framework** on diverse autonomous driving benchmarks, demonstrating improvements in prediction accuracy, uncertainty calibration, and safety metrics compared to baseline modular and end-to-end approaches.

### Significance

This research makes several significant contributions to autonomous driving and machine learning:

**Safety Impact**: By providing calibrated uncertainty estimates with theoretical guarantees, the framework enables autonomous vehicles to recognize their limitations and engage fallback behaviors before safety-critical failures occur. This addresses a fundamental requirement for deploying autonomous systems in the real world.

**Bridging Paradigms**: The approach combines the interpretability and safety certification potential of modular systems with the performance benefits of joint optimization, offering a practical middle ground for production autonomous driving systems.

**Theoretical Foundation**: The integration of evidential deep learning with conformal prediction in hierarchical graph structures provides a principled framework for uncertainty quantification and propagation, advancing the theoretical understanding of uncertainty in structured prediction problems.

**Practical Validation**: The framework will be extensively validated on real-world datasets, providing actionable insights for autonomous driving practitioners and demonstrating measurable improvements in safety-critical scenarios.

## 2. Methodology

### 2.1 Hierarchical Scene Graph Architecture

The proposed HUASG represents driving scenes through a four-level hierarchical graph structure $G = (V, E, \Theta, U)$, where $V$ represents nodes, $E$ represents edges, $\Theta$ represents deterministic attributes, and $U$ represents uncertainty estimates.

**Level 1: Raw Detections** ($L_1$): Nodes represent individual sensor detections with attributes including bounding boxes, class probabilities, and velocity estimates. Each node $v_i^{(1)} \in V^{(1)}$ is associated with:
- State estimate: $\mathbf{s}_i = [x, y, \theta, v_x, v_y, w, h, c]$ (position, orientation, velocity, dimensions, class)
- Evidential parameters: $\alpha_i = [\alpha_{i,1}, ..., \alpha_{i,K}]$ representing a Dirichlet distribution over $K$ possible classes
- Aleatoric uncertainty: $\sigma_i^2$ for continuous attributes

**Level 2: Tracked Objects** ($L_2$): Nodes aggregate multiple detections across time through data association. For each tracked object $v_j^{(2)} \in V^{(2)}$:
- Temporal state sequence: $\mathbf{S}_j = [\mathbf{s}_j^{t-T}, ..., \mathbf{s}_j^t]$
- Epistemic uncertainty from evidential aggregation: $u_j = K / \sum_k \alpha_{j,k}$
- Track confidence score: $\phi_j \in [0,1]$

**Level 3: Interaction Patterns** ($L_3$): Edges $e_{jk}^{(3)}$ between tracked objects encode pairwise interactions:
- Relative pose and velocity: $\Delta \mathbf{s}_{jk}$
- Interaction type distribution: $\pi_{jk} = [\pi_{jk}^{\text{yield}}, \pi_{jk}^{\text{overtake}}, \pi_{jk}^{\text{follow}}, \pi_{jk}^{\text{ignore}}]$
- Mutual influence uncertainty: $\tau_{jk}$

**Level 4: Scene-Level Semantics** ($L_4$): Global scene representation capturing:
- Scene classification: $c_{\text{scene}} \in \{\text{highway}, \text{urban}, \text{intersection}, ...\}$
- Traffic density and flow patterns
- Aggregate uncertainty metric: $U_{\text{scene}} = f(u_1, ..., u_N, \tau_{11}, ..., \tau_{NN})$

### 2.2 Evidential Deep Learning for Uncertainty Quantification

We employ **Evidential Deep Learning** to capture both aleatoric and epistemic uncertainty. For classification tasks (e.g., object class), the neural network outputs evidence parameters $\mathbf{e}_i = [e_{i,1}, ..., e_{i,K}]$, which are transformed to Dirichlet parameters:

$$\alpha_{i,k} = e_{i,k} + 1$$

The predicted class probabilities are given by the expected value of the Dirichlet distribution:

$$p_{i,k} = \frac{\alpha_{i,k}}{S_i}, \quad S_i = \sum_{k=1}^K \alpha_{i,k}$$

The epistemic uncertainty (model uncertainty) is quantified as:

$$u_i = \frac{K}{S_i}$$

For regression tasks (e.g., position, velocity), we predict four outputs $[\gamma_i, \nu_i, \lambda_i, \beta_i]$ parameterizing a Normal-Inverse-Gamma distribution:

$$p(\mu, \sigma^2 | \gamma, \nu, \lambda, \beta) = \text{NIG}(\mu, \sigma^2 | \gamma, \nu, \lambda, \beta)$$

The predicted mean and uncertainties are:

$$\hat{\mu}_i = \gamma_i, \quad \sigma_{\text{aleatoric}}^2 = \frac{\beta_i}{\lambda_i - 1}, \quad \sigma_{\text{epistemic}}^2 = \frac{\beta_i}{\nu_i(\lambda_i - 1)}$$

### 2.3 Hierarchical Uncertainty Propagation

Uncertainty propagates through the hierarchy via message-passing mechanisms. From level $l$ to $l+1$, the aggregated uncertainty is computed as:

$$U_j^{(l+1)} = g\left(\{u_i^{(l)} : v_i^{(l)} \in \mathcal{N}(v_j^{(l+1)})\}, \{\tau_{ij}^{(l)} : e_{ij}^{(l)} \in E^{(l)}\}\right)$$

where $\mathcal{N}(v_j^{(l+1)})$ denotes the neighborhood of node $v_j^{(l+1)}$ in level $l$, and $g$ is a learned aggregation function implemented as a Graph Neural Network (GNN):

$$\mathbf{h}_j^{(l+1)} = \text{GNN}\left(\mathbf{h}_j^{(l)}, \bigoplus_{i \in \mathcal{N}(j)} \psi(\mathbf{h}_i^{(l)}, \mathbf{h}_j^{(l)}, \mathbf{e}_{ij}^{(l)})\right)$$

where $\bigoplus$ is a permutation-invariant aggregation (e.g., sum, max), and $\psi$ is an edge function.

### 2.4 Joint Perception-Prediction Training

The framework is trained end-to-end with a multi-task loss function:

$$\mathcal{L}_{\text{total}} = \lambda_1 \mathcal{L}_{\text{detection}} + \lambda_2 \mathcal{L}_{\text{tracking}} + \lambda_3 \mathcal{L}_{\text{prediction}} + \lambda_4 \mathcal{L}_{\text{uncertainty}}$$

**Detection Loss**: Combines evidential classification loss and regression loss:

$$\mathcal{L}_{\text{detection}} = \sum_i \left[\mathcal{L}_{\text{EDL}}^{\text{class}}(\alpha_i, y_i) + \mathcal{L}_{\text{NIG}}^{\text{reg}}(\gamma_i, \nu_i, \lambda_i, \beta_i, \mathbf{s}_i^*)\right]$$

where $\mathcal{L}_{\text{EDL}}^{\text{class}}$ is the evidential loss incorporating KL divergence with a uniform Dirichlet prior.

**Tracking Loss**: Penalizes inconsistencies in temporal object associations:

$$\mathcal{L}_{\text{tracking}} = \sum_j \sum_{t=1}^T \|\mathbf{s}_j^t - \text{Predict}(\mathbf{s}_j^{t-1})\|^2 + \lambda_{\text{assoc}} \mathcal{L}_{\text{association}}$$

**Prediction Loss**: Multi-modal trajectory prediction with uncertainty:

$$\mathcal{L}_{\text{prediction}} = \sum_j \min_{m=1,...,M} \left[\|\mathbf{f}_j^m - \mathbf{f}_j^*\|^2 + \lambda_u U_j^m\right]$$

where $\mathbf{f}_j^m$ is the $m$-th predicted trajectory mode and $\mathbf{f}_j^*$ is the ground truth.

**Uncertainty Calibration Loss**: Ensures uncertainty estimates are well-calibrated:

$$\mathcal{L}_{\text{uncertainty}} = \sum_i |\mathbb{I}[|\hat{y}_i - y_i^*| \leq \sigma_i] - p_{\text{target}}|$$

where $p_{\text{target}}$ is the desired coverage probability (e.g., 0.95).

### 2.5 Conformal Prediction for Safety Guarantees

To provide finite-sample statistical guarantees, we employ **conformal prediction** on a held-out calibration set. For each predicted trajectory $\hat{\mathbf{f}}_j$ with uncertainty estimate $U_j$, we compute non-conformity scores:

$$R_j = d(\hat{\mathbf{f}}_j, \mathbf{f}_j^*) / (U_j + \epsilon)$$

where $d$ is a distance metric (e.g., average displacement error). On the calibration set $\{(R_1^{\text{cal}}, ..., R_n^{\text{cal}})\}$, we compute the $(1-\alpha)$-quantile:

$$\hat{q} = \text{Quantile}_{1-\alpha}(\{R_1^{\text{cal}}, ..., R_n^{\text{cal}}\})$$

For a new prediction, the conformal prediction set is:

$$C(\mathbf{x}) = \{\mathbf{f} : d(\hat{\mathbf{f}}, \mathbf{f}) \leq \hat{q} \cdot U\}$$

This provides the guarantee that $\mathbb{P}(\mathbf{f}^* \in C(\mathbf{x})) \geq 1 - \alpha$ for any future sample, regardless of the underlying model.

**Safety Triggering**: When the conformal prediction set becomes too large (indicating high uncertainty), defined as:

$$\text{diameter}(C(\mathbf{x})) > \tau_{\text{safe}}$$

the system triggers a fallback behavior (e.g., conservative trajectory, hand-off to human driver).

### 2.6 Experimental Design

**Datasets**: We will evaluate on three benchmark datasets:

1. **nuScenes**: 1000 driving scenes with 3D annotations, multi-modal sensor data
2. **Waymo Open Dataset**: Large-scale dataset with diverse weather and lighting conditions
3. **ScenarioNet**: Real-world traffic scenarios for generalization testing

**Data Split**: For each dataset, we use 60% for training, 20% for calibration (conformal prediction), and 20% for testing.

**Baseline Comparisons**:

1. **Modular Pipeline**: Sequential perception → tracking → prediction with standard object detection (e.g., CenterPoint) and trajectory prediction (e.g., MultiPath)
2. **End-to-End Models**: UniAD, ST-P3, SUPER-AD
3. **Uncertainty-Aware Baselines**: MC Dropout, Deep Ensembles for uncertainty quantification
4. **Ablation Studies**: 
   - HUASG without joint training (separate module training)
   - HUASG without conformal prediction
   - HUASG with single-level graph (no hierarchy)

**Evaluation Metrics**:

*Prediction Performance*:
- Average Displacement Error (ADE) and Final Displacement Error (FDE) at 1s, 3s, 5s horizons
- Miss Rate at various thresholds

*Uncertainty Calibration*:
- Expected Calibration Error (ECE): $\text{ECE} = \sum_{b=1}^B \frac{|B_b|}{N} |\text{acc}(B_b) - \text{conf}(B_b)|$
- Negative Log-Likelihood (NLL)
- Uncertainty-error correlation (Pearson correlation between $U_j$ and actual error)

*Safety Metrics*:
- Coverage probability: $\frac{1}{N}\sum_{i=1}^N \mathbb{I}[\mathbf{f}_i^* \in C(\mathbf{x}_i)]$
- Selective prediction performance: ADE when system abstains on top $k$% uncertain predictions
- Time-to-collision (TTC) in high-uncertainty scenarios
- False positive/negative rates for safety trigger

*Computational Efficiency*:
- Inference time (ms per frame)
- Model parameters and memory footprint

**Implementation Details**:

- **Architecture**: ResNet-50 or Vision Transformer backbone for perception, 4-layer GNN for graph processing with 256-dimensional hidden states
- **Training**: AdamW optimizer, learning rate $10^{-4}$ with cosine annealing, batch size 32, 50 epochs
- **Hardware**: 4× NVIDIA A100 GPUs
- **Loss weights**: $\lambda_1=1.0, \lambda_2=0.5, \lambda_3=2.0, \lambda_4=0.3$ (tuned via validation)
- **Conformal prediction**: $\alpha=0.05$ (95% coverage target)

## 3. Expected Outcomes & Impact

### Expected Outcomes

**Improved Prediction Accuracy**: We anticipate 15-25% reduction in ADE/FDE compared to modular baselines, particularly in complex multi-agent interaction scenarios where joint perception-prediction reasoning provides the most benefit. The hierarchical structure should enable the model to leverage high-level semantic understanding to disambiguate low-level detection uncertainties.

**Calibrated Uncertainty Estimates**: The combination of evidential learning and conformal prediction should achieve ECE < 0.05, significantly better than standard deep learning approaches (typically ECE > 0.15). The theoretical guarantees from conformal prediction ensure that coverage probabilities meet specified targets (e.g., 95% coverage) on test data.

**Safety Performance**: In high-uncertainty scenarios (top 10% uncertainty), we expect:
- 40-60% reduction in collision rates through appropriate fallback triggering
- False positive rate < 5% (unnecessary fallbacks)
- Coverage guarantee violations < 5% (meeting conformal prediction theory)

**Interpretability Benefits**: The hierarchical graph structure should enable visualization and interpretation of failure modes, showing practitioners where uncertainty originates (e.g., low-level detection ambiguity vs. high-level interaction complexity) and propagates through the system.

**Computational Feasibility**: Despite the hierarchical structure, we aim for real-time performance (< 50ms inference latency) through efficient GNN implementations and selective computation strategies.

### Scientific Impact

**Theoretical Contributions**: This research advances the integration of evidential deep learning with conformal prediction in structured prediction settings. The hierarchical uncertainty propagation framework provides a principled approach to reasoning about uncertainty at multiple levels of abstraction, with potential applications beyond autonomous driving (e.g., robotics, healthcare).

**Methodological Innovation**: The joint optimization framework that maintains interpretable structure while enabling end-to-end gradient flow represents a novel paradigm bridging modular and end-to-end approaches. This addresses a fundamental tension in autonomous systems design between performance and interpretability.

### Practical Impact

**Enhanced Safety**: By providing provable uncertainty quantification and safety guarantees, this framework addresses critical barriers to deploying autonomous vehicles at scale. The ability to detect and respond to high-uncertainty situations before failures occur could significantly reduce accident rates.

**Regulatory Compliance**: The interpretable hierarchical structure and statistical safety guarantees align with emerging regulatory requirements for AI systems in safety-critical applications. The framework provides auditable evidence of safety assessment capabilities.

**Industry Adoption**: The modular design allows progressive integration into existing autonomous driving stacks, lowering the barrier to adoption compared to purely end-to-end approaches that require complete system redesigns.

**Generalization to Other Domains**: The core principles of hierarchical uncertainty-aware scene representations extend naturally to other embodied AI domains including robot manipulation, drone navigation, and multi-robot coordination, potentially catalyzing advances across these fields.

### Broader Implications

This research contributes to the responsible development of AI systems by prioritizing uncertainty quantification and safety alongside performance. It demonstrates that rigorous safety guarantees need not come at the cost of state-of-the-art performance, providing a template for deploying machine learning in high-stakes applications. By open-sourcing code and models, we aim to establish new standards for uncertainty-aware perception-prediction systems in the autonomous driving research community.

The framework also advances the scientific understanding of how to effectively combine probabilistic reasoning, deep learning, and formal verification—three traditionally separate paradigms that must be integrated for trustworthy autonomous systems. This interdisciplinary approach exemplifies the type of holistic thinking required to address complex real-world challenges where no single technique suffices.