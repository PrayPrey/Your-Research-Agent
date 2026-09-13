## Related Work

**Related Papers**
1. **Title**: DeepSeek-Prover-V2 (2025, 127 citations)
   - **Authors**: DeepSeek Research Team
   - **Summary**: SOTA neural theorem prover achieving 88.9% MiniF2F, 6/15 AIME problems, 10.3% RLMEval using single-phase RL training (GRPO) on mixed-difficulty Lean corpus.
   - **Year**: 2025

2. **Title**: LeanDojo
   - **Authors**: Kaiyu Yang et al.
   - **Summary**: Infrastructure for Lean RL training with retrieval-augmented tactic generation; early models achieved ~30-50% MiniF2F.
   - **Year**: 2023

3. **Title**: ToRA (Tool-Augmented Reasoning)
   - **Authors**: Not specified
   - **Summary**: Code-augmented reasoning with heuristic curriculum (easy-to-hard) achieving 90%+ on GSM8K/MATH via Python tool integration.
   - **Year**: 2024

4. **Title**: AgentMath (Agentic RL)
   - **Authors**: Not specified
   - **Summary**: Agentic RL with mathematical tool use (calculators, symbolic solvers) achieving 90.6% AIME24, focused on competition-level problems.
   - **Year**: 2024

5. **Title**: Gpass (Goal-Adaptive Neural Theorem Prover for Coq)
   - **Authors**: Chen et al.
   - **Summary**: SOTA on Coq (3,774 theorems with CoqHammer) using goal-adaptive feature integration during proof search.
   - **Year**: 2025

6. **Title**: Curriculum Learning (3,500+ citations)
   - **Authors**: Bengio et al.
   - **Summary**: Foundational work establishing that training on progressively difficult examples improves learning efficiency; provides abstract ML concept without domain-specific guidance.
   - **Year**: 2009

7. **Title**: Automated Curriculum Learning
   - **Authors**: Graves et al.
   - **Summary**: Meta-learning approach where learner controls difficulty progression via performance-based sampling, automatically adjusting curriculum.
   - **Year**: 2017

8. **Title**: Pre-trained Encoders for Child Development: Transfer Learning
   - **Authors**: Fahim & Karim
   - **Summary**: Diversity in pre-training (357,709 children, 44 countries) enables few-shot generalization (AUC 0.65 with 50 samples vs 0.61 cold-start), demonstrating transfer learning bounds.
   - **Year**: 2026

9. **Title**: Quality of Teaching Practices: Cognitive Demand (12 citations)
   - **Authors**: Neugebauer & Prediger
   - **Summary**: Three quality dimensions (Mathematical Richness, Cognitive Demand, Connecting Registers) significantly impact student achievement beyond curriculum content.
   - **Year**: 2022

10. **Title**: Developmental BERTology
    - **Authors**: Wang
    - **Summary**: Biological neural development (gradual complexity increase) inspires efficient deep learning optimization, demonstrating bio-inspired curriculum precedent.
    - **Year**: 2020

11. **Title**: RLMEval: Research-Level Neural Theorem Proving
    - **Authors**: Poiroux et al.
    - **Summary**: Benchmark of 613 theorems from 6 real Lean projects exposing generalization gap (SOTA 10.3%), defining "research-level" complexity distinct from competition problems.
    - **Year**: 2025

12. **Title**: EvolMathEval: Evolvable Benchmarks
    - **Authors**: Wang et al.
    - **Summary**: Identifies "Pseudo Aha Moment" accounting for 77-100% of errors when models learn surface patterns and bypass complex reasoning.
    - **Year**: 2025

13. **Title**: VAR-MATH: Probing True Mathematical Reasoning
    - **Authors**: Yao et al.
    - **Summary**: Parameterized templates reveal 47.9-72.9% performance drops, indicating models rely on superficial learning rather than true mathematical reasoning.
    - **Year**: 2025

14. **Title**: Autoformalize Mathematical Statements (238 citations)
    - **Authors**: Wu et al.
    - **Summary**: Achieves 25.3% autoformalization accuracy, improving MiniF2F from 29.6% to 35.2% through natural language to formal translation.
    - **Year**: 2022

15. **Title**: Multi-language Diversity Benefits Autoformalization (8 citations)
    - **Authors**: Jiang et al.
    - **Summary**: Multi-language training across different formal systems achieves 29-31% accuracy improvement, demonstrating diversity benefits for generalization.
    - **Year**: 2024

**Key Challenges**
1. **Research-Level Generalization Gap**: Current SOTA models achieve 88.9% on benchmark problems (MiniF2F) but only 10.3% on research-level theorems (RLMEval), indicating a severe generalization collapse from competition-level to real-world mathematical proof complexity.

2. **Surface Pattern Learning**: Models exhibit 47.9-72.9% performance drops on template variants (VAR-MATH), with "Pseudo Aha Moment" accounting for 77-100% of errors, revealing reliance on superficial pattern matching rather than abstract reasoning.

3. **Lack of Principled Curriculum Design**: Existing approaches use heuristic curricula (easy-to-hard) without learning-theoretic justification from educational science or developmental psychology, limiting systematic optimization.

4. **No Research-Level Focus**: Most work optimizes for competition benchmarks (MiniF2F, AIME) rather than authentic research-level theorem proving from real formalization projects.

5. **Absence of Template Robustness Evaluation**: Current evaluations don't systematically test model robustness to parameterized variations, missing critical assessment of whether models learn abstract reasoning vs memorize surface patterns.

6. **Cross-Domain Transfer Uncertainty**: Limited understanding of whether curriculum principles from human learning (diversity enables generalization, scaffolding builds understanding) transfer faithfully to artificial neural networks with measurable effects.

7. **Mechanistic Understanding Gap**: No clear explanation of how diversity pre-training and difficulty progression change learned representations (attention patterns, embedding geometry) at the neural level.

8. **Compute Budget Constraints**: Multi-phase curriculum training may require 2-5x baseline compute, raising questions about practical feasibility and cost-benefit trade-offs for research settings.
