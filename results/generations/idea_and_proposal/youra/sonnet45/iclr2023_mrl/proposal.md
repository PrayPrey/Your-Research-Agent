# GeometricWatch: Automated Multi-Scale Monitoring and Intervention for Geometric Pathologies in Multimodal Contrastive Learning

## 1. Introduction

### 1.1 Background

Multimodal representation learning has emerged as a cornerstone of modern machine learning, with vision-language models like CLIP (Contrastive Language-Image Pre-training) demonstrating remarkable zero-shot transfer capabilities across diverse downstream tasks. These models learn joint embedding spaces by training dual encoders with contrastive objectives on large-scale image-text pairs, achieving state-of-the-art performance on tasks ranging from zero-shot classification to cross-modal retrieval. The success of CLIP has spawned widespread adoption, with implementations like OpenAI's CLIP (32,400 GitHub stars) and Open_CLIP (13,300 stars) becoming foundational tools for the research community.

However, the training dynamics of CLIP-style models remain poorly understood, particularly regarding the geometric properties of learned representations. Recent work by Xia et al. (2026) has identified critical **geometric pathologies** that emerge during multimodal contrastive learning: (1) **representation collapse**, where embeddings cluster too tightly within a modality, reducing representational capacity, and (2) **cross-modal misalignment**, where vision and text representations drift apart semantically despite contrastive alignment objectives. These pathologies degrade downstream task performance, yet current training practices lack systematic tools to detect or mitigate them.

The gap between geometric quality and practical training is substantial. While Xia et al. propose dispersive and anchoring regularizers to address these pathologies, their approach requires manual hyperparameter tuning and provides no mechanism for real-time monitoring or adaptive intervention. Practitioners training CLIP models currently rely on opaque loss curves and post-hoc evaluation, discovering geometric failures only after wasting significant computational resources. Furthermore, theoretical work by Zhao (2024) on algebraic-geometric perspectives of multimodal alignment remains disconnected from practical training systems, and neuroscience-inspired metrics like Representational Similarity Analysis (RSA) (Kriegeskorte et al., 2008; Tang et al., 2023) have not been adapted for training-time diagnostics.

This research addresses **Gap 2** identified in the workshop's call for submissions: "Inadequate Understanding of Representation Geometry's Role in Multimodal Learning Quality." Specifically, we lack (1) **metrics** for quantifying geometric quality during training, (2) **diagnostic tools** for real-time monitoring, (3) **design principles** for automated interventions, and (4) **empirical validation** connecting geometric properties to downstream performance.

### 1.2 Research Objectives

This research proposes **GeometricWatch**, a lightweight framework for automated multi-scale monitoring and intervention targeting geometric pathologies in CLIP-style multimodal contrastive learning. Our primary objectives are:

**Objective 1: Develop Multi-Scale Geometric Monitoring System**
- Design **micro-level** metrics (intra-modal dispersion) to detect representation collapse
- Design **macro-level** metrics (cross-modal RSA alignment) to track semantic consistency
- Implement efficient computation with <5% training overhead through subsampling and periodic evaluation

**Objective 2: Create Automated Intervention Mechanism**
- Establish bootstrap-calibrated thresholds for anomaly detection without manual tuning
- Implement graduated intervention policy (gradual ramp-up, cooldown periods) to prevent optimization instability
- Trigger dispersive regularization adaptively when pathologies are detected

**Objective 3: Validate Geometric Health-Performance Connection**
- Empirically test whether geometric pathologies are detectable and prevalent (≥10% of training steps)
- Measure intervention effectiveness (≥30% reduction in collapse events, ≥20% dispersion increase within 500 steps)
- Establish correlation between geometric metrics and downstream task performance (Pearson r > 0.3)

**Objective 4: Deliver Practical Diagnostic Tool**
- Integrate with Open_CLIP via PyTorch callbacks for seamless adoption
- Provide TensorBoard logging for interpretable training insights
- Release open-source implementation with documentation for practitioner use

### 1.3 Research Significance

This research makes three categories of contributions:

**Theoretical Significance:**
- **Multi-Scale Geometric Quality Framework**: First systematic framework connecting geometric properties at multiple scales (micro: intra-modal variance, macro: cross-modal alignment) to multimodal representation quality, providing theoretical justification for why monitoring both dispersion and RSA captures complementary pathology types.
- **Bridging Neuroscience and Multimodal ML**: Adapts RSA from neuroscience to practical multimodal training monitoring, demonstrating cross-domain transfer of metrics for measuring shared semantic structure.
- **Automated Intervention Theory**: Establishes principles for mid-training geometric interventions with stability guarantees, drawing parallels to control theory and adaptive optimization.

**Methodological Significance:**
- **Production-Ready Monitoring System**: Delivers practical PyTorch implementation with <5% overhead, making geometric quality tracking accessible without specialized expertise.
- **Two-Stage Threshold Calibration**: Novel methodology combining bootstrap initialization and adaptive sliding window adjustment, addressing the challenge of setting anomaly detection thresholds.
- **Validation Protocol**: Establishes experimental methodology for evaluating geometric health interventions, including pre/post-intervention analysis, correlation studies, and falsification criteria.

**Practical Significance:**
- **Diagnostic Tool for CLIP Practitioners**: Addresses real need in community deploying CLIP-style models who currently lack geometry diagnostics.
- **Reduced Manual Tuning**: Automated threshold calibration and adaptive intervention reduce trial-and-error in regularization strength selection.
- **Interpretable Training Insights**: TensorBoard logging provides interpretable signals (dispersion collapse, alignment drift) versus opaque loss curves.

The framework directly addresses the workshop's core questions on **representation properties** (What semantic information is encoded? How does geometry affect quality?), **training dynamics** (How do learning objectives influence representations? How do we promote robustness?), and **modality interactions** (How do different modalities contribute to semantics?). By providing both diagnostic capabilities and automated interventions, GeometricWatch enables data-driven understanding of which geometric properties matter for specific downstream tasks, reduces wasted compute from training models with geometric pathologies, and provides a foundation for future work on geometric quality in other multimodal architectures.

## 2. Methodology

### 2.1 Problem Formulation

Consider a CLIP-style dual-encoder model with vision encoder $f_v: \mathcal{X}_v \rightarrow \mathbb{R}^d$ and text encoder $f_t: \mathcal{X}_t \rightarrow \mathbb{R}^d$ trained on paired data $\mathcal{D} = \{(x_v^{(i)}, x_t^{(i)})\}_{i=1}^N$. The standard contrastive learning objective is:

$$\mathcal{L}_{\text{contrastive}} = -\frac{1}{B}\sum_{i=1}^B \left[\log\frac{\exp(\text{sim}(e_v^{(i)}, e_t^{(i)})/\tau)}{\sum_{j=1}^B \exp(\text{sim}(e_v^{(i)}, e_t^{(j)})/\tau)}\right]$$

where $e_v^{(i)} = f_v(x_v^{(i)})$, $e_t^{(i)} = f_t(x_t^{(i)})$, $\text{sim}(\cdot, \cdot)$ is cosine similarity, $\tau$ is temperature, and $B$ is batch size.

**Geometric Pathologies:**

1. **Representation Collapse (Micro-level)**: Embeddings within a modality cluster too tightly, reducing representational capacity. Formally, intra-modal variance $\sigma^2(E_m) = \frac{1}{B}\sum_{i=1}^B \|e_m^{(i)} - \bar{e}_m\|^2$ becomes anomalously low, where $m \in \{v, t\}$ and $\bar{e}_m = \frac{1}{B}\sum_{i=1}^B e_m^{(i)}$.

2. **Cross-Modal Misalignment (Macro-level)**: Vision and text representations drift apart semantically. Measured via Representational Similarity Analysis (RSA):

$$\text{RSA}(E_v, E_t) = \text{corr}(\text{vec}(D_v), \text{vec}(D_t))$$

where $D_v, D_t$ are pairwise distance matrices and $\text{corr}$ is Pearson correlation.

**Research Hypothesis:**

Implementing GeometricWatch (multi-scale monitoring + automated intervention) will:
- Reduce collapse events by ≥30% (measured as steps where $\sigma^2(E_m) < \mu_{\text{bootstrap}} - 2\sigma_{\text{bootstrap}}$)
- Improve downstream accuracy by ≥1% on ImageNet zero-shot classification OR maintain performance (≤0.5% drop) across all evaluation tasks
- Maintain <5% computational overhead (wall-clock time increase)

### 2.2 GeometricWatch Framework Architecture

The framework consists of four components: (1) Multi-Scale Metric Computation, (2) Two-Stage Threshold Calibration, (3) Automated Intervention System, and (4) Logging and Visualization.

#### 2.2.1 Multi-Scale Metric Computation

**Micro-Level: Dispersion Metric**

Computed every 100 training steps on batch embeddings:

$$\sigma^2_v(t) = \frac{1}{B}\sum_{i=1}^B \|e_v^{(i)}(t) - \bar{e}_v(t)\|^2, \quad \sigma^2_t(t) = \frac{1}{B}\sum_{i=1}^B \|e_t^{(i)}(t) - \bar{e}_t(t)\|^2$$

**Computational Complexity:** $O(B \cdot d)$ per modality, where $d$ is embedding dimension (512-768).

**Macro-Level: RSA Alignment Score**

To reduce computational cost, we subsample $n_{\text{sample}} = 200$ pairs from the batch:

1. Compute pairwise distance matrices:
   $$D_v[i,j] = \|e_v^{(i)} - e_v^{(j)}\|_2, \quad D_t[i,j] = \|e_t^{(i)} - e_t^{(j)}\|_2$$
   for $i,j \in \{1, \ldots, n_{\text{sample}}\}$

2. Vectorize upper triangular portions: $\mathbf{d}_v = \text{vec}(D_v), \mathbf{d}_t = \text{vec}(D_t)$

3. Compute Pearson correlation:
   $$\text{RSA}(t) = \frac{\text{cov}(\mathbf{d}_v, \mathbf{d}_t)}{\sqrt{\text{var}(\mathbf{d}_v) \cdot \text{var}(\mathbf{d}_t)}}$$

**Computational Complexity:** $O(n_{\text{sample}}^2)$ = $O(40,000)$ operations, negligible compared to forward/backward pass.

#### 2.2.2 Two-Stage Threshold Calibration

**Stage 1: Bootstrap Calibration (First Epoch)**

Run standard CLIP training for 1 epoch on CC3M subset (or 5,000 steps), collecting metric distributions:

$$\{\sigma^2_v(t_1), \ldots, \sigma^2_v(t_K)\}, \quad \{\sigma^2_t(t_1), \ldots, \sigma^2_t(t_K)\}, \quad \{\text{RSA}(t_1), \ldots, \text{RSA}(t_K)\}$$

Compute bootstrap statistics:
$$\mu_{\sigma^2_v} = \frac{1}{K}\sum_{k=1}^K \sigma^2_v(t_k), \quad s_{\sigma^2_v} = \sqrt{\frac{1}{K-1}\sum_{k=1}^K (\sigma^2_v(t_k) - \mu_{\sigma^2_v})^2}$$

Set initial thresholds (2-sigma rule from statistical process control):
$$\theta_{\text{collapse}}^v = \mu_{\sigma^2_v} - 2s_{\sigma^2_v}, \quad \theta_{\text{collapse}}^t = \mu_{\sigma^2_t} - 2s_{\sigma^2_t}$$
$$\theta_{\text{align}} = \mu_{\text{RSA}} - 2s_{\text{RSA}}$$

**Stage 2: Adaptive Sliding Window (Full Training)**

Maintain sliding window of last 1,000 steps, update thresholds every 500 steps:
$$\theta_{\text{collapse}}^v(t) = \mu_{\text{window}}(t) - 2s_{\text{window}}(t)$$

This allows thresholds to adapt to changing metric distributions as training progresses.

#### 2.2.3 Automated Intervention System

**Anomaly Detection:**

At step $t$, trigger intervention if:
$$\sigma^2_v(t) < \theta_{\text{collapse}}^v(t) \quad \text{OR} \quad \sigma^2_t(t) < \theta_{\text{collapse}}^t(t)$$

**Dispersive Regularizer:**

Following Xia et al. (2026), apply:
$$\mathcal{L}_{\text{disp}} = -\log\left(\frac{\sigma^2_v(t)}{\sigma^2_{\text{target}}}\right) - \log\left(\frac{\sigma^2_t(t)}{\sigma^2_{\text{target}}}\right)$$

where $\sigma^2_{\text{target}}$ is set to bootstrap mean $\mu_{\sigma^2}$.

**Total Loss:**
$$\mathcal{L}_{\text{total}}(t) = \mathcal{L}_{\text{contrastive}}(t) + \lambda(t) \cdot \mathcal{L}_{\text{disp}}(t)$$

**Graduated Application Policy:**

To prevent optimization instability, we implement:

1. **Warm-up Period**: No interventions for first 1,000 steps (allow initial convergence)

2. **Gradual Ramp-up**: When intervention triggered at step $t_0$, increase $\lambda$ linearly:
   $$\lambda(t) = \lambda_{\max} \cdot \min\left(1, \frac{t - t_0}{100}\right), \quad t \in [t_0, t_0 + 100]$$
   where $\lambda_{\max} = 0.1$ (small to preserve contrastive alignment)

3. **Cooldown Period**: After intervention ends at $t_0 + 100$, wait 1,000 steps before next intervention (stability safeguard)

4. **Maximum Strength Bound**: $\lambda \leq 0.1$ ensures contrastive loss dominates

**Intervention Termination:**

Stop applying regularizer when $\sigma^2(t) > \theta_{\text{collapse}}(t)$ (geometric health restored) or after 500 steps maximum.

#### 2.2.4 Logging and Visualization

**TensorBoard Integration:**

Log every 100 steps:
- Scalar metrics: $\sigma^2_v(t)$, $\sigma^2_t(t)$, $\text{RSA}(t)$, $\lambda(t)$
- Thresholds: $\theta_{\text{collapse}}^v(t)$, $\theta_{\text{collapse}}^t(t)$, $\theta_{\text{align}}(t)$
- Intervention events: Binary indicator (0/1)
- Training loss: $\mathcal{L}_{\text{contrastive}}(t)$, $\mathcal{L}_{\text{disp}}(t)$, $\mathcal{L}_{\text{total}}(t)$

**Qualitative Validation:**

Generate t-SNE plots at checkpoints (every 5,000 steps):
- Visualize embedding distributions for vision and text modalities
- Compare collapse periods (low $\sigma^2$) vs. healthy periods (normal $\sigma^2$)

### 2.3 Experimental Design

#### 2.3.1 Data Collection

**Training Data:**
- **Primary Dataset**: Conceptual Captions 3M (CC3M) - 3.3M image-text pairs
- **Preprocessing**: Resize images to 224×224, tokenize text with BERT tokenizer (max length 77)
- **Data Splits**: Use full CC3M for training; no validation split needed (zero-shot evaluation)

**Evaluation Data:**
- **Zero-shot Classification**: ImageNet-1K validation set (50,000 images, 1,000 classes)
- **Image-Text Retrieval**: COCO Captions validation (5,000 images, 25,000 captions) and Flickr30K test (1,000 images, 5,000 captions)

#### 2.3.2 Model Architecture and Training Configuration

**Architecture:**
- **Vision Encoder**: ViT-B/32 (Vision Transformer with 12 layers, 768 hidden dim, 32×32 patch size)
- **Text Encoder**: BERT-base (12 layers, 768 hidden dim)
- **Projection Heads**: Linear layers mapping to 512-dimensional joint embedding space
- **Total Parameters**: ~150M

**Training Hyperparameters:**
- **Optimizer**: AdamW with $\beta_1=0.9$, $\beta_2=0.98$, weight decay $10^{-4}$
- **Learning Rate**: Cosine schedule with warm-up (500 steps to peak $5 \times 10^{-4}$, decay to $10^{-6}$)
- **Batch Size**: 512 (distributed across 4 GPUs)
- **Training Steps**: 50,000 (approximately 8 epochs on CC3M)
- **Temperature**: $\tau = 0.07$ (standard CLIP value)
- **Mixed Precision**: FP16 with gradient scaling

**Implementation:**
- **Framework**: PyTorch 2.0 with Open_CLIP codebase
- **Hardware**: 4× NVIDIA A100 GPUs (40GB VRAM each)
- **Distributed Training**: PyTorch DistributedDataParallel (DDP)

#### 2.3.3 Experimental Groups

**Between-Subjects Design with 5 Groups:**

1. **Control Group (Baseline)**: Standard CLIP training without GeometricWatch
2. **Experimental Group 1 (Bootstrap)**: GeometricWatch with bootstrap threshold calibration (Stage 1 only)
3. **Experimental Group 2 (Adaptive)**: GeometricWatch with adaptive threshold calibration (Stage 1 + Stage 2)
4. **Ablation Group 1 (Monitor-Only)**: Monitoring without intervention (to isolate detection value)
5. **Ablation Group 2 (Fixed-Reg)**: Fixed dispersive regularizer ($\lambda = 0.05$ constant) without adaptive triggering

**Sample Size:**
- **Runs per group**: $n = 5$ (different random seeds: 42, 123, 456, 789, 1024)
- **Total runs**: 5 groups × 5 seeds = 25 training runs
- **Justification**: $n=5$ sufficient for t-tests with medium effect size (Cohen's $d \approx 0.8$), power=0.8

**Randomization:**
- Random seeds control weight initialization and data shuffling
- Counterbalance training order (randomize which group runs first) to control for hardware variations

#### 2.3.4 Evaluation Metrics

**Primary Metrics (Downstream Task Performance):**

1. **Zero-shot Classification Accuracy** (ImageNet):
   $$\text{Acc}_{\text{top-1}} = \frac{1}{N_{\text{test}}}\sum_{i=1}^{N_{\text{test}}} \mathbb{1}[\arg\max_c \text{sim}(e_v^{(i)}, e_t^{(c)}) = y_i]$$
   where $e_t^{(c)}$ is text embedding for class $c$ prompt ("a photo of a [class]")

2. **Image-to-Text Retrieval** (COCO, Flickr30K):
   - Recall@1, Recall@5, Recall@10: Fraction of queries where correct match is in top-k retrieved items
   - Computed via cosine similarity ranking

3. **Text-to-Image Retrieval** (COCO, Flickr30K):
   - Same Recall@k metrics with reversed query direction

**Secondary Metrics (Geometric Health):**

4. **Dispersion Metrics**:
   - Average dispersion: $\bar{\sigma}^2_v = \frac{1}{T}\sum_{t=1}^T \sigma^2_v(t)$
   - Collapse event count: $C = \sum_{t=1}^T \mathbb{1}[\sigma^2_v(t) < \theta_{\text{collapse}}^v(t)]$

5. **RSA Alignment**:
   - Average RSA: $\overline{\text{RSA}} = \frac{1}{T}\sum_{t=1}^T \text{RSA}(t)$
   - Alignment degradation events: $A = \sum_{t=1}^T \mathbb{1}[\text{RSA}(t) < \theta_{\text{align}}(t)]$

6. **Intervention Statistics**:
   - Total intervention count: $I_{\text{total}}$
   - Intervention frequency by training phase (early: 0-10K, mid: 10-30K, late: 30K-50K)
   - Post-intervention recovery: $\Delta\sigma^2 = \sigma^2(t_0 + 500) - \sigma^2(t_0)$ where $t_0$ is intervention trigger time

**Efficiency Metrics:**

7. **Computational Overhead**:
   $$\text{Overhead} = \frac{t_{\text{experimental}} - t_{\text{baseline}}}{t_{\text{baseline}}} \times 100\%$$
   where $t$ is wall-clock training time

8. **Memory Usage**: Peak GPU memory consumption (MB)

#### 2.3.5 Statistical Analysis Plan

**Primary Hypothesis Test (Task Performance):**

**Test**: One-sided independent samples t-test
- **Null Hypothesis**: $\mu_{\text{experimental}} \leq \mu_{\text{control}}$ (no improvement)
- **Alternative**: $\mu_{\text{experimental}} > \mu_{\text{control}}$ (improvement)
- **Significance Level**: $\alpha = 0.05$
- **Effect Size**: Cohen's $d \geq 0.5$ (medium effect)

**Normality Check**: Shapiro-Wilk test; if violated ($p < 0.05$), use Mann-Whitney U test

**Secondary Hypothesis Tests:**

1. **Geometric Metric Improvement (Pre/Post-Intervention)**:
   - **Test**: Paired t-test within same run
   - **Null**: $\Delta\sigma^2(E) \leq 0$ (no dispersion increase)
   - **Alternative**: $\Delta\sigma^2(E) > 0$ (dispersion increases)
   - **Significance**: $\alpha = 0.05$

2. **Correlation Analysis (Geometry ↔ Performance)**:
   - **Test**: Pearson correlation between average dispersion and final accuracy
   - **Null**: $\rho = 0$ (no correlation)
   - **Alternative**: $\rho > 0$ (positive correlation)
   - **Minimum Effect**: $r \geq 0.3$ (medium correlation)
   - **Significance**: $\alpha = 0.05$

**Multiple Comparisons Correction:**
- Bonferroni correction for 4 primary comparisons (4 experimental/ablation groups vs. control): $\alpha_{\text{corrected}} = 0.05/4 = 0.0125$

**Confound Control:**
- **Hardware**: All runs on same GPU type (A100)
- **Software**: Fixed PyTorch 2.0.1, CUDA 11.8, Open_CLIP commit hash
- **Data**: Fixed dataset splits, same preprocessing pipeline
- **Checkpoints**: Save at fixed intervals (every 5,000 steps) for temporal analysis

**Visualization:**
- Box plots for task performance across groups
- Time series plots for geometric metrics (dispersion, RSA) with intervention markers
- Scatter plots for correlation analysis (dispersion vs. accuracy, RSA vs. Recall@10)
- t-SNE embeddings at collapse vs. healthy timepoints

#### 2.3.6 Validation Protocol

**Phase 1: Existence Validation (Sub-Hypothesis 1)**

*"Do CLIP-style models exhibit detectable geometric pathologies during training?"*

**Procedure:**
1. Train baseline CLIP on CC3M for 50,000 steps
2. Compute dispersion and RSA every 100 steps (500 measurements total)
3. Identify anomalous periods using bootstrap thresholds ($< \mu - 2\sigma$)
4. Measure frequency: $f_{\text{collapse}} = C/T$ (fraction of steps with collapse)

**Success Criterion**: $f_{\text{collapse}} \geq 0.10$ (≥10% of training steps show anomalies)

**Qualitative Validation**: Generate t-SNE plots at 5 collapse timepoints and 5 healthy timepoints; visual inspection should show tighter clustering during collapse

**Phase 2: Mechanism Validation (Sub-Hypothesis 2)**

*"Does automated intervention improve geometric health within 500 steps?"*

**Procedure:**
1. Train GeometricWatch-enabled model (Experimental Group 2)
2. For each intervention event at $t_0$, measure:
   - Pre-intervention: $\sigma^2(t_0)$, $\text{RSA}(t_0)$
   - Post-intervention: $\sigma^2(t_0 + 500)$, $\text{RSA}(t_0 + 500)$
3. Compute improvement: $\Delta\sigma^2 = \sigma^2(t_0 + 500) - \sigma^2(t_0)$

**Success Criteria**:
- $\Delta\sigma^2 \geq 0.20 \cdot \sigma^2(t_0)$ (≥20% dispersion increase)
- $|\Delta\text{RSA}| < 0.05$ (RSA remains stable, <5% change)

**Statistical Test**: Paired t-test across all intervention events ($n \approx 20-50$ events per run)

**Phase 3: Comparison Validation (Sub-Hypothesis 3)**

*"Does geometric health correlate with task performance?"*

**Procedure:**
1. Compute average dispersion $\bar{\sigma}^2$ and average RSA $\overline{\text{RSA}}$ for each of 25 runs
2. Evaluate final checkpoint on ImageNet (accuracy) and COCO (Recall@10)
3. Compute Pearson correlations:
   - $r(\bar{\sigma}^2, \text{Acc}_{\text{ImageNet}})$
   - $r(\overline{\text{RSA}}, \text{Recall@10}_{\text{COCO}})$

**Success Criteria**:
- $r(\bar{\sigma}^2, \text{Acc}) > 0.3$ with $p < 0.05$ (medium positive correlation)
- $r(\overline{\text{RSA}}, \text{Recall@10}) > 0.3$ with $p < 0.05$

**Causal Inference**: Compare experimental groups (with intervention) vs. control (without); if experimental groups show both higher geometric metrics AND higher performance, supports causal claim

**Falsification Criteria:**

The hypothesis is **falsified** if ANY of the following occur:
1. Geometric metric improvement <10% (interventions ineffective)
2. Task performance degradation >1% (interventions harmful)
3. Training instability (loss diverges or fails to converge)
4. Computational overhead ≥10% (efficiency requirement violated)
5. No correlation ($|r| < 0.1$) between metrics and performance (monitored metrics irrelevant)

### 2.4 Implementation Details

**PyTorch Callback Architecture:**

```python
class GeometricWatchCallback:
    def __init__(self, config):
        self.dispersion_threshold_v = None
        self.dispersion_threshold_t = None
        self.rsa_threshold = None
        self.intervention_active = False
        self.intervention_start_step = None
        self.last_intervention_step = -1000  # Cooldown tracking
        self.lambda_current = 0.0
        
    def on_train_batch_end(self, step, embeddings_v, embeddings_t):
        # Compute metrics every 100 steps
        if step % 100 == 0:
            sigma2_v = compute_dispersion(embeddings_v)
            sigma2_t = compute_dispersion(embeddings_t)
            rsa_score = compute_rsa(embeddings_v, embeddings_t, n_sample=200)
            
            # Log to TensorBoard
            self.log_metrics(step, sigma2_v, sigma2_t, rsa_score)
            
            # Check for anomalies (after warm-up)
            if step > 1000 and step - self.last_intervention_step > 1000:
                if sigma2_v < self.dispersion_threshold_v or \
                   sigma2_t < self.dispersion_threshold_t:
                    self.trigger_intervention(step)
            
            # Update adaptive thresholds every 500 steps
            if step % 500 == 0 and step > 5000:
                self.update_thresholds()
        
        # Apply graduated regularization
        if self.intervention_active:
            self.lambda_current = self.compute_lambda(step)
            return self.lambda_current
        return 0.0
```

**Efficient RSA Computation:**

```python
def compute_rsa(embeddings_v, embeddings_t, n_sample=200):
    # Subsample to reduce complexity
    indices = torch.randperm(embeddings_v.size(0))[:n_sample]
    e_v_sample = embeddings_v[indices]
    e_t_sample = embeddings_t[indices]
    
    # Compute pairwise distance matrices
    D_v = torch.cdist(e_v_sample, e_v_sample, p=2)
    D_t = torch.cdist(e_t_sample, e_t_sample, p=2)
    
    # Vectorize upper triangular (exclude diagonal)
    mask = torch.triu(torch.ones_like(D_v), diagonal=1).bool()
    d_v = D_v[mask]
    d_t = D_t[mask]
    
    # Pearson correlation
    rsa = torch.corrcoef(torch.stack([d_v, d_t]))[0, 1]
    return rsa.item()
```

**Dispersive Regularizer:**

```python
def dispersive_loss(embeddings_v, embeddings_t, sigma2_target):
    sigma2_v = torch.var(embeddings_v, dim=0).mean()
    sigma2_t = torch.var(embeddings_t, dim=0).mean()
    
    loss_v = -torch.log(sigma2_v / sigma2_target + 1e-8)
    loss_t = -torch.log(sigma2_t / sigma2_target + 1e-8)
    
    return loss_v + loss_t
```

## 3. Expected Outcomes & Impact

### 3.1 Expected Outcomes

**Primary Outcomes:**

1. **Geometric Pathology Reduction**:
   - **Expected**: ≥30% reduction in collapse event count (steps where $\sigma^2 < \theta_{\text{collapse}}$) in GeometricWatch-enabled models compared to baseline
   - **Mechanism**: Automated interventions detect and correct collapse before it becomes severe
   - **Validation**: Statistical comparison of collapse frequencies across experimental groups vs. control

2. **Downstream Task Performance Improvement**:
   - **Expected**: ≥1% improvement in ImageNet zero-shot top-1 accuracy (e.g., baseline 42% → experimental 43%+) OR no degradation (≤0.5% drop) across all 3 evaluation tasks
   - **Mechanism**: Better geometric health (higher dispersion, maintained alignment) → improved semantic encoding → higher task accuracy
   - **Validation**: One-sided t-test with $\alpha = 0.0125$ (Bonferroni-corrected)

3. **Computational Efficiency**:
   - **Expected**: <5% training time overhead (e.g., baseline 24 hours → experimental 25.2 hours on 4× A100)
   - **Mechanism**: Efficient metric computation (subsampling, periodic evaluation) and minimal regularizer cost
   - **Validation**: Wall-clock time profiling with PyTorch profiler

**Secondary Outcomes:**

4. **Post-Intervention Recovery**:
   - **Expected**: Within 500 steps after intervention trigger, dispersion increases by ≥20% relative to pre-intervention value
   - **Validation**: Paired t-test on pre/post-intervention measurements across all intervention events

5. **Intervention Frequency Stabilization**:
   - **Expected**: Intervention rate decreases over training (early: 1 per 500 steps → late: 1 per 2000 steps)
   - **Interpretation**: Model learns better representations, requiring fewer corrections
   - **Validation**: Temporal analysis of intervention event timestamps

6. **Geometry-Performance Correlation**:
   - **Expected**: Positive correlation between average dispersion and downstream accuracy ($r > 0.3$, $p < 0.05$)
   - **Implication**: Validates that monitored geometric properties are task-relevant
   - **Validation**: Pearson correlation across 25 runs (5 groups × 5 seeds)

**Qualitative Outcomes:**

7. **Interpretable Training Insights**:
   - TensorBoard dashboards showing geometric health trajectories alongside loss curves
   - t-SNE visualizations contrasting collapse vs. healthy embedding distributions
   - Intervention event logs enabling post-hoc analysis of training dynamics

8. **Open-Source Diagnostic Tool**:
   - Production-ready PyTorch implementation integrated with Open_CLIP
   - Documentation and tutorials for practitioner adoption
   - Reusable template for adaptive geometric regularization

### 3.2 Impact on Multimodal Representation Learning

**Theoretical Impact:**

1. **Multi-Scale Geometric Quality Framework**: Establishes systematic methodology for connecting geometric properties at multiple scales (micro: intra-modal variance, macro: cross-modal alignment) to representation quality. This framework provides:
   - **Conceptual Clarity**: Distinguishes collapse (within-modality pathology) from misalignment (cross-modality pathology)
   - **Metric Design Principles**: Demonstrates why dispersion and RSA capture complementary aspects of geometric health
   - **Generalization Potential**: Framework extensible to other multimodal architectures (audio-visual, 3D-language) and other scales (meso-level manifold alignment via fiber product)

2. **Bridging Neuroscience and ML**: Demonstrates successful transfer of RSA from neuroscience (brain encoding studies) to practical ML training monitoring, opening pathway for adapting other neuroscience metrics (e.g., centered kernel alignment, procrustes distance) to multimodal learning diagnostics.

3. **Automated Intervention Theory**: Establishes design principles for mid-training geometric interventions with stability guarantees:
   - **Warm-up Period**: Prevents premature interventions during initial convergence
   - **Graduated Application**: Gradual ramp-up avoids optimization shocks
   - **Cooldown Period**: Ensures stability between interventions
   - **Maximum Strength Bound**: Preserves primary objective (contrastive alignment) while correcting pathologies

**Methodological Impact:**

4. **Practical Monitoring System**: Delivers production-ready tool addressing real gap in CLIP practitioner workflow:
   - **Current Practice**: Practitioners rely on opaque loss curves, discover geometric failures post-hoc
   - **GeometricWatch**: Real-time geometric health monitoring with interpretable metrics
   - **Adoption Potential**: Open_CLIP integration via callbacks enables seamless adoption by existing users (13K+ GitHub stars)

5. **Two-Stage Threshold Calibration**: Novel methodology solving challenge of setting anomaly detection thresholds without manual tuning:
   - **Bootstrap Stage**: Short calibration run (1 epoch) captures metric distributions
   - **Adaptive Stage**: Sliding window allows online threshold adjustment as training progresses
   - **Generalization**: Methodology applicable to other adaptive training systems (learning rate scheduling, early stopping)

6. **Validation Protocol**: Establishes experimental methodology for evaluating geometric health interventions:
   - **Three-Phase Validation**: Existence (pathologies detectable) → Mechanism (interventions effective) → Comparison (geometry correlates with performance)
   - **Falsification Criteria**: Concrete conditions for rejecting hypothesis (e.g., <10% metric improvement, >1% performance degradation)
   - **Reusability**: Protocol template for future work on geometric regularization

**Practical Impact:**

7. **Reduced Computational Waste**: Enables early detection of geometric pathologies, preventing wasted compute on models with poor representation quality:
   - **Current Cost**: Training CLIP ViT-B/32 on CC3M requires ~100 GPU-hours (4× A100 for 24 hours)
   - **Potential Savings**: If 20% of training runs exhibit severe collapse, early detection could save 20 GPU-hours per failed run
   - **Scale Impact**: For organizations training hundreds of models, savings compound significantly

8. **Improved Model Quality**: Higher downstream task performance (≥1% accuracy improvement) translates to:
   - **Zero-shot Classification**: Better performance on ImageNet and domain-specific datasets
   - **Retrieval Systems**: Improved image-text matching for search applications
   - **Transfer Learning**: Better initialization for fine-tuning on downstream tasks

9. **Interpretable Diagnostics**: TensorBoard logging provides interpretable signals for debugging training issues:
   - **Dispersion Collapse**: Identifies when embeddings cluster too tightly
   - **Alignment Drift**: Detects when vision and text representations diverge semantically
   - **Intervention Effectiveness**: Visualizes post-intervention recovery trajectories

**Broader Research Impact:**

10. **Foundation for Future Work**:
    - **Meso-Level Alignment**: Framework supports future integration of fiber product metric (via CCA) for manifold alignment monitoring
    - **Multi-Intervention Strategies**: Enables research on combining dispersive and anchoring regularizers with coordinated triggering
    - **Other Architectures**: Methodology extensible to unified encoders (VisualBERT), generative models (DALL-E), and other multimodal paradigms
    - **Other Modalities**: Principles applicable to audio-visual, video-language, 3D-language learning

11. **Data-Driven Understanding**: Correlation analysis (geometry ↔ performance) enables:
    - **Task-Specific Insights**: Identify which geometric properties matter for specific downstream tasks (e.g., does dispersion matter more for classification vs. retrieval?)
    - **Architecture Comparison**: Compare geometric health across different encoder architectures (ViT vs. ResNet, BERT vs. GPT)
    - **Dataset Effects**: Study how dataset characteristics (diversity, noise) affect geometric pathology prevalence

12. **Community Contribution**: Open-source release with documentation:
    - **Reproducibility**: Full code, hyperparameters, and experimental protocols enable replication
    - **Extensibility**: Modular design (PyTorch callbacks) allows easy customization
    - **Education**: Tutorials and visualizations help practitioners understand geometric quality concepts

### 3.3 Addressing Workshop Themes

This research directly addresses the workshop's core questions:

**Representation Properties:**
- *"What semantic information is encoded in learned representations?"* → RSA metric measures shared semantic structure across modalities
- *"How does geometry of representation space affect quality?"* → Dispersion metric quantifies representational capacity; correlation analysis validates geometry-performance connection

**Training Dynamics:**
- *"How do learning objectives influence representations?"* → Demonstrates how contrastive loss alone can lead to collapse; shows dispersive regularizer corrects pathology
- *"How do we promote robustness?"* → Automated intervention system promotes robustness to geometric pathologies during training

**Modality Interactions:**
- *"How do different modalities contribute to semantics?"* → RSA alignment tracks how vision and text modalities maintain semantic consistency
- *"What are benefits of multimodal observations?"* → Framework enables studying whether geometric health in multimodal setting differs from unimodal baselines

### 3.4 Limitations and Future Directions

**Current Limitations:**

1. **Scope**: MVP focuses on CLIP-style dual encoders with vision+text; generalization to other architectures (unified encoders, generative models) and modalities (audio, video, 3D) requires validation

2. **Scale**: Experiments on CC3M (3M pairs); large-scale training (LAION-400M, 400M+ pairs) may exhibit different geometric dynamics

3. **Metrics**: Dispersion and RSA capture micro/macro scales; meso-level manifold alignment (fiber product) deferred to full version

4. **Intervention**: Only dispersive regularizer tested; anchoring regularizer and combined strategies remain unexplored

**Future Directions:**

1. **Full Multi-Scale Framework**: Implement fiber product approximation (via CCA) for meso-level alignment monitoring, completing three-scale framework

2. **Multi-Intervention Strategies**: Explore coordinated triggering of dispersive (collapse correction) and anchoring (drift correction) regularizers

3. **Large-Scale Validation**: Test on LAION-400M with larger models (ViT-L/14) to validate scalability

4. **Cross-Architecture Generalization**: Adapt framework to unified encoders (VisualBERT, FLAVA), generative models (DALL-E, Stable Diffusion)

5. **Cross-Modality Extension**: Extend to audio-visual (AudioCLIP), video-language (VideoCLIP), 3D-language (ULIP) learning

6. **Theoretical Analysis**: Develop formal guarantees for intervention stability and convergence properties

7. **Hyperparameter Optimization**: Automated tuning of intervention policy parameters ($\lambda_{\max}$, ramp-up duration, cooldown period) via meta-learning

This research provides a foundational framework and practical tool for understanding and improving geometric quality in multimodal representation learning, with clear pathways for extension and broad applicability to the multimodal learning community.