# Research Proposal: Latent-Space Bayesian Inference for Calibrated Uncertainty Quantification in Large Language Models

## 1. Title

**Latent-Space Bayesian Inference for Calibrated Uncertainty Quantification in Large Language Models**

## 2. Introduction

### 2.1 Background

The deployment of Large Language Models (LLMs) in critical applications such as healthcare diagnostics, scientific discovery, and legal decision-making has accelerated dramatically. However, a fundamental challenge persists: these models often produce confident predictions even when uncertain, leading to potentially catastrophic failures in high-stakes scenarios. The workshop's emphasis on Bayesian decision-making and uncertainty quantification directly addresses this critical gap, as reliable uncertainty estimates are essential for safe AI deployment.

Current uncertainty quantification (UQ) methods for LLMs face a fundamental trade-off between calibration quality and computational tractability. Deep Ensembles, which train multiple independent models, achieve reasonable calibration (Expected Calibration Error, ECE ≈ 0.08-0.12) but require 5× computational cost at inference time—prohibitive for billion-parameter models. Monte Carlo Dropout (MC Dropout) offers computational efficiency with approximately 10× inference overhead, but suffers from poor calibration (ECE ≈ 0.12-0.15) due to its approximate nature. Temperature scaling provides post-hoc calibration with minimal overhead but lacks principled epistemic uncertainty estimates crucial for out-of-distribution (OOD) detection.

Recent Bayesian approaches have attempted to address these limitations through two primary strategies: (1) parameter-space methods that perform inference over model weights, which become intractable for billion-parameter LLMs, and (2) input-space methods like Textual Bayes (2025) that operate through prompt engineering, which lack the theoretical guarantees of true Bayesian inference. Both approaches miss a critical opportunity: leveraging LLM hidden state representations, which recent neuroscience-inspired research (Zur et al., 2025) demonstrates encode uncertainty information through predictive coding mechanisms.

The success of GroVE (2025), which applied Gaussian Process Generative Latent Variable Models (GP-GPLVM) to frozen CLIP embeddings for multimodal tasks, suggests that operating in latent representation space can achieve both Bayesian rigor and computational tractability. However, no existing work has explored whether this approach transfers to text-only LLM hidden states, which are trained autoregressively rather than contrastively, representing a critical knowledge gap.

### 2.2 Research Objectives

This research proposes **Latent-Space Bayesian Inference for Language Models (LSBI-LM)**, a novel framework that performs Gaussian Process-based Bayesian inference over frozen LLM hidden state representations. Our primary objectives are:

**O1. Theoretical Contribution:** Establish the first formal framework for GP-based Bayesian inference on text-only LLM hidden states, extending neuroscience predictive coding principles to language model uncertainty quantification.

**O2. Methodological Innovation:** Develop a computationally tractable sparse GP framework that achieves calibrated uncertainty estimates (ECE < 0.10) with minimal inference overhead (<200ms per query) for billion-parameter frozen LLMs.

**O3. Empirical Validation:** Demonstrate superior performance compared to existing UQ methods (MC Dropout, Deep Ensembles, Temperature Scaling, Textual Bayes) across multiple text classification and question-answering tasks, with particular emphasis on OOD detection (AUROC > 0.80).

**O4. Practical Impact:** Provide an open-source implementation that enables practitioners to add calibrated uncertainty quantification to any frozen pretrained LLM without retraining, preserving pretrained knowledge while enabling safe deployment.

### 2.3 Research Significance

This research addresses critical challenges identified in the workshop's call:

**Theoretical Significance:** We bridge neuroscience (predictive coding), Bayesian machine learning (Gaussian Processes), and deep learning (LLMs), providing theoretical foundations for latent-space uncertainty quantification that extend beyond current parameter-space or input-space approaches.

**Methodological Advancement:** By operating in latent space (4K-8K dimensions) rather than parameter space (billions of dimensions), we resolve the scalability-rigor trade-off that has hindered Bayesian methods for large models. Our sparse GP formulation with inducing points (m=100-500) enables exact posterior inference with computational tractability.

**Practical Impact:** The ability to add calibrated uncertainty to frozen pretrained LLMs without retraining has immediate applications in:
- **Healthcare:** Medical diagnosis systems requiring uncertainty-aware predictions
- **Scientific Discovery:** Drug discovery and materials science where epistemic uncertainty guides experimental design
- **Active Learning:** Efficient data collection through uncertainty-based query selection
- **Safe AI Deployment:** OOD detection preventing silent failures in production systems

**Alignment with Workshop Themes:** This work directly addresses the workshop's focus on scaling Bayesian methods to handle complexity of larger models while maintaining performance guarantees (calibration), and explores how frontier LLMs can enhance Bayesian methods through their learned representations.

## 3. Methodology

### 3.1 Research Design Overview

Our methodology follows a rigorous hypothesis-driven approach with four phases: (0) Pilot validation on GPT-2 to de-risk core assumptions, (1) Core method development and validation on medium-scale models, (2) Scaling to billion-parameter LLMs, and (3) Comprehensive comparative evaluation. We employ controlled experiments with statistical hypothesis testing, ablation studies, and reproducibility protocols.

### 3.2 Data Collection

**Datasets:** We will evaluate on diverse text classification and question-answering tasks:

1. **Sentiment Analysis:** SST-2 (Stanford Sentiment Treebank, 67K training, 872 validation, 1.8K test examples)
2. **Natural Language Inference:** MNLI (Multi-Genre NLI, 393K training, 20K validation)
3. **Question Answering:** SQuAD 2.0 (extractive QA, 130K training questions)
4. **Domain-Specific:** SciFact (scientific claim verification, 1.4K claims) for domain shift evaluation

**Out-of-Distribution Detection:** For each in-distribution task, we construct OOD test sets:
- SST-2 (movie reviews) → Medical reviews (MIMIC-III clinical notes sentiment)
- MNLI (general text) → Scientific abstracts (arXiv papers)
- SQuAD (Wikipedia) → Legal documents (CaseHOLD)

**Data Splits:** We use standard train/validation/test splits, with additional calibration sets (1K, 5K, 10K examples) sampled from training data for GP training. All experiments use fixed random seeds (42, 123, 456, 789, 1011) for reproducibility.

### 3.3 Algorithmic Framework

#### 3.3.1 Hidden State Extraction

Given a frozen pretrained LLM $f_\theta$ with $L$ transformer layers, we extract hidden state representations from middle layers. For an input text sequence $\mathbf{x} = (x_1, \ldots, x_T)$, the hidden state at layer $\ell$ and position $t$ is denoted $\mathbf{h}_t^{(\ell)} \in \mathbb{R}^d$, where $d$ is the hidden dimension (typically 768-8192).

**Layer Selection Strategy:** We extract representations from three candidate layers:
- Early-middle: $\ell_1 = \lfloor L/4 \rfloor$
- Middle: $\ell_2 = \lfloor L/2 \rfloor$  
- Late-middle: $\ell_3 = \lfloor 3L/4 \rfloor$

**Sequence Aggregation:** For classification tasks, we use the [CLS] token representation or mean-pooling:
$$\mathbf{z}^{(\ell)} = \frac{1}{T} \sum_{t=1}^T \mathbf{h}_t^{(\ell)}$$

For extractive QA, we use the question representation (first sequence in BERT-style models).

#### 3.3.2 Sparse Gaussian Process Formulation

We model the predictive distribution using a Gaussian Process over the extracted latent representations. For a calibration dataset $\mathcal{D} = \{(\mathbf{z}_i, y_i)\}_{i=1}^N$ where $\mathbf{z}_i \in \mathbb{R}^d$ are frozen LLM embeddings and $y_i$ are labels:

**GP Prior:**
$$f(\mathbf{z}) \sim \mathcal{GP}(m(\mathbf{z}), k(\mathbf{z}, \mathbf{z}'))$$

where $m(\mathbf{z}) = 0$ (zero mean) and $k(\mathbf{z}, \mathbf{z}')$ is a kernel function. We primarily use the RBF kernel:
$$k_{\text{RBF}}(\mathbf{z}, \mathbf{z}') = \sigma_f^2 \exp\left(-\frac{\|\mathbf{z} - \mathbf{z}'\|^2}{2\ell^2}\right)$$

with lengthscale $\ell$ and signal variance $\sigma_f^2$ learned via maximum likelihood.

**Sparse Approximation:** To achieve computational tractability, we use the Sparse Variational Gaussian Process (SVGP) framework with $m$ inducing points $\mathbf{Z} = \{\mathbf{z}_j^*\}_{j=1}^m$:

$$q(f) = \int p(f|\mathbf{u}) q(\mathbf{u}) d\mathbf{u}$$

where $\mathbf{u} = f(\mathbf{Z})$ are inducing variables with variational distribution:
$$q(\mathbf{u}) = \mathcal{N}(\mathbf{u}; \mathbf{m}, \mathbf{S})$$

The variational parameters $\mathbf{m} \in \mathbb{R}^m$ and $\mathbf{S} \in \mathbb{R}^{m \times m}$ are optimized via evidence lower bound (ELBO):

$$\mathcal{L} = \sum_{i=1}^N \mathbb{E}_{q(f_i)}[\log p(y_i|f_i)] - \text{KL}[q(\mathbf{u}) \| p(\mathbf{u})]$$

**Predictive Distribution:** For a test point $\mathbf{z}_*$, the predictive distribution is:

$$p(f_*|\mathbf{z}_*, \mathcal{D}) = \int p(f_*|\mathbf{u}, \mathbf{z}_*) q(\mathbf{u}) d\mathbf{u} = \mathcal{N}(f_*; \mu_*, \sigma_*^2)$$

where:
$$\mu_* = \mathbf{k}_*^\top \mathbf{K}_{uu}^{-1} \mathbf{m}$$
$$\sigma_*^2 = k_{**} - \mathbf{k}_*^\top \mathbf{K}_{uu}^{-1} (\mathbf{K}_{uu} - \mathbf{S}) \mathbf{K}_{uu}^{-1} \mathbf{k}_*$$

with $\mathbf{k}_* = k(\mathbf{Z}, \mathbf{z}_*)$ and $\mathbf{K}_{uu} = k(\mathbf{Z}, \mathbf{Z})$.

**Classification:** For binary/multi-class classification, we use the Bernoulli/Categorical likelihood with probit approximation:

$$p(y=c|\mathbf{z}_*) = \Phi\left(\frac{\mu_*^{(c)}}{\sqrt{1 + \sigma_*^{2(c)}}}\right)$$

where $\Phi$ is the standard normal CDF.

#### 3.3.3 Training Procedure

**Algorithm 1: LSBI-LM Training**

```
Input: Frozen LLM f_θ, calibration data D_cal, layer indices {ℓ₁, ℓ₂, ℓ₃}, 
       inducing points m, kernel k
Output: Trained GP models {GP_ℓ₁, GP_ℓ₂, GP_ℓ₃}, selected layer ℓ*

1. For each layer ℓ ∈ {ℓ₁, ℓ₂, ℓ₃}:
2.   Extract embeddings: Z_ℓ = {f_θ^(ℓ)(x_i) : (x_i, y_i) ∈ D_cal}
3.   Initialize inducing points: Z* ← k-means(Z_ℓ, m)
4.   Initialize variational parameters: m ← 0, S ← I
5.   For epoch = 1 to max_epochs:
6.     Compute ELBO: L = Σᵢ E_q(fᵢ)[log p(yᵢ|fᵢ)] - KL[q(u)||p(u)]
7.     Update {m, S, Z*, kernel_params} via Adam optimizer
8.   Evaluate ECE on validation set → ECE_ℓ
9. Select optimal layer: ℓ* = argmin_ℓ ECE_ℓ
10. Return GP_ℓ* as final model
```

**Hyperparameters:**
- Inducing points: $m \in \{100, 200, 500\}$ (grid search)
- Learning rate: $10^{-3}$ with cosine annealing
- Batch size: 256 for SVGP stochastic optimization
- Training epochs: 100 with early stopping (patience=10)
- Kernel: RBF (primary), Matérn-5/2 (ablation)

#### 3.3.4 Inference and Uncertainty Quantification

**Predictive Uncertainty:** For test input $\mathbf{x}_*$:

1. Extract embedding: $\mathbf{z}_* = f_\theta^{(\ell^*)}(\mathbf{x}_*)$
2. Compute GP predictive distribution: $p(f_*|\mathbf{z}_*, \mathcal{D})$
3. Obtain class probabilities: $\hat{p}(y=c|\mathbf{x}_*) = \Phi(\mu_*^{(c)}/\sqrt{1+\sigma_*^{2(c)}})$
4. Epistemic uncertainty: $u_{\text{epist}} = \sigma_*^2$ (GP posterior variance)

**Out-of-Distribution Detection:** We use epistemic uncertainty for OOD detection:

$$\text{OOD-score}(\mathbf{x}) = \max_c \sigma_*^{2(c)}$$

A test example is flagged as OOD if $\text{OOD-score}(\mathbf{x}) > \tau$, where threshold $\tau$ is set to achieve 95% true positive rate on in-distribution validation data.

### 3.4 Experimental Design

#### 3.4.1 Phase 0: Pilot Validation (1 week)

**Purpose:** De-risk the core assumption that text-only LLM embeddings support GP-based UQ.

**Setup:**
- Model: GPT-2 (117M parameters, 12 layers)
- Task: SST-2 sentiment analysis
- Calibration data: 1K examples
- Method: Extract all 12 layers → Train lightweight GPs (m=100) → Measure ECE

**Success Criterion:** ECE < 0.10 AND outperforms MC Dropout

**Go/No-Go Decision:**
- ✅ **GO:** Proceed to Phase 1 (Llama-2-7B)
- ⛔ **NO-GO:** Investigate kernel engineering (deep kernels, spectral kernels), Bayesian Neural Network alternatives, or multi-layer GP combinations

**Resource Estimate:** 1 week, single V100 GPU (~$150 cloud cost)

#### 3.4.2 Phase 1: Core Method Development (4 weeks)

**Models:** Llama-2-7B (7 billion parameters, 32 layers), BERT-Large (340M parameters, 24 layers)

**Tasks:** SST-2, MNLI (in-distribution), Medical reviews, Scientific abstracts (OOD)

**Experiments:**

**E1. Layer Selection Validation:**
- Extract embeddings from layers {8, 16, 24} for Llama-2-7B
- Train GPs with m=200 inducing points
- Measure ECE, Brier score, NLL on validation set
- **Hypothesis:** Middle layers (16) achieve lowest ECE

**E2. Inducing Point Ablation:**
- Fix optimal layer from E1
- Vary m ∈ {50, 100, 200, 500, 1000}
- Measure ECE degradation vs. full GP (m=N, computed on subset)
- Measure training time and inference latency
- **Hypothesis:** m=500 achieves <0.02 ECE degradation vs. full GP

**E3. Calibration Data Scaling:**
- Fix optimal layer and m from E1-E2
- Vary calibration set size: {500, 1K, 2K, 5K, 10K}
- Plot learning curves (ECE vs. calibration size)
- **Hypothesis:** 1K examples sufficient for ECE < 0.10

**E4. Kernel Comparison:**
- Compare RBF, Matérn-5/2, Spectral Mixture kernels
- Measure ECE, computational cost
- **Hypothesis:** RBF sufficient, Matérn-5/2 comparable

#### 3.4.3 Phase 2: Baseline Comparison (3 weeks)

**Baselines:**
1. **MC Dropout:** 10 forward passes with dropout rate 0.1
2. **Deep Ensemble:** 5 independently trained models
3. **Temperature Scaling:** Post-hoc calibration on validation set
4. **Textual Bayes (2025):** Bayesian prompting (if code available)
5. **Vanilla LLM:** Softmax probabilities without calibration

**Evaluation Protocol:**
- Train all methods on same calibration data (5K examples)
- Evaluate on same test sets with 5 random seeds
- Report mean ± std for all metrics

**Statistical Testing:**

**Primary Hypothesis Test:**
$$H_1: \mu_{\text{ECE}}(\text{LSBI-LM}) < 0.10 \quad \text{vs.} \quad H_0: \mu_{\text{ECE}}(\text{LSBI-LM}) \geq 0.10$$

One-sample t-test with $\alpha = 0.05$, bootstrap 95% confidence intervals (1000 samples).

**Comparative Hypothesis Test:**
$$H_1: \mu_{\text{ECE}}(\text{LSBI-LM}) < \mu_{\text{ECE}}(\text{Baseline}) \quad \text{vs.} \quad H_0: \mu_{\text{ECE}}(\text{LSBI-LM}) \geq \mu_{\text{ECE}}(\text{Baseline})$$

Paired t-test for each baseline, Bonferroni correction $\alpha = 0.0125$ (4 primary baselines).

#### 3.4.4 Phase 3: Scaling and Robustness (2 weeks)

**Large-Scale Models:** GPT-3.5 (via API), Llama-2-70B (if resources permit)

**Additional Tasks:** SQuAD 2.0, SciFact (domain-specific)

**Robustness Experiments:**
- **R1. Architecture Generalization:** Evaluate on GPT-2, BERT, Llama-2, RoBERTa
- **R2. Task Diversity:** 6+ tasks spanning sentiment, NLI, QA, fact-checking
- **R3. OOD Robustness:** Multiple distribution shifts per task
- **R4. Computational Profiling:** Latency distribution on A100, V100, T4 GPUs

### 3.5 Evaluation Metrics

**Calibration Metrics:**

1. **Expected Calibration Error (ECE):** Primary metric
$$\text{ECE} = \sum_{b=1}^B \frac{|B_b|}{N} |\text{acc}(B_b) - \text{conf}(B_b)|$$
where $B_b$ are bins of predictions, $N$ total examples. We use 15 bins.

2. **Brier Score:**
$$\text{Brier} = \frac{1}{N} \sum_{i=1}^N \sum_{c=1}^C (\hat{p}_{i,c} - y_{i,c})^2$$

3. **Negative Log-Likelihood (NLL):**
$$\text{NLL} = -\frac{1}{N} \sum_{i=1}^N \log \hat{p}(y_i|\mathbf{x}_i)$$

**OOD Detection Metrics:**

4. **AUROC:** Area under ROC curve for in-distribution vs. OOD classification using epistemic uncertainty scores

5. **AUPR:** Area under precision-recall curve

6. **FPR@95TPR:** False positive rate at 95% true positive rate

**Computational Metrics:**

7. **Inference Latency:** Mean time per query (ms) on single GPU
8. **Training Time:** Total GP training time (hours)
9. **Memory Footprint:** Peak GPU memory (GB)

**Accuracy Metrics:**

10. **Test Accuracy:** Classification accuracy on in-distribution test set
11. **F1 Score:** For imbalanced datasets

### 3.6 Implementation Details

**Software Stack:**
- **LLM Inference:** HuggingFace Transformers (v4.35+)
- **GP Implementation:** GPyTorch (v1.11+) with BoTorch (v0.9+) for SVGP
- **Calibration Metrics:** Uncertainty Toolbox
- **Experiment Tracking:** Weights & Biases
- **Hardware:** NVIDIA A100 (80GB) or V100 (32GB) GPUs

**Reproducibility Protocol:**
- Fixed random seeds for all experiments
- Version-controlled code with Docker containers
- Hyperparameter configurations in YAML files
- Automated experiment scripts with logging
- Public release of code, data splits, and trained models

**Computational Budget:**
- Pilot (Phase 0): 1 GPU-week (~$150)
- Phase 1-2: 8 GPU-weeks (~$1,200)
- Phase 3: 4 GPU-weeks (~$600)
- **Total:** ~12 GPU-weeks (~$2,000 cloud cost)

### 3.7 Falsification Criteria

**Hard Falsification (Reject Hypothesis):**
- ECE ≥ 0.10 on in-distribution tasks (calibration failure)
- Worse than ALL baselines on BOTH SST-2 and MNLI (no improvement)
- Inference latency > 500ms per query (deployment impractical)

**Soft Falsification (Revise Approach):**
- Pilot ECE ≥ 0.10 → Investigate kernel engineering, multi-layer GPs
- OOD AUROC < 0.70 → Revise OOD detection mechanism
- Training time > 8 hours → Optimize inducing point initialization

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Primary Outcomes:**

**O1. Calibration Performance:** We expect LSBI-LM to achieve ECE < 0.10 on text classification tasks (SST-2, MNLI), representing a 10-20% relative improvement over MC Dropout (ECE ≈ 0.12-0.15) and matching or exceeding Deep Ensemble performance (ECE ≈ 0.08-0.12) while requiring only 1× base inference cost plus ~200ms GP overhead versus 5× for ensembles.

**O2. OOD Detection:** GP epistemic uncertainty should enable robust OOD detection with AUROC > 0.80 for distribution shifts (e.g., movie reviews → medical text), outperforming softmax-based methods (AUROC ≈ 0.65-0.75) and matching specialized OOD detectors.

**O3. Computational Efficiency:** With m=500 inducing points, we expect:
- Training time: 2-4 hours on single A100 GPU for 5K calibration examples
- Inference latency: 150-200ms per query (vs. 1000ms for 5-model ensemble)
- Memory overhead: <2GB for GP parameters (vs. 35GB for Llama-2-7B ensemble)

**O4. Layer Selection Insights:** We hypothesize middle layers (L/2 to 3L/4) will achieve optimal calibration, providing empirical validation of the theoretical claim that intermediate representations balance task-specific semantics and uncertainty information.

**Secondary Outcomes:**

**O5. Kernel Analysis:** Ablation studies will reveal whether simple RBF kernels suffice or whether structured kernels (Matérn, Spectral Mixture) provide significant improvements, informing future latent-space UQ research.

**O6. Data Efficiency:** Learning curves will quantify calibration data requirements, potentially demonstrating that 1K-2K examples suffice for ECE < 0.10, enabling practical deployment with limited labeled data.

**O7. Architecture Generalization:** Evaluation across GPT-2, BERT, Llama-2, and RoBERTa will establish whether LSBI-LM generalizes across transformer architectures or requires architecture-specific tuning.

### 4.2 Theoretical Impact

**Advancing Bayesian Deep Learning:** This work establishes latent-space Bayesian inference as a viable alternative to parameter-space and input-space approaches, resolving the scalability-rigor trade-off that has limited Bayesian methods for large models. By demonstrating that frozen LLM representations encode sufficient information for calibrated uncertainty, we provide theoretical foundations for a new class of UQ methods.

**Cross-Domain Knowledge Transfer:** We bridge neuroscience (predictive coding over latent representations), Gaussian Process theory (exact Bayesian inference), and deep learning (transformer representations), creating a principled framework grounded in multiple disciplines. This cross-pollination may inspire similar latent-space approaches in computer vision, reinforcement learning, and multimodal models.

**Uncertainty Decomposition:** By operating in latent space, LSBI-LM naturally separates epistemic uncertainty (GP posterior variance) from aleatoric uncertainty (inherent in data), providing interpretable uncertainty estimates crucial for scientific applications and active learning.

### 4.3 Methodological Impact

**Practical UQ for Frozen LLMs:** The ability to add calibrated uncertainty to any frozen pretrained LLM without retraining addresses a critical gap in the ML toolkit. Practitioners can leverage state-of-the-art pretrained models (GPT-4, Llama-3, etc.) while obtaining Bayesian uncertainty estimates, democratizing access to principled UQ.

**Sparse GP Scalability:** Our SVGP formulation with optimized inducing point selection demonstrates that GPs can scale to high-dimensional latent spaces (4K-8K dimensions) with hundreds of thousands of calibration examples, challenging the perception that GPs are limited to small-scale problems.

**Open-Source Tooling:** We will release a production-ready library integrating with HuggingFace Transformers, enabling researchers and practitioners to apply LSBI-LM with minimal code changes:

```python
from lsbi_lm import LatentSpaceGP
model = LatentSpaceGP.from_pretrained("meta-llama/Llama-2-7b-hf")
model.calibrate(calibration_data, num_inducing=500)
predictions, uncertainty = model.predict(test_data)
```

### 4.4 Practical Impact

**Healthcare Applications:** Medical diagnosis systems require uncertainty quantification to defer to human experts when uncertain. LSBI-LM enables LLM-based clinical decision support systems to provide calibrated confidence scores, improving patient safety. For example, a radiology report classification system could flag uncertain cases for radiologist review.

**Scientific Discovery:** In drug discovery and materials science, active learning guided by epistemic uncertainty can reduce experimental costs by 10-100×. LSBI-LM enables LLM-based molecular property prediction models to identify high-uncertainty candidates for synthesis and testing, accelerating discovery cycles.

**Safe AI Deployment:** Production LLM systems face distribution shift when user queries differ from training data. LSBI-LM's OOD detection (AUROC > 0.80) enables automated monitoring systems to flag anomalous inputs, preventing silent failures. For instance, a customer service chatbot could escalate unusual queries to human agents.

**Active Learning and Data Annotation:** By identifying high-uncertainty examples, LSBI-LM can guide efficient data collection. In low-resource domains (legal, medical, scientific), this reduces annotation costs by prioritizing informative examples, potentially achieving 90% of full-data performance with 20-30% of labels.

### 4.5 Alignment with Workshop Goals

**Scaling Bayesian Methods:** LSBI-LM directly addresses the workshop's challenge of "scaling up Bayesian methods to handle the complexity and dimensionality of larger data and models" by demonstrating that latent-space inference enables tractable Bayesian UQ for billion-parameter LLMs.

**Performance Guarantees:** Our rigorous evaluation protocol with statistical hypothesis testing, calibration metrics (ECE, Brier, NLL), and OOD detection benchmarks establishes performance guarantees crucial for deploying Bayesian methods in critical applications.

**Leveraging Frontier Models:** We demonstrate how pretrained LLM representations serve as "stronger priors" for Bayesian inference, aligning with the workshop's vision of enhancing Bayesian methods with tools from frontier models.

**Interdisciplinary Exchange:** By connecting Gaussian Processes, active learning, uncertainty quantification, and LLMs, this work fosters the "vibrant exchange of ideas" across workshop focus areas, potentially inspiring collaborations between GP researchers and LLM practitioners.

### 4.6 Broader Impacts and Limitations

**Positive Impacts:**
- **Democratization:** Open-source tools enable small research groups and practitioners to add UQ to LLMs without expensive ensemble training
- **Safety:** Calibrated uncertainty and OOD detection reduce risks of deploying LLMs in high-stakes domains
- **Efficiency:** Reduced computational costs (vs. ensembles) lower carbon footprint of uncertainty-aware AI systems

**Limitations and Future Work:**
- **Scope:** Current work focuses on classification and extractive QA; generative tasks (open-ended text generation) require different UQ approaches
- **Calibration Data:** Requires 1K-10K labeled examples; future work should explore few-shot GP methods or transfer learning across tasks
- **Computational Cost:** While efficient vs. ensembles, 200ms overhead may be prohibitive for ultra-low-latency applications; model distillation could address this
- **Theoretical Guarantees:** Empirical calibration does not provide formal PAC-Bayes bounds; future work should establish theoretical calibration guarantees

**Ethical Considerations:** Improved uncertainty quantification may increase trust in LLM predictions, but miscalibration risks remain. We will include prominent disclaimers in documentation emphasizing that ECE < 0.10 does not guarantee perfect calibration, and human oversight remains essential in critical applications.

### 4.7 Timeline and Milestones

**Month 1:** Pilot validation (Phase 0), literature review, codebase setup
**Month 2-3:** Core method development (Phase 1), layer selection, inducing point ablation
**Month 4:** Baseline comparison (Phase 2), statistical analysis
**Month 5:** Scaling experiments (Phase 3), robustness evaluation
**Month 6:** Paper writing, open-source release, workshop submission

**Deliverables:**
1. Research paper submitted to NeurIPS/ICML Bayesian workshop
2. Open-source Python library with documentation and tutorials
3. Benchmark suite for LLM uncertainty quantification
4. Blog post and video tutorial for practitioners

### 4.8 Success Metrics

**Minimum Viable Success:** ECE < 0.10 on at least one task, outperforming MC Dropout, inference < 300ms

**Target Success:** ECE < 0.10 on all tasks, matching Deep Ensemble calibration, OOD AUROC > 0.80, inference < 200ms

**Exceptional Success:** ECE < 0.08 (beating ensembles), OOD AUROC > 0.85, adoption by 100+ GitHub stars within 6 months, citations by follow-up workshop papers

This research has the potential to establish latent-space Bayesian inference as a standard approach for uncertainty quantification in large language models, bridging the gap between Bayesian rigor and computational tractability while enabling safer and more reliable AI systems in critical applications.