# Research Proposal: Compositional Invariance Learning for Unified Spurious Correlation Robustness

## 1. Title

**Compositional Invariance Learning: A Unified Hierarchical Framework for Robust Machine Learning Against Spurious Correlations**

---

## 2. Introduction

### 2.1 Background

Machine learning models deployed in real-world settings frequently fail despite achieving excellent performance on standard benchmarks. A primary cause of this brittleness is the exploitation of spurious correlations—statistical associations present in training data that do not reflect genuine causal relationships and fail to generalize to new environments. This phenomenon manifests across diverse application domains with significant consequences:

In medical imaging, models trained to detect pneumonia from chest X-rays have been shown to rely on hospital-specific scanner artifacts and technician markings rather than physiological indicators of disease. Such models achieve high accuracy within their training hospital but fail catastrophically when deployed elsewhere. In natural language processing, models performing textual entailment tasks exploit superficial lexical overlap between premise and hypothesis rather than understanding semantic relationships, leading to systematic errors on adversarially constructed examples. In precision medicine, polygenic risk scores developed predominantly on European ancestry populations exhibit substantially reduced predictive accuracy for other populations due to reliance on ancestry-correlated genetic variants rather than causal disease mechanisms.

These failures share a common structure: models learn to exploit features that are predictive in training environments but unstable across deployment contexts. The machine learning community has responded with multiple methodological approaches emerging from distinct research traditions. From the causality community, Invariant Risk Minimization (IRM) seeks representations whose optimal predictor is invariant across training environments. From algorithmic fairness, Group Distributionally Robust Optimization (Group DRO) minimizes worst-case loss across demographic subgroups. From robust machine learning, out-of-distribution (OOD) generalization methods develop stress tests and training procedures to improve stability under distribution shift.

Despite shared goals, these communities have developed largely in isolation, resulting in fragmented solutions with limited theoretical understanding of their relationships. Recent work by Kamath et al. (2021) revealed that even variants of IRM differ primarily in how they combine features, while Mehta (2025) established information-theoretic conditions under which certain methods achieve equivalent performance. However, no unified framework exists that explains when and why different approaches succeed or fail, limiting both theoretical progress and practical adoption.

### 2.2 Research Objectives

This research proposes **Compositional Invariance Learning (CIL)**, a hierarchical framework that unifies existing approaches to spurious correlation robustness through the lens of compositional structure. Our central hypothesis is that spurious correlations in real-world data exhibit compositional organization, and that explicitly modeling this structure enables both theoretical unification and practical performance improvements.

The specific objectives are:

1. **Develop a three-level hierarchical learning architecture** that decomposes invariance learning into feature-level primitives, module-level compositions, and model-level objectives.

2. **Demonstrate mathematical unification** by showing that IRM, Group DRO, and standard OOD objectives can be expressed as special cases within the compositional formalism through specific module weighting configurations.

3. **Achieve state-of-the-art performance** on the DomainBed benchmark while providing additional benefits including compositional transfer efficiency and improved worst-group accuracy.

4. **Characterize theoretical conditions** for compositional transfer, complementing existing static equivalence results with dynamic learning mechanisms.

### 2.3 Significance

This research addresses a critical gap at the intersection of causality, fairness, and robust machine learning. By providing a unifying framework, CIL offers several contributions:

**Theoretical Significance:** A compositional perspective reveals shared principles underlying apparently distinct methods, enabling principled method selection and combination. The framework provides sufficient conditions for when compositional decomposition improves robustness over monolithic approaches.

**Practical Significance:** Practitioners currently face a bewildering array of methods with limited guidance on selection. CIL provides a structured approach where learned primitives can be reused across tasks, reducing the need for method-specific expertise and improving efficiency.

**Community Impact:** By bridging causality, fairness, and OOD generalization communities, this work creates opportunities for cross-pollination of ideas and establishes common evaluation protocols, addressing the workshop's goal of forging collaborations and identifying best practices.

---

## 3. Methodology

### 3.1 Framework Architecture

The Compositional Invariance Learning framework operates through three hierarchical levels, each building upon the previous to enable flexible, robust learning.

#### 3.1.1 Level 1: Feature-Level Primitive Learning

The foundation of CIL is a set of $K$ learnable invariance primitives $\{\phi_k\}_{k=1}^K$, where each primitive $\phi_k: \mathcal{X} \rightarrow \mathbb{R}^d$ maps inputs to a $d$-dimensional representation capturing an atomic invariant pattern.

Primitives are learned through gradient-based invariance regularization. For input $x$ from environment $e \in \mathcal{E}_{train}$, we define the primitive learning objective:

$$\mathcal{L}_{primitive}(\phi_k) = \sum_{e \in \mathcal{E}_{train}} \mathcal{L}_{pred}^e(\phi_k) + \lambda_{inv} \cdot \mathcal{R}_{inv}(\phi_k)$$

where $\mathcal{L}_{pred}^e$ is the prediction loss in environment $e$ and $\mathcal{R}_{inv}$ is an invariance regularizer. We employ the gradient-based invariance penalty:

$$\mathcal{R}_{inv}(\phi_k) = \sum_{e \in \mathcal{E}_{train}} \left\| \nabla_{w} \mathcal{L}_{pred}^e(w \cdot \phi_k(x)) \big|_{w=1.0} \right\|^2$$

This encourages each primitive to capture features for which the optimal linear classifier is consistent across environments.

#### 3.1.2 Level 2: Module-Level Compositional Learning

The second level combines primitives into task-specific modules through differentiable selection. We define $M$ modules $\{m_j\}_{j=1}^M$, where each module $m_j$ is a weighted combination of primitives:

$$m_j(x) = \sum_{k=1}^K \alpha_{jk} \cdot \phi_k(x)$$

The selection weights $\alpha_{jk} \in [0,1]$ are learned through a hierarchical credit assignment mechanism adapted from Li et al. (2022). For each module, we maintain a selection policy $\pi_j$ that determines primitive utilization:

$$\alpha_{jk} = \frac{\exp(s_{jk} / \tau)}{\sum_{k'=1}^K \exp(s_{jk'} / \tau)}$$

where $s_{jk}$ are learnable scores and $\tau$ is a temperature parameter controlling selection sharpness.

The credit assignment update follows:

$$s_{jk} \leftarrow s_{jk} + \eta \cdot \delta_j \cdot \mathbb{I}[\phi_k \text{ selected}]$$

where $\delta_j$ is the temporal difference error for module $j$ and $\eta$ is the credit assignment learning rate.

#### 3.1.3 Level 3: Model-Level Multi-Objective Optimization

The final level combines modules to accommodate multiple community-specific objectives simultaneously. The model prediction is:

$$\hat{y} = f\left(\sum_{j=1}^M \beta_j \cdot m_j(x)\right)$$

where $f$ is a classifier head and $\beta_j$ are module importance weights.

The key insight enabling unification is that IRM, Group DRO, and ERM objectives can be expressed through different configurations of the compositional loss:

$$\mathcal{L}_{CIL} = \sum_{e \in \mathcal{E}} w_e \cdot \mathcal{L}_{pred}^e + \lambda_1 \cdot \mathcal{R}_{inv} + \lambda_2 \cdot \mathcal{R}_{group} + \lambda_3 \cdot \mathcal{R}_{comp}$$

where:
- **ERM:** $w_e = 1/|\mathcal{E}|$, $\lambda_1 = \lambda_2 = \lambda_3 = 0$
- **IRM:** $w_e = 1/|\mathcal{E}|$, $\lambda_1 > 0$, $\lambda_2 = \lambda_3 = 0$
- **Group DRO:** $w_e \propto \mathcal{L}_{pred}^e$ (adversarial), $\lambda_2 > 0$

The compositional regularizer $\mathcal{R}_{comp}$ encourages primitive reuse:

$$\mathcal{R}_{comp} = -\sum_{j=1}^M \sum_{k=1}^K \alpha_{jk} \log \alpha_{jk} + \gamma \cdot \|\{\alpha_{jk}\}_{j,k}\|_1$$

balancing diversity (entropy term) with sparsity ($\ell_1$ term).

### 3.2 Algorithm

The complete CIL training procedure is presented in Algorithm 1.

**Algorithm 1: Compositional Invariance Learning**

**Input:** Training data $\{(x_i, y_i, e_i)\}_{i=1}^N$, environments $\mathcal{E}_{train}$, hyperparameters $\lambda_1, \lambda_2, \lambda_3, \gamma, \tau, \eta$

**Initialize:** Primitives $\{\phi_k\}_{k=1}^K$, selection scores $\{s_{jk}\}$, classifier $f$

**For** epoch $= 1$ to $T$ **do:**

1. **Primitive Update Phase:**
   - For each primitive $\phi_k$:
     - Compute $\mathcal{L}_{primitive}(\phi_k)$ across all environments
     - Update $\phi_k \leftarrow \phi_k - \eta_\phi \nabla_{\phi_k} \mathcal{L}_{primitive}$

2. **Module Composition Phase:**
   - Compute selection weights $\alpha_{jk}$ via softmax
   - For each module $m_j$: compose $m_j(x) = \sum_k \alpha_{jk} \phi_k(x)$
   - Compute module-level losses and credit assignment errors $\delta_j$
   - Update selection scores: $s_{jk} \leftarrow s_{jk} + \eta \cdot \delta_j \cdot \alpha_{jk}$

3. **Model Optimization Phase:**
   - Compute unified loss $\mathcal{L}_{CIL}$
   - Update classifier $f$ and module weights $\beta_j$

**Output:** Trained model with primitives, modules, and classifier

### 3.3 Experimental Design

#### 3.3.1 Datasets

We evaluate on the DomainBed benchmark suite comprising five datasets with varying spurious correlation structures:

| Dataset | Domains | Classes | Images | Spurious Correlation Type |
|---------|---------|---------|--------|---------------------------|
| PACS | 4 | 7 | 9,991 | Artistic style |
| VLCS | 4 | 5 | 10,729 | Dataset bias |
| OfficeHome | 4 | 65 | 15,588 | Visual domain |
| TerraIncognita | 4 | 10 | 24,788 | Camera trap location |
| DomainNet | 6 | 345 | 586,575 | Rendering style |

#### 3.3.2 Baselines

We compare against methods from each community:
- **ERM:** Standard empirical risk minimization
- **IRM:** Invariant Risk Minimization (Arjovsky et al., 2019)
- **Group DRO:** Group Distributionally Robust Optimization (Sagawa et al., 2020)
- **SWAD:** Stochastic Weight Averaging Densely (Cha et al., 2021)
- **JTT:** Just Train Twice (Liu et al., 2021)

#### 3.3.3 Evaluation Protocol

Following DomainBed standards, we employ leave-one-domain-out cross-validation. For each dataset with $D$ domains, we train on $D-1$ domains and evaluate on the held-out domain, repeating for all domain choices.

**Metrics:**
1. **OOD Accuracy:** Classification accuracy on held-out test domain
2. **Worst-Group Accuracy:** Minimum accuracy across domain-class subgroups
3. **Compositional Transfer Efficiency:** Performance gain when transferring learned primitives to new domain combinations versus learning from scratch
4. **Expected Calibration Error (ECE):** Calibration quality on OOD test sets
5. **Training Time Ratio:** CIL training time relative to ERM baseline

#### 3.3.4 Statistical Analysis

- **Sample Size:** 20 runs per configuration (5 seeds × 4 hyperparameter samples)
- **Primary Test:** Paired t-test comparing CIL to each baseline
- **Significance Level:** $\alpha = 0.05$ with Bonferroni correction
- **Effect Size:** Cohen's d reported for all comparisons
- **Confidence Intervals:** 95% CI for all metrics

#### 3.3.5 Ablation Studies

To verify the causal mechanism, we conduct systematic ablations:

1. **Primitive Ablation:** Remove invariance regularization ($\lambda_1 = 0$) to test whether primitive learning contributes beyond standard features.

2. **Composition Ablation:** Replace differentiable selection with fixed uniform weights to test whether adaptive composition matters.

3. **Hierarchy Ablation:** Collapse to single-level (L=1) architecture to test whether hierarchical structure is necessary.

4. **Credit Assignment Ablation:** Replace hierarchical credit assignment with standard backpropagation to test the contribution of the cognitive-inspired mechanism.

### 3.4 Implementation Details

**Architecture:** ResNet-50 pretrained on ImageNet serves as the backbone. Primitives are implemented as parallel branches after the third residual block, each producing 256-dimensional representations. We use $K=16$ primitives and $M=4$ modules.

**Hyperparameters:** 
- Learning rates: $\eta_\phi = 5 \times 10^{-5}$ (primitives), $\eta = 10^{-3}$ (credit assignment)
- Regularization: $\lambda_1 \in \{0.1, 1.0, 10.0\}$, $\lambda_2 \in \{0.1, 1.0\}$, $\lambda_3 = 0.01$
- Temperature: $\tau = 0.5$
- Training: 5000 steps with batch size 32 per domain

**Computational Requirements:** Estimated 4-8 GPU-days on NVIDIA A100 for complete DomainBed evaluation.

---

## 4. Expected Outcomes & Impact

### 4.1 Expected Results

**Primary Outcome (P1):** We expect CIL to achieve OOD accuracy competitive with or exceeding SWAD (current SOTA) across DomainBed datasets, targeting $\geq 66.9\%$ average accuracy. The compositional structure should provide particular advantages on datasets with multi-level spurious correlations (PACS, OfficeHome).

**Secondary Outcomes:**
- **P2 (Transfer Efficiency):** 2-5% improvement when reusing primitives on novel domain combinations, demonstrating the value of compositional decomposition.
- **P3 (Unification):** Mathematical derivation showing IRM, Group DRO, and ERM as special cases of the CIL formalism.
- **P4 (Scalability):** Training time within 2× of ERM, confirming practical tractability.
- **P5 (Complementarity):** Improved performance when combining CIL with existing theoretical frameworks.

### 4.2 Falsification Criteria

The hypothesis will be rejected if:
1. OOD accuracy is statistically worse than ERM baseline on majority of datasets
2. Learned primitives show no cross-domain reusability in transfer experiments
3. Fewer than two community methods can be expressed within the formalism
4. Training time exceeds 5× ERM baseline

### 4.3 Broader Impact

**Theoretical Contributions:** CIL provides a unifying lens through which to understand the relationship between causality-inspired, fairness-motivated, and robustness-focused approaches. By revealing compositional structure as a shared principle, this work opens avenues for principled method combination and theoretical analysis.

**Practical Applications:** The framework offers practitioners a structured approach to building robust models without requiring expertise in multiple specialized methods. Learned primitives can be shared across tasks, reducing development costs and improving reproducibility.

**Community Building:** By bridging distinct research communities, this work addresses the workshop's core mission of forging collaborations. The unified framework provides common vocabulary and evaluation protocols, facilitating knowledge transfer and identifying complementary strengths of different approaches.

**Limitations and Future Work:** Current validation is limited to computer vision; extending to NLP and other modalities requires adaptation. The framework assumes access to environment labels during training, which may not always be available. Future work should explore unsupervised environment discovery and scaling to larger datasets.

### 4.4 Conclusion

Compositional Invariance Learning offers a principled framework for understanding and addressing spurious correlations by leveraging the compositional structure inherent in real-world data. Through hierarchical decomposition into primitives, modules, and objectives, CIL unifies approaches from causality, fairness, and robust ML while achieving competitive empirical performance. This work contributes both theoretical insight and practical tools for building machine learning systems that generalize reliably beyond their training distributions.