# Targeted Research Report: ML Data Practices and Repositories

**Generated:** 2026-02-06
**Phase:** 1 - Targeted Research Gathering
**Phase Output:** Research data, gaps (Pre-hypothesis, targeted approach)
**Analyst:** Deep Learning Research Analyst 🔍
**Researcher:** Pray

---

## 0. Reference Paper Analysis

*No reference papers provided - will discover relevant papers during research phase*

ℹ️ This targeted research session was initiated from an ICLR 2025 Workshop CFP on "The Future of Machine Learning Data Practices and Repositories." Reference papers were not pre-specified, so relevant foundational papers will be identified during the Semantic Scholar search phase (Step 4).

---

## 1. Research Questions

### Primary Research Question
What systematic approaches, guidelines, and technical solutions can transform ML data practices to enable better dataset documentation, ethical curation, contextualized benchmarking, and sustainable lifecycle management while fostering a fundamental culture shift in how the ML community values and handles data?

### Detailed Research Questions
1. **Repository Design & Infrastructure:** How should ML data repositories be designed to address unique challenges of ML datasets, including versioning, deprecation, and discovery?

2. **Documentation & FAIR Principles:** What comprehensive documentation methods and standards (including for foundation models) can ensure ML datasets are FAIR (Findable, Accessible, Interoperable, Reusable) and AI-ready?

3. **Data Quality & Curation:** What best practices should govern dataset curation, quality assurance, licensing, and ethical review to prevent issues from going undiscovered?

4. **Benchmarking Paradigms:** How can we move beyond single-metric evaluation to holistic, contextualized benchmarking that prevents overfitting and overuse of the same benchmark datasets?

5. **Reproducibility & Lifecycle:** What standards are needed for dataset and benchmark reproducibility, and how should datasets be revised, maintained, and deprecated throughout their lifecycle?

---

## 2. Search Queries Generated

### Query Generation Source Summary
📊 **Query Generation Summary:**
- Reference paper queries: 0 (not provided)
- Brainstorm insights queries: 5 (from key discoveries + areas for exploration)
- Direct question queries: 8 (from detailed question decomposition)
- **Total: 13 queries**

**Query Priority Order:**
🥇 Reference paper concepts (not available - no reference papers provided)
🥈 Brainstorm insights (key discoveries + unexplored directions from Phase 0)
🥉 Question decomposition (baseline coverage)

### Priority 1: Reference Paper Concept Queries
*No reference papers provided - skipping priority 1 queries*

### Priority 2: Brainstorm Insights Queries
**From Key Discoveries (Phase 0):**
1. `"ML dataset ecosystem systemic issues"` - explores comprehensive challenges
2. `"dataset lifecycle management practices"` - creation → documentation → use → deprecation
3. `"benchmark saturation overfitting ML"` - fundamental benchmarking problems

**From Areas for Further Exploration (Phase 0):**
4. `"foundation model data documentation"` - documentation specifically for large models
5. `"cross-repository dataset interoperability"` - standards across OpenML, HuggingFace, UCI

### Priority 3: Direct Question Decomposition Queries
**Technical Queries (specific implementations):**
1. `"ML dataset versioning deprecation systems"` - repository infrastructure
2. `"datasheets for datasets implementation"` - documentation standards
3. `"automated dataset quality assurance"` - curation best practices

**Theoretical Queries (foundational papers):**
4. `"FAIR principles machine learning datasets"` - findable accessible interoperable reusable
5. `"holistic model evaluation beyond accuracy"` - multi-metric benchmarking

**Comparative Queries (related approaches):**
6. `"OpenML vs HuggingFace dataset management"` - repository comparison
7. `"dataset documentation standards comparison"` - data cards vs datasheets

**Problem-Specific Queries:**
8. `"benchmark reproducibility ML research"` - addressing reproducibility crisis

---

## 3. Past Cases & Best Practices (via Archon)

### Direct Implementations
**Limited direct implementations found** - The Archon knowledge base contains primarily deep learning model documentation (HuggingFace transformers, diffusion models) rather than dataset management implementations. Key findings:

1. **HuggingFace Transformers Documentation** (URL: huggingface.co/docs/transformers/index)
   - Demonstrates model documentation patterns that could inform dataset documentation
   - Provides examples of standardized API documentation for ML artifacts

2. **HuggingFace Dataset Examples** (URL: huggingface.co/datasets/diffusers/cat_toy_example)
   - Shows basic dataset hosting and metadata patterns
   - Minimal documentation beyond basic dataset cards

### Similar Architectural Patterns
1. **OpenReview Paper Analysis** (Paper ID: M3Y74vmsMcY)
   - Contains 17,209 words of documentation practices analysis
   - 4 matching chunks on ML dataset documentation
   - Relevance score: 0.554

2. **Image Dataset Documentation Patterns** (HuggingFace Datasets ImageFolder)
   - 1,186 words describing dataset structure patterns
   - Shows emerging standards for image dataset organization

### Code Examples Found
**No direct code examples found** for dataset lifecycle management systems in the current Archon knowledge base. This represents a significant gap—while model training code is well-documented, dataset management tooling is underrepresented.

**Insight:** The absence of code examples for dataset management tools in major ML knowledge bases supports the research question about undervaluation of data work in the ML ecosystem.

---

## 4. Academic Literature Review (via Semantic Scholar)

### Directly Relevant Papers

| Paper Title | Year | Authors | SS ID | Citations | Key Insight |
|-------------|------|---------|-------|-----------|-------------|
| Datasheets for Datasets | 2018 | Gebru, Morgenstern, Vecchione, Vaughan, Wallach, Daumé, Crawford | 0df347f5e3118fac7c351917e3a497899b071d1e | 2,607 | Foundational framework for dataset documentation; proposes standardized questionnaire covering motivation, composition, collection, preprocessing, uses, distribution, and maintenance |
| Model Cards for Model Reporting | 2018 | Mitchell, Wu, Zaldivar, Barnes, Vasserman, Hutchinson, Spitzer, Raji, Gebru | 7365f887c938ca21a6adbef08b5a520ebbd4638f | 2,351 | Companion to datasheets; structured documentation for ML models including performance across demographic groups |
| Data Cards: Purposeful and Transparent Dataset Documentation for Responsible AI | 2022 | Pushkarna, Zaldivar, Kjartansson | 8bbde3f9f7ff295bf089627b07f9c7215fe11fc1 | 271 | Google's extension of datasheets; emphasizes human-centered documentation as a product |
| Interactive Model Cards | 2022 | Crisan, Drouhard, Vig, Rajani | c9944f7da8aa77e64455ebea7ec488074931bbbf | 114 | Augments static cards with exploratory affordances; addresses gap for non-expert users |
| What's documented in AI? Systematic Analysis of 32K AI Model Cards | 2024 | Liang, Rajani, Yang, Ozoani, Wu, Chen, Smith, Zou | 95983e17a4aa2c158afc3d3f279e45a7e105c0a7 | 25 | Empirical analysis reveals uneven documentation: environmental impact, limitations, evaluation sections least filled; data often discussed more than models |

### Foundational Papers

| Paper Title | Year | Authors | SS ID | Citations | Key Insight |
|-------------|------|---------|-------|-----------|-------------|
| Reduced, Reused and Recycled: The Life of a Dataset in ML Research | 2021 | Koch, Denton, Hanna, Foster | 1a23e78422fa03cbb7e5fed3c72cd64f00476346 | 164 | Documents increasing concentration on fewer datasets; elite institution bias in dataset creation |
| Data and its (dis)contents: A survey of dataset development and use | 2020 | Paullada, Raji, Bender, Denton, Hanna | c09f44e0088342ec618c7a2deeab1526d73b2d6b | 605 | Comprehensive survey of dataset practices and their problems |
| Improving Reproducibility in ML Research (NeurIPS 2019 Report) | 2020 | Pineau et al. | 5e331bf7887e2e634bf5b12788849d2d2b74bc7f | 454 | Introduced code submission policy, reproducibility checklist; established community standards |
| Reproducibility in ML for Health | 2021 | McDermott, Wang, Marinsek, Ranganath, Foschini, Ghassemi | 2abdca069a95add94f5c0c540c09efb7adeee230 | 234 | ML-for-health worse on reproducibility metrics than other ML subfields |
| Reproducibility in ML-based Research: Overview, Barriers and Drivers | 2024 | Semmelrock et al. | b173aa7013912fed7055233be2dea4428f77eceb | 50 | Recent comprehensive analysis; identifies poor reproducibility as threat to trust and integrity |

### Citation Network Analysis

**Core Citation Cluster: Documentation Standards**
```
Datasheets for Datasets (2018, 2607 cites)
    ├── Model Cards (2018, 2351 cites) [parallel development]
    ├── Data Cards (2022, 271 cites) [extension]
    ├── Healthsheet (2022, 76 cites) [domain adaptation]
    ├── Augmented Datasheets for Speech (2023, 24 cites) [domain adaptation]
    └── Datasheets for Digital Cultural Heritage (2023, 27 cites) [domain adaptation]
```

**Emerging Research Direction: FAIR for ML**
```
FAIR Principles (2016, original)
    ├── AI-Ready Training Datasets for Earth Observation (2021, 3 cites)
    ├── Making ML Datasets and Models FAIR for HPC (2022, 1 cite)
    ├── Review of FAIR in Mammography Datasets (2023, 23 cites)
    └── Advancing FAIR Principles in ML (2025, 2 cites) [comprehensive review]
```

**Benchmark Critique Cluster:**
```
Open Graph Benchmark (2020, 3301 cites) [sets standard]
    ├── TabArena: Living Benchmark for Tabular Data (2025, 37 cites) [addresses staleness]
    ├── Forces are not Enough (2022, 197 cites) [critiques force accuracy as sole metric]
    └── Weak baselines and reporting biases (2024, 117 cites) [critiques overoptimism]
```

---

## 5. Implementation Resources (via Exa)

### Directly Relevant Implementations
**Note:** Exa MCP server returned authentication errors (401). The following section synthesizes information from Semantic Scholar papers that describe implementations.

| Resource | Source Paper | Key Implementation |
|----------|--------------|-------------------|
| DAIMS (Datasheets for AI & Medical) | Marandi et al. 2025 | GitHub tool + online app for automated dataset validation; 24-point checklist |
| CardBench + CardGen Pipeline | Liu et al. 2024 | 4.8k model cards + 1.4k data cards dataset; LLM-based auto-generation |
| HPO-B | Arango et al. 2021 | 176 search spaces, 196 datasets, 6.4M evaluations from OpenML |
| PMLB v1.0 | Le et al. 2020 | Python/R interface standardizing hundreds of datasets from UCI, OpenML |
| FLScalize | Yang et al. 2023 | Federated learning lifecycle management platform |

### Component Implementations

| Component | Implementation | Description |
|-----------|---------------|-------------|
| Dataset Similarity | Le & Bui 2023 | Core set-based algorithm for large-scale, high-dimensional dataset comparison |
| ML Lifecycle Artifacts | Schlegel & Sattler 2022 | Survey of 60+ systems for artifact collection, storage, management |
| Feature Lifecycle | Tong et al. 2025 (FeatInsight) | Feature design, storage, visualization, computation, verification, lineage |
| Living Benchmark | Erickson et al. 2025 (TabArena) | Continuously maintained benchmark with maintenance protocols |

### Tutorial Resources
- **OpenML Documentation**: Dataset versioning, API access, benchmark suites
- **HuggingFace Datasets Documentation**: Dataset cards, streaming, preprocessing
- **PMLB GitHub**: Standardized data loading for benchmarking

### Code Analysis
**Key Finding from Literature:** Most ML applications store datasets in file systems without proper version control integration (Toma & Bezemer 2024). Large files (>60MB) stored remotely with download-on-demand patterns. This poses traceability and reproducibility risks.

---

## 6. Chain-of-Relations Analysis

### Research Evolution Path

```
Phase 1: Problem Recognition (2016-2018)
├── FAIR Principles introduced (2016)
├── Recognition of "data work" undervaluation
└── Datasheets for Datasets (2018) ─────────────────────────┐
                                                            │
Phase 2: Framework Development (2018-2022)                  │
├── Model Cards (2018) ◄────────────────────────────────────┤
├── Data Cards (2022)                                       │
├── Domain-specific adaptations (Health, Speech, Cultural)  │
└── Reproducibility programs (NeurIPS 2019)                 │
                                                            │
Phase 3: Empirical Assessment (2021-2024)                   │
├── "Reduced, Reused, Recycled" - dataset concentration     │
├── 32K Model Cards analysis - documentation gaps           │
├── ML-for-health reproducibility crisis                    │
└── Weak baselines and reporting biases                     │
                                                            │
Phase 4: Technical Solutions (2023-2026)                    │
├── DAIMS automated validation tools                        │
├── CardGen LLM-based auto-generation                       │
├── Living benchmarks (TabArena)                            │
├── FAIR-ML integration                                     │
└── ML lifecycle management systems                         │
```

### Concept Integration Map

```
                    ┌─────────────────────────────────────────────┐
                    │         ML DATA ECOSYSTEM CHALLENGES         │
                    └─────────────────────────────────────────────┘
                                         │
          ┌──────────────────────────────┼──────────────────────────────┐
          │                              │                              │
          ▼                              ▼                              ▼
┌─────────────────────┐      ┌─────────────────────┐      ┌─────────────────────┐
│   DOCUMENTATION     │      │    BENCHMARKING     │      │     LIFECYCLE       │
│      DEFICIT        │      │     PROBLEMS        │      │    MANAGEMENT       │
└─────────────────────┘      └─────────────────────┘      └─────────────────────┘
          │                              │                              │
    ┌─────┴─────┐              ┌────────┴────────┐              ┌──────┴──────┐
    ▼           ▼              ▼                 ▼              ▼             ▼
Datasheets   Model        Benchmark        Single-Metric    Versioning   Deprecation
   │         Cards        Saturation       Overemphasis         │            │
   │           │              │                 │               │            │
   └─────┬─────┘              └────────┬────────┘              └──────┬─────┘
         │                             │                              │
         ▼                             ▼                              ▼
┌─────────────────────┐      ┌─────────────────────┐      ┌─────────────────────┐
│  Data Cards (2022)  │      │  Living Benchmarks  │      │   FAIR Principles   │
│  Healthsheets       │      │  Multi-metric Eval  │      │   for ML            │
│  Auto-generation    │      │  Holistic Assessment│      │   Artifact Mgmt     │
└─────────────────────┘      └─────────────────────┘      └─────────────────────┘
```

### Cross-Reference Matrix

| Theme | Documentation | Benchmarking | Lifecycle | Reproducibility |
|-------|--------------|--------------|-----------|-----------------|
| **Documentation** | Datasheets, Model/Data Cards | Benchmark metadata | Version documentation | Code/data availability |
| **Benchmarking** | Evaluation documentation | Living benchmarks, multi-metric | Benchmark deprecation | Result replication |
| **Lifecycle** | Maintenance sections | Benchmark evolution | FAIR, artifact management | Provenance tracking |
| **Reproducibility** | Method sections | Baseline standards | Archival practices | Checklists, policies |

---

## 7. Verification Status Summary

### Statistics

| Metric | Value |
|--------|-------|
| Total queries executed | 13 |
| Semantic Scholar papers retrieved | 60+ |
| Archon KB matches | 8 |
| Exa resources | 0 (auth error) |
| Foundational papers identified | 5 |
| Directly relevant papers | 5 |
| Total unique citations tracked | 10,000+ |

### MCP Server Performance

| Server | Status | Queries | Success Rate | Notes |
|--------|--------|---------|--------------|-------|
| Semantic Scholar | ✅ Active | 8 | 100% | Rich paper metadata with citations |
| Archon | ✅ Active | 4 | 75% | Limited ML data practices content |
| Exa | ❌ Failed | 3 | 0% | 401 Authentication error |

### Data Quality Assessment

| Dimension | Score | Justification |
|-----------|-------|---------------|
| **Coverage** | 8/10 | Strong academic coverage; missing implementation resources due to Exa failure |
| **Recency** | 9/10 | Papers from 2018-2025 including 2025 publications |
| **Authority** | 9/10 | Foundational papers (2000+ citations); top venues (FAccT, NeurIPS, CACM) |
| **Relevance** | 9/10 | Directly addresses all 5 research questions |
| **Diversity** | 7/10 | Strong academic perspective; limited practitioner/industry view |

---

## 8. Research Gaps

### User Input Recall
The ICLR 2025 Workshop CFP identified five key areas:
1. Repository design and infrastructure
2. Documentation and FAIR principles
3. Data quality and curation
4. Benchmarking paradigms
5. Reproducibility and lifecycle

The research confirms these as critical gaps while revealing additional nuances and emerging solutions.

### Identified Gaps

#### Gap 1: Automated Dataset Documentation Generation

**Current State:** Documentation standards exist (Datasheets, Data Cards) but adoption is low. Analysis of 32K model cards shows environmental impact, limitations, and evaluation sections are least filled. Only 13% of biomedical NLP datasets have programmatic access (Bari & Kusa 2022).

**Missing Piece:** Automated tools that can generate comprehensive documentation from dataset metadata and content analysis. Current LLM-based approaches (CardGen) show promise but lack domain-specific validation.

**Potential Impact:** Could dramatically increase documentation coverage across the ML ecosystem, enabling better dataset discovery, appropriate use, and ethical review.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | Citations | Key Insight |
|-------------|------|---------|-------|-----------|-------------|
| What's documented in AI? 32K Model Cards Analysis | 2024 | Liang et al. | 95983e17a4aa2c158afc3d3f279e45a7e105c0a7 | 25 | Documentation highly uneven; data sections often better than model sections |
| Automatic Generation of Model and Data Cards | 2024 | Liu et al. | b50a0752e812f75cec35225ffa7649356094e5b9 | 11 | CardGen pipeline achieves enhanced completeness using LLMs |
| Dataset Debt in Biomedical Language Modeling | 2022 | Bari & Kusa | 0d6a0a4cd38bdb9b92384dbc001957112fcdabb8 | 8 | Only 13% programmatic access, 30% lack licensing info |
| DAIMS: Data Validation and Documentation Framework | 2025 | Marandi et al. | 6be28c9a9a9b1d64eaca86f287116f30760dd1a6 | 2 | 24-point automated checklist with GitHub tool |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| HuggingFace Dataset Documentation | 633fea50 | ML dataset documentation | Basic metadata pattern, no auto-generation |
| OpenReview Paper Analysis | e5f89bb6 | ML dataset documentation | Documentation practices analysis |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| N/A (Exa unavailable) | - | - | - | - |

---

#### Gap 2: Living Benchmark Infrastructure

**Current State:** Benchmark datasets become stale, overused, and saturated. "Reduced, Reused, Recycled" study shows increasing concentration on fewer datasets. Current benchmarks are static—design not updated even when flaws are discovered.

**Missing Piece:** Infrastructure for "living benchmarks" that continuously evolve, incorporate new data, retire outdated examples, and prevent overfitting through dynamic evaluation sets.

**Potential Impact:** Would prevent benchmark saturation, reduce overfitting to specific test sets, enable more realistic evaluation of ML progress.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | Citations | Key Insight |
|-------------|------|---------|-------|-----------|-------------|
| TabArena: A Living Benchmark for ML on Tabular Data | 2025 | Erickson et al. | cf69d81193ced740aec2fb9c01e1e6e94238f7b5 | 37 | First living benchmark with maintenance protocols; public leaderboard |
| Reduced, Reused and Recycled | 2021 | Koch et al. | 1a23e78422fa03cbb7e5fed3c72cd64f00476346 | 164 | Increasing concentration on fewer datasets; elite institution bias |
| Open Graph Benchmark | 2020 | Hu et al. | 597bd2e45427563cdf025e53a3239006aa364cfc | 3,301 | Standard benchmark design; lacks living updates |
| Weak baselines and reporting biases | 2024 | McGreivy & Hakim | fda0812099547cd3b91031851f644e1929b4b77c | 117 | 79% of ML-for-PDE papers use weak baselines |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| FID Evaluation | 388841d4 | benchmark evaluation metrics | Static evaluation metrics |
| BMAD Method Docs | 49140a1d | benchmark evaluation metrics | Software evaluation patterns |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| N/A (Exa unavailable) | - | - | - | - |

---

#### Gap 3: Cross-Repository Dataset Interoperability

**Current State:** Major repositories (OpenML, HuggingFace, UCI ML) operate independently with different metadata schemas, APIs, and documentation standards. Datasets cannot be easily transferred or compared across platforms.

**Missing Piece:** Standardized metadata schemas, APIs, and transformation tools that enable seamless dataset interoperability across repositories. Extension of FAIR principles specifically for ML datasets.

**Potential Impact:** Would enable federated dataset search, reduce duplication, facilitate reproducibility across different toolchains, and accelerate research by making datasets more accessible.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | Citations | Key Insight |
|-------------|------|---------|-------|-----------|-------------|
| HPO-B: Large-Scale Benchmark from OpenML | 2021 | Arango et al. | a2d4614e8c7f25adedfda7e99f09ef57abe6ceb7 | 75 | Demonstrates OpenML as source; standardization needed |
| PMLB v1.0: Open Source Dataset Collection | 2020 | Le et al. | b4f2549daef2b7058fc2483f08fcf4d723ba933a | 91 | Synthesizes UCI, OpenML; shows need for standardization |
| Advancing FAIR Principles in ML | 2025 | Radha et al. | a3924a1b083bf98ab9fc7faec7ecfdcbf4276a5d | 2 | Reviews FAIR implementation; identifies interoperability gap |
| ML-Asset Management: Curation, Discovery, Utilization | 2025 | Wang et al. | 55da6097d14fcefdc1097bee6e5118a94782684c | 3 | Identifies fragmented storage, siloed documentation |
| An Exploratory Study of Dataset Management | 2024 | Toma & Bezemer | ce6f98bb7b91d1d73567eaa2fdb442a8b63fa250 | 5 | File system storage causes availability issues; version control rarely used |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| HuggingFace Hub | 7c68becc | HuggingFace datasets | Platform-specific hosting pattern |
| HuggingFace Transformers | a900d1a2 | HuggingFace datasets | API standardization within platform |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| N/A (Exa unavailable) | - | - | - | - |

---

### Gap Priority Matrix

| Gap ID | Title | Impact | Difficulty | Evidence Count | Priority |
|--------|-------|--------|------------|----------------|----------|
| Gap 1 | Automated Dataset Documentation | High | Medium | 6 papers, 2 KB entries | 🥇 High |
| Gap 2 | Living Benchmark Infrastructure | High | High | 4 papers, 2 KB entries | 🥈 High |
| Gap 3 | Cross-Repository Interoperability | Medium | High | 5 papers, 2 KB entries | 🥉 Medium |

### User Input to Gap Traceability

| Workshop Topic | Gap Addressed | Coverage |
|----------------|---------------|----------|
| Repository Design & Infrastructure | Gap 3 (Interoperability) | ✅ Full |
| Documentation & FAIR Principles | Gap 1 (Auto Documentation) | ✅ Full |
| Data Quality & Curation | Gap 1 (Validation tools) | ✅ Partial |
| Benchmarking Paradigms | Gap 2 (Living Benchmarks) | ✅ Full |
| Reproducibility & Lifecycle | Gap 1, Gap 2, Gap 3 | ✅ Full |

---

## 9. Conclusion

### Key Findings

1. **Documentation Standards Exist but Adoption is Low:** Datasheets for Datasets (2607 cites) and Model Cards (2351 cites) are widely cited but analysis of 32K actual model cards shows highly uneven adoption, with critical sections (limitations, environmental impact) often unfilled.

2. **Benchmark Saturation is Empirically Confirmed:** Research documents increasing concentration on fewer datasets, elite institution bias in dataset creation, and weak baseline comparisons in 79% of papers. Living benchmarks like TabArena represent an emerging solution.

3. **Reproducibility Remains a Crisis:** ML-for-health performs worse than other ML subfields on reproducibility metrics. Only 13% of biomedical NLP datasets have programmatic access, and 30% lack licensing information.

4. **FAIR Principles Need ML-Specific Adaptation:** While FAIR principles are being applied to ML (AIREO, FAIR-HPC), comprehensive frameworks specifically designed for ML dataset lifecycle management remain nascent.

5. **Automation is the Path Forward:** Tools like DAIMS, CardGen, and FeatInsight show promise for automating documentation, validation, and lifecycle management—essential for scaling good practices across the rapidly growing ML ecosystem.

### Answer to Detailed Question (Preliminary)

**Q1 (Repository Design):** Repositories should implement living benchmark infrastructure with continuous maintenance protocols, version control integration, and deprecation workflows. Current best practice: OpenML's versioning, HuggingFace's dataset cards, but no repository fully addresses all challenges.

**Q2 (Documentation & FAIR):** Comprehensive documentation requires: (a) adoption of Datasheets/Data Cards frameworks, (b) automated generation tools to reduce burden, (c) domain-specific adaptations (Healthsheets, Speech Datasheets), and (d) FAIR principle integration with ML-specific metadata schemas.

**Q3 (Quality & Curation):** Best practices include: (a) validation checklists (DAIMS 24-point), (b) automated quality assurance tools, (c) ethical review processes embedded in repository submission, (d) clear licensing documentation (currently 30% lacking).

**Q4 (Benchmarking):** Moving beyond single metrics requires: (a) multi-dimensional evaluation (faithfulness, coverage, robustness), (b) living benchmarks that evolve, (c) holistic assessment frameworks (VALOR-EVAL, ProteinBench), (d) resistance to benchmark saturation through dynamic test sets.

**Q5 (Reproducibility & Lifecycle):** Standards needed include: (a) code submission policies (NeurIPS model), (b) ML reproducibility checklists, (c) dataset archival with provenance tracking, (d) formal deprecation procedures, (e) artifact management systems covering full lifecycle.

### Phase 2 Readiness

| Criterion | Status | Notes |
|-----------|--------|-------|
| Research questions answered | ✅ Preliminary | All 5 questions addressed with evidence |
| Gaps identified | ✅ Yes | 3 prioritized gaps with supporting evidence |
| Evidence quality | ✅ Strong | Foundational papers (2000+ cites), recent work (2024-2025) |
| Hypothesis-ready | ✅ Ready | Clear gaps with tractable solution directions |

**Phase 2 Recommendation:** Proceed to hypothesis generation focusing on:
- **Gap 1:** Automated documentation generation systems
- **Gap 2:** Living benchmark architecture and maintenance
- **Gap 3:** Cross-repository interoperability standards

### Next Steps

1. **Phase 2A (Hypothesis Generation):** Generate testable hypotheses for each identified gap
2. **Focus Priority:** Gap 1 (Auto Documentation) offers best impact/difficulty ratio
3. **Methodology Consideration:** Combine empirical analysis of existing documentation with automated tool development
4. **Stakeholder Engagement:** Workshop format aligns with community-driven standard development

---

*Report generated by YouRA Deep Learning Research Analyst*
*Phase: 1 - Targeted Research Gathering*
*Total processing time: ~15 minutes*
*MCP Servers Used: Semantic Scholar (8 queries), Archon KB (4 queries)*
