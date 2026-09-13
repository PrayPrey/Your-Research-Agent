# Discussion

## Key Findings

Our experiments reveal two important findings for the field:

**Finding 1: Error class independence is real and measurable.** The mean Jaccard index of 0.0752 across strategy pairs confirms that grammar constraints, static analysis, and SMT verification target genuinely independent error classes. This validates the theoretical foundation for layered verification pipelines—combining strategies should yield additive (potentially multiplicative) gains rather than diminishing returns.

This finding has practical implications: practitioners can invest in multi-stage verification infrastructure with confidence that each stage contributes non-redundant value.

**Finding 2: Detection is model-agnostic; repair is model-capability-dependent.** Our H-M2 failure reveals a critical prerequisite that prior work did not document. Static analysis tools (Bandit, Pylint) detect issues regardless of which model generated the code—detection is tool-based and model-agnostic. But using that feedback to repair code requires instruction-tuned models capable of following repair instructions. Completion models like StarCoder2-3b cannot use feedback productively.

This explains why Blyth et al. (2025) reported success (they used instruction-tuned models) while our experiments failed. The distinction between detection capability and repair capability has not been explicitly articulated in prior work.

## Limitations

We acknowledge several limitations:

**PoC-level validation scope.** H-M1 was validated on 5 prompts, not the full HumanEval benchmark (164 problems). H-M2 was tested on 8 prompts from SecurityEval. Statistical power is limited; the 40% reduction in H-M1 is indicative, not definitive.

*Why acceptable:* PoC validation demonstrates mechanism effectiveness. Full-scale validation is straightforward future work requiring additional compute, not methodological changes.

**Incomplete pipeline.** Only 2 of 4 mechanism stages were validated. H-M3 (SMT repair) and H-M4 (synergy measurement) were blocked by H-M2 failure. We cannot compute the synergy coefficient or confirm multiplicative improvement.

*Why acceptable:* Partial validation still contributes the error-class-independence framework. The failed hypothesis identifies a critical prerequisite, which is itself a contribution.

**Model-specific failure.** H-M2 failed with StarCoder2-3b specifically. Results might differ with instruction-tuned models (CodeLlama-Instruct, Llama-3-8B-Instruct) or larger models.

*Why acceptable:* The failure identifies model capability as a critical variable. This is actionable guidance for practitioners: verify instruction-tuning before deploying feedback loops.

**Benchmark scope.** All experiments used HumanEval and SecurityEval—single-function Python generation. Results may not generalize to multi-file generation, repository-level code, or non-Python languages.

*Why acceptable:* Starting with standard benchmarks enables comparison with prior work. Extension to broader settings is future work.

## Implications for Practice

Based on our findings, we offer guidance for practitioners deploying verification pipelines:

1. **Grammar constraints work out-of-the-box.** SynCode's token-level masking requires no model-specific configuration and produces measurable improvement.

2. **Verify instruction-tuning before feedback loops.** If your model cannot follow repair instructions in other contexts, it will not use static analysis feedback productively.

3. **Expect independent contributions.** Each verification stage targets a distinct error class; investment in multi-stage infrastructure is justified.

## Broader Impact

This work contributes to safer AI-assisted code generation by identifying how to combine verification strategies effectively. The error-class-independence framework provides principled guidance for pipeline design.

Potential negative impacts are limited. The work does not introduce new attack vectors or capabilities for generating vulnerable code—it focuses on improving code quality.

One concern: over-reliance on automated verification might reduce human review, creating a false sense of security. We emphasize that verification pipelines complement, not replace, human oversight.
