# Research Idea

## Title
**TabFusion: Cross-Modal Contrastive Pre-training for Tables via SQL-Text-Schema Alignment**

## Motivation
Current table representation learning methods often treat tables in isolation or with limited modality integration. However, in real-world data ecosystems, tables are inherently connected to multiple modalities: natural language descriptions, SQL queries that manipulate them, and schema metadata. Existing approaches fail to fully exploit these rich cross-modal relationships, leading to suboptimal representations that struggle with downstream tasks requiring semantic understanding across modalities (e.g., text-to-SQL, table retrieval, schema matching). A unified pre-training framework that explicitly aligns these modalities could dramatically improve table understanding.

## Main Idea
We propose **TabFusion**, a multimodal contrastive pre-training framework that jointly learns representations across three modalities: table content, SQL queries, and natural language descriptions. 

**Methodology:**
1. Design a tri-encoder architecture with modality-specific encoders sharing cross-attention layers
2. Introduce three contrastive objectives: (a) table-SQL alignment using query-result pairs, (b) table-text alignment using table captions/descriptions, and (c) SQL-text alignment using paired query-question data
3. Leverage large-scale data from code repositories (GitHub), data catalogs, and synthetic augmentation

**Expected Outcomes:**
- Superior zero-shot transfer on text-to-SQL, table QA, and semantic table retrieval
- Robust representations for schema matching and data discovery tasks

**Impact:** Enables more intuitive human-data interaction and improves enterprise data catalog systems.