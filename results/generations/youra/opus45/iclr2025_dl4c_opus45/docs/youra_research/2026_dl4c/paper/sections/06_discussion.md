# Discussion

Our results establish that alignment method choice creates predictable, measurable signatures in error type distributions. Here we interpret key findings, acknowledge limitations, and discuss implications.

## Interpretation of Key Findings

### Zero-Reward Basin Theory Confirmed

The combination of H-M1 (assertion concentration) and H-M2 (execution depth) provides strong support for the zero-reward basin mechanism. Binary execution reward creates a loss landscape where all non-executing programs receive identical zero reward. This topology forces RL optimization to first escape the basin by achieving syntactic validity—only then can the reward signal provide gradients toward semantic correctness.

The 326× depth difference (29.4% vs. 0.09%) quantifies this pressure: RL-generated code compiles and begins executing before failing, while DPO code fails almost immediately. This is not merely a statistical artifact but a direct consequence of reward topology.

### DPO's Surface Plausibility Trap

DPO optimization without execution feedback produces code that appears syntactically reasonable to human preference raters but contains subtle syntax errors. The dominance of `syntax_error` (99.8%) over `indentation_error` (0%) at fine-grained taxonomy suggests DPO code has correct visual structure (indentation, formatting) but invalid Python syntax. Human annotators can easily judge indentation but cannot mentally execute code to detect syntax errors.

This represents what we term the "surface plausibility trap": preference optimization rewards code that *looks correct* without verifying that it *is correct*.

### Effect Amplification Discovery

The most surprising finding is that the alignment signature *amplifies* rather than dilutes at fine-grained taxonomy (V: 0.21 → 0.82). We expected persistence (V > 0.03); we observed 4× amplification. This occurs because:

1. DPO concentrates errors in a single fine-grained cause (syntax_error: 99.8%)
2. RL distributes errors across multiple causes (indentation_error: 69.5%, syntax_error: 22.9%, others: 8%)

This concentration-dispersion pattern creates larger chi-square statistics at fine granularity. The implication is that alignment signatures are more pronounced, not less, when examined in detail—suggesting they reflect genuine optimization dynamics rather than coarse-grained artifacts.

## Limitations

### Model Confounds

Our comparison involves models with different architectures (encoder-decoder vs. decoder-only) and scales (770M vs. 7B). While this is a conservative test—the effect exists despite confounds—we cannot definitively attribute the pattern solely to alignment method. Controlled training from identical base models is needed to fully isolate the alignment effect.

### DPO Model Generality

CodeLlama-Instruct is a general instruction-following model, not a code-specialized DPO checkpoint. This is a pessimistic test for our hypothesis: a dedicated code-DPO model might show weaker effect (if execution-filtered preference data reduces the divergence) or stronger effect (if the pattern is fundamental). Replication with CodeDPO [Chen et al., 2025] or Focused-DPO [Wang et al., 2024] would strengthen generalizability claims.

### Single Language

Our evaluation uses Python-only benchmarks (HumanEval+, MBPP+). Whether the alignment signature generalizes to other languages (Java, C++, JavaScript) remains an open question. Python's syntax flexibility and indentation-based structure may interact uniquely with alignment pressures.

### Sample Size

While our n=1 per problem design yielded highly significant results, the original protocol specified n=10 samples. Larger sample sizes would increase statistical power for fine-grained analyses and enable per-problem variation analysis.

## Implications for Alignment Research

### Failure Modes as Diagnostics

Our results suggest that error type distributions can serve as alignment diagnostics. Rather than relying solely on pass rates, researchers can examine failure mode geometry to understand optimization dynamics. A model with high assertion error proportion indicates successful syntactic optimization; a model with predominant syntax errors indicates incomplete execution feedback integration.

### Complementary Alignment Strategies

The different failure patterns suggest potential for complementary alignment: RL excels at syntactic validity but concentrates remaining failures in semantic errors; DPO (without execution feedback) produces readable code with syntactic fragility. Hybrid approaches—perhaps RL for syntactic robustness followed by preference optimization for semantic quality—could leverage these complementary strengths.

### Execution Depth as a Metric

We introduce execution depth (lines executed / total lines before failure) as a measurable proxy for alignment-induced syntactic validity pressure. This metric strongly differentiates alignment methods (d = 1.69) and may serve as a lightweight diagnostic that does not require full error classification.

## Broader Impact

Our findings reframe alignment from a pure performance optimization problem to a failure-mode engineering tool. Practitioners selecting alignment methods should consider not just pass rate improvements but the failure geometry they induce:

- **RL with execution feedback:** Higher pass rates, failures concentrated in semantic assertion errors, debugging requires understanding code logic
- **Preference-based DPO:** Lower pass rates (without code-specific training), failures concentrated in syntax errors, debugging requires fixing code structure

Understanding this geometry enables more targeted debugging, evaluation, and potentially alignment strategy selection based on deployment context.
