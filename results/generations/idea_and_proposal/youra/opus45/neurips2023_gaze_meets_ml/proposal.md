# Research Proposal: GazePC: Real-Time Intent Detection via Hierarchical Predictive Coding of Gaze Trajectories

## 1. Introduction

### 1.1 Background

Human-AI collaboration represents one of the most promising frontiers in artificial intelligence research, with applications spanning extended reality (XR), assistive robotics, autonomous vehicles, and intelligent user interfaces. A fundamental challenge in achieving seamless human-AI interaction lies in enabling AI systems to anticipate human intentions before explicit actions occur. Such anticipatory capability would allow AI agents to prepare appropriate responses, reduce interaction latency, and create more natural collaborative experiences.

Eye gaze has emerged as a particularly valuable physiological signal for understanding human cognition and intention. Unlike other behavioral signals, eye movements naturally precede intended actions by 300-800 milliseconds, as documented extensively in visuomotor control research (Belardinelli, 2023). This anticipatory property makes gaze an ideal candidate for early intent detection. Furthermore, modern eye-tracking technology has become increasingly accessible and cost-efficient, with consumer-grade devices now capable of 60Hz+ sampling rates, enabling real-time gaze data collection in practical applications.

Despite these advantages, current approaches to gaze-based intent detection have not fully exploited the predictive nature of eye movements. Existing methods predominantly treat intent detection as a pattern classification problem, where gaze features are extracted and fed into classifiers to categorize user intentions. While such approaches have achieved reasonable accuracy—for instance, GazeIntent (2024) reported F1 scores of 0.94—they achieve only marginal anticipation advantages over reactive systems. Bayesian classification approaches (Jo, 2025) similarly struggle to maintain consistent anticipation windows, suggesting that the classification paradigm may be fundamentally limited in capturing the temporal dynamics of gaze-intention relationships.

### 1.2 Research Gap and Motivation

The key insight motivating this research is that gaze patterns follow predictable sequences during periods of stable intention. When a user maintains a consistent goal, their eye movements exhibit characteristic patterns—systematic scanning, target fixation, and anticipatory saccades toward action-relevant locations. Critically, when intentions change, these patterns deviate from their expected trajectories. This observation suggests that intent detection should be framed not as pattern classification but as anomaly detection in a predictive framework.

Predictive coding theory, originating from computational neuroscience (Rao & Ballard, 1999), provides a principled foundation for this approach. According to this theory, the brain continuously generates predictions about incoming sensory information and updates its internal models based on prediction errors. This framework has been successfully applied to various domains, including visual perception, motor control, and recently, machine learning architectures for sensory processing (Gornet & Thomson, 2024).

### 1.3 Research Objectives

This research proposes GazePC (Gaze Predictive Coding), a hierarchical predictive coding architecture for real-time intent detection from eye gaze trajectories. Our primary objectives are:

1. **Develop a lightweight temporal transformer architecture** that continuously predicts gaze trajectories (x, y coordinates and fixation duration) and detects intent changes through accumulated prediction errors.

2. **Validate the predictive coding hypothesis** by demonstrating that prediction errors correlate significantly with actual intent changes (target Pearson r > 0.6).

3. **Achieve real-time performance** with detection latency under 50ms and F1 score exceeding 0.85, while maintaining the 300-800ms anticipation window that gaze naturally provides.

4. **Establish comparative advantages** over existing classification-based and Bayesian approaches for gaze-based intent detection.

### 1.4 Significance

Success in this research would establish predictive coding as a principled framework for gaze-based human-AI interaction, with broad implications for XR interfaces, collaborative robotics, and assistive technologies. Beyond practical applications, this work would contribute to our understanding of how computational models can leverage the anticipatory nature of human gaze, bridging insights from neuroscience with machine learning methodology.

## 2. Methodology

### 2.1 Theoretical Framework

Our approach is grounded in the predictive coding principle that stable behavioral states generate predictable sensory patterns, while state transitions manifest as sustained prediction errors. We formalize this as follows:

Let $\mathbf{g}_t = (x_t, y_t, d_t)$ represent the gaze state at time $t$, where $(x_t, y_t)$ are fixation coordinates and $d_t$ is fixation duration. Given a sequence of past gaze states $\mathbf{G}_{t-T:t-1} = \{\mathbf{g}_{t-T}, ..., \mathbf{g}_{t-1}\}$, our model predicts the next gaze state:

$$\hat{\mathbf{g}}_t = f_\theta(\mathbf{G}_{t-T:t-1})$$

where $f_\theta$ is our temporal transformer with parameters $\theta$. The prediction error at time $t$ is:

$$\epsilon_t = \|\mathbf{g}_t - \hat{\mathbf{g}}_t\|_2$$

We hypothesize that intent changes correspond to periods where accumulated prediction errors exceed an adaptive threshold. We define the accumulated error over a sliding window of size $W$ as:

$$E_t = \sum_{i=t-W+1}^{t} w_i \cdot \epsilon_i$$

where $w_i$ are precision weights learned during training. An intent change is detected when:

$$E_t > \tau_t$$

where $\tau_t$ is an adaptive threshold that adjusts based on recent error statistics:

$$\tau_t = \mu_{E} + \alpha \cdot \sigma_{E}$$

with $\mu_E$ and $\sigma_E$ being the running mean and standard deviation of accumulated errors, and $\alpha$ being a sensitivity hyperparameter.

### 2.2 Architecture Design

The GazePC architecture consists of four main components:

**2.2.1 Gaze Embedding Layer**

Raw gaze coordinates are embedded into a higher-dimensional space:

$$\mathbf{e}_t = \text{Linear}(\mathbf{g}_t) + \text{PE}(t)$$

where PE denotes sinusoidal positional encoding to capture temporal ordering. The embedding dimension is set to 256.

**2.2.2 Temporal Transformer Encoder**

We employ a lightweight transformer with 4 layers, each containing:
- Multi-head self-attention (4 heads, 64 dimensions per head)
- Feed-forward network (hidden dimension 512)
- Layer normalization and residual connections

The self-attention mechanism captures temporal dependencies:

$$\text{Attention}(\mathbf{Q}, \mathbf{K}, \mathbf{V}) = \text{softmax}\left(\frac{\mathbf{Q}\mathbf{K}^T}{\sqrt{d_k}}\right)\mathbf{V}$$

**2.2.3 Prediction Head**

A two-layer MLP projects the transformer output to predicted gaze coordinates:

$$\hat{\mathbf{g}}_t = \text{MLP}(\mathbf{h}_t)$$

where $\mathbf{h}_t$ is the transformer's output representation.

**2.2.4 Error Accumulation and Detection Module**

This module maintains a sliding window of prediction errors, computes precision-weighted accumulated errors, and applies adaptive thresholding for intent detection. The precision weights are learned through backpropagation during fine-tuning.

### 2.3 Training Procedure

**2.3.1 Pre-training Phase**

We pre-train the temporal transformer on the GazeCapture dataset (Krafka et al., 2016), which contains approximately 1.5 million gaze images from diverse participants. The pre-training objective is next-step gaze prediction:

$$\mathcal{L}_{\text{pretrain}} = \mathbb{E}\left[\|\mathbf{g}_t - \hat{\mathbf{g}}_t\|_2^2\right]$$

Pre-training uses the Adam optimizer with learning rate $1 \times 10^{-4}$, batch size 64, and runs for 100 epochs with early stopping based on validation loss.

**2.3.2 Fine-tuning Phase**

For intent detection, we fine-tune on task-specific datasets with ground-truth intent labels. The fine-tuning loss combines prediction accuracy with intent detection performance:

$$\mathcal{L}_{\text{finetune}} = \mathcal{L}_{\text{pred}} + \lambda \cdot \mathcal{L}_{\text{intent}}$$

where $\mathcal{L}_{\text{intent}}$ is binary cross-entropy for intent change detection and $\lambda = 0.5$ balances the two objectives.

### 2.4 Data Collection and Datasets

**2.4.1 Pre-training Data**

- **GazeCapture**: 1.5 million images with gaze annotations from 1,474 participants
- **GazeFollow**: 130,000 images for gaze-following prediction

**2.4.2 Fine-tuning and Evaluation Data**

We will collect a new dataset, **GazeIntent-XR**, specifically designed for intent detection validation:

- **Participants**: 50 adults (25 male, 25 female), ages 18-45, with normal or corrected vision
- **Eye Tracker**: Tobii Pro Glasses 3 (100Hz sampling rate)
- **Tasks**: Three visual target tasks in VR environment:
  1. Object manipulation (pick and place)
  2. Navigation (waypoint selection)
  3. Menu selection (UI interaction)
- **Ground Truth**: Intent changes annotated via button press by participants and verified by two independent annotators
- **Session Structure**: Each participant completes 30 trials per task type (90 total), with approximately 5-10 intent changes per trial
- **Total Data**: ~4,500 trials, ~30,000 intent change events

### 2.5 Experimental Design

**2.5.1 Experiment 1: Primary Hypothesis Validation (SH1)**

*Objective*: Validate that GazePC achieves <50ms detection latency with F1 >0.85.

*Protocol*:
- 5-fold cross-validation on GazeIntent-XR dataset
- Metrics: Detection latency (ms), F1 score, precision, recall
- Statistical analysis: Mean ± SD, 95% confidence intervals

*Success Criteria*: Latency <50ms AND F1 >0.85 (p < 0.05)

**2.5.2 Experiment 2: Mechanism Validation (SH2)**

*Objective*: Verify that prediction error accumulation is the causal mechanism for intent detection.

*Protocol*:
- Ablation studies removing each component:
  - A1: Random prediction errors (shuffled)
  - A2: Fixed threshold (non-adaptive)
  - A3: No precision weighting
  - A4: Single-layer transformer
- Correlation analysis between accumulated errors and ground-truth intent changes

*Success Criteria*: Pearson r > 0.6 for error-intent correlation; significant performance degradation in ablations (p < 0.05)

**2.5.3 Experiment 3: Comparative Evaluation (SH3)**

*Objective*: Demonstrate superiority over baseline methods.

*Baselines*:
- **Bayesian Classification** (Jo, 2025): State-of-the-art Bayesian approach
- **LSTM Classifier** (Xu, 2023): Recurrent neural network baseline
- **Random Forest**: Traditional ML baseline with hand-crafted gaze features
- **Threshold-based**: Simple velocity threshold for saccade detection

*Protocol*:
- Same train/test splits across all methods
- Metrics: F1 score, detection latency, anticipation window
- Statistical comparison: Paired t-tests with Bonferroni correction

*Success Criteria*: Significant improvement over all baselines (p < 0.05)

**2.5.4 Experiment 4: Real-time Performance Validation**

*Objective*: Verify computational efficiency for real-time deployment.

*Protocol*:
- Benchmark inference time on NVIDIA RTX 3080 GPU
- Measure end-to-end latency including data preprocessing
- Test with continuous 60Hz gaze stream

*Success Criteria*: Inference time <16.7ms (compatible with 60Hz input)

### 2.6 Evaluation Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| Detection Latency | Time from ground-truth intent change to system detection | <50ms |
| F1 Score | Harmonic mean of precision and recall | >0.85 |
| Anticipation Window | Time between detection and action execution | 300-800ms |
| Error-Intent Correlation | Pearson r between accumulated error and intent changes | >0.6 |
| Inference Time | Model forward pass duration | <16.7ms |

### 2.7 Statistical Analysis Plan

- **Sample Size**: n ≥ 30 sessions per condition (power = 0.8, α = 0.05, Cohen's d = 0.8)
- **Primary Analysis**: Independent samples t-test for baseline comparisons
- **Secondary Analysis**: Paired t-tests for ablation studies
- **Correlation Analysis**: Pearson correlation with bootstrapped confidence intervals
- **Multiple Comparisons**: Bonferroni correction for family-wise error rate

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

Based on our theoretical framework and preliminary analysis, we anticipate the following outcomes:

**Primary Outcomes**:
1. GazePC will achieve detection latency of 35-45ms with F1 score of 0.87-0.92, meeting our primary targets
2. The anticipation window will be preserved at 350-700ms, enabling meaningful proactive AI responses
3. Prediction error will show strong correlation (r = 0.65-0.75) with actual intent changes

**Comparative Outcomes**:
4. GazePC will outperform Bayesian classification by 15-25% in F1 score
5. Anticipation window will be 2-3× longer than classification-based approaches
6. Ablation studies will confirm that all architectural components contribute significantly

### 3.2 Scientific Contributions

1. **Theoretical Contribution**: Establishing predictive coding as a principled framework for gaze-based intent detection, bridging computational neuroscience with practical ML applications

2. **Methodological Contribution**: A novel architecture combining temporal transformers with predictive coding principles for real-time physiological signal processing

3. **Empirical Contribution**: Comprehensive validation demonstrating the superiority of prediction-error-based detection over classification approaches

4. **Dataset Contribution**: The GazeIntent-XR dataset will be released publicly to support future research in gaze-based intent detection

### 3.3 Practical Impact

**Extended Reality (XR)**: GazePC enables XR systems to anticipate user selections and pre-render content, reducing perceived latency and improving user experience.

**Assistive Robotics**: Collaborative robots can prepare for handoffs and adjust trajectories based on anticipated human intentions, improving safety and efficiency.

**Autonomous Vehicles**: Understanding driver intent through gaze can improve handoff timing between autonomous and manual control modes.

**Accessibility**: Gaze-based intent detection can enable faster, more natural interfaces for users with motor impairments.

### 3.4 Limitations and Future Directions

We acknowledge several limitations that define future research directions:

1. **Individual Variability**: Per-user calibration may be required for optimal performance; future work should explore few-shot adaptation techniques

2. **Multi-Intent Scenarios**: The current framework assumes single active intentions; extending to concurrent goals requires hierarchical intent modeling

3. **Domain Transfer**: Task-specific fine-tuning is likely needed; investigating universal intent representations is an important future direction

4. **Ethical Considerations**: Gaze-based intent detection raises privacy concerns; future work must address consent, data protection, and potential misuse

### 3.5 Timeline

| Phase | Duration | Activities |
|-------|----------|------------|
| Phase 1 | Months 1-3 | Architecture implementation, pre-training on GazeCapture |
| Phase 2 | Months 4-6 | Data collection (GazeIntent-XR dataset) |
| Phase 3 | Months 7-9 | Fine-tuning, primary experiments (SH1, SH2) |
| Phase 4 | Months 10-11 | Comparative evaluation (SH3), real-time validation |
| Phase 5 | Month 12 | Analysis, paper writing, dataset release |

### 3.6 Conclusion

This research proposes GazePC, a hierarchical predictive coding architecture that fundamentally reframes gaze-based intent detection from pattern classification to prediction error accumulation. By leveraging the anticipatory nature of eye movements and the principled framework of predictive coding, we hypothesize that GazePC will achieve real-time intent detection with unprecedented anticipation capabilities. Success in this research would not only advance the state of the art in gaze-assisted machine learning but also establish new paradigms for human-AI collaboration across diverse application domains.