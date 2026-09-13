---
source_paper: "arxiv_2410_22473.md"
generated_at: "2026-03-15T02:46:53.763300"
model: "gpt-4o-mini"
summary_chars: 8075
---

# The State of Data Curation at NeurIPS: An Assessment of Dataset Development Practices in the Datasets and Benchmarks Track

## Key Metadata
- **Authors:** Eshta Bhardwaj et al.
- **Year:** 2024
- **Venue:** NeurIPS 2024 Datasets and Benchmarks Track
- **Core Contribution:** This paper introduces a systematic evaluation framework for dataset documentation in machine learning, applied to 60 datasets presented at NeurIPS, and highlights critical areas needing improvement in data curation practices.

## Section Summaries

### Abstract
Data curation is a field with origins in librarianship and archives, whose scholarship and thinking on data issues go back centuries, if not millennia. The field of machine learning is increasingly observing the importance of data curation to the advancement of both applications and fundamental understanding of machine learning models – evidenced not least by the creation of the Datasets and Benchmarks track itself. This work provides an analysis of recent dataset development practices at NeurIPS through the lens of data curation. We present an evaluation framework for dataset documentation, consisting of a rubric and toolkit developed through a thorough literature review of data curation principles. We use the framework to systematically assess the strengths and weaknesses in current dataset development practices of 60 datasets published in the NeurIPS Datasets and Benchmarks track from 2021-2023. We summarize key findings and trends. Results indicate greater need for documentation about environmental footprint, ethical considerations, and data management. We suggest targeted strategies and resources to improve documentation in these areas and provide recommendations for the NeurIPS peer-review process that prioritize rigorous data curation in ML. We also provide guidelines for dataset developers on the use of our rubric as a standalone tool. Finally, we provide results in the format of a dataset that showcases aspects of recommended data curation practices. Our rubric and results are of interest for improving data curation practices broadly in the field of ML as well as to data curation and science and technology studies scholars studying practices in ML. Our aim is to support continued improvement in interdisciplinary research on dataset practices, ultimately improving the reusability and reproducibility of new datasets and benchmarks, enabling standardized and informed human oversight, and strengthening the foundation of rigorous and responsible ML research.

### Introduction & Motivation
The NeurIPS Datasets and Benchmarks (D&B) track was established in 2021 to address the rapid growth in machine learning applications and related challenges, such as the inappropriate use of datasets as benchmarks. This prompted the need to improve dataset quality and to encourage ethical dataset development practices. The authors recognize that effective documentation and ethical practices are critical to reducing bias and promoting responsibility in ML. They propose the introduction of a structured evaluation framework grounded in data curation principles to assess and enhance the quality of datasets produced within the NeurIPS community.

### Methodology
The authors developed an evaluation framework consisting of a rubric and a toolkit, intended for assessing dataset documentation within the D&B track. The framework is grounded in principles of data curation and embodies five primary categories: 

1. **Scope**: Covers context, purpose, motivation, and requirements of dataset development.
2. **Ethicality and Reflexivity**: Enhances awareness regarding ethical considerations and biases.
3. **Data Pipeline**: Considers data collection, processing, and annotation stages.
4. **Data Quality**: Ensures the dataset’s suitability, representativeness, authenticity, reliability, and documentation structure.
5. **Data Management**: Evaluates compliance with FAIR (Findable, Accessible, Interoperable, Reusable) principles.

In total, the rubric comprises 18 elements with pass/fail criteria for minimum standards and full/partial/none for a standard of excellence. Initial construction involved an iterative process using 25 datasets to refine the rubric through feedback and adjustments based on inter-rater reliability (IRR) measurements. The authors subsequently applied the finalized framework to assess 30 additional datasets, resulting in a total of 60 evaluations.

Key components of the approach included:
- **Inter-rater Reliability (IRR)**: Calculated using a two-way mixed, consistent average-measures intra-class coefficient (ICC) to assess evaluation consistency, achieving a median ICC of 0.90 in the final round.
- **Manual Evaluation Process**: Conducted by a team of reviewers to ensure high-quality assessments and verification of documentation against the rubric.
- **Toolkit**: Provided supplementary resources including guidelines, FAQs, sample evaluations, and further readings to assist in implementing the rubric.

### Experiments & Results
The study assessed 60 datasets submitted to the Datasets and Benchmarks track from 2021 to 2023. The evaluation metrics included pass rates for the minimum documentation standards and adherence to excellent standards for each rubric element. The findings are summarized as follows:

1. **Inter-rater Reliability**: Achieved a median ICC value of 0.90, indicating "excellent" agreement among raters across categories.
2. **Documentation Quality**: Noteworthy variability in the extent of documentation; one dataset achieved an 86% pass rate while another only 39%. The quality criteria were distinctly better for minimum standards compared to excellence measures, indicating a need for more comprehensive documentation practices.
3. **Key Findings**:
   - Elements typically recorded with high consistency included context, purpose, motivation, suitability, and reliability (all achieving 100% pass rates for minimum standards).
   - The worst-performing rubric aspects were "context awareness" and "environmental footprint," both recording 0% pass rates.
   - A downward trend over time was noted in documentation scores from 2021 to 2023, suggesting deteriorating practices despite increasing requirements for submissions.

The analysis emphasizes critical areas for improvement, especially regarding ethical considerations and environmental impacts associated with dataset creation.

### Discussion & Conclusion
The authors conclude that while NeurIPS has established a framework for dataset documentation, there remain significant gaps in ethical considerations, environmental impact, and reflexivity in dataset development. They recommend specific strategies to enhance dataset quality, such as mandatory positionality statements and environmental footprint assessments, as well as improvements to the peer-review process to emphasize rigorous curation standards. The paper highlights the importance of interdisciplinary approaches to data curation, advocating for further research into enhancing practices and frameworks that support effective dataset development and improve transparency and accountability in machine learning.

## Key Contributions
- Development of a systematic evaluation framework for assessing dataset documentation and curation practices in machine learning.
- Identification of critical areas for improvement in dataset documentation, particularly surrounding ethical considerations and environmental impacts.
- Recommendations for enhancing the peer-review process at NeurIPS to promote greater accountability and ethical diligence in dataset development.

## Potential Relevance
Aspects of this paper highlight important methodologies for evaluating dataset quality and ethical considerations, which could inform the development of new hypotheses regarding dataset documentation standards in machine learning. The proposed rubric and recommendations might be insightful for structuring future research approaches to dataset development and ensuring rigorous documentation in machine learning outputs.