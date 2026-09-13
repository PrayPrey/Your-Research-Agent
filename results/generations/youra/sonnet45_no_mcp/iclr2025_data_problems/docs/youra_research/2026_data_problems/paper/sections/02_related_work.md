# 2. Related Work

## 2.1 Curriculum Learning for Deep Learning

Curriculum learning (Bengio et al., 2009) proposes training on examples ordered from easy to hard to improve convergence and generalization. Subsequent work has demonstrated benefits across supervised learning tasks including image classification (Hacohen & Weinshall, 2019) and neural machine translation (Platanios et al., 2019). These methods typically operate at the individual example level, using heuristics like loss-based difficulty or confidence scores to determine ordering.

**Our work differs in two key aspects.** First, we apply curriculum principles to **domain-level composition** rather than example difficulty, ordering entire data sources (web text, code, scientific papers) rather than individual sequences. Second, we ground scheduling decisions in **corpus statistics** (vocabulary diversity, syntactic complexity) rather than training-time metrics, enabling a priori schedule design without iterative tuning. While example-level curriculum learning addresses what to learn when within a fixed dataset, domain-level scheduling addresses which data sources to emphasize when during multi-domain pretraining.

## 2.2 Multi-Domain Pretraining for Language Models

Modern foundation models like GPT-3 (Brown et al., 2020), PaLM (Chowdhery et al., 2022), and Llama (Touvron et al., 2023) train on diverse corpora spanning web text, books, code, and scientific papers. The standard approach uses **static domain mixing**: fixed sampling probabilities (e.g., Common Crawl 67%, Books 16%, Wikipedia 4.5%) maintained throughout training. These ratios are typically determined through grid search or expert intuition, requiring expensive hyperparameter sweeps.

Recent work by Xie et al. (2023) introduces **DoReMi (Domain Reweighting with Minimax Optimization)**, which optimizes static mixing ratios using group distributionally robust optimization to minimize worst-case domain loss. DoReMi demonstrates that tuned static mixtures outperform uniform mixing by 2-6% across benchmarks. However, DoReMi's weights remain **static throughout training**—it optimizes how much of each domain to include, but not when to present it.

**Our approach complements DoReMi** by introducing temporal dynamics. While DoReMi answers "what are the optimal static proportions?", diversity-ranked scheduling asks "what is the optimal temporal ordering given fixed total exposure per domain?" A natural future direction combines both: use DoReMi to determine domain budgets, then apply diversity-ranked scheduling to order their presentation.

## 2.3 Multi-Phase Training Strategies

Practitioners commonly employ two-phase training: general pretraining on broad corpora followed by continued training on domain-specific data (e.g., code-focused training for Codex). This represents a coarse temporal curriculum with a single sharp transition.

Chronopoulou et al. (2019) study intermediate-task transfer in NLP, finding that task ordering affects final performance in multi-task learning. Ruder & Plank (2017) propose learning to select data for neural sequence labeling, including temporal aspects. However, these works focus on task-level transfer in supervised settings rather than unsupervised pretraining with domain-level scheduling.

**Our contribution** extends multi-phase training to smooth, parametric curriculum schedules with explicit mechanistic grounding. Instead of binary phase transitions (general→specialized), we implement continuous Gaussian-weighted domain scheduling with tunable transition smoothness. This enables systematic exploration of the temporal ordering space beyond ad-hoc two-phase heuristics.

## 2.4 Gradient Geometry in Optimization

Understanding optimization dynamics through gradient geometry has gained attention in deep learning theory. Stringer et al. (2019) introduce the participation ratio (PR) to measure gradient covariance rank in neuroscience models, finding that higher PR correlates with learning diverse representations. Fort et al. (2019) demonstrate that later layers exhibit higher gradient diversity during training.

Kornblith et al. (2019) propose Centered Kernel Alignment (CKA) for measuring representational similarity across neural networks, showing that early training phases establish representational structure that persists to convergence. Neyshabur et al. (2020) study implicit bias in deep learning, arguing that early training shapes the geometry of the solution basin.

**We leverage these tools** to propose a mechanistic explanation for why domain ordering matters: early high-diversity training may establish broader gradient covariance (measurable via PR), which then persists through path-dependent optimization (measurable via CKA similarity between early and final checkpoints). However, **this mechanism remains unverified** in our current PoC validation and requires full-scale multi-checkpoint experiments with gradient covariance measurements (planned h-m1 and h-m2 hypotheses).

## 2.5 Continual Learning and Catastrophic Forgetting

Continual learning addresses the challenge of learning new tasks without forgetting previous knowledge. Classic approaches include Elastic Weight Consolidation (Kirkpatrick et al., 2017), which penalizes changes to parameters important for previous tasks, and rehearsal methods that replay previous data during new task learning (Rebuffi et al., 2017).

McCloskey & Cohen (1989) first identified catastrophic forgetting in neural networks, where learning new information drastically impairs performance on previously learned tasks. Recent work by Ramasesh et al. (2021) studies forgetting in large language models during continued pretraining, finding that model scale and data diversity affect forgetting rates.

**Our hypothesis** suggests that pretraining-time intervention (diversity-ranked scheduling establishing broad gradient geometry) may reduce catastrophic forgetting during later continual learning, complementing post-hoc regularization methods. This represents a shift from "fix forgetting after it happens" to "establish robust geometry during initial pretraining." However, continual learning experiments (hypothesis h-m4: legal domain injection after main training) are pending and not covered in this PoC validation.

## 2.6 Positioning of Our Work

Our work sits at the intersection of curriculum learning (temporal ordering principles), multi-domain pretraining (foundation model data mixing), and gradient geometry (mechanistic optimization analysis). The key novelty is establishing **temporal domain composition as a first-class design principle** with:

1. **Systematic scheduling framework**: Corpus statistics → diversity ranking → parametric Gaussian scheduling (vs ad-hoc two-phase heuristics)
2. **Mechanistic grounding**: Proposed connection between corpus diversity and gradient covariance geometry (pending verification)
3. **Controlled experimental design**: Four conditions (static, diversity-ranked, reversed, shuffled) with matched total domain exposure to isolate temporal ordering effects

**Limitations vs prior work.** Unlike DoReMi's published full-scale results, we report only PoC validation confirming implementability. Performance comparison with n=5 statistical rigor and mechanism verification (gradient covariance measurements) are deferred to ongoing experiments. This positions our work as a technical proposal with feasibility demonstration, complementing rather than replacing existing static mixing optimization methods.
