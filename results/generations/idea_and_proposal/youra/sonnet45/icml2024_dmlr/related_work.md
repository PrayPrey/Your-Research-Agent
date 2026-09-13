## Related Work

**Related Papers**
1. **Title**: Software Bill of Materials in Software Supply Chain Security: A Systematic Literature Review
   - **Authors**: O'Donoghue et al.
   - **Summary**: Systematic review of SBOM applications including vulnerability management, transparency, component assessment, risk assessment, and supply chain integrity. Identifies adoption barriers including generation tooling, privacy, format/standardization, and sharing/distribution.
   - **Year**: 2025

2. **Title**: A Landscape Study of Open-Source Tools for Software Bill of Materials (SBOM)
   - **Authors**: Mirakhorli et al.
   - **Summary**: Analyzed 84 SBOM tools for software supply chain security with emerging use cases in vulnerability revelation and outdated component identification. Demonstrates graph-based dependency tracking as standard approach using SPDX and CycloneDX formats.
   - **Year**: 2024

3. **Title**: Operationalising Artificial Intelligence Bills of Materials (AIBOM)
   - **Authors**: Radanliev et al.
   - **Summary**: Extends SBOM to AI systems with model lineage, training provenance, and disclosure metadata. Achieved 98.7% reproducibility fidelity and 96.2% vulnerability matching precision using cryptographic validation and agent-driven automation.
   - **Year**: 2026

4. **Title**: Responsibly Training Foundation Models: Actualizing Ethical Principles for Curating Large-Scale Training Datasets
   - **Authors**: Scheuerman et al.
   - **Summary**: Workshop outcomes on ethical responsibility in dataset composition, process, and release. Identifies challenges unique to unprecedented scale of foundation model datasets and proposes conceptual framework for solutions.
   - **Year**: 2025

5. **Title**: Ethical AI and Responsible Data Engineering: A Framework for Bias Mitigation and Privacy Preservation
   - **Authors**: Muvva
   - **Summary**: Integrates automated bias detection/mitigation tools, data anonymization, and model explanations. Demonstrates effectiveness in finance, healthcare, and criminal justice domains.
   - **Year**: 2025

6. **Title**: Data collection and quality challenges in deep learning: A Data-Centric AI Survey
   - **Authors**: Whang et al.
   - **Summary**: Foundational survey identifying data-centric challenges including collection, quality, labeling, and versioning. Notes limited tooling solutions for provenance and governance.
   - **Year**: 2021

7. **Title**: Model Cards for Model Reporting
   - **Authors**: Mitchell et al.
   - **Summary**: Proposes static documentation of model properties for transparency to improve accountability in machine learning models.
   - **Year**: 2019

8. **Title**: Datasheets for Datasets
   - **Authors**: Gebru et al.
   - **Summary**: Foundational work proposing static documentation of dataset properties for transparency to inform downstream users about dataset characteristics and limitations.
   - **Year**: 2018

9. **Title**: LAION-5B Large-Scale Dataset Construction
   - **Authors**: Not specified
   - **Summary**: Well-defined aggregation methodology with reproducible pipeline using cosine similarity filtering with CLIP embeddings for quality control. Applied post-hoc ethical safeguards (NSFW detection and bias screening) with problems discovered months after release.
   - **Year**: Not specified

10. **Title**: cleanlab/cleanlab (GitHub Repository)
   - **Authors**: Not specified
   - **Summary**: Data-centric AI package for label error detection and dataset curation, focusing on data quality improvement through automated methods.
   - **Year**: Not specified

11. **Title**: NVIDIA Curator (GitHub Repository)
   - **Authors**: Not specified
   - **Summary**: Modular dataset curation pipeline for LLM/multimodal data supporting custom stages, distributed processing (Dask), and GPU acceleration.
   - **Year**: Not specified

12. **Title**: Data Version Control (DVC)
   - **Authors**: Not specified
   - **Summary**: Git-like semantics for ML data using content-addressed storage, snapshots, and diffs. Mature tool with wide adoption that integrates with ML workflows.
   - **Year**: Not specified

**Key Challenges**
1. **Insufficient Post-Hoc Auditing**: Current practices of post-hoc ethical auditing (batch filtering after dataset aggregation) are insufficient for foundation model scale, leading to late detection of ethical issues (months after release) and lost provenance metadata.

2. **Provenance Tracking Gap**: Existing approaches lack operational provenance tracking, with source URLs and timestamps lost during aggregation, resulting in low traceability (<50%) when attempting to trace biased samples back to their origins.

3. **Static Documentation Limitations**: Model cards and datasheets provide post-hoc static documentation but lack operational integration into pipelines, dynamic provenance updates, and version control for continuous dataset evolution.

4. **Reactive vs. Preventive Governance**: Current SOTA approaches (LAION-5B) apply ethical safeguards reactively after data collection, allowing problematic data accumulation before correction rather than preventing it at ingestion boundaries.

5. **Manual Versioning Inefficiency**: Ad-hoc dataset versioning via file naming (dataset_v1, dataset_v2_fixed) is error-prone, slow (no automated diff), and doesn't scale, requiring weeks for ethical iteration cycles.

6. **Tooling Fragmentation**: Existing tools address individual components (DVC for versioning, cleanlab for quality, Curator for curation) but lack unified integration of provenance tracking, governance filters, and version control in a single pipeline.

7. **Cross-Domain Filter Generalization**: Bias and toxicity detection models trained on text-only data have unknown cross-domain performance on multimodal vision-language data, requiring calibration and validation.

8. **Scalability Unknowns**: Graph database performance at web scale (billions of samples), DVC storage overhead for multimedia datasets at TB scale, and computational costs of streaming governance at 2-5x latency overhead remain untested.

9. **Standardization Gap**: Lack of standardized schema for dataset provenance (analogous to SPDX/CycloneDX for SBOM), hindering interoperability and tool ecosystem development.

10. **Domain-Specific Requirements**: Different data modalities (audio, video, 3D, scientific data) have unique ethical governance needs and may require schema extensions beyond vision-language datasets.
