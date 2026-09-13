# Abstract

Execution-feedback reinforcement learning and direct preference optimization are
both widely used to post-train code generation models, yet we lack tools to
distinguish whether these methods produce genuinely different structural policy
changes or merely different levels of confidence about the same surface patterns.
We introduce **structural efficiency of policy movement** — semantic AST edit
distance per unit KL divergence — as a diagnostic metric for code generation
alignment, and present an end-to-end measurement framework combining FA-AST
node classification, ZSS tree edit distance, KL-matched checkpoint comparison,
and bootstrap statistical testing. We validate the framework on
DeepSeek-Coder-7B-instruct-v1.5 and report a preliminary finding: despite GRPO
exhibiting substantially higher raw semantic AST edit distances than DPO on
proof-of-concept data, the Semantic Edit Proportion — the fraction of edits
targeting control-flow and data-flow nodes — is nearly identical for both methods
(≈0.237), challenging the assumption that execution reward selectively
concentrates policy movement on functionally relevant code structures. We further
identify and document checkpoint aliasing as a previously undescribed confound in
RL fine-tuning analysis, and provide a corrected experimental protocol.
The framework is ready for deployment; the empirical question awaits a corrected run.
