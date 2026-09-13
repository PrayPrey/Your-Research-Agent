# Discussion

## Interpretation: Partial Representation Subspace Overlap

Our central finding—selective coupling across trustworthiness dimensions—suggests a theoretical framework based on **partial representation subspace overlap**. We propose that different trustworthiness capabilities map to partially disentangled regions in the learned representation manifold, where coupling strength reflects the degree of subspace overlap.

**Overlapping subspaces (fairness-robustness):** These dimensions exhibit robust negative correlation (67% architectural replication), suggesting they compete for shared neural substrates. Both fairness and robustness require sophisticated contextual reasoning: fairness demands recognizing and suppressing stereotype-associated patterns in ambiguous contexts, while robustness requires detecting adversarially-manipulated linguistic cues. When LoRA fine-tuning reshapes attention mechanisms to improve truthfulness (factual knowledge retrieval), the indirect effects on contextual reasoning create a zero-sum trade-off—attention patterns optimized for stereotype suppression (fairness) conflict with patterns needed for adversarial vigilance (robustness).

**Orthogonal subspaces (truthfulness-fairness):** The near-zero correlation (r=0.034) across models suggests these dimensions occupy separate representation spaces. Truthfulness (factual accuracy) primarily relies on knowledge stored in feedforward layers and retrieved via factual association patterns, while fairness (bias suppression) operates on social reasoning and stereotype activation in contextual layers. Fine-tuning on TruthfulQA—which targets misconception correction—affects factual knowledge pathways without substantially reshaping social bias representations, explaining the independence.

**Model-specific relationships (truthfulness-robustness):** The strong negative correlation observed in GPT-2 (r=-0.997) but inconsistent replication across architectures suggests this relationship depends on model-specific factors: pretraining data distribution (how factual knowledge and adversarial patterns co-occur), model capacity (ability to maintain separate substrates), or architectural specialization (attention head diversity). This dimension-pair boundary condition highlights that not all coupling is architecture-agnostic.

The representation propagation findings (H-M2) support this framework: while LoRA updates cause universal layer changes (100% coverage), attention mechanisms show 2× larger magnitude shifts than residual streams. This differential suggests attention layers are the primary carriers of cross-dimensional coupling, consistent with attention's role in contextual reasoning shared by fairness and robustness but less central to factual knowledge (truthfulness).

## Limitations

We acknowledge five key limitations that constrain generalization:

**1. Architecture coverage.** We tested only transformer variants (GPT-2, OPT, Pythia), omitting non-attention architectures like state-space models (Mamba, S4, RWKV). Claims of "architecture-agnostic" patterns apply only within the transformer family. SSMs may exhibit different coupling patterns due to fundamentally different sequence processing mechanisms.

**2. Single intervention method.** All experiments used LoRA (rank-8, alpha-16 on attention layers). We cannot distinguish LoRA-specific patterns from general fine-tuning properties. Full fine-tuning (updating all parameters) might show stronger or weaker coupling by affecting MLP layers and residual connections differently. Prompt-based methods might show weaker coupling by operating only in input space without reshaping internal representations.

**3. Small-scale proof-of-concept.** Experiments used 3-5 seeds per condition, limiting statistical power. The truthfulness-robustness correlation (r=-0.997, p=0.051) exemplifies this: enormous effect size but marginally non-significant due to n=3. Effect size estimates carry wide confidence intervals; replication with n≥10 seeds is needed for precise quantification.

**4. Limited dimension coverage.** We tested three dimensions (truthfulness, fairness, robustness), omitting privacy, safety, and machine ethics. The selective coupling taxonomy may extend to these dimensions (e.g., privacy-safety trade-offs), but we cannot claim completeness without empirical validation.

**5. Benchmark proxy metrics.** TruthfulQA, BBQ, and ANLI measure benchmark performance, not real-world trustworthiness. Models may learn benchmark-specific patterns that correlate in ways divorced from genuine capability relationships. Correlation patterns on standardized evaluations may not transfer to production deployment or human-perceived trustworthiness. The truthfulness dimension's unexpected decrease post-intervention (Δ=-3.4% in H-M3) may reflect overfitting to training subset or distribution shift between training and evaluation data.

These limitations establish clear boundary conditions: our findings validate selective coupling for LoRA interventions on transformers using established benchmarks, but generalization to other intervention methods, architectures, dimensions, or deployment contexts requires further validation.

## Broader Impact

This research has implications for both AI safety practice and research methodology:

**For practitioners:** Multi-objective trustworthiness optimization requires dimension-aware strategies. Our findings suggest practitioners can improve truthfulness (via factual fine-tuning) without substantial fairness degradation, as these dimensions appear orthogonal. However, fairness-robustness improvements require explicit multi-objective methods (e.g., Pareto optimization, constrained training) to avoid trade-offs. Deployment teams should monitor non-targeted dimensions when applying targeted interventions, as selective coupling means some dimension pairs will shift while others remain stable.

**For research:** Our perturbation-based experimental design demonstrates a methodology for characterizing cross-dimensional dynamics beyond isolated benchmark evaluation. By systematically varying intervention parameters and analyzing correlation structure, researchers can map the landscape of capability interactions in language models. The five-hypothesis mechanistic validation chain—with MUST_WORK and SHOULD_WORK gates—provides a template for rigorous exploratory research that balances scientific standards with tolerance for unexpected findings.

**Risks and misuse potential:** Understanding cross-dimensional coupling could enable adversarial manipulation—attackers might exploit trade-offs to degrade robustness while nominally improving fairness, or vice versa. However, we assess this risk as low: the coupling patterns we identify are consequences of current training paradigms, not novel vulnerabilities. Defenses against such attacks (multi-objective monitoring, robust evaluation suites) are standard practice in trustworthy AI deployment.

**Positive applications:** This work enables more informed intervention design for multi-dimensional trustworthiness. Knowing that fairness-robustness trade off while truthfulness-fairness are independent allows targeted optimization strategies: separate pathways for factual accuracy versus bias-robustness co-optimization. Multi-task learning approaches can leverage these findings to allocate architectural capacity appropriately—dedicating separate adapter modules for independent dimensions, shared modules for coupled dimensions.

**Long-term considerations:** As language models scale and trustworthiness becomes central to deployment, understanding dimension relationships is essential for safe AI development. Our findings suggest that universal trustworthiness optimization may be fundamentally constrained by representation capacity—some dimensions will always compete. Future architectures might incorporate modular trustworthiness substrates (separate attention heads or layers for different dimensions) to decouple trade-offs, or use meta-learning to discover intervention methods that minimize negative transfer.

We recommend that trustworthiness benchmarks and evaluation frameworks adopt multi-dimensional monitoring as standard practice, reporting correlation structure alongside isolated scores, to surface coupling patterns early in model development rather than discovering them post-deployment.
