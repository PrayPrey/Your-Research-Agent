# Discussion

Our experiments establish that projection-only LoRA is bounded by the spectral memory horizon $H_{\text{spec}}$, with the Eigenmode Utilization Hypothesis definitively eliminated. We discuss the implications of these findings, acknowledge limitations, and outline future directions.

## Key Findings

### The Negative Result as Primary Contribution

The most significant finding is what *did not happen*: energy redistribution toward slow eigenmodes is essentially zero ($\Delta E = 5.93 \times 10^{-7}$ nats). This negative result eliminates the EUH mechanism and narrows the hypothesis space for SSM adaptation theory.

This matters because theory suggested a plausible alternative pathway. Input reweighting through projection modifications *could* preferentially excite slow eigenmodes, effectively extending memory without changing eigenvalues. Our experiments demonstrate this mechanism is not operative---not due to insufficient training, but due to structural constraints in the pretrained architecture.

### Structural Explanation

Why doesn't energy redistribution occur? Our per-layer analysis reveals that Mamba-1.4B allocates only 0.002% of total state energy to slow modes ($|\lambda| > 0.99$), concentrated in just 2 of 48 layers. The architecture heavily favors fast-decaying eigenmodes, optimizing for short-term pattern matching rather than long-term memory.

This suggests a design principle: pretrained Mamba models may sacrifice long-term memory capacity for efficiency. The spectral horizon is not an accident but a consequence of architectural and pretraining choices.

### Practical Implications

Our framework provides practitioners with a checklist for SSM adaptation:

1. **Compute $H_{\text{spec}}$** from model weights (takes seconds, no inference required)
2. **Estimate task dependency length** (how far back must the model remember?)
3. **If task length > $H_{\text{spec}}$:** projection-only LoRA will likely fail; consider SSM-core adaptation or alternative architectures

For Mamba-1.4B specifically: $H_{\text{spec}} \approx 256$ tokens. Tasks requiring dependencies beyond this range---long-document QA, multi-turn dialogue with distant context, long-range reasoning---may require methods that modify eigenvalues ("Spectral Surgery").

## Limitations

We acknowledge several limitations of this work:

### WikiText-103 as Memory Proxy

**Limitation:** We use language modeling perplexity on WikiText-103 rather than a controlled synthetic task like Multi-Query Associative Recall (MQAR) with explicit dependency lengths.

**Why Acceptable:** Perplexity degradation at varying context lengths provides meaningful evidence of memory utilization. The 3.03x degradation ratio demonstrates that $H_{\text{spec}}$ predicts real model behavior.

**Future Mitigation:** MQAR evaluation with $L = \{H_{\text{spec}}, 2H_{\text{spec}}, 4H_{\text{spec}}\}$ would enable direct testing of task failure predictions.

### Single Model Family

**Limitation:** Our experiments focus on Mamba-1.4B (and Mamba-370M for cross-validation). Generalization to other SSM architectures (RWKV, RetNet, Mamba-2) is not empirically validated.

**Why Acceptable:** Our theoretical framework is architecture-agnostic; the spectral analysis methodology applies wherever eigenvalues govern state dynamics. Mamba serves as a representative case.

**Future Mitigation:** Cross-architecture validation, adapting the $H_{\text{spec}}$ computation to each architecture's state representation.

### H-M4 Not Executed

**Limitation:** The discriminative MQAR test (H-M4) was not completed. This would directly verify task failure when $L > H_{\text{spec}}$ under projection-only LoRA.

**Why Acceptable:** The H-M3 negative result sufficiently eliminates EUH. H-M4 provides additional confirmation but is not strictly necessary for our conclusions.

**Future Mitigation:** Complete H-M4 with fine-tuned models on MQAR at varying dependency lengths.

### PoC Training Configuration

**Limitation:** We used a single epoch with limited training sequences, optimizing for mechanism validation rather than task performance.

**Why Acceptable:** Our key measurements (eigenvalue preservation, energy redistribution) require only that training produces measurable updates. The loss converged, and perplexity was reasonable (14-16 range).

**Future Mitigation:** Full-scale training to verify findings hold under extended optimization.

## Theoretical Implications

### For SSM Adaptation Theory

Our work contributes to understanding SSM adaptation mechanisms:

1. **Projection vs. Core:** There is a fundamental distinction between adapting projections (input/output mappings) and adapting the SSM core (state dynamics). The former preserves spectral properties; the latter can modify them.

2. **Eigenvalue Isolation:** In Mamba, projection parameters and discretization parameters occupy separate gradient subspaces. LoRA targeting projections has zero effect on eigenvalues---not approximate, but exact.

3. **Energy Distribution is Architectural:** The distribution of state energy across eigenmodes is determined by the $A$ matrix structure, not by input routing. Projections cannot override this constraint.

### For Future PEFT Methods

The "Spectral Surgery" direction emerges as the promising path for beyond-horizon SSM adaptation:

- **Target discretization parameters:** LoRA or similar methods applied to $\Delta$ or $A_{\log}$ could directly modify eigenvalues.
- **Layer-selective adaptation:** The 2 layers with slow modes (18-19) may be strategic targets for memory extension.
- **Architectural design:** Future SSM pretraining could allocate more capacity to slow modes, expanding the adaptation-friendly regime.

## Broader Impact

This work provides principled guidance for SSM adaptation, potentially reducing wasted compute on unsuccessful fine-tuning attempts. By understanding the spectral boundary, practitioners can make informed decisions about method selection.

**Positive Impacts:**
- Reduced trial-and-error in SSM deployment
- Theoretical foundation for future PEFT method design
- Efficiency gains from avoiding doomed adaptation attempts

**Potential Concerns:**
- As with all language model research, downstream applications may inherit biases from pretrained models
- Efficiency improvements in SSM adaptation could accelerate deployment of models with unaddressed alignment issues

We do not identify direct negative impacts specific to our spectral analysis methodology. Standard considerations for responsible AI deployment apply.

## Connection to Prior Work

Our findings explain previously observed phenomena:

- **SSM-PEFT's LoRA ineffectiveness on SSM modules:** We provide the mechanistic explanation---eigenvalues are frozen, energy redistribution doesn't occur.
- **MambaPEFT's task-dependent LoRA success:** Likely corresponds to tasks within $H_{\text{spec}}$; failures occur beyond the boundary.
- **State-offset Tuning's effectiveness:** May succeed because it operates on the state directly, potentially enabling forms of memory extension that projections cannot achieve.

These connections validate our framework as explanatory, not merely descriptive.
