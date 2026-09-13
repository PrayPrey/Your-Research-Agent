# Research Proposal: Hypothesis-Driven Biological Discovery via LLM-Guided Knowledge Gap Detection and Experimental Design

## 1. Introduction

### Background

The biomedical research landscape is experiencing an unprecedented information explosion, with over one million scientific papers published annually in life sciences alone. This exponential growth creates a paradoxical challenge: while our collective biological knowledge expands rapidly, individual researchers struggle to synthesize findings across disciplines, identify meaningful knowledge gaps, and formulate novel hypotheses that connect disparate discoveries. Traditional literature review approaches remain largely manual, inherently biased toward familiar domains, and systematically miss cross-disciplinary connections that could catalyze breakthrough discoveries.

Simultaneously, generative AI has achieved remarkable successes in biology, from AlphaFold's protein structure prediction to diffusion-based models for de novo protein design. These tools can now design novel biomolecules with unprecedented precision. However, a critical bottleneck persists: identifying *which* molecules to design and *why* remains predominantly human-intuition-driven. This disconnect between our capacity to design and our ability to systematically identify what to design represents a fundamental barrier to accelerating scientific discovery.

Recent advances in large language models (LLMs) and graph neural networks (GNNs) offer promising avenues for addressing this challenge. The GAPMAP framework (Salem et al., 2025) demonstrated that LLMs can effectively identify both explicit and implicit knowledge gaps in biomedical literature. Concurrently, advances in graph representation learning for biomedical networks have shown success in predicting molecular interactions and uncovering hidden relationships in biological systems. However, no existing framework integrates these capabilities into a unified system that bridges knowledge gap identification with actionable experimental design.

### Research Objectives

This proposal introduces **BioGapFinder**, an integrated framework designed to:

1. **Systematically identify knowledge gaps** in biomedical literature by constructing and analyzing dynamic knowledge graphs using LLM-based information extraction
2. **Generate ranked, testable hypotheses** by combining graph-based link prediction with LLM-powered biological plausibility assessment
3. **Automate experimental design suggestions**, including recommendations for which generative AI tools could help validate each hypothesis
4. **Establish evaluation benchmarks** for retrospective and prospective validation of AI-generated biological hypotheses

### Significance

BioGapFinder addresses a fundamental challenge in generative biology: ensuring that AI-designed molecules address meaningful biological questions rather than technically impressive but scientifically irrelevant targets. By closing the loop between discovery and design, this framework could:

- Accelerate drug discovery by identifying unexplored therapeutic targets
- Enable cross-disciplinary discoveries by revealing connections invisible to domain-specific researchers
- Democratize hypothesis generation by providing researchers with AI-augmented literature synthesis
- Optimize resource allocation by prioritizing experimentally testable hypotheses with high potential impact

## 2. Methodology

### 2.1 Overview

BioGapFinder consists of four interconnected modules: (1) Dynamic Knowledge Graph Construction, (2) Graph-Based Knowledge Gap Detection, (3) Hypothesis Generation and Ranking, and (4) Experimental Design Automation. Figure 1 illustrates the overall architecture.

### 2.2 Module 1: Dynamic Knowledge Graph Construction

#### Data Collection

We will aggregate biomedical literature from multiple sources:
- **PubMed/MEDLINE**: Full abstracts and metadata for approximately 35 million biomedical papers
- **PubMed Central Open Access**: Full-text articles for deep extraction
- **Preprint servers**: bioRxiv and medRxiv for emerging findings
- **Existing databases**: UniProt, STRING, DrugBank, and KEGG for structured biological knowledge

#### LLM-Based Information Extraction

We employ a fine-tuned LLM (based on LLaMA-3 or GPT-4) for structured information extraction. For each document $d$, we extract:

**Entities** $E_d = \{e_1, e_2, ..., e_n\}$ categorized as:
- Genes/Proteins ($E_G$)
- Small molecules/Drugs ($E_M$)
- Diseases/Phenotypes ($E_D$)
- Biological processes ($E_P$)
- Cell types/Tissues ($E_C$)

**Relations** $R_d = \{r_1, r_2, ..., r_m\}$ with semantic types:
- Physical interactions (binds, phosphorylates)
- Regulatory relationships (activates, inhibits, upregulates)
- Disease associations (causes, treats, biomarker-of)
- Functional annotations (involved-in, located-in)

Each relation is represented as a tuple $(e_i, r_k, e_j, c_{ijk}, s_d)$ where $c_{ijk} \in [0,1]$ represents extraction confidence and $s_d$ contains source metadata (publication date, journal impact, citation count).

#### Knowledge Graph Assembly

The global knowledge graph $\mathcal{G} = (\mathcal{V}, \mathcal{E}, \mathcal{A})$ is constructed where:
- $\mathcal{V}$ = unified entity set after entity resolution
- $\mathcal{E}$ = aggregated edges with consolidated confidence scores
- $\mathcal{A}$ = temporal and provenance attributes

Edge confidence is computed as:

$$C_{ij} = 1 - \prod_{d \in D_{ij}} (1 - c_{ijk}^{(d)} \cdot w_d)$$

where $D_{ij}$ is the set of documents supporting edge $(i,j)$ and $w_d$ is a document reliability weight based on journal impact and citation metrics.

### 2.3 Module 2: Graph-Based Knowledge Gap Detection

#### Heterogeneous Graph Neural Network

We adapt a heterogeneous GNN architecture inspired by RUN-GNN and GPLP to learn entity and relation embeddings that capture both local topology and global graph structure.

**Node Embedding Update:**

$$h_v^{(l+1)} = \sigma\left(\sum_{r \in \mathcal{R}} \sum_{u \in \mathcal{N}_r(v)} \frac{1}{|\mathcal{N}_r(v)|} W_r^{(l)} h_u^{(l)} + W_0^{(l)} h_v^{(l)}\right)$$

where $\mathcal{N}_r(v)$ denotes neighbors of node $v$ under relation type $r$, and $W_r^{(l)}$ are relation-specific transformation matrices.

**Query-Aware Relation Composition:**

For modeling multi-hop reasoning paths, we employ a gated fusion mechanism:

$$g_t = \sigma(W_g[r_t; h_{path}^{t-1}])$$
$$h_{path}^t = g_t \odot \tanh(W_r r_t) + (1-g_t) \odot h_{path}^{t-1}$$

#### Missing Link Prediction

We formulate knowledge gap detection as a link prediction task. For a candidate triple $(e_i, r_k, e_j)$, we compute:

$$\phi(e_i, r_k, e_j) = f(h_{e_i}, h_{r_k}, h_{e_j})$$

where $f$ is a scoring function (we evaluate DistMult, RotatE, and a learned MLP-based scorer).

**Gap Score Computation:**

We define the "gap score" for a potential but unobserved link as:

$$\text{GapScore}(e_i, r_k, e_j) = \phi(e_i, r_k, e_j) \cdot (1 - \text{Obs}(e_i, r_k, e_j)) \cdot \text{Nov}(e_i, e_j)$$

where $\text{Obs}(\cdot)$ indicates whether the link is already observed and $\text{Nov}(\cdot)$ measures novelty based on research activity in the local neighborhood.

### 2.4 Module 3: Hypothesis Generation and Ranking

#### LLM-Based Plausibility Assessment

For each high-scoring candidate gap $(e_i, r_k, e_j)$, we construct a structured prompt for the LLM:

```
Given the biological entities [e_i description] and [e_j description], 
and the proposed relationship [r_k], evaluate:
1. Mechanistic plausibility (0-10): What biological mechanisms could explain this relationship?
2. Existing evidence (0-10): What indirect evidence supports or contradicts this hypothesis?
3. Testability (0-10): How feasible is experimental validation?
4. Impact potential (0-10): If true, how significant would this discovery be?
Provide detailed reasoning for each score.
```

#### Multi-Criteria Ranking

The final hypothesis score combines GNN predictions with LLM assessments:

$$H(e_i, r_k, e_j) = \alpha \cdot \text{GapScore} + \beta \cdot \text{Plausibility} + \gamma \cdot \text{Testability} + \delta \cdot \text{Impact}$$

where $\alpha, \beta, \gamma, \delta$ are learned weights calibrated on retrospective validation data.

#### Hypothesis Clustering and Synthesis

We cluster related hypotheses using semantic similarity of their LLM-generated explanations to identify coherent research directions rather than isolated predictions.

### 2.5 Module 4: Experimental Design Automation

For each top-ranked hypothesis, the system generates an experimental validation plan:

1. **Validation Strategy Selection**: Maps hypothesis types to experimental modalities (e.g., protein-protein interactions → co-IP, yeast two-hybrid, or structural prediction)

2. **Generative AI Tool Recommendation**: Suggests appropriate computational tools:
   - Protein design hypotheses → RFDiffusion, ProteinMPNN
   - Drug-target hypotheses → molecular docking, generative chemistry models
   - Regulatory hypotheses → perturbation modeling, gene expression prediction

3. **Resource Estimation**: Provides estimated cost, time, and expertise requirements

### 2.6 Experimental Validation

#### Retrospective Evaluation

**Benchmark Construction**: We create time-split benchmarks using papers from 2020-2023 for training and 2024 publications as ground truth. The task is to predict which novel relationships reported in 2024 papers could have been hypothesized from pre-2024 literature.

**Metrics**:
- Precision@K: Fraction of top-K predictions that match actual discoveries
- Recall@K: Fraction of actual discoveries captured in top-K predictions
- Mean Reciprocal Rank (MRR): Average reciprocal rank of true discoveries
- Biological Coherence Score: Expert evaluation of mechanistic explanations

#### Prospective Validation

We will collaborate with experimental biology laboratories to test 10-20 top-ranked novel hypotheses through wet-lab experiments over a 12-month period. Success metrics include:
- Hypothesis validation rate
- Time-to-validation compared to traditional discovery pipelines
- Quality of experimental design recommendations

#### Baseline Comparisons

We compare against:
- GAPMAP (LLM-only gap detection)
- Standard link prediction on biomedical KGs (TransE, ComplEx)
- Random hypothesis generation with matched novelty distribution
- Human expert panels for hypothesis ranking

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **BioGapFinder Framework**: An open-source, modular system integrating knowledge graph construction, gap detection, hypothesis generation, and experimental design automation

2. **Benchmark Datasets**: Curated retrospective benchmarks for evaluating biological hypothesis generation systems, including annotated knowledge gaps and validated discoveries

3. **Validated Hypotheses**: A ranked database of novel biological hypotheses with mechanistic explanations and suggested validation strategies

4. **Performance Metrics**: We anticipate achieving:
   - Precision@100 > 0.3 on retrospective benchmarks (30% of top predictions match actual discoveries)
   - >50% of generated hypotheses rated as "biologically plausible" by domain experts
   - >20% experimental validation rate for prospectively tested hypotheses

### Scientific Impact

BioGapFinder represents a paradigm shift from reactive to proactive scientific discovery. By systematically mapping the "unknown unknowns" in biological knowledge, we enable:

- **Accelerated Drug Discovery**: Identification of unexplored therapeutic targets and mechanisms before competitors
- **Cross-Disciplinary Innovation**: Automated detection of connections that siloed expertise misses
- **Resource Optimization**: Prioritization of high-impact experiments over incremental investigations

### Broader Impact

1. **Democratization of Discovery**: Researchers at resource-limited institutions gain access to sophisticated hypothesis generation previously available only to large research teams

2. **Training and Education**: The framework provides a teaching tool for training scientists in systematic literature analysis and hypothesis formulation

3. **Policy Applications**: Funding agencies could use gap analysis to identify underfunded but promising research areas

### Limitations and Future Work

We acknowledge potential limitations including LLM hallucination risks in hypothesis generation, biases inherited from literature (publication bias, Western-centric research), and the challenge of validating truly novel hypotheses that lack ground truth. Future work will address these through uncertainty quantification, bias detection modules, and expanded prospective validation partnerships.

## Conclusion

BioGapFinder addresses a critical bottleneck in modern biological research: the systematic identification of meaningful knowledge gaps and their translation into testable hypotheses. By integrating LLM-based literature understanding with graph neural network reasoning and automated experimental design, we create a closed-loop system that bridges the gap between generative AI's design capabilities and scientific discovery's strategic needs. This framework promises to accelerate biological discovery by ensuring that our powerful molecular design tools are directed toward the most impactful questions.