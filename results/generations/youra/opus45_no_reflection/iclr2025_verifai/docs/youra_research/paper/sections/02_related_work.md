# Related Work

## Self-Repair and Iterative Refinement

LLM-based self-repair has emerged as a promising paradigm for improving code generation accuracy. \citet{howmanytries2026} systematically evaluated self-repair on HumanEval, finding improvements of 4.9–17.1 percentage points over single-shot generation. Critically, they identified that assertion errors have the lowest repair success (~45%) while syntax errors are easiest to fix. CodeCoR \citep{codecor2025} achieved 77.13% Pass@1 through multi-agent collaboration, representing current state-of-the-art. However, these works focus on *whether* repair works rather than *why* certain feedback enables better repair.

\citet{debuggingdecay2025} identified "debugging decay"—60–80% capability loss after 2–3 repair attempts—suggesting that feedback quality in early attempts is crucial. This motivates our focus on single-attempt success and understanding what makes initial feedback effective.

## Trace-Based Debugging

DebugRepair \citep{debugrepair2026} demonstrated that runtime traces outperform error messages for code repair, using debugging-style execution to provide richer context. Self-Debug \citep{selfdebug2023} introduced execution trace methodology for self-repair. While these works establish the superiority of traces over messages, they do not decompose *which aspects* of traces drive improvement. Our Actionable Specificity framework attempts this decomposition.

## Type-Guided Generation

TyFlow \citep{tyflow2025} showed that type system internalization improves functional correctness by providing structured constraints. This suggests that specific, actionable information (types) helps LLMs generate correct code. Our AS framework generalizes this insight: type information contributes to AS_loc (type error locations) and AS_state (type constraints as state).

## Feedback Informativeness Gap

Prior work treats feedback signals as categorical (trace vs. message vs. static analysis) rather than decomposing their information content. CoTran \citep{cotran2023} combined compiler and symbolic execution feedback but did not measure which components drive improvement. Meta's Agentic APR \citep{agenticapr2025} achieved 42.3% solve rate with 11.8 average iterations, demonstrating that iteration quantity alone is insufficient.

**Our contribution** fills this gap by proposing measurable AS components (localization, state exposure, causal context) and testing their extractability. Our negative result—that extraction fails on assertion-dominated benchmarks—reveals a boundary condition that prior work implicitly assumed away.
