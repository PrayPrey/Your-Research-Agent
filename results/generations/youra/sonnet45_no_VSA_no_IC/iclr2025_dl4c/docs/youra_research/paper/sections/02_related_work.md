# Related Work

Our work builds on three research threads: execution feedback for code generation, RL-based alignment for small models, and test-based evaluation methods.

## Execution Feedback for Code Generation

CodeRL [Le et al., 2022] pioneered RL-based code generation using execution feedback from unit tests. Their actor-critic framework treats the code model as policy and trains a critic to predict functional correctness. While CodeRL demonstrates viability, it uses accumulated trajectory rewards without explicit granularity ablation—our work isolates feedback component contributions (binary vs error-type vs trace).

Self-debugging approaches [Chen et al., 2023] employ lightweight execution feedback loops: generate → test → explain → fix. These methods use raw test outcomes and error messages without heavy critic networks, aligning with our stability-first design. However, they focus on iterative refinement rather than training-time alignment efficiency.

CodeRL+ [Jiang et al., 2025] extends execution feedback to variable-level semantics, extracting execution traces with intermediate variable states. This approach targets capability maximization for larger models (>3B parameters) through richer supervision—the opposite direction from our minimal-sufficient-feedback question for small models (<1B). Their +15.5% gain on code-reasoning tasks validates rich feedback value when capacity permits, but introduces infrastructure complexity our lightweight approach avoids.

**Gap:** No prior work systematically measures feedback efficiency (gain-per-bit) across granularity levels for small models. Existing methods use binary [Skopin et al., 2026] or rich traces [Jiang et al., 2025] without controlled comparison.

## RL-Based Alignment for Small Models

Recent work demonstrates execution feedback viability for small models (0.6B-3B parameters). RLVR [Skopin et al., 2026] achieves +13 percentage points on MBPP using unit test outcomes (binary pass/fail) for 0.6-1B models. CoCoS [Cho et al., 2025] achieves +35.8% on MBPP using self-correction with RL-based feedback for 1B models. These results validate that small models benefit from execution signals, but neither explores granularity optimization or efficiency metrics.

Feedback Over Form [McAndrews, 2026] demonstrates execution feedback outperforms pipeline complexity at 1-3B scale, showing feedback presence matters more than training algorithm sophistication. Our work assumes feedback is valuable (building on McAndrews) and asks **which** granularity is optimal—complementary rather than contradictory.

**Gap:** Prior work focuses on capability maximization ('does feedback help?') rather than efficiency optimization ('how much feedback per bit?'). Our efficiency metric (pp-gain / bits-per-problem) provides new lens absent from existing alignment method comparisons.

## Test-Based Code Evaluation

EvalPlus [Liu et al., 2023] exposes test suite insufficiency by augmenting HumanEval with 80× more test cases via automated generation. Their work shows passing limited tests doesn't guarantee functional correctness, motivating execution feedback over token-level supervision. We extend this insight by hypothesizing test coverage moderates feedback granularity requirements (P3): comprehensive tests enable binary sufficiency, weak coverage benefits from error-type semantic hints.

HumanEval [Austin et al., 2021] and MBPP [Chen et al., 2021] provide standard benchmarks with executable test suites, enabling our controlled granularity ablation. We use HumanEval for primary validation (algorithm-focused, hypothesized high coverage) and defer MBPP to future work (entry-level, hypothesized low coverage for cross-benchmark generalization).

**Gap:** EvalPlus demonstrates test quality matters but doesn't explore how coverage moderates feedback requirements. We hypothesize and test (via branch coverage measurement) whether test quality is a design factor for feedback granularity selection.

## Positioning Our Contribution

Our work differs from prior approaches in three ways:

1. **Efficiency optimization lens:** We introduce gain-per-bit metric for principled capacity-aware tradeoffs, enabling resource-constrained practitioners to balance feedback richness against model capacity limitations.

2. **Systematic granularity ablation:** We control for training compute and model architecture while varying only feedback information content (1 bit, 2.3 bits, 5.6 bits), isolating efficiency effects prior work conflates with algorithm or scale differences.

3. **Lightweight sufficiency validation:** We test dual thresholds (absolute gain ≥8 pp AND relative retention ≥80%) to prevent weak-but-technically-sufficient results—binary feedback must achieve meaningful improvement, not just non-zero gain.

This work provides the first systematic efficiency study of execution feedback granularity for small code models, filling the gap between 'feedback helps' (known) and 'which feedback is optimal' (unknown).
