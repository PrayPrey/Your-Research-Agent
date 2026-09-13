# Research Idea: Socially-Grounded Red-Teaming through Participatory Harm Elicitation

## Title
Participatory Red-Teaming: Engaging Affected Communities in LM Safety Evaluation through Culturally-Informed Harm Detection

## Motivation
Current red-teaming approaches for LMs predominantly rely on expert-driven adversarial testing, which often overlooks culturally-specific harms and context-dependent risks that affect marginalized communities. This creates a critical gap where models may pass standard safety evaluations yet cause significant harm to underrepresented groups. By involving affected communities directly in the red-teaming process, we can identify blind spots in safety evaluation and ensure more equitable protection across diverse user populations.

## Main Idea
Develop a participatory framework that enables community members to contribute domain-specific adversarial prompts and harm taxonomies based on their lived experiences. The methodology involves: (1) Creating accessible interfaces for non-expert participants to generate test cases reflecting culturally-specific concerns (e.g., microaggressions, dialectal biases, religious sensitivities); (2) Building a collaborative annotation platform where communities validate and prioritize harm categories; (3) Training specialized reward models on community-generated examples to automate detection of context-dependent harms; (4) Establishing feedback loops where deployment insights inform iterative red-teaming.

**Expected outcomes**: A diverse, representative dataset of culturally-informed adversarial examples; improved detection of subtle, context-dependent harms; and a replicable framework for ongoing community engagement in LM safety evaluation. This approach bridges the gap between technical safety work and social accountability, ensuring more inclusive and robust LM deployment.