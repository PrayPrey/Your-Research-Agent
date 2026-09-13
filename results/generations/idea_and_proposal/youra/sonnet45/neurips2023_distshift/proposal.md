# Research Proposal: Layer-Wise Feature Diversity Preservation in Foundation Model Fine-Tuning

## 1. Title

**Mechanistic Analysis of Robustness Degradation in Foundation Model Fine-Tuning: A Layer-Wise Feature Diversity Perspective on Distribution Shift Resilience**

## 2. Introduction

### 2.1 Background

Foundation models—large-scale pretrained models such as BERT, GPT, Vision Transformers (ViT), and CLIP—have revolutionized machine learning by achieving unprecedented performance across diverse tasks through transfer learning. These models are typically pretrained on massive, diverse datasets and then adapted to downstream tasks via fine-tuning. However, a critical challenge emerges when these fine-tuned models encounter distribution shifts: data distributions different from both pretraining and fine-tuning distributions. Such shifts are ubiquitous in real-world deployments, occurring when models trained on one hospital's patient data are applied to another hospital, when wildlife conservation models encounter new geographic regions, or when educational systems serve demographically diverse populations.

Recent empirical studies have revealed a puzzling phenomenon: while full fine-tuning (updating all model parameters) achieves high in-distribution (ID) accuracy on downstream tasks, it often substantially degrades out-of-distribution (OOD) robustness compared to the pretrained model baseline. Conversely, parameter-efficient fine-tuning methods—such as adapters (Houlsby et al., 2019) and Low-Rank Adaptation (LoRA; Hu et al., 2021)—which freeze most pretrained parameters and introduce small trainable modules, empirically preserve OOD robustness better while achieving comparable ID accuracy (Chen et al., 2023). This observation has been documented across multiple benchmarks including WILDS (Koh et al., 2020), ImageNet-C (Hendrycks & Dietterich, 2019), and domain adaptation datasets.

Despite these empirical findings, the underlying mechanism explaining *why* parameter-efficient methods preserve robustness remains poorly understood. Existing work has primarily focused on engineering solutions—developing new adaptation methods that empirically improve robustness—without providing mechanistic explanations at the parameter level. This gap in understanding limits our ability to: (1) predict which fine-tuning strategies will maintain robustness for new tasks and architectures, (2) design principled adaptation methods based on theoretical insights rather than trial-and-error, and (3) identify which model components are critical for OOD generalization and should be protected during adaptation.

### 2.2 Research Objectives

This research aims to provide a mechanistic, parameter-level explanation for robustness degradation during foundation model fine-tuning through three primary objectives:

**Objective 1: Mechanistic Understanding**  
Establish a causal mechanistic framework explaining how fine-tuning methods differentially affect robustness-critical parameters in foundation models. Specifically, we hypothesize that full fine-tuning disproportionately updates early-layer parameters (layers 1-4 in typical 12-layer architectures) that encode high-diversity, task-agnostic features essential for OOD generalization, while parameter-efficient methods architecturally constrain updates to preserve these features.

**Objective 2: Quantitative Characterization**  
Develop and validate quantitative metrics to identify robustness-critical parameters before fine-tuning. We will introduce the Robustness-Critical Parameter Score (RCPS), combining intrinsic dimensionality analysis and Fisher Information computed on OOD data, to predict which parameters are most important for maintaining distribution shift resilience.

**Objective 3: Empirical Validation and Generalization**  
Validate the proposed mechanism across multiple architectures (CNNs and Transformers), modalities (vision and language), and distribution shift types through comprehensive experiments including correlational analysis and causal interventions (selective layer freezing).

### 2.3 Central Hypothesis

We hypothesize that **full fine-tuning degrades robustness to distribution shifts because it disproportionately updates parameters in early-to-middle layers (L1-L4 for 12-layer models) that encode high-diversity, task-agnostic features critical for out-of-distribution generalization**. These robustness-critical parameters undergo larger gradient updates during full fine-tuning ($\|\Delta w\|_2 > 0.5$ normalized) compared to parameter-efficient methods ($\|\Delta w\|_2 < 0.1$), leading to reduction in feature diversity (intrinsic dimensionality decrease $> 20\%$) and corresponding OOD accuracy drop ($> 10$ percentage points) while maintaining in-distribution accuracy.

The causal mechanism operates as follows: Pretrained foundation models learn hierarchical representations where early layers encode diverse, general-purpose features applicable across many tasks and distribution shifts, while later layers encode more task-specific features. During full fine-tuning on a narrow downstream task, gradient-based optimization updates all parameters to maximize ID performance, inadvertently specializing early-layer features to the specific downstream distribution. This specialization reduces feature diversity—quantifiable via intrinsic dimensionality (ID)—eliminating the representational flexibility needed to handle OOD samples. In contrast, parameter-efficient methods freeze early layers, preserving their diverse pretrained features while adding task-specific capacity through adapter modules or low-rank updates in later layers, thus maintaining the robustness-critical general features.

### 2.4 Significance

This research addresses a critical gap at the intersection of foundation models and distribution shift robustness, with significance spanning theoretical understanding, methodological innovation, and practical impact:

**Theoretical Significance:**  
This work advances our fundamental understanding of the adaptation-robustness trade-off in transfer learning. While prior work has established that early layers learn general features (Yosinski et al., 2014), we extend this to demonstrate that these layers are specifically *robustness-critical*—essential for OOD generalization. This mechanistic framework provides the first parameter-level explanation for empirically observed robustness patterns, moving beyond "adapters work better" to "adapters work better *because* they preserve high-diversity features in early layers."

**Methodological Significance:**  
The proposed RCPS metric and layer-wise OOD analysis methodology provide new tools for the research community to identify robustness-critical parameters proactively. Unlike existing methods that evaluate robustness post-hoc, RCPS enables prediction of which parameters require protection *before* fine-tuning begins. The causal intervention protocol establishes a rigorous framework for distinguishing correlation from causation in robustness analysis.

**Practical Significance:**  
For practitioners deploying foundation models in high-stakes domains (biomedicine, conservation, criminal justice), this research provides actionable guidance on which parameters to protect during fine-tuning. The RCPS-guided selective freezing approach offers a computationally efficient middle ground between full fine-tuning (high performance, low robustness) and adapters (high robustness, higher memory overhead). Understanding which layers are robustness-critical enables informed deployment decisions based on application-specific robustness requirements.

**Broader Impact:**  
By explaining *why* certain adaptation methods preserve robustness, this work provides a principled foundation for developing next-generation robust fine-tuning techniques. The mechanistic insights can inform architectural design choices, regularization strategies, and hyperparameter selection for robust adaptation. Furthermore, the framework is directly relevant to ongoing challenges in foundation model development, including instruction-following alignment (RLHF) and adaptation to specialized domains beyond web-scraped pretraining data.

## 3. Methodology

### 3.1 Research Design Overview

We employ a mixed-methods approach combining correlational analysis, causal interventions, and cross-validation across architectures and modalities. The research is structured in four phases:

- **Phase 0 (Assumption Validation):** Validate core methodological assumptions (2-3 weeks)
- **Phase 1 (Correlational Analysis):** Measure layer-wise parameter updates, feature diversity changes, and robustness across fine-tuning methods (4-6 weeks)
- **Phase 2 (Causal Interventions):** Conduct selective layer freezing experiments to establish causality (2-3 weeks)
- **Phase 3 (Cross-Architecture Validation):** Replicate findings across multiple architectures and modalities (integrated with Phase 1)

**Experimental Design:** Mixed between-within subjects design
- **Between-subjects factor:** Fine-tuning method (4 levels: Full fine-tuning, Adapter, LoRA, Frozen baseline)
- **Within-subjects factor:** Layer depth (12 levels: L1-L12)
- **Blocking factor:** Architecture (4 levels: ResNet-50, ViT-B/16, BERT-base, GPT-2-small)

### 3.2 Data Collection

#### 3.2.1 Models and Datasets

**Vision Domain:**
- **Architectures:** ResNet-50 (pretrained on ImageNet-1K), ViT-B/16 (pretrained on ImageNet-21K)
- **Downstream Tasks:** CIFAR-10 (60K images, 10 classes), Caltech-101 (9K images, 101 classes)
- **OOD Evaluation:** ImageNet-C (19 corruption types, 5 severity levels), CIFAR-10-C (same corruptions)
- **Distribution Shifts:** Corruption-based (Gaussian noise, motion blur, snow, fog), natural domain shift (ImageNet → CIFAR-10)

**Language Domain:**
- **Architectures:** BERT-base (pretrained on BooksCorpus + Wikipedia), GPT-2-small (pretrained on WebText)
- **Downstream Tasks:** MNLI (Multi-Genre NLI, 433K examples), QQP (Quora Question Pairs, 404K examples)
- **OOD Evaluation:** MNLI-matched → MNLI-mismatched (genre shift), HANS (heuristic-based adversarial examples)
- **Distribution Shifts:** Genre/domain shift, compositional generalization

**Rationale:** These datasets are standard benchmarks in distribution shift research (WILDS, RobustBench), enabling comparison with prior work while covering diverse shift types (corruption, domain, compositional).

#### 3.2.2 Fine-Tuning Configurations

**Full Fine-Tuning:**
- All parameters trainable
- Learning rate: Grid search over $\{1\mathrm{e}{-5}, 5\mathrm{e}{-5}, 1\mathrm{e}{-4}\}$ to match adapter ID accuracy
- Optimizer: AdamW with weight decay $0.01$
- Batch size: 32
- Training: Until validation accuracy plateau (early stopping, patience=5 epochs)

**Adapter (Houlsby et al., 2019):**
- Freeze all pretrained parameters
- Insert adapter modules (bottleneck dimension 64) after each Transformer block
- Adapter parameters: ~3.6% of total parameters
- Learning rate: $1\mathrm{e}{-4}$ (standard for adapters)
- Same optimizer and stopping criteria as full fine-tuning

**LoRA (Hu et al., 2021):**
- Freeze all pretrained parameters
- Add low-rank updates to attention weight matrices: $W' = W + BA$ where $B \in \mathbb{R}^{d \times r}$, $A \in \mathbb{R}^{r \times d}$, rank $r=8$
- LoRA parameters: ~0.8% of total parameters
- Learning rate: $3\mathrm{e}{-4}$ (standard for LoRA)
- Same optimizer and stopping criteria

**Frozen Baseline:**
- All parameters frozen, only final classification head trainable
- Provides baseline for pretrained model robustness

**Control Variables:**
- Ensure all methods achieve similar ID accuracy (within 2 percentage points) via hyperparameter tuning
- Use identical data augmentation (random crop, horizontal flip for vision; none for language)
- Fix random seeds for reproducibility (5 seeds per condition: 42, 123, 456, 789, 1024)

### 3.3 Algorithmic Steps and Metrics

#### 3.3.1 Intrinsic Dimensionality (ID) Estimation

Intrinsic dimensionality measures the number of effective dimensions in layer representations, quantifying feature diversity. We use the Maximum Likelihood Estimator (MLE) from Levina & Bickel (2004):

**Algorithm:**
1. For layer $l$, extract activations $\mathbf{h}_l^{(i)} \in \mathbb{R}^{d_l}$ for $N=1000$ OOD samples
2. For each sample $i$, find $k=10$ nearest neighbors in activation space (Euclidean distance)
3. Compute distances: $r_i(k) = \|\mathbf{h}_l^{(i)} - \mathbf{h}_l^{(i_k)}\|_2$ (distance to $k$-th neighbor)
4. Estimate local ID: 
$$\hat{m}_i = \left( \frac{1}{k-1} \sum_{j=1}^{k-1} \log \frac{r_i(k)}{r_i(j)} \right)^{-1}$$
5. Average over samples: $\text{ID}_l = \frac{1}{N} \sum_{i=1}^{N} \hat{m}_i$

**ID Change Metric:**
$$\Delta \text{ID}_l = \frac{\text{ID}_l^{\text{pretrained}} - \text{ID}_l^{\text{finetuned}}}{\text{ID}_l^{\text{pretrained}}} \times 100\%$$

**Interpretation:** Higher $\Delta \text{ID}_l$ indicates greater diversity reduction. We hypothesize $\Delta \text{ID}_l > 20\%$ for early layers in full fine-tuning vs. $< 5\%$ in adapters.

#### 3.3.2 Parameter Update Magnitude

Measure the L2 norm of parameter changes from pretrained to fine-tuned state:

$$\|\Delta w_l\|_2 = \frac{\|w_l^{\text{finetuned}} - w_l^{\text{pretrained}}\|_2}{\|w_l^{\text{pretrained}}\|_2}$$

where $w_l$ represents all parameters in layer $l$ (concatenated into a single vector).

**Hypothesis:** Full fine-tuning will show $\|\Delta w_l\|_2 > 0.5$ for early layers, while adapters show $\|\Delta w_l\|_2 < 0.1$ (parameters frozen).

#### 3.3.3 Fisher Information on OOD Data

Fisher Information quantifies parameter sensitivity to data distribution. We compute it on OOD data (novel application) to identify robustness-critical parameters:

**Algorithm:**
1. For layer $l$ with parameters $\theta_l$, compute gradient of log-likelihood on OOD samples:
$$\mathbf{g}_i = \nabla_{\theta_l} \log p(y_i | \mathbf{x}_i; \theta_l)$$
where $(\mathbf{x}_i, y_i)$ are OOD samples
2. Estimate Fisher Information Matrix diagonal (computational efficiency):
$$\mathcal{F}_l = \frac{1}{N_{\text{OOD}}} \sum_{i=1}^{N_{\text{OOD}}} \mathbf{g}_i \odot \mathbf{g}_i$$
where $\odot$ denotes element-wise product
3. Aggregate to layer-level score:
$$\text{Fisher}_{\text{OOD}, l} = \|\mathcal{F}_l\|_2$$

**Rationale:** High Fisher Information on OOD data indicates parameters whose changes significantly affect OOD predictions, identifying robustness-critical parameters.

#### 3.3.4 Robustness-Critical Parameter Score (RCPS)

Combine ID change and Fisher Information into a unified metric:

$$\text{RCPS}_l = \alpha \cdot \frac{\Delta \text{ID}_l}{\max_j \Delta \text{ID}_j} + \beta \cdot \frac{\text{Fisher}_{\text{OOD}, l}}{\max_j \text{Fisher}_{\text{OOD}, j}}$$

where $\alpha, \beta$ are weighting coefficients (normalized to $\alpha + \beta = 1$).

**Coefficient Determination (Phase 0):**
- Use ridge regression on validation set to learn optimal $\alpha, \beta$ predicting OOD accuracy drop
- Alternative: Equal weighting ($\alpha = \beta = 0.5$) as baseline
- Compare predictive performance via cross-validation

**Interpretation:** $\text{RCPS}_l \in [0, 1]$, with higher scores indicating layers more critical for robustness. We hypothesize early layers (L1-L4) will have $\text{RCPS}_l > 0.7$.

### 3.4 Experimental Validation

#### 3.4.1 Primary Experiment: Correlational Analysis (Phase 1)

**Objective:** Measure correlations between parameter updates, feature diversity changes, and robustness across fine-tuning methods.

**Procedure:**
1. For each architecture (ResNet-50, ViT-B, BERT-base, GPT-2-small):
   - Fine-tune using 4 methods (Full FT, Adapter, LoRA, Frozen) on 2 downstream tasks
   - Repeat for 5 random seeds
2. For each fine-tuned model:
   - Extract layer activations on OOD test set (1000 samples)
   - Compute $\text{ID}_l$ for all layers $l \in \{1, ..., 12\}$
   - Compute $\|\Delta w_l\|_2$ for all layers
   - Compute $\text{Fisher}_{\text{OOD}, l}$ for all layers
   - Calculate $\text{RCPS}_l$ for all layers
3. Evaluate performance:
   - ID accuracy on clean test set
   - OOD accuracy on distribution shift benchmarks (ImageNet-C severity 3-5, MNLI-mismatched)
4. Statistical analysis:
   - Pearson correlation: $\Delta \text{ID}_l$ vs. OOD accuracy drop
   - Two-sample t-tests: Full FT vs. Adapter on $\Delta \text{ID}_l$, OOD accuracy (Bonferroni correction, $\alpha = 0.0125$)
   - Layer-wise ANOVA: Compare $\text{RCPS}_l$ across methods

**Expected Outcomes:**
- Strong negative correlation ($r < -0.7$, $p < 0.01$) between early-layer ID reduction and OOD accuracy
- Significant difference in early-layer $\Delta \text{ID}_l$ between Full FT (mean $> 20\%$) and Adapter (mean $< 5\%$), Cohen's $d > 0.8$
- Early layers (L1-L4) show highest $\text{RCPS}_l$ scores across architectures

#### 3.4.2 Causal Intervention Experiment (Phase 2)

**Objective:** Establish causality by selectively freezing layers and measuring robustness preservation.

**Experimental Conditions:**
1. **Full Fine-Tuning (Baseline):** All layers trainable
2. **Early Frozen:** L1-L4 frozen, L5-L12 trainable
3. **Middle Frozen:** L5-L8 frozen, L1-L4 and L9-L12 trainable
4. **Late Frozen:** L9-L12 frozen, L1-L8 trainable
5. **Adapter (Comparison):** Standard adapter configuration
6. **All Frozen (Control):** Only classification head trainable

**Procedure:**
1. Fine-tune ResNet-50 and BERT-base (representative CNN and Transformer) under all 6 conditions
2. Ensure ID accuracy parity across conditions (within 2 percentage points) via hyperparameter tuning
3. Measure OOD accuracy on ImageNet-C (vision) and MNLI-mismatched (language)
4. Repeat for 5 random seeds

**Statistical Analysis:**
- One-way ANOVA comparing OOD accuracy across 6 conditions
- Post-hoc Tukey HSD tests for pairwise comparisons
- Effect size: Partial $\eta^2$

**Causal Prediction:**
If early-layer diversity is causally responsible for robustness, then:
- **Early Frozen** should preserve OOD robustness comparable to **Adapter** (difference $< 3$ pp, $p > 0.05$)
- **Early Frozen** should significantly outperform **Full Fine-Tuning** (difference $> 8$ pp, $p < 0.01$)
- **Middle Frozen** and **Late Frozen** should show intermediate or no robustness preservation

**Falsification:** If **Early Frozen** does not preserve robustness better than **Full Fine-Tuning**, the causal hypothesis is falsified (Criterion F3).

#### 3.4.3 Cross-Architecture Validation (Phase 3)

**Objective:** Test generalization of findings across architectures and modalities.

**Procedure:**
1. Replicate primary correlational analysis (Phase 1) for all 4 architectures
2. For each architecture, compute:
   - Correlation: $\Delta \text{ID}_{L1-L4}$ (average over early layers) vs. OOD accuracy drop
   - Layer-wise $\text{RCPS}_l$ distribution
3. Meta-analysis:
   - Fisher's Z-transform to compare correlation coefficients across architectures
   - Test hypothesis: All 4 architectures show $r > 0.7$ (strong correlation)

**Expected Outcome:**
- Pattern generalizes across CNNs (ResNet-50) and Transformers (ViT-B, BERT-base, GPT-2-small)
- Pattern generalizes across vision and language modalities
- If pattern fails for $\geq 3$ architectures, hypothesis is architecture-specific (Criterion F5)

### 3.5 Evaluation Metrics

**Primary Metrics:**

1. **OOD Accuracy:** Classification accuracy on distribution shift benchmarks
   - Vision: ImageNet-C (average over corruption types at severity 3-5), CIFAR-10-C
   - Language: MNLI-mismatched accuracy, HANS accuracy
   - **Target:** Adapter/LoRA maintain within 3 pp of pretrained baseline; Full FT drops $> 10$ pp

2. **ID Accuracy:** Classification accuracy on clean in-distribution test set
   - **Control:** All methods achieve within 2 pp of each other (fair comparison)

3. **Intrinsic Dimensionality Change ($\Delta \text{ID}_l$):** Percentage reduction in feature diversity per layer
   - **Target:** Full FT shows $> 20\%$ reduction in L1-L4; Adapter shows $< 5\%$

4. **Parameter Update Magnitude ($\|\Delta w_l\|_2$):** Normalized L2 norm of parameter changes
   - **Target:** Full FT shows $> 0.5$ in L1-L4; Adapter shows $< 0.1$ (frozen)

**Secondary Metrics:**

5. **RCPS (Robustness-Critical Parameter Score):** Composite metric identifying robustness-critical layers
   - **Target:** Early layers (L1-L4) have $\text{RCPS}_l > 0.7$; late layers $< 0.4$

6. **Gradient Magnitude Ratio:** Ratio of gradient norms between Full FT and Adapter during training
   - **Target:** Ratio $> 2.0$ in early layers, indicating disproportionate updates

7. **Correlation Coefficient ($r$):** Pearson correlation between $\Delta \text{ID}_l$ and OOD accuracy drop
   - **Target:** $|r| > 0.7$ (strong correlation), $p < 0.01$

**Statistical Rigor:**

- **Power Analysis:** Minimum 20 samples per group (5 seeds × 4 architectures) to detect large effects (Cohen's $d > 0.8$) with power $0.90$ at $\alpha = 0.05$
- **Multiple Comparison Correction:** Bonferroni correction for primary tests ($\alpha_{\text{adjusted}} = 0.0125$ for 4 comparisons)
- **Effect Sizes:** Report Cohen's $d$ for t-tests, Pearson's $r$ for correlations, partial $\eta^2$ for ANOVA
- **Confidence Intervals:** 95% CIs for all effect sizes
- **Reproducibility:** All experiments repeated with 5 random seeds; report mean $\pm$ standard error

### 3.6 Computational Resources

**Estimated Compute Requirements:**
- **Total Model Instances:** 80 (4 architectures × 4 methods × 5 seeds)
- **GPU-Hours per Instance:** ~8 hours (fine-tuning + evaluation)
- **Total GPU-Hours:** ~640 hours
- **Hardware:** 4-8 NVIDIA A100 or V100 GPUs
- **Timeline:** 6-8 weeks for complete experimental pipeline

**Software Stack:**
- PyTorch 2.0+ for model training
- Hugging Face Transformers for pretrained models
- scikit-learn for ID estimation (k-NN implementation)
- NumPy/SciPy for statistical analysis
- Weights & Biases for experiment tracking

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Primary Outcome 1: Mechanistic Validation**

We expect to validate the core hypothesis that full fine-tuning degrades robustness by disproportionately updating early-layer parameters encoding high-diversity features. Specifically:

- **Correlational Evidence:** Strong negative correlation ($r < -0.7$, $p < 0.01$) between early-layer intrinsic dimensionality reduction and OOD accuracy drop across all 4 architectures
- **Quantitative Differences:** Full fine-tuning will show $> 20\%$ ID reduction in layers L1-L4 with corresponding $> 10$ percentage point OOD accuracy drop, while adapters/LoRA show $< 5\%$ ID reduction and maintain OOD accuracy within 3 pp of pretrained baseline
- **Parameter Update Patterns:** Early layers in full fine-tuning will exhibit $\|\Delta w\|_2 > 0.5$ (normalized), 5-10× larger than adapter updates ($< 0.1$, frozen parameters)

**Primary Outcome 2: Causal Evidence**

The selective layer freezing intervention will establish causality:

- **Robustness Preservation:** Freezing early layers (L1-L4) during fine-tuning will preserve OOD robustness comparable to adapters (difference $< 3$ pp, $p > 0.05$), significantly outperforming full fine-tuning (difference $> 8$ pp, $p < 0.01$)
- **Specificity:** Freezing middle or late layers will not preserve robustness, demonstrating that early layers are specifically robustness-critical
- **ID Accuracy Parity:** All intervention conditions will achieve similar ID accuracy (within 2 pp), confirming that robustness preservation does not sacrifice task performance

**Primary Outcome 3: Methodological Contribution**

The RCPS metric will successfully identify robustness-critical parameters:

- **Predictive Validity:** RCPS computed on pretrained models will predict OOD accuracy drop after fine-tuning with Spearman correlation $\rho > 0.6$
- **Layer Ranking:** Early layers (L1-L4) will consistently rank highest in RCPS ($> 0.7$) across architectures, providing actionable guidance for selective freezing
- **Generalization:** RCPS pattern will generalize across CNNs (ResNet-50), Vision Transformers (ViT-B), and language models (BERT-base, GPT-2-small), demonstrating architecture-agnostic applicability

**Secondary Outcomes:**

- **Cross-Architecture Generalization:** The ID reduction → robustness degradation pattern will hold across all 4 tested architectures (ResNet-50, ViT-B, BERT-base, GPT-2-small) with consistent correlation coefficients ($r > 0.7$)
- **Cross-Modality Generalization:** Pattern will generalize across vision (ImageNet-C, CIFAR-10-C) and language (MNLI-mismatched, HANS) distribution shifts
- **Gradient Dynamics:** Training-time analysis will reveal 2-5× higher gradient magnitudes in early layers during full fine-tuning compared to adapters, explaining the mechanism of disproportionate updates

**Potential Negative Results:**

If the hypothesis is falsified (per Criteria F1-F6), we will report:
- Which specific predictions failed and under what conditions
- Alternative explanations for observed robustness patterns
- Boundary conditions where the mechanism does not apply
- Revised hypotheses for future investigation

### 4.2 Theoretical Impact

**Advancing Foundation Model Understanding:**

This research will provide the first mechanistic, parameter-level explanation for a widely observed but poorly understood phenomenon in foundation model adaptation. The theoretical contributions include:

1. **Parameter-Level Decomposition Framework:** Distinguishing robustness-critical parameters (early layers, high diversity) from task-critical parameters (late layers, task-specific features) provides a new lens for understanding transfer learning beyond the traditional "general vs. specific features" dichotomy

2. **Adaptation-Robustness Trade-off Formalization:** Quantifying the tension between task-specific adaptation (requiring parameter updates) and general feature preservation (requiring parameter freezing) enables principled navigation of this trade-off based on application requirements

3. **Mechanistic Bridge:** Connecting high-level empirical observations (adapters preserve robustness) to low-level mechanisms (feature diversity preservation in early layers) bridges the gap between engineering practice and scientific understanding

**Implications for Transfer Learning Theory:**

- Extends Yosinski et al.'s (2014) finding that early layers learn general features to demonstrate these layers are specifically *robustness-critical* for OOD generalization
- Provides quantitative metrics (ID, RCPS) to operationalize "generality" and "robustness-criticality"
- Suggests that pretrained feature diversity, not just feature transferability, is essential for robust adaptation

**Implications for Distribution Shift Research:**

- Identifies a specific failure mode (early-layer specialization) underlying robustness degradation, complementing existing work on domain adaptation and OOD detection
- Demonstrates that robustness is not solely a function of training data diversity or model capacity, but also of which parameters are updated during adaptation
- Provides mechanistic foundation for understanding why certain distribution shifts (requiring diverse general features) are more affected by fine-tuning than others

### 4.3 Methodological Impact

**New Tools for Robustness Analysis:**

1. **RCPS Metric Adoption:** The Robustness-Critical Parameter Score provides a proactive tool for identifying which parameters to protect before fine-tuning begins. We expect this metric to be adopted in:
   - Robustness benchmarking studies (complementing accuracy metrics)
   - Model selection pipelines (choosing pretrained checkpoints with high early-layer ID)
   - Hyperparameter tuning (optimizing layer-specific learning rates based on RCPS)

2. **Layer-wise OOD Analysis Protocol:** The methodology of computing intrinsic dimensionality on OOD data (not just ID data) provides a template for future mechanistic interpretability research on robustness, applicable beyond fine-tuning to other adaptation scenarios (continual learning, domain adaptation, test-time adaptation)

3. **Causal Intervention Framework:** The selective layer freezing protocol establishes a rigorous approach for distinguishing correlation from causation in robustness research, addressing a common limitation in empirical ML studies

**Reproducibility and Open Science:**

- All code, data, and experimental protocols will be open-sourced, enabling replication and extension
- RCPS computation toolkit will be released as a Python package for easy integration into existing workflows
- Detailed hyperparameter logs and model checkpoints will be shared for transparency

### 4.4 Practical Impact

**Guidance for Practitioners:**

1. **Selective Freezing Strategies:** Practitioners can use RCPS to identify which layers to freeze during fine-tuning, achieving a middle ground between full fine-tuning (high ID accuracy, low robustness) and adapters (high robustness, higher memory overhead). Expected practical benefit: 5-10% OOD accuracy improvement over naive full fine-tuning with minimal computational overhead

2. **Model Selection:** Before fine-tuning, practitioners can evaluate pretrained models' early-layer intrinsic dimensionality to predict post-fine-tuning robustness. Models with higher baseline ID in early layers will maintain better robustness after adaptation

3. **Application-Specific Trade-offs:** Understanding the mechanism enables informed decisions:
   - **High-stakes domains (medicine, criminal justice):** Prioritize robustness by freezing early layers or using adapters
   - **Low-stakes domains (entertainment, recommendation):** Optimize ID accuracy via full fine-tuning, accepting robustness trade-off
   - **Resource-constrained deployment (edge devices):** Use RCPS-guided selective freezing to reduce trainable parameters while preserving robustness

**Impact on Foundation Model Development:**

1. **Pretraining Objectives:** Insights suggest that pretraining should explicitly optimize for early-layer feature diversity (e.g., via diversity-promoting regularization) to improve downstream robustness

2. **Architecture Design:** Future architectures could incorporate robustness-aware design principles, such as separating robustness-critical and task-critical parameters into distinct modules

3. **Adaptation Method Design:** The mechanistic framework provides principled guidance for developing next-generation robust fine-tuning methods:
   - Layer-aware learning rates (lower rates for high-RCPS layers)
   - RCPS-weighted regularization (stronger regularization on robustness-critical parameters)
   - Dynamic layer freezing (adaptively freeze layers based on validation robustness)

**Estimated Practical Impact:**

- **Short-term (1-2 years):** Adoption of RCPS-guided selective freezing in robustness-critical applications, reducing OOD accuracy gaps by 5-10 percentage points compared to naive full fine-tuning
- **Medium-term (3-5 years):** Integration of robustness-aware adaptation methods into standard ML frameworks (Hugging Face, PyTorch Lightning), making robust fine-tuning accessible to non-experts
- **Long-term (5+ years):** Influence on foundation model pretraining practices, with explicit optimization for robustness-critical feature diversity becoming standard

### 4.5 Broader Impact on Workshop Themes

This research directly addresses multiple open questions posed in the workshop call:

**Adaptation Question:** *"What causes fine-tuning to reduce distributional robustness gains from foundation models, and how can we adapt models without sacrificing robustness?"*
- **Our Answer:** Fine-tuning reduces robustness by updating early-layer parameters encoding diverse, general features. Adaptation can preserve robustness by freezing high-RCPS layers or using parameter-efficient methods that architecturally constrain updates.

**Empirical Trends Question:** *"What aspects of foundation models are driving robustness?"*
- **Our Answer:** Early-layer feature diversity (intrinsic dimensionality) is a key driver. Models with higher pretrained ID in early layers maintain better robustness after adaptation.

**Pretraining Question:** *"How does pretraining distribution shift affect downstream performance?"*
- **Our Answer:** Pretraining on diverse data creates high-diversity early-layer features. Fine-tuning on narrow downstream distributions reduces this diversity, degrading robustness. The mechanism explains why pretraining-downstream distribution mismatch matters.

**Broader Implications:**

- **Fairness:** Understanding robustness mechanisms is critical for ensuring models perform equitably across demographic subgroups (a form of distribution shift)
- **Sustainability:** RCPS-guided selective freezing reduces computational costs (fewer trainable parameters) while maintaining robustness, supporting sustainable ML practices
- **Democratization:** Open-source RCPS toolkit lowers barriers for practitioners in resource-constrained settings to deploy robust models

### 4.6 Limitations and Future Directions

**Known Limitations:**

1. **Mechanistic Reductionism:** This work focuses on one mechanism (feature diversity in early layers). Robustness is likely multi-causal; other mechanisms (batch normalization statistics, attention patterns) may also contribute.

2. **Shift Type Coverage:** Experiments focus on corruption-based and domain shifts. Adversarial robustness and subpopulation shifts may involve different mechanisms.

3. **Architecture Scope:** Testing 4 architectures provides breadth, but emerging architectures (e.g., state-space models, mixture-of-experts) may exhibit different patterns.

**Future Research Directions:**

1. **Complementary Mechanisms:** Investigate other contributors to robustness degradation (late-layer contributions, normalization layer effects, attention diversity)

2. **Dynamic Analysis:** Track robustness and feature diversity throughout training (not just pre/post), identifying critical training phases where degradation occurs

3. **Intervention Methods:** Develop and benchmark RCPS-guided fine-tuning methods (layer-aware learning rates, diversity-preserving regularization)

4. **Scaling Laws:** Investigate how the mechanism scales with model size (does the pattern hold for 1B+ parameter models?)

5. **Real-World Deployment:** Validate findings in high-stakes applications (medical imaging, wildlife conservation) with real-world distribution shifts

**Conclusion:**

This research provides a mechanistic foundation for understanding and addressing robustness degradation in foundation model fine-tuning—a critical challenge for real-world deployment. By identifying robustness-critical parameters and explaining why parameter-efficient methods preserve robustness, we enable principled development of robust adaptation techniques and informed deployment decisions in high-stakes domains. The combination of theoretical insights, methodological innovations, and practical guidance positions this work to significantly impact both the scientific understanding and engineering practice of foundation model adaptation under distribution shifts.