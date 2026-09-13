1. **Title**: UNJOIN: Enhancing Multi-Table Text-to-SQL Generation via Schema Simplification (arXiv:2505.18122)
   - **Authors**: Poojah Ganesan, Rajat Aayush Jha, Dan Roth, Vivek Gupta
   - **Summary**: UNJOIN introduces a two-stage framework that simplifies complex multi-table schemas by merging column names into a single-table representation. This approach decouples schema retrieval from SQL logic generation, improving performance on multi-table text-to-SQL tasks.
   - **Year**: 2025

2. **Title**: PSM-SQL: Progressive Schema Learning with Multi-granularity Semantics for Text-to-SQL (arXiv:2502.05237)
   - **Authors**: Zhuopan Yang, Yuanzhen Xie, Ruichao Zhong, Yunzhi Tan, Enjie Liu, Zhenguo Yang, Mochi Gao, Bo Hu, Zang Li
   - **Summary**: PSM-SQL proposes a framework that progressively reduces redundant database schemas by learning multi-granularity semantics at the column, table, and database levels. It employs a chain loop strategy to enhance schema linking, leading to improved text-to-SQL performance.
   - **Year**: 2025

3. **Title**: MultiTabQA: Generating Tabular Answers for Multi-Table Question Answering (arXiv:2305.12820)
   - **Authors**: Vaishali Pal, Andrew Yates, Evangelos Kanoulas, Maarten de Rijke
   - **Summary**: MultiTabQA addresses the challenge of answering questions over multiple tables by generating tabular answers. It introduces a pre-training dataset and evaluates the model's performance on multi-table QA tasks, demonstrating its effectiveness in handling complex queries.
   - **Year**: 2023

4. **Title**: CHESS: Contextual Harnessing for Efficient SQL (arXiv:2405.16755)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: CHESS presents a pipeline that selects an efficient schema augmented by relevant context to generate SQL queries. It involves candidate generation and revision steps to ensure the correctness of the SQL queries, aiming to improve efficiency in SQL generation tasks.
   - **Year**: 2024

5. **Title**: Set the Clock: Temporal Alignment of Pretrained Language Models (arXiv:2402.16797)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This work focuses on aligning pretrained language models temporally by constructing a dataset (TAQA) from Wikipedia tables. It involves generating questions and extracting answers to create QA pairs, aiming to enhance the temporal understanding of language models.
   - **Year**: 2024

6. **Title**: Popularity-Aware Alignment and Contrast for Mitigating Popularity Bias (arXiv:2405.20718)
   - **Authors**: Miaomiao Cai, Lei Chen, Yifan Wang, Haoyue Bai, Peijie Sun, Le Wu, Min Zhang, Meng Wang
   - **Summary**: This paper addresses popularity bias in collaborative filtering by proposing a method that uses supervised alignment and contrastive learning. It aims to improve the representation of unpopular items and mitigate the representation separation caused by popularity bias.
   - **Year**: 2024

7. **Title**: GraPPa: Grammar-Augmented Pre-Training for Table Semantic Parsing (arXiv:2009.13845)
   - **Authors**: Tao Yu, Chien-Sheng Wu, Xi Victoria Lin, Bailin Wang, Yi Chern Tan, Xinyi Yang, Dragomir Radev, Richard Socher, Caiming Xiong
   - **Summary**: GraPPa introduces a pre-training approach for table semantic parsing that learns compositional inductive biases in joint representations of textual and tabular data. It constructs synthetic question-SQL pairs and employs a text-schema linking objective to enhance performance on table semantic parsing benchmarks.
   - **Year**: 2020

8. **Title**: BINDER: A Training-Free Neural-Symbolic Framework for Programmatic Reasoning (arXiv:2210.02875)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: BINDER proposes a training-free neural-symbolic framework that maps task inputs to programs, allowing binding to a unified language model API for additional functionalities. It aims to combine the strengths of end-to-end and symbolic approaches, achieving state-of-the-art performance on various tasks.
   - **Year**: 2023

9. **Title**: [Title not specified in the provided excerpt] (arXiv:2405.16755)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This work presents a pipeline that selects an efficient schema augmented by relevant context to generate SQL queries. It involves candidate generation and revision steps to ensure the correctness of the SQL queries, aiming to improve efficiency in SQL generation tasks.
   - **Year**: 2024

10. **Title**: [Title not specified in the provided excerpt] (arXiv:2402.16797)
    - **Authors**: [Authors not specified in the provided excerpt]
    - **Summary**: This work focuses on aligning pretrained language models temporally by constructing a dataset (TAQA) from Wikipedia tables. It involves generating questions and extracting answers to create QA pairs, aiming to enhance the temporal understanding of language models.
    - **Year**: 2024

**Key Challenges**:

1. **Capturing Cross-Table Relationships**: Effectively modeling and understanding the semantic dependencies and relationships across multiple tables remain challenging, especially when dealing with complex schemas and foreign key constraints.

2. **Schema Simplification and Alignment**: Simplifying complex multi-table schemas without losing critical information and aligning them with natural language queries is a significant hurdle in improving text-to-SQL generation.

3. **Handling Large and Noisy Data**: Processing and reasoning over large-scale, heterogeneous, and potentially noisy tabular data require robust models capable of filtering and integrating relevant information efficiently.

4. **Temporal Understanding**: Aligning language models to understand and reason over temporal data within tables is essential for tasks requiring time-sensitive information retrieval and analysis.

5. **Mitigating Biases**: Addressing biases, such as popularity bias in collaborative filtering, is crucial to ensure fair and accurate representations of less popular items or underrepresented data in table-based learning tasks. 