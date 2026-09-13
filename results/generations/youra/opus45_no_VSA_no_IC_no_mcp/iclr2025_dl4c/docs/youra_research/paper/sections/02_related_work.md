# Related Work

We survey three research streams that inform our investigation: execution-based code refinement, AI-based feedback methods, and hybrid approaches. Our work differs from all prior efforts in isolating the feedback signal itself rather than comparing complete method architectures.

## Execution-Based Code Refinement

Execution feedback has emerged as a powerful signal for code generation and repair. CodeRL [Le et al., 2022] pioneered using unit test execution as a reward signal for reinforcement learning, demonstrating that pass rates provide a strong training signal. Self-Debug [Chen et al., 2023] extended this paradigm to inference-time refinement, showing that LLMs can effectively use execution error traces to iteratively fix their own code, achieving approximately 10% improvement on HumanEval. LDB [Li et al., 2024] further demonstrated that runtime debugging traces enable localized bug identification.

However, these methods evaluate execution feedback in isolation. Self-Debug does not compare against AI-based feedback under matched conditions; CodeRL's RL framework differs fundamentally from prompt-based refinement used in AI feedback methods. This architectural confounding prevents attributing improvements to the feedback signal itself.

## AI-Based Feedback Methods

Parallel work has explored using LLM-generated critique as feedback. Self-Refine [Madaan et al., 2023] demonstrated that models can iteratively improve their outputs through self-generated critique, achieving 5-8% improvement across various tasks. Constitutional AI [Bai et al., 2022] established that AI feedback can guide behavior without human labels. Reflexion [Shinn et al., 2023] combined verbal self-reflection with task outcomes.

These approaches reduce infrastructure requirements—no execution sandbox needed—but may miss errors that only manifest at runtime. Critically, AI critics approximate error signals rather than providing ground-truth localization. Whether this approximation is "good enough" for code refinement remained untested.

## Hybrid and Comparative Approaches

Some recent work combines execution and AI signals. Reflexion uses execution outcomes as triggers for verbal reflection, but does not ablate the contribution of each signal. The closest to our work is concurrent research on feedback granularity [Self-Edit, 2023], which showed detailed error traces outperform simple pass/fail—but only within the execution feedback family, without AI comparison.

## Our Positioning

Existing work compares methods, not signals. CodeRL versus Self-Refine is not a fair comparison of execution versus AI feedback because the methods differ in architecture, prompting, and training procedure. Our contribution is orthogonal: we fix the method (prompt-based iterative refinement) and vary only the feedback signal. This isolation reveals that execution's advantage stems from counterfactual localization information—a finding obscured in prior method-level comparisons.

Furthermore, we provide the first quantitative measurement of counterfactual information density in execution traces (84.7% ≥ 0.4 CF-score) and establish the complete causal chain from localization to fix success. This mechanistic understanding enables principled feedback pipeline design beyond empirical trial-and-error.
