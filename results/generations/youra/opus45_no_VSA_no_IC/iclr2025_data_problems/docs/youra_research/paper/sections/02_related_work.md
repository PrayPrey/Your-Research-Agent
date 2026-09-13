# Related Work

Our work builds on three research threads: data attribution methods, attribution benchmarking, and the analysis of learning dynamics.

## Data Attribution Methods

Training data attribution has evolved from influence functions [Koh and Liang, 2017] through increasingly scalable approximations. TracIn [Pruthi et al., 2020] introduced gradient tracing across checkpoints, trading theoretical guarantees for computational tractability. TRAK [Park et al., 2023] achieved further speedup through random projection of gradients, using the insight that influence rankings may be preserved even when absolute scores are approximate. Kronfluence [Grosse et al., 2023] applied Kronecker-factored curvature approximation (K-FAC) to enable influence computation at LLM scale.

These methods represent different computational strategies, but prior work has not systematically characterized *what* each strategy measures. Our work addresses this gap by showing that computational differences manifest as systematic differences in sensitivity to influence modes.

## Attribution Method Fragility and Benchmarking

Basu et al. [2020] demonstrated that influence functions are fragile in deep networks, with approximation errors increasing with network depth. This finding raised concerns about the reliability of gradient-based attribution. However, we show that apparent fragility may be reframed: rather than random errors, different methods exhibit *systematic* sensitivity patterns that become predictable fingerprints.

The DATE-LM benchmark [Jiao et al., 2025] provided the first unified evaluation of LLM attribution methods, revealing that no single method dominates across tasks. Our work complements DATE-LM by explaining *why* methods differ: the inductive biases embedded in each algorithm's mathematics create different sensitivities to memorization, feature transfer, and spurious association.

Several efficiency-focused works have pushed attribution to larger scales. LoRIF [Li et al., 2026] achieved 20x storage reduction on 70B models, and GraSS [Hu et al., 2025] demonstrated 165% throughput improvement through gradient sparsification. GGDA [Ley et al., 2024] introduced group-level attribution with 10-50x speedup. These works focus on computational efficiency; our work focuses on characterizing what efficient methods actually measure.

## Learning Dynamics and Influence Modes

Research on learning dynamics has identified distinct phases and patterns in neural network training. Studies of memorization [Feldman, 2020] show that models memorize atypical examples to achieve low training loss. Feature transfer research demonstrates how learned representations enable generalization. Work on spurious correlations [Sagawa et al., 2020] reveals that models exploit dataset shortcuts.

These distinct influence *modes*—memorization, feature transfer, spurious association—have been studied in isolation. Our contrastive mode probing framework provides a unified lens for measuring how attribution methods respond to each mode, enabling systematic comparison.

## Positioning of Our Work

Prior work either develops individual attribution methods (TRAK, TracIn, Kronfluence), benchmarks their accuracy (DATE-LM), or addresses their efficiency (LoRIF, GraSS). We provide the missing piece: a framework for characterizing methods by their sensitivity profiles, explaining why benchmarks show method-dependent performance and enabling informed method selection based on application requirements.
