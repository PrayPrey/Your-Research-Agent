## Related Work

**Related Papers**
1. **Title**: Evaluating the Robustness of Large Language Model Safety Guardrails Against Adversarial Attacks (arXiv:2511.22047)
   - **Authors**: Richard J. Young
   - **Summary**: Established evaluation methodology with 21 attack categories across 1,445 prompts, revealing a 57.2% gap between benchmark and novel attack performance in LLM safety guardrails.
   - **Year**: 2025

2. **Title**: Jailbroken: How Does LLM Safety Training Fail?
   - **Authors**: Wei, Haghtalab, Steinhardt
   - **Summary**: Introduced the concept of "mismatched generalization," demonstrating that safety training fails when model capabilities exist in domains not covered by training, providing theoretical foundation for why pattern-matching defenses fail.
   - **Year**: 2023

3. **Title**: Why LLM Safety Guardrails Collapse After Fine-tuning
   - **Authors**: Hsiung, Pang, Tang, Song, Ho, Chen, Yang
   - **Summary**: Demonstrated that high similarity between alignment and fine-tuning data weakens guardrails, supporting the need for semantic rather than surface-level defense mechanisms.
   - **Year**: 2025

4. **Title**: Qwen3Guard-8B
   - **Authors**: Alibaba
   - **Summary**: Achieved best overall accuracy (85.3%) among guardrail models but exhibited worst generalization with a 57.2% performance gap on novel attacks.
   - **Year**: 2025

5. **Title**: Granite-Guardian-3.2-5B
   - **Authors**: IBM
   - **Summary**: Demonstrated best generalization among guardrail models with only a 6.5% performance gap, though at the cost of lower overall accuracy.
   - **Year**: 2025

6. **Title**: RAILS: A Robust Adversarial Immune-inspired Learning System (arXiv:2012.10485)
   - **Authors**: Not specified
   - **Summary**: Applied immune-inspired approaches to image classifiers, achieving 5-12% robustness improvement and demonstrating the feasibility of cross-domain transfer of biological defense principles.
   - **Year**: 2021

7. **Title**: On Guardrail Models Robustness to Mutations and Adversarial Attacks (10.18653/v1/2025.findings-emnlp.922)
   - **Authors**: JRC
   - **Summary**: Evaluated 15 guardrail models and found that a single adversarial token deceives 44.5% of models on average, confirming widespread guardrail fragility.
   - **Year**: 2025

**Key Challenges**
1. **Generalization Gap**: Current guardrail models exhibit significant performance degradation (up to 57.2% gap) when facing novel attacks compared to benchmark performance, indicating poor generalization to unseen adversarial patterns.

2. **Mismatched Generalization**: Safety training fails when model capabilities exist in domains not covered by the training data, causing pattern-matching approaches to be fundamentally limited.

3. **Fine-tuning Vulnerability**: High similarity between alignment and fine-tuning data weakens guardrails, suggesting that surface-level defenses are insufficient and semantic-level approaches are needed.

4. **Adversarial Fragility**: Guardrail models are highly susceptible to simple adversarial manipulations, with single adversarial tokens capable of deceiving nearly half of evaluated models.

5. **Accuracy-Generalization Trade-off**: Existing models must choose between high overall accuracy and robust generalization, with no current solution achieving both simultaneously.
