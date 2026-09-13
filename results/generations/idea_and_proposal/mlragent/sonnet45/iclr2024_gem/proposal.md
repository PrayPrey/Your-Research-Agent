# Adaptive Generative Models with Uncertainty-Guided Experimental Feedback Loops for Protein Engineering

## 1. Introduction

### Background

Protein engineering stands at the intersection of biology, chemistry, and computational science, offering transformative solutions to challenges in medicine, industrial biocatalysis, and environmental sustainability. Traditional protein design approaches rely heavily on rational design and directed evolution, which are time-consuming and resource-intensive. The advent of generative machine learning has introduced powerful tools for exploring vast sequence spaces and proposing novel protein designs with desired properties. However, a critical gap persists between computational predictions and experimental validation—the so-called "generate-then-validate" paradigm creates inefficiencies where computational models operate independently of experimental feedback, leading to suboptimal resource allocation and slow iterative improvement.

Current generative models for protein design, including variational autoencoders (VAEs), generative adversarial networks (GANs), and diffusion models, excel at generating diverse protein sequences but typically lack robust uncertainty quantification mechanisms. This limitation prevents intelligent prioritization of which designs warrant expensive experimental validation. Moreover, these models rarely incorporate experimental feedback in a systematic, adaptive manner, missing opportunities to refine predictions and accelerate the design cycle.

Recent advances in active learning and Bayesian deep learning offer promising avenues for addressing these limitations. ProSpero (Kmicikiewicz et al., 2025) demonstrated the value of integrating pre-trained generative models with surrogate models updated from experimental feedback, enabling exploration beyond wild-type sequences. Similarly, Bayesian active learning approaches in protein docking (Cao & Shen, 2019) have shown that uncertainty-guided sampling can significantly improve optimization efficiency. However, a comprehensive framework that combines state-of-the-art generative models with principled uncertainty quantification and adaptive experimental design specifically for protein engineering remains underdeveloped.

### Research Objectives

This research proposes to develop and validate an integrated computational-experimental framework termed **Adaptive Generative Models with Uncertainty-Guided Experimental Feedback Loops (AGM-UEFL)** for protein engineering. The specific objectives are:

1. **Develop a Bayesian deep generative framework** that incorporates uncertainty quantification into protein sequence generation, leveraging ensemble methods and evidential deep learning
2. **Design intelligent acquisition functions** that prioritize experimental validation based on predicted performance and epistemic uncertainty
3. **Implement continual learning mechanisms** that enable adaptive model refinement from experimental feedback without catastrophic forgetting
4. **Validate the framework** through collaboration with high-throughput screening facilities on real protein engineering challenges
5. **Demonstrate improved efficiency** in achieving target protein properties compared to conventional generate-then-validate approaches

### Significance

This research directly addresses the computational-experimental divide highlighted by the GEM workshop, offering several significant contributions:

**Scientific Impact**: By creating a closed-loop system where computational models actively participate in experimental design, this work fundamentally shifts the paradigm from passive prediction to active learning. The uncertainty quantification framework will provide researchers with confidence estimates crucial for decision-making, while the adaptive retraining mechanism ensures models continuously improve from real-world data.

**Practical Impact**: The expected 3-5× reduction in experimental cycles needed to achieve target properties translates to substantial savings in time, resources, and costs. For pharmaceutical and biotechnology industries, this acceleration could significantly shorten development timelines for therapeutic proteins, enzymes, and biosensors.

**Methodological Impact**: The proposed framework establishes a blueprint for integrating generative ML with experimental biology that can extend beyond protein engineering to other biomolecular design domains, including small molecules, RNA, and metabolic pathway engineering.

## 2. Methodology

### 2.1 Overall Framework Architecture

The AGM-UEFL framework consists of three interconnected modules operating in iterative cycles:

**Module 1: Bayesian Generative Model** - Generates diverse protein sequence candidates with uncertainty estimates  
**Module 2: Acquisition Function Optimizer** - Prioritizes candidates for experimental validation  
**Module 3: Continual Learning Engine** - Updates the model with experimental feedback

### 2.2 Bayesian Generative Model with Uncertainty Quantification

#### 2.2.1 Base Generative Architecture

We employ a hybrid architecture combining variational autoencoders with diffusion model components for protein sequence generation. The VAE structure is defined as:

**Encoder**: $q_\phi(z|x)$ maps protein sequences $x \in \mathcal{X}$ to latent representations $z \in \mathbb{R}^d$

**Decoder**: $p_\theta(x|z)$ reconstructs sequences from latent codes

**Prior**: $p(z) = \mathcal{N}(0, I)$

The VAE objective combines reconstruction and regularization:

$$\mathcal{L}_{VAE} = \mathbb{E}_{q_\phi(z|x)}[\log p_\theta(x|z)] - \beta \cdot D_{KL}(q_\phi(z|x) || p(z))$$

where $\beta$ controls the regularization strength.

To enhance sequence quality, we augment the decoder with a diffusion process that iteratively refines generated sequences through learned denoising steps:

$$x_t = \sqrt{\bar{\alpha}_t}x_0 + \sqrt{1-\bar{\alpha}_t}\epsilon, \quad \epsilon \sim \mathcal{N}(0,I)$$

#### 2.2.2 Uncertainty Quantification via Deep Ensembles

We implement uncertainty estimation through deep ensembles, training $M=10$ independent models with different random initializations:

$$\{(p_{\theta_1}, q_{\phi_1}), (p_{\theta_2}, q_{\phi_2}), ..., (p_{\theta_M}, q_{\phi_M})\}$$

For a given latent code $z$, the predictive distribution is:

$$p_{ensemble}(x|z) = \frac{1}{M}\sum_{i=1}^M p_{\theta_i}(x|z)$$

**Epistemic uncertainty** (model uncertainty) is quantified using the variance across ensemble predictions:

$$\sigma^2_{epistemic}(z) = \frac{1}{M}\sum_{i=1}^M ||f_{\theta_i}(z) - \bar{f}(z)||^2$$

where $f_{\theta_i}(z)$ represents predicted properties and $\bar{f}(z) = \frac{1}{M}\sum_{i=1}^M f_{\theta_i}(z)$.

**Aleatoric uncertainty** (data uncertainty) is captured through evidential deep learning, where the network outputs parameters of a higher-order distribution. For continuous property prediction, we output Gaussian parameters with learnable variance:

$$p(y|x, \theta_i) = \mathcal{N}(y|\mu_{\theta_i}(x), \sigma^2_{\theta_i}(x))$$

Total predictive uncertainty combines both sources:

$$\sigma^2_{total} = \sigma^2_{epistemic} + \mathbb{E}[\sigma^2_{aleatoric}]$$

#### 2.2.3 Multi-Objective Property Prediction

Following the compositional approach of Tagasovska et al. (2022), we model multiple protein properties (stability, binding affinity, solubility, etc.) using separate predictive heads that share the latent representation:

$$f_{prop_j}(x) = h_j(g(x)), \quad j \in \{1, 2, ..., K\}$$

where $g(x)$ is a shared encoder and $h_j$ are property-specific heads.

### 2.3 Uncertainty-Guided Acquisition Functions

We design acquisition functions that balance exploitation (selecting high-predicted-value sequences) with exploration (selecting sequences where the model is uncertain):

#### 2.3.1 Upper Confidence Bound (UCB)

$$\alpha_{UCB}(x) = \mu(x) + \kappa \cdot \sigma_{total}(x)$$

where $\mu(x)$ is the mean predicted property value, $\sigma_{total}(x)$ is total uncertainty, and $\kappa$ is a tunable exploration parameter.

#### 2.3.2 Expected Improvement (EI)

$$\alpha_{EI}(x) = \mathbb{E}[\max(f(x) - f^*, 0)]$$

where $f^*$ is the current best observed value. Under Gaussian assumptions:

$$\alpha_{EI}(x) = (\mu(x) - f^*)\Phi(Z) + \sigma(x)\phi(Z)$$

with $Z = \frac{\mu(x) - f^*}{\sigma(x)}$, $\Phi$ the standard normal CDF, and $\phi$ its PDF.

#### 2.3.3 Multi-Objective Acquisition

For multiple properties, we implement a Pareto-aware acquisition function:

$$\alpha_{Pareto}(x) = \sum_{j=1}^K w_j \cdot \alpha_{EI,j}(x) + \lambda \cdot \mathcal{D}(x, \mathcal{P})$$

where $w_j$ are property weights, $\alpha_{EI,j}$ is EI for property $j$, and $\mathcal{D}(x, \mathcal{P})$ measures distance to the current Pareto front $\mathcal{P}$.

### 2.4 Continual Learning and Adaptive Model Updating

#### 2.4.1 Experience Replay Buffer

To prevent catastrophic forgetting, we maintain a replay buffer $\mathcal{B}$ storing past experimental results:

$$\mathcal{B} = \{(x_i, y_i, t_i)\}_{i=1}^N$$

where $x_i$ are sequences, $y_i$ are measured properties, and $t_i$ are timestamps.

#### 2.4.2 Elastic Weight Consolidation

We implement Elastic Weight Consolidation (EWC) to preserve important parameters learned from previous data:

$$\mathcal{L}_{EWC} = \mathcal{L}_{new} + \frac{\lambda_{EWC}}{2}\sum_i F_i(\theta_i - \theta^*_i)^2$$

where $\mathcal{L}_{new}$ is the loss on new data, $F_i$ is the Fisher information matrix diagonal element for parameter $i$, and $\theta^*_i$ are previous optimal parameters.

#### 2.4.3 Update Protocol

When new experimental data $\mathcal{D}_{new} = \{(x_j, y_j)\}_{j=1}^B$ arrives:

1. Sample mini-batch $\mathcal{D}_{replay}$ from buffer $\mathcal{B}$
2. Combine: $\mathcal{D}_{train} = \mathcal{D}_{new} \cup \mathcal{D}_{replay}$
3. Update each ensemble member: $\theta_i \leftarrow \theta_i - \eta \nabla_{\theta_i}\mathcal{L}_{EWC}(\mathcal{D}_{train})$
4. Add $\mathcal{D}_{new}$ to buffer $\mathcal{B}$

### 2.5 Experimental Design and Validation

#### 2.5.1 Data Collection

**Initial Training Data**: We will leverage publicly available datasets including:
- ProteinGym (>250 deep mutational scanning datasets)
- UniProt (sequence annotations)
- PDB (structural information)
- FLIP benchmark sequences with measured properties

**Wet-lab Validation**: Partnership with high-throughput screening facilities to conduct experimental validation on:
- **Task 1**: Engineering thermostable variants of GFP (Green Fluorescent Protein)
- **Task 2**: Optimizing binding affinity for therapeutic antibodies
- **Task 3**: Enhancing catalytic efficiency of industrial enzymes

#### 2.5.2 Experimental Protocol

For each design cycle $t$:

1. **Generation Phase**: Sample $N_{candidates}=1000$ sequences from $p_{ensemble}(x|z)$
2. **Scoring Phase**: Compute acquisition scores $\{\alpha(x_i)\}_{i=1}^{N_{candidates}}$
3. **Selection Phase**: Select top $B=96$ sequences (matching 96-well plate format)
4. **Synthesis & Assay**: Synthesize selected sequences and measure target properties
5. **Update Phase**: Retrain model with new data using continual learning
6. **Iteration**: Repeat for $T_{max}=10$ cycles

#### 2.5.3 Baseline Comparisons

We compare AGM-UEFL against:
- **Random Sampling**: Random selection from generative model
- **Greedy Selection**: Selecting highest predicted value sequences
- **Standard Active Learning**: Gaussian Process with UCB (no generative model)
- **ProSpero**: Current state-of-the-art adaptive method
- **Directed Evolution**: Traditional random mutagenesis and screening

#### 2.5.4 Evaluation Metrics

**Primary Metrics**:
- **Experimental Efficiency**: Number of cycles to reach target property threshold
- **Resource Utilization**: Fraction of synthesized sequences meeting criteria
- **Best Value Found**: Maximum property value discovered

**Secondary Metrics**:
- **Diversity**: Sequence diversity of discovered solutions (measured by edit distance)
- **Pareto Front Quality**: Hypervolume indicator for multi-objective tasks
- **Calibration**: Correlation between predicted uncertainty and actual errors
- **Computational Cost**: Wall-clock time per cycle

**Statistical Validation**: All experiments repeated with 5 independent runs; significance tested using Mann-Whitney U tests with Bonferroni correction.

### 2.6 Implementation Details

- **Framework**: PyTorch with Pyro for Bayesian components
- **Architecture**: Transformer encoder (6 layers, 512 hidden dims) for sequences
- **Training**: Adam optimizer, learning rate $10^{-4}$, batch size 128
- **Hardware**: 4× NVIDIA A100 GPUs for parallel ensemble training
- **Sequence Constraints**: Maintain structural motifs and functional residues using constrained generation

## 3. Expected Outcomes & Impact

### 3.1 Scientific Outcomes

**Quantitative Performance Targets**:
1. **3-5× reduction in experimental cycles** to achieve 90% of theoretical maximum property value compared to baselines
2. **50-70% improvement in hit rate** (fraction of tested sequences meeting criteria) over random sampling
3. **Calibrated uncertainty estimates** with expected calibration error <0.1
4. **Discovery of sequences with >20% property improvement** over wild-type

**Methodological Contributions**:
- Novel integration of diffusion models with Bayesian ensembles for protein design
- Theoretically grounded acquisition functions tailored to biomolecular optimization
- Continual learning framework preventing catastrophic forgetting in sequential experimental settings
- Open-source implementation enabling community adoption

### 3.2 Practical Impact

**Accelerated Protein Engineering**: The framework will demonstrate practical value through:
- **Pharmaceutical Applications**: Faster antibody optimization for therapeutic development
- **Industrial Biocatalysis**: Rapid enzyme engineering for sustainable chemical production
- **Biosensor Development**: Efficient design of protein-based diagnostic tools

**Economic Benefits**: 3-5× cycle reduction translates to:
- 60-80% cost savings in experimental budgets
- 6-12 month acceleration in development timelines
- Reduced environmental impact through minimized wet-lab waste

### 3.3 Broader Impact

**Bridging Computational-Experimental Divide**: This work directly addresses the GEM workshop's core mission by creating a framework where:
- Computational models actively guide experimental efforts
- Experimental results systematically improve computational predictions
- The iterative loop creates synergistic value exceeding either approach alone

**Extensibility**: The framework architecture is generalizable to:
- Small molecule drug design
- RNA therapeutics engineering
- Metabolic pathway optimization
- Materials science applications

**Educational Value**: Open-source release will provide:
- Teaching materials for integrating ML with experimental biology
- Benchmark datasets for uncertainty quantification in protein design
- Best practices for active learning in biomolecular applications

**Ethical Considerations**: We will implement safeguards against potential dual-use concerns by:
- Restricting generation to beneficial applications
- Transparent reporting of all sequences tested
- Collaboration with biosafety experts for risk assessment

### 3.4 Validation Through Publication and Dissemination

Results will be disseminated through:
1. **Primary Research Article**: Submission to Nature Biotechnology (via GEM fast-track)
2. **Methodological Paper**: Detailed computational framework in NeurIPS or ICML
3. **Open-source Release**: GitHub repository with documentation and tutorials
4. **Community Engagement**: Workshops at GEM, NeurIPS, and ISMB conferences
5. **Industry Partnerships**: Collaboration with biotech companies for real-world validation

### 3.5 Timeline and Milestones

**Months 1-6**: Framework development and validation on public datasets  
**Months 7-12**: Initial wet-lab experiments on GFP thermostability  
**Months 13-18**: Scale-up to antibody and enzyme engineering tasks  
**Months 19-24**: Comprehensive analysis, manuscript preparation, and open-source release

This research proposal presents a comprehensive approach to bridging the computational-experimental gap in protein engineering through adaptive generative models with uncertainty-guided feedback loops. By combining cutting-edge machine learning with principled experimental design, we expect to demonstrate substantial improvements in efficiency while establishing a new paradigm for integrative biomolecular design.