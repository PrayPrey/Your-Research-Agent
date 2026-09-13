## Related Work

**Related Papers**

1. **Title**: A path towards AI-scale, interoperable biological data (Aevermann et al., 2025)
   - **Authors**: Aevermann et al. (30+ authors)
   - **Summary**: Nature perspective paper identifying data standardization as critical bottleneck for multimodal foundational datasets and proposing technological roadmap for scaling multi-modal measurements and pooled resources.
   - **Year**: 2025

2. **Title**: Multimodal Transformers for Drug Target Discovery (Steurer et al., 2024)
   - **Authors**: Steurer et al.
   - **Summary**: Uses cross-attention between biomedical text, molecular graphs, and gene expression for targeting aging/age-related diseases, employing concatenation + attention without explicit scale transition modeling.
   - **Year**: 2024

3. **Title**: AI-enabled language models to large language models in drug discovery (Chakraborty et al., 2025)
   - **Authors**: Chakraborty et al.
   - **Summary**: Comprehensive review of LLM/MLLM evolution in drug discovery, covering foundation model landscape but no mention of renormalization group (RG) approaches or cross-scale mechanisms.
   - **Year**: 2025

4. **Title**: Multimodal pretraining for unsupervised protein representation learning (Nguyen & Hy, 2023)
   - **Authors**: Nguyen & Hy
   - **Summary**: Symmetry-preserving multimodal pretraining integrating protein sequence, graph, and 3D point clouds into unified latent space with HySonLab implementation available.
   - **Year**: 2023

5. **Title**: Multimodal protein representation learning and target-aware VAE (Ngo & Hy, 2024)
   - **Authors**: Ngo & Hy
   - **Summary**: Protein Multimodal Network (PMN) unifying sequence, 3D structure, and graph representations for target-aware ligand generation using VAE framework.
   - **Year**: 2024

6. **Title**: Diffusion Sequence Models for Enhanced Protein Representation (Hallee et al., 2025)
   - **Authors**: Hallee et al.
   - **Summary**: DSM framework using masked diffusion for unified protein representation and generation, producing diverse biomimetic sequences with predicted functions.
   - **Year**: 2025

7. **Title**: Integration of pan-omics technologies and 3D in vitro tumor models (Jose et al., 2024)
   - **Authors**: Jose et al.
   - **Summary**: Multi-omics integration (genomics, transcriptomics, proteomics, metabolomics) with 3D tumor models for genotype-phenotype correlations, demonstrating data availability but lacking predictive AI models.
   - **Year**: 2024

8. **Title**: Organoids: development and applications in disease models, drug discovery (Yao et al., 2024)
   - **Authors**: Yao et al.
   - **Summary**: Comprehensive organoid review establishing organoid technology as experimental platform for drug discovery, noting that organoids generate multimodal data but analysis methods lag behind.
   - **Year**: 2024

9. **Title**: Multi-scale AI for disease prediction (Canpolat et al., 2024)
   - **Authors**: Canpolat et al.
   - **Summary**: Multi-scale integration approach for disease classification using hierarchical feature extraction from multi-scale medical images (image-only, no molecular-cellular integration).
   - **Year**: 2024

10. **Title**: Foundation Model Vine Platform for multi-scale integration (FN-MVP, 2025)
    - **Authors**: Not specified
    - **Summary**: Graph-based multi-scale integration for disease prediction using multi-scale graph neural networks with hierarchical pooling, lacking explicit coarse-graining operators or physics-inspired framework.
    - **Year**: 2025

11. **Title**: Pathology & scRNA-seq Transformer (PAST, 2025)
    - **Authors**: Not specified
    - **Summary**: Foundation model for single-cell histopathology integration using dual-encoder (scRNA-seq transformer + histopathology ViT) with late fusion, achieving ~0.85 accuracy for cell type classification but limited to cellular+tissue scales.
    - **Year**: 2025

12. **Title**: Using Renormalization Group for Scale-Invariant Features in DNNs (Liaw et al., 2025)
    - **Authors**: Liaw et al.
    - **Summary**: AAAI paper applying RG theory to deep learning for learning scale-invariant features in computer vision (image classification), demonstrating feasibility of RG in deep learning context for general scale invariance.
    - **Year**: 2025

13. **Title**: Renormalization Group Theory (Wilson & Kadanoff, Nobel Prize 1982)
    - **Authors**: Wilson & Kadanoff
    - **Summary**: Foundational work establishing mathematical framework for scale transitions in statistical physics, including coarse-graining operators, fixed points, universality classes, and scaling flows.
    - **Year**: 1982

14. **Title**: An exact mapping between the Variational RG and Deep Learning (Mehta & Schwab, 2014)
    - **Authors**: Mehta & Schwab
    - **Summary**: Establishes theoretical connection showing deep learning architectures (restricted Boltzmann machines) are mathematically equivalent to RG transformations, providing theoretical justification for using neural networks to implement RG operators.
    - **Year**: 2014

15. **Title**: CRISPRlnc: machine learning method for lncRNA-specific sgRNA design (Yang et al., 2024)
    - **Authors**: Yang et al.
    - **Summary**: SVM-based lncRNA-specific CRISPR design for on-target activity and off-target prediction at molecular scale (single-scale, doesn't predict cellular/tissue effects).
    - **Year**: 2024

16. **Title**: Artificial Intelligence for CRISPR Guide RNA Design: XAI and Safety (Abbaszadeh & Shahlai, 2025)
    - **Authors**: Abbaszadeh & Shahlai
    - **Summary**: Review of explainable AI for CRISPR focusing on off-target safety prediction and interpretability, noting lack of mechanistic understanding in current XAI methods.
    - **Year**: 2025

17. **Title**: UniDiffuser (thu-ml/unidiffuser)
    - **Authors**: Not specified
    - **Summary**: Unified diffusion framework for multiple modalities (text, image) where shared latent space enables cross-modal generation and comparison.
    - **Year**: Not specified

18. **Title**: ModelScope Framework
    - **Authors**: Not specified
    - **Summary**: Modular multimodal architecture patterns using separate encoders per modality plus fusion module for scale-specific encoder integration.
    - **Year**: Not specified

19. **Title**: HySonLab/Protein_Pretrain (GitHub)
    - **Authors**: HySonLab
    - **Summary**: Multimodal protein pretraining implementation (sequence + graph + 3D) leveraging LLMs and generative models for protein representation.
    - **Year**: Not specified

**Key Challenges**

1. **Data Standardization Bottleneck**: Multi-modal biological data lacks standardization and interoperability, limiting ability to create unified foundational datasets for cross-scale modeling (Aevermann et al., 2025).

2. **Lack of Principled Cross-Scale Mechanisms**: Existing multimodal models rely on concatenation or attention-based fusion without mathematical or conceptual framework for scale transition operators (Steurer 2024, PAST 2025).

3. **Missing Biological Priors in Aggregation**: Hierarchical transformers learn aggregation from data without integrating domain knowledge such as biological pathway structure from gene ontology databases (KEGG, Reactome).

4. **Cross-Scale Interpretability Gap**: Multi-scale models remain black-boxes without methods to identify conserved biological modules across scales or understand learned scale transition rules (FN-MVP, PAST, hierarchical transformers).

5. **Molecular-to-Tissue Prediction Gap**: No existing foundation model explicitly bridges molecular scale (compounds, CRISPR) to tissue scale (organoid responses) for drug discovery applications via cellular intermediate representations.

6. **Analysis Methods Lagging Behind Data Generation**: Organoid technology generates rich multimodal data but computational analysis methods have not kept pace with experimental capabilities (Yao et al., 2024).

7. **Physics-Biology Analogy Validity Uncertainty**: Unclear whether biological systems follow physics-like coarse-graining principles given evolved complexity, entangled scales, and context-dependent rules rather than universal conservation laws.

8. **Error Amplification in Sequential Hierarchies**: Multi-layer hierarchical models risk compounding errors through sequential transformations without recovery mechanisms when early-stage predictions are inaccurate.

9. **Limited CRISPR Mechanistic Understanding**: Current ML methods for CRISPR design focus on on-target/off-target prediction but lack mechanistic understanding of cross-scale effects from molecular edits to tissue-level outcomes (Abbaszadeh & Shahlai, 2025).

10. **Data Efficiency for Multi-Scale Training**: Fully-paired multi-scale biological data (molecular + cellular + tissue measurements on same samples) is scarce and expensive, limiting training of comprehensive cross-scale models.
