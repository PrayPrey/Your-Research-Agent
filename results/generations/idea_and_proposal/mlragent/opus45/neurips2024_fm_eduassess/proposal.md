# Research Proposal: Concept-Level Explanations for LLM-Based Automated Essay Scoring via Knowledge Graph Augmentation

## 1. Introduction

### Background

The integration of large foundation models into educational assessment represents one of the most significant technological transformations in contemporary education. Models such as GPT-4, Llama, and Gemini have demonstrated remarkable capabilities in understanding and generating human-like text, offering unprecedented opportunities for automating complex assessment tasks including essay scoring. However, despite their impressive performance on scoring accuracy metrics, these models face a critical adoption barrier: the lack of explainability and accountability that stakeholders in educational ecosystems demand.

The systematic review by Yan et al. (2023) identified 53 distinct use cases for LLMs in education across nine categories, yet consistently highlighted transparency and explainability as fundamental challenges limiting practical deployment. This concern is particularly acute in high-stakes assessments where scoring decisions can significantly impact students' academic trajectories, institutional accountability, and educational equity. Current LLM-based automated essay scoring (AES) systems typically produce holistic scores without providing transparent justifications that educators, students, policymakers, and accreditation bodies can scrutinize and trust.

The challenge of explainability in AES is multifaceted. Students need actionable feedback to understand their strengths and areas for improvement. Teachers require insights into scoring rationale to validate automated assessments and provide supplementary guidance. Assessment developers need audit trails to demonstrate validity and fairness. Policymakers and regulators demand accountability mechanisms to ensure equitable treatment across diverse student populations. Simply fine-tuning LLMs for improved scoring accuracy fails to address these fundamental requirements.

Recent work on rubric-aligned Chain-of-Thought prompting, such as the QwenScore+ framework (2025), has begun addressing transparency by generating feedback aligned with human reasoning patterns. However, these approaches remain limited by their reliance on model-generated reasoning that may not consistently align with established educational constructs and may produce hallucinated justifications that appear plausible but lack grounding in validated assessment criteria.

### Research Objectives

This research proposes a novel framework for augmenting LLM-based essay scoring with educational knowledge graphs to generate concept-level explanations that are both transparent and pedagogically grounded. The specific objectives are:

1. To construct domain-specific educational knowledge graphs that encode scoring rubric criteria, learning objectives, concept hierarchies, and their interrelationships.

2. To develop a retrieval-augmented scoring framework (KAES: Knowledge-Augmented Essay Scoring) that leverages knowledge graph structures to guide LLM scoring decisions.

3. To implement a structured explanation module that traces scoring decisions to specific rubric criteria and identified concept coverage, producing audit trails suitable for validity studies.

4. To empirically validate the framework's effectiveness in terms of scoring accuracy, explanation quality, and stakeholder trust.

### Significance

This research directly addresses the explainability and accountability challenges identified as primary barriers to AI adoption in large-scale educational assessments. By grounding LLM-generated explanations in established educational knowledge structures, the proposed approach offers several significant contributions:

- **Enhanced Trust**: Explanations anchored in validated rubric criteria and learning objectives provide stakeholders with verifiable justifications for scoring decisions.
- **Actionable Feedback**: Concept-level analysis enables detailed, pedagogically meaningful feedback that students can use for targeted improvement.
- **Audit Capability**: Explicit knowledge graph pathways create traceable reasoning chains suitable for fairness audits and validity studies.
- **Reduced Hallucination**: Constraining LLM reasoning through knowledge graph structures mitigates the risk of plausible-sounding but unfounded justifications.

## 2. Methodology

### 2.1 Educational Knowledge Graph Construction

The first phase involves constructing comprehensive domain-specific knowledge graphs that capture the multidimensional structure of essay assessment criteria.

**Knowledge Graph Schema Design**: The knowledge graph $\mathcal{G} = (V, E, R)$ consists of vertices $V$, edges $E$, and relation types $R$. We define the following entity types:

- **Rubric Criteria** ($RC$): Discrete scoring dimensions (e.g., thesis clarity, evidence quality, organization)
- **Performance Levels** ($PL$): Score bands with associated descriptors
- **Learning Objectives** ($LO$): Educational goals the assessment targets
- **Concepts** ($C$): Domain knowledge elements relevant to essay topics
- **Linguistic Indicators** ($LI$): Textual markers associated with quality levels

Relation types include:
- $\text{requires}(LO, C)$: Learning objective requires mastery of concept
- $\text{assesses}(RC, LO)$: Rubric criterion assesses learning objective
- $\text{indicates}(LI, PL)$: Linguistic indicator suggests performance level
- $\text{prerequisite}(C_i, C_j)$: Concept $C_i$ is prerequisite for $C_j$
- $\text{evidences}(LI, RC)$: Linguistic indicator serves as evidence for rubric criterion

**Knowledge Graph Population**: We employ a hybrid approach combining:

1. **Expert Curation**: Domain experts annotate rubric documents, learning standards, and scoring guides to extract core entities and relationships.

2. **LLM-Assisted Extraction**: Using structured prompting, we leverage GPT-4 to expand the knowledge graph by identifying additional concepts, indicators, and relationships from assessment documentation:

$$P_{extract} = \text{LLM}(D_{rubric}, \mathcal{G}_{seed}, T_{extraction})$$

where $D_{rubric}$ is rubric documentation, $\mathcal{G}_{seed}$ is the expert-curated seed graph, and $T_{extraction}$ is the extraction prompt template.

3. **Validation**: Expert reviewers verify LLM-extracted additions, ensuring knowledge graph quality through iterative refinement.

### 2.2 Knowledge-Augmented Essay Scoring Framework (KAES)

The KAES framework integrates knowledge graph retrieval with LLM-based scoring through a three-stage pipeline.

**Stage 1: Essay Analysis and Concept Extraction**

Given an input essay $E$, we first extract relevant concepts and linguistic features:

$$\mathcal{C}_E = \text{ConceptExtractor}(E, \mathcal{G})$$

The concept extractor uses embedding-based retrieval to identify knowledge graph concepts present in the essay. For each sentence $s_i \in E$, we compute:

$$\text{sim}(s_i, c_j) = \frac{\text{emb}(s_i) \cdot \text{emb}(c_j)}{||\text{emb}(s_i)|| \cdot ||\text{emb}(c_j)||}$$

where $\text{emb}(\cdot)$ denotes sentence embeddings from a fine-tuned encoder. Concepts exceeding threshold $\tau$ are included in $\mathcal{C}_E$.

**Stage 2: Knowledge Graph-Guided Reasoning**

We construct a reasoning context by traversing the knowledge graph from identified concepts to relevant rubric criteria:

$$\mathcal{P} = \{p : p = \text{path}(c, rc) \mid c \in \mathcal{C}_E, rc \in RC, \text{len}(p) \leq k\}$$

where $\mathcal{P}$ is the set of knowledge graph paths connecting extracted concepts to rubric criteria within $k$ hops.

The reasoning context is structured as:

$$\text{Context}_\mathcal{G} = \text{Serialize}(\mathcal{C}_E, \mathcal{P}, \text{relevant\_descriptors})$$

**Stage 3: Constrained Chain-of-Thought Scoring**

We employ constrained Chain-of-Thought (CoT) prompting where the LLM generates scoring rationale explicitly referencing knowledge graph elements:

$$\text{Score}, \text{Explanation} = \text{LLM}(E, \text{Context}_\mathcal{G}, T_{scoring})$$

The scoring prompt template $T_{scoring}$ enforces structured output:

```
Given the essay and the following assessment context from the knowledge graph:
[Context_G]

For each rubric criterion, provide:
1. Evidence from the essay (direct quotes)
2. Relevant concepts identified: [must reference C_E]
3. Performance level determination with justification
4. Specific strengths and improvement areas

Final holistic score with weighted criterion aggregation.
```

The constrained generation ensures explanations reference verified knowledge graph elements rather than hallucinated criteria.

### 2.3 Explanation Generation Module

The explanation module transforms raw LLM output into structured, stakeholder-appropriate explanations:

**For Students**: Concept-level feedback highlighting:
- Demonstrated concept mastery with textual evidence
- Missing or underdeveloped concepts with learning recommendations
- Specific rubric criteria achievements and gaps

**For Educators**: Audit-ready documentation including:
- Complete knowledge graph pathway traces
- Criterion-level score breakdown
- Confidence indicators based on evidence density

The explanation quality is enhanced through a post-processing step:

$$\text{Explanation}_{final} = \text{Validate}(\text{Explanation}_{raw}, \mathcal{G}, E)$$

where the validation function verifies that all referenced concepts and criteria exist in $\mathcal{G}$ and cited evidence exists in $E$.

### 2.4 Experimental Design

**Datasets**: We evaluate KAES on two established AES datasets:
1. **ASAP (Automated Student Assessment Prize)**: 8 prompts with holistic scores, approximately 13,000 essays
2. **TOEFL11**: Essays from English language learners with detailed rubric scores

Additionally, we collect a new dataset with expert-annotated concept-level feedback for 500 essays across three domains to evaluate explanation quality.

**Baselines**: We compare against:
- Fine-tuned BERT-based AES models
- GPT-4 with standard prompting
- GPT-4 with Chain-of-Thought prompting
- QwenScore+ (rubric-aligned CoT with RLHF)

**Evaluation Metrics**:

*Scoring Accuracy*:
- Quadratic Weighted Kappa (QWK): $\kappa_w = 1 - \frac{\sum_{i,j} w_{ij} O_{ij}}{\sum_{i,j} w_{ij} E_{ij}}$
- Exact Agreement Rate
- Adjacent Agreement Rate

*Explanation Quality*:
- **Groundedness Score**: Percentage of explanation claims traceable to knowledge graph elements
$$\text{Groundedness} = \frac{|\text{claims} \cap \mathcal{G}|}{|\text{claims}|}$$
- **Faithfulness**: Percentage of cited evidence accurately extracted from essays
- **Completeness**: Coverage of relevant rubric criteria in explanations

*Human Evaluation*:
- Educator ratings of explanation usefulness (5-point Likert scale)
- Student comprehension and actionability ratings
- Expert assessment of validity for audit purposes

**Ablation Studies**: We conduct ablations to assess contributions of:
- Knowledge graph augmentation vs. plain retrieval
- Constrained vs. unconstrained CoT prompting
- Different knowledge graph completeness levels

**Fairness Analysis**: We examine score and explanation consistency across demographic subgroups to identify potential biases amplified or mitigated by knowledge graph augmentation.

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **KAES Framework and Implementation**: A fully functional knowledge-augmented essay scoring system with open-source code and documentation enabling replication and extension.

2. **Educational Knowledge Graph Resources**: Domain-specific knowledge graphs for multiple assessment contexts, providing reusable infrastructure for future research.

3. **Empirical Findings**: Comprehensive evaluation demonstrating:
   - Maintained or improved scoring accuracy (target: QWK ≥ 0.80)
   - Significantly enhanced explanation groundedness (target: ≥ 90% traceable claims)
   - Improved stakeholder trust ratings compared to baseline LLM systems

4. **Guidelines for Deployment**: Practical recommendations for integrating explainable AES in operational assessment programs.

### Research Impact

**Scientific Contributions**: This work advances the intersection of knowledge graphs and large language models for educational applications, establishing methodological foundations for grounded, explainable AI in assessment contexts. The constrained Chain-of-Thought approach offers a novel paradigm for reducing hallucination in high-stakes applications.

**Practical Impact**: By addressing the explainability barrier, this research enables broader adoption of AI-assisted scoring in large-scale assessments, potentially reducing costs while maintaining quality and accountability. The framework's audit capabilities support regulatory compliance and continuous validity monitoring.

**Educational Impact**: Concept-level feedback transforms automated scoring from a gatekeeping mechanism into a formative learning tool, providing students with actionable insights for improvement rather than opaque numerical judgments.

**Policy Implications**: Transparent, auditable AI scoring systems enable evidence-based policy discussions about AI in education, moving beyond abstract concerns to concrete evaluation of specific systems against established standards.

### Limitations and Future Directions

We acknowledge that knowledge graph construction requires initial expert effort, and the framework's effectiveness depends on graph quality. Future work will explore automated knowledge graph refinement through feedback loops and extension to multimodal assessments incorporating diagrams, multimedia responses, and collaborative artifacts.

This research represents a critical step toward trustworthy AI in educational assessment, demonstrating that powerful foundation models can be augmented with structured knowledge to meet the transparency and accountability requirements essential for responsible deployment in high-stakes educational contexts.