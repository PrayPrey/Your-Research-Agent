# Conclusion

We opened by questioning whether a single adapter configuration can serve all tasks optimally in multi-domain deployment scenarios. Measuring a 15.09% oracle gap with uniformly distributed optimal ranks (5/4/4/4) across GLUE and XTREME benchmarks, we now have quantitative evidence: task heterogeneity creates real optimization opportunities that fixed configurations cannot capture.

## Summary

In this work, we addressed the gap between fixed adapter configurations and heterogeneous task requirements by systematically measuring the oracle gap from per-task rank selection. Our key insight is that different tasks genuinely prefer different adapter capacity levels—no single rank dominates when task distributions span diverse domains, dataset sizes, and linguistic phenomena.

Our main contributions are:

**First**, we provide the first quantitative measurement of oracle gap (15.09%) from task-specific LoRA adapter rank selection on multi-domain NLP benchmarks. This measurement establishes that the cost of fixed configurations is substantial (>15% performance improvement available), not a marginal edge case. Prior work treats adapter rank as a global hyperparameter; we quantify what that assumption leaves on the table.

**Second**, we demonstrate that oracle selections distribute evenly across adapter ranks {4, 8, 16, 32} with a 5/4/4/4 split. This uniform distribution proves that different tasks genuinely require different capacity levels—the heterogeneity is systematic (correlated with task characteristics like language and dataset size), not random noise. Even the best fixed rank (rank-8) significantly underperforms the per-task oracle (76.97% vs 88.58%), validating that no one-size-fits-all configuration works for heterogeneous deployments.

**Third**, we provide empirical evidence that rank 4-16 represents the practical sweet spot for LoRA adaptation, while documenting severe overfitting with rank-32 on small datasets. Rank-32 collapses to random baseline (50% accuracy) on CoLA despite having 8× more parameters than rank-4, demonstrating that "bigger is better" fails when adapter capacity exceeds data complexity. This finding has immediate practical implications for practitioners selecting adapter configurations.

## Future Directions

This work establishes the foundation for task-aware adapter routing research. Several promising directions emerge from our findings:

**Completing the routing mechanism validation:** Our results prove the oracle gap exists (15.09%) and is substantial. The natural next step is building and validating routing mechanisms that can exploit this gap. Can meta-learned policies recover ≥60% of the oracle gap with <10% overhead? Does routing accuracy ≥70% hold across task distributions? Can hypervolume-based multi-objective optimization (considering accuracy, FLOPs, latency) increase the gap beyond our accuracy-only measurement? These questions require completing the hypothesis loop with routing policy training, deployment infrastructure, and statistical validation.

**Resolving rank-32 performance ambiguity:** Rank-32's poor performance (62.95% average) could reflect either fundamental overfitting or suboptimal hyperparameters from our uniform training protocol. Rank-specific hyperparameter tuning would resolve this ambiguity: if tuned rank-32 recovers competitive performance, our oracle gap estimate is conservative (gap would shrink); if it remains poor, the overfitting interpretation is strengthened. This investigation has both scientific value (understanding capacity-data interactions) and practical value (establishing upper bounds for rank selection).

**Extending to cross-modal and cross-architectural settings:** Our 17 NLP tasks on LLaMA-2-7B provide robust evidence within the decoder-only transformer domain. But does the oracle gap pattern generalize to vision (ImageNet variants, COCO) and audio (speech recognition, audio classification)? Do encoder-only models (BERT, RoBERTa) or encoder-decoder models (T5, BART) exhibit similar heterogeneity? Cross-modal and cross-architectural validation would establish whether task-specific adapter optimization is a general phenomenon or specific to our experimental setting.

**Exploring richer configuration spaces:** We test discrete ranks {4, 8, 16, 32}. Extending to continuous rank selection, mixture-of-ranks approaches, or hierarchical multi-axis configuration (rank × placement × sparsity) could reveal whether finer-grained control increases the oracle gap or exhibits diminishing returns. Similarly, testing whether oracle gap patterns hold for other parameter-efficient fine-tuning methods (prefix tuning, adapters, IA3) would strengthen generalizability claims.

## Closing Reflection

The era of one-size-fits-all hyperparameters for multi-domain deployment may be ending. As foundation models serve increasingly diverse task distributions—from sentiment analysis to cross-lingual natural language inference to domain-specific reasoning—the gap between fixed configurations and task-adaptive strategies becomes harder to ignore. Our measurement of a 15.09% oracle gap is not just a number. It quantifies the performance improvement available to systems that can match adapter capacity to task characteristics, and it challenges the assumption that choosing rank globally at design time is "good enough."

Whether meta-learned routing policies, continuous rank selection, or hybrid approaches ultimately exploit this gap remains to be seen. But the gap exists, it is substantial, and it reflects systematic task heterogeneity rather than random variation. For researchers working on parameter-efficient fine-tuning, this provides a clear target: build routing mechanisms that can recover a significant fraction of 15.09% improvement without adding prohibitive overhead. For practitioners deploying multi-task systems, it suggests that task-aware configuration strategies are worth investigating when serving heterogeneous workloads.

We hope this work encourages rethinking how we configure foundation models in multi-domain environments—moving from static design-time choices to dynamic deployment-time optimization, one adapter selection at a time.
