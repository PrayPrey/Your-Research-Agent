# Gaze-Driven Curriculum Learning: Using Eye-Tracking Data to Dynamically Prioritize Training Samples

## 1. Introduction

### Background

Machine learning models have achieved remarkable success across various domains, yet their training paradigms often diverge significantly from how humans acquire knowledge. Traditional deep learning approaches treat training data uniformly or randomly, overlooking the fundamental principle that has guided human education for centuries: curriculum learning—the idea that learning progresses from simple to complex concepts. While curriculum learning has been explored in machine learning, existing methods typically rely on heuristic-based difficulty metrics (e.g., loss values, model uncertainty) that may not align with genuine cognitive complexity as perceived by humans.

Eye-tracking technology offers a unique window into human cognitive processing, revealing what captures our attention, what we find challenging, and how we navigate visual information. Neuroscience research has established that gaze patterns—including fixation duration, saccade frequency, pupil dilation, and revisitation patterns—serve as reliable indicators of cognitive load and task difficulty. When humans encounter challenging visual stimuli, they exhibit characteristic gaze behaviors: longer fixations, more frequent revisitations, higher saccade frequencies, and irregular scan paths. These patterns encode rich information about perceptual and cognitive difficulty that remains largely untapped in modern machine learning systems.

The intersection of eye-gaze research and machine learning presents a compelling opportunity. Recent work has demonstrated the value of human attention patterns in improving code language models (EyeMulator), detecting behavioral engagement through multimodal learning, and learning robust gaze representations through contrastive learning (CLRGaze). However, no existing framework systematically leverages eye-tracking data to construct adaptive curricula for training computer vision models, despite the natural alignment between human visual attention and the challenges faced by visual recognition systems.

### Research Objectives

This research proposes a novel framework—**Gaze-Driven Curriculum Learning (GDCL)**—that bridges human cognitive science and machine learning optimization. The primary objectives are:

1. **Develop gaze-based difficulty metrics**: Establish a comprehensive set of eye-tracking features that quantitatively capture human-perceived visual difficulty across diverse vision tasks.

2. **Create a difficulty estimation network**: Design and train a neural network that can predict gaze-derived difficulty metrics for unlabeled images, enabling scalable curriculum generation without requiring eye-tracking data for every training sample.

3. **Implement adaptive curriculum scheduling**: Develop dynamic training schedulers that leverage predicted difficulty to order and weight training samples, optimizing for both convergence speed and final performance.

4. **Validate across diverse domains**: Demonstrate the effectiveness of GDCL across multiple vision tasks and datasets, including general object recognition, medical imaging, and autonomous driving scenarios.

### Significance

This research addresses critical gaps at the intersection of human cognition and artificial intelligence. First, it provides a principled, human-grounded approach to curriculum learning, replacing arbitrary heuristics with cognitively meaningful difficulty measures. Second, it contributes to interpretability by aligning model learning trajectories with human perceptual strategies, potentially yielding models whose internal representations better mirror human visual processing. Third, it offers practical benefits for data-efficient learning, particularly valuable in domains where labeled data is scarce or expensive to obtain, such as medical imaging where expert radiologists' gaze patterns could guide model training on rare pathologies.

The broader impact extends to human-AI interaction and trustworthy AI. Models trained with human-aligned curricula may exhibit more predictable behaviors and failure modes, improving safety in critical applications like autonomous driving. Furthermore, this work establishes methodological foundations for leveraging other physiological signals (EEG, pupillometry) in machine learning, opening new avenues for human-centered AI development.

## 2. Methodology

### 2.1 Data Collection and Gaze Feature Extraction

#### Eye-Tracking Data Acquisition

We will collect eye-tracking data across three benchmark datasets representing different visual complexity levels:

- **CIFAR-100**: Natural images for general object recognition (100 categories)
- **ChestX-ray14**: Medical imaging dataset for pathology detection (14 disease categories)
- **nuScenes**: Autonomous driving scenes for hazard detection

For each dataset, we will recruit 30-50 participants with normal or corrected-to-normal vision. Participants will perform task-specific activities while their gaze is recorded at 120 Hz minimum using a high-precision eye-tracker (e.g., Tobii Pro Spectrum or EyeLink 1000). Tasks include:

- **Recognition task**: Identify the primary object/pathology/hazard in each image
- **Free-viewing task**: Naturally explore images without specific instructions
- **Comparison task**: Compare pairs of images and identify key differences

Each image will be viewed by at least 10 participants to ensure reliability and account for individual variability.

#### Gaze-Based Difficulty Metrics

We extract the following gaze features for each image $I_i$, where participant set $P = \{p_1, ..., p_n\}$ views the image:

1. **Mean Fixation Duration (MFD)**:
$$\text{MFD}(I_i) = \frac{1}{|P|}\sum_{p \in P} \frac{1}{|F_p|}\sum_{f \in F_p} d_f$$
where $F_p$ is the set of fixations for participant $p$ and $d_f$ is the duration of fixation $f$.

2. **Saccade Frequency (SF)**:
$$\text{SF}(I_i) = \frac{1}{|P|}\sum_{p \in P} \frac{|S_p|}{T_p}$$
where $S_p$ is the set of saccades and $T_p$ is the total viewing time for participant $p$.

3. **Revisitation Rate (RR)**: Proportion of regions visited multiple times:
$$\text{RR}(I_i) = \frac{1}{|P|}\sum_{p \in P} \frac{|\{r \in R: \text{visits}(r) > 1\}|}{|R|}$$
where $R$ is a grid of image regions.

4. **Scanpath Irregularity (SI)**: Measured using normalized scanpath saliency:
$$\text{SI}(I_i) = \frac{1}{|P|}\sum_{p \in P} \left(1 - \frac{1}{|F_p|-1}\sum_{j=1}^{|F_p|-1} \cos(\theta_j)\right)$$
where $\theta_j$ is the angle between consecutive saccade vectors.

5. **Attentional Spread (AS)**: Standard deviation of fixation coordinates:
$$\text{AS}(I_i) = \frac{1}{|P|}\sum_{p \in P} \sqrt{\text{Var}(x_f) + \text{Var}(y_f)}$$

6. **Time to First Fixation on Target (TFFT)**: Average time to fixate on the ground-truth region of interest.

The composite difficulty score is computed as:
$$D(I_i) = \alpha_1 \cdot \text{norm}(\text{MFD}) + \alpha_2 \cdot \text{norm}(\text{SF}) + \alpha_3 \cdot \text{norm}(\text{RR}) + \alpha_4 \cdot \text{norm}(\text{SI}) + \alpha_5 \cdot \text{norm}(\text{AS}) + \alpha_6 \cdot \text{norm}(\text{TFFT})$$
where $\text{norm}(\cdot)$ denotes min-max normalization and $\alpha_i$ are learnable weights determined through validation performance.

### 2.2 Difficulty Estimation Network

Since collecting eye-tracking data for all training images is impractical, we develop a Difficulty Estimation Network (DEN) that predicts gaze-based difficulty metrics from visual features alone.

#### Architecture

The DEN consists of:

1. **Visual Encoder**: A pretrained convolutional network (ResNet-50 or Vision Transformer) that extracts feature representations $\mathbf{h} = f_{\text{enc}}(I; \theta_{\text{enc}})$

2. **Multi-task Regression Head**: Predicts individual gaze metrics:
$$\hat{\mathbf{g}} = [\hat{g}_1, ..., \hat{g}_6] = f_{\text{reg}}(\mathbf{h}; \theta_{\text{reg}})$$
where each $\hat{g}_j$ corresponds to one of the six gaze metrics.

3. **Difficulty Aggregation**: Combines predicted metrics into final difficulty score:
$$\hat{D}(I) = \sum_{j=1}^6 \alpha_j \cdot \hat{g}_j$$

#### Training Objective

The DEN is trained on images with collected eye-tracking data using a multi-task loss:

$$\mathcal{L}_{\text{DEN}} = \sum_{j=1}^6 \lambda_j \|\hat{g}_j - g_j\|_2^2 + \gamma \|\hat{D} - D\|_2^2$$

where $g_j$ are ground-truth gaze metrics, $\lambda_j$ and $\gamma$ are loss weights, and the second term ensures consistency in the composite difficulty prediction.

We incorporate uncertainty estimation through Monte Carlo Dropout or Deep Ensembles to quantify prediction confidence, which will be used in the curriculum scheduler.

### 2.3 Adaptive Curriculum Scheduler

#### Curriculum Strategies

We propose three curriculum scheduling strategies:

**Strategy 1: Discrete Pacing**
Training progresses through discrete difficulty stages. At epoch $e$, the training set is:
$$\mathcal{D}_e = \{(I_i, y_i) : \hat{D}(I_i) \leq \tau_e\}$$
where $\tau_e = \tau_{\min} + (e/E) \cdot (\tau_{\max} - \tau_{\min})$ increases linearly over total epochs $E$.

**Strategy 2: Continuous Weighting**
All samples are available but weighted by difficulty:
$$w_i(e) = \exp\left(-\beta \cdot \max(0, \hat{D}(I_i) - \tau_e)\right)$$
The training loss becomes:
$$\mathcal{L}_{\text{train}}(e) = \frac{1}{|\mathcal{D}|}\sum_{i=1}^{|\mathcal{D}|} w_i(e) \cdot \ell(f(I_i; \theta), y_i)$$

**Strategy 3: Self-Paced Learning**
Combines model uncertainty with predicted difficulty:
$$w_i(e) = \mathbb{1}\left[\hat{D}(I_i) \leq \tau_e \text{ OR } \mathcal{L}_i^{(e-1)} \leq \delta_e\right]$$
where $\mathcal{L}_i^{(e-1)}$ is the previous epoch's loss on sample $i$, allowing the model to revisit previously difficult samples.

#### Dynamic Adaptation

The curriculum adapts based on training dynamics:
- **Plateau detection**: If validation performance plateaus for $k$ consecutive epochs, accelerate difficulty progression by increasing $\tau_e$ more rapidly
- **Forgetting prevention**: Periodically sample from easier examples (temperature-based sampling) to prevent catastrophic forgetting
- **Uncertainty-guided sampling**: Prioritize samples where DEN uncertainty is high, potentially indicating domain gaps

### 2.4 Experimental Design

#### Baseline Comparisons

We compare GDCL against:
1. **Random sampling**: Standard uniformly random mini-batches
2. **Self-paced learning**: Using model loss as difficulty metric
3. **Transfer teacher**: Using predictions from a pretrained model as difficulty
4. **Hand-crafted curricula**: Domain-specific heuristics (e.g., image resolution, number of objects)

#### Evaluation Protocol

For each dataset and baseline:
- Split data into train (70%), validation (15%), test (15%)
- Collect eye-tracking data on 20% of training images and all validation images
- Train DEN on eye-tracked training subset, validate on eye-tracked validation set
- Apply curriculum strategies to full training set using DEN predictions
- Train task-specific models (ResNet-50, EfficientNet) with different schedulers
- Measure convergence speed (epochs to reach target accuracy), final accuracy, sample efficiency (accuracy vs. training set size), and attention alignment (correlation between model attention maps and human gaze heatmaps)

#### Evaluation Metrics

1. **Performance metrics**:
   - Classification accuracy and F1-score
   - Training efficiency: epochs to reach 90% of final accuracy
   - Sample efficiency: performance with 25%, 50%, 75% of data

2. **Alignment metrics**:
   - **Gaze-Attention Correlation**: Pearson correlation between model attention maps (Grad-CAM, attention weights) and aggregated human gaze heatmaps
   - **Scanpath Similarity**: Dynamic Time Warping (DTW) distance between model-generated and human scanpaths using attention-based saccade simulation

3. **Robustness metrics**:
   - Performance on out-of-distribution samples
   - Adversarial robustness using standard attacks (FGSM, PGD)

#### Ablation Studies

- Effect of individual gaze metrics: Train DEN variants using subsets of the six gaze features
- Curriculum pacing: Compare different $\tau_e$ progression schedules (linear, exponential, step-wise)
- Transfer across domains: Train DEN on one dataset, apply to others to assess generalization
- Data requirements: Study performance vs. amount of eye-tracking data used to train DEN

## 3. Expected Outcomes & Impact

### Expected Outcomes

**Primary Research Contributions**:

1. **Validated Gaze-Based Difficulty Framework**: We expect to establish that eye-tracking metrics provide cognitively grounded difficulty measures that outperform existing heuristics. Based on preliminary analyses of existing eye-tracking datasets, we anticipate correlation coefficients above 0.6 between gaze-derived difficulty and model convergence speed.

2. **Improved Training Efficiency**: GDCL is expected to achieve 15-30% faster convergence compared to random sampling baselines across benchmark datasets, with more pronounced benefits in complex domains like medical imaging where expert gaze patterns encode domain knowledge.

3. **Enhanced Sample Efficiency**: In low-data regimes (25-50% of full training data), we anticipate GDCL will maintain 5-10% higher accuracy than baselines, particularly valuable for domains with expensive annotation requirements.

4. **Human-Aligned Representations**: Models trained with GDCL should demonstrate significantly higher correlation (20-40% improvement) between their attention mechanisms and human gaze patterns, as measured by gaze-attention correlation and scanpath similarity metrics.

5. **Transferable Difficulty Estimator**: The DEN trained on one domain should achieve reasonable transfer performance to related domains (e.g., natural images to satellite imagery), with expected correlation above 0.5 between predicted and actual gaze-derived difficulty.

**Secondary Contributions**:

- Comprehensive eye-tracking datasets for CIFAR-100, ChestX-ray14, and nuScenes with rich gaze annotations
- Open-source implementation of GDCL framework compatible with popular deep learning libraries
- Empirical insights into which gaze features are most predictive of learning difficulty across different visual domains

### Broader Impact

**Scientific Impact**:

This research advances multiple fields simultaneously. For **machine learning**, it establishes a new paradigm for curriculum learning grounded in human cognition rather than algorithmic heuristics, potentially inspiring similar approaches using other physiological signals. For **cognitive neuroscience**, the requirement that gaze patterns predict model training difficulty provides testable hypotheses about the relationship between visual attention and perceptual complexity. The framework also contributes to **interpretable AI** by creating models whose learning progression and internal representations align with human cognitive processes.

**Practical Applications**:

1. **Medical Imaging**: Radiologists' gaze patterns when examining rare pathologies could guide training of diagnostic AI systems, improving performance on underrepresented conditions while reducing the need for extensive labeled datasets.

2. **Autonomous Driving**: Expert drivers' attention patterns in hazardous scenarios could prioritize training on safety-critical situations, potentially improving perception systems' ability to detect rare but dangerous edge cases.

3. **Educational Technology**: The framework could be reversed—analyzing where AI models struggle could identify which educational materials require curriculum restructuring for human learners.

4. **Accessibility**: For domains like reading assistance (similar to GazeReader), understanding visual difficulty patterns could improve adaptive interfaces for users with cognitive or visual impairments.

**Ethical Considerations and Responsible AI**:

This research addresses several dimensions of trustworthy AI. By aligning model training with human perceptual strategies, GDCL may produce more predictable systems whose failure modes better match human intuitions, improving safety in critical applications. However, we must also consider potential risks:

- **Privacy concerns**: Eye-tracking data can reveal sensitive information about cognitive states and health conditions. Our protocols will ensure informed consent, data anonymization, and compliance with privacy regulations (GDPR, HIPAA where applicable).

- **Bias amplification**: If eye-tracking participants lack diversity, gaze-derived curricula may encode demographic biases. We will ensure diverse participant recruitment and analyze model fairness across demographic groups.

- **Generalization limitations**: Over-reliance on human gaze patterns may limit models' ability to discover non-human-like but effective visual strategies. We will explore hybrid approaches that balance human alignment with exploratory learning.

**Long-term Vision**:

This research represents a step toward bi-directional human-AI learning systems where humans and AI models mutually inform each other's learning processes. Future extensions could incorporate real-time gaze feedback during model training, creating interactive curriculum learning systems that adapt not just to model performance but to ongoing human supervisory signals. As eye-tracking technology becomes more accessible through webcam-based solutions and AR/VR integration, gaze-driven learning could transition from specialized applications to mainstream machine learning practice, fundamentally reshaping how we design human-centered AI systems.

In conclusion, Gaze-Driven Curriculum Learning bridges cognitive science and machine learning, offering both theoretical insights into human-aligned AI and practical improvements in training efficiency and model interpretability. By grounding curriculum design in measurable human cognitive patterns, this research contributes to the broader goal of developing AI systems that learn and perceive more like humans, ultimately enhancing collaboration, trust, and safety in human-AI interaction.