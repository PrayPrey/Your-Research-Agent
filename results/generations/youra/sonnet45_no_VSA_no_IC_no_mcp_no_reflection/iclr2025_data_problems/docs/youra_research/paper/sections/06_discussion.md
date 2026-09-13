# Discussion

Our results validate a four-component measurement framework for data quality in foundation model pretraining, while exposing important limitations in our understanding of the causal mechanisms and compute tradeoffs.

## Key Findings and Interpretation

**Deduplication as strongest quality factor (r = 0.72)** provides quantitative support for practitioner intuition. GPT-3, Gopher, and LLaMA all employ fuzzy deduplication, but prior to this work, no controlled experiments isolated its effect size relative to other quality dimensions. Our finding that dedup explains 52% of information density variance—more than diversity (42%), perplexity (34%), or efficiency (28%)—gives evidence-based priority ranking for curation resource allocation.

Why is deduplication so important? Information theory provides a mechanistic explanation: duplicate tokens carry **zero marginal information** (Shannon, 1948). The second occurrence of identical text cannot teach a language model anything new, yet it consumes full compute cost during training. A corpus with 40% duplicates wastes 40% of gradient updates on zero-information examples. Removing them increases the effective information density per token—exactly what we observe.

**Domain diversity as second-strongest (r = 0.65)** validates The Pile's emphasis on multi-domain curation (Gao et al., 2020), but our quantitative comparison reveals an interesting hierarchy: **deduplication > diversity**. This suggests that within-domain redundancy removal matters more than cross-domain breadth. For practitioners, this implies: first deduplicate each domain, then mix diverse sources—not the reverse.

**Modest composite advantage (+8% over best single metric)** indicates quality dimensions are approximately linear. This has two implications: (1) production systems can use simple weighted averages (no need for neural quality scorers), and (2) strong non-linear interactions between quality factors are absent. The latter is surprising—one might expect perplexity and efficiency to interact (low-perplexity boilerplate has high redundancy)—but our data shows additive effects dominate.

**Reproducibility (CV < 10%)** addresses a critical practical concern: is Q(D) measurement stable enough for production use? Data quality metrics that vary wildly between samples would be useless for scaling law integration. Our low variance (average CV = 5.3%) confirms Q(D) captures robust, replicable signals. This stability likely stems from aggregation over billions of tokens—small sample noise averages out at corpus scale.

## Negative Result: h-m1 PoC Failure

The h-m1 proof-of-concept failed to validate the causal mechanism (curation increases information density) due to scale mismatch: 500k tokens vs 10B specification. We report this negative result **honestly and in detail** because it illustrates an important lesson about scale-dependent effects in foundation models.

Why did PoC fail when h-e1 succeeded? h-e1 measured **static correlation** across 12 independently created subsets—no training required, no scale threshold. h-m1 tested **dynamic causal effect** via gradient-based training—this requires convergence, which demands scale. At 500k tokens (0.005% of spec), GPT-2 small barely memorizes training data, let alone learns distributional properties sensitive to curation.

The **Fisher information decrease** (-20.84% vs +15% expected) is particularly puzzling. Three competing explanations:

1. **PoC artifact:** Insufficient data for FIM to stabilize. Full-scale experiment may show expected increase.
2. **Easier-data hypothesis:** Curated data has lower perplexity → model predicts better → gradients smaller. This would mean Fisher is *inversely* correlated with quality in pretraining (opposite supervised learning regimes where harder examples increase Fisher). If true, entropy is correct density proxy; Fisher is not.
3. **Metric definition issue:** Diagonal FIM approximation may be insufficient. Full Fisher trace or gradient L2 norm may behave differently.

We cannot definitively resolve this without full-scale h-m1 execution (budgeted for future work). For now, we recommend **entropy as primary density measure** based on h-e1 validation, and treat Fisher as optional pending further validation.

## Limitations

### Domain Scope: Web Text Only

We validated Q(D) on C4 (web-crawled English text), the most common pretraining corpus (GPT-3, T5, LLaMA). Generalization to other domains—code (The Stack), scientific text (arXiv), multilingual (mC4)—is untested. This is a **principled boundary condition**, not an oversight.

Why might Q(D) transfer or fail to transfer?

- **Likely to transfer:** Deduplication (redundancy is universal). Token efficiency (boilerplate exists in all domains).
- **May require recalibration:** Domain diversity (8 web categories vs 50 programming languages). Perplexity (code has different syntactic patterns than prose).

Future work should test Q(D) on The Stack and arXiv, expecting component *weights* to differ but *correlation structure* to hold.

### Scale Limitation: Correlation, Not Causation

h-e1 validates correlation between Q(D) and information density. It does NOT prove that **curation increases density** (causality) or that **higher density reduces compute requirements** (efficiency claim). These require:

- **h-m1 at full scale (900 GPU-hours):** Train models on curated vs baseline data, measure entropy/Fisher change >20%/15%
- **h-m2 (2000-5000 GPU-hours):** Map compute-quality tradeoff surface, test whether higher Q(D) reduces FLOPs for target performance

Without h-m1 → h-m2 validation, our contribution is a **measurement tool**, not a complete scaling law. Practitioners can *measure* Q(D) now, but cannot yet *optimize* compute-quality tradeoffs quantitatively.

### Model Scale: GPT-2 Small Only

We used GPT-2 small (125M params) for perplexity scoring and h-m1 training. Scale-invariance—whether Q(D) component weights hold at 1B-100B parameters—is untested (hypothesis h-c1, blocked by h-m1/h-m2). 

Two possibilities:

1. **Universal Q(D):** Same weights work across 125M-100B (ideal case, simplifies deployment)
2. **Scale-dependent recalibration:** Larger models weight diversity higher (hypothetical: 100B models need broader knowledge coverage)

Literature provides weak evidence for (2): GPT-3 (175B) used more aggressive domain mixing than GPT-2 (1.5B). But this is correlation, not controlled experiment. h-c1 would test this rigorously.

## Broader Impact

**Positive impacts:**

1. **Cost reduction:** Q(D) measurement enables data-driven curation investment decisions. If dedup (r=0.72) provides 2× ROI vs efficiency (r=0.53), allocate accordingly.
2. **Environmental benefit:** Reducing redundancy → less wasted compute → lower carbon footprint for same model quality.
3. **Democratization:** Smaller labs can achieve better performance with optimized data, not just more GPUs.

**Negative impacts:**

1. **Bias amplification risk:** Q(D) optimizes for "information density" without fairness constraints. If deduplication removes minority-group text at higher rates (e.g., AAVE has fewer web duplicates than standard English), maximizing Q(D) could amplify demographic biases.

2. **Measurement-target mismatch:** Optimizing perplexity score (GPT-2-based) may overfit to GPT-2's specific biases. A perplexity filter trained on biomedical text would score medical jargon as "high quality" and everyday language as "low quality."

**Mitigation:** Future work should integrate fairness-aware Q(D) extensions—e.g., stratified deduplication (equal dedup rates across demographic groups), or multi-model perplexity consensus (average of GPT-2, BERT, domain-specific models).

**Impact Statement (ICML Requirement):** This work provides tools for more efficient foundation model training, with potential cost and environmental benefits. However, practitioners must be aware that optimizing data quality metrics without fairness constraints risks amplifying existing biases in web-scale corpora. We recommend auditing Q(D) optimization for demographic disparities and incorporating fairness constraints in production deployments.

## Comparison to Prior Work

**Chinchilla (Hoffmann et al., 2022):** Provides L(N, D, C) with compute-optimal N-D ratios. Our Q(D) extends this toward L(N, D, Q(D), C). Chinchilla treats quality as constant; we measure it.

**GPT-3 (Brown et al., 2020):** Uses fuzzy dedup heuristically. We validate it quantitatively (r=0.72, strongest component).

**The Pile (Gao et al., 2020):** Emphasizes diversity (22 sources). We show dedup > diversity (r=0.72 vs 0.65) for web text—diversity matters, but redundancy removal matters more.

**Data pruning (Sorscher et al., 2022; Abbas et al., 2023):** Removes low-value examples via model-based scoring. Our Q(D) is model-agnostic (computable before training), enabling pretraining-from-scratch use cases.

**Data-Centric AI (Ng, Mazumder):** Qualitative quality emphasis. We provide quantitative operationalization.

Our unique contribution is **controlled experimental validation** of quality metrics via information density, bridging qualitative practitioner knowledge and quantitative scaling law formalism.

## Future Directions

**Immediate priority:** Execute h-m1 at full scale (9 conditions × 50GB × 50k steps, 900 GPU-hours). This unblocks the entire hypothesis chain (h-m2 → h-c1 → Phase 5 baseline comparison).

**Medium-term (6-12 months):** 
- h-m2: Map compute-quality tradeoff curves (test "does 20% Q(D) improvement reduce compute 15%?")
- h-c1: Test scale-invariance across 1B-100B parameters
- Domain transfer: Validate Q(D) on The Stack (code) and arXiv (science)

**Long-term vision:**
- Unified scaling law: L(N, D, Q(D), C) with fitted power-law coefficients
- Pareto-optimal resource allocation: Solver for "given $10M budget, what (N, D, Q(D), curation_cost) maximizes performance?"
- Quality-aware data markets: Datasets priced by measured Q(D), not just token count

## Positioning as Measurement Contribution

We emphasize: this is a **tool paper**, not a solved scaling law. We provide:
- ✅ Validated Q(D) measurement framework (r=0.78, CV<10%)
- ✅ Evidence-based curation priority ranking (dedup > diversity > perplexity > efficiency)
- ❌ NOT: Causal proof that curation increases density (h-m1 PoC failed)
- ❌ NOT: Compute efficiency quantification (h-m2 blocked)

The contribution is making data quality **measurable**—the necessary first step before *optimizing* it. Future work will complete the optimization story.
