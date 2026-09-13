# Research Proposal: PETAL - Participatory Evaluation Toolkit for Assessing Local-to-Global Impacts of Generative AI

## 1. Title

**PETAL: A Participatory Evaluation Toolkit for Assessing Local-to-Global Impacts of Generative AI Systems Through Structured Multi-Stakeholder Engagement**

## 2. Introduction

### Background

Generative AI systems have rapidly permeated diverse sectors of society, from creative industries and journalism to education and healthcare. These systems produce text, images, audio, and video content that profoundly affects individuals, communities, and institutions. However, the current paradigm for evaluating these systems remains predominantly technical, relying on metrics such as perplexity, BLEU scores, or FID scores that measure model performance but fail to capture the multifaceted societal impacts experienced by affected communities (Bender et al., 2023).

The NeurIPS Broader Impact statement represents a significant step toward acknowledging the societal implications of AI research. Nevertheless, as highlighted in recent literature, there exists no standardized framework for conducting comprehensive impact assessments that incorporate perspectives beyond machine learning experts (Bordes et al., 2025; Weidinger et al., 2023). This gap is particularly problematic given that different stakeholder groups—artists whose livelihoods are threatened by generative image models, journalists grappling with AI-generated misinformation, educators adapting to AI-assisted writing, and content moderators exposed to harmful outputs—experience distinct and often profound impacts that technical evaluations systematically overlook.

Recent work has begun addressing this limitation. The PARTICIP-AI framework (Mun et al., 2024) demonstrates the value of involving laypeople in anticipating AI use cases and impacts, while Bergman et al. (2023) emphasize the critical importance of representation in AI evaluations. However, these efforts remain scattered, lacking standardized methodologies, reproducible protocols, and systematic integration mechanisms that would enable widespread adoption. Furthermore, critical examinations by Dalal et al. (2024) reveal that participatory structures can inadvertently harm marginalized communities if not carefully designed, highlighting the need for ethically grounded approaches.

### Research Objectives

This research proposes to develop PETAL (Participatory Evaluation Toolkit for Assessing Local-to-Global Impacts), a comprehensive, modular, open-source toolkit that enables structured participatory evaluation of generative AI systems. The specific objectives are:

1. **Develop a systematic Stakeholder Mapping Protocol** that identifies affected communities and their evaluation priorities across different generative AI applications
2. **Design and validate Multi-Modal Feedback Mechanisms** that enable non-technical participants to contribute meaningful qualitative and quantitative assessments
3. **Create an Impact Translation Layer** that synthesizes diverse stakeholder inputs into actionable technical improvements and policy recommendations
4. **Establish a Standardized Documentation Schema** that ensures transparency, reproducibility, and accountability in participatory evaluations
5. **Validate the toolkit through 3-5 case studies** across diverse generative AI applications, demonstrating its effectiveness in revealing evaluation blind spots
6. **Produce evidence-based policy recommendations** for investment in inclusive evaluation infrastructure

### Significance

This research addresses critical gaps at the intersection of AI evaluation science and participatory design. By providing structured, reproducible methods for inclusive evaluation, PETAL will:

- **Enhance evaluation comprehensiveness**: Capture impacts that purely technical metrics miss, leading to more robust AI systems
- **Democratize AI governance**: Empower affected communities to meaningfully shape AI development trajectories
- **Establish evaluation standards**: Provide the field with replicable protocols that can become community norms
- **Inform policy**: Generate empirical evidence for policymakers regarding the value and implementation of participatory evaluation
- **Bridge research communities**: Foster collaboration between ML researchers, HCI practitioners, social scientists, and affected communities

The toolkit aligns with emerging calls for sociotechnical safety evaluation (Weidinger et al., 2023) and responds to the NeurIPS workshop's emphasis on broadening participation in evaluation practices.

## 3. Methodology

### 3.1 Research Design Overview

PETAL will be developed through an iterative, community-engaged research approach combining design science methodology with participatory action research. The development will proceed through four integrated phases: (1) Framework Development, (2) Toolkit Implementation, (3) Case Study Validation, and (4) Standardization and Dissemination.

### 3.2 Phase 1: Stakeholder Mapping Protocol Development

**Objective**: Create a systematic methodology for identifying affected stakeholder groups and their evaluation priorities.

**Methodology**:

The Stakeholder Mapping Protocol will consist of three components:

**Component 1: Stakeholder Identification Framework**

We will develop a structured taxonomy of stakeholder categories based on their relationship to generative AI systems:

$$S = \{S_p, S_i, S_d, S_c, S_r\}$$

where:
- $S_p$ = Primary users (direct system users)
- $S_i$ = Indirect affected parties (those impacted by system outputs)
- $S_d$ = Developers and deployers
- $S_c$ = Civil society organizations and advocates
- $S_r$ = Regulators and policymakers

For each generative AI application domain $D$ (e.g., text generation, image synthesis), we will conduct:

1. **Literature analysis**: Systematic review of documented impacts in domain $D$
2. **Expert consultation**: Semi-structured interviews with $n \geq 15$ domain experts per application
3. **Snowball sampling**: Identification of additional stakeholder groups through referral networks

**Component 2: Impact Priority Elicitation**

For each identified stakeholder group $s \in S$, we will elicit evaluation priorities through:

1. **Participatory workshops** (2-3 hours, 8-12 participants per group)
2. **Structured priority ranking** using Analytic Hierarchy Process (AHP)
3. **Qualitative interviews** to understand context and nuance

Participants will rank impact dimensions on a pairwise comparison matrix $M$, where element $m_{ij}$ represents the relative importance of dimension $i$ versus dimension $j$. Priority weights $w$ are derived from the principal eigenvector:

$$Mw = \lambda_{max}w$$

**Component 3: Power and Positionality Analysis**

Following Dalal et al. (2024), we will conduct systematic power analysis to identify:

- Historical marginalization and systemic barriers
- Capacity for meaningful participation
- Potential risks of participation
- Appropriate compensation and support structures

This will be documented using a Positionality Matrix $P_{s}$ for each stakeholder group:

$$P_s = \{power\_level, resources, risks, benefits, historical\_context\}$$

### 3.3 Phase 2: Multi-Modal Feedback Mechanism Design

**Objective**: Create accessible interfaces for diverse participants to contribute evaluation insights.

**Design Approach**:

We will develop three integrated feedback mechanisms:

**Mechanism 1: Structured Survey Instrument**

Design domain-specific evaluation surveys incorporating:

- Validated scales for impact dimensions (5-point Likert scales)
- Open-ended qualitative response sections
- Scenario-based evaluation prompts
- Accessibility features (multilingual support, screen reader compatibility)

Each survey will measure impact across dimensions $D = \{d_1, d_2, ..., d_k\}$ with reliability assessed through Cronbach's alpha:

$$\alpha = \frac{k}{k-1}\left(1 - \frac{\sum_{i=1}^k \sigma_{d_i}^2}{\sigma_D^2}\right)$$

Target $\alpha \geq 0.7$ for internal consistency.

**Mechanism 2: Deliberative Focus Groups**

Conduct structured focus group sessions using:

- **Modified Delphi technique** for consensus-building on key impacts
- **Critical incident technique** for collecting concrete harm/benefit examples
- **Participatory scenario planning** for anticipating future impacts

Sessions will be recorded (with consent), transcribed, and analyzed using thematic analysis with inter-rater reliability $\kappa \geq 0.6$ (Cohen's kappa).

**Mechanism 3: Experience Sampling Method (ESM)**

Implement mobile-based ESM protocol where participants log real-time encounters with generative AI:

- Prompt frequency: 2-3 times daily for 2-4 weeks
- Capture: context, emotional response, perceived impact, system characteristics
- Analysis: Mixed-effects models accounting for within-person and between-person variation

The model specification:

$$Y_{ij} = \beta_0 + \beta_1X_{ij} + u_{0j} + u_{1j}X_{ij} + \epsilon_{ij}$$

where $Y_{ij}$ is the impact measure for person $j$ at time $i$, $X_{ij}$ represents contextual factors, $u_{0j}$ and $u_{1j}$ are random effects, and $\epsilon_{ij}$ is residual error.

### 3.4 Phase 3: Impact Translation Layer

**Objective**: Synthesize diverse stakeholder inputs into actionable recommendations.

**Translation Framework**:

The Impact Translation Layer consists of four sub-components:

**Component 1: Qualitative-Quantitative Integration**

Apply convergent mixed-methods design:

1. **Qualitative coding**: Thematic analysis of open-ended responses and focus group data using both deductive (theory-driven) and inductive (data-driven) approaches
2. **Quantification**: Convert qualitative themes to structured impact categories
3. **Statistical analysis**: Quantitative analysis of survey and ESM data
4. **Integration**: Compare, contrast, and synthesize findings using joint display tables

**Component 2: Stakeholder Weight Calibration**

Address the challenge of aggregating preferences across stakeholder groups with potentially conflicting priorities. We propose a weighted aggregation framework:

$$I_{total} = \sum_{s \in S} w_s \cdot I_s$$

where $I_s$ represents the impact assessment from stakeholder group $s$, and weights $w_s$ are determined through:

- Ethical weighting principles (prioritizing marginalized voices)
- Severity of impact experienced
- Representation in evaluation process
- Transparent documentation of weighting rationale

**Component 3: Technical Recommendation Generation**

Map identified impacts to technical interventions using structured template:

```
Impact: [Specific harm/concern identified]
Affected Stakeholders: [Groups experiencing impact]
Technical Root Cause: [Model/system characteristics]
Proposed Interventions: [Specific technical changes]
Validation Metrics: [How to measure improvement]
Trade-offs: [Potential costs or competing concerns]
```

**Component 4: Policy Recommendation Synthesis**

Generate structured policy briefs incorporating:

- Evidence summary of stakeholder-identified impacts
- Gaps between current technical evaluations and real-world experiences
- Specific policy interventions (regulatory, industry standards, investment priorities)
- Implementation roadmap with milestones

### 3.5 Phase 4: Standardized Documentation Schema

**Objective**: Ensure transparency and reproducibility through comprehensive documentation standards.

**Documentation Framework**:

Building on Eval Factsheets (Bordes et al., 2025), we will develop the PETAL Documentation Schema with six core components:

1. **Stakeholder Participation Record**
   - Who was included/excluded and why
   - Recruitment methods and response rates
   - Demographic characteristics of participants
   - Compensation and support provided

2. **Evaluation Process Documentation**
   - Timeline and phases
   - Methods used for each stakeholder group
   - Participation rates and engagement levels
   - Challenges encountered and adaptations made

3. **Impact Findings Summary**
   - Quantitative results with effect sizes and confidence intervals
   - Qualitative themes with representative quotes
   - Convergent and divergent findings across stakeholder groups
   - Severity and prevalence of identified impacts

4. **Weighting and Trade-off Decisions**
   - How stakeholder inputs were weighted
   - Rationale for prioritization decisions
   - Documented disagreements or conflicts
   - Ethical considerations in decision-making

5. **Recommendations and Actionability**
   - Technical recommendations with implementation guidance
   - Policy recommendations with supporting evidence
   - Limitations and uncertainties
   - Follow-up evaluation plans

6. **Reflexivity Statement**
   - Researcher positionality
   - Potential biases and mitigation strategies
   - Power dynamics in evaluation process
   - Ethical concerns and how they were addressed

### 3.6 Case Study Validation

**Objective**: Validate PETAL through diverse real-world applications.

**Case Study Selection**:

We will conduct 3-5 case studies across different generative AI applications, selected to maximize variation in:

- **Application domain**: text generation, image synthesis, voice cloning, video generation
- **Deployment context**: consumer products, professional tools, public sector applications
- **Stakeholder diversity**: different affected communities and power dynamics
- **Development stage**: deployed systems, systems under development

Proposed case studies:

1. **Text Generation in Education**: Assessing impacts on students, educators, and academic integrity
2. **Image Synthesis in Creative Industries**: Evaluating effects on visual artists, photographers, and designers
3. **Voice Cloning Technology**: Understanding implications for voice actors, public figures, and consent
4. **AI-Generated News Content**: Examining impacts on journalists, news consumers, and information ecosystems
5. **Video Deepfakes**: Analyzing concerns of potential victims, content moderators, and platform governance

**Validation Methodology**:

For each case study, we will:

1. **Apply complete PETAL framework**: Execute all four components (stakeholder mapping, feedback collection, impact translation, documentation)

2. **Conduct comparative evaluation**: Compare findings from participatory evaluation against:
   - Standard technical benchmarks
   - Expert-only assessments
   - Documented real-world incidents

3. **Assess added value**: Measure:
   - Novel impacts identified through participatory process
   - Differences in priority rankings between stakeholders and technical experts
   - Actionability of generated recommendations
   - Stakeholder satisfaction with process (validated scales)

4. **Evaluate feasibility**: Document:
   - Resource requirements (time, cost, personnel)
   - Scalability considerations
   - Barriers to implementation
   - Participant burden and retention rates

**Evaluation Metrics**:

- **Coverage**: Proportion of documented real-world impacts identified through PETAL vs. technical-only evaluation
- **Novelty**: Number of previously unrecognized impacts surfaced
- **Diversity**: Representation metrics across stakeholder groups
- **Actionability**: Expert ratings (1-5 scale) of recommendation specificity and implementability
- **Stakeholder satisfaction**: Validated scales measuring perceived influence, fairness, and value
- **Convergent validity**: Correlation between PETAL findings and independent impact assessments
- **Implementation success**: Adoption rate of recommendations by development teams (6-month follow-up)

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Deliverable 1: PETAL Toolkit (Open-Source)**

A comprehensive, modular toolkit comprising:
- Detailed methodological protocols and templates
- Digital tools for survey deployment, data collection, and analysis
- Training materials and implementation guides
- Sample documentation using standardized schema
- Code repository with analysis pipelines

Expected release: 18 months after project initiation

**Deliverable 2: Validated Case Studies**

3-5 comprehensive case study reports demonstrating:
- Application of PETAL across diverse contexts
- Comparative analysis showing participatory evaluation benefits
- Identified blind spots in technical-only assessments
- Documented novel impacts and stakeholder perspectives
- Implementation stories and lessons learned

Expected completion: 24 months after project initiation

**Deliverable 3: Standardized Evaluation Framework**

A peer-reviewed framework document including:
- PETAL Documentation Schema ready for community adoption
- Best practice guidelines for participatory AI evaluation
- Ethical guidelines for stakeholder engagement
- Quality standards and validation criteria

Expected publication: 20 months after project initiation

**Deliverable 4: Policy Recommendations**

Evidence-based policy brief addressing:
- Investment priorities for participatory evaluation infrastructure
- Regulatory standards for AI impact assessment
- Industry best practices and voluntary commitments
- Research funding priorities

Expected release: 24 months after project initiation

**Deliverable 5: Community Resources**

- Workshop curriculum for training evaluators
- Stakeholder engagement playbook
- Repository of validated survey instruments
- Video tutorials and documentation

Expected release: Ongoing throughout project

### 4.2 Academic Impact

**Advancing Evaluation Science**: PETAL will contribute novel methodologies at the intersection of participatory design, AI evaluation, and impact assessment, providing empirically validated approaches that bridge technical and social considerations.

**Establishing Standards**: By providing comprehensive documentation schemas and reproducible protocols, this work can catalyze standardization in AI evaluation practices, similar to how reporting guidelines (CONSORT, PRISMA) transformed their respective fields.

**Theoretical Contributions**: The research will yield insights into:
- How different stakeholder perspectives reveal distinct impact dimensions
- The relationship between technical metrics and real-world impacts
- Effective methods for synthesizing diverse evaluation inputs
- Power dynamics in participatory AI evaluation

**Empirical Evidence**: The case studies will generate novel empirical data demonstrating the added value of participatory evaluation, quantifying coverage gaps in technical-only approaches, and documenting implementation feasibility.

### 4.3 Practical Impact

**For AI Developers**: PETAL provides actionable methodologies for comprehensive impact assessment, enabling development of more robust, aligned AI systems. The toolkit reduces barriers to inclusive evaluation by providing ready-to-use protocols and tools.

**For Affected Communities**: By creating structured mechanisms for meaningful participation, PETAL empowers stakeholders to influence AI systems that affect them, shifting power dynamics in AI development and governance.

**For Policymakers**: Evidence-based recommendations and case study data will inform:
- AI evaluation requirements in regulatory frameworks
- Investment priorities for evaluation infrastructure
- Standards for public sector AI deployment
- International AI governance discussions

**For Evaluation Practitioners**: The toolkit provides validated instruments, protocols, and best practices that evaluation professionals can adopt and adapt, improving evaluation quality and consistency.

### 4.4 Broader Societal Impact

**Democratizing AI Governance**: PETAL contributes to shifting AI development from purely technical optimization toward more democratic, stakeholder-responsive processes, aligning with broader movements for participatory technology design.

**Reducing AI Harms**: By systematically identifying impacts that technical evaluations miss, PETAL-informed development can prevent or mitigate real-world harms before deployment, particularly for marginalized communities disproportionately affected by AI systems.

**Building Trust**: Transparent, inclusive evaluation processes can enhance public trust in AI systems and institutions developing them, addressing growing skepticism about AI deployment.

**Influencing Norms**: Successful demonstration of participatory evaluation's value can shift community norms, making inclusive impact assessment standard practice rather than exception, similar to the cultural shift initiated by Broader Impact statements.

### 4.5 Long-term Vision

This research represents an initial step toward a future where:
- Participatory evaluation is standard practice for AI systems with societal impact
- Diverse stakeholder perspectives systematically inform AI development
- Evaluation science integrates technical and social considerations seamlessly
- Clear standards ensure transparency and accountability in AI impact assessment
- Investment in evaluation infrastructure matches the scale of AI deployment

By providing rigorous, validated methodologies and demonstrating their value through concrete case studies, PETAL aims to catalyze this transformation, ensuring that the voices of those affected by generative AI systems meaningfully shape their development and governance.

**Timeline**: 24-month project with ongoing community engagement and toolkit evolution based on adoption feedback and emerging needs.

**Estimated Budget**: $750,000-900,000 covering personnel (research team, community coordinators), participant compensation, technology development, case study implementation, and dissemination activities.