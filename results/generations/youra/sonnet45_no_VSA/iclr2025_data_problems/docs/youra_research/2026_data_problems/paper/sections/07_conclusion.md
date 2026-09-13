# Conclusion

We opened by noting that code generation models exhibit Expected Calibration Error of 0.53—dramatically worse than the 0.08-0.13 typical for image classifiers. To our knowledge, our work establishes the first calibration benchmark for code generation and demonstrates that standard temperature scaling produces 84.8% ECE reduction, substantially exceeding both our validation gate (≥30%) and prior work on CNNs (5-15%).

This finding reveals a fundamental pattern: **autoregressive generation amplifies miscalibration compared to discriminative classification**, creating both challenge (larger calibration problem) and opportunity (more room for calibration improvement). The 3-6× higher baseline ECE reflects autoregressive probability aggregation across tokens and binary evaluation of code correctness—neither of which occur in standard image classification.

Our contributions provide foundation for confidence-based resource allocation in agentic code generation systems:

**First ECE benchmark for code generation:** To our knowledge, we quantify baseline calibration quality (ECE 0.53 on MBPP), establishing that code models are dramatically more miscalibrated than previously studied tasks. This benchmark enables future calibration research in this domain.

**Demonstration of larger calibration effects:** We show temperature scaling achieves 84.8% ECE reduction while preserving pass@1 accuracy (Δpass@1 = 0.0%). This 6-17× larger relative effect than classification tasks (Guo et al., 5-15%) reflects our higher baseline miscalibration (ECE 0.53 vs. 0.10-0.15), demonstrating that code generation has substantially more room for calibration improvement.

**Analysis of why generation amplifies miscalibration:** We provide theoretical rationale (autoregressive probability compounding, binary evaluation, training-eval mismatch) and empirical evidence (reliability diagrams, per-bin error analysis) explaining why code generation exhibits worse calibration than classification.

**Foundation for future confidence-based policies:** By establishing calibrated confidence as a necessary prerequisite, our work enables research on adaptive iteration control—where confidence scores gate decisions about execution, self-critique, and compute allocation. Full validation requires testing monotonicity (H-M1), marginal benefit (H-M2), and system integration (H-C1).

Calibration is not just about reliability—it's the foundation for confidence-based resource allocation in agentic systems. As code generation moves from single-shot prediction to multi-step reasoning, knowing when the model is likely correct becomes essential for deciding when to iterate, when to execute, and when to stop.

Beyond validating this foundation (H-M1: monotonicity, H-M2: marginal benefit, H-C1: execution efficiency), our work opens broader questions:

**Can calibration be improved during training, not just post-hoc?** Modifying the training loss to penalize miscalibration could produce models that are well-calibrated by default, eliminating the need for post-hoc correction.

**Do confidence scores transfer across model scales?** If temperature $T^*$ learned for 7B model transfers to 13B/34B, calibration cost amortizes across model families. If not, per-model calibration is required.

**Does calibration enable adaptive compute allocation beyond code generation?** Confidence-based policies could apply to any multi-step reasoning task (math problem solving, scientific reasoning, autonomous agents)—allocating more compute to uncertain problems and less to confident ones.

We conclude where we began: large language models achieve impressive functional correctness, yet their confidence scores are poorly calibrated. Our work establishes the magnitude of this gap (ECE 0.53) and demonstrates that simple post-hoc methods (temperature scaling) produce dramatic improvements (84.8% reduction). This transforms calibration from a known problem to a research opportunity—understanding why generation amplifies miscalibration and designing methods that produce well-calibrated generative models by default, not just after correction.

Calibration is the bridge from models that work to models that know when they work—enabling agentic systems that allocate resources intelligently under uncertainty.
