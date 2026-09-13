# Research Proposal: Bridging the CRL Theory-Practice Gap through Automated Deployment Framework for Medical Imaging Domain Experts

## 1. Title

**Automated Causal Representation Learning Deployment Framework with Identifiability Verification: Enabling Master's-Level Medical Imaging Experts to Deploy Causally Sound Models**

## 2. Introduction

### 2.1 Background

Causal Representation Learning (CRL) represents a paradigm shift in machine learning by integrating causal inference principles with representation learning to discover high-level causal variables and their relationships from raw, unstructured data. Unlike traditional deep learning systems that rely solely on statistical correlations, CRL methods promise models that can reason about interventions, generalize across domains, and provide interpretable causal explanations—capabilities critical for high-stakes applications like medical imaging where clinical confounding, multi-site biases, and domain shifts plague diagnostic systems.

Recent theoretical advances have established identifiability conditions under which causal variables can be recovered from observational data. Schölkopf et al. (2021) formalized CRL as discovering high-level causal variables from low-level observations (e.g., RGB pixels), while Moran & Aragam (2025) introduced statistical frameworks for verifying identifiability conditions in deep generative models. In medical imaging, these advances have demonstrated practical value: cheng-01037's work on causality-based domain generalization achieved robust cross-hospital performance by explicitly modeling clinical confounders and site-specific biases.

However, a critical theory-practice gap prevents widespread CRL adoption in medical imaging and other high-impact domains. Deploying CRL methods requires PhD-level expertise in causal inference theory—understanding structural causal models (SCMs), identifiability proofs, interventional assumptions, and complex mathematical frameworks. Medical imaging domain experts (radiologists, clinical researchers, medical imaging scientists) possess deep knowledge of clinical problems, data characteristics, and domain-specific confounders, but typically lack the specialized causality training needed to implement CRL solutions. This expertise barrier creates a paradox: those who best understand the problems CRL could solve cannot access the tools, while CRL researchers lack the domain knowledge to identify appropriate applications.

Current solutions are inadequate. Generic AutoML frameworks (AutoKeras, Auto-sklearn) optimize predictive performance without causal guarantees, potentially learning spurious correlations that fail under distribution shift. Existing CRL libraries (py-why/causal-learn) provide general causal discovery algorithms but lack deployment-focused interfaces and domain-specific guidance. Manual CRL implementation requires 12-16 hours per model and deep theoretical knowledge, achieving <30% success rates for practitioners without PhD-level causality training.

### 2.2 Research Objectives

This research aims to bridge the CRL theory-practice gap through a novel two-tier automated deployment framework that enables Master's-level medical imaging domain experts to deploy causally sound models while maintaining theoretical rigor. Our specific objectives are:

**Primary Objective**: Design and validate a CRL deployment framework that reduces expertise barriers by 60% (measured by time and required education level) while preserving identifiability guarantees through automated verification.

**Secondary Objectives**:
1. Develop a novice-tier template-based interface enabling ≥70% deployment success within 4 hours for Master's-level users (vs. <30% baseline)
2. Implement automated identifiability verification achieving ≥90% precision and ≥85% recall in detecting causal assumption violations
3. Demonstrate model quality maintenance within 2% accuracy of manual CRL implementations across three medical imaging benchmarks
4. Create domain-specific template library encoding validated medical imaging CRL patterns (clinical confounding removal, multi-site generalization)
5. Validate framework generalizability through user study with N=10 medical imaging domain experts

### 2.3 Research Hypothesis

**Main Hypothesis**: If medical imaging domain experts (Master's-level education, 2+ years clinical experience) are provided with a two-tier CRL deployment framework comprising (1) novice-tier YAML-template-based automatic causal discovery with human-readable explanations, (2) expert-tier full architecture control with identifiability analysis tools, and (3) automated causal verification module implementing Moran & Aragam's (2025) statistical identifiability framework, then they will successfully deploy causal representation learning models for clinical confounding and multi-site generalization tasks with ≥70% completion rate within 4 hours (vs. <30% for manual PhD-level deployment), while maintaining model accuracy within 2% of manual CRL implementations on medical imaging benchmarks (ISIC skin lesion, ChestX-ray14, BraTS brain tumor datasets), thereby bridging the theory-practice gap in CRL applications by reducing deployment barriers by 60% (time + expertise) without compromising theoretical guarantees.

**Core Innovation**: Automated identifiability verification acts as a "safety net"—users interact with simplified interfaces (novice tier) or full architecture control (expert tier), while statistical identifiability tests automatically flag causal assumption violations *before* training, preserving theoretical rigor despite accessibility layers.

### 2.4 Significance

This research addresses a critical bottleneck in translating CRL theory to real-world impact. By enabling domain experts to deploy CRL methods without PhD-level causality training, we unlock applications in medical imaging where causal reasoning is essential but expertise is scarce:

**Scientific Significance**:
- First formalization of the accessibility-theoretical rigor trade-off in CRL deployment
- Novel abstraction-verification duality framework proving that template-based deployment preserves identifiability conditions when coupled with automated verification
- Demonstration that Master's-level domain experts with automated verification can achieve equivalent causal correctness to PhD-level manual implementation

**Practical Significance**:
- Enables 5-10× more practitioners to use CRL in medical imaging (Master's-level medical imaging researchers >> PhD-level CRL experts)
- Reduces diagnostic biases in clinical decision support systems (e.g., skin lesion classification biased by patient demographics)
- Improves multi-hospital model generalization (e.g., rural vs. urban hospital X-ray protocols)
- Accelerates CRL adoption in high-impact healthcare applications

**Broader Impact**:
- Template expansion pathway to robotics (BISCUIT pattern) and biology (scMultiomeGRN pattern) validated via supplementary evidence
- Foundation for "Causal Accessibility Guidelines" (CAG) analogous to WCAG 2.1 web accessibility standards
- Demonstration that complex theoretical frameworks can be made accessible without sacrificing correctness through principled automated verification

## 3. Methodology

### 3.1 Framework Architecture

Our two-tier CRL deployment framework consists of three integrated components: (1) Novice-Tier Template Interface, (2) Expert-Tier Full Control Interface, and (3) Automated Identifiability Verification Module.

#### 3.1.1 Novice-Tier Template Interface

**Design Philosophy**: Separate domain expertise (medical knowledge) from causal inference expertise (identifiability theory) through declarative YAML-based specification.

**Input Specification**:
Users provide three components via YAML configuration:
```yaml
task:
  type: "clinical_confounding_removal"  # or "multi_site_generalization"
  dataset: "ISIC_skin_lesion"
  target: "melanoma_classification"
  
confounders:
  observed: ["age", "sex", "lesion_location"]
  suspected_unobserved: ["genetic_factors"]
  
environments:
  - hospital_A
  - hospital_B
  - hospital_C
```

**Template Library Architecture**:
We encode validated CRL patterns from cheng-01037 as reusable templates:

**Template 1: Clinical Confounding Removal**
- **Causal Structure**: $Z \rightarrow X \leftarrow C$, where $Z$ = causal latent variables (disease state), $X$ = observed images, $C$ = clinical confounders (age, sex)
- **Architecture**: Encoder $f_\theta: X \rightarrow Z$, Decoder $g_\phi: Z \rightarrow X$, Confounder Predictor $h_\psi: Z \rightarrow C$
- **Loss Function**: 
$$\mathcal{L} = \mathcal{L}_{\text{recon}}(X, g_\phi(f_\theta(X))) + \lambda_1 \mathcal{L}_{\text{inv}}(C, h_\psi(f_\theta(X))) + \lambda_2 \mathcal{L}_{\text{ind}}(Z, C)$$
where $\mathcal{L}_{\text{inv}}$ enforces invariance to confounders and $\mathcal{L}_{\text{ind}}$ promotes independence between $Z$ and $C$.

**Template 2: Multi-Site Generalization**
- **Causal Structure**: $Z \rightarrow X$, $S \rightarrow X$ (site-specific spurious correlations), where $S$ = site indicator
- **Architecture**: Shared encoder $f_\theta$, site-specific decoders $\{g_{\phi_s}\}_{s=1}^{S}$
- **Loss Function**:
$$\mathcal{L} = \sum_{s=1}^{S} \mathcal{L}_{\text{recon}}^{(s)}(X^{(s)}, g_{\phi_s}(f_\theta(X^{(s)}))) + \lambda \mathcal{L}_{\text{align}}(\{f_\theta(X^{(s)})\}_{s=1}^{S})$$
where $\mathcal{L}_{\text{align}}$ enforces alignment of latent distributions across sites.

**Human-Readable Explanation Generation**:
For each template instantiation, the system generates natural language explanations:
- **Causal Graph Visualization**: Interactive DAG with medical terminology labels
- **Assumption Documentation**: "This model assumes age and sex affect lesion appearance but not the underlying disease state. Violation: If age directly causes melanoma (not just appearance), identifiability may fail."
- **Intervention Semantics**: "Changing hospital site should not affect predicted disease state, only image appearance characteristics."

#### 3.1.2 Expert-Tier Full Control Interface

**Design Philosophy**: Provide escape hatch for custom CRL architectures while maintaining automated verification safety net.

**Capabilities**:
1. **Manual Causal Model Specification**: Define custom SCMs with arbitrary functional forms
2. **Architecture Customization**: Implement novel encoder/decoder architectures beyond templates
3. **Identifiability Analysis Tools**:
   - Sensitivity testing: Vary environment count, functional form assumptions
   - Assumption relaxation: Test robustness to partial identifiability
   - Counterfactual exploration: Simulate interventions on causal graph

**Example Expert-Tier Workflow**:
```python
# Define custom SCM
scm = CausalModel()
scm.add_variable("Z", parents=[], functional_form="nonlinear")
scm.add_variable("C", parents=[], functional_form="linear")
scm.add_variable("X", parents=["Z", "C"], functional_form="nonlinear")

# Specify identifiability assumptions
assumptions = {
    "sufficient_environments": 3,
    "functional_form": "additive_noise",
    "unobserved_confounding": False
}

# Run identifiability analysis
analysis = verify_identifiability(scm, assumptions, data)
if not analysis.is_identifiable:
    print(f"Violation: {analysis.violation_reason}")
    print(f"Suggested fix: {analysis.suggested_fix}")
```

#### 3.1.3 Automated Identifiability Verification Module

**Theoretical Foundation**: Implements Moran & Aragam (2025) statistical identifiability framework with three core tests.

**Test 1: Sufficient Environment Diversity**

For multi-environment identifiability, we require data from $K \geq 2$ distinct environments. The test statistic measures distributional diversity:

$$T_{\text{env}} = \frac{1}{K(K-1)} \sum_{i \neq j} \text{MMD}^2(\mathcal{P}_i, \mathcal{P}_j)$$

where $\text{MMD}$ is Maximum Mean Discrepancy between environment distributions $\mathcal{P}_i, \mathcal{P}_j$. We reject insufficient diversity if $T_{\text{env}} < \tau_{\text{env}}$ (threshold calibrated via bootstrap).

**Test 2: Functional Form Constraints**

For linear identifiability, we test whether learned representations satisfy linearity assumptions:

$$T_{\text{lin}} = \mathbb{E}_{x_1, x_2, \alpha} \left[ \| f_\theta(\alpha x_1 + (1-\alpha) x_2) - (\alpha f_\theta(x_1) + (1-\alpha) f_\theta(x_2)) \|^2 \right]$$

Reject linearity assumption if $T_{\text{lin}} > \tau_{\text{lin}}$.

**Test 3: Unobserved Confounding Detection**

Using proximal causal inference framework, we test for unobserved confounders $U$ affecting both treatment $Z$ and outcome $Y$:

$$T_{\text{conf}} = \sup_{g \in \mathcal{G}} \left| \mathbb{E}[g(Z, W) \cdot (Y - \mathbb{E}[Y|Z, W])] \right|$$

where $W$ are proxy variables. Reject no-confounding assumption if $T_{\text{conf}} > \tau_{\text{conf}}$.

**Uncertainty Quantification**:
Following Tayal et al. (2025), we use conformal prediction to provide confidence intervals for test statistics:

$$\text{CI}_{1-\alpha}(T) = \left[ \hat{T} - q_{1-\alpha/2}(\{\hat{T}_b\}_{b=1}^{B}), \hat{T} + q_{1-\alpha/2}(\{\hat{T}_b\}_{b=1}^{B}) \right]$$

where $\{\hat{T}_b\}$ are bootstrap resamples and $q_{1-\alpha/2}$ is the $(1-\alpha/2)$-quantile.

**Violation Reporting**:
When violations are detected, the system generates actionable reports:
- **Violation Type**: "Insufficient environment diversity detected"
- **Evidence**: "$T_{\text{env}} = 0.12 < \tau_{\text{env}} = 0.25$ (95% CI: [0.08, 0.16])"
- **Impact**: "Multi-environment identifiability requires $K \geq 3$ sufficiently diverse environments. Current data has only 2 effective environments."
- **Suggested Fix**: "Collect data from additional hospital sites OR relax to single-environment identifiability with stronger functional form assumptions"

### 3.2 Data Collection

#### 3.2.1 Medical Imaging Benchmarks

We evaluate on three public medical imaging datasets representing diverse clinical confounding and multi-site generalization scenarios:

**Dataset 1: ISIC Skin Lesion Classification**
- **Task**: Binary melanoma classification
- **Size**: 25,331 dermoscopic images
- **Confounders**: Age (continuous), sex (binary), lesion location (categorical: 7 body sites)
- **Environments**: 3 data collection sites (Hospital for Skin Diseases Barcelona, Medical University of Vienna, Memorial Sloan Kettering Cancer Center)
- **Ground Truth**: Histopathology-confirmed diagnoses
- **CRL Challenge**: Age and sex correlate with melanoma prevalence but also affect lesion appearance (e.g., older patients have more sun damage), creating confounding

**Dataset 2: ChestX-ray14 Multi-Label Diagnosis**
- **Task**: Multi-label classification (14 thoracic diseases)
- **Size**: 112,120 frontal-view X-ray images
- **Confounders**: Patient age, imaging protocol (AP vs. PA view)
- **Environments**: 2 hospital systems with different X-ray equipment manufacturers
- **Ground Truth**: NLP-extracted labels from radiology reports
- **CRL Challenge**: Equipment-specific artifacts (e.g., different scatter patterns) create site-specific spurious correlations

**Dataset 3: BraTS Brain Tumor Segmentation**
- **Task**: Semantic segmentation (tumor core, enhancing tumor, whole tumor)
- **Size**: 484 multi-modal MRI scans (T1, T1ce, T2, FLAIR)
- **Confounders**: Scanner manufacturer (Siemens, GE, Philips), magnetic field strength (1.5T vs. 3T)
- **Environments**: 19 institutions with different MRI protocols
- **Ground Truth**: Expert manual segmentations
- **CRL Challenge**: Scanner-specific intensity distributions and artifacts require domain-invariant representations

#### 3.2.2 Data Preprocessing

**Standardization Pipeline**:
1. **Image Normalization**: Resize to 224×224, normalize to [0,1] range
2. **Confounder Encoding**: One-hot encoding for categorical variables, standardization for continuous variables
3. **Train/Validation/Test Split**: 60%/20%/20% stratified by environment and target label
4. **Environment Balancing**: Ensure each environment has ≥500 samples for identifiability testing

**Synthetic Identifiability Violation Injection**:
For verification accuracy testing (Prediction 2), we create 10 synthetic datasets with known violations:
- **Violation 1-3**: Single-environment data (violates multi-environment identifiability)
- **Violation 4-6**: Unobserved confounding (inject latent variable affecting both $Z$ and $Y$)
- **Violation 7-10**: Incorrect functional forms (nonlinear data with linear identifiability assumption)

### 3.3 Experimental Design

#### 3.3.1 User Study Protocol

**Study Design**: Mixed between-subjects (tier assignment) and within-subjects (benchmark tasks) design.

**Participants**:
- **Sample Size**: N=10 medical imaging domain experts
- **Inclusion Criteria**:
  - Master's or PhD degree in medical imaging, radiology, or related field
  - ≥2 years experience with medical imaging data analysis
  - Proficiency in Python programming
  - No prior CRL implementation experience (verified via pre-study survey)
- **Recruitment**: Medical imaging research labs, clinical radiology departments, professional societies (RSNA, MICCAI)
- **Compensation**: $200 for 4-8 hour study session

**Group Assignment**:
- **Novice-Tier Group**: N=5 Master's-level participants
- **Expert-Tier Group**: N=3 PhD-level participants
- **Baseline Group**: N=2 PhD-level participants (manual CRL deployment, no framework)

**Study Procedure**:

**Phase 1: Training (30 minutes)**
- Framework overview presentation
- Tutorial on YAML template specification (novice-tier) or SCM definition (expert-tier)
- Practice task on toy dataset (not measured)

**Phase 2: Deployment Tasks (4 hours maximum)**

Each participant completes three tasks (within-subjects):
1. **Task A**: ISIC skin lesion classification with clinical confounding template
2. **Task B**: ChestX-ray14 diagnosis with multi-site generalization template
3. **Task C**: BraTS brain tumor segmentation with domain robustness template

**Task Workflow**:
1. Load dataset and explore data characteristics (15 min)
2. Select/configure CRL template via YAML or manual SCM (30 min)
3. Review automated identifiability verification report (15 min)
4. Train model with framework-generated code (60 min)
5. Evaluate on hold-out test set (15 min)
6. Complete post-task survey (10 min)

**Phase 3: Post-Study Interview (30 minutes)**
- Semi-structured interview on usability, trust in verification, perceived complexity
- Suggestions for template library expansion
- Comparison to prior ML deployment experiences

**Data Collection**:
- **Quantitative**: Timestamp logs (start/completion times), binary success/failure, model accuracy metrics, verification flags
- **Qualitative**: Screen recordings, think-aloud protocols, post-task surveys (5-point Likert scales), interview transcripts

#### 3.3.2 Baseline Comparisons

**Baseline 1: Manual CRL Deployment**
- **Method**: Provide participants with cheng-01037 GitHub repository and documentation
- **Measurement**: Time to successful deployment, success rate
- **Expected Performance**: 12-16 hours, <30% success for Master's-level users

**Baseline 2: Generic AutoML**
- **Method**: Use AutoKeras with same datasets
- **Measurement**: Model accuracy, deployment time
- **Expected Performance**: Faster deployment (1-2 hours) but no causal guarantees, potential accuracy degradation under distribution shift

**Baseline 3: Existing CRL Library (py-why/causal-learn)**
- **Method**: Provide py-why documentation and ask participants to implement CRL pipeline
- **Measurement**: Success rate, time to deployment
- **Expected Performance**: Similar to manual deployment (requires deep causality knowledge)

### 3.4 Evaluation Metrics

#### 3.4.1 Primary Metrics

**Metric 1: Deployment Success Rate**

$$\text{Success Rate} = \frac{\text{Number of participants completing deployment within 4 hours}}{\text{Total participants}} \times 100\%$$

**Success Criteria**: 
- Model trains without errors
- Achieves ≥60% of baseline accuracy on validation set
- Passes automated identifiability verification (or explicitly acknowledges violations)

**Target**: ≥70% for novice-tier group

**Metric 2: Time-to-Deployment**

$$T_{\text{deploy}} = T_{\text{completion}} - T_{\text{start}}$$

Measured in hours from task start to validated model output.

**Target**: Median ≤4 hours for novice-tier group

**Metric 3: Model Accuracy**

Task-specific metrics:
- **ISIC**: Area Under ROC Curve (AUC) for binary melanoma classification
- **ChestX-ray14**: Macro-averaged F1 score for 14-class multi-label classification
- **BraTS**: Dice coefficient for tumor segmentation

**Target**: Within 2% absolute difference of manual CRL baselines:
- ISIC: AUC ≥ 0.85 (baseline: 0.87)
- ChestX-ray14: F1 ≥ 0.78 (baseline: 0.80)
- BraTS: Dice ≥ 0.88 (baseline: 0.90)

#### 3.4.2 Secondary Metrics

**Metric 4: Verification Accuracy**

$$\text{Precision} = \frac{TP}{TP + FP}, \quad \text{Recall} = \frac{TP}{TP + FN}$$

where TP = true positive violations detected, FP = false positive flags, FN = missed violations.

**Measurement**: Compare automated checker flags against ground truth (synthetic violations) and independent expert review (2 CRL researchers).

**Target**: Precision ≥90%, Recall ≥85%

**Metric 5: Expertise Level Required**

$$\text{Expertise Gap} = \text{Success Rate}_{\text{Master's}} - \text{Success Rate}_{\text{PhD}}$$

**Target**: Gap ≤15% (demonstrating framework reduces expertise barrier)

**Metric 6: Usability (System Usability Scale)**

Standard 10-item SUS questionnaire (Likert scale 1-5):
- "I think I would like to use this framework frequently"
- "I found the framework unnecessarily complex" (reverse scored)
- "I thought the framework was easy to use"
- ... (7 additional items)

$$\text{SUS Score} = \sum_{i=1}^{10} \text{Item}_i \times 2.5$$

**Target**: SUS ≥70 (above average usability)

### 3.5 Statistical Analysis

#### 3.5.1 Hypothesis Testing

**Test 1: Deployment Success Rate (Prediction P1)**

**Null Hypothesis**: $H_0: p_{\text{success}} = 0.70$
**Alternative Hypothesis**: $H_1: p_{\text{success}} > 0.70$

**Test**: One-proportion z-test
$$z = \frac{\hat{p} - p_0}{\sqrt{p_0(1-p_0)/n}}$$

**Parameters**: $p_0 = 0.70$, $n = 5$ (novice-tier group), $\alpha = 0.05$

**Power Analysis**: With effect size Cohen's $h = 0.8$ (70% vs. 30% baseline), power = 0.80 requires $n \geq 10$ total participants.

**Test 2: Model Accuracy Maintenance (Prediction P3)**

**Null Hypothesis**: $H_0: \mu_{\text{diff}} = 0$ (no difference between template-based and manual)
**Alternative Hypothesis**: $H_1: |\mu_{\text{diff}}| \leq 0.02$ (equivalence within 2%)

**Test**: Paired t-test with Bonferroni correction for 3 benchmarks
$$t = \frac{\bar{d}}{s_d / \sqrt{n}}$$

**Parameters**: $n = 5$ (novice-tier participants × 3 tasks), $\alpha = 0.017$ (Bonferroni correction: 0.05/3)

**Test 3: Verification Accuracy (Prediction P2)**

**Null Hypothesis**: $H_0: \text{Precision} \geq 0.90, \text{Recall} \geq 0.85$

**Test**: Bootstrap confidence intervals (1000 resamples)
$$\text{CI}_{95\%}(\text{Precision}) = [q_{0.025}, q_{0.975}]$$

**Parameters**: 10 synthetic violation test cases, 2 independent expert reviewers

**Test 4: Expertise Gap (Prediction P4)**

**Null Hypothesis**: $H_0: p_{\text{Master's}} - p_{\text{PhD}} = 0$
**Alternative Hypothesis**: $H_1: p_{\text{Master's}} - p_{\text{PhD}} \geq -0.15$

**Test**: Two-proportion z-test
$$z = \frac{\hat{p}_1 - \hat{p}_2}{\sqrt{\hat{p}(1-\hat{p})(1/n_1 + 1/n_2)}}$$

**Parameters**: $n_1 = 5$ (Master's), $n_2 = 5$ (PhD), $\alpha = 0.05$

#### 3.5.2 Confound Control

**Controlled Variables**:
1. **Hardware**: All experiments run on identical compute environment (1× NVIDIA A100 GPU, 40GB RAM, Ubuntu 20.04)
2. **Data Splits**: Fixed random seeds for train/validation/test splits (reproducibility)
3. **Training Time**: Maximum 2 hours per model with early stopping (patience=10 epochs)
4. **Hyperparameters**: Fixed via templates (learning rate=1e-4, batch size=32, optimizer=Adam)

**Measured Confounds**:
1. **Prior ML Experience**: Pre-study survey measuring years of Python/PyTorch experience, prior AutoML usage
2. **Task Order Effects**: Counterbalance task order (A→B→C vs. C→B→A) across participants
3. **Template Familiarity**: Measure time spent reviewing template documentation

**Statistical Control**:
- ANCOVA with prior ML experience as covariate
- Repeated measures ANOVA for within-subjects task effects
- Correlation analysis between confounds and deployment success

### 3.6 Implementation Details

**Software Stack**:
- **Framework Backend**: Python 3.9, PyTorch 2.0, PyTorch Lightning 2.0
- **YAML Parsing**: Hydra configuration framework
- **Identifiability Verification**: Custom implementation of Moran & Aragam (2025) tests using NumPy/SciPy
- **Visualization**: NetworkX for causal graph rendering, Matplotlib for explanations
- **User Interface**: Jupyter Notebook-based interface for novice-tier, Python API for expert-tier

**Template Implementation**:
Each template is a Python class inheriting from base `CRLTemplate`:

```python
class ClinicalConfoundingTemplate(CRLTemplate):
    def __init__(self, config):
        self.encoder = ResNetEncoder(latent_dim=config.latent_dim)
        self.decoder = ConvDecoder(latent_dim=config.latent_dim)
        self.confounder_predictor = MLPPredictor(
            input_dim=config.latent_dim,
            output_dim=len(config.confounders)
        )
    
    def loss_function(self, x, c):
        z = self.encoder(x)
        x_recon = self.decoder(z)
        c_pred = self.confounder_predictor(z)
        
        loss_recon = F.mse_loss(x_recon, x)
        loss_inv = F.cross_entropy(c_pred, c)  # Invariance loss
        loss_ind = hsic(z, c)  # Independence loss (HSIC)
        
        return loss_recon + self.lambda1 * loss_inv + self.lambda2 * loss_ind
```

**Identifiability Checker Implementation**:

```python
def verify_identifiability(scm, assumptions, data):
    results = {}
    
    # Test 1: Environment diversity
    if assumptions["multi_environment"]:
        mmd_matrix = compute_mmd_matrix(data.environments)
        T_env = np.mean(mmd_matrix[np.triu_indices_from(mmd_matrix, k=1)])
        results["env_diversity"] = {
            "statistic": T_env,
            "threshold": 0.25,
            "passed": T_env >= 0.25,
            "confidence_interval": bootstrap_ci(T_env, data, n_bootstrap=1000)
        }
    
    # Test 2: Functional form
    if assumptions["functional_form"] == "linear":
        T_lin = test_linearity(scm.encoder, data.X)
        results["linearity"] = {
            "statistic": T_lin,
            "threshold": 0.1,
            "passed": T_lin <= 0.1,
            "confidence_interval": bootstrap_ci(T_lin, data, n_bootstrap=1000)
        }
    
    # Test 3: Unobserved confounding
    if assumptions["no_unobserved_confounding"]:
        T_conf = test_confounding(data.Z, data.Y, data.W)
        results["confounding"] = {
            "statistic": T_conf,
            "threshold": 0.05,
            "passed": T_conf <= 0.05,
            "confidence_interval": bootstrap_ci(T_conf, data, n_bootstrap=1000)
        }
    
    return IdentifiabilityReport(results)
```

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

#### 4.1.1 Quantitative Outcomes

Based on our hypothesis and statistical power analysis, we expect the following outcomes:

**Outcome 1: Deployment Success**
- **Prediction**: ≥70% of Master's-level participants (≥4 of 5) will successfully deploy CRL models within 4 hours using novice-tier templates
- **Baseline Comparison**: <30% success rate for manual deployment (historical data from cheng-01037 development)
- **Impact**: 2.3× improvement in deployment success rate, demonstrating 60% barrier reduction

**Outcome 2: Model Quality Maintenance**
- **Prediction**: Template-based models will achieve accuracy within 2% of manual CRL implementations:
  - ISIC: AUC = 0.85-0.87 (baseline: 0.87)
  - ChestX-ray14: F1 = 0.78-0.80 (baseline: 0.80)
  - BraTS: Dice = 0.88-0.90 (baseline: 0.90)
- **Impact**: Demonstrates that accessibility layers do not sacrifice model quality

**Outcome 3: Verification Accuracy**
- **Prediction**: Automated identifiability checker will achieve:
  - Precision ≥90% (≤10% false positive rate)
  - Recall ≥85% (≤15% false negative rate)
- **Impact**: Validates safety net effectiveness—automated verification maintains theoretical rigor

**Outcome 4: Expertise Gap Reduction**
- **Prediction**: Master's-level success rate will be ≥85% of PhD-level success rate (gap ≤15%)
- **Impact**: Demonstrates framework enables domain experts without PhD-level causality training to deploy CRL methods

**Outcome 5: Time Efficiency**
- **Prediction**: Median deployment time ≤4 hours (vs. 12-16 hours for manual implementation)
- **Impact**: 67-75% time reduction, enabling rapid prototyping and iteration

#### 4.1.2 Qualitative Outcomes

**User Experience Insights**:
- Identification of usability pain points in template specification
- Understanding of trust factors in automated verification (when do users override warnings?)
- Insights into medical domain expert mental models of causality

**Template Library Expansion Roadmap**:
- Validated patterns for clinical confounding removal and multi-site generalization
- Identified gaps requiring additional templates (e.g., temporal disease progression, rare disease scenarios)
- Generalization pathway to robotics and biology domains

**Framework Refinement**:
- Optimal YAML template granularity (simplicity vs. expressiveness trade-off)
- Identifiability checker sensitivity tuning (false positive vs. false negative balance)
- Expert-tier feature prioritization based on user feedback

### 4.2 Scientific Impact

#### 4.2.1 Theoretical Contributions

**Abstraction-Verification Duality Framework**:
We formalize the principle that complex theoretical frameworks can be made accessible without sacrificing correctness through automated verification. This contributes to broader ML accessibility research by demonstrating that:

$$\text{Accessibility} \wedge \text{Theoretical Rigor} \iff \text{Abstraction Layer} + \text{Automated Verification}$$

This framework is generalizable beyond CRL to other theory-heavy ML domains (e.g., differential privacy, fairness-aware learning, physics-informed neural networks).

**Identifiability Verification as Safety Net**:
We demonstrate that statistical identifiability tests (Moran & Aragam 2025) can serve as runtime safety checks, analogous to type systems in programming languages. This opens research directions in:
- Formal verification for causal ML pipelines
- Certified CRL deployment with provable guarantees
- Causal assumption debugging tools

#### 4.2.2 Methodological Contributions

**Two-Tier Abstraction Design Pattern**:
Our novice-tier (template-based) and expert-tier (full control) design provides a reusable pattern for ML framework development. This addresses the "expert-friendly vs. beginner-friendly" tension by providing multiple entry points.

**Domain-Specific Template Libraries**:
We establish a methodology for encoding domain-specific CRL patterns as reusable templates. This contributes to:
- Transfer learning for causal models (template adaptation across domains)
- Best practices documentation for CRL deployment
- Standardization of CRL architectures for common use cases

**Human-Readable Causal Explanations**:
Our approach to generating natural language explanations of causal assumptions and identifiability violations contributes to explainable AI research, particularly for causal models.

### 4.3 Practical Impact

#### 4.3.1 Medical Imaging Applications

**Immediate Impact**:
- Enable 5-10× more medical imaging researchers to deploy CRL methods (Master's-level researchers >> PhD-level CRL experts)
- Accelerate development of robust diagnostic models for:
  - Skin lesion classification with reduced demographic bias
  - Multi-hospital chest X-ray diagnosis systems
  - Brain tumor segmentation across MRI scanner types

**Long-Term Impact**:
- Reduce diagnostic biases in clinical decision support systems deployed in diverse healthcare settings
- Improve model generalization across hospitals, reducing need for site-specific retraining
- Enable causal reasoning in medical imaging AI, supporting counterfactual explanations ("What if this patient were 10 years younger?")

#### 4.3.2 Broader CRL Adoption

**Cross-Domain Expansion**:
Our supplementary evidence validates template expansion to:
- **Robotics**: BISCUIT pattern for pose estimation and manipulation (35 citations)
- **Biology**: scMultiomeGRN pattern for gene regulatory network inference (21 citations)

This demonstrates framework generalizability beyond medical imaging.

**Industry Adoption Pathway**:
- Template libraries lower barrier for industry practitioners to adopt CRL
- Automated verification provides safety guarantees for deployment in regulated domains (healthcare, finance, autonomous systems)
- Expert-tier enables ML engineers to customize for proprietary applications

#### 4.3.3 Educational Impact

**CRL Education**:
- Framework serves as teaching tool for causal inference courses, allowing students to experiment with CRL without deep theoretical prerequisites
- Template library provides concrete examples of CRL architectures for different problem types
- Identifiability verification helps students understand theoretical concepts through interactive exploration

**Interdisciplinary Collaboration**:
- Enables collaboration between domain experts (medical imaging, robotics, biology) and CRL researchers by providing common language (templates) and safety checks (verification)
- Reduces communication overhead in interdisciplinary projects

### 4.4 Societal Impact

#### 4.4.1 Healthcare Equity

**Bias Reduction**:
By enabling deployment of CRL methods that explicitly model clinical confounders (age, sex, race), our framework contributes to reducing diagnostic biases that disproportionately affect underrepresented populations. For example:
- Skin lesion classifiers that account for skin tone variations
- Chest X-ray models that generalize across socioeconomic groups (different hospital quality)

**Multi-Site Generalization**:
Improved cross-hospital generalization enables deployment of AI diagnostic tools in resource-limited settings (rural hospitals, developing countries) where local training data is scarce.

#### 4.4.2 Responsible AI Development

**Transparency**:
Human-readable causal explanations and identifiability verification reports increase transparency in AI model development, supporting:
- Regulatory compliance (FDA approval for medical devices)
- Stakeholder trust (clinicians understanding model assumptions)
- Ethical review (IRB assessment of causal claims)

**Robustness**:
CRL models with verified identifiability conditions are more robust to distribution shift, reducing risk of:
- Silent failures when deployed in new environments
- Spurious correlation exploitation (e.g., learning hospital-specific artifacts)
- Adversarial vulnerabilities

### 4.5 Future Research Directions

**Causal Accessibility Guidelines (CAG)**:
Inspired by WCAG 2.1 web accessibility standards, we envision developing formal guidelines for making causal inference methods accessible to domain experts. This includes:
- Standardized template specification formats
- Identifiability verification protocols
- Human-readable explanation requirements

**Automated Template Discovery**:
Future work could explore meta-learning approaches to automatically discover CRL templates from successful deployments, creating a self-improving template library.

**Federated CRL Deployment**:
Extend framework to federated learning settings where data cannot be centralized (e.g., multi-hospital collaborations with privacy constraints), combining CRL with differential privacy.

**Temporal CRL Templates**:
Expand beyond cross-sectional data to temporal causal discovery (disease progression modeling, treatment effect estimation over time) using frameworks like CITRIS.

**Certification and Auditing**:
Develop formal certification procedures for CRL deployments, analogous to software testing standards, enabling third-party auditing of causal assumptions and identifiability claims.

---

### 4.6 Limitations and Mitigation Strategies

**Limitation 1: Small User Study Sample Size**
- **Risk**: N=10 participants limits statistical power and generalizability
- **Mitigation**: Report effect sizes and confidence intervals, plan follow-up larger-scale study (N=30-50) if initial results promising

**Limitation 2: Template Library Initially Small**
- **Risk**: Single validated template (cheng-01037 pattern) may not cover diversity of medical imaging tasks
- **Mitigation**: Prioritize expansion based on user study feedback, validate on 4th held-out dataset

**Limitation 3: Identifiability Checker False Positives**
- **Risk**: Overly conservative verification may frustrate users with false alarms
- **Mitigation**: Implement tiered violation severity (ERROR/WARNING/INFO), allow expert override with explicit acknowledgment

**Limitation 4: Recruitment Challenges**
- **Risk**: Clinician time is expensive and limited, may struggle to recruit 10 participants
- **Mitigation**: Flexible scheduling, remote participation option, competitive compensation ($200), partner with medical imaging research groups

**Limitation 5: Generalization Beyond Medical Imaging**
- **Risk**: Framework designed for medical imaging may not transfer to other domains without modification
- **Mitigation**: Supplementary evidence (BISCUIT robotics, scMultiomeGRN biology) validates cross-domain potential, plan domain-specific template development

---

## Conclusion

This research addresses a critical bottleneck in translating causal representation learning theory to real-world impact by developing an automated deployment framework that bridges the expertise gap between CRL researchers and domain experts. Through a principled two-tier abstraction design coupled with automated identifiability verification, we enable Master's-level medical imaging experts to deploy causally sound models while maintaining theoretical rigor. Our expected outcomes—≥70% deployment success within 4 hours, model accuracy within 2% of manual baselines, and ≥90% verification precision—demonstrate that complex theoretical frameworks can be made accessible without sacrificing correctness. This work has immediate impact in medical imaging (reducing diagnostic biases, improving multi-hospital generalization) and establishes a generalizable framework for democratizing CRL across high-impact domains including robotics and biology. By reducing deployment barriers by 60% while preserving causal guarantees, we accelerate the path from CRL theory to societal benefit in healthcare, autonomous systems, and beyond.