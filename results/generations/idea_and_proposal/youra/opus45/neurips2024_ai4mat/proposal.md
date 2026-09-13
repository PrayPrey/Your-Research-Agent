# Research Proposal: Hierarchical Cross-Modal Binding Networks for Robust Multimodal Materials Property Prediction

## 1. Title

**HCMB-Net: A Hierarchical Cross-Modal Binding Architecture for Scalable and Robust Multimodal Materials Property Prediction Under Incomplete Data Conditions**

---

## 2. Introduction

### 2.1 Background

The intersection of artificial intelligence and materials science holds transformative potential for accelerating the discovery and design of novel materials with targeted properties. While adjacent fields such as drug discovery, computational biology, and natural language processing have witnessed exponential growth driven by AI innovations, materials science has yet to experience comparable breakthroughs. A critical barrier to this progress lies in the unique challenges posed by materials characterization data: it is inherently multimodal, frequently incomplete, and collected from diverse experimental equipment with varying fidelity and coverage.

Modern materials characterization generates data across multiple modalities—compositional information, crystal structure coordinates, X-ray diffraction (XRD) patterns, spectroscopic measurements, and electron microscopy images. Each modality captures complementary aspects of material properties: composition reveals elemental makeup, crystal structure encodes atomic arrangements and symmetries, while XRD patterns provide fingerprints of phase purity and crystallinity. However, real-world materials datasets exhibit significant modality dropout, with 10-50% of samples missing one or more characterization modalities due to experimental constraints, equipment availability, or measurement costs.

Existing approaches to multimodal materials learning remain limited in scope and robustness. COSNet, a recent state-of-the-art method, demonstrates effective bimodal fusion of composition and structure but cannot scale beyond two modalities. General-purpose multimodal fusion architectures from computer vision and natural language processing lack the domain-specific inductive biases necessary for materials science—they fail to respect physical symmetries (e.g., rotational equivariance for crystal structures) and cannot leverage materials-specific feature representations. Furthermore, no existing framework provides graceful degradation under arbitrary modality dropout while scaling to three or more characterization modalities.

### 2.2 Research Objectives

This research proposes HCMB-Net (Hierarchical Cross-Modal Binding Network), a novel architecture designed to address the fundamental challenges of multimodal, incomplete materials data. Our primary objectives are:

1. **Develop a scalable multimodal fusion architecture** that unifies arbitrary numbers of materials characterization modalities through domain-appropriate encoders and hierarchical attention mechanisms.

2. **Achieve robust property prediction under modality dropout** by designing attention masking strategies that enable graceful performance degradation when modalities are missing.

3. **Demonstrate superior performance over existing methods** on large-scale materials datasets, specifically targeting formation energy and band gap prediction on the Alexandria dataset (5M samples).

4. **Validate the hierarchical binding mechanism** through systematic ablation studies comparing against flat attention baselines and single-modality approaches.

### 2.3 Significance

This research addresses a critical gap identified by the AI4Mat community: the need for machine learning frameworks that can handle the multimodal, incomplete nature of real-world materials data. By bridging the scalability of general multimodal architectures with materials-specific inductive biases, HCMB-Net has the potential to:

- Enable more comprehensive materials property prediction by leveraging all available characterization data
- Reduce experimental costs by maintaining prediction accuracy even when some measurements are unavailable
- Provide a foundation for integrating emerging characterization modalities as materials science instrumentation evolves
- Accelerate the transition from AI-driven materials discovery to real-world impact by handling the messy realities of experimental data

---

## 3. Methodology

### 3.1 Overall Architecture

HCMB-Net employs a three-stage architecture: (1) modality-specific encoding, (2) contrastive cross-modal alignment, and (3) hierarchical attention binding. This design ensures that domain-specific physical constraints are respected during encoding, modalities are projected into a shared semantic space for meaningful comparison, and the final fusion mechanism scales gracefully with the number of modalities while handling missing data.

### 3.2 Stage 1: Modality-Specific Encoding

Each characterization modality is processed by a domain-appropriate encoder that preserves relevant physical information.

**Composition Encoder ($E_{\text{comp}}$):**
We employ a hybrid approach combining Magpie-style handcrafted elemental features with learned embeddings. For a material with composition $\{(e_i, f_i)\}_{i=1}^{n}$ where $e_i$ is element type and $f_i$ is fractional occupancy:

$$\mathbf{h}_{\text{comp}} = \text{MLP}\left(\sum_{i=1}^{n} f_i \cdot (\mathbf{m}_{e_i} \oplus \mathbf{w}_{e_i})\right)$$

where $\mathbf{m}_{e_i} \in \mathbb{R}^{145}$ are Magpie features, $\mathbf{w}_{e_i} \in \mathbb{R}^{64}$ are learned embeddings, and $\oplus$ denotes concatenation.

**Crystal Structure Encoder ($E_{\text{struct}}$):**
We utilize an E(3)-equivariant graph neural network based on the e3nn framework to respect rotational and translational symmetries of crystal structures. Given atomic positions $\{\mathbf{r}_i\}$ and species $\{z_i\}$:

$$\mathbf{h}_i^{(l+1)} = \mathbf{h}_i^{(l)} + \sum_{j \in \mathcal{N}(i)} \phi^{(l)}\left(\mathbf{h}_i^{(l)}, \mathbf{h}_j^{(l)}, Y^{(l)}(\hat{\mathbf{r}}_{ij}), \|\mathbf{r}_{ij}\|\right)$$

where $Y^{(l)}$ are spherical harmonics encoding directional information, and $\phi^{(l)}$ is an equivariant message-passing function. The final structure embedding is obtained via invariant pooling:

$$\mathbf{h}_{\text{struct}} = \text{InvariantPool}\left(\{\mathbf{h}_i^{(L)}\}_{i=1}^{N}\right)$$

**XRD Pattern Encoder ($E_{\text{XRD}}$):**
XRD patterns are treated as 1D sequences and processed by a Transformer encoder. Given discretized intensity values $\{I(2\theta_k)\}_{k=1}^{K}$:

$$\mathbf{H}_{\text{XRD}} = \text{TransformerEncoder}\left(\text{PosEmbed}(\{I(2\theta_k)\})\right)$$
$$\mathbf{h}_{\text{XRD}} = \text{MeanPool}(\mathbf{H}_{\text{XRD}})$$

All encoders output embeddings of dimension $d = 256$.

### 3.3 Stage 2: Contrastive Cross-Modal Alignment

To enable meaningful fusion across modalities, we project modality-specific embeddings into a shared semantic space using CLIP-style contrastive learning. For each modality $m$, a projection head maps embeddings to the shared space:

$$\mathbf{z}_m = \text{LayerNorm}\left(\text{MLP}_m(\mathbf{h}_m)\right) \in \mathbb{R}^{d_{\text{shared}}}$$

We train with an InfoNCE loss that encourages embeddings from the same material to be similar across modalities:

$$\mathcal{L}_{\text{contrast}} = -\frac{1}{|\mathcal{P}|} \sum_{(i,j) \in \mathcal{P}} \log \frac{\exp(\text{sim}(\mathbf{z}_i^{m_1}, \mathbf{z}_i^{m_2})/\tau)}{\sum_{k=1}^{B} \exp(\text{sim}(\mathbf{z}_i^{m_1}, \mathbf{z}_k^{m_2})/\tau)}$$

where $\mathcal{P}$ is the set of modality pairs, $\text{sim}(\cdot, \cdot)$ is cosine similarity, $\tau = 0.07$ is the temperature, and $B$ is batch size.

### 3.4 Stage 3: Hierarchical Attention Binding

The core innovation of HCMB-Net is the hierarchical binding mechanism that fuses aligned representations through two levels of attention.

**Modality Grouping:**
We organize modalities into semantically meaningful groups:
- Group 1 (Compositional): Composition embeddings
- Group 2 (Structural): Crystal structure, XRD patterns
- Group 3 (Spectroscopic): Future extensibility for Raman, IR spectra

**Local Binding (Within-Group Attention):**
For each group $g$ with modalities $\{m_1, ..., m_{|g|}\}$:

$$\mathbf{Z}_g = [\mathbf{z}_{m_1}; \mathbf{z}_{m_2}; ...; \mathbf{z}_{m_{|g|}}] \in \mathbb{R}^{|g| \times d_{\text{shared}}}$$
$$\mathbf{Z}_g^{\text{local}} = \text{MultiHeadAttn}(\mathbf{Z}_g, \mathbf{Z}_g, \mathbf{Z}_g, \mathbf{M}_g^{\text{local}})$$
$$\mathbf{h}_g = \text{MeanPool}(\mathbf{Z}_g^{\text{local}})$$

where $\mathbf{M}_g^{\text{local}}$ is an attention mask that zeros out attention weights for missing modalities.

**Global Binding (Cross-Group Attention):**
Group representations are fused via global attention:

$$\mathbf{H}_{\text{global}} = [\mathbf{h}_{g_1}; \mathbf{h}_{g_2}; ...; \mathbf{h}_{g_G}] \in \mathbb{R}^{G \times d_{\text{shared}}}$$
$$\mathbf{H}_{\text{fused}} = \text{MultiHeadAttn}(\mathbf{H}_{\text{global}}, \mathbf{H}_{\text{global}}, \mathbf{H}_{\text{global}}, \mathbf{M}^{\text{global}})$$
$$\mathbf{h}_{\text{unified}} = \text{MeanPool}(\mathbf{H}_{\text{fused}})$$

**Missing Modality Handling:**
When modality $m$ is missing, we set $\mathbf{z}_m = \mathbf{0}$ and mask all attention connections involving $m$. This ensures that the model gracefully degrades without propagating undefined values.

### 3.5 Property Prediction Head

The unified representation is passed through a prediction MLP:

$$\hat{y} = \text{MLP}_{\text{pred}}(\mathbf{h}_{\text{unified}})$$

### 3.6 Training Objective

The total loss combines property prediction and contrastive alignment:

$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{pred}} + \lambda \mathcal{L}_{\text{contrast}}$$

where $\mathcal{L}_{\text{pred}} = \text{MAE}(y, \hat{y})$ and $\lambda = 0.1$ balances the two objectives.

### 3.7 Data Collection and Preprocessing

**Primary Dataset:** Alexandria dataset containing approximately 5 million inorganic crystalline materials with DFT-computed formation energies and band gaps.

**Modality Extraction:**
- Composition: Extracted directly from chemical formulas
- Crystal Structure: Atomic coordinates and lattice parameters from CIF files
- XRD Patterns: Simulated using pymatgen with Cu-Kα radiation ($\lambda = 1.5406$ Å), discretized to 4096 bins over $2\theta \in [10°, 90°]$

**Data Splits:** 80% training, 10% validation, 10% test with stratified sampling by crystal system.

**Missing Modality Simulation:** During training, we randomly drop modalities with probability $p_{\text{drop}} \in \{0, 0.1, 0.2, 0.3, 0.4, 0.5\}$ to simulate real-world incompleteness.

### 3.8 Experimental Design

**Experiment 1: Primary Performance Evaluation**
- Compare HCMB-Net (3 modalities) against COSNet (2 modalities), single-modality baselines, and simple concatenation fusion
- Metrics: MAE, RMSE on formation energy (eV/atom) and band gap (eV)
- Statistical validation: 25 independent runs, paired t-test, report mean ± std, 95% CI, Cohen's d

**Experiment 2: Robustness Under Modality Dropout**
- Evaluate performance degradation across dropout rates $p_{\text{drop}} \in \{0, 0.1, 0.2, 0.3, 0.4, 0.5\}$
- Metric: Robustness score $R = (\text{MAE}_{\text{missing}} - \text{MAE}_{\text{full}}) / \text{MAE}_{\text{full}}$
- Success criterion: $R < 10\%$ at $p_{\text{drop}} = 0.3$

**Experiment 3: Hierarchical vs. Flat Attention Ablation**
- Compare hierarchical binding against flat attention (all modalities attend to all others directly)
- Vary number of modalities $N \in \{2, 3, 4, 5\}$
- Hypothesis: Hierarchical outperforms flat when $N \geq 3$

**Experiment 4: Component Ablation**
- Remove contrastive alignment (direct fusion)
- Replace E(3)-equivariant GNN with standard GNN
- Remove hierarchical structure (single-level attention)

### 3.9 Evaluation Metrics

| Metric | Formula | Target |
|--------|---------|--------|
| MAE | $\frac{1}{N}\sum_i |y_i - \hat{y}_i|$ | < 0.045 eV/atom |
| RMSE | $\sqrt{\frac{1}{N}\sum_i (y_i - \hat{y}_i)^2}$ | < 0.065 eV/atom |
| Robustness Score | $(MAE_{missing} - MAE_{full})/MAE_{full}$ | < 10% at 30% dropout |
| Cohen's d | $(\mu_1 - \mu_2)/s_{pooled}$ | > 0.5 (medium effect) |

### 3.10 Implementation Details

- Framework: PyTorch with PyTorch Geometric and e3nn
- Embedding dimension: $d = 256$, shared dimension: $d_{\text{shared}} = 256$
- Attention heads: 8 for both local and global binding
- Optimizer: AdamW with learning rate $10^{-4}$, weight decay $10^{-5}$
- Batch size: 256, trained for 100 epochs with early stopping (patience=10)
- Hardware: 8× NVIDIA A100 GPUs, estimated 500 GPU-hours total

---

## 4. Expected Outcomes & Impact

### 4.1 Expected Results

**Primary Outcome (P1):** We expect HCMB-Net with 3 modalities to achieve MAE < 0.045 eV/atom on formation energy prediction, representing a >5% improvement over COSNet's reported ~0.05 eV/atom. This improvement stems from the complementary information captured by XRD patterns that is not available from composition and structure alone.

**Robustness Outcome (P2):** Under 30% modality dropout, we anticipate <10% performance degradation (MAE < 0.050 eV/atom), demonstrating that the hierarchical attention masking mechanism successfully handles missing data without catastrophic failure.

**Mechanism Validation (P3):** Ablation studies will confirm that hierarchical binding outperforms flat attention for $N \geq 3$ modalities, with expected improvements of 3-5% MAE reduction due to reduced attention complexity and more structured information flow.

### 4.2 Scientific Contributions

1. **Architectural Innovation:** HCMB-Net introduces the first hierarchical cross-modal binding framework specifically designed for materials science, combining domain-specific equivariant encoders with scalable attention mechanisms.

2. **Robustness Framework:** The attention masking strategy for handling missing modalities provides a principled approach applicable beyond materials science to any multimodal learning scenario with incomplete data.

3. **Empirical Insights:** Systematic ablations will reveal which components (equivariance, contrastive alignment, hierarchical structure) contribute most to performance, guiding future architecture design.

### 4.3 Broader Impact

**Accelerating Materials Discovery:** By enabling robust property prediction from incomplete characterization data, HCMB-Net can reduce the experimental burden in high-throughput materials screening campaigns. Researchers can obtain reliable predictions even when some measurements are unavailable, accelerating the design-make-test cycle.

**Bridging AI and Materials Science:** This work directly addresses the AI4Mat community's question of "Why Isn't it Real Yet?" by tackling the practical challenge of multimodal, incomplete data that distinguishes materials science from adjacent fields.

**Foundation for Future Extensions:** The modular architecture allows straightforward integration of additional modalities (Raman spectroscopy, electron microscopy, synthesis parameters) as the field evolves, providing a sustainable framework for continued development.

### 4.4 Limitations and Future Work

We acknowledge several limitations: (1) the current scope is restricted to inorganic crystalline materials with periodic structures; (2) XRD patterns are simulated rather than experimental, potentially missing noise characteristics; (3) the Alexandria dataset, while large, may not capture the full diversity of real-world materials. Future work will extend HCMB-Net to amorphous materials, incorporate experimental XRD data with noise modeling, and explore active learning strategies for optimal modality acquisition.

### 4.5 Conclusion

HCMB-Net represents a significant step toward practical AI-driven materials discovery by addressing the fundamental challenge of multimodal, incomplete characterization data. Through hierarchical cross-modal binding with domain-appropriate encoders, we expect to demonstrate that scalable, robust multimodal learning is achievable for materials science, bringing the field closer to the transformative impact seen in adjacent AI applications.