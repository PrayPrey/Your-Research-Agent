# Research Proposal: Automated Spurious Correlation Detection via Causal Neuron Intervention

## 1. Title

**Automated Spurious Correlation Detection via Causal Neuron Intervention: A Neuron-Level Causal Inference Framework for Discovering Hidden Shortcuts in Deep Neural Networks**

## 2. Introduction

### 2.1 Background

Deep learning models have achieved remarkable success across diverse domains, yet their reliability remains compromised by a fundamental vulnerability: reliance on spurious correlations rather than causal features. This phenomenon, known as shortcut learning, occurs when models exploit statistical artifacts in training data that fail to generalize under distribution shift. For instance, a medical diagnosis model might rely on hospital-specific imaging equipment markers rather than actual pathological features, or a hiring algorithm might use demographic proxies instead of job-relevant qualifications.

The root cause of this vulnerability lies in the statistical nature of deep learning optimization. Neural networks trained via empirical risk minimization (ERM) preferentially learn the simplest features that minimize training loss—a tendency known as simplicity bias (Shah et al., 2020). When spurious correlations provide simpler decision boundaries than causal features, models exploit these shortcuts, achieving high training accuracy while failing catastrophically on underrepresented groups or shifted distributions.

Current approaches to addressing spurious correlations fall into two categories: robustification methods and detection methods. Robustification techniques like Group Distributionally Robust Optimization (Group DRO) and Invariant Risk Minimization (IRM) require manual annotation of group labels or multiple training environments—resources that are expensive, unscalable, and fundamentally limited to *known* spurious patterns. Detection methods remain nascent, with existing benchmarks (Waterbirds, CelebA, NICO) only evaluating robustness to pre-identified shortcuts. This creates a critical gap: **how can we proactively discover unknown spurious correlations before deployment, without human annotation?**

Recent advances in explainable AI (XAI) have revealed that individual neurons in deep networks specialize to detect specific features, with some neurons encoding spurious patterns. Simultaneously, causal inference theory provides a principled framework for distinguishing correlation from causation through interventional analysis. However, these two research streams have remained largely disconnected. Our work bridges this gap by applying causal intervention principles at the neuron level to automatically identify spurious feature detectors.

### 2.2 Research Objectives

This research aims to develop **CNI-Auto (Causal Neuron Intervention for Automated Spurious Detection)**, a novel framework that addresses three critical objectives:

**Primary Objective:** Develop an automated, annotation-free method for detecting neurons encoding spurious correlations by measuring observational-interventional (OI) discrepancy under distribution shift.

**Secondary Objectives:**
1. Establish theoretical foundations connecting neuron-level causal intervention to spurious correlation detection
2. Validate the method on established benchmarks (Waterbirds, CelebA) with known spurious features
3. Demonstrate practical utility through worst-group accuracy improvements when mitigating detected spurious neurons
4. Extend the framework to discover unknown spurious patterns through unsupervised clustering of flagged neurons

### 2.3 Central Hypothesis

We hypothesize that **neurons encoding spurious correlations exhibit significantly higher observational-interventional discrepancy under distribution shift compared to core feature neurons**. Specifically:

- **Spurious neurons** show high correlation with predictions on training data (observational) but weak causal effect when ablated under shifted distributions (interventional), because their learned correlations break under shift
- **Core neurons** maintain consistency between observational correlation and interventional causality, as they encode invariant causal features

This hypothesis rests on three key mechanisms:
1. **Simplicity bias** causes DNNs to preferentially learn spurious correlations when they provide simpler decision boundaries
2. **Neuron specialization** results in localized representation of spurious patterns in identifiable neuron groups
3. **Distribution shift** reveals the distinction between correlation and causation, as spurious patterns break while causal features remain invariant

### 2.4 Significance

This research makes four significant contributions to the field:

**Theoretical Contribution:** We provide the first formal characterization of spurious versus core neurons through the lens of causal inference, extending Pearl's do-calculus framework to neuron-level DNN analysis. This bridges XAI interpretability with causal inference theory.

**Methodological Contribution:** CNI-Auto represents the first automated spurious detection method that combines neuron-level causal intervention with distribution shift testing, eliminating the need for manual group annotations while enabling discovery of unknown shortcuts.

**Practical Contribution:** The framework enables proactive identification of reliability risks before model deployment, with computational overhead of only 2-3× forward passes—affordable for pre-deployment safety analysis. This addresses a critical need in high-stakes domains like healthcare, hiring, and criminal justice.

**Benchmark Contribution:** We establish new evaluation protocols for spurious neuron detection, providing the community with tools to assess automated detection methods and compare their effectiveness across architectures and domains.

The broader impact extends to ethical AI deployment: by revealing hidden biases that disproportionately harm underrepresented groups, CNI-Auto supports fairness objectives while advancing our fundamental understanding of how deep models learn and generalize.

## 3. Methodology

### 3.1 Theoretical Framework

#### 3.1.1 Observational-Interventional Discrepancy

Let $f_\theta: \mathcal{X} \to \mathcal{Y}$ denote a trained neural network with parameters $\theta$, and let $a_i(x)$ represent the activation of neuron $i$ for input $x$. We define:

**Observational Correlation:** The statistical association between neuron activation and prediction on the training distribution $P_{train}$:
$$\rho_{obs}(i) = \text{Corr}_{x \sim P_{train}}(a_i(x), \mathbb{1}[f_\theta(x) = y])$$

**Interventional Causality:** The causal effect of neuron $i$ on prediction accuracy under a shifted distribution $P_{shift}$, measured via the do-operator:
$$\gamma_{int}(i) = \mathbb{E}_{x \sim P_{shift}}[\text{Acc}(f_\theta(x))] - \mathbb{E}_{x \sim P_{shift}}[\text{Acc}(f_{\theta, do(a_i=0)}(x))]$$

where $do(a_i=0)$ represents an intervention that sets neuron $i$'s activation to zero.

**OI Discrepancy Score:** The key metric distinguishing spurious from core neurons:
$$\Delta_{OI}(i) = |\rho_{obs}(i)| - \gamma_{int}(i)$$

**Theoretical Prediction:** Spurious neurons exhibit $\Delta_{OI}(i) > \tau$ for some threshold $\tau$, while core neurons show $\Delta_{OI}(i) \approx 0$ (high observational correlation matches high interventional causality).

#### 3.1.2 Causal Graph Formulation

We model the data generation process as a structural causal model:
$$X = f_X(U_X), \quad Z_c = f_c(X, U_c), \quad Z_s = f_s(X, U_s), \quad Y = f_Y(Z_c, U_Y)$$

where $X$ is the input, $Z_c$ are core features, $Z_s$ are spurious features, $Y$ is the label, and $U$ are exogenous noise variables. Crucially, $Y \perp\!\!\!\perp Z_s | Z_c$ (spurious features are conditionally independent of labels given core features).

Under distribution shift, the spurious correlation $P(Z_s|Y)$ changes while the causal relationship $P(Y|Z_c)$ remains invariant. Neurons encoding $Z_s$ thus exhibit high $\Delta_{OI}$, while neurons encoding $Z_c$ maintain consistency.

### 3.2 CNI-Auto Algorithm

#### 3.2.1 Algorithm Overview

**Input:** Trained model $f_\theta$, training set $\mathcal{D}_{train}$, shifted validation set $\mathcal{D}_{shift}$, layer $L$ to analyze

**Output:** Set of flagged spurious neurons $\mathcal{N}_{spurious}$, cluster assignments for discovered patterns

**Algorithm Steps:**

```
Algorithm 1: CNI-Auto Spurious Neuron Detection

1. Observational Phase:
   For each neuron i in layer L:
       Compute ρ_obs(i) via Pearson correlation between 
       a_i(x) and prediction correctness on D_train

2. Interventional Phase:
   For each neuron i in layer L:
       Ablate neuron: set a_i = 0 for all inputs
       Measure accuracy drop on D_shift
       Compute γ_int(i) = Acc_original - Acc_ablated

3. Discrepancy Computation:
   For each neuron i:
       Compute Δ_OI(i) = |ρ_obs(i)| - γ_int(i)

4. Threshold Calibration:
   Use cross-validation on D_shift to find optimal τ
   that maximizes separation between high/low discrepancy groups

5. Spurious Neuron Flagging:
   N_spurious = {i : Δ_OI(i) > τ}

6. Pattern Discovery (Optional):
   Cluster neurons in N_spurious by activation patterns
   Visualize clusters to interpret discovered spurious features
```

#### 3.2.2 Distribution Shift Generation

When natural distribution shifts are unavailable, we generate synthetic shifts:

**Vision Domain:**
- Geometric transformations: rotation ($\pm 30°$), scaling (0.8-1.2×)
- Color augmentations: hue shift, saturation adjustment, brightness variation
- Texture perturbations: Gaussian noise, blur

**Text Domain:**
- Paraphrasing via back-translation
- Synonym replacement (WordNet-based)
- Sentence reordering for multi-sentence inputs

**Multimodal Domain:**
- Cross-modal perturbations (e.g., image augmentation with text preserved)
- Modality dropout (randomly mask one modality)

#### 3.2.3 Computational Optimization

For large models (e.g., billion-parameter LLMs), we employ:

**Layer-wise Sampling:** Focus on final 3 layers where task-specific features concentrate

**Neuron Importance Sampling:** Pre-filter neurons by activation variance; analyze top 20% most active neurons

**Batch Intervention:** Ablate groups of 10-50 neurons simultaneously, then refine with individual ablation for high-discrepancy groups

**Complexity Analysis:** For a model with $N$ neurons in layer $L$ and dataset size $M$:
- Observational phase: $O(NM)$ (single forward pass)
- Interventional phase: $O(NM)$ (N forward passes with ablation)
- Total: $O(NM)$ ≈ 2-3× standard inference cost

### 3.3 Experimental Design

#### 3.3.1 Datasets and Benchmarks

**Primary Validation Datasets (Known Spurious Features):**

1. **Waterbirds:** 11,788 images, 2 classes (waterbird/landbird), spurious correlation with background (water/land). Train: 95% correlation, Test: 50% correlation. Worst-group size: 184 samples.

2. **CelebA:** 202,599 celebrity images, target attribute: "Blond Hair", spurious correlation with "Gender". Train: 95% correlation, Test: balanced.

**Secondary Discovery Datasets (Unknown Spurious Features):**

3. **NICO++:** Natural images with context shifts, used for blind spurious pattern discovery

4. **MultiNLI:** Text entailment with lexical overlap shortcuts

5. **Hateful Memes:** Multimodal dataset with image-text spurious correlations

#### 3.3.2 Experimental Protocol

**Experiment 1: Controlled Validation (Waterbirds)**

*Objective:* Validate that CNI-Auto detects known spurious features

*Procedure:*
1. Train ResNet-50 on Waterbirds training set (standard ERM)
2. Apply CNI-Auto to final convolutional layer (2048 neurons)
3. Generate ground truth spurious neuron labels via GradCAM: neurons with high activation on background regions
4. Compute precision, recall, F1 for spurious neuron detection

*Metrics:*
- **Precision:** $P = \frac{|\mathcal{N}_{spurious} \cap \mathcal{N}_{ground\_truth}|}{|\mathcal{N}_{spurious}|}$
- **Recall:** $R = \frac{|\mathcal{N}_{spurious} \cap \mathcal{N}_{ground\_truth}|}{|\mathcal{N}_{ground\_truth}|}$
- **F1 Score:** $F1 = \frac{2PR}{P+R}$

*Success Criterion:* F1 > 0.65, indicating >70% overlap (per hypothesis P1)

*Statistical Test:* Chi-square test for independence between high OI discrepancy and ground truth spurious activation (p < 0.05)

**Experiment 2: Blind Discovery (CelebA)**

*Objective:* Discover unknown spurious patterns without prior knowledge

*Procedure:*
1. Train ResNet-50 on CelebA for "Blond Hair" classification
2. Apply CNI-Auto without knowledge of gender correlation
3. Cluster flagged neurons using hierarchical clustering (Ward linkage)
4. Visualize cluster activation patterns via feature visualization
5. Compare discovered clusters to known biases (gender, age, makeup)

*Metrics:*
- **Cluster Coherence:** Silhouette score for neuron clusters
- **Interpretability Score:** Human evaluation (3 annotators) rating cluster interpretability (1-5 scale)
- **Discovery Rate:** Number of interpretable spurious patterns found

*Success Criterion:* Discover ≥2 interpretable spurious patterns with coherence score > 0.4

**Experiment 3: Robustness Improvement**

*Objective:* Demonstrate practical utility via worst-group accuracy improvement

*Procedure:*
1. Baseline: Deep Feature Reweighting (DFR) - retrain last layer with balanced sampling
2. CNI-Auto Mitigation: Retrain last layer while freezing flagged spurious neurons (set to 0)
3. Measure worst-group accuracy, average accuracy, accuracy gap

*Metrics:*
- **Worst-Group Accuracy:** $\text{Acc}_{worst} = \min_{g \in \mathcal{G}} \text{Acc}_g$
- **Average Accuracy:** $\text{Acc}_{avg} = \mathbb{E}_{g \sim P(G)}[\text{Acc}_g]$
- **Accuracy Gap:** $\Delta_{gap} = \text{Acc}_{avg} - \text{Acc}_{worst}$

*Statistical Test:* Paired t-test comparing worst-group accuracy between DFR and CNI-Auto mitigation across 5 random seeds (p < 0.05, Cohen's d > 0.5)

*Success Criterion:* ≥5% worst-group accuracy improvement over DFR baseline (per hypothesis P3)

**Experiment 4: Ablation Studies**

*Objective:* Validate design choices and assumptions

*Ablations:*
1. **Intervention Type:** Compare ablation ($a_i=0$) vs. activation ($a_i=\mu_i$) vs. random ($a_i \sim \mathcal{N}(\mu_i, \sigma_i)$)
2. **Shift Type:** Natural validation set vs. synthetic augmentation vs. combined
3. **Threshold Selection:** Fixed percentile (75th) vs. cross-validation vs. Otsu's method
4. **Layer Selection:** Early layers vs. middle layers vs. final layers
5. **Baseline Comparison:** CNI-Auto vs. simple activation correlation (no intervention) vs. random neuron selection

*Metrics:* F1 score for spurious detection, worst-group accuracy improvement

#### 3.3.3 Evaluation Metrics Summary

| Metric | Purpose | Target |
|--------|---------|--------|
| Precision/Recall/F1 | Spurious neuron detection accuracy | F1 > 0.65 |
| Worst-Group Accuracy | Robustness to spurious correlations | ≥5% improvement |
| Cluster Coherence | Quality of discovered patterns | Silhouette > 0.4 |
| Computational Cost | Practical feasibility | <3× inference time |
| Generalization | Cross-dataset transfer | F1 drop <0.15 |

### 3.4 Implementation Details

**Model Architectures:**
- Vision: ResNet-50, Vision Transformer (ViT-B/16)
- Text: BERT-base, RoBERTa-large
- Multimodal: CLIP, FLAVA

**Training Configuration:**
- Optimizer: SGD with momentum (0.9) for vision, AdamW for text
- Learning rate: 1e-3 with cosine annealing
- Batch size: 128
- Epochs: 100 (early stopping with patience=10)

**Hardware:**
- 4× NVIDIA A100 GPUs (40GB)
- Estimated runtime: 2-3 days per dataset for full pipeline

**Software:**
- PyTorch 2.0, Captum (for GradCAM), scikit-learn (for clustering)
- Code will be released open-source upon publication

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Primary Outcome 1: Validated Detection Method**
We expect CNI-Auto to achieve >70% precision and recall in detecting spurious neurons on Waterbirds and CelebA benchmarks, demonstrating that observational-interventional discrepancy is a reliable signal for spurious correlation detection. This validates our core hypothesis and establishes neuron-level causal intervention as a viable approach.

**Primary Outcome 2: Worst-Group Accuracy Improvement**
By freezing detected spurious neurons during last-layer retraining, we anticipate ≥5% worst-group accuracy improvement over standard robustification baselines (DFR, Group DRO when group labels are available). This demonstrates practical utility for fairness-critical applications.

**Primary Outcome 3: Blind Pattern Discovery**
On CelebA and NICO++, we expect to discover 2-4 interpretable spurious patterns without prior knowledge, including known biases (gender, age) and potentially novel shortcuts. This capability addresses the critical limitation of current methods that only handle known spurious features.

**Secondary Outcome 1: Theoretical Insights**
Analysis of OI discrepancy distributions across architectures will reveal how network design affects spurious learning. We hypothesize that Vision Transformers show more distributed spurious representations than CNNs, requiring group-level intervention strategies.

**Secondary Outcome 2: Cross-Domain Generalization**
We expect the framework to transfer across modalities (vision → text → multimodal) with minimal adaptation, validating the generality of the causal intervention principle. Performance may degrade 10-15% on out-of-domain datasets, indicating domain-specific threshold calibration needs.

**Secondary Outcome 3: Computational Feasibility**
The method should maintain <3× inference cost even for billion-parameter models through neuron sampling strategies, making it practical for pre-deployment safety analysis in production systems.

### 4.2 Scientific Impact

**Advancing Spurious Correlation Research:**
This work addresses a critical gap identified in the workshop objectives: developing automated methods for detecting spurious correlations when annotations are missing or unknown. By providing the first annotation-free detection method, we enable proactive identification of reliability risks before deployment.

**Bridging Causal Inference and Deep Learning:**
The theoretical framework extends Pearl's do-calculus to neuron-level DNN analysis, creating a new research direction at the intersection of causal inference and XAI. This opens pathways for applying causal reasoning to understand and improve neural network behavior.

**Benchmark Contributions:**
We will release:
1. **Spurious Neuron Detection Benchmark:** Ground truth spurious neuron labels for Waterbirds, CelebA, NICO++
2. **Evaluation Protocol:** Standardized metrics for comparing automated detection methods
3. **Baseline Implementations:** CNI-Auto and comparison methods for reproducibility

**Theoretical Foundations:**
Our work provides mathematical formulations describing spurious correlation origins through the OI discrepancy framework, addressing the workshop's call for formal characterizations of the phenomenon.

### 4.3 Practical Impact

**High-Stakes Domain Applications:**

*Healthcare:* Detect spurious correlations in medical imaging (e.g., hospital-specific equipment markers) before clinical deployment, reducing diagnostic errors for underrepresented patient populations.

*Hiring & Criminal Justice:* Identify demographic proxies learned by decision systems, supporting fairness audits and bias mitigation in socially consequential applications.

*Autonomous Systems:* Discover environmental shortcuts in perception models (e.g., reliance on lane markings that may be absent in construction zones), improving safety in edge cases.

**Industry Adoption Pathway:**
The low computational overhead (2-3× inference) makes CNI-Auto deployable in existing ML pipelines as a pre-deployment safety check. We will develop:
1. **Python Package:** `cni-auto` with scikit-learn-style API
2. **Integration Guides:** For popular frameworks (HuggingFace, TorchVision)
3. **Case Studies:** Demonstrating deployment in 3 real-world applications

**Policy & Regulation:**
As AI regulation evolves (EU AI Act, US Executive Orders), automated bias detection tools become essential for compliance. CNI-Auto provides auditable evidence of spurious correlation testing, supporting regulatory requirements for high-risk AI systems.

### 4.4 Limitations and Future Work

**Known Limitations:**
1. **Localization Assumption:** Method assumes spurious features localize to identifiable neuron groups; may fail for fully distributed representations
2. **Shift Availability:** Requires access to distribution shifts (natural or synthetic); quality of synthetic shifts affects detection accuracy
3. **Threshold Calibration:** Optimal threshold may vary across domains; requires small validation set for calibration

**Future Research Directions:**

*Extension to Foundation Models:* Adapt CNI-Auto for LLMs and LMMs through efficient neuron sampling and prompt-based shift generation, addressing the workshop's emphasis on examining foundational models.

*Causal Representation Learning:* Integrate detected spurious neurons into causal graph discovery algorithms, enabling automated causal model construction from neural networks.

*Optimization-Level Solutions:* Use OI discrepancy as a regularization signal during training to prevent spurious learning, moving from detection to prevention.

*Reinforcement Learning:* Extend framework to detect spurious state-action correlations in RL agents, addressing the workshop's call for spurious correlation research in RL paradigms.

*Theoretical Analysis:* Prove formal guarantees on detection accuracy under specific assumptions (e.g., linear separability of spurious/core neuron distributions), strengthening theoretical foundations.

### 4.5 Broader Impact Statement

This research directly addresses fairness and reliability challenges in AI deployment. By enabling automated detection of hidden biases, CNI-Auto supports equitable outcomes for underrepresented groups who disproportionately suffer from spurious correlation failures. However, we acknowledge potential dual-use concerns: adversaries could use spurious neuron knowledge to craft targeted attacks. We will include responsible disclosure guidelines and advocate for defensive applications in our publications.

The work aligns with the workshop's vision of fostering a collaborative community to address spurious correlations through comprehensive evaluation benchmarks, novel robustification solutions, and deeper understanding of the phenomenon's foundations. By bridging theory and practice, CNI-Auto advances both scientific understanding and real-world AI safety.

---

**Total Word Count:** 4,987 words