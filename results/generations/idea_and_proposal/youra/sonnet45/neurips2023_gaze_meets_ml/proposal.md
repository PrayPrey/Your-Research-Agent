# Research Proposal: Gaze-to-Attention Collaborative Loop (G2ACL) for Explainable Medical Diagnosis

## 1. Title

**Gaze-to-Attention Collaborative Loop (G2ACL): Bidirectional Human-AI Alignment for Explainable Medical Diagnosis Through Real-Time Attention Convergence**

## 2. Introduction

### 2.1 Background

Eye gaze has emerged as a powerful physiological signal for understanding human cognitive processes, particularly in medical image interpretation where radiologists' visual attention patterns reveal diagnostic reasoning strategies. Recent advances in eye-tracking technology and deep learning have enabled unprecedented opportunities to bridge human expertise with machine intelligence. However, current AI diagnostic systems face a critical challenge: **attention mismatch**—radiologists often focus on different image regions than the model, leading to misdiagnosis, reduced trust, and barriers to clinical adoption.

Existing approaches to integrating eye gaze with machine learning fall into three categories: (1) **training-time supervision**, where gaze annotations guide model learning but provide no inference-time interaction; (2) **post-hoc validation**, where gaze data retrospectively evaluates model attention for interpretability assessment; and (3) **unidirectional guidance**, where either human guides machine or machine guides human, but not both simultaneously. These approaches miss a fundamental opportunity: **real-time bidirectional collaboration** where human expertise and machine pattern recognition synergistically align during inference through iterative refinement.

The medical imaging domain presents an ideal testbed for this paradigm shift. Radiologists possess domain expertise and contextual reasoning capabilities, while deep learning models excel at detecting subtle patterns across large-scale data. Yet, when their attention diverges—the radiologist examining cardiac silhouette while the model detects peripheral lung nodules—diagnostic errors occur. Current explainable AI (XAI) methods provide post-hoc explanations (saliency maps, attention visualizations) but cannot dynamically adjust model reasoning based on real-time human input.

This research draws inspiration from **shared autonomy** paradigms in assistive robotics, where human intent (joystick commands, gaze direction) and autonomous control (robot path planning) blend through confidence-based arbitration functions. Wheelchair navigation systems and robotic teleoperation have demonstrated that bidirectional control loops with convergence guarantees enable stable task completion. We propose transferring this paradigm to explainable AI: treating human gaze as a control signal that modulates model attention weights, while model uncertainty heat maps guide human gaze to ambiguous regions, creating a feedback loop that converges to aligned human-machine reasoning.

### 2.2 Research Objectives

This research aims to develop and validate **G2ACL (Gaze-to-Attention Collaborative Loop)**, a bidirectional framework for real-time human-AI attention alignment in medical image diagnosis. The specific objectives are:

**Primary Objective:**
- Design and implement a bidirectional attention alignment system where radiologist gaze dynamically modulates deep learning attention weights during inference, while model uncertainty visualizations guide human gaze to high-uncertainty regions, achieving convergence within real-time latency constraints (<100ms).

**Secondary Objectives:**
1. Develop a learned gaze-attention mapping function $\theta$ that translates eye tracker coordinates to transformer attention weight adjustments through two-phase transfer learning (pre-training on REFLACX, fine-tuning on MIMIC-CXR).

2. Implement lazy attention recomputation optimization that caches non-gaze regions and updates only top-K attended areas to maintain real-time performance.

3. Establish convergence criteria combining KL divergence thresholds ($D_{KL} < 0.15$), iteration limits (maximum 5 iterations), and timeout constraints (10 seconds) to guarantee termination.

4. Validate diagnostic accuracy improvement (+5% F1 score), attention alignment (IOU > 0.70), and convergence reliability (≥80% success rate) through controlled user studies with board-certified radiologists.

5. Assess clinical feasibility through cognitive load measurement (NASA-TLX workload scores) and workflow integration evaluation.

### 2.3 Research Questions

**RQ1 (Existence):** Can bidirectional gaze-attention control loops reliably converge to stable alignment (KL divergence < 0.15) within practical iteration/time limits for medical image diagnosis tasks?

**RQ2 (Mechanism):** Does lazy attention recomputation (caching non-gaze regions, updating top-K areas) enable real-time performance (P99 latency ≤100ms) while maintaining diagnostic accuracy?

**RQ3 (Effectiveness):** Does G2ACL improve diagnostic accuracy (+5% F1 score) and attention alignment (IOU > 0.70) compared to static attention baselines and unidirectional gaze-supervised approaches?

**RQ4 (Generalization):** Can gaze-attention mapping functions transfer across medical imaging tasks through two-phase training with reduced annotation requirements?

**RQ5 (Usability):** Do uncertainty-guided visual cues impose acceptable cognitive load (NASA-TLX < 60) for clinical workflow integration?

### 2.4 Significance

This research addresses critical gaps at the intersection of explainable AI, human-computer interaction, and medical imaging:

**Theoretical Significance:**
- **Paradigm transfer:** First application of shared autonomy control theory from assistive robotics to explainable AI, establishing bidirectional human-AI collaboration as a formal framework with convergence guarantees.
- **Interactive XAI:** Extends explainable AI from passive explanation (post-hoc saliency maps) to active collaboration (real-time attention co-evolution), fundamentally reframing human-AI interaction.
- **Attention alignment theory:** Formalizes bidirectional attention convergence through KL divergence minimization, providing theoretical foundations for human-machine reasoning alignment.

**Methodological Significance:**
- **Gaze-attention integration:** Novel learned mapping function $\theta$ enabling end-to-end training of gaze-guided attention modulation for vision transformers.
- **Computational optimization:** Lazy recomputation algorithm reducing attention complexity from $O(N^2)$ to $O(K \cdot N)$ for real-time gaze-responsive systems.
- **Convergence protocols:** Formal stopping criteria balancing alignment quality, iteration efficiency, and real-time responsiveness.

**Practical Significance:**
- **Clinical decision support:** Reduces misdiagnosis from attention mismatch in radiology workflows, directly impacting patient safety and diagnostic quality.
- **Trust and adoption:** Provides verifiable reasoning pathways through spatial gaze-attention alignment, addressing "black box" concerns hindering clinical AI adoption.
- **Workflow integration:** Real-time latency enables seamless integration into existing Picture Archiving and Communication Systems (PACS) without disrupting clinical practice.
- **Generalization potential:** Framework applicable beyond medical imaging to document analysis, visual question answering, and any domain requiring human-AI attention alignment.

**Impact on Workshop Themes:**
This research directly addresses multiple workshop topics: (1) annotation and ML supervision with eye-gaze through bidirectional refinement, (2) attention mechanisms and their correlation with eye-gaze via convergence metrics, (3) human-AI interaction through shared autonomy paradigms, (4) explainable AI through verifiable reasoning alignment, and (5) radiology applications with clinical validation. The bidirectional collaborative loop paradigm has potential to transform how physiological signals inform machine learning across domains.

## 3. Methodology

### 3.1 Research Design Overview

The research follows a five-phase methodology: (1) **Gaze-Attention Mapping Development** through two-phase transfer learning, (2) **Bidirectional Loop Implementation** with lazy recomputation optimization, (3) **Convergence Protocol Design** with formal stopping criteria, (4) **Controlled User Study** with radiologists on MIMIC-CXR dataset, and (5) **Clinical Feasibility Assessment** through cognitive load and workflow integration evaluation.

### 3.2 Phase 1: Gaze-Attention Mapping Function Development

**Objective:** Learn end-to-end mapping $\theta$ from eye tracker coordinates to transformer attention weight modulations.

#### 3.2.1 Two-Phase Transfer Learning Protocol

**Phase 1A: Pre-training on REFLACX Dataset**

*Dataset:* REFLACX (Johnson et al., 2021) containing 3,940 chest X-ray images with radiologist eye-tracking annotations.

*Architecture:* Vision Transformer (ViT-B/16) with custom gaze-attention fusion module.

*Mapping Function:* The gaze-attention mapping $\theta$ translates gaze coordinates $(x_g, y_g)$ to spatial attention modulation weights:

$$\theta: (x_g, y_g, \mathbf{F}) \rightarrow \mathbf{W}_{\text{gaze}} \in \mathbb{R}^{H \times W}$$

where $\mathbf{F} \in \mathbb{R}^{H \times W \times D}$ represents spatial feature maps from the transformer encoder, and $\mathbf{W}_{\text{gaze}}$ is the gaze-derived attention weight map.

*Implementation:* Multi-layer perceptron (MLP) with spatial positional encoding:

$$\mathbf{W}_{\text{gaze}}[i,j] = \text{MLP}_\theta\left(\left[\mathbf{F}[i,j], \text{PE}(i,j), \text{Gauss}(i,j; x_g, y_g, \sigma)\right]\right)$$

where $\text{PE}(i,j)$ is 2D sinusoidal positional encoding, and $\text{Gauss}(i,j; x_g, y_g, \sigma)$ is a Gaussian kernel centered at gaze coordinates with standard deviation $\sigma = 2°$ visual angle.

*Training Objective:* Minimize combined loss:

$$\mathcal{L}_{\text{pre}} = \mathcal{L}_{\text{task}} + \lambda_1 \mathcal{L}_{\text{align}} + \lambda_2 \mathcal{L}_{\text{reg}}$$

where:
- $\mathcal{L}_{\text{task}}$ = Binary cross-entropy for pathology classification
- $\mathcal{L}_{\text{align}} = D_{KL}(\mathbf{P}_{\text{gaze}} || \mathbf{P}_{\text{attn}})$ = KL divergence between gaze fixation distribution and model attention distribution
- $\mathcal{L}_{\text{reg}} = ||\theta||_2^2$ = L2 regularization
- $\lambda_1 = 0.5$, $\lambda_2 = 0.01$ (hyperparameters tuned via validation set)

*Training Details:* 50 epochs, AdamW optimizer, learning rate $3 \times 10^{-4}$ with cosine annealing, batch size 32, image resolution 224×224.

**Phase 1B: Fine-tuning on MIMIC-CXR Dataset**

*Dataset:* MIMIC-CXR-JPG (Johnson et al., 2019) with 227,835 chest X-rays and 14 pathology labels. We collect gaze annotations for 500 training images and 200 test images from 10 radiologists.

*Fine-tuning Strategy:* Freeze ViT backbone, fine-tune only gaze mapping MLP $\theta$ and final classification head.

*Training Objective:* Same as Phase 1A but with task-specific pathology labels (pneumonia, cardiomegaly, edema, etc.).

*Training Details:* 20 epochs, learning rate $1 \times 10^{-4}$, batch size 16.

#### 3.2.2 Attention Modulation Mechanism

During inference, the learned mapping $\theta$ modulates transformer attention weights:

$$\mathbf{A}'[i] = \alpha \cdot \mathbf{A}[i] + (1-\alpha) \cdot \theta(\text{gaze}, \text{region}[i])$$

where:
- $\mathbf{A}[i]$ = Original attention weights for spatial region $i$
- $\mathbf{A}'[i]$ = Modulated attention weights
- $\alpha \in [0,1]$ = Modulation coefficient balancing model autonomy vs. gaze guidance
- $\theta(\text{gaze}, \text{region}[i])$ = Gaze-derived attention weight for region $i$

*Adaptive Modulation:* We implement adaptive $\alpha(t)$ that decreases as alignment improves:

$$\alpha(t) = \alpha_0 \cdot \exp\left(-\beta \cdot \max(0, D_{KL}^{(t)} - D_{\text{target}})\right)$$

where $\alpha_0 = 0.7$, $\beta = 2.0$, $D_{\text{target}} = 0.15$ (convergence threshold).

### 3.3 Phase 2: Bidirectional Loop Implementation

**Objective:** Implement real-time feedback loop where gaze modulates attention (human→model) and uncertainty guides gaze (model→human).

#### 3.3.1 Model-to-Human: Uncertainty-Guided Visual Cues

*Uncertainty Quantification:* Compute spatial entropy map from model predictions:

$$H[i,j] = -\sum_{c=1}^{C} p_c[i,j] \log p_c[i,j]$$

where $p_c[i,j]$ is the predicted probability for class $c$ at spatial location $(i,j)$, obtained by applying the classification head to each spatial feature token.

*Visual Cue Rendering:* High-uncertainty regions ($H[i,j] > H_{\text{threshold}}$) are highlighted with adaptive intensity:

$$I_{\text{cue}}[i,j] = \begin{cases}
\min\left(1.0, \frac{H[i,j]}{H_{\max}} \cdot \gamma\right) & \text{if } H[i,j] > H_{\text{threshold}} \\
0 & \text{otherwise}
\end{cases}$$

where $H_{\max}$ is the maximum entropy across the image, $\gamma = 0.8$ is the cue intensity scaling factor, and $H_{\text{threshold}}$ is set to the 75th percentile of entropy values.

*Rendering Strategy:* Semi-transparent yellow halos overlaid on original image, with intensity proportional to uncertainty. Cue intensity decreases as alignment improves to reduce distraction:

$$\gamma(t) = \gamma_0 \cdot \left(1 - \frac{t}{t_{\max}}\right)^{0.5}$$

where $\gamma_0 = 0.8$, $t$ is iteration number, $t_{\max} = 5$.

#### 3.3.2 Lazy Attention Recomputation Optimization

*Motivation:* Full transformer attention recomputation has $O(N^2)$ complexity where $N$ is the number of spatial tokens (e.g., $N = 196$ for 224×224 images with 16×16 patches). Real-time performance requires reducing this overhead.

*Algorithm:* Cache non-gaze regions, recompute only top-K gaze-attended regions.

**Step 1: Gaze Region Identification**
- Compute gaze-attention weights $\mathbf{W}_{\text{gaze}}$ using mapping $\theta$
- Select top-K regions: $\mathcal{R}_{\text{gaze}} = \text{TopK}(\mathbf{W}_{\text{gaze}}, K)$

**Step 2: Selective Recomputation**
- For regions $i \in \mathcal{R}_{\text{gaze}}$: Recompute attention $\mathbf{A}'[i]$ using modulation formula
- For regions $i \notin \mathcal{R}_{\text{gaze}}$: Use cached attention $\mathbf{A}[i]$ from previous iteration

**Step 3: Attention Aggregation**
$$\mathbf{A}_{\text{final}}[i] = \begin{cases}
\mathbf{A}'[i] & \text{if } i \in \mathcal{R}_{\text{gaze}} \\
\mathbf{A}_{\text{cache}}[i] & \text{otherwise}
\end{cases}$$

*Complexity Analysis:* Reduces from $O(N^2)$ to $O(K \cdot N)$ where $K = 20\text{-}50 \ll N = 196$.

*Latency Budget:*
- Base ViT inference: ~50-80ms
- Gaze mapping $\theta$: ~5-10ms
- Top-K selection: ~2-5ms
- Selective attention recomputation: ~15-25ms (for K=30)
- Uncertainty computation + cue rendering: ~5-10ms
- **Total: ~80-110ms** (target P99 ≤100ms)

#### 3.3.3 Bidirectional Convergence Loop

**Algorithm 1: G2ACL Bidirectional Refinement**

```
Input: Image I, Initial model M, Eye tracker E, Max iterations T_max=5, Timeout t_max=10s
Output: Aligned attention A_final, Diagnosis y_pred

1. Initialize:
   - A_0 ← M.forward(I)  // Initial attention without gaze
   - t ← 0, converged ← False
   - Start timer

2. While (t < T_max) AND (timer < t_max) AND (NOT converged):
   
   a. Capture gaze: (x_g, y_g) ← E.get_gaze()
   
   b. Human→Model: Modulate attention
      - W_gaze ← θ(x_g, y_g, M.features)
      - R_gaze ← TopK(W_gaze, K=30)
      - For i in R_gaze:
          A_t[i] ← α(t)·A_{t-1}[i] + (1-α(t))·θ(gaze, region[i])
      - For i not in R_gaze:
          A_t[i] ← A_{t-1}[i]  // Use cached attention
   
   c. Model→Human: Guide gaze with uncertainty
      - H ← Compute_Entropy(M.predict(I, A_t))
      - Render_Cues(H, threshold=percentile(H, 75), intensity=γ(t))
   
   d. Check convergence:
      - P_gaze ← Gaze_Distribution(x_g, y_g, history)
      - P_attn ← Attention_Distribution(A_t)
      - D_KL ← KL_Divergence(P_gaze || P_attn)
      - If D_KL < 0.15:
          converged ← True
   
   e. t ← t + 1

3. Return A_final ← A_t, y_pred ← M.classify(I, A_final)
```

**Convergence Metrics:**

*KL Divergence:* Measures alignment between gaze and attention distributions:

$$D_{KL}(\mathbf{P}_{\text{gaze}} || \mathbf{P}_{\text{attn}}) = \sum_{i=1}^{N} \mathbf{P}_{\text{gaze}}[i] \log \frac{\mathbf{P}_{\text{gaze}}[i]}{\mathbf{P}_{\text{attn}}[i]}$$

where distributions are computed by normalizing gaze fixation density and attention weights over spatial regions.

*Convergence Criterion:* $D_{KL} < 0.15$ (empirically determined threshold balancing alignment quality and iteration efficiency).

*Stopping Conditions:*
1. **Convergence:** $D_{KL} < 0.15$ (success)
2. **Iteration limit:** $t \geq 5$ (timeout with best-effort alignment)
3. **Time limit:** Elapsed time $\geq 10$ seconds (hard timeout)

### 3.4 Phase 3: Experimental Validation

#### 3.4.1 Dataset and Participants

**Medical Imaging Dataset:**
- **Source:** MIMIC-CXR-JPG (publicly available, IRB-approved)
- **Test Set:** 200 chest X-ray images stratified by:
  - Pathology prevalence: Common (pneumonia, cardiomegaly) vs. Rare (pneumothorax, mass)
  - Image difficulty: Easy (single pathology, clear findings) vs. Hard (multiple pathologies, subtle findings)
  - Demographic balance: Age, sex distribution representative of clinical population

**Participants:**
- **N = 10 board-certified radiologists**
- **Inclusion criteria:** ≥2 years post-residency clinical experience in chest radiology
- **Exclusion criteria:** Visual impairments affecting eye tracking accuracy, prior participation in gaze-guided AI studies (to avoid learning effects)
- **Recruitment:** Academic medical centers with IRB approval
- **Compensation:** $100/hour (standard research participation rate)

**Eye Tracking Hardware:**
- **Device:** Tobii Pro Fusion (250 Hz sampling rate, <0.5° accuracy)
- **Calibration:** 9-point calibration at session start, validation test (accuracy check), recalibration every 15 minutes
- **Drift monitoring:** Continuous validation using periodic fixation targets

#### 3.4.2 Experimental Design

**Design Type:** Within-subjects repeated measures with randomized condition assignment.

**Conditions:**
1. **G2ACL (Bidirectional):** Full framework with gaze→attention modulation and uncertainty→gaze guidance
2. **Static Baseline:** Standard ViT-B/16 without gaze input (pre-trained on MIMIC-CXR)
3. **Gaze-Supervised:** Model trained with gaze supervision (Phase 1A+1B) but no inference-time interaction
4. **Uncertainty-Only:** Model displays uncertainty cues but does not accept gaze modulation (unidirectional model→human)

**Task Assignment:**
- Each radiologist diagnoses all 200 test images
- Condition assignment: Randomized per image using Latin square design to counterbalance order effects
- Each condition receives 50 images (balanced across pathology types and difficulty levels)

**Procedure:**
1. **Pre-session (15 min):**
   - Informed consent, demographic questionnaire
   - Eye tracker calibration and validation
   - Practice trials (10 images per condition, excluded from analysis)

2. **Main session (90-120 min):**
   - Diagnose 200 images in randomized order
   - For each image:
     - View image with assigned condition interface
     - Provide diagnosis (binary labels for 14 pathologies)
     - Rate confidence (1-5 Likert scale)
     - Maximum 60 seconds per image (clinical realism)
   - Mandatory 5-minute break every 30 minutes
   - Recalibration every 15 minutes

3. **Post-session (15 min):**
   - NASA-TLX workload questionnaire (per condition)
   - Usability questionnaire (perceived usefulness, ease of use, workflow integration)
   - Semi-structured interview on visual cue perception and gaze awareness

**Data Collection:**
- **Diagnostic labels:** Binary predictions for 14 pathology classes
- **Confidence scores:** 1-5 Likert scale per diagnosis
- **Gaze data:** Fixation coordinates, duration, saccade patterns (250 Hz)
- **Attention maps:** Spatial attention weights from transformer (per iteration)
- **Latency:** Inference time per image (milliseconds)
- **Convergence metrics:** KL divergence, iteration count, timeout flags
- **Cognitive load:** NASA-TLX scores (mental demand, physical demand, temporal demand, performance, effort, frustration)
- **Usability ratings:** 5-point Likert scales for perceived usefulness, ease of use, trust, workflow fit

#### 3.4.3 Evaluation Metrics

**Primary Outcome: Diagnostic Accuracy**

*Metrics:*
- **F1 Score (Macro-average):** Harmonic mean of precision and recall across 14 pathology labels
  $$F1 = \frac{1}{C} \sum_{c=1}^{C} \frac{2 \cdot \text{Precision}_c \cdot \text{Recall}_c}{\text{Precision}_c + \text{Recall}_c}$$
- **AUC-ROC:** Area under receiver operating characteristic curve (per pathology, macro-averaged)

*Hypothesis Test:* Paired t-test comparing $F1_{\text{G2ACL}}$ vs. $F1_{\text{Static}}$ (within-subject design)

*Success Criterion:* $F1_{\text{G2ACL}} \geq F1_{\text{Static}} + 0.05$ with $p < 0.05$ and Cohen's $d \geq 0.50$ (medium effect size)

**Secondary Outcome 1: Attention Alignment**

*Metrics:*
- **KL Divergence:** $D_{KL}(\mathbf{P}_{\text{gaze}} || \mathbf{P}_{\text{attn}})$ at convergence
- **Intersection-over-Union (IOU):** Spatial overlap between gaze fixation regions and top-K attention regions
  $$\text{IOU} = \frac{|\mathcal{R}_{\text{gaze}} \cap \mathcal{R}_{\text{attn}}|}{|\mathcal{R}_{\text{gaze}} \cup \mathcal{R}_{\text{attn}}|}$$
  where regions are defined as connected components above 50th percentile threshold

*Success Criteria:*
- $D_{KL} < 0.15$ for ≥80% of converged cases
- $\text{IOU} \geq 0.70$ for converged cases

**Secondary Outcome 2: Convergence Reliability**

*Metrics:*
- **Convergence rate:** Proportion of cases achieving $D_{KL} < 0.15$ within 5 iterations
- **Iteration count:** Mean and median iterations to convergence
- **Timeout rate:** Proportion of cases exceeding 10-second limit

*Success Criterion:* Convergence rate ≥ 0.80 (binomial test, $p < 0.05$)

**Secondary Outcome 3: Real-Time Performance**

*Metrics:*
- **Latency distribution:** P50, P95, P99 inference time (milliseconds)
- **Latency breakdown:** Component-wise profiling (base ViT, gaze mapping, attention recomputation, cue rendering)

*Success Criterion:* $P99_{\text{latency}} \leq 100$ ms

**Secondary Outcome 4: Cognitive Load and Usability**

*Metrics:*
- **NASA-TLX Total Workload:** Sum of 6 subscales (range 0-100)
- **Perceived Usefulness:** 5-point Likert scale (1=strongly disagree, 5=strongly agree)
- **Workflow Integration:** Qualitative themes from semi-structured interviews

*Success Criteria:*
- NASA-TLX $\leq 60$ (moderate load, comparable to standard PACS reading)
- ≥70% of radiologists rate usefulness ≥4/5

#### 3.4.4 Statistical Analysis Plan

**Power Analysis:**
- **Target effect size:** Cohen's $d = 0.50$ (medium effect for F1 improvement)
- **Significance level:** $\alpha = 0.05$ (two-tailed)
- **Power:** $1 - \beta = 0.80$
- **Required sample:** $n = 10$ radiologists × 50 images per condition = 500 diagnoses per condition (sufficient for within-subjects design with repeated measures)

**Primary Analysis:**
- **Paired t-test:** Compare $F1_{\text{G2ACL}}$ vs. $F1_{\text{Static}}$ (within-subject)
- **Effect size:** Cohen's $d$ with 95% confidence interval (bootstrap, 10,000 resamples)
- **Multiple comparisons:** Bonferroni correction for 4-way condition comparison ($\alpha_{\text{adj}} = 0.0125$)

**Secondary Analyses:**
- **Convergence rate:** Binomial test (observed proportion vs. 0.80 threshold)
- **Latency validation:** Bootstrap 95% CI for P99 latency
- **Subgroup analyses:**
  - Stratify by radiologist experience (2-5 years, 5-10 years, >10 years)
  - Stratify by pathology type (common vs. rare)
  - Stratify by image difficulty (easy vs. hard)
- **Mixed-effects models:** Account for random effects of radiologist and image while testing condition effects

**Confound Control:**
- **Order effects:** Latin square counterbalancing, exclude first 10 images per condition as practice trials
- **Eye tracker drift:** Recalibration every 15 min, drift validation tests, exclude trials with >2° drift
- **Expertise variation:** Include radiologist experience as covariate in mixed-effects models
- **Image difficulty:** Stratified sampling ensures balanced difficulty across conditions

**Sensitivity Analyses:**
- **Threshold variation:** Test convergence criteria $D_{KL} \in \{0.10, 0.15, 0.20\}$ to assess robustness
- **K parameter:** Vary top-K regions $K \in \{10, 20, 30, 50\}$ to measure latency-accuracy tradeoff
- **Modulation coefficient:** Test fixed $\alpha \in \{0.3, 0.5, 0.7\}$ vs. adaptive $\alpha(t)$

### 3.5 Phase 4: Ablation Studies and Mechanism Validation

**Objective:** Isolate contributions of individual components and validate causal mechanisms.

#### 3.5.1 Component Ablation

**Ablation Conditions:**
1. **No gaze modulation:** Uncertainty cues only (model→human unidirectional)
2. **No uncertainty cues:** Gaze modulation only (human→model unidirectional)
3. **Fixed $\alpha$:** Replace adaptive $\alpha(t)$ with fixed $\alpha = 0.5$
4. **No lazy recomputation:** Full attention recomputation (measure latency impact)
5. **Random cues:** Replace entropy-based cues with random region highlighting (control for visual distraction)

**Metrics:** F1 score, convergence rate, latency, IOU for each ablation vs. full G2ACL

**Analysis:** Quantify contribution of each component via performance degradation when removed

#### 3.5.2 Transfer Learning Validation

**Objective:** Validate two-phase training effectiveness.

**Conditions:**
1. **Two-phase (proposed):** REFLACX pre-training + MIMIC-CXR fine-tuning (100 annotated images)
2. **End-to-end:** MIMIC-CXR only (500 annotated images)
3. **No pre-training:** MIMIC-CXR only (100 annotated images)
4. **Frozen mapping:** Pre-trained $\theta$ without fine-tuning

**Metrics:** F1 score, convergence rate, IOU, annotation efficiency (performance per annotated image)

**Success Criterion:** Two-phase F1 ≥ End-to-end F1 - 0.02 (non-inferior with 80% less data)

#### 3.5.3 Convergence Dynamics Analysis

**Objective:** Characterize convergence behavior and identify failure modes.

**Analyses:**
1. **Trajectory visualization:** Plot $D_{KL}(t)$ over iterations for converged vs. non-converged cases
2. **Oscillation detection:** Identify cases where $D_{KL}$ increases between iterations (instability)
3. **Timeout analysis:** Characterize images/pathologies associated with non-convergence
4. **Attention drift:** Measure spatial stability of attention maps across iterations

**Metrics:**
- **Convergence speed:** Iterations to reach $D_{KL} < 0.15$
- **Stability:** Variance of $D_{KL}$ across iterations
- **Spatial consistency:** IOU between attention maps at consecutive iterations

### 3.6 Phase 5: Clinical Feasibility Assessment

**Objective:** Evaluate real-world deployment readiness.

#### 3.6.1 Workflow Integration Study

**Setting:** Simulated clinical reading room with PACS workstation

**Participants:** Same 10 radiologists from Phase 3

**Task:** Read 50 clinical cases (mix of normal and pathological) using G2ACL integrated into PACS interface

**Metrics:**
- **Reading time:** Time per case (compare to baseline PACS reading)
- **Workflow disruption:** Frequency of calibration issues, system errors, user frustration events
- **Adoption willingness:** Post-study survey on likelihood of using G2ACL in clinical practice (1-5 Likert)

#### 3.6.2 Cognitive Load Deep Dive

**Methods:**
- **NASA-TLX:** Detailed subscale analysis (mental demand, physical demand, temporal demand, performance, effort, frustration)
- **Dual-task paradigm:** Secondary task (auditory response) to measure cognitive reserve
- **Pupillometry:** Pupil diameter as physiological cognitive load indicator (collected via eye tracker)

**Analysis:** Correlate cognitive load metrics with performance (F1 score) and convergence (iteration count)

#### 3.6.3 Qualitative User Experience

**Semi-structured interviews (30 min per radiologist):**
- Perceived benefits and limitations of G2ACL
- Visual cue perception (helpful vs. distracting)
- Gaze awareness and self-monitoring
- Trust in model suggestions
- Workflow integration challenges
- Suggestions for improvement

**Thematic analysis:** Identify recurring themes using grounded theory approach (open coding, axial coding, selective coding)

### 3.7 Ethical Considerations

**IRB Approval:** Obtain institutional review board approval for human subjects research (radiologist participants, use of clinical imaging data)

**Informed Consent:** All participants provide written informed consent explaining study purpose, procedures, risks, benefits, and right to withdraw

**Data Privacy:**
- MIMIC-CXR dataset: Publicly available, de-identified per HIPAA standards
- Gaze data: De-identified, stored on encrypted servers, access restricted to research team
- No patient identifiers collected or retained

**Participant Safety:**
- Eye tracking non-invasive, no known risks
- Mandatory breaks to prevent fatigue
- Right to withdraw without penalty

**Bias Mitigation:**
- Stratified sampling ensures demographic balance in test set
- Radiologist diversity (experience levels, training backgrounds)
- Transparent reporting of limitations and failure modes

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Primary Hypothesis Validation:**

We expect G2ACL to achieve **+5% F1 score improvement** over static attention baselines (from ~0.70 to ~0.75) on MIMIC-CXR chest X-ray diagnosis, with **≥80% convergence rate** within 5 iterations and **P99 latency ≤100ms**. This will demonstrate that bidirectional human-AI attention alignment provides measurable diagnostic value while maintaining real-time responsiveness.

**Attention Alignment:**

We anticipate **IOU ≥ 0.70** between gaze fixation regions and model attention regions for converged cases, representing a substantial improvement over post-hoc gaze-attention correlation (~0.50-0.65 in prior work). This spatial alignment will provide verifiable evidence of human-machine reasoning convergence.

**Convergence Dynamics:**

We expect **mean convergence in 2-3 iterations** for typical cases, with **<20% timeout rate** for complex multi-pathology images. KL divergence trajectories will show monotonic decrease for stable cases and oscillation patterns for challenging cases, informing future refinements.

**Component Contributions:**

Ablation studies will reveal:
- **Bidirectional loop:** +3-4% F1 improvement over unidirectional approaches
- **Lazy recomputation:** 40-50% latency reduction vs. full recomputation with <1% accuracy loss
- **Adaptive $\alpha(t)$:** +1-2% F1 improvement over fixed modulation
- **Uncertainty-guided cues:** +2-3% convergence rate improvement

**Transfer Learning Efficiency:**

Two-phase training will achieve **comparable performance** (within 2% F1) to end-to-end training while requiring **80% fewer gaze annotations** (100 vs. 500 images), demonstrating practical scalability.

**Clinical Feasibility:**

We expect **NASA-TLX scores ≤60** (moderate cognitive load) and **≥70% radiologists rating usefulness ≥4/5**, indicating clinical deployment readiness. Qualitative interviews will identify workflow integration challenges (e.g., calibration frequency, visual cue design preferences) to guide future development.

**Failure Mode Characterization:**

We anticipate **non-convergence** for:
- Multi-pathology images with spatially distributed findings (>3 pathologies)
- Subtle findings requiring high magnification (small nodules <5mm)
- Cases where radiologist and model have fundamentally different diagnostic strategies (e.g., model detects incidental findings radiologist deems clinically irrelevant)

These failure modes will inform scope boundaries and future research directions.

### 4.2 Theoretical Impact

**Paradigm Shift in Explainable AI:**

G2ACL will establish **interactive collaboration** as a new paradigm for explainable AI, moving beyond passive post-hoc explanations to active real-time reasoning alignment. This reframes XAI from "explaining model decisions to humans" to "co-constructing decisions through bidirectional feedback."

**Cross-Domain Knowledge Transfer:**

Successful application of **shared autonomy control theory** from assistive robotics to deep learning will open new research directions:
- Confidence-based arbitration functions for human-AI task allocation
- Convergence guarantees for interactive machine learning systems
- Formal verification of human-machine collaboration protocols

**Attention Alignment Theory:**

The framework will contribute formal foundations for **human-machine attention convergence**, including:
- KL divergence as alignment metric with empirically validated thresholds
- Convergence conditions for bidirectional control loops in high-dimensional attention spaces
- Trade-offs between alignment speed, cognitive load, and diagnostic accuracy

### 4.3 Methodological Impact

**Gaze-Guided Deep Learning:**

The learned gaze-attention mapping function $\theta$ will provide a **reusable architectural component** for vision transformers, enabling:
- Plug-and-play integration into existing ViT-based models
- Transfer learning across medical imaging modalities (X-ray, CT, MRI)
- Extension to non-medical domains (document analysis, visual QA)

**Computational Optimization:**

Lazy attention recomputation will establish **design patterns** for real-time gaze-responsive systems:
- Selective computation strategies for interactive deep learning
- Latency budgeting for human-in-the-loop inference
- Cache-aware attention mechanisms

**Evaluation Frameworks:**

The multi-metric evaluation protocol (accuracy, alignment, convergence, latency, cognitive load) will provide a **template** for assessing interactive AI systems, addressing gaps in current XAI evaluation practices that focus solely on explanation quality.

### 4.4 Practical Impact

**Clinical Decision Support:**

G2ACL will directly improve **patient safety** by reducing misdiagnosis from attention mismatch. In radiology workflows where radiologists review hundreds of images daily, even 5% accuracy improvement translates to:
- **Fewer missed diagnoses** (e.g., overlooked lung nodules, pneumothorax)
- **Reduced false positives** (unnecessary follow-up imaging, patient anxiety)
- **Enhanced diagnostic confidence** (spatial alignment provides verification)

**Trust and Adoption:**

By providing **verifiable reasoning pathways** through gaze-attention alignment, G2ACL addresses the primary barrier to clinical AI adoption: lack of trust in "black box" systems. Radiologists can visually confirm that the model focuses on the same regions they consider diagnostically relevant, increasing willingness to integrate AI into practice.

**Workflow Integration:**

Real-time latency (<100ms) enables **seamless integration** into existing PACS workflows without disrupting clinical efficiency. Radiologists can use G2ACL as a "second opinion" system that adapts to their reasoning in real-time, rather than a separate post-hoc review step.

**Generalization Beyond Medical Imaging:**

The framework is applicable to diverse domains:
- **Document analysis:** Legal contract review, scientific literature screening
- **Visual question answering:** Educational tutoring systems, accessibility tools
- **Autonomous vehicles:** Driver-vehicle attention alignment for semi-autonomous driving
- **AR/VR:** Gaze-guided content rendering, interactive training simulations

### 4.5 Broader Impact on Workshop Themes

**Gaze Meets ML Community:**

This research will catalyze workshop discussions on:
- **Bidirectional human-AI interaction:** Moving beyond unidirectional supervision/validation to collaborative loops
- **Real-time physiological computing:** Integrating eye gaze into inference pipelines with latency constraints
- **Convergence guarantees:** Formal verification of interactive ML systems
- **Cross-domain paradigm transfer:** Applying robotics control theory to deep learning

**Future Research Directions:**

G2ACL will inspire follow-up work on:
- **Multi-modal physiological integration:** Combining gaze with EEG, GSR, pupillometry for richer human state estimation
- **Privacy-preserving gaze processing:** Federated learning and differential privacy for multi-institution clinical trials
- **Adaptive automation:** Dynamic task allocation between human and AI based on real-time performance monitoring
- **Neuroscience validation:** fMRI studies correlating gaze-attention alignment with neural activation patterns

**Ethical and Societal Considerations:**

The research will contribute to discussions on:
- **Human agency in AI systems:** Ensuring humans retain control and decision-making authority
- **Cognitive augmentation vs. deskilling:** Balancing AI assistance with radiologist skill development
- **Equity and access:** Ensuring gaze-guided systems are accessible across diverse clinical settings (resource-limited environments, varying hardware availability)

### 4.6 Limitations and Future Work

**Current Scope Limitations:**

- **Single-image diagnosis:** Does not address longitudinal analysis (time-series, CT volumes)
- **Expert users only:** Framework designed for experienced radiologists; novice gaze patterns may be noisy
- **Medical imaging focus:** Cross-domain transfer (e.g., document QA) requires additional validation
- **Commercial eye trackers:** Requires specialized hardware; not yet compatible with standard displays

**Future Extensions:**

1. **Multi-modal integration:** Incorporate EEG (cognitive load), GSR (arousal), pupillometry (uncertainty) for richer human state modeling
2. **Privacy-preserving deployment:** Implement federated learning for multi-institution clinical trials while protecting gaze data privacy
3. **Adaptive automation:** Dynamic task allocation where AI handles routine cases, human focuses on complex cases, with smooth handoff based on uncertainty
4. **3D volumetric imaging:** Extend to CT/MRI with slice-wise gaze tracking and 3D attention mechanisms
5. **Novice training:** Use G2ACL to train radiology residents by guiding their gaze to diagnostically relevant regions
6. **Cross-cultural validation:** Test generalization across radiologists trained in different educational systems (Western vs. Eastern medical curricula)

### 4.7 Dissemination and Open Science

**Publications:**
- **Primary venue:** Workshop on Gaze Meets ML (initial results)
- **Follow-up venues:** Medical Image Computing and Computer Assisted Intervention (MICCAI), Conference on Human Factors in Computing Systems (CHI), Journal of Medical Imaging

**Open-Source Release:**
- **Code:** PyTorch implementation of G2ACL framework (GitHub repository with documentation)
- **Models:** Pre-trained gaze-attention mapping function $\theta$ (HuggingFace model hub)
- **Data:** Gaze annotations for MIMIC-CXR test set (200 images, 10 radiologists) released under data use agreement

**Clinical Translation:**
- **Collaboration:** Partner with radiology departments for pilot deployment studies
- **Regulatory pathway:** Explore FDA 510(k) clearance for clinical decision support software
- **Industry engagement:** Engage PACS vendors (e.g., GE Healthcare, Philips) for commercial integration

---

**Conclusion:**

The Gaze-to-Attention Collaborative Loop (G2ACL) represents a paradigm shift in explainable AI, transforming static attention mechanisms into dynamic human-AI partnerships with convergence guarantees. By transferring shared autonomy principles from assistive robotics to deep learning, this research establishes bidirectional collaboration as a formal framework for interactive machine learning. The expected outcomes—improved diagnostic accuracy, verifiable attention alignment, real-time responsiveness, and clinical feasibility—will directly impact patient safety in radiology while opening new research directions across machine learning, human-computer interaction, and neuroscience. This work addresses critical gaps identified by the Gaze Meets ML workshop community and provides a foundation for future physiological computing systems that seamlessly integrate human expertise with machine intelligence.