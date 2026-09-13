# Introduction

Large language models can now generate code that passes 99% of benchmark tests, yet they still fail to fix 60% of their own compiler errors when given raw error messages. This striking gap between code generation capability and self-repair capability suggests that *how* we present errors to models matters as much as *whether* we present them at all.

Consider a model achieving 95% accuracy on HumanEval. When this model encounters a type error in its own output, the standard practice is to feed back the raw compiler traceback—terse, technical syntax designed for human developers who understand stack traces and exception hierarchies. Yet LLMs are trained on natural language prose, documentation, and code with explanatory comments. The mismatch between compiler output format and model training distribution may explain why iterative self-repair often yields diminishing returns after the first repair attempt.

Prior work has extensively studied *whether* to include compiler feedback in self-repair loops, demonstrating consistent improvements of +4.9% or more across model scales [Chen et al., 2024]. However, the question of *how* to format this feedback remains largely unexplored. Existing approaches treat error messages as fixed inputs, varying only the iteration count or combining static and dynamic analysis. The implicit assumption is that any error message format is equally useful to the model—an assumption our work challenges.

We observe that compiler errors exhibit structural properties fundamentally different from LLM training distributions: they are terse where natural language is elaborate, technical where training data is explanatory, and formatted for terminal display rather than comprehension. This observation leads to our key insight: **representational alignment**—transforming compiler output toward natural language structure—should be the causal mechanism driving self-repair improvement. By reformatting errors with explicit section labels (PROBLEM/LOCATION/CONTEXT/ROOT_CAUSE), we transform them toward patterns the model understands. This is not about adding information—it is about organizing existing information in a form the model can process.

To test this hypothesis, we design controlled experiments that isolate the effect of error format structure from information content. Our scrambled condition contains identical diagnostic information as the structured format but with randomly ordered sections, enabling causal inference about whether structure itself matters. Additionally, we investigate fix specificity—whether intermediate-level hints (general strategies) outperform both no hints and exact fixes, following scaffolding theory from human-computer interaction research.

Our contributions are:

1. **First causal evidence for representational alignment**: We demonstrate that structured error formatting significantly outperforms scrambled formatting with identical content (+14.4%, p < 0.001), proving that *how* information is organized matters independently of *what* information is present.

2. **Fix specificity framework**: We show that intermediate-specificity hints (Level 2: specific patterns) achieve optimal repair success (60.2%), outperforming both no hints (34.7%) and exact fixes (39.6%), consistent with scaffolding theory predictions.

3. **Practical guidelines**: We provide a simple preprocessing step—format transformation—that improves self-repair without model changes, applicable to any LLM-based code repair system.

The remainder of this paper is organized as follows: Section 2 discusses related work on self-repair and compiler feedback. Section 3 presents our methodology, including the structured error format and experimental design. Section 4 describes our experimental setup, and Section 5 presents results. Section 6 discusses implications and limitations. Section 7 concludes.
