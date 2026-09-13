# Related Work

Our work intersects parameter-efficient fine-tuning, multi-task learning, and neural architecture search. We position our contribution as measuring the foundation for task-aware adapter routing—quantifying the oracle gap that existing fixed-configuration approaches leave on the table.

## Parameter-Efficient Fine-Tuning

**LoRA** (Hu et al., 2021) introduced low-rank adaptation as an efficient alternative to full fine-tuning, injecting trainable rank-decomposition matrices into frozen transformer layers. The method achieves comparable performance to full fine-tuning while training only 0.1-1% of parameters, with rank r controlling the capacity-efficiency trade-off through O(d·r) parameter scaling. Follow-up work explored variants: AdaLoRA (Zhang et al., 2023) adapts rank dynamically during training, and QLoRA (Dettmers et al., 2023) combines LoRA with quantization for memory efficiency.

However, all these methods treat rank as a global hyperparameter chosen once and applied uniformly across tasks. Practitioners typically fix rank at 8 or 16 based on validation performance on a single task or average performance across a task suite. Our work challenges this assumption by measuring the oracle gap from per-task rank selection, demonstrating that heterogeneous task distributions create 15% optimization opportunities that fixed configurations cannot capture.

**Adapter-based methods** (Houlsby et al., 2019; Pfeiffer et al., 2020) inject small bottleneck layers into transformers, achieving task-specific adaptation while keeping the base model frozen. AdapterHub (Pfeiffer et al., 2020) provides a framework for sharing and composing adapters across tasks, demonstrating that different tasks benefit from different adapter configurations. While this work shows task-specific adapter effectiveness, it does not quantify the oracle gap from capacity selection or systematically measure heterogeneity across multi-domain benchmarks. We extend this line by providing quantitative evidence that adapter rank heterogeneity creates measurable performance gaps.

**Prefix tuning and prompt-based methods** (Li and Liang, 2021; Lester et al., 2021) prepend trainable vectors to input sequences, achieving parameter efficiency through soft prompt optimization. These methods also face the same fixed-configuration problem: prefix length and depth are chosen globally. Our oracle gap measurement methodology could extend to these methods, though we focus on LoRA as the most widely adopted approach.

## Multi-Task Learning and Task Heterogeneity

**Multi-task learning** (Caruana, 1997; Ruder, 2017) has long recognized that different tasks may benefit from different model capacities or architectures. Recent work on task-conditional computation includes Mixture-of-Experts (Shazeer et al., 2017; Fedus et al., 2022), which routes inputs to different expert subnetworks, and multi-domain learning (Guo et al., 2018), which adapts representations based on domain characteristics.

However, these methods route *during training* to learn shared representations with task-specific specialization, not *at deployment* to select from pre-trained adapter configurations. Our work focuses on the deployment scenario: given a library of pre-trained adapters with different ranks, how much performance is lost by using a single fixed rank versus selecting per-task? The 15.09% oracle gap we measure quantifies this deployment-time optimization opportunity.

**Task complexity analysis** (Bingel and Søgaard, 2017; Talmor and Berant, 2019) has studied why some tasks are harder than others, identifying factors like dataset size, label noise, and linguistic complexity. Our finding that oracle rank selections correlate with task characteristics (Chinese tasks prefer rank-4, German tasks prefer rank-32) aligns with this literature, but extends it to the adapter capacity dimension. We show that task heterogeneity manifests not just in difficulty but in optimal configuration choices.

## Neural Architecture Search and Hyperparameter Optimization

**Neural Architecture Search** (Zoph and Le, 2017; Pham et al., 2018; Liu et al., 2019) automatically discovers optimal architectures for each task, achieving state-of-the-art performance at the cost of expensive search procedures (hundreds of GPU hours per task). AutoML systems (Feurer et al., 2015; Thornton et al., 2013) similarly optimize hyperparameters per task through extensive grid or Bayesian search.

These approaches validate that per-task optimization can improve over fixed configurations, but their computational cost makes deployment-time adaptation impractical. Adapter rank selection offers a lighter-weight alternative: instead of searching architecture space, select from a small discrete set of pre-trained ranks. Our oracle gap measurement establishes an upper bound (15.09%) for this approach—if meta-learned routing can approach this bound with minimal overhead, it provides a practical alternative to expensive per-task search.

**Once-for-all networks** (Cai et al., 2020) train a single super-network that supports multiple sub-architectures, enabling deployment-time selection without retraining. This paradigm aligns with our vision: train multiple adapter ranks once, then route at deployment based on task characteristics. However, once-for-all networks focus on edge device constraints (latency, memory), while we focus on multi-task performance optimization. Our oracle gap measurement provides the missing piece: quantitative evidence that task-adaptive selection is worth the added routing complexity.

## Multi-Domain Benchmarks

**GLUE** (Wang et al., 2018) and **SuperGLUE** (Wang et al., 2019) established multi-task evaluation as a standard for natural language understanding, comprising 9 and 8 tasks respectively spanning sentiment analysis, natural language inference, paraphrase detection, and semantic similarity. **XTREME** (Hu et al., 2020) extends multi-domain evaluation to cross-lingual settings, covering 40 languages across 9 task types.

These benchmarks were designed explicitly for task diversity—measuring model robustness across linguistic phenomena, not just average performance. Our work leverages this diversity to test the task heterogeneity hypothesis: if GLUE and XTREME span fundamentally different task characteristics, then optimal adapter configurations should vary across tasks. The uniform distribution of oracle selections (5/4/4/4 across ranks) confirms that these benchmarks exhibit sufficient heterogeneity to create measurable optimization opportunities.

## Positioning Our Contribution

Prior work has established: (1) parameter-efficient fine-tuning methods like LoRA work well with fixed rank configurations, (2) different tasks have different characteristics and difficulty levels, and (3) per-task architecture or hyperparameter optimization can improve performance at high computational cost.

Our contribution bridges these areas by asking: **how much performance is lost by forcing a single fixed adapter rank across heterogeneous tasks?** By systematically training all rank-task configurations and measuring the oracle gap (15.09%), we provide the first quantitative answer to this question. This measurement establishes the foundation for future task-aware routing research: the gap exists, it is substantial (not a 2-3% edge case), and it is worth investigating whether lightweight routing mechanisms can capture a significant fraction of this performance improvement.
