---
source_paper: "arxiv_2503_13463.md"
generated_at: "2026-03-15T02:47:28.055006"
model: "gpt-4o-mini"
summary_chars: 5755
---

# Completeness of Datasets Documentation on ML/AI Repositories: An Empirical Investigation

## Key Metadata
- **Authors:** Marco Rondina, Antonio Vetrò, Juan Carlos De Martin
- **Year:** 2023
- **Venue:** Progress in Artificial Intelligence (EPIA 2023)
- **Core Contribution:** This paper analyzes the completeness of dataset documentation in ML/AI repositories and proposes a Documentation Test Sheet (dts) to evaluate essential information for transparency and accountability.

## Section Summaries

### Abstract
ML/AI is the field of computer science and computer engineering that arguably received the most attention and funding over the last decade. Data is the key element of ML/AI, so it is becoming increasingly important to ensure that users are fully aware of the quality of the datasets that they use, and of the process generating them, so that possible negative impacts on downstream effects can be tracked, analysed, and, where possible, mitigated. One of the tools that can be useful in this perspective is dataset documentation. The aim of this work is to investigate the state of dataset documentation practices, measuring the completeness of the documentation of several popular datasets in ML/AI repositories. We created a dataset documentation schema—the Documentation Test Sheet (dts)—that identifies the information that should always be attached to a dataset (to ensure proper dataset choice and informed use), according to relevant studies in the literature. We verified 100 popular datasets from four different repositories with the dts to investigate which information was present. Overall, we observed a lack of relevant documentation, especially about the context of data collection and data processing, highlighting a paucity of transparency.

### Introduction & Motivation
The study highlights the importance of datasets in ML/AI applications, where issues of fairness, transparency, and accountability often stem from the data collection and processing stages. Poor documentation undermines users' trust and can lead to negative downstream effects. The research aims to assess the amount and quality of information regarding data collection and processing available within popular ML/AI datasets, thus facilitating transparency and accountability in ML/AI systems. The main research question is: What key information documented in datasets is currently accessible to users?

### Methodology
The researchers developed the Documentation Test Sheet (dts), a schema to evaluate dataset documentation completeness. The dts focuses on essential fields grouped into six sections: 
1. **Motivation**
2. **Composition**
3. **Collection processes**
4. **Data processing procedures**
5. **Uses**
6. **Maintenance**
Each section encompasses various Test Fields adapted primarily from 'Datasheets for Datasets' and relevant literature on documentation standards.

The dts uses three Presence Check Values to assess documentation completeness: 
- **1:** Information present 
- **0:** Information absent 
- **NA:** Information not applicable

The final completeness measure, the Presence Average, is computed by averaging the respective Presence Check Values. The study analyzed datasets from four repositories—Hugging Face, Kaggle, OpenML, and UC Irvine ML Repository—selected for their popularity based on metrics like download counts or view counts. A total of 100 datasets were evaluated, with 25 from each repository.

### Experiments & Results
The analysis revealed that documentation completeness is generally low across the evaluated datasets. The results were measured using various metrics including test field averages. 

- **Results Summary:**
   - **Hugging Face** datasets showed the most comprehensive documentation, while **UCI** datasets highlighted the least.
   - For the **Uses** section, completeness averages were high (0.95 overall), while the **Collection processes** section averaged only 0.10, indicating significant gaps in documentation practices regarding data origin and processing.
   - Specific findings indicated that basic dataset information such as descriptions (0.92) and instance numbers (0.90) were commonly documented, whereas critical ethical considerations and processes received little to no documentation.

**Table 1** contains the characteristics of the 100 datasets assessed, showing trends relating to updates and presence of sensitive information.

### Discussion & Conclusion
The findings present a clear need for improved documentation practices in dataset curation within the ML/AI community. The most documented aspects concern dataset usage, whereas essential phases such as data generation and maintenance lack transparency, which could result in various issues in model training. The dts can serve as an implementable tool for dataset creators and maintainers, promoting accountability and trust in the ML/AI field. 

## Key Contributions
- Developed a comprehensive Documentation Test Sheet (dts) to evaluate dataset documentation completeness.
- Conducted an empirical analysis of 100 popular datasets across multiple ML/AI repositories.
- Highlighted significant gaps in dataset documentation, advocating for enhanced practices to ensure transparency and accountability.

## Potential Relevance
This investigation provides a structured methodology to assess dataset documentation completeness, which can guide future efforts to improve transparency in ML/AI applications. The dts method, if adopted widely, has the potential to inform best practices in dataset documentation, central to assuring dataset quality and accountability. The findings on prevalent documentation gaps can influence hypothesis development regarding dataset curation and long-term impacts on ML/AI outcomes.