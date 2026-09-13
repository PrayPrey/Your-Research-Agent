# Introduction

When code generation models fail, the nature of their failure reveals more about their training than their architecture. A model aligned with execution-based reinforcement learning fails fundamentally differently than one aligned with preference-based direct preference optimization—yet this distinction has been invisible in standard benchmark evaluations that report only aggregate pass rates.

This matters for anyone building, debugging, or deploying code generation systems. A developer troubleshooting an RL-aligned model should expect assertion errors—code that executes completely but produces incorrect output. In contrast, debugging a DPO-aligned model means anticipating syntax crashes—code that fails before execution begins. Without understanding these alignment-specific failure modes, practitioners misattribute errors and apply ineffective remediation strategies; researchers design metrics that mask true model capabilities.

The surface problem is well-known: code generation models fail on significant portions of benchmarks, with even state-of-the-art systems achieving 50-70% pass rates on standard evaluations. The deeper problem we address is that different alignment methods—reinforcement learning with execution feedback versus direct preference optimization from human rankings—create fundamentally different optimization pressures that should manifest as systematically different failure patterns. Yet the research community has focused almost exclusively on aggregate pass rates, treating failures as an undifferentiated mass rather than a structured signal of training dynamics.

The gap we identify is stark: no prior study has examined how alignment method choice affects the conditional error type distribution P(error_type | failure). Error taxonomies exist [Wang et al., 2025; Zhang et al., 2024], and alignment method comparisons exist [Xu et al., 2024], but the intersection—stratifying error distributions by alignment method—remains unexplored.

Our key insight is that binary execution reward creates what we term a "zero-reward basin" that forces RL-aligned models to achieve syntactic validity before semantic correctness. When all non-executing code receives identical zero reward, the optimization landscape provides no gradient to distinguish "almost works" from "completely broken." This creates pressure to first escape the zero-reward basin by producing executable code, then optimize for semantic correctness. The result: RL failures occur deeper in execution (code runs further before failing) and concentrate in assertion errors. DPO, optimizing human preferences without execution feedback, produces failures concentrated in early-stage syntax errors.

Building on this insight, we make the following contributions:

**Empirical:** We provide the first systematic comparison of error type distributions between RL-aligned and DPO-aligned code generation models, demonstrating statistically significant divergence (chi-square p < 0.001, Cramér's V = 0.21) across 766 failures on HumanEval+ and MBPP+.

**Mechanistic:** We validate the zero-reward basin theory, showing that RL-aligned models produce a non-zero proportion of assertion errors (2.12%) compared to zero for DPO (Fisher's exact p = 0.0027), and execute 326 times deeper into code before failure (Cohen's d = 1.69).

**Methodological:** We introduce execution depth as a measurable proxy for alignment-induced syntactic validity pressure, demonstrating that this metric strongly differentiates alignment methods with large effect size.

**Discovery:** We uncover an unexpected amplification effect: the alignment signature strengthens rather than dilutes at fine-grained error taxonomy levels (Cramér's V increases from 0.21 to 0.82), contrary to the naive expectation that finer granularity would introduce noise.

These findings reframe alignment from a pure performance optimization problem to a failure-mode engineering tool. Alignment objectives act as inductive biases over error geometry, and understanding this geometry enables more targeted debugging, evaluation, and potentially complementary alignment strategies.

The remainder of this paper is organized as follows: Section 2 situates our work within existing literature on alignment methods and code generation error analysis. Section 3 presents our methodology, including the hierarchical hypothesis structure and statistical framework. Section 4 describes our experimental setup. Section 5 presents results across four sub-hypotheses. Section 6 discusses implications and limitations, and Section 7 concludes with future directions.
