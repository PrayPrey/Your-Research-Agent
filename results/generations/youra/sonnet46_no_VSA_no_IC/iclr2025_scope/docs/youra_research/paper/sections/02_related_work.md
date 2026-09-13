# Related Work

Our work sits at the intersection of three research areas: attention efficiency methods, entropy-based attention analysis, and zero-shot model modification. We discuss each, highlighting where existing methods fall short of the zero-shot selective layer conversion goal.

## Attention Efficiency Architectures

The quadratic cost of full attention has motivated substantial work on sub-quadratic alternatives. Longformer [Beltagy et al., 2020] demonstrates that sliding window attention reduces FLOPs from O(n²) to O(n·w) per layer, establishing the core efficiency primitive we build upon. Mistral 7B [Jiang et al., 2023] applies SWA with window = 4096 tokens at 7B scale, achieving state-of-the-art performance — but this requires training from scratch with SWA as a design commitment. Neither approach addresses post-hoc conversion of already-trained full-attention models.

More recent work addresses the conversion problem directly. SWAA (Sliding Window Attention Adaptation) [Yu et al., 2025] is the closest baseline: it converts a pre-trained Llama-2 model to SWA but demonstrates that naive zero-shot full-model conversion causes catastrophic quality collapse, requiring lightweight fine-tuning for recovery. SWAT (Sliding Window Attention Training) [Fu et al., 2025] explores SWA during training with proper position encoding adjustments, outperforming linear recurrence on 8 benchmarks — but again, training-time commitment rather than post-hoc conversion. SWARR (SWA + Architecture-Aware RL) [Liu et al., 2026] shows that SFT alone is insufficient after SWA conversion, requiring reinforcement learning for accuracy recovery, further emphasizing the challenge of fine-tuning-free conversion.

*Our positioning:* We share the goal of SWA conversion but specifically target the zero-shot, no-fine-tuning case. SWAA establishes the failure mode of full-model conversion; we ask whether selective conversion of entropy-identified layers can avoid this failure. Our approach requires no fine-tuning — only a 100-sequence calibration pass.

## Entropy-Based Attention Analysis and Pruning

Entropy-based analysis of attention heads has produced actionable pruning insights. Michel et al. [2019] demonstrate that a large fraction of attention heads can be removed at test time without significant accuracy loss, establishing the existence of redundant heads in transformer models. Head-level entropy has been used as a signal for this redundancy: high-entropy heads (diffuse attention weight distributions) contribute less discriminative information.

HIES (Head Importance-Entropy Score) [Choi et al., 2025] combines head importance with entropy for structured head pruning, achieving +15.2% quality improvement over importance-only criteria. This validates entropy as a useful signal for attention head characterization. Entropy-Lens [Ali et al., 2025] analyzes per-layer entropy profiles as information signatures across transformer layers, finding that entropy evolves systematically across depth — consistent with our observation of layer-level entropy heterogeneity in Llama-2-7B.

*Our positioning:* These methods operate at the **head level** for **pruning** — they remove heads entirely. We operate at the **layer level** for **SWA conversion** — we replace the attention mechanism while preserving the layer's residual connection and MLP. This is a distinct operation with different failure modes and different design considerations. Crucially, we show that the aggregation method for layer-level entropy (head-MEAN vs head-MAX) is a first-class methodological decision not examined in head-level pruning literature.

## Fixed and Local Attention Patterns

Several studies establish that transformer attention patterns are not uniformly global. Raganato et al. [2020] demonstrate that fixed positional attention patterns (diagonal, BOS-attending, EOS-attending) emerge in encoder models and are functionally separable from content-adaptive heads, with fixed-pattern heads tolerating removal without quality loss. Michel et al. [2019] complement this with head removability analysis. StreamingLLM [Xiao et al., 2024] exploits sink token attention patterns for streaming inference with a local + sink-token window, suggesting that LLMs have attention structure amenable to local constraints.

*Our positioning:* These works suggest that local-pattern attention is pervasive, motivating our hypothesis that high-entropy (diffuse) layers can tolerate SWA constraints. However, they do not provide a calibration-based criterion for identifying which specific layers in a causal decoder LLM can be converted zero-shot. We operationalize this insight as a per-layer entropy score with explicit stability validation.

## Calibration-Based Model Analysis

Calibration-based methods are well-established in quantization (GPTQ [Frantar et al., 2023], AWQ [Lin et al., 2024]), where 100-sequence calibration sets are standard for collecting activation statistics. Our use of a 100-sequence WikiText-103 calibration set for entropy scoring follows this precedent, adapting it from quantization to layer characterization for SWA conversion. The use of Spearman rank correlation for stability validation follows calibration quality analysis approaches [Pmlr 2026] that assess how consistently a given measurement criterion ranks model components across different data subsets.

*Summary of gaps addressed:* No prior work provides (1) a calibration-only, training-free criterion for layer-level SWA conversion in causal decoder LLMs, (2) a systematic comparison of head-mean vs head-max pooling for layer-level entropy stability, or (3) a validated prerequisite for zero-shot selective SWA conversion in Llama-2-7B. Our work fills this gap.
