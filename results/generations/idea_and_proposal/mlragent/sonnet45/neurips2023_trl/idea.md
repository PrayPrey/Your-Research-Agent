# Title
Contrastive Pre-training for Cross-Table Schema Alignment and Semantic Type Detection

# Motivation
Real-world tabular data suffers from extreme schema heterogeneity—the same semantic concept appears under different column names, types, and formats across tables. Current table representation models struggle to capture semantic similarities across diverse schemas, limiting their effectiveness in critical data integration and preparation tasks. This problem is particularly acute in enterprise settings where thousands of tables with inconsistent schemas need to be understood, integrated, and queried. Existing approaches either rely on expensive manual annotation or fail to generalize across domains.

# Main Idea
We propose a contrastive learning framework that pre-trains table encoders to recognize semantic equivalence across heterogeneous schemas. The key innovation is generating positive pairs through controlled schema transformations (renaming columns, reordering, type casting) and augmentations (value paraphrasing, format changes) while maintaining semantic meaning. Negative pairs come from semantically different columns within and across tables.

The model learns column-level and table-level representations simultaneously using a dual-encoder architecture with: (1) a column encoder capturing local semantics from values and metadata, and (2) a table encoder capturing global relational context. We incorporate hard negative mining by sampling structurally similar but semantically different columns.

Expected outcomes include state-of-the-art performance on schema matching, semantic type detection, and zero-shot table integration tasks. This approach enables robust table understanding across domains without task-specific fine-tuning, directly addressing production challenges in data cataloging and preparation pipelines.