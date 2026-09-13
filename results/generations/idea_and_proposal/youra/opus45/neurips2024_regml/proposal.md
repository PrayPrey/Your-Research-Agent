# Research Proposal: Certified Unlearning Verification via Multi-Attack Ensemble for GDPR Compliance

## 1. Introduction

### 1.1 Background

The General Data Protection Regulation (GDPR), enacted by the European Union in 2018, fundamentally transformed the landscape of data privacy rights. Article 17, commonly known as the "right to be forgotten" or "right to erasure," grants individuals the right to request deletion of their personal data from organizations' systems. While this regulation was designed primarily with traditional databases in mind, its implications for machine learning systems present unprecedented technical challenges. Unlike conventional data storage where deletion is straightforward, machine learning models encode information about training data within their parameters in complex, distributed ways that resist simple removal.

Machine unlearning has emerged as a research field dedicated to addressing this challenge, developing methods to remove the influence of specific training samples from trained models without complete retraining. Approaches range from exact unlearning methods that provide mathematical guarantees but require expensive retraining, to approximate methods that efficiently modify model parameters but offer weaker guarantees. However, a critical gap remains: **how can we verify that unlearning has actually occurred?**

Current verification approaches predominantly rely on single attack types, particularly Membership Inference Attacks (MIA), which attempt to determine whether a specific sample was used in training. While MIA provides valuable insights, it captures only one dimension of potential information leakage. Models may retain information about forgotten data through other channels—reconstructable features (vulnerable to model inversion attacks) or inferable attributes (vulnerable to attribute inference attacks)—that single-attack verification fails to detect. This limitation creates a significant gap between regulatory requirements for complete data deletion and the technical capabilities for verification.

### 1.2 Research Objectives

This research proposes **Certified Unlearning Verification (CUV)**, a comprehensive framework that addresses the verification gap through three primary objectives:

1. **Develop a multi-attack ensemble verification framework** that combines membership inference, model inversion, and attribute inference attacks to provide comprehensive coverage of potential information retention channels in unlearned models.

2. **Establish statistical certification criteria** based on indistinguishability testing that can provide quantifiable compliance certificates suitable for regulatory auditing, bridging probabilistic machine learning guarantees with legal requirements.

3. **Validate architecture-independent calibration** using ACMIA (Automatic Calibration for Membership Inference Attacks) methodology to ensure consistent verification thresholds across diverse model architectures, enabling practical deployment in heterogeneous MLaaS environments.

### 1.3 Significance

This research addresses a critical intersection of machine learning, privacy, and regulatory compliance. The significance is threefold:

**Regulatory Impact:** As GDPR enforcement intensifies and similar regulations emerge globally (CCPA in California, LGPD in Brazil, PIPL in China), ML service providers face increasing legal uncertainty regarding compliance with deletion requests. CUV provides a practical pathway to demonstrable compliance through quantifiable certificates.

**Technical Advancement:** By synthesizing insights from multiple attack paradigms and establishing statistical certification criteria, CUV advances the theoretical foundations of machine unlearning verification beyond current single-attack approaches.

**Practical Utility:** The black-box nature of CUV enables third-party auditing without requiring model access, supporting the emerging ecosystem of AI auditing services and regulatory bodies that need to verify compliance without accessing proprietary model architectures.

## 2. Methodology

### 2.1 Framework Overview

The Certified Unlearning Verification (CUV) framework operates through four sequential phases: (1) Attack Ensemble Construction, (2) Threshold Calibration, (3) Statistical Verification, and (4) Certificate Generation. We detail each phase below.

### 2.2 Attack Ensemble Construction

The multi-attack ensemble comprises three complementary attack types, each targeting distinct information retention channels:

**Membership Inference Attack (MIA):** Given a target model $f_\theta$ and a sample $x$, MIA determines whether $x \in D_{train}$. We employ the likelihood ratio attack:

$$\text{MIA}(x, y) = \mathbb{1}\left[\frac{P(f_\theta(x) | x \in D_{train})}{P(f_\theta(x) | x \notin D_{train})} > \tau_{MIA}\right]$$

where $f_\theta(x)$ represents the model's output distribution and $\tau_{MIA}$ is the calibrated threshold.

**Model Inversion Attack (MI):** MI attempts to reconstruct training samples from model outputs. For a target class $c$, the attack solves:

$$\hat{x}_c = \arg\max_x \log P(c | x; f_\theta) - \lambda \cdot R(x)$$

where $R(x)$ is a regularization term enforcing realistic reconstructions. Verification measures reconstruction quality using:

$$\text{MI\_Score}(x, \hat{x}) = \text{SSIM}(x, \hat{x}) + \alpha \cdot \text{FID}(x, \hat{x})$$

**Attribute Inference Attack (AI):** AI infers sensitive attributes $a$ not directly predicted by the model. Given auxiliary knowledge $x_{aux}$ and model outputs:

$$\text{AI}(x_{aux}, f_\theta(x)) = \arg\max_a P(a | x_{aux}, f_\theta(x); \phi)$$

where $\phi$ parameterizes the attack model trained on shadow data.

### 2.3 ACMIA-Based Threshold Calibration

To achieve architecture independence, we employ Automatic Calibration for Membership Inference Attacks (ACMIA) with temperature scaling. For each attack type $k \in \{MIA, MI, AI\}$:

**Step 1: Shadow Model Training.** Train $M$ shadow models $\{f^{(m)}\}_{m=1}^M$ on disjoint subsets of calibration data $D_{cal}$.

**Step 2: Attack Distribution Estimation.** For each shadow model, compute attack scores on member and non-member samples:

$$S^{(m)}_{in} = \{s_k(x) : x \in D^{(m)}_{train}\}, \quad S^{(m)}_{out} = \{s_k(x) : x \notin D^{(m)}_{train}\}$$

**Step 3: Temperature Calibration.** Learn temperature parameter $T_k$ minimizing calibration error:

$$T_k^* = \arg\min_T \text{ECE}\left(\sigma\left(\frac{s_k(x)}{T}\right), y_{member}\right)$$

where ECE is Expected Calibration Error.

**Step 4: Threshold Selection.** Set threshold $\tau_k$ such that attack accuracy on calibration data equals $50\% + \epsilon$:

$$\tau_k = \text{Quantile}_{1-\epsilon}\left(\bigcup_{m=1}^M S^{(m)}_{out}\right)$$

### 2.4 Statistical Verification Protocol

Given an unlearned model $f_{\theta'}$ and forget set $D_f = \{(x_i, y_i)\}_{i=1}^n$, verification proceeds as:

**Step 1: Attack Execution.** For each attack $k$ and sample $x_i \in D_f$:

$$a_{k,i} = \mathbb{1}[\text{Attack}_k(x_i, f_{\theta'}) > \tau_k]$$

**Step 2: Accuracy Computation.** Compute per-attack accuracy:

$$\text{Acc}_k = \frac{1}{n}\sum_{i=1}^n a_{k,i}$$

**Step 3: Statistical Testing.** For each attack, test $H_0: \text{Acc}_k = 0.5$ against $H_1: \text{Acc}_k > 0.5$:

$$t_k = \frac{\text{Acc}_k - 0.5}{\sqrt{\frac{0.5 \times 0.5}{n}}}$$

Apply Bonferroni correction: reject $H_0$ if $p_k < \alpha/3$ where $\alpha = 0.05$.

**Step 4: Aggregate Decision.** Certification passes if and only if:

$$\forall k \in \{MIA, MI, AI\}: \text{Acc}_k \leq 0.55 \text{ AND } p_k \geq 0.0167$$

### 2.5 Certificate Generation

Upon successful verification, CUV generates a compliance certificate containing:

$$\mathcal{C} = \langle H(f_{\theta'}), H(D_f), \{\text{Acc}_k, \text{CI}_k, p_k\}_{k}, \text{timestamp}, \text{version} \rangle$$

where $H(\cdot)$ denotes cryptographic hash, $\text{CI}_k$ is the 95% confidence interval for attack $k$.

### 2.6 Experimental Design

**Datasets:** We evaluate on standard benchmarks: CIFAR-10, CIFAR-100, ImageNet-subset (100 classes), and CelebA (for attribute inference with sensitive attributes).

**Model Architectures:** To validate architecture independence, we test across: MLP (3-layer), CNN (VGG-16), ResNet-18, LSTM (for sequential data), and Vision Transformer (ViT-B/16).

**Unlearning Methods:** We evaluate multiple unlearning approaches:
- Exact retraining (gold standard)
- SISA (Sharded, Isolated, Sliced, and Aggregated training)
- Gradient-based approximate unlearning
- Fisher forgetting
- Intentionally incomplete unlearning (for detection validation)

**Experimental Conditions:**

| Condition | Forget Set Size | Expected Outcome |
|-----------|-----------------|------------------|
| Complete Unlearning | 100, 500, 1000 | Certification PASS |
| Partial Unlearning (50%) | 100, 500, 1000 | Certification FAIL |
| No Unlearning | 100, 500, 1000 | Certification FAIL |
| Retrained Model | 100, 500, 1000 | Certification PASS |

**Evaluation Metrics:**

1. **Certification Accuracy:** Proportion of correctly classified cases (true positives + true negatives).

2. **Detection Rate Improvement:** Percentage of incomplete unlearning cases detected by multi-attack ensemble but missed by single-attack (MIA-only):

$$\Delta_{detect} = \frac{|\text{Detected}_{ensemble}| - |\text{Detected}_{MIA}|}{|\text{Total Incomplete}|} \times 100\%$$

3. **Architecture Variance:** Standard deviation of calibrated thresholds across architectures:

$$\sigma_{arch} = \text{Std}(\{\tau_k^{(a)}\}_{a \in \text{Architectures}})$$

4. **Computational Overhead:** Time and query complexity relative to single-attack verification.

**Statistical Analysis:** All experiments repeated with 5 random seeds. Results reported as mean ± standard deviation with 95% confidence intervals. Significance testing via paired t-tests with Bonferroni correction.

## 3. Expected Outcomes & Impact

### 3.1 Expected Outcomes

**Primary Outcome (P1):** We expect CUV to achieve certification accuracy exceeding 95% on complete unlearning scenarios while maintaining false positive rate below 5% on incomplete unlearning cases. Specifically, when unlearning is complete (verified against retrained baseline), all three attacks should achieve accuracy within $50\% \pm 5\%$ with $p \geq 0.0167$.

**Secondary Outcome (P2):** Multi-attack ensemble verification is expected to detect at least 15% more incomplete unlearning cases than single-attack (MIA-only) approaches. This improvement stems from capturing information leakage through model inversion (reconstructable features) and attribute inference (inferable sensitive attributes) channels that MIA alone misses.

**Tertiary Outcome (P3):** With ACMIA calibration, threshold variance across the five tested architectures should remain below 3%, demonstrating practical architecture independence. This enables deployment of a single calibrated CUV instance across heterogeneous MLaaS environments.

### 3.2 Theoretical Contributions

CUV advances the theoretical understanding of machine unlearning verification by:

1. **Formalizing multi-channel information retention:** Establishing that complete unlearning requires indistinguishability across multiple attack vectors, not just membership inference.

2. **Bridging probabilistic and legal guarantees:** Providing a framework for translating statistical indistinguishability into actionable compliance certificates that satisfy regulatory requirements.

3. **Quantifying verification completeness:** Introducing metrics for measuring the comprehensiveness of unlearning verification beyond binary pass/fail outcomes.

### 3.3 Practical Impact

**For ML Service Providers:** CUV provides a practical pathway to GDPR Article 17 compliance with quantifiable certificates. Providers can demonstrate due diligence in responding to deletion requests, reducing legal liability and building user trust.

**For Regulatory Bodies:** The black-box nature of CUV enables third-party auditing without requiring access to proprietary model architectures. Regulators can verify compliance claims independently, strengthening enforcement capabilities.

**For Users:** CUV empowers data subjects with meaningful verification of their deletion rights. Rather than trusting provider claims, users can request or access independent certification of data removal.

**For the Research Community:** By establishing standardized verification protocols and benchmarks, CUV facilitates reproducible research in machine unlearning and enables meaningful comparison of unlearning methods based on verifiable outcomes.

### 3.4 Limitations and Future Directions

We acknowledge several limitations that define future research directions:

1. **Generative Models:** CUV's current design targets classification models. Extending to large language models and diffusion models requires incorporating memorization extraction attacks and adapting statistical tests for generative outputs.

2. **Single-Sample Verification:** Statistical power requires batch aggregation ($n \geq 30$). Future work should develop protocols for single-sample deletion verification, potentially through synthetic neighbor generation.

3. **Legal Acceptance:** While CUV provides probabilistic guarantees, legal acceptance of statistical certificates remains untested. Collaboration with legal scholars and regulatory bodies is essential for practical deployment.

4. **Adversarial Robustness:** Sophisticated unlearning methods might specifically target passing CUV verification while retaining information through channels not covered by the attack ensemble. Continuous expansion of the attack suite is necessary.

### 3.5 Conclusion

This research proposes Certified Unlearning Verification (CUV), a comprehensive framework addressing the critical gap between GDPR's right to be forgotten and technical verification capabilities. By combining multi-attack ensemble verification with statistical certification criteria and architecture-independent calibration, CUV provides a practical pathway to demonstrable compliance with data deletion regulations. The expected outcomes—improved detection of incomplete unlearning, architecture independence, and quantifiable compliance certificates—position CUV as a foundational contribution to the emerging field of regulatable machine learning, bridging the gap between algorithmic capabilities and regulatory requirements.