## Related Work

**Related Papers**

1. **Title**: Interpretable Causal Representation Learning for Biological Data in the Pathway Space (SS: c3387ab986d9497714504357e7445b0ca173d5e3)
   - **Authors**: de la Fuente et al.
   - **Summary**: Proposes pathway-space causal learning framework using VAEs and causal discovery for disease subtyping, demonstrating that pathway-level causal models improve biological interpretability over gene-level models.
   - **Year**: 2025

2. **Title**: From classical mendelian randomization to causal networks for systematic integration of multi-omics (SS: 1cff7263179385303691da6129a48506b18da1f4)
   - **Authors**: Yazdani et al.
   - **Summary**: Reviews transition from single-exposure Mendelian randomization to multi-omics causal networks, providing conceptual framework for multi-mediator analysis in disease etiology studies.
   - **Year**: 2022

3. **Title**: An Interpretable Machine Learning Strategy for Antimalarial Drug Discovery with LightGBM and SHAP (SS: 92b906f2e86c2f3e5ff13fa429a997768b1ecf74)
   - **Authors**: Noviandy et al.
   - **Summary**: Demonstrates SHAP interpretability for QSAR models achieving 86% accuracy, providing correlational feature importance explanations for antimalarial drug discovery.
   - **Year**: 2024

4. **Title**: GSRF-DTI: graph-based representation learning for drug-target interaction (SS: a8bc1df04487af1c684e47ccbbe10aef6420f044)
   - **Authors**: Zhu et al.
   - **Summary**: Graph neural networks for drug-target binding prediction at molecular level, addressing limitations of traditional QSAR models that ignore molecular graph structure.
   - **Year**: 2024

5. **Title**: Resolving tissue complexity by multimodal spatial omics modeling with MISO (SS: e47a9918829003a93f398ed9e563361008b2b513)
   - **Authors**: Coleman et al.
   - **Summary**: Demonstrates feasibility of multi-modal omics integration (transcriptomics + proteomics + metabolomics) for spatial tissue characterization and architecture analysis.
   - **Year**: 2025

6. **Title**: Multi-modal Transfer Learning between Biological Foundation Models (IsoFormer) (SS: c94cf63c86cbeefe668b6cb6b118506e8e144b7a)
   - **Authors**: Garau-Luis et al.
   - **Summary**: Demonstrates DNA-RNA-protein modality connections using transfer learning for transcript expression prediction in molecular biology applications.
   - **Year**: 2024

7. **Title**: CLADD - LLM Agents for Drug Discovery (SS: 2fd3ebcc9ab0ffd4b544d8b1515567f88f5a771d)
   - **Authors**: Lee et al.
   - **Summary**: Emerging LLM agent paradigm for drug discovery using RAG, multi-agent collaboration, and hypothesis generation focused on literature synthesis and knowledge retrieval.
   - **Year**: 2025

8. **Title**: PharmaSwarm - LLM Agents for Drug Discovery (SS: 4a93b2ea1408944be3fe41d8d0a88b28d6b82778)
   - **Authors**: Song et al.
   - **Summary**: LLM-based multi-agent system for pharmaceutical research, focusing on collaborative hypothesis generation and literature-based drug discovery.
   - **Year**: 2025

9. **Title**: DrugPilot - LLM Agents for Drug Discovery (SS: a51b28d8fcf17077a038fe775117865731f9c98d)
   - **Authors**: Li et al.
   - **Summary**: LLM agent framework for drug discovery utilizing retrieval-augmented generation and multi-agent collaboration for knowledge synthesis.
   - **Year**: 2025

10. **Title**: Sequential Optimal Experimental Design of Perturbation Screens Guided by Multi-modal Priors (SS: 0c8cce7d6eb0f53945ebae4f864a1b5794913b97)
    - **Authors**: Huang et al.
    - **Summary**: Active learning framework for perturbation biology experiments, optimizing experimental design for maximum information gain in biological screens.
    - **Year**: 2023

**Key Challenges**

1. **Lack of End-to-End Causal Framework**: No existing work integrates genomic instrumental variables (Mendelian randomization), hierarchical multi-scale mediation (genotype → transcriptome → proteome → pathway → drug response), pathway-constrained graph neural networks, and counterfactual reasoning in a unified framework for drug response prediction.

2. **Correlational vs. Causal Interpretability**: Current interpretable ML methods (SHAP, feature importance) provide correlational explanations without causal guarantees, insufficient for mechanistic understanding and regulatory approval in pharmacogenomics.

3. **Single-Scale Mendelian Randomization Limitations**: Standard MR approaches limited to single exposure-outcome pairs without multi-omics mediation analysis or pathway-level interpretability, providing "what" but not "why" biological mechanisms.

4. **Pathway Database Completeness and Bias**: Reliance on curated pathway databases (KEGG, Reactome) may introduce bias toward well-studied pathways while missing novel drug mechanisms not yet documented.

5. **Multi-Omics Data Integration Complexity**: Handling missing modalities, measurement quality variations (RNA-seq CV <20%, proteomics CV <30%), and batch effects across multi-omics datasets requires robust integration strategies.

6. **Causal Graph Misspecification Risk**: Learned causal DAGs may misspecify true biological relationships through wrong edge directions, missing edges, or violations of faithfulness assumptions.

7. **Cross-Cohort Generalization Gap**: Models trained on cell lines (in vitro) may not generalize to population cohorts (in vivo) due to domain shift, different outcome measures (IC50 vs. clinical response), and context-specific pathway mechanisms.

8. **Instrumental Variable Assumptions Violations**: IV analysis requires strong assumptions (relevance F>10, exclusion restriction, exchangeability) that may be violated by pleiotropic variants, unmeasured confounding, or population stratification.

9. **Scalability to Large-Scale Pharmacogenomics**: Framework must scale to 1000+ drugs × 20,000+ genes × 500+ pathways while maintaining computational feasibility and statistical power.

10. **Clinical Actionability of Pathway Explanations**: Uncertainty about whether pathway-level mechanistic explanations will be actionable for clinicians versus requiring finer-grained (gene-level) or coarser-grained (drug-level) information for treatment decisions.
