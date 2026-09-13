# Participatory Red-Teaming: Engaging Affected Communities in LM Safety Evaluation through Culturally-Informed Harm Detection

## 1. Introduction

### Background

Large Language Models (LLMs) have become increasingly prevalent across diverse global contexts, yet their safety evaluation mechanisms remain largely centralized within expert-driven frameworks that may overlook culturally-specific harms and context-dependent risks. Traditional red-teaming approaches, while effective at identifying broad categories of unsafe behaviors, systematically underrepresent the nuanced concerns of marginalized and underrepresented communities. This gap manifests in models that pass standard safety benchmarks yet perpetuate harm through subtle microaggressions, dialectal biases, and culturally insensitive outputs that technical experts may not recognize without lived experience.

Recent work has begun addressing this limitation through sociotechnical frameworks like STAR and culturally-focused approaches like CulturalTeaming. However, these methods still rely primarily on researcher-mediated processes rather than genuine participatory design that centers affected communities as co-creators of safety infrastructure. The consequences of this gap are significant: LLMs deployed globally may systematically fail to serve—or actively harm—populations whose safety concerns were not represented during evaluation.

The fundamental challenge lies in the epistemological distance between those who design safety evaluations and those who experience the harms. Expert-driven red-teaming excels at identifying technical vulnerabilities and well-documented harm categories, but struggles with emergent, context-dependent risks that require cultural competency and lived experience to recognize. For instance, a prompt that appears benign in one cultural context may carry harmful connotations in another, or certain response patterns may constitute microaggressions invisible to evaluators outside the affected community.

### Research Objectives

This research proposes to develop and validate a **Participatory Red-Teaming Framework** that systematically engages affected communities in LM safety evaluation through three interconnected objectives:

1. **Design and deploy accessible interfaces** that enable non-expert community members to contribute culturally-informed adversarial test cases and harm taxonomies based on lived experiences, without requiring technical expertise in machine learning or prompt engineering.

2. **Establish collaborative validation mechanisms** where communities can collectively annotate, prioritize, and contextualize harm categories, creating rich datasets that capture the nuanced, intersectional nature of AI-mediated harms.

3. **Develop specialized detection models** trained on community-generated examples to automate identification of context-dependent harms, creating scalable safety infrastructure informed by participatory knowledge.

4. **Create sustainable feedback loops** that connect deployment insights back to community red-teamers, enabling iterative refinement of safety evaluations as new harm patterns emerge.

### Significance

This research addresses critical gaps at the intersection of AI safety, participatory design, and social justice. First, it operationalizes the principle that those most affected by AI systems should have agency in shaping safety standards—moving beyond consultation to genuine co-creation. Second, it generates novel datasets capturing culturally-specific harms that current benchmarks systematically miss, improving the robustness and fairness of LM evaluations. Third, it establishes replicable methodologies for ongoing community engagement, creating sustainable infrastructure for equitable AI development.

The broader impacts extend beyond immediate safety improvements. By demonstrating that participatory approaches can enhance technical rigor while advancing social accountability, this work challenges the false dichotomy between inclusive processes and high-quality evaluation. Furthermore, the framework provides a template for responsible AI development that acknowledges the situated, contextual nature of harm and the necessity of incorporating diverse epistemologies into technical practice.

## 2. Methodology

### 2.1 Research Design Overview

The methodology follows a mixed-methods, iterative design comprising four interconnected phases: (1) Community Partnership and Co-Design, (2) Participatory Data Generation, (3) Model Development and Validation, and (4) Deployment and Feedback Integration. Each phase incorporates both quantitative and qualitative components to ensure methodological rigor while centering community knowledge.

### 2.2 Phase 1: Community Partnership and Co-Design

**Partner Selection and Engagement**: We will establish partnerships with 6-8 community organizations representing diverse marginalized groups, including linguistic minorities, religious communities, LGBTQ+ groups, disability advocacy organizations, and racial/ethnic communities. Partner organizations will be selected based on: (a) established trust within their communities, (b) interest in AI accountability, and (c) capacity to facilitate participant recruitment.

**Co-Design Workshops**: Conduct 3-4 iterative co-design sessions with 8-12 representatives from each partner organization ($N \approx 60$ total participants) to:
- Identify priority harm categories relevant to each community
- Design culturally-appropriate elicitation protocols
- Develop accessible interface prototypes
- Establish ethical guidelines for data collection and attribution

**Harm Taxonomy Development**: Working collaboratively, develop a hierarchical harm taxonomy with three levels:
1. **Universal categories** (e.g., explicit hate speech, violence)
2. **Community-specific categories** (e.g., religious microaggressions, dialectal delegitimization)
3. **Context-dependent subcategories** (e.g., appropriation of cultural practices, erasure of historical trauma)

This taxonomy will be operationalized using a flexible schema allowing communities to define and add categories:

$$T = \{(c_i, d_i, e_i, s_i)\}_{i=1}^{N}$$

where $c_i$ is the category name, $d_i$ is the community-provided definition, $e_i$ is a set of example prompts/responses, and $s_i$ is a severity rating on a 5-point scale defined by the community.

### 2.3 Phase 2: Participatory Data Generation

**Interface Development**: Create a web-based platform with three primary modules:

*Module 1: Guided Prompt Creation*
- Scaffolded templates supporting various adversarial strategies (direct, indirect, contextual)
- Multi-lingual support for non-English languages
- Cultural context fields allowing annotators to explain why a prompt may elicit harm
- Example prompts demonstrating the concept without biasing creation

*Module 2: Response Evaluation*
- Present LM responses to community-generated prompts
- Multi-dimensional rating interface capturing:
  - Harm severity: $h \in [0, 4]$ (none to extreme)
  - Harm type: $t \in T$ (from community taxonomy)
  - Contextual factors: $F = \{f_1, f_2, ..., f_k\}$ (e.g., identity mentions, stereotypes)
  - Open-ended explanation of harm mechanism

*Module 3: Collaborative Validation*
- Peer review system where community members validate each other's contributions
- Discussion threads for contested cases
- Consensus-building tools for establishing ground truth

**Data Collection Protocol**:
1. Recruit 150-200 participants across partner communities (20-30 per community)
2. Provide 2-hour training covering: platform use, prompt engineering basics, safety considerations
3. Compensate participants at $25/hour for all activities (training, generation, validation)
4. Each participant generates 30-50 adversarial prompts over 4 weeks
5. Each prompt evaluated by 5 community members from the same cultural context
6. Target dataset: 5,000-10,000 culturally-informed test cases

**Quality Assurance**: Implement multi-level quality controls:
- Automated filtering for spam, duplicates, and off-task responses
- Expert review of 10% sample to assess alignment with safety objectives
- Inter-rater reliability analysis using Krippendorff's alpha:

$$\alpha = 1 - \frac{D_o}{D_e}$$

where $D_o$ is observed disagreement and $D_e$ is expected disagreement by chance. Target $\alpha > 0.67$ for harm severity ratings.

### 2.4 Phase 3: Model Development and Validation

**Specialized Reward Model Training**: Develop context-aware harm detection models fine-tuned on community-generated data.

*Base Architecture*: Fine-tune a DeBERTa-v3-large model on the participatory dataset, with input format:

$$x = [\text{CLS}] \oplus P \oplus [\text{SEP}] \oplus R \oplus [\text{SEP}] \oplus C$$

where $P$ is the prompt, $R$ is the model response, and $C$ is community-provided context (e.g., cultural background, identity markers).

*Training Objective*: Multi-task learning combining harm detection and severity estimation:

$$\mathcal{L} = \mathcal{L}_{\text{clf}} + \lambda_1 \mathcal{L}_{\text{sev}} + \lambda_2 \mathcal{L}_{\text{type}}$$

where:
- $\mathcal{L}_{\text{clf}} = -\sum_{i} y_i \log(\hat{y}_i)$ (binary cross-entropy for harm/no-harm)
- $\mathcal{L}_{\text{sev}} = \text{MSE}(h, \hat{h})$ (severity regression)
- $\mathcal{L}_{\text{type}} = -\sum_{j} t_j \log(\hat{t}_j)$ (multi-label classification for harm types)

*Community-Specific Adaptation*: Train community-specific adapter layers using parameter-efficient fine-tuning (LoRA) to capture group-specific harm patterns while maintaining general capabilities:

$$h_{\text{adapted}} = h + \alpha \cdot \Delta W h$$

where $\Delta W = BA$ are low-rank update matrices, $\alpha$ is a scaling factor, and separate adapters are trained for each partner community.

**Comparative Evaluation Design**:

*Benchmark Datasets*: Evaluate on three categories of test sets:
1. **Community-generated holdout set** (20% of participatory data)
2. **Existing safety benchmarks** (ToxiGen, BBQ, BOLD)
3. **Cross-community generalization set** (prompts from one community evaluated by others)

*Baseline Models*:
- Perspective API (industry standard)
- GPT-4-based safety classifier
- Standard reward models (trained on RLHF data)
- STAR framework implementation

*Evaluation Metrics*:
- **Detection Performance**: Precision, Recall, F1, AUC-ROC
- **Severity Alignment**: Mean Absolute Error between predicted and community-rated severity
- **Coverage**: Percentage of community-identified harms detected
- **Fairness**: Disaggregated performance across communities, measured by equalized odds ratio:

$$\text{EOR} = \frac{\min_g \text{TPR}_g}{\max_g \text{TPR}_g}$$

where $g$ indexes communities and TPR is true positive rate.

### 2.5 Phase 4: Deployment and Feedback Integration

**Pilot Deployment**: Partner with 2-3 organizations deploying LLMs in community-facing applications to integrate the participatory red-teaming framework into their safety pipelines.

**Continuous Monitoring Infrastructure**:
- Automated flagging of user interactions matching community-identified harm patterns
- Monthly aggregation reports shared with partner communities
- Quarterly review sessions where communities assess new harm patterns

**Iterative Refinement Protocol**:
1. Community reviewers assess samples of flagged interactions ($n=200$ per quarter)
2. Identify emergent harm categories not in original taxonomy
3. Generate new adversarial examples targeting gaps
4. Retrain detection models with augmented data
5. Measure improvement in coverage and detection rates

**Feedback Loop Evaluation**: Assess framework sustainability through:
- Participant retention rates across iterations
- Time-to-detection for novel harm patterns
- Community satisfaction surveys (validated scales for trust, agency, impact perception)

### 2.6 Ethical Considerations

- **IRB Approval**: Obtain approval from institutional review board with particular attention to vulnerable populations
- **Informed Consent**: Multilingual consent forms explaining data use, compensation, and opt-out rights
- **Data Protection**: Encrypted storage, limited access, and options for data deletion
- **Psychological Safety**: Content warnings, access to counseling resources, and regular check-ins for participants reviewing harmful content
- **Attribution and Ownership**: Clear agreements on intellectual property, with communities retaining rights to their contributions
- **Equitable Compensation**: Payments exceeding minimum wage standards, with additional compensation for community organizations

## 3. Expected Outcomes & Impact

### 3.1 Primary Deliverables

**1. Culturally-Informed Adversarial Dataset**: A novel, openly-released dataset of 5,000-10,000 test cases capturing context-dependent harms across multiple cultural contexts, with rich annotations including harm explanations, cultural context, and severity ratings. This dataset will fill critical gaps in existing safety benchmarks, which predominantly reflect Western, English-centric perspectives.

**2. Specialized Harm Detection Models**: Open-source release of fine-tuned models demonstrating improved detection of culturally-specific harms, with performance gains of 15-25% in recall for community-identified harm categories compared to general-purpose safety classifiers. Community-specific adapters will enable organizations to customize safety infrastructure for their user populations.

**3. Participatory Framework Documentation**: Comprehensive guidelines for implementing participatory red-teaming, including:
- Interface design specifications and open-source code
- Community engagement protocols and recruitment strategies
- Ethical guidelines for working with affected communities
- Cost-benefit analyses demonstrating feasibility
- Templates for partnership agreements and compensation structures

**4. Empirical Insights**: Peer-reviewed publications documenting:
- Comparative analysis of participatory vs. expert-driven red-teaming effectiveness
- Characterization of culturally-specific harm patterns invisible to standard evaluations
- Measurement of community satisfaction and empowerment outcomes
- Best practices for sustainable community engagement in AI safety

### 3.2 Scientific Contributions

**Methodological Advancement**: This research establishes participatory design as a rigorous methodology for AI safety evaluation, demonstrating that inclusive processes enhance rather than compromise technical quality. By operationalizing community expertise through structured elicitation and validation protocols, we bridge human-computer interaction and machine learning safety research.

**Theoretical Contributions**: The work advances understanding of situated harm in AI systems, demonstrating that harm categories are not universal but rather culturally constructed and context-dependent. The hierarchical harm taxonomy provides a framework for conceptualizing harm at multiple levels of abstraction while preserving cultural specificity.

**Empirical Evidence**: Quantitative demonstration that:
- Community-generated test cases expose vulnerabilities missed by expert red-teamers
- Models trained on participatory data achieve better fairness-performance tradeoffs
- Iterative community engagement sustains safety improvements over time

### 3.3 Broader Impacts

**Equity and Inclusion**: By centering marginalized communities in safety infrastructure development, this research redistributes epistemic authority in AI development. Community members gain skills and agency in shaping technologies affecting their lives, while LM developers access knowledge essential for equitable deployment.

**Industry Adoption**: The framework provides practical tools for organizations committed to responsible AI, with clear ROI through improved safety coverage and reduced post-deployment harm incidents. Pilot partnerships will generate case studies demonstrating feasibility at scale.

**Policy Implications**: The research generates evidence supporting regulatory frameworks that mandate inclusive safety evaluation, particularly for high-stakes LM applications. Documentation of participatory processes can inform standards development by organizations like NIST and ISO.

**Community Capacity Building**: Partner organizations develop lasting expertise in AI accountability, creating infrastructure for ongoing engagement as LM capabilities evolve. Trained community members can serve as consultants, advocates, and researchers in their own right.

**Academic Impact**: The methodology is transferable to other AI systems beyond language models, including vision, multimodal, and recommendation systems. The framework establishes a template for participatory AI research more broadly, potentially catalyzing a methodological shift toward community-engaged technical work.

### 3.4 Sustainability and Scalability

The framework is designed for sustainability through:
- **Open-source infrastructure** allowing adoption without proprietary dependencies
- **Modular design** enabling implementation at various resource levels
- **Training materials** supporting independent replication by other research groups
- **Partnership with existing organizations** leveraging established community relationships rather than creating new structures

Scalability is addressed through:
- **Automated components** reducing human labor requirements as datasets grow
- **Transfer learning approaches** allowing knowledge sharing across communities
- **Federated models** where communities can contribute without sharing raw data
- **Tiered implementation** supporting both deep engagement (co-design) and lighter participation (crowdsourced validation)

### 3.5 Success Metrics

The research will be evaluated against:
1. **Technical Performance**: 20% improvement in detection of community-identified harms; fairness metrics (EOR > 0.75) across communities
2. **Data Quality**: Inter-rater reliability (α > 0.67); expert validation of 90%+ of community contributions
3. **Community Impact**: 70%+ participant satisfaction; 80%+ retention across iterations; measurable increase in AI literacy
4. **Adoption**: 5+ organizations implementing framework within 2 years; 500+ citations to released datasets/models
5. **Policy Influence**: Integration into at least 2 AI safety standards or regulatory frameworks

This comprehensive framework represents a paradigm shift from extractive to participatory AI safety research, demonstrating that technical rigor and social responsibility are not competing objectives but rather mutually reinforcing commitments essential for equitable AI development.