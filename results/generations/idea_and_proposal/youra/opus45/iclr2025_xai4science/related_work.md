## Related Work

**Related Papers**
1. **Title**: Label-Free Concept Bottleneck Models (arXiv:2304.06129)
   - **Authors**: Oikarinen, Das, Nguyen, Weng
   - **Summary**: Scales Concept Bottleneck Models to ImageNet without requiring labeled concept data by leveraging CLIP embeddings for concept representation.
   - **Year**: 2023

2. **Title**: Concept Bottleneck Models (arXiv:2007.04612)
   - **Authors**: Koh, Nguyen, Tang, Mussmann, Pierson, Kim, Liang
   - **Summary**: Introduces the original CBM framework that enables concept-based interpretability and allows for concept intervention during inference.
   - **Year**: 2020

3. **Title**: HINN: Hierarchical Input Neural Network (Semantic Scholar ID: 888d7f11f1b8f9df266a0d197f0086fd0d3731f0)
   - **Authors**: Vashishath et al.
   - **Summary**: Embeds cross-omics hierarchical relationships directly into neural network architecture, providing precedent for hierarchical knowledge embedding in neural networks.
   - **Year**: 2025

4. **Title**: Process-Guided Concept Bottleneck Model (arXiv:2601.10562)
   - **Authors**: Asiyabi et al.
   - **Summary**: Applies biophysical constraints for Earth Observation applications using flat concept representations within the CBM framework.
   - **Year**: 2026

5. **Title**: Incremental Residual Concept Bottleneck Models
   - **Authors**: Shang et al.
   - **Summary**: Addresses the concept completeness problem in CBMs but does not incorporate hierarchical structure into the concept representation.
   - **Year**: 2024

6. **Title**: How to build a cognitive map
   - **Authors**: Whittington et al.
   - **Summary**: Demonstrates that cognitive maps organize knowledge hierarchically, providing theoretical foundation for multi-resolution concept organization in neural systems.
   - **Year**: 2022

7. **Title**: OWL2Vec*: Embedding of OWL Ontologies
   - **Authors**: Chen et al.
   - **Summary**: Generates embeddings that preserve ontology structure, enabling conversion of formal ontological knowledge into vector representations.
   - **Year**: 2021

**Key Challenges**
1. **Flat Concept Representations**: Existing CBM approaches, including process-guided variants, utilize flat concept structures that fail to capture the inherent hierarchical organization of scientific knowledge domains.

2. **Lack of Hierarchical Knowledge Integration**: Current neural architectures for interpretable AI do not systematically embed hierarchical relationships from domain ontologies into their concept representations.

3. **Concept Completeness Without Structure**: While some methods address concept completeness in CBMs, they do not incorporate the structural relationships between concepts that reflect domain knowledge organization.

4. **Scalability of Concept Labeling**: Traditional CBMs require labeled concept data, limiting their applicability to domains where such annotations are unavailable or expensive to obtain.

5. **Multi-Resolution Concept Organization**: Existing approaches lack mechanisms to represent concepts at multiple levels of abstraction, which is essential for aligning with how domain experts organize and reason about scientific knowledge.
