# Research Proposal: Hierarchical Differentiable Attention Patterns for Genomic Long-Context Modeling (HP-Genome)

## 1. Title

**HP-Genome: Automated Discovery of Biologically Interpretable Sparse Attention Patterns for Long-Context Genomic Foundation Models via Hierarchical Differentiable Neural Architecture Search**

## 2. Introduction

### 2.1 Background

The emergence of foundation models has revolutionized artificial intelligence across multiple domains, yet their application to genomics faces unique challenges. Genomic sequences exhibit multi-scale hierarchical structures spanning orders of magnitude: from local regulatory motifs (promoters ~200 base pairs, enhancers ~500 bp) to chromosome-scale topologically associating domains (TADs ~1 Mbp). Recent genomic foundation models like GENERator process sequences up to 98,000 base pairs, requiring attention mechanisms that can capture dependencies across these diverse scales while maintaining computational tractability.

Current approaches to long-context genomic modeling face a critical dilemma. Dense attention mechanisms scale quadratically with sequence length ($O(L^2)$), becoming prohibitively expensive for sequences exceeding 10K tokens. Sparse attention patterns offer computational relief but typically rely on either: (1) fixed, domain-agnostic patterns (e.g., strided, dilated, or random attention) that ignore biological structure, or (2) manually engineered domain-specific patterns requiring months of expert knowledge and iterative refinement. The GENERator model exemplifies the latter approach, achieving strong performance through carefully designed attention patterns informed by genomic domain expertise.

This manual engineering bottleneck represents a fundamental limitation in scaling foundation models to new biological domains. Each organism, genomic region type, or analytical task may require different attention patterns optimized for its specific regulatory architecture. Furthermore, manually designed patterns may miss novel biological structures not yet characterized in the literature, limiting the potential for AI-driven scientific discovery.

Recent advances in neural architecture search (NAS) and differentiable attention mechanisms suggest a potential solution. Works like DARTS have demonstrated gradient-based architecture optimization, while SPARSEK has shown that learned sparse attention masks can match dense attention performance. However, these approaches have not been adapted to: (1) hierarchical multi-scale biological structures, (2) domain-specific interpretability requirements, or (3) genomic sequence modeling.

### 2.2 Research Objectives

This research proposes **HP-Genome** (Hierarchical Pattern-learning for Genomics), a novel framework that automatically discovers biologically interpretable sparse attention patterns through hierarchical differentiable neural architecture search. Our primary objectives are:

**Objective 1 (Performance):** Develop a hierarchical attention learning framework that matches manually designed genomic baselines (GENERator) within ±5% perplexity while maintaining sparse attention (≤15% density).

**Objective 2 (Interpretability):** Ensure learned attention patterns align with known biological regulatory structures (promoters, enhancers, TADs) with intersection-over-union (IoU) ≥ 0.70 against ENCODE and JASPAR annotations.

**Objective 3 (Automation):** Eliminate manual attention pattern engineering by enabling end-to-end gradient-based optimization of pattern selection, reducing development time from months to weeks.

**Objective 4 (Scientific Discovery):** Validate whether learned patterns reveal novel regulatory structures not captured by existing annotations, enabling AI-driven biological hypothesis generation.

### 2.3 Research Significance

This research addresses critical challenges in long-context foundation models across three dimensions:

**Methodological Significance:** HP-Genome introduces the first hierarchical differentiable NAS framework specifically designed for attention pattern discovery within transformers. Unlike DARTS (which searches full architectures) or SPARSEK (which learns flat single-scale masks), our approach searches a biologically motivated two-level hierarchy: local patterns (0-4K bp) for regulatory motifs and global patterns (4K-98K bp) for chromosome-scale dependencies. This represents a novel integration of neuroscience-inspired hierarchical temporal memory principles with modern transformer architectures.

**Practical Significance:** By automating attention pattern discovery, HP-Genome democratizes genomic foundation model development. Researchers without deep genomics expertise can adapt models to new organisms, genomic regions, or tasks without months of manual pattern engineering. The explicit biological interpretability validation (IoU with regulatory annotations) ensures learned patterns remain scientifically meaningful, addressing the "black box" criticism often leveled at deep learning in biology.

**Scientific Significance:** Learned attention patterns validated against biological annotations may reveal novel regulatory structures or dependencies not yet characterized in genomic databases. If HP-Genome discovers patterns that improve performance but diverge from existing annotations, these discrepancies warrant experimental validation, potentially uncovering new biological mechanisms. This positions AI as a hypothesis generation tool for genomics research.

**Broader Impact:** Success in genomics establishes a template for applying hierarchical differentiable attention learning to other long-context domains with multi-scale structure (e.g., protein sequences, medical records, legal documents, climate data). The framework's emphasis on domain-specific interpretability provides a roadmap for responsible AI deployment in scientific domains requiring human-verifiable explanations.

## 3. Methodology

### 3.1 Data Collection and Preparation

**Dataset:** We utilize the ENCODE (Encyclopedia of DNA Elements) database, focusing on regulatory regions from the human genome (hg38 assembly). Our dataset comprises:

- **Training Set:** 8,000 sequences × 98,304 bp (98K bp, matching GENERator context length)
- **Validation Set:** 1,000 sequences × 98K bp
- **Test Set:** 1,000 sequences × 98K bp

Sequences are selected from diverse genomic contexts (promoter-proximal, enhancer-rich, gene-desert regions) to ensure representativeness. Each sequence is tokenized using 6-mer encoding (vocabulary size 4,096), reducing sequence length to ~16,384 tokens while preserving local motif information.

**Biological Annotations:** For interpretability validation, we compile multi-scale annotations:

- **Local Scale (0-4K bp):** JASPAR transcription factor binding motifs, ENCODE promoter/enhancer annotations
- **Global Scale (4K-98K bp):** Hi-C topologically associating domain (TAD) boundaries, ENCODE chromatin interaction data

Annotations are converted to binary masks aligned with tokenized sequences for IoU computation.

### 3.2 HP-Genome Architecture

#### 3.2.1 Hierarchical Attention Framework

HP-Genome employs a two-level hierarchical attention structure motivated by biological multi-scale organization:

**Level 1 - Local Attention (0-4K bp):** Captures regulatory motifs and cis-regulatory elements. For each query position $i$, local attention is computed over a learned window:

$$A_{\text{local}}^{(h)}(i, j) = \begin{cases} 
\text{softmax}_j\left(\frac{Q_i K_j^T}{\sqrt{d_k}}\right) & \text{if } |i - j| \leq w_{\text{local}}(i; \alpha_L) \\
0 & \text{otherwise}
\end{cases}$$

where $w_{\text{local}}(i; \alpha_L)$ is a position-dependent window size selected from templates $\{128, 256, 512, 1024\}$ bp via differentiable selection (detailed in Section 3.2.2).

**Level 2 - Global Attention (4K-98K bp):** Captures long-range chromosome-scale dependencies. Global attention employs strided, dilated, or random sparse patterns:

$$A_{\text{global}}^{(h)}(i, j) = \begin{cases}
\text{softmax}_j\left(\frac{Q_i K_j^T}{\sqrt{d_k}}\right) & \text{if } j \in \mathcal{S}_{\text{global}}(i; \alpha_G) \\
0 & \text{otherwise}
\end{cases}$$

where $\mathcal{S}_{\text{global}}(i; \alpha_G)$ is a sparse index set selected from templates:
- **Strided:** $\{j : (j - i) \mod s = 0\}$ for $s \in \{2, 4, 8, 16\}$
- **Dilated:** $\{j : |j - i| = d \cdot k, k \in \mathbb{Z}\}$ for $d \in \{2, 4, 8, 16\}$
- **Random:** Uniform sampling of $\{1\%, 5\%\}$ of positions

**Fusion:** Local and global attention are combined via learned fusion weights:

$$A^{(h)}(i, j) = \lambda_L(\alpha_F) \cdot A_{\text{local}}^{(h)}(i, j) + \lambda_G(\alpha_F) \cdot A_{\text{global}}^{(h)}(i, j)$$

where $\lambda_L, \lambda_G = \text{softmax}(\alpha_F)$ and $\alpha_F \in \mathbb{R}^2$ are learnable fusion parameters.

#### 3.2.2 Differentiable Pattern Selection

Pattern selection is formulated as a continuous relaxation of discrete template choice, enabling gradient-based optimization:

**Local Pattern Selection:** For each attention head $h$, local window size is computed as:

$$w_{\text{local}}^{(h)}(i) = \sum_{k=1}^{4} p_k^{(h)} \cdot w_k$$

where $w_k \in \{128, 256, 512, 1024\}$ are template window sizes and $p_k^{(h)} = \frac{\exp(\alpha_{L,k}^{(h)} / \tau)}{\sum_{j=1}^{4} \exp(\alpha_{L,j}^{(h)} / \tau)}$ are softmax-normalized selection probabilities. $\alpha_L^{(h)} \in \mathbb{R}^4$ are learnable architecture parameters, and $\tau$ is a temperature parameter (initially 1.0, annealed to 0.1 during training).

**Global Pattern Selection:** Similarly, global sparse patterns are selected via:

$$\mathcal{S}_{\text{global}}^{(h)}(i) = \bigcup_{k=1}^{10} \mathbb{1}[p_k^{(h)} > \epsilon] \cdot \mathcal{S}_k(i)$$

where $\mathcal{S}_k$ are the 10 template patterns (4 strided + 4 dilated + 2 random), $p_k^{(h)} = \text{softmax}(\alpha_{G,k}^{(h)} / \tau)$, and $\epsilon = 0.01$ is a pruning threshold. During training, we use the continuous relaxation:

$$A_{\text{global}}^{(h)}(i, j) = \sum_{k=1}^{10} p_k^{(h)} \cdot A_k^{(h)}(i, j)$$

where $A_k^{(h)}$ is attention computed using template $k$.

**Discretization:** After training, we discretize patterns by selecting $\arg\max_k p_k^{(h)}$ for each head, yielding a fixed sparse pattern for efficient inference.

#### 3.2.3 Training Objective

The complete training objective balances task performance with sparsity:

$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{task}} + \lambda_{\text{sparse}} \cdot \mathcal{L}_{\text{sparsity}} + \lambda_{\text{reg}} \cdot \mathcal{L}_{\text{reg}}$$

**Task Loss (Next-Nucleotide Prediction):**
$$\mathcal{L}_{\text{task}} = -\frac{1}{N} \sum_{i=1}^{N} \log P(x_i | x_{<i}; \theta, \alpha)$$

where $\theta$ are model weights and $\alpha = \{\alpha_L, \alpha_G, \alpha_F\}$ are architecture parameters.

**Sparsity Loss:**
$$\mathcal{L}_{\text{sparsity}} = \frac{1}{H \cdot L^2} \sum_{h=1}^{H} \sum_{i,j} \mathbb{1}[A^{(h)}(i,j) > 0]$$

measuring average attention density across $H$ heads and sequence length $L$.

**Regularization Loss:**
$$\mathcal{L}_{\text{reg}} = \sum_{h=1}^{H} \left( \|\alpha_L^{(h)}\|_2^2 + \|\alpha_G^{(h)}\|_2^2 \right)$$

preventing architecture parameter explosion.

**Hyperparameters:**
1. Learning rate: $\eta = 1 \times 10^{-4}$ (AdamW optimizer)
2. Sparsity weight: $\lambda_{\text{sparse}} \in \{0.01, 0.05, 0.1\}$ (tuned on validation)
3. Temperature: $\tau$ annealed from 1.0 to 0.1 over 50 epochs
4. Fusion weight initialization: $\alpha_F = [0, 0]$ (equal weighting initially)

### 3.3 Baseline Models

**Primary Baseline - GENERator:** We compare against the GENERator genomic foundation model, which employs manually designed attention patterns optimized for regulatory sequence modeling. We replicate GENERator's architecture (12 layers, 768 hidden dimensions, 12 attention heads) but replace its fixed attention patterns with our learned hierarchical patterns.

**Secondary Baselines:**
- **Dense Attention:** Standard transformer with full $O(L^2)$ attention (upper bound on performance)
- **Fixed Sparse Patterns:** π-Attention (periodic patterns), random sparse (5% density)
- **Flat Learned Patterns:** SPARSEK-style single-scale learned masks (ablation control)

### 3.4 Experimental Design

#### 3.4.1 Training Protocol

**Phase 1 - Joint Training (Epochs 1-100):**
- Simultaneously optimize model weights $\theta$ and architecture parameters $\alpha$
- Temperature annealing: $\tau(t) = \max(0.1, 1.0 - 0.9 \cdot t/50)$ for $t \in [0, 50]$
- Sparsity weight warmup: $\lambda_{\text{sparse}}(t) = \lambda_{\text{final}} \cdot \min(1, t/20)$

**Phase 2 - Discretization (Epoch 101):**
- Discretize patterns: $k^{(h)*} = \arg\max_k p_k^{(h)}$
- Freeze architecture parameters $\alpha$

**Phase 3 - Fine-tuning (Epochs 102-120):**
- Fine-tune model weights $\theta$ with fixed discrete patterns
- Standard cross-entropy loss (no sparsity penalty)

**Computational Resources:** Training on single NVIDIA A100 GPU (40GB), estimated 7 days per model run.

#### 3.4.2 Evaluation Metrics

**Primary Metric - Perplexity:**
$$\text{PPL} = \exp\left(-\frac{1}{N} \sum_{i=1}^{N} \log P(x_i | x_{<i})\right)$$

computed on held-out test sequences. Success criterion: $\text{PPL}_{\text{HP-Genome}} \leq 1.05 \cdot \text{PPL}_{\text{GENERator}}$.

**Biological Interpretability - Intersection-over-Union (IoU):**

For each annotation type $a \in \{\text{promoters, enhancers, TADs}\}$:

$$\text{IoU}_a = \frac{|\mathcal{A}_{\text{attention}} \cap \mathcal{A}_a|}{|\mathcal{A}_{\text{attention}} \cup \mathcal{A}_a|}$$

where $\mathcal{A}_{\text{attention}}$ are positions with attention weight > 0.1, and $\mathcal{A}_a$ are annotated positions. Success criterion: $\text{IoU}_a \geq 0.70$ for at least two annotation types.

**Sparsity Density:**
$$\rho = \frac{1}{H \cdot L^2} \sum_{h=1}^{H} \sum_{i,j} \mathbb{1}[A^{(h)}(i,j) > 0]$$

Success criterion: $\rho \leq 0.15$ (15% density).

**Generalization Gap:**
$$\Delta_{\text{gen}} = \frac{\text{PPL}_{\text{val}} - \text{PPL}_{\text{train}}}{\text{PPL}_{\text{train}}}$$

Success criterion: $\Delta_{\text{gen}} \leq 0.10$ (10% gap).

#### 3.4.3 Statistical Testing

**Sample Size Calculation:** For perplexity comparison (primary outcome), we require $N = 175$ sequences per condition to detect Cohen's $d = 0.3$ effect size with $\alpha = 0.05$, power $= 0.80$ (two-sample t-test). Our test set of 1,000 sequences provides sufficient power.

**Hypothesis Tests:**

1. **HP-Genome vs. GENERator (Performance):**
   - $H_0$: $\mu_{\text{PPL, HP}} > 1.05 \cdot \mu_{\text{PPL, GEN}}$
   - $H_1$: $\mu_{\text{PPL, HP}} \leq 1.05 \cdot \mu_{\text{PPL, GEN}}$
   - Test: One-tailed independent t-test, $\alpha = 0.05$

2. **Biological Alignment vs. Random (Interpretability):**
   - $H_0$: $\mu_{\text{IoU}} \leq \mu_{\text{IoU, random}}$ (random baseline $\approx 0.15$)
   - $H_1$: $\mu_{\text{IoU}} > 0.70$
   - Test: One-sample t-test, $\alpha = 0.05$

3. **Ablation Studies:**
   - 2-level vs. 1-level hierarchy (paired t-test)
   - Learned vs. best fixed pattern (paired t-test)
   - Bonferroni correction: $\alpha_{\text{corrected}} = 0.0125$ (4 comparisons)

**Replication:** All experiments run with 3 random seeds; results reported as mean ± standard deviation with 95% confidence intervals.

#### 3.4.4 Ablation Studies

**Ablation 1 - Hierarchy Necessity:**
- **Condition:** Single-level flat learned patterns (no local/global separation)
- **Hypothesis:** 2-level outperforms 1-level by ≥5% perplexity
- **Rationale:** Tests whether biological hierarchy improves learning

**Ablation 2 - Learning Benefit:**
- **Condition:** Best fixed pattern (grid search over strided/dilated combinations)
- **Hypothesis:** Learned patterns outperform best fixed by ≥3%
- **Rationale:** Validates necessity of differentiable search

**Ablation 3 - Sparsity Sensitivity:**
- **Condition:** Vary $\lambda_{\text{sparse}} \in \{0.001, 0.01, 0.05, 0.1, 0.5\}$
- **Analysis:** Plot perplexity vs. density trade-off curve
- **Rationale:** Identifies optimal sparsity-performance operating point

**Ablation 4 - Template Coverage:**
- **Condition:** Expand templates to include genomics-specific patterns (e.g., motif-aware windows at 200bp, 500bp)
- **Hypothesis:** Domain-specific templates improve IoU by ≥10%
- **Rationale:** Tests whether generic templates suffice or domain knowledge helps

### 3.5 Interpretability Analysis

**Attention Pattern Visualization:**
- Generate heatmaps of learned attention patterns overlaid with ENCODE/JASPAR annotations
- Cluster attention heads by pattern similarity (hierarchical clustering on pattern matrices)
- Identify "specialist" heads (high IoU with single annotation type) vs. "generalist" heads

**Novel Pattern Discovery:**
- Extract high-attention regions with low annotation overlap (IoU < 0.3)
- Cross-reference with recent genomic literature (post-ENCODE publications)
- Propose candidate novel regulatory elements for experimental validation

**Biological Validation Protocol:**
- For top 10 novel high-attention regions:
  - Check conservation across species (PhyloP scores)
  - Analyze chromatin accessibility (ATAC-seq data)
  - Predict transcription factor binding (motif scanning)
- Collaborate with experimental genomics labs for CRISPR validation (future work)

### 3.6 Computational Efficiency Analysis

**Metrics:**
- Training time (hours per epoch)
- Inference latency (ms per sequence)
- Memory footprint (GB)
- FLOPs (floating-point operations per forward pass)

**Comparison:** Benchmark HP-Genome against dense attention and GENERator on identical hardware, reporting speedup factors and memory reduction percentages.

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Outcome 1 - Performance Parity:** We expect HP-Genome to achieve perplexity within 3-5% of GENERator on held-out ENCODE test sequences, demonstrating that automated pattern discovery matches manual engineering. Conservative estimate: 5% margin; optimistic: 2% margin or better.

**Outcome 2 - Biological Interpretability:** Learned attention patterns will exhibit IoU ≥ 0.70 with at least two of three annotation types (promoters, enhancers, TADs). We anticipate strongest alignment with promoters (local patterns) and TADs (global patterns), with moderate alignment for enhancers (which span both scales).

**Outcome 3 - Sparse Efficiency:** Final models will maintain attention density ≤ 12% (below 15% threshold), achieving ~8× speedup over dense attention and ~2× speedup over GENERator's manually designed patterns.

**Outcome 4 - Hierarchy Validation:** Ablation studies will demonstrate that 2-level hierarchy outperforms 1-level flat patterns by 5-8% perplexity, confirming the value of multi-scale biological structure modeling.

**Outcome 5 - Novel Discovery:** We expect to identify 5-10 high-confidence novel regulatory regions (high attention, low annotation overlap, high conservation) warranting experimental follow-up, demonstrating AI-driven hypothesis generation.

### 4.2 Scientific Impact

**Genomics Foundation Models:** HP-Genome establishes a new paradigm for genomic model development, replacing months of manual attention engineering with automated gradient-based search. This democratizes access to state-of-the-art genomic AI, enabling researchers without deep domain expertise to build competitive models for new organisms (mouse, zebrafish, plants) or genomic contexts (coding regions, repetitive elements).

**Interpretable AI for Biology:** By explicitly validating learned patterns against biological annotations, HP-Genome addresses the interpretability crisis in AI-driven biology. The framework provides a template for domain-specific interpretability validation applicable to protein structure prediction, drug discovery, and systems biology.

**AI-Driven Discovery:** If learned patterns reveal novel regulatory elements validated experimentally, this demonstrates AI's potential as a hypothesis generation tool rather than mere pattern recognition. This could accelerate genomic annotation efforts, particularly for non-model organisms with sparse experimental data.

### 4.3 Methodological Impact

**Long-Context Foundation Models:** HP-Genome's hierarchical differentiable attention search generalizes beyond genomics to any domain with multi-scale structure:
- **Medical Records:** Local (symptom clusters) + Global (disease progression)
- **Legal Documents:** Local (clause-level) + Global (cross-reference networks)
- **Climate Data:** Local (weather patterns) + Global (seasonal cycles)

**Neural Architecture Search:** Our focused search over attention patterns (rather than full architectures) reduces search space complexity while maintaining biological interpretability. This "constrained NAS" approach balances automation with domain knowledge integration, offering a middle ground between fully manual design and unconstrained black-box search.

**Neuroscience-Inspired AI:** The hierarchical temporal memory principles underlying HP-Genome's design demonstrate productive cross-pollination between neuroscience and deep learning. This may inspire further biologically motivated architectural innovations.

### 4.4 Practical Impact

**Computational Efficiency:** Sparse learned patterns reduce inference costs for genomic foundation models, enabling deployment on resource-constrained platforms (edge devices, clinical settings). An 8× speedup translates to processing 8× more patient genomes per dollar, directly impacting precision medicine scalability.

**Open-Source Release:** We will release HP-Genome code, pretrained models, and learned attention patterns as open-source resources, accelerating community adoption. Pretrained patterns can serve as initialization for new genomic tasks, reducing training time.

**Industry Applications:** Pharmaceutical companies and biotech startups developing genomic AI for drug target identification, variant effect prediction, and personalized medicine can adopt HP-Genome to reduce model development cycles from 6-12 months to 2-3 months.

### 4.5 Broader Societal Impact

**Equitable Access:** By reducing the expertise barrier for genomic AI development, HP-Genome enables researchers in low-resource settings (developing countries, small institutions) to build competitive models, promoting global equity in genomic medicine.

**Responsible AI:** Explicit interpretability validation ensures learned patterns remain scientifically meaningful, reducing risks of spurious correlations or biologically implausible predictions that could mislead clinical decisions.

**Educational Value:** HP-Genome's transparent pattern learning process serves as an educational tool for teaching AI-biology integration, helping train the next generation of computational biologists.

### 4.6 Limitations and Future Directions

**Limitations:**
- **Annotation Dependence:** Interpretability validation relies on existing annotations (ENCODE, JASPAR), which may be incomplete or biased toward well-studied genomic regions.
- **Single Organism:** Initial validation focuses on human genome; cross-species generalization requires additional validation.
- **Computational Cost:** While inference is efficient, training requires GPU resources that may limit accessibility.

**Future Directions:**
1. **Cross-Domain Transfer:** Extend to protein sequences (AlphaFold-style structure prediction) and RNA (secondary structure modeling)
2. **3-Level Hierarchy:** Add intermediate "meso" scale (1K-16K bp) for gene-level regulatory networks
3. **Meta-Learning:** Learn to adapt patterns across organisms/tasks with few-shot learning
4. **Experimental Validation:** Collaborate with wet-lab genomics teams to CRISPR-validate novel predicted regulatory elements
5. **Clinical Deployment:** Apply to variant effect prediction in clinical genomics pipelines

### 4.7 Success Metrics and Timeline

**6-Month Milestones:**
- Month 1-2: Implementation and initial training (SH1 - technical feasibility)
- Month 3-4: Baseline comparisons and performance validation (SH3)
- Month 5: Interpretability analysis (SH2)
- Month 6: Ablation studies and manuscript preparation (SH4, SH5)

**Success Criteria:**
- **Full Success:** All four predictions (P1-P4) met, 2+ ablations significant
- **Partial Success:** P1 + P2 met (performance + interpretability), ablations mixed
- **Failure (Pivot Required):** P1 fails by >10% margin after extensive tuning

**Dissemination Plan:**
- Submit to NeurIPS Workshop on Long-Context Foundation Models (primary venue)
- Follow-up full paper to Nature Methods or Bioinformatics (if experimental validation completed)
- Preprint on bioRxiv + arXiv for rapid community feedback
- Open-source release on GitHub with documentation and tutorials

---

**Conclusion:** HP-Genome represents a principled integration of biological domain knowledge, modern deep learning, and neural architecture search to address the critical challenge of automated, interpretable, and efficient long-context modeling in genomics. By validating learned patterns against biological ground truth while maintaining performance parity with manually engineered baselines, this research establishes a new paradigm for domain-specific foundation model development with broad applicability across scientific AI.