## Related Work

**Related Papers**

1. **Title**: Systematic Diagnosis of Brittle Reasoning
   - **Authors**: V. S. R. Parupudi
   - **Summary**: Reveals nonhuman-like brittleness in LLMs where models achieve near-perfect procedural accuracy but fail dramatically on combinatorial reasoning tasks.
   - **Year**: 2025

2. **Title**: Reasoning or Memorization? Unreliable RL Results Due to Contamination
   - **Authors**: Mingqi Wu, Zhihao Zhang, et al.
   - **Summary**: Demonstrates that the Qwen2.5 series is particularly susceptible to benchmark contamination and that only accurate rewards yield steady improvements in RL training.
   - **Year**: 2025

3. **Title**: Putnam-AXIOM: Functional and Static Benchmark
   - **Authors**: Aryan Gulati, Brando Miranda, et al.
   - **Summary**: Introduces a contamination-resilient benchmark with 522 university-level problems; OpenAI o1-preview scores 41.9% on original problems but drops to 22.3% on variations (19.6 percentage point drop).
   - **Year**: 2025

4. **Title**: Relational Reasoning and Generalization Using Non-Symbolic Neural Networks
   - **Authors**: Atticus Geiger, Alexandra Carstensen, et al.
   - **Summary**: Establishes that neural networks can learn relational reasoning (equality, sequential patterns, hierarchical relationships) without explicit symbolic representations.
   - **Year**: 2020

5. **Title**: Automatic Generation of Challenging Distractors Using Context-Sensitive Inference Rules
   - **Authors**: Mark J. Gierl, Okan Bulut, Qi Guo, Xinxin Zhang
   - **Summary**: Presents methodological framework for item generation that maintains difficulty through rule-based transformations with expert validation.
   - **Year**: 2017

6. **Title**: The Validity of Automatically Generated Mathematics Test Items
   - **Authors**: M. K. Singley, H. Taft
   - **Summary**: Validates isomorphic item generation with difficulty preservation via Item Response Theory (IRT) analysis, demonstrating that equivalence class difficulty preservation is empirically achievable.
   - **Year**: 1995

7. **Title**: LiveBench - Contamination-Limited Benchmark
   - **Authors**: Colin White, Samuel Dooley, et al.
   - **Summary**: Introduces frequently-updated benchmark with questions from recent sources (monthly refresh) to prevent training data contamination.
   - **Year**: 2024

8. **Title**: VAR-MATH - Symbolic Multi-Instance Benchmark
   - **Authors**: Not specified
   - **Summary**: Demonstrates symbolic variations with algebraic transformations; findings show 47.9%-72.9% performance drops on symbolic variants for large models.
   - **Year**: Not specified

9. **Title**: Compositional Processing Emerges in Neural Networks Solving Math Problems
   - **Authors**: Russin et al.
   - **Summary**: Demonstrates that compositional processing capabilities can emerge in neural networks trained on mathematical problem-solving tasks.
   - **Year**: 2021

10. **Title**: Developing Conceptual and Procedural Knowledge of Mathematics
    - **Authors**: Rittle-Johnson & Schneider
    - **Summary**: Reviews the distinction between procedural fluency and conceptual understanding in mathematics education, establishing foundations for understanding assessment.
    - **Year**: 2015

11. **Title**: Adding It Up: Helping Children Learn Mathematics
    - **Authors**: Kilpatrick et al.
    - **Summary**: Defines mathematical proficiency framework including adaptive reasoning and transfer capability as key components of understanding.
    - **Year**: 2001

12. **Title**: Applications of Item Response Theory
    - **Authors**: Lord
    - **Summary**: Foundational work on Item Response Theory providing methodology for difficulty modeling and measurement in educational assessment.
    - **Year**: 1980

13. **Title**: Item Response Theory for Psychologists
    - **Authors**: Embretson & Reise
    - **Summary**: Comprehensive treatment of IRT methodology including variance decomposition techniques applicable to psychometric measurement.
    - **Year**: 2000

14. **Title**: Standards for Educational and Psychological Testing
    - **Authors**: AERA/APA/NCME
    - **Summary**: Establishes validity framework and inter-rater reliability standards for educational and psychological measurement.
    - **Year**: 2014

**Key Challenges**

1. **Brittle Pattern Matching vs. Understanding**: LLMs demonstrate high accuracy on benchmark problems but exhibit dramatic performance drops on structural variations, revealing surface-feature dependence rather than genuine compositional abstraction.

2. **Benchmark Contamination**: Training data overlap with evaluation benchmarks compromises measurement validity, making it difficult to distinguish true reasoning capability from memorized solutions.

3. **Lack of Diagnostic Metrics**: Current evaluation paradigm relies solely on accuracy metrics, which cannot distinguish between understanding-based and memorization-based performance.

4. **Absence of Structural Invariance Testing**: Existing evaluation approaches lack systematic frameworks for testing performance consistency across structure-preserving transformations.

5. **Confound Control in Variation-Based Evaluation**: Prior variation-based approaches (Putnam-AXIOM, VAR-MATH) demonstrate sensitivity but lack systematic protocols for controlling difficulty drift, contamination, and stochastic variance.

6. **Understanding Operationalization**: The field lacks computational operationalization of "compositional abstraction" and "mathematical understanding" that can be measured quantitatively in neural systems.

7. **Cross-Domain Transfer Assessment**: Limited frameworks exist for assessing whether model performance generalizes across contexts that preserve deep mathematical structure while varying surface features.

8. **Diagnostic Pattern Identification**: Evaluation systems cannot classify models into diagnostic categories (e.g., brittle memorization vs. robust understanding) beyond single-dimensional accuracy metrics.
