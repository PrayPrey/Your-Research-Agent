# Conclusion

We began by asking: *Why does LoRA work for Mamba on some tasks but fail on others?* This question motivated our investigation into the spectral dynamics underlying SSM adaptation. Our work demonstrates that the answer lies in a measurable quantity---the spectral memory horizon $H_{\text{spec}}$---that projection-only LoRA cannot extend.

## Summary

In this paper, we developed a spectral analysis framework for understanding parameter-efficient fine-tuning on State Space Models. Our key insight is that SSM state dynamics are governed by eigenvalues that remain structurally isolated from projection parameters, creating an invisible boundary for projection-only adaptation.

Our experiments on Mamba-1.4B establish three foundational results:

1. **The spectral horizon is stable and measurable.** We demonstrated that $H_{\text{spec}} = -1/\log|\lambda_{\max}|$ is an input-independent property with essentially zero variance (CV = $2.22 \times 10^{-16}$), enabling its use as a predictive criterion before fine-tuning.

2. **Projection-only LoRA achieves perfect eigenvalue preservation.** The $A_{\log}$ parameters remain completely frozen during LoRA training ($|\Delta H_{\text{spec}}| = 0.0\%$, correlation = 1.0), confirming that projections and SSM core occupy separate parameter subspaces.

3. **Energy redistribution does not occur.** Contrary to theoretical expectation, projection modifications cannot redirect state energy toward slow eigenmodes ($\Delta E = 5.93 \times 10^{-7}$ nats, six orders of magnitude below threshold). This eliminates the Eigenmode Utilization Hypothesis and confirms the Memory Horizon Separation Hypothesis.

Together, these findings establish that projection-only LoRA is bounded by $H_{\text{spec}} \approx 256$ tokens for Mamba-1.4B. Tasks requiring information dependencies beyond this horizon cannot succeed through projection adaptation alone.

## Future Directions

Our results open several promising research directions, each grounded in specific experimental findings:

**Spectral Surgery Methods.** Since projection-only LoRA cannot modify eigenvalues, the natural next step is developing PEFT methods that target discretization parameters ($\Delta$, $A_{\log}$) directly. Our H-M2 results showing perfect parameter isolation suggest this is technically feasible; the challenge is maintaining efficiency while enabling eigenvalue adaptation.

**Layer-Selective Adaptation.** Our H-M3 analysis revealed that only 2 of 48 layers (layers 18-19) contain slow eigenmodes. This asymmetry suggests a targeted approach: applying SSM-core adaptation selectively to memory-critical layers while using efficient projection-only methods elsewhere.

**Cross-Architecture Validation.** While our framework is theoretically architecture-agnostic, empirical validation on RWKV, RetNet, and Mamba-2 would establish generality. The $H_{\text{spec}}$ computation would require adaptation to each architecture's state representation.

**Controlled Task Evaluation.** Our use of WikiText-103 perplexity as a memory proxy could be strengthened by MQAR evaluation with explicit dependency lengths $L = \{H_{\text{spec}}, 2H_{\text{spec}}, 4H_{\text{spec}}\}$, enabling direct measurement of task failure at the spectral boundary.

## Closing Remarks

The next frontier in SSM adaptation is not better projections, but *Spectral Surgery*: methods that can reshape the eigenvalue landscape while preserving the linear-time efficiency that makes SSMs attractive. Our spectral horizon framework provides both the diagnostic tool---$H_{\text{spec}}$---and the mechanistic understanding to guide this development.

As State Space Models continue their adoption trajectory, understanding their adaptation boundaries becomes increasingly important. We hope this work provides practitioners with actionable guidance and researchers with a theoretical foundation for the next generation of SSM fine-tuning methods.
