## Related Work

**Related Papers**
1. **Title**: EvoSchema: Towards Text-to-SQL Robustness Against Schema Evolution (VLDB 2025)
   - **Authors**: Zhang et al.
   - **Summary**: Provides a comprehensive taxonomy of 10 schema perturbation types and demonstrates that table-level perturbations have greater impact than column-level perturbations on Text-to-SQL systems.
   - **Year**: 2025

2. **Title**: CEL: A Continual Learning Model via Elastic Weight Consolidation (arXiv:2401.08940)
   - **Authors**: Aslam et al.
   - **Summary**: Demonstrates that Elastic Weight Consolidation reduces catastrophic forgetting by 65% while achieving 18% higher memory stability in continual learning settings.
   - **Year**: 2024

3. **Title**: Relational Transformer for Relational Data
   - **Authors**: Not specified
   - **Summary**: Proposes a zero-shot foundation model using cell-level tokenization that achieves 94% of supervised AUROC, validating the feasibility of zero-shot schema transfer.
   - **Year**: 2025

4. **Title**: CoRaL: Continual Representation Learning
   - **Authors**: Yasar & Iqbal
   - **Summary**: Introduces a dual-module architecture that maintains past knowledge while learning new distributions, balancing stability and plasticity in continual learning.
   - **Year**: 2023

5. **Title**: Elastic Weight Consolidation for KG Continual Learning
   - **Authors**: Jhajj & Lin
   - **Summary**: Shows that EWC reduces forgetting from 12.62% to 6.85% (45.7% reduction) in knowledge graph domains, demonstrating EWC effectiveness for structured data.
   - **Year**: 2025

6. **Title**: TAPAS
   - **Authors**: Herzig et al.
   - **Summary**: A BERT-based table question answering model that uses fixed position encodings for table understanding.
   - **Year**: 2020

7. **Title**: TaBERT
   - **Authors**: Yin et al.
   - **Summary**: Proposes joint natural language and table pre-training on 26 million tables for improved table understanding.
   - **Year**: 2020

8. **Title**: TQA-Bench
   - **Authors**: Qiu et al.
   - **Summary**: Benchmark demonstrating that large language models struggle with multi-table context at scale.
   - **Year**: 2024

9. **Title**: Graph ML for Multi-Table (Survey)
   - **Authors**: Gan et al.
   - **Summary**: Survey of graph machine learning approaches for multi-table data that identifies schema adaptation as an open problem in the field.
   - **Year**: 2024

**Key Challenges**
1. **Schema Evolution Robustness**: Table-level schema perturbations significantly impact Text-to-SQL systems, with existing models lacking robustness to schema changes over time.
2. **Catastrophic Forgetting**: Continual learning systems suffer from forgetting previously learned knowledge when adapting to new schema configurations.
3. **Multi-Table Context Scaling**: Large language models struggle to effectively handle multi-table contexts at scale, limiting their applicability to complex relational databases.
4. **Schema Adaptation**: Schema adaptation remains an open problem in graph machine learning approaches for multi-table data, with no established solutions for dynamic schema environments.
5. **Fixed Position Encoding Limitations**: Existing table understanding models like TAPAS rely on fixed position encodings, limiting their flexibility to handle evolving table structures.
