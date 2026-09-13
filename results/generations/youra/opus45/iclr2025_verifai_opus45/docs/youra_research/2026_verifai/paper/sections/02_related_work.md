# Related Work

Our work intersects three research areas: LLM-based code repair, execution feedback for program synthesis, and automated program repair. We position our contribution as the first controlled granularity comparison, addressing a gap that spans all three areas.

## LLM Self-Repair and Iterative Refinement

The paradigm of using execution feedback for LLM code repair was established by Chen et al. [2023] with Self-Debug. This seminal work demonstrated that LLMs can improve their own code using "rubber duck debugging"—explaining the code and error, then generating a fix. Self-Debug achieved 12% improvement on MBPP and 2-3% on Spider using error message feedback (approximately G2-level in our taxonomy). However, the work did not explore whether simpler or more detailed feedback would yield different results.

Subsequent work extended this paradigm. Jiang et al. [2024] introduced LeDex, adding chain-of-explanation before refinement to improve Pass@1 by 15.92%. Gehring et al. [2024] applied reinforcement learning to execution feedback in RLEF, achieving state-of-the-art on competitive programming. Li et al. [2024] explored tree search over the repair space with CodeTree, reaching 95.1% on HumanEval. These works demonstrate the effectiveness of execution-guided repair but share a common limitation: **feedback granularity is treated as fixed rather than as a design variable**.

Most closely related to our finding is Haque et al. [2025], who observed that execution traces "provide limited improvement unless LLM-optimized prompts are used." This hints at our result but stops short of systematic granularity comparison. Our work provides the controlled experiment needed to quantify the granularity effect.

## Execution Trace-Based Repair

A parallel line of research focuses specifically on leveraging detailed execution traces. TraceFixer [Bouzenia et al., 2024] uses runtime traces with divergence point detection, achieving 13-20% improvement over baselines. DynaFix [Huang et al., 2025] incorporates variable states, control-flow paths, and call stacks for iterative repair, fixing 186 bugs on Defects4J. TraceCoder [Huang et al., 2026] applies fine-grained trace analysis with multi-agent architectures.

These works implicitly assume that detailed traces provide superior signal—the "more information is better" assumption our results challenge. While these approaches may be effective for larger models or different task distributions, our evidence suggests the assumption does not hold universally. At the 7B scale on MBPP-style problems, full traces (G4) achieve only 22.7% success compared to 41.8% for pass/fail (G0).

## Automated Program Repair

Traditional automated program repair (APR) uses fault localization to guide patch generation [Dikici and Bilgin, 2025]. Spectrum-based and mutation-based localization techniques identify suspicious code regions, which repair algorithms then target. This paradigm assumes localization is beneficial—a reasonable assumption for template-based and search-based repair.

Recent work has integrated APR techniques with LLMs. GiantRepair [Li et al., 2024] combines LLM patch generation with program-specific optimization. TokenRepair [Kong et al., 2025] uses token-level uncertainty to localize faulty code. RepairAgent [Bouzenia et al., 2024] implements an autonomous localize-analyze-fix-test loop.

Our results suggest that the value of localization for LLM-based repair may be scale-dependent. Traditional APR benefits from precise localization because repair algorithms have limited search capacity. LLMs, by contrast, may have sufficient capacity for global reasoning but insufficient capacity to productively integrate detailed localization signals—at least at smaller scales.

## Positioning Our Contribution

Prior work varies feedback granularity incidentally rather than systematically. Table 1 summarizes the feedback levels used by key approaches:

| Approach | Feedback Level | Granularity Comparison |
|----------|---------------|----------------------|
| Self-Debug [Chen et al., 2023] | G2 (error + message) | None |
| TraceFixer [Bouzenia et al., 2024] | G4 (full trace) | None |
| DynaFix [Huang et al., 2025] | G4+ (trace + states) | None |
| LeDex [Jiang et al., 2024] | G2 | None |
| Haque et al. [2025] | G4 | Observed limited benefit |
| **This work** | **G0-G4** | **Systematic comparison** |

Our contribution fills this gap with a controlled five-level comparison using the same model, benchmark, and prompt template across all conditions. This reveals that granularity is not merely an implementation detail but a critical design choice with 25+ percentage point impact on repair success.
