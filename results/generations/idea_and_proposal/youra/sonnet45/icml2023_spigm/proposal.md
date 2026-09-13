# Research Proposal: Modality-Agnostic Discrete Latent Spaces for Cross-Modal Structured Data Learning

## 1. Title

**Modality-Agnostic Discrete Latent Spaces for Cross-Modal Structured Data Learning: A Vector-Quantized Framework with Distribution-Free Uncertainty Quantification**

## 2. Introduction

### 2.1 Background

Probabilistic inference and generative modeling have achieved remarkable success in capturing complex probability distributions across various domains. However, a critical challenge persists when dealing with highly structured, heterogeneous data modalities—such as molecular graphs, chemical text representations, and temporal binding affinity profiles. Current approaches predominantly rely on modality-specific architectures that operate in isolation, requiring separate models for each data type and lacking the ability to leverage cross-modal information effectively.

In scientific domains like drug discovery and materials science, data naturally exists across multiple structured modalities. A single molecule can be represented as a molecular graph (atoms and bonds), a SMILES string (sequential chemical notation), or characterized by temporal binding affinity profiles. These representations encode complementary information: graphs capture structural topology, text provides human-readable notation, and time series reveal dynamic properties. Yet, existing probabilistic methods fail to unify these modalities into a coherent framework, limiting their ability to perform cross-modal queries (e.g., retrieving molecular structures from textual descriptions) or provide consistent uncertainty estimates across representations.

The Vector-Quantized Variational Autoencoder (VQ-VAE) framework has demonstrated success in learning discrete latent representations for individual modalities like images, audio, and video. Meanwhile, contrastive learning approaches such as CLIP have shown that shared continuous embeddings can align vision and language modalities. However, no existing work has successfully combined discrete representation learning with cross-modal contrastive alignment for heterogeneous structured data, particularly non-grid structures like graphs combined with sequential and temporal modalities.

### 2.2 Research Objectives

This research proposes a novel framework called **Modality-Agnostic Latent Spaces (MALS)** that addresses three fundamental objectives:

**Objective 1: Unified Representation Learning** - Develop a shared discrete codebook that can encode molecular graphs, chemical text (SMILES), and binding affinity time series into a single latent space, forcing modality-agnostic abstraction through information bottleneck.

**Objective 2: Cross-Modal Transfer** - Enable zero-shot cross-modal retrieval and generation capabilities, allowing queries in one modality (e.g., text description "aromatic compound with hydroxyl group") to retrieve or generate representations in another modality (molecular graph structure).

**Objective 3: Calibrated Uncertainty Quantification** - Provide distribution-free uncertainty estimates across all modalities using Conformal Prediction, ensuring reliable confidence measures essential for high-stakes scientific applications.

### 2.3 Research Significance

This research makes several significant contributions to both machine learning theory and scientific practice:

**Theoretical Contributions:**
- First demonstration that discrete latent codes can effectively unify heterogeneous structured modalities including non-grid structures (graphs), sequential data (text), and temporal data (time series)
- Novel integration of VQ-VAE discrete representation learning with contrastive multi-modal alignment, extending both frameworks beyond their current capabilities
- Theoretical framework for understanding how discretization enforces modality-agnostic abstraction in structured data

**Methodological Contributions:**
- A principled approach to cross-modal structured data learning that reduces architectural engineering overhead from M separate models to a single unified framework
- Distribution-free uncertainty quantification methodology applicable across heterogeneous modalities
- Scalable training strategy for multi-modal discrete representations with contrastive alignment

**Practical Impact:**
- Direct applications to drug discovery: text-to-molecule retrieval, property prediction with calibrated uncertainty, and cross-modal molecular design
- Generalizable framework applicable to other scientific domains with multi-modal structured data (materials science, protein engineering, climate modeling)
- Reduced computational costs and improved sample efficiency through shared representations and cross-modal knowledge transfer

The success of this research would establish a new paradigm for probabilistic modeling of structured heterogeneous data, with immediate applications in computational chemistry and broader implications for scientific machine learning.

## 3. Methodology

### 3.1 Data Collection and Preparation

**Dataset:** We utilize the QM9 dataset, a comprehensive molecular database containing 133,885 organic molecules with up to 9 heavy atoms (C, O, N, F). Each molecule in QM9 provides:
- **Molecular graphs**: Nodes represent atoms (with features: atom type, charge, hybridization), edges represent chemical bonds (with features: bond type, aromaticity)
- **SMILES strings**: Sequential text representation of molecular structure
- **Quantum properties**: 13 computed properties including binding affinity, which we convert to temporal profiles through molecular dynamics simulation or use existing temporal datasets

**Data Splits:** 
- Training: 107,108 molecules (80%)
- Calibration: 13,388 molecules (10%) - for Conformal Prediction calibration
- Test: 13,389 molecules (10%)

**Preprocessing:**
- Graphs: Standardize atom/bond features, apply random augmentation (node/edge dropout 0.1)
- SMILES: Tokenization with vocabulary size ~100, padding to max length 120
- Time series: Normalize to zero mean and unit variance, fixed length 128 timesteps

### 3.2 Model Architecture

#### 3.2.1 Modality-Specific Encoders

**Graph Encoder** ($E_G$): Graph Attention Network (GAT) with 4 layers
$$\mathbf{h}_i^{(l+1)} = \sigma\left(\sum_{j \in \mathcal{N}(i)} \alpha_{ij} \mathbf{W}^{(l)} \mathbf{h}_j^{(l)}\right)$$

where $\alpha_{ij}$ are learned attention coefficients, $\mathbf{W}^{(l)}$ are layer-specific weight matrices, and $\mathcal{N}(i)$ denotes neighbors of node $i$. Global graph representation obtained via attention-weighted pooling:
$$\mathbf{z}_G = \sum_{i=1}^{N} \beta_i \mathbf{h}_i^{(L)}$$

**Text Encoder** ($E_T$): Transformer encoder with 6 layers, 8 attention heads, dimension 512
$$\mathbf{z}_T = \text{Transformer}(\text{Embed}(\text{SMILES}))[\text{CLS}]$$

**Time Series Encoder** ($E_{TS}$): Temporal Transformer with positional encoding
$$\mathbf{z}_{TS} = \text{Transformer}(\mathbf{X}_{ts} + \mathbf{PE})[\text{mean-pool}]$$

All encoders output representations $\mathbf{z}_m \in \mathbb{R}^{512}$ for modality $m \in \{G, T, TS\}$.

#### 3.2.2 Vector Quantization Layer

The continuous encoder outputs are mapped to discrete codes via vector quantization:

$$\mathbf{z}_q = \text{VQ}(\mathbf{z}_m) = \mathbf{e}_k, \quad k = \arg\min_{j \in [K]} \|\mathbf{z}_m - \mathbf{e}_j\|_2$$

where $\mathbf{e}_j \in \mathbb{R}^{512}$ are learnable codebook vectors, and $K = 1024$ is the codebook size. The codebook $\mathcal{C} = \{\mathbf{e}_1, \ldots, \mathbf{e}_K\}$ is **shared across all modalities**.

#### 3.2.3 Modality-Specific Decoders

**Graph Decoder** ($D_G$): Graph generation via sequential node/edge prediction
$$P(\mathcal{G}|\mathbf{z}_q) = \prod_{t=1}^{T} P(v_t, e_t | v_{<t}, e_{<t}, \mathbf{z}_q)$$

**Text Decoder** ($D_T$): Autoregressive Transformer decoder
$$P(\text{SMILES}|\mathbf{z}_q) = \prod_{t=1}^{L} P(s_t | s_{<t}, \mathbf{z}_q)$$

**Time Series Decoder** ($D_{TS}$): Temporal Transformer decoder
$$\hat{\mathbf{X}}_{ts} = \text{TransformerDecoder}(\mathbf{z}_q)$$

### 3.3 Training Objectives

#### 3.3.1 VQ-VAE Loss Components

For each modality $m$, the standard VQ-VAE loss consists of:

**Reconstruction Loss:**
$$\mathcal{L}_{\text{recon}}^m = -\log P(x_m | \mathbf{z}_q)$$

**Codebook Loss** (updates codebook to match encoder outputs):
$$\mathcal{L}_{\text{codebook}} = \|\text{sg}[\mathbf{z}_m] - \mathbf{e}_k\|_2^2$$

**Commitment Loss** (encourages encoder to commit to codebook):
$$\mathcal{L}_{\text{commit}} = \beta \|\mathbf{z}_m - \text{sg}[\mathbf{e}_k]\|_2^2$$

where $\text{sg}[\cdot]$ denotes stop-gradient, and $\beta = 0.25$.

#### 3.3.2 Cross-Modal Contrastive Loss

The key innovation is the cross-modal contrastive objective that aligns codes from the same molecule across modalities:

$$\mathcal{L}_{\text{contrast}} = -\frac{1}{B} \sum_{i=1}^{B} \log \frac{\exp(\text{sim}(\mathbf{z}_q^{m_1}(i), \mathbf{z}_q^{m_2}(i)) / \tau)}{\sum_{j=1}^{B} \exp(\text{sim}(\mathbf{z}_q^{m_1}(i), \mathbf{z}_q^{m_2}(j)) / \tau)}$$

where $\text{sim}(\mathbf{u}, \mathbf{v}) = \mathbf{u}^\top \mathbf{v} / (\|\mathbf{u}\| \|\mathbf{v}\|)$ is cosine similarity, $\tau$ is temperature, $B$ is batch size, and $(m_1, m_2)$ are modality pairs.

#### 3.3.3 Total Training Objective

$$\mathcal{L}_{\text{total}} = \sum_{m \in \{G,T,TS\}} \lambda_m \mathcal{L}_{\text{recon}}^m + \mathcal{L}_{\text{codebook}} + \mathcal{L}_{\text{commit}} + \lambda_c \mathcal{L}_{\text{contrast}}$$

where $\lambda_m$ are modality-specific weights (tuned to balance reconstruction quality), and $\lambda_c = 0.5$ is the contrastive loss weight.

### 3.4 Training Strategy

**Staged Training Approach:**

**Stage 1 (Weeks 1-4):** Train on two modalities (graphs + text)
- Batch size: 64, Learning rate: 3e-4 with cosine annealing
- Optimizer: AdamW with weight decay 0.01
- Codebook updated via exponential moving average (EMA) with decay 0.99
- Contrastive temperature $\tau = 0.1$

**Stage 2 (Weeks 5-8):** Add third modality (time series)
- Fine-tune with all three modalities
- Reduced learning rate: 1e-4
- Balanced batch sampling: equal representation from each modality

**Codebook Collapse Prevention:**
- Monitor codebook utilization: $U = |\{k : \exists i, \arg\min_j \|\mathbf{z}_i - \mathbf{e}_j\| = k\}| / K$
- Reset unused codes (utilization < 0.01 over 1000 batches) to random encoder outputs
- EMA updates for stable codebook learning

### 3.5 Uncertainty Quantification via Conformal Prediction

After training, we calibrate uncertainty estimates using Conformal Prediction on the calibration set:

**Step 1: Compute Non-Conformity Scores**
For each calibration sample $i$, compute reconstruction error:
$$\alpha_i = \|\mathbf{x}_i - \hat{\mathbf{x}}_i\|_2$$

**Step 2: Determine Quantile Threshold**
For desired coverage level $1-\delta$ (e.g., 90%), compute:
$$\hat{q} = \text{Quantile}(\{\alpha_i\}_{i=1}^{n_{\text{cal}}}, 1-\delta)$$

**Step 3: Prediction Sets**
For test sample $\mathbf{x}_{\text{test}}$, the prediction set is:
$$C(\mathbf{x}_{\text{test}}) = \{\mathbf{z}_q : \|\mathbf{x}_{\text{test}} - D(\mathbf{z}_q)\|_2 \leq \hat{q}\}$$

This provides distribution-free coverage guarantees: $P(\mathbf{x}_{\text{true}} \in C(\mathbf{x}_{\text{test}})) \geq 1-\delta$.

### 3.6 Experimental Design

#### 3.6.1 Evaluation Metrics

**Cross-Modal Retrieval:**
- **Top-k Accuracy**: Percentage of queries where correct match appears in top-k retrieved items (k=1,5,10)
- **Mean Reciprocal Rank (MRR)**: $\text{MRR} = \frac{1}{|Q|}\sum_{i=1}^{|Q|} \frac{1}{\text{rank}_i}$

**Reconstruction Quality:**
- **Graphs**: Validity (% valid molecules), Uniqueness, Novelty, Fréchet ChemNet Distance (FCD)
- **Text**: BLEU score, exact match accuracy
- **Time Series**: Mean Squared Error (MSE), Dynamic Time Warping (DTW) distance

**Uncertainty Calibration:**
- **Expected Calibration Error (ECE)**: $\text{ECE} = \sum_{b=1}^{B} \frac{|B_b|}{N} |\text{acc}(B_b) - \text{conf}(B_b)|$
- **Coverage**: Empirical coverage of conformal prediction sets
- **Prediction Set Size**: Average size of prediction sets

**Codebook Metrics:**
- **Utilization**: Percentage of codebook entries used
- **Perplexity**: $\exp(-\sum_k p_k \log p_k)$ where $p_k$ is usage frequency of code $k$

#### 3.6.2 Baseline Comparisons

**Baseline 1: Modality-Specific VQ-VAEs**
- Three separate VQ-VAE models, one per modality
- Same architecture as MALS encoders/decoders
- Cross-modal retrieval via nearest neighbor in continuous pre-quantization space

**Baseline 2: Continuous Multi-Modal VAE**
- Shared continuous latent space (no quantization)
- Product-of-Experts (PoE) for multi-modal fusion

**Baseline 3: LLM-Based Cross-Domain Integration**
- Large language model (LLaMA-7B) fine-tuned for cross-modal translation
- Represents current state-of-the-art in flexible multi-modal learning

#### 3.6.3 Ablation Studies

**Ablation 1: Codebook Size**
- $K \in \{512, 1024, 2048, 4096\}$
- Hypothesis: Optimal K balances expressiveness and generalization

**Ablation 2: Contrastive Temperature**
- $\tau \in \{0.05, 0.1, 0.2, 0.5\}$
- Hypothesis: Lower temperature improves alignment but may reduce diversity

**Ablation 3: Loss Weight Sensitivity**
- $\lambda_c \in \{0.1, 0.5, 1.0, 2.0\}$
- Analyze reconstruction vs. alignment trade-off

**Ablation 4: Training Strategy**
- Compare staged (2-modal → 3-modal) vs. joint training
- Measure impact on convergence and final performance

#### 3.6.4 Statistical Testing

**Cross-Modal Accuracy:**
- McNemar's test for paired comparisons between MALS and baselines
- Significance level: $\alpha = 0.05$ with Bonferroni correction

**Reconstruction Quality:**
- One-way ANOVA across methods
- Post-hoc Tukey HSD for pairwise comparisons

**Uncertainty Calibration:**
- Bootstrap confidence intervals (10,000 samples) for ECE
- Paired t-test for coverage comparison

### 3.7 Implementation Details

**Hardware:** 8× NVIDIA A100 GPUs (40GB), estimated 56 GPU-days total compute

**Software Stack:**
- PyTorch 2.0 with PyTorch Geometric for graph operations
- HuggingFace Transformers for text/time series encoders
- Custom VQ-VAE implementation based on AntixK/PyTorch-VAE

**Reproducibility:**
- Fixed random seeds (42, 123, 456 for three runs)
- All hyperparameters logged with Weights & Biases
- Code and trained models released on GitHub

**Timeline:**
- Weeks 1-4: Implementation + Stage 1 training
- Weeks 5-8: Stage 2 training + uncertainty calibration
- Weeks 9-10: Baseline training and evaluation
- Weeks 11-12: Ablation studies and statistical analysis

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Primary Hypothesis Validation:**
We expect MALS to achieve the following quantitative outcomes on the QM9 test set:

1. **Cross-Modal Retrieval Performance:**
   - Text→Graph top-5 accuracy: ≥70% (vs. 55-60% for modality-specific baselines)
   - Graph→Text top-5 accuracy: ≥75%
   - Time Series→Graph top-5 accuracy: ≥65%
   - Mean Reciprocal Rank (MRR): ≥0.60 across all modality pairs

2. **Uncertainty Quantification:**
   - Expected Calibration Error (ECE): ≤0.10 across all modalities
   - Conformal prediction coverage: 90% ± 2% (matching theoretical guarantee)
   - Average prediction set size: <15% of codebook size

3. **Reconstruction Quality:**
   - Graph validity: ≥95% (within 5% of modality-specific baseline)
   - SMILES exact match: ≥85% (within 10% of baseline)
   - Time series MSE: within 10% of baseline
   - Fréchet ChemNet Distance: <2.0

4. **Codebook Efficiency:**
   - Codebook utilization: ≥80%
   - Perplexity: ≥800 (for K=1024)

**Ablation Study Insights:**
- Optimal codebook size K=1024-2048 for QM9 dataset size
- Contrastive temperature τ=0.1 provides best alignment-diversity trade-off
- Staged training improves convergence speed by ~30% vs. joint training

**Falsification Criteria:**
The hypothesis will be considered falsified if:
- Cross-modal accuracy <50% (below random baseline)
- Codebook utilization <50% (indicating collapse)
- Any modality reconstruction >20% worse than baseline
- ECE >0.20 (worse than uncalibrated predictions)

### 4.2 Scientific Impact

**Theoretical Contributions:**

1. **Discrete Representation Theory:** This work will provide the first empirical evidence that discrete latent codes can unify heterogeneous structured modalities beyond grid-structured data. This extends VQ-VAE theory to non-Euclidean domains and establishes theoretical foundations for modality-agnostic discrete representations.

2. **Cross-Modal Learning Framework:** By combining discrete representation learning with contrastive alignment, we establish a new paradigm that bridges two previously separate research directions. This framework provides theoretical insights into how information bottlenecks (discretization) can enforce modality-agnostic abstraction.

3. **Uncertainty Quantification for Structured Data:** The integration of Conformal Prediction with discrete latent variable models provides distribution-free uncertainty guarantees for structured data—a significant advancement over existing heuristic approaches.

**Methodological Contributions:**

1. **Unified Architecture for Heterogeneous Data:** MALS reduces the engineering overhead from M separate models to a single unified framework, with immediate applications to any domain with multi-modal structured data.

2. **Scalable Training Strategy:** The staged training approach (2-modal → 3-modal) provides a principled methodology for incrementally adding modalities, applicable to systems with 4+ modalities.

3. **Calibrated Cross-Modal Transfer:** The combination of shared discrete codes with conformal prediction enables reliable cross-modal queries with quantified uncertainty—essential for high-stakes applications.

### 4.3 Practical Impact

**Drug Discovery Applications:**

1. **Text-to-Molecule Retrieval:** Chemists can query molecular databases using natural language descriptions ("aromatic compound with two hydroxyl groups and high binding affinity to protein X"), with calibrated confidence scores for each retrieved structure.

2. **Property Prediction with Uncertainty:** Predict molecular properties across modalities with distribution-free uncertainty bounds, enabling risk-aware decision-making in lead optimization.

3. **Cross-Modal Molecular Design:** Generate molecular structures conditioned on desired temporal binding profiles or textual property descriptions, with uncertainty quantification for generated candidates.

**Broader Scientific Applications:**

1. **Materials Science:** Unify crystal structures (graphs), chemical formulas (text), and thermal/mechanical property curves (time series) for materials discovery.

2. **Protein Engineering:** Integrate protein structures (graphs), amino acid sequences (text), and folding dynamics (time series) for protein design.

3. **Climate Modeling:** Combine spatial networks (graphs), textual event descriptions, and temporal climate signals for improved prediction and attribution.

**Computational Efficiency:**

- **Reduced Training Costs:** Single unified model vs. M separate models reduces training time by ~60%
- **Improved Sample Efficiency:** Cross-modal knowledge transfer enables learning from smaller datasets per modality
- **Inference Speedup:** Shared codebook enables efficient cross-modal queries via discrete code lookup

### 4.4 Limitations and Future Directions

**Known Limitations:**

1. **Modality Scalability:** Current design tested on 3 modalities; scaling to 5+ modalities may require hierarchical codebooks
2. **Domain Specificity:** Evaluation focused on molecular data; generalization to other scientific domains requires validation
3. **Computational Requirements:** Training requires significant GPU resources (56 A100-days), limiting accessibility

**Future Research Directions:**

1. **Hierarchical Discrete Codes:** Develop multi-scale codebooks (coarse + fine) to eliminate reconstruction vs. transfer trade-offs
2. **Active Learning Integration:** Use uncertainty estimates to guide data acquisition in multi-modal experimental design
3. **Causal Discovery:** Leverage cross-modal representations to identify causal relationships between molecular structure and properties
4. **Federated Multi-Modal Learning:** Extend MALS to privacy-preserving settings where modalities are distributed across institutions

### 4.5 Dissemination Plan

**Publications:**
- Primary venue: NeurIPS (Structured Probabilistic Inference & Generative Modeling track)
- Application paper: Journal of Chemical Information and Modeling
- Methods paper: Journal of Machine Learning Research

**Open Science:**
- Release code, trained models, and preprocessed datasets on GitHub
- Interactive demo for text-to-molecule retrieval on HuggingFace Spaces
- Tutorial notebooks for applying MALS to new domains

**Community Engagement:**
- Workshop presentation at NeurIPS Probabilistic Methods workshop
- Invited talks at computational chemistry conferences (ACS, RSC)
- Collaboration with pharmaceutical companies for real-world validation

This research establishes a new paradigm for probabilistic modeling of heterogeneous structured data, with immediate applications in drug discovery and broader implications for scientific machine learning. By successfully demonstrating that discrete latent codes can unify graphs, text, and time series with calibrated uncertainty, we provide both theoretical foundations and practical tools for the next generation of multi-modal scientific AI systems.