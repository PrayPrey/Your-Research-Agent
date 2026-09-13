## Related Work

**Related Papers**
1. **Title**: PANGAEA: A Global and Inclusive Benchmark for Geospatial Foundation Models (2024)
   - **Authors**: V. Marsocci, Yuru Jia, et al.
   - **Summary**: Demonstrates that geospatial foundation models don't consistently outperform supervised models and establishes a standardized evaluation protocol that enables extensible benchmarking across geospatial tasks.
   - **Year**: 2024

2. **Title**: Data Cards: Purposeful and Transparent Dataset Documentation (2022)
   - **Authors**: Mahima Pushkarna, Andrew Zaldivar, Oddur Kjartansson
   - **Summary**: Introduces structured documentation standards for datasets that enable transparent and reproducible dataset use, demonstrating that community adoption of documentation standards is achievable.
   - **Year**: 2022

3. **Title**: Unified Transferability Metrics for Time Series Foundation Models (2025)
   - **Authors**: Weiyang Zhang, Xinyang Chen, et al.
   - **Summary**: Proposes three complementary metrics (Dependency, Pattern, Task Adaptation) for model selection that achieve 35% improvement over ETran, validating that transferability metrics can predict cross-domain success.
   - **Year**: 2025

4. **Title**: HELM (Holistic Evaluation of Language Models)
   - **Authors**: Not specified
   - **Summary**: Provides a score aggregation approach for evaluating language models without formal traceability mechanisms.
   - **Year**: Not specified

5. **Title**: lm-evaluation-harness (EleutherAI)
   - **Authors**: Not specified
   - **Summary**: Offers a task coverage approach for evaluating large language models across diverse benchmarks.
   - **Year**: Not specified

6. **Title**: EHRSHOT: An EHR Benchmark for Few-Shot Evaluation of Foundation Models (2023)
   - **Authors**: Michael Wornow, Rahul Thapa, et al.
   - **Summary**: Presents a high-quality clinical benchmark for few-shot evaluation of foundation models on electronic health record data, though without cross-domain links.
   - **Year**: 2023

7. **Title**: SzCORE: Seizure Community Open-Source Research Evaluation (2024)
   - **Authors**: Jonathan Dan, U. Pale, et al.
   - **Summary**: Establishes a unified framework for EEG-based seizure detection evaluation with standardized protocols, demonstrating successful standardization in a specialized domain.
   - **Year**: 2024

**Key Challenges**
1. **Domain Siloing**: Foundation models and benchmarks are developed within isolated domains without cross-domain evaluation frameworks, limiting understanding of transferability across scientific fields.
2. **Inconsistent Performance of Foundation Models**: Geospatial foundation models don't consistently outperform supervised models, indicating gaps in understanding when and why foundation models provide benefits.
3. **Lack of Transfer Efficiency Metrics**: Existing evaluation frameworks like HELM focus on aggregated task performance without measuring transfer efficiency or providing formal traceability.
4. **Limited Multi-Modal Evaluation**: Current evaluation harnesses primarily target language models and lack extension to multi-modal foundation models with cross-domain bridge datasets.
5. **Absence of Cross-Domain Links**: High-quality domain-specific benchmarks (e.g., clinical EHR benchmarks) exist in isolation without mechanisms to connect evaluation across different scientific domains.
