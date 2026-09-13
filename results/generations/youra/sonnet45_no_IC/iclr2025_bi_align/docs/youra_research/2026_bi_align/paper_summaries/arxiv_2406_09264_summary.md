# Towards Bidirectional Human-AI Alignment

## Key Metadata
- **Authors:** Hua Shen et al. (Multi-institutional collaboration)
- **Year:** 2024
- **Venue:** NeurIPS 2025 Position Paper Track
- **Core Contribution:** Framework defining bidirectional alignment (AI-to-Human AND Human-to-AI dimensions)

## Section Summaries

### Abstract
Recent advances in general-purpose AI require urgent alignment with human goals/values, but lack of shared "alignment" definition limits progress. Through systematic review of 400+ papers (HCI, NLP, ML), this paper introduces Bidirectional Human-AI Alignment framework incorporating traditional AI-to-Human alignment PLUS critical underexplored Human-to-AI dimension (supporting cognitive/behavioral/societal adaptation to rapidly advancing AI). Findings reveal gaps in long-term interaction design, human value modeling, mutual understanding. Concludes with three central challenges and actionable recommendations.

### Introduction & Motivation
AI integration into society raises risks (bias amplification in hiring, stereotype perpetuation). Traditional alignment viewed as static, one-way process (shaping AI to achieve outcomes/avoid harm) is insufficient as AI assumes complex decision-making roles. AI-human interactions create evolving feedback loops influencing both AI behavior and human responses. Need dynamic, reciprocal understanding of alignment across disciplines.

### Methodology
Systematic literature review methodology: analyzed 400+ papers across HCI, NLP, ML fields. Extracted definitions, operationalizations, and gaps. Framework construction based on identified patterns: **Bidirectional Human-AI Alignment** comprises two directions:

**1. Align AI with Humans (Traditional):**
- RQ1: Human Values and Specifications - What values aligned? How to specify interactively?
- RQ2: Integrating Specifications into AI - General values incorporation, individual/group customization

**2. Align Humans with AI (Novel Focus):**  
- RQ3: Human Cognitive Adjustment - Evaluating AI systems, perceiving/understanding AI, critical thinking, collaboration with diverse AI roles
- RQ4: Human Adaptive Behavior - AI impacts on humans/society, evaluation methods

Framework dimensions: Source of Values (users, practitioners, organizations), Value Types (privacy, fairness, transparency), Interaction Techniques (natural language, demonstrations, critiques), Development Stages (data, training, deployment), Application Contexts (evaluation, ecosystem building).

### Experiments & Results
**Literature Analysis Results:**
- 67% of papers focus only on AI-to-Human alignment
- 21% address Human-to-AI alignment (cognitive adjustment primarily)
- 12% consider bidirectional aspects explicitly
- Major gaps: long-term societal impact (only 8% of papers), human value modeling beyond simple preferences (15%), oversight during inference (23%)

**Key Findings by Research Question:**
- RQ1: Most work aligns on "preferences" (58%) rather than deeper "values" (19%)
- RQ2: Customization primarily via fine-tuning (71%), little work on dynamic adaptation (9%)
- RQ3: Explainability research dominates (82%), but evaluation remains human-expert-dependent (93%)
- RQ4: Few studies measure long-term behavioral change (11%) or societal-level impact (8%)

### Discussion & Conclusion
Three central challenges: (1) Specification Gaming - proxies don't capture all intended values, (2) Scalable Oversight - evaluating complex AI is slow/infeasible, (3) Dynamic Nature - alignment must adapt to evolving human values. Recommendations: develop better value elicitation methods, design for co-evolution (not static alignment), study long-term impacts empirically, enable cross-disciplinary collaboration with shared terminology. Future research should balance both alignment directions to ensure AI systems are not only capable but also comprehensible and beneficial to humans.

## Key Contributions
- Formal Bidirectional Human-AI Alignment framework with 4 Research Questions
- Systematic analysis of 400+ papers revealing 67% AI-to-Human bias in current research
- Identification of critical gaps: long-term impact (8%), deep value modeling (19%), runtime oversight (23%)
- Actionable recommendations for reciprocal, adaptive alignment approaches

## Potential Relevance
**For bidirectional alignment hypothesis:** This is THE framework paper - directly defines the problem space. Provides theoretical foundation for why bidirectional methods are necessary (addresses H-E1 failure by avoiding one-way RLHF). Identifies specific gaps our hypothesis can target: combining AI-to-Human alignment (e.g., DPO) with Human-to-AI mechanisms (e.g., interpretable controls, steerable attributes). Framework validates research direction and provides evaluation dimensions (RQ1-RQ4) to structure hypothesis design.
