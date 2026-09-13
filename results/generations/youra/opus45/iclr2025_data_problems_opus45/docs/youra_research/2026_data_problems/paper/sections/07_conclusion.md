# Conclusion

We began by observing a striking phenomenon: when practitioners ask "which training examples most influenced this prediction?", different attribution methods give answers that agree on less than 1% of the identified examples. This disagreement is not a deficiency to be overcome with better algorithms—it is a structural property of non-convex optimization landscapes.

## Summary

Our work provides the first rigorous Pareto characterization of data attribution methods under finite-compute constraints. Through systematic validation of four sub-hypotheses, we established that:

1. **Trade-offs exist and are genuine.** IF and FastIF exhibit statistically significant metric crossings at all five tested compute budgets, with IF achieving higher rank preservation ($\rho_r$) while FastIF achieves higher magnitude fidelity ($\rho_m$). These methods optimize fundamentally different quality dimensions—neither is universally "better."

2. **Trade-offs arise from non-convex geometry.** In convex settings (logistic regression), all quality metrics remain tightly coupled (correlation $\geq 0.99$). But in deep networks (ResNet-18), this coupling breaks down completely ($R^2 = 0.034$), proving that decoupling is structural rather than artifactual.

3. **The practical consequences are extreme.** Different methods identify almost entirely different sets of influential examples (Jaccard = 0.0024). A practitioner debugging model behavior would address different training examples depending on method choice.

These findings fundamentally change how practitioners should approach method selection: rather than seeking the "best" attribution method, they should identify which quality dimension matters for their use case and select accordingly.

## Future Directions

This work opens several promising research directions grounded in our experimental findings:

**Validating on Alternative Architectures.** Our experiments used ResNet-18, which exhibits canonical non-convex behavior. However, Transformer architectures have fundamentally different Hessian structures due to self-attention mechanisms. Validating whether Pareto trade-offs persist—or take different forms—in BERT and vision Transformers would extend the generality of our findings.

**Designing Pareto-Optimal Hybrid Methods.** The discovery that methods optimize different quality dimensions suggests opportunity for hybrid approaches. A method combining TRAK's random projections (strong on rank preservation) with TracIn's gradient similarity (strong on magnitude fidelity) could potentially extend the Pareto frontier rather than simply moving along it.

**Developing Application-Specific Selection Guidelines.** Our results provide the foundation for principled method selection based on downstream application. Future work could develop concrete decision frameworks: "If your goal is X, prioritize metric Y and use method Z."

**Scaling Ground Truth Estimation.** Our ground truth relies on gradient-based proxies due to the computational cost of true LOO retraining. Developing scalable ground truth proxies that remain valid at foundation model scale (billions of parameters) would enable Pareto characterization where it matters most for practitioners.

## Closing Remarks

When practitioners now ask "which attribution method should I use?", our findings suggest they should first ask a different question: "which quality dimension matters for my application?" The search for a universally best attribution method may be fundamentally misguided in non-convex settings—the Pareto frontier is the destination, not an obstacle.

We hope this work encourages the field to embrace multi-objective evaluation, report Pareto fronts rather than single metrics, and recognize that method disagreement reveals different valid perspectives on influence rather than methodological failure. As data attribution becomes increasingly critical for model debugging, data valuation, and ML safety, understanding these structural trade-offs is essential for informed method selection.
