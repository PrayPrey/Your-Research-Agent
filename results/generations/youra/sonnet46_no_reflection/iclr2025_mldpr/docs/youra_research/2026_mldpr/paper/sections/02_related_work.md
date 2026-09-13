# Related Work

We position BCBHS at the intersection of three research threads: benchmark saturation detection, benchmark overfitting measurement, and contamination-based evaluation quality assessment. Each thread contributes partial solutions; none addresses the cross-domain causal framework we establish.

## Benchmark Saturation Metrics

The most closely related work is the $S$-index of [Polo et al. 2026], which quantifies score ceiling compression for LLM benchmarks as $S_\text{index} = \exp(-R_\text{norm}^2)$, achieving Bayesian $R^2 = 0.884$ in predicting saturation from benchmark metadata features (age, test set size, adoption). The evaleval/benchmark-saturation repository implements $S$-index for 60 LLM benchmarks with time-series tracking and saturation clustering. While this work represents a significant advance, it is LLM-specific, retrospective (it describes current saturation state rather than predicting future collapse), and uses a single formula not designed for CV or tabular domains. Critically, it does not validate a causal mechanism linking submission accumulation to compression, leaving open the question of whether $S$-index detects a causal process or a correlated descriptor.

Our work extends this line by: (a) operating across CV, NLP, and tabular domains simultaneously with domain-calibrated signals; (b) providing Granger causal validation of the compression mechanism on real panel data; and (c) measuring compression prevalence at the field scale (466 benchmarks, 7 years).

## Benchmark Overfitting Measurement

Roelofs [2019] established the foundational methodology for quantifying benchmark overfitting through CV retesting studies, demonstrating that CIFAR-10 and ImageNet models exhibit systematic accuracy drops on newly constructed test sets, consistent with implicit overfitting to statistical properties of the original test distributions. This work characterizes overfitting post-hoc via retest experiments and is limited to CV benchmarks with available held-out data. It does not automate detection from leaderboard submission patterns, does not generalize to NLP or tabular domains, and does not provide a prospective prediction framework.

Recht et al. [2019] independently confirmed the robustness gap phenomenon on ImageNet, showing that top models achieving $\sim$76% on the original ImageNet test set achieve only $\sim$64% on a newly sampled ImageNet distribution — a persistent gap across architectures and training procedures. This robustness gap serves as a signal of CV benchmark over-optimization, and we adopt score variance as our CV-domain $H_d$ proxy based on this line of work.

Both Roelofs [2019] and Recht et al. [2019] focus on CV-specific retest studies. BCBHS automates detection using leaderboard submission trajectories — no held-out test sets required — and extends the framework to NLP and tabular by designing domain-appropriate health signals.

## Test Set Contamination Detection

A separate thread addresses test set contamination: training data leakage into benchmark evaluation. ConStat [eth-sri] provides performance-based contamination detection without requiring text access, detecting contamination through statistical anomalies in performance distributions. The lm-sys/llm-decontaminator [320★] and Contamination\_Detector [liyucheng09, 53★] detect rephrased sample contamination in LLM training corpora. MLE-bench [Chan et al. 2024] investigates pre-training contamination impact on 75 Kaggle benchmarks, finding that contamination measurably inflates apparent benchmark performance.

These tools address contamination as a cause of benchmark score inflation, which is one pathway to saturation. BCBHS incorporates contamination-adjusted deviation as the NLP-domain $H_d$ signal (building on ConStat methodology), but situates it within a broader framework that also captures CV convergence compression and tabular rank stability — phenomena orthogonal to contamination. The saturation problem is broader than contamination alone.

## Dataset Documentation and FAIR Quality Assessment

The dataset documentation literature [Gebru et al. 2018; Wilkinson et al. 2016; Heinke et al. 2025] addresses static dataset quality at collection time through structured documentation standards (Datasheets for Datasets, FAIR principles). While foundational for responsible data management, this work does not address dynamic benchmark health over the leaderboard submission lifecycle. FAIR compliance metrics and benchmark saturation indicators exist in isolation — no unified pipeline connects static documentation quality to dynamic compression risk.

## Survival Analysis in Evaluation Research

Survival analysis has been applied extensively in clinical and reliability domains for time-to-event prediction [Cox 1972; Kaplan and Meier 1958], but has not previously been applied to benchmark lifecycle prediction on leaderboard panel data. BCBHS introduces the framing of benchmark health monitoring as a survival analysis problem: the time-to-discriminative-collapse $T(B)$ is the event of interest, domain-specific $H_d$ signals are the time-varying covariates, and a Cox proportional hazards model provides the prospective prediction framework. The Granger causal validation we provide (H-M1) establishes the temporal precedence required to justify this survival framing — a prerequisite that prior benchmark evaluation work has not established.

## Summary

Existing work on benchmark saturation is domain-specific (CV or NLP/LLM), retrospective, and lacks causal validation. BCBHS addresses each gap: cross-domain simultaneous coverage (CV, NLP, tabular), empirically validated causal mechanism (Granger causality on real panel data), and field-scale prevalence measurement (31.1% across 466 benchmarks). The prospective survival prediction component (Cox PH C-index validation) is deferred to follow-up work pending collapse event recalibration, but the causal foundation established here makes that step tractable.
