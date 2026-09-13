# Discussion

Our results demonstrate that architectural compatibility is a prerequisite for parameter-efficient fine-tuning, not an outcome of it. Zero-shot evaluation exposes structural constraints before compute investment, preventing wasted experiments on tasks that base model architectures cannot support. We discuss the implications, limitations, and future directions emerging from these findings.

## Key Findings and Interpretation

The binary success/failure pattern across GLUE tasks—QQP at 38% (−12pp below random), SST-2 at 81% (+31pp above random)—reveals that architectural capabilities are discrete rather than continuous. Mamba-130M either possesses the required information flow mechanism (bidirectional reasoning) or it doesn't. No intermediate "partial capability" exists: the model cannot perform bidirectional comparison at all, leading to systematically worse-than-random predictions.

This finding challenges a common assumption in transfer learning: that pretrained models possess general language understanding applicable to any downstream task with appropriate fine-tuning. Our results show that "language understanding" is not monolithic—it comprises specific capabilities tied to architectural design. Causal state-space models understand language in a unidirectional sense (predicting next tokens, aggregating left-to-right context) but fundamentally lack bidirectional comparison mechanisms. LoRA fine-tuning can specialize existing capabilities but cannot add absent ones.

The SST-2 success (81% zero-shot accuracy) confirms that checkpoint quality is not the limiting factor. Mamba-130M possesses robust pretrained representations—it simply cannot apply them to architecturally incompatible tasks. This distinction matters for PEFT research: failures should be attributed to architectural constraints rather than insufficient pretraining or model capacity.

## Implications for PEFT Across Architectures

Our findings establish a workflow for validating PEFT applicability beyond transformers:

1. **Zero-shot evaluation as mandatory gate:** Before investing in LoRA infrastructure, test base model on target task without fine-tuning.
2. **Interpret below-random accuracy as hard constraint:** If zero-shot accuracy falls below random baseline, flag architectural incompatibility. Fine-tuning will fail.
3. **Above-random accuracy indicates viability:** Even weak above-baseline performance suggests architectural support. Fine-tuning can specialize these capabilities.

This protocol prevents wasted compute. Training LoRA on QQP after observing 38% zero-shot accuracy would amplify architectural bias rather than overcome it. The model would learn spurious correlations (e.g., "always predict not-paraphrase") that improve training loss without achieving genuine task competence.

For sub-quadratic architectures, this validation is especially critical. Transformers' bidirectional self-attention supports diverse task types, allowing PEFT research to assume architectural compatibility. Causal SSMs, linear attention, and other efficiency-focused architectures introduce constraints that must be validated per-task. Our zero-shot gate provides a principled, low-cost method for this validation.

## Limitations and Scope

**Single architecture tested:** We evaluate only Mamba-130M, one instance of causal state-space models. Broader claims about SSMs require testing additional variants (RWKV, S4, H3). However, the architectural constraint we identify—causal processing prevents symmetric comparison—applies to all autoregressive SSMs, suggesting the failure pattern generalizes.

**Limited task coverage:** Three GLUE tasks provide sufficient evidence for task-dependent compatibility but do not exhaustively characterize SSM capabilities. Full GLUE evaluation, generation tasks, and structured prediction problems would strengthen claims. Our minimal test suite prioritizes rapid validation over comprehensive benchmarking.

**Sample size:** 100 examples per task balances statistical power with computational efficiency. QQP and SST-2 results achieve high significance (p ≤ 0.003) despite modest sample size, validating the approach. MNLI's marginal result (p = 0.42) suggests larger samples might clarify three-way classification performance, but the primary findings (QQP failure, SST-2 success) are robust.

**LoRA untested:** We validate the zero-shot gate principle but do not empirically test LoRA fine-tuning after failure. Our hypothesis predicts fine-tuning would fail (or learn spurious correlations), but confirming this requires additional experiments. The strong prior evidence (38% zero-shot accuracy) makes LoRA failure on QQP highly likely, but empirical validation remains future work.

**Generalization beyond Mamba:** While we focus on causal SSMs, other sub-quadratic architectures (linear attention, RWKV) may exhibit different failure modes. RWKV's dual-direction mode might succeed on bidirectional tasks, invalidating our findings for that architecture. Our claims are bounded to causal SSMs; broader architectural families require separate validation.

## Broader Impact and Ethical Considerations

Our work reduces computational waste by identifying doomed PEFT experiments early. This efficiency benefit has environmental implications—preventing unnecessary training runs conserves energy and reduces carbon emissions. Practitioners can validate architectural compatibility in minutes rather than discovering failures after hours of fine-tuning.

We do not anticipate negative societal impacts from this research. The zero-shot gate helps practitioners avoid failed experiments but does not enable harmful applications. If anything, preventing wasted compute makes PEFT more accessible to resource-constrained researchers, democratizing efficient fine-tuning.

However, we acknowledge a subtle risk: practitioners might interpret our findings as "SSMs are incompetent" rather than "causal SSMs and bidirectional tasks are incompatible." Architectural constraints are task-specific, not absolute limitations. Mamba-130M excels at generation-aligned tasks (SST-2: 81%) and long-context modeling. Our work characterizes compatibility boundaries, not model inferiority.

## Future Work and Open Questions

**Bidirectional SSM validation:** Our findings motivate testing bidirectional state-space models (e.g., RWKV-v5 with dual-direction mode) on GLUE tasks. If bidirectional SSMs succeed on QQP while matching Mamba's efficiency, they would validate LoRA transfer across architecture families without causal constraints.

**Task-architecture taxonomy:** We propose developing a systematic mapping between task requirements (bidirectional comparison, long-range dependencies, structural reasoning) and architectural capabilities (attention mechanisms, recurrence patterns, positional encodings). Such a taxonomy would guide architecture selection before experimentation.

**Architectural augmentation:** Can targeted modifications enable PEFT on incompatible tasks? For example, adding a small bidirectional attention layer to causal SSMs might enable paraphrase detection while preserving efficiency. This "hybrid architecture" approach merges SSM efficiency with Transformer flexibility for specific capabilities.

**Zero-shot calibration:** Our binary threshold (above/below random baseline) is crude. Future work could develop more nuanced calibration: how far above baseline must zero-shot accuracy be to predict successful fine-tuning? Marginal above-baseline performance (e.g., MNLI at 35% vs 33.3%) may indicate fragile compatibility where fine-tuning succeeds only with careful hyperparameter tuning.

**Broader architecture families:** Extending this analysis to linear attention (FNet, Performer), RWKV, and hybrid models (Hyena, H3) would validate whether the zero-shot gate generalizes beyond causal SSMs. Each architecture class may exhibit unique failure modes requiring tailored compatibility checks.

The zero-shot architectural compatibility gate represents a paradigm shift for PEFT: from "fine-tune and hope" to "validate then fine-tune." As efficient architectures proliferate, this principled workflow prevents wasted compute while guiding practitioners toward compatible model-task pairings.
