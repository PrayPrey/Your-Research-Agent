## Related Work

**Related Papers**
1. **Title**: Mice to Machines: Neural Representations from Visual Cortex for Domain Generalization (Semantic Scholar ID: 9cfb3c90f895294bd228fcac8ac6581add09de54)
   - **Authors**: Qazi, Jalil, Iqbal
   - **Summary**: Proposes a NeuRN layer that mimics excitatory/inhibitory balance from visual cortex, demonstrating improved domain generalization robustness on PACS and Office-Home benchmarks.
   - **Year**: 2025

2. **Title**: Failure to Achieve Domain Invariance With Domain Generalization Algorithms (Semantic Scholar ID: 79523b28bf5b1c7b5ee99221a4896411c9d68905)
   - **Authors**: Korevaar, Tennakoon, Bab-Hadiashar
   - **Summary**: Demonstrates that all 8 tested domain generalization algorithms retain domain-specific information, identifying feature extraction as the critical failure point.
   - **Year**: 2023

3. **Title**: Emergence of a contrast-invariant representation of naturalistic texture in macaque visual cortex (Semantic Scholar ID: 937f7a23021ee82040e1eb6db81178e636a20088)
   - **Authors**: Lee, Majaj, Deliz, Kiorpes, Movshon
   - **Summary**: Shows that V4 visual cortex achieves superior invariant decoding through greater diversity in neural selectivity, providing principles for population diversity in uncertainty quantification.
   - **Year**: 2025

4. **Title**: DomainBed Benchmark
   - **Authors**: Facebook Research
   - **Summary**: Provides a comprehensive benchmark framework for domain generalization methods including CORAL, DANN, IRM, GroupDRO, and ERM baselines.
   - **Year**: Not specified

5. **Title**: Grad-CAM
   - **Authors**: Selvaraju et al.
   - **Summary**: Introduces gradient-weighted class activation mapping for visual explanations in deep networks, serving as a baseline for explanation faithfulness comparison.
   - **Year**: 2017

6. **Title**: A Systematic Review of Generalization Research in Medical Image Classification (arXiv:2403.12167)
   - **Authors**: Matta et al.
   - **Summary**: Reviews 77 articles on generalization in medical imaging, finding that learning-based domain generalization methods are emerging but require better evaluation protocols.
   - **Year**: 2024

7. **Title**: Explainable, trustworthy, and ethical ML for healthcare: A survey (Semantic Scholar ID: ef77f88c475b2fb3fbb07a57435d72f42464c0cf)
   - **Authors**: Rasheed et al.
   - **Summary**: Surveys explainability, uncertainty quantification, and robustness in healthcare ML, finding these aspects are addressed separately without unified frameworks.
   - **Year**: 2021

**Key Challenges**
1. **Domain-Specific Information Retention**: Existing domain generalization algorithms fail to achieve true domain invariance, with all tested methods retaining domain-specific information in learned features.
2. **Feature Extraction as Failure Point**: The critical bottleneck in domain generalization lies in the feature extraction stage rather than downstream components.
3. **Lack of Integrated Framework**: Explainability, uncertainty quantification, and robustness are addressed as separate concerns in healthcare ML, with no unified framework combining these essential properties.
4. **Inadequate Evaluation Protocols**: Learning-based domain generalization methods in medical imaging lack standardized and rigorous evaluation protocols.
5. **Insufficient Neural Diversity**: Current approaches do not leverage population diversity principles observed in biological visual systems for achieving invariant representations.
