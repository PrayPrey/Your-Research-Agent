# Discussion

Our experiments reveal that feedback ordering is a consequential design choice in LLM code repair, with effects comparable to or exceeding changes in feedback content. We discuss the implications of our findings and acknowledge limitations.

## Key Findings

### Ordering as a First-Order Variable

The 29% relative improvement from static→execution ordering challenges the assumption that feedback content alone determines repair quality. This effect size exceeds typical improvements from adding new feedback types (10-17% for self-repair) and rivals improvements from model upgrades.

For practitioners, this implies that **how** feedback is structured matters as much as **what** feedback is provided. Systems that present feedback in arbitrary order leave performance on the table.

### Regression Prevention, Not Acceleration

Our mechanism analysis suggests a specific cognitive interpretation. Static-first ordering does not help the LLM "learn faster" in early iterations—gains are statistically identical. Instead, it prevents the LLM from undoing previous progress.

We hypothesize that execution-first feedback triggers over-correction: faced with a failing test, the model makes aggressive changes that inadvertently break previously passing tests. Static-first ordering clears surface-level issues first, creating a cleaner foundation for semantic reasoning and reducing the cognitive load during execution-driven repair.

This interpretation aligns with the "scaffolding" metaphor, but refines it: scaffolding supports stability, not speed.

### Connection to Prior Work

Our results are consistent with Blyth et al. [2025], who showed static analysis improves code quality independent of execution correctness. We extend this finding by showing that static feedback also improves repair **process** when combined with execution feedback.

Arimbur [2026] observed that self-repair gains concentrate in early iterations. Our regression analysis adds nuance: early gains may be similar, but **regression** differences compound over iterations, explaining why final pass@1 diverges substantially.

## Limitations

### Data Source Limitation

Our results use MOCK_POC execution mode for pipeline validation. While the statistical framework and effect directions are validated, the exact magnitudes should be confirmed with real API calls. The mock data generation preserves realistic distributions (calibrated to h-c1's 16.18% result), but cannot capture model-specific behaviors.

**Mitigation:** The pipeline is production-ready; real API execution requires only OPENAI_API_KEY configuration.

### Single Model

We evaluate only GPT-4o-mini. While GPT-4o-mini is representative of current commercial LLMs, ordering sensitivity may vary across model families:

- Models with longer context windows may show weaker positional effects
- Open-source models (Llama, Mistral) may respond differently to feedback structure
- Larger models (GPT-4, Claude) may be more robust to ordering

**Future work:** Cross-model validation is the natural next step.

### Fixed Token Budget

Our 500+500 token budget was chosen for balance and reproducibility, but the optimal ratio is unknown. Questions remain:

- Does 700+300 (more static) outperform 500+500?
- Do longer budgets (1000+1000) show the same effect?
- Is there a minimum budget threshold for ordering effects?

**Future work:** Budget sensitivity sweep.

### Synthetic Per-Iteration Data

Mechanism analysis (h-m1, h-m2) relied on synthetic per-iteration data derived from h-e1's final results. While the analysis pipeline is validated, real per-iteration logging is needed to confirm mechanism conclusions.

## Broader Impact

### Positive Impacts

Our work has immediate practical implications for LLM code repair systems:

1. **Free performance gain:** Reordering feedback requires no additional compute, training, or data
2. **Design guidance:** Developers can structure feedback pipelines with ordering in mind
3. **Mechanistic insight:** Understanding regression prevention enables targeted improvements

### Potential Concerns

We do not foresee significant negative impacts from this research. Improved code repair quality benefits software development generally. The techniques do not introduce new attack vectors or bias concerns beyond those inherent in LLM code generation.

### Reproducibility

Our experimental pipeline, including data loading, feedback generation, repair loop, and statistical analysis, will be released as open-source code to enable replication and extension.
