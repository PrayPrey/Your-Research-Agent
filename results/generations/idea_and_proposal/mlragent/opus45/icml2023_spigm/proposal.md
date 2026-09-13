# Research Proposal: Hierarchical Graph Grammars for Structured Molecular Generation with Principled Uncertainty Quantification

## 1. Introduction

### Background

The discovery of novel drug candidates remains one of the most challenging and resource-intensive endeavors in pharmaceutical research, with typical development cycles spanning 10-15 years and costing billions of dollars. Generative molecular modeling has emerged as a promising paradigm to accelerate early-stage drug discovery by computationally proposing novel molecules with desired properties. However, current approaches face a fundamental trilemma: they struggle to simultaneously guarantee chemical validity, capture the hierarchical compositional nature of molecular structures, and provide principled uncertainty quantification for generated candidates.

Existing molecular generative models broadly fall into three categories. First, SMILES-based approaches treat molecules as linear strings and leverage sequence models such as recurrent neural networks or transformers. While flexible, these methods frequently generate invalid molecules (often 10-40% invalidity rates) because the SMILES grammar imposes only weak structural constraints. Second, graph-based neural methods such as GraphVAE, Junction Tree VAE, and normalizing flow models like GraphDF directly operate on molecular graphs, achieving better validity rates but often lacking explicit mechanisms to capture hierarchical substructure patterns such as functional groups, ring systems, and pharmacophores that are fundamental to medicinal chemistry reasoning. Third, rule-based and grammar-guided methods can guarantee validity but typically lack the flexibility of neural approaches and, crucially, do not provide uncertainty estimates for their outputs.

The absence of reliable uncertainty quantification represents a critical gap for practical drug discovery applications. Medicinal chemists must prioritize which computationally-proposed molecules to synthesize and test experimentally—a costly and time-consuming process. Without calibrated confidence estimates, practitioners cannot distinguish between molecules the model generates with high confidence versus those representing speculative extrapolations. Recent work on conformal prediction for generative models, including the CPQ framework by Noorani et al. (2025), demonstrates growing interest in this problem but has not been specifically adapted for structured molecular generation with validity guarantees.

### Research Objectives

This research proposes a novel framework called **Hierarchical Grammar Networks (HGN)** that unifies stochastic graph grammars with deep generative models to address the aforementioned challenges. Our specific objectives are:

1. Develop a learnable hierarchical graph grammar framework where production rules are parameterized by graph neural networks, enabling both hard constraint satisfaction and flexible distribution learning over molecular structures.

2. Design a variational inference algorithm that treats grammar derivation sequences as latent variables, enabling principled posterior inference and uncertainty quantification through marginalization over derivation paths.

3. Establish rigorous uncertainty quantification methods that provide calibrated confidence estimates for generated molecules, leveraging both Bayesian treatment of grammar derivations and conformal prediction techniques.

4. Validate the framework on standard molecular generation benchmarks, demonstrating 100% validity by construction, competitive or superior diversity and novelty metrics, and well-calibrated uncertainty estimates.

### Significance

This research addresses a fundamental challenge at the intersection of structured probabilistic inference, generative modeling, and computational chemistry. By integrating the constraint-satisfaction guarantees of formal grammars with the flexibility of neural generative models and principled Bayesian uncertainty quantification, our framework will enable pharmaceutical researchers to trust and effectively utilize generative model outputs. The hierarchical grammar structure also provides inherent interpretability—chemists can inspect which production rules and substructure patterns the model employs, facilitating human-AI collaboration in drug design.

## 2. Methodology

### 2.1 Hierarchical Graph Grammar Formulation

We define a **Stochastic Context-Sensitive Hyperedge Replacement Grammar (SCHRG)** for molecular graphs. Formally, the grammar is specified as $\mathcal{G} = (N, T, S, \mathcal{R}, \theta)$, where:

- $N$ is a finite set of non-terminal hyperedge labels representing molecular fragments at various abstraction levels (e.g., "aromatic system," "hydrogen bond acceptor region")
- $T$ is a finite set of terminal symbols (atoms and bond types)
- $S \in N$ is the start symbol
- $\mathcal{R} = \{r_1, r_2, ..., r_K\}$ is a set of production rules
- $\theta$ represents neural network parameters governing rule selection probabilities

Each production rule $r_k: A \rightarrow G_k$ replaces a non-terminal hyperedge $A$ with a hypergraph fragment $G_k$ that may contain both terminal and non-terminal elements. Critically, rules are designed to preserve chemical validity invariants—every intermediate and final structure satisfies valence constraints, aromaticity rules, and other chemical validity criteria.

We organize rules into a three-level hierarchy:
- **Level 1 (Scaffold)**: Rules generating molecular scaffolds and core ring systems
- **Level 2 (Functional Group)**: Rules attaching functional groups and pharmacophoric features
- **Level 3 (Atomic)**: Rules completing atomic-level details and hydrogen atoms

### 2.2 Neural Parameterization of Rule Probabilities

Given a partial molecular graph $G_t$ at derivation step $t$ with a selected non-terminal hyperedge $e$ to expand, we parameterize the probability of selecting rule $r_k$ using a graph neural network:

$$P(r_k | G_t, e; \theta) = \frac{\exp(f_\theta(G_t, e)^\top w_k)}{\sum_{r_j \in \mathcal{R}_e} \exp(f_\theta(G_t, e)^\top w_j)}$$

where $\mathcal{R}_e \subseteq \mathcal{R}$ is the set of rules applicable to hyperedge $e$, $f_\theta(G_t, e)$ is a context embedding computed by a message-passing GNN, and $w_k$ are learnable rule embeddings.

The context embedding is computed as:

$$f_\theta(G_t, e) = \text{MLP}\left(\text{CONCAT}\left[h_e^{(L)}, \frac{1}{|V|}\sum_{v \in V} h_v^{(L)}\right]\right)$$

where $h_v^{(L)}$ denotes node embeddings after $L$ layers of graph attention:

$$h_v^{(\ell+1)} = h_v^{(\ell)} + \sum_{u \in \mathcal{N}(v)} \alpha_{uv}^{(\ell)} W^{(\ell)} h_u^{(\ell)}$$

with attention coefficients $\alpha_{uv}^{(\ell)}$ computed via multi-head attention mechanisms.

### 2.3 Variational Inference over Derivation Paths

For a molecular graph $G$, let $\mathbf{z} = (z_1, z_2, ..., z_T)$ denote the sequence of rule selections (latent variables) in a derivation producing $G$. The generative model defines:

$$P(G, \mathbf{z}; \theta) = \prod_{t=1}^{T} P(z_t | G_{t-1}, e_t; \theta)$$

where the final graph $G_T = G$. We introduce a recognition network $q_\phi(\mathbf{z} | G)$ that approximates the posterior over derivations given a target molecule. This recognition network operates by parsing the molecule top-down, predicting which rules were likely used:

$$q_\phi(\mathbf{z} | G) = \prod_{t=1}^{T} q_\phi(z_t | G, z_{1:t-1})$$

Training maximizes the evidence lower bound (ELBO):

$$\mathcal{L}(\theta, \phi) = \mathbb{E}_{q_\phi(\mathbf{z}|G)}\left[\log P(G, \mathbf{z}; \theta)\right] - D_{KL}\left(q_\phi(\mathbf{z}|G) \| P(\mathbf{z})\right)$$

For tighter bounds and better uncertainty estimates, we employ importance-weighted variational inference:

$$\mathcal{L}_K(\theta, \phi) = \mathbb{E}_{\mathbf{z}^{(1)}, ..., \mathbf{z}^{(K)} \sim q_\phi}\left[\log \frac{1}{K}\sum_{i=1}^{K} \frac{P(G, \mathbf{z}^{(i)}; \theta)}{q_\phi(\mathbf{z}^{(i)} | G)}\right]$$

### 2.4 Uncertainty Quantification Framework

We derive uncertainty estimates at multiple levels:

**Derivation Uncertainty**: For a generated molecule $G$, we estimate epistemic uncertainty by computing the entropy over derivation paths:

$$H[\mathbf{z} | G] \approx -\frac{1}{M}\sum_{m=1}^{M} \log q_\phi(\mathbf{z}^{(m)} | G)$$

where $\mathbf{z}^{(m)}$ are sampled derivations. High derivation entropy indicates the molecule can be constructed in many different ways, suggesting potential ambiguity.

**Predictive Uncertainty**: For property prediction tasks, we propagate uncertainty through derivations:

$$\text{Var}[y | G] = \mathbb{E}_{\mathbf{z}}[\text{Var}[y | G, \mathbf{z}]] + \text{Var}_{\mathbf{z}}[\mathbb{E}[y | G, \mathbf{z}]]$$

**Conformal Calibration**: Following recent work on conformal prediction for generative models, we construct prediction sets with coverage guarantees. Given a calibration set, we compute nonconformity scores based on negative log-likelihood under our model and apply split conformal prediction to construct sets of molecules with guaranteed coverage at level $1-\alpha$.

### 2.5 Experimental Design

**Datasets**: We evaluate on three standard benchmarks:
- ZINC-250K: 250,000 drug-like molecules for general molecular generation
- GuacaMol: Benchmark suite with multiple goal-directed generation tasks
- MOSES: Molecular Sets benchmark for distribution learning

**Baselines**: We compare against:
- SMILES-based: CharacterVAE, GrammarVAE, SMILES-LSTM
- Graph-based: GraphVAE, JT-VAE, GraphDF, MoFlow
- Recent methods: Foundation Molecular Grammar (FMG)

**Evaluation Metrics**:

1. *Validity*: Percentage of generated molecules passing RDKit sanitization
2. *Uniqueness*: Percentage of unique molecules among valid generations
3. *Novelty*: Percentage of generated molecules not in training set
4. *Diversity*: Average pairwise Tanimoto distance among generated molecules
5. *Fréchet ChemNet Distance (FCD)*: Distribution similarity to reference set
6. *Uncertainty Calibration*: Expected calibration error (ECE) for property predictions; empirical coverage of conformal prediction sets

**Ablation Studies**: We systematically evaluate contributions of (1) hierarchical grammar structure vs. flat rules, (2) neural parameterization vs. frequency-based probabilities, (3) importance-weighted bounds vs. standard ELBO, and (4) conformal calibration vs. raw posterior uncertainty.

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Guaranteed Chemical Validity**: By construction, our grammar-based approach will achieve 100% validity rates, eliminating the need for post-hoc filtering that reduces effective sample efficiency in existing methods.

2. **Improved Structural Diversity**: The hierarchical composition of substructures will enable more systematic exploration of chemical space, with expected diversity improvements of 15-25% over non-hierarchical baselines as measured by scaffold diversity metrics.

3. **Calibrated Uncertainty Estimates**: We expect to achieve expected calibration errors below 0.05 for property predictions, compared to typical values of 0.15-0.30 for uncalibrated neural generative models.

4. **Interpretable Generation Process**: The explicit grammar derivations will provide human-interpretable explanations of the generation process, enabling chemists to understand and critique model decisions.

5. **Competitive Generation Quality**: We anticipate achieving FCD scores within 5% of state-of-the-art methods while providing the additional benefits of validity guarantees and uncertainty quantification.

### Broader Impact

This research will directly impact computational drug discovery by providing pharmaceutical researchers with generative tools they can trust. Calibrated uncertainty estimates enable rational prioritization of synthesis candidates, potentially reducing wasted experimental resources by 20-30% in hit-to-lead optimization campaigns.

The framework also contributes to the broader agenda of structured probabilistic inference by demonstrating how formal language-theoretic constructs (grammars) can be integrated with modern deep learning while maintaining probabilistic coherence. This methodology extends naturally to other domains with compositional structure, including materials science (crystal generation), synthetic biology (pathway design), and program synthesis.

From a scientific perspective, this work bridges communities in machine learning, formal languages, and computational chemistry, establishing new connections between grammatical inference, variational methods, and molecular representation learning. The resulting codebase and pre-trained models will be released open-source to accelerate further research.

Finally, by providing interpretable generation processes, our framework supports the growing emphasis on explainable AI in high-stakes scientific applications, enabling meaningful human oversight of AI-assisted molecular design decisions.