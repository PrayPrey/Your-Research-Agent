# Research Idea

## Title
Stakeholder-Adaptive Explanation Framework (SAEF): Ontology-Constrained XAI for LLM-Based Educational Assessment

## Motivation
Large language models show promise for automated essay scoring, yet their adoption in high-stakes educational assessment remains limited due to inadequate explainability for diverse stakeholders. Teachers, students, parents, and administrators have fundamentally different mental models of assessment—a teacher needs pedagogical insights, while a parent needs actionable guidance. Current XAI approaches (e.g., SHAP visualizations) provide generic technical outputs that fail to address these distinct needs, creating a critical trust barrier. This research addresses the gap between powerful LLM assessment capabilities and stakeholder-appropriate explanations.

## Main Idea
We propose SAEF, a three-stage pipeline that transforms LLM scoring explanations into role-appropriate formats. First, SHAP feature attributions extract interpretable scoring factors. Second, these features map to established educational ontologies (CEFR, Bloom's Taxonomy, Webb's DOK), translating technical metrics into pedagogically meaningful concepts. Third, role-specific templates generate tailored explanations matching each stakeholder's mental model.

The core hypothesis: ontology-constrained, role-adapted explanations significantly improve comprehension, trust calibration, and perceived actionability compared to generic XAI outputs. We will validate this through a 4×4 mixed-design study (480 participants across four stakeholder types and four explanation formats), measuring comprehension via quiz scores, trust via confidence-accuracy correlation, and actionability via Likert ratings. Expected outcomes include >10% comprehension improvement over baselines, enabling broader LLM adoption in educational assessment.