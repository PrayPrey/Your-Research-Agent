# Research Proposal

## Title
UniGenBench: A Hierarchical Three-Tier Benchmark Framework for Cross-Modal Evaluation of Generative Biomolecule Models

---

## 1. Introduction

### 1.1 Background

Generative artificial intelligence has catalyzed transformative advances in computational biology, enabling the de novo design of proteins, small molecule therapeutics, antibodies, and other biomolecules with unprecedented precision. Landmark achievements—including AlphaFold's protein structure prediction, diffusion-based protein design systems like RFDiffusion, and molecular generative models such as MolGPT—demonstrate that AI can now create functional biomolecules never before seen in nature. These capabilities hold profound implications for drug discovery, synthetic biology, and our fundamental understanding of molecular life.

Despite this remarkable progress, a critical bottleneck has emerged: the evaluation of generative biomolecule models remains fragmented and inconsistent. Current benchmarks operate in isolation—ProteinBench evaluates protein generators, MolGenBench assesses small molecule models, and antibody-specific metrics exist separately—each employing different quality criteria, normalization schemes, and validation protocols. This fragmentation creates several serious problems for the field:

**Cross-modal incomparability:** Researchers cannot meaningfully compare whether a protein generator achieves higher relative quality than a molecule generator, even when both target similar therapeutic applications. A protein design model scoring 0.85 on one benchmark cannot be compared to a molecule generator scoring 0.72 on another, as the metrics measure fundamentally different properties with different scales.

**Reproducibility failures:** Rankings of generative models frequently differ across laboratories due to inconsistent metric implementations, dataset preprocessing choices, and evaluation protocols. Studies have shown that model rankings can reverse entirely depending on which lab conducts the evaluation, wasting resources and obscuring genuine scientific advances.

**Diagnostic opacity:** When a generative model fails, current flat evaluation approaches provide limited insight into whether the failure stems from structural invalidity, poor quality optimization, or functional inadequacy. This diagnostic blindness impedes systematic model improvement.

### 1.2 Research Objectives

This proposal introduces **UniGenBench**, a hierarchical three-tier benchmark framework designed to establish the first unified evaluation standard for generative biology. Our primary objectives are:

1. **Develop a hierarchical evaluation architecture** that separates assessment into three distinct tiers: structural validity (Tier 1), normalized quality metrics (Tier 2), and functional verification (Tier 3).

2. **Achieve cross-modal evaluation consistency** with Kendall's tau correlation > 0.7 for model rankings across proteins, small molecules, and antibodies.

3. **Establish inter-laboratory reproducibility** with coefficient of variation (CV) < 10% across independent evaluation sites.

4. **Enable precise failure mode diagnosis** with > 90% precision in classifying model failures by tier.

5. **Quantify ranking uncertainty** through bootstrap estimation to identify unstable model comparisons.

### 1.3 Research Significance

UniGenBench addresses a fundamental infrastructure gap in generative biology. By establishing standardized, reproducible evaluation protocols, this work will:

- **Accelerate model development** by enabling researchers to identify specific weaknesses and compare approaches across modalities
- **Reduce wasted resources** by eliminating contradictory benchmark results that currently confuse the field
- **Enable meta-analyses** by providing comparable metrics across the generative biology literature
- **Bridge computational and experimental biology** through Tier 3 functional verification that correlates with wet-lab outcomes

Success would establish the evaluation foundation upon which the next generation of generative biomolecule models can be systematically developed and compared.

---

## 2. Methodology

### 2.1 Hierarchical Framework Architecture

UniGenBench implements a three-tier evaluation hierarchy where each tier serves a distinct purpose and models must pass lower tiers before higher-tier evaluation becomes meaningful.

#### Tier 1: Structural Validity

Tier 1 applies modality-specific rules to verify that generated structures are chemically and physically plausible. This binary pass/fail assessment filters invalid outputs before quality evaluation.

**For proteins:**
- Bond length validation: $d_{ij} \in [\mu_{bond} - 3\sigma, \mu_{bond} + 3\sigma]$ for all covalent bonds
- Ramachandran plot compliance: $\geq 90\%$ residues in allowed regions
- Clash detection: No atom pairs with $d_{ij} < 0.8 \times (r_i + r_j)$ where $r$ denotes van der Waals radii
- Chain connectivity: Continuous backbone with valid peptide bonds

**For small molecules:**
- Valence satisfaction: All atoms satisfy standard valence rules
- Ring strain: No rings with $> 8$ members unless biologically precedented
- Stereochemistry: Valid chiral centers with defined configurations
- Aromaticity: Consistent aromatic ring systems

**For antibodies:**
- Framework region integrity: Conserved residues present at canonical positions
- CDR loop validity: Complementarity-determining regions within length bounds
- Disulfide bond patterns: Canonical Cys-Cys pairings preserved
- VH-VL interface: Valid heavy-light chain pairing geometry

The Tier 1 validity score for a set of $N$ generated structures is:

$$V_1 = \frac{1}{N} \sum_{i=1}^{N} \mathbb{1}[\text{valid}(s_i)]$$

where $\mathbb{1}[\cdot]$ is the indicator function.

#### Tier 2: Normalized Quality Metrics

Tier 2 evaluates the quality of valid structures using modality-aware metrics normalized to enable cross-modal comparison. We define a normalized quality score:

$$Q_2^{(m)} = \frac{1}{|M_m|} \sum_{j \in M_m} \frac{q_j - q_j^{min}}{q_j^{max} - q_j^{min}}$$

where $M_m$ is the set of metrics for modality $m$, and $q_j^{min}, q_j^{max}$ are established bounds from reference datasets.

**Protein metrics ($M_{protein}$):**
- pLDDT (predicted local distance difference test): Structure confidence
- TM-score: Global structural similarity to targets
- GDT-TS: Global distance test for structure quality
- Designability: Inverse folding recovery rate

**Small molecule metrics ($M_{molecule}$):**
- QED (Quantitative Estimate of Drug-likeness): Drug-like property composite
- SA Score: Synthetic accessibility
- Validity rate: Fraction passing SMILES parsing
- Novelty: Tanimoto distance from training set

**Antibody metrics ($M_{antibody}$):**
- CDR RMSD: Root-mean-square deviation of CDR loops
- Paratope quality: Predicted binding interface score
- Humanness: Sequence similarity to human germline
- Developability: Aggregation and immunogenicity predictors

#### Tier 3: Functional Verification

Tier 3 correlates computational predictions with experimental outcomes where available. This tier uses Spearman correlation between predicted and measured functional properties:

$$F_3 = \rho(\hat{y}, y_{exp})$$

where $\hat{y}$ represents model-predicted functional scores and $y_{exp}$ represents experimental measurements (binding affinity, enzymatic activity, cellular efficacy, etc.).

### 2.2 Uncertainty Quantification

UniGenBench implements bootstrap uncertainty estimation to identify unstable rankings. For each metric, we compute confidence intervals via:

$$CI_{95} = [Q^*_{0.025}, Q^*_{0.975}]$$

where $Q^*$ values are obtained from $B = 1000$ bootstrap resamples of the evaluation dataset.

**Ranking stability analysis:** For each pair of models $(i, j)$, we compute the probability of ranking reversal:

$$P_{reversal}(i, j) = \frac{1}{B} \sum_{b=1}^{B} \mathbb{1}[rank_b(i) > rank_b(j)]$$

Rankings with $P_{reversal} \in [0.3, 0.7]$ are flagged as unstable.

### 2.3 Data Collection and Datasets

**Protein dataset:** We curate structures from the Protein Data Bank (PDB) with a temporal cutoff of January 2024 to prevent data leakage. The dataset includes:
- 10,000 monomeric proteins (50-500 residues)
- Stratified by CATH classification for structural diversity
- Experimental resolution $\leq 2.5$ Å

**Small molecule dataset:** We extract compounds from ChEMBL 33 with:
- 50,000 drug-like molecules (MW 200-600 Da)
- Bioactivity annotations against diverse targets
- Standardized using RDKit 2024.03

**Antibody dataset:** We compile structures from SAbDab (Structural Antibody Database):
- 5,000 antibody-antigen complexes
- Annotated CDR regions using IMGT numbering
- Binding affinity data where available

### 2.4 Experimental Design

#### Experiment 1: Cross-Modal Consistency Evaluation

**Objective:** Validate that UniGenBench achieves Kendall's tau > 0.7 for model rankings.

**Protocol:**
1. Select 30+ generative models: 12 protein generators (ESMFold, RFDiffusion, ProteinMPNN, etc.), 12 molecule generators (MolGPT, REINVENT, GraphAF, etc.), 8 antibody generators (IgLM, AntiBERTy, etc.)
2. Generate 1,000 structures per model per modality
3. Evaluate all structures through Tiers 1-3
4. Compute model rankings independently at each tier
5. Calculate Kendall's tau between rankings from different evaluation runs

**Comparison baseline:** Flat evaluation using raw metrics without hierarchical structure or normalization.

#### Experiment 2: Reproducibility Assessment

**Objective:** Demonstrate CV < 10% across independent evaluation sites.

**Protocol:**
1. Distribute UniGenBench to 3+ independent laboratories
2. Each lab evaluates identical model outputs using provided protocols
3. Compute coefficient of variation for each metric:

$$CV = \frac{\sigma_{sites}}{\mu_{sites}} \times 100\%$$

4. Compare against reproducibility of existing benchmarks (ProteinBench, MolGenBench)

#### Experiment 3: Failure Mode Diagnosis

**Objective:** Achieve > 90% precision in classifying failure modes.

**Protocol:**
1. Curate 500 known failure cases with ground-truth labels (validity failure, quality failure, functional failure)
2. Apply UniGenBench hierarchical evaluation
3. Classify failures based on which tier first indicates problems
4. Compute precision, recall, and F1-score against ground truth

#### Experiment 4: Ablation Study

**Objective:** Isolate each tier's contribution to evaluation consistency.

**Protocol:**
1. **Ablation A:** Remove Tier 1 (evaluate all structures regardless of validity)
2. **Ablation B:** Remove Tier 2 normalization (use raw metrics)
3. **Ablation C:** Remove Tier 3 (no functional verification)
4. **Ablation D:** Remove uncertainty quantification
5. Measure Kendall's tau degradation for each ablation

### 2.5 Evaluation Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| Kendall's tau ($\tau$) | Rank correlation coefficient | $\tau > 0.7$ |
| Coefficient of Variation (CV) | $\sigma/\mu \times 100\%$ | CV < 10% |
| Failure diagnosis precision | TP / (TP + FP) | > 90% |
| Failure diagnosis recall | TP / (TP + FN) | > 90% |
| Ranking reversal rate | Fraction of unstable pairs | Report |
| Intraclass correlation (ICC) | Inter-rater reliability | ICC > 0.8 |

### 2.6 Implementation Details

**Software stack:**
- RDKit 2024.03 for molecular processing
- ESMFold 1.0 for protein structure prediction
- DeepChem 2.8 for molecular property prediction
- BioPython for structural analysis
- All versions pinned for reproducibility

**Computational requirements:**
- Quick mode: ~1 GPU-hour per 1,000 structures
- Rigorous mode (with bootstrap): ~10 GPU-hours per 1,000 structures

**Code availability:** All code will be released under MIT license with Docker containers for reproducible execution.

---

## 3. Expected Outcomes & Impact

### 3.1 Primary Outcomes

**Outcome 1: Validated Hierarchical Framework**
We expect UniGenBench to achieve cross-modal ranking consistency with Kendall's tau > 0.7, significantly exceeding the tau < 0.5 observed with current flat evaluation approaches. This will demonstrate that hierarchical separation of validity, quality, and function provides meaningful evaluation structure.

**Outcome 2: Reproducible Evaluation Standard**
We anticipate inter-laboratory reproducibility with CV < 10%, compared to CV > 25% commonly observed with existing benchmarks. This will establish UniGenBench as a reliable standard for comparing results across research groups.

**Outcome 3: Diagnostic Capability**
The hierarchical structure should enable > 90% precision in failure mode classification, allowing researchers to identify whether model improvements should target structural validity, quality optimization, or functional relevance.

**Outcome 4: Uncertainty-Aware Rankings**
Bootstrap analysis is expected to reveal that 20-30% of model comparisons are unstable, providing crucial information about which performance differences are statistically meaningful.

### 3.2 Scientific Impact

**For generative biology research:**
UniGenBench will provide the first unified evaluation framework enabling systematic comparison across biomolecule modalities. Researchers will be able to identify whether advances in protein generation translate to molecule or antibody design, accelerating cross-pollination of methods.

**For drug discovery:**
Pharmaceutical companies will gain reliable benchmarks for selecting generative models, reducing the risk of adopting approaches that perform well on one benchmark but fail in practice. The functional verification tier will help bridge the gap between computational predictions and experimental outcomes.

**For reproducible science:**
By establishing standardized protocols with uncertainty quantification, UniGenBench will improve the reliability of published results and enable meaningful meta-analyses across the generative biology literature.

### 3.3 Broader Impact

**Community adoption:** Following the successful model of GEMv2 in NLP, we will engage the generative biology community through workshops, tutorials, and integration with popular model repositories. We target adoption by 10+ research groups within 12 months.

**Educational value:** UniGenBench will serve as a teaching resource for understanding evaluation best practices in generative biology, with documentation explaining the rationale for each design decision.

**Future extensions:** The modular architecture will support addition of new modalities (peptides, oligonucleotides, targeted degraders) and new metrics as the field evolves.

### 3.4 Risk Mitigation

**Risk 1:** Tier 3 functional data may be sparse for some modalities.
*Mitigation:* Tier 3 is optional; Tiers 1-2 provide value independently.

**Risk 2:** Community may resist adopting new standards.
*Mitigation:* Provide backward-compatible interfaces to existing benchmarks.

**Risk 3:** Computational overhead of rigorous mode may limit adoption.
*Mitigation:* Quick mode provides immediate utility; rigorous mode for publication-quality results.

---

## 4. Conclusion

UniGenBench addresses a critical infrastructure gap in generative biology by providing a hierarchical, reproducible, and uncertainty-aware benchmark framework. By separating evaluation into structural validity, normalized quality, and functional verification tiers, we enable meaningful cross-modal comparison while maintaining modality-specific rigor. Success will establish the evaluation foundation for the next generation of generative biomolecule models, accelerating progress toward AI-designed therapeutics and synthetic biology applications.