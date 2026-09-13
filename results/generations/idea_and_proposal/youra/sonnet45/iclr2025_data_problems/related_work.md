## Related Work

**Related Papers**
1. **Title**: Data Contamination Can Cross Language Barriers
   - **Authors**: Yao et al.
   - **Summary**: Demonstrated that text-overlap detection fails for translated contamination and that cross-lingual transfer propagates contamination across languages, establishing the foundational problem of cross-lingual contamination detection.
   - **Year**: 2024

2. **Title**: PaCoST: Paired Confidence Significance Testing for Benchmark Contamination Detection
   - **Authors**: Zhang et al.
   - **Summary**: Introduced paired statistical tests on confidence scores to detect memorization in models, showing that contaminated samples exhibit distinct confidence patterns.
   - **Year**: 2024

3. **Title**: Benchmarking Benchmark Leakage in Large Language Models
   - **Authors**: Xu et al.
   - **Summary**: Developed a perplexity and N-gram accuracy detection pipeline for monolingual contamination, providing a scalable baseline detection approach.
   - **Year**: 2024

4. **Title**: Contamination Taxonomy (271 citations)
   - **Authors**: Sainz et al.
   - **Summary**: Defined multi-level contamination taxonomy including exact match, paraphrase, and topic overlap categories, providing systematic framework for understanding contamination types and severity levels.
   - **Year**: 2023

5. **Title**: MMLU-CF: Contamination-free Benchmark
   - **Authors**: Zhao et al.
   - **Summary**: Created dynamically generated benchmark with verifiably new knowledge to provide known-clean validation resource for testing false positive rates in contamination detection methods.
   - **Year**: 2024

6. **Title**: Neural Detection of Cross-lingual Syntactic Knowledge
   - **Authors**: Chen & Farrús
   - **Summary**: Showed that typologically different languages exhibit distinct neural signatures in specific layers, demonstrating how typology modulates cross-lingual transfer patterns.
   - **Year**: 2022

7. **Title**: Negation typology for cross-lingual zero-shot
   - **Authors**: Shaitarova & Rinaldi
   - **Summary**: Demonstrated that typologically distant language pairs require different transfer strategies, providing empirical evidence for typology-based adaptation in cross-lingual models.
   - **Year**: 2021

8. **Title**: Side-Channel Analysis of CRYSTALS-Kyber
   - **Authors**: Hamoudi et al.
   - **Summary**: Developed multi-channel correlation analysis framework using power, timing, and electromagnetic signals to detect cryptographic key leakage, achieving high accuracy through ensemble methods.
   - **Year**: 2021

9. **Title**: Enhancing Malware Detection through EM Side-Channel
   - **Authors**: Khattab & Alheeti
   - **Summary**: Applied Random Forest ensemble classification on multi-modal side-channel signals to achieve 97% malware detection accuracy, demonstrating effectiveness of multi-channel fusion.
   - **Year**: 2025

10. **Title**: How multilingual is Multilingual BERT? (1000+ citations)
    - **Authors**: Pires et al.
    - **Summary**: Demonstrated that mBERT learns cross-lingual representations without explicit alignment, providing mechanistic understanding of how multilingual models transfer knowledge across languages.
    - **Year**: 2019

11. **Title**: K et al. (2020) - Cross-lingual transfer learning in multilingual models
    - **Authors**: K et al.
    - **Summary**: Explained shared vocabulary and encoder mechanisms in multilingual models that enable cross-lingual transfer, contributing to understanding of contamination propagation pathways.
    - **Year**: 2020

**Key Challenges**
1. **Single-Method Detection Limitations**: Existing approaches (text-overlap, confidence-only, generalization-only) capture only one aspect of contamination, failing to detect cross-lingual contamination that evades text matching.

2. **Cross-Lingual Typology Ignored**: Current detection methods use fixed thresholds across all language pairs without accounting for linguistic typology distance, leading to inconsistent performance across diverse languages.

3. **Lack of Cross-Domain Transfer**: Contamination detection methods developed in isolation without leveraging insights from related fields like cryptography and information security that have addressed similar information leakage problems.

4. **Closed-Source Model Inaccessibility**: Most detection methods require access to training data or model internals, making them inapplicable to API-based closed-source models like GPT-4 and Claude.

5. **Cross-Contamination Validation Complexity**: Establishing truly "clean" baseline datasets for validation is challenging, requiring careful experimental design to avoid circular validation where contamination detection is validated using potentially contaminated data.

6. **Computational Cost-Accuracy Trade-offs**: Multi-channel detection approaches face challenges balancing comprehensive analysis with practical deployment constraints in terms of inference latency and computational overhead.

7. **Adversarial Robustness**: If detection methods become widely known, adversaries could potentially design training data injection strategies that mask behavioral signatures, creating an arms race scenario.

8. **Low-Resource Language Coverage**: Languages lacking WALS typology data or high-quality benchmark translations pose challenges for typology-aware detection methods, limiting global applicability.
