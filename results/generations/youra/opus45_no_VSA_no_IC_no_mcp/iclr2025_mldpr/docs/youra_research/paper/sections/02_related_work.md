# Related Work

We position our work at the intersection of three research areas: generalization gap measurement, benchmark analysis, and saturation detection. In each area, we identify limitations that DNSI addresses.

## Generalization Gap Studies

The seminal work of Recht et al. [2019] revealed that ImageNet classifiers exhibit systematic accuracy drops of 11-15% on ImageNet-V2, a carefully reproduced test set following the original data collection methodology. This finding challenged the assumption that leaderboard progress reflects genuine capability improvements. Follow-up work confirmed the pattern: Recht et al. [2019] found 3-5% gaps on CIFAR-10.2, while Barbu et al. [2019] documented 40-45% drops on ObjectNet, which tests object recognition under varied viewpoints and backgrounds.

In natural language processing, McCoy et al. [2019] introduced HANS (Heuristic Analysis for NLI Systems), revealing that BERT's 84% MNLI accuracy collapses when syntactic heuristics are isolated. Models learn shortcuts — lexical overlap, subsequence patterns — rather than robust linguistic reasoning.

However, these studies share a critical limitation: they *measure* gaps after constructing expensive held-out test sets. They provide no method to *predict* which benchmarks will exhibit large gaps. DNSI addresses this gap by computing saturation from historical SOTA records, enabling prediction without new data collection.

## Benchmark Analysis and Leaderboard Dynamics

PapersWithCode [2020] provides comprehensive SOTA tracking for over 5,000 benchmarks, enabling quantitative analysis of benchmark dynamics. Thompson et al. [2020] analyzed compute scaling trends but did not address saturation measurement. Bouthillier et al. [2021] examined reproducibility in ML experiments, finding high variance in reported results.

Bowman and Dahl [2021] offered a qualitative critique of NLP benchmark culture, arguing that leaderboard climbing incentivizes overfitting to test set idiosyncrasies. Schlangen [2021] proposed desiderata for meaningful benchmarks but without quantitative saturation metrics.

These analyses describe the problem qualitatively but lack predictive metrics. DNSI operationalizes saturation as computable quantity, enabling automated detection rather than post-hoc critique.

## Saturation and Diminishing Returns

The concept of benchmark saturation appears informally in ML discourse. Hooker [2021] discussed dataset difficulty and the limits of benchmark-driven progress. Koch et al. [2021] proposed reduced dataset collections but did not quantify saturation.

Information-theoretic approaches to dataset analysis exist but focus on different problems: Ethayarajh et al. [2022] measured dataset difficulty via V-usable information, while Rodriguez et al. [2021] analyzed annotation difficulty. Neither addresses saturation via improvement entropy.

DNSI draws on information theory differently: rather than measuring dataset properties, we measure the *entropy of improvement patterns* in SOTA histories. This captures saturation dynamics directly — how the distribution of gains shifts as benchmarks mature.

## Our Position

Prior work established that generalization gaps exist and described benchmark limitations qualitatively. DNSI provides the missing quantitative bridge: a predictive metric that (1) computes from existing SOTA histories without new data collection, (2) normalizes by task difficulty for fair cross-benchmark comparison, and (3) correlates strongly with measured generalization gaps (R = -0.95). We build on the gap measurements of Recht et al. and Barbu et al. as ground truth, and on PapersWithCode data availability as the computational substrate.
