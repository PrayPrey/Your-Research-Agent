# Related Work

## Execution Feedback for Code LLMs

Reinforcement learning from execution feedback has emerged as a powerful paradigm for improving code generation. CodeRL introduced using program execution outcomes as reward signals, demonstrating improvements over supervised fine-tuning alone. RLTF extended this by combining multiple feedback granularities: coarse (pass/fail), fine-grained (token-level penalties at error locations), and adaptive (based on test case outcomes). Their ablation studies showed that the combined approach outperforms any single signal, establishing that feedback composition matters.

RLEF took a different approach, incorporating textual execution feedback directly into model prompts during training. While effective, this approach is orthogonal to reward signal design—it modifies the input rather than the reward structure.

Our work builds on RLTF's multi-granularity framework but identifies a critical gap: the uniform application of fine-grained feedback ignores localization reliability. We show that conditioning on error type preserves benefits where localization is accurate while avoiding harm where it is not.

## Aggregation and Credit Assignment

VeRPO recently highlighted that aggregation strategy matters for dense rewards. They identified cardinality bias—where rewards computed over different numbers of test cases create artificial variance—and proposed variance-reduced aggregation. Their analysis demonstrates that naive dense reward application can degrade rather than help training.

Our work addresses a complementary dimension: localization reliability rather than aggregation. While VeRPO asks "how should we combine signals?", we ask "which signals should we apply where?" Both insights derive from recognizing that more information is not always better—it must be accurate information.

## Error Localization in Programming

The program repair and fault localization literature has long recognized that tracebacks vary in usefulness. Spectrum-based fault localization methods weight suspicious lines based on test outcome correlations rather than trusting stack traces directly. However, this insight has not been incorporated into RL reward design for code generation.

RLTF's error categorization (U_line, U_global, U_ignore) implicitly acknowledges this variation but does not exploit it for conditional feedback application. We leverage their existing categorization, demonstrating that it meaningfully partitions errors by localization reliability.

## Credit Assignment in RL

The credit assignment problem—determining which actions led to which outcomes—is fundamental to RL. Temporal difference methods address assignment across time; our work addresses it across tokens. When traceback localization is unreliable, fine-grained feedback misassigns credit to wrong tokens, analogous to delayed reward attribution in temporal credit assignment.

This framing suggests that feedback granularity selection is a credit assignment reliability decision: finer granularity provides better assignment when localization is accurate but worse assignment when localization is misleading.
