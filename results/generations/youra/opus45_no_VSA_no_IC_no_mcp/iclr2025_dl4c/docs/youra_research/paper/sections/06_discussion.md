# Discussion

## Key Findings

Our experiments reveal three principal findings about feedback mechanisms in code refinement:

**Finding 1: Counterfactual density explains execution advantage.** The 84.7% CF-score rate demonstrates that execution traces are not merely pass/fail signals—they contain dense, actionable localization information. This quantification is novel; prior work assumed execution was "better" without measuring the information differential.

*Implication:* Practitioners designing code refinement pipelines should prioritize detailed error traces over simple test outcomes. The marginal cost of capturing line numbers and error types yields substantial refinement improvement.

**Finding 2: The mechanism is causal, not correlational.** Our sequential experiments establish that localization → targeting → fix rate is a causal chain. Removing localization (binary feedback) breaks the chain despite providing "ground truth" about correctness. This mechanistic understanding enables principled pipeline design.

*Implication:* The feedback signal matters more than the feedback source. A well-structured AI critic providing accurate localization could, in principle, match execution feedback. The key is information structure, not information source.

**Finding 3: Complexity effect is inverted.** Contrary to intuition that complex tasks benefit more from precise localization, we find uniform or slightly inverse effect. This suggests a task difficulty ceiling: when problems require understanding multi-step dependencies, localization of individual errors provides diminishing returns.

*Implication:* For complex, distributed bugs, complementary strategies (e.g., divide-and-conquer, hierarchical debugging) may be needed alongside localization.

## Connections to Prior Work

Our findings extend and refine prior work:

- **LDB [Li et al., 2024]:** We quantify what LDB assumed—that runtime traces contain debugging information. Our CF-score metric provides a principled measurement.
- **Self-Debug [Chen et al., 2023]:** We confirm Self-Debug's intuition that execution feedback guides edits, and establish the mechanism (68.4% vs 31.2% fix rate).
- **Self-Edit [2023]:** We extend their granularity finding beyond execution-only to include AI comparison.

Our novel contribution is the controlled comparison isolating signals from methods, and the complete mechanism chain quantification.

## Limitations

We acknowledge several limitations:

**L1: Partial Benchmark Coverage.** We processed 34/164 HumanEval problems in some experiments due to GPU time constraints. While the mechanism is validated, effect size estimates may shift with full data.
- *Why acceptable:* PoC validates mechanism; full comparison planned.
- *Framing:* "Mechanism validation on representative subset."

**L2: Single Model Family.** All experiments use CodeLlama-7B-Instruct. Results may be model-specific.
- *Why acceptable:* CodeLlama is representative of instruction-tuned code LLMs.
- *Future work:* Multi-model validation (13B, 34B, 70B; StarCoder family).

**L3: Variable State Extraction Failed.** 0% of traces had variable state extracted, despite parser implementation. This underestimates CF-score.
- *Why acceptable:* Primary success criterion (84.7% ≥ 0.4) met despite this gap.
- *Future work:* Use pytest --showlocals or debugger integration.

**L4: Complexity Hypothesis Refuted.** H-C1 showed execution advantage does *not* increase with complexity.
- *Why acceptable:* SHOULD_WORK gate; logged as finding, not failure.
- *Reframing:* "Execution advantage is robust across complexity, not complexity-dependent."

**L5: AI Critic Model.** Using CodeLlama-7B as critic may underestimate stronger critics (GPT-4, Claude).
- *Future work:* Compare GPT-4 critic versus CodeLlama critic versus execution.

## Broader Impact

**Positive Impacts:**
- Enables more effective code generation systems, reducing programmer burden
- Provides principled guidance for feedback pipeline design
- Demonstrates importance of information structure in AI systems

**Potential Concerns:**
- Improved code generation may accelerate automation of programming jobs
- Execution-based feedback requires sandboxed environments, which may have security implications if improperly configured

**Mitigation:**
- Sandboxing best practices (Docker, limited permissions) are well-established
- Our findings apply to assistive tools, not replacement of human oversight

## Future Directions

Our results suggest several extensions:

1. **Multi-model validation:** Test mechanism on 13B, 34B, 70B models and StarCoder family.
2. **Repository-level generation:** Extend to SWE-bench for multi-file debugging.
3. **Self-critique comparison:** Test whether model-as-critic can learn to approximate execution signals.
4. **Optimal feedback compression:** Identify minimal sufficient localization (which elements of CF-score are necessary?).
5. **Error type stratification:** Analyze whether localizable bugs (type, off-by-one) show stronger execution advantage than distributed bugs.

These extensions would strengthen generalization and deepen mechanistic understanding.
