---
source_paper: "arxiv_2411_00266.md"
generated_at: "2026-03-15T02:47:15.181275"
model: "gpt-4o-mini"
summary_chars: 6310
---

# A Systematic Review of NeurIPS Dataset Management Practices

## Key Metadata
- **Authors:** Yiwei Wu et al.
- **Year:** 2023
- **Venue:** arXiv
- **Core Contribution:** This paper presents a systematic review of dataset management practices in the NeurIPS community, highlighting significant inconsistencies in provenance, distribution, ethical disclosures, and licensing.

## Section Summaries

### Abstract
As new machine learning methods demand larger training datasets, researchers and developers face significant challenges in dataset management. Although ethics reviews, documentation, and checklists have been established, it remains uncertain whether consistent dataset management practices exist across the community. This lack of a comprehensive overview hinders our ability to diagnose and address fundamental tensions and ethical issues related to managing large datasets. We present a systematic review of datasets published at the NeurIPS Datasets and Benchmarks track, focusing on four key aspects: provenance, distribution, ethical disclosure, and licensing. Our findings reveal that dataset provenance is often unclear due to ambiguous filtering and curation processes. Additionally, a variety of sites are used for dataset hosting, but only a few offer structured metadata and version control. These inconsistencies underscore the urgent need for standardized data infrastructures for the publication and management of datasets.

### Introduction & Motivation
Datasets are foundational in machine learning, driving advancements but also raising ethical concerns such as lack of consent, documentation debt, legal risks, and malign content. To promote responsible dataset management, various procedures have been proposed, yet limited research has systematically examined data management practices at scale. The absence of a comprehensive overview limits the ability to address key tensions in managing large datasets. This study reviews 238 dataset papers from the NeurIPS Datasets and Benchmarks track focusing on provenance, distribution, ethical disclosure, and licensing—highlighting gaps and inconsistencies in practices that could inform better dataset stewardship.

### Methodology
The study systematically reviewed 238 dataset papers published at NeurIPS in 2021 (73 papers), 2022 (85 papers), and a random sample of 80 papers from the 193 published in 2023. Papers focusing solely on comparing benchmarks without new datasets were excluded. The review categorizes practices across four aspects: 

1. **Provenance:** Tracing the original source and data creation.
2. **Distribution:** How datasets were shared (hosting sites such as Zenodo, GitHub, and personal websites).
3. **Ethical Disclosures:** Addressing ethical concerns reported by authors.
4. **Licensing:** The types of licenses applied to datasets.

A qualitative approach was employed, using a schema established by the first and last authors to categorize the papers. They independently annotated papers and executed periodic cross-checks.

**Notable findings include:**
- 57% of datasets were collected post hoc from existing sources, complicating provenance tracing.
- Various hosting sites led to inconsistent metadata reporting and lack of support for version control.
- Ethical considerations were addressed inconsistently, with only 40% of papers discussing potential ethical concerns.
- Creative Commons licenses were predominant, utilized by 61 papers, but notable gaps in license clarity were found (e.g., 36 papers lacked defined licenses).

### Experiments & Results
The review encompasses a diverse range of datasets, including images, texts, and action logs across domains like health, banking, and biology. The study aims not to critique existing practices but to highlight gaps for improving guidelines and processes. Key results show:
- Provenance tracing varied significantly; 57% of datasets were post hoc, often leading to unclear data collection processes.
- Distribution patterns showed 44 papers used personal websites, 34 used Zenodo, and 33 GitHub, with only sites like Zenodo supporting metadata and DOIs.
- Ethical disclosures were present in 96 papers, primarily concerning privacy and sampling biases, with significant gaps in expressing potential bias or misuse.
- Licensing demonstrated a reliance on Creative Commons, but with notable ambiguity in terms of licensing information's location, affecting user access and understanding.

**Main Result Table:**
| Aspect            | Findings                                   |
|-------------------|-------------------------------------------|
| Provenance        | 57% post hoc, unclear details              |
| Distribution      | Dominant sites: Personal (44), Zenodo (34), GitHub (33) |
| Ethical Disclosures| 40% mentioned concerns like privacy and biases |
| Licensing         | Predominantly Creative Commons with 36 papers without clear license |

### Discussion & Conclusion
Inconsistent dataset management practices highlight the urgent need for standardized infrastructures supporting dataset sharing and ethical management. The findings also indicate that compliance issues with the FAIR principles (Findable, Accessible, Interoperable, Reusable) are prevalent. Recommendations include developing structured documentation templates, establishing clear and consistent metadata standards, and promoting robust data management infrastructures. Future work should also address secondary impacts related to dataset usage, beyond the immediate ethical concerns identified.

## Key Contributions
- Identified major inconsistencies in dataset management practices at NeurIPS.
- Recommended the establishment of standardized data infrastructures for dataset management.
- Emphasized the need for better ethical disclosures and licensing clarity in dataset papers.

## Potential Relevance
This paper's findings highlight the need for improved dataset management practices, which could inform hypotheses related to the ethical implications of dataset usage, compliance with FAIR principles, and recommendations for best practices in dataset creation and sharing. The gaps identified in provenance tracing and ethical considerations could directly facilitate discussions around improving accountability and transparency in dataset management.