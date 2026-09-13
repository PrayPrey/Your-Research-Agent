# Research Proposal: BioDistill: Progressive Knowledge Distillation with Uncertainty-Aware Active Learning for Lab-Deployable Protein Foundation Models

## 1. Introduction

### Background

Protein foundation models have revolutionized computational biology, enabling unprecedented capabilities in protein structure prediction, function annotation, and variant effect prediction. Models such as ESM-2 (with up to 15 billion parameters) and ProtTrans have achieved remarkable performance by learning rich representations from hundreds of millions of protein sequences. However, these advances come with a significant accessibility challenge: deploying these models requires substantial computational resources, typically involving multiple high-end GPUs with hundreds of gigabytes of memory—infrastructure that is far beyond the reach of most wet lab environments.

This resource gap creates a critical bottleneck in translating machine learning advances to practical biological discovery. While a computational biology lab at a major research university might have access to a single workstation with an 8-16GB GPU, state-of-the-art protein foundation models demand orders of magnitude more computational power. Furthermore, biologists require not just predictions but also reliable confidence estimates to prioritize expensive and time-consuming experimental validations. Current approaches to model compression and uncertainty quantification have been developed largely in isolation, missing crucial opportunities for synergy that could simultaneously address both efficiency and reliability requirements.

Knowledge distillation, the process of transferring knowledge from large "teacher" models to smaller "student" models, offers a promising pathway toward deployable models. However, standard distillation approaches suffer from significant performance degradation, particularly on underrepresented protein families and novel sequences—precisely the cases of greatest scientific interest. Recent advances in uncertainty-aware distillation (Zhang et al., 2023) and active learning for scientific applications (Cao & Shen, 2019) suggest that these challenges can be addressed through careful algorithmic design, but no existing framework specifically targets the unique requirements of lab-deployable biological foundation models.

### Research Objectives

This research proposes **BioDistill**, a novel framework that jointly addresses model compression and uncertainty quantification for protein foundation models through three integrated innovations:

1. **Develop an uncertainty-guided distillation methodology** that leverages multi-teacher ensembles to simultaneously compress models and produce calibrated confidence estimates.

2. **Design a progressive compression pipeline** that iteratively distills knowledge through intermediate-sized models, preserving critical biological representations while achieving 10-50× parameter reduction.

3. **Create an active refinement protocol** that enables efficient model adaptation through uncertainty-guided experimental prioritization, supporting true lab-in-the-loop workflows.

### Significance

BioDistill directly addresses the accessibility gap highlighted by the workshop's call for efficient and accessible foundation models. By producing models that run on single GPUs with <8GB memory while maintaining >95% of original performance and providing calibrated uncertainty estimates, this work will enable individual labs to leverage the power of foundation models without requiring institutional-scale computational infrastructure. The active refinement protocol further empowers biologists to iteratively improve model performance based on their specific experimental context, creating a virtuous cycle between computational predictions and wet lab validation.

## 2. Methodology

### 2.1 Problem Formulation

Let $f_T: \mathcal{X} \rightarrow \mathcal{Y}$ denote a large pre-trained protein foundation model (teacher) that maps protein sequences $x \in \mathcal{X}$ to representations or predictions $y \in \mathcal{Y}$. Our goal is to learn a compressed student model $f_S$ with parameters $\theta_S$ such that:

1. $|\theta_S| \ll |\theta_T|$ (significant parameter reduction)
2. $\mathbb{E}_{x \sim P_{data}}[L(f_S(x), f_T(x))] < \epsilon$ (bounded performance loss)
3. $f_S$ produces calibrated uncertainty estimates $u(x)$ where $\mathbb{E}[|u(x) - \text{err}(x)|]$ is minimized

### 2.2 Uncertainty-Guided Distillation

We employ an ensemble of $K$ teacher models $\{f_{T_1}, ..., f_{T_K}\}$ obtained through different strategies: (a) checkpoints from different training stages, (b) models trained with different random seeds, and (c) models fine-tuned on different biological domains. The ensemble disagreement provides a natural uncertainty signal.

**Step 1: Teacher Ensemble Construction**

For a base foundation model $f_T$ (e.g., ESM-2-650M), we construct the ensemble:
$$\mathcal{T} = \{f_{T_k}\}_{k=1}^{K} \text{ where } f_{T_k} = \text{Perturb}(f_T, \xi_k)$$

Here, $\text{Perturb}(\cdot, \xi_k)$ applies structured perturbations including dropout-based weight perturbation and domain-specific fine-tuning.

**Step 2: Uncertainty-Aware Loss Function**

For each input sequence $x$, we compute the teacher ensemble predictions and their disagreement:
$$\bar{y}(x) = \frac{1}{K}\sum_{k=1}^{K} f_{T_k}(x), \quad \sigma^2(x) = \frac{1}{K}\sum_{k=1}^{K}||f_{T_k}(x) - \bar{y}(x)||^2$$

The student model is trained to predict both the mean prediction and the uncertainty:
$$\mathcal{L}_{distill} = \mathbb{E}_x\left[\underbrace{||f_S(x) - \bar{y}(x)||^2}_{\text{prediction loss}} + \lambda_u \underbrace{||u_S(x) - \sigma^2(x)||^2}_{\text{uncertainty loss}}\right]$$

where $u_S(x)$ is the student's uncertainty head output and $\lambda_u$ balances the two objectives.

**Step 3: Adaptive Sample Weighting**

Following insights from prime-aware adaptive distillation (Zhang et al., 2020), we weight samples based on their informativeness:
$$w(x) = \alpha \cdot \mathbb{I}[\sigma^2(x) > \tau_{\text{high}}] + (1-\alpha) \cdot \text{softmax}\left(\frac{\sigma^2(x)}{\tau}\right)$$

This weighting emphasizes both high-uncertainty samples (where careful learning is needed) and samples with moderate uncertainty (which provide the richest learning signal).

### 2.3 Progressive Compression Pipeline

Rather than directly distilling from the largest teacher to the smallest student, we employ a progressive approach through $M$ intermediate models.

**Stage Definition**

For a target compression ratio $r$ (e.g., $r=0.02$ for 50× compression), we define intermediate stages:
$$r_m = r^{m/M}, \quad m \in \{1, 2, ..., M\}$$

Each stage produces a model with approximately $r_m \cdot |\theta_T|$ parameters.

**Architecture Scaling**

At each stage $m$, we define the student architecture by scaling:
- Hidden dimension: $d_m = d_T \cdot \sqrt{r_m}$
- Number of layers: $L_m = \max(6, \lfloor L_T \cdot r_m^{0.3} \rfloor)$
- Attention heads: $h_m = \max(4, \lfloor h_T \cdot \sqrt{r_m} \rfloor)$

**Layer-wise Knowledge Transfer**

We align intermediate representations between consecutive stages using projection matrices:
$$\mathcal{L}_{layer} = \sum_{l \in \mathcal{A}} ||P_l \cdot h_S^{(l)}(x) - h_{T_{m-1}}^{(\phi(l))}(x)||^2$$

where $\mathcal{A}$ is a set of aligned layer indices, $P_l$ is a learnable projection matrix, and $\phi(\cdot)$ maps student layers to teacher layers.

**Complete Training Objective**

The full objective for stage $m$ is:
$$\mathcal{L}_m = \mathcal{L}_{distill} + \lambda_{layer}\mathcal{L}_{layer} + \lambda_{task}\mathcal{L}_{task}$$

where $\mathcal{L}_{task}$ is a task-specific supervised loss (e.g., for protein function prediction) when labeled data is available.

### 2.4 Active Refinement Protocol

The compressed model with calibrated uncertainties enables an efficient lab-in-the-loop workflow.

**Acquisition Function**

Given a pool of candidate proteins $\mathcal{P}$ for experimental validation, we select the next batch using:
$$x^* = \arg\max_{x \in \mathcal{P}} \left[\beta \cdot u_S(x) + (1-\beta) \cdot \text{EI}(f_S(x))\right]$$

where EI is the Expected Improvement for optimization tasks and $\beta$ controls exploration-exploitation trade-off.

**Model Update Strategy**

After receiving experimental results $\mathcal{D}_{new}$, we perform efficient adaptation:
1. Freeze base layers of $f_S$
2. Fine-tune only top $k$ layers and task-specific heads
3. Apply elastic weight consolidation to prevent catastrophic forgetting:
$$\mathcal{L}_{update} = \mathcal{L}_{task}(\mathcal{D}_{new}) + \lambda_{EWC}\sum_i F_i(\theta_i - \theta_i^*)^2$$

where $F_i$ represents Fisher information for parameter importance.

### 2.5 Experimental Design

**Datasets**

1. **Pre-training/Distillation**: UniRef50 (45M sequences) for representation learning
2. **Downstream Tasks**: 
   - TAPE benchmark (fluorescence prediction, stability prediction, remote homology)
   - DeepLoc 2.0 (subcellular localization)
   - Enzyme Commission number prediction

**Baselines**

1. Standard knowledge distillation (Hinton et al.)
2. DistilProtBERT (direct distillation without progressive stages)
3. Post-hoc uncertainty calibration (temperature scaling, MC-Dropout)
4. Random sampling for active learning comparison

**Evaluation Metrics**

- **Performance**: Spearman correlation (regression), accuracy/F1 (classification)
- **Efficiency**: Parameters, FLOPs, GPU memory, inference time
- **Uncertainty Quality**: Expected Calibration Error (ECE), Area Under Sparsification Error curve (AUSE)
- **Active Learning Efficiency**: Area under learning curve, samples to reach 95% performance

**Hardware Requirements Validation**

We will validate deployability on:
- Consumer GPU (NVIDIA RTX 3060, 12GB)
- Workstation GPU (NVIDIA RTX 3090, 24GB)
- Cloud notebook (Google Colab free tier, ~12GB)

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Compressed Model Suite**: A family of protein foundation models at 4 compression levels (10×, 20×, 30×, 50×) with documented performance-efficiency trade-offs.

2. **Performance Targets**: 
   - 50× compressed model achieving >90% of ESM-2-650M performance
   - 10× compressed model achieving >97% performance
   - All models deployable on 8GB GPUs

3. **Calibrated Uncertainties**: Models with ECE < 0.05 across downstream tasks, enabling reliable experimental prioritization.

4. **Active Learning Efficiency**: Demonstration of 3-5× reduction in required experimental iterations compared to random selection for model refinement.

5. **Open-Source Release**: Complete codebase, pre-trained models, and documentation for lab deployment.

### Broader Impact

This research directly addresses the workshop's core mission of bridging the gap between ML advances and wet lab adoption. By democratizing access to protein foundation models, BioDistill will:

1. **Enable Individual Labs**: Allow researchers without institutional computing infrastructure to leverage state-of-the-art models for hypothesis generation and experimental prioritization.

2. **Accelerate Discovery Cycles**: The uncertainty-guided active refinement protocol will reduce wasted experimental resources by focusing validation efforts on the most informative candidates.

3. **Establish Best Practices**: Provide a template for compressing other biological foundation models (genomic, transcriptomic, structural) with the same joint optimization of efficiency and uncertainty quantification.

4. **Foster Interdisciplinary Collaboration**: The lab-in-the-loop framework creates natural collaboration points between computational and experimental researchers, encouraging the iterative refinement workflows essential for biological discovery.