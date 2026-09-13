# Conclusion

Not all execution feedback is created equal—and now we understand why. Fine-grained rewards that pinpoint error locations improve training when that localization is reliable, but inject gradient noise when tracebacks point to symptoms rather than causes.

## Summary

We introduced error-type-gated fine-grained feedback for code LLM training. By conditioning token-level penalties on error type, we preserve the benefits of fine-grained credit assignment for reliably-localized errors (U_line: SyntaxError, NameError, etc.) while avoiding noise injection for unreliably-localized errors (U_ignore: RuntimeError, RecursionError, etc.).

Our systematic verification validates the complete causal mechanism:
- Fine-grained penalties concentrate gradients at traceback locations (16.11×)
- U_line errors have 100% localization accuracy; U_ignore errors have 20%
- Unreliable localization causes measurable gradient noise (p<10⁻¹³)
- Gating improves signal-to-noise ratio (+4.61%) and sample efficiency

This work demonstrates that feedback granularity is a credit assignment reliability decision. Finer is not always better—it depends on whether the underlying localization is trustworthy.

## Future Work

Several directions extend this work. Continuous weighting based on per-exception-type accuracy could replace binary gating. Validation on larger models (770M+) would establish scale generality. Extension to multi-file codebases, where localization is even more challenging, presents both greater difficulty and greater potential benefit.

More broadly, the credit assignment reliability framing applies wherever RL uses spatially localized feedback. Understanding when localization is trustworthy—and designing feedback strategies accordingly—offers a general principle for reward design.
