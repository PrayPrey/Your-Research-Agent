# 2. Related Work

## 2.1 Execution-Based Feedback for Code Generation

Execution-based feedback — using test pass/fail signals to guide model training — has been central to code generation research since HumanEval (Chen et al., 2021) established pass@k as the standard metric. CodeRL (Le et al., 2022) pioneered using execution outcomes as reinforcement learning rewards, achieving ~70-80% pass@1 on HumanEval and APPS benchmarks. The approach assumes that test-based feedback captures code quality uniformly across task types.

However, this assumption remains empirically unvalidated. Liu et al. (2023) observed that HumanEval performance drops 30-40 percentage points when evaluated on HumanEval+ (hidden tests), suggesting that models overfit to visible test coverage. Chen et al. (2023) demonstrated that iterative self-debugging using error traces improves pass rates, but this still relies on execution feedback capturing human-valued properties. No prior work has measured **how well execution feedback proxies human judgment** across task types with varying specification completeness.

Our work differs by directly quantifying execution-human correlation segmented by task type (competitive vs realistic), revealing that execution feedback effectiveness is task-dependent rather than uniform.

## 2.2 AI Feedback vs Human Feedback

The AI alignment community has explored alternatives to human-in-the-loop training. Reinforcement Learning from Human Feedback (RLHF, Ouyang et al., 2022) trains reward models on human preference annotations, then uses these models to guide policy optimization for text generation. Lee et al. (2023) showed that Reinforcement Learning from AI Feedback (RLAIF) — using AI-generated preferences instead of human labels — approximates human feedback quality for text tasks.

However, these methods do not address **code-specific feedback modalities** (execution vs AI vs human) or include execution-based signals. InstructGPT's reward model measures text quality (helpfulness, harmlessness, honesty), not runtime correctness or code efficiency. Li et al. (2022) trained CodeReviewer to predict code quality, but did not compare its correlation with human judgment against execution feedback or segment by task type.

Our work extends RLAIF to code generation by comparing three modalities (execution, AI, human) and demonstrating that supervised AI feedback achieves ρ=0.85 AI-human correlation, validating supervised learning as a code-specific alignment path.

## 2.3 Code Evaluation Benchmarks

Code generation evaluation has evolved from syntax-only metrics (BLEU, CodeBLEU) to execution-based benchmarks:

- **HumanEval** (Chen et al., 2021): 164 function-level programming problems with visible unit tests. Competitive programming tasks with relatively complete specifications.
- **MBPP** (Austin et al., 2021): 974 basic Python problems. Educational tasks with intermediate specification completeness.
- **SWE-bench** (Jimenez et al., 2023): 2294 GitHub issues from real repositories. Realistic software tasks with underspecified requirements.

Each benchmark measures functional correctness via test pass/fail, but none systematically compare execution feedback reliability across these datasets. Jimenez et al. (2023) noted that SWE-bench tasks are underspecified (issue descriptions lack complete requirements), but did not quantify the resulting gap between execution feedback and human evaluation.

Our work bridges this gap by measuring execution-human correlation across all three benchmarks, revealing a 2.29× variance (ANOVA p<0.0001) driven by specification completeness differences.

## 2.4 Feedback Orthogonality in Machine Learning

The concept of feedback orthogonality — measuring correlation structure between different evaluation signals — has been explored in reinforcement learning (reward shaping, Ng et al., 1999) and preference learning (consistency checks, Christiano et al., 2017). However, no prior work has applied this framework to code generation.

Most code generation research treats feedback modalities independently:
- Execution-only methods (CodeRL, AlphaCode) optimize for test pass/fail
- Human evaluation studies (HumanEval, MBPP) collect ratings separately
- AI reward models (CodeT5, CodeBERT fine-tuned) train on code corpora without cross-modal comparison

Our contribution is the first systematic mapping of pairwise correlations (execution-AI, execution-human, AI-human) segmented by task type, revealing when each modality provides unique signal versus redundant information.

## 2.5 Positioning Summary

| Work | Modalities Compared | Task Segmentation | Code-Specific | Key Finding |
|------|---------------------|-------------------|---------------|-------------|
| CodeRL (Le et al., 2022) | Execution only | No | Yes | RL on test feedback achieves ~70-80% pass@1 |
| RLAIF (Lee et al., 2023) | AI vs Human | No | No (text) | AI approximates human for text generation |
| HumanEval+ (Liu et al., 2023) | Visible vs Hidden tests | No | Yes | Hidden test gap 30-40% performance drop |
| **Our Work** | **Execution vs AI vs Human** | **Yes (competitive/basic/realistic)** | **Yes** | **Exec-human ρ task-dependent (0.68→0.35), supervised AI ρ=0.85** |

We position our work as the first to combine multi-modal feedback comparison with task-type segmentation, addressing the gap left by execution-only (CodeRL), text-only AI alignment (RLAIF), and unsegmented evaluation (HumanEval+).
